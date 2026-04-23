# Sprint 3 Results: Probe Discipline, Targeted Synthesis, and Taxonomy Correction

**Run dates:** 2026-04-22 (v0.2 synthesis + retrofit), 2026-04-23 (v0.3 taxonomy + re-score)
**Corpus:** `corpus/lost-in-the-middle/` + 7 synthesized items under `corpus/synthesized/`
**Converter:** MinerU (pipeline backend)
**Judge model:** `claude-haiku-4-5-20251001`

---

## Goal

Three things, all on the same branch:

1. **Probe discipline.** Codify the lessons from Sprint 2's v0.0 smoke run: paired content/format probes, unambiguous wording, N=3 unanimous-agreement scoring.
2. **Targeted synthesis.** Author ~6 PDFs-by-construction covering catalog cells underrepresented in the wild Lost-in-the-Middle item. Each synthesized with vanilla `article.cls` + `pdflatex`, so the author owns the source→PDF pipeline and can author probes against PDF-visual ground truth with full confidence.
3. **Reading-order coverage.** At least one synthesized item exercising Layer 0 reading-order probes (multi-column layout).

The sprint delivered all three. Mid-sprint it also revealed two blind spots that required a methodology correction — **provenance** and **readability** as scored dimensions. v0.3 codifies the correction as a three-probe-class taxonomy.

## What was built

**Seven synthesized corpus items**, each rendered from stock `article.cls` sources with `pdflatex`:

- `multi-column-reading-order` — two-column layout with interleaved text, numbered reading-order markers
- `nested-headings-deep` / `nested-headings-unnumbered` — diagnostic pair isolating numbered vs unnumbered heading hierarchy
- `formatted-text-in-context` — italic / bold / monospace × 3 positions (body, table cell, footnote)
- `mixed-lists` — bulleted / numbered / two-level nested / definition list combinations
- `tables-and-captions` — two tables with captions and cross-references, including a synthesized PNG asset (Pillow-generated chart)
- `code-blocks-and-images` — verbatim code block, blockquote, figure with caption and cross-reference

**Harness extension** — `scripts/run-eval.py` gained N=3 unanimous-agreement scoring (a probe matches only if all three runs agree AND the agreed answer matches expected; disputed runs count as probe-quality signal, not converter failure).

**Lost-in-the-Middle retrofit** — `corpus/lost-in-the-middle/probes.json` rewritten v0.1 → v0.2 under the Sprint 3 probe-design disciplines. 15 probes covering heading, list, table, italic, inline code, code-block features with paired content/format structure.

**Catalog amendments** — `docs/failure-mode-catalog.md` v0.1 → v0.2 added three amendment subsections: LLM-reader-equivalence as the honesty test, probe-design disciplines codified, and MinerU per-feature observations.

## Two blind spots mid-sprint

After the v0.2 work shipped to the branch, two blind spots surfaced in conversation that required a methodology correction:

### Blind spot 1 — Provenance

A converter's strongest LLM-era use case includes enabling verifiable citations: an LLM-analyst answers a legal or audit question and produces *"`exact quote`, page N, section M"* — a citation a human reader takes back to the source PDF and verifies. This requires the converter to preserve **positional coordinates**: page markers, section numbers, cross-reference targets, footnote anchors. Catalog v0.2 did not index any of these as first-class testable features.

The gap was not an oversight of downstream needs — the `legible-pdf` essay explicitly names the intermediate representation's extensions to Pandoc's AST: *per-element provenance, confidence scores, reading-order metadata, anchors back to the lossless text layer, **anchors back to the original PDF coordinates***. The architecture anticipated citation-fit. The catalog and probes had not caught up to the architecture.

### Blind spot 2 — Readability

Sprint 3's v0.2 amendment stated the load-bearing honesty call: *"LLM-reader-equivalence is the honesty test."* It illustrated with the `mixed-lists` item: MinerU emitted bullet-prefixed paragraphs (no markdown list syntax), the downstream judge-LLM still recovered list structure from context, probes scored 100%, converter passed honesty. The framing treated format preservation as a question subordinate to LLM-readability.

The correction: **users preview converted markdown.** Humans paste output into Word or Pages to produce clean documents. A converter that flattens every heading to `##` — even if an LLM reader can recover hierarchy from section numbers — still imposes tedious manual re-leveling on any user trying to restore depth. *"How long does it take to format it properly?"* is a question with a real cost. Readability is a non-zero scored dimension, below honesty but above zero.

### The common cause — failure-modes-first vs audience-needs

