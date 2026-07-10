# rasa.domain.canvas

The **vertical-builder domain**: the runtime brain behind RasaOS canvas
apps ("Studio" verticals). Its sessions author each app's UI as a kernel
canvas (`rasa.layout.v1` + sandboxed html artifacts), persist app state in the
app's own workspace directory, and handle the app's interactions (`ui_event`
turns) — publishing a new canvas version is shipping the app.

- **Doctrine:** `content/BUILDER.md` (how it operates — the fine-tuning surface)
- **App model:** `content/APP_MODEL.md` (what a vertical IS on disk —
  workspace schema, `app.json` manifest, persistence + versioning law,
  multi-screen model)
- **Processes:** `content/PROCESSES.md` (the named procedures — BOOTSTRAP,
  BUILD, EVENT, SWITCH_SCREEN, ADD_SCREEN, REBUILD, RETIRE)
- **Component/artifact contract:** `content/COMPONENTS.md` (kept in lockstep
  with the shell's renderer, frontend-rasaos SA-026/027/028)
- **Platform asks:** `content/KERNEL_ASKS.md`
- **Enforcement:** `schemas/rasa.app.v1.schema.json` (the published manifest
  contract) + `bin/check-app <app-dir>` (audits an app; gates every publish
  per PROCESSES.md §gate) + `bin/check-doctrine` (self-audit; gates every
  commit via `.githooks/pre-commit` and CI). `examples/orders-desk` is the
  golden reference app; `examples/fixtures/*` must fail.

Session model: one app = one session, keyed
`(element=rasa.domain.canvas, cwd=<tenant>/.rasaos/apps/<app-id>)`.
The app directory is the source of truth (`app.json` + `screens/` + `state/`);
the canvas is a projection of the active screen.
