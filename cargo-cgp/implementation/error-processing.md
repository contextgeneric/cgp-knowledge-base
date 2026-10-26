# Error processing

`cargo-cgp` turns a compiler's raw diagnostics into readable, root-cause-first CGP errors, and the
string-level logic that does the turning lives in one rustc-free crate,
[`cargo-cgp-error-processing`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing).
This document records what that crate holds, why it is kept apart from the driver, how the driver
drives it, and how it is tested.

The crate is **driven entirely by the driver**; the front-end never touches diagnostics. It exists
as a separate crate for one reason: it links no compiler internals, so it builds and its tests run
on any toolchain, without the driver's `rustc_private` linkage. The driver depends on it and calls
into it from its emitter; the crate never depends on the driver or the front-end. Keeping the logic
here is what lets a plain unit test exercise a transform over a hand-built string, with no compiler,
no cargo, and no `cargo-cgp` process in the loop.

## What the crate holds

The crate's tenants are listed below, all driven by the driver's emitter. Grouping them here, apart
from the driver, is what keeps them unit-testable.

- **Post-processing**
  ([`postprocess`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/postprocess))
  is the set of fallback text transforms the driver applies to a diagnostic's messages so raw CGP
  constructs do not look confusing. Each is a pure `&str -> Option<String>` (`Some` when it changed
  the text), and
  [`postprocess_message`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/chain.rs)
  chains them.
