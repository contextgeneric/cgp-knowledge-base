# The `cargo-cgp` toolchain

This directory documents `cargo-cgp`, the cargo subcommand that makes CGP's compiler errors readable
and shows the Rust that CGP macros generate. It is one member section of the
[CGP knowledge base](../README.md), and its purpose is to record how the tool works — how it is
structured, why it is built the way it is, and how it integrates with cargo and the Rust compiler — so
that an agent can pick up the work from where the last one left off without re-deriving that
understanding from the source each time. The
[AGENTS.md](https://github.com/contextgeneric/cargo-cgp/blob/main/AGENTS.md) at that project's
repository root orients an agent in the code; this section is the durable, version-controlled record
that goes deeper and stays in sync with it.

The member project is [`cargo-cgp`](https://github.com/contextgeneric/cargo-cgp), and
[../sibling-projects.md](../sibling-projects.md) says where to find it and which revision to read.
Because CGP is the tool's subject matter, this section leans on the [`cgp`](../cgp/README.md) section
next door — above all its [error catalog](../cgp/errors/README.md), the map of every error class the
tool recognizes or should.

## Why this exists

`cargo-cgp` integrates with two moving targets — cargo's subcommand and wrapper protocol, and the
compiler's unstable `rustc_driver` API — and neither is self-documenting from the source alone.
Reading [`crates/cargo-cgp`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp)
and
[`crates/cargo-cgp-driver`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver)
tells you *what* each function does, but not why the two-executable split exists, why the front-end
must compute a sysroot the driver could seemingly find itself, or how the design compares to the tool
it is modeled on. That reasoning has to be reconstructed by whoever reads the code next, so these
documents capture it once, in prose — which is why they carry design rationale as prominently as
description.

They are also a contract. When an agent changes how the tool is structured — the argument handling,
the environment variables the two executables agree on, the way the driver accesses the compiler — the
matching document is where the intended new behavior is stated in plain language, so a reviewer can
compare the prose against the code. Documentation that drifts out of sync with the code is worse than
none, so keeping it accurate is a hard requirement of any change; this section's own rules live in
[AGENTS.md](AGENTS.md), on top of the base-wide rules in [../AGENTS.md](../AGENTS.md).

## How it is organized

This section is divided into categories, and it will grow to hold more as the tool does. Each category
answers a different question, so a reader picks the one that matches their need rather than reading in
sequence.

There are three categories. The [reference/](reference/README.md) directory is the *usage* guide —
how to install, update, and use the tool — for an agent running or explaining `cargo-cgp` rather than
changing it (it is agent-internal, like the rest of the knowledge base; documentation for human end
users is kept separate); its [index](reference/README.md#index) lists every reference document. The
[implementation/](implementation/README.md) directory documents the *internals* of the tool — how
each executable is built, how they cooperate, and how the driver reaches the compiler — for an agent
reviewing, debugging, or extending the source. Its
[catalog](implementation/README.md#catalog) indexes every implementation document and tracks which
parts of the tool are covered.

The [issues/](issues/README.md) directory is the third category, and it tracks *work* rather than
describing the tool: the problems `cargo-cgp` is meant to solve but does not yet, foremost the CGP
error classes it does not yet handle. Every issue is backed by a fixture under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui) that reproduces it — a
class with no reproducing fixture counts as resolved — and the issues split along one axis, whether
the root cause is recoverable from the tool's output at all.
[Hidden root cause](issues/hidden-root-cause.md) is the tool-oriented sufficiency question: the
cases where no downstream consumer could identify the root cause from the output alone.
[Usability issues](issues/usability.md) is the human-oriented readability question: output that
carries the cause but buries it, foremost overly verbose messages. Unlike the other categories, its
entries describe absent behavior and are deleted as the tool closes each gap.

Alongside those two directories sits one standalone top-level document, [error-code.md](error-code.md):
the catalog of the `CGP-E` error codes `cargo-cgp` stamps on a main message it rewrites into a
recognized CGP error class — what each code means, what triggers it, and how to fix it — and the
record of the rewrites that carry no code. It is user-facing where the two directories are
internals-facing, so it sits beside them rather than inside a category. The
[`cgp` error catalog](../cgp/errors/README.md) cites it from every class's *How cargo-cgp presents it*
section, which is the seam where the two member sections meet: `cgp` owns the anatomy of an error class,
`cargo-cgp` owns the code it stamps on the message it rewrites that class into.

As the tool grows more moving parts, expect further categories and documents to appear. The
`reference/` category will grow a fuller reference for the CGP error classes the tool learns to
recognize (drawing on the [CGP error catalog](../cgp/errors/README.md) next door) alongside
its installation and usage guides. Add a category by creating its directory with a `README.md` and
registering it here in the same change, and record its documents in
[../summary.md](../summary.md); add a standalone document (like `error-code.md`) the same way.
