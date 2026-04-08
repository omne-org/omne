"""omne upgrade — update distro image and kernel to latest."""

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


def _read_origin_url(target: Path) -> str | None:
    """Read the clone URL from .omne-origin file."""
    origin_file = target / ".omne-origin"
    if origin_file.is_file():
        return origin_file.read_text(encoding="utf-8").strip()
    return None


def upgrade(root: Path | None = None) -> None:
    """Upgrade the distro image and kernel to latest."""
    if root is None:
        root = Path.cwd()

    omne = root / ".omne"
    if not omne.is_dir():
        print("Error: .omne/ not found", file=sys.stderr)
        sys.exit(1)

    image = omne / "image"
    core = omne / "core"

    if is_mounted(omne):
        # Mounted mode: update submodules independently
        print("Upgrading (mounted mode)...")
        subprocess.run(
            ["git", "submodule", "update", "--remote", ".omne/image"],
            cwd=str(root), check=True,
        )
        gitmodules = root / ".gitmodules"
        if gitmodules.is_file() and ".omne/core" in gitmodules.read_text(encoding="utf-8"):
            subprocess.run(
                ["git", "submodule", "update", "--remote", ".omne/core"],
                cwd=str(root), check=True,
            )
        print("Upgrade complete (submodules updated).")
    else:
        # Embedded mode: re-clone and replace independently
        image_url = _read_origin_url(image)
        if image_url is None:
            print("Error: cannot determine distro URL (no .omne/image/.omne-origin)", file=sys.stderr)
            sys.exit(1)

        print(f"Upgrading (embedded mode)...")
        with tempfile.TemporaryDirectory() as tmp:
            # Replace image/
            tmp_distro = Path(tmp) / "distro"
            subprocess.run(
                ["git", "-c", "protocol.file.allow=always",
                 "clone", image_url, str(tmp_distro)],
                check=True,
            )
            subprocess.run(_rmtree_cmd() + [str(image)], check=True)
            shutil.copytree(
                tmp_distro, image,
                ignore=shutil.ignore_patterns(".git", "core"),
            )
            (image / ".omne-origin").write_text(image_url, encoding="utf-8")

            # Replace core/ (if origin is known)
            core_url = _read_origin_url(core) if core.is_dir() else None
            if core_url:
                tmp_kernel = Path(tmp) / "kernel"
                subprocess.run(
                    ["git", "-c", "protocol.file.allow=always",
                     "clone", core_url, str(tmp_kernel)],
                    check=True,
                )
                subprocess.run(_rmtree_cmd() + [str(core)], check=True)
                shutil.copytree(
                    tmp_kernel, core,
                    ignore=shutil.ignore_patterns(".git"),
                )
                (core / ".omne-origin").write_text(core_url, encoding="utf-8")

        print("Upgrade complete (image and core replaced).")


def main() -> None:
    upgrade()


if __name__ == "__main__":
    main()
