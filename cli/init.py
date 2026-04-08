"""omne init — scaffold a new volume with a distro."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.distro import parse_distro
from lib.manifest import introspect_image, stamp

_DEFAULT_KERNEL_URL = "https://github.com/omne-org/omne.git"

BOOTLOADER_CONTENT = """\
# CLAUDE.md

> Bootloader — loads the omne kernel.

Read `.omne/MANIFEST.md` and follow its boot sequence.
"""


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


def _read_kernel_url(image_dir: Path) -> str:
    """Read kernel-url from SYSTEM.md frontmatter, or return default."""
    system_md = image_dir / "SYSTEM.md"
    if not system_md.is_file():
        return _DEFAULT_KERNEL_URL
    content = system_md.read_text(encoding="utf-8")
    for line in content.splitlines():
        if line.startswith("kernel-url:"):
            return line.split(":", 1)[1].strip()
    return _DEFAULT_KERNEL_URL


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
    omne.mkdir(exist_ok=True)
    (omne / "cfg").mkdir(exist_ok=True)
    (omne / "log").mkdir(exist_ok=True)

    image = omne / "image"
    core = omne / "core"

    if mounted:
        # Two independent submodule adds
        subprocess.run(
            ["git", "-c", "protocol.file.allow=always",
             "submodule", "add", url, ".omne/image"],
            cwd=str(root), check=True,
        )
        kernel_url = _read_kernel_url(image)
        subprocess.run(
            ["git", "-c", "protocol.file.allow=always",
             "submodule", "add", kernel_url, ".omne/core"],
            cwd=str(root), check=True,
        )
    else:
        # Two independent clones — no --recurse-submodules, no split-copy
        with tempfile.TemporaryDirectory() as tmp:
            # Clone distro -> image/
            tmp_distro = Path(tmp) / "distro"
            subprocess.run(
                ["git", "-c", "protocol.file.allow=always",
                 "clone", url, str(tmp_distro)],
                check=True,
            )
            shutil.copytree(
                tmp_distro, image,
                ignore=shutil.ignore_patterns(".git", "core"),
                dirs_exist_ok=True,
            )
            # Record distro origin URL for upgrade
            (image / ".omne-origin").write_text(url, encoding="utf-8")

            # Clone kernel -> core/
            kernel_url = _read_kernel_url(image)
            tmp_kernel = Path(tmp) / "kernel"
            subprocess.run(
                ["git", "-c", "protocol.file.allow=always",
                 "clone", kernel_url, str(tmp_kernel)],
                check=True,
            )
            shutil.copytree(
                tmp_kernel, core,
                ignore=shutil.ignore_patterns(".git"),
                dirs_exist_ok=True,
            )
            # Record kernel origin URL for upgrade
            (core / ".omne-origin").write_text(kernel_url, encoding="utf-8")

    # Seed cfg/ from distro defaults (if present)
    defaults = image / "defaults"
    cfg = omne / "cfg"
    if defaults.is_dir():
        for src in defaults.rglob("*"):
            if src.is_file():
                rel = src.relative_to(defaults)
                dest = cfg / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)

    # Seed log/ subdirectories from SYSTEM.md log-dirs field
    log = omne / "log"
    system_md = image / "SYSTEM.md"
    if system_md.is_file():
        for line in system_md.read_text(encoding="utf-8").splitlines():
            if line.startswith("log-dirs:"):
                raw = line.split(":", 1)[1].strip()
                if raw.startswith("[") and raw.endswith("]"):
                    for d in raw[1:-1].split(","):
                        d = d.strip()
                        if d:
                            (log / d).mkdir(parents=True, exist_ok=True)
                break

    # Introspect the installed distro and stamp manifest
    version = _read_distro_version(image)
    volume_name = root.name
    intro = introspect_image(image)
    manifest_content = stamp(
        volume_name, name, version,
        stages=intro["stages"],
        agents=intro["agents"],
        context_routing=intro["context_routing"],
    )
    (omne / "MANIFEST.md").write_text(manifest_content, encoding="utf-8")

    # Write bootloader
    (root / "CLAUDE.md").write_text(BOOTLOADER_CONTENT, encoding="utf-8")

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
