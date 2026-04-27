# Probe-authoring discipline (v0.3.x)

Working notes on the disciplines that produce a probe set worth scoring against. Surfaced during Sprint 4b's authoring of 81 probes across 4 wild corpus items, refined under Claire's AT red-team. Companion to `docs/failure-mode-catalog.md` (which catalogs *what* to probe) and `corpus/lost-in-the-middle/probes.json` (which is the reference exemplar of probe shape).

This file is for the *how*: practices and checks that make probe authoring more reliable.

---

## The disciplines

### 1. Falsify before commit

**Discipline:** before asserting "no Y in this source" in an anti-fabrication probe, scan the source for Y indicators. Use a deterministic tool — `pdftotext` + `grep` is sufficient — not your reading memory.

**Why:** anti-fab probes (probes with `expected_answer: "no"`) carry the strongest authoring risk. If a probe asserts "the document contains no code blocks" and the document actually has a single fenced HTTP-protocol block on page 47 that the author missed, every converter that *correctly preserves* the block fails the probe. The probe becomes the wrong measurement, baked into the matrix.

A few minutes of grep beats hours of post-hoc explanation when matrix runs surface anomalies traced to probe-author error.

**How:** for each anti-fab claim, identify likely indicators of the feature in question and run a plain text scan. Examples from Sprint 4b:

| Anti-fab claim | Indicators to grep for |
|----------------|------------------------|
| No code blocks | `HTTP/[0-9]`, `POST `, `GET `, `Content-Type:`, `^\s*\{[^}]*"`, `-----BEGIN`, `<\?xml`, `\bJWT\b`, `\bJOSE\b` |
| No bulleted lists | `^[ \t]*[-*+•]\s+\S` (CommonMark + unicode bullet markers) |
| No tables | `^\|.*\|\s*$` (markdown), `\\begin{tabular}` (LaTeX source if owned), HTML `<table>` |
| No footnotes | `^\d+\.\s+(See|See also|Id\.|See, e\.g\.,)` (footnote-body lead-ins typical in legal/regulatory genres) |

If the scan returns zero hits, the anti-fab probe is well-founded. If hits surface, *re-read the source at those locations* before committing — what looked like the absent feature may be a false positive (e.g., `^\d+\.\s+See` could be a numbered list of cases, not a footnote), or it may be a real instance of the feature you missed.

**Limit:** the scan can only falsify, not confirm. A probe that asserts presence (`expected_answer: "yes"`) needs human reading; the scan can't tell you whether the matched text is *the specific feature you described in the probe*. Use the scan to falsify "no" claims, then accept that "yes" claims rest on PDF-visual reading.

### 2. Anchor-vs-body location precision (regulatory-genre)

**Discipline:** for footnote-content probes, distinguish between the page that hosts the *anchor* (the small superscript number in body text) and the page that hosts the *body* (the footnote text at the bottom margin). Cite the body page as the ground-truth location.

**Why:** in regulatory and legal documents, a footnote anchor is referenced from body text on page N, but the footnote body may run at the bottom of page N or N+1 (and sometimes spans pages with "Continued from previous page" markers). For multi-converter measurement, what matters is where the *body text* is rendered — that's what the converter's markdown either preserves or drops.

Sprint 4b caught one instance of this: an FCC probe cited footnote 6 as "page 1" because that's where the anchor `⁶` appeared in body text; the actual footnote body sits at the bottom of page 2. Under matrix scoring, a converter that correctly emits the footnote body but omits its origin marker would have been scored against the wrong page.

**How:** when authoring a footnote probe, note both locations in `ground_truth_basis`:

```
"Source PDF page 2 footnote 6 begins '...' . The footnote-6 anchor
is referenced from body text on page 1; the footnote body itself
appears at the bottom of page 2."
```

**Generalization:** the same precision applies to any feature that has separable "where it's referenced" and "where it lives" coordinates — figures (caption page vs. figure-render page if they wrap), tables in regulatory documents that span pages, sidebars that float, etc.

### 3. Pair every content-presence with format/readability where the source supports it

**Discipline:** for every content probe testing whether content X exists, author a paired probe testing whether X is preserved with its format. The paired probe shares a feature label and tests the structural property.

**Why:** without pairing, a single "is X present?" probe answered "yes" can mask a converter that flattens X's structure beyond recovery. The Sprint 2 `lt-h-c` content probe ("does the doc have a Models section?") was paired with `lt-h-f` (readability-class, "is Models marked at deeper heading depth than its parent?"). MinerU passes the content probe (heading text preserved) but fails the readability probe (heading flattened to `##` regardless of source depth). Both findings matter; only paired probes surface both.

**How:** for each catalog cell instantiated, ask both questions:

