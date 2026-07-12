---
id: TASK-011
category: release
status: backlog
priority: critical
---

# TASK-011: Reconcile the divergent `main` line + get this (canonical) line onto the remote

## User story

As the **element maintainer**, I want **this v0.11.0 development line pushed to
the remote and reconciled with the stale `main` line** so the real current
domain-canvas (binding registry, three-modes doctrine, the corrected component
doctrine) is not lost, and there is ONE canonical line the kernel mounts and the
workspace REGISTRY tracks.

## Why this matters (discovered 2026-07-11, frontend-rasaos canvas session)

The repo has **two divergent lines off the v0.5.2 commit `dd139a1`**:

- **`main`** — was stale at v0.5.2. A frontend-rasaos wiring audit
  (`elements/frontend-rasaos/docs/audits/2026-07-11-canvasos-wiring-audit.md`)
  independently caught that `content/COMPONENTS.md` prop keys had drifted from
  the shell renderer, and a fix was landed on `main` as **v0.5.3** (commit
  `5c2ce61`, tag `v0.5.3`, pushed). The workspace REGISTRY + track-2 were
  bumped to 0.5.3.
- **THIS branch `claude/core-internal-structure-12c464`** — the real, active,
  task-tracked line: **v0.6.0 → v0.11.0** (TASK-001..010, the binding-registry
  contract TASK-004, three-modes doctrine TASK-005, hardened `check-app`, …).

**The redundancy:** this line's `content/COMPONENTS.md` ALREADY has the correct
keys the v0.5.3 main-line fix just re-derived — `markdown-block{content}`,
`chart{data:[{label,value}]}`, `timeline{events}`, `form{fields:[{id,…}]}`,
`card{subtitle}`, `media-viewer{src}` link-only. So the v0.5.3 doctrine content
needs **no careful preservation** here; this line is already correct. (One
residual nit — see Scope.)

**The risk (CRITICAL):** `git ls-remote origin` shows the remote has branches
`main` / `canvas-doctrine-reconcile` / `claude/deliver-kernel-gaps-reply` and
tags only up to **v0.5.3**. This branch and its tags **v0.6.0–v0.11.0 are
LOCAL-ONLY — never pushed.** ~6 versions of the canonical line exist in a single
worktree on one machine. A disk failure or `git worktree remove` loses all of
it. (If TASK-011 was pushed with the branch, this file is itself the proof it
was backed up.)

## Scope

**In scope:**
- **Push this branch + its tags to `origin` FIRST** (backup before anything
  else): `git push -u origin claude/core-internal-structure-12c464` and
  `git push origin v0.6.0 v0.6.1 v0.7.0 v0.8.0 v0.9.0 v0.10.0 v0.10.1 v0.11.0`.
- **Decide the canonical line + merge direction.** Evidence says THIS line is
  canonical (advanced, task-tracked, doctrine-correct). Bring `main` up to it —
  merge this → `main` (expect a trivial conflict/supersession against the lone
  v0.5.3 commit `5c2ce61`, whose doctrine content is already here) — or, if
  `main` is to be retired as a line, document that.
- **Fix the one residual doctrine nit on this line:** `COMPONENTS.md` documents
  the form emit as `on_submit`, but the shell renderer emits **`submit`**
  (verified live; frontend-rasaos v0.8.10 `components.manifest.json` fixed the
  same drift). Correct it here.
- **Version/tag hygiene:** the numbering is tangled (`main` carries a lone
  v0.5.3; this line runs to v0.11.0). Pick coherent post-merge versioning and
  retag if needed.
- **Update the workspace surfaces** after reconcile: `elements/REGISTRY.md` row
  + `elements/CHANGELOG.md` (track-2) to the reconciled version (currently
  they say 0.5.3, tracking `main`).
- **Confirm the kernel mount.** The kernel loads `elements/domain-canvas` from
  its working tree (read-only mount). It is currently checked out on `main`
  (v0.5.3) — so the running builder is missing all v0.6–v0.11 doctrine. After
  reconcile, ensure the mounted checkout is the canonical line.

**Out of scope:**
- The doctrine content itself (already correct on this line).
- The frontend renderer aliases (shipped, frontend-rasaos v0.8.10).

## Cross-ref

- `TASK-008` (this branch) already anticipated relaying + folding the frontend
  F-handoffs — this is the concrete reconciliation it foresaw.
- frontend-rasaos: audit `docs/audits/2026-07-11-canvasos-wiring-audit.md`;
  doctrine fix (main) `RasaOS/domain-canvas` PR #2 / tag `v0.5.3`; renderer
  aliases v0.8.10; workspace bump `RasaOS/rasa-tenant` PR #2.
