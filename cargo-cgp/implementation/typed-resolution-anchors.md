# Typed resolution: anchoring the starting obligation

This document covers the first stage of the driver's
[typed root-cause resolution](typed-root-cause-resolution.md), which recovers from a failing
diagnostic the **real trait obligation** that seeds the [walk](typed-resolution-walk.md): a
consumer-trait obligation `Ctx: ConsumerTrait<Params…>`, or, for a `#[check_providers]` entry or a
provider's own method called directly, the provider-trait obligation it asserts. Twelve anchors
recover it from twelve failure shapes, tried in the order of the list in `resolve/anchors.rs`, and
the first that succeeds wins. Each entry of the list states the anchor, the gate that says which
diagnostics it may read (the last three, a trait used as a bound, read only an `E0277`), a check on
its resolution, and whether the result is anchored at the call expression. Eight are
described here. The remaining four re-read the failing call expression, one for a call through a
consumer or blanket trait, one for a call to an extensible-data operation, one for a provider
trait's method called through the provider's own path, and one for a bound of a generic function
the call names; they are tried seventh to tenth and share
[their own document](typed-resolution-call-site.md). How the recovered causes are worded and
emitted is [the transformed diagnostic](typed-resolution-output.md).

**From a `check_components!` entry, by span.** A `check_components!` entry expands to a concrete
impl of a generated check trait,
`impl __CheckRectangle<AreaCalculatorComponent, ()> for Rectangle {}`, whose check trait carries
`CanUseComponent<Marker, Params>` as a supertrait. The macro re-spans the context type in that impl
onto the entry the user wrote, so the impl's `Self`-type span equals the failing diagnostic's
primary span. `resolve_check_failure` walks the crate's check traits (those with a
`cgp_component::CanUseComponent` supertrait) and picks the impl whose `Self` span matches the caret,
through the query layer's `check_impls_at`, which the provider-check anchor, the `E0275` overflow
analysis, and the unit-parameters detector share. That ties *this* diagnostic to *this* entry
without reading either one's text. It reads the entry's `CanUseComponent<Marker, Params>` assertion
only to learn *which* component the check names: it maps the marker to its consumer trait
(`marker_to_consumer`) and ungroups the `Params` slot back into the consumer's own arguments
(`can_use_to_consumer_obligation` over `consumer_obligation`), yielding the real obligation, e.g.
`Rectangle: CanCalculateArea`. The ungrouping is decided by the consumer's own generics, not by the
slot's shape: the slot carries the parameters as all-types data (none as `()`, one bare, several as
a tuple, a lifetime lifted into `Life<'a>`), so the trait's parameter count decides whether a tuple
is *the* single tuple-typed parameter or several to spread, and a lifetime parameter takes its
region back out of the `Life<'a>` lift. Trusting the slot's shape instead would hand the solver a
malformed obligation (a `Life<'a>` *type* where a region belongs aborts the compiler when related),
so any mismatch declines to the fallback rather than build one (the
[`lifetime_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/lifetime_component.rs)
and
[`tuple_param_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/tuple_param_component.rs)
fixtures pin the two shapes). `CanUseComponent` is the user's own check assertion, legitimately read
here to find the component; it is the marker map, not the walk, that then routes to the consumer.

