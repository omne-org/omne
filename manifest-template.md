---
volume: {{volume}}
distro: {{distro}}
distro-version: {{distro-version}}
created: {{created}}
---

# MANIFEST

## Identity

- **Volume:** {{volume}}
- **Distro:** {{distro}}
- **Version:** {{distro-version}}
- **Created:** {{created}}

## Directory Contract

- `image/` — distro layer (agents, skills, hooks)
- `cfg/` — install contract, frozen during active work
- `log/` — runtime, mutable, per-collaborator via branches

## Boot Sequence

1. `CLAUDE.md` loads this file
2. This file loads `.omne/image/SYSTEM.md`
3. `SYSTEM.md` loads distro-specific agents and context map

## Stages

Declared by distro, listed here for agent discoverability.

## Agents

Summary of available agents and their roles (populated from `image/`).

## Context Routing

See `image/context-map.md` for which agent reads what.

## Depth Rule

Max 3 levels from `.omne/` root. Enforced by `omne validate`.
