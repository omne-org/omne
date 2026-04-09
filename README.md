# omne

Kernel for the omne operating system. Ships as a release artifact into `.omne/core/` inside volumes.

## Contents

- `manifest.json` — kernel version and gate runner path
- `manifest-template.md` — template stamped into `MANIFEST.md` during `omne init`
- `skills/` — kernel-level skills available to agents in every volume
- `hooks/` — boot hooks (session_start) for automatic kernel loading
- `scripts/` — shared scripts used by hooks and skills
- `docs/` — agent-readable documentation
- `man/` — human-readable reference

## Manual

- [Kernel Layout](man/kernel-layout.md) — what each directory and file does
- [Gate Protocol](man/gate-protocol.md) — how the kernel calls distro validators

## See Also

- `spec/omne-sys-design.md` — full system design (not included in release artifact)
