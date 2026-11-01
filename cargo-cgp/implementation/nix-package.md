# The Nix package

A [`flake.nix`](https://github.com/contextgeneric/cargo-cgp/blob/main/flake.nix) packages
`cargo-cgp` for the one machine [the rustup-based flow](distribution.md) cannot serve. A Nix user
has no rustup, so `setup`, the preflight, and `update` have nothing to drive. Instead Nix builds
both binaries under the pinned nightly, and the front-end runs in
[unmanaged mode](distribution.md#escape-hatches-for-local-development). Provisioning becomes a
build-time fact, and a user upgrades by updating the flake input.

## Design points

- **The toolchain cannot drift.** `rust-overlay` reads the same `rust-toolchain.toml` as the build
  scripts, so the driver embeds the compiler whose sysroot it is later handed.
- **Two wrappers replace what rustup would arrange:** the front-end's selects unmanaged mode and the
  toolchain, and the driver's finds `librustc_driver`, so it also loads when run directly.
- **The source input is narrowed** to what the build reads, so editing a fixture or a document keeps
  the built binaries cached. A file the build starts reading must be added to that list.

## A library collision the front-end wrapper prevents

The front-end wrapper also prefixes the toolchain's `lib` on the dynamic-library path, and removing
it breaks only some projects. `cargo cgp check` enters through rustup's `cargo` shim, which puts the
project's active toolchain first on the loader path. A rustc shared library is named for its Rust
version, not by hash, so this is harmless until the two versions match. Then the Nix `rustc` loads
rustup's copy and exits 127 before printing a sysroot. So the failure appears only in a project
tracking the same Rust version as the pin. A rustup-managed install is immune, since its probe runs
through `rustup run`. The user-facing account is in
[Troubleshooting](../reference/troubleshooting.md#a-nix-install-fails-its-sysroot-probe-under-cargo-cgp).

## Tests

No test builds the flake, because the package build runs no tests and the UI suite needs a sibling
`cgp` checkout a sandboxed build lacks. These commands are the checks to run after changing the
flake or the manifests:

- `nix build`: builds and wraps both binaries.
- `nix flake check`: evaluates the outputs.

A nightly bump needs
[one more step](pinned-nightly-bump.md#updating-the-nix-packages-for-a-new-nightly).

## Source

- [`flake.nix`](https://github.com/contextgeneric/cargo-cgp/blob/main/flake.nix): the package and
  its wrappers.
- [`flake.lock`](https://github.com/contextgeneric/cargo-cgp/blob/main/flake.lock): the locked
  revisions.
