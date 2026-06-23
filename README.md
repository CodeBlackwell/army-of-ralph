# Army of Ralph

Autonomous [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) orchestrator. Runs Claude agents in two modes — **solo** (one task per iteration) and **army** (parallel agents in sequential waves with verification) — driven by PRD files. Point it at one PRD or a whole directory of them.

## Install

```bash
pip install army-of-ralph          # PyPI
brew install codeblackwell/tap/ralph   # Homebrew
```

Both install the `ralph` command. Requires Python 3.10+ and the `claude` CLI on your PATH.

## Quick Start

```bash
ralph PRDs/01-feature           # one PRD — mode auto-detected
ralph PRDs/01-feature 20        # solo, max 20 iterations
ralph PRDs/01-feature --army    # force army mode
ralph PRDs --all                # campaign: run every PRD subdir in order
```

Mode is auto-detected per PRD: a directory with an `agents/` subdir runs in **army** mode, otherwise **solo**. `--army` forces it on.

## Targeting One PRD or All of Them

A PRD lives in its own directory (`PRD.md` plus, for army mode, `agents/` and `progress/`). You organize features as sibling subdirs:

```
PRDs/
├── 01-schema/      PRD.md                 → solo
├── 02-auth/        PRD.md + agents/       → army
└── 03-dashboard/   PRD.md + agents/       → army
```

- **One PRD:** `ralph PRDs/02-auth` runs just that directory.
- **All PRDs:** `ralph PRDs --all` discovers every `*/PRD.md` under `PRDs/`, runs them in name order (so number your dirs), and stops the campaign if one fails. Each subdir's mode is auto-detected.

## Modes

### Solo

Finds the first unchecked `[ ]` task in `PRD.md`, implements it, marks it `[x]`, commits, repeats — one task per iteration until the PRD is done or `max_iterations` is hit.

### Army

Reads wave assignments from the PRD, launches agents in parallel per wave, gates between waves, and verifies completion.

```
┌─────────┐   gate   ┌─────────┐   gate   ┌─────────┐
│ Wave 0  │ ──────►  │ Wave 1  │ ──────►  │ Wave 2  │
│Foundation│         │ Parallel │         │ Parallel │
└─────────┘          └─────────┘          └─────────┘
```

**Domain isolation** — each agent owns specific file paths, so parallel agents never conflict.

**Wave gating** — gate commands (typecheck, tests) run between waves; a failed gate re-launches the wave's agents with error context (up to 3 retries). Define waves in the PRD:

```
WAVE_0_AGENTS=("foundation")
WAVE_0_GATE="cd my-project && npm run typecheck"

WAVE_1_AGENTS=("auth" "profile" "dashboard")
WAVE_1_GATE="cd my-project && npm run typecheck && npm test"
```

**Three-layer completion** — prevents an agent from falsely claiming "done":

| Layer | Tag | Who writes it |
|-------|-----|---------------|
| Promise | `<promise>COMPLETE</promise>` | Templates only (never triggers completion) |
| Delivered | `<delivered>COMPLETE</delivered>` | Agent self-reports |
| Verified | `<verified>COMPLETE</verified>` | A separate verification Claude confirms it |

## Generating PRDs

The `skills/prd-SKILL.md` Claude Code skill generates PRDs in the right shape for either mode. Copy it into your `.claude/skills/` and run `/prd`. Templates for hand-authoring live in `templates/`.

## Project Structure (army mode)

```
PRDs/02-auth/
├── PRD.md                       # spec + wave config
├── agents/<name>-agent.md       # one spec per agent (owned paths, stories)
├── progress/progress-<name>.txt # checkbox tracker + completion signal
└── logs/                        # auto-created — agent + verify stdout, timing
```

## CLI Reference

```
ralph [target] [max_iterations] [sleep] [options]

  target           PRD dir/file, or a parent dir of PRD subdirs (with --all)
  max_iterations   Max iterations for solo mode (default: 10)
  sleep            Seconds between iterations (default: 2)

  -a, --army       Force army mode (otherwise auto-detected from agents/ dir)
  --all            Run every */PRD.md subdir under target, in name order
  -t, -n, -s       Named forms of target / max-iterations / sleep
```

## License

MIT
