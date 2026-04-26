# Sprint 4 Results: Multi-Converter Comparison (DRAFT — matrix run in flight)

**Run dates:** 2026-04-26 → 2026-04-27 (Sprint 4b, multi-converter comparison)
**Corpus:** 12 items — 5 wild + 7 synthesized (from `corpus/`)
**Converters:** MinerU (pipeline backend), docling, marker, PyMuPDF4LLM
**Judge model:** `claude-haiku-4-5-20251001` (LLM-judged path); `scripts/rules.py` (mechanical path)
**Probe set:** 81 + 60 = 141 probes total (81 new wild-item probes from Sprint 4b authoring + 60 existing across Lost-in-the-Middle and 7 synthesized items)

---

## Goal

Three deliverables on the same branch:

1. **Add 4 wild corpus items.** Grow N from 8 to 12. Cover four genres beyond LITM's scientific-paper baseline: legal/court filing, regulatory filing, technical guideline (textbook-equivalent), and popular-press magazine.
2. **Run a complete 4-converter × 12-item matrix.** Each converter on each item; per-converter three-track honesty profile; cross-converter comparison.
3. **Surface methodology lessons that emerged.** Sprint 4b's probe-authoring work generated two new disciplines worth landing in `docs/probe-authoring-discipline.md` (companion to this results doc).

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

Each item gets `source.pdf` + `README.md` capturing provenance, license, retrieval URL+date, and probe-authoring guidance for the genre.

**Substitution from original plan:** the original Sprint 4b sequence called for an OpenStax CC-BY textbook chapter in the textbook slot. OpenStax CDN serves 403 to direct fetches (interactive download only); reproducible corpus retrieval was awkward. NIST SP 800-63B is structurally equivalent for the failure-mode lens (multi-level numbered headings, substantive tables, real bulleted lists, italic + bold inline, dense in-text section/standard cross-references) and reliably retrievable. Pure pedagogical textbook can be added in a later sprint if the genre distinction matters.

**Eighty-one probes** authored for the 4 wild items + AT-pass amendments (`e52c1a2` → `0bf7ee3`):

| Item | Total | Content | Readability | Provenance |
|------|-------|---------|-------------|------------|
| `scotus-loper-bright` | 20 | 12 | 2 | 6 |
| `fcc-numbering-order` | 22 | 11 | 3 | 8 |
| `nist-sp-800-63b` | 20 | 9 | 5 | 6 |
| `nasa-spinoff` | 19 | 11 | 4 | 4 |
| **total** | **81** | **43** | **14** | **24** |

Probes follow LITM (`corpus/lost-in-the-middle/probes.json`) as the reference exemplar — paired content/format under v0.3.1 class discipline; paired provenance presence + accuracy. Ground truth is rendered-PDF-visual per probe. New `paragraph-marker` rule introduced (LLM-judged for now; mechanical check deferred to v0.3.3 hardening).

Combined with existing 60 probes across Lost-in-the-Middle (21) and 7 synthesized items (39), the matrix scores against **141 total probes** per converter.

**Three new converters installed and harnessed** (`6055061`):

- **docling** — IBM's PDF-to-markdown converter with layout analysis
- **marker** — Vik Paruchuri's marker-pdf with surya OCR + table recognition
- **PyMuPDF4LLM** — thin markdown wrapper around PyMuPDF (no models)

Plus existing **MinerU** (pipeline backend) carrying through from Sprint 3.

**Matrix orchestration** (`scripts/run_converter.py` + `scripts/run_matrix.py`) — single-command full matrix run with resumability (skip cells whose output exists unless `--force`), phase split (convert | score | both), per-converter time tracking.

---

## Per-converter three-track profiles

> **Status: pending matrix run completion.** This section will be populated when the convert + score phases finish. Profile shape per converter:
>
> | Converter | Content | Readability | Provenance | Notes |
> |-----------|---------|-------------|------------|-------|
> | mineru | TBD | TBD | TBD | (existing baseline from Sprint 3, re-scored under v0.3.1 with new wild items) |
> | docling | TBD | TBD | TBD | First measurement |
> | marker | TBD | TBD | TBD | First measurement |
> | pymupdf4llm | TBD | TBD | TBD | First measurement |

---

## Per-item scores

> **Status: pending matrix run completion.** Per-item × per-converter table populated when matrix runs finish. Format follows `docs/sprint-3-results.md` shape: `matches/n (rate)` per cell, with `m` noting mechanical-answered counts and `d` noting disputed (LLM-unanimous-only) counts.

---

## Cross-converter comparison

> **Status: pending matrix run completion.** Comparison narrative addresses:
>
> - **Honesty (content) gap:** which converter best preserves substantive content; which has the largest content-loss footprint.
> - **Readability gap:** which converter produces output most directly usable by a human paster (markdown syntax preservation); per-feature breakdown (heading-depth, list-bullets, table-structure, italic, bold).
> - **Provenance gap:** which converter best preserves citation coordinates (page markers, section numbers, cross-ref targets, paragraph markers in regulatory genres).
> - **Genre interactions:** does converter ranking shift across genres (e.g., does converter X dominate on academic papers but lag on regulatory filings)?
>
> No composite. Three-track profiles are the deliverable shape — reducing them to a single number destroys the finding (per Sprint 3 methodology).

---

## Methodology discoveries

