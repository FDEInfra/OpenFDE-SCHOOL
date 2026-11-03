#!/usr/bin/env python3
"""Exercise the bundled lab's business rules, HTTP behavior and write boundaries."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets/enterprise-lab"
spec = importlib.util.spec_from_file_location("enterprise_lab", ASSETS / "lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class EnterpriseLabTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.workspace = Path(self.directory.name) / "workspace"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(lab.main(["init", "--workspace", str(self.workspace)]), 0)
        self.state = lab.LabState(self.workspace)

    def start_server(self):
        server = lab.ThreadingHTTPServer(("127.0.0.1", 0), lab.handler_for(self.state))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def cleanup():
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        self.addCleanup(cleanup)
        return f"http://127.0.0.1:{server.server_port}"

    def test_rule_evaluation(self):
        answer = lab.evaluate(self.state.data["expenses"], self.state.policy, lab.read(ASSETS / "evals.json"))
        self.assertEqual((answer["passed"], answer["failed"]), (12, 0))
        self.assertEqual(set(answer["groups"]), {"direct", "clarify", "partial", "cannot_process"})

    def test_mutation_is_detected(self):
        answer = lab.evaluate(self.state.data["expenses"], self.state.policy, lab.read(ASSETS / "evals.json"), "boundary-bug")
        self.assertEqual({x["id"] for x in answer["cases"] if not x["passed"]}, {"C002", "C011"})

    def test_boolean_is_not_a_valid_amount(self):
        item = dict(self.state.data["expenses"][0], amount_cents=True)
        self.assertEqual(lab.precheck(item, [], self.state.policy)["rule"], "invalid_amount")

    def test_untrusted_note_does_not_change_policy(self):
        code, answer = self.state.precheck("E012")
        self.assertEqual(code, 200)
        self.assertEqual(answer["decision"], "manual_review")
        self.assertFalse(answer["approval"])
        self.assertFalse(answer["payment"])

    def test_init_refuses_overwrite(self):
        before = self.state.path.read_bytes()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertNotEqual(lab.main(["init", "--workspace", str(self.workspace)]), 0)
        self.assertEqual(self.state.path.read_bytes(), before)

    def test_auth_is_required(self):
        base = self.start_server()
        self.assertEqual(lab.request(base, "/expenses", "wrong")[0], 401)

    def test_read_chain(self):
        base = self.start_server()
        code, answer = lab.request(base, "/expenses", "training-only")
        self.assertEqual((code, len(answer["items"])), (200, 12))
        self.assertEqual(lab.request(base, "/expenses/E003/precheck", "training-only")[1]["rule"], "over_limit")
        self.assertEqual(lab.request(base, "/expenses/UNKNOWN/precheck", "training-only")[0], 404)

    def test_write_lifecycle_and_conflicts(self):
        base = self.start_server()
        payload = {"decision": "manual_review", "rule": "over_limit", "policy_version": "training-1"}
        path = "/expenses/E003/reviews"
        code, first = lab.request(base, path, "training-only", "POST", payload, "batch-1-E003")
        self.assertEqual(code, 201)
        self.assertFalse(first["replayed"])
        code, second = lab.request(base, path, "training-only", "POST", payload, "batch-1-E003")
        self.assertEqual(code, 200)
        self.assertTrue(second["replayed"])
        self.assertEqual(first["review"]["review_id"], second["review"]["review_id"])
        self.assertEqual(lab.request(base, path, "training-only", "POST", payload, "other-key")[0], 409)
        self.assertEqual(lab.request(base, path, "training-only", "POST", dict(payload, rule="within_limit"), "batch-1-E003")[0], 409)
        self.assertEqual(len(lab.LabState(self.workspace).data["reviews"]), 1)

    def test_server_rejects_forged_outcome(self):
        base = self.start_server()
        payload = {"decision": "ready_for_review", "rule": "within_limit", "policy_version": "training-1"}
        code, answer = lab.request(base, "/expenses/E003/reviews", "training-only", "POST", payload, "forged")
        self.assertEqual((code, answer["error"]), (409, "review_does_not_match_current_policy"))
        self.assertEqual(self.state.data["reviews"], [])

    def test_server_requires_training_ack(self):
        base = self.start_server()
        request = Request(base + "/expenses/E003/reviews", data=b"{}", method="POST",
                          headers={"Authorization": "Bearer training-only"})
        with self.assertRaises(HTTPError) as result:
            urlopen(request, timeout=3)
        self.assertEqual(result.exception.code, 403)
        result.exception.close()

    def test_cli_without_ack_sends_no_write(self):
        payload = self.workspace / "payload.json"
        lab.write(payload, {"decision": "manual_review", "rule": "over_limit", "policy_version": "training-1"})
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(lab.main(["write-review", "--id", "E003", "--payload", str(payload),
                                       "--idempotency-key", "no-ack"]), 2)
        self.assertEqual(self.state.data["reviews"], [])

    def test_nonlocal_url_rejected(self):
        with self.assertRaises(ValueError):
            lab.request("https://example.com", "/expenses", "training-only")

    def test_audit_contains_no_token(self):
        base = self.start_server()
        lab.request(base, "/expenses", "training-only")
        text = (self.workspace / "audit.jsonl").read_text()
        self.assertIn("expense.list", text)
        self.assertNotIn("training-only", text)

    def test_eval_command_writes_failure_report(self):
        output = self.workspace / "baseline.json"
        with redirect_stdout(io.StringIO()):
            code = lab.main(["eval", "--workspace", str(self.workspace), "--variant", "boundary-bug", "--output", str(output)])
        self.assertEqual(code, 1)
        self.assertEqual(lab.read(output)["failed"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
