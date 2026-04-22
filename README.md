# legible-pdf

**The legible converter is the honest converter.**

`legible-pdf` is a measurement framework for asking, of any tool that turns a PDF into something readable (markdown, HTML, JSON, structured intermediate, anything): *how honestly does this preserve what a careful reader sees?* The answer comes back as concrete numbers across three axiom-layer dimensions — capture, fabrication, definedness — with no judgement-laden questions and no probability hedging. Point it at any tool ([MinerU](https://github.com/opendatalab/MinerU), [docling](https://github.com/docling-project/docling), [marker](https://github.com/datalab-to/marker), your own), get a structured honesty profile back across whichever output forms the tool produces.

This is not a converter. It is the measurement that determines which converters — and which output forms — preserve the PDF viewing experience legibly.

---

## Why this exists

The PDF→Markdown space has many converters and no honest yardstick. Existing benchmarks measure faithfulness — how much source content survives — and treat silent dropping as just-low-faithfulness rather than as a categorically different failure mode. They don't measure fabrication. They don't measure self-disclosure. They reward converters that smooth over rough sources to look better than they were.

The premise is simple: a converter that captures 95% of a document and *says what it dropped* is more useful than a converter that captures 99% and silently loses the 1% that mattered. **Honest beats faithful.**

## What "best" means

A working definition, single-criterion:

> **Best = most honest.**
>
> An honest converter: when it captures something, captures it correctly. When it can't, says so. Doesn't fabricate. Behaves the same way twice on the same input.
>
> A dishonest converter: silently drops content; hallucinates structure that wasn't there; smooths over rough sources; misclassifies content (figure caption rendered as H3) without flagging the uncertainty.

Operationalization: **LLM-reader-equivalence, without judgement.**

A successful converter generates Markdown such that, when a vision-less LLM is asked an objective, judgement-less question about the document, it returns the answer an intelligent and attentive human would have given after reading the original PDF. If the LLM is wrong, the conversion was dishonest about what the reader sees. If the LLM hallucinates or can't answer, the conversion distorted semantics.

The "without judgement" qualifier is load-bearing. The eval cannot use questions whose answers depend on interpretation ("is the proposal well-argued?" "what is the main thesis?"). It uses observational questions whose ground truth a human can verify by direct inspection of the source PDF, with no room for two readers to disagree. Axiom-layer first; higher-order claims are not in scope here.

## How honesty is measured

Three axiom-layer probe types:

1. **Capture probe.** *"Does X appear in this document?"* where X is observably present in the source PDF. Ground truth YES; the markdown should support a YES answer. Counting questions are a special case: *"How many code blocks does this paper contain?"* — silent dropping is caught precisely because the count comes back wrong.

2. **Hallucination probe.** *"Does Y appear in this document?"* where Y is plausibly-absent (something a converter might fabricate but isn't actually there). Ground truth NO; the markdown should support a NO answer. Without this mirror probe, a converter that adds plausible content gets credit for matching all the YES probes and is never caught.

3. **Definedness probe.** For things present in the source PDF that the converter could not capture, did the markdown emit an explicit `undefined` marker for that location? Or did the content silently disappear? This probe distinguishes the converter that says *"equation in §4.2: conversion undefined (image-only, no alt text)"* from one that just drops the equation.

All three probes are observational. None require calibration of LLM uncertainty. None ask anyone to make a judgement.

## Architecture intuition

A converter is a deterministic PDF reader with a defined capability table. Every input either matches a converter in the table (defined output) or is positively recognized as outside the table (axiomatic `undefined` output). No probability. No calibration. Categorical.

This makes the converter introspectable in a way LLM-self-uncertainty isn't: the capability table is enumerable. You can ask the converter what it has defined: *"multi-column reading order: defined as left-then-right column-major; merged-cell tables across pages: undefined by design; equations rendered as image with alt-text: defined; without alt-text: undefined."*

The corollary at the representation layer: **a converter shouldn't target Markdown directly.** Markdown lacks primitives for what we need to preserve (page breaks, footnote-to-body relationships, structured equations, captions-as-semantic-units, self-disclosure conventions). The cleaner architecture is to read PDFs into a **rich intermediate representation** — semantic roles tagged, undefined regions marked, provenance preserved — projected to Markdown (or HTML, or JSON, or whatever the consumer needs) as a final destination step.

We refer to that representation as **`legible-ir`** — the intermediate format that captures what the reader sees, projection-agnostic. `legible-ir` is an aspiration, not a delivered artifact. It will be developed through the battle scars of writing this eval and watching what the methodology forces the representation to express. Likely starting point: a Pandoc AST extension with provenance and undefinedness primitives added. Formalization comes *after* the eval has revealed what's necessary.

The eval can run against the intermediate representation OR any final projection — both are testable.

## What this isn't

- **Not a converter.** Converters are participants in the eval, not the eval itself.
- **Not Markdown-only.** The eval measures honesty of any PDF→{representation or projection} pipeline. Markdown is one common output; HTML, JSON, structured IR, or domain-specific formats can all be measured by the same probes.
- **Not [OmniDocBench](https://github.com/opendatalab/OmniDocBench).** OmniDocBench measures faithfulness on a fixed corpus. `legible-pdf` measures honesty across capture, fabrication, and definedness — a different question with different probes.
- **Not a paper-quality eval.** Quality is judgement-laden. This eval works strictly at the axiom layer (what the reader observably sees), so its ground truth is incontestable.

## Prior art and influences

What we leverage and learn from:

- **[Pandoc](https://github.com/jgm/pandoc)** — the canonical document AST. Our planned intermediate representation (`legible-ir`, aspirational) will likely start as a Pandoc-AST extension with provenance and undefinedness primitives added. Pandoc has solved most of the document-structure type system; we add what's missing for honest PDF interpretation.
- **[MinerU](https://github.com/opendatalab/MinerU)** — current breadth leader on PDF extraction; primary participant in the eval.
- **[docling](https://github.com/docling-project/docling)** — IBM's PDF→structured pipeline; another primary participant.
- **[PyMuPDF](https://github.com/pymupdf/PyMuPDF) / [pymupdf4llm](https://github.com/pymupdf/PyMuPDF4LLM)** — span-level metadata that survives extraction (color, font, flags); useful overlay layer.
- **[Marker](https://github.com/datalab-to/marker)** — open-source LLM-assisted converter, popular participant.
- **[OmniDocBench](https://github.com/opendatalab/OmniDocBench)** — closest existing benchmark; we differ in goals (honesty vs faithfulness) but share the discipline of public methodology.

## Status

Vision phase. Methodology defined; harness not yet built; intermediate representation (`legible-ir`) named as aspiration, to be developed through eval-development battle scars rather than designed up front. First implementation work: corpus selection, probe-generation tooling, single-tool end-to-end smoke test, then expansion to comparative measurement.

This README is the design document. It is also the publishable methodology piece. The harness, the corpus, and eventually the formalized IR follow from it.

## Collaboration

If this resonates — if you are building a converter, evaluating one, or thinking about honest measurement of generative or semi-generative pipelines — engage. Open an issue with a question or counterargument. Push back on the methodology. Suggest probe types we haven't considered. Or just point at it from your own work.

The strongest version of this project is one shaped by the people who care about honest PDF→Markdown conversion — which turns out to be most people who have ever tried to use one.

## License

TBD (probably MIT or Apache-2.0; aligned with the open-source converter ecosystem this project participates in).
