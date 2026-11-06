# Usage

`cargo-cgp` has two commands that read your code. `cargo cgp check` stands in for `cargo check` and
re-presents CGP wiring errors with their root cause first; `cargo cgp expand` shows the ordinary
Rust your CGP macros generate, with CGP's type-level constructs spelled the way you wrote them. You
run either in a cargo project the way you run `cargo check`. This document covers running the check,
reading its output, expanding a target, using the tool from an editor, and the switches that change
its behavior. For installing it, see [Installation](installation.md).

cargo-cgp is **optional**, and its job is developer-time readability. Its two reading commands
compile your code only to inspect it (`check` re-checks it under the pinned nightly solely to
reshape the diagnostics, and `expand` stops as soon as the macros are expanded), and there is no
`cargo cgp build`, `run`, or `test` (`setup` and `update` only provision the tool). CGP is an
ordinary library that builds on any **stable Rust ≥ 1.89**, so plain `cargo check`, `cargo build`,
`cargo run`, and `cargo test` all work on a CGP project unchanged. Use `cargo cgp check` when you
hit or expect a wiring error and want it readable; use plain `cargo check` when you do not; and
always build, run, and test with ordinary cargo.

## Running a check

Run the command from anywhere inside a cargo package or workspace that uses `cgp`:

```sh
cargo cgp check
```

Every argument after `check` is forwarded verbatim to `cargo check`, so the flags you already use
work unchanged: `cargo cgp check --workspace`, `cargo cgp check -p my-crate`, `cargo cgp check -v`.
The command also runs directly as `cargo-cgp check` when you have not installed it as a cargo
subcommand. For a summary of the available commands, run `cargo cgp --help` (or `cargo cgp` with no
subcommand at all, which prints the same overview); `cargo cgp --version` (or `-V`) prints the tool's
version alone, as `cargo-cgp <version>`.

cargo-cgp does not interpret those forwarded flags; cargo validates them, so an unknown flag produces
cargo's own error (`error: unexpected argument '--nope' found`). `cargo cgp check --help` prints
`cargo check`'s own help and runs no check. The front-end only reads `--target-dir`, to decide whether
to inject its own default, and `--manifest-path` and `--config`, to ask cargo for that default, and it
passes all three through.

A check differs from a plain `cargo check` in three deliberate ways, so it is a diagnostic pass rather
than a reproduction of your project's own check:

- **The pinned nightly:** it compiles under the tool's own nightly, so the embedded compiler matches
  the driver. Your project's toolchain is left alone for its ordinary builds.
- **The next-generation trait solver:** `-Znext-solver` surfaces the dependency errors the default
  solver hides, reporting the real missing bound, such as `HasField<Symbol!("name")>`.
- **An isolated `target/cgp` directory:** cargo locks a target directory while it builds there, so a
  shared one would make each check wait for your other cargo runs and the editor's, and the reverse.

