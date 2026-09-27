# `WithProvider<Provider>`

`WithProvider<Provider>` is a zero-sized adapter that turns a foundational provider, one implementing `TypeProvider` or `FieldGetter`, into a provider of a specific CGP component.

## Purpose

`WithProvider` lets a provider written once against a generic trait serve many named components. The foundational traits [`TypeProvider`](../components/has_type.md) and [`FieldGetter`](../traits/has_field.md) do not know which component they serve: a `TypeProvider` supplies a type for a tag, and a `FieldGetter` reads a field for a tag. A component such as `HasNameType` or `HasName` has its own provider trait, `NameTypeProvider` or `NameGetter`, and a context wires that. `WithProvider<Provider>` implements the component's provider trait by forwarding to the foundational one, so a type provider or field getter written once serves every type or getter component.

Users rarely write `WithProvider` in full, because its common uses have aliases:

| Alias | Expands to | Defined in | In the prelude |
| --- | --- | --- | --- |
| `WithContext` | `WithProvider<UseContext>` | `cgp-component` | yes |
| `WithType<Type>` | `WithProvider<UseType<Type>>` | `cgp-type` | no, `cgp::core::types` |
| `WithDelegatedType<Components>` | `WithProvider<UseDelegatedType<Components>>` | `cgp-type` | no, `cgp::core::types` |
| `WithField<Tag>` | `WithProvider<UseField<Tag>>` | `cgp-field` | no, `cgp::core::field::impls` |
| `WithFieldRef<Tag, Value>` | `WithProvider<UseFieldRef<Tag, Value>>` | `cgp-field` | no, `cgp::core::field::impls` |

## Definition

`WithProvider` is defined in `cgp-component` and is in the prelude:

```rust
pub struct WithProvider<Provider>(pub PhantomData<Provider>);
```

`Provider` is the foundational provider being adapted, held in `PhantomData` and never constructed.

## Behavior

`WithProvider` has no impls of its own in `cgp-component`. [`#[cgp_type]`](../macros/cgp_type.md) and [`#[cgp_getter]`](../macros/cgp_getter.md) generate one for each component they define, keyed by the component's marker:

- **A type component** gets an impl that takes its associated type from the inner `TypeProvider`:

```rust
impl<__Provider__, Name, __Context__> NameTypeProvider<__Context__> for WithProvider<__Provider__>
where
    __Provider__: TypeProvider<__Context__, NameTypeProviderComponent, Type = Name>,
{
    type Name = Name;
}
```

- **A getter component with exactly one method** gets an impl that reads through the inner `FieldGetter`. A getter with several methods gets none, since one field getter cannot serve several methods:

```rust
impl<__Context__, __Provider__> NameGetter<__Context__> for WithProvider<__Provider__>
where
    __Provider__: FieldGetter<__Context__, NameGetterComponent, Value = String>,
{
    fn name(__context__: &__Context__) -> &str {
        __Provider__::get_field(__context__, PhantomData::<NameGetterComponent>).as_str()
    }
}
```

A `&mut self` getter bounds the inner provider by `MutFieldGetter` instead, and a slice getter bounds the value by `AsRef<[T]> + 'static` rather than fixing it. Each generated impl is paired with an `IsProviderFor` impl, so dependencies reach the [check traits](../../concepts/check-traits.md).

The component's own marker is the tag passed to the foundational provider, which decides what each alias reads:

- **`WithType<T>`** ignores the tag and supplies `T`.
- **`WithDelegatedType<Table>`** looks the component's marker up in `Table`.
- **`WithField<Tag>`** reads the context's `Tag` field and ignores the marker. `UseField` is also a `TypeProvider`, so wired to a type component it sets the abstract type to that field's type.
- **`WithFieldRef<Tag, Value>`** reads the `Tag` field and borrows it as `&Value` through `AsRef<Value>`.
- **`WithContext`** asks the context itself, through `UseContext`: for a getter it reads the context's `HasField` entry keyed by the component's marker, and for a type component it reads the context's `HasType` keyed by the marker.

## Examples

This getter reads a field whose name differs from the method's:

```rust
use cgp::prelude::*;
use cgp::core::field::impls::WithField;

#[cgp_getter]
pub trait HasName {
    fn name(&self) -> &str;
}

#[derive(HasField)]
pub struct Person {
    pub first_name: String,
}

delegate_components! {
    Person {
        NameGetterComponent: WithField<Symbol!("first_name")>,
    }
}
```

`WithField<Symbol!("first_name")>` is `WithProvider<UseField<Symbol!("first_name")>>`. The generated `WithProvider` impl forwards `name()` to `UseField`'s `FieldGetter::get_field`, which reads `first_name`. For this getter the plain `UseField<Symbol!("first_name")>` works as well, through the `UseField` impl `#[cgp_getter]` also generates. The aliases matter for providers that exist only as a foundational impl.

## Related constructs

These constructs are the ones `WithProvider` works with:

- [`#[cgp_type]`](../macros/cgp_type.md) and [`#[cgp_getter]`](../macros/cgp_getter.md) — generate its impls.
- [`TypeProvider`](../components/has_type.md) and [`FieldGetter`](../traits/has_field.md) — the foundational traits it adapts.
- [`UseContext`](use_context.md), [`UseType`](use_type.md), [`UseDelegatedType`](use_delegated_type.md), [`UseField`](use_field.md), and [`UseFieldRef`](use_field_ref.md) — the inner providers of its aliases.
- [`IsProviderFor`](../traits/is_provider_for.md) — carries the adapted provider's dependencies to the checks.

## Source

- The struct is defined in [crates/core/cgp-component/src/providers/with_provider.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/providers/with_provider.rs), and the `WithContext` alias in [crates/core/cgp-component/src/providers/use_context.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/providers/use_context.rs).
- The remaining aliases are defined beside their inner providers: `WithType` and `WithDelegatedType` in [crates/core/cgp-type/src/impls/use_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-type/src/impls/use_type.rs) and [use_delegated_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-type/src/impls/use_delegated_type.rs), and `WithField` and `WithFieldRef` in [crates/core/cgp-field/src/impls/use_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/use_field.rs) and [use_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/use_ref.rs).
- The component `WithProvider` impls are generated by `#[cgp_type]` in [crates/macros/cgp-macro-core/src/types/cgp_type/item.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_type/item.rs) and by `#[cgp_getter]` in [crates/macros/cgp-macro-core/src/types/cgp_getter/with_provider.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_getter/with_provider.rs).
- For how it is generated and the index of tests, see the implementation document [implementation/entrypoints/cgp_getter](../../implementation/entrypoints/cgp_getter.md).

## Public pages derived from this document

The public reference gives each provider alias its own page, so this document feeds **six pages** rather than one: [`with_provider`](https://contextgeneric.dev/docs/reference/providers/with_provider), and the five `With…` aliases [`with_context`](https://contextgeneric.dev/docs/reference/providers/with_context), [`with_type`](https://contextgeneric.dev/docs/reference/providers/with_type), [`with_field`](https://contextgeneric.dev/docs/reference/providers/with_field), [`with_field_ref`](https://contextgeneric.dev/docs/reference/providers/with_field_ref), and [`with_delegated_type`](https://contextgeneric.dev/docs/reference/providers/with_delegated_type). Each alias page also draws its worked example from the alias's inner-provider document. A change to the alias family here is propagated to each page, per the [synchronization rule](../../../AGENTS.md#the-synchronization-rule); the granularity rule behind the split is recorded in [website/writing-guides/reference.md](../../../website/writing-guides/reference.md#granularity-one-page-per-named-construct) and the mapping in [website/site-structure.md](../../../website/site-structure.md).
