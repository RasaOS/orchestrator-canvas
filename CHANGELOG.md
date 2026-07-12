# Changelog — rasa.orchestrator.canvas

## 0.5.3 — 2026-07-11

### Reconcile COMPONENTS.md prop keys to the shell renderer (canvas wiring audit)

The 2026-07-11 CanvasOS wiring audit (frontend-rasaos
`docs/audits/2026-07-11-canvasos-wiring-audit.md`) found the doctrine's
documented prop keys had drifted from what the shell renderer actually reads —
so a layout authored strictly to `content/COMPONENTS.md` rendered **empty**
(no error tile — the kernel validates only the component name). Every drifted
component reconciled to the renderer's canonical key:

- **markdown-block** `{markdown}` → `{content}`
- **chart** `{type, series/points, labels}` → `{data: [{label, value}]}`
- **timeline** `{items: [{label, detail?, at?}]}` → `{events: [{at, label}]}`
- **form** field key `{name}` → `{id}`, and the emitted action stated as `submit`
  with `{<field-id>: value}` (an empty-`name` form was silently submitting `{}`)
- **card-strip / card-list** `{cards: [{body?/description?}]}` → `{subtitle?}`;
  card-strip documented as presentational-only (its `on_click` was dead), the
  per-card `on_click` VALUE named as the emitted action
- **media-viewer** doctrine corrected — renders an http(s) `src` as a link only,
  never an inline/`data:` image

The frontend shipped matching renderer aliases (v0.8.10) so layouts authored to
the OLD doctrine degrade gracefully instead of blanking; this change fixes the
authoring source so new builds are correct at the root.

## 0.5.2 — 2026-07-09

### Element identity layer (canon SA-025)

- Added `rasa.identity` ("the RasaOS domain for building canvas-vertical UIs"); `bin/init` generates `.claude/rasa-identity.md` from it every install + stamps project-owned `.claude/rasa-deployment.md`; ships `/whoami`; CLAUDE.md "Who you are" header.

## 0.5.1 — 2026-07-09

### Added generic `/sync` + `/promote` + `/kit`-aware `bin/init` (canon SA-024)

- `bin/init` now clones the Element source into `<project>/kit/<element>/`; `/sync` smart-pulls upstream, `/promote` smart-pushes local edits back upstream (both directory-mirror → installed into consumers).

## 0.5.0 — 2026-07-09

### Folded to `rasa.domain.canvas` (canon SA-023)

- The `orchestrator` kind was folded into `tenant`; this vertical-builder Element becomes a domain. Renamed rasa.orchestrator.canvas → rasa.domain.canvas; folder orchestrator-canvas → domain-canvas. Content re-role is a follow-up.

## 0.4.0 — 2026-07-08

The enforcement layer. The law is now machine-checked.
`schemas/rasa.app.v1.schema.json` publishes the app-manifest contract.
`bin/check-app <app-dir>` audits an app directory against APP_MODEL.md:
registries exhaustive both ways, event coverage (button-row ids, card
on_click, form submit, `rasa.emit` scans inside artifacts), nav contract +
targets, screen.name identity (newly codified: layout `screen.name` equals
the screen id), size budgets, state/data hygiene. `bin/check-doctrine`
audits the doctrine itself: the seven process names across
PROCESSES/BUILDER/CLAUDE, COMPONENTS.md ↔ `bin/_contract.py` component
lockstep, version plumbing (VERSION == rasa.json == CHANGELOG), schema
parses, BUILDER terseness, and the fixture gate — `examples/orders-desk`
(golden reference app) must pass and all four `examples/fixtures/*`
negatives (orphan-screen, missing-screen-file, unregistered-event,
bad-active-screen) must fail. Authoring-time teeth: `.githooks/pre-commit`
+ GitHub Actions run check-doctrine on every commit/PR. Runtime teeth:
PROCESSES.md gains §gate — every publishing process runs check-app between
the file writes and canvas_set; RED blocks the publish (BUILDER.md
discipline + APP_MODEL.md §enforcement updated). Kernel asks #9 (stable
element-mount handle, e.g. RASA_ELEMENT_ROOT) and #10 (kernel-side
manifest/layout validation adopting the published schema) filed.

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