**From a `#[check_providers]` entry, by span.** The `#[check_providers(P)]` form of
`check_components!` asserts a provider directly: it expands to an impl of a generated check trait
whose supertrait is `IsProviderFor<Component, Context, Params>`, with the listed provider as `Self`
and that type's span on the entry the user wrote
(`impl CheckRectangleProviders<AreaCalculatorComponent, Rectangle, ()> for ScaledArea<RectangleArea> {}`).
`resolve_provider_check` matches that impl by its `Self` span, as the check-entry anchor does, and
tells a check trait from a component's own provider trait (which also carries `IsProviderFor`) by
its supertrait's component argument being one of the trait's own parameters. It maps the marker to
the component's provider trait and seeds the walk with the provider obligation
`ScaledArea<RectangleArea>: AreaCalculator<Rectangle>`, so the tree starts at the provider the entry
lists, whatever the context wires; a provider the context does not wire at all is checked the same
way. The result records the provider, which makes the block the provider class `[CGP-E002]`
([`check_providers_layer`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/higher-order-provider-layer/check_providers_layer.rs),
[`check_providers_unwired_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/check_providers_unwired_provider.rs)).
One attribute over several components generates one impl per component, each with the provider as
`Self` on the one token the attribute names, so their errors share a caret. The impls' spans
differ in their syntax contexts, which the span comparison includes, so each error reads its own
impl and gets its own block
([`check_providers_two_components`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/check_providers_two_components.rs)).

**From a hand-written `impl Trait for Context` block.** A wiring failure often surfaces inside an
impl the programmer wrote rather than at a check entry. A wrapper trait that adds a bound the
component cannot express, such as `Send`, is the common case, and the
[`manual_supertrait_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/manual_supertrait_impl.rs)
fixture distills it:

```rust
pub trait CanCalculateAreaChecked<Shape>: CanCalculateArea<Shape> {
    fn area_checked(&self, shape: PhantomData<Shape>) -> f64;
}

impl CanCalculateAreaChecked<Rectangle> for App {
    fn area_checked(&self, shape: PhantomData<Rectangle>) -> f64 {
        self.area(shape)
    }
}
```

`CanCalculateAreaChecked` carries the CGP consumer trait `CanCalculateArea<Shape>` as a supertrait and
is implemented directly on `App`. When the underlying `CanCalculateArea` wiring is broken, the caret
lands on this impl (its header, a method signature, or the forwarding call), never on `App`'s
own type definition, so the use-site anchor cannot recover the context from a struct-definition
span. `resolve_impl_site` handles it: it finds the enclosing trait impl whose *full* HIR span (not
`def_span`, which for an impl covers only the header) contains the diagnostic's primary span, takes
its `Self` type as the context, and instantiates the impl's supertraits for that `Self`. A
supertrait on that context that does not hold and is either a CGP consumer trait **or** a
`#[cgp_fn]` / `#[blanket_trait]` blanket-impl trait
(`impl<Context> Trait for Context where Self: HasField<…>`, a trait with a blanket impl but no
provider, recognized by `is_blanket_trait` as described under *Recognizing a blanket trait* below)
**is** the obligation to walk. The resolver seeds it directly (`wrapper_consumer_causes`), with its
concrete component parameter intact (`CanCalculateArea<Rectangle>`, not the `()` a parameterless
re-check would substitute), so no marker detour is needed. The blanket-impl case is what reshapes a
`#[cgp_fn]` blanket-trait check (`pub trait CheckGetUser: GetUser {}` +
`impl CheckGetUser for App {}`, the tutorial idiom for asserting a blanket trait holds) whose real
cause is a field the context is missing: the walk descends the blanket's `where` clause
(`Self: HasField<…>`, or a `#[uses]`-chained sibling trait) to the `` missing field `…` `` leaf, in
place of rustc's misleading "`#[derive(HasField)]` is required" note. A plain supertrait such as
`Send` is neither, so it is left alone.

**The impl counts only when the caret is about it.** A method body inside the impl can hold an
unrelated error, such as an `Rc` passed to a `T: Send` function, and re-anchoring that error onto
the impl's failing supertrait would replace it with the CGP tree and then de-duplicate it away. So
`is_about_impl` (in `spans.rs`) accepts a primary span on the impl outside every method body (the
header or a signature), or one inside a body only on a call to a method that the impl's trait or one
of its supertraits declares, which is the forwarding call that fails because the supertrait does.
The span must be about that call by the call-site anchor's rule (on the call, its method name, or a
whole argument, never strictly inside its receiver or an argument), so an error nested in the
forwarding call's argument keeps its own diagnostic too. The wrapper-chain anchor below applies the
same gate. A secondary label or a note never counts, since rustc points those at any code the
failure passed through.

