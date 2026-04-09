# Gate Protocol

How the kernel delegates distro validation to the distro's own validator.

## Mechanism

1. `core/manifest.json` contains a `gate_runner` field (e.g., `"tools/inspect_tool.py"`).
2. During `omne validate`, the CLI reads this field.
3. The CLI runs `image/{gate_runner}` against the `image/` directory.
4. If the gate runner exits 0, the distro passes. If non-zero, validation fails.
5. If no file exists at the gate runner path, the step is skipped with a warning.

## Contract

- The kernel defines the protocol (fixed path in `manifest.json`).
- The distro implements the validator (ships a script at that path).
- The kernel never inspects distro semantics directly — it delegates.

## Example

```json
{
  "name": "omne",
  "version": "0.2.0",
  "gate_runner": "tools/inspect_tool.py"
}
```

The CLI runs: `python .omne/image/tools/inspect_tool.py .omne/image/`
