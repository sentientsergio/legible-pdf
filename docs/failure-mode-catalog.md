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

_v0.1, 2026-04-22. Drafted from frompdf SOTA research as primary source. Will accumulate observations from prior CPPA/EI work and from eval runs._
