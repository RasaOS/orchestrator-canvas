# The component contract — what a canvas region may be

The layout document is `rasa.layout.v1`:

```json
{ "layout": "1.0.0",
  "screen": { "name": "orders", "title": "Orders" },
  "regions": [ { "id": "kpis", "component": "kpi-tile", "props": { } } ] }
```

Regions flow vertically unless a region carries `frame {x,y,w,h}` (absolute,
canvas-local px; overlap legal; z = document order).

## Kernel allowlist (canvas_set validates component names)

`card-strip · inbox-list · matter-detail · doc-viewer · table · chart ·
kanban · timeline · kpi-tile · filter-bar · nav · modal · form ·
calendar-grid · media-viewer · code-block · ai-rail · map ·
markdown-block · button-row · card-list`

The RasaOS shell currently RENDERS this subset (the rest error-tile —
author ONLY these): `table · card-strip · card-list · form · chart · code-block ·
media-viewer · kpi-tile · timeline · markdown-block · button-row`

## Prop shapes the shell actually consumes (verified against the renderer, 2026-07-09)

These are the REAL shapes from frontend-rasaos `app/src/canvas/components.tsx`.
The renderer reads props defensively — a wrong key doesn't crash, it renders
EMPTY. Author exactly these:

- **kpi-tile** `{value, label, delta?}` — delta colored by leading `-`
- **table** `{title?, columns: [string | {key,label}], rows: [[…] | {…keyed by column key}]}`
- **card-strip** `{cards: [{title, subtitle?}]}` — horizontal, non-interactive
- **card-list** `{cards: [{title, subtitle?}], on_card_click?}` — with
  `on_card_click` set, each card is a button (see emission grammar)
- **chart** `{data: [{label, value}]}` — horizontal bars ONLY (no line type,
  no axes)
- **form** `{fields: [{id, label?, type?, placeholder?}], submit_label?}` —
  `type:'textarea'` special-cased, else a raw input type
- **timeline** `{events: [{at, label}]}`
- **button-row** `{buttons: [{id, intent, label?, style?}]}` — `style:'primary'`
  for the accent button; ALWAYS set `intent` (it is the emitted action; `id` is
  just the button's identity)
- **markdown-block** `{content}` — escaped subset only: `#/##/###`, `**bold**`,
  `` `code` ``, `- ` lists, paragraphs (raw HTML is escaped, never rendered)
- **code-block** `{code}` — plain `<pre>` text; NO syntax highlight, NO
  render carriage (`render:true` does nothing)
- **media-viewer** `{src}` — renders a safe LINK (http/https only, opens in a
  new tab); it never embeds. data:/javascript: render as inert text.

## Interactions — the emission grammar (what actions actually arrive)

Every interaction arrives in this session as `[canvas] <action> (<region-id>)`.
The shell computes the action string as follows — register every emittable
action in `app.json#events`:

- **button-row**: emits `intent`, else `'on_click'` with `{button_id}` in the
  payload. An intent-less button is ambiguous — always set `intent`.
  Navigation buttons carry `intent: "nav:<screen-id>"`.
- **card-list** with `on_card_click`: emits `on_card_click` with
  `{card_index, title}`.
- **form**: emits `on_submit` with `{<field-id>: value, …}` (uncontrolled).
- **any non-form region** with `props.on_click`: the whole region is clickable
  and emits `on_click` with `{region_id}`.

## §artifact — the escape hatch for custom visuals / animation / 3D

**LIVE** (verified 2026-07-09 against frontend-rasaos `main` @ `a5f6ff1`,
`app/src/canvas/components.tsx:64-163`). One region carries a complete
self-contained HTML document, rendered in a **sandboxed iframe** — opaque
origin (`allow-scripts` only: no parent DOM, no cookies/storage, no top-nav).

**Author it as the carriage** (the kernel-legal form — canvas_set rejects the
`html-embed` name until the kernel enum lands, KERNEL_ASKS #3):

```json
{ "id": "hero", "component": "code-block",
  "props": { "code": "<!doctype html>…", "render": true, "height": 460 } }
```

(`html-embed {html, height}` is the same renderer and becomes the preferred
form once allowlisted. `height` defaults to 420px.)

The contract (all shell-injected — unspoofable by the document):

- **CSP**: `connect-src 'none'` — scripts run, nothing phones home (no
  fetch/XHR/WebSocket). `script-src` allows inline + `unsafe-eval` + exactly
  cdnjs.cloudflare.com · cdn.jsdelivr.net · unpkg.com · esm.sh — so
  **three.js / D3 / Chart.js / React+JSX work, 3D/WebGL works** (WebGL needs
  no network). Images/media: `data:`/`blob:` only — remote asset fetches
  (textures/GLTF/wasm) are blocked; use data-URIs or procedural geometry.
- **The bridge**: `window.rasa.emit(action, payload)` is predefined and is
  the ONLY way out — calls arrive here as `[canvas] <action> (<region-id>)`
  turns. Register every emitted action in `app.json#events` (check-app scans
  `rasa.emit` calls inside artifacts).
- **Stateless across versions**: each `canvas_set` fully re-mounts the
  document. Bake server-truth state INTO the html you publish (e.g.
  `const SAVES=3`); keep ephemeral UI state (hover, tabs) in the framework.
- **Budgets**: the authored document rides the layout JSON — keep it ≤ ~10KB
  (check-app warns >10KB, fails >16KB). CDN libraries load at runtime and
  don't count.
- **Rules**: ONE artifact region per screen; reach for it only when the
  declarative set can't express the screen; prefer a small framework over
  hand-rolled DOM (preact+htm from esm.sh is the light default; React 18 +
  Babel-standalone works under `unsafe-eval` when a library needs React).
  Match the shell palette (deep teal/green, coral `#d96b3a`, bone `#f4ead6`).

## Versioning

Every `canvas_set` bumps the canvas version; the shell renders monotonically
and rehydrates from snapshot on reload. Publish complete, coherent states.
