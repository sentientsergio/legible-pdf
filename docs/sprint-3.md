# Sprint 3: Probe Discipline + Targeted Synthesis + Reading-Order Coverage

**Status:** in progress (started 2026-04-22, after Sprint 2 ship)

## Why this sprint

Sprint 2 shipped a working pipeline (probes → MinerU → harness → honesty
profile) but exposed three things blocking further measurement:

1. **Probe quality is the bottleneck.** The 10-probe set had two known design
   defects: conflated probes (content-presence vs format-preservation) and
   judge-judgment-sensitive probes. Adding more converters or wild-corpus items
   is wasted effort if probes are silently flawed.

2. **Catalog coverage is opportunistic.** The wild corpus exercises whatever
   happens to be in Lost in the Middle. The catalog has cells (depth-3+
   headings, definition lists, mixed-content tables, formatted-text-in-footnote,
   multi-column reading order, etc.) the wild corpus doesn't cover.

3. **Reading order is a Layer 0 capability with zero probe coverage.** Many
   converters fail on multi-column layouts; we have no way to detect that.

Synthesis — concretely de-risked in Sprint 2's `experiments/source-fidelity-test/`
— solves all three at once. We can author PDFs that deliberately exercise
specific cells, derive probes by construction (source we control = ground
truth tight), and apply the new probe disciplines from the start.

## Goal

Produce a small synthesized corpus (~5-6 PDFs) that deliberately exercises
catalog cells underrepresented in wild documents, including reading order,
with probes authored under the new disciplines. Re-run MinerU against the
new corpus and against the rewritten Lost-in-the-Middle probes. Update the
catalog with the failure-mode cells the synthesized corpus actually exposes.

## Scope

### 1. Synthesized corpus items

Each item is one `.tex` (stock `article.cls`), one rendered PDF, one
`probes.json`, and one MinerU output.

Initial cell selection (subject to refinement as we author):

| Item | Catalog cells exercised |
|------|--------------------------|
| `multi-column-reading-order` | Layer 0 reading order across columns and pages |
| `nested-headings-deep` | heading depth 3+, nesting preservation |
| `mixed-lists` | bullet, numbered, definition, nested list combinations |
| `formatted-text-in-context` | italic, bold, inline code, in body / footnote / table cells |
| `tables-and-captions` | mixed-content tables (text + bold + numbers + math), captions, table refs |
| `code-blocks-and-images` | verbatim block, image with caption, block quote |

Authored at `corpus/synthesized/<item-name>/`:
- `source.tex` — source we control
- `paper.pdf` — rendered output (eyeball-verified)
- `probes.json` — probes authored by construction
- `output/<converter>/...` — converter results
- `metadata.json` — what cells this item exercises

### 2. Probe disciplines (apply to all new + retrofit existing)

**(a) Pair format-preservation with content-presence.** Every probe asking
"is X formatted as Y?" must be paired with "is X present at all?" If both
fail, the converter dropped content. If only the format probe fails, the
converter preserved content but lost formatting. Both are honest losses, but
they're different failure modes.

**(b) Unambiguous wording.** Probe questions must specify the observable
structure unambiguously, leaving no judge-interpretation room. Where two
defensible interpretations exist (e.g. "is this a subsection?" — markdown
depth or numbering convention?), pick one explicitly in the question.

**(c) N=3 unanimous-agreement.** Every probe runs N=3 times. If all three
runs agree, record the agreed answer. If any disagree, record `disputed:run1=X,run2=Y,run3=Z`
in the result. Disputed probes are a probe-quality signal — they should be
either rewritten for unambiguity or kept with a flag indicating known
sensitivity.

### 3. Harness update

`scripts/run-eval.py` extended to:
- Run each probe N times (default N=3, configurable)
- Record per-run answers + agreement status
- Honesty profile schema gains `agreement` field per probe
- Score only counts unanimous-agreement probes (disputed probes are
  reported separately, not folded into the rate)

### 4. Lost-in-the-Middle retrofit

The existing 10 probes get rewritten under the new disciplines:
- `cap-001` heading nesting → split into "is `Models` present?" + "what
  markdown depth is `Models` emitted at?" with explicit depth answer
- `cap-005` inline_code → replaced with paired probes for content-presence
  and format-preservation on `0613`
- Reading-order probe added: "Does paragraph A appear before paragraph B?"
- All probes run N=3

### 5. Catalog refresh

After re-running MinerU against the new corpus, fold any newly observed
failure modes into `docs/failure-mode-catalog.md`. Specifically expected:
- Layer 0 entries for column scramble, page interleaving
- Layer 1 entries for whatever new cells the synthesized PDFs exposed

## Out of scope (for this sprint)

- Multi-converter comparison (Sprint 4 — adds docling, marker, etc.)
- Definedness probe (Sprint 6 — requires converters that emit `undefined`)
- `legible-ir` formalization (deferred per non-negotiable #3)
- Public methodology writeup
- Probe-generation tooling (probes still manually authored from catalog cells)

## What this sprint teaches

- Whether probe-by-construction yields a materially cleaner probe set than
  wild-corpus-derived probes
- What MinerU's failure modes actually are once exercised systematically
  rather than opportunistically
- First measured signal of probe-set repeatability (N=3 unanimous-agreement
  discipline)
- Whether the harness CLI + JSON shape want to change once we have multiple
  PDFs in play
- Whether the catalog needs structural revision once we have cell-by-cell
  failure data

## Order of operations

1. ✅ Write this spec (`docs/sprint-3.md`)
2. Author `corpus/synthesized/multi-column-reading-order/` first — biggest
   coverage gap, easiest to author by construction
3. Update harness to support N=3 + agreement field
4. Author probes for multi-column item (paired, unambiguous, N=3-ready)
5. Run MinerU + harness; capture results
6. Author remaining 4-5 synthesized items
7. Retrofit Lost-in-the-Middle probes
8. Catalog refresh
9. Sprint 3 results writeup; ship

Items 2-5 form the smallest end-to-end (one item, full pipeline) — useful
to land first as a vertical slice before broadening.
