# PDF→Markdown Failure Mode Catalog

A catalog of known failure modes that PDF→Markdown converters exhibit. Each entry is the basis for one or more eval probes.

## Premise

For now, **markdown is both the working representation and the projection target** (richer IR remains forward aspiration — see [README.md](../README.md)). This catalog therefore inventories failures *at the markdown ceiling* — the limit of fidelity any honest converter could achieve when its output target is markdown. Failures that involve preserving content markdown structurally cannot express (precise font kerning, page-relative layout, native color metadata in body text) are out of scope here; they belong to a future IR-targeted catalog.

## Taxonomy

Two layers, exhaustive by construction:

**Layer 0 — Foundation.** Text content and reading order. Without these, nothing downstream measures coherently.

**Layer 1 — Per markdown feature, four failure modes:**
- **Correctly used** — feature applied accurately to a source structure that warrants it
- **Incorrectly used** — feature applied but to the wrong source structure (or with wrong parameters: heading at wrong level, code with wrong language tag, table with wrong column headers)
- **Hallucinated** — feature applied where source has no structure warranting it
- **Missed** — source warrants the feature but converter doesn't apply it (silently produces body text, drops content, or substitutes a less-specific feature)

The probe space is `features × 4 modes` slots. Coverage of cells is a measurable property of any probe set.

