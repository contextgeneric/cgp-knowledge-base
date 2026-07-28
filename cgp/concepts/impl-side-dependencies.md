# Impl-side dependencies

The core idea of CGP is dependency injection through the `where` clause of a blanket impl: a clean trait interface hides the constraints its implementation needs, so a context that satisfies those constraints gains the capability without ever naming them.

## The problem

Generic code needs dependencies, and the usual way of declaring them — a `where` clause on a generic function — leaks those dependencies to every caller. A function `fn greet<Context>(ctx: &Context) where Context: HasName` forces its constraint onto its signature, so any generic caller of `greet` must repeat `Context: HasName`, and that caller's callers must repeat it again. The bounds propagate outward through the whole call graph, and a function deep in a library can end up demanding that its distant callers spell out requirements they have no direct interest in.

CGP removes this leak by moving the dependency off the interface and onto an implementation. The capability is exposed as a trait whose declaration mentions none of its requirements; the requirements live only in the `where` clause of the impl that satisfies the trait. A caller bounds on the clean trait alone, and the requirements stay hidden one level down — which is precisely what stops them from cascading through transitive callers.

## How CGP expresses it

The mechanism is a blanket impl whose `where` clause carries the hidden constraints. A trait `CanGreet` exposes only `greet`; its blanket impl over a generic context requires `Context: HasName`, so any context implementing `HasName` automatically implements `CanGreet`, while a caller bounding on `CanGreet` never sees `HasName`.

```rust
use cgp::prelude::*;

pub trait CanGreet {
    fn greet(&self);
}

impl<Context> CanGreet for Context
where
    Context: HasName,
{
    fn greet(&self) {
        println!("Hello, {}!", self.name());
    }
}
```

This constraint-hiding is why a blanket impl is preferred over a generic function for the same logic: the dependency `HasName` is injected at the impl, not demanded at the interface, so transitive callers carry nothing. The same `where` clause that would bloat a function's signature becomes invisible plumbing on the impl. Writing this impl by hand is repetitive — the supertrait bounds are stated twice and each default body is copied — which is the boilerplate [`#[blanket_trait]`](../reference/macros/blanket_trait.md) removes: you declare the trait with its supertraits and default bodies, and the macro generates the matching blanket impl.

## How it scales up

The same `where`-clause injection appears at every level of CGP, from the simplest extension trait to full components. A [`#[blanket_trait]`](../reference/macros/blanket_trait.md) hides trait dependencies declared as supertraits; a [`#[cgp_component]`](../reference/macros/cgp_component.md) provider hides them in the `where` clause of its provider impl, where they are also captured by [`IsProviderFor`](../reference/traits/is_provider_for.md) so a missing one is reported clearly. In both cases the dependency is a constraint on the implementation that the public interface does not mention. The difference is only that a component admits many alternative providers selected by wiring, while a blanket trait admits exactly one.

Stating those dependencies is made to read like importing them rather than constraining `Self`. The [`#[uses(...)]`](../reference/attributes/uses.md) attribute turns `#[uses(HasName)]` into a `Self: HasName` predicate on the generated impl, so a provider declares the capabilities its body calls in a line that reads like a `use` statement — the dependency lands on the impl, hidden from anyone who uses the trait. This is the same injection as a hand-written `where Self: HasName`, dressed to match a programmer's existing intuition.

## Value dependencies, not just trait dependencies

Impl-side dependencies inject values as readily as they inject capabilities, through the same `where`-clause mechanism keyed on fields instead of traits. A provider that needs a `name` value declares `Context: HasField<Symbol!("name"), Value = String>` in its `where` clause and reads it with `get_field`; any context that derives [`HasField`](../reference/derives/derive_has_field.md) and happens to have a matching field satisfies the bound, with the field never appearing in any interface. The field requirement is injected at the impl exactly as a trait requirement is.

