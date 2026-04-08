"""Tests for cli/lib/volume.py."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cli"))

from lib.volume import find_omne_root, is_mounted


class TestFindOmneRoot(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_finds_root_when_omne_exists(self):
        (self.tmpdir / ".omne").mkdir()
        result = find_omne_root(self.tmpdir)
        self.assertEqual(result, self.tmpdir)

    def test_finds_root_from_subdirectory(self):
        (self.tmpdir / ".omne").mkdir()
        child = self.tmpdir / "src" / "deep"
        child.mkdir(parents=True)
        result = find_omne_root(child)
        self.assertEqual(result, self.tmpdir)

    def test_returns_none_when_not_found(self):
        result = find_omne_root(self.tmpdir)
        self.assertIsNone(result)


class TestIsMounted(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.omne = self.tmpdir / ".omne"
        self.omne.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_returns_false_when_no_gitmodules(self):
        self.assertFalse(is_mounted(self.omne))

    def test_returns_false_when_gitmodules_has_no_image(self):
        (self.tmpdir / ".gitmodules").write_text("[submodule \"other\"]\n\tpath = other\n")
        self.assertFalse(is_mounted(self.omne))

    def test_returns_true_when_gitmodules_has_image(self):
        (self.tmpdir / ".gitmodules").write_text(
            '[submodule ".omne/image"]\n\tpath = .omne/image\n\turl = https://example.com\n'
        )
        self.assertTrue(is_mounted(self.omne))


if __name__ == "__main__":
    unittest.main()
