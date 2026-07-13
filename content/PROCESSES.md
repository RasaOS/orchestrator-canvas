# Processes — the named procedures

Every turn runs exactly one of these. Steps are ordered; the write-order law
(screen file → app.json → canvas_set) is never skipped or reordered. Every
process ends with the one-sentence reply.

## The gate — check before you publish

Every process that publishes new or changed content (BOOTSTRAP, BUILD, EVENT,
ADD_SCREEN) runs the app auditor between the file writes and `canvas_set`:

    <element>/bin/check-app .      # <element> = this element's mount

RED blocks the publish — fix the findings, re-run, then publish. GREEN is the
license to `canvas_set`. (SWITCH_SCREEN and REBUILD publish files that already
passed a gate; they may skip it.)

**Unreachable-mount bypass — loud, not silent.** If the element mount isn't
reachable and you cannot run `check-app`, you MAY publish anyway — the gate is
protection, not a hostage-taker — but that publish is UNVERIFIED, so you must:
(a) say so in your one-sentence reply ("published UNCHECKED — check-app
unreachable"), (b) hand-verify the envelope first (`layout_grid` + every
region's `slot` + allowlisted components + the write-order), and (c) re-run
`check-app` and repair at the next turn that can reach it. An unchecked publish
is a temporary, visible state — never the norm. This failure mode closes when
KERNEL_ASKS #9 (a stable element-mount handle) lands.

## BOOTSTRAP — first contact

Trigger: this directory has no `app.json`.

1. Scan the tenant: its `CLAUDE.md`, obvious data files, sibling apps, and
   what the addressing turn says this app is for.
2. Write the skeleton: `app.json` (id from the directory name, one `home`
   screen marked default, version `0.1.0`), `CHANGELOG.md`, `screens/`,
   `state/`.
3. Author `screens/home.json` from real tenant data — a working surface, not
   a splash page. If no data is discoverable yet: an honest markdown-block
   saying what the app is, plus a form asking for the first data source.
4. Gate, publish (write order), reply.

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
2. Apply state changes to `state/` files first.
3. Re-render: bake the new state into the screen file, gate, publish (write
   order).
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

1. **Integrity pass first.** Run `check-app .` — a fresh session, or one
   recovering from an interrupted turn, may find a half-written manifest, an
   orphan/missing screen, or a malformed file. If RED, the write-order law was
   cut mid-flight: repair the directory (re-derive the manifest from the screen
   files, register or drop the orphan) until GREEN before you publish. Recover
   the files, not the canvas.
2. Read `app.json` → `active_screen` → `screens/<active>.json`.
3. `canvas_set` it verbatim. No new content, no version bump — this is
   recovery, not change.
4. Continue with whatever the turn actually asked; mention the rebuild only
   if the user would otherwise be confused.

## RETIRE — the user is done with the app

1. Confirm intent in chat first (this is destructive-adjacent).
2. Publish a final markdown-block screen stating the app is retired.
3. Leave the directory intact — it is tenant data; deleting it is the
   tenant's call, not yours.
