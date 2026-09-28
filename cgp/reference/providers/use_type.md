# `UseType` (provider)

`UseType<Type>` is a zero-sized provider that supplies a concrete `Type` as the value of an abstract
CGP type, so a context fixes an abstract type through wiring alone.

This document covers the provider, the struct `UseType<Type>(PhantomData<Type>)`. The [`#[use_type]`
attribute](../attributes/use_type.md) is a different construct: it rewrites bare type names inside a
definition and adds the owning trait as a bound. The attribute refers to an abstract type; the
provider chooses the concrete type behind it.

## Purpose

`UseType` spares a context from writing a provider every time it fixes an abstract type. An abstract
type is a trait with one associated type, such as
`#[cgp_type] trait HasScalarType { type Scalar; }`. Without `UseType`, choosing `f64` for `Scalar`
would take a bespoke provider whose only content is `type Scalar = f64;`, repeated for every
abstract type and every choice.

`UseType<T>` captures that shape once. Wiring a context's type component to `UseType<f64>` sets the
abstract type to `f64` with no custom impl. It plays the role for types that
[`UseField`](use_field.md) plays for getters: a general provider parameterized by exactly what the
context wants to supply. Like every provider it holds no runtime data and exists only to be named in
a delegation table.

## Definition

`UseType` is defined in `cgp-type`, with an alias for use through
[`WithProvider`](with_provider.md):

```rust
pub struct UseType<Type>(pub PhantomData<Type>);

pub type WithType<Type> = WithProvider<UseType<Type>>;
```

`UseType` is in the prelude. `WithType` is not, and is imported from `cgp::core::types`.

## Behavior

`UseType` answers two kinds of type component, through two impls of the same struct:

- **The built-in [`HasType`](../components/has_type.md) component.** `cgp-type` implements the
  provider trait `TypeProvider` for every context and every tag, with the struct's parameter as the
  type:

```rust
#[cgp_provider(TypeProviderComponent)]
impl<Context, Tag, Type> TypeProvider<Context, Tag> for UseType<Type> {
    type Type = Type;
}
```

- **Every [`#[cgp_type]`](../macros/cgp_type.md) component.** The macro generates an impl of the
  component's own provider trait:

```rust
impl<Scalar, __Context__> ScalarTypeProvider<__Context__> for UseType<Scalar>
where
    Scalar: Copy,
{
    type Scalar = Scalar;
}
```

(shown for `type Scalar: Copy`; an unbounded associated type gives an empty `where` clause).

The first impl ignores the tag, so a single `TypeProviderComponent: UseType<f64>` entry resolves
`HasType<Tag>` to `f64` for every `Tag`. The second makes
`ScalarTypeProviderComponent: UseType<f64>` set `Scalar = f64`.

A bound on the associated type, such as `type Scalar: Copy`, is copied into the generated impl's
`where` clause. Wiring is lazy, so an unsatisfied bound is not reported where the entry is written:
`ScalarTypeProviderComponent: UseType<String>` compiles until something requires the context's
`HasScalarType`, or until a [`check_components!`](../macros/check_components.md) block checks the component, which reports
``error[E0277]: the trait bound `String: Copy` is not satisfied`` with the note
``required for `cgp::prelude::UseType<String>` to implement `IsProviderFor<ScalarTypeProviderComponent, App>` ``.

`WithType<T>` reaches the same result by another route. The `WithProvider` impl that `#[cgp_type]`
generates accepts any `TypeProvider` for the component's key, and `UseType<T>` is one through its
built-in impl.

## Examples

This context fixes a `#[cgp_type]` abstract type to `f64`:

```rust
use cgp::prelude::*;

#[cgp_type]
pub trait HasScalarType {
    type Scalar: Copy;
}

pub struct App;

delegate_components! {
    App {
        ScalarTypeProviderComponent: UseType<f64>,
    }
}

check_components! {
    App {
        ScalarTypeProviderComponent,
    }
}

fn zero<Context>() -> Context::Scalar
where
    Context: HasScalarType,
    Context::Scalar: Default,
{
    Default::default()
}
```

`App` implements `HasScalarType` with `Scalar = f64` through the generated `UseType` impl, and the
check confirms that `f64` meets the `Copy` bound. The same binding can be written with the alias,
after `use cgp::core::types::WithType;`:

```rust
delegate_components! {
    App {
        ScalarTypeProviderComponent: WithType<f64>,
    }
}
```

## Related constructs

These constructs are the ones `UseType` works with:

- [`#[cgp_type]`](../macros/cgp_type.md): defines abstract-type components and generates their
  `UseType` impl.
- [`HasType`](../components/has_type.md): the built-in abstract-type component whose `TypeProvider`
  it implements.
- [`UseDelegatedType`](use_delegated_type.md): resolves the type through a lookup table instead of a
  fixed parameter.
- [`WithProvider`](with_provider.md): the adapter behind the `WithType` alias.
- [`UseField`](use_field.md): the getter counterpart.
- [`#[use_type]`](../attributes/use_type.md): the attribute with a similar name.

## Source

- The `UseType` struct, its `WithType` alias, and the built-in `TypeProvider` impl are in
  [crates/core/cgp-type/src/impls/use_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-type/src/impls/use_type.rs).
- The `HasType` consumer trait, the `TypeProvider` provider trait, and the `TypeOf` alias are in
  [crates/core/cgp-type/src/traits/has_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-type/src/traits/has_type.rs).
- The `#[cgp_type]`-generated `UseType` impl is built in
  [crates/macros/cgp-macro-core/src/types/cgp_type/item.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_type/item.rs).
- For how it is generated and the index of tests, see the implementation document
  [implementation/entrypoints/cgp_type](../../implementation/entrypoints/cgp_type.md).

## Public pages derived from this document

This document feeds two public pages:
[`use_type`](https://contextgeneric.dev/docs/reference/providers/use_type) and its alias page
[`with_type`](https://contextgeneric.dev/docs/reference/providers/with_type), which carries the
`WithType` wiring example. The alias family itself is documented in
[with_provider.md](with_provider.md). A change here is propagated to both, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule).
