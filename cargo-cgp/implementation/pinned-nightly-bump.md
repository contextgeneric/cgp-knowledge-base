# Bumping the pinned nightly

Moving `cargo-cgp` to a newer nightly is a one-line edit plus the follow-ups a new compiler forces.
This document lists every consumer of the pin and what a bump must do in the same change. The pin's
role in [distribution](distribution.md) is the reason it exists at all.

The pinned nightly lives in exactly one place, and every consumer derives its value from there
rather than repeating it. The `channel` field of
[`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml)
is that single source of truth, so **the version bump itself is a one-line edit**: change the date
on that `channel` line (and only touch the `components`/`profile` lines if a component was renamed
upstream). Everything that needs the version reads it back from that file:

- Both crates' build scripts parse the `channel` at build time into the baked-in `PINNED_TOOLCHAIN`
  constant.
  [`cargo-cgp/build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/build.rs)
  and
  [`cargo-cgp-driver/build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/build.rs)
  both expose it as `CARGO_CGP_PINNED_TOOLCHAIN`, which `config.rs` and the driver's `version.rs`
  read with `env!`. No Rust source names the date. Each build script *searches upward* from its
  manifest directory for the first `rust-toolchain.toml`, rather than hardcoding the
  workspace-relative path, because the workspace file is not part of a package tarball: when a
  published crate is built from crates.io (a `cargo install --locked cargo-cgp`, or the
  `cargo install cargo-cgp-driver` that `setup` runs) there is no workspace above it. To keep the
  value available there, each binary crate carries a `rust-toolchain.toml` symlink to the
  workspace file (one physical file, so the single-source-of-truth property holds), which cargo
  dereferences into a real file in the tarball, and which the upward search then finds in the crate
  root. A crate's bundled `rust-toolchain.toml` does not affect the installing user's own toolchain,
  since [`cargo install` ignores it](https://github.com/rust-lang/cargo/issues/11036).
- The driver's `built-against-rustc` identity is captured automatically: its build script runs
  `$RUSTC --version` on whatever compiler cargo hands it, so the value reflects the toolchain that
  *actually* compiled the driver, with nothing to edit.
- The Nix flake reads the same file through `fromRustupToolchainFile ./rust-toolchain.toml` (see
  [The Nix package](nix-package.md)), so the flake picks up the new channel and components
  with no separate edit, subject to the one Nix follow-up below.

An automated guard means the sync cannot silently rot. The
`pinned_toolchain_matches_the_toolchain_file` test in
[`preflight.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/preflight.rs)
asserts the baked-in `PINNED_TOOLCHAIN` equals the channel it re-reads from `rust-toolchain.toml`,
so a build whose constant drifted from the file fails the test. (The dated string elsewhere in that
same test file is fixed *sample* `--version` output feeding the parser test; it is both the input
and the expected value, not the live pin, so it neither tracks the real toolchain nor needs updating
on a bump.) A bump leaves the tool version the preflight compares alone, since `cargo-cgp` and
`cargo-cgp-driver` share one through `[workspace.package]`, and the preflight's other comparison, of
the compiler, follows the new pin.

What is *not* automatic still has to happen in the same change, because a new compiler changes both
the code that links it and the diagnostics it prints. Three follow-ups round out a bump:

- **Fix the driver against `rustc_private` API changes.** The `rustc_driver`/`rustc_interface` API
  is unstable and shifts between nightlies, so the driver may not compile against the new one until
  its code is updated. This is why the pin is bumped deliberately, and it is the whole reason the
  toolchain is welded to an exact date (see
  [The driver](driver.md#accessing-the-rust-compiler-api)).
- **Re-bless the UI snapshots.** The `.cgp.stderr`/`.rust.stderr` snapshots are recorded under the
  pinned toolchain, and a new rustc can reword a diagnostic or move a span, so a bump can fail the
  UI suite until the snapshots are regenerated with
  `cargo test -p cargo-cgp-ui-tests --test ui -- --bless` and the diffs reviewed (see
  [Testing](testing.md)).
- **Provision the new toolchain for the tool's own build.** On a rustup machine, `rustup` installs
  the new dated nightly with the components the toolchain file lists on first build of it; under
  Nix, refresh the flake as below. A released tool then reaches its users through the
  `setup`/`update` flow, which installs whatever nightly the new release pins.

## Updating the Nix packages for a new nightly

Bumping the `channel` is necessary but not always sufficient for the flake, because the flake's
toolchain comes from `rust-overlay`, and `rust-overlay` only knows the nightlies its own pinned
revision carries manifests for. A date newer than the `rust-overlay` revision locked in
[`flake.lock`](https://github.com/contextgeneric/cargo-cgp/blob/main/flake.lock) will make
`fromRustupToolchainFile` fail to find the manifest, so a forward bump needs the overlay refreshed
alongside it:

- Run `nix flake update rust-overlay` (or `nix flake update` to refresh every input, including
  `nixpkgs`) after editing `rust-toolchain.toml`, so the locked overlay is new enough to resolve the
  new nightly's manifest. Commit the updated `flake.lock` in the same change as the `channel` edit,
  so the two stay consistent.
- Rebuild to confirm and to refresh the cache: `nix build .#` compiles both binaries under the new
  toolchain, and `nix flake check` evaluates the outputs. Because the source input is narrowed to
  the crate sources and `rust-toolchain.toml` (see [The Nix package](nix-package.md)), the
  `channel` edit alone changes the input hash and triggers exactly this rebuild.

A Nix user consuming the flake as an input performs the mirror of this: they run
`nix flake update cargo-cgp` in their own flake to pull the release that carries the new pin, which
is how a Nix consumer "upgrades the tool" in place of `cargo cgp update`.

## Tests

- [`crates/cargo-cgp/tests/front_end/preflight.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/preflight.rs):
  `pinned_toolchain_matches_the_toolchain_file` asserts the baked-in `PINNED_TOOLCHAIN` equals the
  channel in `rust-toolchain.toml`.
- The [UI snapshot suite](testing.md) fails on any diagnostic a new compiler words differently,
  which is why a bump re-blesses it and reviews the diffs.

## Source

- [`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml):
  the pin.
- [`crates/cargo-cgp/build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/build.rs)
  and
  [`crates/cargo-cgp-driver/build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/build.rs):
  read the pin, and the driver's also records the compiler that built it.
- [`flake.lock`](https://github.com/contextgeneric/cargo-cgp/blob/main/flake.lock): the `rust-overlay`
  revision that must know the new nightly.
