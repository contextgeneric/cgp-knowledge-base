# Typed resolution: walking to the root cause

This document covers the descent at the heart of the driver's
[typed root-cause resolution](typed-root-cause-resolution.md): from the consumer obligation an
[anchor](typed-resolution-anchors.md) seeds, down the wiring's trait obligations to every terminal
unmet bound. [Leaves and labels](typed-resolution-leaves.md) covers what ends a branch and how each
leaf and hop is worded, and [the emitter](typed-resolution-output.md) turns the result into the
dependency tree.

## Walking the dependency graph downward

From the anchored consumer obligation the resolver walks *down* the wiring's trait obligations,
because the tree shows the transitive path to each root cause, not only the root. For a failing
obligation it finds the impl that would satisfy it, takes that impl's `where`-clause obligations as
its direct dependencies, and recurses into just the ones that do **not** already hold. A satisfied
dependency (an already present field, a wired provider that checks out) is pruned. Following *every*
unmet dependency, not only the first, surfaces independent causes as **separate** paths: the
next-generation solver short-circuits a conjunction at its first unmet bound, so a provider needing
two absent fields would otherwise hide one.

The walk reads an impl's `where` clauses in the order the program wrote them, so the causes, and the
tree's branches, come out in that order. The compiler does not keep that order: it moves each
associated-type constraint (the `Value = u64` of `HasField<Symbol!("f"), Value = u64>`) to the front
by swapping it with the clause there, which scrambles the trait clauses behind it. Source positions
cannot restore the order either, because every bound a getter or an `#[implicit]` argument generates
carries the macro's call site. The constraints keep their written order, so `written_order` gives
each trait clause that carries one its constraint's place and leaves the others in the compiler's
order. That is exact for an impl with no constraint, and for one whose every bound carries one, as a
getter's and a provider's with only implicit arguments do; an impl mixing the two (a `#[uses]` bound
beside implicit arguments) lists its constrained bounds first.

The descended chain is the real one: `Ctx: Consumer`, then `Ctx: Provider<Ctx>` (the delegation
routing, whose label the tree drops), then the delegate's `Provider: ProviderTrait<Ctx>` (the real
wired provider), then that provider impl's own `where` bounds, then the leaf. The provider's bounds
are read from its *own* concrete impl, which is why `IsProviderFor` is never needed: it carried a
copy of exactly these bounds only for rustc's benefit. An `IsProviderFor` or `CanUseComponent`
obligation that appears *beside* the real one in a generated blanket (the provider blanket bounds
`P: IsProviderFor<…>` right next to `P::Delegate: ProviderTrait<…>`) is dropped from a node's
dependencies by `is_workaround_plumbing` before recursion, so the walk follows the real provider
obligation rather than the marker's copied bounds.

## Finding the impl that satisfies an obligation

Finding *which* impl satisfies an obligation takes two rules past a flat wiring. First, a
provider obligation such as `DeserializeRecordFields: ValueDeserializer<…>` unifies with *two*
impls: the provider's own `#[cgp_provider]` impl and the CGP delegation blanket
`impl<P: DelegateComponent> ValueDeserializer<…> for P`. Only the concrete-`Self` impl's
`where`-clauses lead to the real cause (the blanket's lead to a
`DeserializeRecordFields: DelegateComponent` dead-end, since a leaf provider does not delegate), so
a **concrete-`Self` impl is preferred** over a param-`Self` blanket, the blanket used only when it
is the sole match (as for an obligation whose `Self` *is* the context). Second, an impl may carry a
**parameter fixed only by an associated-type `where`-clause** (a record deserializer's `Builder`,
pinned by `Record: HasOptionalBuilder<Builder = Builder>`) that stays a free inference variable
after the trait ref unifies. The walk registers and **solves the impl's satisfiable clauses first**,
binding such a parameter, so the sibling clause that carries it (the branch to the cause) is not
dropped as inference-laden.

## Recovering a later pipeline stage

A clause the impl match leaves genuinely unconstrained is the subtle case, and the one that matters
most is a **later stage of a pipeline keyed on an earlier stage's output type**. Two pieces of
background make it concrete.

