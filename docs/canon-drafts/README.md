# Canon drafts — authored here, filed from the canon-workspace session

Canon edits go through `canon/tasks/` (workspace rule). This element cannot
edit `canon/` directly, so canvas-motivated canon proposals are **drafted
here** and **filed by a canon-workspace session** (the user runs it). Each
draft is canon-triage-task-shaped and self-contained.

## To file (canon-workspace session)

1. Copy each `*.md` below into `canon/tasks/triage/`, assigning the real id
   (SA-NNN / DOC-NN-edit-*) in place of the `SA-0XX` / draft placeholders.
2. Record the assigned ids back here (and in the domain-canvas AUDIT) so the
   loop closes.

| Draft | Proposes | Status of the work it describes |
|---|---|---|
| `DOC-10-edit-html-embed-escape-region.md` | admit `html-embed` as the single sandboxed escape region + lock **FE-022** | shell half already IMPLEMENTED (frontend-rasaos @ `a5f6ff1`); kernel enum + FE-002 review outstanding |
| `SA-0XX-module-collections-declaration.md` | `provides.collections[]` — modules declare the record collections they own (+ `write_via`) | additive convention; interim seam-first discovery works without it |
| `SA-0XX-tenant-app-state-directory.md` | resolve `.rasa/` vs `.rasaos/apps/` (where tenant app-state lives) | interim: keep `.rasaos/apps/` (matches the live shell) |
| `canvas-SA-tracking-note.md` | *(not a task)* what domain-canvas needs SA-026/027/028 to preserve | reference note for the canvas-SA author |

## Provenance

All authored 2026-07-09 in the domain-canvas core-internal-structure session
(Phase 1, TASK-006 + TASK-007). Grounding + full specs live in this repo's
`docs/design/` and `docs/handoff/`.
