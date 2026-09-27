# `UseDelegatedType`

`UseDelegatedType<Components>` is a zero-sized type provider that resolves an abstract CGP type by
looking its tag up in a delegation table, instead of fixing it to one concrete type.

## Purpose

`UseDelegatedType` lets one provider answer several abstract types, each with its own concrete type
chosen in a table. [`UseType<T>`](use_type.md) binds an abstract type to one fixed `T`, so a context
with several abstract types needs one `UseType` entry per type. `UseDelegatedType<Components>`
gathers those choices into one `Components` table that can be reused, swapped, or supplied from
elsewhere, while each context only points its type components at the table.

It is the type-level counterpart of [`UseDelegate`](use_delegate.md). Both read an entry from a
[`DelegateComponent`](../traits/delegate_component.md) table keyed by a tag, but `UseDelegate`
yields a provider to call and `UseDelegatedType` yields a type.

## Definition

`UseDelegatedType` is defined in `cgp-type`, with an alias for use through
[`WithProvider`](with_provider.md):

```rust
pub struct UseDelegatedType<Components>(pub PhantomData<Components>);

pub type WithDelegatedType<Components> = WithProvider<UseDelegatedType<Components>>;
```

`Components` is a table type with a `DelegateComponent` entry for each tag the provider answers, the
kind of table `delegate_components!` builds. Neither name is in the prelude; both are imported from
`cgp::core::types`.

## Behavior

`UseDelegatedType<Components>` implements the built-in [`TypeProvider`](../components/has_type.md)
by looking the tag up in `Components`:

```rust
#[cgp_provider(TypeProviderComponent)]
impl<Context, Tag, Components, Type> TypeProvider<Context, Tag> for UseDelegatedType<Components>
where
    Components: DelegateComponent<Tag, Delegate = Type>,
{
    type Type = Type;
}
```

The table maps each tag straight to a type, not to a provider. A tag with no entry leaves the bound
unsatisfied, so the context does not implement the abstract type for that tag.

Which tag is looked up depends on how the provider is wired:

- **Directly on the built-in `HasType`**, as `TypeProviderComponent: UseDelegatedType<Table>`, the
  tag is the `Tag` of `HasType<Tag>`, so the table maps tags such as `ScalarTag` to types.
- **Through `WithDelegatedType` on a [`#[cgp_type]`](../macros/cgp_type.md) component**, the tag is
  the component's key. The `WithProvider` impl that `#[cgp_type]` generates asks for
  `TypeProvider<Context, ScalarTypeProviderComponent>`, so the table maps
  `ScalarTypeProviderComponent` to a type.

## Examples

This context resolves two `#[cgp_type]` abstract types from one table:

```rust
use cgp::prelude::*;
use cgp::core::types::WithDelegatedType;

#[cgp_type]
pub trait HasScalarType {
    type Scalar;
}

#[cgp_type]
pub trait HasIndexType {
    type Index;
}

pub struct App;
pub struct AppTypes;

delegate_components! {
    AppTypes {
        ScalarTypeProviderComponent: f64,
        IndexTypeProviderComponent: usize,
    }
}

delegate_components! {
    App {
        [
            ScalarTypeProviderComponent,
            IndexTypeProviderComponent,
        ]: WithDelegatedType<AppTypes>,
    }
}
```

When `App` resolves `Scalar`, `WithDelegatedType<AppTypes>` looks `ScalarTypeProviderComponent` up
in `AppTypes` and finds `f64`; for `Index` it finds `usize`. One entry on `App` answers both
abstract types, and the concrete choices live together in `AppTypes`.

## Related constructs

These constructs are the ones `UseDelegatedType` works with:

- [`UseDelegate`](use_delegate.md): the same table lookup for behavioral components.
- [`UseType`](use_type.md): the simpler provider that fixes one type.
- [`HasType`](../components/has_type.md): the built-in component whose `TypeProvider` it implements.
- [`WithProvider`](with_provider.md) and [`#[cgp_type]`](../macros/cgp_type.md): the adapter behind
  `WithDelegatedType` and the macro that generates its impl.
- [`DelegateComponent`](../traits/delegate_component.md): the table trait it reads.

## Source

- The `UseDelegatedType` struct, its `WithDelegatedType` alias, and the `TypeProvider` impl are in
  [crates/core/cgp-type/src/impls/use_delegated_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-type/src/impls/use_delegated_type.rs).
- The `HasType` consumer trait and `TypeProvider` provider trait are in
  [crates/core/cgp-type/src/traits/has_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-type/src/traits/has_type.rs),
  and `DelegateComponent` is in
  [crates/core/cgp-component/src/traits/delegate_component.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/traits/delegate_component.rs).

## Public pages derived from this document

This document feeds two public pages:
[`use_delegated_type`](https://contextgeneric.dev/docs/reference/providers/use_delegated_type),
which keeps the foundational mechanism, and its alias page
[`with_delegated_type`](https://contextgeneric.dev/docs/reference/providers/with_delegated_type),
which carries the wiring form and worked example for `#[cgp_type]` components. The alias family
itself is documented in [with_provider.md](with_provider.md). A change here is propagated to both,
per the [synchronization rule](../../../AGENTS.md#the-synchronization-rule).
