# Distribution

This directory documents how `cargo-cgp` reaches a machine and stays in step with its pinned nightly. The
tool is two binaries and one exact nightly compiler, delivered to a user whose project builds on stable.
Start with provisioning, the path most users take. The others cover the alternative package, the
maintainer's bump, and the editor.

- [Provisioning through cargo and rustup](provisioning.md): installing both binaries in lockstep, `setup`
  and `update`, the read-only preflight in `check`, and how the design compares to Clippy.
- [The Nix package](nix-package.md): the flake for a machine without rustup, which builds both binaries
  under the pinned nightly.
- [Bumping the pinned nightly](pinned-nightly-bump.md): every consumer of the pin, and what a bump must do
  in the same change.
- [Rust Analyzer integration](rust-analyzer-integration.md): running the check on save, and the
  `target/cgp` directory that keeps it off cargo's build lock.
