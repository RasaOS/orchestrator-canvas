# Page-creation standard — design spec

> **STATUS: STAGED FOR PHASE B. Not live doctrine.**
> This is a design document, not part of `content/`. Runtime sessions never
> read it. It captures the page-creation standard so the Phase B hardening
> pass (see `[[canvas-hardening-plan]]`) authors it into the doctrine in ONE
> clean pass, against the **real** `rasa.layout.v1` contract
> (`layout_grid` + `slot` + canonical prop keys), never the current fictional
> flat-region shape. Author, don't invent, from this file.

## Why this exists

Today the doctrine has the *mechanics* of multi-screen apps — the nav
contract, the events registry, `ADD_SCREEN`, `card-list on_click` — but no
**named, enforced page pattern** and no **multi-screen build procedure**. A
runtime session building "show me my backlog" has no standard that forces each
task to be openable into a detail screen; it's left to taste, so it drifts.

This spec locks two things:

1. **LIST_DETAIL** — the openable-list → detail-screen pattern (a page
   *pattern*: a fixed composition of components + events + screens).
2. **SCAFFOLD** — publish the primary screen fast, fan out siblings, reveal
   when ready (a *procedure*: how a multi-screen app gets built in order).

The difference between a *guideline* and a *standard* here is the **check-app
invariant** (§4). A guideline is advice the builder may follow; the invariant
is a red gate — ship a list with a dead "open" button and the publish is
blocked. That is the lock.

---

## 1. LIST_DETAIL — the openable-list pattern

**Trigger.** A screen shows a collection of records (tasks, orders, leads,
docs…) and any record carries more detail than a row can hold. i.e. "give me a
list where I can click into each one."

**Component choice (load-bearing).** Use **`card-list`** — its cards have
native per-item `on_click` (COMPONENTS.md). Do **not** use `table` for an
openable list: a `table` is `{columns, rows}` only, with no per-row click.
`table` is for dense, read-only tabular data. (Clickable table rows are a
kernel gap — see §6.)

**Expansion (fixed).** A LIST_DETAIL surface always produces:

- **List screen** — a `card-list` bound to the collection; each card's
  `on_click` value is an **`open:<record-id>`** action.
- **An event row per open** (or one templated row, see below) in
  `app.json#events`, declaring how the detail is produced.
- **Detail screen** — `detail-<record-id>.json`, bound to that one record,
  carrying `nav` back to the list (`nav:<list-screen>`). The detail screen is a
  **LEAF** (`parent: <list-screen>`); its `nav` is one back button, and the list
  card's `open:*` events row carries `target: <detail-id>` so the leaf is
  provably reachable. (Nav model shipped in 0.6.0 — see **§8.5**.)

### Example — the "backlog" case (REAL contract shape)

Degenerate single-column grid per the hardening plan: `layout_grid:"full"` +
every region `slot:"main"`, `ai_rail_inherited:true`. Exact slot-per-region
semantics reconcile to the vendored kernel schema in Phase B; the pattern
logic here is independent of that.

`screens/backlog.json`:

```json
{
  "layout": "1.0.0",
  "screen": { "name": "backlog", "title": "Backlog", "layout_grid": "full", "ai_rail_inherited": true },
  "regions": [
    { "id": "nav", "slot": "main", "component": "button-row",
      "props": { "buttons": [ { "id": "nav:home", "label": "Overview" } ] } },
    { "id": "tasks", "slot": "main", "component": "card-list",
      "props": { "cards": [
        { "title": "Fix auth redirect", "subtitle": "open · high",        "on_click": "open:task-1042" },
        { "title": "Ship canvas gate",  "subtitle": "in progress · med",  "on_click": "open:task-1041" }
      ] } }
  ]
}
```

`screens/detail-task-1042.json`:

```json
{
  "layout": "1.0.0",
  "screen": { "name": "detail-task-1042", "title": "Fix auth redirect", "layout_grid": "full", "ai_rail_inherited": true },
  "regions": [
    { "id": "nav", "slot": "main", "component": "button-row",
      "props": { "buttons": [ { "id": "nav:backlog", "label": "← Backlog" } ] } },
    { "id": "summary", "slot": "main", "component": "kpi-tile",
      "props": { "value": "high", "label": "Priority" } },
    { "id": "body", "slot": "main", "component": "markdown-block",
      "props": { "content": "**Status:** open\n\nRedirect drops `return_to` after SSO…" } }
  ]
}
```

`app.json#events` additions:

