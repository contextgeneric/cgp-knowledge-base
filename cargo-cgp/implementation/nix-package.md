# The Nix package

A [`flake.nix`](https://github.com/contextgeneric/cargo-cgp/blob/main/flake.nix) at the repository root packages `cargo-cgp` for Nix, the
supported answer for the one machine [the rustup-based flow](distribution.md) cannot serve.

A Nix user has no rustup to install a toolchain or force one, so `setup`, the preflight, and `update`
have nothing to drive. The flake sidesteps all of them. Nix itself
supplies the pinned nightly and builds both binaries against it, so provisioning is a build-time
fact rather than a runtime handshake, and the front-end runs in the unmanaged mode the
[escape hatches](distribution.md#escape-hatches-for-local-development) already provide.

Nix reconstructs by hand what a nightly bump would otherwise coordinate through crates.io. The
toolchain comes from [`oxalica/rust-overlay`](https://github.com/oxalica/rust-overlay), whose
`fromRustupToolchainFile` reads the same
[`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml)
the `build.rs` scripts read (channel plus the `rustc-dev` and `llvm-tools` components the driver
needs, and the `rust-src` the UI snapshots need; see [Testing](testing.md)), so the Nix toolchain
cannot drift from the pinned one. That toolchain is passed to `makeRustPlatform`, and
`buildRustPackage` compiles the front-end and the driver together under it, exactly as `setup`'s
`cargo +<pinned> install` does, so the driver embeds the same compiler whose sysroot and
`librustc_driver` it will later be handed.

Two `wrapProgram` wrappers replace the environment rustup would have arranged. The front-end wrapper
sets `CARGO_CGP_NO_MANAGE` so the front-end skips the preflight and toolchain forcing, sets `RUSTC`
to the toolchain's `rustc`, and prepends the toolchain to `PATH`; the wrapped `cargo check` then
compiles under the same nightly the driver embeds, and the front-end's existing
`rustc --print sysroot` discovery returns that toolchain's sysroot. Its `lib` holds the matching
`librustc_driver`, which the front-end prepends to the driver's dynamic-library path just as it does
on a managed machine. The driver wrapper adds that same `lib` directory to the driver's own runtime
search path, so the driver loads `librustc_driver` even when invoked directly rather than only
through the front-end. Both binaries land in one `bin/` directory, so the front-end's
[sibling lookup](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/driver_path.rs)
finds the driver with no override.

**The front-end wrapper needs that dylib prefix too, and for a reason peculiar to being invoked
through rustup.** `cargo cgp check` enters through rustup's `cargo` shim, which exports the
project's active toolchain's `lib` directory on the loader path for every child, so the Nix `rustc`
the front-end probes is searched against a *foreign* toolchain's libraries before its own `RUNPATH`.
That is inert while the two Rust versions differ, because a rustc shared library is named for its
version (`libLLVM.so.<n>-rust-<version>`) rather than by content hash. When they match, the names
collide: the Nix `rustc` loads rustup's copy, which wants a system library the Nix loader cannot
resolve, and exits 127 before printing a sysroot. The counter-intuitive consequence is that the
failure appears in whichever project tracks the *same* Rust version as the pinned nightly. Prefixing
the toolchain's own `lib` on the front-end wrapper (the same protection the driver has) makes its
libraries win that lookup while leaving the caller's entries after them. A rustup-managed install is
immune by construction: its probe runs through `rustup run`, which points the path at the toolchain
being queried. The user-facing account is in
[Troubleshooting](../reference/troubleshooting.md#a-nix-install-fails-its-sysroot-probe-under-cargo-cgp).

The flake's source input is deliberately narrowed with `lib.fileset` to the crate sources, the
manifests, the lockfile, `rust-toolchain.toml`, and the `LICENSE` the crates link to: everything the
build reads, plus the target of those links, and nothing else. The churny, build-irrelevant trees at
the repository root (the `tests/ui` fixtures, `README.md`, `AGENTS.md`) are excluded, so
editing them leaves the derivation's input hash unchanged and the built binaries cached; only a real
source change triggers a rebuild.

Running the check under Nix inherits the same caveat as the managed path: because the tool forces a
fixed diagnostic nightly under `-Znext-solver`, the check compiles against a compiler the project
did not choose, which is
[the accepted trade-off](distribution.md#the-pinned-toolchain-is-an-internal-detail). What Nix does
*not* provide is the lockstep-and-`update` machinery (a Nix user upgrades the tool by updating the
flake input, not through `cargo cgp update`; a nightly bump is in
[Bumping the pinned nightly](pinned-nightly-bump.md#updating-the-nix-packages-for-a-new-nightly)),
so the crates.io version handshake is simply not part of this path.

## Tests

No test in the repository builds the flake, since the package build runs no tests
(`doCheck = false`) and the UI suite needs a sibling `cgp` checkout a sandboxed build lacks.
`nix build` and `nix flake check` are the checks to run after a change to the flake or the
manifests.

## Source

- [`flake.nix`](https://github.com/contextgeneric/cargo-cgp/blob/main/flake.nix): the Nix package:
  builds both binaries under the pinned nightly from `rust-overlay` (read from
  `rust-toolchain.toml`), wraps the front-end for unmanaged mode and the driver for
  `librustc_driver` loading, and narrows the source input to the build-relevant paths.
- [`flake.lock`](https://github.com/contextgeneric/cargo-cgp/blob/main/flake.lock): the locked `nixpkgs` and `rust-overlay`
  revisions.
