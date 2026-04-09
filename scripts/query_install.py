"""Query omne installation info from manifest.json files."""

from __future__ import annotations

import json
from pathlib import Path


def _read_manifest(path: Path) -> dict | None:
    """Read a manifest.json, return None if missing or invalid."""
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def query_installation(root: Path) -> dict:
    """Read kernel and distro manifests, return combined info.

    Returns:
        {"kernel": {...} | None, "distro": {...} | None}
    """
    omne = root / ".omne"
    kernel = _read_manifest(omne / "core" / "manifest.json")
    distro = _read_manifest(omne / "image" / "manifest.json")
    return {"kernel": kernel, "distro": distro}


def format_installation(info: dict) -> str:
    """Format installation info as human-readable text."""
    lines = []
    k = info.get("kernel")
    if k:
        lines.append(f"Kernel: {k.get('name', '?')} v{k.get('version', '?')}")
    else:
        lines.append("Kernel: not installed")

    d = info.get("distro")
    if d:
        lines.append(f"Distro: {d.get('name', '?')} v{d.get('version', '?')}")
        if d.get("domain"):
            lines.append(f"Domain: {d['domain']}")
    else:
        lines.append("Distro: not installed")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    root = Path.cwd()
    info = query_installation(root)
    print(format_installation(info))
