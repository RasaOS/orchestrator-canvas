# Changelog — rasa.domain.canvas

## 0.8.0 — 2026-07-13

Harvest the data-binding subsystem from the v0.11 line onto the enforcement +
nav foundation — the element's main objective (bind canvas UIs to tenant data,
two-way), re-applied as orthogonal deltas rather than a branch merge.

- **`bindings[]` registry** in `app.json` + `events[].writes[]` — one row per
  bound region (`source` = a sibling module's collection | a tenant file | a
  `context` query; `mode` bound/derived/provision; `direction` read/read-write;
  `reactive` on-event/live). Published in `schemas/rasa.app.v1.schema.json`
  (additive within v1).
- **`context.json` — the per-install binding index** (`rasa.canvas.context.v1`,
  new published schema) written by the new **AUDIT** process (8th): walks the
  tenant + sibling modules seam-first, recording each module's collections (dir,
  shape, fields, states, `writable`).
- **Three binding modes** (BUILDER §binding-modes) + the **extended write-order
  law** (bound-collection writes → state → screen → app.json → canvas_set) +
  the **EVENT executor rule** (module-declared write procedure first; direct
  writes only on `writable` collections).
- **check-app** gains `check_context` / `check_bindings` / `check_writes` (ids
  unique, source resolves in `context.json`, read-write has a writer, tenant
  paths contained) — orthogonal to the layout + nav passes.
- Golden `orders-desk` gains two bindings (tenant-read + module read-write) +
  `context.json`; new negative fixture `binding-unknown-module`.
- `provides.collections[]` filed as a canon proposal (`RasaOS/canon` — not yet
  ratified).

## 0.7.0 — 2026-07-13

Smart-merge of the page-creation nav standard onto the Phase-B/C enforcement
foundation (branch `claude/page-creation-standards-c5e7c9`). The two are
complementary — real-contract enforcement (how a screen is drawn) + the nav
topology that scales multi-screen apps — reconciled into one gate.

- **Nav contract: sections mesh, leaves climb** — replaces the old full-mesh nav
  (which blew up N² on per-record detail screens). An optional `screens[].parent`
  splits screens into SECTIONS (no parent — co-equal tabs meshing to peers) and
  LEAVES (a detail/step whose `nav` carries only ancestor back-links, default one
  back button); parent graph acyclic + rooted. Forward/lateral jumps live in
  content regions and their `events[]` row carries `target:<screen-id>`. Every
  leaf must be reachable (a forward `nav:` link or an `events[].target`) — a dead
  leaf FAILs. Lands across check-app + APP_MODEL §multi-screen + BUILDER + the
  rasa.app.v1 schema (`parent`/`target`).
- **card-strip `on_click` is a dead handler → hard FAIL** (the shell renders
  card-strip clicks inert; use card-list). Dropped from the event harvest too.
- New golden `examples/task-backlog` demonstrates LIST_DETAIL (`card-list`
  `open:<id>` → detail leaves) and passes check-app AND the real kernel
  `validateLayout`; check-doctrine now gates every golden. Five new nav fixtures
  (`leaf-missing-back`, `leaf-nav-to-sibling`, `parent-cycle`, `unreachable-leaf`,
  `card-strip-onclick`). The design spec lands in `docs/page-creation-standard.md`.
- **Staged for a follow-up authoring pass (NOT in this merge):** the LIST_DETAIL
  pattern → `content/PATTERNS.md`, the SCAFFOLD process, and the `open:*` gate
  invariant (see `docs/page-creation-standard.md` §1–4).

## 0.6.1 — 2026-07-12

Phase C hardening — the remaining gate + recovery gaps.

- **data_sources tenant-containment** (check-app): reject absolute paths and
  paths that escape the tenant root (>3 levels up from the app dir). Was
  doctrine-only and unenforced (security-adjacent). New fixture `data-source-escape`.
- **Write-order is an order, not a transaction** (APP_MODEL): the non-atomicity
  is documented honestly; REBUILD gains an integrity pass (`check-app` on session
  start) so a fresh or interrupted session repairs the directory to GREEN before
  trusting the canvas — files-are-truth recovery, not atomicity.
- **Gate bypass is loud now** (PROCESSES §gate): an unreachable-mount publish must
  announce itself UNCHECKED, hand-verify the envelope, and re-check next turn
  (closes fully when KERNEL_ASKS #9 lands).

## 0.6.0 — 2026-07-12

Reconciled to canon — the enforcement layer now validates the REAL kernel
contract. Ground truth (kernel + frontend-rasaos + RasaOS/schema on disk) showed
the doctrine validated a fictional flat-regions layout the kernel would reject;
canon v1.4.0 absorbed the canvas family (doc 10 v1.1: the layout_grid+slot
envelope, 22 components incl. html-embed, per-profile Appendix B incl. the B.2
canvas dialect; Spec §56), and this release conforms the element to it.

- **Vendored `schemas/rasa.layout.v1.json`** (== RasaOS/schema 0.3.0 == kernel).
  check-app loads its constraint values so it cannot drift from the published schema.
- **check-app is a real gate now.** GREEN means "canvas_set accepts this AND it
  renders": required `screen.layout_grid` + region `slot`, name/id `^[a-z][a-z0-9-]*`,
  title ≤60; components HARD-failed against the real 12-name allowlist (was 21 + a
  soft warn); kernel `validator.ts` caps (256KB layout / 64 regions / dup-region-id —
  the old 32KB is now a soft density warn); per-component required props (canon
  Appendix B.2). Golden passes check-app AND the real kernel `validateLayout`.
- **Allowlist 21→12** in `_contract.py` + COMPONENTS.md; allowlist == shell-rendered;
  non-allowlisted is rejected, not error-tiled. `html-embed` is first-class.
- **Doctrine text reconciled** (COMPONENTS.md): canonical prop keys (content, id,
  `data:[{label,value}]`, events, subtitle, button-row intent→id precedence,
  media-viewer = http(s) link not a data-URI embed); layout-doc def gains
  layout_grid+slot; artifact section updated.
- **Golden + fixtures reshaped** to the real envelope; 4 new negative fixtures
  (no-layout-grid, no-slot, bad-component, bad-props) prove the new teeth.
- KERNEL_ASKS #3 (html-embed) + #10 (kernel-side validation) + #5 (size limits)
  marked resolved against the shipped kernel.

## 0.5.3 — 2026-07-11

### Completed the SA-023 `orchestrator`→`domain` content re-role (deferred at v0.5.0)

- **Identity strings.** Renamed the residual `rasa.orchestrator.canvas` identity
  strings → `rasa.domain.canvas` across the doc titles (CLAUDE.md, README.md,
  this file), `rasa.json` (`session_model` element key + `tenant_model`
  composition target), and the published schema `$id` (dead
  `RasaOS/orchestrator-canvas` repo path → `RasaOS/domain-canvas`).
- **Role-noun.** Folded the self-describing noun "orchestrator" → "domain" where
  it names what this element *is* (README, CLAUDE.md, rasa.json, KERNEL_ASKS.md);
  the behavior verb "orchestrates" stays. This element is a `domain` — SA-023
  folded the orchestrator *kind* into `tenant`.
- The v0.5.0 historical entry is preserved verbatim.

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
