# `RedirectLookup<Key, Components>`

`RedirectLookup` is a zero-sized provider that implements a component's provider trait by looking a
type-level path up in a table, instead of looking the component up in the context directly. It is
the mechanism behind the `open` statement and namespaces.

## Purpose

`RedirectLookup` separates the key a component is looked up under from the table that answers it.
The ordinary provider blanket impl looks a component up in the context's own
[delegation table](../traits/delegate_component.md), keyed by the component's marker.
`RedirectLookup` consults a given table keyed by a given type-level path, and delegates to whatever
provider that entry holds.

This indirection lets wiring be organized by path:

- **The `open` statement** of [`delegate_components!`](../macros/delegate_components.md) wires a
  component to a `RedirectLookup` rooted at the component's own name in the context's table, so
  entries such as `@AreaCalculatorComponent.Rectangle` choose a provider per type argument.
- **A [namespace](../../concepts/namespaces.md)** routes a component to a `RedirectLookup` along the
  path the component was registered under with [`#[prefix]`](../attributes/prefix.md), so a context
  that joins the namespace binds the provider at that path.

`RedirectLookup` is never written by hand. Every `#[cgp_component]` generates its impl, and `open`,
`#[prefix]`, and the namespace machinery generate the entries that point to it.

## Definition

`RedirectLookup` is defined in `cgp-component` and exported by the prelude:

```rust
pub struct RedirectLookup<Key, Components>(pub PhantomData<(Key, Components)>);
```

The declared parameter names do not match how the type is used. Every generated impl and entry
passes the table first and the path second, as `RedirectLookup<Components, Path>`. The path is a
[`PathCons`](../types/path_cons.md) chain, usually of [`Symbol!`](../macros/symbol.md) segments and
a component marker, and the table is a type implementing
[`DelegateComponent`](../traits/delegate_component.md).

## Behavior

`#[cgp_component]` generates a `RedirectLookup` impl of the provider trait next to the
[`UseContext`](use_context.md) impl. For a trait with no type parameters:

```rust
#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self) -> String;
}
```

the impl looks the path up once and forwards to the delegate found:

```rust
impl<__Context__, __Components__, __Path__> Greeter<__Context__>
    for RedirectLookup<__Components__, __Path__>
where
    __Components__: DelegateComponent<__Path__>,
    <__Components__ as DelegateComponent<__Path__>>::Delegate: Greeter<__Context__>,
{
    fn greet(__context__: &__Context__) -> String {
        <__Components__ as DelegateComponent<__Path__>>::Delegate::greet(__context__)
    }
}
```

When the consumer trait has type parameters, the impl first appends them to the path with
[`ConcatPath`](../types/path_cons.md). Every type parameter is appended, in declaration order;
lifetime and const parameters are skipped. For `CanCompute<Code, Input>` the bound is
`__Path__: ConcatPath<PathCons<Code, PathCons<Input, Nil>>>`, so a redirect rooted at
`@ComputerComponent` looks up `@ComputerComponent.Code.Input`:

```rust
impl<__Context__, Code, Input, __Components__, __Path__> Computer<__Context__, Code, Input>
    for RedirectLookup<__Components__, __Path__>
where
    __Path__: ConcatPath<PathCons<Code, PathCons<Input, Nil>>>,
    __Components__: DelegateComponent<<__Path__ as ConcatPath<PathCons<Code, PathCons<Input, Nil>>>>::Output>,
    /* … the delegate implements `Computer<__Context__, Code, Input>` */
{ /* … forwards to the delegate */ }
```

The lookup is still a single `DelegateComponent` query on the whole extended path, not a walk
segment by segment. A table can answer a shorter prefix of the path because `delegate_components!`
generates entries generic over the remaining segments: a key that stops after `Code` matches every
`Input`, and a longer key matches a particular `Input`. The `open` section of
[`delegate_components!`](../macros/delegate_components.md) documents these key forms. The impl is
paired with an `IsProviderFor` impl, so dependencies reach the
[check traits](../../concepts/check-traits.md).

## Examples

This component registers itself under `@app` in `DefaultNamespace`, and a context binds its provider
at that path:

```rust
use cgp::prelude::*;

#[cgp_component(Greeter)]
#[prefix(@app in DefaultNamespace)]
pub trait CanGreet {
    fn greet(&self) -> String;
}

#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self) -> String {
        "hello".into()
    }
}

pub struct App;

delegate_components! {
    App {
        namespace DefaultNamespace;

        @app.GreeterComponent: GreetHello,
    }
}

check_components! {
    App {
        GreeterComponent,
    }
}
```

`#[prefix]` makes `DefaultNamespace` route `GreeterComponent` to a `RedirectLookup` over the path
`@app.GreeterComponent`. The `namespace` statement makes `App` resolve its components through that
namespace, so `App.greet()` looks up `@app.GreeterComponent` in `App`'s own table and finds
`GreetHello`. The component marker is the last segment of the path rather than a key of its own.

A context that joins the namespace cannot also bind the component at its bare key. The `namespace`
statement already gives `App` an entry for `GreeterComponent`, the one that redirects to
`@app.GreeterComponent`, so adding `GreeterComponent: GreetHello` to the same table fails with
``error[E0119]: conflicting implementations of trait `IsProviderFor<GreeterComponent, _, _>` for type `App` ``
(and the same for `DelegateComponent<GreeterComponent>`), pointing at the `namespace` statement as
the first implementation.

## Related constructs

These constructs are the ones `RedirectLookup` works with:

- [`#[cgp_component]`](../macros/cgp_component.md): generates its impl for every component.
- [`delegate_components!`](../macros/delegate_components.md): the `open` and `namespace` statements
  that produce redirects.
- [`#[prefix]`](../attributes/prefix.md), [`cgp_namespace!`](../macros/cgp_namespace.md), and
  [namespaces](../../concepts/namespaces.md): register components under paths.
- [`DelegateComponent`](../traits/delegate_component.md), [`PathCons`](../types/path_cons.md), and
  [`Symbol!`](../macros/symbol.md): the table and the path it looks up.
- [`UseContext`](use_context.md): the other generated provider, which routes back to the context.

## Source

- The struct is defined in
  [crates/core/cgp-component/src/providers/redirect_lookup.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/providers/redirect_lookup.rs),
  and the related `DefaultNamespace` trait in
  [crates/core/cgp-component/src/namespaces.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/namespaces.rs).
- The `RedirectLookup` provider impl is generated by `to_redirect_lookup_impl` in
  [crates/macros/cgp-macro-core/src/types/cgp_component/evaluated/to_redirect_lookup_impl.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_component/evaluated/to_redirect_lookup_impl.rs),
  which appends generic parameters through `ConcatPath`.
- The namespace delegates that target `RedirectLookup` are produced by the `#[prefix]` attribute in
  [crates/macros/cgp-macro-core/src/types/attributes/prefix.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/prefix.rs)
  and the redirect mapping in
  [crates/macros/cgp-macro-core/src/types/delegate_component/mapping/redirect.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/delegate_component/mapping/redirect.rs).
- For how it is generated and the index of tests, see the implementation document
  [implementation/entrypoints/cgp_component](../../implementation/entrypoints/cgp_component.md).
