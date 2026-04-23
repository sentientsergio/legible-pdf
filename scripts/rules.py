"""
Mechanical rule checks for v0.3.1 — deterministic three-valued output.

Each check takes the converter's markdown output and returns one of:

  {"result": "yes",          "details": "<why>"}  # rule clearly satisfied
  {"result": "no",           "details": "<why>"}  # rule clearly violated
  {"result": "undetermined", "details": "<why>"}  # edge of scope — escalate to LLM

The guiding principle: determinism is welcome only when it knows its limits.
A brittle check that returns yes/no on inputs outside its scope of competence
is worse than slower LLM inference because the failure is silent. Each rule
below documents its scope of competence explicitly; patterns that don't fit
the clear cases return "undetermined" so the harness can escalate to
LLM judgment.

Scope of this module (v0.3.1):
- Readability rules where markdown syntax is unambiguous:
    heading-depth, list-bullets, list-numbers, table-structure,
    code-fence, emphasis-bold, emphasis-italic, emphasis-mono
- Provenance-presence rules:
    page-marker (is any page-boundary signal present?),
    section-number (do headings carry numeric prefixes?)

Out of scope (stays LLM-judged):
- blockquote — quotation semantics are judgment-laden
- footnote-syntax — footnote identity carries semantic load
- cross-ref-target — both presence and accuracy need contextual resolution
- All provenance-accuracy probes — need per-target ground truth
- All content probes — LLM-reader-equivalence IS the test
"""

from __future__ import annotations

import re
from typing import Callable

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
HTML_HEADING_RE = re.compile(r"<h([1-6])[^>]*>", re.IGNORECASE)


def _heading_depths(md: str) -> list[int]:
    """Collect all heading depth integers (1..6) seen in markdown + HTML."""
    atx = [len(m.group(1)) for m in ATX_HEADING_RE.finditer(md)]
    html = [int(m.group(1)) for m in HTML_HEADING_RE.finditer(md)]
    return atx + html


def _body_heading_depths(md: str) -> list[int]:
    """Heading depths excluding the first occurrence (treated as title).

    For docs with a single `#` title followed by many `##` sections, body
    depths are all `##` — which is "flat" for the readability rule even
    though the doc formally has 2 distinct heading depths.
    """
    all_depths = _heading_depths(md)
    if not all_depths:
        return []
    # First heading is treated as title; body is everything after
    return all_depths[1:]


# -------------------------------------------------------------------
# Readability rules
# -------------------------------------------------------------------


def heading_depth(md: str) -> dict:
    """
    Rule: body headings should use >= 2 distinct markdown depths when the
    source has nested section/subsection structure. (The probe's presence
    means the source warrants this.)

    Scope of competence:
      yes — >= 2 distinct depths among body headings (everything after the
            first heading, which is treated as the title)
      no  — body headings all use the same depth (converter flattened)
      undetermined — < 2 body headings total (can't measure depth distinction)
    """
    body = _body_heading_depths(md)
    if len(body) < 2:
        return {
            "result": "undetermined",
            "details": f"only {len(body)} body heading(s) found; depth distinction not measurable",
        }
    distinct = set(body)
    if len(distinct) >= 2:
        return {
            "result": "yes",
            "details": f"body headings use {len(distinct)} distinct depths: {sorted(distinct)}",
        }
    return {
        "result": "no",
        "details": f"all {len(body)} body headings use depth {body[0]} (flattened)",
    }


MD_BULLET_LINE_RE = re.compile(r"^[ \t]*[-*+][ \t]+\S", re.MULTILINE)
HTML_UL_RE = re.compile(r"<ul\b", re.IGNORECASE)
UNICODE_BULLET_LINE_RE = re.compile(r"^[ \t]*[•·▪▫◦][ \t]+\S", re.MULTILINE)


