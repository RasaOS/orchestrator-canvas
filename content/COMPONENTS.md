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
prefer these): `table · card-strip · card-list · form · chart · code-block ·
media-viewer · kpi-tile · timeline · markdown-block · button-row`.

Prop shapes the shell renders (keep to these):
- **kpi-tile** `{value, label, delta?}`
- **table** `{columns: [string | {key,label}], rows: [[]|{}]}`
- **card-strip / card-list** `{cards: [{title, body?/description?, on_click?}]}`
- **chart** `{type: 'bar'|'line', series/points, labels}`
- **form** `{fields: [{name,label,type}], submit_label?}` → emits `submit`
- **timeline** `{items: [{label, detail?, at?}]}`
- **button-row** `{buttons: [{id,label}]}` → each click emits its id
- **markdown-block** `{markdown}` · **code-block** `{language, code}`
- **media-viewer** `{src (data: URI), alt?}`

Interactions: any `on_click`/button/submit emits a `ui_event` turn back into
this session as `[canvas] <action> (<region-id>)`.

## §artifact — the escape hatch (arbitrary generated UI)

For custom visuals, animation, drawing, and 3D, emit an **artifact region**:
ONE complete self-contained HTML document rendered by the shell in a
**sandboxed iframe** (opaque origin, `allow-scripts` only — no parent DOM, no
cookies/storage, no top navigation).

Preferred form (pending SA-027 vocabulary addition):
```json
{ "id": "hero", "component": "html-embed",
  "props": { "html": "<!doctype html>…", "height": 460 } }
```
**Carriage fallback** (the kernel currently rejects `html-embed` — use the
allowlisted code-block; identical rendering):
```json
{ "id": "hero", "component": "code-block",
  "props": { "language": "html", "code": "<!doctype html>…",
             "render": true, "height": 460 } }
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
