# `IsProviderFor`

`IsProviderFor<Component, Context, Params>` is the marker trait that every CGP provider trait
carries as a supertrait. It repeats a provider's `where` bounds on a separate path, so an unmet
dependency is reported as a readable compiler error instead of being hidden.

## Purpose

`IsProviderFor` makes missing dependencies diagnosable. A provider implements its provider trait
under a `where` clause listing what it needs from the context. When that clause is unmet, asking
whether the provider implements the provider trait gets an unhelpful answer: Rust reports only that
the trait is not implemented. The provider blanket impl from
[`#[cgp_component]`](../macros/cgp_component.md) is a second candidate for the same trait, and when
more than one impl could apply, Rust withholds the reasons each one failed.

`IsProviderFor` is an independent path with only one candidate. The macros implement it for a
provider under exactly the provider trait impl's `where` bounds, and since no blanket impl competes,
Rust commits to that impl and reports which bound failed. The trait has no behavior; its value is
making the dependency set visible along a path Rust will explain.

Users rarely name it. It is plumbing that the macros generate and
[`check_components!`](../macros/check_components.md) consumes, and it matters to anyone reading a
wiring error or building higher-order providers.

## Definition

`IsProviderFor` is an empty trait:

```rust
pub trait IsProviderFor<Component, Context, Params: ?Sized = ()> {}
```

The parameters identify one provider trait implementation:

- **`Self`** is the provider whose validity is asserted.
- **`Component`** is the component's marker, the same key used in delegation tables.
- **`Context`** is the context the provider trait is implemented for.
- **`Params`** holds the provider trait's other generic parameters: one parameter as itself, several
  as a tuple, and none as the default `()`. So a provider trait with parameters `<I, J>` uses
  `Params = (I, J)`, and one with `<Shape>` uses `Shape`, which the generated supertrait writes as
  `(Shape)`, a parenthesized type rather than a tuple. A lifetime parameter is lifted into
  [`Life<'a>`](../types/life.md). Asserting a one-parameter marker with a one-element tuple, as
  `IsProviderFor<AreaCalculatorComponent, App, (Rectangle,)>`, is a different bound, and rustc adds
  ``help: for that trait implementation, expected `Rectangle`, found `(Rectangle,)` ``.

The trait is in the prelude. It carries no `#[diagnostic::on_unimplemented]` attribute; diagnostics
are left to [cargo-cgp](../cargo-cgp.md).

## Behavior

Three macros generate the pieces that form the diagnostic chain:

- **[`#[cgp_component]`](../macros/cgp_component.md)** gives every provider trait `IsProviderFor` as
  a supertrait. For a component `CanGetFooAt<I, J>` with provider `FooGetterAt`, the provider trait
  is `pub trait FooGetterAt<Context, I, J>: IsProviderFor<FooGetterAtComponent, Context, (I, J)>`.
  Any use of the provider trait must therefore establish `IsProviderFor`, which is why probing the
  marker is equivalent to probing the provider's dependencies.
- **[`#[cgp_provider]`](../macros/cgp_provider.md) and [`#[cgp_impl]`](../macros/cgp_impl.md)**
  emit, beside each provider trait impl, an empty `IsProviderFor` impl for the same provider with
  the same `where` clause. The marker holds exactly when the provider trait impl applies.
- **[`delegate_components!`](../macros/delegate_components.md)** emits, for every table entry, an
  impl on the table that forwards to the delegate's own marker:

```rust
impl<__Context__, __Params__> IsProviderFor<FooGetterAtComponent, __Context__, __Params__>
    for MyAppComponents
where
    GetFooValue: IsProviderFor<FooGetterAtComponent, __Context__, __Params__>,
{}
```

A provider trait impl written without `#[cgp_provider]` gets no marker impl, so it fails its own
supertrait with
``the trait bound `GreetHello: IsProviderFor<GreeterComponent, Context>` is not satisfied``.
When a check fails on a provider's dependency, the notes run from the check through
``required for `GreetHello` to implement `IsProviderFor<GreeterComponent, Person>` `` down to the
`#[uses(HasName)]` attribute that introduced the unmet bound. Two `check_components!` blocks in one
module both declare `__Check{Context}`, so a second one, such as a `#[check_providers(...)]` block
beside a context check, needs its own `#[check_trait(Name)]`.

The forwarding impl is what carries dependencies across layers. When a context delegates to an
[aggregate provider](../../concepts/aggregate-providers.md) that delegates further, each table
forwards to the next, so a requirement unmet several tables deep still reaches the point where the
component is checked. The entry's key need not be a component marker; the impl is emitted for every
entry, whatever its key.

## Examples

A provider that needs a field gets a matching marker impl automatically:

```rust
use cgp::prelude::*;

#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}

#[cgp_impl(new GreetHello)]
impl Greeter
where
    Self: HasField<Symbol!("name"), Value = String>,
{
    fn greet(&self) {
        println!("Hello, {}!", self.get_field(PhantomData));
    }
}

#[derive(HasField)]
pub struct App {
    pub first_name: String,
}

delegate_components! {
    App {
        GreeterComponent: GreetHello,
    }
}

check_components! {
    App {
        GreeterComponent,
    }
}
```

`#[cgp_impl]` emits both the `Greeter` impl and an `IsProviderFor<GreeterComponent, Context, ()>`
impl for `GreetHello`, each guarded by the `HasField` bound. `App` has `first_name`, not `name`, so
the check fails. It asserts `App: CanUseComponent<GreeterComponent>`, which requires
`GreetHello: IsProviderFor<GreeterComponent, App, ()>`, and the compiler reports the missing
`HasField<Symbol!("name")>` bound rather than a bare "provider trait not implemented".

The marker can also be asserted directly, which is what the `#[check_providers(...)]` form of
`check_components!` does for a provider the context does not delegate to:

```rust
fn assert_provider()
where
    GreetHello: IsProviderFor<GreeterComponent, App, ()>,
{}
```

## Related constructs

These constructs are the ones `IsProviderFor` works with:

- [`#[cgp_component]`](../macros/cgp_component.md): attaches it as a supertrait of every provider
  trait.
- [`#[cgp_provider]`](../macros/cgp_provider.md) and [`#[cgp_impl]`](../macros/cgp_impl.md): emit
  the impl beside each provider impl.
- [`delegate_components!`](../macros/delegate_components.md) and
  [`DelegateComponent`](delegate_component.md): forward it through each table entry.
- [`CanUseComponent`](can_use_component.md): the context-side counterpart built on it.
- [`check_components!`](../macros/check_components.md): asserts it, directly with
  `#[check_providers(...)]` or through `CanUseComponent`.

## Source

- The trait is defined in
  [crates/core/cgp-component/src/traits/is_provider.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/traits/is_provider.rs)
  and re-exported through
  [crates/core/cgp-component/src/macro_prelude.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/macro_prelude.rs).
- The provider-trait supertrait link and the per-impl marker impl are emitted by
  [crates/macros/cgp-macro-core/src/types/cgp_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_component/)
  and the `#[cgp_provider]`/`#[cgp_impl]` codegen; the table forwarding impl is built in
  [crates/macros/cgp-macro-core/src/types/delegate_component/mapping/eval.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/delegate_component/mapping/eval.rs).
- For how it is generated and the index of tests, see the implementation document
  [implementation/entrypoints/cgp_component.md](../../implementation/entrypoints/cgp_component.md).