**The check reports only what the next-generation solver rejects.** A passing `cargo cgp check` is not
a passing `cargo check`: two namespaces that inherit from each other are rejected by stable `rustc`
with an `E0275` and compile clean under the tool
([`namespace_inheritance_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-inheritance-cycle/namespace_inheritance_cycle.rs)).
Build and test with plain cargo on your own toolchain for that reason.

Pass `--target-dir` to choose the check's directory exactly. Otherwise it is the `cgp` subdirectory of
the project's own target directory, read from `cargo metadata --no-deps` with any forwarded
`--manifest-path` and `--config`, so it follows `CARGO_TARGET_DIR` or a configured `build.target-dir`:
with `CARGO_TARGET_DIR=/build`, the check builds in `/build/cgp`. When that query fails, as outside any
package, the front-end falls back to a relative `target/cgp`, and the wrapped command reports the real
problem. `expand` uses the same default.

Two further consequences of the wrapping are worth knowing. **Only workspace members are reshaped**,
because the driver is installed through `RUSTC_WORKSPACE_WRAPPER`, which cargo applies to workspace
members alone; a path dependency outside the workspace compiles through plain `rustc` and its errors
arrive raw. And **the front end sets `RUSTC_WORKSPACE_WRAPPER` unconditionally**, replacing any
value the user exported, so a wrapper of the user's own given through that variable does not run
under the tool. It says so on stderr when it replaces one:

```text
warning: RUSTC_WORKSPACE_WRAPPER is set to `/usr/local/bin/my-wrapper`; cargo-cgp replaces it with its driver for this run, so that wrapper does not run
```

A user's `RUSTC_WRAPPER`, such as `sccache`, does compose with the driver: cargo runs the wrapper
with the driver and the real `rustc` as its next two arguments, so the driver still sees wrapper
mode and rewrites as usual, and `sccache` does not cache a failing compilation, so it never replays
an output from before the rewrite.

## Expanding a target

`cargo cgp expand` prints the crate as the compiler sees it after macro expansion, which is how you
answer "what did that macro actually generate?": for a wiring table you are unsure about, for a
provider whose bound you want to see, or to confirm what an error is telling you:

```sh
cargo cgp expand --lib          # expand the library target
cargo cgp expand --bin my-app   # expand one binary
cargo cgp expand -p my-crate --lib
```

Arguments are forwarded to `cargo rustc`, so target selection is cargo's own, and because it expands
exactly one target, cargo asks you to choose when a package has several. That is worth knowing
before your first run: a package with both a library and a binary needs `--lib` or `--bin <NAME>`,
and without one cargo declines with *"extra arguments to `rustc` can only be passed to one target"*.
Expanding a module of a library crate is therefore `cargo cgp expand --lib --item <path>`. The
output goes to stdout, so it pipes and redirects like any other program's:

```sh
cargo cgp expand --lib > expanded.rs
cargo cgp expand --lib | rg 'Symbol!'
cargo cgp expand --help                 # the expand options, including --item
```

`expand` answers `--help` (or `-h`) itself rather than forwarding it: `cargo cgp expand --help`
prints the tool's own expand help, which documents `--item`, the forwarding to `cargo rustc`, and
examples, and points at `cargo rustc --help` for the cargo options. This differs from `check`, which
forwards `--help` to `cargo check`.

**A whole crate's expansion is long, so `--item <path>` narrows it to one part.** The path is
`::`-separated, and what it selects depends on what it names:

```sh
cargo cgp expand --lib --item shapes             # a module: its contents
cargo cgp expand --lib --item shapes::Rectangle  # a type: its declaration and every impl for it
cargo cgp expand --lib --item AreaCalculator     # a trait: its definition and every impl of it
```

The path names a module or item **inside the crate being expanded**, and a leading `crate::` is
accepted, so `--item crate::contexts::app` and `--item contexts::app` are the same request.
(`self::` and a bare leading `::` work too.)

The trait form is usually what you want on CGP code, because a component's generated items *are*
impls: `--item AreaCalculator` gives the provider trait together with the blanket impls, the
`UseContext` impl, and each provider's impl of it. A type's form is the companion:
`--item Rectangle` shows the struct with its `HasField` impls and its wiring, including an impl a
derive put inside a `const _: () = { … };` block, which comes with its block. If the path matches
nothing you get an error saying so, not a silent whole-crate expansion.

The filter is the one argument `expand` does not forward to cargo, and `expand` reads it and a help
flag only before a `--`, as cargo reads its own flags. Arguments after a `--` go to rustc, so
`cargo cgp expand --lib -- --item a` fails at rustc as an unknown option. A bare positional path (the way
`cargo-expand` takes it) is not accepted, because with everything else passed through untouched a
bare word cannot be told from the value of a cargo flag (`--bin my_module`).

Two things about the output are worth knowing. **Every macro is expanded**, not only CGP's, so
`#[derive(Debug)]` and `println!` appear in their generated form too; the CGP-specific part is that
CGP's own type-level constructs are resugared, so a field name reads `Symbol!("height")` rather than
a six-level `Chars` list. And the `cgp::macro_prelude::` qualifier the macros emit is stripped for
readability, which means the output is meant to be *read* rather than compiled.

`expand` is not a check: the compilation stops once the crate is expanded, so no type analysis runs, a
wiring mistake goes unreported, and the command exits 0. An error reported before that point fails the
command with cargo's exit code. Most such errors, such as a CGP macro rejecting its input, still print
what expanded, while a type defined twice, a `macro_rules!` call matching no rule, or an unclosed
delimiter prints nothing ([how a run fails](../implementation/expand-command.md#how-a-run-fails)).

## Reading the output

The output is ordinary rustc/cargo diagnostics, with the errors `cargo-cgp` recognizes rewritten
into a clearer form. When the tool rewrites an error into a known CGP class, it stamps the message
with a short code in square brackets and states the cause after it:

```text
error[E0277]: [CGP-E001] missing field `height` on `Rectangle`
```

The `[CGP-Exxx]` code names one class of CGP mistake (here, a context that cannot implement a
consumer trait) and is looked up in the [CGP error-code catalog](../error-code.md). The diagnostic's
own Rust code (`E0277` here) is always kept, so `rustc --explain` still works and nothing is
reclassified away from rustc; the CGP code rides inside the message as a tag on the sentence it
classifies. Errors the tool does not recognize pass through as the compiler wrote them.

Some mistakes keep rustc's own headline, and [issues/usability.md](../issues/usability.md) lists them.
For example, a check on a context with a type parameter is not traced, because the resolver works
without that context's bounds. Fix such an error from rustc's text, or check a concrete context.

## Editor integration (Rust Analyzer)

Rust Analyzer can run `cargo cgp check` as its on-save check backend. Because the command is two
words and must emit JSON, wire it through `check.overrideCommand` (not `check.command`) with
`--message-format=json`:

```jsonc
"rust-analyzer.check.overrideCommand": [
  "cargo", "cgp", "check", "--workspace", "--all-targets", "--message-format=json"
]
```

The tool renders the transformed diagnostics as rustc JSON, which cargo wraps and the editor parses, so
the transforms appear inline: the `[CGP-Exxx]` headline, the `root cause:` line, and the dependency tree,
the same text the terminal prints minus the code frame.

Four consequences of the override are worth telling a user:

- **Rust Analyzer runs the array exactly as written,** so its `check.features`, `check.allTargets`,
  `check.extraArgs`, and `check.workspace` settings do not reach the check, and any feature or target
  flag goes in the array.
- **Its as-you-type diagnostics are separate,** computed by its own analysis on the user's toolchain, so
  they are never rewritten and can disagree with the pinned-nightly check.
- **The setting belongs in workspace settings** (VS Code's `.vscode/settings.json`), since a
  user-level override runs the tool on every Rust project, and a committed workspace file breaks the
  editor check for anyone without the tool.
- **The editor's `PATH` decides whether `cargo` finds the subcommand,** which matters when the tool is on
  `PATH` only through shell start-up files and the editor was launched from a desktop launcher.

A failing command surfaces as a Rust Analyzer warning reading
`cargo check failed to start: Cargo watcher failed, the command produced no valid metadata (…)`
followed by the command's stderr, so a preflight failure arrives with its
`` help: run `cargo cgp setup` `` line. The full notes are in
[Rust Analyzer integration](../implementation/distribution/rust-analyzer-integration.md).

## Running on a project outside this repository

To exercise the tool on CGP source in another location, run it through Nix, and **prefer a local
`cargo-cgp` checkout whenever one is available**: you are usually working inside this repository or
beside it, and the local build reflects the current code, including any uncommitted changes, which a
freshly fetched release would not. Point the flake reference at the local checkout and run its
default app from the target project's directory:

```sh
cd /path/to/the/target/project                 # a cargo package/workspace that uses `cgp`
nix run /path/to/the/local/cargo-cgp -- check   # local checkout, which reflects current code
```

Only when no local checkout is available, fall back to the published flake:

```sh
nix run github:contextgeneric/cargo-cgp/v0.1.0 -- check
```

Either way this builds (or reuses a cached) `cargo-cgp` and `cargo-cgp-driver` under the pinned
nightly and runs `cargo cgp check` in the current directory, with everything after `--` forwarded to
the check as usual. Running through the flake makes it work from *any* directory: the flake
wraps the front-end to force the pinned nightly and run unmanaged, so it needs no rustup and leaves
the target project's own toolchain and `target/` untouched.

When the local binaries are already built and the pinned nightly is the active toolchain, drive them
directly with the overrides under [Installing from source](installation.md#installing-from-source),
skipping the flake build. That relies on the ambient toolchain matching the driver's embedded compiler,
which the flake otherwise guarantees.

## Environment overrides

A few environment variables change how the front-end behaves, for local development and unusual
setups. They are summarized here; the full contract is in
[Distribution](../implementation/distribution/provisioning.md#escape-hatches-for-local-development).

- `CARGO_CGP_NO_MANAGE`: when set, skip the preflight and the toolchain forcing, and trust whatever
  driver and toolchain the environment already provides. Used when running a source or Nix build
  that is not provisioned through rustup.
- `CARGO_CGP_DRIVER`: an explicit path to the driver executable, bypassing the sibling lookup. Point
  it at a freshly built `target/debug/cargo-cgp-driver`.
- `CARGO_CGP_TOOLCHAIN`: override the pinned nightly at runtime, for testing a toolchain bump. `setup`
  reads it too, so it installs the overriding toolchain and builds the driver under it, and the
  preflight then compares the driver with that toolchain. It has no effect on a check run with
  `CARGO_CGP_NO_MANAGE`, which forces no toolchain.
- `CARGO_TARGET_DIR`: moves the project's target directory, and the check builds in its `cgp`
  subdirectory. Pass `--target-dir` to choose the check's directory exactly.

## Calling the driver directly (debugging)

You normally never invoke `cargo-cgp-driver` yourself: the front-end wires it in as cargo's rustc
wrapper, and cargo calls it once per workspace crate. But when `cargo cgp check` misbehaves, calling
the driver directly is how you tell a front-end wiring problem apart from a driver or compiler one,
because it takes cargo and the front-end out of the loop.

Start with the version query, which doubles as a load test:

```sh
cargo-cgp-driver --version   # or -V
```

The driver links `librustc_driver` dynamically and loads it before printing, so this is the quickest
confirmation that the binary can run at all. (`cargo-cgp-driver --help`, `-h`, or a bare invocation
with no arguments prints a short description of the driver and these same flags instead.) On success
`--version` prints three lines: its own version, the `pinned-toolchain:` it targets, and the
`built-against-rustc:` compiler it was actually built with:

```text
cargo-cgp-driver 0.1.0
pinned-toolchain: nightly-2026-11-05
built-against-rustc: rustc 1.101.0-nightly (2d20b42b8 2026-11-04)
```

A failure *before* that output, typically
`error while loading shared libraries: librustc_driver-<hash>.so: cannot open shared object file`,
means the loader cannot find the compiler library, either because the dynamic-library path is not
set or because the driver was built against a different nightly than the one installed. A Nix-built
driver has that path baked into its wrapper, so `--version` works as-is; a from-source driver needs
the pinned toolchain's `lib` directory on the loader path, which the front-end normally sets
for it (`DYLD_FALLBACK_LIBRARY_PATH` on macOS, `LD_LIBRARY_PATH` elsewhere):

```sh
SYSROOT=$(rustc --print sysroot)                        # run under the pinned toolchain
LD_LIBRARY_PATH=$SYSROOT/lib cargo-cgp-driver --version
```

A driver from the [Nix flake](installation.md#installing-with-nix) needs no library-path setup, since the
flake bakes that path into its wrapper. Bring it onto `PATH` in a throwaway shell:

```sh
nix shell /path/to/the/local/cargo-cgp -c cargo-cgp-driver --version
```

There is no `nix run` app for the driver, since it is a second binary of the same package, so reach it
through `nix shell` or a built `result/bin`. To replay a full compilation with it, you still supply
`CARGO_CGP_SYSROOT` as below, and running the whole check through the flake is usually easier.

To debug an actual compilation, reproduce the exact command cargo hands the driver rather than
building one by hand. Run the failing check verbosely and cargo prints each driver invocation in
full:

```sh
cargo cgp check -v
```

Each `Running …` line, showing a full `cargo-cgp-driver … rustc --crate-name …` command, is a
complete, replayable invocation. (If none prints, the crate was cached; touch a source file or clean
`target/cgp` to force a recompile.) Copy one and run it directly, with the two environment values
the front-end passes reconstructed: the sysroot, which the driver reads from `CARGO_CGP_SYSROOT` to
inject `--sysroot`, and the library path above:

```sh
SYSROOT=$(rustc --print sysroot)
LD_LIBRARY_PATH=$SYSROOT/lib CARGO_CGP_SYSROOT=$SYSROOT \
  cargo-cgp-driver /path/to/rustc --crate-name … <the rest of the printed args>
```

Run this way the driver behaves as it does under cargo, but in isolation, where you can add
`RUST_BACKTRACE=1`, extra `-Z` flags, or a debugger. The leading `rustc` path puts it in wrapper
mode, so keep it; without it the driver runs in the direct mode `--version` uses
([preparing the arguments](../implementation/driver/program.md#preparing-the-argument-vector)).

## Further reading

- [Installation](installation.md): installing and updating the tool.
- [CGP error codes](../error-code.md): the catalog of the `[CGP-Exxx]` codes in the output.
- [Distribution](../implementation/distribution/provisioning.md): the design behind the check's toolchain
  forcing, the isolated target directory, and the Rust Analyzer integration.
- [The driver](../implementation/driver/program.md): how the driver wraps rustc and transforms
  diagnostics, for when direct invocation surfaces a driver-side problem.
