# CLAUDE.md — rasa.orchestrator.canvas

You are working on the **canvas-builder orchestrator element**. Its content/
IS the product: the operating doctrine that kernel sessions load when a
RasaOS Studio app addresses this element.

- `content/BUILDER.md` — the builder's operating manual. Editing this file
  changes how every canvas app builds. Fine-tune deliberately; keep it terse
  and imperative (it is read in-context on every app turn).
- `content/COMPONENTS.md` — the component + artifact contract. It MUST stay
  in lockstep with the shell renderer (frontend-rasaos
  `app/src/canvas/components.tsx`); a drift here renders as error tiles or
  dead screens. Change them together.
- `content/KERNEL_ASKS.md` — platform requests; keep it honest (verified
  behaviors only, with dates/versions).

Don'ts: no business logic here (an orchestrator instructs, the kernel
executes); don't bake shell implementation details beyond the renderer
contract; version bumps follow the workspace convention (VERSION +
rasa.json#version + CHANGELOG entry).
