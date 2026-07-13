# Design — the canvas binding model

**Status:** DRAFT / reviewable spec. Not yet ratified doctrine.
**Author pass:** 2026-07-09 (core-internal-structure session).
**Companion:** `docs/design/ui-engine-and-architecture.md` (the render/UI engine, design
system, and per-layer engine choices). This doc is the *data*/binding half; that doc is the
*render* half. Note: bound UIs render **only** through the frozen declarative component set
(tables/lists/forms/kpis/nav); custom visuals/3D go through the sandboxed `html-embed`
escape region — live in the shell @ `a5f6ff1` (see that doc §2.1/§2.1a).
**Fold targets once ratified:** `content/APP_MODEL.md` (the store + `bindings[]` +
`context.json`), `content/PROCESSES.md` (the `AUDIT` process + provision/bind steps),
`content/BUILDER.md` (the three-modes doctrine), `content/KERNEL_ASKS.md` (asks #11–#12),
`schemas/rasa.app.v1.schema.json` + `bin/check-app` + `bin/_contract.py` (enforcement),
`examples/orders-desk` (golden example gains a binding).

This document exists to be **red-lined before any code is written**. Nothing here
changes runtime behavior until it is folded into `content/`.

---

## 0. Why this exists (the post-fold world, in one breath)

Canon SA-023 ("the fold", WORKING in v1.4.0) removed the `orchestrator` kind; the
**tenant is now the orchestrator** (its brain is `rasa.tenant.core`). This element was
`rasa.orchestrator.canvas` and is now **`rasa.domain.canvas`, kind=domain** — *"a
knowledge brain that installs into a project and can host modules; NOT a sub-tenant."*
It sits **inside a tenant, alongside sibling domains and modules.** See the Evidence
Appendix (§A) for the grounded facts and citations behind every claim in this doc.

The four requirements this design serves:

1. Be a domain that **creates/utilizes modules** (real Element folders, not markdown files).
2. **Bind UIs to tenant/domain/module data** (mainly module) — files change → UI reflects;
   button press → files update. Two-way.
3. **Audit parent + sibling data at install** → keep a **registry of context** (domains,
   modules, data structure, types) so bound UIs can be planned.
4. **Stay generic** — a template brain installed anywhere that takes on a life of its own.

---

## 1. The core model — a binding brain, not a storage engine

**domain.canvas does not own the data. The sibling record-modules do**
(`module-research`, `module-tasks`, `module-notes`, `module-field-log`, `module-schedule`,
`module-ingest` …). Each is a project-owned store of records: a directory of frontmatter
files organized by a state-machine of subdirectories — *directory = collection,
subdirectory = state, frontmatter = fields*. That is already a UI-ready data model on disk
(§A6).

What domain.canvas owns is **one dedicated place that knows how to bind**: the app store,
extended with a **binding registry** and a **context index**. Every UI resolves to a
binding. Even "make me something new" resolves to *provision a record in a module, then
bind to it* (§4, mode `provision`).

Consequence for requirement #1: domain.canvas **owns zero modules initially.** It binds to
the modules that already exist. We revisit authoring a companion `module-canvas-*` only if
a canvas-specific record type appears that no existing module holds (§6).

---

## 2. The place — the canvas store, extended

```
<tenant>/.rasaos/apps/<app-id>/
├── app.json          # + bindings[]  ← the binding registry              (NEW)
├── context.json      # the install/bootstrap audit index                 (NEW, per-install, discovered)
├── CHANGELOG.md
├── screens/*.json    # rasa.layout.v1, one per screen                    (unchanged)
├── state/*.json      # app-local memory                                  (unchanged)
└── data/*.json       # derived/cached views (_source + _derived_at)      (unchanged)
```

Two additions carry the whole model: `context.json` (what exists to bind to — §3) and
`app.json#bindings[]` (how each region is bound — §5). Both are **per-install data**, never
baked into `content/` — the stay-generic line (§7).

---

## 3. `context.json` — the audit / context registry (requirement #3)

The **planning input** for bound-UI authoring. Produced by a new `AUDIT` step (§8) that
walks the parent tenant + sibling domains/modules and records each module's data
collections and record shapes. It is discovered, per-install, and disposable (re-derivable
by re-running the audit).

### Shape (`rasa.canvas.context.v1`)

```json
{
  "_schema": "rasa.canvas.context.v1",
  "_audited_at": "2026-07-09T18:20:00Z",
  "_tenant_flavor": "holding-folder",          // holding-folder | co-located | canon-author (§3 rules)
  "_tenant_root": "../../..",                   // relative to this app dir
  "tenant":  { "name": "rasa.tenant.rasaos", "claude_md": "../../../CLAUDE.md" },
  "domains": [
    { "name": "rasa.domain.soccer.goalkeeping", "path": "../../../elements/domain-soccer-goalkeeping",
      "version": "0.2.0", "description": "…" }
  ],
  "modules": [
    { "name": "rasa.module.tasks", "path": "../../../elements/module-tasks",
      "version": "0.1.3", "parent_kind": ["domain", "tenant"],
      "collections": [
        { "id": "tasks", "dir": "tasks", "shape": "folder-of-records",
          "record": { "file_glob": "TASK-*.md",
                      "fields": { "id": "string", "category": "string",
                                  "status": "enum(triage|backlog|active|blocked|completed)" },
                      "states": ["triage", "backlog", "active", "blocked", "completed"] },
          "writable": true }
      ] }
  ],
  "tenant_data": [
    { "path": "../../../data/orders.csv", "kind": "csv", "purpose": "orders table" }
  ]
}
```

### Rules

- **All THREE tenant flavors are handled** (a design-review correction — SA-019 WC-001
  defines a third): holding-folder → siblings at `<tenant-root>/elements/<name>/` +
  hidden `.rasa/holding/`; co-located → member repos `<ns>-<name>/`, no `elements/`;
  **canon-author** → full clones under `elements/`, NO holding folder (the rasaos
  workspace itself). Detection must be **structural**, not presence-of-`elements/`:
  `.rasa/holding/` present → holding-folder; `tenant.members[]` declared → co-located;
  `elements/` full clones without holding → canon-author.
- **Naming tension — RESOLVED for now (TASK-006, user decision 2026-07-09): keep
  `.rasaos/apps/` and file upstream.** The live shell (`VerticalCanvasPane` @ `a5f6ff1`)
  bootstraps `.rasaos/apps/<id>`; doctrine stays in agreement with reality, and the
  platform-level naming question goes to canon as a draft
  (`docs/canon-drafts/SA-0XX-tenant-app-state-directory.md`, files via TASK-007). If canon
  rules `.rasa/apps/`, the element migrates in ONE coordinated pass with the frontend.
- **Source of the walk:** filesystem today (readable from cwd — §A4); the kernel's
  `GET /v1/elements` registry is the cleaner future source (§A7) and `PUT /v1/fs` the
  deterministic file surface. The audit MUST degrade to a filesystem walk when the kernel
  surface is unavailable.
- **`collections[]` discovery precedence** (a design-review upgrade): (1) **the module's
  own declared structure** — its seeded seam/config file when one exists (e.g.
  module-research seeds `.claude/research-canon.md` declaring its research root, taxonomy,
  and promotion target — read the seam FIRST); (2) the module's `rasa.json` seed/scaffold
  declarations; (3) inference from `seed/` layout + sample records (fallback). Record
  `fields` carry per-field **types** where inferable (`string`, `date`,
  `enum(a|b|c)` from observed values) — requirement #3 asked for structure AND types.
  Still advisory until modules publish `provides.collections[]` (OQ-3).
- **Staleness, defined.** BOOTSTRAP always re-audits. Any turn whose binding target fails
  to resolve re-audits before erroring. `_audited_at` is advisory: a publishing process
  MAY re-audit when the element roster looks newer than the index (e.g. a sibling
  `rasa.json` mtime exceeds `_audited_at`). Binding authors re-read sources before
  publishing regardless — the index plans, files decide.

---

## 4. The three binding modes

| Mode | What it is | Resolution |
|---|---|---|
| **bound** | UI ↔ existing module/tenant records, two-way | binds directly to a live collection |
| **derived** | UI synthesized from the *overall* context, not live-bound | reads `context.json` + sources, snapshots into the screen |
| **provision** | a new thing with no home → create records, then bind | provisions into a record-module, then becomes `bound` |

### The provision-then-bind trace (the goalkeeping case)

> *"Create a UI to plan goalkeeping sessions about positioning and distribution."*

1. Canvas reads `context.json` → no existing goalkeeping collection, but
   `rasa.module.research` (folder-per-topic) is mounted and can hold topic records.
2. **PROVISION** — creates `research/topics/goalkeeping/{positioning,distribution}.md`
   records (frontmatter-shaped) in module-research.
3. **BIND** — registers a `bound`, `read-write` binding for that new collection; sets
   `provisioned: true`.
4. Publishes the UI bound to the new records. An "add drill" button → EVENT → writes a new
   record file in the bound collection → republish. External edits to those files reflect
   live once the kernel bridge lands (§5 `reactive`).

There is **no `module-sessions` today** — `module-research` already is it. We reuse rather
than reinvent; `module.sessions` stays a deferred generalization (§6, OQ-2).

**RETIRE semantics (design-review addition):** records this app provisioned into a sibling
module are **tenant data owned by that module** — RETIRE leaves them intact, notes the
retirement (and the collection paths) in the app's CHANGELOG, and never bulk-deletes
another module's records. Cleanup is the tenant's call, through that module's own tooling.

---

## 5. `app.json#bindings[]` — the binding registry (requirement #2)

The declarative "knows how to bind properly" store. One row per bound region.

```json
"bindings": [
  { "id": "board",
    "region": "sessions",                      // region id on the screen this binding feeds
    "screen": "home",
    "source": { "module": "rasa.module.research", "collection": "topics/goalkeeping", "select": "*" },
    "shape": "folder-of-records",              // folder-of-records | record | file | table | derived
    "mode": "bound",                            // bound | derived | provision
    "direction": "read-write",                  // read | read-write
    "reactive": "on-event",                     // on-event (today) | live (needs KERNEL_ASKS #11)
    "provisioned": true }
]
```

`source` is one of: `{ module, collection, select? }` · `{ tenant: "<path>" }` ·
`{ context: "<query over context.json>" }` (for `derived`).

### Write-back — binding the events registry to the binding registry

Event rows gain an optional `writes[]` clause (array — one action often touches a module
record AND an app-local state file):

```json
"events": [
  { "action": "drill_status_changed", "emits": ["board"],
    "writes": [
      { "binding": "board", "op": "move-record", "field": "status" },
      { "state": "filters.json" }
    ],
    "handling": "move the record file between state subdirs of the bound collection, refresh filters, then republish" }
]
```

Entries are either `{ binding, op, field? }` (a bound-collection write) or
`{ state: "<file>" }` (app-local memory). `op` ∈
`create-record | update-record | move-record | delete-record`.

> **RESOLVED (OQ-4, 2026-07-09):** the executor follows a two-step resolution — (1) if the
> owning module DECLARES a write procedure for the operation (its skills/rules — the same
> seam-first philosophy as discovery), EVENT executes that procedure: the module's skill is
> its write API, invariants preserved, concurrency mediated by the owner; (2) otherwise
> EVENT performs a direct conventional write (matching the module's observed record
> conventions), allowed only on collections `context.json` marks writable. `op` names the
> intent either way — the registry shape is executor-agnostic. Direct writes are
> last-writer-wins; that risk is why module-declared procedures win when they exist.
> Kernel-side convergence per the kernel-heavy principle: ask #12's validated write path
> (and possibly canon SA-025 FileManager, triage) eventually mediates writes platform-side.

### The write-order law, extended

The sacred invariant gains the two new write classes, in this exact order:

1. **bound module-record writes** (via the module's declared procedure when one exists,
   else direct conventional write — resolved OQ-4)
2. **app-local `state/`** files
3. re-derive + write **`screens/<id>.json`**
4. **`app.json`** (+ `context.json` if re-audited, + `CHANGELOG.md`)
5. **`canvas_set`**

Never reversed, never partial. A publish that skipped a file write didn't happen.

### Binding rules

- `bindings[].id` values are **unique** (check-app enforces).
- Multiple bindings may share one `source` (one binding per region) — a KPI on `home` and
  a table on `orders` reading the same collection are two rows.
- `select` grammar is **TBD** — v1 supports only `"*"` (the whole collection).
- **`data_sources[]` fate (resolved):** it remains valid as read-only sugar — a
  `data_sources` row is equivalent to a binding `{ source: {tenant: <path>}, shape: "file",
  mode: "bound", direction: "read" }`. New authoring prefers `bindings[]`; check-app treats
  rows of either as one registry. Additive, no breaking change (§8 schema-evolution note).

### The `reactive` upgrade (why this shape is future-proof)

`reactive` is **advisory and upgrades for free**:

- **Today** every binding is honored by **re-derive-on-EVENT** — the fully-wired path:
  button → session turn → `canvas_set` → per-canvas SSE push → client (§A8). Real and live
  for user-driven change.
- **When KERNEL_ASKS #11 lands** (file-event → canvas bridge), bindings marked `live` are
  patched automatically on any external file change — **the same declarations, no
  re-authoring.**

### Doctrine change this forces

Current `APP_MODEL.md`: *"the EVENT process writes to `state/` and nowhere else"*; and
`data_sources[]` are read-only tenant paths (§A9). This design **extends** EVENT to write
**into bound module collections** (via a `writes` clause), and generalizes `data_sources[]`
into `bindings[]` (module-scoped, two-way). `state/` remains app-local memory; module
collections are the shared, bound data. Both are legal write targets, distinguished by the
binding.

---

## 6. The module question (requirement #1)

**Recommendation: domain.canvas is a binding brain over the *existing* record-modules and
owns no module of its own initially.**

- Canon fully sanctions a domain owning modules: author sibling `module-<name>` repos
  (`kind:"module"`, `requires.parent_kind:["domain"]`), copy the `module-tasks` anatomy,
  and optionally bind by name via the module's `requires.elements:{"rasa.domain.canvas": …}`
  (§A2, §A3). But `parent_kind` binds by **kind, not by name** — there is no way to pin a
  module to canvas specifically except a `requires.elements` dependency edge (§A2).
- The mount is **aspirational** — no parent mounts any module on disk yet; the full
  convergence was gated on the kernel dep-resolver (§A3, OQ-4). domain.canvas would be an
  early real consumer, which argues *against* leading with a module.
- Provision-then-bind's home is **`module-research`** (folder-per-topic) today; a thin
  `module.sessions` generalization is deferred until a concrete gap appears (OQ-2).

Revisit authoring `module-canvas-*` only when usage surfaces a canvas-specific record type
no existing module holds (e.g. a "layouts library" or "app catalog" the canvas itself
curates).

---

## 7. Stay generic (requirement #4)

The hard line: **nothing tenant-specific enters `content/`.** "A fresh session reads
`content/` and takes over any app cold" only holds if the doctrine is identical every
install.

| Stays in the element (species — versioned by element VERSION) | Discovered per-install (instance) |
|---|---|
| The doctrine (`BUILDER/APP_MODEL/PROCESSES/COMPONENTS/KERNEL_ASKS`) | `context.json` (the audit index) |
| The `bindings[]` **grammar** + the three modes | the specific `bindings[]` of an app |
| The `AUDIT` **procedure** | the app instances (`app.json`, `screens/`, `state/`) |
| Schema + `bin/check-*` enforcement | provisioned records in sibling modules |

The audit/binding machinery ships as **generic skills/processes**; the tenant knowledge it
discovers lives only in per-install data files.

---

## 8. Enforcement plan

- **`schemas/rasa.app.v1.schema.json`** gains `bindings[]` (optional array) and the
  `writes` clause on event rows. A companion `rasa.canvas.context.v1` schema for
  `context.json`.
- **`bin/check-app`** gains: `bindings[].id` unique; every `binding.source.module` resolves
  to a `context.json` module (warn if `context.json` absent — audit not yet run); every
  event `writes[].binding` names a real binding; `direction:"read-write"` bindings have at
  least one writing event; `provision`-mode bindings carry a provisioning note; region ids
  in bindings exist on their screen. (All additive; existing checks unchanged.)
- **Fixture design note (review #13):** the `binding-unknown-module` negative fixture MUST
  ship WITH a `context.json` — absent one, the module-resolution check only warns and the
  fixture would silently pass. The golden app likewise gains an example `context.json`
  (per-install data is legal inside `examples/`).
- **Schema evolution (review #16):** all additions are OPTIONAL fields — additive evolution
  within `rasa.app.v1`, no v2 bump. The published `$id` document changes shape in place;
  consumers pinning a snapshot should re-pull. (The `$id` repo path was corrected
  2026-07-09: `orchestrator-canvas` → `domain-canvas`.)
- **`bin/_contract.py`** unchanged unless new component kinds are needed (they are not —
  bindings are a manifest concern, not a component concern).
- **`examples/orders-desk`** gains one binding (bind the orders table to a module
  collection) so the golden app exercises the new contract; a new negative fixture
  (`binding-unknown-module` or `writes-unknown-binding`) must fail.

The `AUDIT` process (new, `PROCESSES.md`):

```
AUDIT — build/refresh the context index
Trigger: BOOTSTRAP, or an explicit "what can I bind to?" turn, or a stale context.json.
1. Determine _tenant_flavor (elements/ present → holding-folder; else co-located member).
2. Walk sibling domains + modules: read each rasa.json (name, version, kind, parent_kind).
3. For each module, infer collections[] from its seed/ layout + sample records.
4. Note tenant data files (csv/json/etc.) reachable from the tenant root.
5. Write context.json (write-order law still applies to any published screen).
```

---

## 9. Real-time posture (calibrated to the kernel — §A8)

- **Floor, buildable now:** button → file → republish → SSE push is fully real and live for
  user-driven change. The kernel's per-canvas SSE (`GET /v1/canvas/{id}/watch`) already
  pushes every `canvas_set` to the client with no polling.
- **File-watch exists but is unbridged:** the kernel runs an `fsnotify` watcher
  (`gateway/internal/filewatch.go`) that emits `events.files.*` — consumed only by the
  Console firehose. **Nothing routes a file change to a canvas.**
- **Two kernel asks close the gap** (both modest — the watcher, store, and push all exist):
  - **KERNEL_ASKS #11 — file-event → canvas bridge:** a core subscriber on
    `events.files.*` that looks up bindings for the changed path, patches the bound region,
    bumps version, publishes on `canvas.<tenant>.<id>`. Turns `reactive:"live"` on.
  - **KERNEL_ASKS #12 — direct edit → file write:** `POST /v1/canvas/{id}/edit` (or a
    `field.commit` event) that writes the bound file **without a full LLM turn**, for
    instant field commits; emits both `file.*` and `ui` events.
- **Honest caveat to document:** inotify over the macOS Docker **bind-mount is best-effort**
  — host-side edits often don't propagate; the deterministic path is `PUT /v1/fs`. The
  kernel already defers "real-time collaboration" to v2+.
- **Two more caveats (design review):** (i) kernel tenancy is hardcoded `tenant:"dev"`
  (TASK-074 pending) — every per-tenant claim here runs ahead of kernel tenancy; (ii) ask
  #11 has an open **mechanism decision** — the kernel doesn't parse `app.json`, so it can't
  "look up bindings" without one of: parsing our app model (rejected — coupling),
  register-bindings-at-publish (fast, trivial projections only), or **nudge-the-session**
  (recommended v1: works for every binding shape, one-turn latency). Options + analysis in
  `docs/handoff/KERNEL_GAPS.md`; "upgrades for free" holds under all three, but the latency
  profile differs.

---

## 10. Build order

Superseded (design review #24): the merged, dependency-ordered plan across BOTH design
docs now lives at **`docs/design/BUILD_ORDER.md`**.

---

## 11. Open questions for red-lining

- **OQ-1 — The "own place". ✅ RESOLVED (user, 2026-07-09):** the extended app store; zero
  canvas-owned modules. And a **standing principle** was set: *"the kernel should hold all
  core dependencies that it can so the domain is as light as it can be"* — kernel-heavy,
  domain-light. Where a mechanism can be platform-generic (binding index, validation, file
  mediation, reactivity), prefer the kernel ask over element-side machinery; element-side
  implementations are explicit stopgaps that migrate down.
- **OQ-2 — Provision home.** Reuse `module-research` (recommended) vs author a thin
  `module.sessions`. **Recommend: reuse; defer module.sessions.**
- **OQ-3 — Collection shape discovery.** Three options (review #10 upgraded this): (a)
  **read the module's own seam/config file first** — module-research seeds
  `.claude/research-canon.md` declaring its root/taxonomy/promotion; the module declares
  its own structure (STRONGEST, exists today); (b) a `provides.collections[]` convention in
  module `rasa.json` (cross-module contract; a canon task); (c) inference from `seed/` +
  samples (fallback). **Recommend: seam-first with inference fallback now; propose (b)
  upstream later.**
- **OQ-4 — Write-into-a-sibling-module. ✅ RESOLVED (2026-07-09, delegated to us):**
  **module-mediated first, direct as fallback** — if the module declares a write procedure
  (skills/rules), EVENT executes it (the skill is the write API); else direct conventional
  writes on `writable` collections only. Executor rule encoded at §5; registry shape
  unchanged. Kernel-side mediation (ask #12 / SA-025) is the convergence target.
- **OQ-5 — `contract_version`.** Bump to `1.4.0` (SA-023 propagated; the schema already
  dropped `orchestrator`) vs hold at `1.3.0`. **Recommend: bump, but coordinate with the
  workspace sweep** (review #22) — all 37 registered Elements declare 1.3.0; going first is
  schema-legal but REGISTRY/conformance tooling should expect the outlier.
- **OQ-6 — `reactive` default.** Should new bindings default to `on-event` (safe, works
  today) or `live` (aspirational, needs #11)? **Recommend: default `on-event`.**
- **OQ-7 — The #11 bridge mechanism. ✅ RESOLVED (user → recommendation, 2026-07-09):**
  **(c) nudge-the-session ships v1** (works for every binding shape, zero coupling);
  **(b) register-bindings-at-publish is the COMMITTED target state** — per the kernel-heavy
  principle the kernel eventually owns the live binding index and fast-path patches simple
  projections; complex derivations keep routing via (c). Encoded in
  `docs/handoff/KERNEL_GAPS.md` K2.

---

## A. Evidence appendix (grounded facts + citations)

Every load-bearing claim above, with its source. LOCKED = canon-sealed (v1.3.0);
WORKING = authored into v1.4.0 (IN PROGRESS); IMPLEMENTED = verified on disk/in code.

- **A1 — The fold.** SA-023 removes the `orchestrator` kind (8→7); the tenant is the
  orchestrator; its brain is `rasa.tenant.core`. *Spec §55 SA-023 / FD-001, FD-003;
  `canon/tasks/done/SA-023-orchestrator-folded-into-tenant.md`.* **WORKING.**
- **A2 — Domain↔module mount.** `requires.parent_kind` is module-only; a non-empty subset
  of `["domain","tenant"]` (was `["domain","orchestrator"]` pre-v1.4). Binds by KIND;
  name-level binding only via a `requires.elements` edge. *Spec §9.3 (line 787), §8 (line
  720), conformance check #15.* **WORKING** (topology **LOCKED** in §8).
- **A3 — A domain can own modules.** Sibling `module-<name>` repos, `parent_kind:["domain"]`;
  precedent `domain-code v0.43.0` listed 5 modules in `requires.elements[]` "as standards"
  (unverified on disk — was staged-uncommitted). Composition is resolved by the
  Recipe/Tenant + Gateway, not by the domain enumerating modules. `domain-core` and
  `domain-canvas` both ship `requires:{}`. *Spec §7/§8; `elements/domain-core/rasa.json`;
  this repo's `rasa.json`.* **WORKING / IMPLEMENTED.**
- **A4 — Install mechanic.** `bin/init` is declarative: applies `element.files[]` (→ consumer
  `.claude/`) + `seed.files[]` (one-time), stamps a lockfile; no hardcoded logic. domain.canvas
  currently ships no `bin/init` and installs nothing (`scaffold: "operates in-session"`).
  *`elements/module-tasks/bin/init`, `elements/domain-core/bin/init`; this repo's `rasa.json`.*
  **IMPLEMENTED.**
- **A5 — Two tenant flavors.** Holding-folder (SA-019, LOCKED): siblings at
  `<tenant-root>/elements/<name>/` + hidden `.rasa/holding/<name>/`. Co-located (SA-022/023,
  WORKING): member repos `<ns>-<name>/`, no `elements/` folder. *Spec §53/§54;
  ELEMENT_CONTRACT §8b.*
- **A6 — Record-modules are UI-ready.** `module-tasks` owns `tasks/` — one frontmatter file
  per record (`id`/`category`/`status`), organized into state subdirs
  (triage→backlog→active→completed). `module-research` = folder-per-topic (5-file topic
  template) + a seeded **adapter seam** (`.claude/research-canon.md` declaring root/
  taxonomy/promotion) — the closest thing to a module-declared data schema, and §3's
  discovery hook; `module-notes`, `module-field-log`, `module-schedule`, `module-ingest`
  are record-store shaped. No module publishes a *formal* schema (OQ-3).
  *`elements/module-*` on disk; corrected per design review #10.* **IMPLEMENTED.**
- **A7 — No existing audit/context concept in canon.** Install machinery only copies declared
  files. Platform-level discovery exists: kernel registers each `<mount>/<name>/rasa.json`;
  `GET /v1/elements` returns the registry. *ELEMENT_CONTRACT (grep: sibling/discover/scan);
  kernel routes.* An install-time context index is net-new.
- **A8 — Kernel real-time reality (read from kernel v0.27.0 code; re-confirmed @ v0.32.0).**
  - File-watch **IMPLEMENTED but unbridged**: `gateway/internal/filewatch.go` (fsnotify at
    boot) → `events.files.*` → SSE firehose only; no file→canvas bridge (searched
    `file.(created|modified|removed|saved)`, `canvas.*file` — none).
  - Per-canvas push **IMPLEMENTED**: `GET /v1/canvas/{id}/watch` streams `ui` events from
    `canvas.<tenant>.<id>` the instant `canvas_set` fires (SSE; no WebSocket).
  - ui_event round-trip **IMPLEMENTED end-to-end** but always through a full LLM turn
    (`commands.go:312`, `dispatcher.ts:214/459`, `ui-event-context.ts`, `mcp-server.ts`,
    `mcp-main.ts:56`).
  - Canvas store **IMPLEMENTED** (Redis `rasa:canvas:{tenant}:{id}`, versioned, one-step
    `lkg`/revert, no multi-history; `store.ts`).
  - Session = `(element, cwd, selector)`-keyed; **canvas id = session id**; `/v1/sessions`
    is the record surface; no kernel "app-id" concept — just a cwd path.
  - Direct client→file write already exists: `PUT /v1/fs/{path}` (emits `file.*`). Tenancy
    hardcoded `"dev"` pending JWT (TASK-074).
- **A9 — Current binding doctrine.** `data_sources[]` are read-only tenant-relative paths;
  EVENT re-reads source, re-bakes into the active screen, republishes; *"the EVENT process
  writes to `state/` and nowhere else."* *`content/APP_MODEL.md`, `content/PROCESSES.md`.*
  **IMPLEMENTED.**

*Note on provenance: the canon reads were done by a fan-out grounding sweep; two of six
readers (install-audit, binding-runtime) flaked and returned stubs — those slices were
re-grounded directly (A4, A5, A7) and by the kernel-code investigation (A8), which is more
authoritative than the canon-doc reader would have been.*
