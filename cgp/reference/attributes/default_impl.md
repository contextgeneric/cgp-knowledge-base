# `#[default_impl(...)]`

`#[default_impl(...)]` registers a [`#[cgp_impl]`](../macros/cgp_impl.md) provider as a [namespace](../../concepts/namespaces.md)'s default for a key, from the provider's own definition, by emitting one impl of the namespace's lookup trait whose `Delegate` is the provider.

## Purpose

A namespace supplies defaults that a context inherits by joining it and overrides where it needs to. Ordinarily those defaults are written in the namespace's own body, one entry per key. `#[default_impl(...)]` lets a provider register itself instead, at the point where it is defined, so the wiring sits next to the implementation it wires rather than in a distant table. Adding a per-type implementation is then one place to edit rather than two, which is the reason to reach for it once per-type defaults accumulate: a conversion, a formatter, or a codec with one provider per type.

The attribute is the provider-side half of namespace registration. [`#[prefix(...)]`](prefix.md) on a component *routes* the component to a path; `#[default_impl(...)]` on a provider *binds* a provider at a key. The two meet in the traits under [`DefaultNamespace`](../traits/default_namespace.md), and the prescriptive account of when to use the attribute, which namespace to register into, and where it stops scaling is [organizing wiring with namespaces and prefixes](../../guides/namespaces-and-prefixes.md).

## Syntax

The attribute is written on a `#[cgp_impl]` provider block and takes one argument in two parts, joined by the keyword `in`: a key, and the lookup trait to register into.

```rust
#[cgp_impl(new ShowString)]
#[default_impl(String in DefaultImpls1<ShowImplComponent>)]
impl ShowImpl<String> {
    fn show(&self, value: &String) -> String {
        value.clone()
    }
}
```

**The key becomes the emitted impl's `Self`, and the namespace path names the lookup trait plus whatever leading arguments you write inside it.** The macro appends the components-table parameter itself. So the attribute above emits `impl<__Components__> DefaultImpls1<ShowImplComponent, __Components__> for String`, with `String` in the `Self` position and `ShowImplComponent` as the trait's leading argument. The trait's own parameter names suggest the opposite arrangement, and [`DefaultNamespace`](../traits/default_namespace.md) records why.

The key takes two forms. A **type key**, as above, is the usual form for a per-type default: the type is the value of the component's dispatch parameter, and the component is named inside the lookup trait's arguments. A **path key** is a `@`-sigil path in [`Path!`](../macros/path.md)'s syntax, and it binds the provider at a full path inside the namespace. Its common use is a prefixed component's own path, so that a context that joins the namespace resolves the component with no `for` loop at all:

```rust
#[cgp_component(Greeter)]
#[prefix(@app in DefaultNamespace)]
pub trait CanGreet {
    fn greet(&self) -> String;
}

#[cgp_impl(new GreetHello)]
#[default_impl(@app.GreeterComponent in AppNamespace)]
impl Greeter {
    fn greet(&self) -> String {
        "Hello!".to_owned()
    }
}
```

Unlike `#[prefix]`, the macro appends nothing to a path key: you write the whole path, marker included, and any dispatch type after it, as in `@test.ShowImplComponent.u32`. Segments follow [`Path!`](../macros/path.md)'s encoding, so a lowercase non-primitive identifier becomes a `Symbol` and any other segment names a type. A path key cannot declare generic parameters, and the parser accepts neither of the `[…]` and `{…}` grouping forms a [`delegate_components!`](../macros/delegate_components.md) key allows.

**The namespace path may name any trait with the lookup shape**, `Trait<…, Components> { type Delegate; }`, not only the three CGP ships. [`DefaultNamespace`](../traits/default_namespace.md) takes a component-only key, [`DefaultImpls1`](../traits/default_namespace.md) a per-type key (the usual choice), and [`DefaultImpls2`](../traits/default_namespace.md) a two-type key, and a trait of your own with the same shape works identically, which is how `DefaultImpls2` became reachable without a new construct. A namespace defined with [`cgp_namespace!`](../macros/cgp_namespace.md) is such a trait, which is what the path-key example above registers into.

**The attribute may be repeated**, one attribute per table, to register the same provider under several keys or into several namespaces. The argument itself is not comma-separated: each attribute carries exactly one `Key in NamespacePath` pair.

The registration impl carries only the parameters that name the key and the provider, plus the components table, and never the provider's `where` clause. A provider whose bounds come from [`#[uses]`](uses.md), [`#[use_type]`](use_type.md), [`#[implicit]`](implicit.md), or [`#[use_provider]`](use_provider.md) therefore registers cleanly; those bounds stay on the provider's own impl and its [`IsProviderFor`](../traits/is_provider_for.md), where a real context checks them. The one thing this rules out is a generic impl; see Known issues.

