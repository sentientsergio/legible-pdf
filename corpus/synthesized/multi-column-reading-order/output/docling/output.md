## Reading Order Test: Two Columns Across Pages

legible-pdf synthesized corpus

## 1 Introduction

This document is part of the legible-pdf synthesized corpus. Its purpose is to exercise reading-order preservation across two-column layouts and across page boundaries. Each numbered marker in the body below identifies a specific sentence whose order in the document is known by construction from the source. Converters that scramble reading order will produce markdown in which these markers appear out of sequence.

## 2 Body

Marker 01. The cardinal axiom of this experiment is that ordered markers must remain ordered after conversion.

Marker 02. A converter that respects two-column reading order will present marker two immediately after marker one.

Marker 03. Each marker introduces a distinct topical noun so that probes can reference content unambiguously: this sentence mentions a telescope .

Marker 04. The fourth sentence mentions a kettle , so that probes can ask whether telescope precedes kettle.

Marker 05. A common failure mode is the converter treating each column as a separate stream and reading column one of page one followed by col- umn one of page two.

Marker 06. A subtler failure mode is the converter weaving the two columns together line-by-line, producing interleaved gibberish that nominally contains all the words but in scrambled order.

Marker 07. Marker seven mentions a compass , the third distinct topical noun.

Marker 08. Marker eight begins the discussion of how layout detection typically works in pipeline-based converters.

Marker 09. A layout detector identifies bounding boxes for text regions and labels them as headings, paragraphs, columns, captions, or figures.

Marker 10. A reading-order re- solver then sorts those bounding boxes into a sequence that approximates the order a human reader would follow.

Marker 11. Marker eleven mentions a lantern , the fourth distinct topical noun.

- Marker 12. Resolution mistakes accumulate: missing one column boundary on page one cascades into wrong order for the rest of the document.
- Marker 13. The middle of the document is here. Markers below this point are intended to span at least one page break in the rendered PDF.

Marker 14. Marker fourteen mentions a harpoon , the fifth distinct topical noun.

- Marker 15. A correct readingorder resolver places marker fifteen after marker fourteen, regardless of which

## 3 Conclusion

The body above contains twenty sequential markers spanning two columns and at least one page break. Markers also embed distinct topical nouns (telescope, kettle, compass, lantern, harpoon, anchor, sextant) so that probes may ask about content order in addition to marker order.

page each occupies.

- Marker 16. Page boundaries are a second axis of failure: even when column order is right within a page, a converter may interleave pages incorrectly.

Marker 17. Marker seventeen mentions a anchor , the sixth distinct topical noun.

Marker 18. The penultimate marker tests that the converter does not truncate at page boundaries.

Marker 19. Marker nineteen mentions a sextant , the seventh distinct topical noun.

- Marker 20. The final marker, marker twenty, must appear last in the converted document. If it does not, the converter has failed reading-order preservation in some way that the previous nineteen markers may help diagnose.