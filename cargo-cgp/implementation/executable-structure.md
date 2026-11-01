# Executable structure

`cargo-cgp` is two cooperating executables, a front-end that wraps `cargo` and a driver that wraps
`rustc`, so that it can work inside a real compilation through the compiler's `rustc_driver` API while
presenting an ordinary cargo subcommand to the user.

## Why two executables

The tool is split because only one binary may link the compiler internals, and isolating that linkage
keeps the other small and ordinary. The **front-end**
([`crates/cargo-cgp`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp)) is the cargo subcommand a user invokes, and it
has no compiler linkage. The **driver**
([`crates/cargo-cgp-driver`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver)) is a `rustc` replacement that links
the compiler's unstable libraries under the `rustc_private` feature. In one binary, the front-end would
carry the compiler dylib and LLVM behind every invocation, and `cargo install` could not build it on
stable Rust. The [architecture document](architecture.md#the-crates) places the two rustc-free library
crates the driver uses.

## Wrapping cargo: the front-end

The front-end's main job is to run cargo with the driver installed as the compiler for the user's own
crates: `cargo check` for a check, `cargo rustc` for an [expansion](expand-command.md). It sets
`RUSTC_WORKSPACE_WRAPPER`, which makes cargo call the driver in place of `rustc` for each *workspace*
crate and compile dependencies with the normal compiler. That scope is deliberate, because the point of
the tool is the user's code, not their dependency tree.

The tool is reachable two ways, which the front-end reduces to the same arguments before it routes on
the first remaining word:

```text
cargo cgp check --workspace   →  cargo-cgp  cgp  check --workspace   (cargo inserts "cgp")
cargo-cgp check --workspace   →  cargo-cgp       check --workspace   (invoked directly)
```

Only a *leading* `cgp` is dropped, so a later argument with that value survives. There are four
subcommands: `check`, `expand`, and the provisioning commands `setup` and `update`
([Distribution](distribution/provisioning.md)). Arguments after `check` go to `cargo check` as written.
No subcommand or a help flag prints the help and succeeds, so a bare `cargo cgp` is an overview rather
than an error. `setup` and `update` install things, so they refuse any argument other than `--help`
rather than ignore it.

The wrapped command differs from a plain cargo run in these ways:

- **The driver:** the path found by the `CARGO_CGP_DRIVER` override, else beside the running front-end,
  since `cargo install` and `setup` put the two together, else on `PATH`. Messages say which it was, so
  a stale driver found on `PATH` is not mistaken for the installed one.
- **A replaced wrapper:** cargo runs one workspace wrapper, so the driver takes the place of a wrapper
  the user had set, as in `cargo clippy`, and the front-end warns that it did not run.
- **The target directory:** the `cgp` subdirectory of the directory cargo would use, unless the caller
  forwards `--target-dir`, so a check does not wait on the lock other cargo runs hold
  ([why](distribution/rust-analyzer-integration.md)).
- **The toolchain and the environment:** the [contract below](#the-environment-contract).

The front-end never sees a diagnostic. It inherits cargo's stdio, so progress lines and the compiler's
diagnostics appear live, and every CGP transform happens inside the driver's emitter, which renders in
whatever format the invocation asks for ([the flow](architecture.md#the-flow-of-a-diagnostic)). It
propagates cargo's exit code, so a failed check fails the command. A signal leaves `cargo` without a
code, so on Unix the front-end exits with 128 plus the signal number, as a shell reports it.

The front-end's own messages take cargo's forms on stderr, so they read as part of cargo's output:
`error:` with each cause under a `Caused by:`, `help:`, `warning:`, and right-aligned status lines.
Another program's output, such as rustup's reason a toolchain is missing, is quoted indented two spaces,
so its own `error:` lines read as part of the quote. The help and version texts go to stdout, as cargo's
do.

## Wrapping rustc: the driver

Cargo invokes the driver the way `RUSTC_WORKSPACE_WRAPPER` prescribes, with the real compiler's path
first:

```text
cargo-cgp-driver  /path/to/rustc  --edition=2024  --crate-name foo  src/lib.rs  ...
```

The driver runs the compiler in-process rather than shelling out to that path, because only in-process
can it read and rewrite the compilation's diagnostics. [The driver](driver/program.md) covers its
argument preparation, its compiler-API access, and the transformations.

## The environment contract

The two are separate processes, so what the driver needs travels through the environment, and all of it
exists because the driver lives *outside* any toolchain (in `target/debug` or `~/.cargo/bin`, not the
toolchain's `bin`). The compiler cannot infer from that location what it normally would. Three things
cross the boundary:

- **The toolchain:** the front-end forces `RUSTUP_TOOLCHAIN` to the pinned nightly, so the sysroot and
  the `librustc_driver` the driver loads both belong to the nightly it embeds, whatever the project pins.
  A preflight confirms a matching driver first. `CARGO_CGP_NO_MANAGE` turns both off and uses the ambient
  compiler
  ([why this is internal](distribution/provisioning.md#the-pinned-toolchain-is-an-internal-detail)).
- **The sysroot:** `CARGO_CGP_SYSROOT` holds what `rustc --print sysroot` reports. The driver injects it
  as `--sysroot` unless the invocation carries one, because a `rustc_driver` binary outside a toolchain
  has no other way to find `std`. The two crates declare the variable's name independently, so the shared
  string is the contract.
- **The library path:** the sysroot's `lib` directory goes first on the dynamic-library search path
  (`LD_LIBRARY_PATH` or its platform equivalent), so the loader finds `librustc_driver` when cargo spawns
  the driver. Nothing else would put it there.

`expand`'s requests are flags rather than environment variables, placed after cargo's `--`, so cargo
scopes them to the one target ([The expand command](expand-command.md)).

## Comparison with Clippy

`cargo-cgp` is modeled closely on Clippy. Both are a front-end plus a driver; both set
`RUSTC_WORKSPACE_WRAPPER` to the driver and run a cargo subcommand; both locate the driver beside the
front-end through `current_exe`; both detect wrapper mode by testing whether the second argument's file
stem is `rustc` and drop it; both inject `--sysroot` only when one is absent; and both run the compiler
with `rustc_driver::compiler_entrypoint` inside `catch_with_exit_code`. Read
[`external/rust/src/tools/clippy/src/driver.rs`](../../../external/rust/src/tools/clippy/src/driver.rs) and
[`external/rust/src/tools/clippy/src/main.rs`](../../../external/rust/src/tools/clippy/src/main.rs) beside
the two crates.

The sysroot is the structural difference, and it follows from not being a rustup component.
`clippy-driver` ships inside the toolchain, next to `rustc`, so the compiler infers the sysroot from the
driver's location, and Clippy injects `--sysroot` only when its `SYSROOT` variable is set and never
touches the dynamic-library path. `cargo-cgp-driver` is out of tree, so the front-end computes the sysroot
and sets the loader path itself.

Argument forwarding is simpler here. `cargo-cgp` forwards extra arguments straight to cargo, while Clippy
packs its own into a `CLIPPY_ARGS` variable and chooses between the `check` and `fix` cargo subcommands.
`cargo-cgp`'s one tool-specific argument, `expand`'s `--item`, becomes a flag after cargo's `--`, so it
needs no environment packing. The driver-side gaps are catalogued in
[the driver's comparison](driver/program.md#comparison-with-clippy).

## Further reading

The Cargo Book states the protocol the front-end drives and the driver decodes in wrapper mode:

- [Environment Variables, in The Cargo Book](https://doc.rust-lang.org/cargo/reference/environment-variables.html)
  defines `RUSTC_WORKSPACE_WRAPPER` and `RUSTC_WRAPPER`: cargo runs the wrapper with the real `rustc`
  path as its first argument, the workspace variant applies only to workspace members, and it affects the
  artifact hash, so wrapped builds cache separately.

[The driver's reading list](driver/program.md#further-reading) collects the compiler-side references.

## Tests

The front-end's helpers are tested directly, and the UI snapshot suite exercises the end-to-end wrapping,
since it runs every fixture through the real front-end ([Testing](testing.md)). `preflight.rs`,
`setup.rs`, and `update.rs` belong to [Distribution](distribution/provisioning.md#tests), and `expand.rs` to
[The expand command](expand-command.md#tests). These are the files under
[`crates/cargo-cgp/tests/front_end/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/tests/front_end):

- [`args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/args.rs): the invocation forms, and a
  non-Unicode argument reported by position.
- [`command.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/command.rs): the target directory, read
  from `cargo metadata` under the forwarded configuration.
- [`dispatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/dispatch.rs): the side-effect-free
  routes, including `setup` and `update` refusing arguments.
- [`driver_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/driver_path.rs): the order of the
  driver's locations.
- [`dylib.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/dylib.rs): the sysroot library first, and a
  directory holding the list separator reported instead of panicking.
- [`exit.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/exit.rs): an exit code passed through, and a
  signal turned into 128 plus its number.
- [`forwarded_flag.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/forwarded_flag.rs): reading a flag
  from the forwarded arguments, in either form and only before a separator.
- [`help.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/help.rs): what the help texts list.
- [`invocation.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/invocation.rs): the order of a wrapped
  command's arguments, with one separator.
- [`report.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/report.rs): the message forms.
- [`sysroot.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/sysroot.rs): a failed sysroot probe's
  stderr quoted in its error, and the query through `rustup run` under a forced toolchain.
- [`workspace_wrapper.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/workspace_wrapper.rs): the
  warning for a replaced wrapper, and silence when it is unset, empty, or already the driver.

## Source

These are the front-end's modules, which sit under
[`crates/cargo-cgp/src/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src); the driver's are in
[its Source section](driver/program.md#source).

- [`run.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/run.rs), [`args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/args.rs),
  [`help.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/help.rs):
  the entry point, the normalization, the dispatch, and the help texts.
- [`launch/command.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/command.rs): the wrapped cargo command
  both reading subcommands run.
- [`launch/invocation.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/invocation.rs),
  [`launch/forwarded_flag.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/forwarded_flag.rs): its arguments,
  and the one scan that reads a flag from the forwarded ones.
- [`launch/driver_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/driver_path.rs),
  [`launch/workspace_wrapper.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/workspace_wrapper.rs): locating
  the driver, and the warning for a replaced wrapper.
- [`launch/target_dir.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/target_dir.rs): the isolated directory.
- [`launch/sysroot.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/sysroot.rs),
  [`launch/dylib.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/dylib.rs): the sysroot and the search path.
- [`launch/preflight/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src/launch/preflight): the read-only pre-check
  ([Distribution](distribution/provisioning.md)).
- [`check.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/check.rs), [`expand/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src/expand):
  the two reading subcommands.
- [`toolchain.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/toolchain.rs),
  [`setup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/setup.rs),
  [`update/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src/update): toolchain resolution and provisioning.
- [`exit.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/exit.rs), [`report.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/report.rs):
  the exit code and the message forms.
- [`config.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/config.rs),
  [`build.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/build.rs): the shared names, and the baked-in
  `PINNED_TOOLCHAIN` read from `rust-toolchain.toml`.
