"""omne reset — re-stamp manifest and re-seed cfg/log without touching image/core."""

import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "docs" / "manifest-template.md"


def _read_frontmatter_field(path: Path, field: str) -> str:
    """Read a single frontmatter field from a markdown file."""
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip()
    return ""


def reset(root: Path | None = None) -> None:
    """Re-stamp manifest and re-seed cfg/log from distro defaults."""
    if root is None:
        root = Path.cwd()

    omne = root / ".omne"
    if not omne.is_dir():
        print("Error: .omne/ not found", file=sys.stderr)
        sys.exit(1)

    image = omne / "image"
    system_md = image / "SYSTEM.md"

    # Read distro info from SYSTEM.md
    distro = _read_frontmatter_field(system_md, "distro") or "unknown"
    version = _read_frontmatter_field(system_md, "distro-version") or "0.0.0"
    volume_name = root.name

    # Re-stamp manifest
    today = date.today().isoformat()
    text = _TEMPLATE_PATH.read_text(encoding="utf-8")
    text = text.replace("{{volume}}", volume_name)
    text = text.replace("{{distro}}", distro)
    text = text.replace("{{distro-version}}", version)
    text = text.replace("{{created}}", today)
    (omne / "MANIFEST.md").write_text(text, encoding="utf-8")

    # Re-seed cfg/ from defaults (if present)
    defaults = image / "defaults"
    cfg = omne / "cfg"
    if defaults.is_dir():
        for src in defaults.rglob("*"):
            if src.is_file():
                rel = src.relative_to(defaults)
                dest = cfg / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)

    # Re-seed log/ subdirs
    log = omne / "log"
    log_dirs_raw = _read_frontmatter_field(system_md, "log-dirs")
    if log_dirs_raw.startswith("[") and log_dirs_raw.endswith("]"):
        for d in log_dirs_raw[1:-1].split(","):
            d = d.strip()
            if d:
                (log / d).mkdir(parents=True, exist_ok=True)

    print("Reset complete — manifest re-stamped, cfg/log re-seeded.")


def main() -> None:
    reset()


if __name__ == "__main__":
    main()
