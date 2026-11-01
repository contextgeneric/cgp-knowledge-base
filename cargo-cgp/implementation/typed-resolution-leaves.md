# Typed resolution: leaves and labels

This document covers what ends a branch of the [walk](typed-resolution-walk.md): which terminal
bound counts as which cause, and how each leaf and each hop above it is worded for the dependency
tree [the emitter emits](typed-resolution-output.md).

## The leaf shapes

The walk treats any obligation it does not follow as a **terminal leaf**, and `classify_leaf` turns
each one into the rustc-free `Leaf` the emitter words, or drops it as a routing dead-end. The leaf
shapes are:

- An unmet **`HasField`** is the field leaf.
- An unmet **`DelegateComponent<Marker>` on the context** is the missing-wiring leaf: the context
  delegates that component to no provider. Nothing else can explain it, since a wired key would hold
  and never become a node. So the walk stops here even when an impl unifies, as the blanket a
  namespace join writes does for every key, whose lookup machinery would end on plumbing. The
  exception is an entry that forwards the key to
  another table (`GreeterComponent -> Bundle`), which the context does carry: its impl's
  `where Bundle: DelegateComponent<GreeterComponent>` bound fails, so the walk descends into
  that lookup and reports the missing-dispatch-entry leaf on `Bundle`
  ([`direct_delegation_missing_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/direct_delegation_missing_key.rs)).
- An unmet **`DelegateComponent<PathCons<…>>`**, whose key is a redirect path rather than a bare
  marker, splits by owner. On the context it is the missing-*redirect*-wiring leaf (`[CGP-E113]`),
  named by its whole path. On any other type it is the missing-dispatch-entry leaf below, since the
  lookup ran in an aggregate provider that `open`s the component in its own table; the path is kept
  whole as that leaf's key. An owner with its own impl of the provider trait reached this lookup
  only because that impl did not unify, so the leaf is kept only when one argument explains the
  mismatch, as for the provider-for-other-arguments leaf below, and dropped otherwise. A redirect
  appends the component's parameters to its path, so a lookup recovered from a call whose input is
  inferred ends in a placeholder segment; on the context the leaf drops that trailing run and names
  the path the programmer can wire (`@HandlerComponent.Missing`, from
  [`pipeline_unhandled_code`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/pipeline_unhandled_code.rs)).
  The trimmed leaf claims the context has no entry under that path for any value of the unknown, so
  it is kept only when the solver, given an inference variable in place of each placeholder, finds
  that the lookup can hold for none. An `open` error table that routes `String` can serve an unknown
  error type, so its lookup is not reported
  ([`placeholder_error_route_leaf`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/placeholder_error_route_leaf.rs)).
- An unmet **`DelegateComponent<Key>` on a *non-context* delegation table** is the
  missing-dispatch-entry leaf (`[CGP-E114]`): the owner is a provider that delegates (an aggregate
  provider missing a component wiring, or a `UseDelegate`/`UseInputDelegate` table missing a branch
  for the type it dispatches on, a `Code` fragment or an `Input` value's type), and it does not wire
  this key. It is told apart from a higher-order-provider dead-end (dropped, below) two ways, so it
  is reported when *either* holds (`classify_leaf`, over `is_dispatch_lookup` and
  `owner_has_impl_of`; the first in `classify/reportable.rs`, the second in the query layer):
  - **structurally**, when the obligation is a *dispatch lookup into a separate table*: its owner is
    a proper part of the parent obligation's `Self`, as `Components` is of `UseDelegate<Components>`
    / `UseInputDelegate<Components>` (or any custom dispatcher that holds its table as a parameter).
    Such a `where`-clause is unambiguously a table lookup, so an unmet one is a missing entry
    *regardless of whether that table wires any other key*. This reaches an **empty**
    dispatch table.
  - **by owner property** otherwise (the generic-blanket case, where the owner *equals* the parent
    `Self`): the owner wires at least one other key, i.e. carries a `DelegateComponent` impl, and
    has no concrete impl of the parent provider trait. This is the aggregate-provider case, where
    the blanket keys on the provider itself so no separate-table structure is visible. An owner with
    its own impl of the trait can never wire the trait's key as well, since the blanket and the
    impl would overlap, so reaching its blanket means that impl did not unify: the dead-end or
    the provider-for-other-arguments leaf below, even when it wires other keys, as a
    `#[cgp_computer]` provider wires its promotions
    ([`cgp_computer_no_error_type_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/cgp_computer_no_error_type_call.rs),
    whose `(_, _)` input keeps `Add`'s own `Computer` impl from matching).

  This is the leaf a handler pipeline bottoms out on when a stage's output type is not one a later
  stage's `UseInputDelegate` input dispatcher handles: a raw `GenericArray` digest, say, reaching an
  `AsyncRead` sink's dispatcher because a byte-encoding stage is missing. The shape is distilled in
  [`cascade_nested_projection`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_nested_projection.rs),
  with the empty-table variant in
  [`empty_dispatch_table`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/empty_dispatch_table.rs).
  A dispatcher that `open`s its component instead reaches the redirect-wiring leaf above.
- An unmet **`DelegateComponent<Marker>` on a type that is neither the context nor any table**
  arises via the generic blanket for the parent provider trait `T` (owner == parent `Self`), and
  splits by whether the owner has a *concrete* impl of `T` (`owner_has_impl_of`). A genuine
  non-provider has *none*: a type wired where a provider was expected that does not implement the
  provider trait at all (`UseBasicAuth<QueryBalanceRequest>`, a request type in a handler slot), the
  **not-a-provider** leaf (`[CGP-E115]`), named against `T` rather than a wiring key
  ([`non_provider_wired`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/non_provider_wired.rs)
  pins it). The leaf also records the **adapters** that make the owner a provider
  (`wrapping_adapters`, `classify/fix/adapter.rs`): for each impl of the provider trait whose `Self`
  is an ADT over one type parameter the impl bounds by a trait (`WithProvider<P>`, `Promote<P>`; an
  ADT such as `UseType<T>`, which only carries `T` as a type, bounds it by nothing), the ADT applied
  to the owner, kept when the solver confirms it implements the trait for the same arguments. No
  adapter is recognized by name, and the search declines when the obligation holds an unknown. It
  also records the other components the owner is a provider of for the same context
  (`provided_components`, `classify/fix/provided_components.rs`): each provider trait with no
  parameter beyond `Self` and the context whose delegation blanket keys on a marker, kept when the
  solver confirms `Owner: Trait<Context>`
  ([`wrong_component_provider_check`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/wrong_component_provider_check.rs)).
  `core_provider_hint` (`classify/fix/core_provider.rs`) handles two core providers, anchored by
  `DefId` to the crates that define them: `UseField` on a trait with no `UseField` impl, where
  `UseFields` implements the trait for the context (a multi-method getter), and `UseDelegate` on a
  component with parameters whose trait has a `RedirectLookup` impl, which an `open` statement uses
  ([`getter_multi_method_use_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/getter_multi_method_use_field.rs),
  [`use_delegate_without_derive`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_delegate_without_derive.rs);
  [`use_field_multi_method_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_field_multi_method_missing_field.rs)
  and
  [`use_delegate_parameterless_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_delegate_parameterless_component.rs)
  name neither, since `UseFields` would not hold and the component has no parameters to dispatch
  on). An owner that *has* one reached the blanket only because that impl did not unify with the
  arguments the walk gives it, and two cases follow:
  - When those arguments are fully known (no placeholder, inference variable, or unreduced
    projection) and exactly one argument position is one that none of the owner's concrete impls
    accepts, the owner implements `T` for other arguments: the **provider-for-other-arguments** leaf
    (`[CGP-E127]`, `provider_for_other_arguments` in `classify/fix/other_arguments.rs`). It names
    that argument and the ones the impls take there: the context for a provider written for another
    context
    ([`provider_for_other_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/provider_for_other_context.rs)),
    or a component parameter for a pipeline stage given another stage's output type
    ([`pipe_handlers_stage_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/pipe_handlers_stage_mismatch.rs)).
    An impl's own generic parameters print as `_` (`Input = Result<_, _>`).
  - Otherwise it is the **dead-end**, dropped, its real cause running through that impl: a stage fed
    an input the walk does not know (`HandleShout` in
    [`cascade_after_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_after_use_site.rs),
    the dead-end that must stay dropped), or a mismatch at several positions, which no single
    argument explains.
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

## The wiring-without-`IsProviderFor` leaf

Before it searches an impl for an
[unmet projection](typed-resolution-walk.md#an-impl-whose-trait-clauses-all-hold), the walk checks
the one scaffolding requirement that can be the cause itself. The delegation blanket a consumer call
routes through requires the context's own `IsProviderFor<Component, Context, …>` beside its
delegate, and `delegate_components!` implements it with each entry. A context wired by a
hand-written `DelegateComponent` impl has no such impl, so its delegation step fails on that bound
alone while every other requirement holds, and a check of the component passes, since it needs only
the delegate's `IsProviderFor`. So when an impl's only failing requirements are scaffolding, one of
them an `IsProviderFor` on the context, and the context has no `IsProviderFor` impl for the
component (nor a blanket one over every key, as a namespace join writes),
`wiring_without_provider_for` (`classify/fix/hand_wiring.rs`) reports the
**wiring-without-`IsProviderFor`** leaf (`[CGP-E128]`), carrying the delegate the hand-written impl
names for its `help`
([`hand_delegate_without_is_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/hand_delegate_without_is_provider.rs)).
A context that has the impl is left alone, since the failure then lies with the delegate's own
`IsProviderFor`.

## Dropping a routing dead-end

A branch that bottoms out on a `DelegateComponent` is kept only when the owner genuinely lacks an
entry it *should* carry, and dropped as **pure wiring plumbing** otherwise. A delegation that
*holds* is pruned before it can be a leaf, so bottoming out unmet always means the key is unwired,
and the question is only whether that owner is meant to be a table.
[The leaf shapes](#the-leaf-shapes) above list what is kept. The rest is a leaf provider reached
through its delegation blanket only because its own impl failed to unify, with no single argument to
explain why, so its real cause runs through that impl down another branch.

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
bounded against a cyclic `Deref`. Only a struct with named fields carries a field a `Symbol!` tag
names: a tuple struct keys its fields by `Index<N>`, so a `Symbol!("0")` tag on one is a *missing*
field, never an underived one, and the resolver records the `Index<0>` tag the position takes
([`symbol_tag_on_tuple_struct_check`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/symbol_tag_on_tuple_struct_check.rs);
[`symbol_tag_not_a_tuple_position`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/symbol_tag_not_a_tuple_position.rs)
gets no `Index` tag for a position past the fields or a padded spelling). For a missing field the
resolver also records what its fix can name: adding the field is confirmed only when the struct has
named fields (a tuple struct cannot gain one) and implements `HasField` for another field (so it
derives it), and the field's type is the `Value = T` constraint the requirement writes beside its
`HasField` bound, read off the impl that requires the field (`required_field_type`) and kept only
when concrete, and a similar field the struct carries is recorded as a likely typo (`similar_field`;
see [the fix `help`s](typed-resolution-output.md#the-fix-helps)). A missing wiring key records a
similar key the context wires the same way (`similar_wired_key`). A field present with a mismatched
**type** is a fourth case reached differently, through
[the projection rule](typed-resolution-walk.md#an-impl-whose-trait-clauses-all-hold). From the
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
which earns it the `abstract type` wording and a `help` naming the wiring entry to change.
That is recognized structurally by the three things
[`#[cgp_type]`](../../cgp/reference/macros/cgp_type.md) generates and nothing else does: a consumer
trait, whose only associated item is a type, whose provider trait carries the `UseType` blanket. The
last condition is anchored by `DefId` to the crate defining `UseType`, since it makes
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
`Self`); and a user's own blanket or getter trait (or a terminal ordinary bound) renders as
`` trait impl `Trait<…>` for `Self` ``. A type with no wiring of its own is named plainly rather
than as a context. A `HasField` obligation is never a step: the walk ends a
branch there as the field leaf. Several details make the
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
  or ``… for the extractor of `Shape` with `Circle` ruled out``, rather than by its generated name.
  A partial value in a trait argument (a builder pipeline's input) keeps its generated type.
- **Type-level lists are resugared.** A rendered label's `Self` type has its `Cons`/`Either` list
  read back as the `Product![A, B]` or `Sum![A, B]` the programmer wrote, and one step further to a
  CGP `Struct!` or `Enum!` shape when every element is a `Field` cell and the shape has an exact
  spelling, so a field- or variant-list
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
(`CGP-E110` onward), an ordinary bound included. A provider step above a not-a-provider leaf keeps
`CGP-E102` but reads as what is required, since the impl it names does not exist. The walk emits one
flat path of these nodes per way a cause is reached, and the rustc-free
[dependency graph](dependency-graph-rendering.md) merges the paths and renders them as
`cargo tree`-style text, every construct named in full. A dispatch pipeline's plumbing hops all
restate the same program-sized `Code` type, and each spells it out, since the type a reader is
tracing is the point of the chain
([`deep_dispatch_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/verbosity/deep_dispatch_chain.rs)
pins the resulting shape). All of the merge and render is in the rustc-free
`cargo-cgp-error-processing` crate, unit-tested on any toolchain.

A seed that is itself the cause, an operation with no impl at all (a `FinalizeBuild` on a builder
with a field unset, a `FromVariant` for a variant the enum lacks), still heads its chain with its
own step, so the chain names the operation the cause is about rather than restating the cause
([`finalize_build_premature`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_build_premature.rs)).

## Further reading

- [Typed resolution: walking to the root cause](typed-resolution-walk.md): the descent that reaches
  each leaf.
- [Typed resolution: the transformed diagnostic](typed-resolution-output.md): how the emitter words
  each leaf and what its `help` names.
- [Resugaring](resugaring.md): the tool's three resugaring implementations, `render_ty` among them.

## Tests

The leaf classes (fields, wiring, redirects, dispatch tables, non-providers, extensible data) carry
most of the resolver's fixtures. The consolidated catalog, one entry per pinned behavior, lives in
the parent document's [Tests](typed-root-cause-resolution.md#tests) section.

## Source

- [`crates/cargo-cgp-driver/src/resolve/classify/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/classify):
  `reportable.rs` (the shapes that tell a delegation table from a routing dead-end), `known.rs`
  (whether a provider obligation is known well enough to confirm a fix against), `leaf.rs`
  (`classify_leaf`, which builds the rustc-free `Leaf` or drops a routing dead-end), `data.rs`
  (`classify_data_leaf`, the extensible-data leaf read off the presence markers), `field.rs` (the
  struct and `Deref`-chain inspection), and `fix/`, the finders
  of the facts a `help` names: `adapter.rs` (the adapter types that make a non-provider a
  provider), `provided_components.rs` (the other components it provides), `core_provider.rs`
  (what serves a slot a misused core provider cannot), `other_arguments.rs` (the argument a
  provider does not implement its provider trait for), `hand_wiring.rs` (a component wired
  without its `IsProviderFor`), `required_type.rs` (the type a requirement gives a missing
  field), and `near_miss.rs` (a similar field, variant, or wiring key the program wrote).
- [`crates/cargo-cgp-driver/src/resolve/data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/data):
  `traits.rs` (the extensible-data traits, the operations among them, their list recursions, and
  the derive each data trait comes from) and `partial.rs` (`read_partial`, a partial value's target
  and markers).
- [`crates/cargo-cgp-driver/src/resolve/label/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/label):
  `predicate_label.rs` (each hop as a structured `DepNode`, read off the obligation),
  `render_ty.rs` (the type-level list resugaring), and `empty_lists.rs` (a standalone `Nil` or
  `Void` written `Product![]` or `Sum![]`).

The per-file map of the whole resolver lives in the parent document's
[Source](typed-root-cause-resolution.md#source) section.
