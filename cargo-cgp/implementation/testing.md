# Testing

`cargo-cgp` is tested at two levels: fast unit tests over each crate's pure logic, and a UI snapshot
suite. The suite is a custom Rust test harness, in the style of Clippy's, that compiles example CGP
programs through the real tool. It pins the tool's rendered output (`.cgp.stderr`) and, for
contrast, the output plain `cargo check` produces for the same fixture (`.rust.stderr`). Every test
lives in its crate's `tests/` directory; per the project's
[AGENTS.md](https://github.com/contextgeneric/cargo-cgp/blob/main/AGENTS.md) the project keeps no
inline `#[cfg(test)]` modules, so all tests are integration tests against a crate's public API.

## The layers of testing

Testing the tool splits along the seam between its two kinds of logic: the ordinary Rust that
decides *how to invoke the compiler* and what to do with its text, and the emergent behavior of
*actually invoking it*. The first is pure and cheap to test; the second only appears when a real
`cargo` drives a real compiler through the driver, so it is exercised by running the whole tool
against example crates and snapshotting what it prints. The unit tests, above all those of the two
rustc-free libraries, guard the former; the UI snapshot suite guards the latter. Each is described
below.

## Unit tests

**Each crate builds its unit tests into one test target**, so `cargo test` links one test binary
per crate rather than one per file. The target is an entrypoint `tests/<name>_tests.rs` that
declares one module directory, `tests/<name>/`, holding a module per subject: `front_end` for the
front-end, `driver` for the driver, `error_processing` and `expand` for the two rustc-free
libraries, and `harness` for the UI harness's own library. A large subject becomes a directory of
its own, as the diagnosis tests have (`error_processing/diagnosis/`, split into the plan, headers,
notes, and helps), and builders that several subjects share live in a `support` module. The UI
suite is the one second target, since it runs with its own `fn main`.

One target per crate matters most for the driver. Its tests link `cargo-cgp-driver`, which links
the compiler's `rustc_driver` dylib, and every such test binary repeats that expensive link. The
link is permitted only in a crate that opts into the `rustc_private` feature, so the driver's
entrypoint `driver_tests.rs` carries the same `#![feature(rustc_private)]` gate as the driver
binary.

**A test pins short output with `assert_eq!` and multi-line rendered output with an `insta`
snapshot.** A rendered dependency tree spans many lines. An inline snapshot shows it as it prints,
and `insta` can update the snapshot in place after a deliberate change. A wording, a header, or a
rewritten line is short enough to compare as a string. The error-processing crate's graph tests are
the worked example.

The argument-handling logic on both sides of the tool is a typical unit-test subject, because it
is pure input-to-output transformation with corner cases that are easy to get wrong and easy to
pin. New argument-handling behavior should arrive with a test rather than a manual check.

Two crates carry these. The front-end's
[`tests/front_end/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/args.rs)
checks that `strip_subcommand` drops the cargo-inserted `cgp` token for the `cargo cgp check` form,
leaves the direct form alone, keeps a later token that merely equals `cgp`, and yields nothing when
only the program name is present. The driver's
[`tests/driver/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/args.rs)
checks that `rustc_args` strips the injected `rustc` path in wrapper mode, leaves a direct
invocation alone, injects `--sysroot` when absent, keeps an existing sysroot, appends an injected
flag when absent, lets an explicit `-Znext-solver` override it, and adds no flag to cargo's `-vV`
and `--print` probes. The harness crate additionally tests its own option parsing and output
normalization, in its `harness` module.

## The UI snapshot suite

The UI suite is modeled on Clippy's: a tree of `.rs` fixtures, each paired with committed snapshots,
checked by compiling the fixture and diffing. Each fixture `<name>.rs` has three siblings:
`<name>.cgp.stderr`, the tool's rendered output; `<name>.rust.stderr`, what plain `cargo check`
prints for the same fixture, the untransformed "before" against which the tool's `.cgp.stderr` is
the "after"; and `<name>.expand.rs`, the Rust the fixture's CGP macros generate, as
`cargo cgp expand` shows it. A fixture that compiles cleanly has an empty `.cgp.stderr` and an empty
`.rust.stderr`, but still has an `.expand.rs`, since expansion happens before type-checking and so
succeeds whether or not the fixture compiles.

**The fixtures live under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui) in one directory per
error class**, so a fixture moves only when its class changes, never when its message improves. The
class directories mirror the [error catalog](../../cgp/errors/README.md): `checks/`, `hidden/`,
`lowering/`, `wiring/`, and `data/`, each holding one directory per class document
(`checks/check-trait-failure/`, `wiring/orphan-rule/`, `data/extensible-data/`, and so on). Mistakes
the catalog does not yet cover sit under `uncataloged/<class>/` (implicit-argument mistakes and
macro defects), each awaiting a catalog page. The largest class, `checks/check-trait-failure/`,
keeps concept sub-directories (`fields/`, `providers/`, `missing-wiring/`, and the rest) so no
directory grows crowded. Three directories hold fixtures that belong to no error class: `ok/` for
programs that compile clean, `pass-through/` for plain Rust errors the tool must render exactly as
rustc does, and `robustness/` for how the tool degrades when the compilation fails under it, such as
a compiler crash or a fatal error while it holds diagnostics. A panic in its own emitter is pinned
by the driver's unit tests instead (see [The driver](driver.md#containing-the-drivers-own-panics)).
Every fixture name is unique across the tree, so a fixture can be found by name alone.