Because the raw `HasField` bound is verbose, the surface syntax hides it the same way [`#[uses(...)]`](../reference/attributes/uses.md) hides a trait bound. A getter method written with [`#[cgp_auto_getter]`](../reference/macros/cgp_auto_getter.md) generates the `HasField` bound from the method name, and an [`#[implicit]`](../reference/attributes/implicit.md) function argument generates it from the argument name — both producing the same injected constraint from familiar-looking code. That value-injection model, where providers look like functions taking arguments sourced from context fields, is the subject of [implicit arguments](implicit-arguments.md).

## Type dependencies, and why they need no parameter

The injection reaches *types* as well, and this is where it buys the most, because the alternative it displaces is not a leaked bound but a leaked **parameter**. A provider that needs a type it does not fix — an error type, a scalar, a database handle — declares an [abstract-type](abstract-types.md) trait as a bound and names the type through it: `Self: HasErrorType` on the impl makes `<Self as HasErrorType>::Error` available to the body, and any context that wires the component satisfies the bound. The requirement is injected at the impl exactly as a field or a capability is.

What makes the type case different is *where the choice lives*. A generic parameter is an **input**: the caller supplies it, so it appears in the signature and every intermediate function that passes a value along has to declare it and repeat its bounds — the same outward propagation the [problem section](#the-problem) describes for a `where` clause, except a parameter cannot be hidden on an impl at all, because it is part of the interface by construction. An abstract type is an **output**: it is an associated type the context determines, so a provider names it without anyone choosing it at a call site. Nothing is threaded because there is nothing to thread.

That asymmetry survives even when the type must reach the interface, which it often must — a component whose signatures name the type has to declare the owning trait as a supertrait, so `CanLoad: HasErrorType` is genuinely part of the contract rather than hidden on an impl. It still does not leak the way a parameter would: a caller bounding on `CanLoad` gets `HasErrorType` implied, never restates it, and names the type only if it handles one, and then as `Self::Error`. Compare a `trait CanLoad<E>`, which forces every caller and every caller's caller to carry `<E>` whether they touch an error or not. The bound is on `Self`; the parameter would be on everyone.

The surface syntax hides the projection the same way `#[uses]` hides a trait bound and `#[implicit]` hides a field bound. [`#[cgp_type]`](../reference/macros/cgp_type.md) declares the abstract-type component, wiring supplies the concrete type through [`UseType<T>`](../reference/providers/use_type.md), and [`#[use_type]`](../reference/attributes/use_type.md) imports it into a definition so the author writes a bare `Error` in place of `<Self as HasErrorType>::Error` — adding the supertrait or the `where` bound at the same time. Which of the two homes a type dependency belongs in, and the two conditions that force the climb from an inferred `#[impl_generics]` parameter to an abstract type, are the subject of [naming a type dependency](../guides/naming-a-type-dependency.md).

## Related constructs

[`#[blanket_trait]`](../reference/macros/blanket_trait.md) is impl-side dependencies in their purest form: a trait with supertraits and default bodies, plus the generated blanket impl that hides those supertraits. [`#[cgp_component]`](../reference/macros/cgp_component.md) extends the pattern to providers, where the hidden constraints live in each provider's `where` clause and many providers can coexist — see [consumer and provider traits](consumer-and-provider-traits.md) for that duality, and [`IsProviderFor`](../reference/traits/is_provider_for.md) for how the hidden dependencies are surfaced in error messages.

The injection is declared idiomatically through [`#[uses(...)]`](../reference/attributes/uses.md) for trait dependencies, through [`HasField`](../reference/traits/has_field.md) for value dependencies, and through [`#[use_type]`](../reference/attributes/use_type.md) over a [`#[cgp_type]`](../reference/macros/cgp_type.md) component for type dependencies. Each has a concept of its own that develops one leg in full: [implicit arguments](implicit-arguments.md) dresses `HasField` reads as ordinary function parameters, and [abstract types](abstract-types.md) does the same for the types a context chooses. The prescriptive companion for the type leg — inferred parameter or abstract type, and what forces the choice — is [naming a type dependency](../guides/naming-a-type-dependency.md).
