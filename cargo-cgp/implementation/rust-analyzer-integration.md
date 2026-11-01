# Rust Analyzer integration

Rust Analyzer can run `cargo cgp check` as its on-save diagnostic backend, and the tool's choice of
a target directory of its own comes from the same concern, so both are here. The toolchain the check
forces is in [Distribution](distribution.md#the-pinned-toolchain-is-an-internal-detail).

## The on-save check

The design already accommodates the on-save check, and two of the distribution choices decide
whether it works: the JSON rendering and the forced nightly. The one interaction a reader would
expect to break, Rust Analyzer's own compiler wrapper colliding with the tool's, does not happen.
The real risk is build-artifact contention, and it has a concrete fix.

The tool is wired in through `rust-analyzer.check.overrideCommand`, not `check.command`. Rust
Analyzer's `check.command` names a single cargo subcommand and appends its own flags after it, so it
cannot express `cargo cgp check` (a two-word invocation), and multi-word or alias commands there are
[not fully supported](https://github.com/rust-lang/rust-analyzer/issues/8098). The `overrideCommand`
setting takes the full command as an argument array, is run from the workspace root, and **must emit
JSON**, so the user supplies the whole line including `--message-format=json`:

```jsonc
"rust-analyzer.check.overrideCommand": [
  "cargo", "cgp", "check", "--workspace", "--all-targets", "--message-format=json"
]
```

The JSON reaches Rust Analyzer through the pipeline the tool already has, with nothing new to build.
Rust Analyzer's flycheck parses cargo's `--message-format=json` stream: the `compiler-message`
records cargo wraps each rustc diagnostic in. In `cargo-cgp` the driver renders the *transformed*
diagnostic as rustc JSON through its `JsonEmitter`, cargo wraps that into its own message stream,
and the front-end forwards cargo's stdout untouched (see
[Architecture](architecture.md#the-flow-of-a-diagnostic)). So the front-end need only forward the
`--message-format=json` argument to `cargo check` (which it does, since it forwards everything after
`check` verbatim), and Rust Analyzer receives well-formed cargo JSON with the CGP transforms already
applied inside each diagnostic.

Rust Analyzer's own `RUSTC_WRAPPER` does not collide with the tool's `RUSTC_WORKSPACE_WRAPPER`,
because the two operate in different phases. Rust Analyzer sets `RUSTC_WRAPPER=rust-analyzer` only
when running build scripts and gathering proc-macro information
(`rust-analyzer.cargo.buildScripts.useRustcWrapper`), to skip work it does not need, and *not* for
the flycheck check command. The check command `cargo-cgp` runs is therefore a clean cargo invocation
with only the tool's own `RUSTC_WORKSPACE_WRAPPER` set. Even in the hypothetical where both were
present, cargo nests them as `$RUSTC_WRAPPER $RUSTC_WORKSPACE_WRAPPER $RUSTC`, so the driver still
receives the real `rustc` path as its second argument and its wrapper-mode detection holds; the only
realistic way to actually chain a second wrapper is a user's global `RUSTC_WRAPPER` such as
`sccache`, which is a minor, user-created interaction rather than something Rust Analyzer imposes.

## The target directory

The genuine integration risk is build-artifact contention, and the fix is a dedicated target
directory that the tool uses by default. Because `cargo-cgp` forces the pinned nightly and injects
`-Znext-solver` and `--verbose`, its check produces artifacts with a different fingerprint from the
project's ordinary `cargo build` and from Rust Analyzer's own project-loading builds. Sharing one
`target/` directory then means the two wait on each other for cargo's build lock, the class of
trouble reported when clippy is used as the check command
([rust-analyzer#19336](https://github.com/rust-lang/rust-analyzer/issues/19336)). The artifacts
themselves coexist, since cargo keeps each build's by hash; a probe sharing one directory between
stable, the pinned nightly, and the tool showed each keeping its own, and the check waiting for the
lock another cargo run held.

So `cargo cgp check` and `expand` always build into a `cgp` subdirectory of the project's target
directory, `target/cgp` beside `target/debug`, on every invocation (whether Rust Analyzer is the
caller or not), so a check never waits on the lock a normal build holds, and the reverse. This
mirrors how `rustc_plugin` isolates its own `target/plugin-<channel>` directory, and the isolation
helps command-line use as much as the editor; the cost is a one-time rebuild of the dependency graph
in `target/cgp`, cached thereafter. The front-end finds the project's target directory by running
`cargo metadata --no-deps` (forwarding any `--manifest-path` and `--config`) and reading its
`target_directory`, so the directory is the same wherever in the package the command runs, and
follows a `CARGO_TARGET_DIR`, a `build.target-dir` in a config file, or one given with `--config`;
each gets the `cgp` subdirectory, since each is a directory other cargo runs share. When that query
fails (no package, a broken manifest) it falls back to the relative `target/cgp` and lets the
wrapped command report the problem. A user who needs a different location passes `--target-dir`,
which is taken as given: the front-end injects its default only when the forwarded arguments do not
already set one, the same inject-only-when-absent rule the driver follows for its own flags.

## When the editor and the check disagree

One residual caveat has no fix, only awareness: Rust Analyzer's inline semantic analysis and the
`cargo-cgp` flycheck can disagree. Rust Analyzer's own type inference runs against the project's
toolchain and default solver, while the flycheck diagnostics come from the pinned nightly under
`-Znext-solver`, so occasionally `cargo-cgp` surfaces a diagnostic Rust Analyzer's inline analysis
does not, or the reverse. This is the same solver-and-toolchain divergence the tool already accepts
on the command line ([The driver](driver.md#choosing-the-trait-solver)), now visible in the editor;
it is a property of running a fixed diagnostic compiler, not a bug to resolve.

## Tests

- [`crates/cargo-cgp/tests/front_end/command.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/command.rs):
  `metadata_query_args` forwards the manifest path and every `--config` value, in either form, and
  ignores arguments after a `--`; `parse_target_directory` reads `target_directory` out of
  `cargo metadata`'s JSON; and `cgp_target_dir` picks the `cgp` subdirectory or the relative
  fallback.
- [`crates/cargo-cgp/tests/front_end/forwarded_flag.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/forwarded_flag.rs):
  `scan_flag` gives a flag's values in order and leaves the other arguments in order, stops at a
  `--` and keeps what follows, and takes the argument after a spaced flag as its value; a spaced
  flag at the end counts as given without a value; the first `--manifest-path` decides; and a longer
  flag is another flag. `forwards_target_dir` detects an explicit `--target-dir` (spaced or `=`) so
  the default is not injected over it, and ignores one after a `--`, which is rustc's;
  `forwarded_manifest_path` finds a `--manifest-path` in either form. `expand`'s `--item`, help
  flag, and profile flags count only before a `--` too.

## Source

- [`crates/cargo-cgp/src/launch/target_dir.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/target_dir.rs):
  the `cgp` subdirectory, the `cargo metadata` query behind it, and the relative fallback.
- [`crates/cargo-cgp/src/launch/forwarded_flag.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/forwarded_flag.rs):
  reads `--target-dir`, `--manifest-path`, and `--config` out of the forwarded arguments.
- [`crates/cargo-cgp/src/check.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/check.rs):
  lets cargo inherit the front-end's stdio, so cargo's JSON reaches Rust Analyzer untouched.
