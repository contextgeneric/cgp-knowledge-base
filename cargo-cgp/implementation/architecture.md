# Architecture

`cargo-cgp` is four shipped crates and a test harness, split so that only one crate links the
compiler and the logic that needs no compiler can be tested on any toolchain. This document is the
map: the crates, the flow of a diagnostic through the driver, and the module layers inside it. Each
subsystem's own document holds the detail.

## The crates

The crates form a small tree, with the compiler's internal libraries linked only at one node. These
are the crates and what each one holds:

- **`cargo-cgp`:** the front-end, the cargo subcommand a user runs. It launches cargo with the
  driver wired in and forwards cargo's output, and it depends on no other crate here, so
  `cargo install` builds it on stable Rust ([Executable structure](executable-structure.md),
  [Distribution](distribution.md)).
- **`cargo-cgp-driver`:** the `rustc` replacement cargo calls for each workspace crate. It runs the
  real compiler in-process through `rustc_driver`, and it is the one crate that needs the pinned
  nightly ([The driver](driver.md)).
- **`cargo-cgp-error-processing`:** the rustc-free half of the diagnostics: the root-cause model and
  its wording, the dependency tree, the text transforms, and the spelling rules
  ([Error processing](error-processing.md)).
- **`cargo-cgp-expand`:** the rustc-free half of `cargo cgp expand`, which resugars the source the
  compiler printed ([The expand command](expand-command.md)). It calls the error-processing crate's
  spelling rules, so a name is spelled the same in an expansion and in a diagnostic.
- **`cargo-cgp-ui-tests`:** the snapshot harness, which is not shipped ([Testing](testing.md)).

The line between the driver and the rustc-free crates follows one rule: compiler state is read into
an owned, `String`-only model at the edge, and everything downstream of that model lives outside the
compiler's linkage. The wording of an error therefore gets unit tests that run in milliseconds,
while the code that reads the compiler is pinned by whole-program fixtures.

## The flow of a diagnostic

Every transformation runs inside the driver, in three steps, because only the driver can reach the
live `TyCtxt`. A front-end that saw only cargo's serialized output could not name the traits behind
a component marker or re-run a check obligation, so the front-end plays no part beyond launching
cargo and letting its output stream through.

