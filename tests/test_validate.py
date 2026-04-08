"""Tests for cli/validate.py."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cli"))

from validate import validate

MINIMAL_MANIFEST = """\
---
volume: test
distro: omne-faber
distro-version: 1.0.0
created: 2026-01-01
---

# MANIFEST
"""


def _make_valid_volume(root: Path) -> None:
    """Create a minimal valid volume for testing."""
    omne = root / ".omne"
    omne.mkdir()
    (omne / "cfg").mkdir()
    (omne / "log").mkdir()
    image = omne / "image"
    image.mkdir()
    (image / "agents").mkdir()
    (image / "skills").mkdir()
    (image / "hooks").mkdir()
    (image / "context-map.md").write_text("# Context Map\n")
    (image / "SYSTEM.md").write_text("# SYSTEM\n")
    (omne / "MANIFEST.md").write_text(MINIMAL_MANIFEST)


class TestValidate(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_valid_volume_no_issues(self):
        _make_valid_volume(self.tmpdir)
        issues = validate(self.tmpdir)
        self.assertEqual(issues, [])

    def test_missing_omne_dir(self):
        issues = validate(self.tmpdir)
        self.assertTrue(any(".omne/ not found" in i for i in issues))

    def test_missing_cfg(self):
        _make_valid_volume(self.tmpdir)
        import shutil
        shutil.rmtree(self.tmpdir / ".omne" / "cfg")
        issues = validate(self.tmpdir)
        self.assertTrue(any("cfg/" in i for i in issues))

    def test_missing_log(self):
        _make_valid_volume(self.tmpdir)
        import shutil
        shutil.rmtree(self.tmpdir / ".omne" / "log")
        issues = validate(self.tmpdir)
        self.assertTrue(any("log/" in i for i in issues))

    def test_missing_image(self):
        _make_valid_volume(self.tmpdir)
        import shutil
        shutil.rmtree(self.tmpdir / ".omne" / "image")
        issues = validate(self.tmpdir)
        self.assertTrue(any("image/" in i for i in issues))

    def test_missing_manifest(self):
        _make_valid_volume(self.tmpdir)
        (self.tmpdir / ".omne" / "MANIFEST.md").unlink()
        issues = validate(self.tmpdir)
        self.assertTrue(any("MANIFEST.md" in i for i in issues))

    def test_manifest_missing_field(self):
        _make_valid_volume(self.tmpdir)
        (self.tmpdir / ".omne" / "MANIFEST.md").write_text("---\nvolume: test\n---\n")
        issues = validate(self.tmpdir)
        self.assertTrue(any("distro" in i for i in issues))

    def test_depth_violation(self):
        _make_valid_volume(self.tmpdir)
        deep = self.tmpdir / ".omne" / "cfg" / "sub1" / "sub2"
        deep.mkdir(parents=True)
        issues = validate(self.tmpdir)
        self.assertTrue(any("depth" in i.lower() for i in issues))

    def test_missing_image_agents(self):
        _make_valid_volume(self.tmpdir)
        import shutil
        shutil.rmtree(self.tmpdir / ".omne" / "image" / "agents")
        issues = validate(self.tmpdir)
        self.assertTrue(any("agents/" in i for i in issues))

    def test_missing_image_system_md(self):
        _make_valid_volume(self.tmpdir)
        (self.tmpdir / ".omne" / "image" / "SYSTEM.md").unlink()
        issues = validate(self.tmpdir)
        self.assertTrue(any("SYSTEM.md" in i for i in issues))

    def test_missing_image_context_map(self):
        _make_valid_volume(self.tmpdir)
        (self.tmpdir / ".omne" / "image" / "context-map.md").unlink()
        issues = validate(self.tmpdir)
        self.assertTrue(any("context-map.md" in i for i in issues))


if __name__ == "__main__":
    unittest.main()
