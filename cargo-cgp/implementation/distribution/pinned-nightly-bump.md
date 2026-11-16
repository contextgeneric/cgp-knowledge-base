# Bumping the pinned nightly

The bump itself is a one-line edit to the `channel` in
[`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml),
the single source of truth. Everything else derives from that file, but a new compiler forces
follow-ups in the same change.

## What derives from the pin

Both crates' build scripts bake the channel into `PINNED_TOOLCHAIN`, the driver records the compiler
that actually built it, and the Nix flake reads the same file. A test fails when the constant drifts
from the file.

One detail is easy to break. Each build script reads the pin from a copy in its own crate, never
through a workspace-relative path, because `cargo install` builds from a package tarball with no
workspace above it. The copy is `pinned-toolchain.toml`, a symlink to the workspace file that cargo
packages as a regular file. It is not named `rust-toolchain.toml`, because docs.rs deletes a crate's
`rust-toolchain.toml` before building it. Rustup reads only a file of that name or
`rust-toolchain`, so the copy selects no toolchain either.

## What a bump must do by hand

- **Fix the driver against `rustc_private` changes.** That API shifts between nightlies, which is
  why the pin is an exact date ([The driver](../driver/program.md#accessing-the-rust-compiler-api)).
- **Re-bless the UI snapshots and review the diffs,** since a new rustc can reword a diagnostic or
  move a span ([Testing](../testing.md)).
- **Run the suite under threads,** with `--threads default --iterations 3` and `--threads 8`, since
  a new rustc can change how its front end splits work between threads, and with it the order
  diagnostics arrive in ([parallel runs](../testing.md#parallel-runs)).
- **Refresh the flake,** as below.

A released tool reaches users through `setup` and `update`, which install whatever nightly the
release pins.

## Updating the Nix packages for a new nightly

`rust-overlay` knows only the nightlies its locked revision carries, so a newer date fails to find
its manifest. Run `nix flake update rust-overlay` after the edit, commit `flake.lock` in the same
change, and confirm with `nix build` and `nix flake check`.

## Tests

- [`front_end/preflight.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/preflight.rs):
  the constant matches the file.
- The [UI snapshot suite](../testing.md): fails on any diagnostic a new compiler words differently.

## Source

- [`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml):
  the pin.
- [`crates/cargo-cgp/build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/build.rs)
  and
  [`crates/cargo-cgp-driver/build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/build.rs):
  read it.
