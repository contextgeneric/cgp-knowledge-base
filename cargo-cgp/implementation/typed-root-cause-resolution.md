# Typed root-cause resolution

The driver's most valuable transformation turns a CGP check-failure diagnostic into a compact,
root-cause-first error by *asking the compiler* what really failed rather than parsing rustc's text.
When a context is wired wrong, the compiler reports the failure against generated types the
programmer never wrote, and the one fact that matters (a missing field, an unwired component) is
buried under `IsProviderFor`/`CanUseComponent` scaffolding or dropped entirely. The resolver re-runs
the failing obligation through the trait solver, walks the wiring down to the actual root cause, and
re-renders the whole diagnostic as a `cargo tree`-style dependency chain with a single coded
headline.

The resolver reads the failure from the **real consumer and provider trait obligations**, never from
the `CanUseComponent`/`IsProviderFor` scaffolding. Those two traits exist only so that plain rustc
can surface a wiring failure at all (see [check traits](../../cgp/concepts/check-traits.md)):
`IsProviderFor` is generated to carry a *copy* of a provider's `where` bounds precisely so the
compiler names the missing one. cargo-cgp does not need that copy (it re-runs the trait solver on
the real provider impl, whose own `where` clause holds the same bounds), so it treats
`IsProviderFor` and `CanUseComponent` as plumbing to resolve *around*, reading the actual traits
instead. This is a deliberate constraint, not an accident of implementation: cargo-cgp aims to make
`IsProviderFor` *removable*, so its dependency resolution must not lean on it. (The text-rewrite
fallback for diagnostics the resolver declines still recognizes `IsProviderFor`/`CanUseComponent` in
rustc's rendered output; that is a separate concern, covered in [The driver](driver.md).)

This is a deeper transformation than the rename, and it builds on it.
[Naming the traits behind a component marker](driver.md#naming-the-traits-behind-a-component-marker)
edits a diagnostic in place, renaming its wording; the resolver instead reconstructs the failure
from compiler state and replaces the diagnostic wholesale. It is the compiler-state enrichment
described in [The driver](driver.md) and [The error pipeline](error-pipeline.md), and everything
downstream of its rustc-free
[`Resolved`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/resolved.rs)
model (the wording, the tree) is unit-tested without a compiler.

## A worked example

The clearest way in is one failure end to end, from the
[area-calculation example](../../examples/area-calculation.md). A `Rectangle` computes its area
through a wired `RectangleArea` provider that reads the rectangle's fields, but the struct is
missing one of them:

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_auto_getter]
pub trait HasRectangleFields {
    fn width(&self) -> f64;
    fn height(&self) -> f64;
}

#[cgp_impl(new RectangleArea)]
impl AreaCalculator
where
    Self: HasRectangleFields,
{
    fn area(&self) -> f64 {
        self.width() * self.height()
    }
}

#[derive(HasField)]
pub struct Rectangle {
    pub width: f64,
    // the `height` field is missing
}

delegate_components! {
    Rectangle {
        AreaCalculatorComponent: RectangleArea,
    }
}

check_components! {
    Rectangle {
        AreaCalculatorComponent,
    }
}
```

`RectangleArea` reads `width` and `height` through the `HasRectangleFields` getter, whose
`#[cgp_auto_getter]` blanket impl requires the context to have both fields. `Rectangle` derives
`HasField` but declares only `width`, so the wiring cannot be satisfied (the **root cause is the
absent `height` field**), and `check_components!` fails. Left to rustc, the failure reads as an
unmet `HasField<Symbol!("height")>` bound (often with the field name itself compressed to an
unreadable `Symbol<6, Chars<'h', …>>` list), routed through `IsProviderFor` and `CanUseComponent`.
The resolver replaces all of that with:

```text
error[E0277]: [CGP-E001] missing field `height` on `Rectangle`
  --> src/main.rs:62:9
   |
62 |         AreaCalculatorComponent,
   |         ^^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: root cause: [CGP-E110] missing field `height` on `Rectangle`
           this is required through the dependency chain:
             [CGP-E101] consumer trait impl `CanCalculateArea` for context `Rectangle`
             └─ [CGP-E102] provider trait impl `AreaCalculator` with context `Rectangle` for provider `RectangleArea`
               └─ [CGP-E104] trait impl `HasRectangleFields` for `Rectangle`
                 └─ [CGP-E110] missing field `height` on `Rectangle`
   = help: add the field `height: f64` to `Rectangle`
```

Every element of that output is reconstructed from the compiler, not read from rustc's message: the
headline states the actual mistake in one sentence, after the code `[CGP-E001]`, which classes the
failure as a context that cannot implement a *consumer trait*; the `root cause:` note repeats that
sentence above the tree; the tree shows the transitive path from the consumer trait the reader
checked (`CanCalculateArea`) down to the missing field, with each node named straight off the trait
it stands for; and the `help` names the field to add, with the type the getter requires. Read the chain as the real obligation chain the walk descended:
`Rectangle: CanCalculateArea` (the consumer) needs `RectangleArea: AreaCalculator<Rectangle>` (the
wired provider), which needs `Rectangle: HasRectangleFields` (the getter), which needs the `height`
field. No `IsProviderFor` node appears because the walk never went through one. The `[CGP-Exxx]`
codes are catalogued in [error-code.md](../error-code.md). The rest of this document explains how
each piece is produced.

## When the resolver engages, and when it declines

The resolver treats a diagnostic as a candidate whenever it reports an **unmet obligation** that
plausibly stems from a CGP component failure, then either traces it to a root cause or steps aside.
Concretely, a diagnostic is a candidate when it carries code **`E0271`**, **`E0277`**, or a
**method-bounds `E0599`**: the "the method `…` exists … but its trait bounds were not satisfied"
shape. An `E0275` overflow is no candidate, since the walk explains one only by a cut (a cycle, or a
lookup that grows), which [the driver](driver.md#naming-the-traits-behind-a-component-marker) words
from the overflow walk; a bound the walk stops at instead is one whose own evaluation overflowed,
which no root cause states truly. Any other code declines before the walk, even one whose text
names a CGP trait: a coherence conflict (`E0119`) between a derived `HasField` impl and
the `Deref` blanket impl names `HasField`, but two impls overlapping leaves no bound unmet, and
walking it would invent a missing-impl cause
([`deref_has_field_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/deref_has_field_conflict.rs)).
The gate does not ask whether the text names a CGP construct, because a failure that names none can
still be one a CGP component caused: a hand-written `Send`-recovery wrapper's `async fn` fails with
an `E0271` opaque-future mismatch, or a downstream bound needs a method the context cannot supply.
The resolver traces the dependency chain and treats the error as CGP-related exactly when a CGP
component failure sits in that chain; a candidate whose chain reaches no CGP cause **declines** and
passes through to the fallback text rewrite untouched.

Two more shapes are candidates for one anchor alone, the data-call anchor: the method probe's "no
method named `…`" `E0599`, and an `E0308` on a call's argument. A call to one of CGP's
extensible-data operations can fail with either before its bounds are checked (a builder finalized
with a field unset has no `finalize_build` at all, and an extractor with one variant left rejects
the tag of the variant it already ruled out), and an `E0308` is taken only when the walk finds the
field or variant state the operation rejects
([the data-call anchor](typed-resolution-call-site.md#calls-to-extensible-data-operations)).

The `E0599` arm is otherwise narrowed to those two shapes for a reason beyond relevance: a
*resolution*-class `E0599` (`no variant named …`, `no associated item …`) is emitted while type
lowering is still mid-flight, and running the resolver's trait solver on it re-enters the diagnostic
context and aborts the compiler. Declining such an `E0599` before any solving is both crash-safe and
correct (the resolver has nothing to say about a name-resolution error), whereas `E0271`/`E0277` are
trait-solving failures reported after collection and do not hit the hazard. This is the
re-entrant-emission panic catalogued in
[rustc diagnostic internals](rustc-diagnostic-internals.md#re-entering-the-diagnostic-context-lock-was-already-held),
where the phase a diagnostic is emitted in is what decides whether the solver may safely run on it.

A candidate the resolver accepts is transformed in two independent halves (the coded headline and
the root-cause notes), described in
[Typed resolution: the transformed diagnostic](typed-resolution-output.md). A candidate it declines
keeps rustc's diagnostic, cleaned only by the fallback [post-processing](error-processing.md).

## Why it runs in the emitter

The natural home for whole-crate typed analysis would be an `after_analysis` callback, where the
compiler hands the driver a `TyCtxt` directly, but that door is closed for exactly the crates that
matter. The `analysis` query raises a fatal error the moment type-checking reports any non-lint
error (`rustc_interface`'s `analysis` calls `has_errors_excluding_lint_errors().raise_fatal()`), and
that unwind happens *before* `after_analysis` runs. A crate with a CGP check failure has an error by
definition, so `after_analysis` never sees it, the same reason Clippy's late passes only run on code
that type-checks.

The one place that executes *while the error exists but before the fatal unwind* is the diagnostic
emitter, which the compiler calls as it emits each error during trait solving. A `TyCtxt` is in
thread-local scope there (the driver already relies on this for the trait-renaming rewrite), so the
resolver reaches the compiler through `rustc_middle::ty::tls` from inside `emit_diagnostic`. The
subtlety this design must be sound against is that it re-enters the trait solver *from within a
diagnostic being emitted mid-solve*. Building a fresh `InferCtxt` and `ObligationCtxt` and solving a
concrete obligation there works cleanly, and that re-entrancy is the load-bearing assumption of the
whole approach, exercised by every fixture the resolver reshapes.

Running compiler code from this position is also the source of every panic risk the tool faces. The
constraints it imposes (never force a query that emits, instantiate a binder before relating it,
keep each fresh `InferCtxt`'s variables to itself) are catalogued together in
[rustc diagnostic internals](rustc-diagnostic-internals.md#panic-hazards-running-compiler-code-inside-the-emitter),
and the boundaries at the end of this document note where a hazard puts a case out of reach.

## How the root cause is recovered

The recovery is a pipeline of typed lookups with no string parsing until the very last step decodes
a field name. It runs in the driver's
[`resolve`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve)
module (one sub-directory per stage, `anchor/`, `call_site/`, `walk/`, `classify/`, `label/`, over
the `query/` layer of compiler readers and CGP recognizers the stages share, each behind a
re-exporting `mod.rs`) and fills the rustc-free
`Cause`/`Leaf`/`FieldIssue`/`Resolved` types with owned `String`s, so the wording that consumes them
needs no compiler. Every stage is anchored by `DefId` to the CGP crate that defines the trait or
type it matches, so a same-named item from an unrelated crate can never drive a replacement. The
stages run in order: anchor the starting obligation, walk it down to the leaves, decode and classify
each leaf, render the chain, and emit. Each stage has its own document, and this section is the map
of them.

Two facts hold across every stage, and everything below assumes them. **The obligation the walk
works on is always a real trait obligation**, never a `CanUseComponent` or `IsProviderFor` wrapper:
a consumer-trait obligation `Ctx: ConsumerTrait<Params…>`, or, for a `#[check_providers]` entry, the
provider-trait obligation `Provider: ProviderTrait<Ctx, Params…>` the entry asserts. And **the
traits are recognized structurally, without `IsProviderFor`**:

- A **provider trait** is identified by the delegation blanket `#[cgp_component]` generates,
  `impl<Ctx, P> ProviderTrait<Ctx> for P where P: DelegateComponent<Marker>, …`, whose `Self` is a
  bare type parameter bounded by `DelegateComponent` (`is_provider_trait` /
  `provider_blanket_marker` in `query/cgp_item/`). That same blanket's `DelegateComponent<Marker>`
  bound also yields the component marker when an anchor needs it, in place of reading the
  `IsProviderFor<Marker, …>` supertrait.
- A **consumer trait** is identified by its blanket impl
  `impl<C> Consumer for C where C: Provider<C>` routing to such a provider
  (`consumer_provider_trait` / `is_consumer_trait`).
- The **marker → consumer** inversion the check and use-site anchors need (`marker_to_consumer`) is
  the composition of those two: the provider trait whose blanket keys on the marker, then the
  consumer whose blanket routes to that provider.

**[Anchoring the starting obligation](typed-resolution-anchors.md)** recovers the obligation the
compiler failed to prove, one of twelve ways tried in order. A `check_components!` entry is matched
by its caret to the check impl and its `CanUseComponent<Marker, Params>` assertion mapped to the
real consumer obligation, and a `#[check_providers]` entry the same way to the provider obligation
it asserts; a failure inside a hand-written `impl Trait for Context` block is recovered from the
impl's CGP consumer supertrait, and one inside an `impl … for Foreign` wrapper by descending its
supertrait's `where`-clause hops to a consumer on the context; a consumer-method `E0599` is
recovered from the context's own wired components, or from the consumer trait the diagnostic names
(the anchor that reaches a namespace-joined context); and a `#[cgp_fn]` / `#[blanket_trait]`
**blanket trait** required through a `where` bound (an `E0277`) is recovered from the blanket trait
the diagnostic names and the context read off the failing expression.

**[The call-site anchor](typed-resolution-call-site.md)** is tried seventh, for the use-site failure
whose spans touch nothing the span-matching anchors can read: a wiring that matches the called
component unconditionally (an `E0277` on the call itself), or a call to a `#[cgp_fn]` blanket-trait
method. It re-reads the failing call expression from HIR alone: the receiver carries the context,
the component's parameters come from unifying the call's *written* argument types against the
method's own declared signature, and every parameter the call leaves to inference is seeded as a
rigid placeholder the walk resolves around but never reports on. The eighth, the data-call anchor
`resolve_data_call`, re-reads a call to one of CGP's extensible-data operations, typing the builder,
extractor, or remainder it is called on through the chain of data operations and pattern bindings
that produced it. The ninth, the provider-call anchor `resolve_provider_call`, re-reads a provider
trait's method called through the provider's own path and walks the provider obligation it asserts,
as a `#[check_providers]` entry's is. The tenth, the bound-call anchor `resolve_bound_call`, reads
a call to a generic function whose own `where` bound the context fails, instantiating the bound
from the call's turbofish and arguments. The eleventh, `resolve_use_site_blanket_trait`, is the
by-consumer anchor's counterpart for a blanket trait required as a *bound* elsewhere rather than
*called*; both are gated to `E0277` and tried after the call-site anchors, so a method call leads
with the trait the programmer invoked. The twelfth and last, `resolve_forwarding_entry`, reads an
error on a `Key -> Table` wiring entry whose own forwarding bound fails, seeding the consumer
obligation the entry wires.

**[Walking to the root cause](typed-resolution-walk.md)** descends the seeded obligation's
dependency graph (following only the CGP wiring vocabulary and obligations on the context itself,
never `IsProviderFor`/`CanUseComponent`) to every terminal unmet bound, then decodes each terminal
(a `Symbol!` field name read structurally, the struct and its `Deref` chain inspected, a missing
wiring or dispatch entry named) and renders each hop as a tree label with the type-level lists
resugared.

**[The transformed diagnostic](typed-resolution-output.md)** is the output side: the coded
`[CGP-E001]` to `[CGP-E005]` and `[CGP-E050]` headline classes and the cause each headline states, the `root cause:`
notes over their merged dependency trees (with underived-field causes coalesced), and the emitter's
application of the rustc-free plan to the compiler's `DiagInner`.

## Boundaries and open ends

The resolver is deliberately bounded, and a few edges are worth recording. Because it anchors the
twelve ways above, a wiring failure that is *none* of them declines. The consumer-trait use-site
anchor reaches a manual supertrait bound in a trait definition or `where` clause, and a
namespace-joined use-site call, whenever a local CGP consumer trait and its context appear in the
diagnostic's spans (the `use_type_foreign_unsatisfied`, `use_type_nested_unsatisfied`, and
`namespace_join_use_site` fixtures under
[`checks/check-trait-failure/use-type/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/use-type)
and
[`hidden/unsatisfied-dependency/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/hidden/unsatisfied-dependency)).
The [call-site anchor](typed-resolution-call-site.md) covers the *foreign generic consumer* case,
the unconditionally-matching dispatch shape
([`cascade_after_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_after_use_site.rs)).
A caret on a *provider* struct's own impl is handled narrowly rather than fully. The impl-site and
wrapper-chain anchors skip the provider impl's *supertrait* recovery (its only supertrait is
`IsProviderFor`, so routing a cause through it would leak the provider trait's `__Context__` and an
`IsProviderFor` hop), but the impl-site anchor does recover a failing bound of any impl's own
`where` clause at its caret, such as a *cross-context* dependency in a provider's
(`where Inner: CanCompute`, a concrete context), walking it as that consumer obligation so it
de-duplicates into the context's own check
([`cross_context_node_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/cross_context_node_key.rs));
a provider impl carrying no such recoverable bound declines. What else declines is a failure none of
the recoveries reach: a generic component's trait definition, a call whose *receiver's type* is not
syntactically recoverable (a method call's result or a field access, `self.app.handle(…)`; typing
those needs the typeck results the emitter can never force), unless the receiver is a chain of
extensible-data operations the data-call anchor types from their signatures, or a written type
beyond the call-site anchor's small hand lowering. The wrapper-chain descent is itself bounded (it
follows only real impl `where`-clauses, reports a cause only at a genuine CGP consumer on a context,
and stops at a recursion bound), and every call-site seed is gated on actually failing, so neither
can fabricate a chain from an unrelated bound.

One use-site shape is out of reach for a hard reason worth recording: a **consumer-method call whose
failure is an `E0271`, not an `E0599`**: `app.deserialize_json_string::<Payload>(…)` on a context
that cannot deserialize `Payload`, which fails as a type mismatch on the trait's output (the
modular-serialization arena test hits this). Its caret sits on the method call, naming no
context-definition span, so neither use-site anchor finds a context; and recovering the obligation
would need the compiler's **typeck results**, which the resolver cannot obtain. `tcx.typeck` replays
its cached diagnostics when forced, so forcing it from the emitter re-enters the diagnostic context
and panics, the re-entrant-emission hazard in
[rustc diagnostic internals](rustc-diagnostic-internals.md#re-entering-the-diagnostic-context-lock-was-already-held).
Only the fresh-`InferCtxt` trait solver is safe to re-enter mid-emit; a full query is not, and there
is no hook between typeck and the fatal error to precompute the result. So this failure falls
through to rustc's output, usually redundant with the `check_components!` failure for the same
trait, which the resolver *does* reshape.

A few parameter-recovery limits remain. The impl-site path recovers a generic component's concrete
parameter from the supertrait, the by-component use-site path recovers it for an `open`-dispatched
component from the `PathCons<Component, Value>` redirect key, and the call-site path recovers every
parameter the call *writes*, seeding the rest as unknowns; what no path recovers is a parameter
whose only carrier is an argument the call does **not** type syntactically (a plain variable, an
unsuffixed literal), where the by-component path skips a generic component's bare marker, the
by-consumer path only fires for a consumer whose sole generic is `Self`, and the call-site seed's
unknown makes every root cause parameter-dependent. Such a failure declines to the fallback, whose
method-probe advice the emitter strips, so the unmet wiring bound leads
([`generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs)
pins the cleaned output). The plausible recovery, should the class need resolving in full, is to
re-check the wired delegate's *implemented* parameter values rather than skip the marker. And the
walk uses an **empty parameter environment** throughout, which suits the concrete check impls the
fixtures exercise but will need the impl's own environment to extend cleanly to checks that carry
generic parameters. The resolver renders only leaves it can trust (a `HasField` field (missing,
underived, or type-mismatched), an associated type the owner supplies differently from what a
provider requires, a missing wiring, a missing dispatch entry on a non-context delegation table, a
namespace redirect the context does not terminate, an extensible-data field or variant in a state
its operation does not allow or a data derive a type lacks, an ordinary foreign bound, or a terminal
blanket-trait bound), dropping pure wiring-plumbing dead-ends, so a diagnostic whose only
recoverable leaf is one of those falls back. Parallel branches, deep nesting, and non-field leaves,
by contrast, are all handled. The associated-type leaf is bounded in one way worth recording: it is
reported only for a *trait* associated-type projection, since an opaque, inherent, or const alias
has no `Trait::Assoc` to name; and where normalizing the projection does not reduce to a concrete
type, the leaf renders that side as `_` rather than guessing.

How a transformed diagnostic is *marked* as CGP is settled by the
[error-code scheme](../error-code.md): a rewritten, classified main message carries its `[CGP-Exxx]`
code inline, and everything else (a kept header over rewritten sub-messages included) stays in
rustc's own `error[E0277]:` form. There is no separate header brand; the inline code is the only
marking.

## Source

- [`crates/cargo-cgp-driver/src/resolve/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve):
  the typed resolution, split by stage into sub-directories behind re-exporting `mod.rs` files and
  building the rustc-free `Resolved` model. Every anchor feeds the walk a real trait obligation
  (the consumer obligation `Ctx: ConsumerTrait<Params…>`, or the provider obligation a
  `#[check_providers]` entry or a provider's own method call asserts), never a `CanUseComponent` or
  `IsProviderFor` wrapper.
  - [`anchor/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/anchor)
    holds eight of the twelve anchors, plus their two shared ingredients: `seed.rs`
    (`consumer_obligation`, the `Params`-slot ungrouping decided by the consumer's own generics: a
    single tuple-typed parameter kept whole, a lifetime restored from `Life<'a>` via `life_region`,
    any mismatch declining rather than handing the solver a malformed trait ref) and `spans.rs` (the
    local impls and struct definitions a diagnostic's spans land on, never a provider struct or a
    component marker, and `is_about_impl`, whether a caret inside an impl is about it).
    `check_failure.rs` matches the check impl by span (the query layer's `check_impls_at`), then
    `can_use_to_consumer_obligation` maps its `CanUseComponent<Marker, Params>` assertion through
    `marker_to_consumer` to the consumer obligation. `provider_check.rs` matches a
    `#[check_providers]` entry's check impl the same way and seeds the walk with the provider
    obligation it asserts, built by `seed.rs`'s `provider_obligation` and walked by
    `resolve_provider_leaves`, which records the provider. `impl_site.rs` recovers the context and
    the failing supertrait from an enclosing `impl Trait for Context` block, heading the tree with
    the impl's own wrapper trait (`[CGP-E001]` or `[CGP-E003]` by its blanket-impl fingerprint)
    through `wrapper_consumer_causes`, which seeds the supertrait directly when it is a CGP consumer
    *or* a `#[cgp_fn]`/`#[blanket_trait]` blanket-impl trait (`is_blanket_trait`), the latter
    reshaping a `#[cgp_fn]` blanket-trait check whose cause is a missing field; before that,
    `where_bound_on_context` reads a failing consumer bound on a concrete context in the impl's own
    `where` clause at the caret. `wrapper_chain.rs` is the foreign-wrapper case, descending each
    hop's `where`-clauses via `wrapper_chain_children` read un-normalized so an associated-type
    bound descends to its base trait, until `consumer_handoff_causes` reaches a CGP consumer on the
    context, named plainly with `subject_is_context = false`. `use_site.rs` recovers the context ADT
    from the diagnostic's spans and its wired components from `DelegateComponent` impls via
    `delegated_check_targets`, mapping each marker to its consumer and recovering an `open`-dispatch
    value from a `PathCons` key through `open_dispatch_target`, while skipping a raw path key, a
    redundant bare marker, a free-parameter catch-all, and a `namespace …;` blanket `__Key__` key.
    `forward_entry.rs` matches a `Key -> Table` entry by its forwarding bound's span inside the
    caret and seeds the consumer obligation the entry wires. `use_site_consumer.rs` recovers a
    local, non-generic CGP consumer trait from the diagnostic's spans and walks `Ctx: Consumer`
    directly (the anchor that reaches a namespace-joined context), and its by-blanket-trait sibling
    `resolve_use_site_blanket_trait` (eleventh, gated to `E0277`, tried after the call anchors) does
    the same for a `#[cgp_fn]`/`#[blanket_trait]` blanket trait required as a bound, reading the
    context off the failing expression via the call-site anchor's `contexts_at_spans` and heading
    the result `[CGP-E003]` by giving it the wrapper class. A blanket trait is recognized by
    `is_blanket_trait`: a blanket impl over a bare context, accepted only on evidence that the
    blanket depends on a CGP construct, so a `#[cgp_fn]` trait or one a library publishes is reached
    while `ToString`, `Into`, and a crate's own plain blanket traits are not.
  - [`call_site/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/call_site)
    holds the seventh to tenth anchors, `resolve_call_site`, `resolve_data_call`,
    `resolve_provider_call`, and `resolve_bound_call`, the HIR re-reads of the failing call, one
    stage per file: `find_call.rs` (`method_calls_at`, the calls a primary span lands on without
    lying strictly inside the receiver or an argument (`is_about_call`, over the rustc-free
    `byte_range` decision of that name), each tried against the
    candidate consumer traits and `#[cgp_fn]`/`#[blanket_trait]` blanket traits the query layer's
    `traits_with_method` finds by method name, the blanket traits headed `[CGP-E003]` by the wrapper
    class), `data_call.rs` (`resolve_data_call`, a method or type-relative call to an
    extensible-data operation in scope at the call, headed `[CGP-E050]` by the data-operation
    class), `provider_call.rs` (`resolve_provider_call`, a type-relative call to a
    provider trait's function in scope at the call, its provider obligation walked by
    `resolve_provider_leaves` from the context argument, headed `[CGP-E002]`), `bound_call.rs`
    (`resolve_bound_call`, a path call to a generic function whose own bound on a consumer or
    blanket trait fails for a context, the bound instantiated from the turbofish and the arguments,
    a binding typed by `query/binding.rs`'s `declared_binding_ty` with its references), `chain.rs`
    (`data_expr_ty`, the value such a call is made on, typed through the data operations and pattern
    bindings that produced it), `receiver.rs` (`receiver_context`/`local_binding_context`, the
    receiver's type from its binding, annotation, parameter, literal, or constructor-call signature,
    plus `contexts_at_spans`, the same reading applied to every expression at the diagnostic's
    spans, which is the by-blanket-trait anchor's context source), `unbounded.rs`
    (`unbounded_receiver`, a consumer method called on a receiver typed by a type parameter its item
    does not bound by the consumer trait, reported as the `[CGP-E129]` cause without a walk),
    `seed.rs` (`seed_from_call`, the signature unification: fresh variables for the method's item,
    `Self` pinned to the context, each written argument type unified with its declared input by the
    query layer's `unify_call_inputs` (from the first input for a type-relative call, and a data
    value's argument typed by `data_expr_ty` too), the trait's parameters read back with the query
    layer's `unknowns_to_placeholders` folding what stayed unresolved). The argument types the call
    writes and the syntactic type lowering they stand on are read in the query layer (below).
  - [`walk/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/walk)
    walks the cause chain to each terminal leaf. `leaves/` drives the recursion (`resolve_leaves`
    erasing the seed, `resolve_node` the per-node memoized descent with the cycle guard and
    `MAX_DEPTH` backstop, `select_children` what each node descends into, the foreign-getter descent into just context-side dependencies plus a
    same-trait list recursion, the drop of a leaf still carrying a call-site placeholder (an
    unknowable `_: Send` is never reported), and `compute_leaves` folding the root node's sub-result
    into a `Resolved`). `vocabulary.rs` decides what the descent walks into (`is_descendable`:
    provider traits, `DelegateComponent`, context obligations, and extensible-data traits, *not*
    `IsProviderFor`/`CanUseComponent`; `is_context_side`, the subset a foreign bound's blanket is
    followed into; and the `is_workaround_plumbing` drop of a
    `CanUseComponent`/`IsProviderFor` dependency beside the real obligation). The solver queries the
    walk asks live in the query layer (below).
  - [`classify/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/classify)
    classifies a terminal: `data.rs` reads an extensible-data terminal off the presence markers of
    the partial type it lands on (`classify_data_leaf`), `leaf.rs` turns it into the rustc-free
    `Leaf` (a field by inspecting the struct and its `Deref` chain in `field.rs`, with a missing
    field's fix confirmed by the struct's other `HasField` impls and typed by
    `fix/required_type.rs`'s `required_field_type`, which reads the `Value = T` constraint beside
    the bound on the impl that requires it, and with a similar field or wiring key the program wrote
    found by `fix/near_miss.rs`; a field-type mismatch with `field_type` reading the actual type by
    `DefId`, an abstract-type mismatch with the query layer's `projected_type` normalizing the
    projection for the actual type and `abstract_type_component_marker` recovering the wiring marker
    for its `help`, a missing wiring on the context, a missing dispatch entry on a non-context
    delegation table, a not-a-provider on a non-table type, a provider for other arguments named by
    `fix/other_arguments.rs`, a component wired without its `IsProviderFor` recognized by
    `fix/hand_wiring.rs`, a missing redirect wiring told apart by `is_path_cons`, or a bound);
    `leaf.rs` also drops a routing dead-end, keeping an unmet `DelegateComponent` on the context
    (a missing wiring), on a non-context delegation table (a missing dispatch entry, recognized as a
    separate-table lookup by `is_dispatch_lookup`, the owner a proper part of the parent
    obligation's `Self`, or by owner property via `owner_has_impl_of` for `DelegateComponent`), or
    on a non-table type with no concrete impl of the parent provider trait (a not-a-provider, via
    `owner_has_impl_of` against that trait), and on a non-table type that *does* have one when the
    walk's arguments are fully known and one argument explains the mismatch (a provider for other
    arguments, `is_blanket_dead_end` and `provider_for_other_arguments`), while dropping the
    remaining dead-end (such an owner fed an argument the walk does not know); `reportable.rs` holds
    the two shapes it reads. An unmet `CanUseComponent` or `IsProviderFor` never reaches it, since
    the walk drops both as plumbing before descending.
  - [`data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/data)
    recognizes CGP's extensible-data traits (`is_data_trait`; `is_data_operation`, the ones a call
    to a data operation names, which leave out the field-access traits; `is_data_list_recursion`;
    and `data_derive`, the derive behind each data trait) and reads a partial value back into its
    target and the state of each field or variant (`read_partial`).
  - [`label/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/label)
    turns each obligation into a structured node: `predicate_label.rs` names each consumer/provider
    node off its trait `DefId` and the obligation's arguments (`trait_generics`) as a rustc-free
    `DepNode` variant, dropping the plumbing (an extensible-data list recursion among it) and naming a
    partial value in words (`DepNode::PartialTrait`); `render_ty.rs` resugars a `DefId`-anchored
    `Cons`/`Nil` or `Either`/`Void` self type to `Product![…]`/`Sum![…]`, or (when every element is
    a `Field` and the shared `shape` rules give a spelling) to a `Struct!`/`Enum!` shape, rendering a call-site placeholder as `_` (recursing
    into a tuple so a nested placeholder prints `_` rather than the raw `!N` form); and
    `empty_lists.rs` writes a standalone CGP `Nil` or `Void` as `Product![]` or `Sum![]`, in a
    label and in an ordinary-bound leaf alike.
  - [`query/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/query)
    holds the compiler readers and solver helpers more than one stage uses, and decides no
    resolution, so the resolver's stages and the class detectors import it and it imports none of
    them. `impl_match.rs` holds the one impl match (`match_impl`: the impl's parameters as fresh
    variables, its trait ref normalized and unified with the obligation, a higher-ranked binder
    first instantiated with placeholders via `enter_forall_and_leak_universe`) that the walk, the
    projection-mismatch reader, the wrapper-chain anchor, and the required-type finder share, each
    reading the matched impl's clauses its own way, and reads the walk's dependencies
    (`impl_where_obligations` preferring a concrete-`Self` impl over the delegation blanket and
    solving satisfiable clauses first). `unknowns.rs` carries a call-site unknown across inference
    contexts (`unknowns_to_placeholders`, shared by the walk and the call-site anchor;
    `resolve_fixed_projections` / `try_project_fixed` / `placeholders_to_infer` recovering a stalled
    associated-type projection whose value is *fixed* independent of an unknown input, structurally,
    for any trait and associated type, keeping only a fully-concrete result, so a later pipeline
    stage keyed on an earlier stage's un-normalized output projection is still descended and
    reported on when its input concretizes). `projection_mismatch.rs` finds an unmet associated-type
    projection on the concrete-`Self` impl (`projection_mismatch`/`impl_projection_mismatch`,
    deferring the blanket and preferring a `HasField` projection over any other; `unmet_projection`
    over an impl's instantiated clauses), `holds.rs` asks the solver whether a predicate is
    satisfied, `projected_type.rs` normalizes a projection to the type its owner supplies,
    `written_order.rs` reads an impl's clauses in the order the program wrote them (`written_order`,
    undoing the compiler's move of each associated-type constraint to the front), and
    `misdirected.rs` reads the requirements of a provider impl whose `#[cgp_impl]` header names the
    consumer trait (`misdirected_impl_clauses`). `written_ty.rs` (`expr_written_ty`, the argument
    shapes whose types a call writes, a tuple read partially, its shape recovered with a fresh
    inference variable per unwritten element) and `lower.rs` (`lower_hir_ty`/`instantiate_written`,
    the small syntactic type lowering over cached `type_of`, a literal const argument read through
    the `lit_to_const` query) serve the call-site anchors and the undeclared-trait detector,
    `unify_call_inputs.rs` unifies a call's arguments with the inputs its callee declares (for the
    call-site seed, the data-call chain, the bound-call anchor, and the undeclared-dependency and
    missing-`#[use_provider]` detectors, each pinning and reading back its own parameters), and
    `traits_with_method.rs` finds the traits a call by method name could resolve through, over
    `trait_items_named.rs`, the scan of every trait for an associated item of a name that the
    data-call and provider-call anchors and the undeclared-dependency, missing-`#[use_provider]`,
    and unimported-abstract-type detectors share. `binding.rs` reads the local binding an expression
    names and the type it is declared with, as written (`declared_binding_ty`, for the call-site
    anchors) or as the enclosing signature gives it (`param_declared_input`, following an `async fn`'s
    forwarding `let`, for the undeclared-dependency detector), and `argument_ty.rs` reads an argument
    through that signature for the undeclared-dependency and missing-`#[use_provider]` detectors.
    `enclosing_trait_impl.rs` finds the trait impl a body sits in, and `context_param.rs` the reserved
    `__Context__` parameter of a generated impl. `byte_range.rs` converts a `Span` to the byte range
    the rustc-free span decisions read, and holds `same_range`, which compares two spans' ranges
    whatever their expansion contexts. `keys.rs` renders a wiring key, a redirect path,
    and a provider in the surface forms an entry writes (`describe_key`, `render_path`), and
    `check_impl.rs`, `import_path.rs`, `local_body_exprs.rs`, `local_trait_impls.rs`, and
    `owner_has_impl_of.rs` are the lookups several stages make: the check impls at a caret
    (`check_impls_at`, over the check trait's `CanUseComponent` assertion or another asserting
    supertrait, and an impl's `Self`-type caret), the path a `use` imports an item by, every
    expression of the crate's own bodies (`local_body_exprs`, which the call-site anchors and the
    undeclared-dependency and missing-`#[use_provider]` detectors filter for the calls, or with
    `contexts_at_spans` the expressions, a diagnostic is about, each with its own test), the crate's
    own trait impls (`local_trait_impls`, which the span-matching anchors and the detectors scan,
    each with its own test of the impl), and whether a type is the concrete `Self` of an impl of a
    trait.
  - `query/cgp_item/` holds the structural, `IsProviderFor`-free trait recognition
    (`is_provider_trait` / `provider_blanket_marker` (the `DelegateComponent`-bounded provider
    blanket), `consumer_provider_trait` / `is_consumer_trait`, and `marker_to_consumer`), plus the
    `Symbol!` field-name decode, `is_namespace_lookup_trait` (by the
    single-`Delegate`-associated-type fingerprint plus CGP evidence), and the shared
    `PathCons`/`Nil`/local-ADT and context-ADT recognizers. The class detectors live beside
    `resolve/`, in the driver's
    [`detect/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect)
    module, which imports from the resolver only the query layer, where these recognizers live:
    [`conflict/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect/conflict)
    handles the duplicate-key `E0119` conflict, and
    [`orphan.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/orphan.rs)
    the orphan-rule `E0210`/`E0117` namespace registration, both separate coherence-class transforms
    documented in [The driver](driver.md#reshaping-a-duplicate-key-conflict), and
    [`structural/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect/structural)
    the structural mistakes in a check table or a wiring entry
    ([The driver](driver.md#reshaping-a-structural-mistake)). The macro-lowering detectors sit
    beside them: `undeclared.rs`, `missing_use_provider.rs`, `unimported.rs`, and `requirement.rs`
    for an undeclared dependency ([The driver](driver.md#reshaping-an-undeclared-dependency)), and
    `cgp_impl_misuse.rs` and `uses_misuse.rs` for a wrong component half
    ([The driver](driver.md#reshaping-a-wrong-component-half)), and `wiring_name/` reads a wiring
    entry's names back from the HIR for an unresolved wiring name
    ([The driver](driver.md#reshaping-an-unresolved-wiring-name)). Beside `query/` in `resolve/`,
    `cache.rs` memoizes the walk at every node (keyed on the region-erased obligation and context),
    so a wiring failure re-reported at many sites, or a shared trait, is walked once (see
    [Cached dependency resolution](cached-dependency-resolution.md)).
- [`crates/cargo-cgp-driver/src/emitter/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter):
  the `try_resolve` seam (gated to an unmet-obligation code, `E0271`/`E0277` or a
  method-bounds `E0599`, with a resolution-class `E0599` excluded so the solver never runs on an
  error emitted mid-`clauses_of`) that tries the twelve anchors of `resolve/anchors.rs` in turn (the bound-call,
  by-blanket-trait, and forwarding-entry anchors last, gated to `E0277`) and sends the method probe's "no method named" `E0599`
  (`is_no_matching_item`) and an `E0308` to the data-call anchor alone, and the `transform_resolved`
  mutation it feeds, mapping the rustc code to a `DiagKind` (overridden to the use-site kind for a
  call-anchored resolution), calling `plan_resolved`, and applying the plan to the `DiagInner`,
  falling back to the in-place text rewrite when resolution returns `None`. A final cross-diagnostic
  de-duplication suppresses a re-report of a failure already shown.
- [`crates/cargo-cgp-error-processing/src/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis):
  the rustc-free model and wording, `leaf.rs`/`resolved.rs` (the `Leaf`, `FieldIssue`, `Cause`
  holding a leaf and every path that reaches it, and `Resolved`), `node.rs`/`graph.rs` (the
  structured `DepNode`/`ChainNode` and the `DependencyGraph` that merges and renders their paths;
  see [Dependency-graph rendering](dependency-graph-rendering.md)), the `wording/` directory (the
  coded headers, the `root cause:`/`root causes:` notes with `cause_notes` folding every cause's
  paths into one graph, the leads and their codes, the fix `help`s, and the de-duplication
  `cause_signature`), `coalesce.rs` (`coalesce_underived_fields`, merging several underived fields
  on one struct into a single heading cause), and `plan.rs` (`DiagKind`, `DiagnosisPlan`, the
  unrendered `PendingNote`, and `plan_resolved` with its `categorized_header`), unit-tested in
  [`tests/error_processing/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/diagnosis),
  [`tests/error_processing/coalesce.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/coalesce.rs),
  and
  [`tests/error_processing/graph.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/graph.rs).
- [`crates/cargo-cgp-error-processing/src/tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/tree.rs):
  the `DependencyTree` type and its `cargo tree`-style renderer over `termtree`, the target the
  graph expands into, unit-tested in
  [`tests/error_processing/tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/tree.rs).
- [`crates/cargo-cgp-driver/src/config/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/config):
  the crate and trait-name anchors the resolution matches against.

## Tests

The resolver is exercised end to end by the UI snapshot suite. The fixtures it reshapes live in the
error-class directories under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/), above all
[`checks/check-trait-failure/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure)
(its `fields/`, `field-types/`, `types/`, `providers/`, `generic/`, `resolution/`, `verbosity/`,
`missing-wiring/`, `use-site/`, `use-type/`, and `duplication/` subgroups) and
[`hidden/unsatisfied-dependency/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/hidden/unsatisfied-dependency),
carrying `.cgp.stderr` snapshots of the transformed output. The failure it declines (a use-site
`E0599` on a generic consumer whose dispatch parameter rides in an argument the call does not type
syntactically) pins its fallback (with the method-probe advice stripped) in
[`checks/check-trait-failure/use-site/generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs),
so the two sides together pin both the transform and the decline boundary;
[`checks/check-trait-failure/verbosity/deep_dispatch_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/verbosity/deep_dispatch_chain.rs)
pins a resolved deep dispatch chain, every hop naming its program type in full.
[Testing](testing.md) describes the suite and its bless workflow. The fixtures group by what they
pin.

Each **leaf class** has fixtures for its field, wiring, and redirect shapes:

- `base_area_1`: a genuinely missing field (the worked example).
- `missing_has_field_derive`: a present-but-underived field, with the derive `help`.
- `field_via_deref`: a field on a `Deref` target, with the `help` pointed at the target.
- `field_type_mismatch` and `field_type_mismatch_1`: a matching name with a mismatched type, read
  through a getter and directly via an `#[implicit]` argument.
- `abstract_field_type_mismatch` (under
  [`checks/check-trait-failure/field-types/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/field-types))
  : the same leaf where the *required* type is itself a projection through the context's own wiring
  (`Pool<<App as HasDbType>::Db>`, from a provider reading `&Pool<Db>` under an imported abstract
  type), so the mismatch is between two of the context's own decisions rather than between a
  provider and a struct. Pins the dual rendering: `classify::leaf` normalizes the required type
  alongside the un-normalized form and keeps the reduction only when it differs, so the `[CGP-E004]`
  header and the `[CGP-E112]` leaf both read `` `Pool<<App as HasDbType>::Db>` (`Pool<Postgres>`) ``
  while a concrete requirement stays bare. `abstract_field_type_missing` (under `fields/`) is the
  same requirement on a context that lacks the field, whose help names the field without a type,
  since the required type still holds a projection.
- `abstract_type_mismatch` (under
  [`checks/check-trait-failure/types/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/types)):
  the abstract-type sibling of those two: a context binds `HasScalarType` to `UseType<u32>` while
  its provider pins the same type to `f64` with the `#[use_type(HasScalarType.{Scalar = f64})]`
  equality form, so the trait bound holds and only the projection fails. Pins the generalized
  projection recovery (the walk reports the unmet non-`HasField` projection instead of declining),
  the `[CGP-E005]` header and `[CGP-E116]` leaf, the actual type read by normalizing the projection,
  and the `UseType<…>` `help` the `#[cgp_type]` recognition earns.
- `abstract_type_mismatch_projected`: the same class where the provider pins the abstract type to a
  type that *projects through another one* (`{Transaction = Tx<Db>}`), so the requirement is
  `Tx<<App as HasDbType>::Db>` and the two things in conflict are both the context's own wiring
  decisions. Pins the dual rendering on `[CGP-E005]`/`[CGP-E116]` (the projection followed by what
  it reduces to) and that the `help` uses the reduced form alone, since it names an edit to type. It
  depends on a pin grounding an alias nested in its right-hand side.
- `plain_assoc_type_mismatch`: the negative counterpart, and the pin on that recognition's
  discriminator: the same projection failure on a plain associated-type trait implemented directly
  on the context. It takes the same `[CGP-E005]` class, since the mechanism is the projection rather
  than the trait, but reads `associated type` and carries **no** `help`: there is no wiring entry to
  change, so suggesting `UseType<…>` would name a fix that does not exist.
- `field_type_mismatch_modules`: two `Rectangle` contexts in separate modules with differently-typed
  `height` fields, proving the actual-type query is `DefId`-anchored.
- `basic_missing_wiring`: a `#[uses]` dependency on an unwired component.
- `direct_missing_wiring`: a checked component wired nowhere (a single-node chain).
- `parallel_missing_wiring`: two unwired components, both dependencies of one provider, so the two
  missing-wiring causes share a root and render as one branching note with a `root causes:` heading.
- `transitive_missing_wiring`: a component wired through an *aggregate provider* that the aggregate
  itself does not wire, the `[CGP-E114]` missing-dispatch-entry leaf on a non-context delegation
  table
  (`` missing entry for `BarProviderComponent` in provider `CommonProvider` ``),
  with the whole tree correctly rooted at the checked context.
- `record_field_chain`: a record provider building each field through the context over a recursive
  `Cons`/`Nil` handler (the modular-serialization `DeserializeRecordFields`/`HandleMapEntry` shape),
  whose tree entries also pin the `Cons`/`Nil` → `Struct! { … }` resugaring.
- `sum_variant_chain`: the sum counterpart over a `Sum![u64, f64]` list of bare types, pinning the
  `Either`/`Void` → `Sum![…]` resugaring left as a plain list.
- `enum_variant_chain`: a sum of *named* variants, pinning the `Enum! { Rect(u64), … }` form.
- `enum_variant_shapes_chain`: a sum using every variant shape, pinning each variant's shortest
  spelling (`Empty`, `Rect { w: f64 }`, `Pair(u8, u16)`, `Circle(f64)`).
- `unregistered_prefix_path`, `qualified_prefix_path` (a module-qualified path still folding to a
  clean `@…`), `multi_redirect_missing` (several hops), and `open_missing_type_key`: the
  namespace-redirect variants.
- `redirect_distinct_keys`: two dependencies dispatched along the *same* `open` route for two
  distinct unwired keys (`Left`, `Right`), each redirect the first on its branch. The two redirect
  hops render the same label but are different lookups, so the graph keeps them distinct (keyed on
  the dispatched value): the tree branches to each key's own redirect and missing-wiring leaf rather
  than collapsing both under one shared redirect (see
  [Dependency-graph rendering](dependency-graph-rendering.md)).

Several fixtures pin the **harder mechanics**:

- `parallel_branches`: two independent missing fields under one provider, merged into one branching
  note whose two branches end at the distinct field leaves.
- `many_missing_fields`: six missing fields read through `#[implicit]` arguments, listed and
  branched in the order the arguments are written, under a headline that names the first three and
  counts the rest; `empty_field_struct` and `base_area_2` pin the written order of a getter's fields.
- `deep_nesting`: higher-order providers nested four deep, one long list.
- `dependency_cascade`: a chain of providers each depending on the next, its intermediate consumers
  each a `[CGP-E101]` node.
- `mixed_rust_error`: a CGP tree beside an untouched `E0308`.
- `same_name_components`: two components sharing a marker name in different modules, resolved to
  their own traits (off their `DefId`s) with no cross-over.
- `generic_area_multi`: a three-parameter component, its parameters reattached to the labels from
  the obligation's own arguments.
- `lifetime_component`: a component carrying a *lifetime* parameter (`(Life<'a>, str)` in its check
  entry), the lifetime restored from its `Life<'a>` lift to a region when the consumer obligation is
  rebuilt, the provider label's context read by type position past the leading lifetime, and the
  lifetime kept in each step's trait as `'_` (`` `HasReference<'_, str>` ``).
- `tuple_param_component`: a component whose single parameter is itself a *tuple* type, kept whole
  (`CanFormatPair<(u32, u64)>`) rather than spread into two parameters by the params-slot
  ungrouping.
- `check_providers_layer` (under
  [`checks/higher-order-provider-layer/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/higher-order-provider-layer)):
  a `#[check_providers(...)]` per-layer assertion, matched by the provider-check anchor to its
  generated check impl and walked from the listed provider's obligation into a `[CGP-E002]` block
  whose tree starts at the failing layer. `check_providers_unwired_provider` checks a provider the
  context does not wire at all, `same_name_marker_rename` one whose marker shares its name with
  another component's, and `check_providers_two_components` one provider over two components that
  fail at one caret, each read from its own check impl.
- `ordinary_bound_unsatisfied`: a non-field `f64: Eq` bound whose rustc header is kept over a
  lead-less chain note.
- `constrained_delegate_key` and `pipe_handlers_empty` (under
  [`checks/check-trait-failure/constrained-key/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/constrained-key)):
  a delegation whose `DelegateComponent` impl carries a constrained key that is unsatisfied, so the
  walk descends the delegation impl and bottoms out on its unmet `where`-bound as an ordinary-bound
  leaf. The first is a self-contained dispatcher (`PickFirstProvider<Product![]>`, whose `Nil` list
  has no `PickFirst` impl); the second is the canonical core-CGP form, an empty
  `PipeHandlers<Product![]>` whose `Nil` fails `ComposeProviders`.
  `constrained_delegate_key_empty_sum` is the first's variant counterpart, `Sum![]` for the `Void`
  rustc prints.
- `foreign_getter_missing_wiring`: the money-transfer `UseBasicAuth` shape, where the walk descends
  a request getter's blanket impl into its context-side dependency; the provider's two dependencies
  both reach the one missing `HasCredentialType` wiring, so the graph renders them converging on it
  (the second `(*)`-deduped), under a promoted `CGP-E001` header.
- `diamond_shared_trait`: `CanTop` depends on both `CanLeft` and `CanRight`, which both depend on
  the shared `CanShared` (missing `name`). One root cause reached by two paths, rendered as a
  diamond: the shared subtree drawn in full under the first branch and `(*)`-referenced under the
  second, both branches visible (see [Dependency-graph rendering](dependency-graph-rendering.md)).
- `projected_impl_argument`: two blanket impls of one trait that differ only in a projected
  argument (`Pick<<u8 as Assoc>::Out>` and `Pick<<u16 as Assoc>::Out>`), each requiring a different
  field. The impl match reduces each impl's trait ref before relating it, so the walk takes the
  impl the obligation names and reports its field; relating the unreduced projection would leave it
  a goal for later and take the first impl.
- `higher_ranked_descent`: a recursive provider with a `Self: for<'a> CanEncodeItem<&'a Value>`
  dependency (the `SerializeIterator` shape), resolved through the placeholder instantiation, where
  reaching the trait ref with `skip_binder()` would feed an escaping bound variable into the solver
  and panic rustc.
- `nested_higher_ranked_descent`: the same nested twice through the record machinery (the
  `MessagesArchive` shape), which resolves only because nested higher-ranked hops normalize against
  placeholders.
- `enum_hasfields_lock`: a resolution-class `E0599` emitted mid-`clauses_of`, which the resolver
  must decline rather than run its solver on and re-enter the `DiagCtxt` lock.

The **use-site paths** are pinned by the
[`hidden/unsatisfied-dependency/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/hidden/unsatisfied-dependency)
and
[`checks/check-trait-failure/use-type/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/use-type)
fixtures:

- `missing_dependency` and `unsatisfied_dependency`: a consumer-method `E0599` giving the `CGP-E001`
  header with the method-syntax advice dropped over a `missing field` note.
- `missing_wiring`: a use-site `E0599` whose provider needs an unwired component.
- `ordinary_bound_unsatisfied`: a use-site `f64: Eq`, code kept `E0599`.
- `open_dispatch_use_site`: the dispatch value recovered from the redirect key, so the tree starts at
  `CanEncodeItem<Seq<u64>>` and the headline and note reach the real `@ItemEncoderComponent.u64`
  wiring rather than reporting the internal `PathCons` key as a bogus consumer trait.
- `namespace_join_use_site`: a use-site `E0599` on a namespace-joined context, anchored on the
  `CanGreet` consumer trait from the diagnostic and walked through the namespace's `RedirectLookup`
  to the missing field, with the blanket `__Key__` forwarding skipped.
- `cascade_after_use_site`: the unconditionally-dispatched `E0277` of the
  [call-site anchor](typed-resolution-call-site.md)'s worked example, resolved into one `[CGP-E001]`
  block whose await-site re-report de-duplicates and whose `?`-operator cascade the emitter's gate
  drops (the resolver never takes a `?` error, so the fixture fails without the gate).
- `foreign_context_error_route`: a handler-pipeline call on a context from an upstream crate whose
  error table lacks a route, recovered by the call-site anchor into the `[CGP-E113]` leaf the local
  form reports, rather than rustc's two provider-plumbing errors that never name the route.
- `unrelated_error_before_call`: an `Rc` `Send` error on the line before a failing consumer call
  keeps its own diagnostic, because the call-site anchor matches a call only by the diagnostic's
  primary span.
- `unrelated_error_in_call_argument` and `unrelated_error_in_awaited_argument`: the same `Send`
  error nested in an argument of the failing call, plain and awaited, also keeps its own diagnostic,
  because a span strictly inside an argument is not about the call.
- `cascade_later_stage`: the same dispatch shape but with the missing field read by the *second*
  pipeline stage rather than the first, so the cause sits behind a `ComposeHandlers` stage keyed on
  the first stage's un-normalized `::Output`. Pins the placeholder-fold of a still-unresolved
  clause: the walk descends the later stage instead of dropping it as inference-laden, reaching the
  field the first stage's un-reportable `_: Send` would otherwise have hidden. This is a common
  real-world shape (a multi-stage pipeline whose later stage reads a field the context has not
  wired, behind an earlier stage that consumes the pipeline's own input), and the fixture is the
  self-contained distillation of it.
- `cascade_later_stage_input`: the harder variant of the same shape, where the later stage's only
  cause is a requirement on its **input type** (`Input: AsRef<[u8]>`) and that input is the earlier
  stage's *fixed* output, threaded through a forwarding handler so it resolves through `CanHandle`.
  Folding the stalled projection to a placeholder leaves the requirement an unreportable
  `_: AsRef<[u8]>`; pins the
  [`resolve_fixed_projections`](typed-resolution-walk.md#walking-the-dependency-graph-downward)
  recovery that reduces the earlier stage's fixed output by re-normalizing the projection with the
  unknown input treated as deferrable, so the later stage's `<output>: AsRef<[u8]>` becomes the
  reported cause.
- `cascade_nested_projection`: the three-stage variant of the Hypershell checksum pipeline shape,
  where the later stage's input (an earlier stage's fixed, projection-typed output produced by a
  nested `PipeHandlers`) reaches an **input dispatcher** written as a `UseInputDelegate` table with
  no entry for it. Pins the `[CGP-E114]` missing-dispatch-entry leaf: the cause is an unmet
  `DelegateComponent` on the dispatch *table* rather than the context, which the walk reports rather
  than dropping as plumbing, leading with
  `` missing entry for `Tagged<Bytes>` in provider `SinkHandlers` `` over the
  chain. Hypershell's own dispatchers are `open`-based aggregates, which reach the redirect-wiring
  leaf instead; see [typed-resolution-walk](typed-resolution-walk.md).
- `empty_dispatch_table`: the same missing-dispatch-entry leaf on an **empty** `UseInputDelegate`
  table, the case the owner-property check cannot see (no `DelegateComponent` impl to find). Pins
  the structural `is_dispatch_lookup` recognition: the unmet `DelegateComponent`'s owner is a proper
  part of the parent `UseInputDelegate<EmptySink>` obligation's `Self`, so it is reported regardless
  of the table wiring any other key.
- `consumer_trait_in_provider_impl` and `consumer_trait_in_provider_impl_field_type` (under
  [`lowering/wrong-component-half/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/lowering/wrong-component-half)):
  a provider whose `#[cgp_impl]` header names the consumer trait, beside a missing field or a field
  of the wrong type. Pins the descent into the misdirected impl's requirements: the check resolves
  to the `[CGP-E001]` missing-field or `[CGP-E004]` field-type block the program gives once the
  header is fixed, kept beside the `[CGP-E032]`;
  `consumer_trait_in_provider_impl_call_missing_field` is the missing field reached from a call,
  with no check. `consumer_trait_in_provider_impl_called` is the case with every requirement met,
  where the walk ends at the not-a-provider leaf and the emitter drops the call's error as the
  header's consequence. `consumer_trait_in_inner_provider_impl` puts the misdirected provider
  inside a higher-order provider that also needs a missing field, so the check keeps its block with
  both causes: it is dropped only when every cause is the header's consequence.
- `direct_delegation_missing_key` (under `checks/check-trait-failure/missing-wiring/`): a
  `GreeterComponent -> Bundle` entry into a table that lacks the key, beside a check. Pins the
  forwarding-entry anchor: the compiler's error on the entry's own forwarding bound reads as the
  `[CGP-E001]` block over `[CGP-E114]`, and the unsized-projection error and the check's report
  drop as the same failure. `direct_delegation_missing_key_unchecked` is the same entry with no
  check or call, where the entry's errors are the only report.
- `non_provider_wired` (under
  [`checks/check-trait-failure/providers/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/providers)):
  a type wired where a provider was expected that does not implement the provider trait at all
  (`WrapGreeter<NotAGreeter>` with `NotAGreeter` an ordinary struct, the `money-transfer-api`
  `UseBasicAuth<QueryBalanceRequest>` shape). Pins the `[CGP-E115]` not-a-provider leaf and its
  discriminator against the `cascade_after_use_site` dead-end: `NotAGreeter` has no concrete
  `Greeter` impl (`owner_has_impl_of` false), so it is reported as
  `` `NotAGreeter` is not a provider of `Greeter` `` rather than declining to a
  `[CGP-E002]` block naming the whole `WrapGreeter<NotAGreeter>` pipeline.
- `provider_for_other_context` (under
  [`checks/check-trait-failure/providers/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/providers)),
  with its call form `provider_for_other_context_call` under `hidden/unsatisfied-dependency/`: a
  provider written for `Person` and wired on `Robot`. Pins the `[CGP-E127]` leaf the dead-end
  becomes when the walk's arguments are fully known: `GreetPerson` has a concrete `Greeter` impl,
  for `Person`, so the leaf names the context it takes. `pipe_handlers_stage_mismatch`,
  `pipe_monadic_non_result`, and `promote_ref_owned_input` (under `handlers/`) pin the
  component-argument form, the last from an `E0271`, and `pipe_monadic_non_result` an impl's own
  parameters printed as `_`.
- `hand_delegate_without_is_provider` (under `hidden/unsatisfied-dependency/`): a context wired by a
  hand-written `DelegateComponent` impl, called. Pins the `[CGP-E128]` leaf the delegation step
  gives when its only failing requirement is the context's own `IsProviderFor` and the context has
  none for the component, with the `help` naming the `delegate_components!` entry.
- `call_site_annotated_receiver`: the same anchor's receiver typed by a `let` annotation, its
  initializer a generic call that writes no type.
- `generic_consumer_use_site`: the same anchor's value-argument case: the dispatch parameter
  recovered by signature unification from a written tuple, no tag argument involved, with the
  misleading method-syntax advice dropped.
- `call_site_tuple_input`: a provider that destructures its input on a tuple shape
  (`(CondInput, Rest)`), reached by a call whose tuple argument the code does not type
  (`(Vec::new(), Vec::new())`). Pins the *partial* tuple recovery: the anchor keeps the tuple arity
  (with each unwritten element a placeholder) so the provider's impl matches and the walk reaches
  the field a branch reads, where collapsing the tuple to one flat unknown would leave the impl
  unmatched and decline. This is the shape a branching/comparison DSL interpreter hits, such as a
  real `If<Compare<…>, …>` program reading an unwired field inside its condition.
- `provider_called_directly` and `provider_called_directly_without_error_type` (under
  `hidden/unsatisfied-dependency/`), and `matcher_missing_arm` (under `data/extensible-data/`): a
  provider trait's method called through the provider's own path. Pins the provider-call anchor:
  the provider read off the path, the context and component parameters off the arguments (a
  parameter binding typed from the enclosing signature in `matcher_missing_arm`), and the
  `[CGP-E002]` class, over a stage given another stage's output type (`[CGP-E127]`), a missing
  error-type wiring (`[CGP-E113]`), and a variant never extracted (`[CGP-E121]`).
- `raise_error_unwired_call` and `consumer_bound_call` (under `hidden/unsatisfied-dependency/`): a
  call to a generic function whose own consumer-trait bound the context fails, the context read
  from the turbofish and from a reference argument. Pins the bound-call anchor and its order before
  the by-blanket-trait anchor: `consumer_bound_call`'s tree starts at the bound `CanGreet`, not at
  the getter rustc's notes name. `cgp_fn_where_bound` is its blanket-trait form, the context a
  parameter binding of reference type, and `generic_consumer_bound_reference_binding` pins that
  binding's reading: its consumer takes a parameter, so no other anchor recovers the bound.
- `generic_fn_missing_bound` (under `hidden/unsatisfied-dependency/`): a consumer method called on
  `context: &Context` in `fn run<Context>`, which does not bound `Context` by the consumer. Pins the
  call-site anchor's type-parameter receiver: the `[CGP-E129]` cause and its `help` naming the
  bound, in place of rustc's "use associated function syntax" advice.
- `cgp_fn_use_site`: a direct call to a `#[cgp_fn]` trait method (`app.describe()`) whose context is
  missing a field one composed blanket trait reads. Pins the call-site anchor's *blanket-trait*
  candidate: the called `Describe` is a `#[cgp_fn]`/`#[blanket_trait]` blanket-impl trait, not a CGP
  consumer, so no span-matching anchor recovers it; the anchor finds it by method name, walks
  `App: Describe` to the missing field, and gives the block the `[CGP-E003]` code (the wrapper
  class) rather than declining to rustc's `E0599` with the cause buried under a
  method-probe candidate list. The use-site counterpart of the impl-site
  [`cgp_fn_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/cgp_fn_missing_field.rs).
- `upstream_blanket_trait_use_site`: the `cgp_fn_use_site` shape with the blanket trait defined in
  an *upstream* crate (via `//@aux-build`), the arrangement a library publishing blanket traits
  produces. Pins the foreign reach of `is_blanket_trait`: a locality-only rule would stop the
  `[CGP-E003]` reshaping at the crate boundary and leave rustc's `E0599`, while the CGP-evidence
  rule (`Describe` → `HasName` → `HasField`) reaches it.
- `local_blanket_trait_reached` (under
  [`pass-through/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/pass-through)):
  a local blanket trait bounded only on `Clone`, reached through a wrapper impl and a direct call,
  left as rustc wrote it because its blanket shows no CGP evidence.
- `lookalike_namespace_trait` (same directory): a user trait with a lone `type Delegate` and two
  conflicting impls, left as rustc's `E0119` because no impl shows namespace evidence.
- `cgp_fn_where_bound`: the same `#[cgp_fn]` trait required through a `where` **bound**
  (`fn greet_all<Context: GetName>(…)`) rather than called, so the failure is an `E0277` on the call
  with no method call to read. Pins the bound-call anchor's blanket-trait form: it reads `GetName`
  off `greet_all`'s own bound and the context `App` from the argument `app`, a parameter declared
  `&App`, heading `[CGP-E003]` over the missing-field tree, where raw rustc mangles the field name
  to an unreadable `Symbol<4, Chars<..>>` in a `help`. The bound-call anchor is tried first, so
  this fixture never reaches the by-blanket-trait anchor (`resolve_use_site_blanket_trait`). Its
  decline-boundary sibling is
  [`generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs),
  an `E0599` whose deep blanket-trait bound stays declined because the anchor is gated to `E0277`.
- `cgp_fn_struct_bound`: the same trait required by a **struct's** bound
  (`pub struct Holder<T: GetName>(pub T)`, built as `Holder(app)`), the shape that reaches the
  by-blanket-trait anchor. Pins its current output, which names the wrong owner: the field is
  reported missing on `Holder<T>`, the struct whose definition holds the bound, rather than on `App`
  (see [usability issues](../issues/usability.md#errors-the-tool-misattributes)).
- `use_type_foreign_unsatisfied` and `use_type_nested_unsatisfied`: an unsatisfiable `#[use_type]`
  abstract-type import in a trait definition, recovered by the consumer-trait anchor into a
  `[CGP-E001]` missing-wiring tree instead of leaking generated `__…__` placeholder names. The type
  argument the import is required of carries no wiring, so the consumer step names it plainly
  rather than calling it a context.

The **extensible-data leaf** is pinned by the fixtures of
[`data/extensible-data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/data/extensible-data),
which the [extensible data](../../cgp/errors/data/extensible-data.md) class catalogs:

- `builder_missing_field`, `builder_field_set_twice`, and `matcher_missing_arm_check`: a builder or
  matcher wired behind a check, the field not set, the field set twice, or the variant not extracted
  read off the partial type's markers under `[CGP-E001]`, the last builder step naming the builder in
  words.
- `build_and_merge_extra_field` and `build_and_merge_missing_field`: a merge whose source carries a
  field the target lacks, reached through the descent into `CanBuildFrom` and the builder's
  `BuildField`, the stray field named as a missing field with no add-the-field `help`.
- `upcast_missing_variant`, `downcast_missing_source_variant`, and `upcast_payload_mismatch`: a cast
  on a constructed enum, read by the data-call anchor under `[CGP-E050]`, the missing variant or the
  payload of the wrong type named.
- `build_field_twice`, `build_field_unknown`, `take_field_absent`, and `finalize_build_premature`: a
  builder typed through its `builder()` and `build_field` chain, the field set twice, missing from
  the struct, or not set, the last a "no method named" `E0599` whose chain starts at the finalize.
- `build_from_overlapping_sources` and `build_from_field_not_in_target`: a merge into a builder
  typed after an earlier merge, the field already set or missing from the target.
- `extract_field_twice`, `finalize_extract_early`, and `downcast_on_remainder`: a remainder a
  pattern binds, the variant already extracted (an `E0308`), not extracted, or the remainder given
  where its enum belongs, with the `downcast_fields` `help` and its import.
- `set_optional_on_core_builder`: an optional builder's `set` on a core builder, with the
  `to_optional` `help` and its import.
- `from_variant_wrong_case`, `build_with_default_without_default`, and
  `finalize_with_default_without_default`: type-relative and chained calls, the misspelled variant
  with its near miss, and the `Port: Default` bound an unset field needs.
- `has_fields_bound_without_derive`, `auto_dispatch_missing_derive`,
  `build_from_source_without_has_fields`, and `upcast_source_without_has_fields`: a data trait a type
  lacks, with the derive `help`, the second merging two traits on one enum, the last a "no method
  named" `E0599`.
- `data_operation_name_not_in_scope` (under
  [`pass-through/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/pass-through)):
  calls named like data operations in a module without CGP's traits in scope, left as rustc wrote
  them.
- `from_variant_bound_missing_variant`: a plain function's bound no anchor recovers, keeping rustc's
  headline and pinning the resugaring of the "similar impl" help rustc splits into styled fragments.

The **impl-site and wrapper-chain paths** are pinned by:

- `manual_supertrait_impl`: a wrapper carrying a generic CGP consumer supertrait implemented
  directly on the context (the `CanHandleApiSend` shape), failing at both the impl header `E0277`
  and its forwarding-call `E0599`, both collapsing to one `[CGP-E003]` block.
- `traced_send_wrapper`: an async `Send`-recovery wrapper whose opaque-future `E0271` names no CGP
  construct, traced to the wrapper-headed tree.
- `foreign_wrapper_chain`: a routing trait on a foreign `Box<App>` whose `where`-clause chain
  reaches a CGP consumer two hops down, the cause reached through a projection bound's base trait,
  headed by the `[CGP-E003]` foreign-plain form.
- `cgp_fn_missing_field` (under
  [`checks/check-trait-failure/fields/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/fields)):
  a `#[cgp_fn]` trait asserted through a wrapper (`pub trait CheckFormatName: FormatName {}` +
  `impl CheckFormatName for App {}`) whose blanket-impl supertrait is not a CGP component, pinning
  the `is_blanket_trait` case: the impl-site anchor walks the `#[cgp_fn]` blanket's `where` clause
  (and a `#[uses]`-chained sibling) to the `` missing field `name` `` cause instead of declining to
  rustc's misleading `#[derive(HasField)]` note.
- `symbol_tag_on_tuple_struct_check` (same directory): a provider that requires `HasField<Symbol!("0")>`,
  checked on a tuple struct that derives `HasField`. The classifier reads only a struct with named
  fields as carrying a `Symbol!`-tagged field, so the cause is a missing field, not the underived
  one it would have blamed, and its `help` names the `Index<0>` tag.
- `foreign_context_wrapper_impl`: a local wrapper trait implemented on a context from an upstream
  crate (via `//@aux-build`), reaching the same `[CGP-E113]` missing error route the local form
  reports, because the impl-site anchor accepts a foreign context that carries its own wiring.
- `unrelated_error_in_wrapper_impl`: an `Rc` `Send` error inside a wrapper impl's method body keeps
  its own diagnostic, while the forwarding call to the failing supertrait's method joins the
  `[CGP-E003]` block (`is_about_impl`).
- `unrelated_error_in_forwarding_argument`: the same `Send` error nested in the forwarding call's
  argument keeps its own diagnostic beside the `[CGP-E003]` block, by the call-site anchor's rule.
- `unrelated_error_noted_on_wrapper_impl` and `unrelated_error_noted_on_foreign_wrapper_impl`: an
  unrelated `Send` error whose note lands on the header of a wrapper impl, on a context and on a
  foreign type, keeps its own diagnostic, because the impl-site and wrapper-chain anchors read only
  the primary spans.
- `wrapper_impl_with_failing_bound`: a wrapper impl whose supertrait and own `where` bound fail for
  different causes, each reported on its own caret: the bound read as the consumer obligation it
  names, and the supertrait at the impl's `Self` type.
- `foreign_context_where_bound` and `foreign_context_wrapper_chain`: the same reach for a context
  from an upstream crate (via `//@aux-build`), through a failing bound of an impl's own `where`
  clause and through a wrapper chain's handoff.
- `impl_bound_on_plain_trait` (under
  [`pass-through/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/pass-through)):
  a failing `where Person: Clone` bound on a context left as rustc wrote it, since the bound names
  no CGP consumer trait.

Finally, the leaf wording and the tree renderer are unit-tested over hand-built `Resolved` values,
independently of the compiler:

- [`cargo-cgp-error-processing/tests/error_processing/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/diagnosis):
  the coded headers, the `root cause:` notes, and the fix `help`s.
- [`cargo-cgp-error-processing/tests/error_processing/graph.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/graph.rs):
  the dependency-graph build-and-render (list, branch, diamond, super-root, within-path repeat) as
  `insta` inline snapshots.
- [`cargo-cgp-error-processing/tests/error_processing/tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/tree.rs):
  the `cargo tree`-style renderer.

## Further reading

- The per-stage documents this overview links:
  [anchoring the starting obligation](typed-resolution-anchors.md),
  [the call-site anchor](typed-resolution-call-site.md),
  [walking to the root cause](typed-resolution-walk.md), and
  [the transformed diagnostic](typed-resolution-output.md).
- [The driver](driver.md): the emitter seam this resolver extends, and the trait-renaming text
  rewrite it falls back to (which still recognizes `IsProviderFor`/`CanUseComponent` in rustc's
  output).
- [Error processing](error-processing.md): the rustc-free crate that holds the `Resolved` model, the
  wording, and the fallback post-processing.
- [Check traits](../../cgp/concepts/check-traits.md): why `IsProviderFor`/`CanUseComponent` exist,
  the workaround this resolver is designed to make removable.
- [rustc diagnostic internals](rustc-diagnostic-internals.md): where rustc drops information the
  resolver must recover, and the panic hazards of running compiler code inside the emitter.
- [The error pipeline](error-pipeline.md): where this driver-side transformation sits among the
  pipeline's stages.
- [CGP check-trait failure](../../cgp/errors/checks/check-trait-failure.md): the upstream error
  class the resolver reshapes.
