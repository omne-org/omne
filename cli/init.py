"""omne init — scaffold a new volume with a distro."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.distro import parse_distro
from lib.manifest import stamp
from lib.scaffold import create_volume_dirs, write_bootloader, write_manifest


def _read_distro_version(image_dir: Path) -> str:
    """Try to read distro-version from image/SYSTEM.md frontmatter."""
    system_md = image_dir / "SYSTEM.md"
    if not system_md.is_file():
        return "0.0.0"
    content = system_md.read_text(encoding="utf-8")
    for line in content.splitlines():
        if line.startswith("distro-version:"):
            return line.split(":", 1)[1].strip()
    return "0.0.0"


def init(distro_spec: str, mounted: bool = False, root: Path | None = None) -> None:
    """Initialize an omne volume."""
    if root is None:
        root = Path.cwd()

    omne = root / ".omne"
    if omne.exists():
        print("Error: .omne/ already exists", file=sys.stderr)
        sys.exit(1)

    url, name = parse_distro(distro_spec)

    # Create directory structure
    create_volume_dirs(root)

    # Install image
    image = omne / "image"
    if mounted:
        subprocess.run(
            ["git", "-c", "protocol.file.allow=always", "submodule", "add", url, ".omne/image"],
            cwd=str(root), check=True,
        )
    else:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_clone = Path(tmp) / "distro"
            subprocess.run(
                ["git", "clone", url, str(tmp_clone)],
                check=True,
            )
            shutil.copytree(
                tmp_clone, image,
                ignore=shutil.ignore_patterns(".git"),
                dirs_exist_ok=True,
            )
            # Record origin URL for upgrade
            (image / ".omne-origin").write_text(url, encoding="utf-8")

    # Stamp and write manifest
    version = _read_distro_version(image)
    volume_name = root.name
    manifest_content = stamp(volume_name, name, version)
    write_manifest(root, manifest_content)

    # Write bootloader
    write_bootloader(root)

    print(f"Initialized omne volume '{volume_name}' with distro '{name}' ({'mounted' if mounted else 'embedded'})")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Initialize an omne volume")
    parser.add_argument("distro", help="Distro specifier (e.g. omne-org/omne-faber)")
    parser.add_argument("--mounted", action="store_true", help="Use submodule (mounted) mode")
    args = parser.parse_args()
    init(args.distro, args.mounted)


if __name__ == "__main__":
    main()
