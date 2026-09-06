# `#[prefix(...)]`

`#[prefix(...)]` registers a component into a [namespace](../../concepts/namespaces.md) under a type-level path prefix, from the component's own [`#[cgp_component]`](../macros/cgp_component.md) trait, so every context that joins the namespace addresses the component by that path.

## Purpose

A namespace answers a lookup by routing it: asked for a component, it says where to look next. `#[prefix(...)]` is how a component contributes its own route. The attribute emits one impl of the namespace trait for the component's marker, whose `Delegate` is a [`RedirectLookup`](../providers/redirect_lookup.md) down the prefixed path, so a context that joins the namespace and asks for the component is redirected to `@prefix.Component`, and whatever is bound at that path is the provider that runs.

The attribute records only the route. Binding a provider at the path happens elsewhere: a direct `@prefix.Component: Provider` entry on the context, an entry in the namespace's body, or a `#[default_impl(...)]` on a provider, documented under [`DefaultNamespace`](../traits/default_namespace.md). That division lets a component's crate publish the route while each application chooses the provider, and it is why nothing restricts where the attribute may be written: the emitted impl is for the marker, a type the component's crate owns, so any crate may register its own components into any namespace, including `cgp`'s `DefaultNamespace`.

Prefixes turn a flat wiring table into a tree. Components registered under `@app.auth`, `@app.finance`, and `@app.error` sort together, a reader finds one layer's wiring without reading the others, and a library can register its components into a shared namespace for applications it will never see. CGP's own components do this: [`HasErrorType`](../components/has_error_type.md) and the error components carry `#[prefix(@cgp.core.error in DefaultNamespace)]`, and the [handler family](../components/handler.md) carries `#[prefix(@cgp.extra.handler in DefaultNamespace)]`. The prescriptive account, including how to choose a prefix and which namespace to register it into, is [organizing wiring with namespaces and prefixes](../../guides/namespaces-and-prefixes.md).

## Syntax

The attribute is written on a trait that carries `#[cgp_component]`, or one of the macros built on it, [`#[cgp_type]`](../macros/cgp_type.md) and [`#[cgp_getter]`](../macros/cgp_getter.md). Its argument is a path, the keyword `in`, and the namespace to register into:

```rust
#[cgp_component(Greeter)]
#[prefix(@app in AppNamespace)]
pub trait CanGreet {
    fn greet(&self) -> String;
}
```

The path is a prefix, and the macro appends the component marker to it: this registers `GreeterComponent` at `@app.GreeterComponent`. Writing the marker in the attribute doubles it; see Known issues.

Path segments follow [`Path!`](../macros/path.md)'s encoding. A lowercase identifier that is not a primitive type name becomes a `Symbol` type-level string, so `@app` and `@cgp.core.error` are strings, and any other segment names a type, so `@MyApp.MyBarComponent` is two types. A segment cannot declare generic parameters, and the `[…]` and `{…}` grouping forms of a [`delegate_components!`](../macros/delegate_components.md) path key are not accepted, so one attribute registers under exactly one prefix.

The namespace is a type path with optional generic arguments: `DefaultNamespace`, or a namespace defined with [`cgp_namespace!`](../macros/cgp_namespace.md), possibly qualified by a module path. The macro appends the components-table argument itself.

The attribute may be repeated to register the same component into several namespaces, one attribute per namespace:

```rust
#[cgp_component(BarProvider)]
#[prefix(@MyApp.MyBarComponent in MyNamespace)]
#[prefix(@my_app.MyBarComponent in OtherNamespace)]
pub trait Bar {
    fn bar(&self);
}
```

A component with type parameters is addressed with the parameters after the marker, because the `RedirectLookup` impl appends them to the path before the lookup: a `CanShow<T>` registered under `@app` is wired with entries such as `@app.ShowImplComponent.String: ShowWithDisplay`. Lifetime parameters do not appear in the path.

## Syntax Grammar

The attribute argument of `#[prefix]` is a path, the keyword `in`, and a namespace path:

```ebnf
PrefixArgs    -> Path `in` NamespacePath

Path          -> `@` PathSegment ( `.` PathSegment )*
PathSegment   -> Type

NamespacePath -> TypePath GenericArgs?
```