Both gaps traced to a single methodological miss: the catalog was built **failure-mode-first** (*"what converters get wrong when they try"*) rather than also **audience-needs-first** (*"what the downstream consumers require the output to carry"*). Page markers are the canonical case of the former missing: no converter *gets them wrong* because no converter emits them at all; the absence is invisible to a failure-mode-first lens. The catalog is now indexed by both lenses, and v0.3 adds a methodology note codifying the audience-needs construction rule.

## v0.3 response — three probe classes

v0.3 formalizes the correction as three probe classes plus a rule-based discipline shared by all three. See `docs/failure-mode-catalog.md` §v0.3 amendments for the full taxonomy; summary:

| Class | Audience | What it measures |
|-------|----------|------------------|
| **content** | Downstream LLM-reader | Honesty. Content preserved; nothing fabricated. |
| **readability** | Human previewing / pasting into Word | Formatting signals a human needs to restore the doc without manual re-structuring. |
| **provenance** | LLM-analyst producing verifiable citations | Positional coordinates a human can use to verify a quote in the source PDF. |

All three share one discipline: rule-based, binary per probe, ground-truthable from PDF-visual inspection, LLM-reader-equivalence judged, N=3 unanimous-agreement required. **No judge-as-taste-maker anywhere.** Readability and provenance rules each enumerate specific markdown-syntax criteria tied to human-cleanup cost (e.g., `heading-depth` rule fails when all headings collapse to the same level, because a user pasting into Word must manually re-level every one).

Each converter gets three scores reported independently. No composite. The profile is the finding — *"strong honesty, mixed readability, weak provenance"* — not a percentage gold medal.

## Scores (MinerU pipeline backend)

Per-item, v0.3 three-class scoring with N=3 unanimous-agreement:

| Corpus item | Content | Readability | Provenance |
|-------------|---------|-------------|------------|
| `lost-in-the-middle` | 9/12 (75%) *2 disputed* | 2/3 (67%) | 4/6 (67%) |
| `code-blocks-and-images` | 5/5 (100%) | 4/4 (100%) | 1/1 (100%) |
| `formatted-text-in-context` | 11/11 (100%) | **0/9 (0%)** | — |
| `mixed-lists` | 6/6 (100%) | 4/4 (100%) | — |
| `multi-column-reading-order` | 10/10 (100%) | — | — |
| `nested-headings-deep` | 5/5 (100%) | 5/5 (100%) | — |
| `nested-headings-unnumbered` | 5/5 (100%) | **2/5 (40%)** | — |
| `tables-and-captions` | 6/6 (100%) | 5/5 (100%) | 1/1 (100%) |
| **Aggregate** | **57/60 (95%)** *2 disputed* | **22/35 (63%)** | **6/8 (75%)** |

