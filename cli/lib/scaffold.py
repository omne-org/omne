"""Volume directory scaffolding."""

from pathlib import Path

BOOTLOADER_CONTENT = """\
# CLAUDE.md

> Bootloader — loads the omne kernel.

Read `.omne/MANIFEST.md` and follow its boot sequence.
"""


def create_volume_dirs(root: Path) -> None:
    """Create .omne/ directory structure with cfg/ and log/."""
    omne = root / ".omne"
    omne.mkdir(exist_ok=True)
    (omne / "cfg").mkdir(exist_ok=True)
    (omne / "log").mkdir(exist_ok=True)


def write_bootloader(root: Path) -> None:
    """Write CLAUDE.md bootloader to volume root."""
    (root / "CLAUDE.md").write_text(BOOTLOADER_CONTENT, encoding="utf-8")


def write_manifest(root: Path, content: str) -> None:
    """Write stamped manifest to .omne/MANIFEST.md."""
    (root / ".omne" / "MANIFEST.md").write_text(content, encoding="utf-8")