Where the attribute may be *written* follows Rust's orphan rule, because the emitted impl is `impl Namespace<…> for Key`. The impl is legal when the crate owns the namespace trait, or when a local type appears in the impl header ahead of the table parameter: the key itself, or a component named inside the namespace path, as in `String in DefaultImpls1<LocalComponent>`. A path key is a `PathCons` list, which is never a local type even when it contains a local marker, so a path key can be registered only into a namespace the crate owns. A crate that needs to bind a foreign prefixed component into a foreign namespace defines a local namespace that inherits the foreign one and registers there, or writes the entry in a namespace body it owns.

## Syntax Grammar

The attribute argument of `#[default_impl]` is a key, the keyword `in`, and a namespace path:

```ebnf
DefaultImplArgs -> Key `in` NamespacePath

Key             -> Type | Path

Path            -> `@` PathSegment ( `.` PathSegment )*
PathSegment     -> Type

NamespacePath   -> TypePath GenericArgs?
```

`Key` is either a Rust `Type`, which becomes the emitted impl's `Self`, or a `Path`, which is [`Path!`](../macros/path.md)'s own production and lowers to a `PathCons` list in the same position. The two are told apart by the leading `@`. `NamespacePath` is a Rust type path with the lookup trait's leading arguments written out; the table argument is appended by the macro and must not be given. Each attribute takes exactly one such argument, and the attribute may be repeated.

## Expansion

`#[default_impl(...)]` adds one impl to the items `#[cgp_impl]` emits, after the provider impl, its `IsProviderFor` impl, and the struct a `new` keyword declares: an impl of the named lookup trait for the key, whose `Delegate` is the provider. From the type-key example above:

```rust
impl<__Components__> DefaultImpls1<ShowImplComponent, __Components__> for String {
    type Delegate = ShowString;
}
```

and from the path-key example, with the path lowered to a `PathCons` list that `cargo cgp expand` resugars to `Path!(@app.GreeterComponent)`:

```rust
impl<__Components__> AppNamespace<__Components__>
    for PathCons<Symbol!("app"), PathCons<GreeterComponent, Nil>>
{
    type Delegate = GreetHello;
}
```

`__Components__` is the table the lookup runs against. The macro appends it to the lookup trait's arguments and adds it to the impl's generic list, so one registration serves every context that consults the table. The impl's generic list otherwise copies the provider impl's parameters, but its `where` clause is dropped: by the time the attribute is lowered, `#[implicit]`, `#[uses]`, `#[use_type]`, and `#[use_provider]` have pushed their `Self`-keyed bounds into that clause, and on the registration impl `Self` is the key, so a retained `Self: HasErrorType` would demand `String: HasErrorType` or `PathCons<…>: HasErrorType` and never hold. The impl is re-spanned onto the key token, so a conflict between two registrations for one key is reported on the key rather than on the whole attribute.

A context consumes the registration in one of two ways. A path key is resolved by the namespace join alone: `namespace AppNamespace;` on a context emits a blanket `DelegateComponent` impl forwarding every key through the namespace, the component's `#[prefix]` redirects `GreeterComponent` to `@app.GreeterComponent`, and the registration impl answers that path with `GreetHello`. A type key is pulled in by a `for … in` loop of [`delegate_components!`](../macros/delegate_components.md), whose generated impl projects the default: `for <T, Provider> in DefaultImpls1<ShowImplComponent> { @test.ShowImplComponent.T: Provider }` emits a `DelegateComponent` impl `where T: DefaultImpls1<ShowImplComponent, App, Delegate = Provider>`, one entry per registered type. Because the loop variables appear only in that bound and in the key, the key must mention them, or the impl is rejected with `E0207`.

## Examples

A per-type default registered on the provider and pulled into a context, which overrides one type directly:

```rust
use cgp::core::component::DefaultImpls1;
use cgp::prelude::*;
use core::fmt::Display;

#[cgp_component(ShowImpl)]
#[prefix(@test in DefaultNamespace)]
pub trait Show<T> {
    fn show(&self, value: &T) -> String;
}

#[cgp_impl(new ShowString)]
#[default_impl(String in DefaultImpls1<ShowImplComponent>)]
impl ShowImpl<String> {
    fn show(&self, value: &String) -> String {
        value.clone()
    }
}

#[cgp_impl(new ShowWithDisplay)]
impl<T: Display> ShowImpl<T> {
    fn show(&self, value: &T) -> String {
        format!("{value}")
    }
}

pub struct App;

delegate_components! {
    App {
        namespace DefaultNamespace;

        for <T, Provider> in DefaultImpls1<ShowImplComponent> {
            @test.ShowImplComponent.T: Provider,
        }

        @test.ShowImplComponent.u64: ShowWithDisplay,
    }
}
```

`App` is an **environmental context** and `Show<T>` is **parameter-targeted**: the shown value is the parameter, and `App` only carries the wiring. The loop wires every type with a registered default, and the direct `u64` line shadows whatever the namespace would otherwise supply for that type. `DefaultImpls1` is not in the prelude and comes from `cgp::core::component`.

