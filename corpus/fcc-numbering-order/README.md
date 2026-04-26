# fcc-numbering-order

**Genre:** regulatory filing / agency order
**Document:** *Numbering Policies for Modern Communications; Telephone Number Requirements for IP-Enabled Service Providers; Implementation of TRACED Act Section 6(a)* — Third Report and Order and Third Further Notice of Proposed Rulemaking
**Adopted:** December 18, 2025
**Released:** December 19, 2025
**FCC document number:** FCC 25-86
**Pages:** 34
**License:** Public domain — work of the U.S. federal government (17 U.S.C. § 105)
**Source URL:** https://docs.fcc.gov/public/attachments/FCC-25-86A1.pdf
**Retrieved:** 2026-04-26

## Why chosen

Sprint 4b corpus expansion targeting the regulatory-genre failure-mode envelope: numbered paragraph structure (¶ N), Roman-numeral section hierarchy with deeply-nested A/B/C/i/ii sub-headings, dense cross-references both internal (¶ N supra/infra) and external (47 CFR § N, prior FCC orders), tables of fee schedules / rule changes, formal docket-and-caption headers. FCC Reports and Orders are the canonical genre exemplar.

## Probe authoring guidance

- Ground truth is the rendered FCC PDF (visual). Test paragraph numbering preservation, cross-reference resolution, and table structure.
- Dense footnoting — provenance probes for footnote anchors and bodies.
- Cross-references to other FCC docket numbers and CFR sections — provenance probes for citation preservation.
- Roman-numeral / lettered section hierarchy — readability probes for heading-depth preservation.
