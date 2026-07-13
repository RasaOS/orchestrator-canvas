# The component contract — what a canvas region may be

The layout document is `rasa.layout.v1` (canon doc 10 Appendix A):

```json
{ "layout": "1.0.0",
  "screen": { "name": "orders", "title": "Orders", "layout_grid": "full", "ai_rail_inherited": true },
  "regions": [ { "id": "kpis", "slot": "main", "component": "kpi-tile", "props": { } } ] }
```

`screen.layout_grid` (one of `full · sidebar-main · sidebar-main-rail · two-col ·
three-col · dashboard`) and each region's `slot` are **required** — `canvas_set`
rejects a layout missing either. The canvas shell renders a flex column and
honors `frame` (it does not lay out by grid/slot yet), so `layout_grid:"full"` +
`slot:"main"` is the honest default: the fields satisfy the shared envelope and
map onto the grid model as the shell grows. `ai_rail_inherited: true` marks the
canvas as ai-rail-by-construction (FE-005 per-profile — the conversation is the
rail). Regions flow vertically unless a region carries `frame {x,y,w,h}`
(absolute, canvas-local px; overlap legal; z = document order).

## Kernel allowlist (canvas_set validates component names)

`card-strip · table · form · chart · code-block · media-viewer · kpi-tile ·
timeline · markdown-block · button-row · card-list · html-embed`

These twelve are the operational allowlist `canvas_set` validates against
(kernel `allowlist.ts`). A layout naming anything else is a **hard validation
error at the write boundary — rejected, not rendered as an error tile.** The
published `rasa.layout.v1` schema enum is broader (the full 22-name doc-10
library); narrowing to these twelve is the kernel allowlist's job (canon Spec
§56). The RasaOS shell RENDERS this subset — identical to the allowlist above
(what the kernel accepts is exactly what renders): `card-strip · table · form ·
chart · code-block · media-viewer · kpi-tile · timeline · markdown-block ·
button-row · card-list · html-embed`.

Prop shapes — the canvas inline dialect (canon Appendix B.2; check-app
hard-gates the required prop of each):
- **kpi-tile** `{value, label, delta?}`
- **table** `{columns: [string | {key,label}], rows: [[] | {}]}`
- **card-strip** `{cards: [{title, subtitle?}]}` · **card-list** `{cards: [{title, subtitle?, on_click?}]}`
- **chart** `{data: [{label, value}]}` — the shell renders horizontal bars; `type`
  is accepted but ignored (line/pie is a known shell gap)
- **form** `{fields: [{id, label?, type?}], submit_label?}` → emits `submit` (values keyed by field `id`)
- **timeline** `{events: [{at, label}]}`
- **button-row** `{buttons: [{id, label?, intent?, style?}]}` → emits `intent` if
  set, else `id`, else `on_click`; a `nav:<screen-id>` id drives SWITCH_SCREEN
- **markdown-block** `{content}` · **code-block** `{code, language?, render?}`
- **media-viewer** `{src}` — rendered as an http(s) **link, not an embed**; a
  `data:` URI renders inert. For embedded image/video use an **html-embed** artifact.

Interactions: any `on_click`/button/submit emits a `ui_event` turn back into
this session as `[canvas] <action> (<region-id>)`.

## §artifact — the escape hatch (arbitrary generated UI)

For custom visuals, animation, drawing, and 3D, emit an **artifact region**:
ONE complete self-contained HTML document rendered by the shell in a
**sandboxed iframe** (opaque origin, `allow-scripts` only — no parent DOM, no
cookies/storage, no top navigation).

Preferred form — `html-embed` is **first-class now** (canon FE-002 v1.1 / SA-027;
`html` ≤ 16 KB, `height` 120–2000):
```json
{ "id": "hero", "slot": "main", "component": "html-embed",
  "props": { "html": "<!doctype html>…", "height": 460 } }
```
**Carriage alias** (the allowlisted `code-block` with `render:true` routes to the
same sandboxed iframe — identical rendering; `html-embed` is canonical, this
still works):
```json
{ "id": "hero", "slot": "main", "component": "code-block",
  "props": { "code": "<!doctype html>…", "render": true, "height": 460 } }
```

