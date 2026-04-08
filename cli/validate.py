"""omne validate — check volume integrity and distro compliance."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.inspect import inspect_distro

# ---------------------------------------------------------------------------
# Volume-level constants
# ---------------------------------------------------------------------------

REQUIRED_DIRS = ["image", "cfg", "log"]
REQUIRED_IMAGE_DIRS = ["agents", "skills", "hooks"]
REQUIRED_IMAGE_FILES = ["context-map.md", "SYSTEM.md"]
REQUIRED_MANIFEST_FIELDS = ["volume", "distro", "distro-version", "created"]
MAX_DEPTH = 2


# ---------------------------------------------------------------------------
# Volume-level checks
# ---------------------------------------------------------------------------

def _check_dirs(omne: Path) -> list[str]:
    """Check required directories exist under .omne/."""
    issues = []
    for d in REQUIRED_DIRS:
        if not (omne / d).is_dir():
            issues.append(f"missing required directory: .omne/{d}/")
    return issues


def _check_core(omne: Path) -> list[str]:
    """Check core/ — warn if missing, validate contents if present."""
    core = omne / "core"
    if not core.is_dir():
        return ["warning: .omne/core/ not found (kernel not installed in volume)"]
    issues = []
    if not (core / "cli" / "omne.py").is_file():
        issues.append("core/ missing required file: core/cli/omne.py")
    return issues


def _check_image(image: Path) -> list[str]:
    """Check image/ has required contents."""
    issues = []
    if not image.is_dir():
        return issues
    for d in REQUIRED_IMAGE_DIRS:
        if not (image / d).is_dir():
            issues.append(f"missing required image directory: image/{d}/")
    for f in REQUIRED_IMAGE_FILES:
        if not (image / f).is_file():
            issues.append(f"missing required image file: image/{f}")
    return issues


def _check_manifest(omne: Path) -> list[str]:
    """Check MANIFEST.md exists and has required frontmatter fields."""
    manifest = omne / "MANIFEST.md"
    if not manifest.is_file():
        return ["missing MANIFEST.md"]

    content = manifest.read_text(encoding="utf-8")
    issues = []

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return ["MANIFEST.md has no YAML frontmatter (---...---)"]

    frontmatter = match.group(1)
    for field in REQUIRED_MANIFEST_FIELDS:
        pattern = rf"^{re.escape(field)}\s*:"
        if not re.search(pattern, frontmatter, re.MULTILINE):
            issues.append(f"MANIFEST.md missing required field: {field}")

    return issues


def _check_depth(omne: Path) -> list[str]:
    """Check no directory under .omne/ exceeds MAX_DEPTH levels deep."""
    issues = []
    omne_resolved = omne.resolve()
    for path in omne.rglob("*"):
        if not path.is_dir():
            continue
        relative = path.resolve().relative_to(omne_resolved)
        # Exempt core/ (kernel repo) and image/ (distro — has its own depth enforcement)
        if relative.parts and relative.parts[0] in ("core", "image"):
            continue
        depth = len(relative.parts)
        if depth > MAX_DEPTH:
            issues.append(
                f"depth violation ({depth} > {MAX_DEPTH}): .omne/{relative}"
            )
    return issues


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate(root: Path) -> list[str]:
    """Validate volume integrity. Returns list of issue strings (empty = valid)."""
    omne = root / ".omne"
    if not omne.is_dir():
        return [".omne/ not found — not an omne volume"]

    issues = []
    issues.extend(_check_dirs(omne))
    issues.extend(_check_image(omne / "image"))
    issues.extend(_check_core(omne))
    issues.extend(_check_manifest(omne))
    issues.extend(_check_depth(omne))
    return issues


def validate_distro(root: Path) -> dict[str, list[str]]:
    """Run distro quality gate checks against the installed image."""
    image = root / ".omne" / "image"
    if not image.is_dir():
        return {"structural": [".omne/image/ not found"]}
    return inspect_distro(image)


def main() -> None:
    root = Path.cwd()

    # Layer 1: Volume checks
    issues = validate(root)
    warnings = [i for i in issues if i.startswith("warning:")]
    errors = [i for i in issues if not i.startswith("warning:")]

    if errors:
        print("Volume validation failed:")
        for issue in errors:
            print(f"  {issue}")
        for w in warnings:
            print(f"  {w}")
        sys.exit(1)

    print("[volume] PASS")
    for w in warnings:
        print(f"  {w}")

    # Layer 2: Distro checks
    image = root / ".omne" / "image"
    if not image.is_dir():
        print("[distro] SKIP — no image/ found")
        return

    results = inspect_distro(image)
    any_fail = False
    for gate, gate_issues in results.items():
        if gate_issues:
            print(f"[distro] FAIL [{gate}]")
            for issue in gate_issues:
                print(f"  - {issue}")
            any_fail = True
        else:
            print(f"[distro] PASS [{gate}]")

    if any_fail:
        sys.exit(1)

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
