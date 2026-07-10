---
id: TASK-005
category: spec
status: completed
---

# TASK-005: The three-modes doctrine fold (bound / derived / provision)

## User story

As a **tenant user asking for UI**, I want the builder to **resolve every
request to a binding mode** — bind to existing data, derive from the overall
context, or provision new records then bind — so "create a new session about
X and Y" works even when no home for it exists yet.

## Why this matters

The modes are the user's core interaction model (the goalkeeping →
module-research trace). Bound/derived are implicit today; provision-then-bind
doesn't exist at all. Design: `docs/design/binding-model.md` §4 (ratified).

## Scope

**In scope:**
- `content/BUILDER.md`: the three modes as operating doctrine — mode selection
  (existing collection → bound; synthesis ask → derived with snapshot
  provenance; no home → provision into the best-fit writable module, then
  bound with `provisioned: true`).
- `content/PROCESSES.md`: provision steps inside BUILD/ADD_SCREEN (find home
  via context index → create records per the module's declared conventions/
  procedure → register binding → publish), honoring the extended write-order
  law; RETIRE addendum (provisioned records stay — tenant data, noted in the
  app CHANGELOG).
- Derived-mode provenance: derived screens stamp their source snapshot
  (`data/` files with `_source`/`_derived_at`, already spec'd).

**Out of scope (explicit):**
- New processes beyond the canon list (provision is steps inside existing
  processes, NOT a ninth process) · `module.sessions` (deferred OQ-2) ·
  COMPONENTS.md.

## References

- `docs/design/binding-model.md` §4 (modes + the goalkeeping trace + RETIRE
  addendum), §5 executor rule (provision writes follow it).
- Resolved OQ-1/OQ-2: app store is the place; module-research is the
  provision home exemplar.

## Artifacts expected to change

- `content/BUILDER.md` (watch the 8KB terseness budget)
- `content/PROCESSES.md`
- `VERSION` + `rasa.json#version` + `CHANGELOG.md` (minor bump)

## Execution order

1. BUILDER mode-selection doctrine (terse — it's read every turn).
2. PROCESSES provision steps + RETIRE addendum.
3. Cross-check BUILDER/APP_MODEL/PROCESSES agree (one doctrine, three files).
4. Gate GREEN; bump + CHANGELOG; commit.

## Acceptance criteria

- [x] A fresh session reading BUILDER+PROCESSES can run the goalkeeping trace
      cold — self-walkthrough evidence in the closing report; **final tick is
      the reviewer's** (user walkthrough at review).
- [x] BUILDER.md stays under the 8KB terseness warn. *(7225B.)*
- [x] Process canon unchanged (eight named processes; provision = steps
      inside BUILD/ADD_SCREEN); check-doctrine GREEN.
- [x] RETIRE explicitly covers provisioned records (step 4).

## Verification plan (per the done-gate)

1. **Setup:** the golden app + a mock writable collection in its context.json.
2. **Checks:** the walkthrough (criterion 1) recorded step-by-step · byte
   count of BUILDER.md · check-doctrine output.
3. **Done-gate run:** all gates; evidence in the closing report.

## Manual verification (in addition to the done-gate)

1. Reviewer plays the tenant: asks for a UI with no data home and confirms
   the doctrine's answer is provision-then-bind, not fabrication.

## Gotchas & learned lessons

- **Never fabricate data to satisfy a mode** — an honest empty state + a
  provision offer beats invented rows (BUILDER's existing law).
- **Provision writes follow the OQ-4 executor rule** — module procedure
  first, conventions fallback, writable collections only.
- **BUILDER is read every turn** — every added sentence costs; prefer
  pointing at APP_MODEL/PROCESSES over restating.

## Open questions / risks

- None.

## Blocker notes

(empty)

## Self-review checklist

- [x] I followed the execution order in the spec.
- [x] Every acceptance criterion is met and individually verified.
- [x] I verified each step, not just the end state.
- [x] The done-gate passes (every gate in `.claude/done-gate.md`).
- [x] I didn't touch artifacts outside "Artifacts expected to change".

### Dependencies

- **Blocks / blocked by:** blocked by TASK-003 + TASK-004.

---

**Definition of done** (per `.claude/task-rules.md`): all criteria verified ·
plan ran with evidence · done-gate passes · closing report posted.
