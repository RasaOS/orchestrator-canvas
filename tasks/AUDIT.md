# Audit Log — rasa.domain.canvas

Curated, append-only record of meaningful project actions (per
`.claude/task-rules.md` → "Audit log"). Newest entries on top within a date.

## 2026-07-09

- 📦 **TASK-007 shipped** — canon drafts authored (docs/canon-drafts/):
  DOC-10-edit-html-embed-escape-region (FE-022), SA-0XX-module-collections-
  declaration (provides.collections[] + write_via), + the canvas-SA tracking
  note; README indexes all four (incl. TASK-006's dot-dir SA) with the
  file-from-canon-session procedure. Filing DEFERRED to the canon-workspace
  session (element can't edit canon/). Docs-only.
- 🏗 **Phase 1 "The binding brain" COMPLETE** — all element-side tasks
  shipped (TASK-001..007 + HOTFIX-001); TASK-008 remains blocked on external
  teams. Requirements #1-4 built + enforced. Elements v0.6.0 → v0.10.0.
- 📦 **TASK-005 shipped** — the three binding modes (bound / derived /
  provision-then-bind) folded into BUILDER §binding-modes + PROCESSES
  (BUILD mode-resolution step, ADD_SCREEN bindings, RETIRE provisioned-records
  addendum). Process canon unchanged; BUILDER 7.2KB. Receipt: tag v0.10.0.
- 📦 **TASK-004 shipped** — the binding registry: `bindings[]` + events
  `writes[]` (additive in rasa.app.v1), the OQ-4 executor rule in §EVENT,
  the extended write-order law, full check-app cross-checks, golden app
  exercising tenant-read + module-read-write bindings, new
  `binding-unknown-module` fixture (ships WITH context.json → hard-fails).
  Receipt: tag v0.9.0.
- 📦 **TASK-003 shipped** — the context index: AUDIT becomes the eighth named
  process (structural three-flavor detection — dry-run verified against the
  real workspace as canon-author; seam-first discovery; typed fields);
  `rasa.canvas.context.v1` schema published; check-app validates
  `context.json`; golden app carries a valid index. Receipt: tag v0.8.0.
- 📦 **TASK-006 shipped** — dot-dir reconciliation decided (user): keep
  `.rasaos/apps/` (matches the live shell @ `a5f6ff1`); the platform-naming
  question drafted for canon
  (docs/canon-drafts/SA-0XX-tenant-app-state-directory.md, rides TASK-007).
  Docs-only; receipt: commit SHA in the closing report.
- 📦 **TASK-002 shipped** — the SA-023 re-role: domain identity on every
  surface (CLAUDE/README/CHANGELOG titles, rasa.json prose + session key,
  KERNEL_ASKS headers); `contract_version` → 1.4.0 (first 1.4.0 declarer in
  the roster — workspace flagged). Receipt: tag v0.7.0.
- 🔥 **HOTFIX-001 shipped** — restored the artifact-lane doctrine: v0.6.0 had
  forbidden a working capability (frontend-rasaos @ `a5f6ff1` ships the full
  sandboxed artifact lane; the "absent" verdict came from an unpinned
  checkout). Receipt: tag v0.6.1.
  Postmortem: docs/postmortems/2026-07-09-artifact-lane-overcorrection.md.
- ⚠ **Postmortem: artifact-lane over-correction** — root cause: cross-repo
  verification against an unpinned checkout state; prevention: SHA-pinning
  rule added to the done-gate's doctrine-truth gate; F3 (component manifest)
  urgency raised. docs/postmortems/2026-07-09-artifact-lane-overcorrection.md.
- 📦 **TASK-001 shipped** — the truth-pass + design corpus + task system,
  released as **v0.6.0** (tag on the merge-with-main commit so the release
  contains main's v0.5.1/v0.5.2). Receipt: tag `v0.6.0`.
- 🚀 **v0.6.0 released** — doctrine now matches the verified platform
  (COMPONENTS real shapes + emission grammar, §custom-visuals honesty,
  nav-intent, check-app grammar); design corpus + handoffs shipped;
  module-tasks installed; Phase 1 registered. Receipt: tag `v0.6.0`.
- 🏗 **Handoffs relayed (TASK-008 → blocked)** — delivered copies placed at
  `kernel/docs/handoff-domain-canvas-binding-gaps.md` and
  `frontend-rasaos/docs/handoff-domain-canvas-gaps.md`; task parked blocked
  on team responses.
- 🏗 **Task system installed** — `rasa.module.tasks` v0.1.2 installed via its
  `bin/init` (module SHA `8d83b0cf3d09`); `.claude/` toolkit + `tasks/`
  lifecycle tree seeded; `kit/` stash gitignored; dependency declared in
  `rasa.json#requires.elements`.
- 📜 **Done-gate defined** — `.claude/done-gate.md` filled with this domain's
  real gates: check-doctrine GREEN, the doctrine-truth rule (capability claims
  carry verified evidence — lesson of the 2026-07-09 artifact-fiction finding),
  design-doc consistency, ship-shape version plumbing, gated-file review.
- 🏗 **Phase 1 registered** — "The binding brain — design → doctrine" in
  `tasks/ROADMAP.md` with TASK-001..TASK-008 (spec category, full contracts),
  covering: ship v0.6.0 · SA-023 re-role · context index + AUDIT procedure ·
  bindings[] contract · three-modes doctrine · dot-dir reconciliation · canon
  drafts · external-handoff tracking.
