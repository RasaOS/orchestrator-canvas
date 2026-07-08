# Changelog — rasa.orchestrator.canvas

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
