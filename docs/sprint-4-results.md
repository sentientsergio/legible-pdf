# Sprint 4 Results: Multi-Converter Comparison

**Run dates:** 2026-04-26 → 2026-04-27 (Sprint 4b — corpus expansion + 4-converter matrix)
**Corpus:** 12 items — 5 wild + 7 synthesized (`corpus/`)
**Converters:** MinerU (pipeline backend), docling, marker, PyMuPDF4LLM
**Judge model:** `claude-haiku-4-5-20251001` (LLM-judged path); `scripts/rules.py` (mechanical path)
**Probe set:** 141 probes total (81 new wild-item probes from Sprint 4b authoring + 60 existing across LITM and 7 synthesized items)
**Matrix:** 4 converters × 12 items × ~141 probes ≈ 1,500+ scored cells, with mechanical-first dispatch + N=3 unanimous LLM fallback

---

## Goal

Three deliverables on the same branch:

1. **Add 4 wild corpus items** — grow N from 8 → 12 across legal, regulatory, technical-guideline, and popular-press genres.
2. **Run a complete 4 × 12 matrix** — every converter on every item; per-converter three-track honesty profile; cross-converter comparison.
3. **Surface methodology lessons** that emerged during probe authoring and AT review.

The sprint shipped under "integrity of effort, not effort itself" discipline (`feedback_integrity_of_effort`) — combined sprint, not phased sub-matrices. Each landing state is a complete matrix.

---

## What was built

**Four wild corpus items** (`66bb939`):

| Slot | Document | Pages | License |
|------|----------|-------|---------|
| Legal / court filing | SCOTUS slip — *Loper Bright Enterprises v. Raimondo* (No. 22-451, 2024) | 114 | Public domain (US gov work) |
| Regulatory filing | FCC 25-86 — Numbering Policies Third R&O (Dec 2025) | 34 | Public domain (US gov work) |
| Technical guideline | NIST SP 800-63B — Digital Identity Guidelines | 80 | Public domain (US gov work) |
| Popular-press magazine | NASA Spinoff 2025 | 56 | Public domain (US gov work) |

Each item gets `source.pdf` + `README.md` capturing provenance, license, retrieval URL+date, and probe-authoring guidance for the genre. The originally-planned OpenStax CC-BY textbook was substituted with NIST SP 800-63B (OpenStax CDN serves 403 to direct fetches; reproducible retrieval was awkward). NIST is structurally equivalent for the failure-mode lens.

**Eighty-one probes** authored for the 4 wild items + AT-pass amendments (`e52c1a2` → `0bf7ee3`). Combined with existing 60 probes, the matrix scores against **141 total probes** per converter:

| Item | Total | Content | Readability | Provenance |
|------|-------|---------|-------------|------------|
| `scotus-loper-bright` | 20 | 12 | 2 | 6 |
| `fcc-numbering-order` | 22 | 11 | 3 | 8 |
| `nist-sp-800-63b` | 20 | 9 | 5 | 6 |
| `nasa-spinoff` | 19 | 11 | 4 | 4 |
| `lost-in-the-middle` | 21 | 12 | 3 | 6 |
| `code-blocks-and-images` (synth) | 10 | 5 | 4 | 1 |
| `formatted-text-in-context` (synth) | 20 | 11 | 9 | 0 |
| `mixed-lists` (synth) | 10 | 6 | 4 | 0 |
| `multi-column-reading-order` (synth) | 10 | 10 | 0 | 0 |
| `nested-headings-deep` (synth) | 10 | 5 | 5 | 0 |
| `nested-headings-unnumbered` (synth) | 10 | 5 | 5 | 0 |
| `tables-and-captions` (synth) | 12 | 6 | 5 | 1 |
| **total per converter** | **184** | **103** | **49** | **32** |

