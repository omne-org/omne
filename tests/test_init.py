"""Tests for cli/init.py — integration tests using local git repos."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cli"))

from init import init


def _create_fake_distro(tmpdir: Path) -> str:
    """Create a bare git repo mimicking a distro. Returns file:// URL."""
    distro = tmpdir / "fake-distro"
    distro.mkdir()
    (distro / "agents").mkdir()
    (distro / "skills").mkdir()
    (distro / "hooks").mkdir()
    (distro / "agents" / ".gitkeep").write_text("")
    (distro / "skills" / ".gitkeep").write_text("")
    (distro / "hooks" / ".gitkeep").write_text("")
    (distro / "context-map.md").write_text("# Context Map\n")
    (distro / "SYSTEM.md").write_text("---\ndistro-version: 0.1.0\n---\n# SYSTEM\n")
    env = {**__import__("os").environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "init"], cwd=str(distro), capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=str(distro), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(distro), capture_output=True, check=True, env=env)
    return f"file:///{distro.as_posix()}"


class TestInitEmbedded(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.distro_url = _create_fake_distro(self.tmpdir)
        self.volume = self.tmpdir / "my-app"
        self.volume.mkdir()
        subprocess.run(["git", "init"], cwd=str(self.volume), capture_output=True, check=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_creates_omne_dir(self):
        init(self.distro_url, mounted=False, root=self.volume)
        self.assertTrue((self.volume / ".omne").is_dir())

    def test_creates_cfg_and_log(self):
        init(self.distro_url, mounted=False, root=self.volume)
        self.assertTrue((self.volume / ".omne" / "cfg").is_dir())
        self.assertTrue((self.volume / ".omne" / "log").is_dir())

    def test_copies_image(self):
        init(self.distro_url, mounted=False, root=self.volume)
        image = self.volume / ".omne" / "image"
        self.assertTrue(image.is_dir())
        self.assertTrue((image / "agents").is_dir())
        self.assertTrue((image / "SYSTEM.md").is_file())
        self.assertTrue((image / "context-map.md").is_file())

    def test_image_has_no_dotgit(self):
        init(self.distro_url, mounted=False, root=self.volume)
        self.assertFalse((self.volume / ".omne" / "image" / ".git").exists())

    def test_writes_manifest(self):
        init(self.distro_url, mounted=False, root=self.volume)
        manifest = self.volume / ".omne" / "MANIFEST.md"
        self.assertTrue(manifest.is_file())
        content = manifest.read_text()
        self.assertIn("my-app", content)

    def test_writes_bootloader(self):
        init(self.distro_url, mounted=False, root=self.volume)
        self.assertTrue((self.volume / "CLAUDE.md").is_file())

    def test_fails_if_omne_exists(self):
        (self.volume / ".omne").mkdir()
        with self.assertRaises(SystemExit):
            init(self.distro_url, mounted=False, root=self.volume)


class TestInitMounted(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.distro_url = _create_fake_distro(self.tmpdir)
        self.volume = self.tmpdir / "my-app"
        self.volume.mkdir()
        subprocess.run(["git", "init"], cwd=str(self.volume), capture_output=True, check=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_creates_submodule(self):
        init(self.distro_url, mounted=True, root=self.volume)
        self.assertTrue((self.volume / ".gitmodules").is_file())
        content = (self.volume / ".gitmodules").read_text()
        self.assertIn(".omne/image", content)

    def test_image_dir_exists(self):
        init(self.distro_url, mounted=True, root=self.volume)
        self.assertTrue((self.volume / ".omne" / "image").is_dir())


if __name__ == "__main__":
    unittest.main()
