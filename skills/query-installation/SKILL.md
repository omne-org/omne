---
name: query-installation
description: Query kernel and distro version information for the current volume
---

# Query Installation

Reports the kernel version, distro name, distro version, and domain for the current omne volume.

## Procedure

1. Run the query script: `python .omne/core/scripts/query_install.py`
2. Report the output to the user

## Output

- Kernel name and version (from `.omne/core/manifest.json`)
- Distro name, version, and domain (from `.omne/image/manifest.json`)
- If either manifest is missing, report "not installed"
