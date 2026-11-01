# The driver

`cargo-cgp-driver` is the `rustc` replacement cargo runs for each workspace crate: it executes the
real compiler in-process through `rustc_driver`, and on that foothold it applies the transformations
that make CGP errors readable and renders them like vanilla `rustc`. This document is the deep dive
into how the driver is built (how it prepares the compiler's arguments, how it links the compiler's
internal API, and the transformations it applies to the diagnostics) for an agent reviewing,
debugging, or extending it.

The driver is one half of a two-executable design, and this document assumes the shape of the other
half. The front-end that invokes it, the reason the tool is split in two, and the environment
contract between them are in [Executable structure](executable-structure.md), and the flow the
driver's transformations sit within is in [Architecture](architecture.md).

## How cargo invokes the driver

Cargo runs the driver the way `RUSTC_WORKSPACE_WRAPPER` prescribes: the wrapper name, then the real
compiler path, then the rustc arguments:

```text
cargo-cgp-driver  /path/to/rustc  --edition=2024  --crate-name foo  src/lib.rs  ...
```

The driver runs the compiler in-process rather than shelling out, which is the whole reason it
exists: only in-process, through `rustc_driver`, can it install the callbacks and emitter that read
and rewrite diagnostics. The entrypoint is
[`run::run`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/run.rs),
called by the thin
[`bin/cargo-cgp-driver.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/bin/cargo-cgp-driver.rs)
wrapper; it reads the sysroot from the environment, prepares the argument vector, and runs the
compiler.

A *direct* (non-wrapper) invocation is handled before any of that: `--help`/`-h` or no arguments
prints the driver's help
([`help`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/help.rs))
and `--version`/`-V` prints its version handshake
([`version`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/version.rs)),
then the driver exits. These are gated on *not* being in wrapper mode, because in wrapper mode the
same flags belong to the real compiler cargo is probing, so cargo's `rustc --version`/`--help` still
reach the compiler untouched.

## Preparing the argument vector

The driver reads its arguments with rustc's own `rustc_driver::args::raw_args`, which reports an
argument that is not valid Unicode as a fatal error where `std::env::args` would panic. It reads
them before installing its panic hooks, because rustc's ICE hook reads `env::args` itself when
`RUST_BACKTRACE` is unset and would panic on such an argument, as plain `rustc` does. The checks for
a direct invocation's `--help` and `--version` run on a lossy copy, in which such an argument
matches no flag.

Before reading its own flags, the driver expands `@file` arguments
([`args::expand_arg_files`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/args.rs),
over rustc's own `rustc_driver::args::arg_expand_all`). When a command line grows long, cargo keeps
the wrapper and the `rustc` path visible and moves the rest into such a file, one argument per line,
so the driver's own `--cgp-expand=` flag and a user's explicit `-Znext-solver`, `--verbose`, or
`--sysroot` may sit inside it. Expanding first lets the driver find them; rustc then receives the
arguments already expanded. The expansion runs inside `catch_with_exit_code`, so an unreadable file
ends the compilation with the fatal error rustc itself would report.

Then
[`args::rustc_args`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/args.rs)
turns the wrapper's argument vector into a rustc one. It detects "wrapper mode" (the second argument
is a path whose file stem is `rustc`) and removes that injected compiler path, because
`rustc_driver::compiler_entrypoint` treats the vector's first element as the ignored program name
and everything after it as flags; leaving the `rustc` path in would make the compiler treat it as an
input file.

It then injects flags, each only when the invocation does not already set it. `--sysroot` is
injected with the value the front-end passes through `CARGO_CGP_SYSROOT`, because a `rustc_driver`
binary outside a toolchain cannot locate `std` on its own. The
[environment contract](executable-structure.md#the-environment-contract) covers both sides of that
hand-off. The two diagnostic flags `-Znext-solver=globally` and `--verbose` are injected next; they
drive the [trait-solver](#choosing-the-trait-solver) and [un-eliding](#un-eliding-the-diagnostic)
transformations below.

Injection is skipped entirely for cargo's info queries, `rustc -vV` and `--print`, which carry no
code to diagnose. `--verbose` would actively break `-vV`, since that already implies `-v` and a
second one makes rustc reject the invocation. Because each flag is injected only when absent, an
explicit choice on the command line always wins: a user's own `--sysroot`, or an explicit
`-Znext-solver=no`, is left in place. Absence is checked in every spelling rustc accepts: `key` and
`key=value`, a `-Z` option written as two arguments (`-Z next-solver=no`), and `-v` for `--verbose`
(beside which a second `--verbose` would make rustc reject the invocation).

## Running the compiler

The prepared vector runs under
[`rustc_driver::catch_with_exit_code`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/run.rs),
which executes the compiler and converts a compiler-signalled failure into the process `ExitCode`,
matching what plain `rustc` returns. The compiler behavior the driver adds is installed through
[`callbacks::CgpCallbacks`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/callbacks.rs),
which implements two hooks. Its `config` hook installs the diagnostic-rewriting emitter, and turns on the session's `trimmed_def_paths` option as rustc's own driver does, so the compiler
prints a type by its short name wherever that name is unique and not glob-imported
(`Option<String>`, not `std::option::Option<std::string::String>`). A compiler run through
`rustc_driver` leaves the option off unless its callbacks set it, and without it every diagnostic
the tool leaves alone would print paths plain rustc shortens, suggestions included. Its
`after_expansion` hook, which the compiler calls once name resolution is over, has a job in each of
the driver's modes. In a check it hands the emitter the `TyCtxt` it needs to reshape the
name-resolution errors of the crate's wiring entries (see
[Reshaping an unresolved wiring name](diagnostic-reshapes.md#reshaping-an-unresolved-wiring-name)), to replace the help
on a misspelled `#[use_type]` import (see
[Replacing the help on a misspelled `#[use_type]` import](diagnostic-reshapes.md#replacing-the-help-on-a-misspelled-use_type-import)),
and to drop the suggestions that name an identifier a macro generated (see
[Dropping a suggestion that names a generated identifier](diagnostic-reshapes.md#dropping-a-suggestion-that-names-a-generated-identifier)). When
`cargo cgp expand` asked for an expansion, it prints the expanded crate and stops the compilation
there instead of checking it (see [The expand command](expand-command.md)). Aside from the injected
flags, that emitter, and that second mode, the driver compiles exactly as `rustc` would.

## Accessing the Rust compiler API

The driver reaches the compiler through the `rustc_private` feature, which permits linking the
compiler's internal crates from the sysroot. Three facts about that access shape the crate.

First, the internal crates are pulled in by `extern crate`, not through Cargo. The library
[`lib.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/lib.rs)
carries `#![feature(rustc_private)]` and one `extern crate rustc_*;` line per compiler crate it
uses: `rustc_driver` to run the compiler; `rustc_interface`, `rustc_errors`, `rustc_middle`,
`rustc_session`, `rustc_span`, `rustc_data_structures`, and `rustc_lint_defs` for the emitter and
its queries; `rustc_hir`, `rustc_infer`, and `rustc_trait_selection` for the resolver; and
`rustc_ast` and `rustc_ast_pretty` for expand mode. A module needing a further crate adds another
line there; the compiler crates are never declared under `[dependencies]`. The crate's two ordinary
Cargo dependencies are the rustc-free libraries: `cargo-cgp-error-processing`, which holds the
message-rewrite logic and the `ComponentNameMap` the driver fills in from the compiler, and
`cargo-cgp-expand`, which resugars an expansion.

Second, the feature gate is needed on **both** the library and the binary crate. The binary
[`bin/cargo-cgp-driver.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/bin/cargo-cgp-driver.rs)
repeats `#![feature(rustc_private)]`, because the binary ultimately links the compiler
dylib, and that link is only permitted when the linking crate opts into the feature.

Third, the API is unstable and only ships with a nightly toolchain carrying the `rustc-dev`
component, so the toolchain is pinned in
[`rust-toolchain.toml`](https://github.com/contextgeneric/cargo-cgp/blob/main/rust-toolchain.toml)
to an exact dated nightly and bumped deliberately. The pinned nightly is the compiler the driver
*embeds*, so when `cargo cgp check` runs against a project, that nightly does the checking, and the
sysroot the front-end discovers must belong to the same nightly: a mismatched sysroot would load the
wrong `librustc_driver`. In practice the tool runs under the pinned toolchain. Because the API moves
between nightlies, every use of it is verified against the read-only compiler checkout at
[`../external/rust`](../../../external/rust) before being relied on.

## The driver's diagnostic transformations

The driver changes diagnostics in two ways. Two **argument levers**, below, change how the compiler
produces diagnostics and need no parsing. Everything else runs in a **custom emitter**, which acts on
diagnostics the compiler has already built, using facts only the live compiler holds.

The emitter tries its stages in order on each diagnostic, as
[Architecture](architecture.md#the-flow-of-a-diagnostic) describes, and
[Diagnostic reshapes](diagnostic-reshapes.md) covers what each stage does to its error class. A
diagnostic no stage claims goes to the [typed resolver](typed-root-cause-resolution.md), then to the
[text rewrite](diagnostic-reshapes.md#naming-the-traits-behind-a-component-marker) when the resolver
declines. The [post-processing](error-processing.md) transforms then clean up every rewritten
diagnostic, and change an untransformed one only where they recover a CGP encoding, so a plain Rust
error stays as rustc printed it (the injected `--verbose` aside).

The emitter also renders the diagnostics, the way plain `rustc` would. The wrapper type
[`CgpEmitter`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/cgp_emitter.rs) is generic over an
inner emitter, and [`install`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/install.rs) rebuilds
the emitter the compiler's own `default_emitter` would build for the active error format (a
`JsonEmitter` for `--message-format=json`, an `AnnotateSnippetEmitter` for the human format) and wraps
it. The session's own emitter cannot be wrapped directly, because `DiagCtxt::set_emitter` replaces it
with no way to recover the original. `install` therefore reads the session options in the `config`
hook and builds the emitter from inside `psess_created`. The wrapper forwards every emitter method
unchanged except `emit_diagnostic`, which transforms first. It edits the compiler's `DiagInner` in
place, so the change reaches a JSON diagnostic's structured `children` and its regenerated `rendered`
field, and a human diagnostic's text, alike.

### Choosing the trait solver

The driver injects `-Znext-solver=globally` into every workspace-crate compilation
([`config::NEXT_SOLVER_FLAG`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/config/rustc_flags.rs),
applied in
[`args::rustc_args`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/args.rs)),
turning on the next-generation trait solver. This is an argument-lever transformation, and it
targets the class of CGP error whose root cause the *default* solver hides.

When a provider's impl-side dependency is unmet (say a `name` field the context does not carry), and
the failure is reached by calling the consumer method directly, what the default solver reports
depends on the compiler. On stable Rust its method-resolution path bottoms out at the provider
trait (`Person: Greeter<Person>`) and never reports the real missing leaf bound. The pinned nightly
does name the leaf in a note, as `Person: HasField<Symbol<4, Chars<..>>>`, but with the field name
elided and the note buried under method-probe advice (the fixture's `.rust.stderr` records this).

The next-generation solver reaches the leaf on every compiler the tool supports. Under
`-Znext-solver=globally` the same mistake names the concrete `Person: HasField<Symbol!("name")>`
bound. (CGP's traits carry no `#[diagnostic::on_unimplemented]` hints, so cargo-cgp's own messages
are the only CGP wording.) So merely compiling the workspace crate under the new solver un-hides the
cause, with no diagnostic parsing required. The flag is scoped to workspace crates (only they go
through the driver), so dependencies still build with the default solver. The before/after is pinned
by the
[`hidden/unsatisfied-dependency/unsatisfied_dependency`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unsatisfied_dependency.cgp.stderr)
UI snapshot, a fixture of `acceptable` quality because this solver switch, with the typed resolver
on top, turns its buried cause into a clean, root-cause-first error.

Two things follow from changing the solver. The new solver is not perfectly compatible with the old
one (see
[Significant changes and quirks](https://rustc-dev-guide.rust-lang.org/solve/significant-changes.html)),
so in principle a crate could compile under a plain `cargo check` yet report a spurious error under
`cargo cgp check`, or the reverse; this is the accepted cost of using the new solver as the
diagnostic engine, and an explicit `-Znext-solver` on the command line still overrides the
injection. The reverse case is not merely hypothetical: two namespaces that inherit from each other
are rejected by stable `rustc` with an `E0275` overflow but **compile clean** under
`cargo cgp check`, because the next-gen solver does not eagerly overflow on the mutually-recursive
inheritance impls. On the pinned nightly the default solver accepts them too, so the fixture that
pins the case,
[`wiring/namespace-inheritance-cycle/namespace_inheritance_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-inheritance-cycle/namespace_inheritance_cycle.rs),
has two empty snapshots. It is a *missing* error, not a suppressed root cause. Separately, the
richer cross-crate diagnostics name absolute paths (the `cgp` checkout) and can point at a
hash-named temp file for an elided long type, volatile details the UI-test harness normalizes away,
described in [Testing](testing.md).

### Un-eliding the diagnostic

The driver injects the stable `--verbose` flag into every workspace-crate compilation
([`config::VERBOSE_FLAG`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/config/rustc_flags.rs),
applied in
[`args::rustc_args`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/args.rs)).
This is the second argument-lever transformation, and it targets a different failure from the solver
switch: not a cause the compiler never computes, but a cause the compiler computes and then *elides
while printing*.

rustc compresses long or repetitive types in its diagnostics, and every one of those compressions is
destructive to a CGP error, whose types are deep `Symbol` / `Cons` lists. When it reports "trait `X`
is not implemented … but trait `Y` is" it diffs the two traits and replaces every generic argument
they share with `_`; when a type's printed form grows long it truncates it and writes the full form
to a `long-type-*.txt` file; when more than nine impls could apply it collapses the rest to "and N
others". All three are gated on the compiler's `opts.verbose` flag, which `--verbose` sets, so the
one flag turns all three off and the full type is always present in the output. Crucially
`--verbose` is *not* `-Zverbose-internals`: it un-elides without switching on the compiler's
internal debug printing (disambiguator suffixes, region ids), so the diagnostics keep their ordinary
shape. The emitter undoes the third: a failed bound's help listing the trait's implementors is cut
back to rustc's eight and "and N others" (`bound_candidate_list`), because a CGP crate implements
`IsProviderFor` hundreds of times and the full list buries the diagnostic it belongs to.
[`many_implementors`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/many_implementors.rs)
pins that a plain Rust bound's list then matches plain `cargo check`.
The full mechanism (which function performs each elision, and the two-verbosity-switch distinction
that makes `--verbose` the surgical choice) is documented in
[rustc diagnostic internals](rustc-diagnostic-internals.md#the-suppression-points).

The worked case is a missing field surfaced through the two-line similar-impl hint. Asking for a
`height` field on a `Rectangle` that has only `width`, rustc diffs `HasField<Symbol!("height")>`
against `HasField<Symbol!("width")>`; because the two symbols share the character `'h'`, the shared
`'h'` is collapsed to `_` in *both* names, printing `h,e,i,g,_,t` and `w,i,d,t,_`, and the field
name cannot be read back from the text at all. Under `--verbose` both symbols print in full. The
before/after is pinned by the
[`checks/check-trait-failure/fields/base_area_1`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_1.cgp.stderr)
UI snapshot, a fixture of `acceptable` quality because the flag, with the typed resolver on top,
turns its otherwise hidden cause into a clean, root-cause-first error, as the solver switch does for
`unsatisfied_dependency`.

**The flag reaches every diagnostic in the compilation, so a diagnostic the tool leaves alone also
prints un-elided.** rustc reads `opts.verbose` from the session options, which are fixed once the
session is built, so the driver cannot turn the flag off for one diagnostic. In the
[`provider_wrong_signature`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/provider_wrong_signature.rs)
fixture, a `#[cgp_impl]` provider method takes a `u64` where its component declares a `u32`, and
the `E0053` note reads `` expected signature `fn(&__Context__, u32) -> String` ``, naming the
context parameter `#[cgp_impl]` generates. Plain rustc diffs the two signatures and prints
`fn(&_, u32) -> String`. A crate's own types differ the same way: in
[`lookalike_cgp_names`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/lookalike_cgp_names.rs),
a program that never names CGP, `Symbol<1, Chars<'a', Nil>>` prints in full where rustc shows
`Symbol<1, Chars<..>>`.

This is a known limitation, kept because both alternatives cost more. Without the flag, the
CGP diagnostics the resolver declines lose their field names: a `Symbol!("nmae")` reads
`Symbol<4, Chars<'n', Chars<'m', _>>>`, and rustc's similar-impl hint replaces the help naming the
missing field. Re-eliding the text afterward cannot work either, because rustc prints `_` only for
the arguments the two compared types share, and the text does not record which those were. Plain
`cargo check` still shows any diagnostic in rustc's own wording.

## De-duplicating and coalescing

One mistake surfaces at many sites because CGP wiring is lazy, so the emitter removes repeats in two
steps: de-duplication on arrival, and coalescing at the flush.

A missing dependency is reported at the `check_components!` entry, again at every hand-written `impl`
that references the broken consumer, and again at each call. The emitter records each transformed diagnostic in a
[`DedupLedger`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/dedup.rs)
(the rustc-free ledger that owns the key scheme, so it is unit-tested without a compiler) and
suppresses any later diagnostic whose **span-independent signature** the ledger has seen. A resolved
diagnostic is keyed by its recovered cause (the context, the failing consumer trait(s), and each
root-cause leaf, via the rustc-free `cause_signature`), so the *same* consumer's failure re-reported
at several spans collapses to one, while two *distinct* consumers that happen to share a cause keep
separate signatures, so each survives de-duplication (no trait's failure is ever hidden) to be
*coalesced* at flush, described next. A diagnostic the resolver declined but the text rewrite still
transformed is keyed by its rendered message text instead (`message_signature`), so the fallback
re-reports coalesce too. A third key is the **coded class headline**: a failure the resolver
declined but still rewrote (falling back to raw `IsProviderFor` scaffolding) carries the *same*
`[CGP-Exxx]` class sentence the resolved tree of the same failure is classed under, so keying on it
collapses that declined fallback into the resolved occurrence even though their bodies differ. A
resolved report records its class headline (the plan's `class_header`), not the cause its displayed
headline states, since the text rewrite of a declined report words only the class; when rustc's own
headline is an `IsProviderFor` bound, it also records the provider form the text rewrite gives that
headline (`declined_header`), since a declined re-report carries that form instead. The header key
works in that one direction only: a resolved report records it but never consults it, so a declined
fallback that arrived first never hides the resolved tree after it, and two resolved reports of one
consumer with different causes are both kept for the flush to coalesce. The ledger keys only the
tool's own transformed diagnostics. An untouched `rustc` error is merged only when rustc reports it
twice: at the flush, in a crate that uses CGP, a later diagnostic with the same level, code, and
message as an earlier one, and a primary caret on the same line, is merged into the earlier block
([`merge_repeats`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/repeats.rs)),
whose notes are the fuller. rustc repeats an error that way when it checks one requirement for each
item a macro generated (the repeat renames or drops a note;
[`implicit_conflicting_types`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/implicit-arguments/implicit_conflicting_types.rs))
or a call's bound for the call and an argument (the repeat has its own caret;
[`transform_map_fields_missing_marker`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/transform_map_fields_missing_marker.rs),
whose first block already covers the call). A caret the earlier block does not already cover is
kept, labelled "also required here", so no location is lost. A crate without CGP keeps both blocks
([`repeated_bound_without_cgp`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/repeated_bound_without_cgp.rs)),
and the driver's unit tests pin each condition of the merge.
The count stays honest because cargo re-counts the diagnostics the emitter actually produces (a
suppressed re-report drops out of its "N errors" summary as well), so the visible block count and
the summary agree. This is the [one-mistake-many-errors](../issues/usability.md) usability class the
per-diagnostic resolver could not address on its own.

De-duplication collapses the *same* consumer's re-reports; a second gate, **coalescing**, collapses
*different* failures that share one root cause into a single block. One missing field can break
several endpoints, a chain of dependent components fails top to bottom for the one field the
innermost provider needs, and a hand-written wrapper trait fails beside the check of the consumer it
reduces to. Stating the shared cause once, pointing at every site, is only possible once they have
all arrived, and the `Emitter` trait has no end-of-compilation hook, so the emitter does not emit as
it goes: it **holds every diagnostic in an arrival-ordered buffer** and flushes it from its `Drop`.
`Drop` runs during the `DiagCtxt`'s own teardown, after every diagnostic has been handed to the
emitter but while the inner emitter (a field of the wrapper, dropped only afterward) is still alive
to render; the diagnostics were counted by the `DiagCtxt` as they arrived, so deferring their
*rendering* to `Drop` leaves the error count untouched. At flush, each buffered failure whose
headline gives way to its cause (`DiagnosisPlan::coalesces`: a rewritten headline that is not a type
mismatch, whether on a consumer, a wrapper, or a foreign subject) is grouped with every failure it
**shares a root cause** with, by the rustc-free `group_by_shared_cause`. It keys each cause on its
`Leaf` structurally rather than on the `root cause:` lead that leaf words, so grouping does not
shift when a lead is reworded. A leaf names its owner, so failures on different contexts that bottom
out on one owner's mistake group too; an ordinary trait bound names no owner and is keyed with the
context it was reached from. Grouping on a shared cause rather than on one whole-failure key keeps a single mistake in a single block, because the depths one mistake surfaces at each see a
different *subset* of its causes: a `check_components!` entry stops at the first unmet leaf on its
own branch, while a use-site call walks every wired component and reaches them all. Those subsets
overlap without ever being equal, so an exact-match key would group none of them. The block whose
causes were the *union* of the others would fare worst, since every one of its roots would already
be drawn and its chain would then be
[fully elided](dependency-graph-rendering.md#eliding-across-blocks) into a bare `root causes:` list
with no chain at all. The relation is made transitive so it is a partition rather than an ambiguous
overlap graph, which also earns an invariant the exact key could not: **no two coalesced blocks
share a root cause**. A group of one emits its own per-entry block unchanged; a group of several
emits **one merged block**, its members ordered by source position: a headline stating the shared
cause (`coalesced_headline`, which takes the first member's class code, and falls back to every
member's class sentence with the cause count when the causes are mixed), the first failing entry as
its one primary caret and every other entry as a secondary span labelled "also required here"
(`merged_span`), one root-cause note built by folding every member's paths into a single
[dependency graph](dependency-graph-rendering.md), and after it the fix `help`s the causes call for.
Because the members were grouped for *sharing* a cause, the union of their causes holds one copy of
it per member, so the block folds those copies back into one through the rustc-free `Causes::union`
before wording anything. Otherwise the same mistake would be stated once per member, most visibly as
an underived field listed once per consumer that reads it. The graph does the merging: when one
failing consumer transitively depends on another (`CanCalculateDensity` needs `CanCalculateArea`, so
its chain *contains* the other's), the contained consumer is not a top-level root and the block
leads with the subsuming chain; a wrapper's chain runs through the consumer it reduces to in the
same way; when two consumers are independent but share the cause, both chains render, converging at
the shared node. An untouched `rustc` error, a conflict, or an orphan reshape is buffered as a plain
entry and emitted verbatim at its arrival position, so global ordering (a CGP block beside an
unrelated `E0308`, say) is preserved.

The flush is also where every resolution's `root cause:` note is *rendered*, not merely where the
coalesced ones are merged, which lets the notes elide against one another. Each note goes
ahead of its block's fix `help`s, so a fix follows the cause it repairs. A resolution that does not
coalesce still buffers its causes rather than its note (a type mismatch, or a kept rustc headline
over an ordinary bound), because only at flush is the emission order known, and one
[dependency graph](dependency-graph-rendering.md#eliding-across-blocks) `seen` set threaded through
the blocks in that order lets a later one `(*)`-truncate at the subtree an earlier one already drew,
while still ending at the root cause, since the block it points into is one the reader may not have
to hand. The redundancy this removes is large in real code: CGP wiring is lazy, so one mistake
reaches several diagnostics that legitimately do *not* de-duplicate, and their chains can share
everything below their own first few hops. A block whose whole chain was already drawn is rendered
against a fresh set instead, keeping a chain of its own rather than heading a lone `(*)`: with no
distinct prefix to hang a shared tail under, eliding would remove the entire derivation. Either way
the block stays actionable alone: its header, its fix `help`, and its `root cause:` lead all still
name the cause, so only chain *detail* is ever elided. The
[`density_3`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/density_3.rs)
(two components, one missing field),
[`dependency_cascade`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/dependency_cascade.rs)
(three chained providers), and
[`missing_normal_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/missing_normal_bound.rs)
(two consumers sharing an `App: Clone` bound) fixtures pin the merged blocks where one consumer's
chain *subsumes* another's, so the deepest leads;
[`parallel_consumers`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/parallel_consumers.rs)
pins the complementary shape (two *independent* consumers reaching one cause by equal-depth chains
that neither subsumes), where the representative is the first check entry deterministically.

## Containing the driver's own panics

**A panic in the driver's own code never costs the user their diagnostics.** The emitter re-runs
compiler code from inside `emit_diagnostic` and renders every buffered diagnostic from its `Drop`,
so a bug in either would otherwise stop the compilation with nothing printed, or abort the process
outright, since the flush runs while the thread unwinds from rustc's fatal-error abort, as every
failing compilation does. So the emitter runs both under `catch_unwind`
([`containment`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/containment.rs)):

- **A panic in a transform** buffers that diagnostic as rustc built it, with a note saying the
  transform failed, naming the panic, and giving the issue tracker, and the compilation goes on to
  the next diagnostic.
- **A panic in the flush** emits every buffered diagnostic as rustc built it, each resolution with
  the same note, in arrival order.

A `FatalErrorMarker` unwind is rustc aborting on a fatal error rather than a panic of the
driver's, so containment lets it continue.

**A crash elsewhere in the compiler keeps rustc's output order.** Plain rustc prints each error as
it arrives, so an internal compiler error's report follows the errors before it. The emitter holds
its diagnostics until the flush, which would put them after the report. The driver therefore sets
up its panic hooks before the compiler runs, as rustc's own driver does. It installs rustc's ICE
hook with cargo-cgp's issue tracker as the bug-report URL and the driver version as an extra note.
It then wraps that hook: a panic the emitter is containing is recorded for the note and printed
nowhere, and any other panic first has the emitter emit its buffer, untransformed, and then hands
over to the ICE hook. The buffer and the inner emitter sit behind a lock the hook can reach
([`output`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/output.rs)).
They go out untransformed because a second panic inside a panic hook aborts the process, so a crash
is no time to run the flush's rendering. The driver also initializes rustc's `RUSTC_LOG` logger,
as rustc and Clippy do.

**No input is known to make the emitter panic**, so the fallback is tested through its own functions
rather than through a compilation. The emitter runs its transform and its flush through
[`transform_or_original` and `render_or_untransformed`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/fallback.rs),
which take the step as a closure, and the driver's unit tests pass a closure that panics. The
shipped driver therefore carries no switch that makes it panic. The ICE ordering has a fixture of
its own, in
[`robustness/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/robustness), which
crashes the compiler rather than the emitter: `RUSTFLAGS=-Ztreat-err-as-bug=2` turns the second
error into an internal compiler error. An ICE report also carries a backtrace, a timestamped
crash-report file, and the panicking thread's id, so the fixture sets `RUST_BACKTRACE=0` and
`RUSTC_ICE=0` (no file), and the harness replaces the thread id. The report still names the compiler
and driver versions, so a toolchain bump or a version change re-blesses it.

## Comparison with Clippy

The driver follows `clippy-driver` closely in its skeleton: both detect wrapper mode by testing
whether the second argument's file stem is `rustc` and drop it, both inject `--sysroot` only when
one is absent, and both run the compiler with `rustc_driver::compiler_entrypoint` inside
`catch_with_exit_code`. Reading
[`external/rust/src/tools/clippy/src/driver.rs`](../../../external/rust/src/tools/clippy/src/driver.rs) alongside this
crate, the correspondence maps function for function.

The transformations diverge where the purpose does. Clippy's `config` callback calls
`register_lints` to add lint passes that emit *new* diagnostics; `cargo-cgp`'s `config` callback
installs a diagnostic *emitter* that *rewrites* the compiler's existing notes. That is the same
`Callbacks` lever put to the opposite end (adding versus clarifying), and it is why the driver reads
the `TyCtxt` from a custom emitter where Clippy reads it from a lint pass. The `--sysroot` handling
also diverges structurally, because `cargo-cgp-driver` is out-of-tree while `clippy-driver` ships
inside the toolchain; that difference belongs to the shared environment contract and is covered in
[Executable structure](executable-structure.md#comparison-with-clippy).

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
  same hook the driver uses. The guide shows a `Translate`-based emitter API the pinned nightly lacks.
- [Tracking issue for crates that are compiler dependencies (#27812), rust-lang/rust](https://github.com/rust-lang/rust/issues/27812),
  is the `rustc_private` feature's tracking issue, the background for why linking the compiler
  crates needs a nightly toolchain with the `rustc-dev` component.
- [Next-gen trait solving, in the Rust Compiler Development Guide](https://rustc-dev-guide.rust-lang.org/solve/trait-solving.html),
  explains what `-Znext-solver` selects and how it evaluates goals.

## Tests

- [`crates/cargo-cgp-driver/tests/driver/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/args.rs):
  `rustc_args` wrapper-mode stripping, sysroot injection, an existing sysroot left alone,
  injected-flag appending, an explicit `-Znext-solver` override in either spelling, `-v` counted as
  `--verbose`, and the `-vV`/`--print` info-query skips; and `expand_arg_files` expanding an
  argument file that holds `--cgp-expand=` and a user's `-Znext-solver`.
- [`crates/cargo-cgp-driver/tests/driver/run.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/run.rs):
  runs the built driver with a non-Unicode argument and `RUST_BACKTRACE` unset, pinning that it
  exits with rustc's error rather than a panic.
- [`crates/cargo-cgp-driver/tests/driver/help.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/help.rs):
  `wants_help` detecting the help flags, and the help text explaining the wrapper role and flags.
- [`crates/cargo-cgp-driver/tests/driver/containment.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/containment.rs):
  `contain` returning a value, naming a contained panic's message and location, reading a formatted
  (`String`) and a non-string payload, letting a `FatalErrorMarker` unwind on, and restoring the
  outer state after a nested call; and the two
  fallbacks with a panicking step: a transform's panic giving back rustc's diagnostic with the
  internal-error note, and a flush's panic emitting every entry untransformed, in order.
- [`crates/cargo-cgp-driver/tests/driver/footers.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/footers.rs):
  `rebuild_explain_footers` over hand-built diagnostic lists: a footer whose codes all survive left
  as it is, a code whose errors were all dropped leaving the list, one surviving code keeping only
  the pointer line, no surviving code dropping both lines, and a footer line naming no readable
  code left as written.
- [`crates/cargo-cgp-driver/tests/driver/pipeline.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/pipeline.rs):
  `apply_reshape` over hand-built diagnostics: the plan's header, notes, and then helps replacing
  rustc's message, notes, and suggestions, and each span policy (rustc's spans kept, the primary
  span alone, its call site, and the two definitions relabelled); and the verdict chain, where a
  stage that drops or reshapes a diagnostic ends it.
- [`crates/cargo-cgp-driver/tests/driver/repeats.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/repeats.rs):
  `merge_repeats` over hand-built diagnostics: a repeat at another caret on the line merged and
  labelled, one the first block covers adding no label, and the same error kept on another line or
  in another file, with another code, message, or level, without a code, or with an inline message.
- [`crates/cargo-cgp-driver/tests/driver/flush.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/flush.rs):
  the flush over hand-built buffers: only coalescible resolutions group, a group is one block at its
  first member's position with its caret on the site written first, a merged block states the cause
  once, names every consumer, and drops rustc's children and suggestions, a later block elides a
  subtree an earlier one drew, a note goes ahead of the first `help`, and the shared-dispatch pairing
  leaves a diagnostic without its helper to the next stage.
- [`crates/cargo-cgp-driver/tests/driver/postprocess.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/postprocess.rs):
  a span label the post-processing rewrites, with the span's primary span and context span kept.
- [`crates/cargo-cgp-error-processing/tests/error_processing/internal_error.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/internal_error.rs):
  the note on a diagnostic shown untransformed after a contained panic.
- [`tests/ui/pass-through/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/pass-through):
  `consumer_not_in_scope`, `headline_std_path`, and
  `suggestion_full_paths` pin the trimmed paths: each diagnostic the tool leaves alone, suggestions
  included, matches plain `cargo check` exactly. `repeated_bound_without_cgp` pins that a crate
  without CGP keeps a repeated error, and `respanned_token_suggestion` and
  `function_macro_suggestion` that a suggestion at a token an attribute macro re-spanned, or at the
  end of a function-like macro's call, stays. `same_name_types`, `compute_bare_name_ambiguous`,
  `raise_error_ambiguous`, and `update_field_marker_unannotated` pin that the post-processing keeps
  the paths, labels, and context spans of an untransformed diagnostic, and `lookalike_cgp_names`
  that a crate not using CGP is never resugared. `provider_wrong_signature` and
  `lookalike_cgp_names` pin the `--verbose` limitation, marked `//@rewrites-falsely:`.
- [`tests/ui/robustness/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/robustness):
  `fatal_after_buffered_diagnostic` pins a fatal error that stops the compilation early: a rewritten
  wiring failure, held in the buffer, then a fatal query cycle (`E0391`); both print, in rustc's
  order. `ice_after_buffered_diagnostic` pins a compiler crash (`-Ztreat-err-as-bug=2`) after a
  buffered wiring failure: the panic hook prints the failure, untransformed, before the crash
  report, as plain rustc orders them.
- [`crates/cargo-cgp-error-processing/tests/error_processing/postprocess/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/postprocess):
  the compiler-free post-processing transforms the emitter applies as its final pass: prefix
  stripping, the `Symbol!` and `Path!` resugaring, and the missing-field reword branches.
- [`tests/ui/hidden/unsatisfied-dependency/unsatisfied_dependency.cgp.stderr`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unsatisfied_dependency.cgp.stderr):
  pins the un-hidden output the solver switch produces.
- [`tests/ui/checks/check-trait-failure/fields/base_area_1.cgp.stderr`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_1.cgp.stderr):
  pins the un-elided field name (`--verbose`) and the trait-named header and wiring notes; watch for
  a `_` returning inside its `Symbol`, or a marker-based header/note returning.

## Source

- [`crates/cargo-cgp-driver/src/run.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/run.rs):
  the entrypoint: installs the logger and the panic hooks, reads the sysroot, prepares the argument
  vector, and runs the compiler under `catch_with_exit_code`.
- [`crates/cargo-cgp-driver/src/args.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/args.rs):
  `expand_arg_files`, the `@file` expansion, and `rustc_args`: wrapper-mode stripping, sysroot
  injection, flag injection, and the info-query skip.
- [`crates/cargo-cgp-driver/src/config/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/config):
  the shared names, one module per subject: the injected flags (`NEXT_SOLVER_FLAG`, `VERBOSE_FLAG`
  in `rustc_flags.rs`, `SYSROOT_ENV` in `front_end.rs`) and the identity anchor
  (`CGP_COMPONENT_CRATE`, `IS_PROVIDER_FOR_TRAIT` in `cgp_component.rs`), each with its rationale.
- [`crates/cargo-cgp-driver/src/callbacks.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/callbacks.rs):
  the `Callbacks` implementation: its `config` hook installs the transforming emitter, and its
  `after_expansion` hook runs the name-resolution reshape, the `#[use_type]` help replacement, and
  the generated-name suggestion drop in a check and serves expand mode
  ([The expand command](expand-command.md)).
- [`crates/cargo-cgp-driver/src/emitter/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter):
  the generic `CgpEmitter<E>`, split behind a re-exporting `mod.rs`: `install.rs` rebuilds the
  compiler's default emitter for the active format (a `JsonEmitter` or an `AnnotateSnippetEmitter`)
  and wraps it, `cgp_emitter.rs` holds the `CgpEmitter<E>` type (holding the `ComponentNameMap`, the
  rustc-free `DedupLedger` of already-emitted failures, the `cgp_spans` list of recognized-failure
  spans that anchors the `?`-operator cascade suppression, and the shared output whose
  arrival-ordered buffer of `BufEntry`s is flushed from `Drop`) and its
  transform/post-process/de-duplicate orchestration, `flush/` the rendering of that buffer (`Plain`
  entries verbatim in place, `Resolved` ones with their `root cause:` note rendered against the
  flush's shared `seen` set, the `coalescible` ones additionally partitioned by
  `group_by_shared_cause` and merged into one consumer header per group by `merged_diag`, after
  which `rebuild_explain_footers` makes the trailing `rustc --explain` footer name only the codes
  that survived), `pipeline/` the `Verdict` a stage returns, the `Reshape` that holds a reshaping
  stage's edits as data, and `apply_reshape`, which writes one into the diagnostic, `stage/` the
  stages, one module each, the typed resolver's `resolver.rs` last (among them
  `shared_dispatch_method.rs`, the pairing of the two `E0428`s two dispatch traits sharing a method
  name produce), `buffer.rs` the buffered entries and their untransformed fallback, `buffer_pass.rs`
  the shape the after-expansion passes share, `crate_facts.rs` the facts about the crate the
  post-processing reads (whether it uses CGP, and its ambiguous type names), `output.rs` the inner
  emitter, the buffer, and the recorded unprovable requirements, shared with the panic hook and the
  name-resolution reshape, `containment.rs` the `catch_unwind` wrapper and the panic hooks,
  `name_resolution.rs` the reshape of the wiring entries' name-resolution errors and the overflow
  drop that goes with it, `generated_names.rs` the drop of a suggestion that names a generated
  identifier, `use_type_misspelling.rs` the help on a misspelled `#[use_type]` import,
  `attribute_splice.rs` the drop of a suggestion spliced after an attribute macro, `repeats.rs` the
  flush's merge of a diagnostic rustc reports twice, `fallback.rs` the diagnostics emitted when the
  transform or the flush panics, and `edit/` holds the `DiagInner`-editing helpers, one module per
  subject: `spans.rs` the span edits (including `merged_span`, the merged block's one caret and its
  labelled other sites, and `two_definitions_span`, the relabelled carets of a generated name defined
  twice, for two check tables sharing a check-trait name or two dispatch traits sharing a method),
  `readers.rs` the message readers and predicates (including `message_signature`, the
  span-independent text key for de-duplicating a declined-but-rewritten diagnostic, and
  `is_question_mark_cascade`, the `Try`/`FromResidual`-shape recognizer for the cascade drop),
  `children.rs` the header, child, and suggestion edits (including `strip_method_probe_advice`, the
  drop of rustc's associated-function framing on a declined consumer-method `E0599`), and `text.rs`
  the rustc-free text transforms applied in place; the rustc phrasings `is_question_mark_cascade`
  and `strip_method_probe_advice` key on live in the rustc-free
  [`signals`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs)
  module.
- [`crates/cargo-cgp-driver/src/lib.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/lib.rs):
  the `rustc_private` feature gate and the `extern crate` declarations.
