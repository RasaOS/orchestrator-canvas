# rasa.orchestrator.canvas

The **vertical-builder orchestrator**: the runtime brain behind RasaOS canvas
apps ("Studio" verticals). Its sessions author each app's UI as a kernel
canvas (`rasa.layout.v1` + sandboxed html artifacts), persist app state in the
app's own workspace directory, and handle the app's interactions (`ui_event`
turns) — publishing a new canvas version is shipping the app.

- **Doctrine:** `content/BUILDER.md` (how it operates — the fine-tuning surface)
- **Component/artifact contract:** `content/COMPONENTS.md` (kept in lockstep
  with the shell's renderer, frontend-rasaos SA-026/027/028)
- **Platform asks:** `content/KERNEL_ASKS.md`

Session model: one app = one session, keyed
`(element=rasa.orchestrator.canvas, cwd=<workspace>/.rasaos/apps/<app-id>)`.
