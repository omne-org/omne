"""Manifest template loading and stamping."""

from datetime import date
from pathlib import Path

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent / "manifest-template.md"


def load_template() -> str:
    """Read the manifest template from disk."""
    return _TEMPLATE_PATH.read_text(encoding="utf-8")


def stamp(volume: str, distro: str, version: str) -> str:
    """Stamp the manifest template with concrete values."""
    today = date.today().isoformat()
    text = load_template()
    text = text.replace("{{volume}}", volume)
    text = text.replace("{{distro}}", distro)
    text = text.replace("{{distro-version}}", version)
    text = text.replace("{{created}}", today)
    return text
