# Boot Chain

How omne volumes boot when a Claude Code session starts.

## Sequence

1. Claude Code loads `CLAUDE.md` from the volume root (automatic).
2. `CLAUDE.md` says: read `.omne/MANIFEST.md`.
3. The kernel session-start hook fires (configured as a Claude Code hook).
4. The hook reads `core/manifest.json` and `image/manifest.json`.
5. The hook loads kernel skills from `core/skills/`.
6. The hook loads `image/SYSTEM.md`, which loads distro agents and context routing.

## Requirements

- The volume must have a `CLAUDE.md` at root pointing to `.omne/MANIFEST.md`.
- The Claude Code session-start hook must be configured to run `core/hooks/session-start`.
- Both `core/manifest.json` and `image/manifest.json` must exist.
