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
  that screen — byte-for-byte the last published layout.
- `state/` files are the app's memory. One concern per file (`saves.json`,
  `filters.json`); the EVENT process writes here and nowhere else.
- `data/` holds derived views (a parsed CSV, an aggregation). Tenant files
  stay the source; derived views are disposable and carry `_source` +
  `_derived_at` fields so staleness is visible.

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

## Persistence — files are truth, Redis is a projection

The kernel canvas store is Redis-backed and a container restart can wipe it
(verified 2026-07-07; KERNEL_ASKS #6–8). Doctrine:

- **The write-order law:** 1) `screens/<id>.json` → 2) `app.json` (+ `state/`
  and `CHANGELOG.md` if touched) → 3) `canvas_set`. Never reversed, never
  partial. A publish that skipped the file write didn't happen.
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

## Multi-screen — many screens, one canvas (for now)

The kernel keys one canvas per session (KERNEL_ASKS #1), so:

- ALL screens exist as files; exactly ONE (`active_screen`) is on the canvas
  at a time. Switching screens = publishing a different file (SWITCH_SCREEN).
- **The nav contract:** every screen with siblings carries a region
  `{ "id": "nav", "component": "button-row" }` whose buttons are
  `{ "id": "nav:<screen-id>", "label": "<title>" }` — one per OTHER screen.
  A `[canvas] nav:<id> (nav)` turn is a SWITCH_SCREEN, always. Keep nav
  first in `regions[]` unless the screen has a reason not to.
- Adding a screen touches every sibling's nav (ADD_SCREEN owns this).
- When `args.canvas_id` lands, screens map 1:1 onto named canvases and
  `active_screen` becomes advisory. The files, the nav contract, and the
  processes stay exactly as they are — only the publish target changes.
