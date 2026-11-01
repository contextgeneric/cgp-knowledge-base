# Rust Analyzer integration

Rust Analyzer can run `cargo cgp check` as its on-save backend, with nothing new in the tool. This
document records why the setup takes the form it does, and why the check builds in a target
directory of its own.

## The on-save check

The tool is wired through `rust-analyzer.check.overrideCommand`, because `check.command` names a
single cargo subcommand and cannot express a two-word one
([not fully supported](https://github.com/rust-lang/rust-analyzer/issues/8098)). The override must
emit JSON, so the user supplies the whole line:

```jsonc
"rust-analyzer.check.overrideCommand": [
  "cargo", "cgp", "check", "--workspace", "--all-targets", "--message-format=json"
]
```

The transforms happen inside the driver, and the front-end forwards cargo's stdout untouched
([Architecture](architecture.md#the-flow-of-a-diagnostic)). So the editor gets well-formed cargo
JSON with no extra work, and any stage that reshaped the front-end's output would break it.

Rust Analyzer's `RUSTC_WRAPPER` does not collide with the tool's `RUSTC_WORKSPACE_WRAPPER`, since it
sets its own only for build scripts and proc-macro information. Even a user's global `RUSTC_WRAPPER`
is safe, because cargo nests the wrappers and the driver still receives the `rustc` path as its
second argument.

## The target directory

`cargo cgp check` and `expand` build into a `cgp` subdirectory of the project's target directory, to
stay off cargo's build lock. The tool's nightly and flags give different fingerprints from the
project's builds, so in a shared directory the runs wait on each other, the class of trouble
reported when clippy is the check command
([rust-analyzer#19336](https://github.com/rust-lang/rust-analyzer/issues/19336)). The lock is the
reason, not lost artifacts: a probe sharing one directory showed each build keeping its own. The
cost is one rebuild of the dependencies.

These behaviors are easy to break:

- **The directory comes from `cargo metadata`,** so it is the same anywhere in the package and
  follows `CARGO_TARGET_DIR` or `build.target-dir`. Each gets the `cgp` subdirectory, since each is
  shared with other cargo runs.
- **The query runs under the forced toolchain,** or rustup's proxy could install the toolchain the
  project pins, which the check never uses.
- **A failed query falls back to the relative `target/cgp`,** and the wrapped command reports the
  problem.
- **An explicit `--target-dir` is taken as given.** One after a `--` is rustc's, so it does not
  count.

## When the editor and the check disagree

Rust Analyzer's inline analysis uses the project's toolchain and default solver, while the check
uses the pinned nightly under `-Znext-solver`, so either can show a diagnostic the other does not.
This has no fix. It is the [divergence the tool accepts](driver.md#choosing-the-trait-solver) on the
command line.

## Tests

- [`front_end/command.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/command.rs):
  the directory query and its fallback.
- [`front_end/forwarded_flag.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/forwarded_flag.rs):
  reading a flag from forwarded arguments.

## Source

- [`launch/target_dir.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/target_dir.rs):
  the directory and its query.
- [`launch/forwarded_flag.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/forwarded_flag.rs):
  the forwarded flags.