Artifact rules:
- **Self-contained**: inline CSS/JS; images as data: URIs or drawn (SVG/canvas).
- **Libraries**: `<script src>` is allowed ONLY from cdnjs.cloudflare.com,
  cdn.jsdelivr.net, unpkg.com, esm.sh (the shell injects a CSP enforcing
  this; fetch/XHR/WebSocket are blocked entirely). Three.js, D3, Chart.js
  et al. from those CDNs are fine — **3D/WebGL works**.
- **The bridge**: `window.rasa.emit(action, payload)` is predefined inside
  every artifact. It is the ONLY way out of the sandbox; calls arrive to you
  as `[canvas]` turns. Wire every meaningful interaction through it.
- **Stateless across versions**: the document fully re-renders on every canvas
  version. Bake server-truth state INTO the html you publish (e.g.
  `const SAVES=3`); never rely on in-iframe state surviving a version. (Ephemeral
  in-session UI state — hover, an open tab, a spin value — SHOULD live in the
  framework; only durable state round-trips through `emit`.)
- **Size**: keep the *document you author* ≤ ~10KB — that text rides inside the
  canvas layout JSON. Libraries pulled from the allowlisted CDNs load at
  runtime and DO NOT count against that budget, so a React/three.js app whose
  source is 6KB is fine even though it loads megabytes of framework.

## §artifact starter kits — reach for these, don't reinvent

Custom UI does NOT mean hand-rolled DOM. You have two batteries-included kits;
default to the first, escalate to the second only when you need the React
ecosystem (recharts, a specific lib).

**Kit A — preact + htm (preferred: light, no build/eval, ~12KB runtime).**
JSX-like via tagged templates. This is your default for interactive component UI:

```html
<!doctype html><html><head><meta charset="utf-8"><style>
  :root{color-scheme:dark} body{margin:0;font:14px system-ui;background:#0c1a17;color:#f4ead6}
  .card{background:#12241f;border:1px solid #24413a;border-radius:10px;padding:16px}
  button{background:#d96b3a;color:#0c1a17;border:0;border-radius:8px;padding:8px 14px;font-weight:600;cursor:pointer}
</style></head><body><div id="root"></div>
<script type="module">
  import { h, render } from 'https://esm.sh/preact@10'
  import { useState } from 'https://esm.sh/preact@10/hooks'
  import htm from 'https://esm.sh/htm@3'
  const html = htm.bind(h)
  const SEED = 3 // ← bake server-truth here
  function App(){
    const [n,setN] = useState(SEED)
    return html`<div class="card">
      <h2>Saved ${n}×</h2>
      <button onClick=${()=>{ setN(n+1); window.rasa.emit('save_logged',{count:n+1}) }}>Save</button>
    </div>`
  }
  render(html`<${App}/>`, document.getElementById('root'))
</script></body></html>
```

**Kit B — React 18 + JSX via Babel (full parity, heavier).** Use when a library
needs React. CSP allows `unsafe-eval`, so in-browser Babel works:

```html
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<div id="root"></div>
<script type="text/babel">
  const { useState } = React
  function App(){ const [n,setN]=useState(SEED)
    return <button onClick={()=>{setN(n+1); window.rasa.emit('save_logged',{count:n+1})}}>Saved {n}×</button> }
  ReactDOM.createRoot(document.getElementById('root')).render(<App/>)
</script>
```

Kit rules: keep local UI state in the framework; call `window.rasa.emit` only
for state the app must remember (it round-trips as a `[canvas]` turn, and you
republish with the new SEED baked in). Match the shell palette (deep teal/green,
coral `#d96b3a`, bone `#f4ead6`). One artifact region per screen.

## Versioning

Every `canvas_set` bumps the canvas version; the shell renders monotonically
and rehydrates from snapshot on reload. Publish complete, coherent states.
