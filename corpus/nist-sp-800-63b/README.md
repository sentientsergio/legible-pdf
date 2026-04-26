# nist-sp-800-63b

**Genre:** technical guideline / standards document (textbook-equivalent for failure-mode lens)
**Document:** *Digital Identity Guidelines: Authentication and Lifecycle Management*
**Publication:** NIST Special Publication 800-63B
**Pages:** 80
**License:** Public domain — work of the U.S. federal government (17 U.S.C. § 105)
**Source URL:** https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63b.pdf
**Retrieved:** 2026-04-26

## Why chosen

Sprint 4b corpus expansion targeting the textbook/technical-guideline failure-mode envelope: multi-level numbered heading hierarchy (1 → 1.1 → 1.1.1), tables (authenticator types, security characteristics, allowed operations), figures with captions, code/protocol blocks (HTTP request/response examples), bibliographies, dense cross-references to other NIST publications and IETF RFCs.

Originally Sprint 4b targeted an OpenStax textbook chapter (CC BY) for this slot. OpenStax PDF distribution requires interactive download (no clean direct URL — CDN serves 403 to direct fetches), making reproducible corpus retrieval awkward. NIST SP 800-63B is structurally equivalent for the failure-mode lens (heading hierarchy, mixed content, figures, tables, code, references) and reliably retrievable. A pure pedagogical textbook can be added in a later sprint if needed.

## Probe authoring guidance

- Ground truth is the rendered NIST PDF (visual). Test heading-depth preservation, table structure, code-block formatting.
- Authenticator-type tables (multi-column, merged headers in some) — readability probes for table syntax.
- Code/protocol blocks for HTTP/JWS/CTAP examples — readability probes for code-fence preservation.
- Bibliography section with structured citations — provenance probes for reference preservation.
- Cross-references to other SP-800 series and IETF RFCs — content + provenance probes.
