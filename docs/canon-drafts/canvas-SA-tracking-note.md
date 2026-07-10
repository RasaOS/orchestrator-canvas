# Tracking note — what rasa.domain.canvas needs from the canvas SAs

**Not a canon task** — a reference note for whoever authors SA-026/027/028
(the canvas model, still in `canon/tasks/triage/`). domain-canvas is the
reference consumer of these; this records what our doctrine relies on so the
canon authoring can honor it. Filed by the domain-canvas TASK-007 session,
2026-07-09.

## The canvas model is PRE-CANON — we invent on top of it

The word "canvas" does not appear in the LOCKED frontend spec (doc 10 v1.0.0).
The whole live-AI-authored-UI model lives in triage: SA-026 (ui-event type),
SA-027 (canvas API surface), SA-028 (spatial model), plus the two DOC-10-edits
(canvas components; frontend profiles). domain-canvas is the
`conversational-canvas` profile and builds its entire doctrine on this
unratified foundation. **We track these IDs; we do not cite the canvas model
as locked.**

## What our doctrine depends on (please preserve when authoring)

**From SA-026 (ui-event type):**
- The `ui` event on the command stream carries `canvas_id` (defaulting to
  session id) + a monotonic `version`. Our REBUILD/version discipline assumes
  monotonic versions with gap-detection.
- Interactions arrive as `[canvas] <action> (<region-id>)` turns. Our EVENT
  process and the whole `events[]`/`writes[]` registry are keyed on this.

**From SA-027 (canvas API surface):**
- `canvas_get` / `canvas_set` / `canvas_patch` + `GET /v1/canvas/{id}` +
  the `/watch` SSE stream. Our write-order law ends in `canvas_set`; our
  "files are truth, canvas is a projection" model assumes the store is
  re-derivable and the snapshot is authoritative on reload.
- The write-boundary validator (component allowlist + size caps). Our
  `bin/check-app` is the element-side pre-image of this; if the kernel adopts
  our published schemas (`rasa.app.v1`, `rasa.layout.v1`), the soft gate
  becomes a hard wall — desirable.

**From SA-028 (spatial model):**
- `frame{x,y,w,h}` absolute placement, z = document order. Our COMPONENTS.md
  documents this; the shell renders it (verified @ a5f6ff1).
- `PUT /v1/canvas/{id}/view` (measured geometry back to the kernel). Fixed
  `html-embed` height exists partly to keep this stable.

## Adjacent asks we've filed (see elements/domain-canvas/docs/handoff/)

- **KERNEL_GAPS.md** — the binding runtime: K1 (html-embed enum), K2
  (file-event → canvas bridge; nudge-session v1 → registered-bindings target,
  the kernel-heavy direction), K3 (direct edit → file write). These extend
  the SA-027 surface toward reactive two-way binding.
- **args.canvas_id** (KERNEL_ASKS #1) — named canvases; our multi-screen
  file model is already 1:1 ready for it.

## The domain-canvas contracts a canvas-SA author can reuse

- `schemas/rasa.app.v1.schema.json` — the app manifest (screens/events/
  bindings registries).
- `schemas/rasa.canvas.context.v1.schema.json` — the per-install context
  index.
- `docs/design/{binding-model,ui-engine-and-architecture,html-embed-spec}.md`
  — the ratified design.