**How well the tool presents a fixture's error is a header field rather than a directory.** Every
error fixture declares `//@quality: acceptable` (the tool leads with the cause), `usability` (the
cause is present but buried), or `hidden` (the cause is absent from the output), and `//@codes: …`
lists the exact `[CGP-Exxx]` codes its output carries (`none` for an uncoded one); the header check
below holds the two in step with the output. `--list` prints every fixture with its quality and
codes, so `--list | grep ^usability` shows the open usability cases. The tree holds one fixture per
post-codegen error class, giving the tool a snapshot of its own transformed output for the whole
catalog; `cgp` has no compile-fail suite of its own, so these fixtures are the maintained copy.

The suite pins *both* halves of that transformation, so the tool's contribution is legible on the
page. The `.cgp.stderr` is the output of `cargo-cgp` itself. Each fixture is compiled by running the
real `cargo-cgp check` end to end, front-end, driver, and all, so the snapshot is whatever the tool
emits, already shaped by the driver's emitter. The `.rust.stderr` beside it is the output of plain
`cargo check` on the same fixture, with no driver and no CGP transforms, and it exists as the
recorded "before". Both snapshots come out of the *same* renderer, the compiler's default human
emitter, because the driver renders the human path itself. The only difference between them is the
transforms the driver applied, so their diff is therefore purely the tool's work, cleaner than a
diff across two different renderers would be. Reading the two side by side shows exactly what the
tool changed: the resugared type names, the renamed wiring traits, and the CGP error codes on the
messages it fully rewrites. As the tool reshapes more diagnostics in the driver's emitter, the
`.cgp.stderr` is what will change while the `.rust.stderr` stays fixed, so the widening gap between
them is the visible measure of the tool's work, and the `.cgp.stderr` diff is the signal that a
change did what was intended. The suite exists so that is caught the moment it lands.

### Three passes per fixture

Each fixture is verified by three passes: two about what the compiler *says* (the tool's real output
and the plain-compiler baseline it improves on) and one about what the macros *generate*. There is
no separate capture or unit pass. Because the driver
applies every CGP transform in-process and renders the result, `.cgp.stderr` is simply what
`cargo-cgp` prints, with nothing to reconcile it against. All three are implemented in
[`passes`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/src/passes.rs):

- **The cgp-stderr pass** runs `cargo-cgp check` directly and compares the tool's rendered stderr to
  `<name>.cgp.stderr`. This is the end-to-end check that the whole binary produces the expected
  output.
- **The rust-stderr pass** runs plain `cargo check` (no `cargo-cgp`, no driver) and compares its
  rendered stderr to `<name>.rust.stderr`. Nothing cross-checks it, because it is the untransformed
  compiler output, not a tool result; it exists to record the "before" the cgp-stderr pass improves
  on.
- **The expand pass** runs `cargo cgp expand` and compares its **stdout** to `<name>.expand.rs`. It
  is the only pass whose artifact is not a diagnostic, and it earns its place twice over: it makes
  every fixture's *generated code* visible beside the error about it, which is where the answer to
  "why does it say that?" usually is, and it is the end-to-end coverage of
  [the expand command](expand-command.md) and the syntax-tree [resugaring](resugaring.md) it drives,
  neither of which any other test exercises through a real compilation.

