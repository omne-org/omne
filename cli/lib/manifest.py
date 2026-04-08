"""Manifest template loading, stamping, and image introspection."""

import re
from datetime import date
from pathlib import Path

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "manifest-template.md"


def load_template() -> str:
    """Read the manifest template from disk."""
    return _TEMPLATE_PATH.read_text(encoding="utf-8")


def introspect_image(image_dir: Path) -> dict[str, str]:
    """Introspect an installed distro image and return markdown sections.

    Returns dict with keys: 'stages', 'agents', 'context_routing'.
    Each value is a markdown string ready to insert into the manifest.
    """
    result = {"stages": "", "agents": "", "context_routing": ""}

    system_md = image_dir / "SYSTEM.md"
    if system_md.is_file():
        text = system_md.read_text(encoding="utf-8", errors="replace")

        # Extract ## Stages section (the full table)
        m = re.search(r"(## Stages\s*\n.*?)(?=\n## |\Z)", text, re.DOTALL)
        if m:
            # Return just the table rows, not the heading (the manifest already has ## Stages)
            section = m.group(1)
            lines = section.splitlines()
            table_lines = [l for l in lines if l.startswith("|") or l.startswith("-")]
            if table_lines:
                result["stages"] = "\n".join(table_lines)

        # Extract ## Agents section
        m = re.search(r"## Agents\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
        if m:
            result["agents"] = m.group(1).strip()

    # Context routing: reference the file
    context_map = image_dir / "context-map.md"
    if context_map.is_file():
        result["context_routing"] = "See `image/context-map.md` for which agent reads what."

    return result


def stamp(
    volume: str,
    distro: str,
    version: str,
    stages: str = "",
    agents: str = "",
    context_routing: str = "",
) -> str:
    """Stamp the manifest template with concrete values."""
    today = date.today().isoformat()
    text = load_template()
    text = text.replace("{{volume}}", volume)
    text = text.replace("{{distro}}", distro)
    text = text.replace("{{distro-version}}", version)
    text = text.replace("{{created}}", today)
    text = text.replace("{{stages}}", stages or "Declared by distro, listed here for agent discoverability.")
    text = text.replace("{{agents}}", agents or "Summary of available agents and their roles (populated from `image/`).")
    text = text.replace("{{context-routing}}", context_routing or "See `image/context-map.md` for which agent reads what.")
    return text
