# The app model — what a vertical IS

A vertical is a **directory, not a canvas**. The canvas is a projection of
one screen of it. This file defines the directory exactly, so a fresh
session that reads it can take over any app cold — no archaeology, no asking.

## The workspace

```
<tenant>/.rasaos/apps/<app-id>/
├── app.json          # the manifest — identity, screens, events, version (spec below)
├── context.json      # the audit index — what exists to bind to (per-install, disposable)
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

Written by the AUDIT process (PROCESSES.md): the per-install registry of what
exists to bind to — the tenant flavor, sibling domains + modules, each
module's collections (dir, record shape, per-field types, states, writable),
and tenant data files. Published schema: `rasa.canvas.context.v1`
(`schemas/rasa.canvas.context.v1.schema.json` in this element's repo).

- **Per-install, discovered, disposable** — re-derivable by re-running AUDIT;
  nothing from it is ever baked into the element (`content/` stays generic).
- **Staleness:** BOOTSTRAP always re-audits; any turn whose binding/data
  target fails to resolve re-audits before erroring; `_audited_at` is
  advisory — re-audit when the roster looks newer than the index.
- **The index plans; files decide.** Re-read sources before any publish;
  the index is a map, never the territory.

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
    { "action": "status_changed", "emits": ["orders"],
      "writes": [ { "binding": "queue", "op": "move-record", "field": "status" },
                  { "state": "filters.json" } ],
      "handling": "move the bound record between state subdirs, refresh filters, publish" },
    { "action": "nav:home",     "emits": ["nav"],    "handling": "SWITCH_SCREEN home" }
  ],
  "bindings": [
    { "id": "queue", "region": "orders", "screen": "orders",
      "source": { "module": "rasa.module.tasks", "collection": "tasks", "select": "*" },
      "shape": "folder-of-records", "mode": "bound", "direction": "read-write",
      "reactive": "on-event" }
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

One row per bound region: the declared data relationship the screen renders.
Schema: `bindings[]` in `rasa.app.v1` (published). check-app enforces the
cross-field law.

- **`id`** — unique across the registry (check-app enforces).
- **`region` + `screen`** — must name a registered screen and a region that
  exists on it. Multiple bindings may share one source (one row per region).
- **`source`** — exactly ONE of: `{module, collection, select?}` (a sibling
  module's collection — must resolve in `context.json#modules`, and
  `read-write` requires the collection be marked `writable`); `{tenant:
  "<path>"}` (a tenant file); `{context: "<query>"}` (derived mode). `select`
  v1 grammar is `"*"` only.
- **`mode`** — `bound` (live relationship) · `derived` (synthesized snapshot)
  · `provision` (created-then-bound; carries `provisioned: true`).
- **`direction`** — `read` | `read-write`. A `read-write` binding must have
  at least one event that writes it (check-app enforces).
- **`reactive`** — absent/`on-event` (today: re-derive on the next EVENT
  turn) | `live` (auto-updates on external file change — requires the kernel
  file-event bridge, KERNEL_ASKS #11; the same declaration upgrades free).
- **`events[].writes[]`** — what an action mutates, in write-order:
  `{binding, op, field?}` entries execute per the executor rule (PROCESSES.md
  §EVENT); `{state: "<file>"}` entries are app-local memory. `op` ∈
  `create-record | update-record | move-record | delete-record`.
- **`data_sources[]` is read-only sugar** — a row is equivalent to a binding
  `{source:{tenant}, shape:"file", mode:"bound", direction:"read"}`. New
  authoring prefers `bindings[]`; both are legal.

## Persistence — files are truth, Redis is a projection

The kernel canvas store is Redis-backed and a container restart can wipe it
(verified 2026-07-07; KERNEL_ASKS #6–8). Doctrine:

- **The write-order law (extended for bindings):** 1) bound module-record
  writes — via the owning module's declared procedure when one exists, else
  direct conventional writes, allowed only on collections `context.json`
  marks `writable` → 2) app-local `state/` → 3) re-derive + write
  `screens/<id>.json` → 4) `app.json` (+ `context.json` if re-audited,
  + `CHANGELOG.md`) → 5) `canvas_set`. Never reversed, never partial. A
  publish that skipped a file write didn't happen.
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

- The manifest contract is published as `schemas/rasa.app.v1.schema.json`
  (in this element's repo).
- `bin/check-app <app-dir>` (ships with this element) audits an app against
  this whole file: registries exhaustive both ways, event coverage (including
  `rasa.emit` scans inside artifacts), nav contract + targets, screen.name
  identity, size budgets, state/data hygiene. RED blocks a publish — see
  PROCESSES.md §gate.
- The doctrine audits itself: `bin/check-doctrine` keeps BUILDER / APP_MODEL /
  PROCESSES / COMPONENTS in lockstep and gates every commit to the element.

## Multi-screen — many screens, one canvas (for now)

The kernel keys one canvas per session (KERNEL_ASKS #1), so:

- ALL screens exist as files; exactly ONE (`active_screen`) is on the canvas
  at a time. Switching screens = publishing a different file (SWITCH_SCREEN).
- **The nav contract:** every screen with siblings carries a region
  `{ "id": "nav", "component": "button-row" }` whose buttons are
  `{ "id": "nav:<screen-id>", "intent": "nav:<screen-id>", "label": "<title>" }`
  — one per OTHER screen. `intent` is what the shell emits as the action
  (COMPONENTS.md §interactions) — a button without it emits ambiguous
  `on_click`. A `[canvas] nav:<id> (nav)` turn is a SWITCH_SCREEN, always.
  Keep nav first in `regions[]` unless the screen has a reason not to.
- Adding a screen touches every sibling's nav (ADD_SCREEN owns this).
- When `args.canvas_id` lands, screens map 1:1 onto named canvases and
  `active_screen` becomes advisory. The files, the nav contract, and the
  processes stay exactly as they are — only the publish target changes.