Three checks then hold each fixture to more than its snapshots. Two compare the passes with each
other, because a snapshot alone cannot catch the two failures that matter most: a crash that prints
nothing, and a rewrite of an error the tool should leave alone. The third checks the fixture's
header.

- **The status check** requires the tool and plain `cargo check` to agree on whether the fixture
  compiles. A crash with no output, or the tool accepting what rustc rejects, would otherwise pass
  whenever the snapshot happened to match. The one known case where the next-generation solver
  accepts a mistake, a namespace inheritance cycle, is no exception here: on the pinned nightly the
  default solver accepts it too (only stable rejects it), so its fixture
  `wiring/namespace-inheritance-cycle/namespace_inheritance_cycle` compiles under both, and the
  check fails if a later nightly makes them disagree.
- **The pass-through check** runs for every fixture under `pass-through/`: a program whose errors
  are plain Rust, which the tool must render exactly as rustc does. It requires the tool's stderr to
  equal plain `cargo check`'s, both normalized as the baseline is, so the property holds without a
  hand-reviewed snapshot. A pass-through fixture whose output still differs from rustc's, for a fix
  still to come or a documented limitation, declares `//@rewrites-falsely: <reason>`; its snapshots
  then pin today's output, and the check reports the marker once the outputs agree, so the fix that
  closes a difference also removes it.
- **The header check** runs for every error fixture (everything outside `ok/`, `pass-through/`, and
  `robustness/`): it requires a `//@quality:` directive and a `//@codes:` list equal to the set of
  `[CGP-Exxx]` codes in the tool's output, so a fixture that gains or loses a code fails instead of
  being re-blessed unnoticed.

A fixture that declares `//@json` also runs **the JSON pass**, which runs
`cargo cgp check --message-format=json` and compares its compiler messages with `<name>.cgp.json`.
Editors and agents read this stream rather than the rendered text, and nothing else exercises it.
The snapshot reduces each message to the fields a consumer uses (its level, code, message, spans,
and children) and leaves out the `rendered` text the `.cgp.stderr` already pins and cargo's artifact
lines. A handful of representative fixtures carry the directive: a resolved check-trait failure, a
use-site failure, an undeclared import, a duplicate wiring key, a merged block (one primary span,
the other site labelled), an untransformed diagnostic, and a clean compile.

The expand pass normalizes less than the other two, deliberately. Only the absolute paths are
replaced; none of the diagnostic normalization applies, and one piece of it would actively hide a
defect. The `Chars<…>` list collapse exists to absorb how rustc truncates a list in a *diagnostic*,
but in an expansion a raw `Chars<…>` list means the resugaring declined, which is exactly what the
snapshot is there to show. (Across the current tree, no expansion contains one outside a fixture's
own doc comment.)

Two small things follow from an `.expand.rs` being Rust. The fixture collector skips `*.expand.rs`,
or a snapshot would be collected as a fixture and then expanded in turn. And a fixture whose
compilation stops before expansion completes has no expansion to record, so its snapshot holds a
two-line comment marker saying so. Two causes stop it that early: a malformed macro invocation, and
a type defined twice, which rustc treats as fatal once name resolution finishes. The marker is worth
pinning, since it says the failure precedes type-checking. The fixtures under
`wiring/conflicting-wiring/` that define a name twice record it: a duplicate component or provider
name, two check tables sharing a check-trait name, and two dispatch traits sharing a method name.

### The harness is a custom Rust test binary

