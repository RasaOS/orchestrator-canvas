---
id: TASK-002
category: spec
status: completed
---

# TASK-002: Finish the SA-023 re-role — domain identity everywhere

## User story

As a **runtime or authoring session opening this element**, I want **every
identity surface to say `rasa.domain.canvas` (a domain under the tenant's
brain)** so that no session inherits the retired orchestrator self-description.

## Why this matters

Canon SA-023 folded orchestrators into the tenant; v0.5.0 renamed only
`rasa.json#name/#kind`. `CLAUDE.md` ("the vertical-builder orchestrator"),
`README.md`, the CHANGELOG title, and `rasa.json`'s prose fields
(`session_model` still says `element=rasa.orchestrator.canvas`;
`tenant_model`, `canvas_model`, `note`, `scaffold.description`) all still
speak orchestrator. Contradictory self-description is identity drift.

## Scope

**In scope:**
- `CLAUDE.md` re-role: title + "who you are" → a domain knowledge-brain that
  authors bound canvas apps, sitting under `rasa.tenant.core`; keep the two-hats
  section, the capsule, and all seven process names (check-doctrine enforces).
- `README.md` + `CHANGELOG.md` title line.
- `rasa.json` prose fields: `session_model` (key becomes
  `element=rasa.domain.canvas`), `tenant_model`, `canvas_model`, `note`,
  `scaffold.description`.
- `contract_version` `1.3.0` → `1.4.0` — **coordinated**: flag to the
  orchestrator-workspace session so REGISTRY/conformance expect the outlier
  (resolved OQ-5).
- Minor version bump + CHANGELOG entry (0.7.0).

**Out of scope (explicit):**
- Any binding/doctrine content change (TASK-003+).
- Renaming the repo/remote (already `domain-canvas`).

## References

- Canon: Spec §55 SA-023 (FD-001..FD-004); `canon/tasks/done/SA-023-…md`.
- `docs/design/binding-model.md` §0–§1; `ui-engine-and-architecture.md` §0.
- Residual-drift inventory: binding-model §1 "Residual identity drift".

## Artifacts expected to change

- `CLAUDE.md` ⚠ gated — explicit user approval at close
- `README.md`
- `CHANGELOG.md` (title + new entry)
- `rasa.json` (prose fields + `contract_version` + version)
- `VERSION`

## Execution order

1. Rewrite `CLAUDE.md` identity sections (keep process names + gate wording).
2. Update `README.md` + `CHANGELOG.md` title.
3. Update the five `rasa.json` prose fields + `contract_version: "1.4.0"`.
4. Bump 0.7.0 (VERSION + rasa.json + CHANGELOG same commit).
5. `bin/check-doctrine` → GREEN; commit; flag the contract_version outlier to
   the workspace session.

## Acceptance criteria

- [x] `grep -ri "orchestrator" CLAUDE.md README.md rasa.json` returns only
      historical/canon references (SA-023 mentions), no self-description.
      *(Verified: single hit = CLAUDE.md:7 "per SA-023 the tenant is the
      orchestrator" — the canon reference itself.)*
- [x] `rasa.json#rasa.session_model` keys on `element=rasa.domain.canvas`.
- [x] `contract_version` == `1.4.0`; workspace session notified (note in the
      closing report).
- [x] check-doctrine GREEN; version plumbing consistent at 0.7.0.

**Scope addition (mid-task, per scope-discipline rule):**
`content/KERNEL_ASKS.md` (header + ask #4 said "this orchestrator" —
self-description living in content/; the acceptance grep didn't cover
content/, the re-role's intent does). Both fixed; content/ sweep now clean.

## Verification plan (per the done-gate)

1. **Setup:** none (text edits).
2. **Checks:** criterion 1 → the grep, output pasted in the report ·
   criterion 2 → `python3 -c` read of the field · criterion 3 → rasa.json diff
   + the notification note · criterion 4 → `check-doctrine; echo $?`.
3. **Done-gate run:** all gates incl. **gated-file review** (CLAUDE.md) —
   user approval recorded in the closing report.

## Manual verification (in addition to the done-gate)

1. User reads the new CLAUDE.md top section and confirms the identity reads
   right.

## Gotchas & learned lessons

- **check-doctrine requires all seven process names in CLAUDE.md** — don't
  drop any while rewriting.
- **Don't fold binding design into CLAUDE.md here** — identity only; the
  doctrine folds land in TASK-003/004/005.

## Open questions / risks

- Whether the workspace wants the contract_version bump batched with its own
  sweep — the flag in the closing report resolves it.

## Blocker notes

(empty)

## Self-review checklist

- [x] I followed the execution order in the spec.
- [x] Every acceptance criterion is met and individually verified.
- [x] I verified each step, not just the end state.
- [x] The done-gate passes (every gate in `.claude/done-gate.md`).
- [x] I didn't touch artifacts outside "Artifacts expected to change" (the
      one addition — content/KERNEL_ASKS.md — was recorded with justification
      before changing it).

### Dependencies

- **Blocks / blocked by:** after TASK-001 (clean baseline).

---

**Definition of done** (per `.claude/task-rules.md`): all criteria verified ·
plan ran with evidence · done-gate passes (incl. gated-file approval) ·
closing report posted.
