# Sprint 2 Results: v0.0 Smoke Test

**Run date:** 2026-04-22
**Corpus item:** `corpus/lost-in-the-middle/` (arXiv:2307.03172)
**Converter:** MinerU (pipeline backend)
**Judge model:** `claude-haiku-4-5-20251001`

---

## Goal

Smallest end-to-end that proves the methodology runs against a real PDF and a
real converter, with probes derived from the failure-mode catalog rather than
improvised. Output: a structured honesty profile.

## What was built

- `scripts/run-eval.py` — single-file harness. Loads probes, sends each probe
  + markdown to the Anthropic API, scores against expected answers, writes
  `honesty_profile.json`.
- `corpus/lost-in-the-middle/probes.json` — 10 probes (5 capture, 5 hallucination)
  covering heading, list, table, italic, inline_code, code_block features across
  correctly-used and hallucinated modes.
- MinerU output — `corpus/lost-in-the-middle/output/mineru/paper/auto/paper.md`
  and supporting images.

## Score

```
Capture:       100.0% (5/5)
Hallucination: 100.0% (5/5)
Overall:       100.0% (10/10)
```

**The score is hollow. Read the caveats before quoting it.**

## Caveats on the score

The 100% reflects two passes that don't mean what they look like:

1. **`cap-001` (heading nesting) flipped FAIL → OK across runs without any probe
   change.** Same markdown, same probe text, different judge answer. The probe
   wording — "is `Models` presented as a subsection nested under Multi-Document
   Question Answering?" — is genuinely ambiguous given MinerU's output: all
   sections are `##`, so by markdown depth they are siblings, but numbering
   ("2.2" under "2") implies hierarchy. The judge picks differently across runs.
   **The first-run finding still stands**: MinerU flattens heading depth.

2. **`cap-005` (inline_code on `0613`) passes for the wrong reason.** PDF-visual
   ground truth is "0613 is not monospace in footnote 5" → expected "no".
   MinerU returns "no" → match. But MinerU's "no" is because it dropped the
   entire footnote — silent content loss — not because it honestly preserved
   plain text. The probe yields the same answer for both behaviors and can't
   distinguish them.

## Real findings about MinerU (robust across runs)

- **Conservative on hallucination.** Did not invent any of the five feature
  patterns the hallucination probes tested for.
- **Flattens heading depth.** Every section/subsection/subsubsection emitted as
  `##`. Hierarchy is conveyed only through the author's numbering scheme
  ("2.2" implies child of "2"). Downstream readers that consume markdown
  heading levels (TOC builders, navigation tooling, agent scaffolding) see
  this paper as ~30 sibling sections.
- **Drops footnote content silently.** Footnote markers (e.g. ⁵) survive
  inline, but footnote bodies are missing from the document with no indication
  of loss.
- **Preserves tables well.** Table 1 (Closed-Book / Oracle accuracy by model)
  came through with structure and data intact.

## Methodology lessons

### Lesson 1: Ground truth must be PDF-visual, not LaTeX-source

Two probes failed (`cap-002` bullet list, `cap-004` italic) due to drift between
LaTeX source and rendered PDF, not converter behavior:

- `cap-002`: source has `\begin{itemize}`, PDF visually shows three
  bullet-prefixed paragraphs without typeset list block.
- `cap-004`: source has `\textit{use}`, PDF visually shows no italic — likely
  `tacl2021v1.sty` overriding `\textit{}` for body text.

We initially overreached and concluded "no rendering pipeline is faithful."
Empirical test (`experiments/source-fidelity-test/`) disproved that claim:
stock `article.cls` + `pdflatex` renders every catalog feature faithfully.
The real finding is narrower: **conference style files routinely override
semantic markup**, so source-as-ground-truth is unsafe for any wild PDF with
a custom template.

Resulting rule:

| Mode | Source→PDF fidelity | Ground truth basis |
|------|--------------------|--------------------|
| Wild PDF, no source | N/A | Eyes-on-PDF only |
| Wild PDF + source, conference template | Unreliable | Eyes-on-PDF |
| Wild PDF + source, vanilla template | Likely reliable | Source supports PDF visual after spot-check |
| Synthesized with vanilla template | Reliable (we own the pipeline) | Source-anchored |

Three of the original probe `ground_truth_basis` strings cited LaTeX line
numbers — those have been rewritten to cite PDF-visual evidence.

### Lesson 2: Two probe-design failure modes worth cataloging

Both are derived from concrete probes in this run.

**(a) Conflated probes — content-presence vs. format-preservation.**
`cap-005` asks "is `0613` formatted as monospace?" If the converter drops
`0613` entirely, the answer is "no" — same as if the converter preserved it
as plain text. The probe is blind to the difference between honest plain-text
preservation and silent content loss. **Rule:** every format-preservation
probe needs a paired content-presence probe.

**(b) Judge-judgment-sensitive probes.** `cap-001`'s phrasing leaves room for
the judge to interpret "subsection nested under" via either markdown depth or
numbering convention. Different judge runs answer differently. **Rule:** probe
wording must specify the observable structure unambiguously, leaving no
interpretation room. Failing that, run probes N times and require unanimous
agreement.

### Lesson 3: Synthesis path is concretely de-risked

The source-fidelity test (`experiments/source-fidelity-test/NOTES.md`)
empirically validated that we can author probes-by-construction: write source
with stock templates, render, know the PDF shows what the source said, write
probes against that with full confidence. This unlocks systematic catalog
coverage that wild corpus alone can't provide.

## Sprint 2 status

- [x] Author ~10 probes from catalog cells
- [x] Install MinerU and run on `paper.pdf`
- [x] Wire LLM Q&A loop using Anthropic API
- [x] Score against ground-truth answers; output `honesty_profile.json`

Sprint 2 closes with v0.0 smoke run committed and methodology lessons captured.

## Artifacts

- `scripts/run-eval.py` — harness
- `corpus/lost-in-the-middle/probes.json` — 10 probes (PDF-anchored ground truth)
- `corpus/lost-in-the-middle/output/mineru/paper/auto/paper.md` — converter output
- `corpus/lost-in-the-middle/output/mineru/paper/auto/honesty_profile.json` — scored profile
- `experiments/source-fidelity-test/` — `test.tex`, `test.pdf`, `NOTES.md`
- `docs/sprint-2-results.md` — this file
