---
date-created: 2026-04-07-17:12:06
date-modified: 2026-04-07
---

# Omne System Design Spec

Omne (Latin: omni) is a kernel-based, MAS-native operating system for managing work across devices and collaborators. A `.omne/` dotdir at the repo root holds all governance. Content lives outside it in userspace. The kernel + content together form a **volume**. One repo = one volume.

Omne is not one tool -- it is a family of **distros**, each tuned for a domain. All distros share the same kernel architecture but ship different agents, skills, hooks, and context routing.

## Core Principles

1. **Cross-device, async-first** -- collaborators work on branches, merge back via git. No real-time sync required.
2. **MAS-native** -- multi-agent delegation is a first-class primitive. Orchestrator talks to user; subagents do the work with minimal context.
3. **Max 3 levels deep** -- `.omne/<dir>/<one-subdir>/file`. No deeper nesting anywhere.
4. **Rigorous stages** -- every distro declares and enforces lifecycle stages. The kernel provides the mechanism; distros define the content.
5. **Contract-protected** -- `cfg/` is frozen during active work. Changes require a deliberate review cycle.

## Terminology

| Term | Meaning |
| --- | --- |
| **omne** | System name (Latin: omni). The kernel-based OS. |
| **volume** | Complete bundle: `.omne/` kernel + content layer. One repo = one volume. |
| **.omne/** | Kernel directory. Ring-fenced dotdir at repo root. |
| **image/** | `.omne/image/` -- distro layer. Agents, skills, hooks, context routing. Shared across all installs of a distro. Updated only on distro upgrade. |
| **cfg/** | `.omne/cfg/` -- install contract. Per-volume SSoT. Frozen during active work. |
| **log/** | `.omne/log/` -- runtime state. Mutable, per-collaborator via git branches. Distributed log pattern. |
| **MANIFEST.md** | `.omne/MANIFEST.md` -- kernel entry point. Volume identity, boot sequence, stage declarations. |
| **bootloader** | `CLAUDE.md` -- thin pointer that loads the kernel. |
| **distro** | A specialization of omne for a domain. Ships as `image/` content. Named in Latin, max 5-char suffix. |
| **usr** | Content layer. Everything outside `.omne/`. Where actual work product lives. |

## Kernel Architecture

The kernel is four directories, one manifest file, and a CLI.

```
.omne/
  MANIFEST.md      # kernel entry point
  core/            # kernel layer (CLI, spec, manifest template — submodule or copied)
  image/           # distro layer (submodule or copied)
  cfg/             # install contract (frozen during active work)
  log/             # runtime (mutable, per-collaborator via branches)
```

| Component | Nature | Mutability | Git behavior |
| --- | --- | --- | --- |
| `MANIFEST.md` | Kernel | Stamped once, rarely updated | Committed |
| `core/` | Kernel | Updated only on kernel upgrade | Committed or submodule |
| `image/` | Distro | Updated only on distro upgrade | Committed or submodule |
| `cfg/` | Install | Frozen during active work | Committed |
| `log/` | Runtime | Freely mutable, per-collaborator via branches | Committed (embedded) or gitignored (mounted) |

**Bootloader chain:** `CLAUDE.md` -> `.omne/MANIFEST.md` -> `.omne/image/SYSTEM.md` -> distro-specific loading.

**One-level-under rule:** every dir inside `.omne/` allows one level of subdirs. Max depth: 3. Exception: `core/` is exempt from depth checking — it is a full kernel repo with its own internal structure (e.g. `core/cli/lib/`).

**Upgrade path:** distro updates touch `image/` and `core/`. `cfg/` and `log/` survive untouched. If a breaking `image/` change requires `cfg/` migration, the distro documents it as an explicit migration step.

### image/ Contract

Every distro must ship exactly these:

```
image/
  agents/            # agent role definitions
  skills/            # predefined per-distro skills
  hooks/             # enforcement scripts
  context-map.md     # what each agent touches and reads
  SYSTEM.md          # single-file schema, first thing loaded after MANIFEST
```

The full contract is defined in `docs/distro-spec.md` — the kernel's single-file declarative spec that `omne validate` reads to check distro compliance.

### CLI

Ships with the kernel repo (`omne-org/omne`). Five operations:

| Command | What it does |
| --- | --- |
| `omne init <distro> [--mounted]` | Scaffold `.omne/`, independently clone distro to `image/` and kernel to `core/`, introspect and stamp `MANIFEST.md`, seed `cfg/` from defaults, create `log/` subdirs, write `CLAUDE.md` bootloader |
| `omne upgrade` | Pull latest `image/` and `core/` independently. `cfg/` and `log/` untouched |
| `omne validate` | Two-layer check: volume integrity (dirs, manifest, depth) + distro compliance (6 quality gates) |
| `omne remove` | Tear down `.omne/` and `CLAUDE.md`, clean up submodules if mounted |
| `omne reset` | Re-stamp manifest, re-seed `cfg/` and `log/` from distro defaults. `image/` and `core/` untouched |

## MANIFEST.md

The manifest is the kernel's single file. Stamped from the kernel template during `omne init`. First thing any agent reads.

Required fields:

```markdown
---
volume: <volume-name>
distro: <distro-name>
distro-version: <semver>
created: <date>
---

# MANIFEST

## Identity
Volume name, distro origin, version.

## Directory Contract
- image/ -- distro layer (agents, skills, hooks)
- cfg/ -- install contract, frozen during active work
- log/ -- runtime, mutable, per-collaborator via branches

## Boot Sequence
1. CLAUDE.md loads this file
2. This file loads .omne/image/SYSTEM.md
3. SYSTEM.md loads distro-specific agents and context map

## Stages
Declared by distro, listed here for agent discoverability.

## Agents
Summary of available agents and their roles (populated from image/).

## Context Routing
Reference to image/context-map.md -- which agent reads what.

## Depth Rule
Max 3 levels from .omne/ root. Enforced by omne validate.
```

The manifest is descriptive -- it reflects what the distro installed. The kernel spec defines which fields are required.

## Deployment Modes

Two modes. Same kernel structure, different `image/` and `core/` shipping.

| Mode | How image/ and core/ ship | When to use |
| --- | --- | --- |
| **Embedded** | Copied into `.omne/image/` and `.omne/core/` | Solo dev, personal vaults, small projects |
| **Mounted** | Two first-level git submodules at `.omne/image/` and `.omne/core/` | Team sharing one distro, coordinated upgrades |

**Embedded:**
- `omne init omne-org/omne-liber`
- Clones distro and kernel as two independent operations. Distro content (minus `.git`, `core`) goes to `image/`. Kernel goes to `core/`. No `--recurse-submodules`, no split-copy.
- Kernel URL: read from `kernel-url` field in `SYSTEM.md` frontmatter, defaults to `https://github.com/omne-org/omne.git`.
- After install: seeds `cfg/` from `image/defaults/`, creates `log/` subdirs from `log-dirs` in `SYSTEM.md`.
- Upgrade: `omne upgrade` re-clones and replaces `image/` and `core/` independently. `cfg/` and `log/` untouched.

**Mounted:**
- `omne init omne-org/omne-faber --mounted`
- Adds two independent first-level submodules: distro at `.omne/image/`, kernel at `.omne/core/`. Kernel URL resolved same way as embedded.
- Upgrade: `git submodule update --remote` on both `.omne/image` and `.omne/core`. Version-locked to a commit.
- Team sees same `image/` and `core/` across all clones.

**Distro repos do not embed the kernel.** The `core/` submodule inside distro repos is no longer required. Kernel and distro are independent packages installed separately by `omne init`.

Both modes: `cfg/` is always local to the volume (committed, per-project). `log/` is always local (committed in embedded, gitignored in mounted so each clone gets fresh runtime).

## Agent Model

The kernel defines one universal rule: orchestrator pattern.

- **One orchestrator per volume.** It is the only agent that talks to the user. It reads `MANIFEST.md`, `cfg/`, and `log/` to understand the volume state.
- **All work is delegated to subagents.** Subagents receive minimal context injection -- only the files specified in `image/context-map.md` for their role.
- **Subagents are stateless.** Spawned with zero prior knowledge. Everything they need is injected as documents. If context is lost (window limit), the orchestrator resumes from state files in `log/`.
- **Subagents use tools directly.** They read, write, edit, search. The orchestrator never touches files -- it coordinates.

The kernel does not define which agents exist. That is the distro's job:

| Distro | Example agents |
| --- | --- |
| omne-liber | Clerk, Interlocutor, Sonder, Negator |
| omne-faber | Sonders, Negator, Behavior-spec-writer, Test-spec-writer, Team-lead, Worker, SDET, Auditor, Regression-runner |
| omne-ratio | (defined by that distro) |

Agent definitions live in `image/agents/`. Context routing lives in `image/context-map.md`. Both are distro-level -- shared across all installs of that distro.

## Stages & Lifecycle

The kernel provides the mechanism. Distros provide the content.

**Kernel contract (three verbs):**

1. **Declare** -- distro lists its stages in `MANIFEST.md` and ships stage definitions in `image/skills/`
2. **Enforce** -- distro ships hooks in `image/hooks/` that gate transitions
3. **Track** -- current stage state lives in `log/`. Orchestrator reads it to know where work stands.

**How stages work at runtime:**
- Orchestrator reads `log/` to determine current stage
- Before advancing, enforcement hooks validate prerequisites
- Stage transitions are logged in `log/`
- `cfg/` is frozen for the duration of all stages. Updating `cfg/` is its own dedicated cycle, outside normal work.

**Distro examples:**

| Distro | Stages |
| --- | --- |
| omne-faber | proposal -> behavior_spec -> test_spec -> tests -> code -> review |
| omne-liber | start -> ideation -> stress-test -> during -> terminate -> post-process |
| omne-ratio | hypothesis -> literature -> experiment -> analysis -> writeup |

Each distro defines: what the stages are, what artifacts each stage produces, what prerequisites gate each transition, and what hooks enforce the gates.

## Cross-Device Collaboration

No special sync mechanism. It is just git.

**Solo (typical for omne-liber):**
- One person, one branch. `log/` is yours. Commit and push as normal.

**Collab (typical for omne-faber, omne-ratio):**
- Each collaborator works on their own branch.
- Their `log/` entries travel with their branch.
- Merge the work = merge the logs.
- `cfg/` is shared across all branches (it is the contract everyone agreed on).

**Conflict resolution:**
- `cfg/` conflicts are rare -- it is frozen during active work. If two people update cfg between sprints, that is a deliberate merge.
- `log/` conflicts are resolved like any git merge. Since collaborators work on different branches, conflicts are minimal.
- `image/` never conflicts -- nobody edits it locally. Updates come from the distro.

**Branch conventions:** distro defines branch naming in `image/skills/`. The kernel does not prescribe branch strategy.

## omne-org Ecosystem

```
omne-org/
  omne/              # kernel -- spec, CLI, MANIFEST template
  omne-nosce/        # distro: self-governing (know thyself)
  omne-liber/        # distro: knowledge management
  omne-faber/        # distro: software engineering
  omne-ratio/        # distro: research
```

**omne** (kernel) contains:
- `spec/` -- the system design doc
- `cli/` -- `omne init`, `omne upgrade`, `omne validate`
- `manifest-template.md` -- stamped into volumes during init

**Distro repos** each contain the content that becomes `image/` plus a `core/` submodule pointing to the kernel: `agents/`, `skills/`, `hooks/`, `context-map.md`, `SYSTEM.md`, and `core/` (submodule -> `omne-org/omne`). A distro repo's root is the `image/` content. The `core/` submodule is separated during install — it goes to `.omne/core/`, not `.omne/image/core/`.

**omne-nosce** governs the org itself:
- `omne-org/` is a volume with `.omne/image/` and `.omne/core/` pointing at omne-nosce and omne respectively
- Manages updates to the kernel and all distros
- Distro versioning, release management, cross-distro validation

**Distro naming convention:** `omne-<latin-word>`. Latin suffix, max 5 characters, hints at the domain's essence.

**Installation:**

```bash
omne init omne-org/omne-faber           # embedded
omne init omne-org/omne-liber --mounted # mounted (submodule)
```

## Distro-Volume Examples

### omne-faber (SDE)

```
my-app/
  CLAUDE.md
  .omne/
    MANIFEST.md
    image/
      agents/
      skills/
      hooks/
      context-map.md
      SYSTEM.md
    cfg/
      design/
      engineering/
      planning/
      openspec/
    log/
      sprint/
      sessions/
      trail/
  src/
  tests/
```

### omne-liber (KM)

```
my-vault/
  CLAUDE.md
  .omne/
    MANIFEST.md
    image/
      agents/
      skills/
      hooks/
      context-map.md
      SYSTEM.md
    cfg/
      structure/
      fileclass/
      plugins/
    log/
      buffer/
      sessions/
      tasks/
  ksect/
  msect/
```

### omne-ratio (research)

```
my-paper/
  CLAUDE.md
  .omne/
    MANIFEST.md
    image/
      agents/
      skills/
      hooks/
      context-map.md
      SYSTEM.md
    cfg/
      methodology/
      literature/
      datasets/
    log/
      experiments/
      sessions/
      trail/
  data/
  notebooks/
  drafts/
```
