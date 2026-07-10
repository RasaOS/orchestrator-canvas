# Postmortem — the artifact-lane over-correction (2026-07-09)

**Paired hotfix:** HOTFIX-001 (`tasks/completed/HOTFIX-001-restore-artifact-lane.md`).
**Severity:** high (doctrine-level; no tenant data affected).
**Window:** v0.6.0 tag → v0.6.1 (same day).

## What broke

The v0.6.0 "truth pass" shipped doctrine instructing every runtime session to
**never author artifact regions** ("nothing renders them") — while
frontend-rasaos `main` @ `a5f6ff1` had shipped the full artifact lane
(`HtmlEmbed`: `code-block{render:true}` carriage + direct `html-embed` arm,
sandbox + CSP + `window.rasa.emit` bridge) two days earlier. The doctrine
forbade a live, core-product capability (3D/animation — a hard user
requirement) and told sessions to say so to users on-canvas. It also
"corrected" KERNEL_ASKS #3's original TRUE claim into a false FALSE.

## Root cause

**Cross-repo verification against an unpinned checkout state.** The render
investigation grep'd/read `frontend-rasaos/app/src/canvas/` at a moment when
the working tree did not contain `a5f6ff1` (plausibly the
`audit/console-chat-thread-parity` branch state; the repo now sits on `main`
with `a5f6ff1` in ancestry). The findings were precise and internally
consistent — line-cited, 11 components, no iframe — and were folded into
doctrine the same day **without recording which commit had been read.** When
the checkout state changed, there was no way to notice the evidence had a
different baseline than the live tree.

Contributing factor: the original doctrine (v0.1.0–0.2.0) and the shell's
artifact lane were **co-designed in parallel on 2026-07-07**, so the doctrine
was *right* about a tree the investigator never saw — making the "fiction"
verdict feel like a clean catch instead of a branch-state artifact.

## What went right

- The enforcement instinct was correct even when the verdict was wrong: the
  same sweep caught real, still-confirmed drift (prop shapes, emission
  grammar, the golden app's dead region) — all of which held up against
  `a5f6ff1`.
- The module-tasks lifecycle caught the reversal cleanly: TASK-008's tracking
  surfaced the response; the hotfix lane shipped the correction same-day with
  an audit trail.
- The convergence itself: shell and spec independently arrived at the same
  sandbox/CSP/bridge design — the architecture is validated twice over.

## What changed to prevent recurrence

1. **SHA-pinning rule** (done-gate, doctrine-truth gate): cross-repo evidence
   must record the source repo's commit (`git -C <repo> rev-parse HEAD`)
   alongside every cite. Absence claims require a pinned state too.
2. **KERNEL_ASKS #3** now carries the full verification history (TRUE →
   wrongly-FALSE → re-verified TRUE @ SHA) rather than overwriting.
3. **F3 (generated component manifest)** in the frontend handoff gains
   urgency — a checked-in, versioned manifest of the real renderer contract
   makes "which tree did you read" a diffable fact. (Tracked in TASK-008.)

## Action items (all tracked)

- HOTFIX-001 — restore the artifact doctrine (shipped, v0.6.1). ✅
- TASK-008 — send-backs to frontend: stale `rasa.orchestrator.canvas`
  auto-bind in Studio; `.rasaos/apps` coordination. (blocked/tracking)
- Follow-on to file: golden-app artifact example + `html-embed` check-app
  coverage post-K1 (noted in HOTFIX-001 §follow-ups).
- K1 (kernel enum) — the only remaining blocker for the direct form.
