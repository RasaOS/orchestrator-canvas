# Design — the UI engine, design system & architecture

**Status:** DRAFT / reviewable spec. Not yet ratified doctrine.
**Author pass:** 2026-07-09 (core-internal-structure session).
**Companion to:** `docs/design/binding-model.md` (data binding). This doc covers the
*render/UI* layer, the design system, the engine choices per layer, and code organization.
**Fold targets once ratified:** `content/COMPONENTS.md` (component contract correction +
design tokens), `content/BUILDER.md` + `content/APP_MODEL.md` (the website/layout model),
`content/KERNEL_ASKS.md` (artifact + binding asks), `bin/check-app` + `bin/check-doctrine`
(validator evolution + shell-lockstep check), `rasa.json` (identity).
**Build order:** the merged plan across both design docs is `docs/design/BUILD_ORDER.md`.
**Truth-pass status 2026-07-09:** the correctness slice is already folded — COMPONENTS.md
(real shapes + emission grammar + §custom-visuals), BUILDER/APP_MODEL/CLAUDE artifact +
nav-intent corrections, KERNEL_ASKS #3 rewrite + #11/#12 filed, check-app grammar fix,
golden/fixture/schema-$id fixes.

This document is written to be **red-lined before any code is written.**

---

## 0. Product framing — what we are building

**domain.canvas authors "an internal website for the tenant, built live by the user from
their contextual needs."** Concretely, per grounded canon (§B):

- We are the **`conversational-canvas` profile** (doc-10 frontend-profiles triage): *the AI
  authors the UI, live, validated by the kernel.*
- **We author layout definitions; a canvas-profile *frontend* Element renders them.** We are
  a `domain`, **not** a `frontend` (frontend-rasaos / frontend-canvasos are the renderers).
  Our product is the **authoring doctrine + the app/binding model**, not a Docker image.
- An "internal website" is, in canon's own locked vocabulary, a **vertical workspace**:
  file-per-screen + a `nav` shell + an `ai-rail` conversation surface, rendering the
  tenant's own data. This is **canon-LOCKED (doc 10 v1.0.0)** — the website structure the
  user wants is not our invention; it is the ratified frontend model. What is *not* yet
  ratified is the live-authored "canvas" mechanism we run on (§B4).

---

## 1. The two-layer reality (the reconciliation principle)

There are **two different "frontends"**, and every engine decision below turns on keeping
them straight:

| | Canon doc-10 (LOCKED, "Authoritative" v1.0.0) | frontend-rasaos (as-built, verified) |
|---|---|---|
| Components | **18 frozen** (+3 approved-pending = 21) | **11 implemented**, off-list → amber error tile |
| Layout | 6 named grids (`full`, `sidebar-main`, `sidebar-main-rail`, `two-col`, `three-col`, `dashboard`) + named slots (`sidebar/main-top/main-body/main-bottom/rail`) | one **flat** region list + optional absolute `frame{x,y,w,h}` |
| Navigation | `nav` component (data-driven, active-from-screen) | `button-row` only; nav is an *authoring convention* faked per-turn |
| Conversation | **`ai-rail` mandatory** on primary screens (FE-005) | chat lives in the shell split, no `ai-rail` component |
| Theming | **CSS variables** from theme JSON (`--color-substrate/essence/accent-*`, `--font-*`, `--spacing-unit`) | Tailwind-**baked** classes; no inheritable `--rasa-*` vars |
| Artifacts / HTML | **none** — bounded set is the law | **none** — no iframe/sandbox/bridge |
| Validation | **11-step validator** before publish (FE-020) | client-side defensive readers + error tiles |
| Real-time | (unspecified in doc 10) | **SSE both ways, robust** (`/v1/canvas/{id}/watch` + command stream, version-dedup, gap-recovery) |

**The principle:** *author to what the shell renders **today**, steer the contract toward
what canon **locks**, and track the gap explicitly.* The shell is an early subset of the
canon model plus the (triage) canvas mechanism. We must not author against capabilities
neither has (artifacts), and we should shape our contract so that as the shell grows into
the canon model (grids, `nav`, `ai-rail`, CSS-var theming), our layouts already fit.

