# Example Agent Specification

## Identity
- **Name**: example-agent
- **Wave**: 1 (runs in parallel with other Wave 1 agents)
- **Stories**: US-010 to US-015 (6 stories)

## Mission
[Describe what this agent is responsible for. Be specific about the domain/feature area.]

Example: "Implement the user authentication system including login, registration, password reset, and session management."

## Owned Paths (WRITE access)
These are the ONLY files/directories this agent can modify:

- `app/auth/` - Authentication routes and pages
- `lib/auth/` - Auth utilities and helpers
- `components/auth/` - Auth-specific components
- `tests/auth/` - Auth tests

## Shared Paths (READ-ONLY)
Files this agent can read but NOT modify (owned by other agents):

- `lib/supabase/` - Database client (owned by foundation-agent)
- `components/ui/` - UI components (owned by foundation-agent)
- `lib/hooks/` - Shared hooks (owned by foundation-agent)

## DO NOT MODIFY
Explicit list of files to never touch:

- `package.json` (coordinate with foundation-agent for new deps)
- `middleware.ts` (owned by foundation-agent)
- Any files in `app/(authenticated)/` root

## Dependencies
What must be complete before this agent can start:

- Wave 0 (foundation-agent) must be complete
- Supabase client must be configured
- Base UI components must exist

## Progress File
`progress/progress-example.txt`

---

## Stories

### US-010: User Registration
**Description:** As a new user, I want to create an account so I can access the platform.

**Acceptance Criteria:**
- [ ] Create /register route with form fields (email, password, name)
- [ ] Validate email format and password strength
- [ ] Show loading state during registration
- [ ] Display error messages for validation failures
- [ ] Redirect to /dashboard on success
- [ ] Send verification email
- [ ] Typecheck passes

---

### US-011: User Login
**Description:** As a returning user, I want to log in so I can access my account.

**Acceptance Criteria:**
- [ ] Create /login route with email and password fields
- [ ] Show loading state during authentication
- [ ] Display error messages for invalid credentials
- [ ] Redirect to /dashboard on success
- [ ] Support "remember me" functionality
- [ ] Typecheck passes

---

### US-012: Password Reset Request
**Description:** As a user who forgot my password, I want to request a reset link.

**Acceptance Criteria:**
- [ ] Create /forgot-password route with email input
- [ ] Send password reset email via Supabase
- [ ] Show success message after email sent
- [ ] Handle invalid email gracefully
- [ ] Typecheck passes

---

## Verification Checklist

Before marking as complete:
- [ ] All stories marked [x] in progress file
- [ ] `npm run typecheck` passes
- [ ] `npm run test` passes (if tests exist)
- [ ] Manual verification of key flows

## Handoff Notes

After this agent completes, other agents will have access to:
- Authentication hooks (useAuth, useRequireAuth)
- Login/register/reset pages
- Session management utilities
