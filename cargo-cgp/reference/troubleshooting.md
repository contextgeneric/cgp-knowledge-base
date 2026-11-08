# Troubleshooting

`cargo-cgp` is two binaries plus an exact pinned nightly compiler, held together only by a
sibling-path lookup and a couple of environment variables, so when it misbehaves the fault can sit
at any of several seams. The front-end may fail to find the driver; the driver may fail to load the
compiler library it links; the driver, the installed toolchain, and the front-end may drift out of
step; or the check may simply be run in the wrong place. This document walks the common failures
with the **exact error each prints**, what it means, and how to fix it, so an agent can match a
symptom to a cause quickly. It builds on the driver-level debugging tools in
[Usage](usage.md#calling-the-driver-directly-debugging).

## The moving parts, and where they can break

Three things must line up for a check to run, and each is a place a failure can originate. The
**front-end** (`cargo-cgp`) is the cargo subcommand you invoke; it locates the **driver**
(`cargo-cgp-driver`) as a sibling in the same directory (or via the `CARGO_CGP_DRIVER` override) and
wires it in as cargo's compiler wrapper. The driver links the compiler's internal `librustc_driver`
dynamically, so that library, belonging to the **pinned nightly** the driver was built against, must
be on the loader's search path when the driver runs, and the sysroot handed to it must belong to
that same nightly. The full contract is in
[Executable structure](../implementation/executable-structure.md#the-environment-contract); the
point for troubleshooting is that a mismatch between *the nightly the driver embeds* and *the
toolchain present at run time* is the single most common root cause, and several different-looking
errors trace back to it.

## Isolating the failure

Two probes narrow almost any failure to the right seam before you read the sections below. First,
run the driver's own version query, which loads the compiler library before printing and so doubles
as a load test:

```sh
cargo-cgp-driver --version
```

If that fails, the problem is the driver or its library path, not the front-end; jump to
[The driver cannot load the compiler library](#the-driver-cannot-load-the-compiler-library). If it
succeeds, run the check verbosely to see exactly how the front-end invokes the driver and where it
stops:

```sh
cargo cgp check -v
```

The `Running` lines, each showing a `cargo-cgp-driver … rustc …` command, are the driver being
called; an error before them is a front-end or preflight problem, and an error from one of them is a
driver or compiler problem. [Usage](usage.md#calling-the-driver-directly-debugging) covers running
that printed command in isolation.

## The command itself fails

The simplest failures never reach the driver. If you invoke an unknown subcommand, the front-end
says so and lists the four it accepts:

```text
error: no such command: `frobnicate`

help: the commands are `check`, `expand`, `setup`, and `update`
```

The fix is to use one of those four. Running the tool with no subcommand at all is not an error: it
prints the same overview as `cargo cgp --help`. Note that `cargo cgp check` reaches the same
entrypoint as a direct `cargo-cgp check`: cargo inserts the `cgp` token, which the front-end strips.
An `` error: no such command: `cgp` `` comes from cargo instead: cargo found no `cargo-cgp` on
`PATH`, so the tool is not installed or not on this shell's `PATH`.

If the check runs outside a cargo package, the error comes from cargo, not `cargo-cgp`, because the
front-end forwards to `cargo check`:

```text
error: could not find `Cargo.toml` in `/some/dir` or any parent directory
```

Run the command from inside the package or workspace you mean to check. And if cargo itself is not
on `PATH`, the front-end reports that while trying to launch the wrapped build:

```text
error: failed to run `cargo check` (is cargo on PATH?)

Caused by:
  No such file or directory (os error 2)
```

The front end prints its own errors as cargo does: the message after `error:`, then each underlying
cause, here the operating system's, under a `Caused by:` of its own. This case is hard to reach in
practice: the managed preflight runs rustup first, so a machine missing cargo usually fails there
instead, with the `rustup was not found on PATH` message in
[the preflight section](#the-managed-preflight-rejects-the-setup).

## The front-end cannot find the driver

The front-end expects the driver beside it, so a driver that is missing, or a `CARGO_CGP_DRIVER`
override pointing at the wrong path, fails at the point the driver would be launched, but the
message differs by mode. In **managed** mode the preflight catches it first and names
`cargo cgp setup`:

```text
error: failed to run the cargo-cgp-driver (none is beside cargo-cgp or on PATH): No such file or directory (os error 2)

help: run `cargo cgp setup`
```

In **unmanaged** mode (`CARGO_CGP_NO_MANAGE` set, as on the from-source and Nix paths) there is no
preflight, so the bad path reaches cargo, which reports it as a wrapper it could not execute:

```text
error: could not execute process `/path/to/cargo-cgp-driver …/rustc -vV` (never executed)

Caused by:
  No such file or directory (os error 2)
```

Either way the fix is to make the driver reachable: run `cargo cgp setup` to reinstall it beside the
front-end (managed), point `CARGO_CGP_DRIVER` at the real driver binary (for a from-source build,
`target/debug/cargo-cgp-driver`), or run through the Nix flake, which places both binaries together.
Keep the driver and front-end in the same directory unless `CARGO_CGP_DRIVER` says otherwise: the
front-end looks for the driver beside its own executable first, and only when none is there falls
back to the first `cargo-cgp-driver` on `PATH`, which may be a stale one from another install. Every
preflight message names the driver it ran and where it was found, so such a driver reads
`the cargo-cgp-driver at /nix/profile/bin/cargo-cgp-driver (found on PATH, since none is beside cargo-cgp)`.

## The driver cannot load the compiler library

This is the most common and most confusing failure, because the driver aborts *before* its own code
runs and the message comes from the operating system's loader:

```text
cargo-cgp-driver: error while loading shared libraries: librustc_driver-a1ed262f84b24882.so: cannot open shared object file: No such file or directory
```

The driver links `librustc_driver-<hash>.so` from the pinned nightly, and the `<hash>` is fixed at
build time to that exact nightly. The error means the loader cannot find *that* library, which has
one of two causes.

The first cause is that **the library path is simply not set**: you ran the driver directly without
the search-path setup the front-end normally provides. A Nix-built driver has the path baked into
its wrapper and does not hit this; a from-source driver run by hand does. Provide the pinned
toolchain's `lib` directory on the loader path (`DYLD_FALLBACK_LIBRARY_PATH` on macOS,
`LD_LIBRARY_PATH` elsewhere):

```sh
SYSROOT=$(rustc --print sysroot)                        # under the pinned toolchain
LD_LIBRARY_PATH=$SYSROOT/lib cargo-cgp-driver --version
```

The second cause is a **toolchain mismatch**: the library path is set, but to a *different*
toolchain than the one the driver was built against, so the exact `librustc_driver-<hash>.so` is
absent from it. This happens when an unmanaged check runs under a toolchain that is not the
driver's pinned nightly: the driver embeds, say, `nightly-2026-11-05`, but the ambient toolchain is
`stable`, so cargo's first probe of the wrapper aborts:

```text
error: process didn't exit successfully: `…/cargo-cgp-driver …/stable/…/rustc -vV` (exit status: 127)
--- stderr
…/cargo-cgp-driver: error while loading shared libraries: librustc_driver-a1ed262f84b24882.so: cannot open shared object file
```

The fix is to run under the pinned nightly. Managed mode forces this for you; in unmanaged mode make
the pinned nightly the active toolchain (run inside the `cargo-cgp` checkout, whose
`rust-toolchain.toml` selects it, or set `RUSTUP_TOOLCHAIN` to it), or use the Nix flake, which
forces the matching nightly regardless of the directory. The `--version` line the driver prints on
success names both the `pinned-toolchain:` it needs and the `built-against-rustc:` it was compiled
with, which is the fastest way to see which nightly a driver actually wants.

## The managed preflight rejects the setup

Before a managed check, the front-end runs a read-only preflight that verifies the toolchain and the
driver, and each failure it can repair ends with a `help` naming `cargo cgp setup` as the fix (the
design is in [Distribution](../implementation/distribution/provisioning.md#what-the-preflight-verifies)). The
messages tell the cases apart, in the order the preflight checks them. Each message about the driver
names the driver's path and where it was found: from `CARGO_CGP_DRIVER`, beside `cargo-cgp`, or on
`PATH`.

If the pinned toolchain is not installed, the preflight stops before even reaching the driver and
quotes rustup's own reason, indented so its `error:` and `help:` lines read as rustup's:

```text
error: toolchain `nightly-2026-11-05` is not available:

  error: toolchain 'nightly-2026-11-05-x86_64-unknown-linux-gnu' is not installed
  help: run `rustup toolchain install nightly-2026-11-05-x86_64-unknown-linux-gnu` to install it

help: run `cargo cgp setup`
```

On a machine with no rustup at all, the preflight says so instead, because it queries the toolchain
through rustup and `setup` needs rustup too:

```text
error: rustup was not found on PATH, and cargo-cgp installs and selects its toolchain `nightly-2026-11-05` through rustup

help: install rustup, or install cargo-cgp through its Nix flake, which needs no rustup
```

The Nix flake's wrapper runs the front end unmanaged and so skips the preflight. The answer comes
from rustup even when another `rustc`, such as a Nix one, is on `PATH`, so that compiler is never
taken for the pinned toolchain.

If the toolchain is present but the driver cannot run under it (almost always a driver built against
a *different* nightly than the one now installed), the preflight reports the load failure as a
driver problem, having already confirmed the toolchain exists, and keeps the loader's message:

```text
error: the cargo-cgp-driver at /home/you/.cargo/bin/cargo-cgp-driver (beside cargo-cgp) could not run under toolchain `nightly-2026-11-05` (it was likely built against a different nightly):

  /home/you/.cargo/bin/cargo-cgp-driver: error while loading shared libraries: librustc_driver-a1ed262f84b24882.so: cannot open shared object file: No such file or directory

help: run `cargo cgp setup`
```

If the driver runs but reports a version or a build identity that does not match, the two are out of
lockstep: a partial upgrade, or a stale binary earlier on `PATH`:

```text
error: the cargo-cgp-driver at /home/you/.cargo/bin/cargo-cgp-driver (beside cargo-cgp) is version 0.0.9, but this cargo-cgp is 0.1.0 (the two are out of lockstep)

help: run `cargo cgp setup`
```

```text
error: the cargo-cgp-driver at /home/you/.cargo/bin/cargo-cgp-driver (beside cargo-cgp) was built against `rustc 1.99.0-nightly (0000000 2026-01-01)`, but toolchain `nightly-2026-11-05` provides `rustc 1.101.0-nightly (2d20b42b8 2026-11-04)`

help: run `cargo cgp setup`
```

The toolchain named there is the one the preflight queried, which is the pinned nightly unless
`CARGO_CGP_TOOLCHAIN` overrides it. A driver whose `--version` output is not in the three-line shape
at all (an old or foreign binary on the lookup path) fails the parse instead:

```text
error: could not parse the `--version` output of the cargo-cgp-driver at /nix/profile/bin/cargo-cgp-driver (found on PATH, since none is beside cargo-cgp)

help: run `cargo cgp setup`
```

Every one of these but the missing rustup is resolved by `cargo cgp setup`, which reinstalls the
pinned toolchain and rebuilds the driver against it at the front-end's own version. If you are
deliberately running an unprovisioned build (from source, or a hand-picked toolchain), set
`CARGO_CGP_NO_MANAGE` to skip the preflight and trust the environment instead, but then the
toolchain-match responsibility is yours, per the section above.

## Provisioning fails

`cargo cgp setup` manages toolchains through rustup, so on a machine without rustup it stops plainly
after its first progress line rather than failing obscurely:

```text
  Installing toolchain `nightly-2026-11-05` with rustc-dev and llvm-tools
error: rustup was not found on PATH, and `cargo cgp setup` installs the toolchain `nightly-2026-11-05` through rustup

help: install rustup, or install cargo-cgp through its Nix flake, which needs no rustup
```

On such a machine, install through the [Nix flake](installation.md#installing-with-nix) instead,
which provisions the toolchain at build time and needs no rustup.

## Symptom index

This table maps the distinctive fragment of each error to the section that covers it. Match the text
you see, then read the section for the fix.

| Error fragment | Cause | Section |
| --- | --- | --- |
| `` no such command: `frobnicate` `` with the four commands listed | wrong invocation | [The command itself fails](#the-command-itself-fails) |
| `` no such command: `cgp` `` | cargo-cgp not installed, or not on `PATH` | [The command itself fails](#the-command-itself-fails) |
| `could not find Cargo.toml` | run outside a cargo package | [The command itself fails](#the-command-itself-fails) |
| `is cargo on PATH?` | cargo not installed / not on `PATH` | [The command itself fails](#the-command-itself-fails) |
| `failed to run the cargo-cgp-driver …` | driver missing (managed) | [The front-end cannot find the driver](#the-front-end-cannot-find-the-driver) |
| `could not execute process` … `(never executed)` | driver path wrong (unmanaged) | [The front-end cannot find the driver](#the-front-end-cannot-find-the-driver) |
| `error while loading shared libraries: librustc_driver-…` | library path unset, or toolchain mismatch | [The driver cannot load the compiler library](#the-driver-cannot-load-the-compiler-library) |
| `toolchain … is not available` | pinned nightly absent | [The managed preflight rejects the setup](#the-managed-preflight-rejects-the-setup) |
| `could not run under toolchain …` | driver built against another nightly | [The managed preflight rejects the setup](#the-managed-preflight-rejects-the-setup) |
| `out of lockstep` / `was built against` | front-end and driver versions/builds differ | [The managed preflight rejects the setup](#the-managed-preflight-rejects-the-setup) |
| `could not parse the` … `--version` output | an old or foreign driver binary | [The managed preflight rejects the setup](#the-managed-preflight-rejects-the-setup) |
| `rustup was not found on PATH` | no rustup for the preflight or `setup` | [The managed preflight rejects the setup](#the-managed-preflight-rejects-the-setup), [Provisioning fails](#provisioning-fails) |

## Further reading

- [Usage](usage.md#calling-the-driver-directly-debugging): running the driver directly to isolate a
  problem, and reproducing cargo's exact driver invocation.
- [Installation](installation.md): the install and update paths whose failures this document
  diagnoses.
- [Executable structure](../implementation/executable-structure.md#the-environment-contract): the
  sibling lookup, the sysroot, and the dynamic-library path that the failures above trace to.
- [Distribution](../implementation/distribution/provisioning.md#what-the-preflight-verifies): what the managed
  preflight checks and why.
