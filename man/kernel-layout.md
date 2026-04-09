# Kernel Layout

Reference for every directory and file in `.omne/core/`.

## Files

| Path | Purpose |
|------|---------|
| `manifest.json` | Kernel version, name, and gate runner path. Machine-readable SSoT. |
| `manifest-template.md` | Template stamped into `MANIFEST.md` during `omne init`. Contains placeholders. |
| `README.md` | Catalog and entry point for `man/` pages. |
| `CLAUDE.md` | Instructions for agents working inside a volume with this kernel. |

## Directories

| Path | Purpose |
|------|---------|
| `skills/` | Kernel-level skills available to agents in every volume. Not distro-specific. |
| `hooks/` | Boot hooks. `session-start` fires on Claude Code session start. |
| `scripts/` | Shared Python scripts used by hooks and skills. |
| `scripts/tests/` | Tests for scripts. |
| `docs/` | Agent-readable documentation about kernel behavior. |
| `man/` | Human-readable reference (this directory). |

## Not in Release

| Path | Purpose |
|------|---------|
| `spec/` | System design specification. Lives in the repo, not shipped in artifacts. |
| `.github/` | CI/CD workflows. |
