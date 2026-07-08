# Changelog — rasa.orchestrator.canvas

## 0.3.0 — 2026-07-07

The strict app model. content/ now defines the whole vertical lifecycle so
any session can take over an app cold. New: APP_MODEL.md — the app IS its
directory (`app.json` manifest spec with exhaustive `screens[]` + `events[]`
registries, `screens/` one-file-per-screen, `state/`, per-app CHANGELOG);
files-are-truth / Redis-is-a-projection persistence with the write-order law
(screen file → app.json → canvas_set); three-clock versioning (canvas /
app / element); multi-screen via active-screen projection + the `button-row`
nav contract (`nav:<screen-id>`), 1:1 ready for `args.canvas_id`. New:
PROCESSES.md — seven named procedures (BOOTSTRAP, BUILD, EVENT,
SWITCH_SCREEN, ADD_SCREEN, REBUILD, RETIRE) with exact ordered steps.
BUILDER.md rewritten around the three mandates (create/manage vertical UIs ·
real-time co-building on tenant data · run-by-the-book) and now routes every
turn through a named process; real-time co-building doctrine added (scan
before authoring, bind don't decorate, publish early, ask on-canvas).
COMPONENTS.md untouched (renderer lockstep preserved). CLAUDE.md rewritten
to embody the full mission in-context: the four mandates, the two hats
(runtime vs authoring sessions), and the core model in capsule form, so any
session opening this repo knows the whole picture immediately.

## 0.2.0 — 2026-07-07

Artifact ergonomics. COMPONENTS.md §artifact gains two batteries-included
starter kits — preact+htm (preferred, no build/eval, ~12KB) and React 18 +
JSX via Babel-standalone (full parity; the shell CSP already allows
`unsafe-eval`) — so interactive UI is authored with a component framework, not
hand-rolled DOM. Clarified the size rule: the ~10KB budget is the *authored
document*; CDN libraries load at runtime and don't count (which is what makes a
React/three.js app viable in the carriage). Also encoded tenant-residency in
BUILDER.md ("The tenant model") + rasa.json `tenant_model`.

## 0.1.0 — 2026-07-07

Foundation. The vertical-builder doctrine (BUILDER.md), the component +
artifact contract matching the shell renderer (COMPONENTS.md — 21-component
kernel allowlist, artifact lane via sandboxed iframe + window.rasa.emit
bridge, CDN allowlist for libraries incl. three.js/WebGL), and the platform
asks (KERNEL_ASKS.md). Session model: one app = one session keyed by the
app's workspace directory under <workspace>/.rasaos/apps/.