```json
{ "action": "open:task-1042", "emits": ["tasks"], "handling": "reuse or author detail-task-1042 bound to task 1042, then SWITCH_SCREEN to it" },
{ "action": "nav:backlog",    "emits": ["nav"],   "handling": "SWITCH_SCREEN backlog" }
```

`app.json#screens`: `backlog` and every `detail-*` that has been authored are
registered. (Lazy details not yet built are NOT registered — see §2.)

### The two build strategies

- **Lazy (default).** The list ships now; each `detail-<id>` is authored on
  first `open:<id>` (the EVENT process runs `ADD_SCREEN`, then
  `SWITCH_SCREEN`). Cheapest, matches BUILDER's "publish honest first version
  fast." The event row declares author-on-open, so the wiring is real even
  though the file isn't there yet.
- **Eager.** Pre-author the detail screens (or one detail *template*) in the
  same turn as the list, so the first click renders instantly. Use for small,
  hot record sets. Heavier.

Recommend lazy as the default; eager on explicit request or when the record
set is small and known.

---

## 2. SCAFFOLD — build a multi-screen app in order

**Trigger.** The request implies a screen *graph*, not one surface (a
list + details, or several sections). `BOOTSTRAP` escalates to `SCAFFOLD` when
first contact needs more than a home screen.

**Steps.**

1. **Sketch the graph.** Name the primary (what the user asked to see first)
   and the siblings/details. Register the *known* screens in `app.json#screens`
   and their nav/open actions in `events`.
2. **Publish the primary first.** Author + gate + publish the primary screen
   (write-order law). **Reply now** — the user gets a working surface fast.
3. **Fan out the rest, in priority order**, by strategy:
   - *Eager* — author each sibling/detail file this turn, register it, keep
     `active_screen` on the primary. Siblings are one nav/open tap away the
     instant their files land. Optionally pre-author one detail template.
   - *Lazy (default)* — don't author details now; `open:*` rows declare
     author-on-open; EVENT → ADD_SCREEN builds each on first click.
4. **Reveal when ready.** Either auto-`SWITCH_SCREEN` to a just-finished
   screen the user is waiting on, or leave the primary active and let nav/open
   surface siblings. Never show a half-authored screen — the write-order law
   and the gate still hold per screen.

**Honest note on "background."** One app = one session; turns are driven by
`ui_event`s. There is **no background thread.** "Publish page 1, build page 2
in the background, show when ready" maps to: a fast primary publish, then
sibling files authored either *within the same turn* (eager) or *on a later
turn* (lazy, on open). The UX of "more appears when ready" is real — it's
gated, declared screens becoming reachable — but it is sequential under the
hood. The doctrine must promise exactly this and not imply async it can't do.

`SCAFFOLD` is the orchestration; `ADD_SCREEN` is its unit. They coexist.

---

## 3. Where each piece lands in the doctrine (placement map)

