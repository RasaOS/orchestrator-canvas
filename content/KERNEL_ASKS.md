# Kernel asks — what this domain needs from the platform

Filed from the canvas-vertical prototype (frontend-rasaos, 2026-07-07). Each is
surgical; none block the current session-management model.

**Resolved against the shipped kernel (2026-07-12, kernel v0.29–v0.31 + canon
v1.4.0):** #3 (html-embed vocabulary) — `html-embed` is allowlisted + schema-capped
(TASK-249); #10 (kernel-side manifest/layout validation) — `canvas_set` runs ajv
against `rasa.layout.v1.json` + the allowlist + caps at the write boundary
(TASK-226); #5 (documented size limits) — layout 256KB, html-embed 16KB, 64
regions (validator.ts). Still open below: #1 (args.canvas_id), #2 (auto-create
cwd), #4 (element-scoped tool policy), #6 (durability), #7 (revert tool),
#8 (version history), #9 (element-mount handle).

1. **`args.canvas_id` on POST /v1/commands** — address a NAMED canvas from any
   session, decoupling canvas identity from session identity. Retires the
   one-canvas-per-session constraint and enables multi-screen apps.
   *(Doctrine note 2026-07-07: APP_MODEL.md now formalizes screens-as-files
   with a single active-screen projection and a nav contract — the file model
   is already 1:1 ready for named canvases; this ask is the unlock for
   showing screens simultaneously.)*
2. **Auto-create `args.cwd`** (or an explicit `create:true` flag) — today a
   nonexistent cwd silently falls back to the default session (verified live,
   kernel v0.31.0), which forces the shell's bootstrap turn. Auto-vivify would
   remove a whole failure mode.
3. **SA-027 vocabulary: an artifact region kind** (`html-embed {html, height}`)
   — the shell already renders it sandboxed; today it must ride
   `code-block{render:true}` because canvas_set rejects unknown components.
4. **Element-scoped tool policy** — this domain's sessions need
   canvas_* + fs/shell in the app dir; they do NOT need Gmail/web MCPs. The
   manifest declares `permissions`; the kernel should enforce per-element
   tool exposure.
5. **Canvas/layout size limits, documented** — artifacts ride the layout doc;
   the practical ceiling should be a contract, not a discovery.

## Enforcement (filed 2026-07-08)

9. **A stable element-mount handle for sessions** — runtime sessions need to
   invoke tooling that ships with their element: this element's
   `bin/check-app` gates every publish (PROCESSES.md §gate), but the doctrine
   can only say "`<element>/bin/check-app`" because the mount path isn't
   exposed. Ask: give sessions the element's mount path (e.g. a
   `RASA_ELEMENT_ROOT` env var or a documented stable path).
10. **Kernel-side manifest/layout validation** — `canvas_set` already
    validates component names; adopting published schemas would turn the
    doctrine's soft gates into hard walls. The app-manifest contract ships in
    this element at `schemas/rasa.app.v1.schema.json`; a layout-document
    schema is the natural companion (pairs with ask #5's size limits — one
    validation surface, structured errors back to the session).

## Canvas persistence + history (verified against kernel dist, 2026-07-07)

The store is Redis-backed (`canvas/store.js`, key `rasa:canvas:<tenant>:<id>`),
already versioned (every `set` bumps `version`) and keeps one last-known-good
(`lkg`). Three gaps between that and "full functionality":

6. **Bake durability into the image.** Shipped Redis config is `appendonly no`
   + `save 60 1000`, so a `docker restart` wipes all canvases (verified: it
   erased two live canvases). The data dir `/data/redis` is ALREADY a named
   volume — only the flush policy is missing. The shell now hardens this
   post-deploy (`deploy/harden-canvas-persistence.sh`: `appendonly yes` +
   aggressive `save` + `CONFIG REWRITE`), which is restart-durable, but the
   conf lives in the image (`/opt/kernel/state/redis-stack.conf`) so a
   container *recreate* reverts it. Ask: ship the image with `appendonly yes`
   (fsync everysec) so durability is intrinsic, not a bolt-on.
7. **Expose revert.** `store.revert(tenant, canvasId)` already exists and
   restores `lkg` — but it is wired to NOTHING (no MCP tool, no HTTP route;
   the canvas tools are exactly set/patch/get). Ask: add a `canvas_revert`
   MCP tool AND `POST /v1/canvas/{id}/revert`, so the builder can honor "undo
   that" and the shell can offer a Revert control. Small PR — the storage
   half is done.
8. **Real version history.** The store keeps only ONE prior layout (`lkg`), so
   revert is a single step. For genuine history (a version timeline, revert to
   any version N), keep a bounded ring of the last N layouts per canvas +
   `revert_to(version)`. Pairs with ask #7's surface.
