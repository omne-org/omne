"""Tests for cli/lib/manifest.py."""

import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cli"))

from lib.manifest import load_template, stamp


class TestLoadTemplate(unittest.TestCase):
    def test_returns_string(self):
        result = load_template()
        self.assertIsInstance(result, str)

    def test_contains_placeholders(self):
        result = load_template()
        self.assertIn("{{volume}}", result)
        self.assertIn("{{distro}}", result)
        self.assertIn("{{distro-version}}", result)
        self.assertIn("{{created}}", result)


class TestStamp(unittest.TestCase):
    def test_replaces_all_placeholders(self):
        result = stamp("my-app", "omne-faber", "1.0.0")
        self.assertNotIn("{{", result)
        self.assertNotIn("}}", result)

    def test_contains_volume_name(self):
        result = stamp("my-app", "omne-faber", "1.0.0")
        self.assertIn("my-app", result)

    def test_contains_distro_name(self):
        result = stamp("my-app", "omne-faber", "1.0.0")
        self.assertIn("omne-faber", result)

    def test_contains_version(self):
        result = stamp("my-app", "omne-faber", "1.0.0")
        self.assertIn("1.0.0", result)

    def test_contains_today_date(self):
        result = stamp("my-app", "omne-faber", "1.0.0")
        self.assertIn(date.today().isoformat(), result)

    def test_has_yaml_frontmatter(self):
        result = stamp("my-app", "omne-faber", "1.0.0")
        self.assertTrue(result.startswith("---\n"))


if __name__ == "__main__":
    unittest.main()
