"""Shared contract constants — MUST match content/COMPONENTS.md exactly.

bin/check-doctrine enforces the lockstep (it parses COMPONENTS.md and
compares against these lists). Edit the doc and this file together.
"""

# The kernel allowlist: the 12 component names canvas_set accepts (kernel
# allowlist.ts). A non-allowlisted name is a HARD validation error at the write
# boundary — rejected, never rendered as an error tile. The published
# rasa.layout.v1 schema enum is broader (the full 22-name doc-10 library);
# narrowing to these 12 is the kernel allowlist's job (canon Spec §56).
KERNEL_ALLOWLIST = [
    "card-strip", "table", "form", "chart", "code-block", "media-viewer",
    "kpi-tile", "timeline", "markdown-block", "button-row", "card-list", "html-embed",
]

# The subset the RasaOS shell renders — now IDENTICAL to the allowlist:
# what canvas_set accepts is exactly what renders (frontend-rasaos components.tsx).
SHELL_RENDERED = [
    "card-strip", "table", "form", "chart", "code-block", "media-viewer",
    "kpi-tile", "timeline", "markdown-block", "button-row", "card-list", "html-embed",
]
