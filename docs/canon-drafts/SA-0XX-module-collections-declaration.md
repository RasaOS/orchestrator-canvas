---
id: SA-0XX (canon session assigns)
status: draft — authored in elements/domain-canvas (TASK-007); file to canon/tasks/triage/
spec_proposal_status: "v0.1 — optional additive convention; interim seam-first discovery works without it"
target_version: 1.5.0 (proposed)
target_docs:
  - 01_system_specification.html (Spec §9.4 provides{} — a collections[] declaration for module Elements that own record directories)
  - elements/ELEMENT_CONTRACT.md (§ how a module declares the record collections it owns)
  - downstream: schema/rasa.schema.v1.json (provides.collections[] fields)
originating_design: 2026-07-09 elements/domain-canvas core-internal-structure session — the canvas domain audits sibling modules to know what a UI can bind to (context.json, rasa.canvas.context.v1); today it must INFER each module's data shape
depends_on: []
relationship:
  - Strengthens the domain-canvas AUDIT process (elements/domain-canvas content/PROCESSES.md §AUDIT): a declared collections[] replaces best-effort inference with a module-authored contract.
filed_by: rasa.domain.canvas session 2026-07-09 (TASK-007)
---

# SA-0XX: `provides.collections[]` — let a module declare the record collections it owns

## Source

Filed from rasa.domain.canvas. The record-store modules (module-tasks,
module-notes, module-research, module-field-log, module-schedule, module-ingest,
…) each own a directory of structured records — one-file-per-record with
frontmatter, organized by a state-machine of subdirectories. domain-canvas
binds UIs to these collections and provisions new records into them. To do
that it must know each collection's directory, record shape, fields, states,
and whether it's writable.

**Today there is no declaration.** domain-canvas discovers this "seam-first":
(1) read the module's own seeded config file when it has one (module-research
seeds `.claude/research-canon.md` declaring its root/taxonomy/promotion); (2)
read the module's `rasa.json` seed/scaffold; (3) infer from the seeded layout
+ sample records. This works, but the inference is fragile and every consuming
element re-derives it.

## The proposal

A module MAY declare, in its `rasa.json` `provides{}` block, the collections
it owns:

```json
"provides": {
  "collections": [
    {
      "id": "tasks",
      "dir": "tasks",
      "shape": "folder-of-records",
      "record": {
        "file_glob": "TASK-*.md",
        "fields": { "id": "string", "category": "enum(stub|spec|bug|hotfix)", "status": "enum(triage|backlog|active|blocked|completed)" },
        "states": ["triage", "backlog", "active", "blocked", "completed"]
      },
      "writable": true,
      "write_via": "skill:task"
    }
  ]
}
```

- **Optional + additive** — modules without it keep working; consumers fall
  back to seam-first discovery.
- **`write_via`** (optional) names the module's declared write procedure (a
  skill), which formalizes the resolved-OQ-4 executor rule
  (elements/domain-canvas: module-mediated writes first, direct fallback):
  a consumer with a `write_via` writes through that skill; without one, direct
  conventional writes on `writable` collections.
- Mirrors the `rasa.canvas.context.v1` collection descriptor
  (elements/domain-canvas/schemas/) so the AUDIT walk becomes a copy, not an
  inference.

## Why canon, not just an element convention

The shape is cross-module (every record-store module), and the write-procedure
declaration is the clean, canon-level answer to "may one Element mutate
another's records" — it lets the owning module publish its own write API
instead of consumers guessing. Kernel-heavy/domain-light: the data-shape
contract belongs to the platform vocabulary, not to each consuming domain.

## Interim posture

domain-canvas ships seam-first discovery now (works today). If this lands,
its AUDIT process reads `provides.collections[]` first and only falls back to
inference — one-line precedence change, no rework.
