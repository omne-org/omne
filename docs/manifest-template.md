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

- `core/` — kernel layer (CLI, spec, manifest template — submodule or copy)
- `image/` — distro layer (agents, skills, hooks)
- `cfg/` — install contract, frozen during active work
- `log/` — runtime, mutable, per-collaborator via branches

## Boot Sequence

1. `CLAUDE.md` loads this file
2. This file loads `.omne/image/SYSTEM.md`
3. `SYSTEM.md` loads distro-specific agents and context map

## Stages

{{stages}}

## Agents

{{agents}}

## Context Routing

{{context-routing}}

## Depth Rule

Max 3 levels from `.omne/` root. Enforced by `omne validate`.
