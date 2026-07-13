# Changelog — Task Backlog (example app)

## 0.1.0 — 2026-07-12

LIST_DETAIL reference: a lone SECTION (`backlog`) whose `card-list` opens two
LEAF detail screens (`parent: backlog`) via `open:*` actions. The leaves are
reachable through `events[].target` (not literal `nav:` links), and each carries
a one-button `nav:backlog` back — the section/leaf nav model, minimal shape.
