# AGENTS.md: the `cargo-cgp` member of the knowledge base

Read [README.md](README.md) for what this section covers. The base-wide [../AGENTS.md](../AGENTS.md)
rules apply.

## What the synchronization rule means here

- Revise the matching document in the same change as a change to the tool's behavior, its argument
  handling, the environment contract, the driver, or the crate structure.
- Verify every claim against the source before writing it.
- Fix the code's inline docs in the same pass: add a one-line `///` to a public item that lacks one,
  correct a stale comment, and delete a comment that restates the code.
- Keep a source doc pointer on its knowledge-base path, such as
  `cgp-knowledge-base/cargo-cgp/implementation/driver/program.md`.

## The external references are read-only ground truth

- Verify a claim about `rustc_driver` or Clippy against `../external/rust` or
  `../external/rust-clippy`.
- Cite them, never edit them, and never create a dependency on them.
- Keep their paths as relative filesystem references, not published links.
- Read the `cgp` source but never modify it; revise the `cgp` section of this base when the two must
  agree.

## Show the example behind an error message

- Quote the fragment that carries the point, never a whole cascade.
- Distil a UI fixture's program rather than inventing a fresh one, and check the quoted output against
  its blessed `.cgp.stderr` and `.rust.stderr`.

## Implementation documents

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

## Registering a document

- Register a document in its category's `README.md` and in [../summary.md](../summary.md) in the same
  change.
- Register a new category in this section's [README.md](README.md) with its own `README.md` and, when
  needed, an `AGENTS.md`.
- Follow the base's prose mechanics, including the backtick and lazy-reflow rules.
