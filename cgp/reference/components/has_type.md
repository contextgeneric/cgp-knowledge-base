# `HasType`

`HasType<Tag>` is CGP's built-in abstract-type component: it gives a context one abstract type per
tag, with `TypeProvider` as its provider trait and `TypeOf<Context, Tag>` as the alias for the
resolved type.

## Purpose

`HasType<Tag>` lets generic code name a type that each context chooses. It is an abstract type
indexed by a tag: a context can carry one abstract type per `Tag`, and wiring resolves each to a
concrete type. Generic code writes `<Self as HasType<Tag>>::Type`, or `TypeOf<Context, Tag>`, and
never names the concrete type. See [abstract types](../../concepts/abstract-types.md) for how
abstract types are used across a codebase.

It is the one abstract-type component in CGP indexed by a tag rather than named; CGP's other
abstract types, such as [`HasErrorType`](has_error_type.md) and
[`HasRuntimeType`](has_runtime.md), are named components defined with
[`#[cgp_type]`](../macros/cgp_type.md), which is also how most code defines its own. A named trait such as `HasScalarType` reads
better than `HasType<ScalarTag>` and has its own component key. The two meet at the provider level:
`#[cgp_type]` generates a `WithProvider` impl that lets any `TypeProvider` back the named component,
so a provider written once for `HasType` also serves every `#[cgp_type]` trait.

## Definition

`HasType<Tag>` is a `#[cgp_component]` whose whole source is:

```rust
#[cgp_component(TypeProvider)]
#[derive_delegate(UseDelegate<Tag>)]
pub trait HasType<Tag> {
    type Type;
}

pub type TypeOf<Context, Tag> = <Context as HasType<Tag>>::Type;
```

The parts are these:

- **`Tag`** is the type-level name that tells one abstract type from another in the same context.
- **`Type`** is the concrete type the tag resolves to.
- **`TypeProvider<Context, Tag>`** is the provider trait, named by `#[cgp_component(TypeProvider)]`,
  and `TypeProviderComponent` is its component key.
- **[`#[derive_delegate(UseDelegate<Tag>)]`](../attributes/derive_delegate.md)** generates the
  `UseDelegate` impl for the legacy per-tag delegation table.
- **`TypeOf<Context, Tag>`** is the short spelling of the resolved type.

None of these names except `HasType` and `TypeProvider` is in the prelude. `TypeProviderComponent`
and `TypeOf` are imported from `cgp::core::types`.

## Behavior

A context gets an abstract type by implementing `HasType<Tag>` directly or by wiring
`TypeProviderComponent` to a provider. As a `#[cgp_component]`, `HasType` has the standard
machinery: a consumer blanket impl that forwards to the wired provider, and the `UseContext` and
`RedirectLookup` provider impls.

The usual provider is [`UseType<Type>`](../providers/use_type.md), a zero-sized marker that sets the
abstract type to its own parameter for any context and any tag:

```rust
#[cgp_provider(TypeProviderComponent)]
impl<Context, Tag, Type> TypeProvider<Context, Tag> for UseType<Type> {
    type Type = Type;
}
```

Because the impl ignores the tag, a single `TypeProviderComponent: UseType<T>` entry answers every
tag with the same `T`. To give different tags different types, dispatch on the tag:

- **With `open`**, the recommended form, write `open TypeProviderComponent;` and then one entry per
  tag, such as `@TypeProviderComponent.ScalarTag: UseType<f64>`.
- **With a delegation table**, the legacy form, wire `TypeProviderComponent` to
  `UseDelegate<Table>`, whose table maps each tag to a provider such as `UseType<f64>`, or to
  [`UseDelegatedType<Table>`](../providers/use_delegated_type.md), whose table maps each tag
  straight to its type.

Do not confuse the `UseType` provider with the [`#[use_type]`](../attributes/use_type.md) attribute.
The attribute rewrites bare type names inside a definition and adds a bound on the abstract-type
trait it names, such as `HasScalarType`.

## Examples

This context resolves two tags to two types through `open`:

```rust
use cgp::prelude::*;
use cgp::core::types::{TypeOf, TypeProviderComponent};

pub struct ScalarTag;
pub struct NameTag;

pub struct App;

delegate_components! {
    App {
        open TypeProviderComponent;

        @TypeProviderComponent.ScalarTag: UseType<f64>,
        @TypeProviderComponent.NameTag: UseType<String>,
    }
}

fn zero<Context>() -> TypeOf<Context, ScalarTag>
where
    Context: HasType<ScalarTag>,
    TypeOf<Context, ScalarTag>: Default,
{
    Default::default()
}
```

`App` implements `HasType<ScalarTag>` with `Type = f64` and `HasType<NameTag>` with `Type = String`,
so `zero::<App>()` returns `0.0`. With the single entry `TypeProviderComponent: UseType<f64>`
instead, both tags would resolve to `f64`.

In most code the same need is met by a named abstract type,
`#[cgp_type] pub trait HasScalarType { type Scalar; }`, which gives the readable `Self::Scalar` and
its own component key.

## Related constructs

These constructs are the ones `HasType` works with:

- [`#[cgp_type]`](../macros/cgp_type.md): defines named abstract-type components, whose generated
  `WithProvider` impl accepts any `TypeProvider`.
- [`UseType`](../providers/use_type.md) and
  [`UseDelegatedType`](../providers/use_delegated_type.md): its providers.
- [`#[use_type]`](../attributes/use_type.md): the attribute with a similar name, which rewrites type
  names in definitions.
- [`HasErrorType`](has_error_type.md): the best-known named abstract type, defined with
  `#[cgp_type]`.
- [Abstract types](../../concepts/abstract-types.md): the concept.

## Source

- The trait, the `TypeProvider` provider trait, and the `TypeOf` alias are defined in
  [crates/core/cgp-type/src/traits/has_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-type/src/traits/has_type.rs).
- The `UseType` provider and its `TypeProvider` impl are in
  [crates/core/cgp-type/src/impls/use_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-type/src/impls/use_type.rs).
- The `#[cgp_type]` macro that builds named components on this substrate lives in
  [crates/macros/cgp-macro-core/src/types/cgp_type/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_type/).
- For how it is generated and the index of tests, see the implementation document
  [implementation/entrypoints/cgp_type](../../implementation/entrypoints/cgp_type.md).
