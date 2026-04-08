---
spec-version: 0.1.0
---

# Distro Spec

Single source of truth for what a valid omne distro must contain. The kernel's `omne validate` reads this file to check distro compliance.

## Required Directories

Each must contain at least one `.md` file:

- `agents/`
- `skills/`
- `hooks/`

## Required Files

- `SYSTEM.md`
- `context-map.md`

## SYSTEM.md Contract

### Frontmatter Keys

Required: `distro`, `distro-version`, `domain`

### Required Sections

- `## Agents` — must list every agent defined in `agents/`
- `## Stages` — must contain a markdown table

### Stages Table Columns

Required: `Stage`, `Entry Gate`, `Artifacts`, `Exit Gate`

The table must have at least one data row.

## Agent Contract

Each file in `agents/*.md` must have YAML frontmatter with a `name` key.

## Skill Contract

Each file in `skills/*.md` must have YAML frontmatter with an `agent` key referencing a valid agent name.

## Hook Contract

Each file in `hooks/*.md` must have YAML frontmatter with `from-stage` and `to-stage` keys referencing stages declared in `SYSTEM.md`.

## Cross-Reference Rules

1. Every agent in `agents/` must appear in `SYSTEM.md` `## Agents` section
2. Every agent in `agents/` must appear in `context-map.md`
3. Every agent must have at least one skill with a matching `agent` frontmatter field

## Depth Rule

Max 2 levels of directory nesting from image root.

Exempt from depth checking: `.git`, `__pycache__`, `defaults`, `tools`, `tests`

## Optional Directories

- `defaults/` — distro-provided defaults for seeding `cfg/` on install
- `tools/` — distro-specific tooling
- `tests/` — distro test suite