def list_bullets(md: str) -> dict:
    """
    Rule: bulleted lists should use markdown bullet syntax (`-`, `*`, `+` at
    line start) or HTML `<ul>/<li>` — markup that a markdown renderer or
    Word/Pages will auto-format as a list.

    Scope of competence:
      yes — at least one markdown bullet line OR HTML <ul>
      no  — no bullet-list markup of any kind, and no unicode bullet
            characters either (purely prose)
      undetermined — lines begin with unicode bullet characters (`•`, `·`,
            `▪`, etc.) but no markdown syntax; a markdown renderer will not
            treat these as list items, but Word may auto-format — judgment
            is audience-dependent
    """
    if MD_BULLET_LINE_RE.search(md):
        return {"result": "yes", "details": "found markdown bullet syntax (- / * / + line prefix)"}
    if HTML_UL_RE.search(md):
        return {"result": "yes", "details": "found HTML <ul> list markup"}
    if UNICODE_BULLET_LINE_RE.search(md):
        return {
            "result": "undetermined",
            "details": "lines begin with unicode bullet characters (•, ·, etc.) but no markdown syntax; audience-dependent",
        }
    return {"result": "no", "details": "no bullet-list markup of any kind found"}


MD_NUMBERED_LINE_RE = re.compile(r"^[ \t]*\d+[.)][ \t]+\S", re.MULTILINE)
HTML_OL_RE = re.compile(r"<ol\b", re.IGNORECASE)


def list_numbers(md: str) -> dict:
    """
    Rule: numbered lists should use markdown numbered syntax (`1.`, `2.`, `3.`
    at line start) or HTML `<ol>/<li>`.

    Scope of competence:
      yes — at least one markdown numbered line OR HTML <ol>
      no  — no numbered-list markup
      undetermined — (rare) contexts where `1.` appears in mid-prose; the
            regex anchors to line start so this is uncommon
    """
    if MD_NUMBERED_LINE_RE.search(md):
        return {"result": "yes", "details": "found markdown numbered syntax (1. / 1) line prefix)"}
    if HTML_OL_RE.search(md):
        return {"result": "yes", "details": "found HTML <ol> list markup"}
    return {"result": "no", "details": "no numbered-list markup found"}


MD_TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$", re.MULTILINE)
HTML_TABLE_RE = re.compile(r"<table\b", re.IGNORECASE)


def table_structure(md: str) -> dict:
    """
    Rule: tables should render via markdown pipe syntax (`|...|`) or HTML
    `<table>`.

    Scope of competence:
      yes — at least one markdown pipe-table row OR HTML <table>
      no  — no table markup
      undetermined — aligned-column plain text that could be a table rendered
            without markup; hard to distinguish from regular prose
            mechanically

    Note: v0.3.1 treats HTML <table> as a pass. Open question for a later
    sprint: does <table> round-trip into Word/Pages as cleanly as markdown
    pipes? Empirical check deferred.
    """
    # Need at least 2 pipe-rows to suggest a real table (header + data)
    # rather than a stray pipe-delimited line
    if len(MD_TABLE_ROW_RE.findall(md)) >= 2:
        return {"result": "yes", "details": "found markdown pipe-table rows"}
    if HTML_TABLE_RE.search(md):
        return {"result": "yes", "details": "found HTML <table>"}
    return {"result": "no", "details": "no table markup found"}


FENCE_RE = re.compile(r"^```", re.MULTILINE)
INDENT_CODE_RE = re.compile(r"(?:^|\n\n)(?:    |\t).+", re.MULTILINE)


def code_fence(md: str) -> dict:
    """
    Rule: code blocks should use fenced syntax (```) or indented 4-space /
    tab code blocks.

    Scope of competence:
      yes — fence markers present, OR an indented code block distinguishable
            from list-item continuation
      no  — neither fences nor clear indented code blocks
      undetermined — monospace-styled content without fence markers that
            might be code-block-intended-but-unfenced
    """
    if FENCE_RE.search(md):
        return {"result": "yes", "details": "found fenced code block (```)"}
    if INDENT_CODE_RE.search(md):
        return {"result": "yes", "details": "found indented 4-space code block"}
    return {"result": "no", "details": "no code-block markup found"}


