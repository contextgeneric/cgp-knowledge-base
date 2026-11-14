# The front page

The front page shows what CGP does in one screen, then argues for it in a five-section essay that
ends on routes into the rest of the site.

- **URL:** <https://contextgeneric.dev/>
- **Source:** [src/pages/index.tsx](https://github.com/contextgeneric/contextgeneric.dev/blob/main/src/pages/index.tsx),
  its stylesheet `index.module.css`, and the feature cards in
  [src/components/HomepageFeatures/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/src/components/HomepageFeatures)
- **Status:** Current on the `v0.8.0` branch; the live page on `main` is the earlier landing page it
  replaces
- **How it was made:** written by an agent from this base, level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md), and revised with the author over
  several reviews, including one pass of the copy by another assistant that the agent reviewed. It
  carries no provenance line by the author's decision, the one exception the disclosure page names.
  The author's read before publication is outstanding.

## What it covers

The page is the site's only substantial React, written as its own markup on the theme's tokens
inside the Docusaurus layout. Its first screen holds the hero and the code band:

- **The hero:** the name, Context-Generic Programming, then the tag line and the reassurance line
  verbatim from [identity.md](../../communication-strategy/identity.md); an install line whose button
  copies `cargo add cgp`; the links Quickstart and "Costs and maturity", which jumps to the cost
  section; the GitHub star widget; and the hero illustration, `static/img/cgp-hero.webp`, which the
  dark theme sets on a circle of its own background colour.
- **The code band:** the encoder pair Rust rejects and the same pair under CGP, as two editor windows
  that state their verdict with a mark and a colour; the rejected window quotes rustc's `E0119`
  beneath the block; the caption ends on the pull quote "Coherence is not repealed; it is scoped."

The essay has five sections:

- **Why Rust allows this only once:** coherence as a guarantee, the workaround without CGP, providers
  as named implementations, and the context as a type that stands for an application, linking
  *Bypassing coherence* and *Consumer and provider traits*.
- **What that gives you:** the first four headline features as illustrated cards linking the pages
  [seo.md](../seo.md#the-tag-line-orients-the-reader-the-features-carry-the-searchable-words) maps
  them to, and a line linking the Overview.
- **More than trait implementations:** three linked tiles for abstract types, extensible records and
  variants, and handlers.
- **What it costs:** five labelled costs in a framed panel, with the `cargo cgp check` qualification
  word for word and the agent skill beside the learning time, then the advice to try CGP on a small
  part of a project, linking *Modularity Hierarchy*.
- **Where to go next:** five route cards, one per reader, from trying CGP to helping build it.

Each feature card has its own illustration under `static/img/features/`:
`one-interface-many-implementations.webp`, `zero-cost-abstraction.webp`, `type-safe-wiring.webp`, and
`abstract-over-every-dependency.webp`. The fifth headline feature, Still Ordinary Rust, has no card
and no image, because the reassurance line states it.

The hero's block is the retrofit shape: a value context, self-targeted, since `u64`, `String`, and
`Vec<u8>` are the data being encoded. Section 1's last paragraph introduces the application context
in prose, without code, for the reason the [homepage guide](../writing-guides/homepage.md) records.

**The page sets its own `<title>`,** *Context-Generic Programming (CGP) - Pluggable trait
implementations for Rust*, with no suffix, because the project name belongs first and Docusaurus's
formatter, which renders every other page as `{Page} | CGP — Context-Generic Programming`, can only
append. It uses `@docusaurus/Head` in `src/pages/index.tsx` and sets `og:title` alongside. Leave the
`title` prop off `Layout` there, or the page renders two title tags.

## How it relates to the knowledge base

[writing-guides/homepage.md](../writing-guides/homepage.md) specifies the page: the two tiers, the
settled example and its copy, the essay, the layout, the offload rule, and the draft checks. The
communication strategy governs the copy: [identity.md](../../communication-strategy/identity.md) for
the name, tag line, reassurance line, and curated features;
[message.md](../../communication-strategy/message.md) for the strengths and costs; and
[vocabulary.md](../../communication-strategy/vocabulary.md) for where "context" first appears.
[visual-design.md](../visual-design.md) records the tokens the page uses, including the code windows'
diff tints and verdict marks, and [seo.md](../seo.md#the-off-site-metadata-is-under-set) the title.

The page's code is compiled in the [`example-code` crate](../site.md#the-example-code-crate) at
`tests/front_page.rs`, with the rejected block as a fixture under `tests/compile_fail/front_page/`.
Its tests compare the text between the `front-page:` markers in `index.tsx` with the compiled code,
and the quoted `E0119` with the fixture's snapshot.

## Maintaining it

- Read the homepage guide before any change, and run its draft checks after one.
- Change the page's code and `tests/front_page.rs` in the same commit; a re-blessed compile-fail
  snapshot changes the quoted error as well.
- After a colour change, run `scripts/theme/contrast.py`, which checks the diff tints, the marks, and
  the quoted error's first line, and screenshot every visual change at the guide's sizes in both
  themes in Firefox and Chrome.
- The page is on the author's
  [read-in-full list](../AGENTS.md#who-drafts-a-page-and-who-reads-it-before-it-publishes), so a
  substantial change returns to the author before publication.
