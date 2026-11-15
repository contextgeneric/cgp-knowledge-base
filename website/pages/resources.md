# Resources

Resources is the site's index of what exists around CGP outside its documentation: crates, tools, a
recorded talk, and projects, each with a line on what it is and who it is for.

- **URL:** <https://contextgeneric.dev/docs/resources>
- **Source:** [docs/resources.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/resources.md)
- **Status:** Current on the `v0.8.0` branch; the live page is the older list described under
  *Where it diverges*

## How the page was made

An agent revised the page to [the orientation guide](../writing-guides/orientation.md#resources), and
its foot carries the provenance line for documentation pages.

## What it covers

The opening names Context-Generic Programming, links the Introduction, and relates the short form
"CGP enables pluggable trait implementations in Rust" to the page's job. Four groups follow:

- **Crates:** `cgp`, the error backends `cgp-error-anyhow`, `cgp-error-eyre`, and `cgp-error-std`,
  each with the error type it sets, and `cgp-serde`, each by its crates.io entry.
- **Tools:** `cargo-cgp`, with its install steps, the Linux testing note, and the canonical
  qualification; and CGP's agent skill, linking its pages on the site and the `cgp-skills`
  repository, with what it helps with and that the reader still reviews the assistant's output.
- **Talks:** an embedded player for the RustLab 2025 talk, which scales to the column's width, and
  a link to its [transcript post](../blog/rustlab-2025-coherence.md).
- **Projects:** [CGP Examples](https://github.com/contextgeneric/cgp-examples) and
  [Hypershell](../../projects/hypershell/README.md).

The cgp-serde, CGP Examples, and Hypershell entries link their Projects sections. The page lists
neither the CGP Patterns book nor the Hermes SDK, which are
[legacy resources](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#legacy-resources),
nor the tutorials, which the Introduction's routing list carries.

## How it relates to the knowledge base

The page is the public index of the ecosystem, so it mirrors
[sibling-projects.md](../../sibling-projects.md) for anything public. Four entries have documents
here: [hypershell](../../projects/hypershell/README.md), [cgp-serde](../../projects/cgp-serde/README.md),
[CGP Examples](../../projects/cgp-examples/README.md), and the error backends in
[projects/error/](../../projects/error/README.md). The tooling entry follows
[vocabulary.md](../../communication-strategy/vocabulary.md) for the `cargo-cgp` wording, and the
skill entry follows
[message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these),
which places the skill beside the costs it can help with.

## Where it diverges

The live page on `main` omits `cargo-cgp` and the agent skill, names `cgp-error-anyhow` but not
`cgp-error-eyre` or `cgp-error-std`, lists `cgp-serde` by GitHub URL, carries a books group with the
CGP Patterns book and the Hermes SDK among its projects, and lacks a `description`. The `v0.8.0`
page's changes reach readers when the branch merges.

## Maintaining it

- Keep the page an index rather than a pitch; its readers arrive interested and want routes.
- Add each new crate, tool, talk, or Projects section in the change that publishes it, and check
  every entry when the page is touched: the crate exists under the name given, and the link
  resolves.
- Leave out the CGP Patterns book and the Hermes SDK, and links to this site's other pages apart
  from an entry's own section.
- The page is a `.md` file, which Docusaurus reads as CommonMark, so the video's `style` is a plain
  HTML attribute; a JSX style object is dropped from the output.
