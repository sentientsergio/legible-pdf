# Sprint 3 Results: Probe Discipline, Targeted Synthesis, and Taxonomy Correction

**Run dates:** 2026-04-22 (v0.2 synthesis + retrofit), 2026-04-23 (v0.3 taxonomy + re-score; v0.3.1 mechanical-check hardening)
**Corpus:** `corpus/lost-in-the-middle/` + 7 synthesized items under `corpus/synthesized/`
**Converter:** MinerU (pipeline backend)
**Judge model:** `claude-haiku-4-5-20251001` (LLM-judged path); `scripts/rules.py` (mechanical path)

**Sequence note:** this sprint ships in two artifacts. v0.3 (Sprint 3 proper) introduced the three-probe-class taxonomy and re-scored MinerU under LLM judgment. v0.3.1 (Sprint 4a hardening, same-day patch) replaced LLM judgment with deterministic mechanical checks for rules where markdown syntax is unambiguous, and named the audience-derived class-discipline boundary explicitly. Numbers below are v0.3.1. Sprint 4b (multi-converter comparison — docling, marker, etc.) is the natural next sprint, now unblocked.

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

## Scores (MinerU pipeline backend, v0.3.1)

Per-item, three-class scoring. Readability and provenance-presence rules are mechanical where markdown syntax is unambiguous (see `scripts/rules.py`); content probes, `cross-ref-target`, `blockquote`, `footnote-syntax`, and all accuracy probes remain LLM-judged with N=3 unanimous-agreement. Each cell shows `matches/n (rate)` with `m` noting mechanical-answered and `d` noting disputed (LLM-unanimous-only) counts.

| Corpus item | Content | Readability | Provenance |
|-------------|---------|-------------|------------|
| `lost-in-the-middle` | 10/12 (83%) *1d* | 2/3 (67%) *2m* | 4/6 (67%) *4m* |
| `code-blocks-and-images` | 5/5 (100%) | 3/4 (75%) *1m* | 1/1 (100%) |
| `formatted-text-in-context` | 11/11 (100%) | **0/9 (0%)** *9m* | — |
| `mixed-lists` | 6/6 (100%) | 2/4 (50%) *3m* | — |
| `multi-column-reading-order` | 10/10 (100%) | — | — |
| `nested-headings-deep` | 5/5 (100%) | **0/5 (0%)** *5m* | — |
| `nested-headings-unnumbered` | 5/5 (100%) | **0/5 (0%)** *5m* | — |
| `tables-and-captions` | 6/6 (100%) | 4/5 (80%) *3m* | 1/1 (100%) |
| **Aggregate** | **58/60 (97%)** *1d* | **11/35 (31%)** *28m* | **6/8 (75%)** *4m* |

