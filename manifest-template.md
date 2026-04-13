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

1. Volume `CLAUDE.md` imports this file via `@.omne/MANIFEST.md`
2. This file imports `@image/SYSTEM.md` below
3. `SYSTEM.md` imports the distro context map

@image/SYSTEM.md

## Stages

{{stages}}

## Agents

{{agents}}

## Context Routing

{{context-routing}}

## Depth Rule

Max 3 levels from `.omne/` root. Enforced by `omne validate`.
