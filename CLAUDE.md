# CLAUDE.md

> Kernel-level instructions for agents in omne volumes.

## Available Skills

Kernel skills are in `.omne/core/skills/`. Use them to:

- Query installation info: `query-installation`

## Boot

The session-start hook loads kernel and distro metadata automatically.
To manually check installation info, run: `python .omne/core/scripts/query_install.py`

## Gate Runner

The kernel delegates distro validation to the distro's own validator.
See `man/gate-protocol.md` for details.
