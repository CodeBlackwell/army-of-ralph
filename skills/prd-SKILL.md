---
name: prd
description: "Generate a Product Requirements Document for Ralph Solo or Ralph's Army. Use when: create a prd, write prd, plan a feature, spec this out, requirements for, ralph prd."
user_invocable: true
---

# PRD Generator

Build a PRD formatted for either **Ralph Solo** (single iterating agent) or **Ralph's Army** (multi-agent with waves and domain isolation).

---

## Step 1: Ask Mode + Scope

Ask the user TWO things upfront:

**1. Mode:** Ralph Solo or Ralph's Army?
- **Solo** — one agent iterating through `PRD.md`, one task per iteration. Best for <20 stories, single-domain work.
- **Army** — multiple agents in waves with file ownership. Best for 20+ stories, multi-domain, parallelizable work.

**2. Feature description:** What are we building?

If the user already specified mode or feature in their prompt, skip asking for that part.

---

## Step 2: Clarifying Questions

Ask 3-5 essential questions with **lettered options** so the user can respond quickly ("1A, 2C, 3B"):

```
1. What is the primary goal?
   A. [option based on feature]
   B. [option]
   C. [option]
   D. Other: [specify]

2. What is the scope?
   A. Minimal viable version
   B. Full-featured implementation
   C. Just backend/API
   D. Just the UI
```

Focus on: problem/goal, core actions, scope boundaries, success criteria.

---

## Step 3: Size Stories

**THE #1 RULE: Each story must be completable in ONE context window (~10 min of AI work).**

Ralph spawns fresh per iteration — no memory of previous work. Too-big stories = broken code.

### Right-sized:
- Add a database column and migration
- Add a single UI component
- Update one API endpoint with new logic
- Add a filter to a list

### Too big — MUST split:
| Too Big | Split Into |
|---------|-----------|
| "Build the dashboard" | Schema, queries, UI components, filters |
| "Add authentication" | Schema, middleware, login UI, session handling |
| "Refactor the API" | One story per endpoint |

**Rule of thumb:** If you can't describe the change in 2-3 sentences, it's too big.

---

## Step 4: Order by Dependencies

Stories execute in priority order. Earlier stories must NOT depend on later ones.

