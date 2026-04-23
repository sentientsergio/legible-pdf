# mixed-lists — methodology notes

## Result (2026-04-22, MinerU pipeline backend)

100% honest (10/10 probes, all unanimous N=3).

## What MinerU actually emits

Inspecting `output/source/auto/source.md`:

- **Bulleted list** (itemize) — bullet characters stripped. Items emitted as
  leading-space-prefixed siblings on separate paragraphs:
  ` Mercury` ` Venus` ` Earth`. No `-`, no `*`, no `•`.
- **Numbered list** (enumerate) — cleanly preserved as `1. Red`, `2. Green`,
  `3. Blue`. The numeral prefix carries the ordering signal directly.
- **Nested list** (itemize within itemize) — top-level bullets stripped (parent
  items ` Fruits`, ` Vegetables` appear as plain leading-space lines).
  Sub-items emit em-dash prefixes (`– Apple`, `– Banana`). No indentation
  preserved — the dash is the only nesting cue.
- **Definition list** (description) — `\item[Term]` becomes `Term description...`
  on a single line. Term-bold lost. Term/definition adjacency preserved.
- **Title** — emitted as `# Reference Items...` (h1).
- **Headings** — `## 1 Inner Planets` etc. with the section number folded into
  the heading text.

## Why probes pass anyway

Probes are phrased to accept "any clear list-presentation signal" — markdown
syntax, bullet chars, numerical prefixes, dash prefixes, indentation, term/def
adjacency, etc. Under that wording, the LLM judge correctly identifies all
four list types from MinerU's structurally-weak output.

This is honest under **LLM-reader-equivalence**: the methodology measures what
a downstream LLM reader can recover, not whether the markdown would satisfy a
markdown linter. The LLM reads ` Mercury\n\n Venus\n\n Earth` and sees a
list of three planets; it moves on.

## Methodology lesson captured

A "markdown weenie" critique — that the output is structurally weak — is not a
honesty failure. Honesty is about whether the document's information survives
the conversion. The list-ness survives, even when the list syntax does not.

A separate diagnostic axis (e.g. "structural fidelity for downstream markdown
tooling") could be defined later, but it is not what these probes test, and
the corpus does not currently fail an item for it.

## Why the source uses leak-free prose

Earlier draft of this item used phrasings like "A simple bulleted list of three
planets follows." That prose announces the structure — the LLM judge can
answer format probes from the prose alone, without ever reading the list. This
draft uses content-bearing prose ("The inner solar system contains rocky bodies
orbiting closest to the Sun.") that names the topic without describing the
form. The 100% result was reproduced under both versions, but the leak-free
version is the canonical source — it isolates the list-structure signal and
gives a cleaner diagnostic if MinerU's behavior changes in a future run.
