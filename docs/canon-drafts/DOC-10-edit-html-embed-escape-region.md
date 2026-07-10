---
id: DOC-10-edit-html-embed-escape-region
status: draft — authored in elements/domain-canvas (TASK-007); file to canon/tasks/triage/
spec_proposal_status: "v0.1 — full contract specified; shell half already IMPLEMENTED (frontend-rasaos @ a5f6ff1), kernel enum + FE-002 review outstanding"
target_version: 1.4.0 or 1.5.0 (proposed — FE-002 requires a doc 10 v1.1 minor bump + Frontend release-manager review for any component addition)
target_docs:
  - 10_frontend_specification.html (§4 component overview — the escape region as a distinct class, NOT the 22nd business component; Appendix A enum; Appendix B prop schema; new lock FE-022)
  - 02_brand_kit.html (vocabulary — "artifact / html-embed")
  - downstream: RasaOS/schema rasa.layout.v1.json (component enum + props.html maxLength)
  - downstream: kernel canvas component allowlist
originating_design: 2026-07-09 elements/domain-canvas core-internal-structure session — the "internal website builder" needs 3D/animation/custom-visual regions; grounded implementable spec at elements/domain-canvas/docs/design/html-embed-spec.md
depends_on:
  - DOC-10-edit-canvas-components (sibling — the same FE-002 review lane; that one added 3 business components, this adds the single escape region)
  - DOC-10-edit-frontend-profiles (conversational-canvas is where artifacts earn their keep)
relationship:
  - Gated by lock FE-002 ("build only from the frozen set"). This task does NOT propose a 22nd frozen primitive — it proposes admitting html-embed as THE single sandboxed escape region, a fenced boundary (like an <iframe> is a boundary, not a widget), so FE-002's "reason about a small set" is preserved.
filed_by: rasa.domain.canvas session 2026-07-09 (TASK-007)
---

# DOC-10-edit: admit `html-embed` as the single sandboxed escape region (FE-022)

> **Reality note (verified @ frontend-rasaos main a5f6ff1, 2026-07-09):** the
> shell ALREADY renders this — `app/src/canvas/components.tsx` ships an
> `HtmlEmbed` component serving both `code-block{render:true}` (the
> kernel-legal carriage) and a direct `html-embed` arm. The kernel allowlist
> + schema enum + this canon admission are the remaining work; the renderer
> is done and independently convergent with the spec below.

## Source

The `conversational-canvas` profile authors a tenant's UI live. Data UIs are
fully served by the frozen component set — but **3D, animation, drawing, and
custom visualization** cannot be expressed by any of the 18–21 primitives, and
FE-002 forbids inventing more. Rather than grow the frozen set unboundedly
(a chart type here, a 3D viewer there — each an FE-002 review, and the set
stops being small), admit ONE escape region whose safety comes from a browser
sandbox instead of from the renderer knowing its internals.

## What doc 10 gets

A new component `html-embed` with props `{ html: string, height?: integer }`,
documented as a **distinct class** — the escape region, not a business
component:

- **Rendering:** one self-contained HTML document in a **sandboxed iframe**,
  `sandbox="allow-scripts"` (opaque origin — never `allow-same-origin`): no
  parent DOM, no cookies/storage, no top-navigation.
- **CSP (shell-injected into the document):** `connect-src 'none'` is the
  thesis — scripts run, nothing phones home. `script-src` allows inline +
  `unsafe-eval` + the four claude.ai-parity CDNs (cdnjs, jsdelivr, unpkg,
  esm.sh), so three.js/D3/Chart.js/React load and **3D/WebGL work**;
  `img-src data: blob:` only. Runtime asset fetches (remote textures/GLTF/
  wasm) are blocked by design — procedural + data-URI assets only.
- **The bridge:** `window.rasa.emit(action, payload)` → `postMessage` →
  `ui_event` turn (validated by `e.source === contentWindow` + a `__rasa`
  envelope). The only way out of the sandbox.
- **Size:** `props.html` capped (~16KB) at the schema layer; CDN libraries
  load at runtime and don't count.
- **Discipline:** one artifact region per screen; reach for it only when the
  frozen set can't express the screen.

## Proposed lock — FE-022

> **FE-022 — the escape region.** Exactly one unbounded component
> (`html-embed`). It is sandboxed (`allow-scripts`, opaque origin), CSP-fenced
> (`connect-src 'none'`), size-capped, binds no bus source, nests no regions,
> and cannot reach the parent. The AI still writes only layout JSON (the html
> is a prop string, not renderer/validator code — FE-004 holds). The sandbox +
> CSP is the boundary that FE-002 otherwise gets from the small set. The
> validator (FE-020) enforces the size cap and one-per-screen fence.

## Why it doesn't erode FE-002

FE-002's value is "the AI can reason about composition from a small primitive
set." html-embed is not a composition primitive — it is a fenced boundary the
AI reaches for only when composition can't express the need. The fence
(FE-022 + one-per-screen + validator caps) keeps it from becoming the lazy
default. The safety guarantee moves from "renderer knows every component" to
"browser sandbox + CSP contain an unknown one" — a well-understood trade the
whole claude.ai artifacts architecture rests on.

## Full implementable spec

`elements/domain-canvas/docs/design/html-embed-spec.md` (§B component spec,
§C per-layer change-set, §E honest risks). Cross-refs: KERNEL_ASKS #3
(kernel enum), the frontend handoff F1 (shell — already done @ a5f6ff1).
