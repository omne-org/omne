"""Tests for cli/omne.py — CLI dispatch."""

import subprocess
import sys
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parent.parent / "cli" / "omne.py"


class TestCLIDispatch(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            capture_output=True, text=True,
        )

    def test_no_args_shows_usage(self):
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("usage" in result.stderr.lower() or "usage" in result.stdout.lower())

    def test_help_flag(self):
        result = self._run("--help")
        self.assertEqual(result.returncode, 0)
        output = result.stdout.lower()
        self.assertIn("init", output)
        self.assertIn("upgrade", output)
        self.assertIn("validate", output)
        self.assertIn("remove", output)
        self.assertIn("reset", output)

    def test_validate_in_non_volume(self):
        result = self._run("validate")
        self.assertNotEqual(result.returncode, 0)

    def test_unknown_command(self):
        result = self._run("foobar")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
