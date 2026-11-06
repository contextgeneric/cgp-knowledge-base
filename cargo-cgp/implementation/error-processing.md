# Error processing

[`cargo-cgp-error-processing`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing)
holds the string-level diagnostic logic the driver drives, and links no compiler internals. That is
the one reason it is a separate crate: it builds and its tests run on any toolchain, so a plain unit
test exercises a transform over a hand-built input with no compiler, cargo, or `cargo-cgp` process.
The driver depends on it and calls it from its emitter, and the crate depends on neither executable.
Move logic here when a plain-data boundary lets it, per `cargo-cgp/AGENTS.md`.

## What the crate holds

This document covers post-processing in full. The rest of the crate serves subsystems documented
elsewhere:

| Module | Holds | Documented in |
| --- | --- | --- |
| [`postprocess`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/postprocess) | The final text pass over each message | [Below](#the-post-processing-transforms) |
| [`shape`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/shape) | `Struct!` and `Enum!` spellings, shared by the text and typed resugaring so they cannot disagree | [Resugaring](resugaring.md#struct-and-enum-a-list-of-fields) |
| [`rewrite`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/rewrite) | The wiring-message rename and `ComponentNameMap` | [Diagnostic reshapes](driver/diagnostic-reshapes.md#naming-the-traits-behind-a-component-marker) |
| [`diagnosis`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis) | The `Resolved` model, its wording, the shape decision of a `DelegateComponent` leaf, and the plan and models of each reshape | [The transformed diagnostic](typed-resolution/output.md), [Leaves](typed-resolution/leaves.md#the-leaf-shapes), [Diagnostic reshapes](driver/diagnostic-reshapes.md) |
| [`tree`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/tree.rs) | The `cargo tree`-style renderer the graph expands into | [Dependency-graph rendering](dependency-graph-rendering.md) |
| [`dedup`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/dedup.rs) | The `DedupLedger` | [The driver](driver/program.md#de-duplicating-and-coalescing) |
| [`byte_range`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/byte_range.rs) | The anchors' span decisions over plain ranges | [The anchors](typed-resolution/anchors.md) |
| [`signals`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs) | The stable rustc phrasings the emitter keys on, reads names out of, or writes back | Here |
| [`candidates`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/candidates.rs) | The implementor list cut back to rustc's length | [The driver](driver/program.md#un-eliding-the-diagnostic) |
| [`syntax`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/syntax) | Telling a string literal from code, and spelling a name | [Resugaring](resugaring.md) |
| [`naming`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/naming.rs) | The reserved names CGP macros invent | [Diagnostic reshapes](driver/diagnostic-reshapes.md#dropping-a-suggestion-that-names-a-generated-identifier) |
| [`code`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/code.rs) | The `CGP-E` constants | [error-code.md](../error-code.md) |

These design choices in the modules are worth keeping:

- **The dependence on rustc's phrasing lives in `signals`.** Each phrasing the emitter keys on,
  reads a name out of, or writes back (the rebuilt footer lines) is one pure function, so when a
  nightly rewords a message, the fix and its test sit in one place.
- **`DiagnosisPlan` carries the note unrendered,** as a `PendingNote`, because rendering needs the
  emission order only the flush knows. Keeping one representation also stops the tests pinning one
  note while the emitter shows another.
- **Two kinds of key serve two purposes.** `cause_signature` is textual, because the ledger compares
  it with its rendered-message keys. `group_by_shared_cause` keys on each cause's `Leaf` and
  context, so rewording a lead does not shift the grouping.
- **A resolver decision can move here behind a facts trait.** `delegate_leaf_shape` decides which
  leaf an unmet `DelegateComponent` is over facts the driver reads through `DelegateLeafFacts`, so
  its precedence is tested without a compiler. The driver keeps the reads, since they compare types,
  scan impls, and run the trait solver; a stand-in answering those queries would amount to a second
  solver. Each fact is a method, so the solver-backed one runs only on the branch that needs it.

## Where post-processing sits in the pipeline

Post-processing is the driver's final pass, after the
[typed resolver](typed-resolution/overview.md) and the text rewrite, and how much applies depends
on who built the diagnostic, as the `Origin` it receives says.

**A rewritten diagnostic gets the whole chain.** The tool built its sentences, so the strip gives
every name the bare form the tool's wording uses, except a name whose qualifier
[tells two types apart](resugaring.md#the-path-strips-that-run-first), and the resugaring tidies the
compiler-formatted CGP types a rewrite embeds.

**An untransformed diagnostic changes only where the chain recovers a CGP encoding.** The tool's job
there is to leave it as plain `cargo check` prints it, except that a raw `Symbol`, `PathCons`, or
`Cons`/`Either` spine, or an unmet `HasField` bound, is unreadable. So the strips alone never count
as a change, and a path rustc printed in full on purpose survives: two types sharing a name, or a
glob-imported CGP trait. Once a stage fires, the strips apply to the rest of that message too. A
path resugared here keeps its `Path!(@…)` form, since the reader meets it as a type.

**In a crate that does not use CGP, an untransformed diagnostic is never post-processed,** so its
own `Symbol` or `HasField` is never mistaken for CGP's. A crate that declares `cgp` but never names
it does not load it. The query is safe only once the crate store is frozen, so an untransformed
diagnostic arriving earlier, during name resolution, is skipped
([the hazard](rustc-diagnostic-internals.md#freezing-the-crate-store-during-name-resolution-data-should-not-be-frozen)).

## How the driver applies the transforms

**The driver edits the structured `DiagInner` rather than a rendered blob,** over every plain-string
message and span label of the diagnostic and its children. So a transform cannot corrupt a line of
the user's own code, which the renderer pulls from the `SourceMap`.

**One rustc message can be several styled fragments, and a construct split across them must be read
together.** rustc splits a message at every difference between two types it highlights, so its
"similar impl" hint shreds `Symbol<3, Chars<'B', …>>` into a fragment per character, and no fragment
holds a whole construct. The driver post-processes each fragment first, keeping the highlighting,
then reads them as the one line they render as (`postprocess_fragments`). The message collapses to
one unstyled string only when that recovers something the per-fragment pass could not, never because
a fragment was tidied alone.

**The missing-field reword needs a fact about the whole diagnostic,** since the landmark can sit in
a different child than the clause. So the driver computes `context_has_hasfield_impls` once, up
front. It reads each message's fragments joined, since rustc styles the `is` of
`is implemented for it` as its own fragment, and strips module paths first, since a glob import
makes rustc's note name the trait qualified. Missing either landmark would make a struct that
derives `HasField` read as one that does not.

## The post-processing transforms

The chain runs in an order that matters, because each stage matches what the one before left:

1. **[`strip_unambiguous_paths`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/strip_modules.rs)**
   drops module segments, so later stages match bare names. It keeps a qualifier
   [`AmbiguousNames`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/ambiguous.rs)
   says tells two types apart, a trait before its item, and the path of a `use` statement, which the
   reader types whole.
2. **`resugar_symbol`,** since the next two read its `Symbol!("…")` output.
3. **`resugar_path`,** to a bare `@…`, or the `Path!(@…)` form for an untransformed message.
4. **`resugar_lists`,** to `Product![…]` and `Sum![…]`, or a `Struct!` or `Enum!` shape when every
   element is a `Field` with an exact spelling.
5. **`rewrite_missing_fields`,** which matches the resugared `HasField<Symbol!("…")>`.

The three resugarings reverse a CGP expansion, and [Resugaring](resugaring.md) documents them with
the exact-match rule that makes each decline rather than guess. Read it before changing one, since a
change to what a construct resugars to belongs in all three implementations.

**The missing-field reword fires only where the text proves the field is missing.**
`` the trait `HasField<Symbol!("name")>` is not implemented for `Context` `` becomes
`` missing field `name` on `Context` `` when the diagnostic shows the context implementing
`HasField` for another field: rustc's "similar impl" landmark, inline for one other field and as a
separate note for several. A struct with impls for its other fields derives it. It carries no code,
since codes classify only a main message. It rarely fires, since the resolver recovers most of these
first, and it remains for what the resolver declines.

**Every other clause keeps rustc's wording, because the text cannot tell what the fix is:**

- **No landmark:** a struct lacking the derive, one lacking the field, and a fieldless struct whose
  derive generates nothing all look alike.
- **A digit tag:** `Symbol!("0")` names no field, since a tuple struct keys its fields `Index<0>`
  ([`symbol_tag_on_tuple_struct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/symbol_tag_on_tuple_struct.rs)).
- **A generated parameter:** `__Context__` is no struct, so its fix is a bound
  ([`[CGP-E036]`](driver/diagnostic-reshapes.md#reshaping-an-undeclared-dependency)).

## Adding a transform

A new type-level encoding gets a new function in the chain, with the exact-match caution
`resugar_symbol` sets. Collapsing a cascade does not belong here, because it needs the whole
diagnostic set: the [flush](driver/program.md#de-duplicating-and-coalescing) does that, over this crate's
pure pieces.

## Comparison with Clippy

Clippy offers no prior art for this crate, and the absence is itself informative. Clippy defines no
diagnostic type of its own and never rewrites a diagnostic: it reuses rustc's `Diag`/`DiagCtxt`
machinery and emits its lints through the compiler's own emitters, so its output is rustc's,
unmodified
([`clippy_utils/src/diagnostics.rs`](../../../external/rust/src/tools/clippy/clippy_utils/src/diagnostics.rs)).
`cargo-cgp` does the opposite, *rewriting* the diagnostics rustc already produced, which is why it
needs a body of string transforms Clippy has no equivalent of. Keeping those transforms in a
rustc-free crate is the design that makes them testable without the compiler, precisely because
Clippy's "just use the compiler's emitter" approach is not open to a tool that rewrites.

## Further reading

- [Architecture](architecture.md#the-flow-of-a-diagnostic): the steps around this pass.
- [The driver](driver/program.md): the emitter that drives these transforms.
- [CGP error catalog](../../cgp/errors/README.md): the error classes the transforms recognize.

## Tests

Each transform is a pure function, so a whole catalog of cases runs as ordinary library tests, under
[`crates/cargo-cgp-error-processing/tests/error_processing/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing).
The [UI suite](testing.md) guards the other seam: every `.cgp.stderr` holds the output the driver
rendered after applying them.

- [`postprocess/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/postprocess):
  each transform, what it must skip, and the `Origin` rule.
- [`shape.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/shape.rs),
  [`syntax.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/syntax.rs),
  and
  [`naming.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/naming.rs):
  the spelling and reading rules.
- [`rewrite/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/rewrite):
  the wiring-message rename over a hand-built name map.
- [`diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/diagnosis),
  [`coalesce.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/coalesce.rs),
  [`causes.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/causes.rs),
  and
  [`group.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/group.rs):
  the plan, the wording, and the cause sets, over hand-built `Resolved` values.
- [`graph.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/graph.rs)
  and
  [`tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/tree.rs):
  the graph and the renderer.
- [`wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/wiring.rs),
  [`orphan.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/orphan.rs),
  [`structural.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/structural.rs),
  [`dispatch_names.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/dispatch_names.rs),
  [`overflow.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/overflow.rs),
  [`cgp_impl_misuse.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/cgp_impl_misuse.rs),
  [`undeclared.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/undeclared.rs),
  [`unimported.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/unimported.rs),
  [`requirement.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/requirement.rs),
  and
  [`wiring_name.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/wiring_name.rs):
  the wording of each reshape.
- [`class_plan.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/class_plan.rs):
  each reshape class's header, notes, and `help`s landing in their own lists.
- [`delegate_leaf_shape.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/delegate_leaf_shape.rs):
  the `DelegateComponent` leaf's shape over every combination of its facts, over a stand-in that
  counts its reads of the solver-backed fact.
- [`dedup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/dedup.rs),
  [`signals.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/signals.rs),
  [`candidates.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/candidates.rs),
  [`byte_range.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/byte_range.rs),
  and
  [`internal_error.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/internal_error.rs):
  the smaller modules. `signals.rs` includes the near-miss each phrasing must not match, and a
  reworded footer the rebuild must decline on.

## Source

The table above links each module. These are the entry points into them:

- [`postprocess/chain.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/chain.rs):
  the order and the `Origin` rule.
- [`postprocess/spine.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/spine.rs):
  the split of a cell both resugarers read.
- [`diagnosis/class_plan.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/class_plan.rs):
  each reshape's header, notes, and `help`s in one value, for the stages.
- [`cargo-cgp-driver/src/emitter/edit/text.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/edit/text.rs):
  the caller, applying the transforms over a `DiagInner`.
