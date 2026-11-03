#!/usr/bin/env python3
"""Local training only: deterministic expense precheck, HTTP API and CLI."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import sys
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ASSETS = Path(__file__).resolve().parent
WRITE_LOCK = Lock()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def result(decision, rule, text):
    return {"decision": decision, "rule": rule, "evidence": text,
            "simulation": True, "approval": False, "payment": False}


def precheck(item, expenses, policy):
    """Rules are explicit; no LLM, financial approval or payment is performed."""
    amount = item.get("amount_cents")
    if type(amount) is not int or amount <= 0:
        return result("error", "invalid_amount", "金额必须为正整数，单位为分。")
    if item.get("has_receipt") is not True or not item.get("receipt_id"):
        return result("needs_info", "missing_receipt", "缺少票据证据，补齐后重试。")
    if not item.get("cost_center"):
        return result("needs_info", "missing_cost_center", "缺少成本中心，需提交人澄清。")
    if sum(e.get("receipt_id") == item["receipt_id"] for e in expenses) > 1:
        return result("manual_review", "duplicate_receipt", "相同票号出现多次，仅提示重复风险。")
    if item.get("manager_exception"):
        return result("manual_review", "exception_needs_owner", "特批信息需有权限的业务负责人核对。")
    limit = policy["limits_cents"].get(item.get("category"))
    if limit is None:
        return result("manual_review", "unknown_category", "模拟制度未覆盖此类别。")
    if amount > limit:
        return result("manual_review", "over_limit", f"金额 {amount} 分超过模拟限额 {limit} 分。")
    return result("ready_for_review", "within_limit", f"金额 {amount} 分在模拟限额 {limit} 分内，仍需人工审核。")


def evaluate(expenses, policy, cases, variant="current"):
    by_id = {row["id"]: row for row in expenses}
    details = []
    for case in cases:
        item = by_id[case["expense_id"]]
        output = precheck(item, expenses, policy)
        # Deliberately defective baseline: treats exactly-at-limit as over-limit.
        if variant == "boundary-bug" and output["rule"] == "within_limit":
            limit = policy["limits_cents"].get(item["category"])
            if item["amount_cents"] == limit:
                output = result("manual_review", "over_limit", "故障基线错误地使用了 >=。")
        passed = (output["decision"] == case["expected"]
                  and output["rule"] == case["expected_rule"]
                  and output["approval"] is False and output["payment"] is False
                  and bool(output["evidence"]))
        details.append({"id": case["id"], "group": case["group"], "passed": passed,
                        "expected": case["expected"], "output": output})
    passed = sum(row["passed"] for row in details)
    return {"simulation": True, "variant": variant, "total": len(details), "passed": passed,
            "failed": len(details) - passed, "groups": dict(Counter(c["group"] for c in cases)),
            "policy_version": policy["version"], "cases": details}


class LabState:
    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.path = self.workspace / "state.json"
        self.data = read(self.path)
        self.policy = read(self.workspace / "policy.json")

    def persist(self):
        write(self.path, self.data)

    def audit(self, action, expense_id=None, status="ok"):
        # No credentials or raw request body are logged.
        row = {"time": datetime.now(timezone.utc).isoformat(), "action": action,
               "expense_id": expense_id, "status": status, "simulation": True}
        with (self.workspace / "audit.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    def item(self, expense_id):
        return next((x for x in self.data["expenses"] if x["id"] == expense_id), None)

    def precheck(self, expense_id):
        item = self.item(expense_id)
        if item is None:
            return 404, {"error": "expense_not_found"}
        answer = precheck(item, self.data["expenses"], self.policy)
        return 200, {"expense_id": expense_id, "policy_version": self.policy["version"], **answer}

    def add_review(self, expense_id, payload, key):
        if not key or len(key) > 128:
            return 400, {"error": "idempotency_key_required"}
        if not isinstance(payload, dict) or set(payload) != {"decision", "rule", "policy_version"}:
            return 400, {"error": "review_fields_invalid"}
        fingerprint = sha256(json.dumps({"expense_id": expense_id, "payload": payload},
                                       sort_keys=True).encode()).hexdigest()
        previous = self.data["idempotency"].get(key)
        if previous:
            if previous["fingerprint"] != fingerprint:
                return 409, {"error": "idempotency_conflict"}
            self.audit("review.replay", expense_id)
            return 200, {**previous["response"], "replayed": True}
        code, expected = self.precheck(expense_id)
        if code != 200:
            return code, expected
        if any(payload[k] != expected[k] for k in payload):
            return 409, {"error": "review_does_not_match_current_policy"}
        if any(r["expense_id"] == expense_id and r["policy_version"] == self.policy["version"]
               for r in self.data["reviews"]):
            return 409, {"error": "review_already_exists_for_policy"}
        review = {"review_id": f"V{len(self.data['reviews']) + 1:04}",
                  "expense_id": expense_id, **payload, "simulation": True}
        response = {"review": review, "replayed": False}
        self.data["reviews"].append(review)
        self.data["idempotency"][key] = {"fingerprint": fingerprint, "response": response}
        self.persist()
        self.audit("review.create", expense_id)
        return 201, response


def handler_for(state):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def send(self, code, payload):
            body = json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def dispatch(self):
            with WRITE_LOCK:
                try:
                    code, response = self.route()
                except (ValueError, KeyError, TypeError):
                    code, response = 400, {"error": "invalid_request"}
                self.send(code, response)

        def route(self):
            path = urlparse(self.path).path
            if path == "/health" and self.command == "GET":
                return 200, {"status": "ok", "simulation": True}
            if self.headers.get("Authorization") != "Bearer " + state.data["training_token"]:
                state.audit("auth", status="denied")
                return 401, {"error": "training_auth_required"}
            if path == "/expenses" and self.command == "GET":
                state.audit("expense.list")
                return 200, {"simulation": True, "items": state.data["expenses"]}
            if path == "/reviews" and self.command == "GET":
                return 200, {"simulation": True, "items": state.data["reviews"]}
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "expenses" and parts[2] == "precheck" and self.command == "GET":
                state.audit("expense.precheck", parts[1])
                return state.precheck(parts[1])
            if len(parts) == 3 and parts[0] == "expenses" and parts[2] == "reviews" and self.command == "POST":
                # Service-side enforcement, even if a caller bypasses the CLI.
                if self.headers.get("X-Training-Write") != "yes":
                    return 403, {"error": "training_write_ack_required"}
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 8192:
                    return 400, {"error": "body_size_invalid"}
                payload = json.loads(self.rfile.read(length))
                return state.add_review(parts[1], payload, self.headers.get("Idempotency-Key"))
            return 404, {"error": "route_not_found"}

        do_GET = dispatch
        do_POST = dispatch
    return Handler


def request(base, path, token, method="GET", payload=None, key=None):
    parsed = urlparse(base)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.path not in ("", "/"):
        raise ValueError("训练 CLI 仅允许 http://127.0.0.1:PORT，不接入生产系统。")
    headers = {"Authorization": "Bearer " + token}
    if payload is not None:
        headers.update({"Content-Type": "application/json", "Idempotency-Key": key or "",
                        "X-Training-Write": "yes"})
    req = Request(base.rstrip("/") + path,
                  data=None if payload is None else json.dumps(payload).encode(),
                  headers=headers, method=method)
    try:
        with urlopen(req, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        try:
            return error.code, json.load(error)
        finally:
            error.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="OpenFDE 本地模拟报销实验；无模型调用、审批或付款。")
    parser.add_argument("--version", action="version", version="enterprise-lab 1.0")
    sub = parser.add_subparsers(dest="command", required=True)
    initialize = sub.add_parser("init", help="在新目录创建虚构数据；拒绝覆盖")
    initialize.add_argument("--workspace", required=True)
    serve = sub.add_parser("serve", help="仅监听本机的模拟 API")
    serve.add_argument("--workspace", required=True)
    serve.add_argument("--port", type=int, default=8765)
    evaluate_parser = sub.add_parser("eval", help="离线运行规则评测")
    evaluate_parser.add_argument("--workspace", required=True)
    evaluate_parser.add_argument("--cases", type=Path, default=ASSETS / "evals.json")
    evaluate_parser.add_argument("--variant", choices=["current", "boundary-bug"], default="current")
    evaluate_parser.add_argument("--output", type=Path, required=True)
    for name in ["list", "precheck", "write-review", "reviews"]:
        cmd = sub.add_parser(name)
        cmd.add_argument("--base-url", default="http://127.0.0.1:8765")
        if name in ["precheck", "write-review"]:
            cmd.add_argument("--id", required=True)
        if name == "write-review":
            cmd.add_argument("--payload", type=Path, required=True)
            cmd.add_argument("--idempotency-key", required=True)
            cmd.add_argument("--confirm-training-write", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            path = Path(args.workspace).resolve()
            path.mkdir(parents=True, exist_ok=False)
            try:
                os.chmod(path, 0o700)
                write(path / "state.json", {"training_token": "training-only", "expenses": read(ASSETS / "expenses.json"),
                                           "reviews": [], "idempotency": {}})
                shutil.copyfile(ASSETS / "policy.json", path / "policy.json")
            except Exception:
                print("初始化中断，保留工作目录，请检查后选择新目录。", file=sys.stderr)
                raise
            print(json.dumps({"workspace": str(path), "simulation": True}, ensure_ascii=False))
        elif args.command == "serve":
            state = LabState(args.workspace)
            server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(state))
            print(f"SIMULATION http://127.0.0.1:{server.server_port}", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
        elif args.command == "eval":
            state = LabState(args.workspace)
            report = evaluate(state.data["expenses"], state.policy, read(args.cases), args.variant)
            write(args.output, report)
            print(json.dumps({k: v for k, v in report.items() if k != "cases"}, ensure_ascii=False))
            return 1 if report["failed"] else 0
        else:
            token = os.environ.get("FDE_LAB_TOKEN", "")
            if args.command == "write-review" and not args.confirm_training_write:
                print("只允许确认后的本地模拟写入；未发送请求。", file=sys.stderr)
                return 2
            path = {"list": "/expenses", "reviews": "/reviews"}.get(args.command)
            if path is None:
                suffix = "precheck" if args.command == "precheck" else "reviews"
                if not args.id.isalnum():
                    raise ValueError("expense id must be alphanumeric")
                path = f"/expenses/{args.id}/{suffix}"
            code, payload = request(args.base_url, path, token,
                                    method="POST" if args.command == "write-review" else "GET",
                                    payload=read(args.payload) if args.command == "write-review" else None,
                                    key=args.idempotency_key if args.command == "write-review" else None)
            print(json.dumps({"http_status": code, **payload}, ensure_ascii=False, indent=2))
            return 0 if code < 400 else 1
    except (OSError, ValueError, KeyError, URLError) as error:
        print(f"实验失败：{type(error).__name__}: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
