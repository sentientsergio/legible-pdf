# tables-and-captions — methodology notes

## Result (2026-04-22, MinerU pipeline backend)

100% honest (12/12 probes, all unanimous N=3).

## What MinerU emits

Inspecting `output/source/auto/source.md`:

- **Tables** — emitted as HTML `<table>` with `<tr>`/`<td>` (not markdown
  pipes, no `<th>`, no header separator row). Cell content preserved
  verbatim, including numeric values like `1.008` and `0.0026`.
- **Captions** — preserved on their own line as `Table 1: Atomic properties...`
  / `Table 2: Approximate distances...`, positioned above the table block.
- **Cross-references** — resolved correctly: body text reads `Table 1`,
  `Table 2` (not `\ref` markup, not `Table ??`).
- **Bold headers** — the `\textbf{}` markup on header cells is dropped. All
  cells emit as plain `<td>`. Header status is implicit from row position
  (first row of each table).
- **Inline math** — `$Z = 1$` becomes plain text `Z = 1`. Math markup
  stripped, value preserved.
- **Section headings** — `## 1 First Three Elements` etc. with section
  number folded into heading text (consistent with mixed-lists item).

## Why probes pass anyway

Under LLM-reader-equivalence:
- HTML `<table>` is a clear table-presentation signal.
- "First row contains column names" is a clear header-distinction signal,
  even without `<th>` or markdown separators — the judge correctly identifies
  Element/Symbol/Atomic Number/Atomic Mass as headers.
- Plain-text `Z = 1` is a clear math-expression encoding.
- `Table 1:` adjacent to a table is a clear caption.
- `As shown in Table 1` in body text is a clear cross-reference.

## What a stricter test would catch

A "structural fidelity for downstream markdown tooling" axis (not currently
defined) would flag:
- HTML tables instead of markdown pipe-table syntax (some markdown renderers
  don't process inline HTML).
- Lost `<th>` tags (impacts CSS styling and screen-reader semantics).
- Lost math markup (impacts MathJax rendering and LaTeX round-tripping).

These are real concerns for some pipelines, but they are not honesty failures —
the information survives, an LLM reader recovers it. Recording them here so
that if the project ever defines a second axis, the data is already captured.

## Cross-reference resolution caveat

This item required two `pdflatex` passes to resolve `\ref{}` cross-references.
The first pass writes labels to `.aux`; the second pass reads them back. If
`.aux` is deleted between passes, references emit as `Table ??` and the
`tc-ref` probe will fail. Build script for the corpus should preserve `.aux`
across the two pdflatex passes, then clean up afterward.
