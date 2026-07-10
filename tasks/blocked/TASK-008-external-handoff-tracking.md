---
id: TASK-008
category: spec
status: blocked
---

# TASK-008: Relay + track the external handoffs (kernel K1–K3 · frontend F1–F6)

## User story

As the **element maintainer**, I want **the kernel and frontend handoffs
relayed to their teams and their outcomes tracked back into our doctrine** so
the reactive-binding and 3D/animation capabilities land coordinated, and
KERNEL_ASKS stays a ledger of verified behaviors instead of hopes.

## Why this matters

Two of the design's four pillars (reflects-immediately, 3D/animation) are
external work. The handoffs are written and self-contained; what remains is
relay, response tracking, and folding verified outcomes back into `content/`
(the doctrine-truth rule: capability claims carry verification dates).

## Scope

**In scope:**
- Relay `docs/handoff/KERNEL_GAPS.md` to the kernel session and
  `docs/handoff/FRONTEND_RASAOS_GAPS.md` to the frontend-rasaos session
  (user carries them; this task tracks).
- Track: F2 (emission-grammar confirmations — if any differ, fix
  COMPONENTS.md + check-app in a linked follow-up task), F3 (component
  manifest → then build the check-doctrine lockstep check as a follow-up),
  K1+F1 (html-embed halves → then rewrite COMPONENTS.md §custom-visuals from
  "in flight" to the real contract, with verification date), K2 (bridge →
  flip `reactive:"live"` guidance + binding-model §9), K3 (direct edit path).
- Update `content/KERNEL_ASKS.md` entries with verified dates/versions as
  each lands.

**Out of scope (explicit):**
- Implementing any kernel/shell change ourselves (workspace role-split) ·
  nagging cadence decisions (the user owns team scheduling).

## References

- `docs/handoff/KERNEL_GAPS.md` (K1–K4 with acceptance criteria).
- `docs/handoff/FRONTEND_RASAOS_GAPS.md` (F1–F6, suggested order F2→F1→F3→F4).
- Done-gate "doctrine-truth rule" — the fold-back contract.

## Artifacts expected to change

- `content/KERNEL_ASKS.md` (verified-date updates as things land)
- `content/COMPONENTS.md` (only on F2 corrections or F1 landing — each via
  its own linked follow-up task per the change-audit rule)
- `docs/design/binding-model.md` §9 (reactive status flips)
- This task file (tracking log)

## Execution order

1. Confirm both handoffs relayed (user ack) → move this task to `blocked/`
   with "waiting on team responses" if idle.
2. On each response: log it here, file the follow-up task it triggers, update
   KERNEL_ASKS with the verified date.
3. Close when K1–K3 + F1–F4 are each either landed-and-folded or explicitly
   deferred by the user.

## Acceptance criteria

- [ ] Both handoffs relayed (user-confirmed).
- [ ] Every K1–K3/F1–F4 item has a tracked outcome: landed (with KERNEL_ASKS
      verified-date + doctrine fold-back task id) or user-deferred (noted).
- [ ] No content/ capability claim was updated without its verification
      evidence.

## Verification plan (per the done-gate)

1. **Setup:** the two handoff docs as the checklist.
2. **Checks:** per-item outcome table in this file; KERNEL_ASKS diff review.
3. **Done-gate run:** all gates.

## Manual verification (in addition to the done-gate)

1. User scans the outcome table and agrees it matches reality.

## Gotchas & learned lessons

- **This is the task most likely to sit in `blocked/`** — that's correct
  usage (external dependency, named blocker, check-back date), not abandonment.
- **Fold-backs are their own tasks** — don't smuggle COMPONENTS.md rewrites
  through this tracking task (change-audit rule).

## Open questions / risks

- Team bandwidth/sequencing — user's call; the handoffs carry suggested order.

## Blocker notes

**Blocked 2026-07-09** (external dependency, per task-rules "The blocked state"):

- **What's blocking:** waiting on the kernel + frontend-rasaos teams to pick up
  the delivered handoffs and respond (F2 confirmations first, then K1/F1 builds).
- **Who/what unblocks:** the user running a kernel or frontend-rasaos session
  against the delivered docs; any response re-activates this task.
- **Check back:** whenever either repo's session runs; also at each Phase-1
  ship (TASK-003/004 touch surfaces F2 could correct).

