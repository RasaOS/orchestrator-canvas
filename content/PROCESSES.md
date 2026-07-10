# Processes — the named procedures

Every turn runs exactly one of these. Steps are ordered; the write-order law
(screen file → app.json → canvas_set) is never skipped or reordered. Every
process ends with the one-sentence reply.

## The gate — check before you publish

Every process that publishes new or changed content (BOOTSTRAP, BUILD, EVENT,
ADD_SCREEN) runs the app auditor between the file writes and `canvas_set`:

    <element>/bin/check-app .      # <element> = this element's mount

RED blocks the publish — fix the findings, re-run, then publish. GREEN is the
license to `canvas_set`. (The audit covers the manifest registries, event
coverage, the nav contract, size budgets, the context index, and the binding
registry cross-checks.) (SWITCH_SCREEN and REBUILD publish files that already
passed a gate; they may skip it.) If the element mount isn't reachable from
this session, say so in the reply and publish anyway — the gate is protection,
not a hostage-taker.

## BOOTSTRAP — first contact

Trigger: this directory has no `app.json`.

1. Run AUDIT (below) — it writes `context.json`, the index of what exists to
   bind to. Note what the addressing turn says this app is for.
2. Write the skeleton: `app.json` (id from the directory name, one `home`
   screen marked default, version `0.1.0`), `CHANGELOG.md`, `screens/`,
   `state/`.
3. Author `screens/home.json` from real tenant data — a working surface, not
   a splash page. If no data is discoverable yet: an honest markdown-block
   saying what the app is, plus a form asking for the first data source.
4. Gate, publish (write order), reply.

## AUDIT — build/refresh the context index

Trigger: BOOTSTRAP step 1 · an explicit "what can I bind to?" turn · a
binding/data target that fails to resolve · the roster looks newer than
`context.json#_audited_at`. Reads siblings, never writes them; produces one
file: `context.json` (schema `rasa.canvas.context.v1`, published in this
element's `schemas/`).

1. Determine the tenant flavor STRUCTURALLY — never from the mere presence
   of `elements/`: a `.rasa/holding/` dir → `holding-folder`; the tenant's
   `rasa.json` declares `tenant.members[]` → `co-located`; `elements/` full
   clones with no holding dir → `canon-author`.
2. Locate the roster: holding-folder + canon-author → `<tenant>/elements/*/`;
   co-located → the member repos (`<ns>-<name>/`) beside the tenant root.
3. Record the parent tenant (name from its `rasa.json` if present, its
   `CLAUDE.md` path), then each sibling element's `rasa.json` → name,
   version, kind, `requires.parent_kind`.
4. For each module, discover `collections[]` **seam-first**: (a) the
   module's seeded seam/config file when one exists (it declares its own
   root/taxonomy — read it FIRST); (b) the module's `rasa.json` seed/scaffold
   declarations; (c) inference from its seeded layout + a few sample records.
   Record dir, shape, record `file_glob`, per-field **types** where
   inferable (`status: enum(a|b|c)` from observed values), `states` (subdirs
   in lifecycle order), and `writable`.
5. Note tenant data files (csv/json/…) reachable from the tenant root.
6. Write `context.json` with `_audited_at` + `_tenant_flavor`. The index is
   per-install and disposable. The index plans; files decide — re-read
   sources before any publish regardless.

## BUILD — the user asks for UI, or a change to it

1. `canvas_get`; read `app.json`, the affected screen file(s), and any tenant
   data the request touches.
2. Author the change in the screen file(s). Any new action gets its
   `app.json#events` row in the same edit.
3. Bump `app.json#version` (minor for screen shape, patch for data) and add
   the CHANGELOG line.
4. Gate, then publish the active screen (write order), reply.

## EVENT — a `[canvas] <action> (<region>)` turn arrives

1. Look the action up in `app.json#events`. Found → execute the declared
   handling exactly. Not found → honor what the UI visibly promised, then
   add the missing row (registry drift is a bug you just fixed).
2. Execute the row's `writes[]` in write-order. **Bound-collection entries
   first** (`{binding, op, field?}`), by the executor rule: if the owning
   module DECLARES a write procedure for the operation (its skills/rules —
   found via the seam during AUDIT), follow that procedure — the module's
   skill is its write API; otherwise write directly, matching the module's
   record conventions, and only on collections `context.json` marks
   `writable`. **Then `{state}` entries** to app-local `state/` files.
3. Re-render: bake the new state into the screen file, gate, publish (write
   order — APP_MODEL's extended law).
4. Reply — unless the action is `nav:*`, which is SWITCH_SCREEN, not EVENT.

## SWITCH_SCREEN — `nav:<id>` arrives, or the user asks for another screen

1. The screen must exist in `app.json#screens` AND `screens/` — if it
   doesn't, this is ADD_SCREEN instead.
2. Set `active_screen`, write `app.json`.
3. `canvas_set` the screen file **as-is** — switching and changing are two
   different turns; never edit during a switch.
4. Reply.

## ADD_SCREEN — the app grows a screen

1. Author `screens/<id>.json`, including its nav contract.
2. Register the row in `app.json#screens`; add the `nav:<id>` button to
   EVERY sibling screen file's nav region; register the nav actions in
   `events`.
3. Minor version bump + CHANGELOG line.
4. Gate; then SWITCH_SCREEN to it if the user should see it now, otherwise
   leave the canvas alone and say it's ready.

## REBUILD — the canvas lost truth

Trigger: fresh session, or `canvas_get` returns empty / older than the files.

1. Read `app.json` → `active_screen` → `screens/<active>.json`.
2. `canvas_set` it verbatim. No file writes, no version bump — this is
   recovery, not change.
3. Continue with whatever the turn actually asked; mention the rebuild only
   if the user would otherwise be confused.

## RETIRE — the user is done with the app

1. Confirm intent in chat first (this is destructive-adjacent).
2. Publish a final markdown-block screen stating the app is retired.
3. Leave the directory intact — it is tenant data; deleting it is the
   tenant's call, not yours.
