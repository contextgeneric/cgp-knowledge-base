# Typed resolution: walking to the root cause

The walk descends from the consumer obligation an [anchor](typed-resolution-anchors.md) seeds, along
the wiring's trait obligations, to every terminal unmet bound. [Leaves and
labels](typed-resolution-leaves.md) covers what ends a branch and how it is worded. This document
explains the decisions in the descent that a simpler walk would get wrong.

## Walking the dependency graph downward

For a failing obligation the walk finds the impl that would satisfy it and recurses into each of
that impl's `where` clauses that does not hold. It follows *every* unmet clause because the
next-generation solver stops at the first unmet bound of a conjunction, so a provider needing two
absent fields would otherwise hide one.

The chain it descends is `Ctx: Consumer`, then the routing `Ctx: Provider<Ctx>` (whose label the
tree drops), then `Provider: ProviderTrait<Ctx>`, then that provider impl's own bounds. A provider's
bounds come from its concrete impl, never from `IsProviderFor`. An `IsProviderFor` or
`CanUseComponent` bound beside the real one in a generated blanket only copies those bounds, so it
is dropped before recursion (`is_workaround_plumbing`).

Causes come out in the order the program wrote the clauses, which takes work to recover. The
compiler moves each associated-type constraint (the `Value = u64` of
`HasField<Symbol!("f"), Value = u64>`) to the front by swapping, which scrambles the trait clauses,
and source positions cannot help, because every bound a getter or `#[implicit]` argument generates
carries the macro's call site. `written_order` gives each constrained trait clause its constraint's
place. The order is exact for an impl with no constraint and for one where every bound has one. An
impl mixing the two (a `#[uses]` bound beside implicit arguments) lists its constrained bounds
first.

## Finding the impl that satisfies an obligation

Two rules matter past a flat wiring:

- **A concrete-`Self` impl is preferred over a blanket.** A provider obligation unifies with both
  the provider's own impl and the delegation blanket `impl<P: DelegateComponent> Trait<…> for P`,
  and only the first leads to the cause; the blanket leads to a `DelegateComponent` dead-end. The
  blanket is used only when it is the sole match, as for an obligation whose `Self` is the context.
- **The impl's satisfiable clauses are solved first.** A parameter fixed only by an associated-type
  clause (a record deserializer's `Builder`, pinned by
  `Record: HasOptionalBuilder<Builder = Builder>`) stays a free variable after the trait ref
  unifies. Solving binds it, so the sibling clause that leads to the cause is not dropped as
  inference-laden.

## Recovering a later pipeline stage

A later stage of a pipeline is the case most likely to lose a real cause. A composition such as
`ComposeHandlers<A, B>` requires `B: Handler<Ctx, Code, A::Output>`, so the later stage's input is a
projection through the earlier stage. When a call leaves the pipeline's input unwritten, the walk
holds a [rigid placeholder](typed-resolution-call-site.md), which falsifies `A`'s
`Input: Send`-style bound. So `A`'s impl is rejected, `A::Output` does not normalize, and the clause
reads `Handler<Ctx, Code, _>`. Dropping it would discard every root cause past the first stage.

The walk handles this in two steps:

- **Recover:** `resolve_fixed_projections` re-normalizes each stalled projection with the
  placeholders turned back into inference variables, which makes the blocking bound deferrable
  rather than false. An output type a provider declares independently of its input then comes out
  concrete, and the later stage's bound becomes the reported cause
  ([`cascade_later_stage_input`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_later_stage_input.rs)).
  The result is kept only when fully concrete, so an output that depends on the input falls through.