This taxonomy maps to the three eval probe types defined in [README.md](../README.md):
- **Capture probe** ↔ tests "correctly used" (positive test) and surfaces "missed" (when the answer should be yes but is no)
- **Hallucination probe** ↔ tests "hallucinated" (the converter introduced markup for content that wasn't there)
- **Definedness probe** ↔ tests "missed with explicit `undefined` marker" vs missed silently
- "Incorrectly used" is its own probe shape: *"Is X correctly identified AS feature M (not as feature N)?"* — tests misclassification

## Source key

Throughout: `[SOTA]` = `frompdf/research/pdf-to-markdown-sota.md` (April 2026 deep research). Other sources cited inline.

---

## Layer 0: Foundation

**Whitespace invariance (payload).** Layer 0 measurements are whitespace-invariant for content payload. Probes phrased as *"does X appear in the document?"* or *"does X appear before Y in reading order?"* are invariant by design — the LLM functional reader doesn't experience extra blank lines or paragraph-break choices as meaningful. Penalizing a converter for reflowing prose differently than the source would measure stylistic taste, not honesty. (Whitespace as part of markdown markup is structural — see Layer 1 preamble.)

**Ground truth vs functional reading.** Probes are derived from human reading the source PDF (axiom-layer ground truth, incontestable by inspection). The eval measures by giving an LLM the converter's markdown output and asking the same probes; if the LLM's answers match the human-derived ground truth, the conversion was honest. **Human-as-ground-truth, LLM-as-functional-reader.**

### Text preservation

The converter's output should contain the source PDF's text content, accurately and completely, modulo what markdown can express.

**Observed failures:**
- **Font encoding garbling.** Docling produces unreadable output on non-standard font encodings even with OCR fallback (issue #185). Subsetted/custom fonts produce GLYPH placeholders instead of readable text (issue #2170). [SOTA]
- **Phantom spacing at font boundaries.** ML-based tools (MinerU, Marker, Docling) merge text into continuous strings and lose font-boundary information; transitions between proportional and monospace fonts cause inserted or dropped spaces. PyMuPDF preserves font boundaries explicitly. [SOTA]
- **OCR failure on rasterized PDFs.** PyMuPDF4LLM has no OCR capability and is useless on scanned documents. [SOTA]
- **Hallucinated text.** Nougat documented to produce hallucinated and repeating text. Marker documented to hallucinate image descriptions. [SOTA]

**Probe shape:** does a specific exact phrase appear in the markdown? Does the markdown contain content that is not in the source?

### Reading order preservation

The converter's output should present source content in the order a human reader would read it.

**Observed failures:**
- **Column interleaving in two-column layouts.** Bibliography sections and multi-column body text frequently interleave or split across what the converter interprets as separate paragraphs. [SOTA, OmniDocBench]
- **Bibliography wrap splits.** Multi-line references in two-column layouts get split across paragraphs or interleaved with adjacent column text. No tool gives bibliography sections special handling; GROBID is the specialist but doesn't produce general markdown. [SOTA]
- **Header/footer pollution.** Tools other than PyMuPDF4LLM may include headers/footers as body text, breaking reading flow. [SOTA]
- **Multi-page table breaks.** Tables spanning page boundaries are frequently broken into separate tables or split incorrectly.
- **Vertical text.** MinerU explicitly cannot process vertical text. [SOTA]
- **Complex layout failures.** MinerU's reading order can fail in extremely complex layouts. [SOTA]

**Probe shape:** does X appear before Y in the markdown? Is the bibliography presented as a single coherent section?

---

## Layer 1: Markdown features × 4 modes

**Markup whitespace is structural (pragma), not stylistic.** Markdown features are constituted by their markup syntax, which uses whitespace structurally: a heading needs `# ` (with the space after the hash), a list item needs `- `, a fenced code block needs newlines at fence boundaries. These structural whitespaces are part of the feature — get them wrong and the LLM doesn't see the feature either. The probe *"is X presented as a heading?"* doesn't care whether zero or three blank lines precede it, but it does care that the markup is correctly formed. **Pragma vs payload: structure-syntax whitespace is pragma; content-payload whitespace is invariant.**

### Heading (with level)

Markdown distinguishes heading levels via `#`, `##`, `###`, etc. The converter must (a) identify what is a heading, (b) determine its level, (c) emit the heading text correctly.

**Observed failures:**
- MinerU: only first-level headings supported; multi-level heading detection unreliable. [SOTA]
- Tools commonly downgrade subsections to body text or promote body emphasis to headings.

**4 modes for headings:**
- **Correctly used:** source heading at level N → markdown heading at level N with correct text
- **Incorrectly used:** source heading at level N → markdown heading at level M (N ≠ M); or heading text mangled
- **Hallucinated:** source body text or emphasized paragraph → marked as heading
- **Missed:** source heading → emitted as body text (heading hierarchy collapsed)

**Probe shapes:**
- "Is the text 'X' presented as a heading at level N?" (correctly used)
- "Are sections A and B at the same heading level?" (level distinction)
- "Does the document contain a section titled 'Y' presented as a heading?" (capture)
- "Is the line 'Z' a heading or body text?" (missed/hallucinated discrimination)

### Bullet list (unordered list)

Markdown represents bullet lists with `-`, `*`, or `+`. Converters must preserve list structure including item count and any nesting.

**Observed failures:**
- Lists frequently flattened to inline prose with bullet characters lost or interpreted as text
- Nesting flattened
- List type confusion (bullet ↔ numbered)

**4 modes:**
- **Correctly used:** source bullet list → markdown bullet list with correct item count and nesting
- **Incorrectly used:** rendered as numbered list, or wrong nesting depth, or items merged/split
- **Hallucinated:** source body text with leading dashes treated as list
- **Missed:** source bullet list → flat prose

**Probe shapes:**
- "Does location X contain a bulleted list?" (capture)
- "How many items does the list at location X contain?" (capture + count)
- "Is the list at X bulleted or numbered?" (correct type)

### Numbered list (ordered list)

Markdown uses `1.`, `2.`, `3.` etc. Same shape as bullet lists, with the additional property that numbering must be preserved or recomputable.

**4 modes:** as for bullet list, with additional concerns around number sequence preservation and list-restart behavior.

**Probe shapes:** as for bullet list, with type-discrimination probes.

### Code block (fenced)

Markdown uses ` ``` ` fences (optionally with a language tag) for code blocks. Converters must distinguish code from body prose.

**Observed failures:**
- **MinerU: code blocks "not yet supported"** in the layout model. Critical gap. [SOTA]
- Docling: code recognition listed as future work. [SOTA]
- Marker: detects via monospace font heuristics; fences with triple backticks. Works for obvious cases, fails on inline code, short snippets that look like variable names, code in proportional fonts. [SOTA]
- PyMuPDF4LLM: detects monospace spans but doesn't auto-fence as code. Code block language tag lost. [SOTA]

**4 modes:**
- **Correctly used:** source code block → fenced code block with correct content (and language tag if present)
- **Incorrectly used:** code block fenced with wrong language tag; code rendered as inline code instead of block; partial code block
- **Hallucinated:** non-code body text fenced as code (e.g., variable names, monospace-styled prose)
- **Missed:** source code block → emitted as body text or dropped

**Probe shapes:**
- "Does the document contain a fenced code block with X as its content?" (capture)
- "Is the language tag of the code block at X correctly identified as Y?" (correctly used vs incorrectly used)
- "Does the document contain any fenced code blocks?" (existence)

### Inline code (monospace span)

Markdown uses single backticks for inline code. Distinct from code blocks (block-level) and from body monospace styling.

**Observed failures:**
- ML tools merge inline monospace into body text and lose the inline-code distinction. [SOTA, by inference from font-boundary loss]
- Marker may over-fence proportional code as if it were monospace.

**4 modes:**
- **Correctly used:** source `\texttt{}` or monospace span → markdown inline code with backticks
- **Incorrectly used:** inline code rendered as block code, or with wrong content
- **Hallucinated:** body text rendered as inline code (e.g., short technical terms in non-monospace source)
- **Missed:** monospace inline span → flattened to body text

**Probe shapes:**
- "Is the term 'X' presented in monospace/typewriter font?" (capture)
- "Does any inline code appear in section Y?" (existence)

### Table

Markdown has limited table support (pipes and dashes). Complex tables don't fit. Converters must (a) recognize a table, (b) extract rows and columns, (c) preserve cell content, (d) distinguish header rows.

**Observed failures:**
- MinerU: complex table recognition has documented row/column errors. [SOTA]
- Docling: 97.9% cell accuracy on sustainability reports via TableFormer (best in class). [SOTA]
- Marker: complex nested tables and forms "may not work." [SOTA]
- Multi-page tables: frequently broken or split across boundaries.

**4 modes:**
- **Correctly used:** source table → markdown table with correct structure (rows, columns, headers, cell content)
- **Incorrectly used:** rows/columns merged or split; header row not distinguished; cell contents scrambled; wrong column count
- **Hallucinated:** body text with aligned columns rendered as table
- **Missed:** source table → flat text or dropped

**Probe shapes:**
- "Does the document contain a table with columns labeled A and B?" (capture + column structure)
- "What value is in the cell at row R, column C of the table comparing X?" (cell-level capture)
- "Does the document contain a table comparing inference latency?" (hallucination)
- "Is the first row of the table presented as a header row?" (correctly used vs incorrectly used)

### Bold emphasis

Markdown uses `**X**` or `__X__`. Inline-level structural markup.

**Observed failures:**
- ML tools merge text and lose font-flag information at span level. [SOTA, by inference]
- Bold and italic sometimes confused.

**4 modes:**
- **Correctly used:** source bold span → markdown bold
- **Incorrectly used:** bold rendered as italic or vice versa; wrong span boundaries
- **Hallucinated:** non-bold text rendered as bold
- **Missed:** bold span → plain text

**Probe shapes:**
- "Is the phrase 'X' presented in bold?" (capture)
- "Is any text in section Y bolded?" (existence)

### Italic emphasis

Markdown uses `*X*` or `_X_`. Same shape as bold.

**Observed failures:** as for bold; commonly confused with bold or lost entirely.

**4 modes:** as for bold (correctly used / incorrectly used / hallucinated / missed).

**Probe shapes:**
- "Is the word 'use' italicized in the abstract (in the phrase 'how well they use longer context')?" (capture)
- "Does the paper italicize the term Y in section Z?" (capture)

### Block quote

Markdown uses `>` prefix for block quotes. Converters must distinguish quoted/cited blocks from body prose.

**Observed failures:** generally lower priority for most converters; commonly missed.

**4 modes:** standard 4 modes.

**Probe shapes:** "Is text X presented as a block quote?"

### Link

Markdown uses `[text](url)` for links. Converters must preserve both anchor text and URL.

**Observed failures:** URL extraction varies; in-document references (cross-refs to figures, sections) may be lost.

**4 modes:**
- **Correctly used:** source link → markdown link with correct anchor text and URL
- **Incorrectly used:** wrong URL or wrong anchor text; cross-reference treated as external link
- **Hallucinated:** body text rendered as link (rare)
- **Missed:** link → plain text (URL dropped)

**Probe shapes:** "Does section X contain a link to URL Y?" "Is the text 'Z' a hyperlink?"

### Image

Markdown uses `![alt](url)` for images. PDFs embed images; converters must extract or reference them.

**Observed failures:**
- Marker: hallucinates image descriptions. [SOTA]
- Most tools: extract images as references but lose positioning/captions; alt text rarely populated meaningfully.

**4 modes:**
- **Correctly used:** source image → markdown image reference with placeholder or extracted alt text
- **Incorrectly used:** image referenced but placeholder/alt text wrong; positioned wrongly relative to caption
- **Hallucinated:** image description fabricated by LLM-assisted converter (Marker's documented failure mode)
- **Missed:** source image → dropped silently

**Probe shapes:** "Does the document reference an image at position X?" "Does the image at X have caption Y?"

### Page break

Markdown has no native page-break concept. Some conventions exist (`---` for horizontal rule). Page breaks are usually lost.

**Observed failures:** universally missed in markdown output. This is a markdown ceiling failure (markdown structurally can't preserve page-relative information well) and may be out of scope for measurement.

**Note:** included here for completeness; probably skipped in early eval rounds because no honest markdown converter can preserve page structure.

### Footnote

Markdown has limited footnote support (CommonMark doesn't include them; some flavors do via `[^1]`). Converters must handle inline reference and the footnote text.

**Observed failures:** footnote-to-body relationships poorly preserved; footnote text often inlined into body or appended without anchor.

**4 modes:** standard.

**Probe shapes:** "Does the body text at X have a footnote reference?" "Is footnote Y presented separately from body text?"

### Caption

Captions on figures and tables are not a markdown feature per se (they're typically body paragraphs near the figure/table). Whether they're correctly *associated* with their figure/table is the failure mode.

**Observed failures:** captions frequently misclassified as headings (caption-as-H3 is a documented misclassification across tools).

**4 modes:**
- **Correctly used:** caption presented as text near its figure/table reference
- **Incorrectly used:** caption rendered as H3 heading (common misclassification); caption associated with wrong figure
- **Hallucinated:** body paragraph treated as caption
- **Missed:** caption text dropped or merged into body without identification

**Probe shapes:** "Is the text 'Figure 1: ...' presented as a heading or as caption text?" (the misclassification probe)

---

## Out of scope for the markdown ceiling

These failure modes exist but cannot be measured against any honest markdown converter (markdown structurally can't express the source signal):

- **Text color preservation.** No markdown native syntax. Diff highlighting (green/red) is universally lost. *Fix path:* HTML-in-markdown escape hatch, or IR-layer feature.
- **Font metadata** (font name, size, color in body text). No markdown native syntax.
- **Page-relative positioning.** Markdown is a flow format.
- **Multi-column layout structure.** Reading order can be preserved; column structure cannot.

These move into scope when the eval extends to a richer IR (`legible-ir`).

---

## Coverage and probe instantiation

For each Layer 1 feature, an exhaustive probe set would author all 4 modes. In practice, probe sets sample cells; coverage is reported as fraction of cells with at least one probe.

**Coverage strategy: wild + synthetic corpus.** The wild corpus (real PDFs people encounter) measures real-world honesty but has irregular coverage of failure-mode cells — a typical academic paper will exercise heading hierarchy and inline emphasis but may have no code blocks or block quotes, leaving those cells untestable on that document. To complete coverage, a **synthetic corpus** — PDFs deliberately authored in Word, LaTeX, Pages, or other tools to instantiate specific (feature, mode) cells — provides known-ground-truth documents that exercise underrepresented cells. Wild + synthetic together are complete in a way neither alone is. The wild corpus measures honesty in the real distribution; the synthetic corpus guarantees no failure mode goes unmeasured.

For Sprint 2 (the v0.0 smoke run on Lost in the Middle), we author ~10 probes covering high-value cells:
- Heading: missed and correctly used
- Bullet list: correctly used (with item count)
- Code block: hallucinated (paper has no code blocks; converter shouldn't introduce any)
- Table: correctly used (cell-level capture)
- Italic: correctly used
- And mirrored hallucination probes for each

Source observations beyond `frompdf/research/pdf-to-markdown-sota.md` (paperlint April 16 hardening, tomd evaluation April 13–17, OmniDocBench published taxonomy) will be folded in as the catalog matures.

---

## Sprint 3 amendments (2026-04-22)

Three substantive additions from the Sprint 3 synthesized corpus and discipline pass.

### 1. LLM-reader-equivalence is the honesty test

**Honesty is whether a downstream LLM reader can recover the source's information from the converted markdown.** It is *not* whether the markdown would satisfy a markdown linter. Structurally weak markdown — bullet characters stripped, code-block fences missing, blockquote `>` markers absent — is an honesty pass if the LLM reads it correctly. The methodology measures functional reading, not surface fidelity.

A separate axis ("structural fidelity for downstream markdown tooling") could be defined for projects that need it: lost code-block fences impact syntax-highlighting renderers, lost `<th>` impacts CSS and screen-readers, lost code indentation breaks copy-paste-to-REPL. These are real concerns, but they are not honesty failures by this catalog. They belong to a distinct measurement axis if and when one is added.

### 2. Probe-design disciplines

Sprint 2 surfaced three probe-design failure modes. Sprint 3 codifies the disciplines:

- **Paired content/format probes.** A combined probe ("is X presented as a heading?") cannot distinguish "the converter dropped the content" from "the converter kept the content but lost the format." Always author one content-presence probe (does the token/phrase appear?) and one format-preservation probe (is it presented with the structural cue?). Without the split, real content loss can hide behind a "no" hallucination probe that vacuously passes.

- **"Any clear signal" wording.** Format probes should accept any encoding that a downstream LLM reader could recognize as the structure: markdown syntax, prefix characters (`•`, `–`, `1.`), HTML tags, depth or indentation, numerical hierarchy (`2.1`, `2.1.1`), term/definition adjacency, etc. Narrow probes (e.g., "is X at deeper markdown depth than Y") miss honest preservation via numbering or other channels and produce false negatives.

- **N=3 unanimous-agreement scoring.** Each probe is run three times; a probe matches only if all three runs agree *and* the agreed answer matches expected. Disputed probes (runs disagree) are tracked separately as a probe-quality signal — they reveal probe ambiguity or judge instability rather than converter failure. Implemented in `scripts/run-eval.py`.

### 3. MinerU pipeline-backend observations (per feature)

Empirical findings from running MinerU (`-b pipeline`) on the Sprint 3 synthesized corpus and on Lost in the Middle:

| Feature | Observation |
|---------|-------------|
| Title | Emitted as `# Title` h1. |
| Headings | Section number folded into heading text (e.g., `## 2.1 Models`). Depth correctly preserved when source carries explicit numbering. **Depth collapses to flat when source uses unnumbered headings** — diagnostic pair `nested-headings-deep` (numbered) vs `nested-headings-unnumbered` (no numbering) shows clear before/after. |
| Bulleted list (itemize) | Bullet characters stripped. Items emitted as leading-space-prefixed siblings on separate paragraphs. |
| Numbered list (enumerate) | Cleanly preserved as `1. X` / `2. Y` / `3. Z`. |
| Nested list | Top-level bullets stripped; sub-items emit em-dash prefix (`– X`). Indentation flat. |
| Definition list | `\item[Term] description` becomes `Term description...` on a single line. Term-bold lost; term/definition adjacency preserved. |
| Table | Emitted as HTML `<table>` with `<tr>`/`<td>` (not markdown pipes; no `<th>`; no header separator row). Cell content preserved verbatim. |
| Caption | Preserved on its own line as `Table N: ...` / `Figure N: ...`, positioned above (table) or below (figure) the block. |
| Cross-reference | `\ref{}` resolves to `Table N` / `Figure N` in body text *only if the source PDF was rendered with `.aux` preserved across two pdflatex passes*. If `.aux` is missing the references emit as `Table ??`. |
| Image | Proper markdown `![](images/<sha256>.jpg)`. PNGs re-encoded as JPG with content-hash filename. |
| Code block (verbatim) | Indentation destroyed; no fence markers; no monospace markup. Lines emitted as flush-left text with trailing two-space soft-break markers. |
| Blockquote (quote) | No `>` prefix; no indentation; no italics. Structurally indistinguishable from prose; only attribution-adjacency carries the quotation signal. |
| Italic / Bold / Monospace | **Stripped uniformly across all three positions tested (body, table cell, footnote).** Verified by `formatted-text-in-context` corpus item: 9/9 format probes failed, 9/9 content-presence probes passed. The strip is position-independent — not a footnote-specific or table-cell-specific failure. |
| Footnotes | **Footnote bodies dropped entirely.** Lost in the Middle's footnote 5 ("We use the 0613 OpenAI model versions") is absent from MinerU's markdown. Inline footnote markers in body text are preserved but the footnote contents do not appear anywhere in the output. |
| Inline math | `$expr$` becomes plain text (e.g., `$Z = 1$` → `Z = 1`). Value preserved, math markup lost. Numerical Unicode minus sign (U+2212) sometimes used in place of ASCII hyphen. |

These observations are MinerU-specific. Other converters (Marker, Docling, PyMuPDF4LLM) are expected to differ; cross-converter measurement is a future sprint.

---

_v0.2, 2026-04-22. Sprint 3 amendments add LLM-reader-equivalence framing, probe-design disciplines, and MinerU per-feature observations. v0.1 baseline preserved above; new findings appended rather than rewritten._

---

## v0.3 amendments (2026-04-23)

Sprint 3 surfaced two blind spots after the probes had shipped: **provenance** (the LLM-analyst citing sources) and **readability** (the human previewing converted markdown). Both trace to a single methodological miss — the catalog was built failure-mode-first ("what converters get wrong") rather than also requirement-first ("what downstream consumers need"). v0.3 formalizes the correction as three probe classes plus a methodological lens.

### 1. The three probe classes

A converter has three audiences, and the catalog must test each one:

| Class | Audience | What it measures | Primary question form |
|-------|----------|------------------|-----------------------|
| **content** | Downstream LLM-reader | Honesty. Content preserved; nothing fabricated. | *"Does X appear?"* / *"Does Y appear (when source has no Y)?"* |
| **readability** | Human previewing / pasting into Word | Formatting signals a human needs to restore the doc without manual re-structuring. | *"Is X rendered with the expected markdown structure?"* |
| **provenance** | LLM-analyst producing verifiable citations | Positional coordinates a human can use to verify a quote in the source PDF. | Paired: *"Is any page indicated for X?"* + *"Is X on page N?"* |

All three share one discipline: rule-based, binary per probe, ground-truthable from PDF-visual inspection, LLM-reader-equivalence judged, N=3 unanimous-agreement required. **No judge-as-taste-maker anywhere in the framework.**

The v0.2 amendment's "LLM-reader-equivalence is the honesty test" statement still stands — now scoped correctly. LLM-reader-equivalence defines the **content** class (the honesty test). Readability and provenance are additional scored dimensions, non-zero, reported independently. A converter that passes content but fails readability is honest-but-tedious; one that passes content but fails provenance is honest-but-uncitable. Both failures matter.

**Relationship to v0.1 Taxonomy → probe types mapping.** The original three probe types (capture / hallucination / definedness) fold as follows: capture + hallucination subsume into `content`; definedness is an orthogonal property all three classes can carry (an honest converter says what it can't do, regardless of class). `readability` and `provenance` are new.

### 2. Content probes

Content probes test what the v0.1 + v0.2 catalog already describes. Every Layer 0 probe (text preservation, reading order) is a content probe. Every Layer 1 feature's "correctly used / hallucinated / missed" cells produce content probes (capture-polarity or fabrication-polarity). Nothing in the existing catalog changes — it is re-labeled.

**Representative questions** (drawn from `corpus/lost-in-the-middle/probes.json`):
- *"Does the document contain a section whose title is 'Models'?"* (presence, expected `yes`)
- *"Does the document mention the OpenAI model version identifier '0613'?"* (presence, expected `yes`; MinerU fails this — footnote body silently dropped)
- *"Does the abstract present contributions as an explicitly numbered list?"* (absence, expected `no`)

### 3. Readability probes

Readability probes test whether a human pasting the converted markdown into Word/Pages can work with the output without re-structuring it by hand. Each probe tests one rule. Each rule maps to a Layer 1 feature in the v0.1 catalog.

**v0.3 readability rules (initial set):**

| Rule | PDF source signal | Markdown expected | Violation cost |
|------|-------------------|-------------------|----------------|
| `heading-depth` | Heading levels H1/H2/H3 | Matching depth via `#` / `##` / `###` | Re-level every heading in the doc |
| `list-bullets` | Bulleted list | `-` / `*` / `+` prefix per item | Re-prefix every item |
| `list-numbers` | Numbered list | `1.` / `2.` / `3.` prefix | Re-number every item |
| `table-structure` | Table | MD pipes (`|...|`) or HTML `<table>` | Rebuild the cell grid |
| `code-fence` | Verbatim code block | Fenced ```` ``` ```` or indented | Re-fence, restore monospace |
| `emphasis-bold` | Bold span | `**X**` | Re-bold each span |
| `emphasis-italic` | Italic span | `*X*` / `_X_` | Re-italicize each span |
| `emphasis-mono` | Monospace/typewriter span | `` `X` `` | Re-mark each span as code |
| `blockquote` | Quoted block | `>` prefix per line | Re-prefix every line |
| `footnote-syntax` | Footnote body | Footnote syntax or anchored form | Re-attach footnote to body reference |

**Severity model (v0.3 baseline):** one probe per rule per document. Binary pass/fail per rule. Readability score = fraction of rules passed. Per-instance granularity ("fails 28 of 30 heading instances") is deferrable to a later version if the rule-level signal proves insufficient.

**Relationship to existing Layer 1 probes:** Sprint 3 already authored format-preservation probes for most of these rules (heading, bulleted_list, table, italic, bold, monospace, code_block). Those probes re-classify from `capture` kind to `readability` class with no question changes. New readability probes required: `code-fence` (absent from LITM), `blockquote`, `footnote-syntax`.

### 4. Provenance probes

Provenance probes test whether a human reader, given an LLM-analyst's citation *("`exact quote`, page N, section M")*, can take that citation back to the source PDF and verify it. For this to work, the converter's output must preserve **positional coordinates** (page boundaries, section numbers, cross-reference targets) that a downstream LLM can cite from.

Provenance probes are **paired** — same discipline as content/format pairing from v0.2:

1. **Coordinate-presence probe:** does the markdown carry any indication of this coordinate? (Is any page number indicated for quote X? Is any section number indicated for heading Y?)
2. **Coordinate-accuracy probe:** if a coordinate is indicated, is it the correct one? (Is quote X on page 5? Is heading Y numbered 5.2.3?)

A converter that drops page markers fails the presence probe. A converter that fabricates wrong page markers passes presence, fails accuracy. A converter that preserves correct markers passes both.

**v0.3 provenance rules (initial set):**

| Rule | PDF source signal | Markdown expected | Paired probe shape |
|------|-------------------|-------------------|---------------------|
| `page-marker` | PDF pagination | Page delimiters in any form the LLM can read (`--- Page N ---`, HTML comments, etc.) | *"Any page indicated for X?"* + *"Is X on page N?"* |
| `section-number` | Numbered heading ("5.2.3 Models") | Number preserved in the heading text | *"Any section number for 'Models'?"* + *"Is it '5.2.3'?"* |
| `cross-ref-target` | "see Section 3" inline reference | Target resolvable from markdown | *"Does 'see Section 3' point to identifiable content?"* + *"Is that content the Section 3 heading and body?"* |

**Scope note.** Provenance rules target the coordinates a citation of form *"`exact quote`, page N, section M"* requires the converter's output to carry. Other coordinate types — footnote numbers, paragraph/line numbers, figure/table numbers — are useful in specific document classes but not load-bearing for the general citation case; they are out of scope for v0.3 and may be added as optional rules if a document class warrants them.

**MinerU observation (v0.3 preview):** current pipeline-backend output contains no page markers; section numbers are folded into heading text (provenance pass); cross-references resolve when both the inline `§2.3` tokens and the `## 2.3` target headings are preserved. Page-marker absence drives provenance score down — that finding is the point.

### 5. Scoring model

Three scores per converter per corpus item, reported independently. No composite.

```json
{
  "honesty_profile": {
    "content":     { "n": 10, "matches": 9, "rate": 0.90, "disputed": 0 },
    "readability": { "n":  8, "matches": 2, "rate": 0.25, "disputed": 0 },
    "provenance":  { "n":  4, "matches": 0, "rate": 0.00, "disputed": 0 }
  }
}
```

Each converter gets a profile like *"strong honesty, weak readability, zero provenance."* That is the finding — not a percentage gold medal.

### 6. Probe schema v0.3

```json
{
  "id": "lt-h-f",
  "probe_class": "readability",
  "feature": "heading",
  "rule": "heading-depth",
  "question": "...",
  "expected_answer": "yes" | "no",
  "ground_truth_basis": "..."
}
```

`probe_class` is the new primary field (`content` | `readability` | `provenance`). The v0.2 `kind` (capture/hallucination) and `mode` (correctly_used/hallucinated) fields retire — their semantics fold into `probe_class: content` with polarity carried by `expected_answer`. Readability probes carry a `rule` pointer; provenance probes carry a `rule` pointer and come in presence/accuracy pairs.

### 7. The audience-needs lens

**Methodological correction.** The v0.1 catalog was built by reading SOTA research and cataloging *"what converters get wrong."* That lens is necessary but not sufficient — it misses requirements that the downstream consumer needs but that no converter happens to emit at all. Page markers are the canonical example: no converter *gets them wrong* because no converter emits them; the absence is invisible to a failure-mode-first lens. Readability is another example: an entire class of structural signals (bullets, fences, emphasis) was cataloged as format-preservation but not scored because LLM-reader-equivalence alone justified skipping them.

**Rule:** the catalog is indexed by *two* lenses, not one:
- **Failure-modes** — what converters get wrong when they try (the v0.1 construction method)
- **Audience-needs** — what the three consumer audiences (LLM-reader, human-previewer, LLM-analyst) require the output to carry

A cell appears in the catalog if either lens surfaces it. A probe class exists for each audience. v0.3 closes the audience-needs gap for the three audiences known today; future audiences (accessibility-assistive-reader? structured-data-pipeline?) may surface additional probe classes.

### 8. Migration notes

Existing Sprint 3 probes on `corpus/lost-in-the-middle/probes.json` and each `corpus/synthesized/<item>/probes.json` migrate by re-labeling:

| Old (v0.2) | New (v0.3) |
|------------|------------|
| `kind: capture`, `feature: content_presence`, expected `yes` | `probe_class: content`, `expected_answer: yes` |
| `kind: capture`, `feature: <actual>`, expected `yes` | `probe_class: readability`, `rule: <matching rule>` |
| `kind: hallucination`, expected `no` | `probe_class: content`, `expected_answer: no` |

New probes to author: provenance probes per corpus item where applicable. LITM is the strongest testbed (real pagination, sections, cross-refs, footnotes). Among synthesized items, `tables-and-captions` has cross-references, `nested-headings-deep` has section numbers — those get provenance probes too.

---

_v0.3, 2026-04-23. Three-probe-class taxonomy (content / readability / provenance), each rule-based and ground-truthable. Audience-needs lens codified alongside failure-modes lens. v0.1 baseline and v0.2 amendments preserved above._

---

## v0.3.1 amendments (2026-04-23, same day)

v0.3 introduced the three-probe-class taxonomy but left all probes LLM-judged. Running the re-score surfaced three consequences that v0.3.1 addresses:

- **Judge-interpretation drift.** Even under strict readability probe wording, the LLM judge (Haiku) drifted toward LLM-reader-equivalence interpretation on rules like `list-bullets` — it treated `•`-prefixed paragraphs as list-equivalent despite explicit CommonMark-syntax probe wording. Scoring noise, not a real pass.
- **Per-document probe authoring cost.** Every readability probe on every corpus item needed to be authored and rewritten when the discipline tightened. For pure-syntax rules this is expensive scaffolding around what is structurally a deterministic pattern-match.
- **Class-discipline boundary was implicit.** v0.3 didn't clearly articulate *why* readability probes use strict syntax while content probes use "any clear signal." The boundary is audience-derived and should be named explicitly.

v0.3.1 adds a hybrid mechanical + LLM approach for rules where mechanical pattern-matching is honest. The principle: **determinism is welcome only when it knows its limits.**

### 1. Hybrid three-valued mechanical checks

Each mechanical rule check returns one of **{yes, no, undetermined}**:

- **Yes / no** — rule clearly satisfied or violated; answer is deterministic and authoritative.
- **Undetermined** — input at the edge of the rule's scope of competence (e.g., `•`-prefixed paragraphs that are neither markdown bullets nor definitely-not-a-list). The check explicitly refuses to answer.

Undetermined cases escalate to the LLM judge (N=3 unanimous-agreement) using the probe question. The two paths are both first-class: mechanical handles the clear pattern-matches, LLM handles the semantic edges.

The *refuse to answer* output is load-bearing. A brittle check that returns yes/no on inputs outside its competence is worse than slower LLM inference because the failure is silent. This mirrors the framework's own `undefined` concept — a converter should positively recognize input outside its capability table rather than guess or drop silently. The measurement tooling obeys the principle it measures converters against.

Implementation: `scripts/rules.py` — one function per rule, each with documented scope of competence. `scripts/run-eval.py` dispatches mechanical-first, LLM-fallback-for-undetermined. Each probe result carries `answered_by: "mechanical" | "llm"` so the honesty profile is transparent about which path decided each answer.

### 2. Mechanical rule scope (v0.3.1 initial set)

Pure-syntax rules where markdown markup is unambiguous:

| Rule | Mechanical check | Scope of competence |
|------|------------------|---------------------|
| `heading-depth` | Distinct ATX/HTML heading depths in body (excluding title) | yes if ≥ 2 distinct depths; no if all same; undetermined if < 2 body headings |
| `list-bullets` | `^[-*+] ` line pattern or HTML `<ul>` | yes on match; no if absent and no unicode bullets; undetermined if `•`-prefixed paragraphs (audience-dependent) |
| `list-numbers` | `^\d+[.)]` line pattern or HTML `<ol>` | yes on match; no if absent |
| `table-structure` | Pipe-table rows or HTML `<table>` | yes on match; no if neither |
| `code-fence` | Triple-backtick fences or indented 4-space blocks | yes on match; no if neither |
| `emphasis-bold` | Paired `**X**` / `__X__` or HTML `<b>` / `<strong>` | yes on match; no if absent |
| `emphasis-italic` | Paired `*X*` / `_X_` or HTML `<i>` / `<em>` | yes on match; no if absent |
| `emphasis-mono` | Single-backtick `` `X` `` or HTML `<code>` | yes on match; no if absent |

Provenance-presence rules:

| Rule | Mechanical check | Scope of competence |
|------|------------------|---------------------|
| `page-marker` | Common page-boundary patterns (`--- Page N ---`, `<!-- page N -->`, `[Page N]`, `## Page N`, etc.) | yes on match; no if none found and no ambiguous numeric-only lines; undetermined if ≥ 3 numeric-only lines (could be page numbers or body content) |
| `section-number` | Heading text matching `^#+ <numeric-prefix> ` (e.g., `## 2.2 Models`, `## A.1 Appendix`) | yes on match; no if headings present but none numbered; undetermined if no headings at all |

**Rules that stay LLM-judged** (semantic load or per-target resolution required):
- `blockquote` — quotation semantics aren't pattern-matchable.
- `footnote-syntax` — footnote identity carries semantic load.
- `cross-ref-target` — presence AND accuracy need contextual resolution.
- `list-definition`, `caption-adjacency`, `image-reference` — semantic pairing/adjacency relationships.
- All provenance-**accuracy** probes — need per-target ground truth the markdown alone doesn't carry.
- All **content** probes — LLM-reader-equivalence IS the test for this class.

### 3. Audience-derived class-discipline boundary

The v0.2 "any clear signal" probe-wording discipline remains correct for the **content** class — the audience there is a downstream LLM reader, and LLM-reader-equivalence is the honesty test. A format probe authored under that discipline passes if the LLM recovers the structure from any cue, including prose context, numbering, or adjacency.

The **readability** class has a different audience: a human previewing the converted markdown or pasting it into Word/Pages. That audience needs actual markdown syntax that round-trips into their tool's structures. HTML `<table>` and `<ul>` are fine; unicode `•` without list syntax is not (a markdown renderer won't format it; Word's behavior is inconsistent). Readability probes therefore require strict markdown-syntax preservation, and mechanical checks enforce that strictness deterministically.

**The boundary is intentional and audience-derived.** Different class, different test discipline. Mechanical for readability isn't a regression from v0.2 "any clear signal" — it's the right test for the readability class's audience. v0.2's discipline was correct for the honesty test; v0.3.1's discipline is correct for the readability test.

### 4. Consequence: the readability class is now a deterministic analyzer

For pure-syntax rules, the v0.3.1 framework is closer to a **deterministic static analyzer** than to an LLM-eval framework — reproducible, cheap, invariant across runs. The rhetorical framing *"the framework asks an LLM whether it can read what was converted"* still holds for the content class (where LLM-reader-equivalence IS the test), but no longer applies to the readability class's mechanical rules. Readability for pure-syntax rules is now *"does the converter's markdown emit the specific syntax a markdown renderer requires"* — a question with a deterministic answer.

This is a positive shift on cost, stability, reproducibility, and forward-compatibility: when corpus grows, mechanical readability rules apply for free, with no per-document authoring. Only content + some provenance probes need authoring per new corpus item. Real economic argument beyond judge-stability.

### 5. Readability rule: note on violation cost

The v0.3 readability rules table includes a "violation cost" column describing the human-cleanup friction when a rule fails (re-level headings, re-bullet items, etc.). **v0.3.1 clarification:** this column is rationale, not scoring weight. Scoring is binary per rule, per document. The cost column explains *why* each rule matters; it does not weight aggregate scores. v0.3.1 defers cost-weighted aggregates until corpus growth makes such weighting load-bearing.

### 6. Aggregation across items

Per-item, per-class scoring is the ground truth. For cross-item summary (converter profile):

- **Unweighted mean of per-item rates, per class, per converter.** Each corpus item contributes equally to the class headline — a converter's readability is the average of its readability rates across all items where readability applies.
- **Per-item retained for inspection.** Headline numbers never replace the per-item breakdown; they summarize it.
- **Bias acknowledged explicitly:** small items (few probes) are weighted equally with large items (many probes). Weighting alternatives (by probe count, by rule coverage) are deferred until corpus stratification becomes meaningful; at v0.3.1 corpus size (8 items), unweighted mean is the honest default.

### 7. MinerU profile under v0.3.1 mechanical checks

Re-scoring MinerU with mechanical readability checks produced a substantially lower readability score than v0.3's permissive LLM-judge (**63% → 31%**). The drop is not a regression in MinerU — it's the framework no longer hiding what MinerU doesn't emit. Paragraphs prefixed with `•` don't render as lists in a markdown previewer; depth-collapsed headings don't distinguish hierarchy for a human paster. Mechanical checks call these what they are. *"MinerU is honest but its output is not readable-to-humans without manual restructuring"* — that finding is the point.

See `docs/sprint-3-results.md` for the full v0.3.1 scores by item and per-rule.

---

_v0.3.1, 2026-04-23. Hybrid mechanical + LLM dispatch for rules where markdown syntax is unambiguous; audience-derived class-discipline boundary named; aggregation discipline defined. v0.3 amendments preserved above. Deterministic readability checks obey the "knows its limits" principle — three-valued output with LLM fallback for undetermined._