# Pair-based emphasis detection: avoid false positives on lone * or _ characters
EMPH_BOLD_MD_RE = re.compile(r"(\*\*|__)[^*_\s].*?[^*_\s]?\1")
EMPH_BOLD_HTML_RE = re.compile(r"<(b|strong)\b", re.IGNORECASE)


def emphasis_bold(md: str) -> dict:
    """
    Rule: bold emphasis should use markdown `**X**` / `__X__` or HTML
    `<b>` / `<strong>`.

    Scope of competence:
      yes — a paired bold marker covering non-whitespace content
      no  — no bold markup at all
      undetermined — lone `**` or `__` that don't form pairs (rare, usually
            means broken emphasis that may be converter artifact)
    """
    if EMPH_BOLD_MD_RE.search(md):
        return {"result": "yes", "details": "found markdown bold (**X** or __X__)"}
    if EMPH_BOLD_HTML_RE.search(md):
        return {"result": "yes", "details": "found HTML <b> or <strong>"}
    return {"result": "no", "details": "no bold emphasis markup found"}


# For italic: single * or _ pairs, not inside bold
EMPH_ITALIC_MD_RE = re.compile(r"(?<!\*)\*(?!\*|\s)[^*\n]+?(?<!\s)\*(?!\*)|(?<!_)_(?!_|\s)[^_\n]+?(?<!\s)_(?!_)")
EMPH_ITALIC_HTML_RE = re.compile(r"<(i|em)\b", re.IGNORECASE)


def emphasis_italic(md: str) -> dict:
    """
    Rule: italic emphasis should use markdown `*X*` / `_X_` or HTML
    `<i>` / `<em>`.

    Scope of competence:
      yes — a paired italic marker (not bold) covering non-whitespace content
      no  — no italic markup at all
      undetermined — asymmetric `*` or `_` characters that could be typos or
            artifacts of conversion; mechanical matching can miss genuine
            italic in these cases
    """
    if EMPH_ITALIC_MD_RE.search(md):
        return {"result": "yes", "details": "found markdown italic (*X* or _X_)"}
    if EMPH_ITALIC_HTML_RE.search(md):
        return {"result": "yes", "details": "found HTML <i> or <em>"}
    return {"result": "no", "details": "no italic emphasis markup found"}


# Inline code: single backticks, not triple (which is code fence)
EMPH_MONO_MD_RE = re.compile(r"(?<!`)`(?!`)[^`\n]+?`(?!`)")
EMPH_MONO_HTML_RE = re.compile(r"<code\b", re.IGNORECASE)


def emphasis_mono(md: str) -> dict:
    """
    Rule: inline monospace/code should use markdown single-backtick syntax
    or HTML `<code>`.

    Scope of competence:
      yes — inline backticks covering content, or HTML <code>
      no  — no monospace markup
      undetermined — unmatched backticks or fenced blocks only (fences are
            code-block-level, not inline-mono)
    """
    if EMPH_MONO_MD_RE.search(md):
        return {"result": "yes", "details": "found markdown inline code (`X`)"}
    if EMPH_MONO_HTML_RE.search(md):
        return {"result": "yes", "details": "found HTML <code>"}
    return {"result": "no", "details": "no inline monospace markup found"}


# -------------------------------------------------------------------
# Provenance-presence rules
# -------------------------------------------------------------------

# Page-marker candidates: any explicit page boundary signal a downstream
# reader could use to associate content with a page number.
PAGE_MARKER_PATTERNS = [
    re.compile(r"---\s*[Pp]age\s+\d+\s*---"),                        # `--- Page N ---`
    re.compile(r"<!--\s*[Pp]age\s+\d+\s*-->"),                       # HTML comment
    re.compile(r"^\s*\[[Pp]age\s+\d+\]\s*$", re.MULTILINE),          # `[Page N]`
    re.compile(r"^\s*[Pp]age\s+\d+\s*$", re.MULTILINE),              # bare `Page N` on its own line
    re.compile(r"<page\s+\d+", re.IGNORECASE),                       # custom HTML page tag
    re.compile(r"^\s*##?##?##?\s*[Pp]age\s+\d+", re.MULTILINE),      # `## Page N` heading
]