**MinerU profile: strong honesty, mixed readability, weak provenance.** Content preservation is robust overall — aggregate 95% across 60 probes, with one content fail (LITM's footnote-5 body drop, discussed below) and two disputed probes both on LITM's abstract content (judge instability on short-phrase presence checks). Readability varies dramatically by rule: heading-depth on numbered source passes, heading-depth on unnumbered source fails, italic/bold/monospace fail uniformly. Provenance is weakest at the `page-marker` rule specifically: pagination is entirely absent from markdown output — section-number preservation (via folded heading text) and cross-reference targets both hold up, so provenance aggregate (75%) is driven down almost entirely by the page-marker gap on LITM.

## Per-rule findings

### Content (honesty)

- **Fabrication discipline holds.** Every `content` probe with `expected_answer: no` — tests asking if the converter introduced structure not in the source — passed on every corpus item. MinerU does not invent headings, tables, lists, or code blocks where source has none.
- **One real content failure: LITM `lt-c-c`.** Footnote 5 in the LITM source contains *"We use the 0613 OpenAI model versions"* — the reproducibility-critical model version identifier. MinerU's pipeline backend extracts this content into its internal `content_list.json` (marked as `page_footnote` on page 5) but does not project it to the markdown output. A downstream summarizer reading MinerU's markdown would lose the most reproducibility-critical fact in the document. This is exactly the kind of silent content loss the Sprint 3 probe-design disciplines were built to expose — paired content/format probes make the drop visible (previously the Sprint 2 conflated probe had masked it).
- **Two disputed content probes on LITM abstract (judge instability).** `lt-i-c` (is the phrase *"how well they use longer context"* present in the abstract?) and `lt-bu-c` (are the three introduction findings present?) both returned mixed answers across N=3 runs. The content targets are present verbatim in MinerU's markdown — a human reading the output can find them trivially. Judge instability on content-presence probes over specific phrases appears to be a Haiku-model property rather than a probe-wording issue. Sprint 4 prep: evaluate whether a larger judge model or a stricter prompting pattern resolves the instability, or whether some content probes need mechanical string-match checks instead of LLM judgment.

### Readability (markdown-syntax preservation)

- **Emphasis is universally stripped.** `formatted-text-in-context` scores 0/9 on italic, bold, monospace across body, table-cell, and footnote positions. This is position-independent — not a footnote-specific or table-cell-specific failure, but a pipeline-wide emphasis-stripping behavior in MinerU's pipeline backend. Every user of MinerU on an academic paper loses every italic and bold emphasis.
- **Heading depth is numbering-dependent.** MinerU folds numbered headings into heading text (`## 2.2 Models`) but does not translate the number into markdown depth (`###`). On source with explicit numbering (`nested-headings-deep`), hierarchy is readable via the numbers in the heading text — a markdown renderer treats every heading as `##`, but a user can still see `## 2.2` and `## 2.2.1` and reason about structure. On source *without* explicit numbering (`nested-headings-unnumbered`), there is no recovery path: every heading becomes `##` with no distinguishing cue. The diagnostic pair is the clearest output of Sprint 3 — MinerU's heading behavior is precisely characterized.
- **Table structure is HTML-preserved.** MinerU emits HTML `<table>` (not markdown pipes, and without `<th>`). A user pasting into Word or rendering in a markdown previewer sees the table intact. Readability passes.
- **Judge-interpretation drift on the `list-bullets` rule.** LITM's `lt-bu-f` probe was authored with strict wording — *"lines beginning with `-`, `*`, or `+`, or HTML `<ul><li>`; answer no if paragraphs are prefixed with `•`"* — and MinerU's output emits paragraphs prefixed with `•`. Expected answer: no. The judge (Haiku) returned unanimous yes across three runs. This appears to be the LLM judge drifting toward LLM-reader-equivalence interpretation — it treats `•` as functionally list-like regardless of explicit CommonMark-spec wording. The finding is itself informative: LLM-judged strict readability collapses back toward LLM-reader-equivalence for some rules. Mechanical (regex / parser-based) readability checks are probably the right move for rules with unambiguous markdown syntax (list prefixes, fence markers, heading depth); LLM-judged works fine where the expected answer has structural ambiguity. Sprint 4 prep.

### Provenance (positional-coordinate preservation)

- **Page markers are entirely absent.** MinerU's pipeline-backend markdown contains zero page-number indications. Every `page-marker` probe on LITM fails both presence and accuracy. MinerU's internal `content_list.json` knows page boundaries (`page_idx` field per extracted element); those are simply not projected to the markdown output. For the citation use case, this is the single most consequential gap.
- **Section numbers pass.** MinerU folds source section numbers into heading text (`## 2.2 Models`). The accuracy probe `lt-sn-a` passes unanimously — the reader can produce *"Section 2.2"* citations. The presence probe `lt-sn-p` was disputed on an earlier run (2 yes / 1 no across 3 runs) but resolved to unanimous yes on the current run; the disputed-probe disposition is a Haiku stability signal, not a stable MinerU failure.
- **Cross-references resolve.** Both `lt-cr-p` and `lt-cr-a` pass unanimously. MinerU preserves inline `§2.3` references and also emits the `## 2.3 Results and Discussion` target heading — the reference points at content identifiable in the markdown.
- **Scope note on footnote identity.** An earlier v0.3 draft included a `footnote-anchor` provenance rule testing whether the markdown preserves *"footnote 5"* as an identifiable coordinate. That rule conflated with the content-drop failure (MinerU loses the footnote body) and also generalized beyond the core citation use case — the coordinates a citation of form *"quote, page N, section M"* requires are page + section + cross-ref target. Footnote numbering is a specialized citation coordinate for document classes that use footnote-level citations; it's been removed from v0.3's core rule set and is a candidate for an optional rule in a future sprint.

## Methodology lessons

**Lesson 1 — Audience-needs and failure-modes are dual construction lenses.** The catalog was built failure-mode-first. Both v0.3 additions (provenance, readability) emerged from asking *"what does the downstream consumer need?"* — a question the failure-mode-first construction did not ask. The v0.3 amendments codify both lenses as first-class catalog construction methods. When the catalog is next extended, either lens can surface a cell; both are valid sources.

**Lesson 2 — Each probe class needs its own judgment discipline.** Content probes work well with LLM-reader-equivalence wording ("does the information survive in any clear encoding"). Readability probes need stricter markdown-syntax wording, but LLM judges drift toward equivalence interpretation on some rules (`list-bullets` particularly). Sprint 4 prep includes moving rules with unambiguous markdown syntax to mechanical regex/parser checks, reserving LLM judgment for rules where the decision has structural ambiguity.

**Lesson 3 — A paired probe is not just a doubled probe.** The paired content/format discipline from Sprint 2 generalized: v0.3 provenance probes are also paired (coordinate-presence + coordinate-accuracy). Pairing makes three failure modes individually detectable (drop, fabricate-wrong, preserve-correct) that a single probe cannot distinguish. Every probe class that tests for *"a thing plus a property of that thing"* benefits from pairing.

**Lesson 4 — Honesty pass does not imply overall fitness.** MinerU aggregate content score is 97%. MinerU aggregate readability score is 63%. MinerU aggregate provenance score is 60%. The same converter is strong under one lens, weak under two others. The three-track profile is exactly the deliverable — reducing it to a single number destroys the finding.

## What landed vs what's left

**Landed on this branch** (commits 9ec1455 through the v0.3 amendment series):

- ✅ Sprint 3 spec (`docs/sprint-3.md`), N=3 unanimous-agreement harness, 7 synthesized items, LITM retrofit, v0.2 catalog amendments.
- ✅ v0.3 catalog amendments codifying the three probe classes, readability/provenance rules, audience-needs-lens methodology note.
- ✅ v0.3 probe schema (`probe_class` / `feature` / `rule` fields). LITM probes migrated and extended with 6 provenance probes (3 rules × paired presence/accuracy: page-marker, section-number, cross-ref-target). Seven synthesized items migrated to v0.3 schema.
- ✅ Harness v0.3 — class-based three-track scoring, `honesty_profile.json` with per-class breakdown.
- ✅ Full corpus re-score against MinerU — all 8 items have v0.3 profiles.

**Deferred to Sprint 4 prep** (not blocking Sprint 3 close, but the next work to do):

- **Rewrite synthesized-item readability probes with strict markdown-syntax wording.** Only LITM's `lt-h-f` and `lt-bu-f` were rewritten in this sprint (as exemplars of the v0.3 strict-readability discipline). The 7 synthesized items' readability probes still carry v0.2 "any clear signal" LLM-reader-equivalence wording. Their readability scores in the table above reflect that wording, not strict v0.3. Expected effect when rewritten: `formatted-text-in-context` stays at 0/9; `nested-headings-unnumbered` stays at 40%; `nested-headings-deep` likely drops from 100% to partial (depth flat despite numbering); `mixed-lists` readability drops (bullets stripped despite `•` prefix).
- **Mechanical readability checks.** Convert rules with unambiguous markdown-syntax criteria (`list-bullets`, `heading-depth`, `code-fence`) to regex/parser-based checks. Reserve LLM judgment for rules where the decision has structural ambiguity.
- **Judge-stability investigation.** `lt-i-c` and `lt-sn-p` both disputed under Haiku. Consider stricter prompting, larger judge model, or both.

## Sprint 3 status

- [x] Probe discipline codified (paired probes, unambiguous wording, N=3 unanimous)
- [x] 7 synthesized corpus items authored with PDF-visual ground truth
- [x] Reading-order coverage via `multi-column-reading-order`
- [x] LITM probes retrofitted under Sprint 3 disciplines
- [x] Two blind spots surfaced and corrected — v0.3 three-probe-class taxonomy
- [x] MinerU re-scored under v0.3 across all 8 corpus items
- [x] Results documented (this file)

Sprint 3 closes with the v0.3 taxonomy shipped, MinerU fully profiled, and Sprint 4 (multi-converter comparison with the v0.3 scoring) cleanly teed up.

## Artifacts

- `docs/failure-mode-catalog.md` — v0.3, three-probe-class taxonomy + readability/provenance rules + audience-needs-lens methodology note (v0.1 baseline and v0.2 amendments preserved above).
- `scripts/run-eval.py` — harness v0.3, class-based three-track scoring.
- `corpus/lost-in-the-middle/probes.json` — 21 probes (12 content, 3 readability, 6 provenance). Includes 6 new provenance probes across 3 rules (page-marker, section-number, cross-ref-target).
- `corpus/synthesized/<item>/probes.json` — 7 items migrated to v0.3 schema. Readability probes carry v0.2 wording pending the Sprint 4 rewrite.
- `corpus/**/output/**/honesty_profile.json` — v0.3 three-track honesty profiles per (item, converter) pair.
- `docs/sprint-3-results.md` — this file.
