"""Tests for cli/lib/scaffold.py."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cli"))

from lib.scaffold import create_volume_dirs, write_bootloader, write_manifest


class TestCreateVolumeDirs(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_creates_omne_dir(self):
        create_volume_dirs(self.tmpdir)
        self.assertTrue((self.tmpdir / ".omne").is_dir())

    def test_creates_cfg_dir(self):
        create_volume_dirs(self.tmpdir)
        self.assertTrue((self.tmpdir / ".omne" / "cfg").is_dir())

    def test_creates_log_dir(self):
        create_volume_dirs(self.tmpdir)
        self.assertTrue((self.tmpdir / ".omne" / "log").is_dir())

    def test_idempotent(self):
        create_volume_dirs(self.tmpdir)
        create_volume_dirs(self.tmpdir)
        self.assertTrue((self.tmpdir / ".omne").is_dir())


class TestWriteBootloader(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_creates_claude_md(self):
        write_bootloader(self.tmpdir)
        self.assertTrue((self.tmpdir / "CLAUDE.md").is_file())

    def test_references_manifest(self):
        write_bootloader(self.tmpdir)
        content = (self.tmpdir / "CLAUDE.md").read_text()
        self.assertIn(".omne/MANIFEST.md", content)


class TestWriteManifest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / ".omne").mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_writes_manifest_file(self):
        write_manifest(self.tmpdir, "test content")
        path = self.tmpdir / ".omne" / "MANIFEST.md"
        self.assertTrue(path.is_file())
        self.assertEqual(path.read_text(), "test content")


if __name__ == "__main__":
    unittest.main()
