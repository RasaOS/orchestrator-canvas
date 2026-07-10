# Audit Log — rasa.domain.canvas

Curated, append-only record of meaningful project actions (per
`.claude/task-rules.md` → "Audit log"). Newest entries on top within a date.

## 2026-07-09

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
