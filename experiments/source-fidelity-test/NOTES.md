# Source-Fidelity Test — 2026-04-22

## Question

Does the source→PDF rendering pipeline preserve the catalog features faithfully
enough that source can serve as ground truth for converter evaluation?

## Why we asked

While running the v0.0 smoke harness on Lost in the Middle, two probes failed in
ways that traced back not to MinerU's behavior but to drift between LaTeX source
and rendered PDF:

- `cap-002` (bullet list): source has `\begin{itemize}`, PDF visually shows three
  bullet-prefixed paragraphs without typeset list block (or so close to it the
  converter can't reliably promote)
- `cap-004` (italic): source has `\textit{use}`, PDF visually shows no italic
  (likely `tacl2021v1.sty` overriding `\textit` for body text, or arxiv-eprint
  vs. published-PDF version drift)

This led to an overreach: "no rendering pipeline is faithful, source-as-ground-truth
is structurally impossible." That generalized from n=1 to a methodology-killing
claim. Sergio caught the overreach. We tested empirically.

## Method

Authored `test.tex` using stock `article.cls` with one example of each catalog
feature: heading hierarchy (3 depths), bullet list, numbered list, italic, emph,
bold, inline code (`\texttt`), code block (`verbatim`), table, block quote,
footnote.

Rendered with `pdflatex` (TeX Live 2026, BasicTeX install). Read both the PDF's
extracted text and the rendered page images, compared each feature to source.

## Result

Every feature rendered faithfully:

| Source command | PDF visual | Verdict |
|----------------|------------|---------|
| `\textit{italic}` | italic (slanted glyphs) | faithful |
| `\emph{emphatic}` | italic | faithful |
| `\textbf{bold}` | bold (heavy glyphs) | faithful |
| `\texttt{0613}` | monospace | faithful |
| `\section` / `\subsection` / `\subsubsection` | three distinct depths | faithful |
| `\begin{itemize}` | indented bulleted list | faithful |
| `\begin{enumerate}` | indented numbered list | faithful |
| `\begin{verbatim}` | monospace block, indentation preserved | faithful |
| `\begin{tabular}` with `\hline` | table with rules, header row distinct | faithful |
| `\begin{quote}` | indented block | faithful |
| `\footnote` | superscript marker + bottom-of-page note | faithful |

## Conclusion

Stock `article.cls` + `pdflatex` is faithful for the catalog features. The
"no faithful renderer" claim was wrong. The TACL-template drift in Lost in the
Middle is a class-file problem, not a rendering-fundamentals problem.

**Methodology consequences:**

| Mode | Source→PDF fidelity | Ground truth basis |
|------|--------------------|--------------------|
| Wild PDF, no source | N/A | Eyes-on-PDF only |
| Wild PDF + source, conference template | unreliable (TACL strips italic) | Eyes-on-PDF |
| Wild PDF + source, vanilla template | likely reliable | Source supports PDF visual after spot-check |
| Synthesized with vanilla template | reliable (we control the pipeline) | Source-anchored, with rendered-PDF spot-check |

**What this unlocks:** the synthesized-corpus idea is concretely de-risked.
Author `\textit{x}` with stock `article.cls`, render → know the PDF shows italic
→ write probe with full confidence. Probe-by-construction.

**What it does not change:** for any wild PDF (with or without source), ground
truth must still be eyes-on-PDF. You don't know what the template did.

## Artifacts

- `test.tex` — source used in this test
- `test.pdf` — rendered PDF
- `test.log`, `test.aux` — LaTeX byproducts (delete on cleanup)
