---
name: prd
description: "Generate a Product Requirements Document for Ralph Solo or Ralph's Army. Use when: create a prd, write prd, plan a feature, spec this out, requirements for, ralph prd."
user_invocable: true
---

# PRD Generator

Build a PRD formatted for either **Ralph Solo** (single iterating agent) or **Ralph's Army** (multi-agent with waves and domain isolation).

---

## Step 1: Ask Mode + Scope

Ask the user THREE things upfront:

**1. Mode:** Ralph Solo or Ralph's Army?
- **Solo** — one agent iterating through `PRD.md`, one task per iteration. Best for <20 stories, single-domain work.
- **Army** — multiple agents in waves with file ownership. Best for 20+ stories, multi-domain, parallelizable work.

**2. Build intent:** Prototype (PoC) or Production?
- **Prototype** — the bare proof of concept. Demonstrate the core idea works, nothing more. Run with `ralph ... --prototype`. See the Prototype Mode section below; it changes how you size stories and write criteria.
- **Production** — the full, hardened implementation (the default if unstated).

**3. Feature description:** What are we building?

If the user already specified any of these in their prompt, skip asking for that part.

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

**Capability test:** If a story's acceptance criteria bundle 4+ distinct capabilities (each able to fail on its own), split it. Keep story "mass" roughly uniform across the PRD — same-shaped cells are easier to schedule and verify.

### Splitting late: sub-story IDs
When you split a story *after* numbering — or want to signal "these are one thing decomposed" — suffix with letters (`US-018a`, `US-018b`, `US-018c`) instead of renumbering. Sibling IDs (US-019+) stay stable so references don't shift. Put shared/cross-cutting scaffolding in the first sub-story (`…a`) so the rest stay thin.

---

## Step 4: Order by Dependencies

Stories execute in priority order. Earlier stories must NOT depend on later ones.

