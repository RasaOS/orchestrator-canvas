---
id: HOTFIX-001
category: hotfix
status: completed
severity: high
filed: 2026-07-09
---

# HOTFIX-001: v0.6.0 doctrine forbids the artifact lane — which works

## What's broken in the live state

The shipped v0.6.0 doctrine (`content/COMPONENTS.md` §custom-visuals,
`content/BUILDER.md`, `CLAUDE.md`, `KERNEL_ASKS.md` #3's "verified FALSE"
note) instructs every runtime session to **never author artifact regions**,
claiming "nothing renders them." Verified against frontend-rasaos `main` at
commit `a5f6ff1` (2026-07-09 re-check): **the artifact lane renders** — an
`HtmlEmbed` component serves `code-block{render:true}` (kernel-legal
carriage, `components.tsx:64-68`) and a direct `html-embed` arm (`:69-70`),
with `sandbox="allow-scripts"`, injected CSP (`connect-src 'none'`, 4 CDNs +
unsafe-eval), and the `window.rasa.emit` postMessage bridge (`:109-145`).
Effect: every canvas app session is steered away from a live, core-product
capability (3D/animation — a hard user requirement). Root cause: the render
investigation read a checkout state without `a5f6ff1` and its findings were
folded into doctrine without pinning the source SHA.

## Why this is a hotfix and not a bug

The operative doctrine is live-wrong for every install NOW: sessions are
actively mis-instructed to refuse/avoid a capability the product owner named
as critical, and to tell users on-canvas that it "isn't available." That is
degraded live behavior on the element's primary surface, user-green-lit for
immediate correction ("green lit!", 2026-07-09).

## The smallest fix

### What the fix changes
- `content/COMPONENTS.md` — §custom-visuals → **§artifact** restored: the
  verified contract (carriage + direct arm, props, CSP, bridge, budgets,
  rules), SHA-pinned to `a5f6ff1`.
- `content/BUILDER.md` — restore "declarative first, artifact when it earns
  it" + artifact discipline lines.
- `CLAUDE.md` — the "in flight" line → live-via-carriage (gated file;
  user green-lit this hotfix explicitly).
- `content/KERNEL_ASKS.md` #3 — append the 2026-07-09 re-verification: the
  earlier "verified FALSE" correction was itself wrong (stale checkout);
  remaining ask is the kernel allowlist/schema enum only (K1).
- `docs/design/html-embed-spec.md` + `ui-engine-and-architecture.md` —
  status: shell half IMPLEMENTED (deltas noted).
- `.claude/done-gate.md` — doctrine-truth gate gains the SHA-pinning rule
  (gated file; green-lit).
- Patch release 0.6.1 (VERSION + rasa.json + CHANGELOG same commit) + tag.

### What this fix does NOT do *(deliberate)*
- No component-list changes (`_contract.py` lockstep untouched — `html-embed`
  stays out of KERNEL_ALLOWLIST until the kernel enum lands; the carriage is
  the kernel-legal form).
- No golden-app artifact example, no check-app changes (budgets/EMIT scans
  already handle the carriage) — a golden artifact example is a follow-on.
- No re-litigation of the prop-shape/emission fixes — all re-confirmed
  correct against `a5f6ff1`.

## Artifacts expected to change

- `content/COMPONENTS.md` · `content/BUILDER.md` · `content/KERNEL_ASKS.md`
- `CLAUDE.md` ⚠ gated (green-lit) · `.claude/done-gate.md` ⚠ gated (green-lit)
- `docs/design/html-embed-spec.md` · `docs/design/ui-engine-and-architecture.md`
- `VERSION` · `rasa.json` (#version) · `CHANGELOG.md` · `tasks/AUDIT.md`
- (new) `docs/postmortems/2026-07-09-artifact-lane-overcorrection.md`

## Verification

1. **Reproduce on pre-fix state:** `grep -n "do NOT author" content/*.md` →
   hits in COMPONENTS/BUILDER; KERNEL_ASKS #3 says "verified FALSE".
2. **Apply the fix.**
3. **Re-run:** the grep returns nothing; COMPONENTS §artifact carries the
   `a5f6ff1` SHA-pinned contract; KERNEL_ASKS #3 carries the re-verification.
4. **Sanity-check adjacent:** `bin/check-doctrine` GREEN (lockstep lists
   untouched, version plumbing at 0.6.1, golden passes, fixtures fail).

## Rollback plan

- **How to revert:** `git revert` the hotfix commit (single commit); tag
  v0.6.1 deleted locally if not yet pushed.
- **State after rollback:** back to v0.6.0's wrong-but-consistent doctrine;
  no new regressions.
- **Who can authorize:** the user, on this channel.

## Post-fix follow-ups

- TASK-XXX (to be filed) — golden-app artifact example + check-app coverage
  for a direct `html-embed` region (post-K1).
- Already tracked: TASK-008 send-backs (stale `rasa.orchestrator.canvas`
  auto-bind in Studio; `.rasaos/apps` coordination for TASK-006); K1 kernel
  enum.

## Postmortem

`docs/postmortems/2026-07-09-artifact-lane-overcorrection.md` (written with
this fix; action items link tracked tasks).

## AUDIT entry *(when shipped)*

```
- 🔥 **HOTFIX-001 shipped** — restored the artifact-lane doctrine (v0.6.0 had
  forbidden a working capability). Receipt: tag v0.6.1.
  Postmortem: docs/postmortems/2026-07-09-artifact-lane-overcorrection.md.
```
