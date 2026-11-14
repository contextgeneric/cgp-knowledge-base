# Introduction

The Introduction defines Context-Generic Programming in a few lines and routes readers by question to
the maintained pages.

- **URL:** <https://contextgeneric.dev/docs/>
- **Source:** [docs/index.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/index.md)
- **Status:** Current
- **How it was made:** revised by an agent using this base; the footer records the revision without
  attributing the original draft

## What it covers

The page opens with the name and the tag line whole, a contrast between plain Rust's single
implementation per type and CGP's choice per type, and the reassurance. A short list glosses
context, component, provider, and wiring, each linked to its glossary entry; the mechanism is left
to the routes below. It has no Rust listings. Its front matter sets a title without "CGP", the
sidebar label "Introduction", and a written description.

*Start here* lists the Quickstart, Hello World, and the area-calculation series in that order. *Find
what you need* gives one line per question with the page that answers it: the Overview, Bypassing
coherence and Consumer and provider traits, Modularity Hierarchy and the front page's costs, the
Comparisons, the Reference and the Glossary, `cargo-cgp`, the Projects, the AI section, Resources,
and Contribute. A closing line names the blog as a dated record.

The page has no maturity section, which belongs to the front page's cost section, per the
[homepage guide](../writing-guides/homepage.md#below-the-fold-the-bounded-essay), and it leaves out
the CGP Patterns book, a [legacy resource](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#legacy-resources).

## How it relates to the knowledge base

[Identity](../../communication-strategy/identity.md) governs the opening and
[the message](../../communication-strategy/message.md) the adoption boundaries. The terms come from
[vocabulary](../../communication-strategy/vocabulary.md) and
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md). The learning paths
lead to the [Hello World](../tutorials/hello-world.md) and
[area-calculation](../tutorials/area-calculation.md) teaching contracts.

## Maintaining it

- Keep the page short, and leave the maturity discussion to the front page.
- Define context as a type that stands for one set of choices, as
  [vocabulary](../../communication-strategy/vocabulary.md) glosses an environmental context.
- Key each route on a question, and check every route when a page moves.
- Keep plain trait implementations distinct from providers, and route new code to the maintained
  tutorials and reference pages.
