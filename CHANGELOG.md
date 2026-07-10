# Changelog — rasa.domain.canvas

## 0.7.0 — 2026-07-09

**The SA-023 re-role lands (TASK-002) — domain identity everywhere.** The
v0.5.0 fold renamed only `rasa.json#name/#kind`; every other identity surface
still said "orchestrator." Now: CLAUDE.md (title + opener re-framed — per
SA-023 the tenant is the orchestrator via `rasa.tenant.core`; this element is
a domain that installs alongside sibling domains + modules, its sessions the
runtime brain of each canvas app), README.md (title + opener + session key),
this CHANGELOG's title, `rasa.json` prose (`session_model` keys on
`element=rasa.domain.canvas`; `tenant_model` composition target
`domain.canvas (how)`; scaffold description), and `content/KERNEL_ASKS.md`
headers (added to the task's artifact list mid-flight with justification —
self-description in content/). **`contract_version` 1.3.0 → 1.4.0** (SA-023
is a v1.4.0 amendment; the published schema already dropped `orchestrator` —
resolved OQ-5: flagged to the orchestrator-workspace session as the roster's
first 1.4.0 declarer, coordinate at the next conformance sweep). Historical
references (older CHANGELOG entries, canon SA citations) intentionally
preserved.

## 0.6.1 — 2026-07-09

**HOTFIX-001: the artifact lane is LIVE — doctrine restored.** v0.6.0's
truth-pass over-corrected: it forbade artifact regions ("nothing renders
them") based on a render investigation that read a frontend-rasaos checkout
WITHOUT commit `a5f6ff1` ("v0.5.0 — canvas-vertical lane + artifact studio",
authored 2026-07-07 in parallel). Verified against current `main`: the shell
ships `HtmlEmbed` — `code-block{render:true}` carriage + a direct
`html-embed` arm, `sandbox="allow-scripts"`, injected CSP (`connect-src
'none'`, 4 CDNs + unsafe-eval → three.js/WebGL/React work), injected
`window.rasa.emit` postMessage bridge — independently convergent with
docs/design/html-embed-spec.md §B. Restored: COMPONENTS.md §artifact (the
verified, SHA-pinned contract), BUILDER.md "declarative first, artifact when
it earns it", CLAUDE.md capsule; KERNEL_ASKS #3 re-verified TRUE with full
history (remaining ask = kernel allowlist/schema enum only, K1). All v0.6.0
prop-shape + emission-grammar fixes RE-CONFIRMED against `a5f6ff1` — those
stand. Done-gate doctrine-truth rule gains SHA-pinning for cross-repo
evidence. Postmortem:
docs/postmortems/2026-07-09-artifact-lane-overcorrection.md. Cross-repo
findings sent back via TASK-008: Studio auto-binds the stale
`rasa.orchestrator.canvas` name (post-SA-023 must be `rasa.domain.canvas`);
their VerticalCanvasPane bootstraps `.rasaos/apps/<id>` (coordinate before
any TASK-006 dot-dir migration).

## 0.6.0 — 2026-07-09

The truth pass + the binding design. The doctrine now matches the verified
platform. COMPONENTS.md rewritten to the shell's REAL contract (verified
against frontend-rasaos source 2026-07-09): the 11 rendered components'
actual prop shapes (`markdown-block{content}` not `{markdown}`;
`card-*{title,subtitle}`; `form` fields by `id` → `on_submit`;
`chart{data}` horizontal bars only; `timeline{events}`; `media-viewer`
link-only) + the real emission grammar (button-row emits
`intent || 'on_click'` — NOT the button id; `on_card_click`; `on_submit`;
region-level `on_click`). The §artifact escape hatch — which nothing
renders (no iframe/sandbox path exists in the shell; `code-block{render:true}`
is plain text) — replaced by §custom-visuals: honest status + the real path,
the sandboxed `html-embed` escape region (full implementable spec at
docs/design/html-embed-spec.md; 3D/animation stays a priority capability).
The nav contract gains `intent` (APP_MODEL + golden app + fixtures);
bin/check-app derives actions by the real grammar and warns on intent-less
buttons; golden app fixed (its markdown-block rendered EMPTY in the real
shell while the gate passed GREEN — the proof the enforcement gap is real);
schema `$id` → RasaOS/domain-canvas. KERNEL_ASKS: ask #3's false "the shell
already renders it sandboxed" claim corrected on the record; asks #11
(file-event → canvas bridge; nudge-session v1, registered-bindings target)
and #12 (direct edit → file write) filed. NEW `docs/`: the ratified design
corpus — binding-model.md (context index `rasa.canvas.context.v1`,
`bindings[]` + `writes[]` registry, three binding modes incl.
provision-then-bind, the extended write-order law, resolved OQ-1/4/7 + the
kernel-heavy/domain-light principle), ui-engine-and-architecture.md
(per-layer engine decisions, Brand-Kit tokens, canon doc-10 alignment,
conversational-canvas profile), html-embed-spec.md, BUILD_ORDER.md, and the
team handoffs docs/handoff/{KERNEL_GAPS,FRONTEND_RASAOS_GAPS}.md (delivered
copies placed in both repos 2026-07-09). NEW task system:
rasa.module.tasks v0.1.2 installed via its own bin/init — first
`requires.elements[]` dependency declared; `.claude/done-gate.md` authored
with this domain's real gates (check-doctrine GREEN + the doctrine-truth
rule: capability claims carry verified evidence); Phase 1 "The binding
brain — design → doctrine" registered with TASK-001..008 full specs
(TASK-001 ships as this release; TASK-008 relayed → blocked on team
responses). *Merge note: this release merges main's 0.5.1 + 0.5.2 (below),
which landed in parallel — their identity layer (`rasa.identity` +
`/whoami`) and kit-aware `bin/init` + `/sync` + `/promote` are included.*

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
