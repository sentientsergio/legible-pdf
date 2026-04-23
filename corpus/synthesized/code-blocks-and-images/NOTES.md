# code-blocks-and-images — methodology notes

## Result (2026-04-22, MinerU pipeline backend)

100% honest (10/10 probes, all unanimous N=3).

## What MinerU emits

Inspecting `output/source/auto/source.md`:

- **Code block** — `\begin{verbatim}` becomes plain paragraph text. NO
  fence markers (no ```python, no four-space indent), NO monospace markup.
  Each line of the function body emitted as flush-left text with trailing
  two-space soft-break markers. Indentation completely lost — the function
  body is no longer visually indented under `def`. Underscore in
  `binary_search` escaped as `binary\_search` (markdown-correct, since `_`
  is italic syntax).
- **Blockquote** — `\begin{quote}` becomes plain paragraph text. NO `>`
  prefix, NO indentation, NO italics. The quote is structurally
  indistinguishable from the surrounding prose. Only the attribution
  ("comes from Donald Knuth's writing on optimization") and the typographic
  separation (it is its own paragraph) carry the quotation signal.
- **Image** — `\includegraphics` becomes proper markdown:
  `![](images/<sha256>.jpg)`. The PNG was extracted, re-encoded as JPG,
  saved with a content-hash filename, and referenced with markdown image
  syntax. Caption emitted on the next line as `Figure 1: ...`.
- **Figure cross-reference** — `Figure~\ref{fig:chart}` resolved to
  `Figure 1` in body text.
- **Numeric/symbol** — `$-1$` rendered as Unicode minus sign `−1` (U+2212),
  not ASCII hyphen `-1`. Probe phrasing ("returns -1") still matches because
  the judge reads minus-as-minus regardless of code point.
- **Section headings** — same pattern as previous items: `## 1 Source Code`
  etc., section number folded into heading text.

## Why probes pass anyway

Under LLM-reader-equivalence:
- `def binary_search(arr, target):` and `while lo <= hi:` are recognizable
  Python syntax. The judge identifies the block as code from the syntax
  itself, even without fence markers or indentation.
- The Knuth quote is bracketed by attribution prose ("comes from Donald
  Knuth's writing" before, "The full passage from Knuth continues" after).
  The judge identifies it as a quotation from this contextual framing.
- Markdown image syntax `![](path)` is unambiguous — judge correctly
  identifies an image is present.
- `Figure 1:` adjacent to the image is a clear caption.
- `As shown in Figure 1` in body text is a clear cross-reference.

## What a stricter test would catch

A "structural fidelity for downstream tooling" axis would flag:
- Lost code-block fences (impacts syntax highlighting in markdown renderers
  that rely on language hints).
- Lost blockquote `>` prefix (impacts CSS styling, screen-reader semantics,
  and tooling that extracts quotations programmatically).
- Lost code indentation (impacts copy-paste — the function would not run
  if pasted into a Python REPL).

These are real concerns but are not honesty failures by this methodology.
The information survives; an LLM reader recovers it. Recording here so the
data exists if a second axis is ever defined.

## Artifact note: the chart.png

A 400x300 PNG bar chart synthesized with Pillow accompanies this item as
the image asset. MinerU's pipeline backend appears to re-encode it as JPG
and save it under a content-hash filename in `output/source/auto/images/`.
The original `chart.png` is preserved at the corpus item root for source
fidelity.
