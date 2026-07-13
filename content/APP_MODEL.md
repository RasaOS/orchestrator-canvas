# The app model — what a vertical IS

A vertical is a **directory, not a canvas**. The canvas is a projection of
one screen of it. This file defines the directory exactly, so a fresh
session that reads it can take over any app cold — no archaeology, no asking.

## The workspace

```
<tenant>/.rasaos/apps/<app-id>/
├── app.json          # the manifest — identity, screens, events, version (spec below)
├── CHANGELOG.md      # one line per shipped change, newest first
├── screens/          # one rasa.layout.v1 document per screen
│   └── <screen-id>.json
├── state/            # app memory — small JSON files, one concern each
└── data/             # optional — derived/cached views of tenant data
```

- `<app-id>` is kebab-case, stable, never renamed after creation.
- `screens/<screen-id>.json` holds EXACTLY what `canvas_set` publishes for
  that screen — byte-for-byte the last published layout. Its layout
  `screen.name` equals the screen id: the file name is the identity and the
  document agrees.
- `state/` files are the app's memory. One concern per file (`saves.json`,
  `filters.json`); the EVENT process writes here and nowhere else.
- `data/` holds derived views (a parsed CSV, an aggregation). Tenant files
  stay the source; derived views are disposable and carry `_source` +
  `_derived_at` fields so staleness is visible.

## The context index — context.json

Written by the AUDIT process (PROCESSES.md §AUDIT): the per-install registry of
what exists to bind to — the tenant flavor, sibling domains + modules, each
module's collections (dir, record shape, per-field types, states, `writable`),
and tenant data files. Published schema: `rasa.canvas.context.v1`
(`schemas/rasa.canvas.context.v1.schema.json`).

- **Per-install, discovered, disposable** — re-derivable by re-running AUDIT;
  nothing from it is ever baked into the element (`content/` stays generic).
- **Staleness:** BOOTSTRAP always re-audits; any turn whose binding/data target
  fails to resolve re-audits before erroring; `_audited_at` is advisory.
- **The index plans; files decide.** Re-read sources before any publish; the
  index is a map, never the territory.

## app.json — the manifest

```json
{
  "app": "rasa.app.v1",
  "id": "orders-desk",
  "name": "Orders Desk",
  "version": "0.4.0",
  "created": "2026-07-07",
  "screens": [
    { "id": "home",   "title": "Overview", "default": true },
    { "id": "orders", "title": "Orders" }
  ],
  "active_screen": "orders",
  "data_sources": [
    { "path": "../../data/orders.csv", "purpose": "orders table" }
  ],
  "events": [
    { "action": "order_opened", "emits": ["orders"], "handling": "read the order from the source, bake detail into the active screen, publish" },
    { "action": "nav:home",     "emits": ["nav"],    "handling": "SWITCH_SCREEN home" }
  ]
}
```

Rules:

- **`screens[]` is exhaustive.** A file in `screens/` with no row here is an
  orphan — register it or delete it, same turn you notice.
- **`events[]` is exhaustive.** Every action any published screen can emit
  has a row declaring which region(s) emit it and what handling the user was
  promised. EVENT executes the row, exactly. No row → the screen had no
  business emitting it: honor the user's visible intent, then fix the
  registry in the same turn.
- **`active_screen` always names the screen currently on the canvas.**
- `data_sources[]` paths are tenant-relative; never point outside the tenant
  root.

## bindings[] — the binding registry

Binding the UI to the tenant's real data is this element's **main objective**.
One `bindings[]` row per bound region: the declared data relationship the
screen renders. Schema: `bindings[]` in `rasa.app.v1` (published); check-app
enforces the cross-field law.

- **`id`** — unique across the registry (check-app enforces).
- **`region` + `screen`** — must name a registered screen and a region that
  exists on it. One row per region; multiple bindings may share a source.
- **`source`** — exactly ONE of: `{module, collection, select?}` (a sibling
  module's collection — must resolve in `context.json#modules`, and
  `read-write` requires the collection be marked `writable`); `{tenant:
  "<path>"}` (a tenant file, tenant-relative, never outside the root);
  `{context: "<query>"}` (derived mode). `select` v1 grammar is `"*"` only.
- **`mode`** — `bound` (live relationship) · `derived` (synthesized snapshot,
  stamped in `data/`) · `provision` (created-then-bound; carries
  `provisioned: true`). BUILDER §binding-modes is the operating recipe.
- **`direction`** — `read` | `read-write`. A `read-write` binding must have at
  least one event that writes it (check-app enforces).
- **`reactive`** — absent/`on-event` (re-derive on the next EVENT turn) |
  `live` (auto-updates on external file change — needs the kernel file-event
  bridge, KERNEL_ASKS #11; the same declaration upgrades free).
- **`events[].writes[]`** — what an action mutates, in write-order:
  `{binding, op, field?}` entries execute per the executor rule (PROCESSES.md
  §EVENT); `{state: "<file>"}` entries are app-local memory. `op` ∈
  `create-record | update-record | move-record | delete-record`.
- **`data_sources[]` is read-only sugar** — a row equals a binding
  `{source:{tenant}, shape:"file", mode:"bound", direction:"read"}`. New
  authoring prefers `bindings[]`; both are legal.

## Persistence — files are truth, Redis is a projection

The kernel canvas store is Redis-backed and a container restart can wipe it
(verified 2026-07-07; KERNEL_ASKS #6–8). Doctrine:

- **The write-order law:** 1) bound-collection record writes (a `writes[]`
  `{binding, op}` entry, per the executor rule — PROCESSES.md §EVENT) → 2)
  `state/` files → 3) `screens/<id>.json` → 4) `app.json` (+ `CHANGELOG.md` if
  touched) → 5) `canvas_set`. Never reversed, never partial. A publish that
  skipped the file write didn't happen. (Turns with no `writes[]` collapse to
  the last three steps.)