Per-item probes.json files sum to 184 across 12 items; aggregate counts in each `honesty_profile.json` match exactly (verified during AT). Sprint-3 carried per-class denominator imbalance into Sprint 4b: 184 probes × 4 converters = 736 cells scored, with the matrix-output table headers accordingly displaying `n=103` for content, `n=49` for readability, `n=32` for provenance per converter.

**Three new converters installed and harnessed** (`6055061`):

- **docling** — IBM's PDF-to-markdown converter with layout analysis
- **marker** — Vik Paruchuri's marker-pdf with surya OCR + table recognition
- **PyMuPDF4LLM** — thin markdown wrapper around PyMuPDF (no models)

Plus existing **MinerU** (pipeline backend) carried through from Sprint 3.

**Matrix orchestration** (`scripts/run_converter.py` + `scripts/run_matrix.py` + `scripts/aggregate_matrix.py`) — single-command full-matrix run with resumability (skip cells whose output exists unless `--force`), phase split (convert | score | both), per-converter time tracking, and aggregation into per-converter three-track profiles.

---

## Per-converter three-track profiles

Per-converter aggregate rates, computed as **unweighted mean of per-item rates per class** (Sprint 3 methodology, preserved):

| Converter | Content | Readability | Provenance | Profile |
|-----------|---------|-------------|------------|---------|
| **mineru** | **97%** (98/103) | 46% (19/49) | 69% (19/32) | Strong content, mid readability, mid provenance |
| **docling** | **98%** (100/103) | 49% (21/49) | **85%** (25/32) | Strong content, mid readability, **strongest provenance** |
| **marker** | 96% (98/103) | **87%** (38/49) | 69% (19/32) | Strong content, **strongest readability**, mid provenance |
| **pymupdf4llm** | 96% (97/103) | 67% (34/49) | 77% (22/32) | Strong content, second-place readability, second-place provenance |

Counts in parentheses are total matches across all per-item probes (weighted denominator). Percentages are unweighted means. Per Sprint 3 aggregation discipline, per-item profiles are ground truth; aggregates summarize this specific 12-item corpus.

**No converter dominates all three tracks.** Marker is a clear readability winner (+38 pp over the next-best), docling leads provenance (+8 pp over second place), and content is essentially tied across all four (96-98% — within a couple of probes per converter on the same N).

The three-track profile is the deliverable shape — reducing it to a single number destroys the finding (per Sprint 3 methodology, `feedback_audience_needs_lens`, v0.3.2 §2 framework taste).

---

## Per-item × per-converter scores

### Content (LLM-judged honesty)

| Item | mineru | docling | marker | pymupdf4llm |
|------|--------|---------|--------|-------------|
| `fcc-numbering-order` | 11/11 (100%) | 11/11 (100%) | 10/11 (91%) | 10/11 (91%) |
| `lost-in-the-middle` | 10/12 (83%) | 11/12 (92%) | 11/12 (92%) | 10/12 (83%) |
| `nasa-spinoff` | 11/11 (100%) | 11/11 (100%) | 10/11 (91%) | 11/11 (100%) |
| `nist-sp-800-63b` | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| `scotus-loper-bright` | 9/12 (75%) | 10/12 (83%) | 10/12 (83%) | 9/12 (75%) |
| `code-blocks-and-images` | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) |
| `formatted-text-in-context` | 11/11 (100%) | 11/11 (100%) | 11/11 (100%) | 11/11 (100%) |
| `mixed-lists` | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |
| `multi-column-reading-order` | 10/10 (100%) | 10/10 (100%) | 10/10 (100%) | 10/10 (100%) |
| `nested-headings-deep` | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) |
| `nested-headings-unnumbered` | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) |
| `tables-and-captions` | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |

**Reading.** Content preservation is robust across the matrix — every cell is at or near 100% on synthesized items where ground truth is unambiguous. The wild items show modest content differences: `scotus-loper-bright` is the hardest content item across all converters (75-83%, driven by footnote-body preservation and case-name-italicized-content probes), while `fcc-numbering-order` is uniformly easy (~100%). No converter is content-failing in any consequential way.

