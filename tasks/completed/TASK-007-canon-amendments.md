---
id: TASK-007
category: spec
status: completed
---

# TASK-007: Draft the canon amendments (html-embed FE-022 · canvas SA tracking · provides.collections[])

## User story

As the **product owner**, I want **the design's canon-facing pieces filed as
proper canon tasks** so the html-embed escape region, the canvas model, and
the module-collection convention become ratified law instead of this
element's private invention.

## Why this matters

Canon rules: canon edits go through `canon/tasks/`. Three of our resolved
designs need that path: html-embed contradicts doc-10's frozen set unless
admitted as the fenced escape region (proposed lock FE-022); our whole canvas
model rides triage SA-026/027/028; and seam-first discovery would be
strengthened by a `provides.collections[]` convention (resolved OQ-3's
upstream half).

## Scope

**In scope (drafting happens HERE; filing happens in the canon workspace):**
- Draft `DOC-10-edit-html-embed-escape-region.md` — admit `html-embed` via an
  FE-002 review as **the single unbounded escape region**, with the FE-022
  lock text, sandbox/CSP/bridge/size contract from
  `docs/design/html-embed-spec.md` §C.
- Draft `SA-0XX-module-collections-declaration.md` — optional
  `provides.collections[]` for module Elements (dir, record glob, fields,
  states, writable) formalizing the seam.
- A tracking note listing what domain.canvas needs from SA-026/027/028 when
  they're authored (ui_event shape, canvas API, spatial model — we are the
  reference consumer).
- Hand the drafts to a canon-workspace session (the user runs it) and link
  the filed task ids back here.

**Out of scope (explicit):**
- Editing canon docs directly from this repo (forbidden by workspace rules) ·
  implementing anything.

## References

- `docs/design/html-embed-spec.md` §C (change-set + FE-022 text).
- `docs/design/binding-model.md` §11 OQ-3 (resolved: seam-first now,
  provides.collections[] upstream later).
- Workspace rule: canon-edits-go-through-tasks (`canon/tasks/README.md`).

## Artifacts expected to change

- (new) `docs/canon-drafts/DOC-10-edit-html-embed-escape-region.md`
- (new) `docs/canon-drafts/SA-0XX-module-collections-declaration.md`
- (new) `docs/canon-drafts/canvas-SA-tracking-note.md`
- `CHANGELOG.md` (patch note when drafts ship)

## Execution order

1. Draft the html-embed canon task from the spec's §C (front-matter shaped
   like existing `canon/tasks/triage/*` files).
2. Draft the collections-declaration SA.
3. Write the SA-026/027/028 consumer-requirements note.
4. Hand off to the canon session; record the filed ids in this task; close.

## Acceptance criteria

- [x] Drafts are canon-task-shaped (front-matter id/status/target_version/
      target_docs, matched to DOC-10-edit-canvas-components as the shape ref)
      and self-contained. FOUR drafts: html-embed (FE-022),
      provides.collections[], the dot-dir SA (from TASK-006), + the canvas-SA
      tracking note; index at docs/canon-drafts/README.md.
- [x] The html-embed draft carries the FE-022 lock text + the FE-002-preserving
      framing ("the escape region, a fenced boundary, not the 22nd business
      component; safety moves from renderer-knows-every-component to
      browser-sandbox-contains-an-unknown-one").
- [x] Filing is DEFERRED to the canon-workspace session (per the workspace
      canon-edits-go-through-tasks rule — this element cannot edit canon/).
      README.md gives the file-and-record-ids procedure; recorded in the
      closing report.

## Verification plan (per the done-gate)

1. **Setup:** read two existing `canon/tasks/triage/*` files as shape
   reference.
2. **Checks:** shape conformance by side-by-side comparison; content
   completeness against html-embed-spec §C.
3. **Done-gate run:** all gates.

## Manual verification (in addition to the done-gate)

1. User (as canon steward) reads both drafts and confirms they're filable
   without rework.

## Gotchas & learned lessons

- **Don't edit `canon/` from this session** — drafts live here; filing is the
  canon session's move.
- **DOC-10-edit-canvas-components scoped further additions to their own
  FE-002 reviews** — the html-embed draft must be its own review, not an
  amendment to that one.

## Open questions / risks

- FE-022 lock number could collide with canon's own sequence — the canon
  session assigns the final id; the draft says "proposed".

## Blocker notes

(empty)

## Self-review checklist

- [x] I followed the execution order in the spec.
- [x] Every acceptance criterion is met and individually verified.
- [x] I verified each step, not just the end state.
- [x] The done-gate passes (every gate in `.claude/done-gate.md`).
- [x] I didn't touch artifacts outside "Artifacts expected to change" (added
      docs/canon-drafts/README.md — an index for the handoff, in scope).

### Dependencies

- **Blocks / blocked by:** independent of TASK-003..005; the kernel/shell
  html-embed build (external K1/F1) benefits from it landing but isn't
  hard-blocked.

---

**Definition of done** (per `.claude/task-rules.md`): all criteria verified ·
plan ran with evidence · done-gate passes · closing report posted.