- **It is an ORDER, not a transaction.** The session is the only writer and has
  no multi-file commit, so an interrupted turn can leave a half-written manifest
  or a screen file that disagrees with `app.json`. The recovery is REBUILD's
  integrity pass (`check-app` on session start): files are truth, so a fresh
  session repairs the directory to GREEN before it trusts the canvas. The
  guarantee is ordering + idempotent recovery, not atomicity.
- Nothing durable exists only on the canvas. If it matters, it is in a file
  before it is on screen.
- If `canvas_get` returns empty or older than the files: run REBUILD silently
  before anything else.

## Versioning — three clocks, never conflated

| Clock | Owner | Meaning |
|---|---|---|
| canvas `version` | kernel | Bumps on every `canvas_set`; monotonic render ordering. Not yours to manage. |
| `app.json#version` | you | The app's semver. patch = data/state refresh · minor = screen changed or added · major = app model reshaped. Bump once per shipped user request; mirror one line in the app's `CHANGELOG.md`. |
| element version | workspace | This doctrine's own release version (`VERSION`/`rasa.json`). Nothing to do with apps. |

## Enforcement — the law is machine-checked

- The manifest contract is published as `schemas/rasa.app.v1.schema.json`, the
  context index as `schemas/rasa.canvas.context.v1.schema.json`, and
  the layout contract as `schemas/rasa.layout.v1.json` — the vendored copy of
  `RasaOS/schema`'s `rasa.layout.v1.json` (== the kernel's enforced copy).
- `bin/check-app <app-dir>` (ships with this element) audits an app against this
  whole file AND the vendored layout schema: registries exhaustive both ways,
  event coverage (including `rasa.emit` scans inside artifacts), nav contract +
  targets, screen.name identity + `^[a-z][a-z0-9-]*` pattern, required
  `screen.layout_grid` + region `slot`, the 12-name component allowlist
  (canvas_set rejects anything else), per-component prop shapes (canon Appendix
  B.2), the kernel `validator.ts` caps (256KB layout / 64 regions /
  dup-region-id), state/data hygiene, and the binding layer (`context.json` shape, the `bindings[]` registry — ids unique, `source` resolves in `context.json`, `read-write` has a writer — and `events[].writes[]` targets). GREEN means "canvas_set will accept
  this and it renders"; RED blocks a publish — see PROCESSES.md §gate.
- The doctrine audits itself: `bin/check-doctrine` keeps BUILDER / APP_MODEL /
  PROCESSES / COMPONENTS in lockstep and gates every commit to the element.

## Multi-screen — sections mesh, leaves climb (one canvas, for now)

The kernel keys one canvas per session (KERNEL_ASKS #1), so ALL screens exist
as files; exactly ONE (`active_screen`) is on the canvas at a time. Switching =
publishing a different file (SWITCH_SCREEN). Nav is STATELESS — the kernel keeps
no history/back stack, so "back" must be encoded in the files, not remembered.

**Two screen classes, derived from one optional field.** Each `app.json#screens`
row may carry `parent: "<screen-id>"`:

- **SECTION** (row has NO `parent`) — a co-equal top-level screen (a tab), also
  called a *root*.
- **LEAF** (row HAS `parent`) — a spawned detail / step / nested screen. `parent`
  names its single, deterministic back-target: a registered screen id, not
  itself; the parent graph must be acyclic and every leaf's chain must terminate
  at a section. Classes are DERIVED — SECTIONS = rows without `parent`, LEAVES =
  rows with it.

**The nav contract.** A screen with siblings carries one region
`{ "id": "nav", "component": "button-row" }` whose `nav:<screen-id>` buttons are
its *structural* links; a `[canvas] nav:<id> (nav)` turn is a SWITCH_SCREEN,
always. What those targets must equal is keyed on class:

- **SECTION:** targets == every OTHER section (full mesh among sections only —
  the old rule, now scoped to the few tabs). A lone section (the only
  parent-less screen) carries no `nav:` buttons.
- **LEAF:** targets must include the immediate `parent` and may include only
  further ancestors — `parent ∈ targets ⊆ ancestors(self)`. The default shape is
  one button `nav:<parent>` (one-tap back); a breadcrumb lists more ancestors. A
  leaf NEVER carries a nav button to a sibling leaf or any non-ancestor.

**Structural vs. forward.** The `nav` region is structural only (back / peer-tab).
Every FORWARD or LATERAL jump — a list card opening a detail, a wizard "next", a
cross-entity link — is an ordinary action (`nav:<id>` button, card `on_click`,
form `submit`) in ANY OTHER region, and its `app.json#events` row carries
`target: <screen-id>` naming where it goes. This split is what stops the
combinatorial blow-up: N spawned details are N one-button leaves; the links
between them are content, not structure.

**Reachability.** Every leaf must be reachable by a forward link — either a
`nav:<leaf>` button/`on_click` in a content region, or an `events[]` row with
`target: <leaf>`. A declared-but-unlinked leaf is a dead screen and fails the
gate. Sections are reachable by construction (the mesh / the default).

**"Back" is deterministic and stateless:** a leaf's `nav:<parent>` button IS
back — the same target however the user arrived. Multi-level climb repeats
one-step-back up the chain. Under a cross-link a detail returns to its ONE
canonical parent (the owning entity's list) even when reached laterally — the
honest cost of stateless nav.

Adding a screen is ADD_SCREEN's job and branches on class (a section joins the
mesh; a leaf gets one back button + one inbound forward link). When
`args.canvas_id` lands, screens map 1:1 onto named canvases and `active_screen`
becomes advisory; the parent tree is pure file metadata and the rule is unchanged.