`Path` is [`Path!`](../macros/path.md)'s own production: a leading `@`, then one or more `.`-separated segments, each parsed as a Rust `Type` and encoded as a `Symbol` or a named type by the rule above. It admits neither the per-segment generics nor the `[…]`/`{…}` groups of a `delegate_components!` path key. `NamespacePath` is a Rust type path with optional generic arguments. Both parts are required, and the attribute takes exactly one such argument.

## Expansion

`#[prefix(...)]` adds one impl to the items `#[cgp_component]` emits, after the standard `UseContext`, `RedirectLookup`, and `UseDelegate` provider impls: an impl of the namespace trait for the component marker, whose `Delegate` is a `RedirectLookup` down the prefixed path. From the `CanGreet` definition above:

```rust
impl<__Components__> AppNamespace<__Components__> for GreeterComponent {
    type Delegate = RedirectLookup<
        __Components__,
        PathCons<Symbol!("app"), PathCons<GreeterComponent, Nil>>,
    >;
}
```

`__Components__` is the table the lookup runs against. The macro inserts it as the leading generic of the impl and appends it as the namespace trait's last argument, leaving it generic so one registration serves every context that joins. The path is the prefix with the marker appended, a [`PathCons`](../types/path_cons.md) list that `cargo cgp expand` resugars to `Path!(@app.GreeterComponent)`. A component marker declared with generics through the `name:` key of `#[cgp_component]` carries those generics onto the impl after `__Components__`.

The impl has the same shape as a `=>` entry in a [`cgp_namespace!`](../macros/cgp_namespace.md) body: `GreeterComponent => @app.GreeterComponent` written inside the namespace emits the same item. The attribute lets the component's own crate contribute that entry, which a foreign crate could not write into the namespace's body.

Resolution then runs in three hops. A context that joins the namespace with `namespace AppNamespace;` gets a blanket `DelegateComponent` impl whose `Delegate` is whatever the namespace answers, so asking `App` for `GreeterComponent` yields `RedirectLookup<App, Path!(@app.GreeterComponent)>`. That provider's impl of `Greeter` looks the path up in `App`'s own table, as `App: DelegateComponent<Path!(@app.GreeterComponent)>`, and forwards to the delegate it finds there. For a component with type parameters, `RedirectLookup` first appends the parameters to the path through `ConcatPath`, which is why per-type entries carry them after the marker.

The namespace's key is the marker, not the path. That is why a `help:` list in an unsatisfied-bound error names `GreeterComponent` as implementing the namespace trait even when the path it routes to has nothing bound; see the [unregistered namespace path](../../errors/checks/unregistered-namespace-path.md) error class.

## Examples

A component registered into `DefaultNamespace` under `@app`, a provider, and a context that joins the namespace and binds the provider at the prefixed path:

```rust
use cgp::prelude::*;

#[cgp_component(Greeter)]
#[prefix(@app in DefaultNamespace)]
pub trait CanGreet {
    fn greet(&self) -> String;
}

#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self, #[implicit] name: &str) -> String {
        format!("Hello, {name}!")
    }
}

#[derive(HasField)]
pub struct App {
    pub name: String,
}

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

`app.greet()` looks up `GreeterComponent`. `App` does not wire it directly, so the lookup falls through to `DefaultNamespace`, which redirects to `@app.GreeterComponent`, and `App`'s own table binds that path to `GreetHello`. `App` is an **environmental context** and the capability is **self-targeted**. A second context joins the same namespace and binds a different provider at the same path, with nothing repeated between the two. The prefixes CGP's own components carry are wired the same way: a context joining `DefaultNamespace` chooses its error type with `@cgp.core.error.ErrorTypeProviderComponent: UseType<String>` and an error strategy with `@cgp.core.error.ErrorRaiserComponent.String: ReturnError`, the dispatch type written after the generic component's marker.

## Related constructs

`#[prefix(...)]` is the component-side half of the namespace pattern. [`cgp_namespace!`](../macros/cgp_namespace.md) defines the namespaces a prefix registers into, and its `=>` body entry emits the same impl from the namespace's side. [`delegate_components!`](../macros/delegate_components.md) carries the `namespace` statement that joins a namespace and the `@`-path entries that bind a provider at a prefixed path; its `open` statement is the lightweight alternative for a component wired directly on one context, and the two do not combine on the same component. `#[default_impl(...)]`, documented under [`DefaultNamespace`](../traits/default_namespace.md), is the provider-side registration: it binds where this attribute routes. Every registration resolves through [`RedirectLookup`](../providers/redirect_lookup.md) along a [`Path!`](../macros/path.md) built from [`PathCons`](../types/path_cons.md). The hosts are [`#[cgp_component]`](../macros/cgp_component.md), [`#[cgp_type]`](../macros/cgp_type.md), and [`#[cgp_getter]`](../macros/cgp_getter.md), and [`check_components!`](../macros/check_components.md) is the only thing that catches a route bound to nothing.

