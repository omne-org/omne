"""omne validate — check volume integrity."""

import re
import sys
from pathlib import Path

REQUIRED_DIRS = ["image", "cfg", "log"]
REQUIRED_IMAGE_DIRS = ["agents", "skills", "hooks"]
REQUIRED_IMAGE_FILES = ["context-map.md", "SYSTEM.md"]
REQUIRED_MANIFEST_FIELDS = ["volume", "distro", "distro-version", "created"]
MAX_DEPTH = 2  # max directory levels below .omne/ (e.g. cfg/subdir is OK, cfg/sub1/sub2 is not)


def _check_dirs(omne: Path) -> list[str]:
    """Check required directories exist under .omne/."""
    issues = []
    for d in REQUIRED_DIRS:
        if not (omne / d).is_dir():
            issues.append(f"missing required directory: .omne/{d}/")
    return issues


def _check_image(image: Path) -> list[str]:
    """Check image/ has required contents."""
    issues = []
    if not image.is_dir():
        return issues  # already caught by _check_dirs
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

    # Extract YAML frontmatter
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
        depth = len(relative.parts)
        if depth > MAX_DEPTH:
            issues.append(
                f"depth violation ({depth} > {MAX_DEPTH}): .omne/{relative}"
            )
    return issues


def validate(root: Path) -> list[str]:
    """Validate volume integrity. Returns list of issue strings (empty = valid)."""
    omne = root / ".omne"
    if not omne.is_dir():
        return [".omne/ not found — not an omne volume"]

    issues = []
    issues.extend(_check_dirs(omne))
    issues.extend(_check_image(omne / "image"))
    issues.extend(_check_manifest(omne))
    issues.extend(_check_depth(omne))
    return issues


def main() -> None:
    root = Path.cwd()
    issues = validate(root)
    if issues:
        print("Validation failed:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    print("Volume is valid.")


if __name__ == "__main__":
    main()
