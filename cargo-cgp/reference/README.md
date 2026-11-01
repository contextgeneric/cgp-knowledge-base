# cargo-cgp Reference

This directory is the reference an AI agent consults to install and use `cargo-cgp`, while
[implementation/](../implementation/README.md) documents how the tool is built. It is written by and for
coding agents and is not end-user documentation. Each document is self-contained, so read the one that
matches your need. For an agent working in or beside a `cargo-cgp` checkout, the documents favor the
**local build** over a published release, because it reflects the current code.

The tool has two commands that read your code, both compiling it through a custom `rustc` wrapper:
`cargo cgp check` presents CGP wiring errors with the root cause first, and `cargo cgp expand` shows
the Rust your CGP macros generate, with CGP's type-level constructs spelled the way you wrote them.
Installation is shaped by one fact: `cargo-cgp-driver` links the compiler's internal libraries, so
it must be built against an exact pinned nightly carrying `rustc-dev`, and the front-end must be
able to find it.

## Index

This section lists every reference document with a summary of what it explains. When you add a
document, register it here in the same change.

- [Installation](installation.md): how to install and update `cargo-cgp`. Covers the cargo path
  (`cargo install --locked cargo-cgp` followed by `cargo cgp setup` to provision the pinned nightly
  and the driver, then `cargo cgp update` to upgrade), the Nix path (running or installing the tool
  from the flake, which builds both binaries against the pinned nightly with no rustup needed),
  installing from source for development, and the platforms it is tested on.
- [Usage](usage.md): how to use `cargo-cgp` once installed. Covers the `cargo cgp check` command and
  its argument forwarding, what the check does differently from `cargo check` (the forced pinned
  nightly, the next-generation trait solver, the isolated `target/cgp` directory), how to read the
  transformed output and its `[CGP-Exxx]` codes, using the tool as a Rust Analyzer check backend,
  running it on a project outside this repository through Nix (preferring a local checkout), and the
  environment variables that override its behavior.
- [Troubleshooting](troubleshooting.md): how to diagnose a `cargo-cgp` that will not run. Covers
  isolating the failing seam (the driver `--version` load test, `cargo cgp check -v`) and the common
  failures with the exact error each prints (command and cargo-project errors, the front-end failing
  to find the driver, the driver failing to load `librustc_driver` (unset library path or a
  toolchain mismatch), the managed preflight's toolchain/driver/version verdicts, and a missing
  rustup) plus a symptom-to-section index.