**Correct:** Schema → Backend logic → UI components → Dashboard views
**Wrong:** UI component (needs schema that doesn't exist yet) → Schema

---

## Step 5: Phase & Group the Scope (optional)

When a build has a clear **core** plus a set of **deferred / scaling / stretch** work, don't dump the extras into Non-Goals — emit them as a distinctly-labeled phase section so the boundary is explicit and the deferred work stays specced. **Ralph skips deferred-phase sections by default** (a heading marked `(… — NOT core scope)`), so the core run stops cleanly; `ralph … --include-deferred` opts into building them.

- Core stories first (US-001…), then a `---` rule, then `# [Phase Name] (Phase N — NOT core scope)`.
- Open the phase with a **blockquote barrier note**: (a) it depends on core being complete, (b) the governing invariant that must hold across the phase, (c) "do not build during core scope."
- Within a large phase, group stories under **thematic track headers** (`## Track A — …`, `## Track B — …`). Order tracks so later ones depend on earlier ones.

**The governing-invariant note is the highest-value line in a phased PRD** — the one rule that must never break (e.g. "all controls stay in the deterministic core; the agent/edge layer only operates it"). State it once, at the top of the phase, as the membrane keeping the new layer from invading the core.

Deferred-phase cells keep the same shape as core cells (Description + verifiable criteria + "Typecheck passes"), but may be coarser if they are roadmap rather than immediate build. The heading text **must** contain `NOT core scope` for Ralph to recognize and skip it.

---

## Step 6: Write Acceptance Criteria

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

## Prototype Mode (PoC)

When build intent is **Prototype**, the PRD itself must encode YAGNI. The `--prototype` runtime flag constrains how agents build; this section constrains how you plan, so the two reinforce each other. Apply ALL of these:

1. **Cut to the happy path.** Include only P0 stories that demonstrate the core idea. Drop every P1/P2, every "nice to have", every secondary flow. If a story is not required to show the concept works, delete it.
2. **One core action per story, even smaller than usual.** Prototype stories should be the smallest slice that produces a visible result.
3. **Strip the acceptance criteria.** Keep only the criterion that proves the core behavior, plus `"Typecheck passes"` (and `"Verify changes work in browser"` for UI). Do NOT write criteria for: error handling, validation, loading/empty/error states, edge cases, auth, accessibility, responsiveness, persistence beyond what the demo needs, or performance. Those are non-goals, not unwritten work.
4. **Write an aggressive Non-Goals section.** Explicitly list what is excluded so no agent infers it later. Use these categories: error handling beyond crash prevention, logging, config systems, validation, caching, retries, tests, abstraction layers, auth, and any feature not named in a story.
5. **Fewer agents (Army).** Prefer Solo for a prototype. If using Army, collapse to the minimum number of agents (often one foundation plus one feature agent). Skip the polish agent entirely.
6. **Lean gates.** Wave gates should be typecheck only. Do not require a test suite the prototype will not have.

The litmus test for a prototype story: if you removed it, would the concept still be demonstrable? If yes, remove it.

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

---

# [Scaling / Phase 2 Name] (Phase 2 — NOT core scope)   ← OPTIONAL — see Step 5; omit if no deferred work. Heading MUST contain "NOT core scope" so Ralph skips it.

> Deferred. Depends on US-001…US-NNN. Invariant: [the one rule that must hold across this phase].
> Do not build during core scope.

## Track A — [Theme]
### US-013: [Title]
...

## Track B — [Theme]
### US-018a: [Title]   ← late split → a/b/c, see Step 3
...

## Non-Goals
- [Permanent exclusions. If a phase section is used above, point here to it as deferred (deferred ≠ never).]

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

## Companion Doc: RATIONALE.md (Tiers, Use Cases, Deliberations)

**Always generate `RATIONALE.md` alongside `PRD.md` — it is a required output of every PRD, not optional.** `PRD.md` is the declarative "what" Ralph executes; `RATIONALE.md` is the "why" for humans — tiered options, business justification, stack and scaling reasoning. Keep them separate so the PRD stays clean and machine-focused. RATIONALE.md is **human-facing and never passed to Ralph.** Four sections:

### 1. Tiered Capabilities
A menu by commitment level — what to build and *when to pull it in*. Map each tier to PRD story ranges.

| Tier | Name | What it adds | Pull it in when… | PRD stories |
|------|------|--------------|------------------|-------------|
| T0 | Core (must) | the working spine | always | US-001… |
| T1 | Hardening (should) | integrity / concurrency | first real users | US-013… |
| T2 | Advanced (could) | the differentiator layer | a clear signal appears | US-018… |
| T3 | Later (not yet specced) | speculative scale work | a proven scale signal | — |

### 2. Business Use Case per Section
One plain sentence per PRD section/story — the business reason it exists, in language a non-engineer approves. Forces every story to justify itself.

### 3. Stack Deliberations
Per major choice: **chosen / alternative / why / cost-to-switch-later.** Making reversibility explicit is the point — a cheap-to-switch choice needs less agonizing.

### 4. Scaling Options & Indicators
Per aspect: current state, the scaling move, and the **observable trigger signal** that says "do it now" — a metric or event (p95 latency, DB CPU, concurrent writers, agent becomes primary consumer), never a vibe. Pair every scaling option with its indicator.

### Chaining with /tot
Sections 3 and 4 are deliberations. For a genuinely contested call (e.g. "Postgres now or later?", "MCP vs native tool-calling?"), optionally run the **/tot** skill first (Empiricist · Systems Thinker · Critical Analyst), then distill its conclusion into the table and link the full analysis under a `## Deliberation Log` heading. Use /tot for contested calls only; don't ceremonialize obvious ones.

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
- [ ] Story "mass" roughly uniform; no story bundles 4+ distinct capabilities (else split)
- [ ] Late splits use `US-NNNa/b/c` suffixes with stable sibling IDs
- [ ] (If phased) Deferred work is a labeled phase section whose heading contains "NOT core scope", not buried in Non-Goals
- [ ] (If phased) Phase opens with a barrier note: depends-on + governing invariant + "don't build in core"
- [ ] RATIONALE.md generated (always) and saved as a separate file, not merged into PRD.md
- [ ] RATIONALE.md tiers map to PRD story ranges; every scaling option paired with a trigger indicator
- [ ] **Prototype:** Only P0 happy-path stories; criteria stripped to core behavior + typecheck; aggressive Non-Goals listing the YAGNI categories
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
- **Army:** `ralph <PRD_DIR> --army` (or just `ralph <PRD_DIR>`; army is auto-detected when an `agents/` dir is present)
- **All PRDs:** `ralph <PARENT_DIR>` (point at the parent) runs every `*/PRD.md` subdir in name order

When build intent is **Prototype**, append `--prototype` to the command so the runtime YAGNI constraints match the PRD (e.g. `ralph <PRD_DIR> --prototype`).

Example: `ralph PRDs/24-sub1hr-optimization --army`

If the PRD has a deferred phase (a `NOT core scope` section), tell the user Ralph builds **core only** by default and stops when core is done; add `--include-deferred` to build the phase sections too.

Always mention the `RATIONALE.md` companion (tiers, business cases, stack/scaling decisions) generated alongside `PRD.md` — it is human-facing and **not** consumed by Ralph.
