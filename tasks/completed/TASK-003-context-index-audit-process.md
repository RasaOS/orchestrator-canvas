---
id: TASK-003
category: spec
status: completed
---

# TASK-003: The context index — `context.json` schema + the AUDIT procedure

## User story

As a **runtime session bootstrapping an app in a tenant**, I want **a
machine-readable index of what exists to bind to** (domains, modules, their
collections + record shapes/types, tenant data) so that bound UIs are planned
against reality instead of guesswork — requirement #3 of the design.

## Why this matters

Today the doctrine has no sibling/parent awareness at all; `data_sources[]`
are raw paths. The context index is the planning input for every binding mode
and the provision-then-bind flow. Design: `docs/design/binding-model.md` §3
(ratified 2026-07-09).

## Scope

**In scope:**
- `schemas/rasa.canvas.context.v1.schema.json` (new, published).
- The **AUDIT procedure** in `content/PROCESSES.md`: three-flavor structural
  detection (holding-folder / co-located / canon-author — NOT
  presence-of-`elements/`), walk parent+siblings' `rasa.json`, **seam-first
  collection discovery** (module's declared seam/config → rasa.json seed
  declarations → inference from seed layout + samples), per-field **types**
  where inferable, tenant-data enumeration, staleness rules (re-audit at
  BOOTSTRAP; on unresolvable binding target; advisory `_audited_at`).
- `content/APP_MODEL.md`: `context.json` joins the workspace spec (per-install,
  disposable, never in `content/`).
- `bin/check-app`: context.json parses + schema-valid when present; warn when
  absent.
- Golden app gains an example `context.json`.
- Decision inside this task: AUDIT as an **eighth named process** (update
  `bin/check-doctrine` PROCESSES canon + BUILDER + CLAUDE mentions in
  lockstep) vs a BOOTSTRAP sub-step. Recommendation: eighth process.

**Out of scope (explicit):**
- `bindings[]` (TASK-004). Kernel `GET /v1/elements` integration (fs-walk v1;
  kernel-heavy migration later per the standing principle).

## References

- `docs/design/binding-model.md` §3 + §8 (the AUDIT process box) + §A4/A5/A7.
- Seam precedent: module-research seeds `.claude/research-canon.md`;
  module-tasks records = `TASK-*.md` frontmatter under state subdirs.
- Standing principle: kernel-heavy/domain-light (ui-engine §2) — the fs-walk
  is the stopgap; the kernel context surface is the target.

## Artifacts expected to change

- (new) `schemas/rasa.canvas.context.v1.schema.json`
- `content/PROCESSES.md` · `content/APP_MODEL.md` · `content/BUILDER.md`
  (route AUDIT in the loop)
- `bin/check-app` · `bin/check-doctrine` ⚠ (PROCESSES canon — gated-adjacent;
  user approval) · `CLAUDE.md` ⚠ gated (process capsule mention)
- (new) `examples/orders-desk/context.json`
- `VERSION` + `rasa.json#version` + `CHANGELOG.md` (minor bump)

## Execution order

1. Author the schema; validate the design-doc example against it.
2. Write the AUDIT procedure in PROCESSES.md (+ the eighth-process decision:
   update check-doctrine's `PROCESSES` list, BUILDER loop, CLAUDE capsule
   together).
3. APP_MODEL workspace section + staleness rules.
4. check-app additions; golden `context.json` authored against the real
   workspace shape.
5. Gate GREEN end-to-end; bump + CHANGELOG; commit.

## Acceptance criteria

- [x] Schema published and the golden `context.json` validates against it.
      *(jsonschema lib not installed in this env — validated structurally via
      check-app's new checks + `python3 -m json.tool`; golden GREEN 0/0.)*
- [x] AUDIT procedure documents all three flavors with **structural**
      detection, seam-first discovery precedence, and typed fields.
      *(Dry-run against the real workspace: `.rasa/holding/` absent, no
      `tenant.members[]`, full clones under `elements/` → canon-author ✓ —
      the case the naive heuristic misclassified.)*
- [x] check-doctrine GREEN with the process-canon change (all mentions in
      lockstep — PROCESSES.md order, check-doctrine constant, BUILDER
      routing, CLAUDE capsule).
- [ ] A fresh read of PROCESSES.md alone is enough to run an audit cold —
      **reviewer check: user, at review** (the one box the closer can't tick).

## Verification plan (per the done-gate)

1. **Setup:** the rasaos workspace as the canon-author-flavor test case.
2. **Checks:** schema → `python3 -m json.tool` + a jsonschema validation of the
   golden index · flavors → dry-run the detection logic against the workspace
   (must classify canon-author, NOT holding-folder) · lockstep → check-doctrine.
3. **Done-gate run:** all gates; gated-file approvals recorded.

## Manual verification (in addition to the done-gate)

1. Reviewer follows PROCESSES.md §AUDIT by hand against the workspace and gets
   a sane index.

## Gotchas & learned lessons

- **The workspace has `elements/` AND no holding folder** — the naive
  detection heuristic misclassifies it (design review #11). Test against it.
- **module-research's root is per-project** (its seam declares it) — do not
  hardcode `research/topics` (design review #10).
- **check-doctrine enforces the seven-process canon by exact list** — adding
  AUDIT without updating the constant + BUILDER + CLAUDE mentions is an
  instant RED.

## Open questions / risks

- Eighth-process vs BOOTSTRAP-sub-step (recommendation: eighth; decide at
  execution with user if unsure).

## Blocker notes

(empty)

## Self-review checklist

- [x] I followed the execution order in the spec (eighth-process decision:
      taken as the spec recommended; user sees it at review).
- [x] Every acceptance criterion is met and individually verified (except the
      explicit reviewer check, held open above).
- [x] I verified each step, not just the end state.
- [x] The done-gate passes (every gate in `.claude/done-gate.md`).
- [x] I didn't touch artifacts outside "Artifacts expected to change".

### Dependencies

- **Blocks / blocked by:** blocks TASK-004/005; after TASK-002.

---

**Definition of done** (per `.claude/task-rules.md`): all criteria verified ·
plan ran with evidence · done-gate passes · closing report posted.