**Configure** adds two flags to each workspace crate's compilation, each changing how the compiler
produces diagnostics rather than rewriting what it built. `-Znext-solver=globally` reaches the
missing leaf bound the default solver may stop short of
([choosing the trait solver](driver.md#choosing-the-trait-solver)), and `--verbose` stops rustc
compressing the deep `Symbol` and `Cons` types a CGP error carries
([un-eliding the diagnostic](driver.md#un-eliding-the-diagnostic)).

**Transform** runs in
[`CgpEmitter`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/cgp_emitter.rs),
which receives each diagnostic before any inner emitter sees it. It tries an ordered list of stages,
each recognizing one class of mistake and returning a `Verdict`: continue, drop the diagnostic, or
reshape it ([Diagnostic reshapes](diagnostic-reshapes.md)). A diagnostic no stage claims goes to the
[typed resolver](typed-root-cause-resolution.md), which replaces a wiring failure with its
root-cause tree. When the resolver declines, a text rewrite names the traits behind any wiring notes
it recognizes. Either way the [post-processing chain](error-processing.md) then runs, so no raw CGP
construct leaks from a diagnostic the tool did not rewrite.

**Render** happens at the end of the compilation, because deciding a block's final form needs every
diagnostic. The emitter buffers each result, and its `Drop` flushes the buffer: it coalesces
failures that share a root cause, renders each `root cause:` note against what earlier blocks drew,
and rebuilds the "detailed explanations" footer. The result goes to the inner emitter, the one the
compiler's `default_emitter` would build for the active error format, so JSON and human output both
come from the compiler's own renderers. A fixture's `.cgp.stderr` and its plain `.rust.stderr` share
a renderer for that reason, and their difference is purely the tool's work.

A panic anywhere in the transform or the flush falls back to the diagnostics rustc built, so the
tool cannot lose an error
([containing the driver's own panics](driver.md#containing-the-drivers-own-panics)).

## The driver's modules

The driver's modules import in one direction, which keeps each part readable and testable without
the parts above it. These are the top-level modules:

- **`args`, `callbacks`, `run`, `help`, `version`, `config`:** the program: its arguments, the
  compiler callbacks, and the names it compares against.
- **`emitter`:** the stages, the buffer, the flush, and the containment.
- **`detect`:** the class detectors the stages call. Each confirms one mistake from compiler state
  and fills a rustc-free model, without the resolver's walk.
- **`resolve`:** the typed resolver, and the `query` layer the detectors share with it.
- **`component_map`:** the name map behind the text rewrite.
- **`expand`:** expand mode.

Inside `resolve`, a module imports only modules earlier in this order:

1. `query`, `cache`, and `ctx`: the compiler readers and solver helpers, the cache, and
   `ResolveCtx`.
2. `data`: the extensible-data traits and the partial-value reader.
3. `label`: the structured node for each obligation.
4. `classify`: each leaf's decision and its fix facts.
5. `walk`: the descent to the leaves.
6. `call_site`: the anchors that re-read a failing call.
7. `anchor`: the span-matching anchors.
8. `overflow`: the `E0275` analysis.
9. `anchors`: the ordered list of anchors `resolve` tries.

The detectors import the `query` layer and one another, never the rest of the resolver, so a
detector cannot depend on the walk.

## The resolve context

`ResolveCtx` carries the compiler handle and a borrow of the
[dependency cache](cached-dependency-resolution.md) through the anchors and the walk as one value,
and its lifetimes explain its shape. `CgpEmitter` is built at session setup, before any `TyCtxt`
exists, so it cannot name `'tcx`. During emission the compiler handle is reachable only through
`rustc_middle::ty::tls::with_opt`, for a lifetime bounded by that closure, so the borrow checker
forbids storing it. The state therefore splits in two:

- **`ResolveCache`:** owned, free of compiler lifetimes, and kept on the emitter for the whole
  compilation.
- **`ResolveCtx`:** a `Copy` of the `TyCtxt` and a borrow of the cache, built per diagnostic inside
  the closure.

Reusing the cache across closures is sound because one crate's compilation has one `GlobalCtxt`, so
every entry yields a handle to the same compiler state, and the cache's keys are compiler-free and
its values owned. A step that never reads the cache, such as a detector, takes the `TyCtxt` alone.

## Comparison with Clippy

Clippy is also a diagnostic tool built on this integration, but it adds diagnostics where
`cargo-cgp` rewrites the ones rustc built. Both work inside the compilation and let cargo carry the
output out unchanged, so neither processes output in its front-end. Clippy registers lint passes and
keeps the compiler's default emitter, while `cargo-cgp` wraps that emitter in one that edits each
diagnostic first. Clippy also has no rustc-free crate, since its lints have no wording logic dense
enough to need testing apart from the compiler. The
[driver's comparison](driver.md#comparison-with-clippy) gives the detail.

## Tests

The UI snapshot suite covers this document's own concern: every fixture's `.cgp.stderr` is what the
whole tool, front-end and driver, printed. Each subsystem's document lists its own tests.

- [`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui): the fixtures,
  compiled through the tool and compared with their snapshots ([Testing](testing.md)).

## Source

The crates are listed above, and these are the entry points into the flow:

- [`crates/cargo-cgp/src/launch/command.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/launch/command.rs):
  the wrapped cargo command.
- [`crates/cargo-cgp-driver/src/run.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/run.rs):
  the driver's entry point, with its flags.
- [`crates/cargo-cgp-driver/src/emitter/cgp_emitter.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/cgp_emitter.rs):
  the stage list and the buffering.
- [`crates/cargo-cgp-driver/src/emitter/flush/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter/flush):
  the flush.
- [`crates/cargo-cgp-driver/src/resolve/anchors.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/anchors.rs):
  the anchor list.
- [`crates/cargo-cgp-driver/src/resolve/ctx.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/ctx.rs):
  `ResolveCtx`.