---

## 2. Engines & architecture — the decisions

Two governing principles (professional-engineering directives):

1. **Compose the substrate's real engines; do not reinvent them.**
2. **Kernel-heavy, domain-light** (user, 2026-07-09): *"the kernel should hold all core
   dependencies that it can so the domain is as light as it can be."* Where a mechanism can
   be platform-generic — binding index, validation, file mediation, reactivity — prefer
   filing the kernel ask over building element-side machinery. Element-side implementations
   are explicit stopgaps that migrate down into the kernel as the asks land.

| Layer | Engine we use | Rejected alternative | Status |
|---|---|---|---|
| **UI / render** | the **frozen declarative component set** (11 today → 18–21 canon), styled by Brand-Kit tokens; absolute `frame` for dashboards | hand-rolled HTML / sandboxed artifacts (absent in shell **and** anti-canon §2.1) | 11 buildable now |
| **Custom visuals / 3D & animation** | the **sandboxed artifact lane** — `HtmlEmbed` via the `code-block{render:true}` carriage (three.js/WebGL/CSS-anim, `window.rasa.emit` bridge) — **LIVE in the shell** (frontend-rasaos @ `a5f6ff1`; HOTFIX-001 restored the doctrine) | hand-rolled DOM; waiting for "someday" | **available today**; direct `html-embed` name pends kernel enum (K1) |
| **Data / storage** | the **record-modules** (`module-research/tasks/notes/…`) + kernel `PUT /v1/fs` | a canvas-owned datastore / Redis-as-truth | buildable now |
| **Data binding** | the **binding registry** (`app.json#bindings[]`) + `context.json` audit — see `binding-model.md` | ad-hoc per-screen `data_sources` | design-stage |
| **Reactivity** | kernel **SSE** `/v1/canvas/{id}/watch` (client already robust); file-event→canvas bridge for external change | client polling / websockets (shell has neither; SSE only) | push done; bridge = ask #11 |
| **Persistence** | **files-are-truth + Redis projection** (kernel canvas store: versioned, `lkg`/revert) | canvas-only state | in place |
| **Theming** | **Brand-Kit tokens** referenced by canon CSS-var names; teal+bone invariant, one accent/vertical | inventing colors; hardcoding coral everywhere | tokens locked; var-layer = shell gap |
| **Enforcement / tooling** | **Python** `bin/check-app` evolving toward canon's 11-step validator; `check-doctrine` + a new shell-lockstep check | JS/Go rewrite; trusting internal-only lockstep | Python fine (§6) |
| **Identity / positioning** | `domain` kind, `conversational-canvas` profile, authors layouts a frontend renders | acting as a `frontend` image | re-role pending |

### 2.1 3D / animation / custom visuals — a priority capability on a real path

> **⚡ SUPERSEDED IN THE HAPPIEST DIRECTION (2026-07-09, HOTFIX-001):** the
> capability turned out to be **already built** — frontend-rasaos `main` @
> `a5f6ff1` (authored 2026-07-07, in parallel) ships the artifact lane
> exactly as §2.1a specs it, served via the `code-block{render:true}`
> carriage today. The render investigation that found it "absent" had read a
> checkout without that commit (hence the SHA-pinning rule now in the
> done-gate). Point (i)'s doctrine correction was re-reversed by HOTFIX-001:
> COMPONENTS.md §artifact now documents the live, verified contract. Point
> (ii)'s remaining work is **kernel-side only** (K1: allowlist + schema enum)
> plus the canon admission (FE-022). The text below is kept for the record.

**3D and animation in a page are a core product requirement (user, 2026-07-09).** They are
delivered by a **sandboxed `html-embed` region**: one component that renders a
self-contained HTML document in a sandboxed iframe (three.js / WebGL / `<canvas>` / CSS
animation inside), with a `postMessage` → `window.rasa.emit` bridge back to the session.
This is the escape hatch the current doctrine *assumed already existed* — it does not yet,
but the path to ship it is short. Two things must not be conflated:

