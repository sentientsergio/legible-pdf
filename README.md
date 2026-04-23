# legible-pdf

**The legible converter is the honest converter.**

`legible-pdf` is a measurement framework for asking, of any tool that turns a PDF into something readable (markdown, HTML, JSON, structured intermediate, anything): *how honestly does this preserve what a careful reader sees?* The answer comes back as three concrete scores across three rule-based dimensions — **content** (did the information survive?), **readability** (do the formatting signals a human needs survive?), **provenance** (do the positional coordinates a citation needs survive?) — with no judgement-laden questions and no probability hedging. Point it at any tool ([MinerU](https://github.com/opendatalab/MinerU), [docling](https://github.com/docling-project/docling), [marker](https://github.com/datalab-to/marker), your own), get a structured honesty profile back across whichever output forms the tool produces.

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

Operationalization: **three audiences, three probe classes, three scores.**

A converter's output has three distinct audiences, and each has different requirements that the eval measures independently:

1. **Downstream LLM reader** — does the information survive the conversion? Tested by the **content** class via LLM-reader-equivalence: a vision-less LLM, given the converted markdown, should answer observational questions the same way an attentive human reader of the source PDF would. If the LLM is wrong, the conversion was dishonest about what the reader sees.

2. **Human previewing or pasting into Word/Pages** — do the formatting signals survive as markdown syntax that a renderer or office tool can auto-format? Tested by the **readability** class via rule-based markdown-syntax checks (heading depth, list bullets, code fences, emphasis markers, etc.). A converter that emits unicode `•` prefixes without markdown list syntax fails the readability rule for lists — a markdown renderer won't format them, a human paste-into-Word will need manual list-ifying.

3. **LLM-analyst producing verifiable citations** — do the positional coordinates survive so a reader can take *"quote, page N, section M"* back to the source PDF and verify? Tested by the **provenance** class via rule-based checks on page markers, section numbers, and cross-reference targets.

All three classes share one discipline: rule-based, binary per probe, ground-truthable from PDF-visual inspection, **no judge-as-taste-maker anywhere**. The "without judgement" qualifier is load-bearing across all three — every probe has an observable ground truth a human can verify by direct inspection of the source PDF, with no room for two readers to disagree.

## How honesty is measured

The converter's output is scored on three probe classes, reported independently with no composite:

| Class | Audience | Discipline | How it's judged |
|-------|----------|------------|-----------------|
| **content** | Downstream LLM reader | "Any clear signal" — accept prose, numbering, adjacency, any cue the LLM can recover from | LLM N=3 unanimous-agreement |
| **readability** | Human previewing / pasting | Strict markdown syntax — what a markdown renderer or Word paste would auto-format | Mechanical (regex/parser) for pure-syntax rules with three-valued output {yes, no, undetermined}; LLM fallback for undetermined or semantic-load rules |
| **provenance** | LLM-analyst citing | Positional coordinates (page markers, section numbers, cross-ref targets) preserved; paired presence + accuracy probes | Mechanical for presence where syntax is unambiguous; LLM for accuracy and semantic resolution |

Each converter gets a profile like *"strong honesty, weak readability, mixed provenance"* — the shape is the finding, not a percentage gold medal. Fabrication is tested within each class by probes with `expected_answer: no` (does the markdown falsely claim something the source doesn't have?). Definedness remains a goal of the framework — an honest converter should positively signal what it couldn't handle rather than silently drop — and applies across all three classes: silent dropping is detected by the paired-probe discipline (content-presence + format-preservation catches silent content loss hidden behind format-only success).

**Mechanical vs LLM judgment is deliberate.** The framework uses deterministic pattern-matching where markdown syntax is unambiguous (heading depth, list bullets, code fences), but every mechanical check carries an explicit `undetermined` output for inputs outside its scope of competence — silent mis-answer is worse than slower LLM inference. This mirrors the framework's own `undefined` principle: the measurement tooling obeys the rule it measures converters against.

**For the full taxonomy, rule tables, and scope of mechanical vs LLM checks, see [docs/failure-mode-catalog.md](docs/failure-mode-catalog.md).**

## Architecture intuition

A converter is a deterministic PDF reader with a defined capability table. Every input either matches a converter in the table (defined output) or is positively recognized as outside the table (axiomatic `undefined` output). No probability. No calibration. Categorical.

This makes the converter introspectable in a way LLM-self-uncertainty isn't: the capability table is enumerable. You can ask the converter what it has defined: *"multi-column reading order: defined as left-then-right column-major; merged-cell tables across pages: undefined by design; equations rendered as image with alt-text: defined; without alt-text: undefined."*

The corollary at the representation layer: **a converter shouldn't target Markdown directly.** Markdown lacks primitives for what we need to preserve (page breaks, footnote-to-body relationships, structured equations, captions-as-semantic-units, self-disclosure conventions). The cleaner architecture is to read PDFs into a **rich intermediate representation** — semantic roles tagged, undefined regions marked, provenance preserved — projected to Markdown (or HTML, or JSON, or whatever the consumer needs) as a final destination step.

We refer to that representation as **`legible-ir`** — the intermediate format that captures what the reader sees, projection-agnostic. `legible-ir` is an aspiration, not a delivered artifact. It will be developed through the battle scars of writing this eval and watching what the methodology forces the representation to express. Likely starting point: a Pandoc AST extension with provenance and undefinedness primitives added. Formalization comes *after* the eval has revealed what's necessary.

The eval can run against the intermediate representation OR any final projection — both are testable.

## What this isn't

- **Not a converter.** Converters are participants in the eval, not the eval itself.
- **Not Markdown-only.** The eval measures honesty of any PDF→{representation or projection} pipeline. Markdown is one common output; HTML, JSON, structured IR, or domain-specific formats can all be measured by the same probes.
- **Not [OmniDocBench](https://github.com/opendatalab/OmniDocBench).** OmniDocBench measures faithfulness on a fixed corpus. `legible-pdf` measures honesty across content, readability, and provenance — a different question with different probes, derived from the downstream audiences the converter's output actually serves.
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

**v0.3.1 shipped (2026-04-23).** The three-probe-class taxonomy is codified in the catalog, the harness runs class-based three-track scoring with mechanical + LLM hybrid dispatch, and MinerU (pipeline backend) is fully profiled across eight corpus items — one wild PDF and seven synthesized diagnostic items.

**MinerU v0.3.1 profile on the full corpus:**

- Content: **97%** (58/60) — the converter does not fabricate; one real content fail (silent footnote drop)
- Readability: **31%** (11/35) — italic/bold/monospace uniformly stripped, heading depth collapsed, bullet syntax absent
- Provenance: **75%** (6/8) — section numbers preserved via heading text, cross-references resolve; page markers entirely absent

*Strong honesty, weak readability, mixed provenance.* That shape is the finding.

**Shipped so far:**
- [`docs/failure-mode-catalog.md`](docs/failure-mode-catalog.md) — the taxonomy. v0.1 baseline (Layer 0 + Layer 1 × 14 markdown features × 4 modes) + v0.2 Sprint 3 amendments (probe-design disciplines, LLM-reader-equivalence framing) + v0.3 amendments (three probe classes, audience-needs lens) + v0.3.1 amendments (mechanical-check discipline, aggregation, audience-derived class-discipline boundary).
- [`docs/sprint-3-results.md`](docs/sprint-3-results.md) — methodology narrative, per-rule findings on MinerU, per-item scores, methodology lessons.
- [`scripts/run-eval.py`](scripts/run-eval.py) + [`scripts/rules.py`](scripts/rules.py) — single-file harness plus the mechanical rule checks.
- [`corpus/lost-in-the-middle/`](corpus/lost-in-the-middle/) — wild PDF (arXiv:2307.03172 "Lost in the Middle"); 21 probes authored against PDF-visual ground truth.
- [`corpus/synthesized/`](corpus/synthesized/) — 7 synthesized diagnostic items covering reading order, heading nesting (numbered and unnumbered), mixed list types, formatted text in context, tables with captions, and code blocks with images.

**Next:** Sprint 4b — multi-converter comparison. Add [docling](https://github.com/docling-project/docling), [marker](https://github.com/datalab-to/marker), and [PyMuPDF4LLM](https://github.com/pymupdf/PyMuPDF4LLM) to the eval; produce per-converter three-track profiles for cross-converter comparison. The v0.3.1 hardened infrastructure makes this a straightforward application.

The intermediate representation (`legible-ir`) remains aspiration, to be developed through eval-development battle scars rather than designed up front — likely as a Pandoc-AST extension with per-element provenance, confidence scores, reading-order metadata, and anchors back to PDF coordinates (see the companion essay [*What is a Legible PDF?*](https://sentientsergio.substack.com/p/what-is-a-legible-pdf) for the architectural intuition).

## Collaboration

If this resonates — if you are building a converter, evaluating one, or thinking about honest measurement of generative or semi-generative pipelines — engage. Open an issue with a question or counterargument. Push back on the methodology. Suggest probe types we haven't considered. Or just point at it from your own work.

The strongest version of this project is one shaped by the people who care about honest PDF→Markdown conversion — which turns out to be most people who have ever tried to use one.

## License

TBD (probably MIT or Apache-2.0; aligned with the open-source converter ecosystem this project participates in).
