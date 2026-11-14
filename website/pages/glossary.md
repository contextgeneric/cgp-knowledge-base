# The glossary page

The glossary defines the vocabulary the documentation uses, in one or two sentences per term, and
routes onward; it is the reference's term lookup where the index is its construct lookup.

- **URL:** <https://contextgeneric.dev/docs/reference/glossary>
- **Source:** [docs/reference/glossary.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/reference/glossary.md)
- **Status:** Current
- **How it was made:** as for the [Reference](reference.md)

## What it covers

The page sits at `sidebar_position: 91` beside the compile-errors page and covers CGP's own terms,
the Rust concepts the site assumes, and the borrowed terms the comparison pages use. It does not
overlap the index: the index's *Looking for a name you don't see?* table answers `IsPresent`, and the
glossary answers *environmental context*. It exists because the vocabulary is used far more than it
is defined: *environmental context* appears on some twenty-six pages and *blanket implementation* on
some fifty-three, so each gets one definition those pages link to.

The page's conventions:

- **Every term is an `###` directly under its section's `##`,** with no thematic grouping, because
  the MDX setup rejects `{#custom-id}` and Docusaurus anchors `h2` and `h3` only, so a grouped term at
  `h4` would lose its anchor. `toc_max_heading_level: 2` keeps the table of contents to the sections.
- **Sections are alphabetical,** since the page is looked up rather than read through.
- **Each related-concept entry's external link is one the comparison page it routes to already
  cites,** taken from that page's Sources section.

**The terms are linked from the pages that use them,** first use per page, in page bodies, with the
inline gloss left beside it: some 440 links across 176 pages. Three rules decided what stays
unlinked, and they are settled:

- **A page that owns a term does not link it;** *Bypassing coherence* does not link *coherence*.
- **A compound use is not the general term,** so *consumer blanket impl* and *provider blanket impl*
  stay unlinked and only the full *blanket implementation* links.
- **The basic vocabulary is already glossed:** every reference page glosses *context*, and
  *component*, *provider*, *wiring*, and the two trait names are the section's working words.

Terms already linked to their concept page stay pointed there, which is why *extensible variant* and
*impl-side dependency* have few glossary links.

## How it relates to the knowledge base

The specification is in [writing-guides/reference.md](../writing-guides/reference.md#the-glossary-page),
and the definitions follow [vocabulary.md](../../communication-strategy/vocabulary.md). The page
shows no code, so it has no `example-code` mirror.

## Maintaining it

- Four pages route to it, and a move updates all four: the reference index beside the compile-errors
  link, the Concepts and Comparisons indexes, and the Introduction's routing list.
- Link a new term from the pages that use it under the three rules above.