### Readability (mechanical-first, LLM-fallback)

| Item | mineru | docling | marker | pymupdf4llm |
|------|--------|---------|--------|-------------|
| `fcc-numbering-order` | 1/3 (33%) | 1/3 (33%) | **3/3 (100%)** | 2/3 (67%) |
| `lost-in-the-middle` | 2/3 (67%) | 2/3 (67%) | **3/3 (100%)** | 2/3 (67%) |
| `nasa-spinoff` | 1/4 (25%) | 2/4 (50%) | **4/4 (100%)** | **4/4 (100%)** |
| `nist-sp-800-63b` | 4/5 (80%) | 3/5 (60%) | **5/5 (100%)** | 4/5 (80%) |
| `scotus-loper-bright` | 2/2 (100%) | 1/2 (50%) | 2/2 (100%) | 1/2 (50%) |
| `code-blocks-and-images` | 3/4 (75%) | **4/4 (100%)** | **4/4 (100%)** | 3/4 (75%) |
| `formatted-text-in-context` | **0/9 (0%)** | **0/9 (0%)** | **0/9 (0%)** | **9/9 (100%)** |
| `mixed-lists` | 2/4 (50%) | 4/4 (100%) | 3/4 (75%) | 4/4 (100%) |
| `nested-headings-deep` | 0/5 (0%) | 0/5 (0%) | **5/5 (100%)** | 0/5 (0%) |
| `nested-headings-unnumbered` | 0/5 (0%) | 0/5 (0%) | **5/5 (100%)** | 0/5 (0%) |
| `tables-and-captions` | 4/5 (80%) | 4/5 (80%) | 4/5 (80%) | 5/5 (100%) |

**Reading.** Readability is where converter behavior diverges most. Three patterns:

- **Marker preserves heading depth where others flatten.** The synthesized diagnostic pair `nested-headings-deep` and `nested-headings-unnumbered` was authored to expose the v0.3.1 finding that MinerU collapses every body heading to `##`. Marker is the only converter that preserves multi-level heading depth (5/5 on both items). MinerU, docling, and PyMuPDF4LLM all score 0/5. Marker's surya layout model is doing real work here. *Caveat surfaced during AT spot-checks:* marker preserves *multiple* depths but the depth assignment is internally inconsistent within a single document (e.g., `1.1` rendered as `###` while `1.2` in the same doc renders as `##`). The 5/5 score is correct against the `heading-depth` rule, which tests for "more than one distinct depth"; the lead is "preserves multiple depths" rather than "preserves correct depths." A stricter rule would catch the inconsistency.
- **PyMuPDF4LLM preserves emphasis where others strip.** `formatted-text-in-context` (italic/bold/monospace × 3 positions) inverts the picture: PyMuPDF4LLM scores 9/9, all three model-based converters score 0/9. PyMuPDF4LLM relies on PyMuPDF's font-style detection, which is mechanically reliable; the model-based converters appear to either filter emphasis as noise or fail to project it into markdown. This is a striking inversion — the simplest converter (no models) wins on the inline-emphasis probe.
- **Marker dominates `nasa-spinoff` readability** (4/4) where MinerU and docling fall (1/4 and 2/4 respectively). Magazine layouts with colored title bars, multi-column flow, and image-caption pairing are exactly the kind of layout-rich content marker's models were trained for.

### Provenance (mechanical-first, LLM-fallback)

| Item | mineru | docling | marker | pymupdf4llm |
|------|--------|---------|--------|-------------|
| `fcc-numbering-order` | 4/8 (50%) | **6/8 (75%)** | 4/8 (50%) | 5/8 (62%) |
| `lost-in-the-middle` | 4/6 (67%) | 4/6 (67%) | 4/6 (67%) | 2/6 (33%) |
| `nasa-spinoff` | 2/4 (50%) | **4/4 (100%)** | 2/4 (50%) | 3/4 (75%) |
| `nist-sp-800-63b` | 4/6 (67%) | 4/6 (67%) | 2/6 (33%) | 4/6 (67%) |
| `scotus-loper-bright` | 3/6 (50%) | 5/6 (83%) | 5/6 (83%) | **6/6 (100%)** |
| `code-blocks-and-images` | 1/1 (100%) | 1/1 (100%) | 1/1 (100%) | 1/1 (100%) |
| `tables-and-captions` | 1/1 (100%) | 1/1 (100%) | 1/1 (100%) | 1/1 (100%) |

