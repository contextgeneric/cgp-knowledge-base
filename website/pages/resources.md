# Resources

Resources is the site's link directory for the CGP ecosystem: crates, tooling, tutorials, videos,
and projects.

- **URL:** <https://contextgeneric.dev/docs/resources>
- **Source:** [docs/resources.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/resources.md)
- **Status:** Current on the `v0.8.0` branch; the live page is the older list described under
  *Where it diverges*

## What it covers

The `v0.8.0` page has five groups:

- **Crates:** `cgp`, the error backends `cgp-error-anyhow`, `cgp-error-eyre`, and `cgp-error-std`,
  and `cgp-serde`, each by its crates.io entry.
- **Tooling:** `cargo-cgp`, with its install steps and the canonical qualification.
- **Tutorials:** Hello World and Area Calculation.
- **Videos:** an embedded player for the RustLab 2025 talk, linking its
  [transcript post](../blog/rustlab-2025-coherence.md).
- **Projects:** [CGP Examples](https://github.com/contextgeneric/cgp-examples) and
  [Hypershell](../../projects/hypershell/README.md).

The cgp-serde, CGP Examples, and Hypershell entries link their Projects sections. The page lists
neither the CGP Patterns book nor the Hermes SDK, which are
[legacy resources](../AGENTS.md#leave-legacy-resources-off-public-pages).

## How it relates to the knowledge base

The page is the public index of the ecosystem, so it mirrors
[sibling-projects.md](../../sibling-projects.md) for anything public. Four entries have documents
here: [hypershell](../../projects/hypershell/README.md), [cgp-serde](../../projects/cgp-serde/README.md),
[CGP Examples](../../projects/cgp-examples/README.md), and the error backends in
[projects/error/](../../projects/error/README.md). The tooling entry follows
[vocabulary.md](../../communication-strategy/vocabulary.md) for the `cargo-cgp` wording.

## Where it diverges

The live page on `main` omits `cargo-cgp`, names `cgp-error-anyhow` but not `cgp-error-eyre` or
`cgp-error-std`, lists `cgp-serde` by GitHub URL, and carries a books group with the CGP Patterns
book and the Hermes SDK among its projects. The `v0.8.0` page's changes reach readers when the branch
merges. Neither version mentions the agent skill, which
[message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these)
places beside the costs, with the front page and *Modularity Hierarchy* as the other two places.

## Maintaining it

- Keep the page an index rather than a pitch; its readers arrive interested and want routes.
- Add each new crate, tool, or Projects section in the change that publishes it.
- Leave out the CGP Patterns book and the Hermes SDK.