| Piece | Home | Note |
|---|---|---|
| LIST_DETAIL pattern | **`content/PATTERNS.md`** (NEW — **DECIDED 2026-07-11**) | Patterns compose components + events + screens; they sit above COMPONENTS (per-region) and above any single PROCESS (per-turn). A pattern library is its own layer. It is a *library*, not a one-entry file — see §8 for the entry schema + catalog. |
| SCAFFOLD process | `content/PROCESSES.md` | New named process; cross-ref `ADD_SCREEN` as its unit. |
| Builder pointer | `content/BUILDER.md` | One line: "When a screen matches a known shape, expand it per PATTERNS.md; when an app needs a screen graph, run SCAFFOLD." |
| The invariant | `bin/_contract.py` + `bin/check-app` | The `open:*` target-resolution rule (§4). |
| Doctrine lockstep | `bin/check-doctrine` | PATTERNS.md IS a doctrine file (decided); add it to the lockstep set (5th file, alongside BUILDER/APP_MODEL/PROCESSES/COMPONENTS). |
| Reference | `examples/orders-desk` | Extend the golden to demonstrate LIST_DETAIL (per-row `open:` → order detail), replacing the current degenerate "Open newest" single button. Must pass check-app. |
| Schema | `schemas/rasa.app.v1.schema.json` | No change required (see open decision #3). |

---

## 4. The lock — the check-app invariant

The rule that turns this from guideline to standard. Analogous to the existing
nav-target check (`nav:<id>` must have a screen).

**Rule.** For every published screen, every emitted action `A` (card
`on_click`, button `id`, form `submit`) that matches `open:*`:

1. **must have an `events[]` row** for `A` (registry exhaustiveness — already a
   general check), and
2. **that row must resolve** — either its target `detail-<id>` screen is
   registered in `screens[]` (eager), **or** the row's `handling` declares
   author-on-open (lazy).

Deliberately, the invariant does **not** require the detail *file* to
pre-exist — that would kill the lazy strategy. What it forbids is a **dead
open button**: an `open:*` with no declared handling. That is the real bug this
prevents.

Pseudocode (for `bin/check-app`):

```
for screen in screens/*.json:
  for action in emitted_actions(screen):        # card on_click, button id, form submit
    if action.startswith("open:"):
      row = events_row(action)
      assert row is not None                      # no unregistered open
      assert (row.target in registered_screens)   # eager: detail exists
          or row.declares_author_on_open()        # lazy: handling declares it
```

`bin/_contract.py` carries the shared predicate list; `check-doctrine`
already enforces `_contract.py` ↔ COMPONENTS.md, so keep the emitted-action
extraction in sync there.

---

## 5. Dependencies on Phase B (must be true before authoring)

Do not author this until the Phase B reconciliation has landed these, or the
examples will be written against fiction again:

- `screen.layout_grid` + `region.slot` + `ai_rail_inherited` adopted in
  APP_MODEL, the golden, and fixtures (Phase B core). Confirm exact field
  placement + slot semantics against the **vendored kernel schema**.
- check-app re-based on the vendored kernel schema, so the §4 invariant sits on
  a gate that means "canvas_set will accept it."
- Canonical prop keys locked. `card-list on_click` is already documented
  (COMPONENTS.md:31, reconciled in commit 5c2ce61); `layout_grid`/`slot` are
  the still-pending part.
- ~~**Nav contract reconciled from full-mesh to back-to-parent** (§8.5)~~ **DONE
  2026-07-12 (domain-canvas 0.6.0)** — the hard prerequisite is cleared:
  `check-app` now enforces sections-mesh / leaves-climb + `events[].target`
  reachability; LIST_DETAIL is authorable.
- ~~drop `card-strip` from the `screen_actions` `on_click` harvest (`check-app:68`
  false-positive)~~ **DONE 2026-07-12 (0.6.1)** — dropped from the harvest *and*
  hard-FAILed with a guarding fixture (§8.4).
- **check-app fixes (still pending):** `_contract.py` KERNEL_ALLOWLIST 21→12 +
  html-embed into SHELL_RENDERED (Phase B proper, canon-gated).

---

## 6. Open decisions (defer to authoring time) + a kernel gap

1. ~~PATTERNS.md as a new doctrine file vs. fold into COMPONENTS + PROCESSES.~~
   **DECIDED 2026-07-11: new file.** Patterns are a distinct layer; the 5th
   check-doctrine lockstep file is the accepted cost. Entry schema + candidate
   catalog are §8.
2. **Default strategy: lazy vs. eager.** Recommend lazy default, eager on
   request / small hot sets.
3. **Add `screen.status: planned|ready` to the schema?** Would let check-app
   tell "planned-but-unbuilt" from "orphan." Recommend **no** initially — a
   planned lazy screen is just an `open:*` row with author-on-open handling;
   the §4 invariant already covers it. Add only if the distinction earns its
   keep.
4. **KERNEL GAP — clickable table rows.** `table` renders `{columns, rows}`
   with no per-row `on_click`; only `card-list` gives per-item click. So
   LIST_DETAIL over genuinely tabular data forces card-list (losing column
   alignment) or an adjacent affordance. File a `KERNEL_ASKS.md` entry
   requesting per-row `on_click` / a row-action column on `table`. Until then,
   the pattern rule is explicit: **openable list ⇒ card-list.**

---

## 7. Done-when (for the Phase B authoring pass)

- `content/PATTERNS.md` (new doctrine file) carries LIST_DETAIL with the real
  contract shape, follows the §8 entry schema, and `check-doctrine` adds it as
  a 5th lockstep file.
- `content/PROCESSES.md` carries SCAFFOLD; BUILDER.md points to both.
- `bin/check-app` enforces the §4 `open:*` invariant; `_contract.py` in sync;
  `check-doctrine` GREEN.
- `examples/orders-desk` demonstrates LIST_DETAIL (per-row open → detail
  screen) and passes check-app **and** the real kernel `validateLayout`.
- A negative fixture (list with a dead `open:` button) is added and **fails**
  check-app, proving the lock.
- KERNEL_ASKS.md updated with the table-row-click gap (§6.4) and the other
  gaps consolidated in §8.4.
- The nav-contract scaling fix (§8.5) is designed and the golden reflects it.

---

## 8. The pattern library — entry schema + catalog

Source: a 7-agent fan-out (5 pattern-family scouts → synthesis → an adversarial
completeness critic), 2026-07-12. 35 raw candidates → 23 patterns. The critic's
findings were then **verified against the actual `bin/check-app` and
`bin/_contract.py`** — see §8.4 (confidence tagged; not trusted on the critic's
word). This is a *design* catalog: names, triggers, component-choices, and
invariants. **Only LIST_DETAIL is authored into doctrine in Phase B** unless
more are greenlit; everything else is staged.

### 8.1 Entry schema — the fixed shape of every PATTERNS.md entry

Every pattern in the library is written to these fields, in order:

1. **name** — UPPER_SNAKE_CASE, unique.
2. **trigger** — the user ask / app condition, one line, in the user's words.
3. **components** — which of the rendered allowlist it expands to, with the
   why-this-not-that noted (e.g. "card-list not table — table has no per-row click").
4. **expansion** — the concrete region layout in document order: each region's
   component + the action it emits, plus any sibling screens it registers.
5. **emits** — exhaustive action verbs it introduces; each becomes an
   `app.json#events` row.
6. **spawns_screens** — registers sibling `screens[]` (which), or single-screen.
7. **build_strategies** — how the builder assembles it: SCAFFOLD primary-fast-
   then-fan-out; EVENT re-render in place vs SWITCH_SCREEN; declarative vs artifact.
8. **invariant** — the check-app rule it implies: what must hold for GREEN, what
   turns it RED.
9. **buildable_now** — true/false against the (post-Phase-B) rendered allowlist.
10. **kernel_gap** — if not buildable, the exact missing capability; else "".
11. **composes_with** — sibling patterns it builds on / pairs with.

### 8.2 Core — author these first (in Phase B, priority order)

- **LIST_DETAIL** — openable list → per-record detail screen. (Fully specified
  in §1. Built on `card-list`.) *Nav caveat: see §8.5.*
- **RECORD_DETAIL** — *"open this order/customer and show me everything."* The
  rich single-record page LIST_DETAIL lands on: header `kpi-tile`s + attribute
  `table`/`markdown-block` + related `card-list`s + history `timeline` + action
  `button-row`. LIST_DETAIL only *spawns* it; this names what it composes to.
  Buildable now. *(Added by the critic — the single most common page in a data
  app, previously only implied.)*
- **DASHBOARD_OVERVIEW** — the landing/home: `kpi-tile` strip + `chart` +
  routing `card-list`/`button-row`. Summarize-and-route. Emits `nav:*`,
  `open:*`, `refresh_requested`. (Merged METRIC_OVERVIEW + OVERVIEW_HUB +
  LIVE_METRIC_STRIP.) Note: kpi-tiles flow vertically; a horizontal strip needs
  per-region `frame{x,y,w,h}`.
- **TAB_SHELL** — a few co-equal sections flipped like tabs. A `button-row` nav
  on every section. *Directly implicated by the nav-mesh problem, §8.5.*
- **FILTER_SEARCH** — `form` (query) → re-derived result surface on the *same*
  screen (EVENT). Result is `card-list` if rows must open, else `table`. No
  client-side filter; each query is a builder round-trip. ≤1 form per screen
  (bare `submit` collides). (Merged SEARCH_TO_RESULTS + FILTERED_TABLE.)
- **CREATE_RECORD_FORM** — `form` → append a record to a `state/`/`data/` file
  (write-order law). `submit` + `cancel_create`. ≤1 form per screen.
- **MASTER_DETAIL_SPLIT** — list + selected detail on *one* screen (inbox
  layout) via `select:<id>` → re-author the detail region in place. Distinct
  from LIST_DETAIL (which navigates to a spawned screen). Needs `frame` for
  side-by-side; selection highlight is baked in (card-list persists none).

### 8.3 Extended — the rest of the library (staged)

`bn?` = buildable_now. Gaps are consolidated in §8.4.

| Pattern | Trigger (short) | Key components | bn? | Gap |
|---|---|---|---|---|
| QUICK_ACTION_BAR | persistent command verbs (New/Refresh/Export) | button-row | ✓ | — |
| CROSS_LINK | detail → related records on other entities | card-list, button-row | ✓ | — (nav §8.5) |
| BREADCRUMB_TRAIL | climb back up a nesting hierarchy | button-row | ✓ | no nav history/stack (static trail only) |
| CHART_BREAKDOWN | aggregation/breakdown, re-groupable | chart, kpi-tile, table | ~ | chart = single-series horizontal bars; no grouped/line/pie |
| ACTIVITY_FEED | chronological read / notifications | timeline, card-strip | ✓ | no ephemeral toast (durable feed only) |
| EMPTY_STATE | no data yet / first-run | markdown-block, form, button-row | ✓ | — (no-fabrication is builder discipline) |
| EDIT_RECORD_FORM | edit existing record, values pre-filled | form (or artifact) | ✗ | `form` field has no `value`/`default` → blank submit overwrites |
| CONFIRM_DESTRUCTIVE | confirm irreversible action | markdown-block, button-row | ✓ | no modal/overlay (inline or sibling screen only) |
| INLINE_FIELD_UPDATE | set one enum/toggle field fast | button-row, card-list | ✓ | — (value encoded in action id) |
| DECISION_PROMPT | approve/reject / pick-one, on canvas | markdown-block, button-row, form | ✓ | — |
| WIZARD_FLOW | multi-step create/config | form, button-row, timeline | ✓ | — (nav §8.5; ≤1 form/step) |
| BULK_ACTION | one action over many records | button-row, table/card-list | ~ | no multi-select/checkbox (whole-set only; subset blocked) |
| SETTINGS_SCREEN | app-level config bound to own state | form, button-row | ✓ | ≤1 form/screen |
| REFRESH_POLL_SURFACE | watch drifting state, pull latest | kpi-tile, table, button-row | ✓ | no push channel (turn-granularity only) |
| JOB_PROGRESS_TRACKER | long job progress from state | kpi-tile, chart, timeline | ✓ | determinate only; no push channel |
| ACTIONABLE_TABLE | drill/sort from a dense table row | table (→card-list) | ✗ | `table` emits nothing (the clickable-table gap) |
| CUSTOM_VIZ_EMBED | non-allowlisted visual (map/line/3D) | html-embed/code-block, kpi-tile | ✓ | — (data baked in; CSP blocks fetch) |
| INTERACTIVE_CONTROL_ARTIFACT | custom input (slider/picker/pad) | html-embed/code-block, kpi-tile | ✓ | — (commit round-trips via rasa.emit) |
| GROUPED_LIST | group records by column (kanban-style) | card-list ×N, markdown-block | ✓ | `kanban` error-tiles → stacked card-lists |
| PAGINATED_LIST | page through hundreds of rows | card-list/table, button-row | ✓ | no pagination primitive; size cap forces windowing |
| DATA_EXPORT | download as CSV | code-block, button-row | ~ | no file-download affordance (text-for-copy only) |
| CALENDAR_VIEW | due dates on a month grid | (artifact) | ✗ | `calendar-grid` error-tiles; no rendered calendar |
| MEDIA_GALLERY | show product photos / receipts | (artifact data-URI) | ✗ | media-viewer link-only; no image embed (SA-027) |

*(Bottom 5 added by the completeness critic.)*

### 8.4 Critique — verified against the actual gate

The critic's claims, checked against `bin/check-app` + `bin/_contract.py`:

**CONFIRMED — real, must address in Phase B:**
- **Full-mesh nav** (`check-app:179-194`) — the big one; own section §8.5.
- ~~**card-strip `on_click` false-positive** (`check-app:68`)~~ **FIXED 2026-07-12
  (0.6.1).** `screen_actions` had harvested `on_click` from `card-strip` *and*
  `card-list`, but the shell renders card-strip clicks dead (COMPONENTS.md:30), so
  a registered card-strip click passed the gate as a "handled" event that can never
  fire. Fix went further than "drop from the harvest": card-strip is dropped from
  the live-action harvest **and** a card-strip carrying any `on_click` is now a hard
  **FAIL** ("use card-list for clickable cards") — an always-wrong authoring mistake,
  guarded by the `card-strip-onclick` fixture. A presentational card-strip (no
  `on_click`) still passes.
- **`table` emits nothing** (`check-app:58-76`) — confirms the clickable-table
  gap: `table` contributes zero actions; drill-down must route through card-list.

**DRIFT — already resolved by Phase B (critic read today's drifted files):**
- **html-embed "not allowlisted / only 11 render"** — true of today's
  `_contract.py` (21-item KERNEL_ALLOWLIST, no html-embed; SHELL_RENDERED = 11).
  But that 21-list is the mislabeled schema enum; the real kernel allowlist is 12
  incl. html-embed first-class ([[canvas-kernel-contract-drift]]). Phase B fixes
  `_contract.py` 21→12 + html-embed into SHELL_RENDERED. The catalog assumes the
  post-Phase-B allowlist — correct target. Interim carriage: `code-block{render:true}`.
- **32KB layout cap** — real (`check-app:36`) but element-side; real kernel is
  256KB, Phase B raises it toward 250/256KB. PAGINATED_LIST still warranted —
  even 256KB caps row counts.

**Consolidated kernel gaps (→ `content/KERNEL_ASKS.md`):**
1. `table` emits no ui_events (no per-row `on_click`, no column sort). *[blocks ACTIONABLE_TABLE]*
2. `form` field has no `value`/`default` (edit forms can't pre-fill submittably). *[EDIT_RECORD_FORM]*
3. No multi-select/checkbox component (arbitrary subset selection). *[BULK_ACTION]*
4. No kernel→canvas push channel / reactive binding (every refresh = a full turn). *[REFRESH_POLL_SURFACE, JOB_PROGRESS_TRACKER; kills true LIVE_TAIL]*
5. No modal/overlay region (`modal` error-tiles; artifacts clipped to their box). *[CONFIRM_DESTRUCTIVE overlay variant]*
6. `form` emits one bare literal `submit` (no per-form id) → ≤1 form/screen. *[FILTER_SEARCH, CREATE_RECORD_FORM, WIZARD_FLOW, SETTINGS_SCREEN]*
7. No file-download affordance. *[DATA_EXPORT]*
8. No inline image embed (media-viewer link-only, SA-027). *[MEDIA_GALLERY]*
9. `calendar-grid` / `kanban` allowlisted but error-tile (not shell-rendered). *[CALENDAR_VIEW, GROUPED_LIST]*

### 8.5 The nav-contract scaling problem (LOAD-BEARING — NEW finding)

**The current nav contract does not scale to per-record detail screens, and
LIST_DETAIL forces the issue.** `check-app:179-194` enforces a **full mesh**:
on any multi-screen app, *every* screen must carry a `nav` button-row reaching
*every other registered screen* (`missing = set(ids) - {sid} - targets` → FAIL).
APP_MODEL.md §multi-screen says the same ("one per OTHER screen"). That is fine
for 3–4 co-equal sections (TAB_SHELL). It breaks for LIST_DETAIL / RECORD_DETAIL
/ CROSS_LINK / WIZARD_FLOW: N record-detail screens each demand N−1 nav buttons
to every sibling detail — combinatorial blow-up that also breaches the size cap.

This was a real architectural gap, absent from both hardening memories.

**RESOLVED 2026-07-12 — shipped in domain-canvas 0.6.0.** A design fan-out
(3 models → judge panel → adversarial verify) settled it, and it is now
implemented. The model unifies the two options that were on the table (screen
classes + hierarchical parent):

- One optional `screens[].parent` field. **SECTION** = no parent (a tab; meshes
  to peer sections only). **LEAF** = has parent (a spawned detail/step; its `nav`
  region carries only ancestor back-links — `parent ∈ targets ⊆ ancestors`,
  default one back button). Parent graph must be acyclic + rooted.
- The `nav` region is **structural only**; every forward/lateral jump lives in a
  content region, and its `events[]` row carries a new optional `target:
  <screen-id>`. `check-app` proves every leaf is reachable from a content-region
  `nav:` link **or** an `events[].target` (hard-fail — the user's chosen option
  over a soft WARN).
- Kills the N² blow-up (N details = N one-button leaves); golden `orders-desk`
  stays GREEN (home/orders are peer sections); new golden `examples/task-backlog`
  demonstrates LIST_DETAIL; 4 new negative fixtures guard the new teeth.

The adversarial pass **failed the first spec** and was right to: it caught that a
hard reachability check keyed on literal `nav:<leaf>` links would false-fail the
doctrine's own semantic openers (`order_opened`, form `submit`). The fix — count
`events[].target` as a forward edge — is what shipped. Accepted, disclosed
limits: cross-link back is canonical (not path-sensitive); a deep leaf reaches a
non-ancestor section by climb-then-tab; wizard step-1 is a leaf off a launcher,
not a section. See CHANGELOG 0.6.0 and APP_MODEL §multi-screen.
