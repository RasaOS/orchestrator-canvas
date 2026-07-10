---
id: TASK-004
category: spec
status: completed
---

# TASK-004: The binding registry — `bindings[]` + `writes[]` contract + enforcement

## User story

As a **runtime session building UI on tenant data**, I want **a declarative
binding registry in `app.json`** so every region's data relationship (source,
shape, direction, reactivity) is declared, checkable, and survives session
handoff — requirement #2's foundation.

## Why this matters

Binding is the element's MAIN OBJECTIVE and today it's implicit (raw
`data_sources[]` + prose). The registry is what the kernel bridge (ask #11)
eventually consumes (registered-bindings target state) and what makes
"reflects on next EVENT → live" an upgrade instead of a rewrite. Design:
`docs/design/binding-model.md` §5 (ratified; OQ-4/OQ-7 resolved 2026-07-09).

## Scope

**In scope:**
- `schemas/rasa.app.v1.schema.json`: optional `bindings[]` + event `writes[]`
  (additive within v1 — no v2).
- `content/APP_MODEL.md`: the registry spec — binding row shape
  (`id/region/screen/source/shape/mode/direction/reactive/provisioned`),
  unique ids, `data_sources[]`-as-read-only-sugar, `select` v1 = `"*"` only,
  `reactive` default `on-event`.
- **The extended write-order law** (module-record writes → state → screen →
  app.json → canvas_set) in APP_MODEL + PROCESSES.
- **The resolved OQ-4 executor rule** in PROCESSES §EVENT: module-declared
  write procedure first; direct conventional writes only on `writable`
  collections; `writes[]` entries `{binding,op,field?}` | `{state}`.
- `bin/check-app`: binding ids unique · `source.module` resolves against
  `context.json` (warn when index absent) · `writes[].binding` names a real
  binding · `read-write` bindings have ≥1 writing event · binding regions
  exist on their screens.
- Golden app: one real binding + a `writes[]` event + its `context.json` row.
- (new fixture) `examples/fixtures/binding-unknown-module/` — **ships WITH a
  `context.json`** so the resolution check hard-fails (review #13).

**Out of scope (explicit):**
- The reactive bridge itself (kernel K2) · provision-mode doctrine
  (TASK-005) · any COMPONENTS.md change.

## References

- `docs/design/binding-model.md` §5 (registry + writes[] + executor rule +
  write-order law) + §8 (enforcement plan) + §11 resolved OQs.
- `docs/handoff/KERNEL_GAPS.md` K2 (what the kernel will consume).

## Artifacts expected to change

- `schemas/rasa.app.v1.schema.json`
- `content/APP_MODEL.md` · `content/PROCESSES.md`
- `bin/check-app`
- `examples/orders-desk/{app.json,context.json}`
- (new) `examples/fixtures/binding-unknown-module/**`
- `VERSION` + `rasa.json#version` + `CHANGELOG.md` (minor bump)

## Execution order

1. Schema additions; validate golden app.json against it.
2. APP_MODEL registry section + write-order law extension.
3. PROCESSES §EVENT executor rule (+ §gate mention of the new checks).
4. check-app checks; golden binding + event; new negative fixture.
5. Full gate (golden GREEN, all five fixtures RED); bump + CHANGELOG; commit.

## Acceptance criteria

- [x] Golden app declares ≥1 binding + a `writes[]` event and passes.
      *(Two bindings — tenant-read orders table + module read-write task-queue;
      the `task_logged` event writes both the bound collection and state;
      GREEN 0 fail 0 warn.)*
- [x] `binding-unknown-module` fixture FAILS check-app (not warns).
      *(FAIL: "source.module 'rasa.module.ghost' is not in
      context.json#modules" — index present, hard fail, per review #13.)*
- [x] All pre-existing fixtures still fail; check-doctrine GREEN.
      *(Five fixtures RED; gate GREEN ×2 incl. pre-commit.)*
- [x] Schema change is purely additive (old golden-shaped app.json without
      bindings still validates). *(All four pre-existing fixtures carry no
      bindings and pass the structural layer — their fails remain their named
      reasons; jsonschema lib absent, structural evidence per TASK-003 note.)*

## Verification plan (per the done-gate)

1. **Setup:** golden + fixtures as the test matrix.
2. **Checks:** each criterion → the corresponding check-app/check-doctrine
   run with output captured; additivity → validate a pre-change app.json copy.
3. **Done-gate run:** all gates; evidence in the closing report.

## Manual verification (in addition to the done-gate)

1. Reviewer reads the golden binding row and can trace region → source →
   writes → handling without any other context.

## Gotchas & learned lessons

- **The fixture must include `context.json`** or the module-resolution check
  only warns and the fixture passes (review #13).
- **Don't put a `phase:` or executor choice in binding rows** — the executor
  rule lives in PROCESSES; the registry stays executor-agnostic (resolved
  OQ-4).
- **`emits[]` region cross-checks already exist** — extend, don't duplicate.

## Open questions / risks

- None (OQ-4/OQ-6/OQ-7 resolved 2026-07-09).

## Blocker notes

(empty)

## Self-review checklist

- [x] I followed the execution order in the spec.
- [x] Every acceptance criterion is met and individually verified.
- [x] I verified each step, not just the end state.
- [x] The done-gate passes (every gate in `.claude/done-gate.md`).
- [x] I didn't touch artifacts outside "Artifacts expected to change".

### Dependencies

- **Blocks / blocked by:** blocked by TASK-003 (context.json exists); blocks
  TASK-005.

---

**Definition of done** (per `.claude/task-rules.md`): all criteria verified ·
plan ran with evidence · done-gate passes · closing report posted.