## Tracking log

- **2026-07-09 — relay executed** (pulled to active, step 1 done, parked
  blocked same day): delivered copies placed at
  `kernel/docs/handoff-domain-canvas-binding-gaps.md` and
  `frontend-rasaos/docs/handoff-domain-canvas-gaps.md`, each with a
  delivery header pointing at the canonical source in this repo. Neither
  repo's task registry was touched (their sessions own their IDs).
- **2026-07-09 — frontend-rasaos "wrote back"** (surfaced by the user): their
  checkout now sits on `main` at/past commit `a5f6ff1` ("v0.5.0 — the
  canvas-vertical lane + artifact studio + durable canvas store", authored
  2026-07-07 — PARALLEL work, predating our handoff). Verified directly
  against the current tree (`app/src/canvas/components.tsx`):
  - **F1 (html-embed) — effectively DONE, pre-existing**: an `HtmlEmbed`
    component renders BOTH `code-block{render:true}` (the kernel-legal
    carriage, `:64-68`) AND a direct `html-embed` arm (`:69-70`, pending
    kernel allowlist = K1). `sandbox="allow-scripts"`, srcDoc, injected CSP
    (`connect-src 'none'`, 4 CDNs + unsafe-eval, `:109-113`), injected
    `window.rasa.emit` postMessage bridge with `e.source` +
    `__rasa:1` envelope checks (`:136-141`), `height` default 420. Matches
    our html-embed-spec §B almost exactly (minor CSP deltas: style-src lacks
    esm.sh; no base-uri/form-action).
  - **F2 — RESOLVED by code-read**: button-row emits `intent || 'on_click'`
    `{button_id}` (`:429`) ✓; card-list emits LITERAL `'on_card_click'`
    `{card_index,title}` on prop presence (`:259`) ✓; form emits `'on_submit'`
    `{<id>:value}` (`:287`) ✓; enclosing region-level `on_click` confirmed by
    the stopPropagation comment (`:258`).
  - **All truth-pass prop shapes CONFIRMED against current main**:
    markdown-block `{content}` (`:407`), card `{title,subtitle}`, chart
    `{data}` bars-only, timeline `{events}`, media-viewer link-only, table
    dual shapes. Golden-app + check-app grammar fixes stand.
  - **⚠ OVER-CORRECTION FOUND**: our truth-pass claim "no artifact path
    exists" is FALSE for current main — the earlier render investigation read
    a different checkout state (uncited SHA — the lesson: pin `git rev-parse
    HEAD` in all cross-repo evidence). COMPONENTS §custom-visuals /
    BUILDER "do NOT author artifacts" / KERNEL_ASKS #3 "verified FALSE"
    correction all need re-correction → **HOTFIX-001 proposed**.
  - **Findings to send BACK to frontend team**: (1) Studio auto-binds
    `rasa.orchestrator.canvas` — STALE post-SA-023 name; must become
    `rasa.domain.canvas` (or honor the alias). (2) Their
    `VerticalCanvasPane` bootstraps cwd `.rasaos/apps/<id>` — coordinate
    before any TASK-006 dot-dir migration.
  - Also aligned independently: their "durable canvas store" hardening = our
    ask #6 workaround; they filed revert + history asks = our #7/#8.
- Outcome table: K1 ☐ (still needed — kernel enum for direct `html-embed`) ·
  K2 ☐ · K3 ☐ · **F1 ✅** (pre-existing in `a5f6ff1`; carriage live today) ·
  **F2 ✅** (resolved by direct code-read of current main) · F3 ☐ · F4 ☐.

## Self-review checklist

- [ ] I followed the execution order in the spec.
- [ ] Every acceptance criterion is met and individually verified.
- [ ] I verified each step, not just the end state.
- [ ] The done-gate passes (every gate in `.claude/done-gate.md`).
- [ ] I didn't touch artifacts outside "Artifacts expected to change".

### Dependencies

- **Blocks / blocked by:** independent to start; K2 unblocks live-reactive
  doctrine; K1+F1 unblock the 3D/animation contract rewrite.

---

**Definition of done** (per `.claude/task-rules.md`): all criteria verified ·
plan ran with evidence · done-gate passes · closing report posted.
