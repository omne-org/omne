"""Volume detection helpers."""

from pathlib import Path


def find_omne_root(start: Path) -> Path | None:
    """Walk up from start to find a directory containing .omne/."""
    current = start.resolve()
    while True:
        if (current / ".omne").is_dir():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def is_mounted(omne_dir: Path) -> bool:
    """Check if .omne/image is a git submodule (mounted mode)."""
    gitmodules = omne_dir.parent / ".gitmodules"
    if not gitmodules.exists():
        return False
    content = gitmodules.read_text(encoding="utf-8")
    return ".omne/image" in content