**Correct:** Schema → Backend logic → UI components → Dashboard views
**Wrong:** UI component (needs schema that doesn't exist yet) → Schema

---

## Step 5: Write Acceptance Criteria

Each criterion must be **verifiable** — something Ralph can CHECK.

### Good (verifiable):
- "Add `status` column with default 'pending'"
- "Filter dropdown has options: All, Active, Completed"
- "Typecheck passes"

### Bad (vague):
- "Works correctly"
- "Good UX"
- "Handles edge cases"

**Always include** `"Typecheck passes"` as final criterion. For UI stories also add `"Verify changes work in browser"`.

---

## Output Format: Ralph Solo

Save `PRD.md` and `progress.txt` in the working directory.

### PRD.md structure:

```markdown
# PRD: [Feature Name]

## Introduction
[2-3 sentences: what it does, who it's for]

## Goals
- [Specific, measurable goal]
- [Another goal]

## User Stories

### US-001: [Title]
**Description:** As a [user], I want [feature] so that [benefit].

**Acceptance Criteria:**
- [ ] Specific verifiable criterion
- [ ] Another criterion
- [ ] Typecheck passes

### US-002: [Title]
...

## Non-Goals
- [What this does NOT include]

## Technical Considerations
- [Known constraints, components to reuse]
```

### progress.txt:

```markdown
# Progress Log

## Learnings
(Patterns discovered during implementation)

---
```

---

## Output Format: Ralph's Army

Save these files (create directories if needed):
- `PRD.md` — master plan with roster, waves, ownership map
- `agents/<name>-agent.md` — one per agent, contains stories + file ownership
- `progress/progress-<name>.txt` — one per agent, checkbox tracker + completion signal

### Context Budget Rule

Each agent runs in a single Claude session. Its context load is:
- System prompt injection (~500 tokens, built by `ralph.py`)
- Agent spec file (`agents/<name>-agent.md` — the agent reads this entirely)
- Progress file (grows as agent works)
- Code files the agent reads and writes

**Max 4 stories per agent.** More stories = bigger agent.md = less room for actual code work. If a domain has 5+ stories, split into two agents in the same wave with non-overlapping paths.

| Agent Load | Stories | Risk |
|------------|---------|------|
| Light | 1-2 | Safe — agent has plenty of context headroom |
| Normal | 3-4 | Sweet spot — fills context well without exhaustion |
| Heavy | 5-6 | Risky — split into two agents |
| Overloaded | 7+ | MUST split — agent will lose coherence late in session |

### Agent Sizing Heuristic

Decide agent count by domain decomposition, not story count:

1. List all file paths that will be created or modified
2. Group into non-overlapping domains (no two agents write to same path)
3. Each domain = one agent (merge small domains that are tightly coupled)
4. If a domain has 5+ stories, split by sub-concern (e.g. `api-agent` + `api-tests-agent`)
5. Foundation agent (Wave 0) owns shared infra — schemas, configs, shared libs
6. Polish agent (final wave) gets broad read + narrow write (UI refinements only)

### PRD.md structure:

```markdown
# PRD: [Feature Name]

## Introduction
[2-3 sentences]

## Goals
- [Goal]

## Agent Roster

| Agent | Wave | Stories | Owned Paths |
|-------|------|---------|-------------|
| foundation | 0 | US-001 to US-005 | `lib/core/`, `config/` |
| feature-a | 1 | US-010 to US-015 | `app/feature-a/`, `components/feature-a/` |
| feature-b | 1 | US-020 to US-025 | `app/feature-b/`, `components/feature-b/` |
| polish | 2 | US-080 to US-083 | All paths (UI polish only) |

## Wave Plan

```
Wave 0 (foundation) ──► Wave 1 (feature-a ║ feature-b) ──► Wave 2 (polish)
                   [gate: typecheck]                  [gate: typecheck + test]
```

### Wave Gates
| After Wave | Validation | Failure Action |
|------------|-----------|----------------|
| 0 | Typecheck | Block Wave 1 until fixed |
| 1 | Typecheck + tests | Block Wave 2 until fixed |
| 2 (final) | Full test suite | Manual review |

## Orchestrator Config

```bash
WAVE_0_AGENTS=("foundation")
WAVE_1_AGENTS=("feature-a" "feature-b")
WAVE_2_AGENTS=("polish")
```

## Ownership Map

| Path | Owner | Access |
|------|-------|--------|
| `lib/core/` | foundation | WRITE |
| `config/` | foundation | WRITE |
| `app/feature-a/` | feature-a | WRITE |
| `components/feature-a/` | feature-a | WRITE |
| `app/feature-b/` | feature-b | WRITE |
| `components/feature-b/` | feature-b | WRITE |
| `lib/core/` | feature-a, feature-b | READ |
| `*` | polish | READ (write UI only) |

## Feature Domains

### Domain: [Name] (Wave 0)
**Owner:** foundation-agent

| ID | Story | Status |
|----|-------|--------|
| US-001 | [Description] | [ ] |
| US-002 | [Description] | [ ] |

### Domain: [Name] (Wave 1)
**Owner:** feature-a-agent
...

## Non-Goals
- [Exclusions]

## Progress Tracker

| Wave | Agent | Stories | Completed | Status |
|------|-------|---------|-----------|--------|
| 0 | foundation | 5 | 0 | NOT_STARTED |
| 1 | feature-a | 6 | 0 | NOT_STARTED |
| 1 | feature-b | 6 | 0 | NOT_STARTED |
| 2 | polish | 4 | 0 | NOT_STARTED |
```

### agents/<name>-agent.md structure:

```markdown
# [Name] Agent Specification

## Identity
- **Name**: [name]-agent
- **Wave**: [N]
- **Stories**: US-XXX to US-XXX
- **Context Budget**: [N] stories ([light/normal/heavy])

## Mission
[1-2 sentences: what this agent builds and why]

## Owned Paths (WRITE access)
- `path/to/domain/` - Description

## Shared Paths (READ-ONLY)
- `path/to/shared/` - Description (owned by [other]-agent)

## DO NOT MODIFY
- `package.json` (coordinate with foundation-agent)
- [Other protected files]

## Dependencies
- [What must be complete before this agent starts]
- Wave [N-1] agents: [list]

## Progress File
`progress/progress-[name].txt`

---

## Stories

### US-XXX: [Title]
**Description:** As a [user], I want [feature] so that [benefit].

**Acceptance Criteria:**
- [ ] Criterion
- [ ] Typecheck passes

**Implementation Notes:**
[Optional: code patterns to follow, key imports, API shapes.
Include ONLY when the agent needs context it can't discover from reading owned paths.]

---

## Verification Checklist
- [ ] All stories marked [x] in progress file
- [ ] Tests/typecheck pass
- [ ] No modifications outside owned paths
- [ ] `<delivered>COMPLETE</delivered>` written to progress file

## Handoff Notes
[What downstream agents (later waves) will need from this agent's work.
Example: "Auth hooks exported from `lib/auth/hooks.ts`: useAuth(), useRequireAuth()"]
```

### progress/progress-<name>.txt structure:

```markdown
# [Name] Agent Progress
# Wave: [N]
# Stories: US-XXX to US-XXX

## Status: NOT_STARTED

## Stories

[ ] US-XXX: [Title]
    - [ ] Criterion 1
    - [ ] Criterion 2
    - [ ] Typecheck passes

[ ] US-XXX: [Title]
    - [ ] Criterion 1
    - [ ] Typecheck passes

---

## Notes
(Agent appends learnings here as it works)

Format per story:
## US-XXX: [Title]
- What was implemented
- Files changed
- Learnings for downstream agents

---

## Completion Signal
(When all stories done and verified, agent writes delivered tag here)
```

**IMPORTANT:** Do NOT put the literal completion tag (`<delivered>COMPLETE</delivered>`) in the template text. Ralph's completion check does substring matching — if the tag appears in instruction text, it will false-positive and skip the agent without it doing any work. Use a description like "agent writes delivered tag here" instead.

---

## Army-Specific Rules

### File Ownership
1. **Every file has exactly one owner.** No two agents write to the same path.
2. **Shared paths are read-only.** An agent can import/read a shared component but cannot modify it.
3. **If two agents need to modify the same file** — restructure so one agent creates it and the other reads it, OR put both stories in the same agent.

### Wave Gating
4. **Wave 0 completes before Wave 1 starts.** All agents in a wave run in parallel.
5. **Validation runs between waves.** Typecheck minimum; test suite if available. The orchestrator runs gate commands before launching the next wave.
6. **A failed gate blocks the next wave.** The orchestrator will not proceed until validation passes.

### Story Namespacing
7. **Story IDs are namespaced per agent.** Foundation: US-001-009, Agent A: US-010-019, Agent B: US-020-029, etc. Leave gaps of 10 between agents for future insertion.

### Git Strategy (Manual)
8. **Optionally, create branch `wave-N/<name>-agent` per agent** before launch. Ralph does not automate branch management.
9. **After a wave completes, merge wave branches into `main`** manually or via script. Validate before launching the next wave.
10. **Same-wave agents never touch the same files** — merges are always conflict-free by design.

### Three-Layer Completion
11. Ralph uses three distinct tags to prevent false positives:
    - `<promise>COMPLETE</promise>` — legacy/template only (NEVER triggers completion)
    - `<delivered>COMPLETE</delivered>` — agent writes this when it believes all work is done
    - `<verified>COMPLETE</verified>` — verification Claude writes this after confirming work is actually complete
12. **Agents signal completion** by writing `<delivered>COMPLETE</delivered>` to their progress file. Ralph polls every 15s.
13. **After delivery, Ralph verifies** — launches a separate Claude that checks all tasks are `[x]`, owned files exist, and typecheck passes.
14. **A wave is complete when ALL agents in that wave are verified.**

### Polish Agent
15. **Polish agent (final wave)** gets read access to everything but only writes UI refinements — loading states, error messages, responsive tweaks. No new features.

### Recovery
16. **If an agent fails** (crashes, runs out of context, produces broken code):
    - The orchestrator detects no `<delivered>COMPLETE</delivered>` after timeout
    - Re-launch the agent — it reads its progress file to see what's done vs remaining
    - Progress file acts as checkpoint — completed stories stay `[x]`, agent picks up from first `[ ]`

---

## Pre-Save Checklist

Before saving any files, verify:

- [ ] Asked clarifying questions with lettered options
- [ ] Incorporated user's answers
- [ ] Stories use US-XXX format with sequential IDs (gaps of 10 between agents)
- [ ] Each story completable in ONE context window (small enough)
- [ ] Stories ordered by dependency within each agent
- [ ] All criteria are verifiable (not vague)
- [ ] Every story has "Typecheck passes"
- [ ] UI stories have "Verify changes work in browser"
- [ ] Non-goals section defines clear boundaries
- [ ] **Solo:** Saved `PRD.md` + `progress.txt`
- [ ] **Army:** Saved `PRD.md` + all `agents/*.md` + all `progress/*.txt`
- [ ] **Army:** Ownership map has no overlapping write paths
- [ ] **Army:** Wave dependencies are acyclic
- [ ] **Army:** Max 4 stories per agent (split if more)
- [ ] **Army:** Orchestrator config block has correct wave arrays
- [ ] **Army:** (Optional) Git branch table matches agent roster if using branch isolation
- [ ] **Army:** Each agent.md has Handoff Notes for downstream agents
- [ ] **Army:** Wave gates defined (what validation runs between waves)

## Final Step: Run Command

After all files are saved, print the run command for the user:

- **Solo:** `ralph <PRD_DIR> [max_iterations]`
- **Army:** `ralph <PRD_DIR> --army` (or just `ralph <PRD_DIR>` — army is auto-detected when an `agents/` dir is present)
- **All PRDs:** `ralph <PARENT_DIR> --all` runs every `*/PRD.md` subdir in name order

Example: `ralph PRDs/24-sub1hr-optimization --army`
