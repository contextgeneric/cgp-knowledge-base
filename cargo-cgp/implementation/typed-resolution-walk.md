# Typed resolution: walking to the root cause

This document covers the descent at the heart of the driver's
[typed root-cause resolution](typed-root-cause-resolution.md): from the consumer obligation an
[anchor](typed-resolution-anchors.md) seeds, down the wiring's trait obligations to every terminal
unmet bound, and the decoding, classification, and rendering that turns each terminal into a leaf of
the dependency tree [the emitter emits](typed-resolution-output.md).

## Walking the dependency graph downward

From the anchored consumer obligation the resolver walks *down* the wiring's trait obligations,
because the tree shows the transitive path to each root cause, not only the root. For a failing
obligation it finds the impl that would satisfy it, takes that impl's `where`-clause obligations as
its direct dependencies, and recurses into just the ones that do **not** already hold. A satisfied
dependency (an already present field, a wired provider that checks out) is pruned. Following *every*
unmet dependency, not only the first, is what surfaces independent causes as **separate** paths: the
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
obligation rather than the marker's copied bounds. It would keep working unchanged if
`IsProviderFor` were removed from the generated code entirely.

Finding *which* impl satisfies an obligation is two subtleties deep past a flat wiring. First, a
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
genuinely depends on the unknown input (`_: Send`) from being reported. Both the recovery and the
fold are a no-op when a clause carries no placeholder (the ordinary concrete-input walk, where each
stage's projection normalizes to a real type), so only the unknown-input case is affected.

One descent step is not about the root context at all. A **cross-context** consumer obligation, one
whose `Self` is a *different* local context (`Inner: CanCompute` reached while resolving `Outer`,
the shape where one context's wiring depends on a concrete other context), is re-rooted at that
context before it is walked. The node and everything below it are labeled and classified against
`Inner`, not `Outer`. So it reads as a consumer node `for context Inner`, its delegation-routing hop
is recognized as routing and dropped, and its getter leaf decodes to a missing field rather than an
opaque foreign bound. Re-rooting also keys the node identically to `Inner`'s own walk, so the two
share the [cache](cached-dependency-resolution.md). Without it, the descent would carry the outer
root context down and mislabel the whole foreign-context subtree.

A branch ends at a **terminal leaf**, and which obligations count as terminal is what keeps the tree
honest. The descent follows only the CGP wiring vocabulary (any provider trait, where a
`ProvideFoo: Foo<App>` bound routes on to the provider's own dependencies; `DelegateComponent`; and
any obligation whose `Self` is the context, covering its consumer, getter, and blanket traits) and
CGP's **extensible-data traits** (every trait the `cgp-field` and `cgp-field-extra` crates define:
the builders, extractors, and casts), and treats everything else as a leaf. A data operation's
blanket impl leads to the presence-marker bound that says which field or variant is at fault, so the
walk descends it the way it descends a provider. It deliberately does *not* follow
`IsProviderFor`/`CanUseComponent`, which are dropped as plumbing above. The leaf shapes are:

- An unmet **`HasField`** is the field leaf.
- An unmet **`DelegateComponent<Marker>` on the context** is the missing-wiring leaf: the context
  delegates that component to no provider. The exception is an entry that forwards the key to
  another table (`GreeterComponent -> Bundle`), which the context does carry: its impl's
  `where Bundle: DelegateComponent<GreeterComponent>` bound is what fails, so the walk descends into
  that lookup and reports the missing-dispatch-entry leaf on `Bundle`
  ([`direct_delegation_missing_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/direct_delegation_missing_key.rs)).
- An unmet **`DelegateComponent<PathCons<…>>`**, whose key is a redirect path rather than a bare
  marker, splits by owner. On the context it is the missing-*redirect*-wiring leaf (`[CGP-E113]`),
  named by its whole path. On any other type it is the missing-dispatch-entry leaf below, since the
  lookup ran in an aggregate provider that `open`s the component in its own table; the path is kept
  whole as that leaf's key. A redirect appends the component's parameters to its path, so a lookup
  recovered from a call whose input is inferred ends in a placeholder segment; on the context the
  leaf drops that trailing run and names the path the programmer can wire
  (`@HandlerComponent.Missing`, from
  [`pipeline_unhandled_code`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/pipeline_unhandled_code.rs)).
  The trimmed leaf claims the context has no entry under that path for any value of the unknown, so
  it is kept only when the solver, given an inference variable in place of each placeholder, finds
  that the lookup can hold for none. An `open` error table that routes `String` can serve an
  unknown error type, so its lookup is not reported
  ([`placeholder_error_route_leaf`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/placeholder_error_route_leaf.rs)).
- An unmet **`DelegateComponent<Key>` on a *non-context* delegation table** is the
  missing-dispatch-entry leaf (`[CGP-E114]`): the owner is a provider that delegates (an aggregate
  provider missing a component wiring, or a `UseDelegate`/`UseInputDelegate` table missing a branch
  for the type it dispatches on, a `Code` fragment or an `Input` value's type), and it does not wire
  this key. It is told apart from a higher-order-provider dead-end (dropped, below) two ways, so it
  is reported when *either* holds (`is_reportable_leaf`, over `is_dispatch_lookup` and
  `owner_has_impl_of`, in `classify/reportable.rs`):
  - **structurally**, when the obligation is a *dispatch lookup into a separate table*: its owner is
    a proper part of the parent obligation's `Self`, as `Components` is of `UseDelegate<Components>`
    / `UseInputDelegate<Components>` (or any custom dispatcher that holds its table as a parameter).
    Such a `where`-clause is unambiguously a table lookup, so an unmet one is a missing entry
    *regardless of whether that table wires any other key*. This is what reaches an **empty**
    dispatch table.
  - **by owner property** otherwise (the generic-blanket case, where the owner *equals* the parent
    `Self`): the owner wires at least one other key, i.e. carries a `DelegateComponent` impl, and
    has no concrete impl of the parent provider trait. This is the aggregate-provider case, where
    the blanket keys on the provider itself so no separate-table structure is visible. An owner with
    its own impl of the trait can never wire the trait's key as well, since the blanket and the
    impl would overlap, so reaching its blanket means that impl did not unify: the dead-end below,
    even when it wires other keys, as a `#[cgp_computer]` provider wires its promotions
    ([`cgp_computer_no_error_type_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/cgp_computer_no_error_type_call.rs),
    whose `(_, _)` input keeps `Add`'s own `Computer` impl from matching).

  This is the leaf a handler pipeline bottoms out on when a stage's output type is not one a later
  stage's `UseInputDelegate` input dispatcher handles: a raw `GenericArray` digest, say, reaching an
  `AsyncRead` sink's dispatcher because a byte-encoding stage is missing. The shape is distilled in
  [`cascade_nested_projection`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_nested_projection.rs),
  with the empty-table variant in
  [`empty_dispatch_table`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/empty_dispatch_table.rs).
  Hypershell's own dispatchers `open` their component instead, so the same mistake in its
  `http_checksum_native` example reaches the redirect-wiring leaf above.
- An unmet **`DelegateComponent<Marker>` on a type that is neither the context nor any table** is
  the **not-a-provider** leaf (`[CGP-E115]`): a type wired where a provider was expected that does
  not implement the provider trait at all (`UseBasicAuth<QueryBalanceRequest>`, a request type in a
  handler slot). It arises via the generic blanket for the parent provider trait `T` (owner ==
  parent `Self`), and is split from the **dead-end** by whether the owner has a *concrete* impl of
  `T` (`owner_has_impl_of`): a leaf provider reached via the blanket only because its concrete impl
  did not unify (a pipeline stage fed the wrong input, the `HandleShout` shape) *has* one and is
  dropped, its real cause running through that impl; a genuine non-provider has *none* and is
  reported, named against `T` rather than a wiring key
  ([`non_provider_wired`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/non_provider_wired.rs)
  pins it;
  [`cascade_after_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_after_use_site.rs)
  is the dead-end that must stay dropped).
- An unmet **namespace-lookup bound** is a missing-redirect-wiring leaf too when its table, the
  trait's last type argument, is the context. When the table is an aggregate provider that joins the
  namespace itself, it is the missing-dispatch-entry leaf, as a path key on that provider is. The
  bound is recognized not by name but by the trait's *fingerprint*, a single `Delegate` associated
  type, which `DefaultNamespace`, the `DefaultImpls*` traits, and every user `cgp_namespace!` trait
  share. Any user trait can have that shape, so the trait must also show CGP evidence: it is one of
  CGP's own, an impl of it is keyed by a component marker or a `PathCons` path (the entries
  `cgp_namespace!` writes), or an impl's `where` clause names a parent namespace that shows the same
  evidence. So a user namespace is caught without a `DefId` anchor, and a lookalike trait is not.
- An unmet **extensible-data bound** is the data leaf, read off the presence markers of the partial
  type it lands on ([below](#decoding-classifying-and-rendering-a-leaf)): a builder's `UpdateField`
  for a field the struct lacks is the missing-field leaf; its `Mapper` projection found set where
  the update needs it unset, or unset where it needs it set, is the field-already-set or
  field-not-set leaf (`[CGP-E118]`, `[CGP-E119]`); an unmet `FinalizeBuild` names the fields not
  set; an extractor's `ExtractField` for a variant the enum lacks, or an enum's `FromVariant` for
  one, is the missing-variant leaf (`[CGP-E120]`), and for a variant the extractor already ruled
  out, the already-extracted leaf (`[CGP-E124]`); an unmet `FinalizeExtract` names the variants
  not extracted (`[CGP-E121]`); a `FromVariant` whose `Value` projection differs is the
  variant-type leaf (`[CGP-E122]`); a `Mapper` projection found set or unset where an optional
  builder's `set` needs the field optional is the not-optional leaf (`[CGP-E125]`); and a trait
  only a data derive implements (`HasFields`, `HasExtractor`, `HasBuilder`) is the
  data-trait-unimplemented leaf (`[CGP-E123]`) on a type that is not a partial value, and on a
  partial value the leaf of a builder or an extractor given where its struct or enum belongs
  (`[CGP-E126]`). The shape is pinned by the fixtures of
  [`data/extensible-data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/data/extensible-data),
  such as
  [`builder_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/builder_missing_field.rs)
  and
  [`upcast_missing_variant`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_missing_variant.rs).
- An **ordinary bound on a foreign type** (`f64: Eq`) is a leaf, and the descent must not walk into
  whatever unrelated `std` blanket impl happens to match its `Self` (an `impl<F: FnPtr> Eq for F`
  would otherwise fabricate a misleading `f64: FnPtr` step). A **constrained `DelegateComponent`
  key** whose own `where`-clause is unmet surfaces here. When a dispatcher provider's wiring only
  delegates under a bound (`PipeHandlers<Providers>`'s `delegate_components!` generic list is
  `Providers: ComposeProviders<Provider = Provider>`), an argument that fails that bound (an empty
  `PipeHandlers<Product![]>`, whose `Nil` list has no `ComposeProviders` impl) makes the walk
  descend the delegation impl and bottom out on the unmet composition bound, written
  `Product![]: ComposeProviders` as the program wrote the list, which is the real cause, with the
  `DelegateComponent` node itself dropped as a plumbing label.

Two foreign bounds are exceptions the descent *does* follow, both for the same reason: they reach
the context only deeper. The first is a **getter or blanket trait on a non-context type whose
satisfying impl depends on the context**, such as a request struct's `HasBasicAuthHeader<Ctx>`,
whose `#[cgp_auto_getter]` blanket impl requires `Ctx: HasPasswordType`. There the walk looks into
that blanket impl and follows only its **context-side dependencies** (a provider trait, a
`DelegateComponent`, or an obligation on the context, as `is_context_side` decides; never an
extensible-data trait, which is about the foreign type itself), so the real cause on the
context surfaces (and de-duplicates with the same cause reached down another branch) instead of the
opaque `Request: HasBasicAuthHeader<Ctx>` bound being reported as a second, misleading root cause.
Following only context-side dependencies is what preserves the `f64: Eq` guarantee (a foreign
`f64: FnPtr` step is not context-side, so it is never followed), and it also skips the getter's own
`Ctx::Assoc`-typed `HasField` clause on the request, which is present but a projection mismatch a
plain descent would misreport as a missing field. A provider step that belongs to another context is
not context-side, so it is not followed either, nor is a data trait on the foreign type. The case
both matter for is a dispatch payload: a `#[cgp_auto_dispatch]` trait's blanket impl implements the
trait for every type, by running a matcher with the unit context, so a payload that lacks its own
impl (`Square: HasArea`) matches the blanket, whose dependencies are that matcher and the payload
being an extensible enum (`HasExtractor`, a data trait). Neither is about the context, so the walk
stops at `Square: HasArea`, the payload's missing impl, rather
than descending the matcher into the extractor bounds a plain struct cannot meet
([`auto_dispatch_missing_variant_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/auto_dispatch_missing_variant_impl.rs)).
The second is a **same-trait recursion over a type-level list**: a record's field list
`Cons<Field<.., V0>, Cons<Field<.., V1>, Nil>>: HandleMapEntry<.., Ctx, ..>` handles its head field
here but its later fields through the **tail** `Cons<.., Nil>: HandleMapEntry<..>`, a same-trait
bound on another foreign list node. Following a same-trait recursion lets the walk reach the field
whose dependency is the real cause; following only the *same* trait keeps the `f64: Eq` guarantee,
since a foreign leaf's `impl` dependency is a *different* trait.

Two further rules finish the terminal cases. An obligation whose satisfying impl's trait-clause
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
no such projection yields nothing and declines to the fallback.

Finally, a branch that bottoms out on a `DelegateComponent` is kept only when the owner genuinely
lacks an entry it *should* carry, and dropped as **pure wiring plumbing** otherwise (a delegation
that *holds* is pruned before it can be a leaf, so bottoming out unmet always means the key is
genuinely unwired; the question is only whether that owner is meant to be a table). It is kept in
three shapes: a `DelegateComponent` **on the context** (the missing-wiring leaf); a **dispatch
lookup into a separate table**, recognized structurally because the owner is a proper part of the
parent obligation's `Self` (`Components` inside `UseDelegate<Components>` /
`UseInputDelegate<Components>`, or any custom dispatcher holding its table as a parameter), which
reaches even an *empty* table; and a **non-context table reached via the generic blanket** (owner
*equals* the parent `Self`), recognized because the owner carries at least one `DelegateComponent`
impl and no concrete impl of the parent provider trait, the aggregate-provider case. The two
non-context shapes are both the missing-dispatch-entry leaf. A `DelegateComponent` that is *none* of
these (owner is not the context, not a dispatch lookup, and not a table) splits one final way, by
whether the owner has a **concrete impl of the parent provider trait** (`owner_has_impl_of` against
that trait, not `DelegateComponent`): with no such impl it is a genuine non-provider wired where a
provider was expected (the **not-a-provider** leaf, `[CGP-E115]`); with one, it is a leaf provider
reached via the blanket only because that impl failed to unify (a pipeline stage fed the wrong
input, the `HandleShout` shape), the routing dead-end that is dropped, its real cause running
through that impl down another branch.

Before a provider-trait obligation reaches that not-a-provider leaf, the walk checks for a provider
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

The walk crosses inference-context boundaries carefully, because a stray variable from one
`InferCtxt` panics another. It finds the satisfying impl with the
`fresh_args_for_item`-plus-unification dance rather than `SelectionContext` (which asserts against
the next-generation solver the driver runs under), and each matched impl's predicates are
instantiated, normalized, and region-erased before they cross into the fresh inference context that
checks whether they hold. That avoids the cross-context contamination hazard in
[rustc diagnostic internals](rustc-diagnostic-internals.md#contaminating-one-inference-context-with-anothers-variables).
The obligation being matched crosses the same way: its binder is instantiated with **placeholders**
(via `enter_forall_and_leak_universe`) before it is related, never reached through a bare
`skip_binder()`. A **higher-ranked** obligation makes this load-bearing: the modular-serialization
example's `SerializeIterator` carries
`Self: for<'a> CanSerializeValue<<&'a Value as IntoIterator>::Item>`, and reaching its trait ref
with `skip_binder()` would relate a term with an escaping bound variable and hit the
[generalizer panic](rustc-diagnostic-internals.md#feeding-escaping-bound-variables-to-inference-has_escaping_bound_vars).
Placeholders rather than fresh inference variables are also what let a *nested* higher-ranked hop
resolve: a projection through the bound lifetime (`<&'a Value as IntoIterator>::Item`) normalizes
deterministically against a rigid placeholder region but stalls against an unconstrained inference
region. The instantiation is a no-op for an ordinary binder-free obligation, so only the
higher-ranked case changes.

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
first obligation that restates an earlier one's trait and type with other arguments) and the
provider step that requires it. A provider step is kept only when a wiring entry chose that
provider, so a provider inside a higher-order provider is never named. Where two branches are cut
differently, the cycle wins, since it explains a lookup that never resolves more exactly. The driver
words an `E0275` wiring overflow from this reason (`walk_overflow` seeds the walk, and
[The driver](driver.md#naming-the-traits-behind-a-component-marker) applies it).

The descent is memoized at every node, so a distinct obligation reached from many sites or many
branches is resolved once and reused; the cycle guard and `MAX_DEPTH` cut above are what decide
whether a subtree is complete enough to cache. That mechanism (the node key, the incomplete-subtree
flag, and the reachable-set reuse check) is
[Cached dependency resolution](cached-dependency-resolution.md).

## Decoding, classifying, and rendering a leaf

**Decode the field name.** A `HasField` leaf carries the field name as a type-level `Symbol!`, a
nested `Chars<'h', Chars<'e', …>>` list. The resolver decodes it structurally, walking the list and
reading each `char` const argument until `Nil`, rather than un-sugaring the printed type. Reading
the name from the type is why the replacement never needs the `--verbose` un-eliding the
[text path depends on](driver.md#un-eliding-the-diagnostic): the characters are in the `Symbol`
arguments whether or not the diagnostic would have printed them.

**Classify why the field is unmet.** A "missing" `HasField` bound does not always mean an absent
field, so the resolver inspects the struct the bound lands on and its `Deref` chain to tell three
cases apart. The field is **missing** when neither the struct nor any `Deref` target carries it;
**present** (the underived case) when the struct itself carries the field, so only the
`#[derive(HasField)]` is missing; and **present-via-`Deref`** when the field lives on a `Deref`
target that has not derived it (CGP's `HasField` forwards across `Deref` by a blanket impl, so the
bound *would* hold if that target derived the field), in which case the resolver records the target
so the fix can point at it. The inspection reads named struct fields directly and follows `Deref` by
reading each `impl Deref`'s `Target` associated type, so it needs no inference context, and it is
bounded against a cyclic `Deref`. For a missing field the resolver also records what its fix can
name: adding the field is confirmed only when the struct has named fields (a tuple struct cannot
gain one) and implements `HasField` for another field (so it derives it), and the field's type is
the `Value = T` constraint the requirement writes beside its `HasField` bound, read off the impl
that requires the field (`required_field_type`) and kept only when concrete, and a similar field the
struct carries is recorded as a likely typo (`similar_field`; see
[the fix `help`s](typed-resolution-output.md#the-fix-helps)). A missing wiring key records a similar
key the context wires the same way (`similar_wired_key`). A field present with a mismatched **type**
is a fourth case reached differently, through the projection rule in the walk above. From the
failing projection the resolver reads the expected type, and it queries the struct by `DefId` (with
the struct's own generic arguments substituted, so a same-named struct in another module is never
queried) for the actual type, yielding the `[CGP-E004]` mismatch leaf. A non-field leaf carries no
struct, so it is simply restated as `self: Trait` (`f64: std::cmp::Eq`) for its note lead and for
de-duplicating a leaf reached by several paths.

**Read a partial value's presence markers.** An extensible-data leaf lands on a *partial* value: a
type a data derive generates for each struct and enum (`__PartialPerson<F0, F1>`), with one
`MapType` marker parameter per field or variant. The resolver recognizes one by its `PartialData`
impl, anchored to `cgp-field`, whose `Target` names the struct or enum it builds or matches. Each
field of a partial record, and the payload of each variant of a partial enum, is stored as
`<M as MapType>::Map<…>` for one of its marker parameters, so the ADT's own definition pairs every
marker with the field or variant it tracks, and the value's arguments give each marker's state:
`IsPresent` (set, or still possible), `IsNothing` (unset), `IsVoid` (ruled out), or `IsOptional`
(held as an `Option`). The leaf then names the field or variant the failing bound's tag decodes to,
or the members in the wrong state, against the target's name rather than the generated one. A
missing data derive records the derive a `help` can name only when the type is a struct or enum the
crate defines, of a kind the derive accepts (`ExtractField` and `FromVariant` an enum, `BuildField`
a struct); and a field a builder names that its struct lacks offers no add-the-field fix, since a
merge can then still leave another field unset
([`build_and_merge_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_and_merge_missing_field.rs)).
Two leaves record a method for their `help`, each only when the solver confirms it holds: a core
builder's conversion to an optional one (`to_optional`, through `ToOptional`) for the not-optional
leaf, and for an extractor given to `downcast`, the extractor's own operation (`downcast_fields`,
through `CanDowncastFields`), the pair read from the driver's `PARTIAL_VALUE_OPERATIONS`. Each
records the path a `use` imports its trait by, since these traits are not in the prelude and the
compiler's own import suggestion names a crate path that does not compile.

**Read the type an owner supplies for any other associated type.** A projection mismatch on a trait
other than `HasField` has no struct field to query, so its *actual* side is read by asking the
solver to normalize the projection itself (`projected_type`). That one query covers every way an
owner can supply the type (an abstract type wired to `UseType<T>` resolves through the blanket
`#[cgp_type]` generates, a hand-written `impl HasErrorType for App` through that impl), so no wiring
shape is special-cased, and a result that does not reduce to a concrete type is rendered `_` rather
than half-resolved. The leaf also records whether the trait is a **CGP abstract-type component**,
which is what earns it the `abstract type` wording and a `help` naming the wiring entry to change.
That is recognized structurally by the three things
[`#[cgp_type]`](../../cgp/reference/macros/cgp_type.md) generates and nothing else does: a consumer
trait, whose only associated item is a type, whose provider trait carries the `UseType` blanket. The
last condition is anchored by `DefId` to the crate defining `UseType`, since it is what makes
`UseType<T>` a valid fix to suggest (`abstract_type_component_marker`). A behavioral component, or a
plain trait with an associated type, matches none of the three and reads as a plain
`associated type` with no `help`.

**Render each root cause.** A root-cause path is a list of typed predicates, and rendering it is
where each real trait obligation becomes the concept it stands for, with every name read straight
off the obligation and no component marker or [`ComponentNameMap`](error-processing.md) in the loop.
A consumer-trait obligation `Ctx: Consumer<Params…>` (its `Self` the context) becomes the
consumer-trait impl (`` consumer trait impl `CanCalculateArea` for context `Rectangle` ``), named by
the consumer trait's own `DefId`; a provider-trait obligation
`Provider: ProviderTrait<Ctx, Params…>` becomes the provider-trait impl, naming the provider trait's
`DefId`, the context (the trait's leading argument), and the provider struct (the obligation's
`Self`); a `HasField` becomes the field-trait impl; and a user's own blanket or getter trait (or a
terminal ordinary bound) renders as `` trait impl `Trait<…>` for `Self` ``. Several details make the
labels read well:

- **Plumbing is dropped.** A provider-trait obligation *for the context itself* (the delegation
  routing, as opposed to the real provider), the `DelegateComponent` table lookup, a namespace
  lookup, an extensible-data trait's recursion over a type-level list (`CanBuildFrom`'s
  `FieldsBuilder` over a record's fields, a cast's `FieldsExtractor` over an enum's variants), and
  any residual `CanUseComponent`/`IsProviderFor` obligation carry no information and return no
  label, keeping the chain legible without losing a real step. A
  `RedirectLookup<Table, Path>` provider, by contrast, renders as
  `` redirect lookup to `@Path` in `Table` ``, so a chain of redirects reads as its successive hops.
  `Table` is the lookup's own first type argument, not the walk's context, so a hop inside an
  aggregate provider names the aggregate.
- **Every trait keeps its arguments.** A step's trait is named with the obligation's own arguments
  (the consumer's after `Self`, the provider's after `Self` and the leading context, any other
  trait's after `Self`), so it reads as written: `CanCalculateArea<u32, u64, bool>`, and
  `EncodeVariants<App>` for a blanket trait over a variant list. The context is found by *type*
  position, because a component's lifetime parameters sort ahead of the context in a provider
  trait's argument list (`ReferenceGetter<'a, Ctx, T>`), and indexing by raw argument position would
  land on the region and abort the compiler. A lifetime argument stays in its place; the walk erases
  regions, so it reads `'_`, as in the context `App<'_>` (`ReferenceGetter<'_, str>`).
- **A builder or an extractor is named in words.** A step whose `Self` is a partial value names it
  by what it builds or matches and its markers, as
  ``trait impl `BuildField<Symbol!("host")>` for the builder of `Config` with `host` and `port` set``
  or ``… for the extractor of `Shape` with `Circle` ruled out``, rather than by its generated name. A
  partial value in a trait argument (a builder pipeline's input) keeps its generated type.
- **Type-level lists are resugared.** A rendered label's `Self` type has its `Cons`/`Either` list
  read back as the `Product![A, B]` or `Sum![A, B]` the programmer wrote, and one step further to a
  CGP `Struct!` or `Enum!` shape when every element is a `Field` cell, so a field- or variant-list
  handler (the modular-serialization example's `FieldsSerializer` over a record's field list) names
  the list rather than a chain of cells. The rendering is `render_ty`,
  the **typed** one of the tool's three resugaring implementations, anchored by `DefId` to the CGP
  crate that defines each cell so a same-named type elsewhere is never resugared. What each
  construct folds back to, what makes a fold decline, and how this implementation differs from the
  text and syntax-tree ones is [Resugaring](resugaring.md).

Each hop is a structured [`DepNode`](error-processing.md) variant, one per template, each stamped
with its own [`CGP-E1xx` code](../error-code.md) when rendered. So `consumer trait impl`
(`CGP-E101`), `provider trait impl` (`CGP-E102`), `redirect lookup` (`CGP-E103`), and the general
`trait impl` (`CGP-E104`) each carry a distinct tag, and a terminal leaf takes a leaf code
(`CGP-E110`–`CGP-E117`), an ordinary bound included. The walk emits one flat path of these nodes per
way a cause is reached, and the rustc-free [dependency graph](dependency-graph-rendering.md) merges
the paths and renders them as `cargo tree`-style text, every construct named in full. A dispatch
pipeline's plumbing hops all restate the same program-sized `Code` type, and each spells it out,
since the type a reader is tracing is the point of the chain
([`deep_dispatch_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/verbosity/deep_dispatch_chain.rs)
pins the resulting shape). All of the merge and render is in the rustc-free
`cargo-cgp-error-processing` crate, unit-tested on any toolchain.

A seed that is itself the cause, an operation with no impl at all (a `FinalizeBuild` on a builder
with a field unset, a `FromVariant` for a variant the enum lacks), still heads its chain with its
own step, so the chain names the operation the cause is about rather than restating the cause
([`finalize_build_premature`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_build_premature.rs)).

## Tests

The walk and its leaf classification carry most of the resolver's fixtures: the leaf classes
(fields, wiring, redirects, dispatch tables, non-providers), the harder mechanics (parallel
branches, deep nesting, higher-ranked descents, the mid-`clauses_of` decline), and the
stalled-projection recoveries. The consolidated catalog, one entry per pinned behavior, lives in the
parent document's [Tests](typed-root-cause-resolution.md#tests) section.

## Source

- [`crates/cargo-cgp-driver/src/resolve/walk/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/walk):
  the descent: `leaves.rs` (the recursion), `vocabulary.rs` (what it walks into, and which
  dependencies a foreign bound is followed into), `impl_match.rs`
  (the satisfying impl and its dependencies), `unknowns.rs` (placeholders and stalled projections),
  `projection_mismatch.rs` (the unmet projection an impl carries, `HasField` or otherwise),
  `holds.rs` (the solver query), `written_order.rs` (the order an impl's clauses are read in), and
  `misdirected.rs` (the requirements of a provider impl whose `#[cgp_impl]` header names the
  consumer trait).
- [`crates/cargo-cgp-driver/src/resolve/classify/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/classify):
  `reportable.rs` (root cause versus routing dead-end), `leaf.rs` (`classify_leaf`, which builds the
  rustc-free `Leaf`), `data.rs` (`classify_data_leaf`, the extensible-data leaf read off the presence
  markers), `field.rs` (the struct and `Deref`-chain inspection), `required_type.rs` (the
  type a requirement gives a missing field), `near_miss.rs` (a similar field, variant, or wiring key
  the program wrote), and `assoc_type.rs` (the normalization that reads the
  type an owner supplies for any other projected associated type).
- [`crates/cargo-cgp-driver/src/resolve/data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/data):
  `traits.rs` (the extensible-data traits, the operations among them, their list recursions, and
  the derive each data trait comes from) and `partial.rs` (`read_partial`, a partial value's target
  and markers).
- [`crates/cargo-cgp-driver/src/resolve/label/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/label):
  `predicate_label.rs` (each hop as a structured `DepNode`, read off the obligation) and
  `render_ty.rs` (the type-level list resugaring).

The per-file map of the whole resolver lives in the parent document's
[Source](typed-root-cause-resolution.md#source) section.

## Further reading

- [Typed root-cause resolution](typed-root-cause-resolution.md): the pipeline overview, its
  boundaries, and the consolidated tests and source catalogs.
- [rustc diagnostic internals](rustc-diagnostic-internals.md): the panic hazards the walk's
  inference-context discipline exists to avoid.