**(i) The correctness fix (now).** `content/COMPONENTS.md` §artifact + the two "starter kits"
tell sessions to emit sandboxed-HTML artifacts *as if the shell renders them today* — it
does not. The shell has **no** iframe/srcdoc/bridge path; `code-block{render:true}` renders
as `<pre>` **text**; `media-viewer` is link-only; `markdown-block` is HTML-escaped (§A5). So
operating doctrine must **stop instructing sessions to emit non-rendering artifacts today**
— relabel §artifact from "here's how to do it now" to "target capability + status + real
path," and until the component ships, sessions build from the frozen set. This is a **live
correctness bug** — sessions currently author things that error-tile.

**(ii) The capability commitment (priority).** 3D/animation is NOT dropped — it is elevated
to a **prioritized kernel + shell + canon capability** with a concrete component spec
(§2.1a). Framing against doc-10's bounded discipline (FE-002):
`html-embed` is admitted as **the single sandboxed *escape region*** — not a "19th business
component" but an explicit boundary (like an `<iframe>` is a boundary, not a widget) — so it
coexists with "build only from the frozen set." Canon hook already exists: KERNEL_ASKS #3 +
the SA-027 canvas triage gesture at exactly this. Change-set is small per layer (shell
component + CSP; one-line kernel enum add; a small canon SA).

**Layering recommendation:** lead with the general `html-embed` escape hatch (covers *any*
3D/animation/custom visual, one component forever); later promote recurring patterns (an
animated chart, a simple 3D viewer) into purpose-built declarative components for
consistency + theming.

### 2.1a The `html-embed` component — grounded spec capsule

