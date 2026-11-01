# The driver

`cargo-cgp-driver` is the `rustc` replacement cargo runs for each workspace crate. It runs the real
compiler in-process through `rustc_driver`, which is the whole reason it exists: only in-process can
it install the callbacks and the emitter that read and rewrite diagnostics. Aside from the injected
flags, that emitter, and expand mode, it compiles exactly as `rustc` would. The front-end that
invokes it and the environment contract between them are in
[Executable structure](../executable-structure.md), and the flow its transformations sit within is in
[Architecture](../architecture.md).

## How cargo invokes the driver

Cargo runs the driver as `RUSTC_WORKSPACE_WRAPPER` prescribes: the wrapper, the real compiler's
path, then the rustc arguments.

```text
cargo-cgp-driver  /path/to/rustc  --edition=2024  --crate-name foo  src/lib.rs  ...
```

**A direct invocation answers the tool's own queries first.** `--help`, `-h`, or no arguments prints
the help, and `--version` or `-V` prints the handshake the front-end's preflight reads. This is
gated on not being in wrapper mode, because there the same flags belong to the compiler cargo is
probing.

## Preparing the argument vector

The steps run in an order that matters:

1. **Read with rustc's `raw_args`,** which reports a non-Unicode argument as a fatal error where
   `env::args` would panic. This comes before the panic hooks are installed, because rustc's ICE
   hook reads `env::args` itself when `RUST_BACKTRACE` is unset. The direct-query checks use a lossy
   copy, in which such an argument matches no flag.
2. **Expand `@file` arguments before reading any flag.** Cargo moves a long command line into a
   file, so `--cgp-expand=` and a user's `-Znext-solver`, `--verbose`, or `--sysroot` may sit inside
   it. An unreadable file ends the compilation with rustc's own fatal error.
3. **Take out the expand request,** since it is no rustc flag. Expand mode also leaves the two
   diagnostic flags off, because it stops before analysis.
