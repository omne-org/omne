"""Tests for cli/upgrade.py."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cli"))

from upgrade import upgrade


def _create_fake_distro(tmpdir: Path) -> str:
    """Create a git repo mimicking a distro. Returns file:// URL."""
    distro = tmpdir / "fake-distro"
    distro.mkdir()
    (distro / "agents").mkdir()
    (distro / "skills").mkdir()
    (distro / "hooks").mkdir()
    (distro / "context-map.md").write_text("# Context Map\n")
    (distro / "SYSTEM.md").write_text("---\ndistro-version: 0.1.0\n---\n# SYSTEM\n")
    # Add .gitkeep files so git tracks empty dirs
    for d in ["agents", "skills", "hooks"]:
        (distro / d / ".gitkeep").write_text("")
    env = {
        **__import__("os").environ,
        "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t",
    }
    subprocess.run(["git", "init"], cwd=str(distro), capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=str(distro), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "v1"], cwd=str(distro), capture_output=True, check=True, env=env)
    return f"file:///{distro.as_posix()}"


def _init_embedded_volume(tmpdir: Path, distro_url: str) -> Path:
    """Create a volume with embedded image, return volume root."""
    from init import init
    volume = tmpdir / "my-app"
    volume.mkdir()
    subprocess.run(["git", "init"], cwd=str(volume), capture_output=True, check=True)
    init(distro_url, mounted=False, root=volume)
    return volume


class TestUpgradeEmbedded(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.distro_url = _create_fake_distro(self.tmpdir)
        self.volume = _init_embedded_volume(self.tmpdir, self.distro_url)

        # Now update the distro repo (add a new file)
        distro_path = self.tmpdir / "fake-distro"
        (distro_path / "new-skill.md").write_text("# New\n")
        env = {
            **__import__("os").environ,
            "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t",
        }
        subprocess.run(["git", "add", "."], cwd=str(distro_path), capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "v2"], cwd=str(distro_path), capture_output=True, check=True, env=env)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_upgrade_pulls_new_files(self):
        self.assertFalse((self.volume / ".omne" / "image" / "new-skill.md").exists())
        upgrade(self.volume)
        self.assertTrue((self.volume / ".omne" / "image" / "new-skill.md").exists())

    def test_cfg_untouched(self):
        (self.volume / ".omne" / "cfg" / "test.md").write_text("keep me\n")
        upgrade(self.volume)
        self.assertEqual(
            (self.volume / ".omne" / "cfg" / "test.md").read_text(), "keep me\n"
        )

    def test_log_untouched(self):
        (self.volume / ".omne" / "log" / "session.md").write_text("log data\n")
        upgrade(self.volume)
        self.assertEqual(
            (self.volume / ".omne" / "log" / "session.md").read_text(), "log data\n"
        )


class TestUpgradeNoVolume(unittest.TestCase):
    def test_fails_without_omne_dir(self):
        tmpdir = Path(tempfile.mkdtemp())
        try:
            with self.assertRaises(SystemExit):
                upgrade(tmpdir)
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
