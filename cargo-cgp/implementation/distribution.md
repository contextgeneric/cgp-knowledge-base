# Distribution

`cargo-cgp` must run smoothly on a machine that never asked for a nightly toolchain, so distribution
is the problem of delivering two binaries and one exact nightly compiler, keeping them in lockstep,
and hiding all of it from a user whose own project builds on stable. This document describes how the
tool is packaged, installed, and provisioned through cargo and rustup, and why it is built that way.

A `cargo install --locked cargo-cgp` installs the front-end; `cargo cgp setup` provisions the pinned
toolchain and the matching driver; `cargo cgp check` forces the pinned nightly for the wrapped
compilation and runs a read-only preflight that verifies a matching driver is present before doing
anything; and `cargo cgp update` upgrades the tool when a newer version is published. A handful of
environment variables
([`config`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/config.rs))
override the management for local development. Publishing stays manual: the two crates must be
published to crates.io together, at the same version, for the version handshake and `setup`'s
versioned driver install to hold (see [Known limitations](#known-limitations)).

Three neighbors cover what a reader looks for separately: [The Nix package](nix-package.md), for a
machine without rustup; [Bumping the pinned nightly](pinned-nightly-bump.md), for a maintainer
moving the pin; and [Rust Analyzer integration](rust-analyzer-integration.md), for the on-save check
and the target directory.

## The problem

Distributing `cargo-cgp` is hard because the driver embeds the compiler, and the embedded compiler
is an exact, unstable nightly. The driver links the internal `rustc_driver` libraries under the
`rustc_private` feature, which ship only with a nightly toolchain carrying the `rustc-dev`
component, and the API those libraries expose changes between nightlies. So the driver is welded to
one dated nightly, the one pinned in
[`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml),
and every part of distribution has to respect that weld. Three consequences follow, and the design
is built around all three at once.

The first consequence is that a user needs **two binaries, not one**. The front-end `cargo-cgp` and
the driver `cargo-cgp-driver` are separate crates for a good reason: only the driver links the
compiler and LLVM, and keeping that out of the front-end keeps the front-end a small, ordinary
binary (see [Executable structure](executable-structure.md#why-two-executables)). But a plain
`cargo install --locked cargo-cgp` installs only the front-end, and the front-end cannot do anything
without its driver sibling. Getting the tool working therefore always takes a second step to bring
the driver in, and both must end up side by side.

The second consequence is that the pinned nightly, with its `rustc-dev` component, **has to be
present on the machine**. Building the driver needs `rustc-dev` (the compiler-internal `.rlib`s) and
`llvm-tools`; running it then needs the matching `librustc_driver` shared library and the
standard-library sysroot that only that toolchain supplies. A machine that only has stable Rust has
none of this.

The third consequence is that at check time the **sysroot and the dynamic `librustc_driver` must
both belong to the pinned nightly**, or the driver loads a compiler it was not compiled against and
crashes. The driver embeds the pinned nightly's `rustc_driver`; if it is handed a stable sysroot, or
if the loader finds a differently-versioned `librustc_driver` on its path, the ABI will not match.
The design's job is to make the match automatic.

Two widespread misconceptions are worth clearing up before the design, because both make the problem
sound worse than it is. **Updating the host's nightly does not break the driver.** The pin is a
*dated* nightly (such as `nightly-2026-10-10`), which rustup treats as an immutable, distinct
toolchain; a `rustup update` refreshes the rolling `stable`/`beta`/`nightly` channels and leaves a
dated nightly untouched. The driver keeps working until *cargo-cgp itself* ships a new version that
bumps the pin. **And the project being checked does not need to use nightly at all.** A user's crate
can pin stable, or nothing; `cargo-cgp` forces the pinned nightly it provisions for the check and
leaves the project's real builds alone. The design below makes that true.

## How similar tools solve it

`cargo-cgp` is not the first tool to link the compiler and ship it to strangers, and two reference
points bracket the design space. Clippy sits at one extreme and the `rustc_plugin` family at the
other, and `cargo-cgp` lands deliberately between them.

Clippy avoids the whole problem by **being part of the toolchain**. `clippy-driver` is built in-tree
by the same CI run that builds the `rustc` it links, distributed as the `clippy` rustup component,
and installed with `rustup component add clippy`. Because the driver ships *inside* the toolchain
next to `rustc`, it never has to find a sysroot, never risks a version mismatch, and never needs a
separate install of a compiler. This is the cleanest possible answer, and it is closed to
`cargo-cgp`: an out-of-tree project cannot inject a component into rustup's distribution.

The [`rustc_plugin`](https://github.com/cognitive-engineering-lab/rustc_plugin) framework, which
backs Flowistry, Aquascope, Paralegal, and Argus, solves the out-of-tree case, and it is the model
`cargo-cgp` follows. Three of its techniques carry over directly. It **bakes the pinned nightly into
a compile-time constant** (`pub const CHANNEL: &str = env!("RUSTC_CHANNEL")`), read from the
toolchain file at build time, so both the CLI and the driver agree on exactly one toolchain string.
It **treats a nightly bump as a semver-breaking change**, tagging each release with its nightly as a
prerelease label (`0.15.2-nightly-2026-05-01`), so a user's dependency pin names the nightly too.
And its build script **embeds the toolchain's library directory as an rpath** on the driver
(`rustc --print target-libdir` → `-Wl,-rpath,…`), so the driver finds `librustc_driver` at load time
without any environment variable.

The `rustc_plugin` tools also show what shapes the *install* step. Because
[`cargo install` ignores a crate's bundled `rust-toolchain.toml`](https://github.com/rust-lang/cargo/issues/11036),
a crate that needs a specific nightly to build cannot rely on the toolchain file being honored. The
nightly has to be selected explicitly with `cargo +<pinned> install`. And because compiling against
`rustc-dev` is slow, the mature tools lean on an installer that does the toolchain setup for the
user: Flowistry's editor extension runs
`rustup toolchain install nightly-… -c rustc-dev -c llvm-tools-preview` and then
`cargo +nightly install flowistry`. `cargo-cgp` adopts the baked-in constant and the
installer-driven setup (folding that installer into its own `cargo cgp setup`) and improves on the
`rustc_plugin` model in one place: how the check's toolchain is chosen (below).

## The pinned toolchain is an internal detail

The central design decision is that `cargo-cgp` **forces its own pinned nightly for the check and
never asks the project to supply it**. This is where the design diverges from `rustc_plugin`, whose
tools require the *analyzed project* to pin the same nightly in its own `rust-toolchain.toml`. For a
diagnostic tool that mostly runs `check`, that requirement is an unnecessary imposition on the
user's repository. `cargo-cgp` instead carries the toolchain as an implementation detail and
overrides the project's toolchain for the duration of the check.

The mechanism is one embedded constant and one environment variable. The pinned nightly string lives
in a shared `config` constant, `PINNED_TOOLCHAIN`, generated at build time from
[`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml)
by a build script, exactly as `rustc_plugin` derives `CHANNEL` from `env!("RUSTC_CHANNEL")`, so the
toolchain file stays the single source of truth and the constant can never drift from it. When the
front-end runs the wrapped `cargo check`, it sets `RUSTUP_TOOLCHAIN=<PINNED_TOOLCHAIN>` in the child
environment (`cargo +<PINNED_TOOLCHAIN> check` would be equivalent). This one variable makes
everything downstream consistent.

Forcing the toolchain resolves the sysroot-and-dylib coherence problem for free. The front-end
discovers the sysroot through rustup, as `rustup run <PINNED_TOOLCHAIN> rustc --print sysroot`
([`launch::sysroot`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/sysroot.rs)),
which returns the *pinned* sysroot, so the `--sysroot` the driver injects and the `librustc_driver`
it loads both belong to the nightly the driver was compiled against. The three things that must
agree (the driver's embedded compiler, the injected sysroot, and the loaded shared library) come
from one toolchain by construction, with no version-matching left to chance.

The override is safe because `RUSTUP_TOOLCHAIN` outranks `rust-toolchain.toml`. Rustup's override
precedence runs, highest first: a `+toolchain` on the command line, the `RUSTUP_TOOLCHAIN` variable,
a directory override, the `rust-toolchain.toml` file, then the default. Setting the variable
therefore wins over whatever the project pins, so `cargo cgp check` uses the pinned nightly even in
a repository that has committed its own `rust-toolchain.toml`, and it leaves that file in place,
untouched, for the project's ordinary builds.

Running the check under a nightly the project did not choose is an accepted trade-off, and it is the
same one the tool already makes. The driver already injects `-Znext-solver=globally` and
`--verbose`, so `cargo cgp check` never claims to reproduce a plain `cargo check`: it is a
diagnostic pass with its own compiler settings, the way Clippy runs under its own toolchain. In rare
cases a program could compile under the project's stable toolchain but report an error under the
pinned nightly, or the reverse; this is documented as inherent to using a fixed diagnostic compiler
([The driver](driver.md#choosing-the-trait-solver) records the analogous next-solver caveat), not a
distribution bug.

## Installing the binaries

`cargo-cgp` is always installed with cargo (there is no prebuilt-binary channel), and the install
splits cleanly in two: a `cargo install --locked cargo-cgp` puts the front-end in place, and
`cargo cgp setup` provisions everything heavyweight. That split lets the first command be
one a user types from memory, with no nightly date string in it, and it dissolves the bootstrapping
problem that a `rustc_private` tool would otherwise have.

The front-end installs on an ordinary stable toolchain, which is the key that makes the split work.
Because the front-end is an ordinary binary with no `rustc_private` linkage,
`cargo install --locked cargo-cgp` builds it under whatever toolchain the user already has (stable,
or anything else at or above the `rust-version` the workspace sets) and needs no pinned nightly. So
the cargo#11036 hazard above, that `cargo install` ignores a bundled `rust-toolchain.toml`, never
bites: the front-end does not care which toolchain builds it. The freshly installed front-end embeds
the `PINNED_TOOLCHAIN` constant and the whole setup routine, so it carries everything needed to
provision the rest of the tool itself.

`cargo cgp setup` then performs the two heavyweight steps under the pinned string it reads from that
constant, so the user never types the nightly date. It runs
`rustup toolchain install <PINNED_TOOLCHAIN> -c rustc-dev -c llvm-tools` for the build-time compiler
internals, then `cargo install cargo-cgp-driver --version <version> --locked` with
`RUSTUP_TOOLCHAIN=<PINNED_TOOLCHAIN>` (the equivalent of `cargo +<PINNED_TOOLCHAIN> install …`) to
build the driver under that exact nightly, passing `--root` so it lands next to the front-end in
`~/.cargo/bin`. `--locked` builds the `Cargo.lock` published with the crate, so the driver links the
dependency versions the release was tested with, including the `syn` and `prettyplease` versions
whose output the expand snapshots pin, instead of the newest compatible ones. The explicit toolchain
is mandatory, not stylistic: without it `cargo install` would build the driver against the active
toolchain and fail on stable or mis-version on another nightly (cargo#11036 again). Pinning the
driver to the front-end's own version (`--version <version>`) keeps the pair in lockstep,
and it is possible only because the two crates are released together (below).

Keeping the two crates separate enables this. Folding the driver into the `cargo-cgp` package as a
second `[[bin]]` would force the whole package, front-end included, to build under the pinned
nightly, losing the `cargo install --locked cargo-cgp` bootstrap. Two crates let the front-end
install on any toolchain while the driver stays confined to the pinned one, and cargo places both in
`~/.cargo/bin`, so the front-end's sibling lookup
([`launch::driver_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/driver_path.rs))
finds the driver with no configuration. Lockstep is enforced by the version preflight below, not by
shared packaging.

Each of the four published crates (the two binaries and the two rustc-free libraries the driver
depends on) ships the MIT `LICENSE` its manifest declares and a README. The front-end's README is
the repository's; the driver's says to install it through `cargo cgp setup`, and each library's says
it serves the driver and that its API may change in any release. Each crate's `LICENSE` is a symlink
to the one workspace file, as each binary's `rust-toolchain.toml` is, and cargo packages the file it
points to.

## Provisioning: `setup` does the work, `check` only verifies

All provisioning is delegated to one command, and `cargo cgp check` never installs or builds
anything itself. `cargo cgp setup` performs every mutating step; `cargo cgp check` runs a read-only
preflight that either passes silently or stops with an error telling the user to run
`cargo cgp setup`. The division rests on one rule: **`check` must never do slow, stateful, or
surprising work** (no `rustup` installs, no driver compilation, no toolchain changes), because a
command whose job is to print diagnostics should not, as a side effect, spend minutes compiling or
alter the user's toolchains. Everything of that kind lives in `setup`, which the user invokes
knowingly.

`cargo cgp setup` performs the full provisioning: install the pinned toolchain
(`rustup toolchain install <PINNED_TOOLCHAIN> -c rustc-dev -c llvm-tools`) and build the driver
under it (the equivalent of
`cargo +<PINNED_TOOLCHAIN> install cargo-cgp-driver@<version> --locked`), landing it beside the
front-end. It is the command a user runs once after `cargo install --locked cargo-cgp`, and the
command the preflight names whenever it finds something wrong. Making provisioning a single named
subcommand gives the docs one stable entry point instead of a shifting list of `rustup` and `cargo`
incantations, and it is the one place that reads `PINNED_TOOLCHAIN`, so the user never types the
nightly date.

### What the preflight verifies

The preflight is a fast, read-only sequence at the top of `check`, run before any cargo is spawned,
and every failure of its checks produces an actionable error that names what is wrong and directs
the user to `cargo cgp setup`. The one exception is a machine without rustup, which `setup` cannot
repair either, so that message names rustup and the Nix flake instead. It answers two questions in
order (is the pinned toolchain installed, and does the driver actually run and match) and stops at
the first "no." The ordering is deliberate: the cheap, disambiguating check comes first, so that
when the driver fails, the preflight already knows whether the toolchain underneath it is to blame
and can say so.

The driver it tests is the one the launch has already located, through the
[`driver_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/driver_path.rs)
lookup: the `CARGO_CGP_DRIVER` override if set, otherwise the sibling of the running front-end, and
failing both the first `cargo-cgp-driver` on `PATH`. Every message about the driver names its path
and where it was found, so a stale driver found on `PATH` (from another install, say) is not
mistaken for the one `setup` placed beside the front-end. A driver found nowhere is caught by the
second question, when running it fails with
`failed to run the cargo-cgp-driver (none is beside cargo-cgp or on PATH): …`, the plainest "run
setup" case.

**Is the pinned toolchain installed?** The preflight runs
`rustup run <PINNED_TOOLCHAIN> rustc --version` and reads back the toolchain's own rustc identity,
its version line. Asking rustup directly ties the answer to the pinned toolchain: only rustup's
`rustc` shim honors `RUSTUP_TOOLCHAIN`, so on a machine without rustup another `rustc` on `PATH`
would answer for a toolchain that is not there. `rustup run` installs nothing unless given
`--install`. This is cheap, and doing it first separates a *missing toolchain* from a *bad driver*:
if this query fails, the toolchain the driver needs is not installed, and the user gets that message
with rustup's own reason beneath it. If rustup itself is missing, the message says so. If it
succeeds, the preflight now holds the identity of the compiler the check will force, to compare the
driver against.

**Does the driver run and match?** The preflight then invokes `cargo-cgp-driver --version` under the
*exact* environment the real check will use: `RUSTUP_TOOLCHAIN` forced to the pinned nightly, the
discovered sysroot, and the dynamic-library search path set. This single step is both a load test
and a version handshake, because a driver built against the wrong nightly fails the first and a
driver from the wrong release fails the second:

- **Will it even load?** The driver binary dynamically links `librustc_driver-<hash>.so`, where the
  hash is fixed at build time to the exact nightly the driver was compiled against, and it is
  recorded in the binary's dynamic-dependency list. A driver built against a *different* nightly
  than the one installed therefore names a shared library the pinned toolchain's `lib` directory
  does not contain, and the operating system's loader aborts the process before `main` with a
  "cannot open shared object file" error. So a driver that will not run under the forced toolchain
  is, in the overwhelmingly common case, one compiled against the wrong nightly. Because the
  previous step already confirmed the toolchain *is* installed, the preflight attributes a launch
  failure to the driver and points at `setup`, keeping the loader's own message beneath its
  explanation.
- **Is it the right build?** When the driver does load, it prints its `--version` output and exits.
  That output carries three fields baked in at build time, one per line so a value with spaces stays
  unambiguous: `cargo-cgp-driver <tool_version>`, `pinned-toolchain: <name>`, and
  `built-against-rustc: <rustc --version line>`. The last is the compiler that *actually* compiled
  the driver, which its build script captured by querying the compiling rustc (`$RUSTC --version`)
  so the value reflects reality rather than intent. The preflight reads the first and the last and
  makes two strict comparisons: `tool_version` must equal the front-end's own version exactly (a
  difference is a partial upgrade or a stale binary on `PATH`), and `built_against_rustc` must equal
  the installed toolchain's `rustc --version` read in the previous step (a difference is a driver
  built against a nightly other than the pinned one, which loaded only because its hash happened to
  resolve). Either mismatch sends the user to `setup`. The compiler mismatch names the toolchain the
  preflight queried, which `CARGO_CGP_TOOLCHAIN` can make another one than the driver's own pin.

The flag is the ordinary `--version`. The driver distinguishes a direct invocation from cargo's
wrapper invocation by testing whether its second argument is a `rustc` path (see
[The driver](driver.md#preparing-the-argument-vector)), so `cargo-cgp-driver --version` prints the
tool's version line while a wrapper-mode `--version` still forwards to the real compiler for cargo's
probing, the same split `clippy-driver` uses.

The two comparisons are strict equality rather than a compatibility range, and that is sound only
because the two crates are **released and version-bumped in lockstep**. The crates share one version
through `[workspace.package]` in the root
[`Cargo.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/Cargo.toml), so a version bump
moves both at once, and a release publishes the pair (by hand, see
[Known limitations](#known-limitations)). A correctly provisioned machine therefore holds a matching
pair and the preflight passes trivially, paying only the cost of two quick subprocesses. The checks
exist as the safety net for the ways an installed pair drifts apart *after* a correct install: one
crate upgraded but not the other, a leftover binary on `PATH`, or the pinned toolchain removed from
under a driver that needs it.

The alternative, having `check` itself run `rustup install`, `cargo install`, and rebuild the driver
on any incompatibility, is rejected deliberately. Automatic recompilation would make a routine
`cargo cgp check` occasionally block for minutes and mutate the user's toolchains as a side effect,
which is the wrong behavior for a diagnostic command. Keeping `check` a read-only verifier keeps the
fast path fast and makes every heavy, stateful action something the user triggers on purpose.

### Updating with `cargo cgp update`

A `cargo cgp update` subcommand upgrades the tool to its latest version, and its two-step shape
(update the front-end, then hand off to the *new* front-end's `setup`) is not merely convenient but
the only ordering that can work. A release may bump the pinned nightly, and the knowledge of the new
toolchain and the new provisioning logic lives *inside* the new `cargo-cgp` binary; the old process
cannot provision the new driver because it only knows the old pin. So `update` first reinstalls the
front-end with `cargo install cargo-cgp --version <target> --locked` (which, having no compiler
linkage, needs no pinned nightly; the version is named because a bare `cargo install` takes the
newest *stable* release, the wrong target for a pre-release moving to a newer pre-release), then
runs the freshly installed `cargo-cgp setup` as a child process, which brings the driver and
toolchain up to the new version. It reads its own path before the reinstall, because on Linux
`current_exe` afterward names the replaced binary `<path> (deleted)`. The heavy `rustc-dev` work
stays deferred to the new `setup`, exactly where it belongs.

Before touching anything, `update` finds out whether there is a newer version to move to **that the
running version's channel allows** and skips out early when there is not. It reads the crates.io
sparse index for the front-end crate (`https://index.crates.io/ca/rg/cargo-cgp`, one JSON line per
published version), enumerates every non-yanked version, and picks the highest allowed one: a stable
install considers only stable candidates, while a pre-release install considers every candidate,
pre-release or stable, so it can reach the release it previewed. If that highest in-channel version
is **not strictly newer**, `update` prints `note: cargo-cgp v<current> is already up to date` and
exits without invoking `cargo install`, rustup, or `setup`; only a strictly newer one triggers the
reinstall.

Keeping a stable install on stable releases is why `update` enumerates all versions rather than
asking cargo for the single "latest". Both `cargo search` and `cargo info` report only a crate's
*max version*, which **includes pre-releases**, so if a pre-release higher than the latest stable is
published, a stable install could neither see the latest stable through them nor safely take the
pre-release. Reading the index directly gives every version, so the channel filter can pick the
right one: with hypothetical versions, `v1.0.0 → v1.0.1`, never `v1.1.0-beta`; and
`v1.1.0-beta → v1.1.0` once the release is out. The comparison is `semver`, which orders a
pre-release below its release, so the "highest allowed" and "strictly newer" tests are both exact. A
pre-release install must be able to take a stable release, since one restricted to pre-releases
never sees the release it previewed. Pre-releases themselves are test runs of the cargo integration
and are not documented as versions, per the base's
[rule on versions](../../AGENTS.md#document-official-versions-never-pre-releases); this paragraph
describes only how `update` treats one.

`setup` and `update` take no arguments. Because both install things, each answers `--help` with a
help text of its own instead of running, and refuses any other argument with an error naming it,
rather than ignoring it and starting an install the user did not ask for.

The index is read over HTTP with the widely-used `ureq` (rustls TLS) and `serde_json`. The network
access stays on the front-end's `update` path alone. The check path uses `serde_json` only to read
the local `cargo metadata` output, and the driver uses neither crate. The sparse-index access
follows the shape of the `crates-index` crate but is written directly over those two rather than
taking on that dependency. One limitation follows from reading `index.crates.io` directly: unlike
the eventual `cargo install`, it does not consult a user's configured registry mirror or private
registry, so automatic version discovery targets the default crates.io (see
[Known limitations](#known-limitations)).

Installation and update both go **through cargo**; there is no self-replace mechanism to maintain.
`update` shells out to `cargo install --locked cargo-cgp` (the same tool that installed it), and
where that succeeds the run of the new `setup` follows. This keeps `update` a thin orchestrator over
cargo rather than a re-implementation of what cargo already does.

The one case cargo cannot handle is the running binary on Windows, and there `update` fails cleanly
with instructions rather than trying to be clever. When a user types `cargo cgp update`, the running
process *is* `~/.cargo/bin/cargo-cgp`, the file `cargo install` overwrites. On Unix this is fine:
cargo writes the new binary alongside and moves it over the old name with an atomic rename, and the
running process keeps executing its original inode. On **Windows a running executable is locked**,
so the `cargo install` step fails with "Access is denied." A failed reinstall, whatever its cause,
ends with a note about that lock and the exact commands for the user to run by hand
(`cargo install cargo-cgp --version <version> --locked` followed by `cargo cgp setup`, from a shell
where `cargo-cgp` is not currently running), which succeed precisely because they are not
self-referential. The tool does not embed a self-replacing installer to work around this; it
delegates to cargo and hands the user the manual path when cargo cannot finish.

Two smaller properties round out the design. **An interrupted update degrades safely**: between
reinstalling the front-end and finishing `setup`, the machine briefly holds a new front-end against
an old driver, and that is exactly the mismatch the [preflight](#what-the-preflight-verifies)
already catches, so the next `cargo cgp check` tells the user to run `cargo cgp setup` and recovers.
That is also why the Windows manual path above is safe to leave half-done. And **superseded
toolchains accumulate**: each nightly bump installs a new multi-gigabyte dated toolchain and leaves
the previous one in `~/.rustup/toolchains`. `update` never removes one, since another tool may
depend on that nightly, and it does not report one either ([Known limitations](#known-limitations)).

## Escape hatches for local development

Developing `cargo-cgp` itself means running an unreleased front-end against a just-built driver, so
the provisioning above must be overridable, and a few environment variables provide the escape
hatches. The UI snapshot suite needs only one of them: it runs the `cargo-cgp` it built in
`target/debug` with `CARGO_CGP_NO_MANAGE` set, and that front-end's sibling lookup finds the driver
built beside it.

- `CARGO_CGP_DRIVER` names an explicit driver executable, bypassing the sibling lookup, for a driver
  that sits neither beside the front-end nor on `PATH`.
- `CARGO_CGP_NO_MANAGE` turns off the preflight and the toolchain forcing, telling `cargo-cgp` to
  trust whatever driver and toolchain the environment already provides: the sysroot comes from
  `RUSTC` or the `rustc` on `PATH`. The UI suite and the [Nix package](nix-package.md) set it, and
  so does a developer running inside the source checkout under the pinned toolchain: no
  provisioning, no handshake, just run.
- `CARGO_CGP_TOOLCHAIN` overrides `PINNED_TOOLCHAIN` at runtime, for `setup` and for a managed
  `check` or `expand`, so the tool can be pointed at a different nightly for testing a toolchain
  bump before the constant is changed. The preflight still compares the driver with that nightly, so
  the driver must be built under it, as a `setup` with the same override does. An unmanaged run
  forces no toolchain, so `CARGO_CGP_NO_MANAGE` makes this override have no effect on `check`.

These variables belong in the shared `config` modules alongside the existing well-known names
(`CARGO_CGP_SYSROOT` and the rest), passed into the functions that use them rather than read ad hoc,
per the
[code organization conventions](https://github.com/contextgeneric/cargo-cgp/blob/main/AGENTS.md#code-organization-conventions).

## Loading the compiler at runtime

At runtime the driver must load the pinned nightly's `librustc_driver`, and the front-end finds it
by discovering the sysroot. The front-end runs `rustc --print sysroot` through rustup under the
pinned toolchain, passes it to the driver through `CARGO_CGP_SYSROOT`, and prepends the sysroot's
`lib` directory to the OS dynamic-library search path so the loader finds `librustc_driver`. That is
the contract documented in [Executable structure](executable-structure.md#the-environment-contract).

Runtime discovery is chosen over a build-time rpath, though both would work: because the driver is
always compiled on the machine it runs on, an embedded rpath (as `rustc_plugin`'s `build_main` bakes
in via `rustc --print target-libdir` → `-Wl,-rpath,…`) would point at a valid local path. Discovery
wins on two independent grounds. The front-end must run `rustc --print sysroot` anyway to inject the
`--sysroot` the out-of-tree driver needs, so the search path falls out of work already done; and it
needs no build-time linker configuration. An embedded rpath could be added as a second safeguard,
but the design does not depend on one.

## Comparison with Clippy

Distribution is the one area where `cargo-cgp` cannot follow Clippy, and the divergence is
foundational rather than a gap to close later. Clippy is a first-party rustup component:
`clippy-driver` is compiled in-tree by the same CI that builds its `rustc`, shipped as part of the
toolchain, and installed with `rustup component add clippy`. Every distribution problem this
document solves (two binaries, a matching nightly, a coherent sysroot and `librustc_driver`) Clippy
gets for free, because its driver lives inside the toolchain and is versioned with it atomically.

`cargo-cgp` is out-of-tree, so it must reconstruct by hand what Clippy inherits from the
distribution. It pins a nightly instead of being built with one; it installs that nightly as a
separate step instead of being part of it; it discovers and injects a sysroot instead of being found
next to `rustc`; and it runs a version preflight instead of being versioned atomically with the
compiler. The closest working model for all of this is not Clippy but the `rustc_plugin` family, and
the two places `cargo-cgp` improves on that model are the check-time toolchain override (the
analyzed project needs no nightly of its own, where `rustc_plugin` requires it to pin the same one)
and the `cargo install --locked cargo-cgp` bootstrap that defers every heavyweight step to an
explicit `cargo cgp setup` (so the user never types a nightly date to get started).

## Known limitations

These limits and assumptions of the managed path are deliberate or accepted:

- **Publishing is manual.** The exact-version preflight and `setup`'s `cargo-cgp-driver@<version>`
  assume both crates are published at the same version. `[workspace.package]` keeps the versions
  equal in the source tree, but nothing enforces that a release publishes both, and a release that
  ships `cargo-cgp` alone leaves `setup` unable to find its driver.
- **`update` does not report a superseded toolchain.** It leaves the previous pinned nightly
  installed and says nothing about it.
- **Driver co-location falls back when the front-end is not in a `bin` directory.**
  `setup` derives `--root` from the front-end's `current_exe` so the driver lands beside it (for the
  usual `~/.cargo/bin/cargo-cgp`, root `~/.cargo`). When the front-end sits somewhere that does not
  fit cargo's `<root>/bin` convention, `setup` warns and installs the driver to cargo's default
  location instead of guessing, which may not co-locate them. The ordinary `cargo install` path
  is unaffected.
- **`setup` idempotency rests on cargo's "already installed" being success.**
  Re-running `setup` (as `update` does) relies on `rustup toolchain install` being a no-op when
  already satisfied and on `cargo install cargo-cgp-driver@<version>` exiting successfully when that
  version is already present. Both hold on current cargo and rustup.
- **The managed path assumes rustup.** The `setup`/`update`/preflight flow
  manages toolchains entirely through rustup (`RUSTUP_TOOLCHAIN`, `rustup toolchain install`). A
  machine whose Rust comes from a distro package or another manager has no rustup to drive, so it is
  out of scope for automatic provisioning; `setup` and the preflight report a missing rustup
  plainly rather than failing obscurely. Nix is the exception rather than a gap: it is served by the
  [`flake.nix`](nix-package.md), which provisions the toolchain at build time and runs the
  front-end unmanaged.
- **`update` version discovery targets the default crates.io.** It reads `index.crates.io` directly,
  so unlike the `cargo install` that follows it, it does not consult a user's configured registry
  mirror or source replacement. A locked-down network that blocks `index.crates.io` will make
  `update`'s check fail (with a clear error); the manual `cargo install --locked cargo-cgp` +
  `cargo cgp setup` path still works through the configured registry.

## Further reading

The mechanisms this design rests on are documented authoritatively elsewhere; read these when
changing the piece each one covers.

- [`rustc_plugin`](https://github.com/cognitive-engineering-lab/rustc_plugin) is the closest working
  model for out-of-tree distribution of a `rustc_private` tool: the `CHANNEL` constant, the
  rpath-embedding build script, and the nightly-as-prerelease versioning are all worth reading in
  its `src/lib.rs`, `src/build.rs`, `src/cli.rs`, and `src/driver.rs`.
- [`cargo install` ignores `rust-toolchain.toml` (cargo#11036)](https://github.com/rust-lang/cargo/issues/11036)
  is why `setup` must install the driver with an explicit `cargo +<pinned> install`, and why the
  front-end, needing no particular toolchain, installs with a `cargo install --locked cargo-cgp`.
- [Overrides, in The rustup book](https://rust-lang.github.io/rustup/overrides.html), defines the
  toolchain override precedence that lets `RUSTUP_TOOLCHAIN` win over a project's
  `rust-toolchain.toml`.
- [Flowistry's installation notes](https://github.com/willcrichton/flowistry) show a real editor
  tool driving `rustup toolchain install … -c rustc-dev -c llvm-tools-preview` and
  `cargo +nightly install` from an extension, the same toolchain-install-then-cargo-install shape
  `cargo cgp setup` automates.
- [Replacing a running executable on Windows (rustup#1186)](https://github.com/rust-lang/rustup/issues/1186)
  documents the file-lock that makes `cargo install` fail when it targets the running `cargo-cgp`,
  which is why `cargo cgp update` falls back to printing the manual commands there.
- [The crates.io sparse index](https://index.crates.io/) and the
  [`crates-index` crate](https://crates.io/crates/crates-index): the index `update` reads to
  enumerate versions, and the reference implementation for the sparse-index path convention and the
  `vers`/`yanked` fields (used as a reference, not a dependency).

## Tests

The pieces are unit-tested over their pure logic, keeping the process-spawning at the edges, and the
UI suite exercises the managed/unmanaged wiring end to end.

- [`crates/cargo-cgp/tests/front_end/preflight.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/preflight.rs):
  parses the driver's `--version` output (accepting the real shape, rejecting a foreign first line
  and missing fields); the
  [`evaluate`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/preflight/evaluate.rs)
  verdict on a matching driver, a version mismatch, and a rustc mismatch; and a check that the
  baked-in `PINNED_TOOLCHAIN` equals the channel in
  [`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml);
  `failure_message` for each failure: the driver's path and origin in every driver message, the
  loader's and rustup's reasons kept, the queried toolchain named in a compiler mismatch, each
  repairable failure ending in a `help` naming `setup`, and a missing rustup's `help` naming rustup
  and the Nix flake instead; `judge_driver_answer`, the
  verdict on a driver that ran, failed, or printed another shape; and `toolchain_failure`, the
  failure each toolchain-query error stands for.
- [`crates/cargo-cgp/tests/front_end/driver_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/driver_path.rs):
  `locate_driver`'s order (the override, the sibling, then `PATH`) and the bare name kept for a
  driver found nowhere.
- [`crates/cargo-cgp/tests/front_end/update.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/update.rs):
  `sparse_index_path` over the registry's dir convention; `parse_versions` skipping yanked and
  unparseable lines; `select_update` (a stable install taking the highest stable and *never* a
  pre-release, a pre-release install taking the highest newer version of either kind, including the
  release it previewed, and no-newer/downgrade yielding `None`), all without a network call; and
  `frontend_install_args`, the locked reinstall at the chosen version.
- [`crates/cargo-cgp/tests/front_end/setup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/setup.rs):
  `driver_install_args`, the locked driver install at the front-end's version, with and without the
  `--root` that places it beside the front-end.

- [`crates/cargo-cgp/tests/front_end/dispatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/dispatch.rs):
  the side-effect-free dispatch paths (an unknown subcommand, a missing subcommand or help flag,
  `--version`/`-V`, and `setup` and `update` answering `--help` without running and refusing any
  other argument); [`tests/front_end/help.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/help.rs)
  checks the `setup` and `update` help texts name what each command needs.
- The [UI snapshot suite](testing.md) is the standing end-to-end proof that the driver runs as the
  compiler; it drives the built binaries with `CARGO_CGP_NO_MANAGE` set, so the check runs unmanaged
  against the toolchain `cargo test` already selected. The managed path (preflight + toolchain
  forcing) is not covered by the suite, since installing a provisioned driver is out of scope for
  the source-tree test loop.

## Source

The front-end holds the provisioning and management; the driver adds the version query; each crate
has a build script that bakes in the pinned toolchain.

- [`crates/cargo-cgp/src/config.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/config.rs):
  the well-known names: `PINNED_TOOLCHAIN` and `TOOL_VERSION` (baked in), the environment variables
  (`CARGO_CGP_DRIVER`, `CARGO_CGP_NO_MANAGE`, `CARGO_CGP_TOOLCHAIN`, `RUSTUP_TOOLCHAIN`), the
  `cgp` target subdirectory and its relative fallback, and the crate names.
- [`crates/cargo-cgp/build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/build.rs):
  derives `PINNED_TOOLCHAIN` from
  [`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml),
  mirroring how `rustc_plugin` derives `CHANNEL`.
- [`crates/cargo-cgp/src/run.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/run.rs):
  dispatches `check`, `expand`, `setup`, and `update`, answers `--help` and `--version`, and gives
  `setup` and `update` their own `--help` while refusing any other argument to them.
- [`crates/cargo-cgp/src/toolchain.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/toolchain.rs):
  resolves the effective pinned toolchain and queries its `rustc --version` through rustup.
- [`crates/cargo-cgp/src/launch/command.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/command.rs):
  runs the preflight (when managed), forces `RUSTUP_TOOLCHAIN`, wires the driver and sysroot, and
  injects the `target/cgp` default, found through `cargo metadata` in `launch/target_dir.rs`, unless
  the caller set the target directory.
- [`crates/cargo-cgp/src/launch/preflight/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src/launch/preflight):
  verifies the toolchain is installed and the driver runs and matches (the pure `evaluate` plus the
  `--version`-parsing and IO), returning the discovered sysroot.
- [`crates/cargo-cgp/src/launch/driver_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/driver_path.rs):
  the `CARGO_CGP_DRIVER` override, the sibling lookup, and the fallback to `PATH`.
- [`crates/cargo-cgp/src/launch/dylib.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/dylib.rs):
  the OS dynamic-library search path, shared by the check and the preflight's load test.
- [`crates/cargo-cgp/src/setup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/setup.rs):
  installs the pinned toolchain with `rustup` and the driver with `cargo install`, co-located via
  `--root`.
- [`crates/cargo-cgp/src/update/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src/update):
  reads the crates.io sparse index (`ureq` + `serde_json`), picks the highest in-channel version,
  skips when not newer, else reinstalls and hands off to the new `setup`.
- [`crates/cargo-cgp-driver/src/version.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/version.rs)
  and
  [`run.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/run.rs):
  the `--version` query (answered only in non-wrapper mode), and
  [`build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/build.rs),
  which bakes in `PINNED_TOOLCHAIN` and the `built_against_rustc` identity from the compiling
  `$RUSTC --version`.