Full implementable spec: **`docs/design/html-embed-spec.md`** (grounded 2026-07-09 against
shell source + canon triage + the published layout schema). Verdict: **genuinely
achievable, small change-set** — a `case 'html-embed'` arm in the shell (~70–110 lines:
srcdoc wrapper + `sandbox="allow-scripts"` iframe + postMessage→`interact` listener), a
one-line kernel allowlist add, a schema-enum add with `html maxLength`, and one canon task
(`DOC-10-edit-html-embed-escape-region`, proposed lock **FE-022**: "exactly one unbounded
component, sandboxed + CSP-fenced + size-capped").

Security design in one line: opaque origin (`allow-scripts`, never `allow-same-origin`) +
a shell-injected per-document CSP whose thesis is **`connect-src 'none'`** (scripts run;
nothing phones home) + a `postMessage` bridge validated by `e.source === contentWindow`.

**Honest edges:** CDN three.js/WebGL/D3 **work** for self-contained procedural scenes
(script-src whitelists the four CDNs; WebGL needs no network) — but `connect-src 'none'`
blocks runtime *asset* fetches (remote textures/GLTF/wasm fail; `data:`/`blob:` survive),
offline tenants need self-hosting (a later `connect-src 'self'` decision), the artifact
re-mounts on every canvas version (reload flash), and the fence ("one artifact region per
screen; only when the declarative set can't express it") must be validator-encoded or
FE-002's discipline erodes.

Two reality corrections this grounding forced (tracked in the design review): the shell has
**no CSP at all** (COMPONENTS.md's "the shell injects a CSP" is unimplemented), and
KERNEL_ASKS #3's clause *"the shell already renders it sandboxed"* is **false** — its only
iframe is a deliberately same-origin, unsandboxed proxy. Ask #3 must be rewritten to point
at this spec.

### 2.2 The component contract must be reconciled three ways

`COMPONENTS.md` currently drifts from **both** the shell **and** canon. The real shell prop
shapes (verified, §A2) differ from our doctrine in several places:

| component | doctrine says | shell actually consumes |
|---|---|---|
| `markdown-block` | `{markdown}` | **`{content}`** |
| `media-viewer` | `{src}` data-URI **embed** | `{src}` **link-only**, never embeds |
| `code-block` | `{language, code}` + render carriage | **`{code}`** text only |
| `card-strip`/`card-list` | `{title, body?/description?, on_click?}` | `{title, subtitle?}`; list uses `on_card_click` → `{card_index,title}` |
| `form` | `{fields:[{name,label,type}]}` → `submit` | `{fields:[{id,label?,type?,placeholder?}]}` → `on_submit{<id>:value}` |
| `chart` | `{type:'bar'\|'line', series/points, labels}` | **`{data:[{label,value}]}`, horizontal bars only** |
| `timeline` | `{items:[{label,detail?,at?}]}` | **`{events:[{at,label}]}`** |
| `button-row` | `{buttons:[{id,label}]}` | `{buttons:[{id,label?,intent?,style?}]}` → emits `intent\|\|'on_click'` `{button_id}` |

**Recommendation:** `COMPONENTS.md` becomes the reconciled single source of truth —
**document the real shell shapes** (the floor sessions author against), tag each component
with its **canon doc-10 alignment** (name/prop deltas to the locked 18–21), and note the
action-emission grammar the shell actually uses. Then close the enforcement gap (§6).

> **Status 2026-07-09: DONE (first pass).** COMPONENTS.md rewritten to the verified shapes
> + emission grammar; `check-app`'s action derivation corrected (`intent || 'on_click'`,
> `on_submit`, `on_card_click`, region-level `on_click`); the nav contract now requires
> `intent` (APP_MODEL.md); golden app + fixtures updated (`markdown`→`content`, intents
> added). Residual: the frontend team should confirm two uncertain emissions (card-list's
> literal action name; `props.on_click` flag semantics) — filed in
> `docs/handoff/FRONTEND_RASAOS_GAPS.md`.

---

## 3. The design-system engine (Brand Kit is authoritative)

Adopt the **Brand Kit** (doc 02) as the token authority — doc 10 itself defers to it, and it
is LOCKED (§B2). Our current doctrine's "deep teal/green + coral + bone" is *correct but
under-specified*. Full adoption:

- **Palette (11 tokens):** substrate `teal-deep #082a23` / `teal #0e3d33` / `teal-soft
  #1e4a3f`; essence `bone-soft #faf3e4` / `bone #f4ead6` / `bone-deep #ede0c4`; spark `coral
  #d96b3a` / `coral-soft #e8865a`; ink `#1a1a1a`/`#4a4a4a`; rule `#d8c9a8`; status `lock
  #6b9b3a` / `warn #c97a3a`.
- **Invariants:** **substrate teal + essence bone are RasaOS-wide; the accent varies per
  vertical** (LegalOS `#6ba88a`, HealthOS `#e89c4f`, DevelopOS `#7aa8c4`, …). Coral is the
  *master default*, not a fixed choice — authored sites pick **one** accent and use it as *a
  verb, not decoration* ("if everything is coral, nothing is").
- **Typography (3 faces, never a fourth):** **Fraunces** display, **Inter** body/UI,
  **JetBrains Mono** code/labels/meta. Locked scale (body 16/26, h2 Fraunces 34/39, table
  head JetBrains Mono 11 caps, …).
- **Spacing/grid:** 4-pt scale; 12-col / 1140px-max / 24px gutter; card breakpoints 768/480.
- **Accessibility (hard rule):** WCAG **AA** — 4.5:1 body, 3:1 large. **coral-on-bone is
  3.4:1 → large-text/actionable only, never body copy.** Honor `prefers-reduced-motion`.
- **Reference by canon var names** (`--color-substrate-*`, `--color-essence-*`,
  `--color-accent-*`, `--font-display/body/mono`, `--spacing-unit`) even though the shell
  bakes them today — so when the shell adopts doc-10 §18's CSS-variable layer, our authored
  styles are already aligned. (This also removes the temptation to hardcode `#d96b3a`.)

Design assets exist as reference: **`RasaOS - UI Kit.mhtml`** (full branding/design-system
page — tokens, inputs, progress, specialized cards, layout patterns, component→Swift) and
**`RasaOS - UI MockUps.mhtml`** (RasaConsole concept screens; mantra *"Teal is AI. Coral is
you. Bone is your canvas."*). Both are **Console (Tier-0 Swift)**-oriented — treat as shared
design language + reference IA, not our spec.

---

## 4. The layout / website engine

The "internal website" is canon's **file-per-screen + layout grid + nav + ai-rail** model
(LOCKED, §B3) — which maps almost 1:1 onto our existing app model:

| our model (invented) | canon locked equivalent |
|---|---|
| `screens/<id>.json`, one per screen | `layouts/<name>.json`, one per screen (`screen.name/title/layout_grid`) |
| `active_screen` projection | file-per-screen; `screen.title` used in nav + browser tab |
| `nav:<screen-id>` button-row contract | the `nav` component (data-driven, active-from-screen) |
| (none — the shell's chat pane IS the conversation surface) | `ai-rail` (FE-005) — the profiles edit scopes it to full-workspace only; **N/A to conversational-canvas** |
| (none) | 6 named `layout_grid`s + slots (`sidebar/main-top/main-body/main-bottom/rail`) |

**Recommendation:** evolve `APP_MODEL.md`'s screen model to carry `screen.layout_grid` +
named slots (author toward canon's grids), keep `active_screen`/`nav:<id>` as the **today**
mechanism (the shell renders one flat layout per nav turn). **Do NOT author `ai-rail`
regions** (design-review correction #4): the shell error-tiles them, and the profiles edit
scopes FE-005 to full-workspace only — in our conversational-canvas profile the shell's
chat pane IS the conversation surface. Revisit only if we ever target the full-workspace
profile. Real simultaneous pages (a true multi-tab site) remain the `args.canvas_id`
kernel ask (KERNEL_ASKS #1). Until the shell implements grids, degrade a `layout_grid` to
the flat region list + `frame` placement — the *authored intent* is preserved and upgrades
when the shell catches up.

---

## 5. Real-time engine (settled)

Confirmed from **both** kernel code and shell code (§A6, and `binding-model.md` §A8):

- **Client real-time is genuine and robust** — SSE both directions, monotonic-version dedup
  across the command + watch streams, gap-recovery via re-snapshot, `PUT
  /v1/canvas/{id}/view` geometry feedback. Nothing to build here; use it.
- **Button → turn → `canvas_set` → SSE push** is the live path today. Re-derive-on-EVENT is
  real, not a placeholder.
- **External-file-change → UI** needs the **file-event→canvas bridge** (KERNEL_ASKS #11) and
  optionally the **direct edit→file** path (KERNEL_ASKS #12) — see `binding-model.md` §9.
  Performance budget to honor (canon FE-016): **AI-edit round-trip ≤ 1.0s p95.**

---

## 6. Enforcement engine + code organization (professional structure)

### The enforcement gap (a real false-confidence bug)

`check-doctrine` verifies `COMPONENTS.md ↔ bin/_contract.py` **internally** — but nothing
checks either against the **actual shell renderer** (a separate repo). That is exactly how
the artifact fiction + prop drift sailed through the gate meant to prevent it. Canon's own
analog is doc-10's **11-step validator** (FE-020): JSON → schema → component-exists →
prop-schema → source-URI grammar → slot-exists → unique-ids → ai-rail-reachable →
theme-exists → smoke-render.

**Recommendation:**
1. Evolve `bin/check-app` from app-shape well-formedness toward the **11-step validator**:
   add component-exists (against the real shell set), prop-schema (per §2.2 shapes),
   slot-exists (when grids land), unique region ids, ai-rail-reachable, theme-token fidelity.
2. Add a **shell-lockstep check** to `check-doctrine`: pin the shell repo commit/version and
   diff our component contract against a generated manifest of the shell's real `switch`
   arms + prop readers. Drift fails the gate. (If cross-repo access is unavailable at check
   time, pin a checked-in snapshot of the shell's component manifest and diff against that.)
   *Proof it's needed (review #8): the golden app itself shipped `markdown-block{markdown}`
   — renders EMPTY in the real shell — and the gate passed it GREEN. Fixed 2026-07-09; the
   manifest request is filed in the frontend handoff (F3).*
3. Keep enforcement in **Python** — justified: it is authoring-time tooling, not a runtime
   hot path; it already exists and is clean; a rewrite buys nothing. As the contract grows,
   factor `_contract.py` into focused modules (`_components.py`, `_layout.py`, `_binding.py`)
   so each check script stays single-purpose.

### Code organization (clean boundaries)

| Layer | Home | Rule |
|---|---|---|
| Operating doctrine (LLM-read every turn) | `content/` | terse, imperative, **truthful to the render engine**; nothing tenant-specific |
| Published contracts | `schemas/` | the app manifest + (new) context + binding + layout schemas |
| Enforcement tooling | `bin/` | single-purpose scripts over a shared contract module |
| Design specs (red-line, then fold) | `docs/design/` | this doc + `binding-model.md`; ratified pieces migrate into `content/` |
| Golden + negatives | `examples/` | the reference app passes; fixtures fail |
| Per-install app data | *(never in the element)* | `context.json`, `app.json`, `screens/`, `state/` live in the tenant tree |

The stay-generic line holds: **the render/design/binding *contracts* ship in the element
(species); the tenant's actual site + data are per-install (instance).**

---

## 7. Canon alignment & tracking (be honest about what's ratified)

We are **inventing ahead of canon on the canvas mechanism.** Track these as our anchors and
do not cite the canvas model as locked:

- **SA-026** (ui-event type), **SA-027** (canvas API surface), **SA-028** (canvas spatial
  model) — TRIAGE, proposed 1.4.0 (may slip to 1.5.0).
- **DOC-10-edit-canvas-components** — adds `markdown-block`/`button-row`/`card-list` (18→21);
  **review-approved, kernel-implemented ahead**, doc authoring pending.
- **DOC-10-edit-frontend-profiles** — defines chat-only / **conversational-canvas** / full
  workspace; we are conversational-canvas; scopes `ai-rail` (FE-005) per profile.
- **LOCKED and binding on us regardless:** Brand Kit tokens (doc 02), doc-10 bounded-set
  discipline (FE-002), WCAG AA, the validator concept (FE-020), performance budgets.

A future housekeeping item: consider whether domain.canvas should **push its proven canvas
model back into canon** via those triage IDs (we are the reference consumer) — but that is a
canon-workspace task, not element code.

---

## 8. Decisions for red-lining

- **OQ-A — 3D/animation.** Two moves (§2.1): (i) correct the doctrine so it stops instructing
  sessions to emit artifacts that don't render today (live bug); (ii) **elevate 3D/animation
  to a priority capability** — build the sandboxed `html-embed` escape region (shell + kernel
  enum + canon SA). **Recommend: both; ship the `html-embed` component as a priority ask, not
  a someday.** *(3D/animation is a hard product requirement — the doctrine keeps it central,
  it just moves from "pretend it works" to "real component with a concrete spec.")*
- **OQ-B — Component contract.** Rewrite `COMPONENTS.md` to the **real shell prop shapes** +
  canon-alignment tags, and add the shell-lockstep check? **Recommend: yes.**
- **OQ-C — Design tokens.** Adopt the full Brand-Kit palette/type/spacing via canon CSS-var
  names, with **one-accent-per-vertical** (not hardcoded coral)? **Recommend: yes.**
- **OQ-D — Layout model.** Evolve the screen model toward canon `layout_grid` + slots +
  `ai-rail`, degrading to flat+`frame` on today's shell? **Recommend: yes, incremental.**
- **OQ-E — Validator.** Grow `check-app` toward doc-10's 11-step validator? **Recommend: yes,
  incrementally (component-exists + prop-schema first).**
- **OQ-F — Frontend gaps.** RESOLVED 2026-07-09 (review #5 caught the duplication):
  KERNEL_ASKS #3 was **rewritten in place** (its false "already renders sandboxed" claim
  corrected; kernel half = allowlist + schema enum + caps) — no duplicate ask filed. The
  shell-side work (html-embed component, emission-grammar confirmation, CSS-var tokens,
  grids/`nav`) is filed as a handoff: `docs/handoff/FRONTEND_RASAOS_GAPS.md`. `ai-rail` is
  NOT requested (per-profile scoping — §4).

---

## A. Evidence appendix — render engine (frontend-rasaos, verified from source)

- **A1 — Stack.** Vite 5 + React 18 + TypeScript(strict) + Tailwind 3, ESM, no router; nginx
  same-origin proxy `/v1`→kernel. Client-side SPA; a canvas is runtime JSON rendered by
  React. *`app/package.json`, `tailwind.config.ts`, `nginx.conf`.* IMPLEMENTED.
- **A2 — Renderer.** `app/src/canvas/components.tsx` — one `switch` in `RegionBody`
  (`:37-69`); off-list → amber error tile (`:62-67`). Exactly 11 components; real prop shapes
  per §2.2 table (`:78-351`). Region-level `on_click` → `on_click{region_id}`
  (`CanvasPane.tsx:163-167`). IMPLEMENTED.
- **A3 — Layout.** One canvas at a time (`CanvasProvider.tsx:28-39`); flat region list in a
  flex column (`CanvasPane.tsx:152-154`); absolute `frame{x,y,w,h}` supported, overlap legal,
  z = document order (`:161-183`); `layout_grid` parsed but **never read**. No routing/tabs/
  chrome for canvas content. PARTIAL.
- **A4 — Theming.** `src/theme/theme.json` → `tailwind.config.ts` → Tailwind classes. Palette
  confirmed (`bg #082a23`, `accent #d96b3a`, `text #f4ead6`); fonts Fraunces/Inter/JetBrains
  Mono via Google Fonts CDN (`index.html:8-11`). **No `:root` CSS variables** — tokens not
  inheritable by any embedded HTML. IMPLEMENTED (shell) / ABSENT (inheritable layer).
- **A5 — Artifacts.** ⚠ SUPERSEDED (read from a checkout WITHOUT `a5f6ff1` — the
  unpinned-SHA lesson): current frontend-rasaos `main` ships the full artifact lane
  (`HtmlEmbed`, carriage + direct arm, sandbox + CSP + bridge — see html-embed-spec.md
  status header). `media-viewer` link-only and `markdown-block` escaping remain accurate.
  Was: ABSENT → **IS: IMPLEMENTED** (kernel enum pending).
- **A6 — Real-time.** Command stream (`ConversationProvider.tsx:314-318`) + watch stream
  `GET /v1/canvas/{id}/watch` via `EventSource` (`CanvasProvider.tsx:132-136`); version dedup
  + gap re-snapshot (`:102-124`, `CanvasClient.ts:37-48`); out via `POST /v1/commands`
  `ui_event{…}` (`CommandClient.ts:73-82`); geometry via `PUT /v1/canvas/{id}/view`
  (`CanvasPane.tsx:54-98`). IMPLEMENTED, robust.
- **A7 — Code org.** `src/canvas/` = 4 clean files (provider / pane / components / markdown);
  allowlist-switch + error-tile drift alarm; defensive untyped-JSON readers; security-by-
  construction on every string surface. Exemplary; mirror the discipline.

## B. Evidence appendix — canon frontend + design system

- **B1 — Frontend model (LOCKED, doc 10 v1.0.0 "Authoritative").** Frontend = L4 Element, one
  Docker image per vertical, thin client, zero business logic (FE-001); renders a *vertical
  workspace* + conversation; per-vertical only theme/layouts/nav/brand change (FE-007).
- **B2 — Design system (LOCKED, Brand Kit doc 02; doc 10 defers to it on tokens).** 11 color
  tokens; 3 fonts (no fourth); 4-pt spacing; 12-col/1140 grid; WCAG AA (coral-on-bone AA
  large-only); one accent per vertical (FE-012); bounded component discipline (FE-002).
- **B3 — Navigation/layout (LOCKED, doc 10 §8-9).** file-per-screen; 6 layout grids; named
  slots (`sidebar/main-top/main-body/main-bottom/rail`); `nav` component; `ai-rail` mandatory
  (FE-005); routing mechanics left open.
- **B4 — Canvas is PRE-CANON (TRIAGE).** "canvas" absent from locked doc 10; the model lives
  in SA-026/027/028 + DOC-10-edit-canvas-components (review-approved, kernel-ahead) +
  DOC-10-edit-frontend-profiles (we are `conversational-canvas`). DOC-04-edit earlier framed
  Canvas as Console-internal "not canon." Track, don't cite as locked.
- **B5 — Standards (LOCKED).** doc-10 §16 budgets (JS ≤250KB gzip, AI-edit ≤1.0s p95,
  region-level error boundaries, LKG ≤5s); §21 11-step validator (FE-020); Brand Kit voice/
  accessibility/motion rules.
