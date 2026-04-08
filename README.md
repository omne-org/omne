# omne

Kernel-based, MAS-native operating system for managing work across devices and collaborators.

## What This Repo Contains

- `docs/` — AI-facing specs and templates
  - `distro-spec.md` — declarative contract defining what valid distros must contain
  - `manifest-template.md` — template stamped into volumes during `omne init`
- `man/` — human-facing documentation
  - `omne-sys-design.md` — full system design specification
- `cli/` — CLI tools (`omne init`, `omne upgrade`, `omne validate`, `omne remove`, `omne reset`)
- `tests/` — test suite

## Usage

```bash
python cli/omne.py init <distro> [--mounted]   # scaffold a new volume
python cli/omne.py upgrade                       # update distro image and kernel
python cli/omne.py validate                      # check volume + distro integrity
python cli/omne.py remove                        # tear down the volume
python cli/omne.py reset                         # re-stamp manifest, re-seed cfg/log
```
