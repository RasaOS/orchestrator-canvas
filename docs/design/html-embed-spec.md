# Design — the `html-embed` escape region (3D / animation / custom visuals)

**Status:** ⚡ **SHELL HALF IMPLEMENTED** (discovered 2026-07-09, HOTFIX-001):
frontend-rasaos `main` @ `a5f6ff1` ships `HtmlEmbed` in
`app/src/canvas/components.tsx` — the `code-block{render:true}` carriage
(`:64-68`) AND a direct `html-embed` arm (`:69-70`), `sandbox="allow-scripts"`
+ srcDoc, injected CSP with `connect-src 'none'` (`:109-113`), injected
`window.rasa.emit` bridge with `e.source` + `__rasa:1` checks (`:136-141`),
`height` default 420 — **independently convergent with §B of this spec.**
Deltas from §B: their `style-src` omits esm.sh + fonts.googleapis; no
`base-uri`/`form-action` directives; `media-src data: blob:` added; empty
document → warn tile. **Remaining change-set: kernel K1 (allowlist + schema
enum + maxLength) and the canon task (§C items 5–6, FE-022).** §A's "reality"
findings described a pre-`a5f6ff1` checkout state — superseded for the shell,
still accurate for canon + kernel.

*(Original grounding below, 2026-07-09, against frontend-rasaos source, canon
triage, and the published layout schema — citations inline.)*
**Parent:** `docs/design/ui-engine-and-architecture.md` §2.1/§2.1a.
**Why:** 3D + animation in pages is a hard product requirement. This is the single
sandboxed escape region that delivers it — specified precisely enough to implement.

---

## A. Reality (what exists today — all verified)

- **The shell has NO artifact path and NO sandboxed iframe.** Its only `<iframe>`
  (`app/src/shell/Shell.tsx:110-111`, proxy verticals) is deliberately **same-origin and
  unsandboxed** ("keeps auth + kernel + Vault shared — the moat", `verticals.tsx:16-18`) —
  the *inverse* of what hostile-content artifacts need. The canvas renderer
  (`components.tsx:37-69`) has no `html-embed` arm; `code-block` has **no `render:true`
  path** (renders `<pre>` only, `:254-260`).
- **The shell enforces NO CSP anywhere.** Not in `nginx.conf`, not in `index.html` (which
  itself loads Google Fonts cross-origin), not in Vite config. The doctrine's "the shell
  injects a CSP enforcing this" claim (COMPONENTS.md §artifact) is **unimplemented** — a
  safe artifact must carry its **own** CSP injected into the `srcdoc`.
