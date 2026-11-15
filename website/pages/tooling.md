# Tooling

The Tooling section's index introduces the programs a reader runs beside the `cgp` library and holds
`cargo-cgp`'s pages.

- **URL:** <https://contextgeneric.dev/docs/tooling/>
- **Source:** [docs/tooling/index.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/tooling/index.md)
- **Status:** Current

## How the page was made

An agent wrote the page when the author asked for a Tooling section after the reference, holding
`cargo-cgp` and saying that more tooling will be added. Its foot carries the provenance line for
documentation pages.

## What it covers

The opening names Context-Generic Programming beside the fact that CGP is a library built with
ordinary cargo commands, and says the tools are optional. It leaves out the tag line, because the
section's subject is not choosing an implementation. The *cargo-cgp* section describes the tool with
the canonical sentence from
[vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each)
and links the installation, check, reading, and error-codes pages. *More tools to come* says
`cargo-cgp` is the only tool so far and that more tooling will be added.

## How it relates to the knowledge base

The section follows [information-architecture.md](../information-architecture.md#the-target-page-inventory)
and [writing-guides/tooling.md](../writing-guides/tooling.md#the-section-shape). The tool's pages
have their own record, [cargo-cgp.md](cargo-cgp.md).

## Where it diverges from the guide

- none

## Maintaining it

- The section is `docs/tooling/` at position 7, after the reference. `cargo-cgp`'s pages sit under
  `docs/tooling/cargo-cgp/` and keep their `/docs/cargo-cgp/` URLs through `slug` front matter, as
  [cargo-cgp.md](cargo-cgp.md#what-a-later-revision-must-know) explains.
- Give each new tool a section here that links its pages, and revise *More tools to come* when it
  stops being true.