## Related constructs

`#[default_impl(...)]` binds where [`#[prefix(...)]`](prefix.md) routes; together they let a component's crate and a provider's crate contribute to a namespace that neither defines. The lookup traits it targets, and the positional rule that makes the key the impl's `Self`, are documented under [`DefaultNamespace`](../traits/default_namespace.md). A namespace defined with [`cgp_namespace!`](../macros/cgp_namespace.md) is an equally valid target, and its body entries are the alternative when the defaults belong together as a set or must live outside the provider's crate. [`delegate_components!`](../macros/delegate_components.md) consumes a registration through its `namespace` statement and its `for … in` loop, and [`RedirectLookup`](../providers/redirect_lookup.md) is the delegate a routed lookup passes through before the registration answers it. The host is [`#[cgp_impl]`](../macros/cgp_impl.md), and [`IsProviderFor`](../traits/is_provider_for.md) is where a registered provider's real bounds are checked.

## Known issues

A provider whose impl is generic cannot register a default. The registration impl copies the provider impl's generic parameters but drops its `where` clause, and nothing in `impl DefaultImpls1<ShowImplComponent, __Components__> for String { type Delegate = ShowWithDisplay; }` mentions a parameter such as `T`, so the compiler rejects it with `E0207` (`the type parameter 'T' is not constrained by the impl trait, self type, or predicates`), with the caret on the parameter in the impl header. This holds even when the provider struct itself is not generic, as `ShowWithDisplay` above is not. Write per-type defaults for concrete impls, and wire a generic provider in a namespace body or directly on the context instead.

Two registrations for one key in one table conflict. Each emits an impl of the lookup trait for the same key, and the compiler rejects the second with `E0119` (`conflicting implementations of trait 'DefaultImpls1<ShowImplComponent, _>' for type 'String'`). Both carets land on the key tokens inside the two attributes, because the impl is re-spanned onto its key. The same conflict arises between a `#[default_impl(GreeterComponent in DefaultNamespace)]` and a `#[prefix(… in DefaultNamespace)]` on the same component, since both emit an impl of `DefaultNamespace` for the marker.

A registered default is a fallback, not an assignment. A context's direct entry for the same key shadows it silently. The reverse also holds: a context that joins a namespace cannot override a path the namespace itself binds through a `#[default_impl]`, because the join's blanket impl already covers that path and a direct entry collides with it under `E0119`; this is the [namespace override conflict](../../errors/wiring/namespace-override-conflict.md) error class, and the reason the [guide](../../guides/namespaces-and-prefixes.md) registers prefixes and defaults into different namespaces.

A path key for a component registered into a namespace the crate does not own fails the orphan rule with `E0210`, because a `PathCons` list is never a local type; this is the [orphan-rule violation](../../errors/wiring/orphan-rule.md) error class, and the reason `#[default_impl]` on prefixed components is confined to the namespace's own crate. An unprefixed type key keyed on a foreign component into a foreign namespace fails the same way.

Writing the table parameter yourself, as in `DefaultImpls1<ShowImplComponent, App>`, makes the trait's arity wrong once the macro appends `__Components__`, and the compiler rejects the impl for supplying too many generic arguments.

On the [`#[cgp_impl(Self)]`](../macros/cgp_impl.md) passthrough form the attribute is still lowered, with the provider type `Self`, so the emitted registration reads `type Delegate = Self`, which inside an impl for the key names the key itself rather than a provider. The registration is meaningless there, and the attribute cannot be used sensibly on that form; rejecting it, as the form already silently ignores `new` and a component override, would be the cleaner behavior.

## Source

- Parsing and lowering: `DefaultImplAttribute` in [crates/macros/cgp-macro-core/src/types/attributes/default_impl/attribute.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/default_impl/attribute.rs), whose `to_item_impl` builds the registration impl, drops the provider's `where` clause, and re-spans the result onto the key; the key is a `UniPathOrType` from [crates/macros/cgp-macro-core/src/types/path/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/path/).
- Collection on the provider: the `default_impls` field of `CgpImplAttributes` in [crates/macros/cgp-macro-core/src/types/attributes/cgp_impl_attributes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/cgp_impl_attributes.rs), one entry per attribute.
- Emission after the provider items: `ItemCgpImpl::lower` in [crates/macros/cgp-macro-core/src/types/cgp_impl/item.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_impl/item.rs) and the entry point [crates/macros/cgp-macro-lib/src/cgp_impl.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_impl.rs).
- The lookup traits: [crates/core/cgp-component/src/namespaces.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/namespaces.rs).
- Implementation document (the AST types, the dropped `where` clause, and the index of tests and snapshots): [implementation/asts/attributes/default_impl.md](../../implementation/asts/attributes/default_impl.md).