**A bound of the impl's own `where` clause reads as itself.** The compiler reports a concrete
`where` bound that fails, such as `where Inner: CanCompute` on a provider or `where App: CanRun` on
a wrapper of another type, at the bound, and that bound can fail for a cause of its own beside the
impl's supertrait. So before the supertrait recovery, `where_bound_on_context` looks for the bound a
primary span lies on, and when it is an unmet CGP consumer bound on a context, it walks it as that
consumer obligation, which de-duplicates into the context's own check
([`wrapper_impl_with_failing_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/wrapper_impl_with_failing_bound.rs)).
A context from another crate counts when it carries its own wiring
([`foreign_context_where_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/foreign_context_where_bound.rs)),
and a bound on a plain Rust trait keeps rustc's diagnostic
([`impl_bound_on_plain_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/impl_bound_on_plain_trait.rs)).

A supertrait's tree is **headed by the impl's own trait**, the wrapper the programmer wrote, so
the failure reads `CanCalculateAreaChecked → CanCalculateArea → …` and points at their code rather than
dropping the wrapper. The headline's code turns on the wrapper's **fingerprint**: a wrapper that is itself a
CGP consumer trait (has a consumer blanket routing to a provider) takes `[CGP-E001]`, while a plain
wrapper such as `CanCalculateAreaChecked`, with only a concrete impl, takes `[CGP-E003]`. The wrapper is a
distinct trait from the CGP supertrait it reduces to, so its error is not a re-report of the
`check_components!` entry for that supertrait; when the two share their root cause, they coalesce
into one block at flush, as [the transformed diagnostic](typed-resolution-output.md) describes. This
anchor is tried *before* the wrapper-chain and use-site ones, and its supertrait recovery fires only
for an impl on a **context**: a struct or enum the checked crate defines, or one from another crate
that carries `DelegateComponent` wiring of its own (`is_context_adt`), as a context a library
exports does. An impl on any other foreign type or on a provider struct carries no consumer
supertrait on a context, so only its own `where` bounds are read. A `check_components!` check impl
is skipped altogether, since its generated trait carries `CanUseComponent` as its supertrait: it
belongs to the check-entry anchor, and heading a tree with it would present the generated
`__CanUseApp` as a trait the programmer wrote. No fixture depends on the skip: the check entries the
check-entry anchor declines, ones checked at unit parameters, are reported as a
[structural mistake](diagnostic-reshapes.md#reshaping-a-structural-mistake) before any anchor runs.

**From a foreign wrapper chain.** The routing glue can put the failure one level further out: a
hand-written `impl Trait for Foreign` block whose `Self` is a foreign type holding the context,
where the CGP consumer sits several ordinary-trait `where`-clause hops beneath the impl. The
[`foreign_wrapper_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/foreign_wrapper_chain.rs)
fixture has the shape: `impl CanAddAppRoutes for Box<App>` descends through
`Box<App>: CanAddRoute<App, GreetApi>` before reaching `App: CanHandleApi<GreetApi>`, with the real
context `App` appearing only as a type *argument* of each hop and never as the impl's `Self`. Neither the impl-site anchor (whose `Self`
must be a context) nor the use-site anchor (whose context comes from a struct-definition span the
caret never touches) can recover it.

