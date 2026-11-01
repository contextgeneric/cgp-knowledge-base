# Bumping the pinned nightly

The bump itself is a one-line edit to the `channel` in
[`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml),
the single source of truth. Everything else derives from that file, but a new compiler forces
follow-ups in the same change.

## What derives from the pin

Both crates' build scripts bake the channel into `PINNED_TOOLCHAIN`, the driver records the compiler
that actually built it, and the Nix flake reads the same file. A test fails when the constant drifts
from the file.

One detail is easy to break. A build script searches *upward* for the file, because a package
tarball has no workspace above it, and each binary crate carries a symlink that cargo dereferences
into the tarball. A workspace-relative path would break `cargo install`. The bundled file does not
affect the installer's toolchain, since
[`cargo install` ignores it](https://github.com/rust-lang/cargo/issues/11036).

## What a bump must do by hand

- **Fix the driver against `rustc_private` changes.** That API shifts between nightlies, which is
  why the pin is an exact date ([The driver](driver.md#accessing-the-rust-compiler-api)).
- **Re-bless the UI snapshots and review the diffs,** since a new rustc can reword a diagnostic or
  move a span ([Testing](testing.md)).
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
- The [UI snapshot suite](testing.md): fails on any diagnostic a new compiler words differently.

## Source

- [`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml):
  the pin.
- [`crates/cargo-cgp/build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/build.rs)
  and
  [`crates/cargo-cgp-driver/build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/build.rs):
  read it.