An *associated-type projection* is a type written `<T as SomeTrait<…>>::Assoc`: not named directly,
but computed from a trait impl. The solver *normalizes* it to a real type by selecting the impl of
`SomeTrait` for `T` and reading off the value that impl declares for `Assoc`, which requires the
impl to actually apply: its `where` clauses must hold. CGP's
[handler family](../../cgp/concepts/handlers.md) composes computations into pipelines, and a
composition provider wires each stage's *input* to the previous stage's *output type*, which is
exactly such a projection. Its archetype `ComposeHandlers<ProviderA, ProviderB>` (introduced under
[the failure shape](typed-resolution-call-site.md#the-failure-shape-wiring-that-matches-unconditionally))
has two asymmetric dependencies: `ProviderA: Handler<Ctx, Code, Input>` on the pipeline's own input,
and `ProviderB: Handler<Ctx, Code, ProviderA::Output>` on whatever the first stage *produces*. Here
`ProviderA::Output` is the projection. The handler trait's associated type happens to be named
`Output`, but nothing below turns on that name.

The problem appears when the pipeline's input is unknown. When the walk's own input is a
[call-site placeholder](typed-resolution-call-site.md) (a rigid stand-in for a call argument the
code did not type), `ProviderA`'s own `where` clause is *false* against it (a rigid placeholder
satisfies no `Input: Send`-style bound), so the solver rejects `ProviderA`'s impl and
`ProviderA::Output` cannot normalize. The next-generation solver leaves it a fresh inference
variable, so the `ProviderB` clause reads as `Handler<Ctx, Code, _>`. Dropping it as inference-laden
would silently discard **every root cause living in a stage past the first**: a bound a later stage
places on the value the earlier stage feeds it, which is where a great many real pipeline mistakes
sit.

So the walk first tries to **recover** the earlier stage's output rather than give up on it, because
that output type is very often *fixed* (declared by the provider independently of its input) and
stalled only because the placeholder falsified an unrelated `where` clause.
`resolve_fixed_projections` re-normalizes each stalled projection in a fresh `InferCtxt` with the
placeholders turned back into ordinary inference variables (`placeholders_to_infer`, the inverse of
`unknowns_to_placeholders`). An inference variable makes the blocking bound *deferrable* rather than
false, so the solver commits to the sole impl candidate and reads off the associated type it
declares. The recovered type is kept only when it comes out **fully concrete** (no inference
variable or placeholder left, and no longer an alias), so an output that genuinely depends on the
input never concretizes and falls through to the fold below; and since the seed obligation is still
gated on actually failing, a recovered concrete input can never fabricate a cause. With the earlier
stage's output recovered, the later stage's input becomes that concrete type and the bound it fails
becomes the reported root cause. An example is an `AsRef<[u8]>` requirement a byte-consuming stage
places on a producing stage whose output type is not a byte slice, the shape
[`cascade_later_stage_input`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_later_stage_input.rs)
pins.

The step is **structural**: it recovers `<T as SomeTrait<…>>::Assoc` for *any* trait and *any*
associated type, at any argument position and to any depth (a three-stage pipeline nests one stage's
output projection inside the next). It matches on the projection kind alone and never on an
associated-type name, trait, or `DefId`. `ComposeHandlers`'s `Output` is only the shape that
motivated it.

When a stalled projection *cannot* be recovered this way, because its value genuinely depends on the
unknown input, the walk falls back to **folding each stray inference variable into a rigid
placeholder** (the same `unknowns_to_placeholders` the call-site anchor seeds unknown call arguments
with) and descends the stage anyway. The placeholder is an unknown the walk resolves *around*: it
reaches `ProviderB`'s context-side dependencies (a `Self: HasField` a later stage reads), while the
[placeholder-leaf filter](typed-resolution-output.md#the-root-cause-notes) keeps any leaf that
genuinely depends on the unknown input (`_: Send`) from being reported. The recovery is a no-op
when a clause carries no placeholder and the fold when it carries no stray inference variable (the
ordinary concrete-input walk, where each stage's projection normalizes to a real type), so only the
unknown-input case is affected.

## Re-rooting at another context

One descent step is not about the root context at all. A **cross-context** consumer obligation, one
whose `Self` is a *different* context (`Inner: CanCompute` reached while resolving `Outer`, the
shape where one context's wiring depends on a concrete other context), is re-rooted at that context
before it is walked. A type from another crate counts when it carries wiring, as a context a library
exports does, or a `Vec<T>` the checked crate wires. The node and everything below it are labeled
and classified against `Inner`, not `Outer`. So it reads as a consumer node `for context Inner`, its
delegation-routing hop is recognized as routing and dropped, and its getter leaf decodes to a
missing field rather than an opaque foreign bound. Re-rooting also keys the node identically to
`Inner`'s own walk, so the two share the [cache](cached-dependency-resolution.md). Without it, the
descent would carry the outer root context down and mislabel the whole foreign-context subtree.

## Which obligations the walk follows

The walk descends only what can lead to a wiring cause, which keeps the tree honest. The descent
follows only the CGP wiring vocabulary (any provider trait, where a `ProvideFoo: Foo<App>` bound
routes on to the provider's own dependencies; `DelegateComponent`; and any obligation whose `Self`
is the context, covering its consumer, getter, and blanket traits) and CGP's **extensible-data
traits** (every trait the `cgp-field` and `cgp-field-extra` crates define: the builders, extractors,
and casts), and treats everything else as a
[terminal leaf](typed-resolution-leaves.md#the-leaf-shapes). A data operation's blanket impl leads
to the presence-marker bound that says which field or variant is at fault, so the walk descends it
the way it descends a provider. It deliberately does *not* follow `IsProviderFor`/`CanUseComponent`,
which are dropped as plumbing above.

A bound on a foreign type is normally a leaf, but two are exceptions the descent *does* follow, both
for the same reason: they reach the context only deeper. The first is a **getter or blanket trait on
a non-context type whose satisfying impl depends on the context**, such as a request struct's
`HasBasicAuthHeader<Ctx>`, whose `#[cgp_auto_getter]` blanket impl requires `Ctx: HasPasswordType`.
There the walk looks into that blanket impl and follows only its **context-side dependencies** (a
provider trait, a `DelegateComponent`, or an obligation on the context, as `is_context_side`
decides; never an extensible-data trait, which is about the foreign type itself), so the real cause
on the context surfaces (and de-duplicates with the same cause reached down another branch) instead
of the opaque `Request: HasBasicAuthHeader<Ctx>` bound being reported as a second, misleading root
cause. Following only context-side dependencies preserves the `f64: Eq` guarantee (a foreign
`f64: FnPtr` step is not context-side, so it is never followed), and it also skips the getter's own
`Ctx::Assoc`-typed `HasField` clause on the request, which is present but a projection mismatch a
plain descent would misreport as a missing field. A provider step that belongs to another context is
not context-side, so it is not followed either, nor is a data trait on the foreign type. The case
both matter for is a dispatch payload: a `#[cgp_auto_dispatch]` trait's blanket impl implements the
trait for every type, by running a matcher with the unit context, so a payload that lacks its own
impl (`Square: HasArea`) matches the blanket, whose dependencies are that matcher and the payload
being an extensible enum (`HasExtractor`, a data trait). Neither is about the context, so the walk
stops at `Square: HasArea`, the payload's missing impl, rather than descending the matcher into the
extractor bounds a plain struct cannot meet
([`auto_dispatch_missing_variant_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/auto_dispatch_missing_variant_impl.rs)).
The second is a **same-trait recursion over a type-level list**: a record's field list
`Cons<Field<.., V0>, Cons<Field<.., V1>, Nil>>: HandleMapEntry<.., Ctx, ..>` handles its head field
here but its later fields through the **tail** `Cons<.., Nil>: HandleMapEntry<..>`, a same-trait
bound on another foreign list node. Following a same-trait recursion lets the walk reach the field
whose dependency is the real cause; following only the *same* trait keeps the `f64: Eq` guarantee,
since a foreign leaf's `impl` dependency is a *different* trait.

## An impl whose trait clauses all hold

An obligation whose satisfying impl's trait-clause
`where`-obligations **all hold**, yet is itself unmet, is failing for an associated-type mismatch
the trait-clause walk cannot see: `Self: Trait<Assoc = T>` desugars into *two* predicates, and the
walk follows only the trait half, so a satisfied `Ctx: HasErrorType` beside a failing
`<Ctx as HasErrorType>::Error == AppError` looks, to the trait-clause walk, like an impl with
nothing wrong. The resolver therefore looks among that impl's own predicates for an unmet
**projection** (`projection_mismatch`) and completes the branch with that projection's own trait
ref, tagging the path with the required type. Two leaf shapes come out of it, differing only in
which trait the projection is on: a `HasField` value (`<Ctx as HasField<Symbol!("f")>>::Value == T`,
a field present with the wrong type) renders as the field-type mismatch, and any other associated
type renders as the [abstract-type mismatch](typed-resolution-output.md#the-root-cause-notes), whose
*actual* side is read by normalizing the projection rather than by reading a struct field. A
`HasField` projection wins when an impl carries both, since a field's value type is the more
specific classification and the one whose leaf names a struct field to fix.

The projection search *also* prefers the concrete-`Self` impl over the delegation blanket
(`projection_mismatch` / `impl_projection_mismatch`): the projection lives on the provider's own
impl, and matching the blanket first, which carries no projection, would wrongly report no mismatch.
But a getter trait whose *only* impl is a blanket (`impl<C: HasField<..>> HasName for C`) still has
its projection read from that blanket, so a blanket is deferred, not skipped outright. A branch with
no such projection yields nothing and declines to the fallback, unless the failing scaffolding is
itself the cause, the
[wiring-without-`IsProviderFor` leaf](typed-resolution-leaves.md#the-wiring-without-isproviderfor-leaf).

## A provider whose header names the consumer trait

Before a provider-trait obligation reaches the
[not-a-provider leaf](typed-resolution-leaves.md#the-leaf-shapes), the walk checks for a provider
whose `#[cgp_impl]` header names the component's consumer trait where the provider trait belongs,
the mistake `[CGP-E032]` reports. Such a provider has no impl of the provider trait, so the
obligation fails as if it were no provider at all, a consequence of the header. But its impl still
states what the provider needs from the context, and a need that fails is a separate mistake that
outlives the header fix. So when a local provider has no impl of the provider trait, and exactly one
impl of the paired consumer trait on it carries the `__Context__` parameter `#[cgp_impl]` inserts
and no other type parameter, `misdirected_impl_clauses` reads that impl's clauses with the
obligation's context in place of `__Context__`. The walk descends the ones that fail, or reports the
impl's unmet projection, and a missing field's required type is read off the same impl. The cause is
then the one the program gives once the header names the provider trait, and the emitter keeps it
beside the `[CGP-E032]`. When every clause holds, the obligation ends at the not-a-provider leaf,
which the emitter drops as the header's consequence. Four fixtures pin the outcomes: a missing
field at a check
([`consumer_trait_in_provider_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl.rs)),
the same at a call with no check
([`consumer_trait_in_provider_impl_call_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl_call_missing_field.rs)),
a field of the wrong type
([`consumer_trait_in_provider_impl_field_type`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl_field_type.rs)),
and the header alone
([`consumer_trait_in_provider_impl_called`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl_called.rs)).

## Crossing inference contexts

The walk crosses inference-context boundaries carefully, because a stray variable from one
`InferCtxt` panics another. It finds the satisfying impl by unifying with `fresh_args_for_item`
rather than through `SelectionContext` (which asserts against the next-generation solver the driver
runs under), and each matched impl's predicates are instantiated, normalized, and region-erased
before they cross into the fresh inference context that checks whether they hold. That avoids the
cross-context contamination hazard in
[rustc diagnostic internals](rustc-diagnostic-internals.md#contaminating-one-inference-context-with-anothers-variables).
The obligation being matched crosses the same way: its binder is instantiated with **placeholders**
(via `enter_forall_and_leak_universe`) before it is related, never reached through a bare
`skip_binder()`. A **higher-ranked** obligation makes this essential: the modular-serialization
example's `SerializeIterator` carries
`Self: for<'a> CanSerializeValue<<&'a Value as IntoIterator>::Item>`, and reaching its trait ref
with `skip_binder()` would relate a term with an escaping bound variable and hit the
[generalizer panic](rustc-diagnostic-internals.md#feeding-escaping-bound-variables-to-inference-has_escaping_bound_vars).
Placeholders rather than fresh inference variables are also what let a *nested* higher-ranked hop
resolve: a projection through the bound lifetime (`<&'a Value as IntoIterator>::Item`) normalizes
deterministically against a rigid placeholder region but stalls against an unconstrained inference
region. The instantiation is a no-op for an ordinary binder-free obligation, so only the
higher-ranked case changes.

## Ending a branch early

The walk does not descend an obligation that holds a `{type error}`, the type rustc puts where an
earlier error left a name unresolved. Such a type unifies with anything, so following it could only
invent a cause (a `{type error}: Debug` bound) or a loop, and the earlier error is the cause to fix
([`type_error_in_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/type_error_in_wiring.rs)).

Two safeguards keep the descent bounded. A **cycle guard** stops a branch as soon as an obligation
reappears among its own ancestors (a `UseContext` loop routes `Ctx: Consumer` straight back to
itself), so a cyclic wiring bottoms out at its first repeat rather than spinning. The depth cap
`MAX_DEPTH` is the backstop for what the guard cannot catch: a *divergent* wiring whose obligations
keep growing without ever exactly repeating
([`divergent_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring.rs)).
The cap is set well above a genuine chain's depth (each logical hop expands to a consumer
obligation, the delegation-routing provider obligation, a `RedirectLookup`, the real provider
obligation, then the next consumer, so a deeply nested data type reaches its root cause only tens of
frames down), but not arbitrarily high, because the walk re-runs the solver at every frame, so the
cap also bounds a divergent wiring's worst-case work.

Each cut records why it stopped, on the sub-result it returns (`SubResult.cut`), and the reason
rides up to the root. A repeat is a cycle, recorded with the provider step that requires the
repeated obligation; the cap is a lookup that grows, recorded with its first larger requirement (the
first obligation that restates an earlier one's trait with other arguments, its `Self` type
included) and the provider step that requires it. A lookup that grows in its `Self` type
(`Vec<u32>: CanShow`, then `Vec<Vec<u32>>: CanShow`) reaches the cap through the cross-context
re-rooting above
([`divergent_self_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_self_wiring.rs)).
A provider step is kept only when a wiring entry chose that provider, so a provider inside a
higher-order provider is never named. Where two branches are cut differently, the cycle wins, since
it explains a lookup that never resolves more exactly
([`cycle_beside_growing_lookup`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cycle_beside_growing_lookup.rs)).
The driver words an `E0275` wiring overflow from this reason (`walk_overflow` seeds the walk, and
[Diagnostic reshapes](diagnostic-reshapes.md#naming-the-traits-behind-a-component-marker) applies
it), and leaves an overflow whose walk is not cut in rustc's wording.

The descent is memoized at every node, so a distinct obligation reached from many sites or many
branches is resolved once and reused; the cycle guard and `MAX_DEPTH` cut above are what decide
whether a subtree is complete enough to cache. That mechanism (the node key, the incomplete-subtree
flag, and the reachable-set reuse check) is
[Cached dependency resolution](cached-dependency-resolution.md).

## Further reading

- [Typed resolution: leaves and labels](typed-resolution-leaves.md): what ends a branch, and how
  each leaf and hop is worded.
- [Typed root-cause resolution](typed-root-cause-resolution.md): the pipeline overview, its
  boundaries, and the consolidated tests and source catalogs.
- [rustc diagnostic internals](rustc-diagnostic-internals.md): the panic hazards the walk's
  inference-context discipline exists to avoid.

## Tests

The walk's mechanics are pinned by parallel branches, deep nesting, higher-ranked descents, the
mid-`clauses_of` decline, and the stalled-projection recoveries. The consolidated catalog, one entry
per pinned behavior, lives in the parent document's
[Tests](typed-root-cause-resolution.md#tests) section.

## Source

- [`crates/cargo-cgp-driver/src/resolve/walk/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/walk):
  the descent: `leaves/` (the recursion, one module each for its entry points, the per-node
  descent, the overflow step, the context-wiring checks, and the result builders) and
  `vocabulary.rs` (what it walks into, and which dependencies a foreign bound is followed into).
- [`crates/cargo-cgp-driver/src/resolve/query/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/query):
  the solver queries the walk and the classifiers share: `impl_match.rs` (the impl match and its
  dependencies), `unknowns.rs` (placeholders and stalled projections), `projection_mismatch.rs` (the
  unmet projection an impl carries, `HasField` or otherwise), `holds.rs` (the solver query),
  `projected_type.rs` (the normalization that reads the type an owner supplies for a projected
  associated type), `written_order.rs` (the order an impl's clauses are read in), `misdirected.rs`
  (the requirements of a provider impl whose `#[cgp_impl]` header names the consumer trait), and
  `owner_has_impl_of.rs` (whether a type is the concrete `Self` of an impl of a trait).

The per-file map of the whole resolver lives in the parent document's
[Source](typed-root-cause-resolution.md#source) section.