4. **Drop the compiler path in wrapper mode** (the second argument's file stem is `rustc`).
   `compiler_entrypoint` ignores the first element and reads the rest as flags, so the path would
   become an input file.
5. **Inject flags, each only when absent, so an explicit choice always wins:** `--sysroot` from
   [`CARGO_CGP_SYSROOT`](../executable-structure.md#the-environment-contract), since a driver outside a
   toolchain cannot find `std`, then [`-Znext-solver=globally`](#choosing-the-trait-solver) and
   [`--verbose`](#un-eliding-the-diagnostic). Absence is checked in every spelling rustc accepts:
   `key`, `key=value`, `-Z key=value` as two arguments, and `-v` for `--verbose`.

**The two diagnostic flags are skipped for cargo's info queries,** `-vV` and `--print`. `-vV`
already implies `-v`, so a second one makes rustc reject the invocation, and a query carrying
unexpected flags also poisons cargo's cache.

## Running the compiler

`catch_with_exit_code` runs the compiler and returns what plain `rustc` would. `CgpCallbacks` adds
two hooks:

- **`config`** installs the emitter and turns on `trimmed_def_paths`, as rustc's own driver does. A
  compiler run through `rustc_driver` leaves it off, so every diagnostic the tool leaves alone would
  print paths plain rustc shortens, suggestions included
  ([`suggestion_full_paths`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/suggestion_full_paths.rs)).
- **`after_expansion`,** called once name resolution is over, reshapes in a check
  [an unresolved wiring name](diagnostic-reshapes.md#reshaping-an-unresolved-wiring-name) and
  [a misspelled `#[use_type]` import](diagnostic-reshapes.md#replacing-the-help-on-a-misspelled-use_type-import),
  and
  [drops a suggestion that names a generated identifier](diagnostic-reshapes.md#dropping-a-suggestion-that-names-a-generated-identifier).
  In [expand mode](../expand-command.md) it prints the crate and stops the compilation instead.

## Accessing the Rust compiler API

The driver links the compiler's internal crates through `rustc_private`, and three facts shape the
crate:

- **The compiler crates come through `extern crate` in `lib.rs`,** never `[dependencies]`. The only
  Cargo dependencies are the rustc-free `cargo-cgp-error-processing` and `cargo-cgp-expand`.
- **The feature gate sits on both the library and the binary,** because the binary links the
  compiler dylib, and that link needs the linking crate to opt in.
- **The API ships only with a nightly carrying `rustc-dev`,** so `rust-toolchain.toml` pins an exact
  nightly ([the bump](../distribution/pinned-nightly-bump.md)). That nightly is the compiler the driver embeds, and
  the sysroot must belong to it, or the driver loads the wrong `librustc_driver`. Verify each use of
  the API against [`../external/rust`](../../../../external/rust), since it moves between nightlies.

## The driver's diagnostic transformations

The driver changes diagnostics in two ways. Two **argument levers** change how the compiler produces
them and need no parsing. Everything else runs in a **custom emitter**, on diagnostics already
built, using facts only the live compiler holds. Its stages run in order, as
[Architecture](../architecture.md#the-flow-of-a-diagnostic) describes, and
[Diagnostic reshapes](diagnostic-reshapes.md) covers each. A diagnostic no stage claims goes to the
[typed resolver](../typed-resolution/overview.md), then to the
[text rewrite](diagnostic-reshapes.md#naming-the-traits-behind-a-component-marker) if it declines.
[Post-processing](../error-processing.md) then cleans up every rewritten diagnostic, and changes an
untransformed one only where it recovers a CGP encoding.

**The emitter wraps the one the compiler would have built.** `CgpEmitter` is generic over an inner
emitter, and `install` rebuilds the compiler's `default_emitter` for the active format, since
`DiagCtxt::set_emitter` replaces the session's emitter with no way to recover it. Only
`emit_diagnostic` differs. It edits the `DiagInner` in place, so the change reaches a JSON
diagnostic's `children` and regenerated `rendered` field and a human diagnostic's text alike.

### Choosing the trait solver

**`-Znext-solver=globally` un-hides a cause the default solver does not report, with no parsing.**
On stable, a consumer method call's failure stops at the provider trait (`Person: Greeter<Person>`)
and never reaches the missing bound. The pinned nightly names the bound in a note, but with the
field name elided and under method-probe advice. The next solver names
`Person: HasField<Symbol!("name")>`
([`unsatisfied_dependency`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unsatisfied_dependency.rs)).
Only workspace crates go through the driver, so dependencies still build with the default solver.

**The two solvers are not fully compatible, an accepted cost of using this one as the diagnostic
engine**
([significant changes and quirks](https://rustc-dev-guide.rust-lang.org/solve/significant-changes.html)).
A crate could fail under `cargo cgp check` and compile under `cargo check`, or the reverse. The
reverse is real: two namespaces that inherit from each other are rejected by stable `rustc` with an
`E0275`, but compile clean here, and under the pinned nightly's default solver too. That is a
missing error, not a hidden cause
([`namespace_inheritance_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-inheritance-cycle/namespace_inheritance_cycle.rs),
which has two empty snapshots).

### Un-eliding the diagnostic

**`--verbose` targets a cause the compiler computes and then elides while printing.** rustc
compresses long types, and each compression destroys a CGP error, whose types are deep `Symbol` and
`Cons` lists:

- **Similar-impl hints** replace every generic argument the two traits share with `_`. For `height`
  beside `width`, the shared `'h'` collapses in both names, so the field cannot be read back
  ([`base_area_1`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_1.rs)).
- **Long types** are truncated, with the full form written to a `long-type-*.txt` file.
- **Long impl lists** collapse to "and N others".

All three are gated on `opts.verbose`. It is not `-Zverbose-internals`, so the compiler's internal
debug printing stays off and the diagnostics keep their shape
([the suppression points](../rustc-diagnostic-internals.md#the-suppression-points)). The emitter undoes
one of the three: it cuts a failed bound's implementors back to rustc's eight and "and N others",
because a CGP crate implements `IsProviderFor` hundreds of times
([`many_implementors`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/many_implementors.rs)).

**The flag reaches every diagnostic, a known limitation kept because both alternatives cost more.**
`opts.verbose` is fixed once the session is built, so a diagnostic the tool leaves alone also prints
un-elided: a `#[cgp_impl]` signature mismatch names `__Context__` where rustc prints `_`
([`provider_wrong_signature`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/provider_wrong_signature.rs)),
and a crate's own `Symbol<1, Chars<'a', Nil>>` prints in full
([`lookalike_cgp_names`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/lookalike_cgp_names.rs)).
Without the flag, a diagnostic the resolver declines loses its field names. Re-eliding the text
afterward cannot work, because the text does not record which arguments the two compared types
shared.

## De-duplicating and coalescing

One mistake surfaces at many sites because CGP wiring is lazy, so the emitter removes repeats in two
steps: de-duplication on arrival, and coalescing at the flush. **No trait's failure is ever
hidden:** the first step removes only re-reports of one failure, and the second states a shared
cause once while naming every site.

**The
[`DedupLedger`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/dedup.rs)
suppresses a transformed diagnostic whose span-independent signature it has seen,** and it has three
keys:

- **Recovered cause:** the context, the consumer traits, and each leaf. Two distinct consumers that
  share a cause keep separate signatures, so both survive to be coalesced.
- **Rendered text:** for a diagnostic the resolver declined and the text rewrite changed.
- **Coded class headline, in one direction only:** a resolved report records it but never consults
  it, and a declined report is suppressed when a resolved one recorded its headline. So a declined
  fallback that arrived first never hides the resolved tree, and two resolved reports with different
  causes both reach the flush. A resolved report records its class headline rather than the cause it
  displays, since the text rewrite words only the class.

**The emitter holds every diagnostic and flushes from `Drop`,** because stating a shared cause needs
all its sites and the `Emitter` trait has no end-of-compilation hook. `Drop` runs in the
`DiagCtxt`'s teardown, while the inner emitter is still alive. The diagnostics were counted as they
arrived, so cargo's summary and the visible blocks agree. An untouched `rustc` error stays a plain
entry, emitted at its arrival position, so a CGP block beside an unrelated `E0308` keeps its order.

**Failures group by sharing any root cause, transitively, not by an equal cause set.** The depths
one mistake surfaces at see different subsets: a check entry stops at the first unmet leaf on its
branch, while a use-site call walks every wired component. Those subsets overlap without being
equal, so an exact key would group none, and the block holding their union would have every root
already drawn. Transitivity makes this a partition, with the invariant that **no two coalesced
blocks share a root cause**. Each cause is keyed on its `Leaf` structurally, so rewording a lead
shifts nothing. A leaf names its owner, so failures on different contexts can group, while an
ordinary bound names none and is keyed with its context. Only a failure whose rewritten headline
gives way to its cause coalesces, so a type mismatch does not.

**A group of several becomes one block.** Its members are in source order, the first entry takes the
one caret, and the others are labelled "also required here". Its headline states the shared cause
under the first member's class code, or every member's class sentence with a count when the causes
are mixed. Its causes pass through `Causes::union`
first, because members grouped for sharing a cause hold one copy each, and would otherwise state the
mistake once per member. The [dependency graph](../dependency-graph-rendering.md) then does the
merging, so the chain that subsumes another leads
([`density_3`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/density_3.rs),
[`dependency_cascade`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/dependency_cascade.rs)),
and independent chains render side by side
([`parallel_consumers`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/parallel_consumers.rs)).
Every resolution's note is rendered at the flush, even one that does not coalesce, because only then
is the emission order known for
[eliding against earlier blocks](../dependency-graph-rendering.md#eliding-across-blocks).

**An untouched error is merged only when rustc reports it twice.** In a crate that uses CGP,
`merge_repeats` folds a later diagnostic with the same level, code, and message, and a primary caret
on the same line, into the earlier block. rustc repeats an error that way when it checks one
requirement per generated item, or a call's bound for the call and an argument
([`implicit_conflicting_types`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/implicit-arguments/implicit_conflicting_types.rs),
[`transform_map_fields_missing_marker`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/transform_map_fields_missing_marker.rs)).
A caret the earlier block does not cover is kept, labelled, so no location is lost. A crate without
CGP keeps both
([`repeated_bound_without_cgp`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/repeated_bound_without_cgp.rs)).

## Containing the driver's own panics

**A panic in the driver's own code never costs the user their diagnostics.** The emitter runs
compiler code inside `emit_diagnostic` and renders from `Drop`, while the thread unwinds from
rustc's fatal-error abort, so a bug in either would lose the output or abort the process. So both
run under `catch_unwind`:

- **A panic in a transform** buffers that diagnostic as rustc built it, with a note naming the panic
  and the issue tracker, and the compilation goes on.
- **A panic in the flush** emits every buffered diagnostic as rustc built it, each resolution with
  the same note, in arrival order.
- **A `FatalErrorMarker` unwind** is rustc aborting rather than a panic of the driver's, so
  containment lets it continue
  ([`fatal_after_buffered_diagnostic`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/robustness/fatal_after_buffered_diagnostic.rs)).

**A crash elsewhere in the compiler keeps rustc's output order.** Plain rustc prints errors before a
later ICE report, and the emitter's buffer would put them after it. So the driver wraps rustc's ICE
hook, installed with cargo-cgp's tracker as the bug-report URL: a panic the emitter is containing is
recorded for the note and printed nowhere, and any other first has the emitter emit its buffer,
untransformed, then hands over. They go out untransformed because a second panic inside a panic hook
aborts the process, so a crash is no time to run the flush's rendering
([`ice_after_buffered_diagnostic`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/robustness/ice_after_buffered_diagnostic.rs)).

**No input is known to make the emitter panic, so the fallback is tested through its own
functions.** `transform_or_original` and `render_or_untransformed` take the step as a closure, and
the unit tests pass one that panics. The shipped driver carries no switch that makes it panic, and
must not gain one.

## Comparison with Clippy

The driver follows `clippy-driver` in its skeleton: both detect wrapper mode the same way, inject
`--sysroot` only when absent, and run `compiler_entrypoint` inside `catch_with_exit_code`
([`external/rust/src/tools/clippy/src/driver.rs`](../../../../external/rust/src/tools/clippy/src/driver.rs)).

The transformations diverge where the purpose does. Clippy's `config` callback calls
`register_lints` to add lint passes that emit *new* diagnostics; `cargo-cgp`'s `config` callback
installs a diagnostic *emitter* that *rewrites* the compiler's existing notes. That is the same
`Callbacks` lever put to the opposite end (adding versus clarifying), and it is why the driver reads
the `TyCtxt` from a custom emitter where Clippy reads it from a lint pass. The `--sysroot` handling
also diverges structurally, because `cargo-cgp-driver` is out-of-tree while `clippy-driver` ships
inside the toolchain; that difference belongs to the shared environment contract and is covered in
[Executable structure](../executable-structure.md#comparison-with-clippy).

The remaining differences are where the driver is simpler than Clippy, or does more:

- **Argument reading.** Both read `rustc_driver::args::raw_args`, but the driver then expands
  `@file` arguments before reading its flags, where Clippy reads them unexpanded and peeks inside an
  argument file only for `--sysroot`. The driver needs the full expansion because its own
  `--cgp-expand=` flag can sit in the file.
- **Driver front-matter.** Both drivers install rustc's logger (`init_rustc_env_logger`) and its
  ICE hook (`install_ice_hook`) with their own bug-report URL, and both answer `--version` and
  `--help`. `cargo-cgp` additionally wraps the ICE hook, so a panic its emitter contains is not
  reported and a real crash prints the buffered diagnostics first (see
  [Containing the driver's own panics](#containing-the-drivers-own-panics)); Clippy emits as it
  goes and needs neither. Clippy also has a `--rustc` passthrough, which `cargo-cgp` lacks.
- **Info-query handling.** Clippy detects cargo's info queries (`-vV`, `--print`) and its
  `--cap-lints=allow` / `--no-deps` cases to *skip* running its lints for them. The driver already
  skips *flag injection* for `-vV` and `--print` (above), and its emitter rewrite is a no-op on the
  diagnostic-free output of an info query, so it needs no further guard.
- **Callbacks.** Clippy carries three `Callbacks` implementations (default, rustc-only, and
  lint-registering) and selects among them per invocation. `cargo-cgp` has one `CgpCallbacks`, which
  varies by its fields rather than by type: its `config` hook always installs the rewriting emitter,
  and its `after_expansion` hook reshapes the name-resolution errors, replaces the help on a
  misspelled `#[use_type]` import, and drops the suggestions that name a generated identifier in a
  check, and prints the expansion when the invocation carried an expansion request.

## Further reading

- [rustc_driver and rustc_interface, in the Rust Compiler Development Guide](https://rustc-dev-guide.rust-lang.org/rustc-driver/intro.html),
  describes `rustc_driver::compiler_entrypoint` and the `Callbacks` trait: the entry point the
  driver calls and the hook `CgpCallbacks` implements.
- [Example: Getting diagnostics, in the Rust Compiler Development Guide](https://rustc-dev-guide.rust-lang.org/rustc-driver/getting-diagnostics.html),
  walks a minimal `rustc_driver` program that installs a custom emitter through `psess_created`, the
  same hook the driver uses. The guide shows a `Translate`-based emitter API the pinned nightly
  lacks.
- [Tracking issue for crates that are compiler dependencies (#27812), rust-lang/rust](https://github.com/rust-lang/rust/issues/27812),
  is the `rustc_private` feature's tracking issue, the background for why linking the compiler
  crates needs a nightly toolchain with the `rustc-dev` component.
- [Next-gen trait solving, in the Rust Compiler Development Guide](https://rustc-dev-guide.rust-lang.org/solve/trait-solving.html),
  explains what `-Znext-solver` selects and how it evaluates goals.

## Tests

- [`tests/driver/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/args.rs):
  wrapper-mode stripping, flag injection in each spelling, the info-query skips, and `@file`
  expansion.
- [`tests/driver/run.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/run.rs):
  a non-Unicode argument exits with rustc's error rather than a panic.
- [`tests/driver/help.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/help.rs):
  the help flags and text.
- [`tests/driver/containment.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/containment.rs):
  `contain`, and both fallbacks with a panicking step.
- [`tests/driver/footers.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/footers.rs):
  the `rustc --explain` footer naming only the codes still shown.
- [`tests/driver/pipeline.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/pipeline.rs):
  `apply_reshape`'s span policies, and a verdict ending the stage chain.
- [`tests/driver/repeats.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/repeats.rs):
  each condition of `merge_repeats`.
- [`tests/driver/flush.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/flush.rs):
  grouping, a merged block's shape, elision across blocks, and a note's place before the `help`s.
- [`tests/driver/postprocess.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/postprocess.rs):
  a rewritten span label keeping its spans.
- [`tests/error_processing/dedup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/dedup.rs)
  and
  [`internal_error.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/internal_error.rs):
  the ledger's keys, and the note after a contained panic.
- [`tests/ui/pass-through/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/pass-through):
  diagnostics the tool leaves alone matching plain `cargo check`, and the `--verbose` limitation,
  marked `//@rewrites-falsely:`.
- [`tests/ui/robustness/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/robustness):
  a fatal error and a compiler crash after a buffered diagnostic. The crash fixture sets
  `RUSTFLAGS=-Ztreat-err-as-bug=2`, `RUST_BACKTRACE=0`, and `RUSTC_ICE=0`, and names the compiler
  and driver versions, so a toolchain bump or a version change re-blesses it.

## Source

- [`src/run.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/run.rs):
  the entrypoint, in the order this document gives.
- [`src/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/args.rs):
  `expand_arg_files` and `rustc_args`.
- [`src/config/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/config):
  the injected flags and the names the recognition anchors to, each with its rationale.
- [`src/callbacks.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/callbacks.rs):
  the two hooks.
- [`src/lib.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/lib.rs):
  the feature gate and the `extern crate` lines.
- [`src/emitter/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter):
  `install.rs` and `cgp_emitter.rs` for the wrapper and its orchestration, `stage/` and `pipeline/`
  for the stages, `flush/` for the rendering, `containment.rs`, `fallback.rs`, and `output.rs` for
  panics, `repeats.rs` for repeated errors, and `edit/` for the `DiagInner` edits, with the rustc
  phrasings they key on in the rustc-free
  [`signals`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs)
  module.
