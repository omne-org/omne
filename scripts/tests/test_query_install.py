"""Tests for scripts/query_install.py."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from query_install import query_installation


class TestQueryInstallation(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.omne = self.tmpdir / ".omne"
        self.omne.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_returns_kernel_version(self):
        core = self.omne / "core"
        core.mkdir()
        (core / "manifest.json").write_text(
            json.dumps({"name": "omne", "version": "0.2.0", "gate_runner": "tools/inspect_tool.py"}),
            encoding="utf-8",
        )
        result = query_installation(self.tmpdir)
        self.assertEqual(result["kernel"]["version"], "0.2.0")

    def test_returns_distro_version(self):
        core = self.omne / "core"
        core.mkdir()
        (core / "manifest.json").write_text(
            json.dumps({"name": "omne", "version": "0.2.0", "gate_runner": "tools/inspect_tool.py"}),
            encoding="utf-8",
        )
        image = self.omne / "image"
        image.mkdir()
        (image / "manifest.json").write_text(
            json.dumps({"name": "omne-nosce", "version": "0.1.0", "domain": "org-governance"}),
            encoding="utf-8",
        )
        result = query_installation(self.tmpdir)
        self.assertEqual(result["distro"]["version"], "0.1.0")
        self.assertEqual(result["distro"]["name"], "omne-nosce")

    def test_missing_core_manifest(self):
        result = query_installation(self.tmpdir)
        self.assertIsNone(result["kernel"])

    def test_missing_image_manifest(self):
        core = self.omne / "core"
        core.mkdir()
        (core / "manifest.json").write_text(
            json.dumps({"name": "omne", "version": "0.2.0", "gate_runner": "tools/inspect_tool.py"}),
            encoding="utf-8",
        )
        result = query_installation(self.tmpdir)
        self.assertIsNone(result["distro"])


if __name__ == "__main__":
    unittest.main()
