# Typed resolution: anchoring the starting obligation

An anchor recovers from a failing diagnostic the **real trait obligation** that seeds the
[walk](walk.md): a consumer obligation `Ctx: ConsumerTrait<Params…>`, or the
provider obligation a `#[check_providers]` entry or a provider's own method call asserts. Twelve
anchors read twelve failure shapes, tried in the order the
[overview's table](overview.md#how-the-root-cause-is-recovered) gives, and the
first that succeeds wins. This document covers the eight that match spans; the other four re-read
the call and have [their own document](call-site.md).

Two rules protect the anchors from a false result. An anchor that chooses among candidates seeds
only an obligation that does not hold, so an unrelated bound cannot produce a chain. And an anchor
that re-anchors a diagnostic onto code it sits inside reads **primary spans only**, because rustc
points a secondary label or a note at any code the failure passed through.

## The check anchors

**A `check_components!` entry is matched by span, so its text is never read.** The entry expands to
`impl __CheckRectangle<AreaCalculatorComponent, ()> for Rectangle {}`, and the macro re-spans the
impl's `Self` type onto the entry the user wrote. So `resolve_check_failure` picks the check impl
whose `Self` span equals the caret. It reads the impl's `CanUseComponent<Marker, Params>` assertion
only to learn which component the entry names, then maps the marker to its consumer trait and walks
that obligation.

**The `Params` slot is ungrouped by the consumer's own generics, never by the slot's shape.** The
slot holds parameters as all-types data: none as `()`, one bare, several as a tuple, and a lifetime
lifted into `Life<'a>`. So the parameter count decides whether a tuple is one tuple-typed parameter
or several to spread, and a lifetime takes its region back out of the lift. Trusting the shape would
hand the solver a malformed obligation, and a `Life<'a>` type where a region belongs aborts the
compiler. Any mismatch declines
([`lifetime_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/lifetime_component.rs),
[`tuple_param_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/tuple_param_component.rs)).

**A `#[check_providers]` entry seeds the provider it lists, whatever the context wires.** Its check
impl has the provider as `Self` and `IsProviderFor<Component, Context, Params>` as the check trait's
supertrait. A component's own provider trait carries `IsProviderFor` too, so a check trait is told
apart by that supertrait's component being one of the trait's own parameters. The result is the
provider class `[CGP-E002]`, and its tree starts at the listed layer
([`check_providers_layer`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/higher-order-provider-layer/check_providers_layer.rs),
[`check_providers_unwired_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/check_providers_unwired_provider.rs)).
One attribute over several components generates impls whose errors share a caret. Their spans differ
in syntax context, which the comparison includes, so each error reads its own impl
([`check_providers_two_components`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/check_providers_two_components.rs)).

## The impl anchors

**A failure inside a hand-written impl is recovered from the impl.** A wrapper trait that adds a
bound the component cannot express is the common case
([`manual_supertrait_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/manual_supertrait_impl.rs)):

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

The caret lands on this impl, never on `App`'s definition, so a use-site anchor cannot find the
context. `resolve_impl_site` takes the impl's `Self` as the context and walks each unmet supertrait
that is a CGP consumer or a [blanket trait](#recognizing-a-blanket-trait), with its concrete
parameter intact. A plain supertrait such as `Send` is left alone. This also reshapes the idiom for
asserting that a `#[cgp_fn]` trait holds, `pub trait CheckFormatName: FormatName {}` with
`impl CheckFormatName for App {}`, in place of rustc's misleading note about `#[derive(HasField)]`
([`cgp_fn_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/cgp_fn_missing_field.rs)).

**The impl counts only when the caret is about it,** or an unrelated error would be replaced by the
CGP tree and then de-duplicated away. `is_about_impl` accepts a primary span outside every method
body, or one inside a body on a call to a method the impl's trait or a supertrait declares, which is
the forwarding call that fails because the supertrait does. An error strictly inside that call's
argument keeps its own diagnostic
([`unrelated_error_in_wrapper_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_in_wrapper_impl.rs),
[`unrelated_error_in_forwarding_argument`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_in_forwarding_argument.rs)).

**A bound of the impl's own `where` clause reads as itself.** The compiler reports a concrete bound
that fails (`where Inner: CanCompute` on a provider) at the bound, and it can fail for its own cause
beside the impl's supertrait. So before the supertrait recovery, the anchor walks an unmet CGP
consumer bound on a context at the caret, which de-duplicates into that context's own check
([`wrapper_impl_with_failing_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/wrapper_impl_with_failing_bound.rs)).
A bound on a plain Rust trait keeps rustc's diagnostic
([`impl_bound_on_plain_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/impl_bound_on_plain_trait.rs)).

**The tree is headed by the impl's own trait,** so it points at the code the programmer wrote. A
wrapper that is itself a CGP consumer takes `[CGP-E001]`, and a plain one takes `[CGP-E003]`. A
wrapper is a distinct trait from its supertrait, so its error is no re-report of the check for that
supertrait; when the two share a root cause, they [coalesce at flush](output.md).

These limits keep the anchor honest:

- **Only an impl on a context gets the supertrait recovery:** a local struct or enum, or a foreign
  type that carries its own wiring (`is_context_adt`,
  [`foreign_context_wrapper_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/foreign_context_wrapper_impl.rs)).
- **A provider-trait impl is skipped,** because its only supertrait is `IsProviderFor`, and routing
  through it would leak `__Context__` into the tree.
- **A check impl is skipped,** because it is the check anchor's, and heading a tree with it would
  present the generated `__CanUseApp` as a trait the programmer wrote.

**A wrapper on a foreign type descends to the context.** In
[`foreign_wrapper_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/foreign_wrapper_chain.rs),
`impl CanAddAppRoutes for Box<App>` reaches `App: CanHandleApi<GreetApi>` through
`Box<App>: CanAddRoute<App, GreetApi>`, so `App` appears only as a type argument.
`resolve_wrapper_chain` descends the impl's unmet supertrait through each impl's `where` clauses
until one lands on a CGP consumer on a context, and every ordinary hop becomes a node. A descent
into unrelated clauses contributes nothing, since only a CGP consumer is reported, and
`MAX_WRAPPER_DEPTH` bounds it.

The descent must re-evaluate each obligation and read predicates **un-normalized**. The direct
`App: CanHandleApiSend<GreetApi>` bound is assumed to hold off its own ill-formed impl, so the
consumer is reached through the base trait of a projection clause: `Ctx::Response: Send` over the
broken `CanHandleApi`. Normalizing would lose that base. Because `Self` here is a foreign wrapper,
the class sentence names it without the `context` qualifier (`subject_is_context` is false).

## The use-site anchors

**By wired component, the context comes from the diagnostic's spans.** CGP wiring is lazy, so a
broken dependency often surfaces at a call, as an `E0599` with no check impl behind it. rustc's
"method not found for this struct" span lands on the context's definition, so `resolve_use_site`
takes each local struct or enum a span lands in, re-checks every component it wires, and keeps those
that fail. The anchor is not limited to method calls: any failure whose spans land on the definition
reaches it, which is why a call on a field access still resolves. A span on a generic context's
definition gives `App<T>`, whose seed declines, so a call on `App<u32>` falls to the call-site
anchor, which reads the instantiation from the receiver.

Three corners matter here:

- **The candidates exclude what only looks like a context.** A provider struct is never one, nor a
  component marker, whose definition sits under the macro attribute rustc's notes point at
  ([`getter_unwired_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/getter_unwired_call.rs)),
  nor a struct whose generics a span lands on, since `Holder<T: Trait>` only passes the requirement
  on.
- **A cause several components reach is named once and keeps every route,** so each consumer the
  header lists has a chain
  ([`use_site_shared_cause`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/use_site_shared_cause.rs)).
- **A wiring key is one of several shapes, and most are not re-checkable.** A bare marker of a
  component without type parameters maps to `Ctx: Consumer`. A two-segment `open` path yields
  `Ctx: Consumer<Value>`, with the value the context really wired
  ([`open_dispatch_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/open_dispatch_use_site.rs)).
  The rest are skipped, because each would assert something nothing in the program asks for: a
  generic component's bare marker (`CanRaiseError<()>`,
  [`question_mark_after_failed_handle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/question_mark_after_failed_handle.rs)),
  a bare marker that is also `open`-dispatched, a longer path, a catch-all whose value holds a type
  parameter, and the `__Key__` a namespace join writes.

**By consumer trait, the anchor reaches a namespace-joined context.** A join gives the context only
a blanket `DelegateComponent<__Key__>`, so the previous anchor finds no target. An `E0599` note such
as `` `CanGreet` defines an item `greet` `` puts a span on the trait, so `resolve_use_site_consumer`
seeds `Ctx: CanGreet` directly, and the solver resolves the delegate through the namespace when the
walk normalizes it
([`namespace_join_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/namespace_join_use_site.rs)).
It takes only a local consumer whose one generic is `Self`, since a use site does not carry a
component's parameters. It also reaches a supertrait bound in a trait definition
([`use-type/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/use-type)).

**By blanket trait, the anchor reads a local blanket trait required as a bound elsewhere,** an
`E0277` with no method call to read. rustc puts its "not implemented for `App`" span on the
`#[derive(HasField)]` attribute, outside the struct's item span, so the context comes from the
failing expression too, read off its binding (`contexts_at_spans`). The result takes `[CGP-E003]`.
It is gated to `E0277` and tried after the call anchors: a method call belongs to the call-site
anchor, and a generic consumer whose parameter is unrecoverable must stay declined rather than latch
onto a transitive trait
([`generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs)).
A struct's bound with no expression to read keeps rustc's diagnostic
([`cgp_fn_struct_bound_in_type`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_struct_bound_in_type.rs)).

## Recognizing a blanket trait

A blanket impl over a bare context is the only structural mark a `#[cgp_fn]` or `#[blanket_trait]`
trait carries, and it is far too broad alone: `ToString`, `Into`, and a CGP crate's own
`impl<T: Clone> Describe for T` all have one. So `is_blanket_trait` accepts a trait, local or
foreign, only when its blanket bounds name a trait from CGP's crates, a CGP consumer, or another
blanket trait that does, followed a few links. That admits a trait a library publishes, where such
traits normally live
([`upstream_blanket_trait_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/upstream_blanket_trait_use_site.rs)),
while a plain one keeps rustc's diagnostic
([`local_blanket_trait_reached`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/local_blanket_trait_reached.rs)).
A blanket trait CGP's own crates define, such as `CanUpcast`, is excluded; the data-call anchor
reaches it under `[CGP-E050]`
([`upcast_missing_variant`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_missing_variant.rs)).

## The forwarding-entry anchor

A `Key -> Table` entry lowers to
`impl DelegateComponent<Key> for Context where Table: DelegateComponent<Key>`, with the bound
spanned onto the entry's `->`. So when the table lacks the key, the compiler reports that bound
before any check or call uses the entry. `resolve_forwarding_entry` finds the local entry whose
forwarding bound lies inside the caret and seeds the consumer obligation it wires, so the walk ends
at the table's missing entry, as a check of the component does
([`direct_delegation_missing_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/direct_delegation_missing_key.rs)).
A later report of the same failure de-duplicates against it.

It takes only an error whose caret holds the bound
([`unrelated_error_beside_forwarding_entry`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/unrelated_error_beside_forwarding_entry.rs)).
It declines an entry on a generic context or for a component with type parameters, whose obligation
needs values the entry does not name
([`generic_component_forwarding_missing_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/generic_component_forwarding_missing_key.rs)).

## Further reading

- [Typed root-cause resolution](overview.md): the pipeline overview, the anchor
  order, and the boundaries.
- [The call-site anchor](call-site.md): the seventh to tenth anchors.
- [Walking to the root cause](walk.md): the descent every seed feeds.

## Tests

- [The parent document's catalog](overview.md#tests): the fixture groups that pin
  the anchors.
- [`tests/driver/anchors.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/anchors.rs):
  the list's gates, and the data-call entry's acceptance.

## Source

- [`resolve/anchors.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/anchors.rs):
  what the anchors read from a diagnostic, and the ordered list.
- [`resolve/anchor/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/anchor):
  one file per anchor, with `seed.rs` building the obligations and `spans.rs` finding the items a
  diagnostic's spans land on.
- [`resolve/query/cgp_item/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/query/cgp_item):
  the structural trait recognition, `is_blanket_trait` included.