- **Fold:** otherwise each stray inference variable becomes a rigid placeholder and the walk
  descends anyway, reaching the stage's context-side needs. The
  [placeholder-leaf filter](typed-resolution-output.md#the-root-cause-notes) then keeps a leaf that
  depends on the unknown (`_: Send`) from being reported.

The recovery matches on the projection kind alone, never on an associated-type name or a trait, so
it is not specific to handlers and `Output`. Keep it that way: naming `ComposeHandlers` here would
break every other composition. Both steps are no-ops on a concrete-input walk.

## Re-rooting at another context

A consumer obligation whose `Self` is a *different* context (`Inner: CanCompute` reached while
resolving `Outer`) is re-rooted at that context. A type from another crate counts when it carries
wiring, as an exported context or a `Vec<T>` the checked crate wires does. Without this the subtree
would be labeled and classified against `Outer`, which turns its routing hop into a false step and
its getter leaf into an opaque foreign bound. Re-rooting also lets the node share its
[cache](cached-dependency-resolution.md) entry with `Inner`'s own walk.

## Which obligations the walk follows

The walk descends provider traits, `DelegateComponent`, any obligation whose `Self` is the context,
and CGP's extensible-data traits (those of `cgp-field` and `cgp-field-extra`), whose blanket impls
lead to the presence marker at fault. Everything else is a
[terminal leaf](typed-resolution-leaves.md#the-leaf-shapes). The limit protects a guarantee: an
ordinary bound such as `f64: Eq` must stay the leaf, because a `std` blanket impl that happens to
match (`impl<F: FnPtr> Eq for F`) would otherwise fabricate an `f64: FnPtr` step.

Two foreign bounds are followed anyway, because they reach the context only deeper:

- **A getter or blanket trait on a non-context type whose impl depends on the context**, such as a
  request struct's `HasBasicAuthHeader<Ctx>`. The walk follows only context-side dependencies
  (`is_context_side`), so the real cause surfaces instead of the opaque bound as a second cause.
  This also skips the getter's `HasField` clause on the request, which a plain descent would
  misreport as a missing field. A provider step for another context is not followed, nor is a data
  trait on the foreign type: a `#[cgp_auto_dispatch]` payload lacking its own impl stops at
  `Square: HasArea` rather than descending the unit-context matcher into extractor bounds a plain
  struct cannot meet
  ([`auto_dispatch_missing_variant_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/auto_dispatch_missing_variant_impl.rs)).
- **A same-trait recursion over a type-level list:** a record's `Cons<…>: HandleMapEntry<…>` handles
  later fields through a same-trait bound on its tail. Following only the *same* trait keeps the
  `f64: Eq` guarantee, since a foreign leaf's impl dependency is a different trait.

## An impl whose trait clauses all hold

An unmet obligation whose impl's trait clauses all hold is failing on an associated type.
`Self: Trait<Assoc = T>` desugars into two predicates and the walk follows only the trait half, so
the resolver searches the impl for an unmet projection (`projection_mismatch`) and ends the branch
there. A `HasField` value is the field-type mismatch; any other is the
[abstract-type mismatch](typed-resolution-output.md#the-root-cause-notes). `HasField` wins when an
impl carries both, because its leaf names a field to fix.

This search prefers the concrete impl too, since the delegation blanket carries no projection. A
blanket is deferred, not skipped: a getter trait's only impl is a blanket, and it carries the
projection. A branch with no projection yields nothing, unless the failing scaffolding is itself the
cause, the
[wiring-without-`IsProviderFor` leaf](typed-resolution-leaves.md#the-wiring-without-isproviderfor-leaf).

## A provider whose header names the consumer trait

A provider whose `#[cgp_impl]` header names the consumer trait (`[CGP-E032]`) has no provider-trait
impl, so it would end at the not-a-provider leaf, which is only the header's consequence. But its
impl still states what it needs, and a need that fails outlives the header fix. So
`misdirected_impl_clauses` reads that impl's clauses with the obligation's context in place of
`__Context__`, when the provider is local, has no provider-trait impl, and has exactly one such impl
with no other type parameter. The walk then reports the cause the program gives once the header is
fixed, and the emitter keeps it beside the `[CGP-E032]`. When every clause holds, the emitter drops
the not-a-provider leaf.
[`consumer_trait_in_provider_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl.rs)
and its siblings pin a missing field, a call with no check, a wrong field type, and the header
alone.

## Crossing inference contexts

A stray variable from one `InferCtxt` panics another, so these rules are not optional
([hazard](rustc-diagnostic-internals.md#contaminating-one-inference-context-with-anothers-variables)):

- **No `SelectionContext`.** It asserts against the next-generation solver, so the walk unifies with
  `fresh_args_for_item` instead.
- **Predicates cross clean.** Each matched impl's predicates are instantiated, normalized, and
  region-erased before they enter the fresh context that checks them.
- **Never a bare `skip_binder()` on the obligation.** A higher-ranked obligation such as
  `Self: for<'a> CanSerializeValue<<&'a Value as IntoIterator>::Item>` would relate an escaping
  bound variable and hit the
  [generalizer panic](rustc-diagnostic-internals.md#feeding-escaping-bound-variables-to-inference-has_escaping_bound_vars).
  The binder is entered with placeholders rather than inference variables, because a projection
  through the bound lifetime normalizes against a rigid region but stalls against an inference one.

## Ending a branch early

The walk does not descend an obligation holding a `{type error}`. Such a type unifies with anything,
so following it could only invent a cause or a loop, and the earlier error is the one to fix
([`type_error_in_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/type_error_in_wiring.rs)).

Two guards bound the descent. A **cycle guard** stops a branch when an obligation reappears among
its ancestors. `MAX_DEPTH` is the backstop for a *divergent* wiring whose obligations grow without
repeating
([`divergent_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring.rs)).
Do not lower the cap casually: one logical hop expands to several frames, so a deeply nested data
type reaches its cause tens of frames down. Do not raise it casually either: the solver runs at
every frame, so the cap bounds a divergent wiring's work.

Each cut records why it stopped (`SubResult.cut`), and the driver words an `E0275` wiring overflow
from that reason
([Diagnostic reshapes](diagnostic-reshapes.md#naming-the-traits-behind-a-component-marker)); an
overflow whose walk is not cut keeps rustc's wording. These points are worth attention:

- A provider step is named only when a wiring entry chose that provider, so a provider inside a
  higher-order provider is never named.
- A lookup can grow in its `Self` type (`Vec<u32>: CanShow`, then `Vec<Vec<u32>>: CanShow`), which
  reaches the cap through re-rooting
  ([`divergent_self_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_self_wiring.rs)).
- Where two branches are cut differently the cycle wins, since it explains the failure more exactly
  ([`cycle_beside_growing_lookup`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cycle_beside_growing_lookup.rs)).

The guards also decide what may be cached: a subtree they cut is never stored, as
[Cached dependency resolution](cached-dependency-resolution.md) explains.

## Further reading

- [Typed root-cause resolution](typed-root-cause-resolution.md): the pipeline overview and the
  consolidated tests and source catalogs.
- [rustc diagnostic internals](rustc-diagnostic-internals.md): the panic hazards behind the
  inference-context rules.

## Tests

The fixtures are cataloged in the parent document's [Tests](typed-root-cause-resolution.md#tests).

## Source

- [`resolve/walk/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/walk):
  the recursion, and what it walks into.
- [`resolve/query/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/query):
  the solver queries the walk and the classifiers share.