## Known issues

The marker is appended by the macro, so a path that already ends in the marker doubles it: `#[prefix(@app.GreeterComponent in Ns)]` registers the component at `@app.GreeterComponent.GreeterComponent`. The definition compiles, and a context that binds `@app.GreeterComponent` then finds its entry never consulted, because the route and the binding name different paths.

Registering routes a component and binds nothing. A prefixed component compiles even when nothing binds its path, and so does a context that joins the namespace; only a `check_components!` reports it, as an `E0277` on the path rather than on a provider. This is the [unregistered namespace path](../../errors/checks/unregistered-namespace-path.md) error class.

Two `#[prefix]` attributes naming the same namespace each emit an impl of that namespace's trait for the same marker, and the compiler rejects the second with `E0119` (`conflicting implementations of trait 'AppNamespace<_>' for type 'GreeterComponent'`). Both carets land on the `#[cgp_component]` attribute rather than on the two `#[prefix]` attributes, because `to_namespace_impl` builds the impl from `call_site`-spanned tokens, so the message does not say which registration is the duplicate. Re-spanning the emitted impl onto its `#[prefix]` attribute, as `delegate_components!` does for its entries, would fix that.

`open` does not reach a prefixed component in a joined namespace: `open` roots the route at the bare marker while the prefix routes under the path, so the per-value entries `open` expects are never consulted. The entries must be written with the full prefixed path, as the [namespaces concept](../../concepts/namespaces.md) explains.

Segment case decides the encoding silently. `@app` is a `Symbol` and `@App` is a type, both are valid, and a capitalization slip routes to a path nothing binds, surfacing as the unregistered-path failure above without a hint about the letter.

`#[cgp_auto_getter]` accepts the attribute and drops it. That macro runs `CgpComponentAttributes::preprocess` to apply `#[extend]` and `#[use_type]` but discards the collected prefixes, since it does not generate a component to register, so a `#[prefix]` on it registers nothing and reports nothing.

On `#[cgp_impl]` or `#[cgp_fn]` the attribute is not consumed and reaches the compiler as `cannot find attribute 'prefix' in this scope`.

## Source

- Parsing and lowering: `PrefixAttribute` in [crates/macros/cgp-macro-core/src/types/attributes/prefix.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/prefix.rs), whose `to_namespace_impl` builds the namespace impl.
- Collection on the component: the `prefixes` field of `CgpComponentAttributes` in [crates/macros/cgp-macro-core/src/types/attributes/cgp_component_attributes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/cgp_component_attributes.rs).
- Emission after the standard provider impls: `to_prefix_impls` in [crates/macros/cgp-macro-core/src/types/cgp_component/evaluated/item.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_component/evaluated/item.rs); the `RedirectLookup` impl the route resolves through is built in [to_redirect_lookup_impl.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_component/evaluated/to_redirect_lookup_impl.rs).
- Path parsing: `UniPath` and `PathElement` in [crates/macros/cgp-macro-core/src/types/path/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/path/).
- Implementation documents (the component pipeline that emits the prefix impl, the namespace machinery, and the index of tests and snapshots): [implementation/entrypoints/cgp_component.md](../../implementation/entrypoints/cgp_component.md) and [implementation/asts/namespace.md](../../implementation/asts/namespace.md).
