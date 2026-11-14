# Writing the `cargo-cgp` documents

This guide holds the rules for writing and revising the documents on the `cargo-cgp` tool. The
knowledge base's [AGENTS.md](../AGENTS.md) holds the rules every document follows.

## Keeping a document in step with the tool

A `cargo-cgp` document changes with the tool, and its inline docs change in the same pass:

- Fix the code's inline docs in the same pass: add a one-line `///` to a public item that lacks one,
  correct a stale comment, and delete a comment that restates the code.
- Keep a source doc pointer on its knowledge-base path, such as
  `cgp-knowledge-base/cargo-cgp/implementation/driver/program.md`.
- Read the compiler source from the pinned nightly's `rustc-dev` component when `../external/rust` is
  absent.
- Read the `cgp` source but never modify it; revise the `cgp` section of this base when the two must
  agree.

## Show the example behind an error message

A quoted diagnostic comes from a real fixture, cut to the fragment that carries the point:

- Quote the fragment that carries the point, never a whole cascade.
- Distil a UI fixture's program rather than inventing a fresh one, and check the quoted output against
  its blessed `.cgp.stderr` and `.rust.stderr`.

## Implementation documents

An implementation document gives the architecture and the intention, and leaves the mechanics to the
code:

- Open with a level-one heading and a one-sentence summary, and close with Tests and Source.
- Make Tests and Source bullet lists, one item per line.
- Add a comparison with Clippy or cargo-expand only where such a tool exists; state where the design
  follows it and where it diverges.
- Split a document that grows into a directory with a `README.md`; the parent lists the directory and
  `summary.md` lists every file.
- Give the high-level concepts and architecture; leave the line-by-line mechanics to the code.
- Use a short command, argument vector, or environment snippet where it makes a behavior concrete.
- Add an optional **Further reading** section before Tests, and verify a cited URL resolves.
- Keep the code's intention, a summary for an agent that does not read the source, and the issues and
  corner cases worth attention.
- Record a gap in the comparison section where one exists, otherwise beside the behavior.
- Record a limitation beside the behavior it qualifies, and remove it when closed.

## Registering a category

A new category registers in this section's index:

- Register a new category in this section's [README.md](README.md) with its own `README.md`.
