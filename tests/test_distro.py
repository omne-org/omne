"""Tests for cli/lib/distro.py."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cli"))

from lib.distro import parse_distro


class TestParseDistro(unittest.TestCase):
    def test_full_spec_with_org(self):
        url, name = parse_distro("omne-org/omne-faber")
        self.assertEqual(url, "https://github.com/omne-org/omne-faber.git")
        self.assertEqual(name, "omne-faber")

    def test_bare_name_defaults_to_omne_org(self):
        url, name = parse_distro("omne-liber")
        self.assertEqual(url, "https://github.com/omne-org/omne-liber.git")
        self.assertEqual(name, "omne-liber")

    def test_full_url_passthrough(self):
        url, name = parse_distro("https://github.com/myorg/my-distro.git")
        self.assertEqual(url, "https://github.com/myorg/my-distro.git")
        self.assertEqual(name, "my-distro")

    def test_ssh_url_passthrough(self):
        url, name = parse_distro("git@github.com:omne-org/omne-faber.git")
        self.assertEqual(url, "git@github.com:omne-org/omne-faber.git")
        self.assertEqual(name, "omne-faber")

    def test_strips_trailing_dotgit(self):
        url, name = parse_distro("omne-org/omne-faber")
        self.assertEqual(name, "omne-faber")

    def test_different_org(self):
        url, name = parse_distro("acme-corp/omne-custom")
        self.assertEqual(url, "https://github.com/acme-corp/omne-custom.git")
        self.assertEqual(name, "omne-custom")


if __name__ == "__main__":
    unittest.main()
