# Distribution

`cargo-cgp` must run on a machine that never asked for a nightly, so distribution means delivering
two binaries and one exact nightly compiler, keeping them in lockstep, and hiding this from a user
whose project builds on stable. A `cargo install --locked cargo-cgp` installs the front-end,
`cargo cgp setup` provisions the toolchain and driver, `cargo cgp check` verifies them and forces
the nightly, and `cargo cgp update` upgrades. Related documents cover
[the Nix package](nix-package.md), [bumping the pinned nightly](pinned-nightly-bump.md), and
[Rust Analyzer integration](rust-analyzer-integration.md).

## The problem

The driver links the compiler's `rustc_private` libraries, which ship only with a nightly carrying
`rustc-dev` and whose API changes between nightlies. So the driver is tied to one dated nightly, and
three things follow:

- **Two binaries.** Only the driver links the compiler, which keeps the front-end small and ordinary
  ([why](executable-structure.md#why-two-executables)). So installing the front-end always needs a
  second step.
- **The nightly must be present,** both to build the driver and to run it.
- **The sysroot and the loaded library must match the driver,** or it crashes on a compiler it was
  not built against.

Two common fears do not apply. A `rustup update` does not break the driver, since a dated nightly is
an immutable toolchain. And the checked project need not use nightly at all.

## How similar tools solve it

Clippy avoids the problem by shipping inside the toolchain, which an out-of-tree project cannot do.
The [`rustc_plugin`](https://github.com/cognitive-engineering-lab/rustc_plugin) framework is the
model `cargo-cgp` follows: it bakes the pinned nightly into a constant, treats a nightly bump as a
breaking change, and has an installer do the toolchain setup, since
[`cargo install` ignores a bundled `rust-toolchain.toml`](https://github.com/rust-lang/cargo/issues/11036).
`cargo-cgp` differs by forcing the toolchain itself and by finding the compiler library at runtime.

## The pinned toolchain is an internal detail

`cargo-cgp` forces its own nightly for the check and never asks the project to supply it, where
`rustc_plugin`'s tools require the analyzed project to pin the same one. For a tool that mostly runs
`check`, that requirement would be an imposition on the user's repository.

The front-end sets `RUSTUP_TOOLCHAIN` on the wrapped `cargo check`. Rustup ranks that variable above
`rust-toolchain.toml`, so it wins over whatever the project pins and leaves the file untouched. The
sysroot is queried through rustup too, so the driver's embedded compiler, the injected sysroot, and
the loaded library come from one toolchain by construction.

A program could compile under the project's toolchain and fail under the pinned nightly, or the
reverse. That is an accepted trade-off of a fixed diagnostic compiler, like the
[next-solver caveat](driver.md#choosing-the-trait-solver).

## Installing the binaries

The install splits in two so that the first command has no nightly date in it. The front-end has no
compiler linkage, so it builds under the user's own toolchain, at or above the `rust-version` the
workspace sets, and it embeds the pin and the setup routine. Keep the driver a separate crate: a
second `[[bin]]` in the same package would force the whole package onto the nightly and lose this
bootstrap.

`cargo cgp setup` installs the toolchain through rustup and the driver through `cargo install`. Each
part of that second command has a reason:

- **The explicit toolchain is mandatory,** or `cargo install` builds under the active toolchain and
  fails or mis-versions.
- **`--version` is the front-end's own,** which keeps the pair in lockstep.
- **`--locked` builds the published lockfile,** including the `syn` and `prettyplease` versions
  whose output the expand snapshots pin.
- **`--root` places the driver beside the front-end,** where the lookup finds it.

## Provisioning: `setup` does the work, `check` only verifies

`check` never installs or builds anything, because a command that prints diagnostics should not
spend minutes compiling or alter toolchains as a side effect. Having `check` repair things itself
was rejected for that reason. So it runs a read-only preflight, and `setup` is the one command that
mutates.

### What the preflight verifies

The preflight answers two questions, the cheap one first, so that a driver failure can be attributed
correctly. Each failure of its checks directs the user to `setup`, except a missing rustup, which
`setup` cannot repair. Messages about the driver name its path and origin, so a stale driver on
`PATH` is not mistaken for the one `setup` placed.

**Is the pinned toolchain installed?** It asks rustup directly. Only rustup's shim honors
`RUSTUP_TOOLCHAIN`, so on a machine without rustup another `rustc` on `PATH` would answer for a
toolchain that is not there.

**Does the driver run and match?** It runs `cargo-cgp-driver --version` under the check's exact
environment, which is both a load test and a handshake. A driver from another nightly fails in the
loader, before `main`. One that loads reports its tool version, which must equal the front-end's,
and the compiler that built it, which must equal the toolchain's. In wrapper mode the same flag must
reach the real compiler for cargo's probing, so the driver answers only when run directly
([The driver](driver.md#preparing-the-argument-vector)).

Strict equality is sound only because the crates are released in lockstep: they share one version,
and a release publishes both, by hand ([Known limitations](#known-limitations)). The checks catch
what drifts after a correct install.

### Updating with `cargo cgp update`

`update` reinstalls the front-end, then runs the *new* binary's `setup`. This is the only order that
works: a release may bump the nightly, and only the new binary knows the new pin. There is no
self-replacing installer, so it stays a thin layer over cargo. These details are worth attention:

- **It reads its own path before the reinstall,** because on Linux `current_exe` afterward names the
  replaced binary `<path> (deleted)`.
- **It reads the crates.io index rather than asking cargo,** because `cargo search` and `cargo info`
  report a max version that includes pre-releases. A stable install takes only stable versions; a
  pre-release install takes any newer one, so it can reach the release it previewed.
- **A failed reinstall prints the manual commands,** whatever its cause. They exist for Windows,
  where a running executable is locked.
- **An interrupted update degrades safely,** since a new front-end against an old driver is the
  mismatch the preflight catches.
- **Network access stays on this path.** The check and the driver never use `ureq`.

`setup` and `update` take no arguments. Because both install things, each refuses any other argument
rather than ignoring it.

## Escape hatches for local development

Developing the tool means running an unreleased front-end against a just-built driver. Three
variables allow that:

- **`CARGO_CGP_DRIVER`** names a driver that sits neither beside the front-end nor on `PATH`.
- **`CARGO_CGP_NO_MANAGE`** turns off the preflight and the toolchain forcing, and trusts the
  environment's toolchain. The UI suite and the [Nix package](nix-package.md) set it.
- **`CARGO_CGP_TOOLCHAIN`** overrides the pin for `setup` and for a managed `check` or `expand`, for
  testing a bump before the constant changes. The driver must be built under it, as a `setup` with
  the same override does. It has no effect on a check with `CARGO_CGP_NO_MANAGE`, which forces no
  toolchain.

## Loading the compiler at runtime

The front-end finds `librustc_driver` by discovering the sysroot and prepending its `lib` to the
dynamic-library path ([the contract](executable-structure.md#the-environment-contract)). It prefers
this to `rustc_plugin`'s build-time rpath because it must discover the sysroot anyway, to inject the
`--sysroot` an out-of-tree driver needs.

## Comparison with Clippy

Distribution is where `cargo-cgp` cannot follow Clippy, and this is not a gap to close. Clippy's
driver is versioned with its toolchain atomically, so it gets everything here for free. `cargo-cgp`
pins a nightly instead of being built with one, installs it separately, injects a sysroot, and runs
a preflight.

## Known limitations

These limits of the managed path are accepted:

- **Publishing is manual.** A release that ships `cargo-cgp` alone leaves `setup` unable to find its
  driver.
- **Superseded toolchains stay,** unreported, since another tool may depend on that nightly.
- **Co-location falls back outside a `bin` directory.** `setup` warns and uses cargo's default
  location, which may not place the driver beside the front-end.
- **`setup` is idempotent only because** `rustup` and `cargo install` treat "already installed" as
  success.
- **The managed path assumes rustup.** Other Rust installs are out of scope, apart from
  [Nix](nix-package.md).
- **`update` reads `index.crates.io` directly,** so it ignores a configured mirror. The manual
  install still works.

## Further reading

- [`rustc_plugin`](https://github.com/cognitive-engineering-lab/rustc_plugin): the closest working
  model.
- [Overrides, in The rustup book](https://rust-lang.github.io/rustup/overrides.html): the precedence
  the forced toolchain relies on.
- [rustup#1186](https://github.com/rust-lang/rustup/issues/1186): the Windows lock behind `update`'s
  manual commands.

## Tests

Pure logic is unit-tested in
[`tests/front_end/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/tests/front_end):
the preflight's verdicts and messages, the driver lookup, `update`'s channel rule, and `setup`'s
arguments. The managed path is not in the [UI suite](testing.md), which runs unmanaged, since
installing a provisioned driver is out of scope for the source-tree test loop.

## Source

- [`crates/cargo-cgp/src/setup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/setup.rs):
  provisioning.
- [`crates/cargo-cgp/src/launch/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src/launch):
  the wrapped command and the preflight.
- [`crates/cargo-cgp/src/update/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src/update):
  `update`.
- [`crates/cargo-cgp-driver/src/version.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/version.rs):
  the `--version` record.
