# nasa-spinoff

**Genre:** popular-press article / magazine
**Document:** *NASA Spinoff 2025*
**Pages:** 56
**License:** Public domain — work of the U.S. federal government (17 U.S.C. § 105)
**Source URL:** https://ntts-prod.s3.amazonaws.com/t2p/prod/spinoff/NASA.Spinoff_2025_508.pdf
**Retrieved:** 2026-04-26

## Why chosen

Sprint 4b corpus expansion targeting the popular-press / magazine-layout failure-mode envelope: multi-column flow with image-rich features, photographic and illustrated assets with captions, sidebar callouts, varied feature lengths (single-page profiles, multi-page deep-dives), cover headlines and pull quotes. NASA Spinoff is published annually as the agency's tech-transfer magazine — its layout is genre-faithful (it reads like a magazine) and the publication is public-domain US government work.

The 56-page magazine is sized for end-to-end converter testing. For probe authoring, target representative articles rather than the full publication: a single feature article exercises the multi-column reading-order question; a profile page exercises image+caption pairing.

## Probe authoring guidance

- Ground truth is the rendered Spinoff PDF (visual). Reading-order is the core question for the magazine layout — does the converter produce a coherent left-to-right top-to-bottom traversal of multi-column articles?
- Image+caption pairing — does the converter associate captions with their images, or scatter them?
- Pull quotes / sidebars / callouts — readability probes for whether these are inlined into body text (lossy) vs marked as quote/aside (preserved).
- Multi-column flow within a feature article — Layer 0 reading-order probes (cf. `corpus/synthesized/multi-column-reading-order/`).

## File-size note

The PDF is ~52 MB (image-heavy). Converters may take longer to process; converter outputs are markdown only (small) so probe runs are fast.
