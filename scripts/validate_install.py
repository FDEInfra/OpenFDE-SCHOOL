#!/usr/bin/env python3
"""Exercise real Git installs and migration with local remotes; no network needed."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = "https://github.com/FDEInfra/OpenFDE-SCHOOL.git"
LEGACY = "https://github.com/Alan-Youngzhe/OpenFDE-School.git"
REAL_GIT = shutil.which("git")
SHELLS = []
if os.name != "nt" and shutil.which("bash"):
    SHELLS.append([shutil.which("bash"), str(ROOT / "scripts/install.sh")])
if shutil.which("pwsh"):
    SHELLS.append([shutil.which("pwsh"), "-NoProfile", "-File", str(ROOT / "scripts/install.ps1")])

# Only clone/pull are mapped. The installer still sees and changes real origin URLs.
WRAPPER = r'''import os, subprocess, sys
args = sys.argv[1:]
git = os.environ["INSTALL_TEST_GIT"]
remote = os.environ["INSTALL_TEST_REMOTE"]
known = {
    "https://github.com/FDEInfra/OpenFDE-SCHOOL.git",
    "https://github.com/Alan-Youngzhe/OpenFDE-School.git",
    "git@github.com:Alan-Youngzhe/OpenFDE-School.git",
    "ssh://git@github.com/Alan-Youngzhe/OpenFDE-School.git",
}
if args and args[0] == "clone":
    url, target = args[-2:]
    if url not in known:
        sys.exit("Unexpected clone URL: " + url)
    result = subprocess.run([git, *args[:-2], remote, target])
    if result.returncode:
        sys.exit(result.returncode)
    sys.exit(subprocess.call([git, "-C", target, "remote", "set-url", "origin", url]))
if args and args[-1] == "--ff-only" and "pull" in args:
    prefix = args[:args.index("pull")]
    url = subprocess.check_output([git, *prefix, "remote", "get-url", "origin"], text=True).strip()
    if url not in known:
        sys.exit("Unexpected pull URL: " + url)
    sys.exit(subprocess.call([git, "-c", "url." + remote + ".insteadOf=" + url, *args]))
sys.exit(subprocess.call([git, *args]))
'''


class InstallerTests(unittest.TestCase):
    shell: list[str]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="openfde-install-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.upstream = self.root / "upstream"
        self.remote = self.root / "remote.git"
        self.target = self.root / "skills" / "fde"
        self.env = os.environ.copy()
        for key in list(self.env):
            if key.startswith("GIT_") or key.startswith("OPENFDE_SCHOOL_"):
                self.env.pop(key)
        self.env.update({
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "Installer Test",
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Installer Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "GIT_TERMINAL_PROMPT": "0",
            "OPENFDE_SCHOOL_DIR": str(self.target),
        })
        self.git("init", "-b", "main", str(self.upstream))
        (self.upstream / "scripts").mkdir()
        (self.upstream / "SKILL.md").write_text("fixture\n", encoding="utf-8")
        (self.upstream / "scripts/validate_school.py").write_text("print('fixture validated')\n", encoding="utf-8")
        self.git("-C", str(self.upstream), "add", ".")
        self.git("-C", str(self.upstream), "commit", "-m", "Initial fixture")
        self.git("clone", "--bare", str(self.upstream), str(self.remote))
        self.git("-C", str(self.upstream), "remote", "add", "origin", str(self.remote))
        shim = self.root / "bin"
        shim.mkdir()
        wrapper = shim / "git-wrapper.py"
        wrapper.write_text(WRAPPER, encoding="utf-8")
        if os.name == "nt":
            (shim / "git.cmd").write_text(f'@"{sys.executable}" "{wrapper}" %*\n', encoding="utf-8")
        else:
            command = shim / "git"
            command.write_text(f'#!{sys.executable}\n' + WRAPPER, encoding="utf-8")
            command.chmod(0o755)
        self.env.update({
            "PATH": str(shim) + os.pathsep + self.env["PATH"],
            "INSTALL_TEST_GIT": REAL_GIT,
            "INSTALL_TEST_REMOTE": self.remote.as_uri(),
        })

    def git(self, *args):
        return subprocess.check_output([REAL_GIT, *args], env=self.env, stderr=subprocess.STDOUT, text=True).strip()

    def checkout(self, origin=CANONICAL):
        self.target.parent.mkdir(parents=True, exist_ok=True)
        self.git("clone", str(self.remote), str(self.target))
        self.git("-C", str(self.target), "remote", "set-url", "origin", origin)

    def advance(self):
        (self.upstream / "lesson.md").write_text("New lesson\n", encoding="utf-8")
        self.git("-C", str(self.upstream), "add", ".")
        self.git("-C", str(self.upstream), "commit", "-m", "Add lesson")
        self.git("-C", str(self.upstream), "push", "origin", "main")

    def install(self, success=True):
        result = subprocess.run(self.shell, env=self.env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("fixture validated", result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result.stdout

    def origin(self):
        return self.git("-C", str(self.target), "remote", "get-url", "origin")

    def test_fresh_install(self):
        self.install()
        self.assertEqual(self.origin(), CANONICAL)
        self.assertTrue((self.target / "SKILL.md").is_file())

    def test_clean_update(self):
        self.checkout()
        self.advance()
        self.install()
        self.assertEqual(self.git("-C", str(self.target), "rev-parse", "HEAD"),
                         self.git("-C", str(self.upstream), "rev-parse", "HEAD"))

    def test_legacy_migration(self):
        self.checkout(LEGACY)
        self.advance()
        for origin in [LEGACY, "git@github.com:Alan-Youngzhe/OpenFDE-School.git",
                       "ssh://git@github.com/Alan-Youngzhe/OpenFDE-School.git"]:
            with self.subTest(origin=origin):
                self.git("-C", str(self.target), "remote", "set-url", "origin", origin)
                self.install()
                self.assertEqual(self.origin(), CANONICAL)
                self.assertTrue((self.target / "lesson.md").is_file())

    def test_dirty_legacy_preserves_files_and_origin(self):
        self.checkout(LEGACY)
        (self.target / "SKILL.md").write_text("My local changes\n", encoding="utf-8")
        self.install(success=False)
        self.assertEqual(self.origin(), LEGACY)
        self.assertEqual((self.target / "SKILL.md").read_text(encoding="utf-8"), "My local changes\n")

    def test_untracked_files_preserved(self):
        self.checkout(LEGACY)
        (self.target / "notes.md").write_text("My notes\n", encoding="utf-8")
        self.install(success=False)
        self.assertEqual(self.origin(), LEGACY)
        self.assertEqual((self.target / "notes.md").read_text(encoding="utf-8"), "My notes\n")

    def test_unrelated_repository_rejected(self):
        url = "https://github.com/example/other.git"
        self.checkout(url)
        self.install(success=False)
        self.assertEqual(self.origin(), url)

    def test_non_git_directory_preserved(self):
        self.target.mkdir(parents=True)
        (self.target / "notes.md").write_text("Keep me\n", encoding="utf-8")
        self.install(success=False)
        self.assertEqual((self.target / "notes.md").read_text(encoding="utf-8"), "Keep me\n")

    def test_diverged_history_preserved(self):
        self.checkout()
        (self.target / "local.md").write_text("Local work\n", encoding="utf-8")
        self.git("-C", str(self.target), "add", ".")
        self.git("-C", str(self.target), "commit", "-m", "Local work")
        head = self.git("-C", str(self.target), "rev-parse", "HEAD")
        self.advance()
        self.install(success=False)
        self.assertEqual(self.git("-C", str(self.target), "rev-parse", "HEAD"), head)
        self.assertTrue((self.target / "local.md").is_file())


if __name__ == "__main__":
    if not REAL_GIT or not SHELLS:
        sys.exit("Requires Git and Bash (Unix) or PowerShell 7.")
    suite = unittest.TestSuite()
    for shell in SHELLS:
        cls = type(Path(shell[0]).stem + "InstallerTests", (InstallerTests,), {"shell": shell})
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