| Cell | Content probe | Readability probe |
|------|---------------|-------------------|
| Heading | Does heading X exist? | Is heading X at distinguishable markdown depth? |
| List | Are the list items present? | Are they marked with markdown bullet syntax? |
| Italic | Does the italicized phrase exist as text? | Is it formatted as italic in markdown? |
| Table | Does the tabular data exist? | Is it rendered as table syntax (markdown pipes / HTML `<table>`)? |

If the source genre doesn't support a cell, omit it (e.g., NASA Spinoff has no numbered section hierarchy → no section-number probe). But never split a paired probe across two corpus items "for symmetry"; pair *within* an item where the cell is instantiated.

**Provenance pairing:** for every provenance probe, author the presence-then-accuracy pair (`<id>-p` / `<id>-a`). Presence asks whether a coordinate (page marker, section number, paragraph number, cross-ref target) exists; accuracy asks whether the indicated value is correct. The pair separates three failure modes:

- Drop → fails presence
- Fabricate-wrong → passes presence, fails accuracy  
- Preserve-correct → passes both

A single "did the converter preserve X correctly?" probe collapses these into yes/no and loses the diagnostic.

### 4. Ground-truth ties to PDF visual, not source

**Discipline:** for wild corpus items (PDFs published by third parties), ground-truth claims must be verifiable from the rendered PDF, not from any LaTeX/Word/InDesign source the author could scrape.

**Why:** publication templates strip markup. The original Sprint 2 LITM probe set caught this: TACL conference template strips `\textit{}` from body text, so a probe author reading the LaTeX source would author a probe expecting italic that doesn't appear in the rendered PDF. The converter's job is to preserve what's *visible*, not what the source code intended.

Synthesized corpus items are an exception: when we own the rendering pipeline (vanilla `article.cls` + pdflatex), source-derived ground truth is safe because we control which markup survives. See `experiments/source-fidelity-test/` for the verification of this.

**How:** every `ground_truth_basis` for a wild-item probe should reference a page number and describe what is *visually* on that page. If a probe author's only basis for a claim is "the LaTeX source has `\textit{X}`," the probe is at risk and needs PDF-visual verification before commit.

### 5. Mechanical rules know their scope of competence

**Discipline:** when adding a mechanical rule to `scripts/rules.py`, the rule must return three-valued output (`yes` / `no` / `undetermined`) and explicitly recognize input outside its competence as `undetermined` (which falls through to LLM judgment).

**Why:** see `feedback_deterministic_knows_its_limits` (auto-memory). A brittle mechanical check that returns yes/no on ambiguous inputs is worse than slower LLM inference because the failure is silent. The framework's hybrid measurement quality depends on each rule honestly refusing to answer outside its scope.

**Corollary for probe authoring:** when a probe needs a new rule that doesn't yet exist, *don't add a half-thought rule under deadline pressure*. Set the `rule:` field on the probe to document the intent (e.g., `paragraph-marker`); the dispatch code falls through cleanly to LLM judgment via `has_mechanical_check`. Add the mechanical rule on a hardening branch with the focus that work deserves.

Sprint 4b applied this: FCC paragraph-number provenance probes (`fc-pn-p`, `fc-pn-a`) ship with `rule: paragraph-marker` and no mechanical implementation, deferred to v0.3.3. The conflation risk (`^\d+\.\s` matches both paragraph-numbered prose and markdown numbered-list syntax) was the trigger for the deferral — exactly the kind of distinction a mechanical rule needs to encode in its scope of competence.

---

## Where this fits

These disciplines apply to probe authoring across all corpus items and converters. They sit alongside:

- **Failure-mode catalog** (`docs/failure-mode-catalog.md`) — catalogs *which cells* probes should target.
- **Probe schema** (`corpus/*/probes.json`) — codifies the *shape* of individual probes (id, probe_class, feature, rule, question, expected_answer, ground_truth_basis).
- **Mechanical rules** (`scripts/rules.py`) — implements the deterministic checks for readability and provenance probes where markdown syntax is unambiguous.
- **Per-item READMEs** (`corpus/*/README.md`) — capture genre-specific authoring guidance for the next author.

A probe set that follows the disciplines in this file is *more likely* to produce honest matrix-run results. It does not guarantee correctness — every probe still rests on the author's reading of the source PDF. The disciplines reduce the failure modes an honest author can fall into; they don't replace honesty.

---

## Origin

Drafted Sprint 4b 2026-04-27 after Claire's AT red-team surfaced the falsification-scan and anchor-vs-body precision patterns as worth promoting beyond mesh-message ephemera. Documenting them here so the next probe author benefits from the lessons without re-deriving them.

Discipline 5 (mechanical-rule scope of competence) is preserved here from `feedback_deterministic_knows_its_limits` — it predates Sprint 4b but applies directly to probe-authoring decisions about whether to add or defer mechanical rules during sprint work.