Two probe-authoring disciplines surfaced during Sprint 4b. Both originated in Claire's AT red-team feedback and the fixes I made in response. Promoted to first-class methodology in `docs/probe-authoring-discipline.md`:

1. **Falsify before commit** — for any anti-fabrication probe (`expected_answer: "no"`), run a deterministic `pdftotext + grep` scan for indicators of the feature *before* committing the probe. Caught a stale README guidance line during the AT pass for NIST (the README said code/protocol blocks would be probe targets; the falsification scan confirmed there are no such blocks in the source). Generalizes: anti-fab probes carry the strongest authoring risk because a missed instance silently flips the verdict on every converter.

2. **Anchor-vs-body location precision** — for footnote-content probes in regulatory and legal genres, distinguish between the page that hosts the *anchor* (superscript number in body text) and the page that hosts the *body* (footnote text at bottom margin). Caught a real ground-truth error in the FCC probe set during the AT pass: footnote 6 anchor on page 1, footnote 6 body on page 2; the probe had cited page 1 as the body location.

Both disciplines are documented at length in `docs/probe-authoring-discipline.md` (along with three pre-existing disciplines preserved from prior sprints — paired probes, PDF-visual ground truth for wild items, mechanical-rule scope of competence).

---

## What landed vs what's left

**Landed on `feature/sprint-4b-multi-converter`** (commits `1c9d365` through results-doc commit):

- ✅ Transmigration plumbing — auto-memory entries, `docs/.session-handoff.md`, CLAUDE.md session-continuity section.
- ✅ 4 wild corpus items (`scotus-loper-bright`, `fcc-numbering-order`, `nist-sp-800-63b`, `nasa-spinoff`) with per-item README + source PDF.
- ✅ 81 probes across the 4 wild items, AT-passed under Claire's red-team review.
- ✅ 3 new converters installed + smoke-tested + harnessed (docling, marker, pymupdf4llm).
- ✅ Matrix orchestrator (`scripts/run_matrix.py`) with resumability and phase split.
- 🔄 **Full 4 × 12 matrix run** — convert + score phases.
- ⏳ Per-converter three-track profiles + cross-converter comparison.
- ⏳ This results doc populated with actual numbers.
- ✅ `docs/probe-authoring-discipline.md` — methodology discoveries from Sprint 4b's AT loop.

**Deferred to Sprint 4c / v0.3.3 hardening:**

- Mechanical `paragraph-marker` rule in `scripts/rules.py`. Scope-of-competence design needs care to avoid conflating paragraph-numbered prose (FCC `13.\nRobocall-related certifications...`) with markdown numbered-list syntax. v0.3.3 hardening branch is the right home.
- Tighter italic-readability probes. Current `lb-i-f` / `fc-i-f` / `ns-i-f` / `nf-i-f` use a low-bar "any italic span?" formulation that catches only catastrophic stripping. LITM's `lt-i-f` (specific-phrase, expected=no on template-stripped italic) is more discriminating. Worth tightening per-item.

**Deferred to Sprint 5+ (corpus breadth + frontier work):**

- Additional wild corpus items beyond the 4 added here (e.g., a true OpenStax-style pedagogical textbook chapter; a more diverse popular-press sample beyond NASA Spinoff).
- Catalog v0.4 amendment if matrix data surfaces new failure modes the existing taxonomy doesn't capture.
- Empirical HTML-`<table>` Word/Pages round-trip verification (deferred from Sprint 3 §v0.3.1 hardening).
- Residual judge-stability investigation on short-phrase content probes (`lt-i-c` etc.).

---

## Sprint 4 status

- [x] Probe authoring for 4 wild items under v0.3.1 class discipline (81 probes)
- [x] AT pass on probe authoring (Claire red-team, fixes-back, sign-off)
- [x] 3 new converters installed and harnessed
- [x] Matrix orchestrator scripts (single-command full run, resumable)
- [ ] Full 4 × 12 matrix run completed
- [ ] Per-converter three-track profiles + cross-converter comparison
- [ ] AT pass on results
- [x] Methodology discoveries promoted to `docs/probe-authoring-discipline.md`
- [ ] Sprint results doc finalized (this file)

Sprint 4b closes when the matrix run lands clean profiles, the comparison narrative is written, and Claire's AT pass on the results signs off. Substack-feed summary work, if Sergio judges it due, happens in the between-sprint pause after sprint close — not as a forced gate (`feedback_sprint_cadence`).

---

## Artifacts

- `docs/failure-mode-catalog.md` — v0.3.2 (taxonomy stable; no Sprint 4b changes)
- `docs/probe-authoring-discipline.md` — **new in Sprint 4b** (methodology discoveries from probe authoring + AT loop)
- `scripts/run-eval.py` — harness v0.3.1 (unchanged)
- `scripts/rules.py` — mechanical rule checks (unchanged in Sprint 4b; `paragraph-marker` deferred to v0.3.3)
- `scripts/run_converter.py` — **new in Sprint 4b** (single-converter PDF→markdown runner)
- `scripts/run_matrix.py` — **new in Sprint 4b** (full matrix orchestrator)
- `corpus/{scotus-loper-bright,fcc-numbering-order,nist-sp-800-63b,nasa-spinoff}/` — **new in Sprint 4b** (4 wild items × {source.pdf, README.md, probes.json})
- `corpus/**/output/{mineru,docling,marker,pymupdf4llm}/` — per-converter markdown + honesty profile (matrix output)
- `docs/sprint-4-results.md` — this file