Following Clippy, the suite is a **custom test harness written in Rust**, not a shell script and not
libtest. It lives in its own crate,
[`crates/cargo-cgp-ui-tests`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-ui-tests),
whose `ui` test target sets `harness = false` and provides its own `fn main`
([`tests/ui.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/ui.rs)),
the same shape as Clippy's `tests/compile-test.rs`. The `fn main` is thin; the logic is in the
crate's library so it stays small and testable, split into focused modules: `options` (argument
parsing), `paths` (locating the workspace, fixtures, cgp checkout, and built binaries), `fixtures`
(discovery), `directives` (the `//@` header directives below), `harness` (building the binaries and
compiling a fixture in a worker crate, through `cargo-cgp` or plain `cargo`), `passes` (the
per-fixture passes and the checks across them), `runner` (scheduling fixtures across the worker
pool), `aux` (materializing the auxiliary crates a fixture depends on, described below),
`normalize` (rewriting volatile paths and dropping content-free lines out of the output), and
`snapshot` (compare, bless, diff).

The harness crate is a full workspace member, so `cargo test` runs the whole suite alongside the
unit tests. It shells out to `cargo` and `cargo-cgp`, and its one dependency is `serde_json`,
which reads cargo's message stream for the JSON pass. The driver does every diagnostic transform
in-process, so the harness only launches processes and diffs their output, with no need to link the
tool's libraries. Running the full suite builds the front-end and its driver and expects a sibling
`cgp` checkout at `../cgp` (which each throwaway crate depends on by path), so a plain `cargo test`
needs both present.

A fixture states what the harness must do with it through **directives**: line comments that start
with `//@`, as in Clippy's UI tests, which the compiler ignores and only the harness reads. Six
exist: `//@aux-build: <crate>` (an auxiliary crate, below), `//@rewrites-falsely: <reason>` (the
pass-through exception above), `//@json` (the JSON pass), `//@env: <KEY>=<VALUE>` (an environment
variable for the tool's runs, which a `robustness/` fixture uses to make the compiler crash on
purpose), and the header's `//@quality:` and `//@codes:`. A misspelled directive
would silently do nothing, so the parser rejects an unknown `//@name`, a known name written in
another comment form, such as `// @json` with a space, an `//@aux-build:` without a crate, and a
second `//@codes:`, `//@quality:`, or `//@rewrites-falsely:`, which would silently replace the
first; a comment that merely starts with an `@`-path, such as commented-out wiring, stays legal.

### How a fixture is compiled

A fixture is a loose `.rs` file, so the harness turns it into a crate the tool can check: it
maintains a throwaway crate that depends on `cgp` by path, copies the fixture in as its
`src/main.rs`, and runs `cargo-cgp check -q --color never` there. Naming the crate `ui` keeps
cargo's output stable, and an empty `[workspace]` table in its manifest stops cargo from folding it
into the `cargo-cgp` workspace above it in `target/`. In a full run each of the three passes
compiles the fixture once (the tool, plain `cargo check`, and `cargo cgp expand`), and re-copying it
before each run bumps its mtime, which forces cargo to recompile and re-emit rather than serve a
cached build with nothing to say. The expand pass shares the `cargo-cgp` passes' target directory
and profile, so it reuses their cached dependency builds; cargo re-runs only the fixture crate
itself, whose expansion produces no artifact.

A cross-crate scenario, such as the orphan rule or cross-crate coherence, cannot live in one crate,
so a fixture may pull in **auxiliary crates** with a header directive
(`//@aux-build: cgp-test-crate-a`), the same mechanism Clippy's `aux-build` provides. **The
directive's spelling is exact and a near-miss is rejected rather than ignored**, because a dropped
directive is invisible in a way that matters: the fixture keeps compiling, loses its path
dependency, and fails on an unresolved import instead of reproducing the scenario it was written
for, which reads as ordinary snapshot staleness. A formatter inserting one space (`// @aux-build:`)
is enough to disable a cross-crate fixture this way, which is why the directive parser rejects it.
The `aux` module materializes every stored auxiliary crate once, up front, replacing any earlier
copy so a file deleted from the stored crate does not survive: it copies the crate's source from
[`crates/cargo-cgp-ui-tests/auxiliary/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-ui-tests/auxiliary)
into `target/ui-harness/aux/` and generates its manifest there, substituting the resolved
sibling-`cgp` path (the same path the worker crates use) for the placeholder the stored manifest
carries. When a fixture declares an auxiliary crate, the harness rewrites the worker crate's
manifest to add it as a path dependency before any pass runs; a transitive auxiliary dependency (one
aux crate's `../other-aux` path) resolves through the shared materialized sibling. Because a
worker's manifest is rewritten only when its dependency set actually changes, a run of ordinary
(no-aux) fixtures never disturbs the cached `cgp` build. This is what lets the three cross-crate
orphan-rule fixtures, the published-blanket-trait fixture
`upstream_blanket_trait_use_site`, the positive `ok/cross_crate_wiring.rs`, and the two
cross-crate dispatch fixtures `ok/cross_crate_dispatch_enum.rs` and
`ok/cross_crate_dispatch_payloads.rs` (backed by the `cgp-test-dispatch-traits` and
`cgp-test-dispatch-shapes` auxiliary crates) reproduce what a single crate cannot. One auxiliary
crate has no `cgp` dependency at all: `cgp-test-plain-macros` provides attribute macros whose
expansions fail the way a CGP macro's can, so the `pass-through/` fixtures
`generated_lifetime_without_cgp` and `attribute_splice_without_cgp` pin that a crate without CGP
keeps the suggestions the tool drops in one with it.

The rust-stderr pass builds in a *separate* target directory from the `cargo-cgp` pass:
`target-rust/` beside the worker crate's default `target/`. The reason is cargo's fingerprinting:
`cargo-cgp` sets `RUSTC_WORKSPACE_WRAPPER` and plain `cargo` does not, and that variable is part of
the fingerprint, so sharing one target directory would rebuild `cgp` on every alternation between
the wrapped and unwrapped runs. Two directories keep each variant's `cgp` build cached, at the cost
of compiling `cgp` a second time per worker.

Fixtures are checked in parallel, and the shape of that parallelism is dictated by one cargo
constraint: a `cargo` build holds an exclusive lock on its target directory for the whole build, so
two checks can only overlap if they build in *separate* target directories. The harness therefore
runs a **pool of workers**, each owning its own throwaway crate under
`target/ui-harness/worker-<n>/` (so each gets its own target directory), and hands fixtures to
whichever worker is free (the `runner` module). Reusing a worker's crate across the fixtures it
picks up keeps `cgp` compiled and cached *within* that worker; the price of the isolation is that
`cgp` is built once per worker rather than once overall. The worker count defaults to the machine's
parallelism, capped at both 8 and the fixture count, and is overridable with `--jobs`/`-j` (below).
The cap keeps a many-core machine from starting so many parallel `cgp` builds that the compilation
and disk cost outweighs the parallelism, and `--jobs` raises it again on a machine that can afford
more. Each worker's crate directory carries the worker number, but that absolute path is normalized
to `$DIR`, so a snapshot never depends on which worker produced it. Each fixture's result is printed
the moment it finishes rather than held to the end, so a run streams live; the order is therefore
completion order, not fixture order, which is why every line names its fixture.

The `-q` removes most of the noise: it suppresses cargo's own progress lines (`Checking`,
`Compiling`, `Finished`). What remains and must be normalized away is machine-specific or
non-diagnostic: the absolute paths of the `cgp` checkout, the throwaway crate, and the toolchain
sysroot, the cargo build-failure summary (`could not compile …`, which is cargo's own output rather
than part of any diagnostic), cargo's "process didn't exit successfully" line (which appears only
under coverage instrumentation), and a note pointing at a hash-named temp file when a long type is
elided. The driver's `--verbose` suppresses that elision, so the temp-file note never reaches a
`.cgp.stderr`; but the rust-stderr pass runs plain `cargo check` *without* `--verbose`, so a long
CGP type can be elided there and the note does arise in `.rust.stderr`, which is exactly why
dropping it earns its keep. The sysroot arrives with any diagnostic that points into the standard
library (an implicit `Sized` bound on `Option`, say), and its path carries the contributor's home
directory, the pinned nightly's name, and the host target triple, so it is rewritten to `$SYSROOT`.
The single `normalize` module handles the rendered stderr of both passes: it rewrites the paths to
`$CGP`/`$DIR`/`$SYSROOT`, replaces the thread id in a compiler crash report (which only the
`robustness/` fixture that crashes rustc on purpose prints) with `$TID`, and drops the summary and
temp-file lines, so what is compared depends only on the diagnostic content. The baseline alone also
collapses every `Chars<…>` field-name spine to `Chars<..>`, because plain rustc truncates such a
spine at a depth that varies between runs. The tool's output keeps its spines, since a raw spine
there means the tool's resugaring declined, which the snapshot must show. Normalization applies to
the compared/blessed output only; `--print` shows the raw output untouched. The harness finds the
built `cargo-cgp` by walking up from its own test binary until an ancestor directory holds that
binary, having first built both with `cargo build` (the front-end locates the driver as its
sibling). Searching for the binary rather than counting parent directories keeps the lookup
independent of where cargo puts a test executable, which differs between cargo versions
(`target/debug/deps/` in some, a per-package directory under `target/debug/build/` in others); the
front-end's own place in `target/debug` is the stable anchor.

### Running and blessing

The suite is part of `cargo test`; to run only it, select the crate:

```sh
cargo test                                  # everything (the unit tests + the UI suite)
cargo test -p cargo-cgp-ui-tests            # only the suite
```

To pass an argument to the harness, target the `ui` test explicitly with `--test ui`, so the flag is
not also handed to the crate's other (libtest) tests. The harness accepts a path substring to filter
fixtures, `--bless` to rewrite the snapshots, `--print` to show a fixture's raw output instead of
comparing (the tool's stderr, plain `cargo check`'s stderr, and the expansion, each with its exit
status), and `--jobs N` (`-j N`) to set the worker count:

```sh
cargo test -p cargo-cgp-ui-tests --test ui -- usability    # only fixtures whose path contains "usability"
cargo test -p cargo-cgp-ui-tests --test ui -- --bless      # rewrite all three snapshots per fixture
cargo test -p cargo-cgp-ui-tests --test ui -- -j 4                    # check at most 4 fixtures at once
cargo test -q -p cargo-cgp-ui-tests --test ui -- --print unsatisfied_dependency  # print raw output
```

**`--jobs N`** (`-j N`) sets how many fixtures the harness checks at once; it defaults to the
machine's parallelism, capped at 8 and at the number of fixtures. Raise it past the default on a
machine that can afford more concurrent `cgp` builds (one per worker, since the workers cannot share
a target directory), or set `-j 1` to run fully sequentially.

A mismatch prints a line diff for each pass that failed, labelled with the pass and marking each
line only in the snapshot with `-` and each line only in the actual output with `+`, with two lines
of context. A missing snapshot is a mismatch, not an empty snapshot, so deleting one cannot pass
unnoticed; `--bless` creates it.

After an *intended* change to what the tool emits, `--bless` regenerates all three snapshots (and
`.cgp.json` where the JSON pass runs), the analogue of Clippy's `cargo bless`. It writes
`.cgp.stderr` from the real `cargo-cgp` run, `.rust.stderr` from plain `cargo check`, and
`.expand.rs` from `cargo cgp expand`, and the diff is reviewed before committing. The three move for
different reasons, which is what makes a diff informative: `.cgp.stderr` changes when the tool's
diagnostics change, `.rust.stderr` on a toolchain bump *or* whenever a fixture's own line numbering
shifts, and `.expand.rs` when a CGP macro's expansion changes or when the resugaring does. An
unexpected `.expand.rs` diff after a `cgp` update is a report of what the macros now generate.

**Reading a bless diff means telling three causes apart, and two of them are not about behavior at
all.** Editing a fixture's `//!` header (rewriting a doc pointer, re-wrapping a sentence) moves
every line below it, so both `.stderr` files fill with `--> src/main.rs:N:N` changes and, where a
block's widest line number gains a digit, a one-column gutter shift on every line of that block.
That is pure noise, and the reliable way to see past it is to normalize line numbers and gutter
padding out of the old and new snapshots and diff what remains: what survives is the behavior
change, and if nothing survives there was none. A header edit that shifts lines without re-blessing
leaves the whole suite mismatching, which is worse than it sounds: a genuine regression then hides
among the noise rather than standing out. Re-bless in the same change that edits a header. The third
cause is a fixture that has stopped testing what it claims, of which the disabled `//@aux-build:`
directive above is the worked example. A diff whose *content* changes (a different error code, a
vanished note) is this rather than a shift, and it is never blessed without explaining it first.

### Toolchain and determinism

A snapshot is only reproducible against the toolchain it was blessed with, because it contains the
compiler's diagnostic text. The harness builds and runs under the toolchain the repository pins in
[`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml)
(overridable with `RUSTUP_TOOLCHAIN`), and snapshots must be blessed under that same toolchain.

The pin covers the toolchain's *components* as well as its date, and one of them is there only for
this suite. `rust-src` is no use to the driver, but rustc shows the `core`/`std` source line beneath
a diagnostic that points into the standard library only when that component is present. A fixture
such as `pass-through/local_blanket_trait`, whose error cites `Display`'s definition, renders one
way with it and another way without. Left unpinned, that turns on whichever components a
contributor's toolchain happened to pick up (rustup installs them on demand, and other tools ask for
`rust-src`), and the snapshot flips underneath an unrelated change. Pinning it in
`rust-toolchain.toml` makes the diagnostic content a function of the toolchain file alone, which is
what the rest of this section assumes. It is deliberately *not* added to what `cargo cgp setup`
installs, since a user of the tool never runs this suite. A deliberate toolchain bump can therefore
change the diagnostic wording and require a re-bless, exactly as it does for Clippy. A `.cgp.stderr`
or `.rust.stderr` diff after a toolchain change is expected, not a regression. An `.expand.rs` is
steadier, since it holds generated *source* rather than compiler prose, but it too is
toolchain-dependent: the compiler's own pretty-printer lays it out, and the injected
`#![feature(prelude_import)]`/`extern crate std` preamble comes from the edition's prelude. A
passing `hidden/unsatisfied-dependency/unsatisfied_dependency` snapshot is also the standing proof
that the driver genuinely stands in as the compiler, since its un-hidden root cause could only be
produced by compiling the fixture through the tool.

## Comparison with Clippy

The suite matches Clippy's *approach* closely: a custom Rust test harness with `harness = false` and
its own `fn main`, driving a tree of `tests/ui/*.rs` fixtures against committed snapshots with a
bless step. The mental model transfers directly, and
[`external/rust-clippy/tests/compile-test.rs`](../../../external/rust-clippy/tests/compile-test.rs)
is the reference to read alongside this crate. Two deliberate differences remain.

First, the harness is **hand-rolled rather than built on the
[`ui_test`](https://github.com/oli-obk/ui_test) library** Clippy uses. `ui_test` invokes a compiler
directly on each fixture and, via its `DependencyBuilder`, computes the `--extern`/`-L` flags needed
to make a dependency like `cgp` available. The hand-rolled harness sidesteps that machinery, and the
version-coupling of a large test dependency, by driving the whole `cargo-cgp` tool through `cargo`,
which resolves `cgp` for us. The cost is that compilation goes through cargo (its progress noise,
quieted with `-q`) instead of straight to the compiler.

Second, and following from that, the harness **drives the whole tool, where Clippy's `ui_test`
drives `clippy-driver` directly**. Driving the front-end is a stronger end-to-end test, since it
exercises `cargo-cgp` as a user invokes it, and it is what makes the cargo-resolves-`cgp` shortcut
possible. If the suite grows enough to want per-diagnostic control (inline `//~` annotations,
rustfix, and the like), adopting `ui_test` pointed at `cargo-cgp-driver` is the natural next step.

A third, smaller difference is that the suite pins *three* snapshots per fixture where Clippy pins
one. One extra is the `.rust.stderr` baseline: it records plain `cargo check`, which Clippy never
needs because it only *adds* lints to rustc's output rather than rewriting it, so it has no "before"
worth pinning. `cargo-cgp` rewrites, so the before/after pairing is what makes the rewrite legible.
The other is the `.expand.rs`, which covers the `expand` command Clippy has no counterpart for.
There is no unit-test pass against Clippy's either, and none is possible: the driver applies its
transforms in-process while rendering, so there is no separately renderable stage to check apart
from the end-to-end run.

One gap against Clippy is unrelated to the harness: there is no dogfood test that runs `cargo-cgp`
on this repository's own crates. It becomes worthwhile as the tool's diagnostic transforms grow,
when running them against real crates would catch regressions the curated fixtures miss.

## Further reading

These are the snapshot harnesses this suite's design draws on; both compile each fixture and diff a
committed snapshot with a bless step, the workflow reproduced here.

- [`ui_test`](https://github.com/oli-obk/ui_test): the UI-test library Clippy's harness is built on.
- [`trybuild`](https://docs.rs/trybuild): the general compile-fail snapshot harness for Rust crates;
  this suite holds the post-codegen CGP failures a `trybuild` suite would otherwise carry.

## Tests

The tests this document describes are the argument-handling tests, the harness crate's own unit
tests, and the UI snapshot suite, each a module of its crate's one unit-test target except the
suite. There is no dogfood test yet (see above).

- [`crates/cargo-cgp/tests/front_end/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/args.rs):
  `strip_subcommand` across the `cargo cgp check` form, the direct form, a later matching token, and
  the program-name-only case.
- [`crates/cargo-cgp-driver/tests/driver/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/args.rs):
  `rustc_args` across wrapper-mode stripping, a direct invocation, sysroot injection, an existing
  sysroot, injected-flag appending, an explicit `-Znext-solver` override, and the `-vV` and
  `--print` probes that receive no flags.
- [`crates/cargo-cgp-ui-tests/tests/harness/options.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/options.rs),
  [`crates/cargo-cgp-ui-tests/tests/harness/normalize.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/normalize.rs):
  harness option/filter parsing, and the output normalizer: the `$CGP`/`$DIR`/`$SYSROOT` path
  rewrites, the `$TID` thread id of a crash report, the dropped content-free lines (including the
  coverage failure line), the baseline's `Chars<…>` spine collapse across every truncation depth,
  and the tool output keeping its spines.
- [`crates/cargo-cgp-ui-tests/tests/harness/paths.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/paths.rs):
  the upward search for the built front-end, against both layouts cargo has put a test binary in
  (`<profile>/deps/` and `<profile>/build/<package>/<hash>/out/`), plus the nearest-ancestor rule,
  the absent case, and the file-not-directory rule that keeps cargo's own `build/cargo-cgp/`
  directory from being mistaken for the binary.
- [`crates/cargo-cgp-ui-tests/tests/harness/aux.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/aux.rs):
  the `//@aux-build:` parser: one and several declared crates, a fixture declaring none, an
  unreadable fixture, and the malformed-directive guard from both sides: a space after the slashes
  and a doc-comment form are rejected, while prose mentioning the syntax is not.
- [`crates/cargo-cgp-ui-tests/tests/harness/directives.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/directives.rs):
  every directive read together, none declared, `//@codes: none`, commented-out `@`-path wiring left
  alone, and the rejection of an unknown directive, a spaced directive, a `//@rewrites-falsely:`
  without a reason, an `//@env:` without an assignment, an `//@aux-build:` without a crate, a
  malformed code, an unknown quality, and a second `//@codes:` or `//@quality:`.
- [`crates/cargo-cgp-ui-tests/tests/harness/passes.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/passes.rs):
  the header check (exact codes, a missing directive, `//@codes: none`), the collection of codes
  from output, the status check (agreement and disagreement in both directions), the pass-through
  check (equal output, a difference, and the `//@rewrites-falsely:` marker in both states), and the
  reduction of cargo's JSON stream to compiler messages.
- [`crates/cargo-cgp-ui-tests/tests/harness/snapshot.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/snapshot.rs):
  a missing snapshot reported as a mismatch, blessing it into existence, and the line diff's
  context and markers.
- [`crates/cargo-cgp-ui-tests/tests/harness/fixtures.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-ui-tests/tests/harness/fixtures.rs):
  fixture discovery: nested directories are collected in order, an `.expand.rs` snapshot is not
  collected as a fixture, and the no-expansion marker is a valid Rust comment block.
- [`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui): the UI snapshot
  fixtures, each `<name>.rs` paired with a blessed `<name>.cgp.stderr` (the tool's output) and
  `<name>.rust.stderr` (the plain-`cargo check` baseline) and its `.expand.rs` generated code, run
  by the harness's three passes.

## Source

- [`crates/cargo-cgp-ui-tests/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-ui-tests):
  the custom UI-test harness: `tests/ui.rs` (the `harness = false` entrypoint) and the `src/`
  modules (`options`, `paths`, `fixtures`, `directives`, `harness`, `passes`, `runner`, `aux`,
  `normalize`, `snapshot`).
- [`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui): the fixture tree,
  one scenario per `.rs` file with its `.cgp.stderr`, `.rust.stderr`, and `.expand.rs` snapshots,
  grouped into error-class directories beside `ok/`, `pass-through/`, and `robustness/`.
- [`crates/cargo-cgp/src/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/args.rs),
  [`crates/cargo-cgp-driver/src/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/args.rs):
  the modules the argument tests cover.