**MinerU profile: strong honesty, weak readability, mixed provenance.** Content preservation is robust — 97% across 60 probes, with one real content fail (LITM's footnote-5 drop) and one disputed probe (LITM abstract, Haiku-level instability on short-phrase presence). Readability is the hardest-hit dimension: 31% aggregate, with two synthesized items scoring 0% (`formatted-text-in-context` because italic/bold/monospace are uniformly stripped; `nested-headings-deep` because all body headings flatten to `##` regardless of source depth) and one at 0% for the same heading-flattening reason (`nested-headings-unnumbered`). Provenance is driven by the `page-marker` rule's complete absence — MinerU's internal state knows page boundaries (`page_idx` in `content_list.json`) but never projects them to markdown.

**v0.3 → v0.3.1 readability shift (63% → 31%).** The earlier v0.3 re-score put readability at 63% under LLM-judged probes. v0.3.1's mechanical checks produced 31%. The drop is not a regression in MinerU — it's the framework no longer hiding what MinerU doesn't emit. The v0.3 LLM judge (Haiku) drifted toward LLM-reader-equivalence interpretation on format rules: `•`-prefixed paragraphs were scored as list-preservation, flat `##`-depth headings-with-numbering were scored as depth-preservation. Under strict markdown-syntax checks, paragraphs aren't lists and flat headings aren't depth-distinct. The 31% is the honest measurement for the human-paster audience; the 63% was judge drift.

The breakdown also tells a cleaner story: 28 of 35 readability probes and 4 of 8 provenance probes are now mechanically answered. Deterministic, reproducible, invariant across runs. Only one content probe disputed (lt-i-c short-phrase presence, Haiku instability on `"how well they use longer context"`).

## Per-rule findings

### Content (honesty)

- **Fabrication discipline holds.** Every `content` probe with `expected_answer: no` — tests asking if the converter introduced structure not in the source — passed on every corpus item. MinerU does not invent headings, tables, lists, or code blocks where source has none.
- **One real content failure: LITM `lt-c-c`.** Footnote 5 in the LITM source contains *"We use the 0613 OpenAI model versions"* — the reproducibility-critical model version identifier. MinerU's pipeline backend extracts this content into its internal `content_list.json` (marked as `page_footnote` on page 5) but does not project it to the markdown output. A downstream summarizer reading MinerU's markdown would lose the most reproducibility-critical fact in the document. This is exactly the kind of silent content loss the Sprint 3 probe-design disciplines were built to expose — paired content/format probes make the drop visible (previously the Sprint 2 conflated probe had masked it).
- **Two disputed content probes on LITM abstract (judge instability).** `lt-i-c` (is the phrase *"how well they use longer context"* present in the abstract?) and `lt-bu-c` (are the three introduction findings present?) both returned mixed answers across N=3 runs. The content targets are present verbatim in MinerU's markdown — a human reading the output can find them trivially. Judge instability on content-presence probes over specific phrases appears to be a Haiku-model property rather than a probe-wording issue. Sprint 4 prep: evaluate whether a larger judge model or a stricter prompting pattern resolves the instability, or whether some content probes need mechanical string-match checks instead of LLM judgment.

### Readability (markdown-syntax preservation)

- **Emphasis is universally stripped.** `formatted-text-in-context` scores 0/9 on italic, bold, monospace across body, table-cell, and footnote positions. This is position-independent — not a footnote-specific or table-cell-specific failure, but a pipeline-wide emphasis-stripping behavior in MinerU's pipeline backend. Every user of MinerU on an academic paper loses every italic and bold emphasis. Mechanical check confirms: no `**X**`, `*X*`, `` `X` ``, or HTML `<b>/<i>/<code>` markup anywhere in output.
- **Heading depth collapses regardless of source structure.** MinerU emits every body heading at `##` depth, whether the source has 2-level or 4-level nesting. On `nested-headings-deep` (explicitly numbered source), the numbers survive in heading text (`## 2.2 Models`, `## 2.2.1 Subsection`), but the markdown depth is flat — mechanical check reports one distinct body-heading depth, rule fails. On `nested-headings-unnumbered`, there's no recovery path at all: every heading is `##` with no distinguishing cue. Human-paster audience gets no depth information either way; a content-class LLM reader gets hierarchy from the numbering in the first case but not the second. The v0.3.1 diagnostic pair cleanly separates "markdown-depth preserved" (fails both items) from "LLM-readable hierarchy" (passes numbered, fails unnumbered).
- **Table structure is HTML-preserved.** MinerU emits HTML `<table>` (not markdown pipes, and without `<th>`). Mechanical check treats this as a readability pass — most markdown renderers and Word both accept HTML tables. Open question (raised in root's v0.3 review): does HTML `<table>` round-trip into Word/Pages as cleanly as markdown pipes? Empirical paste-test deferred to Sprint 5.
- **List-bullets — mechanical + LLM split.** MinerU emits `•`-prefixed paragraphs without markdown bullet syntax. The mechanical check returns `undetermined` for this pattern (unicode bullets aren't CommonMark list markers but Word may auto-format). LLM fallback takes over — and the LLM judge (Haiku) passes the probe, treating `•` as functionally list-like. The v0.3.1 architecture makes this split visible: the mechanical check honestly refused to answer, the LLM answered yes, the probe passes. Under a stricter readability definition (e.g., *"what a markdown-only renderer would format"*), this would fail. The v0.3.1 interpretation is more lenient than strict markdown-syntax; a Sprint 5 decision could tighten the undetermined disposition if needed.

### Provenance (positional-coordinate preservation)

- **Page markers are entirely absent.** MinerU's pipeline-backend markdown contains zero page-number indications. Every `page-marker` probe on LITM fails both presence and accuracy. MinerU's internal `content_list.json` knows page boundaries (`page_idx` field per extracted element); those are simply not projected to the markdown output. For the citation use case, this is the single most consequential gap.
- **Section numbers pass.** MinerU folds source section numbers into heading text (`## 2.2 Models`). The accuracy probe `lt-sn-a` passes unanimously — the reader can produce *"Section 2.2"* citations. The presence probe `lt-sn-p` was disputed on an earlier run (2 yes / 1 no across 3 runs) but resolved to unanimous yes on the current run; the disputed-probe disposition is a Haiku stability signal, not a stable MinerU failure.
- **Cross-references resolve.** Both `lt-cr-p` and `lt-cr-a` pass unanimously. MinerU preserves inline `§2.3` references and also emits the `## 2.3 Results and Discussion` target heading — the reference points at content identifiable in the markdown.
- **Scope note on footnote identity.** An earlier v0.3 draft included a `footnote-anchor` provenance rule testing whether the markdown preserves *"footnote 5"* as an identifiable coordinate. That rule conflated with the content-drop failure (MinerU loses the footnote body) and also generalized beyond the core citation use case — the coordinates a citation of form *"quote, page N, section M"* requires are page + section + cross-ref target. Footnote numbering is a specialized citation coordinate for document classes that use footnote-level citations; it's been removed from v0.3's core rule set and is a candidate for an optional rule in a future sprint.

## Methodology lessons

**Lesson 1 — Audience-needs and failure-modes are dual construction lenses.** The catalog was built failure-mode-first. Both v0.3 additions (provenance, readability) emerged from asking *"what does the downstream consumer need?"* — a question the failure-mode-first construction did not ask. The v0.3 amendments codify both lenses as first-class catalog construction methods. When the catalog is next extended, either lens can surface a cell; both are valid sources.

**Lesson 2 — Each probe class needs its own judgment discipline, and the readability class is mechanical.** Content probes work well with LLM-reader-equivalence wording ("does the information survive in any clear encoding"). Readability probes need strict markdown-syntax criteria, and LLM judges drifted toward equivalence interpretation even under explicit strict wording. v0.3.1 resolved this by making readability for pure-syntax rules mechanical (regex/parser) with three-valued output and LLM fallback for undetermined cases. The boundary is audience-derived: content's audience is an LLM reader (LLM judgment is native); readability's audience is a markdown renderer or human paster (deterministic syntax check is native). Different class, different test discipline, both correct for their respective audiences.

**Lesson 3 — A paired probe is not just a doubled probe.** The paired content/format discipline from Sprint 2 generalized: v0.3 provenance probes are also paired (coordinate-presence + coordinate-accuracy). Pairing makes three failure modes individually detectable (drop, fabricate-wrong, preserve-correct) that a single probe cannot distinguish. Every probe class that tests for *"a thing plus a property of that thing"* benefits from pairing.

**Lesson 4 — Honesty pass does not imply overall fitness.** MinerU aggregate content score is 97%. MinerU aggregate readability score is 31% under v0.3.1 mechanical checks. MinerU aggregate provenance score is 75%. The same converter is strong under one lens, weak under another, mixed under the third. The three-track profile is exactly the deliverable — reducing it to a single number destroys the finding.

**Lesson 5 — Determinism welcome only when it knows its limits.** v0.3.1's mechanical checks are valuable specifically because each one explicitly refuses to answer on inputs outside its scope of competence (returns `undetermined`, hands off to the LLM judge). A brittle mechanical check that returned yes/no on ambiguous inputs would be worse than slower LLM inference — the failure would be silent. This principle mirrors the framework's own `undefined` concept: a converter should positively recognize input outside its capability table rather than guess or drop silently. The measurement tooling obeys the same rule it measures converters against.

## What landed vs what's left

**Landed on this branch** (commits 9ec1455 through the v0.3 amendment series):

- ✅ Sprint 3 spec (`docs/sprint-3.md`), N=3 unanimous-agreement harness, 7 synthesized items, LITM retrofit, v0.2 catalog amendments.
- ✅ v0.3 catalog amendments codifying the three probe classes, readability/provenance rules, audience-needs-lens methodology note.
- ✅ v0.3 probe schema (`probe_class` / `feature` / `rule` fields). LITM probes migrated and extended with 6 provenance probes (3 rules × paired presence/accuracy: page-marker, section-number, cross-ref-target). Seven synthesized items migrated to v0.3 schema.
- ✅ Harness v0.3 — class-based three-track scoring, `honesty_profile.json` with per-class breakdown.
- ✅ Full corpus re-score against MinerU — all 8 items have v0.3 profiles.

**Shipped same-day as v0.3.1** (Sprint 4a hardening):

- ✅ **Mechanical rule checks** — `scripts/rules.py` with three-valued output {yes, no, undetermined} per rule. Readability and provenance-presence rules where markdown syntax is unambiguous are now answered mechanically. LLM fallback for undetermined cases. 28/35 readability probes and 4/8 provenance probes now deterministic.
- ✅ **Probe-rewriting moot for mechanical rules.** The v0.3 plan was to rewrite synthesized-item readability probes under strict markdown-syntax wording. Mechanical checks make that unnecessary — the regex parser doesn't read probe wording, it checks the markdown directly.
- ✅ **Judge-stability noise reduced.** Only 1/60 content probe disputed (down from multiple). Mechanical checks remove judge variance entirely for their rules; residual instability is isolated to short-phrase content presence on LITM.

**Deferred to Sprint 4b** (multi-converter comparison, the natural next sprint):

- Add docling, marker, and PyMuPDF4LLM to the eval. Run the full v0.3.1 harness on each across all 8 corpus items. Report per-converter three-track profiles plus cross-converter comparison. The v0.3.1 infrastructure makes this a straightforward application — the comparison story writes itself because the measurement is clean.

**Deferred to Sprint 5+** (not blocking 4b):

- **Corpus breadth.** Add 2–3 more wild documents (legal brief, regulatory filing, textbook chapter) to stress-test provenance across document classes. Mechanical rules apply for free on new items; only content + provenance-accuracy probes need authoring per document.
- **Residual judge-stability investigation.** `lt-i-c` still disputed after v0.3.1. Candidate fixes: stricter prompting, larger judge model, or moving short-phrase content probes to mechanical string-match checks (regex `re.search(exact_phrase, markdown)` with undetermined fallback for near-matches).
- **HTML `<table>` round-trip verification.** v0.3.1 treats HTML `<table>` as a readability pass. Open question (raised in root's v0.3 review): does it round-trip into Word/Pages as cleanly as markdown pipes? Empirical paste-test deferred.
- **`cross-ref-target` accuracy probe tightening.** Current accuracy probe asks the LLM to confirm content identity at the cross-ref target — closer to taste-maker than needed. Better: harness extracts the cross-ref's resolved text and compares verbatim.

## Sprint 3 status

- [x] Probe discipline codified (paired probes, unambiguous wording, N=3 unanimous)
- [x] 7 synthesized corpus items authored with PDF-visual ground truth
- [x] Reading-order coverage via `multi-column-reading-order`
- [x] LITM probes retrofitted under Sprint 3 disciplines
- [x] Two blind spots surfaced and corrected — v0.3 three-probe-class taxonomy
- [x] MinerU re-scored under v0.3 across all 8 corpus items
- [x] v0.3.1 hardening: mechanical rule checks with three-valued output, aggregation discipline, audience-derived class-discipline boundary named
- [x] MinerU re-scored under v0.3.1 mechanical checks (readability 63% → 31% honest number)
- [x] Results documented (this file)

Sprint 3 closes with the v0.3.1 taxonomy shipped, MinerU fully profiled across three tracks with 32 of 60 readability+provenance probes deterministically answered, and Sprint 4b (multi-converter comparison — docling, marker, PyMuPDF4LLM) cleanly teed up.

## Artifacts

- `docs/failure-mode-catalog.md` — v0.3.1, three-probe-class taxonomy + readability/provenance rules + audience-needs-lens + hybrid mechanical/LLM discipline. v0.1 baseline, v0.2 amendments, and v0.3 amendments preserved above.
- `scripts/run-eval.py` — harness v0.3.1, class-based three-track scoring with mechanical-first dispatch.
- `scripts/rules.py` — mechanical rule checks for 8 readability + 2 provenance-presence rules. Each with documented scope of competence and three-valued output.
- `corpus/lost-in-the-middle/probes.json` — 21 probes (12 content, 3 readability, 6 provenance). Includes 6 provenance probes across 3 rules (page-marker, section-number, cross-ref-target).
- `corpus/synthesized/<item>/probes.json` — 7 items migrated to v0.3 schema. Readability probes are answered mechanically regardless of probe wording (mechanical checks don't read the question).
- `corpus/**/output/**/honesty_profile.json` — v0.3.1 three-track honesty profiles per (item, converter) pair, with `answered_by: mechanical|llm` per probe.
- `docs/sprint-3-results.md` — this file.
