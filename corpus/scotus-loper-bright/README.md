# scotus-loper-bright

**Genre:** legal / court filing
**Document:** *Loper Bright Enterprises et al. v. Raimondo, Secretary of Commerce*, slip opinion No. 22-451
**Decided:** June 28, 2024
**Pages:** 114 (majority + concurrences + dissents)
**License:** Public domain — work of the U.S. Supreme Court (17 U.S.C. § 105)
**Source URL:** https://www.supremecourt.gov/opinions/23pdf/22-451_7m58.pdf
**Retrieved:** 2026-04-26

## Why chosen

Sprint 4b corpus expansion targeting the legal-genre failure-mode envelope: dense footnoting, paragraph numbering, citation chains, multi-opinion structure (majority + concurrences + dissents), section headings of varied depth. The *Loper Bright* slip opinion is a structurally rich example — it overrules Chevron, runs majority + concurrence + multiple dissents with full citation density, and is widely-circulated as a representative SCOTUS document of its era.

## Probe authoring guidance

- Ground truth is the rendered slip-opinion PDF (visual). Test paragraphs from each opinion section: majority, concurrence, dissents.
- Footnotes are dense and cross-page; provenance probes should test both anchor preservation and footnote body presence.
- Section structure: *Syllabus* / *Opinion of the Court* / *Concurring opinion* / *Dissenting opinion* — heading-depth probes should test whether converters preserve this top-level structure.
- Section numbering inside opinions (Roman numerals: I, II, III with sub-headings A, B) — provenance / readability tests.
