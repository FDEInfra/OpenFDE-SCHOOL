#!/usr/bin/env python3
"""Validate the OpenFDE School skill package without network access."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifest.json"
REQUIRED = {
    ".github/ISSUE_TEMPLATE/join-wall.yml",
    ".github/pull_request_template.md",
    ".github/workflows/validate.yml",
    "LICENSE",
    "SKILL.md",
    "WALL.md",
    "agents/openai.yaml",
    "references/catalog.md",
    "references/lessons/shared/safety-and-secrets.md",
    "references/lessons/shared/evidence-card.md",
    "references/pedagogy.md",
    "references/state-schema.md",
    "references/sources.md",
    "references/lab-guide.md",
    "references/coverage.md",
    "assets/enterprise-lab/lab.py",
    "assets/enterprise-lab/expenses.json",
    "assets/enterprise-lab/policy.json",
    "assets/enterprise-lab/evals.json",
    "assets/expense-precheck-lab/SKILL.md",
    "assets/templates/expense-sow.md",
    "assets/templates/expense-spec.md",
    "assets/templates/expense-runbook.md",
    "assets/templates/portfolio-case.md",
    "assets/templates/demo-rubric.md",
    "scripts/install.ps1",
    "scripts/install.sh",
    "scripts/validate_wall.py",
    "scripts/validate_lab.py",
}
COURSE_IDS = [
    "fde-landscape",
    "scope-cli-prototype",
    "skills-in-enterprise",
    "cli-enterprise-integration",
    "evals-to-production",
    "demoday",
    "fde-career",
]
SECRET_PATTERNS = {
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub classic token": re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
}
LINK_RE = re.compile(r"\]\(([^)]+)\)")
CODE_PATH_RE = re.compile(r"`((?:\.\.?/|references/|assets/|scripts/)[^`\s]+\.(?:md|json|py))`")
PRIVATE_SOURCE_RE = re.compile(r"逐字稿|(?:^|/)(?:transcripts?|raw-sources?)(?:/|$)", re.I)
PUBLISH_METHOD_PHRASES = [
    "~/.claude/skills/fde",
    "git pull --ff-only",
    "python3 scripts/validate_wall.py",
]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def validate_manifest(failures: list[str]) -> set[str]:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"manifest.json cannot be read: {exc}", failures)
        return set()

    version = data.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail("manifest version must use MAJOR.MINOR.PATCH", failures)

    files = data.get("files")
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        fail("manifest files must be a string list", failures)
        return set()

    listed = set(files)
    if len(listed) != len(files):
        fail("manifest files must not contain duplicate entries", failures)
    safe_listed = set()
    for path in sorted(listed):
        relative = PurePosixPath(path)
        if (relative.is_absolute() or ".." in relative.parts or "\\" in path
                or str(relative) != path or not relative.parts):
            fail(f"manifest path must be a normalized relative path: {path}", failures)
            continue
        resolved = (ROOT / path).resolve()
        if not resolved.is_relative_to(ROOT.resolve()):
            fail(f"manifest path escapes skill root: {path}", failures)
            continue
        safe_listed.add(path)
    listed = safe_listed
    for path in sorted(REQUIRED - listed):
        fail(f"required file is not listed in manifest: {path}", failures)
    for path in sorted(listed):
        if not (ROOT / path).is_file():
            fail(f"manifest points to missing file: {path}", failures)

    packaged = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and path.name != "manifest.json"
        and path.relative_to(ROOT).parts[0] != "work"
    }
    for path in sorted(packaged - listed):
        fail(f"packaged file is missing from manifest: {path}", failures)
    for path in sorted(listed - packaged):
        fail(f"manifest lists a non-packaged file: {path}", failures)
    for path in sorted(packaged):
        if PRIVATE_SOURCE_RE.search(path):
            fail(f"private source material must not be packaged: {path}", failures)
    return listed


def validate_skill(failures: list[str]) -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\nname: fde\n"):
        fail("SKILL.md frontmatter or name is invalid", failures)
    if "description:" not in text.split("---", 2)[1]:
        fail("SKILL.md is missing its description", failures)
    for course_id in COURSE_IDS:
        course_file = f"references/courses/{course_id}.md"
        if course_file not in text:
            fail(f"course is not routed in SKILL.md: {course_id}", failures)
        if not (ROOT / course_file).is_file():
            fail(f"routed course file is missing: {course_file}", failures)

    publishing_text = (ROOT / "README.md").read_text(encoding="utf-8") + (
        ROOT / "WALL.md"
    ).read_text(encoding="utf-8")
    for phrase in PUBLISH_METHOD_PHRASES:
        if phrase not in publishing_text:
            fail(f"publishing requirement is missing: {phrase}", failures)


def validate_markdown(listed: set[str], failures: list[str]) -> None:
    for relative in sorted(listed):
        path = ROOT / relative
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                fail(f"possible {label} in {relative}", failures)
        if path.suffix != ".md":
            continue
        if "[TODO" in text or "TODO:" in text:
            fail(f"placeholder remains in {relative}", failures)
        for target in LINK_RE.findall(text):
            clean = unquote(target.split("#", 1)[0].strip().strip("<>"))
            if not clean or clean.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / clean).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                fail(f"relative link escapes skill root in {relative}: {target}", failures)
                continue
            if not resolved.exists():
                fail(f"broken relative link in {relative}: {target}", failures)
        for target in CODE_PATH_RE.findall(text):
            if "*" in target:
                continue
            if target.startswith(("references/", "assets/", "scripts/")):
                resolved = ROOT / target
            else:
                resolved = path.parent / target
            if not resolved.resolve().is_relative_to(ROOT.resolve()):
                fail(f"referenced resource path escapes skill root in {relative}: {target}", failures)
            elif not resolved.is_file():
                fail(f"broken referenced resource path in {relative}: {target}", failures)


def validate_lesson_routes(failures: list[str]) -> None:
    """Every lesson must be discoverable from its owning course or the skill."""
    routed: set[Path] = set()
    for course_id in COURSE_IDS:
        course = ROOT / "references/courses" / f"{course_id}.md"
        if not course.is_file():
            continue
        content = course.read_text(encoding="utf-8")
        lessons = []
        for target in CODE_PATH_RE.findall(content):
            resolved = ((ROOT if target.startswith(("references/", "assets/", "scripts/")) else course.parent)
                        / target).resolve()
            if resolved.parent == (ROOT / "references/lessons" / course_id).resolve():
                routed.add(resolved)
                lessons.append(resolved)
        if re.search(r"^状态：alpha\b", content, re.M) and not lessons:
            fail(f"alpha course has no routed lessons: {course_id}", failures)
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for lesson in (ROOT / "references/lessons").rglob("*.md"):
        relative = lesson.relative_to(ROOT).as_posix()
        if lesson.parent.name == "shared":
            if relative not in skill:
                fail(f"shared lesson is not routed in SKILL.md: {relative}", failures)
        elif lesson.resolve() not in routed:
            fail(f"lesson is not routed from its course: {relative}", failures)


def main() -> int:
    failures: list[str] = []
    listed = validate_manifest(failures)
    validate_skill(failures)
    validate_markdown(listed, failures)
    validate_lesson_routes(failures)

    if failures:
        print("OpenFDE School validation failed:")
        for item in failures:
            print(f"- {item}")
        return 1

    print(f"OpenFDE School validation passed: {len(listed)} packaged files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
