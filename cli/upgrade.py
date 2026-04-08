"""omne upgrade — update distro image to latest."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LIB = Path(__file__).resolve().parent / "lib"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.volume import is_mounted


def _rmtree_cmd() -> list[str]:
    """Return platform-appropriate rmtree command."""
    if sys.platform == "win32":
        return ["pwsh", "-NoProfile", "-File", str(LIB / "rmtree.ps1")]
    return [str(LIB / "rmtree.sh")]


def _read_origin_url(image: Path) -> str | None:
    """Read the distro clone URL from .omne-origin file."""
    origin_file = image / ".omne-origin"
    if origin_file.is_file():
        return origin_file.read_text(encoding="utf-8").strip()
    return None


def upgrade(root: Path | None = None) -> None:
    """Upgrade the distro image to latest."""
    if root is None:
        root = Path.cwd()

    omne = root / ".omne"
    if not omne.is_dir():
        print("Error: .omne/ not found", file=sys.stderr)
        sys.exit(1)

    image = omne / "image"

    if is_mounted(omne):
        # Mounted mode: submodule update
        print("Upgrading (mounted mode)...")
        subprocess.run(
            ["git", "submodule", "update", "--remote", ".omne/image"],
            cwd=str(root), check=True,
        )
        print("Upgrade complete (submodule updated).")
    else:
        # Embedded mode: re-clone and replace
        origin_url = _read_origin_url(image)
        if origin_url is None:
            print("Error: cannot determine distro URL for upgrade (no .omne-origin file)", file=sys.stderr)
            sys.exit(1)

        print(f"Upgrading (embedded mode) from {origin_url}...")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_clone = Path(tmp) / "distro"
            subprocess.run(
                ["git", "clone", origin_url, str(tmp_clone)],
                check=True,
            )
            # Remove old image
            subprocess.run(_rmtree_cmd() + [str(image)], check=True)
            # Copy new image
            shutil.copytree(
                tmp_clone, image,
                ignore=shutil.ignore_patterns(".git"),
            )
            # Re-write origin file
            (image / ".omne-origin").write_text(origin_url, encoding="utf-8")
        print("Upgrade complete (image replaced).")


def main() -> None:
    upgrade()


if __name__ == "__main__":
    main()