- **No canon triage proposes html-embed.** SA-026/027/028 and DOC-10-edit-canvas-components
  (18→21, review-approved) contain no artifact/embed/iframe component; DOC-10-edit
  explicitly scopes further additions to their own FE-002 reviews. The only specs of
  html-embed anywhere are (a) KERNEL_ASKS #3 — whose clause *"the shell already renders it
  sandboxed"* is **FALSE** — and (b) COMPONENTS.md §artifact, which describes a shell that
  does not exist. Both must be corrected (see review findings #27/#28).
- **doc-10 discipline is the wall:** FE-002 (frozen set; additions need a v1.1 review),
  FE-004 (AI edits data, never render code), FE-018/§15 (unknown components error-tile).
  Admitting html-embed means an explicit **fenced exception**, not a 22nd primitive.
- `bin/check-app` **already** enforces artifact size caps (warn 10KB / fail 16KB) for the
  (non-rendering) carriage — the enforcement layer is ahead of the platform here.

## B. The component spec

### B.1 Prop shape
```json
{ "id": "hero", "component": "html-embed",
  "props": { "html": "<!doctype html>…", "height": 460 } }
```
- `html` (string, required): ONE complete self-contained HTML document.
- `height` (integer px, required; 120–2000): fixed region height (v1 — see B.5).
- No `source`, no bus binding, no `on_*` props — **the bridge is the only I/O** (this is
  what keeps it a *leaf*, not a container).

### B.2 The iframe sandbox (browser-enforced)
```tsx
<iframe
  sandbox="allow-scripts"          // NOTHING else — never allow-same-origin
  srcDoc={wrapped}                  // shell-built wrapper; never src
  style={{ width: '100%', height, border: 0 }}
  referrerPolicy="no-referrer"
  title={region.id}
/>
```
`allow-scripts` **without** `allow-same-origin` → the document runs on an **opaque
origin**: no parent DOM, no cookies/storage, ephemeral world. Omit all other sandbox
tokens (no top-nav, popups, forms, modals).

### B.3 The injected CSP (shell wraps `props.html`)
The shell prepends, as the first children of `<head>`: the bridge bootstrap `<script>` and:
```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'none';
  script-src  'unsafe-inline' 'unsafe-eval'
              https://cdnjs.cloudflare.com https://cdn.jsdelivr.net
              https://unpkg.com https://esm.sh;
  style-src   'unsafe-inline'
              https://cdnjs.cloudflare.com https://cdn.jsdelivr.net
              https://unpkg.com https://esm.sh https://fonts.googleapis.com;
  font-src    https://fonts.gstatic.com data:;
  img-src     data: blob:;
  connect-src 'none';
  frame-src 'none'; child-src 'none'; base-uri 'none'; form-action 'none';
">
```
**`connect-src 'none'` is the security thesis:** scripts may run, but they cannot phone
home (no fetch/XHR/WebSocket/EventSource/sendBeacon). `'unsafe-eval'` (for in-browser
Babel, Kit B) is acceptable *only because* of that + the opaque origin. `img-src data:
blob:` closes the pixel-GET exfil channel. The shell builds the wrapper, so the CSP and
`window.rasa` are unspoofable by authored html.

### B.4 The `window.rasa.emit` bridge (postMessage)
Injected bootstrap:
```js
window.rasa = { emit(action, payload){
  parent.postMessage({ __rasa: 1, action: String(action), payload: payload ?? {} }, '*');
}};
```
Parent (`HtmlEmbed` component):
```tsx
const onMsg = (e: MessageEvent) => {
  // Opaque origin ⇒ e.origin === 'null'. MUST match the source window instead:
  if (e.source !== iframeRef.current?.contentWindow) return
  const d = e.data
  if (!d || d.__rasa !== 1 || typeof d.action !== 'string') return
  interact(region.id, d.action, (d.payload && typeof d.payload === 'object') ? d.payload : {})
}
```
`interact` → `sendUiEvent` (`CanvasPane.tsx:46`) → the existing `ui_event` turn path.
The `e.source === contentWindow` check is **mandatory** (origin is `null` under sandbox);
a naive listener accepts messages from any frame. Emitted actions must still be registered
in `app.json#events` — `check-app` already scans artifacts for `rasa.emit` calls.

### B.5 Height
**v1: fixed `height` prop.** Deterministic, and keeps `CanvasPane.report()` (the
measured-geometry PUT to the kernel, SA-028) stable. Auto-resize (ResizeObserver →
postMessage height) is a deferred option — it thrashes the measure/report loop.

### B.6 Size budget
The html rides inside the layout JSON → Redis → SSE wire, re-sent on every version bump.
Caps (already in check-app): **artifact warn >10KB / fail >16KB; layout warn >28KB / fail
>32KB.** Also encode at the schema layer: `props.html maxLength` (e.g. 16384) — the
published layout schema today caps nothing but `screen.title`. (Satisfies KERNEL_ASKS #5.)

### B.7 CDN 3D/animation viability — the honest edges
- **Works fully:** procedural three.js/WebGL scenes, D3/Chart.js, CSS/`requestAnimationFrame`
  animation, `<canvas>` drawing. CDN libs load via `script-src` at runtime and do NOT count
  against the authored-doc budget. WebGL needs no network.
- **Fails under `connect-src 'none'`:** any runtime *asset fetch* — remote textures, GLTF,
  HDR, `.wasm` (draco/basis/ammo). Only `data:`/`blob:` assets + pure geometry survive.
- **Offline/air-gapped tenants** can't reach the CDNs at all → self-hosting libs/assets
  would require widening `connect-src` to `'self'` (a re-secured same-origin channel) —
  a deliberate later decision, not v1.
- **Perf notes:** the srcdoc fully re-mounts on every canvas version (stateless-across-
  versions law) → scene reinit + CDN re-hit (HTTP-cached) + a visible reload flash on each
  edit; WebGL contexts are limited (~16/page) — hence the "one artifact region per screen"
  fence.

## C. The change-set (minimal, per layer)

| # | Layer | Change | Size |
|---|---|---|---|
| 1 | shell `components.tsx` | `case 'html-embed'` arm + `HtmlEmbed` (srcdoc wrapper + sandbox iframe + message listener → `interact`) | **~70–110 lines** |
| 2 | shell/element lockstep | add `html-embed` to `SHELL_RENDERED` (`_contract.py`) + COMPONENTS.md rendered subset, same commit | small |
| 3 | kernel | add `"html-embed"` to the canvas component allowlist | small |
| 4 | `RasaOS/schema` | add `html-embed` to the `rasa.layout.v1` component enum + a props sub-schema (`html maxLength`, `height` bounds); re-vendor into kernel | small–medium |
| 5 | canon | new task `DOC-10-edit-html-embed-escape-region`: admit via FE-002 v1.1 review, framed as **the escape region**, + a new lock **FE-022** (below) | **medium — load-bearing** |
| 6 | canon | Brand Kit vocabulary ("artifact / html-embed"); fold size caps into SA-027's write-boundary text | small |

**Proposed FE-022 lock:** *"Exactly one unbounded component. It is sandboxed
(`allow-scripts`, opaque origin), CSP-fenced (`connect-src 'none'`), size-capped, binds no
bus source, and cannot reach the parent. The sandbox + CSP is the boundary that FE-002
otherwise gets from the small set."*

**Framing against FE-002/FE-004/FE-018:** html-embed is a leaf, not a container — the AI
still writes only layout JSON (the html is a prop *string*, not render code, so FE-004
holds); the renderer never executes it in its own realm — the browser does, contained. The
safety guarantee *moves* from "renderer knows every component" to "browser sandbox + CSP
contain an unknown one."

**Page-level shell CSP:** optional, separate task, NOT required for this feature (safety is
per-iframe). If ever added it must permit `srcdoc` frames + Google Fonts + esm.sh or it
silently breaks artifacts. Defer; don't couple.

## D. Alternative considered — a declarative `scene`/`viz` component

Shell-owned engine, structured props (`{shapes, camera, lights, animation}`), no iframe/CSP
surface, fully inside FE-002. Rejected as the *first* move: it requires designing a whole
3D/animation DSL that can only express what its grammar anticipated — exactly the wall the
escape hatch climbs — and every new capability becomes a renderer release + FE-002 review.
**Lead with html-embed; let recurring artifact patterns crystallize into declarative
components later** (the doc-10 `workflow-runner`/`diff-viewer` path).

## E. Honest risks

- **Security:** `allow-scripts` + `'unsafe-inline'` + `'unsafe-eval'` is a live execution
  surface — contained by opaque origin + `connect-src 'none'` (no exfil, no parent, no
  cookies). The bridge's `e.source` check is the one mandatory implementation detail; a
  future mis-set page CSP could silently break srcdoc frames.
- **Discipline erosion:** html-embed is a genuine hole in FE-002's layouts-as-data thesis.
  The fence (FE-022 + "one artifact region per screen" + "only when the declarative set
  can't express it") must be *encoded in the validator*, not just doctrine prose, or it
  becomes the lazy default.
- **Perf:** ≤16KB re-ships every version bump; full remount per version (reload flash);
  WebGL context limits.
- **Asset-loading 3D + offline tenants** are out of scope for v1 (see B.7).
