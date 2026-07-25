# AGENTS.md — the `cargo-cgp` member of the knowledge base

This file governs how to write and maintain the documents in this directory, which document the
`cargo-cgp` toolchain. Read [README.md](README.md) first for what this section covers and how it is
organized, the base-wide [../AGENTS.md](../AGENTS.md) for the rules every section shares — the
synchronization rule, the dual-reader prose style, document-the-present, how links are written, the
backtick discipline, and how a document registers itself — and the member project's own
[AGENTS.md](https://github.com/contextgeneric/cargo-cgp/blob/main/AGENTS.md) for the code itself. The
rules below add what is specific to documenting this tool; a category may add more in its own
`AGENTS.md` (the implementation category does, in [implementation/AGENTS.md](implementation/AGENTS.md)).

The member project is [`cargo-cgp`](https://github.com/contextgeneric/cargo-cgp), and
[../sibling-projects.md](../sibling-projects.md) says where to find it and which revision to read.

## What the synchronization rule means here

The base-wide [synchronization rule](../AGENTS.md#the-synchronization-rule) lands on the tool's own
moving parts. When you change how the tool behaves — its argument handling, the environment variables
the executables agree on, the way the driver drives the compiler, the crate or module structure —
revise the matching document in the same change, and verify every claim against the source before you
write it rather than transcribing another document.

The rule extends to the code's own inline documentation, which lives in the member repository. Reading
a module closely enough to document it is exactly when to fix its inline docs, so in the same pass add
a one-line `///` to any public item that lacks one, correct a comment that no longer matches the code,
and delete a comment that only restates the obvious. Keep inline docs terse and leave the deeper
reasoning to the knowledge base; a one-line doc comment that links out to a document beats a paragraph
inlined in the source. A doc pointer in source names the document by its knowledge-base path
(`cgp-knowledge-base/cargo-cgp/implementation/driver.md`), since the two now live in separate
repositories.

## The external references are read-only ground truth

`cargo-cgp` is modeled on Clippy and built against the compiler's internal API, and both are
available as local sources: the Rust compiler at [`../external/rust`](../../external/rust) and
Clippy at [`../external/rust-clippy`](../../external/rust-clippy). When a document makes a claim
about how `rustc_driver` behaves or how Clippy does something, verify it against those sources
rather than from memory, since the compiler's internals shift between nightlies. Treat them as
read-only: cite them, do not edit them, and do not create a dependency on them. Their paths are
filesystem references to local checkouts rather than published links, which is why they stay relative
where a link to a sibling project would be a GitHub URL. The `cgp` project is different in kind: the
tool reads its source but never modifies it, while its *documentation* — the [`cgp` section](../cgp/README.md)
of this base — is revised alongside a change here whenever the two must agree.

## Show the example behind an error message

Every document here quotes diagnostics, so the base-wide rule to
[show the example behind an error message](../AGENTS.md#show-the-example-behind-an-error-message)
bites hardest in this section: a reader who meets a rewritten `[CGP-Exxx]` headline must be able to see,
in the same document, the small program that triggers it and the mistake it is really about. Two
habits follow. Quote the *fragment* that carries the point rather than a whole cascade, since a pasted
multi-screen diagnostic bloats a document and rots the moment the wording shifts. And where a
[UI fixture](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/README.md) already pins the
behavior, prefer distilling that fixture's program into the document over inventing a fresh one — the
fixture's blessed `.cgp.stderr` and `.rust.stderr` are then the evidence the quoted output is current.

## Registering a document

Every document registers itself in its category's `README.md` catalog, and in
[../summary.md](../summary.md), in the same change that creates it, so neither is ever behind the
tree. When you add a whole category, create its directory with a `README.md`, give it an `AGENTS.md`
if it needs rules of its own, and register the category in this section's [README.md](README.md). The
base-wide [prose mechanics](../AGENTS.md#prose-mechanics) — the backtick discipline this section's
long diagnostic snippets make especially easy to break, and the lazy-reflow rule for over-long lines
— apply to every document here and to inline doc comments in the source.
