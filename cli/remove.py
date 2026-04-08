"""omne remove — tear down an omne volume."""

import subprocess
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent / "lib"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.volume import is_mounted


def _rmtree_cmd() -> list[str]:
    """Return platform-appropriate rmtree command."""
    if sys.platform == "win32":
        return ["pwsh", "-NoProfile", "-File", str(LIB / "rmtree.ps1")]
    return [str(LIB / "rmtree.sh")]


def remove(root: Path | None = None) -> None:
    """Remove the omne volume from a repo."""
    if root is None:
        root = Path.cwd()

    omne = root / ".omne"
    if not omne.is_dir():
        print("Error: .omne/ not found", file=sys.stderr)
        sys.exit(1)

    if is_mounted(omne):
        # Clean up submodules first
        for sub in (".omne/image", ".omne/core"):
            gitmodules = root / ".gitmodules"
            if gitmodules.is_file() and sub in gitmodules.read_text(encoding="utf-8"):
                subprocess.run(
                    ["git", "submodule", "deinit", "-f", sub],
                    cwd=str(root), check=False,
                )
                subprocess.run(
                    ["git", "rm", "-f", sub],
                    cwd=str(root), check=False,
                )

    # Remove .omne/ directory
    subprocess.run(_rmtree_cmd() + [str(omne)], check=True)

    # Remove bootloader
    bootloader = root / "CLAUDE.md"
    if bootloader.is_file():
        bootloader.unlink()

    print("Removed omne volume.")


def main() -> None:
    remove()


if __name__ == "__main__":
    main()
