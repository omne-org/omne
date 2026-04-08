# omne

Kernel-based, MAS-native operating system for managing work across devices and collaborators.

## What This Repo Contains

- `manifest-template.md` — template stamped into volumes during `omne init`
- `cli/` — CLI tools (`omne init`, `omne upgrade`, `omne validate`)
- `spec/` — system design specification
- `tests/` — test suite

## Usage

```bash
python cli/omne.py init <distro> [--mounted]   # scaffold a new volume
python cli/omne.py upgrade                       # update distro image
python cli/omne.py validate                      # check volume integrity
```

## See Also

- `spec/omne-sys-design.md` — full system design
