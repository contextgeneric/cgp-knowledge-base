# Testing

`cargo-cgp` is tested at two levels: fast unit tests over each crate's pure logic, and a UI snapshot
suite, a custom Rust harness in the style of Clippy's, that compiles example CGP programs through the
real tool. Every test lives in its crate's `tests/` directory, so all tests reach a crate through its
public API, and no test-only switch exists in shipped code
([AGENTS.md](https://github.com/contextgeneric/cargo-cgp/blob/main/AGENTS.md)).

## The layers of testing

Testing splits along the seam between the tool's two kinds of logic. Deciding how to invoke the compiler
and what to do with its text is pure and cheap to test, so unit tests guard it, above all in the two
rustc-free libraries. The behavior of actually invoking the compiler appears only when a real `cargo`
drives a real compiler through the driver, so the UI suite guards it by running the whole tool and
snapshotting what it prints.

## Unit tests

**Each crate builds its unit tests into one test target**, an entrypoint `tests/<name>_tests.rs` over a
directory `tests/<name>/` with a module per subject. This matters most for the driver, whose test binary
links the compiler's `rustc_driver` dylib, a link every extra binary would repeat. That link needs the
`rustc_private` feature, so `driver_tests.rs` carries the same `#![feature(rustc_private)]` gate as the
driver binary.

**A test pins short output with `assert_eq!` and multi-line rendered output with an `insta` snapshot.** A
rendered dependency tree spans many lines, and an inline snapshot shows it as it prints. The
error-processing crate's graph tests are the worked example.

Argument handling on both sides of the tool is a typical subject, because it is pure, with corner cases
that are easy to get wrong. New argument-handling behavior should arrive with a test.

## The UI snapshot suite

Each fixture `<name>.rs` under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui) has three committed
siblings: `<name>.cgp.stderr`, the tool's output; `<name>.rust.stderr`, what plain `cargo check`
prints, the "before" to the tool's "after"; and `<name>.expand.rs`, the Rust the fixture's macros
generate. A fixture that compiles has two empty `.stderr` files and still an `.expand.rs`.

The diff between the two `.stderr` files is the tool's work, because the driver renders through the
compiler's own human emitter, so both come out of the same renderer. Their difference includes the
driver's choice of solver and its `--verbose`, not only its rewrites.

**The fixtures live in one directory per error class**, so a fixture moves only when its class
changes, never when its message improves. The directories mirror the
[error catalog](../../cgp/errors/README.md): `checks/`, `hidden/`, `lowering/`, `wiring/`, and
`data/`, each with one directory per class document, and `uncataloged/<class>/` for mistakes the
catalog lacks. Three directories hold fixtures outside any class: `ok/` for programs that compile,
`pass-through/` for plain Rust errors the tool must leave alone, and `robustness/` for how the tool
degrades when the compilation fails under it. The driver's unit tests pin a panic in its own emitter
instead ([The driver](driver/program.md#containing-the-drivers-own-panics)). Every fixture name is
unique across the tree. `cgp`'s own tests leave post-codegen compile failures to this suite, so
these fixtures are the maintained copy.

**How well the tool presents a fixture's error is a header field, not a directory.** Every error
fixture declares `//@quality: acceptable` (the tool leads with the cause), `usability` (the cause is
present but buried), or `hidden` (the cause is absent), and `//@codes: …` lists the exact
`[CGP-Exxx]` codes its output carries (`none` for an uncoded one). `--list` prints every fixture
with both.

### Three passes per fixture

Each fixture runs three passes, in
[`passes`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-ui-tests/src/passes): two about what the compiler *says* and one about
what the macros *generate*.

- **The cgp-stderr pass** runs `cargo-cgp check` end to end and compares its stderr with
  `<name>.cgp.stderr`.
- **The rust-stderr pass** runs plain `cargo check` and compares its stderr with
  `<name>.rust.stderr`. It records the "before", so nothing cross-checks it.
- **The expand pass** runs `cargo cgp expand` and compares its **stdout** with `<name>.expand.rs`.
  It shows the generated code beside the error about it, and it is the end-to-end coverage of
  [the expand command](expand-command.md) and its [resugaring](resugaring.md). It does not read the
  command's exit status, or its stderr.

Three checks hold each fixture to more than its snapshots, because a snapshot alone cannot catch a
crash that prints nothing or a rewrite of an error the tool should leave alone:

- **The status check** requires the tool and plain `cargo check` to agree on whether the fixture
  compiles. The known case of the next solver accepting a mistake, a namespace inheritance cycle,
  compiles under both on the pinned nightly (only stable rejects it), so
  `namespace_inheritance_cycle` fails this check if a later nightly makes them disagree.
- **The pass-through check**, for fixtures under `pass-through/`, requires the tool's stderr to
  equal plain `cargo check`'s, both normalized as the baseline is. A fixture whose output still
  differs declares `//@rewrites-falsely: <reason>`, and the check reports the marker once the
  outputs agree.
- **The header check**, for every fixture outside `ok/`, `pass-through/`, and `robustness/`,
  requires a `//@quality:` and a `//@codes:` list equal to the codes in the output, so a fixture
  that gains or loses a code fails instead of being re-blessed unnoticed.

A fixture that declares `//@json` also runs **the JSON pass**, which compares the compiler messages
of `cargo cgp check --message-format=json` with `<name>.cgp.json`. Editors and agents read this
stream, and nothing else exercises it. The snapshot keeps the fields a consumer uses and leaves out
the `rendered` text the `.cgp.stderr` pins.

The expand pass normalizes less, deliberately: only absolute paths. The `Chars<…>` collapse absorbs
how rustc truncates a list in a *diagnostic*, but in an expansion a raw list means the resugaring
declined, which the snapshot must show.

A fixture whose compilation stops before expansion finishes has no expansion, so its snapshot holds
a two-line comment marker. Every fixture holding it today defines a name twice (`E0428`), which
rustc treats as fatal once name resolution finishes. The collector skips `*.expand.rs`, or a
snapshot would be collected as a fixture.

### The harness

The suite is a **custom test harness written in Rust**, in its own crate,
[`crates/cargo-cgp-ui-tests`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-ui-tests),
whose `ui` target sets `harness = false` and provides its own `fn main`, the same shape as Clippy's
`tests/compile-test.rs`. It is a full workspace member, so `cargo test` runs it. It shells out to
`cargo` and `cargo-cgp` rather than linking the tool's libraries, and it expects a sibling `cgp`
checkout at `../cgp`.

A fixture states what the harness must do through **directives**: line comments starting with `//@`.
The six are `//@aux-build: <crate>`, `//@rewrites-falsely: <reason>`, `//@json`,
`//@env: <KEY>=<VALUE>` (which a `robustness/` fixture uses to crash the compiler on purpose),
`//@quality:`, and `//@codes:`. A misspelled directive would silently do nothing, so the parser
rejects an unknown name, a known name in another comment form such as `// @json`, and a second
`//@codes:`, `//@quality:`, or `//@rewrites-falsely:`. Commented-out `@`-path wiring stays legal.

### How a fixture is compiled

The harness copies the fixture into a throwaway crate named `ui` as `src/main.rs`, with `cgp` as a
path dependency and an empty `[workspace]` table so cargo does not fold it into the repository's
workspace. Re-copying before each pass bumps the mtime, which forces cargo to recompile rather than
serve a cached build with nothing to say.

These constraints shape the harness and are easy to break:

- **Workers:** a cargo build holds an exclusive lock on its target directory, so parallel checks
  need separate ones. Each worker owns a crate under `target/ui-harness/worker-<n>/`, which builds
  `cgp` once per worker. The default count is the machine's parallelism, capped at 8 and the fixture
  count, because many parallel `cgp` builds cost more than they save. Two harness runs at once share
  these crates and corrupt each other's results.
- **Two target directories per worker:** `RUSTC_WORKSPACE_WRAPPER` is part of cargo's fingerprint,
  so the rust-stderr pass builds in `target-rust/`. A shared directory would rebuild `cgp` on every
  alternation.
- **Auxiliary crates:** a cross-crate scenario such as the orphan rule declares
  `//@aux-build: <crate>`. The harness copies the crate from
  [`auxiliary/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-ui-tests/auxiliary)
  into `target/ui-harness/aux/` once per run and rewrites a worker's manifest only when its
  dependency set changes, so ordinary fixtures never disturb the cached `cgp` build. The rejection
  of `// @aux-build:` matters here: a dropped directive leaves a fixture that fails on an unresolved
  import instead of its scenario, which reads as ordinary staleness.
- **The built front-end:** the harness walks up from its own test binary until an ancestor holds
  `cargo-cgp`, because cargo versions put test executables in different places.

Normalization makes output independent of the machine. The `-q` flag removes cargo's progress lines.
The `normalize` module rewrites paths to `$CGP`, `$DIR`, and `$SYSROOT`, replaces a crash report's
thread id with `$TID`, and drops cargo's `could not compile` summary and the note about a long
type's temp file, which only the baseline prints, since it lacks `--verbose`. The baseline alone
also collapses every `Chars<…>` spine to `Chars<..>`, because plain rustc truncates it at a depth
that varies between runs. `--print` shows the raw output.

### Running and blessing

The harness takes its arguments after `--test ui`, so they do not reach the crate's other tests:

```sh
cargo test                                                   # everything
cargo test -p cargo-cgp-ui-tests                             # only the suite
cargo test -p cargo-cgp-ui-tests --test ui -- wiring/        # fixtures whose path contains "wiring/"
cargo test -p cargo-cgp-ui-tests --test ui -- --bless        # rewrite the snapshots
cargo test -p cargo-cgp-ui-tests --test ui -- -j 4           # at most 4 fixtures at once
cargo test -q -p cargo-cgp-ui-tests --test ui -- --list      # every fixture, its quality and codes
cargo test -q -p cargo-cgp-ui-tests --test ui -- --print foo # raw output of each pass, with its status
```

A mismatch prints a line diff per failed pass. A missing snapshot is a mismatch, not an empty
snapshot, so deleting one cannot pass unnoticed. Results print as each fixture finishes, so they
come in completion order.

The three snapshots move for different reasons, which makes a diff informative: `.cgp.stderr` when
the tool's diagnostics change, `.rust.stderr` on a toolchain bump or a shift in the fixture's lines,
and `.expand.rs` when a CGP macro's expansion or the resugaring changes.

**Reading a bless diff means telling three causes apart, and two are not about behavior.** Editing a
fixture's `//!` header moves every line below it, so the `.stderr` files fill with
`--> src/main.rs:N:N` changes, and a widened line number shifts a block's gutter by a column. To see
past that, normalize line numbers and gutter padding out of the old and new snapshots and diff what
remains. Re-bless in the same change that edits a header, or a regression hides among the
mismatches. The third cause is a fixture that has stopped testing what it claims, as with a disabled
`//@aux-build:`. A diff whose *content* changes is never blessed without explaining it first.

### Toolchain and determinism

A snapshot reproduces only under the toolchain it was blessed with, because it contains the
compiler's text. The harness runs under
[`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml),
so a toolchain bump can require a re-bless, and a `.stderr` diff after one is expected. An
`.expand.rs` is steadier but still depends on the compiler's printer and preamble.

The pin covers components as well as the date, and `rust-src` is there only for this suite: rustc
shows the `core` or `std` source line under a diagnostic pointing into the standard library only
when that component is present, so `pass-through/local_blanket_trait` renders differently without
it. `cargo cgp setup` deliberately does not install it, since a user of the tool never runs this
suite.

## Comparison with Clippy

The suite follows Clippy's approach: a custom harness with `harness = false`, driving a tree of
`tests/ui/*.rs` fixtures against committed snapshots with a bless step. Read
[`external/rust/src/tools/clippy/tests/compile-test.rs`](../../../external/rust/src/tools/clippy/tests/compile-test.rs)
beside this crate. These differences are deliberate:

- **Hand-rolled, not [`ui_test`](https://github.com/oli-obk/ui_test).** `ui_test` invokes a compiler
  on each fixture and computes the flags that make a dependency such as `cgp` available. Driving the
  tool through `cargo` lets cargo resolve `cgp`, without a large test dependency, at the cost of
  cargo's own output, quieted with `-q`.
- **The whole tool, not the driver.** Clippy's harness drives `clippy-driver`. Driving the front-end
  exercises `cargo-cgp` as a user invokes it.
- **Three snapshots, not one.** Clippy only adds lints, so it has no "before" worth pinning, and it
  has no `expand` command.

One gap has nothing to do with the harness: no dogfood test runs `cargo-cgp` on this repository's
own crates. These crates do not use CGP, so such a test would find little.

## Further reading

These harnesses share this suite's workflow of compiling each fixture and diffing a committed snapshot:

- [`ui_test`](https://github.com/oli-obk/ui_test): the library Clippy's harness is built on.
- [`trybuild`](https://docs.rs/trybuild): the general compile-fail snapshot harness for Rust crates.

## Tests

Every crate has one unit-test target, and the UI suite has its own. These are the targets, with the
document listing each one's tests:

- [`crates/cargo-cgp/tests/front_end/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/tests/front_end):
  the front-end's helpers ([Executable structure](executable-structure.md#tests),
  [Distribution](distribution/provisioning.md#tests),
  [The expand command](expand-command.md#tests)).
- [`crates/cargo-cgp-driver/tests/driver/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/tests/driver):
  the driver's arguments, panic containment, flush, and other code that needs a compiler's types but
  no compilation ([The driver](driver/program.md#tests)).
- [`crates/cargo-cgp-error-processing/tests/error_processing/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing): the
  wording, tree, and text transforms ([Error processing](error-processing.md#tests)).
- [`crates/cargo-cgp-expand/tests/expand/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-expand/tests/expand): the resugaring and item selection
  ([The expand command](expand-command.md#tests)).
- [`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui): the fixtures, run by the harness's passes.

The harness's own library has these tests, under
[`crates/cargo-cgp-ui-tests/tests/harness/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-ui-tests/tests/harness):

- [`aux.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/aux.rs): a fixture's declared auxiliary crates.
- [`cgp_code.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/cgp_code.rs): the form of a `CGP-Exxx` code.
- [`directives.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/directives.rs): reading each directive, and rejecting the malformed ones.
- [`fixtures.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/fixtures.rs): discovery, and the no-expansion marker.
- [`normalize.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/normalize.rs): the rewrites, the dropped lines, and the spine collapse.
- [`options.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/options.rs): option and filter parsing.
- [`passes.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/passes.rs): the header, status, and pass-through checks, and the JSON reduction.
- [`paths.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/paths.rs): the upward search for the built front-end.
- [`snapshot.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/snapshot.rs): a missing snapshot, blessing, and the line diff.

## Source

- [`crates/cargo-cgp-ui-tests/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-ui-tests):
  the harness: `tests/ui.rs` and the `src/` modules `suite`, `options`, `paths`, `fixtures`,
  `directives`, `harness`, `passes`, `runner`, `aux`, `normalize`, `snapshot`, `blocks`, and
  `cgp_code`.
- [`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui): the fixture tree.
