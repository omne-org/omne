"""Distro quality gate checks — validates distro image compliance.

Moved from omne-nosce/tools/inspect_tool.py into the kernel so any
distro can be validated without needing a specific distro installed.
"""

from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_frontmatter(path: Path) -> dict[str, str]:
    """Extract YAML frontmatter as a flat dict from a markdown file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}

    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}

    result: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def _list_md_names(directory: Path) -> list[str]:
    """Return the ``name`` frontmatter values for all .md files in *directory*."""
    names: list[str] = []
    if not directory.is_dir():
        return names
    for md in directory.glob("*.md"):
        fm = _parse_frontmatter(md)
        if "name" in fm:
            names.append(fm["name"])
    return names


def _extract_stages_from_system(system_path: Path) -> list[str]:
    """Parse stage names from the ## Stages table in SYSTEM.md."""
    if not system_path.is_file():
        return []
    text = system_path.read_text(encoding="utf-8", errors="replace")
    stages_match = re.search(r"## Stages\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not stages_match:
        return []
    section = stages_match.group(1)
    stages: list[str] = []
    for line in section.splitlines():
        m = re.match(r"^\|\s*(\w[\w-]*)", line)
        if m:
            name = m.group(1)
            if name.lower() != "stage":  # skip header row
                stages.append(name)
    return stages


# ---------------------------------------------------------------------------
# Gate 1 — Structural
# ---------------------------------------------------------------------------

_SKIP_DIRS = {".git", "__pycache__", "defaults", "tools", "tests"}


def check_structural(target: Path) -> list[str]:
    """Check required dirs/files exist, dirs are non-empty, max depth 2."""
    issues: list[str] = []

    for dirname in ("agents", "skills", "hooks"):
        d = target / dirname
        if not d.is_dir():
            issues.append(f"Missing required directory: {dirname}/")
        elif not any(d.iterdir()):
            issues.append(f"Required directory is empty: {dirname}/")

    for fname in ("context-map.md", "SYSTEM.md"):
        if not (target / fname).is_file():
            issues.append(f"Missing required file: {fname}")

    for path in target.rglob("*"):
        rel = path.relative_to(target)
        if any(part.startswith(".") or part in _SKIP_DIRS for part in rel.parts):
            continue
        depth = len(rel.parts)
        if depth > 2:
            issues.append(f"Depth violation (max 2 levels): {rel}")

    return issues


# ---------------------------------------------------------------------------
# Gate 2 — System
# ---------------------------------------------------------------------------

def check_system(target: Path) -> list[str]:
    """Validate SYSTEM.md frontmatter, required sections, and agent listing."""
    issues: list[str] = []
    system_path = target / "SYSTEM.md"

    if not system_path.is_file():
        issues.append("SYSTEM.md not found")
        return issues

    text = system_path.read_text(encoding="utf-8", errors="replace")
    fm = _parse_frontmatter(system_path)

    if not fm:
        issues.append("SYSTEM.md: missing frontmatter block")
        return issues

    for key in ("distro", "distro-version", "domain"):
        if key not in fm:
            issues.append(f"SYSTEM.md frontmatter missing key: {key}")

    if "## Agents" not in text:
        issues.append("SYSTEM.md: missing ## Agents section")
    if "## Stages" not in text:
        issues.append("SYSTEM.md: missing ## Stages section")

    agent_names = _list_md_names(target / "agents")
    agents_section = ""
    m = re.search(r"## Agents\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if m:
        agents_section = m.group(1)

    for name in agent_names:
        if name not in agents_section:
            issues.append(f"SYSTEM.md ## Agents: agent '{name}' not listed")

    return issues


# ---------------------------------------------------------------------------
# Gate 3 — Coverage
# ---------------------------------------------------------------------------

def check_coverage(target: Path) -> list[str]:
    """Check every agent name appears in context-map.md."""
    issues: list[str] = []
    context_map = target / "context-map.md"

    if not context_map.is_file():
        issues.append("context-map.md not found")
        return issues

    cm_text = context_map.read_text(encoding="utf-8", errors="replace")
    agent_names = _list_md_names(target / "agents")

    for name in agent_names:
        if name not in cm_text:
            issues.append(f"context-map.md: agent '{name}' not mentioned")

    return issues


# ---------------------------------------------------------------------------
# Gate 4 — Stages
# ---------------------------------------------------------------------------

def check_stages(target: Path) -> list[str]:
    """Validate ## Stages table has required columns and non-empty rows."""
    issues: list[str] = []
    system_path = target / "SYSTEM.md"

    if not system_path.is_file():
        issues.append("SYSTEM.md not found")
        return issues

    text = system_path.read_text(encoding="utf-8", errors="replace")

    if "## Stages" not in text:
        issues.append("SYSTEM.md: missing ## Stages section")
        return issues

    m = re.search(r"## Stages\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not m:
        issues.append("SYSTEM.md: could not parse ## Stages section")
        return issues

    section = m.group(1)
    required_columns = ("Stage", "Entry Gate", "Artifacts", "Exit Gate")

    header_match = re.search(r"\|(.+)\|", section)
    if not header_match:
        issues.append("SYSTEM.md ## Stages: no table header found")
        return issues

    header = header_match.group(1)
    for col in required_columns:
        if col not in header:
            issues.append(f"SYSTEM.md ## Stages: missing column '{col}'")

    stage_names = _extract_stages_from_system(system_path)
    if not stage_names:
        issues.append("SYSTEM.md ## Stages: table has no data rows (empty stage list)")

    return issues


# ---------------------------------------------------------------------------
# Gate 5 — Hooks
# ---------------------------------------------------------------------------

def check_hooks(target: Path) -> list[str]:
    """Validate hook frontmatter and stage references."""
    issues: list[str] = []
    hooks_dir = target / "hooks"

    if not hooks_dir.is_dir():
        return issues

    valid_stages = set(_extract_stages_from_system(target / "SYSTEM.md"))

    for hook_file in hooks_dir.glob("*.md"):
        fm = _parse_frontmatter(hook_file)
        name = fm.get("name", hook_file.stem)

        if "from-stage" not in fm:
            issues.append(f"Hook '{name}': missing frontmatter key 'from-stage'")
        if "to-stage" not in fm:
            issues.append(f"Hook '{name}': missing frontmatter key 'to-stage'")

        if valid_stages:
            from_stage = fm.get("from-stage", "")
            to_stage = fm.get("to-stage", "")
            if from_stage and from_stage not in valid_stages:
                issues.append(
                    f"Hook '{name}': from-stage '{from_stage}' not in SYSTEM.md stages"
                )
            if to_stage and to_stage not in valid_stages:
                issues.append(
                    f"Hook '{name}': to-stage '{to_stage}' not in SYSTEM.md stages"
                )

    return issues


# ---------------------------------------------------------------------------
# Gate 6 — Skills
# ---------------------------------------------------------------------------

def check_skills(target: Path) -> list[str]:
    """Check every agent has at least one skill (matched by agent field)."""
    issues: list[str] = []
    skills_dir = target / "skills"

    agent_names = _list_md_names(target / "agents")
    if not agent_names:
        return issues

    agents_with_skills: set[str] = set()
    if skills_dir.is_dir():
        for skill_file in skills_dir.glob("*.md"):
            fm = _parse_frontmatter(skill_file)
            agent_val = fm.get("agent", "")
            if agent_val:
                agents_with_skills.add(agent_val)

    for name in agent_names:
        if name not in agents_with_skills:
            issues.append(f"Agent '{name}': has no skill with matching 'agent' frontmatter field")

    return issues


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def inspect_distro(target: Path) -> dict[str, list[str]]:
    """Run all 6 quality gate checks against *target*.

    Returns a dict mapping gate name -> list of issue strings.
    An empty list means the gate passed.
    """
    return {
        "structural": check_structural(target),
        "system": check_system(target),
        "coverage": check_coverage(target),
        "stages": check_stages(target),
        "hooks": check_hooks(target),
        "skills": check_skills(target),
    }