- **The shape spellings**
  ([`shape`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/shape))
  decide whether a field list has an exact `Struct!`/`Enum!` spelling and render it. They take names
  and already-rendered values, so the text resugaring and the driver's typed renderer both call them
  and cannot disagree; [Resugaring](resugaring.md#struct-and-enum-a-list-of-fields) holds the rules.
- **The wiring rewrite**
  ([`rewrite`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/rewrite))
  is the string transform that renames CGP wiring messages, over the
  [`ComponentNameMap`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/rewrite/names.rs)
  the driver fills in from the compiler. It also rewrites the `E0275` header of a wiring lookup that
  never resolves into its `[CGP-E020]` form for a cycle or its `[CGP-E021]` form for a lookup that
  grows, by the reason the driver's walk found. It is documented where it is used, in
  [The driver](driver.md#naming-the-traits-behind-a-component-marker).
- **The diagnosis model and its wording**
  ([`diagnosis`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis))
  is the rustc-free root-cause model (the `Resolved` failure the driver's typed resolver produces,
  in owned `String` form) and the wording that turns it into diagnostic text. Two pure cause-list
  transforms run ahead of the wording: `Causes::union` folds duplicate copies of one leaf into a
  single cause holding every path (what the emitter's coalesced block needs, since its members were
  grouped for sharing a cause), and `coalesce_underived_fields` then merges the *distinct* underived
  fields of one struct into the single derive fix they share. `plan_resolved` runs the latter and
  composes the rewritten header, the fix `help`s, and the `root cause:` note into a `DiagnosisPlan`,
  which the emitter only maps onto rustc's `DiagInner`. The note travels as an unrendered
  `PendingNote` (the causes and the header-stated leaf), because rendering it needs the emission
  order only the emitter's flush knows. Keeping one representation rather than a rendered string
  alongside is what stops the tests pinning one note while the emitter shows another, and keeping
  every piece rustc-free is what makes the whole diagnosis-to-text layer unit-testable without a
  `TyCtxt`. The same module holds the structured dependency-graph nodes and their rendering
  (`node.rs`) and the graph that merges and renders them (`graph.rs`), so every node template and
  the whole merge/render live here. It is documented in
  [Typed root-cause resolution](typed-root-cause-resolution.md) and
  [Dependency-graph rendering](dependency-graph-rendering.md). The module also holds the
  duplicate-key conflict wording (`wiring.rs`): the `WiringConflict` model and
  `plan_wiring_conflict`, which words the `[CGP-E010]`–`[CGP-E014]` headers (one per conflict shape)
  the driver's `resolve::conflict` classifier feeds it (see
  [The driver](driver.md#reshaping-a-duplicate-key-conflict)). Five more modules word the driver's
  other reshapes, each with a `plan_*` header and a `*_help` fix: `orphan.rs` (`OrphanConflict`, the
  `[CGP-E022]` orphan-rule namespace registration), `undeclared.rs` (`UndeclaredTrait`, the
  `[CGP-E030]` trait a `#[cgp_fn]`/`#[cgp_impl]` body calls without declaring it, with the
  `#[uses(…)]` bound written with the arguments the call uses), `unimported.rs`
  (`UnimportedAbstractType`, the `[CGP-E035]` abstract type used without `#[use_type]`),
  `requirement.rs` (`UndeclaredRequirement` and its `Requirement`s, the `[CGP-E036]` requirements a
  provider does not declare, with a `#[uses]` help and a `#[use_type]` help), and
  `cgp_impl_misuse.rs` (`CgpImplMisuse` for the `[CGP-E032]`–`[CGP-E034]` wrong-half mistakes,
  `ProviderTraitInUses` for the `[CGP-E037]` provider trait in `#[uses]`, and `MissingUseProvider`
  for the `[CGP-E031]` inner provider never imported, with a generic component's parameters),
  `macro_less_provider.rs` (`ProviderImplWithoutMacro`, the `[CGP-E039]` provider-trait impl
  written without `#[cgp_provider]`, with its help), and `wiring_name.rs` (`UnresolvedWiringName`, the `[CGP-E038]` and `[CGP-E040]`–`[CGP-E044]` wiring
  key, value, or provider that does not resolve, with a help only where a fix is known). They are
  documented where the driver detects them, in
  [The driver](driver.md#the-drivers-diagnostic-transformations). `structural.rs` holds
  `StructuralMistake`, the structural mistakes in a check table or a wiring entry the driver's
  `resolve::structural` detectors recover, and words their `[CGP-E015]`–`[CGP-E019]`, `[CGP-E060]`,
  and `[CGP-E061]` headers and fixes, with a note for the one header that does not say why the
  program fails. `dispatch_names.rs` mirrors the names `#[cgp_auto_dispatch]` gives a method's
  helper and computer, which the emitter pairs to recognize `[CGP-E061]`. `overflow.rs` holds
  `WiringOverflow`, the reason the driver's walk gives for a wiring lookup that never resolves (a
  cycle, or a lookup that grows, with the provider step that causes it when a wiring entry chose
  that provider), and words the reason that ends the `[CGP-E020]` or `[CGP-E021]` header and its
  `help` (`wiring_overflow_reason`, `wiring_overflow_help`). Last, `internal_error.rs` words the
  note on a diagnostic the driver shows untransformed after a panic in its own transform (see
  [The driver](driver.md#containing-the-drivers-own-panics)).
- **The dependency-tree renderer**
  ([`tree`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/tree.rs))
  is the `DependencyTree` type and its `cargo tree`-style renderer over the tiny `termtree` crate.
  It is the render target the [dependency graph](dependency-graph-rendering.md) expands into. The
  graph itself (in `diagnosis`) does the merging: the driver's resolver hands over one path of
  structured nodes per way a cause is reached, and the graph fuses the nodes several paths share
  into a DAG with `(*)`-marked shared subtrees. It is documented in
  [Typed root-cause resolution](typed-root-cause-resolution.md) and
  [Dependency-graph rendering](dependency-graph-rendering.md).
- **The de-duplication ledger**
  ([`dedup`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/dedup.rs))
  is the `DedupLedger` the emitter records each transformed diagnostic in, so the re-reports one
  lazy-wiring mistake produces at many sites are suppressed. The key scheme (the recovered cause,
  the rendered text, and the coded header) lives with the ledger, documented in
  [The driver](driver.md#naming-the-traits-behind-a-component-marker).
- **The signature keys**
  ([`signature`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/wording/signature.rs))
  are the two span-independent keys the emitter groups failures on: `cause_signature` (context,
  failing consumer trait(s), and each root-cause leaf) identifies *the same* failure across its
  re-reports for de-duplication. It is deliberately *textual*, because the ledger compares it
  against the rendered-message keys it falls back to for a declined diagnostic. The emitter's
  coalescing groups on a *structural* key instead, through `group_by_shared_cause`
  ([`group`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/group.rs)),
  which partitions the coalescible failures into the connected components of the shares-a-cause
  relation. The key is each cause's context and `Leaf` rather than the lead that leaf words, so
  grouping does not shift when a lead is reworded. It is taken per cause rather than per whole
  failure, because one mistake surfaces at several depths and each depth reaches a different
  *subset* of its causes, so demanding two identical sets would group none of them. Both are pure
  functions over the `Resolved` model.
- **The text signals**
  ([`signals`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs))
  are the stable rustc phrasings the emitter's candidate checks key on: the wiring-trait mention
  that marks a declined `E0599` as CGP's before its method-probe advice is stripped, the
  method-bounds `E0599` shape the resolver may safely run on, the method-probe advice the emitter
  strips, the orphan-parameter `E0210` shape, the `?`-operator cascade wording, rustc's advice to
  raise the recursion limit, which the emitter drops from a rewritten wiring overflow, and the
  trailing "detailed explanations" footer the emitter rebuilds (both recognizing the line and
  reading the codes it names). Each is a pure function, so the wording dependence on rustc's
  phrasing is documented and tested in one place.
- **The candidate bound**
  ([`candidates`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/candidates.rs))
  cuts the list of implementors in a failed bound's help back to the length rustc prints outside a
  verbose session, eight and "and N others" (`bound_candidate_list`). The driver's injected
  `--verbose` lifts that limit, and a CGP crate implements `IsProviderFor` hundreds of times, so the
  emitter applies it to every diagnostic before anything else reads it.

A further module,
[`code`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/code.rs),
holds the `CGP-E` error-code constants the rewrite and the diagnosis wording stamp on classified
main messages (catalogued in [error-code.md](../error-code.md)). This document covers the
post-processing transforms in full and points at the other tenants' own documents.

## Where post-processing sits in the pipeline

Post-processing is the driver's final diagnostic pass, and how much of it applies depends on who
built the diagnostic (see [The error pipeline](error-pipeline.md)). The driver's emitter first tries
the [typed root-cause resolver](typed-root-cause-resolution.md); if that declines, it renames the
CGP wiring messages it recognizes; then it hands the diagnostic to the post-processing chain with an
[`Origin`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/chain.rs)
that says whether either transform rewrote it.

**A rewritten diagnostic gets the whole chain.** The tool built its sentences, so the path strip
gives every name the bare form the tool's own wording uses, except a name whose qualifier tells two
types apart (`std::io::Error`, see [Resugaring](resugaring.md#the-path-strips-that-run-first)), and
the resugaring tidies the compiler-formatted CGP types a rewrite embeds, such as a provider like
`RedirectLookup<…, PathCons<Symbol<…>>>` in a coded header, folded to `RedirectLookup<…, @…>`. The
missing-field reword finds nothing to match, because the resolver's tree never carries the
`` `HasField<…>` is not implemented `` clause the reword keys on.

**An untransformed diagnostic changes only where the chain recovers a CGP encoding.** rustc built
it, and the tool's job there is to leave it as plain `cargo check` prints it, except that a raw
`Symbol`, `PathCons`, or `Cons`/`Either` spine, or an unmet `HasField` bound, is unreadable. So a
message is replaced only when a resugaring stage or the missing-field reword fired; the strips alone
never count as a change. A path rustc printed in full on purpose survives: two types that share a
name ("expected `a::Foo`, found `b::Foo`"), or a CGP trait the crate glob-imports, which rustc's
trimmed paths leave qualified (`cgp::prelude::CanRaiseError`). Once a stage does fire, the strips
apply to the rest of that message too, so the recovered construct does not sit among long paths. A
path resugared in an untransformed message keeps its `Path!(@…)` macro form, since the reader meets
it as a type. One more change reaches an untransformed diagnostic, outside this crate: the driver
merges a diagnostic rustc reports twice into its first report (see
[The driver](driver.md#naming-the-traits-behind-a-component-marker)).

**In a crate that does not use CGP, an untransformed diagnostic is never post-processed.** The
emitter asks the compiler once whether the crate uses `cgp` or one of CGP's own crates
(`crate_uses_cgp` in the driver's `resolve/cgp_item.rs`, reading the `used_crates` query, which
counts a crate's dependencies as used with it). A crate that declares `cgp` but never names it does
not load it, so its own `Symbol`, `Chars`, or `HasField` is never mistaken for CGP's. The query is
safe only once the crate store is frozen, so the emitter skips an untransformed diagnostic that
arrives earlier, during name resolution; see the hazard in
[rustc diagnostic internals](rustc-diagnostic-internals.md#freezing-the-crate-store-during-name-resolution-data-should-not-be-frozen).

## How the driver applies the transforms

The driver applies post-processing over a `DiagInner` before its inner emitter renders it, so the
rendered output reflects the change. Each transform is a text function, and the driver runs
[`postprocess_message`] over every plain-string message and span label of the diagnostic and its
children. That is the same reach the compiler's renderer has, so the caret label, the notes, and the
header are all covered. Editing the structured `DiagInner` rather than a rendered blob means the
transform never touches the source snippets the emitter pulls from the `SourceMap`, so it cannot
corrupt a line of the user's own code the way a whole-text rewrite could.

**One rustc "message" can be several styled fragments, and a construct split across them needs the
fragments read together.** `Diag::highlighted_*` stores one entry per `StringPart`, which the
renderer concatenates; rustc splits a message that way to highlight part of it, and when what it
highlights is the *difference between two types* it splits at every difference. Its "similar impl"
hint does exactly that, so a `Symbol<3, Chars<'B', …>>` in one of the two traits is shredded into a
fragment per character and no fragment holds a whole construct to match. The header beside it would
read `Symbol!("Bar")` while the hint still showed the raw list. So the driver post-processes each
fragment first, keeping rustc's highlighting, and then reads them as the one line they render as
through
[`postprocess_fragments`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/chain.rs).
When that recovers something the per-fragment pass could not, the message collapses to that single
unstyled string. Matching on the concatenation is matching on what the reader actually sees, and the
highlighting is given up only when there was a construct to recover, never merely because a fragment
was tidied on its own.

One transform needs a fact about the whole diagnostic rather than one message, and the driver
computes it once up front. The missing-field reword must know whether the context implements
`HasField` for *any* field, because that decides between two wordings whose fixes differ, and the
"similar impl" landmark that tells it can sit in a different child than the clause. So the driver
scans every message and label with
[`context_has_hasfield_impls`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/missing_field.rs)
first, then passes the answer into each per-message rewrite. It reads each message's fragments
joined, since rustc styles the `is` of `is implemented for it` as a fragment of its own, and the
check strips module paths before it matches, since rustc's separate note names the trait qualified
when the crate glob-imports it (`` implements trait `cgp::prelude::HasField<Tag>` ``). Missing
either landmark would make a struct that derives `HasField` read as one that does not, and the
rewrite would wrongly say the derive is required.

## The post-processing transforms

Post-processing is a chain of transforms applied in order, so the output of one feeds the next, and
the order matters. Module-path stripping runs first so the later transforms match the bare names
(`Symbol`, `Chars`, …) rather than their fully-qualified forms; `Symbol!` resugaring runs before
`Path!` resugaring (which reads the already-resugared `Symbol!("…")` segments), before list
resugaring (which reads a `Field`'s `Symbol!("…")` tag when naming a struct field or enum variant),
and before the field rewrite (which matches the resugared `HasField<Symbol!("…")>` form). Six
transforms run, in three groups:

- **The path strip**:
  [`strip_unambiguous_paths`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/strip_modules.rs),
  which drops the module segments of each `a::b::C` identifier run, keeping a trait or type before
  an item (`TryComputer::try_compute`), unless the qualifier tells two types apart, as the driver's
  [`AmbiguousNames`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/ambiguous.rs)
  says (`cgp::prelude::Chars` → `Chars`, `std::io::Error` kept), or the run is the path of a
  `use` statement, which the reader types whole. It leads the chain because everything after it
  matches bare type names;
  [Resugaring](resugaring.md#the-path-strips-that-run-first) covers what each leaves alone and why.
- **The three resugaring transforms**,
  [`resugar_symbol`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/resugar_symbol.rs)
  (`Symbol<2, Chars<'x', Chars<'y', Nil>>>` → `Symbol!("xy")`),
  [`resugar_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/resugar_path.rs)
  (`PathCons<Symbol!("app"), PathCons<GreeterComponent, Nil>>` → `@app.GreeterComponent`, or the
  `Path!(@…)` macro form when its `wrap` parameter is set), and
  [`resugar_lists`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/resugar_list.rs)
  (`Cons`/`Either` lists → `Product![…]`/`Sum![…]`, or a `Struct!`/`Enum!` shape when every element
  is a `Field` cell and the shape has an exact spelling), reverse a CGP type-level expansion back to
  the syntax the programmer wrote. They are one of the tool's
  [three resugaring implementations](resugaring.md), which **[Resugaring](resugaring.md)** documents
  in full: what each construct expands to and folds back to, the exact-match rule that makes each
  decline rather than guess, why this text implementation needs hand-rolled structural parsing where
  the driver's typed one does not, and who passes `wrap`. Read it before changing any of the three,
  since a change to what a construct resugars to belongs in all three implementations at once.
- **[`rewrite_missing_fields`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/missing_field.rs)**
  turns an unmet `HasField` bound into a missing-field message where the text shows the field is
  missing. It matches (after the two transforms above)
  `` the trait `HasField<Symbol!("name")>` is not implemented for `Context` `` and rewrites it to
  `` missing field `name` on `Context` `` when the same diagnostic shows the context implementing
  `HasField` for another field: rustc's "similar impl" landmark, which the CGP
  [check-trait-failure catalog entry](../../cgp/errors/checks/check-trait-failure.md) documents,
  either inline (`` but trait `HasField<…>` is implemented for it ``, one other field) or as a
  separate `` `Context` implements trait `HasField<…>` `` note (several other fields). A struct with
  `HasField` impls for its other fields derives it, so the field it lacks is missing. The rewrite
  carries no CGP error code: the clause sits in a sub-message, and codes classify only a rewritten
  *main* message (see [error-code.md](../error-code.md)).

  **Every other clause keeps rustc's wording**, because the text cannot tell what the fix is. With
  no landmark the context implements `HasField` for no field, which a struct lacking the derive, a
  struct lacking the field, and a fieldless struct whose derive generates nothing all show alike;
  naming the derive there would state a fix nothing confirms (the `no_landmark_keeps_the_clause`
  test in
  [`postprocess.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/postprocess.rs)).
  A digit tag (`Symbol!("0")`) names no field, since a tuple struct keys its fields `Index<0>`
  ([`symbol_tag_on_tuple_struct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/symbol_tag_on_tuple_struct.rs)),
  and a `__Context__`-style parameter a macro generated is not a struct, so its fix is a bound (the
  driver reports a provider missing such a bound as `[CGP-E036]`, per
  [The driver](driver.md#reshaping-an-undeclared-dependency)).

In practice the missing-field reword rarely fires, because the
[typed root-cause resolver](typed-root-cause-resolution.md) recovers most missing-field failures
from the compiler and replaces them with a dependency tree before this fallback is reached. The
transform remains for the diagnostics the resolver declines, where the text clause is all there is
to work with.

## Testing with pure inputs

Because each transform is a pure function over a string, it is tested without running the tool. A
test drives one transform over the case under test and asserts on the returned `Option<String>`;
nothing compiles, no driver runs, and the test is fast and deterministic, so a whole catalog of
cases can be exercised as ordinary library tests. This is what the rustc-free design buys.
[`tests/error_processing/postprocess.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/postprocess.rs)
drives each transform: a stripped prefix, an exactly-matched `Symbol!`, a wrong length or foreign
type left alone, the single-field rewrite (inline and separate-note landmark) and the clauses it
keeps, and the `postprocess_message` chain end to end. The diagnosis wording is tested the same way,
only over a hand-built `Resolved` rather than a string:
[`tests/error_processing/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/diagnosis)
drives `plan_resolved` through the missing-field, missing-derive, `Deref`-target,
field-type-mismatch, use-site, kept-ordinary-bound, and provider-header cases, asserting the header,
`help`s, and notes it returns with no compiler in the loop.

The [UI snapshot suite](testing.md) exercises the transforms a second way, over real diagnostics:
every fixture's `.cgp.stderr` is what the driver rendered after applying them, so a change to a
transform that affects an emitted diagnostic shows up as a snapshot diff. The two levels guard
different seams: this crate's tests pin a transform on a curated input, while the UI suite proves
the transforms stay consistent with what the driver emits across the whole catalog.

## Planned work

The transforms still ahead extend the per-diagnostic cleanup, each a new function added to the
post-processing chain, each applying the same exact-match caution `resugar_symbol` sets the
precedent for. The type-level encodings a CGP diagnostic carries are all decoded (`Symbol!`,
`Path!`, and the `Product!`/`Sum!` lists with their record and variant forms), so what remains on
that front is whichever encoding a new CGP construct introduces, and the place to add it is
[Resugaring](resugaring.md). Recognizing more error classes is the other direction, each rewriting
its message the way the missing-field transform does.

One larger transformation is deliberately out of scope for this crate's per-string transforms:
collapsing a *cascade*, the one deep mistake reported at every transitively dependent provider, into
a single root cause. That is a cross-diagnostic transform, and it can only be decided by looking at
the whole diagnostic set. It lives in the driver's emitter, which buffers the compilation's
diagnostics and coalesces the failures that share a cause at flush (see
[The driver](driver.md#naming-the-traits-behind-a-component-marker)). This crate supplies the pure
pieces it runs on: `group_by_shared_cause`, `Causes::union`, and the `DedupLedger`.

## Comparison with Clippy

Clippy offers no prior art for this crate, and the absence is itself informative. Clippy defines no
diagnostic type of its own and never rewrites a diagnostic: it reuses rustc's `Diag`/`DiagCtxt`
machinery and emits its lints through the compiler's own emitters, so its output is rustc's,
unmodified
([`clippy_utils/src/diagnostics.rs`](../../../external/rust-clippy/clippy_utils/src/diagnostics.rs)).
`cargo-cgp` does the opposite, *rewriting* the diagnostics rustc already produced, which is why it
needs a body of string transforms Clippy has no equivalent of. Keeping those transforms in a
rustc-free crate is the design that makes them testable without the compiler, precisely because
Clippy's "just use the compiler's emitter" approach is not open to a tool that rewrites.

## Tests

- [`crates/cargo-cgp-error-processing/tests/error_processing/postprocess.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/postprocess.rs):
  drives each post-processing transform over crafted inputs: the head-and-tail split
  `scan_head_tail` over nesting, a string literal, and its two declines, the stripped/left-alone
  prefix cases,
  the exact-match cases `resugar_symbol` must skip, the `PathCons` → `Path!` resugaring (symbol,
  type, and primitive segments, the open `_` tail left out of a key and declined by the `Path!`
  form, and the non-round-trippable cases `resugar_path` must skip), the single-field (inline and
  separate-note landmark, each also with a qualified trait path) rewrite versus the kept clauses (no
  landmark, a digit tag, a generated context) of `rewrite_missing_fields`, the `Product!`/`Sum!`
  folds with their `Struct!`/`Enum!` shapes and declines, and the `postprocess_message` chain,
  including the `Origin` rule: an untransformed message keeps rustc's paths unless a CGP encoding is
  recovered, and a rewritten one is stripped.
- [`crates/cargo-cgp-error-processing/tests/error_processing/shape.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/shape.rs):
  the shared `Struct!`/`Enum!` spelling rules on their own: writable, raw, and unwritable names,
  the named and tuple struct forms and every product that declines, each variant spelling, and the
  enum declines.
- [`crates/cargo-cgp-error-processing/tests/error_processing/rewrite.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/rewrite.rs):
  the wiring-message rewrite over a hand-built name map (see [The driver](driver.md#tests)).
- [`crates/cargo-cgp-error-processing/tests/error_processing/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/diagnosis):
  `plan_resolved` and the wording over hand-built `Resolved` values: the missing-field,
  missing-derive, and `Deref`-target field cases, a field-type mismatch, an abstract-type mismatch
  (with its wiring `help`) and its help-less plain-associated-type sibling, a use-site method
  failure, a kept ordinary bound (header dropped, lead-less note), a provider header via the text
  rewrite, and the pluralized consumer header.
- [`crates/cargo-cgp-error-processing/tests/error_processing/tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/tree.rs):
  the `termtree`-backed `render_dependency_tree` (a list, a branch); building and merging trees is
  the graph's job, tested in `graph.rs`.
- [`crates/cargo-cgp-error-processing/tests/error_processing/graph.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/graph.rs):
  the `DependencyGraph` build-and-render, as `insta` inline snapshots: a list, a shared-prefix
  branch, a subsuming cascade, converging leaves, a diamond, a super-root, a within-path repeat,
  repeated generics rendered in full, and the cross-block elision (see
  [Dependency-graph rendering](dependency-graph-rendering.md)).
- [`crates/cargo-cgp-error-processing/tests/error_processing/wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/wiring.rs):
  `plan_wiring_conflict` and `wiring_conflict_help` over hand-built `WiringConflict` values: the
  duplicate, overlap (component and path forms), multiple-namespaces, redirect (header plus its
  help), and same-/different-path duplicate-redirect headers.
- [`crates/cargo-cgp-error-processing/tests/error_processing/structural.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/structural.rs):
  `plan_structural_mistake` and `structural_mistake_help` over hand-built `StructuralMistake`
  values: the duplicate check entry (plain and with parameters), the two check-trait name forms, the
  `for` loop key, the generic `#[default_impl]`, the wiring entry whose key skips its parameters,
  with one or two parameters, each help form, and a namespace entry, and the check at unit
  parameters, with one or two parameters in each check macro's form, and the shared dispatch method,
  with its note.
- [`crates/cargo-cgp-error-processing/tests/error_processing/dispatch_names.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/dispatch_names.rs):
  the `#[cgp_auto_dispatch]` names: a helper's method read back, other names declined, and the
  computer's PascalCase name.
- [`crates/cargo-cgp-error-processing/tests/error_processing/coalesce.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/coalesce.rs):
  `coalesce_underived_fields` over hand-built causes: the merged group (keeping every field's path),
  its lead and single derive help, and the boundaries (a lone underived field, genuinely missing
  fields, different owners, a group beside a missing field).
- [`crates/cargo-cgp-error-processing/tests/error_processing/group.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/group.rs):
  `group_by_shared_cause` over hand-built resolutions: failures sharing a cause grouped, disjoint
  ones kept apart, the union-of-two-others case partial overlap produces, the transitive bridge that
  makes the relation a partition, the context keeping one field name on two contexts apart, a
  causeless failure alone, and the arrival ordering of the groups and their members.
- [`crates/cargo-cgp-error-processing/tests/error_processing/causes.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/causes.rs):
  the `Causes` set: one leaf reached by three consumers collecting into one cause with all three
  paths, the repeated-underived-field lead the invariant prevents, distinct leaves kept apart, an
  exact repeat of a path dropped, `from_sub_chains` grouping, `union` folding a shared cause while
  keeping every route (and its associativity), and `headed_by` prefixing every path, plus its
  commutation with the grouping, which is why heading needs no re-merge.
- [`crates/cargo-cgp-error-processing/tests/error_processing/candidates.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/candidates.rs):
  the candidate bound: a long list cut to eight and a count, a list rustc prints whole left alone,
  the shared-type heading, and any other help left alone.
- [`crates/cargo-cgp-error-processing/tests/error_processing/dedup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/dedup.rs):
  the `DedupLedger` key scheme: a re-reported cause suppressed, distinct causes kept, the text key,
  the coded-header key collapsing a declined fallback but never a resolved report (in either
  arrival order, or with a second cause set), and a kept rustc header never keying.
- [`crates/cargo-cgp-error-processing/tests/error_processing/signals.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/signals.rs):
  the text signals: the wording each matches and the near-miss it must not (the two `E0599` shapes,
  the method-probe artifacts, the orphan marker-plus-phrase pair, the `?`-cascade phrasing, the
  recursion-limit advice, and both footer forms, including the reworded line that yields no codes,
  the case the rebuild must decline on rather than delete the footer), and the reserved names a
  macro generates beside the words a user's own name can form.
- [`crates/cargo-cgp-error-processing/tests/error_processing/orphan.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/orphan.rs):
  `plan_orphan_conflict` and `orphan_conflict_help` over hand-built conflicts: a component key and a
  path key registered, and the reopen trigger's inheritance fix.
- [`crates/cargo-cgp-error-processing/tests/error_processing/internal_error.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/internal_error.rs):
  the internal-error note naming the panic and the issue tracker.
- [`crates/cargo-cgp-error-processing/tests/error_processing/cgp_impl_misuse.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/cgp_impl_misuse.rs):
  the wrong-half wording: a consumer trait in the header (naming the provider to use), a trait that
  is not a CGP component (whose help names a provider trait for the header), a consumer trait in a
  provider bound, a provider trait in `#[uses]` (naming the consumer trait to declare), and an inner
  provider not imported (plain, and of a generic component, with a parameter left for the reader).
- [`crates/cargo-cgp-error-processing/tests/error_processing/undeclared.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/undeclared.rs):
  the `[CGP-E030]` header naming the undeclared trait, and the help naming the `#[uses(…)]` to
  write: with the arguments a generic trait's call fixes, with a parameter the call does not give
  away left for the reader to replace (one or several), and absent when the bound cannot be written.
- [`crates/cargo-cgp-error-processing/tests/error_processing/wiring_name.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/wiring_name.rs):
  the wiring-name wording: a consumer trait as a key, a component not in scope with its import, a
  guessed key with the real component, an undeclared provider with and without a near miss, and a
  `#[cgp_impl]` provider never declared.
- [`crates/cargo-cgp-error-processing/tests/error_processing/unimported.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/unimported.rs):
  the `[CGP-E035]` header naming the abstract type, and the help naming the `#[use_type(…)]` import.
- [`crates/cargo-cgp-error-processing/tests/error_processing/requirement.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/requirement.rs):
  the `[CGP-E036]` header and helps: one requirement, several declared together, and an
  abstract-type component imported with `#[use_type]` rather than declared.
- The [UI snapshot suite](testing.md) exercises the transforms over every fixture's real
  diagnostics: each `.cgp.stderr` is what the driver rendered after applying them.

## Source

- [`crates/cargo-cgp-error-processing/src/postprocess/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/postprocess):
  the post-processing transforms: `mod.rs` (re-exports), `chain.rs` (the `postprocess_message` chain
  with its `Origin` rule, and `postprocess_fragments`, which reads a message rustc split into styled
  fragments as the one line it renders as), `strip_modules.rs` (`strip_unambiguous_paths`, the
  UTF-8-safe module-qualifier collapse that keeps a disambiguating qualifier, and
  `strip_module_paths`, which keeps none; both keep a `use` statement's path), `ambiguous.rs`
  (`AmbiguousNames`, which qualified names tell two types apart), `strip_prefixes.rs`
  (`strip_cgp_prefixes` and the `CGP_PREFIXES` constant), `resugar_symbol.rs` (the exact-match
  `Symbol!` parser), `resugar_path.rs` (the `PathCons` → `@…`/`Path!(@…)` resugarer, the form chosen
  by its `wrap` parameter), `resugar_list.rs` (`resugar_lists`, the `Product!`/`Sum!` and
  `Struct!`/`Enum!` resugarer), `spine.rs` (`scan_head_tail`, the split of a cell into its head
  and tail that both resugarers read), and `missing_field.rs` (`rewrite_missing_fields`,
  `context_has_hasfield_impls`, and the landmark-gated single-field classification).
- [`crates/cargo-cgp-error-processing/src/shape/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/shape):
  the shared shape spellings: `shape_name.rs` (which names a body can write, and which only raw),
  `struct_shape.rs` (`ShapeTag` and `render_struct_shape`), and `enum_shape.rs`
  (`render_enum_shape` and `render_variant`).
- [`crates/cargo-cgp-error-processing/src/rewrite/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/rewrite):
  the wiring-message rewrite and `ComponentNameMap` the driver drives: `mod.rs` (re-exports),
  `message.rs` (`rewrite_message` and the note/header forms: the code-stamping `rewrite_trait_bound`
  and the `E0275` `rewrite_wiring_overflow`, whose reason comes from the diagnosis model's
  `overflow.rs`), `names.rs` (`ComponentNameMap`/`ComponentTraitNames`), `parse.rs`
  (`parse_trait_bound`), and `text.rs` (the segment/generics splitters). See
  [The driver](driver.md#naming-the-traits-behind-a-component-marker).
- [`crates/cargo-cgp-error-processing/src/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis):
  the rustc-free root-cause model and its wording: `leaf.rs` (`Leaf`/`FieldIssue`, and the facts a
  `help` reads, `FieldFix`/`NearMiss`/`DeriveFix`), `resolved.rs`
  (`Cause`, holding a leaf and every path that reaches it; `Causes`, the set that keeps one cause
  per distinct leaf by construction, through `from_sub_chains`/`union`/`headed_by` over a private
  field; and `Resolved`), `node.rs` (`DepNode` / `ChainNode`, the structured chain nodes and their
  rendering, with `PartialValue`, a builder or extractor named in words) and `graph.rs` (`DependencyGraph`, the DAG build-and-render), the `wording/` directory
  (`header.rs` (`class_sentence`, `class_code`, `consumer_header`, and the finders of the leaf a
  mismatch headline states), `headline.rs` (`cause_headline` and `merged_cause`, the displayed
  headline), `lead.rs`
  (`root_cause_lead` and the leaf codes), `note.rs` (`cause_notes`, which folds every cause's paths
  into one graph and words the heading over it, and `cause_notes_seen`, the same against a `seen`
  set shared with the compilation's other notes), `help.rs` (`fix_help_messages`, which words one
  `help` per kind of fix on one owner and is the one entry point both the streaming plan and the
  emitter's coalesced block build their `help`s through, so a merged block carries the same fixes),
  and `signature.rs` (`cause_signature`)), `group.rs` (`group_by_shared_cause`, partitioning the
  coalescible failures into the connected components of the shares-a-cause relation, keyed
  structurally on each context-scoped `Leaf`), `coalesce.rs` (`coalesce_underived_fields`),
  `plan.rs` (`DiagKind`, `DiagnosisPlan`, the unrendered `PendingNote` and its `render`, and
  `plan_resolved` with its `categorized_header`), `overflow.rs` (`WiringOverflow` and
  `OverflowStep`, with `wiring_overflow_reason` and `wiring_overflow_help` for the `[CGP-E020]` and
  `[CGP-E021]` headers), `structural.rs` (`StructuralMistake`, with `plan_structural_mistake` and
  `structural_mistake_help` for the `[CGP-E015]`–`[CGP-E019]`, `[CGP-E060]`, and `[CGP-E061]`
  headers and fixes, and `structural_mistake_note`), `dispatch_names.rs` (`dispatch_helper_method`
  and `dispatch_computer_name`), `similar.rs` (`similar_name` and `similar_key`, the near-miss rules
  the fix `help`s use), and `wiring.rs` (`WiringConflict`/`WiringKey`, `plan_wiring_conflict` for
  the `[CGP-E010]`–`[CGP-E014]` duplicate-key headers, and `wiring_conflict_help` for the redirect
  fix), plus `orphan.rs`, `undeclared.rs`, `unimported.rs`, `requirement.rs`, `cgp_impl_misuse.rs`,
  `macro_less_provider.rs`, and `wiring_name.rs` (the `[CGP-E022]`, `[CGP-E030]`–`[CGP-E039]`, and `[CGP-E040]`–`[CGP-E044]`
  reshape models and their wording), and `internal_error.rs` (the note on a diagnostic shown
  untransformed after a contained panic). See
  [Typed root-cause resolution](typed-root-cause-resolution.md) and
  [The driver](driver.md#reshaping-a-duplicate-key-conflict).
- [`crates/cargo-cgp-error-processing/src/tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/tree.rs):
  the `DependencyTree` type and its `cargo tree`-style renderer, the target the
  [dependency graph](dependency-graph-rendering.md) expands into (the merging lives in the graph,
  not here).
- [`crates/cargo-cgp-error-processing/src/dedup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/dedup.rs):
  the `DedupLedger` and its span-independent key scheme.
- [`crates/cargo-cgp-error-processing/src/signals.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs):
  the rustc-phrasing predicates the emitter's candidate checks and cleanups key on.
- [`crates/cargo-cgp-error-processing/src/candidates.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/candidates.rs):
  `bound_candidate_list`, the implementor list cut back to rustc's default length.
- [`crates/cargo-cgp-error-processing/src/code.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/code.rs):
  the `CGP-E` error-code constants, catalogued in [error-code.md](../error-code.md).
- [`crates/cargo-cgp-driver/src/emitter/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter):
  the driver-side caller: applies the transforms over a `DiagInner`'s messages and span labels after
  its own rewrite.

## Further reading

- [The error pipeline](error-pipeline.md): the surrounding stages: how rustc is configured to emit
  better diagnostics, how each diagnostic is transformed, and how the result is rendered.
- [The driver](driver.md): the emitter that drives these transforms, and the wiring rewrite in full.
- [CGP error catalog](../../cgp/errors/README.md): the error classes the transforms must learn to
  recognize, and where each class hides or surfaces its root cause.
