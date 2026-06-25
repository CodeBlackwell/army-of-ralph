# Product Requirements Document (PRD) Template

## Overview

**Project Name:** [Your Project Name]
**Version:** 1.0
**Last Updated:** [Date]

## Executive Summary

[2-3 sentences describing what the project does and who it's for]

**Companion:** generate `RATIONALE.md` alongside this PRD (tiered capabilities, business use case per section, stack + scaling decisions). It is human-facing and not consumed by Ralph.

---

## Orchestrator Config

Ralph's Army reads wave assignments and gate commands from this block.

```
WAVE_0_AGENTS=("foundation")
WAVE_0_GATE="cd my-project && npm run typecheck"

WAVE_1_AGENTS=("auth" "profile" "dashboard")
WAVE_1_GATE="cd my-project && npm run typecheck && npm test"

WAVE_2_AGENTS=("settings" "polish")
WAVE_2_GATE="cd my-project && npm run typecheck && npm test"
```

### Agent Roster

| Agent | Wave | Stories | Owned Paths |
|-------|------|---------|-------------|
| foundation | 0 | US-001 to US-005 | `lib/`, `components/ui/` |
| auth | 1 | US-010 to US-015 | `app/auth/`, `lib/auth/` |
| profile | 1 | US-020 to US-024 | `app/profile/`, `components/profile/` |
| dashboard | 1 | US-030 to US-034 | `app/dashboard/`, `components/dashboard/` |
| settings | 2 | US-040 to US-043 | `app/settings/` |
| polish | 2 | US-080 to US-083 | All paths (UI polish only) |

---

## Feature Domains

### Domain 1: Foundation (Wave 0)
**Owner:** foundation-agent

| ID | Story | Priority |
|----|-------|----------|
| US-001 | Set up project structure and base config | P0 |
| US-002 | Create database client and schema | P0 |
| US-003 | Build shared UI component library | P0 |

### Domain 2: Authentication (Wave 1)
**Owner:** auth-agent

| ID | Story | Priority |
|----|-------|----------|
| US-010 | User can register with email/password | P0 |
| US-011 | User can log in | P0 |
| US-012 | User can reset password | P1 |

### Domain 3: User Profile (Wave 1)
**Owner:** profile-agent

| ID | Story | Priority |
|----|-------|----------|
| US-020 | User can view their profile | P0 |
| US-021 | User can edit their profile | P0 |

### Domain 4: Settings (Wave 2)
**Owner:** settings-agent

| ID | Story | Priority |
|----|-------|----------|
| US-040 | User can change password | P0 |
| US-041 | User can manage notifications | P1 |

---

## Deferred Phase (optional)

Work that is real but out of the current build. A heading containing **`NOT core scope`** tells Ralph to skip the whole section by default, so a core run stops when core is done. Build it later with `ralph … --include-deferred`.

```markdown
# Scaling & Hardening (Phase 2 — NOT core scope)

> Deferred. Depends on Wave 0–2 core. Invariant: [the one rule that must hold across this phase].
> Do not build during core scope.

### US-090: [Deferred story title]
**Acceptance Criteria:**
- [ ] [criterion]
- [ ] Typecheck passes
```

---

## Project Structure

```
your-project/
├── PRD.md                    # This file
├── agents/
│   ├── foundation-agent.md   # Agent specs
│   ├── auth-agent.md
│   └── profile-agent.md
├── progress/
│   ├── progress-foundation.txt
│   ├── progress-auth.txt
│   └── progress-profile.txt
└── logs/                     # Created by ralph.py
    ├── foundation-agent.log
    ├── foundation-verify.log
    └── ...
```

---

## Wave Dependencies

```
Wave 0: Foundation
   │
   ├──► Wave 1: Core Features (parallel)
   │       ├── auth-agent
   │       ├── profile-agent
   │       └── dashboard-agent
   │
   └──► Wave 2: Extended Features (parallel, after Wave 1)
           ├── settings-agent
           └── polish-agent
```
