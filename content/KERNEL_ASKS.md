# Kernel asks — what this orchestrator needs from the platform

Filed from the canvas-vertical prototype (frontend-rasaos, 2026-07-07). Each is
surgical; none block the current session-management model.

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
3. **SA-027 vocabulary: an artifact region kind** (`html-embed {html, height}`).
   **RE-VERIFIED 2026-07-09 (HOTFIX-001):** the original claim ("the shell
   already renders it sandboxed") is **TRUE on frontend-rasaos `main` @
   `a5f6ff1`** — `components.tsx` ships `HtmlEmbed` serving BOTH the
   `code-block{render:true}` carriage (`:64-68`) and a direct `html-embed`
   arm (`:69-70`), with `sandbox="allow-scripts"` + injected CSP
   (`connect-src 'none'`) + the `window.rasa.emit` bridge. *(An intermediate
   2026-07-09 correction marked this FALSE — it had read a checkout without
   `a5f6ff1`; lesson: cross-repo evidence is now SHA-pinned per the
   done-gate.)* **The remaining ask is kernel-side only:** add `html-embed`
   to the canvas component allowlist + the published `rasa.layout.v1` schema
   enum, with a `props.html` maxLength cap (~16KB) and `height` bounds — then
   the direct form replaces the carriage. Spec: `docs/design/html-embed-spec.md`;
   see also `docs/handoff/KERNEL_GAPS.md` K1.
4. **Element-scoped tool policy** — this orchestrator's sessions need
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

## Data binding + reactivity (filed 2026-07-09; verified against kernel v0.27.0 source)

The binding objective: a canvas region bound to tenant/module files updates
when those files change — by ANY writer, not just this session. What already
exists (verified): an fsnotify file-watcher runs at boot
(`gateway/internal/filewatch.go`) and publishes `file.*` events to
`events.files.*`; the per-canvas SSE push (`GET /v1/canvas/{id}/watch`) is
live and robust; `PUT /v1/fs/{path}` writes files and emits authoritative
`file.*` events. The watcher is wired to NOTHING on the canvas side. Full
context: `docs/handoff/KERNEL_GAPS.md` (this repo).

11. **A file-event → canvas bridge.** Subscribe to `events.files.*`; when a
    changed path falls inside a session's app/bound scope, refresh the canvas.
    Mechanism options (decision pending, see the handoff doc): (a) kernel
    parses `app.json` bindings — rejected, couples kernel to element doctrine;
    (b) bindings registered with the canvas doc at publish — fast direct
    patching, but only for trivial projections; (c) **recommended v1**: the
    bridge nudges the owning session (a system turn naming the changed path);
    the session re-derives and republishes — works for every binding shape,
    zero kernel coupling, one-turn latency. (b) can layer on later for
    sub-second simple projections. Loop-protection needed (the session's own
    writes must not re-trigger it; precedent: `recentlyAPIWritten` dedup).
12. **A direct edit → file write path** (no LLM turn): `POST
    /v1/canvas/{id}/edit` (or a `field.commit` event) that, for a bound
    region, writes the target file directly (validated, tenant-scoped) and
    emits both `file.*` and `ui` events. Precedent: `PUT /v1/fs/{path}`.
    Pairs with #11: the write triggers the bridge, which refreshes the canvas
    — closing "user edits a bound field → file updates → UI reflects"
    without a model in the loop. Honest caveat to carry: inotify over the
    macOS Docker bind-mount is best-effort — host-side edits should route
    through `/v1/fs` (the kernel's own `filewatch.go` documents this).