`resolve_wrapper_chain` descends the impl's own unmet supertrait through the ordinary trait
obligations beneath it (each impl's `where`-clause bounds) until one lands on a CGP consumer whose
`Self` is a context, the handoff (`consumer_handoff_causes`) it then seeds and walks directly. Every
ordinary hop becomes a `trait impl` node, so the tree reads from the code the programmer wrote down
to the root cause. Two subtleties make the descent work. First, it **re-evaluates each obligation
with the trait solver** rather than trusting rustc's cascade-suppressed diagnostic: the direct
`App: CanHandleApiSend<GreetApi>` bound is *assumed to hold* off its own ill-formed impl, so the
descent reaches the consumer instead through the **base trait of a projection `where`-clause** (a
`Ctx::Response: Send` bound over the broken `CanHandleApi`, whose base `Ctx: CanHandleApi<…>` is
what genuinely fails), which requires reading the impl's predicates *un-normalized* so the
projection's base survives. Second, the tree is headed by the impl's own trait, fingerprinted for
the `[CGP-E001]`/`[CGP-E003]` code as the impl-site anchor does. But because `Self` is a foreign
wrapper rather than the context, the class sentence names it **plainly**
(`` the trait `CanAddAppRoutes` is not implemented for `Box<App>` ``, with no `context`
qualifier), carried by the `Resolved::subject_is_context` flag; it is the internal headline, and the
displayed one only when the causes are too mixed to state at once. Only a genuine CGP consumer is
ever reported as a cause, so a descent into unrelated `where`-clauses contributes nothing. This
anchor is tried after the impl-site anchor and before the use-site ones.

**From a use site, by wired component.** When no impl matches the caret, the failure is often a
consumer-method call: CGP wiring is lazy, so a broken dependency surfaces where the method is
*called* rather than at a check:

```rust
let person = Person { /* … */ };
person.greet(); // `Person` cannot satisfy `CanGreet`'s wiring
```

This is an `E0599` "the method `greet` exists … but its trait bounds were not satisfied", with no
check impl to anchor on. `resolve_use_site` recovers the context from the diagnostic's own spans
instead: it scans every local struct/enum whose definition span contains one of the diagnostic's
spans (the receiver's type is one such: the "method not found for this struct" span lands on
`Person`'s definition) and, for each candidate, reads the `DelegateComponent<Key>` impls that
context wires, maps each key to its consumer trait, seeds that consumer obligation, and keeps the
ones that do not hold. Because it walks every wired component, several of them can bottom out on one
shared cause, so the collected causes go through `Causes::union`: the shared cause is named once and
keeps *every* component's route to it, so each consumer the header lists has a chain in the note
([`use_site_shared_cause`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/use_site_shared_cause.rs)).
A diagnostic span can also land on a *provider* struct, so a candidate that wires no failing
component is discarded, which selects the real context. A **component marker** is never a candidate
at all: rustc's notes often point at a component macro's attribute (`#[cgp_getter]`, say), under
which the generated marker struct is defined, and reading that marker as the context would name
`NameGetterComponent` where the context `Person` belongs
([`getter_unwired_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/getter_unwired_call.rs)).
The transformed error is the same `[CGP-E001]` consumer form over a root-cause note, and the
misleading "this is an associated function… use associated function syntax instead" advice, which
the method probe emits for CGP's `self`-less provider methods, is dropped with the rest of rustc's
sub-notes. The anchor is not limited to method calls: any failure whose spans land on the context's
struct definition reaches it.

A `DelegateComponent` key comes in three shapes, and each is handled differently. The distinction
matters for an `open`-dispatched context, whose per-value entries are redirect *paths*, not markers.
A **bare component marker** maps to `Ctx: Consumer` (its parameterless form), and only for a
component without type parameters: the bare marker carries no parameter values, and re-checking a
generic component with `()` in its parameter slot would assert an obligation nothing in the program
asks for (`CanRaiseError<()>` for a wired `ErrorRaiserComponent`), so such a failure is left to the
call-site anchor
([`question_mark_after_failed_handle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/question_mark_after_failed_handle.rs)).
An **`open`-dispatch redirect path** (`PathCons<Component, PathCons<Value, …>>`, the key an
`@Component.Value:` entry emits) is decomposed, and the real dispatch value re-checked as
`Ctx: Consumer<Value>`, so the failure is traced with the value the context actually wired
(re-checking the raw `PathCons` key would report the internal list as a bogus consumer bottoming out
on `T: Sized` noise). Three keys are skipped: a bare marker that is *also* `open`-dispatched (its
`()` form would report a spurious `@Component.()` redirect, while its real values are covered by the
path entries); a generic catch-all whose recovered value still carries a free type parameter
(`<'a, T> &'a T: SerializeDeref` yields `&T`, whose re-check produces only `T: Sized`); and a
**blanket-forwarding key**, a bare type parameter (`__Key__`) from the impl a `namespace …;` join
emits (`impl<__Key__> DelegateComponent<__Key__> for Ctx`) to forward *every* lookup to the
namespace. That key names no concrete component, and re-checking a free parameter as one bottoms out
on `__Key__: Sized` noise; skipping it means this anchor yields nothing for a pure namespace join
(whose concrete wiring lives in the namespace, not the context's own impls), leaving that case to
the next anchor. The
[`open_dispatch_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/open_dispatch_use_site.rs)
fixture pins the path re-check.

**From a use site, by consumer trait.** The next anchor closes the namespace-joined gap the previous
one leaves. When a use-site failure names a **local, non-generic CGP consumer trait** in the
diagnostic (an `E0599` note such as `` `CanGreet` defines an item `greet` `` points its span at the
trait definition), `resolve_use_site_consumer` recovers that consumer trait and the context ADT from
the diagnostic's spans and seeds `Ctx: CanGreet` directly, no marker involved. The walk then
descends through the context's joined namespace to the real provider and its missing dependency: a
namespace join gives the context only a blanket `DelegateComponent<__Key__>` forwarding, so its
concrete wiring is invisible to the per-component anchor above, but the trait solver resolves the
delegate *through* the namespace's `RedirectLookup` when the walk normalizes it. This anchor is
restricted to a consumer whose only generic is `Self`, so the obligation forms without the component
parameters a use site does not carry. It reaches not only namespace-joined method calls
([`namespace_join_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/namespace_join_use_site.rs))
but any failure that names a local consumer and its context in its spans, including a manual
supertrait bound in a trait definition or `where` clause (the `use_type_*_unsatisfied` fixtures
under
[`checks/check-trait-failure/use-type/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/use-type)).
A directly-wired context keeps the more precise per-component recovery.

**From the call expression itself.** The seventh anchor, `resolve_call_site`, handles the use-site
failure whose spans touch *nothing* the other anchors can read. Two shapes reach it. In the first, a
context's wiring matches the called component unconditionally, so the method is *found*, the failure
is an `E0277` rather than an `E0599`, and its spans never leave the call. In the second, the called
method belongs to a `#[cgp_fn]`/`#[blanket_trait]` **blanket trait** rather than a CGP consumer.
That is a blanket-impl trait that is not a component, so the by-consumer anchor (restricted to CGP
consumers) declines its `E0599`; the anchor finds it by method name and gives the result the
`[CGP-E003]` code. Either way it re-reads the failing call expression from HIR. It takes the context
from the method's *receiver*, the component's parameters by *unifying the call's written argument
types against the method's own declared signature*, and seeds every parameter the call leaves to
inference as a rigid placeholder the walk resolves around. It is the one anchor whose recovery works
from the code the programmer wrote rather than from the diagnostic's spans, and its rationale,
mechanics, and worked example have their own document:
[Typed resolution: the call-site anchor](typed-resolution-call-site.md).

**From a call to an extensible-data operation.** The eighth anchor, `resolve_data_call`, re-reads a
failing call to one of CGP's builder, extractor, or cast operations (`build_field`,
`extract_field`, `downcast`, `Shape::from_variant`), whose value is usually another data
operation's result or a remainder a pattern binds, not a context. It types that value through the
chain of operations that produced it, seeds the call the way the seventh anchor does, and gives the
result the `[CGP-E050]` code. It takes two diagnostic shapes no other anchor sees: an `E0599` "no
method named" (a finalize on a builder with a field unset) and an `E0308` on a tag argument (a
variant extracted twice). The same document covers it.

**From a call to a provider's own method.** The ninth anchor, `resolve_provider_call`, re-reads a
call that names a provider and calls its provider trait's method directly
(`PipeHandlers::<…>::compute(&(), …)`, `Add::try_compute(&App, …)`), with no consumer trait between
them. It seeds the provider obligation from the call, the provider read off the path and the
context and component parameters off the arguments, and walks it as a `#[check_providers]` entry's
obligation is walked, so the result is the provider class `[CGP-E002]`. The same document covers
it.

**From a bound of a called generic function.** The tenth anchor, `resolve_bound_call`, reads a
call to a generic function by path (`fail::<App>()` for `fn fail<Context: CanRaiseError<String>>()`,
or `greet_twice(&person)` for `fn greet_twice<Context: CanGreet>(…)`), whose `E0277` names a bound
the call instantiates rather than a trait the call invokes. It instantiates the function's own
`where` clauses with the type arguments the turbofish and the arguments write, and seeds each
consumer-trait or blanket-trait bound on a context that does not hold. It is gated to `E0277` and
tried before the by-blanket-trait anchor, so the tree starts at the bound the call requires rather
than at a trait deeper in the chain that rustc's notes name. The same document covers it.

**Recognizing a blanket trait.** Three of the anchors (the impl-site, the call-site, and the
by-blanket-trait use-site anchors) reach a `#[cgp_fn]`/`#[blanket_trait]` **blanket trait**: a trait
consumed like a consumer but which is not a component, so no marker or provider trait identifies it.
The only structural mark it carries is a blanket impl over a bare context, and that alone is far too
broad to key on: `ToString`, `Into`, and `Borrow` all have one, and reshaping their failures into
CGP errors would be an over-reach. A CGP crate's own ordinary blanket traits carry one too
(`impl<T: Clone> Describe for T`). So `is_blanket_trait` accepts a trait, local or foreign, only
when its blanket genuinely depends on CGP: on a trait from cgp's own crates (`HasField` above all),
on a CGP consumer trait, or on another blanket trait that does, followed a few links through
composed blanket traits. That admits the `#[cgp_fn]` output of the checked crate and a blanket trait
a *library* publishes, which is where such traits normally live
([`upstream_blanket_trait_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/upstream_blanket_trait_use_site.rs)),
while a plain blanket trait in either place keeps rustc's diagnostic
([`local_blanket_trait_reached`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/local_blanket_trait_reached.rs)).
A blanket trait CGP's own crates define, an extensible-data cast or builder such as `CanUpcast`, is
not a blanket trait in this sense: the data-call anchor reaches it instead, and its failure takes
the `[CGP-E050]` class
([`upcast_missing_variant`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_missing_variant.rs)).

**From a use site, by blanket trait.** The eleventh anchor,
`resolve_use_site_blanket_trait`, is the by-consumer anchor's counterpart for a
`#[cgp_fn]`/`#[blanket_trait]` **blanket trait**, a blanket-impl trait that is not a CGP component.
It reaches the shape a blanket trait required through a `where` **bound** or supertrait produces:
an `E0277` naming the blanket trait, with no method call on a concrete context for the call-site
anchor to read. A bound of the called function itself (`fn greet_all<Context: GetName>(…)` called
with a context missing the field) is the bound-call anchor's, tried just before. It
recovers the blanket trait from the diagnostic's spans (as the by-consumer anchor recovers a
consumer), and the context from the **failing expression itself** (the call argument whose type
fails: `app`, read off its binding by the call-site anchor's `contexts_at_spans`), because rustc
puts its "not implemented for `App`" span on the context's `#[derive(HasField)]` attribute,
*outside* the struct's item span, so no struct-definition span carries it. The by-consumer anchor
reads the same expressions. Neither takes a struct as the context for a span on its generics: for
`struct Holder<T: GetName>`, rustc's "required by a bound in `Holder`" note lands there, and `Holder`
only passes the requirement on. The walk then descends
`Ctx: BlanketTrait` to the cause, and the result takes the `[CGP-E003]` code (not `[CGP-E001]`)
since a blanket trait is not a component. It is gated to the `E0277` shape and tried **after** the
call-site anchor deliberately: an `E0599` method call belongs to the call-site anchor, and a
*generic-consumer* method call whose deep blanket-trait bound is unrecoverable
(`generic_consumer_unwritten_arg`) must stay declined rather than latch onto that transitive trait.

**From a forwarding entry.** The twelfth and last anchor, `resolve_forwarding_entry`, reads an
error on a `Key -> Table` entry of `delegate_components!`. The entry lowers to
`impl DelegateComponent<Key> for Context where Table: DelegateComponent<Key>`, with the bound
spanned onto the entry's `->`, so when the table lacks the key the compiler reports that bound, and
the unsized `Delegate` projection it leaves, at the `-> Table` caret, before any check or call that
uses the entry. The anchor matches the local entry whose forwarding bound lies inside the caret and
seeds the consumer obligation that entry wires, `Context: Consumer` for a bare component marker
without parameters, so the walk descends the forwarding into the table and ends at its missing
entry, as a check of the component does
([`direct_delegation_missing_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/direct_delegation_missing_key.rs)).
The result is the consumer class `[CGP-E001]`, and a later report of the same failure, the check's
or the projection's, de-duplicates against it. It is gated to `E0277`, takes only an error whose
caret holds the forwarding bound
([`unrelated_error_beside_forwarding_entry`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/unrelated_error_beside_forwarding_entry.rs)),
and declines an entry for a component with type parameters, whose consumer obligation needs values
the entry does not name
([`generic_component_forwarding_missing_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/generic_component_forwarding_missing_key.rs)).

## Further reading

- [Typed root-cause resolution](typed-root-cause-resolution.md): the pipeline overview, its
  boundaries, and the consolidated tests and source catalogs.
- [Typed resolution: the call-site anchor](typed-resolution-call-site.md): the seventh to tenth
  anchors.
- [Typed resolution: walking to the root cause](typed-resolution-walk.md): the descent every
  anchor's seed feeds.

## Tests

Every anchor is pinned end to end by the UI snapshot suite; the consolidated fixture catalog, with
one entry per pinned behavior, lives in the parent document's
[Tests](typed-root-cause-resolution.md#tests) section. The check-entry seed's params-slot
ungrouping, the impl-site and wrapper-chain paths, and the span-matching use-site paths are the
groups anchored here. The driver's
[`tests/driver/anchors.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/anchors.rs)
unit-tests the list's gates and the data-call entry's check.

## Source

- [`crates/cargo-cgp-driver/src/resolve/anchors.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/anchors.rs):
  `AnchorInput`, what the anchors read from a diagnostic, and the ordered list `resolve` tries.
- [`crates/cargo-cgp-driver/src/resolve/anchor/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/anchor):
  one file per anchor (`check_failure.rs`, `provider_check.rs`, `impl_site.rs`, `wrapper_chain.rs`,
  `use_site.rs`, `forward_entry.rs`, and `use_site_consumer.rs`, which holds both the by-consumer `resolve_use_site_consumer` and its
  by-blanket-trait sibling `resolve_use_site_blanket_trait` over one shared helper) over the shared
  `seed.rs` (the consumer-obligation builder) and `spans.rs` (the local items a diagnostic's spans
  land on, and `is_about_impl`, whether a caret inside an impl is about it, over the rustc-free
  `caret_place`). The by-blanket-trait
  anchor recovers its context from the failing expression through the call-site anchor's
  `contexts_at_spans`.
- [`crates/cargo-cgp-driver/src/resolve/query/cgp_item/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/query/cgp_item):
  the DefId-anchored, `IsProviderFor`-free trait recognition every anchor relies on.

The per-file map of the whole resolver lives in the parent document's
[Source](typed-root-cause-resolution.md#source) section.