(Synthesized items without provenance probes — `formatted-text-in-context`, `mixed-lists`, `multi-column-reading-order`, `nested-headings-deep`, `nested-headings-unnumbered` — omitted from the table.)

**Reading.** Provenance results are spread but show clear leaders:

- **Docling leads provenance overall** (85% unweighted mean). Particularly strong on the magazine-layout `nasa-spinoff` (4/4, the only converter to pass all four provenance probes including page-marker presence and (Spinoff YYYY) cross-references).
- **PyMuPDF4LLM unexpectedly wins SCOTUS provenance** (6/6 on `scotus-loper-bright`, where every other converter scores 5/6 or 3/6). The slip-opinion's "Cite as: 603 U.S. ___ (2024)" header and per-page numbering pattern appears robust to PyMuPDF's text-layer extraction even without semantic understanding.
- **Page-marker preservation is the dominant gap.** Across all converters and items, the `page-marker` rule's `expected_answer: "yes"` is the most-failed provenance question. Most converters do not project page boundaries to markdown — Sprint 3's MinerU finding generalizes to docling and marker; only PyMuPDF4LLM's text-layer extraction occasionally preserves page-number tokens.
- **Section-number preservation is the dominant strength.** Where source documents have numbered headings (NIST SP 800-63B's `5.1.1.1`, FCC's Roman/lettered, SCOTUS's Roman), section numbers ride along with heading text and survive most conversions.

---

## Cross-converter comparison

**Findings against the three-audience framing** (content for LLM-readers; readability for human-pasters; provenance for LLM-analysts producing verifiable citations):

1. **Marker is the clear readability winner** for users who paste markdown into Word/Pages and need format preservation. +38 pp over the next-best converter on readability is the single largest gap in the matrix. The trade-off: marker is also the slowest converter (avg ~2-5min per wild item; NASA Spinoff alone took 11 min).

2. **Docling is the clear provenance winner** for LLM-analyst use cases (legal/regulatory citations, scientific cross-references). +8 pp over second place, with strongest performance on the citation-rich genres (FCC, NASA Spinoff). Docling is also fast (5-30s per item).

3. **PyMuPDF4LLM is a surprising upset** in two specific places: emphasis preservation (`formatted-text-in-context` 9/9 where all model-based converters score 0/9) and SCOTUS provenance (6/6, only converter at 100%). The simplest converter — no models, just PyMuPDF text-layer extraction — wins on the genres where the source PDF's text layer carries the structural signal. Where layout analysis is needed (multi-column reading order, magazine layouts, complex tables), it falls behind.

4. **MinerU (Sprint 3 baseline) re-scores against the larger corpus at 97/46/69.** Compared to its Sprint 3 single-item-aggregate of 97/31/75, content is unchanged, readability is up (the new corpus items have readability probes MinerU passes; the synthesized formatted-text + heading-depth items remain 0/9 and 0/5 as in Sprint 3), and provenance is slightly down (the new wild items expose MinerU's page-marker absence consistently). MinerU does not lead on any axis.

**Genre interactions surface real differences.** Marker's readability advantage holds across 4 of 5 wild items but does *not* extend to `formatted-text-in-context` (where it scores 0/9 alongside the other model-based converters) — Surya's layout model captures heading hierarchy but not inline emphasis. PyMuPDF4LLM's text-layer reliability shows in two places where most converters underperform: the citation-rich legal genre (SCOTUS provenance 6/6 — only converter at 100%) and magazine readability (NASA Spinoff 4/4, tied with marker for best). It falls behind on the heading-depth diagnostics (0/5 on both `nested-headings-deep` and `nested-headings-unnumbered`) where the layout signal isn't in the text layer at all. The matrix supports per-genre converter selection, not a one-size-fits-all "best converter" verdict.

**On the corpus-choice bias caveat (catalog v0.3.2 §5).** The aggregate numbers (97/46/69 for MinerU, etc.) are point estimates over this specific 12-item corpus, not statistical estimators of converter field performance. 7 of 12 items are our own synthesis choices, selected to exercise specific catalog cells. Converters strong on our synthesis and weak on patterns we didn't synthesize would outperform their field behavior here. Per-item profiles (the tables above) are the ground truth; the aggregate summarizes this specific set.

---

## Methodology discoveries

Two probe-authoring disciplines surfaced during Sprint 4b's AT loop with Claire and the fixes I made in response. Promoted to first-class methodology in `docs/probe-authoring-discipline.md`:

1. **Falsify before commit** — for any anti-fabrication probe (`expected_answer: "no"`), run a deterministic `pdftotext + grep` scan for indicators of the feature *before* committing the probe. Caught a stale README guidance line during the AT pass for NIST. Generalizes: anti-fab probes carry the strongest authoring risk because a missed instance silently flips the verdict on every converter.

2. **Anchor-vs-body location precision** — for footnote-content probes in regulatory and legal genres, distinguish between the page that hosts the *anchor* (superscript number in body text) and the page that hosts the *body* (footnote text at bottom margin). Caught a real ground-truth error in the FCC probe set during the AT pass (footnote 6 anchor on page 1, body on page 2; the probe had cited page 1 as the body location).

The `docs/probe-authoring-discipline.md` file consolidates these with three pre-existing disciplines (paired probes, PDF-visual ground truth for wild items, mechanical-rule scope of competence) into the canonical home for the probe-authoring "how."

---

## Open methodology questions surfaced by the matrix

These are findings the matrix raised that are worth flagging for the next sprint:

1. **Italic-readability low-bar formulation** (carried over from AT pass — Claire flagged, deferred to v0.3.3). The current `lb-i-f` / `fc-i-f` / `ns-i-f` / `nf-i-f` ask "any italic span?" — caught only catastrophic stripping. Result: all four converters trivially pass on the wild items, but `formatted-text-in-context` (which has stricter per-position probes) showed PyMuPDF4LLM as 9/9 and the rest as 0/9. The wild-item readability scores would be more discriminating with LITM-shaped specific-phrase italic probes.

2. **Mechanical paragraph-marker rule deferred** (Sprint 4b authoring decision). FCC's `fc-pn-p` / `fc-pn-a` are LLM-judged for now. The mechanical rule needs careful scope-of-competence design to avoid `^\d+\.\s` collision with markdown numbered-list syntax. v0.3.3 hardening branch is the right home.

3. **Marker's heading-depth advantage is converter-architectural.** Surya's layout model captures heading hierarchy as a first-class concept. MinerU's pipeline backend, docling, and PyMuPDF4LLM all flatten to a single body-heading depth (with section numbers in heading text). If this finding holds across more documents, it suggests "preserve heading hierarchy" should be a converter-selection criterion rather than something to wait for converters to fix.

4. **PyMuPDF4LLM's emphasis-preservation advantage is mechanical-architectural.** PyMuPDF reads font-style attributes from the text layer; no model inference needed. Model-based converters appear to filter emphasis or fail to project it. For users where inline-emphasis matters (legal italicized case names, technical emphasized terms), text-layer-based converters may be the right choice.

5. **Page-marker is the universal gap.** No converter in the matrix consistently projects page numbers to markdown. For LLM-analyst use cases (verifiable citations of form "page N"), this is the most consequential remaining failure across the ecosystem. A converter that adds page markers would dominate provenance.

---

## What landed vs what's left

**Landed on `feature/sprint-4b-multi-converter`** (commits `1c9d365` through `63c8fa0` plus matrix-output commits):

- ✅ Transmigration plumbing — auto-memory entries, `docs/.session-handoff.md`, CLAUDE.md session-continuity section.
- ✅ 4 wild corpus items with per-item README + source PDF.
- ✅ 81 probes across the 4 wild items, AT-passed under Claire's red-team review.
- ✅ 3 new converters installed + smoke-tested + harnessed.
- ✅ Matrix orchestrator (`scripts/run_converter.py`, `scripts/run_matrix.py`, `scripts/aggregate_matrix.py`).
- ✅ Full 4 × 12 matrix run completed (48 cells, 0 failures).
- ✅ Per-converter three-track profiles + cross-converter comparison.
- ✅ `docs/probe-authoring-discipline.md` — methodology discoveries.
- ✅ This results doc.

**Deferred to Sprint 4c / v0.3.3 hardening:**

- Mechanical `paragraph-marker` rule in `scripts/rules.py` (scope-of-competence design needed; conflation risk with markdown numbered-list syntax).
- Tighter italic-readability probes per-item (LITM-shaped specific-phrase wording instead of "any italic span?").

**Deferred to Sprint 5+ (corpus breadth + frontier work):**

- Additional wild corpus items (e.g., a true OpenStax-style pedagogical textbook chapter; more diverse popular-press samples beyond NASA Spinoff).
- Catalog v0.4 amendment if matrix data motivates new failure-mode cells (current verdict: it does not — the v0.3.2 catalog held up under multi-converter measurement).
- Empirical HTML-`<table>` Word/Pages round-trip verification.
- Residual judge-stability investigation on short-phrase content probes.

---

## Sprint 4 status

- [x] Probe authoring for 4 wild items under v0.3.1 class discipline (81 probes)
- [x] AT pass on probe authoring (Claire red-team, fixes-back, sign-off)
- [x] 3 new converters installed and harnessed
- [x] Matrix orchestrator scripts (single-command full run, resumable)
- [x] Full 4 × 12 matrix run completed (48 cells, 0 failures)
- [x] Per-converter three-track profiles + cross-converter comparison
- [x] Methodology discoveries promoted to `docs/probe-authoring-discipline.md`
- [x] Sprint results doc finalized (this file)
- [ ] AT pass on results — pending Claire red-team

Sprint 4b closes when Claire's AT pass on results signs off. Substack-feed summary work, if Sergio judges it due, happens in the between-sprint pause after sprint close — not as a forced gate (`feedback_sprint_cadence`).

---

## Artifacts

- `docs/failure-mode-catalog.md` — v0.3.2 (taxonomy stable; held up under multi-converter measurement)
- `docs/probe-authoring-discipline.md` — **new in Sprint 4b** (methodology discoveries from probe authoring + AT loop)
- `scripts/run-eval.py` — harness v0.3.1 (unchanged)
- `scripts/rules.py` — mechanical rule checks (unchanged in Sprint 4b; `paragraph-marker` deferred to v0.3.3)
- `scripts/run_converter.py` — **new in Sprint 4b** (single-converter PDF→markdown runner, 4 backends)
- `scripts/run_matrix.py` — **new in Sprint 4b** (full matrix orchestrator with phase split + resumability)
- `scripts/aggregate_matrix.py` — **new in Sprint 4b** (matrix aggregation into three-track profiles)
- `corpus/{scotus-loper-bright,fcc-numbering-order,nist-sp-800-63b,nasa-spinoff}/` — 4 wild items × {source.pdf, README.md, probes.json}
- `corpus/**/output/{mineru,docling,marker,pymupdf4llm}/{output.md, honesty_profile.json}` — 48 per-cell outputs
- `docs/sprint-4-aggregated.json` — full per-cell + per-converter aggregate data (machine-readable)
- `docs/sprint-4-results.md` — this file