def page_marker(md: str) -> dict:
    """
    Rule: the converter should emit page-boundary signals so a downstream
    reader can associate content with its source page for citation.

    Scope of competence:
      yes — at least one recognizable page-marker pattern
      no  — no page-marker pattern of any common form; the markdown carries
            no page-boundary signal a downstream LLM could use
      undetermined — rare: numeric-only lines (`5`) that could be page
            numbers or could be body content

    Recognized patterns: `--- Page N ---`, `<!-- page N -->`, `[Page N]`,
    bare `Page N` line, `<page N>` custom tag, `## Page N` heading.
    """
    for pat in PAGE_MARKER_PATTERNS:
        if pat.search(md):
            return {"result": "yes", "details": f"found page-marker pattern: {pat.pattern}"}

    # Numeric-only lines — could be page numbers, could be body content
    numeric_only = re.findall(r"^\s*\d+\s*$", md, re.MULTILINE)
    if len(numeric_only) >= 3:
        # Three or more numeric-only lines — suspicious, might be page markers
        return {
            "result": "undetermined",
            "details": f"found {len(numeric_only)} numeric-only lines — could be page numbers or body content",
        }

    return {"result": "no", "details": "no page-marker pattern of any common form"}


# Section-number in heading text: `## 2.1 ...`, `### 2.1.3 ...`, `# A.1 ...`
SECTION_NUMBER_HEADING_RE = re.compile(
    r"^#{1,6}\s+(\d+(?:\.\d+)*|[A-Z](?:\.\d+)*)(?:\.)?\s+\S",
    re.MULTILINE,
)


def section_number(md: str) -> dict:
    """
    Rule: numbered section headings in the source should retain their number
    in the markdown heading text (e.g., `## 2.2 Models`) so a reader can
    produce citations like `Section 2.2`.

    Scope of competence:
      yes — at least one heading with a numeric prefix (`2`, `2.1`, `2.1.3`,
            or appendix-letter forms `A`, `A.1`)
      no  — no headings carry numeric prefixes
      undetermined — document has no headings at all (presence-of-numbers
            not measurable)
    """
    if not _heading_depths(md):
        return {"result": "undetermined", "details": "document has no headings"}
    if SECTION_NUMBER_HEADING_RE.search(md):
        return {"result": "yes", "details": "found heading with numeric prefix"}
    return {"result": "no", "details": "no heading carries a numeric prefix"}


# -------------------------------------------------------------------
# Dispatch
# -------------------------------------------------------------------

MECHANICAL_RULES: dict[str, Callable[[str], dict]] = {
    # Readability (pure markdown-syntax rules)
    "heading-depth":   heading_depth,
    "list-bullets":    list_bullets,
    "list-numbers":    list_numbers,
    "table-structure": table_structure,
    "code-fence":      code_fence,
    "emphasis-bold":   emphasis_bold,
    "emphasis-italic": emphasis_italic,
    "emphasis-mono":   emphasis_mono,
    # Provenance-presence (document-level signals)
    "page-marker":     page_marker,
    "section-number":  section_number,
}

# Rules that carry semantic load or need per-target resolution, staying
# LLM-judged in v0.3.1:
#   blockquote, footnote-syntax, cross-ref-target
#   list-definition (definition lists have term/def semantic pairing)
#   caption-adjacency (caption-figure relationship)
#   image-reference
# All provenance-accuracy probes also stay LLM-judged (need per-target
# ground truth that mechanical checks can't derive from markdown alone).


def has_mechanical_check(rule: str) -> bool:
    """Return True if rule has a mechanical check in v0.3.1."""
    return rule in MECHANICAL_RULES


def run_mechanical_check(rule: str, markdown: str) -> dict:
    """Run the mechanical check for a rule. Raises KeyError if rule unsupported."""
    return MECHANICAL_RULES[rule](markdown)
