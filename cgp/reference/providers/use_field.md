# `UseField`

`UseField<Tag>` is a zero-sized provider that reads the context's field named by `Tag` through [`HasField`](../traits/has_field.md). Its main use is to implement a getter whose method name differs from the field it reads.

## Purpose

`UseField` separates a getter's method name from the field that stores the value. A getter component defined with [`#[cgp_getter]`](../macros/cgp_getter.md), such as `fn name(&self) -> &str`, describes a value the context supplies, but a context may store it as `first_name`, and different contexts may use different names. `UseField<Tag>` carries the field name as a type parameter, so wiring `NameGetterComponent: UseField<Symbol!("first_name")>` makes `name()` read `first_name`. The field name lives in the wiring, not in the trait. [`#[cgp_auto_getter]`](../macros/cgp_auto_getter.md), which always reads the field named after the method, cannot express this.

The `Tag` is usually a [`Symbol!`](../macros/symbol.md) string such as `Symbol!("name")`, or an [`Index<N>`](../types/index.md) for a tuple field. These are the tags [`#[derive(HasField)]`](../derives/derive_has_field.md) generates impls for. Any other type works as a tag if the context implements `HasField` for it by hand.

## Definition

`UseField` is defined in `cgp-field`, with an alias for use through [`WithProvider`](with_provider.md):

```rust
pub struct UseField<Tag>(pub PhantomData<Tag>);

pub type WithField<Tag> = WithProvider<UseField<Tag>>;
```

`UseField` is in the prelude. `WithField` is not, and is imported from `cgp::core::field::impls`.

## Implementations

`UseField<Tag>` is implemented in several places, all forwarding to the context's `HasField<Tag>`:

- **Every single-method [`#[cgp_getter]`](../macros/cgp_getter.md) component.** The macro generates an impl of the getter's provider trait for `UseField<__Tag__>`, with the tag left free and the return-type conversion, such as `.as_str()`, applied. This is the impl a direct `UseField` wiring uses.
- **The foundational [`FieldGetter`](../traits/has_field.md) and `MutFieldGetter`.** These read the field by reference and let `UseField` back a getter through `WithField`:

```rust
impl<Context, OutTag, Tag, Value> FieldGetter<Context, OutTag> for UseField<Tag>
where
    Context: HasField<Tag, Value = Value>,
{
    type Value = Value;

    fn get_field(context: &Context, _tag: PhantomData<OutTag>) -> &Value {
        context.get_field(PhantomData)
    }
}
```

  `OutTag` is the tag the component asks under, its own marker, and the impl ignores it and reads `Tag`. That is the decoupling in its plainest form. The `MutFieldGetter` impl is the same with `HasFieldMut` and `get_field_mut`.
- **[`TypeProvider`](../components/has_type.md).** `UseField<Tag>` reports the field's type as an abstract type, so a type component wired to `UseField<Symbol!("width")>` or `WithField<Symbol!("width")>` takes the type of the `width` field. This impl has a matching `IsProviderFor<TypeProviderComponent, …>` impl.
- **The handler family.** `cgp-handler` implements `Computer` and `AsyncComputer` for `UseField<Tag>` by forwarding to the value stored in the field, as described under [`Computer`](../components/computer.md).

## Examples

This getter reads a field whose name differs from the method's:

```rust
use cgp::prelude::*;

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
        NameGetterComponent: UseField<Symbol!("first_name")>,
    }
}

check_components! {
    Person {
        NameGetterComponent,
    }
}
```

`person.name()` resolves through the `NameGetter` impl `#[cgp_getter]` generated for `UseField<__Tag__>`, with `Symbol!("first_name")` as the tag, so it returns the `first_name` field as a `&str`. The same binding can be written with the alias, after `use cgp::core::field::impls::WithField;`:

```rust
delegate_components! {
    Person {
        NameGetterComponent: WithField<Symbol!("first_name")>,
    }
}
```

## Related constructs

These constructs are the ones `UseField` works with:

- [`#[cgp_getter]`](../macros/cgp_getter.md) — generates its getter impl.
- [`HasField`, `FieldGetter`, and `MutFieldGetter`](../traits/has_field.md) — the traits it reads and implements.
- [`#[derive(HasField)]`](../derives/derive_has_field.md), [`Symbol!`](../macros/symbol.md), and [`Index<N>`](../types/index.md) — the field impls and tags it relies on.
- [`WithProvider`](with_provider.md) — the adapter behind `WithField`.
- [`UseFieldRef`](use_field_ref.md) — borrows the field as another type through `AsRef`.
- [`ChainGetters`](chain_getters.md) — reads through nested contexts.
- [`UseType`](use_type.md) — the counterpart for abstract types.

## Source

- The `UseField` struct, its `WithField` alias, and the `FieldGetter`, `MutFieldGetter`, and `TypeProvider` impls are in [crates/core/cgp-field/src/impls/use_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/use_field.rs).
- The `HasField`, `FieldGetter`, and (in `has_field_mut.rs`) `HasFieldMut`, `MutFieldGetter` traits are in [crates/core/cgp-field/src/traits/](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-field/src/traits/).
- The `#[cgp_getter]`-generated `UseField` impl is built in [crates/macros/cgp-macro-core/src/types/cgp_getter/use_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_getter/use_field.rs).
- For how it is generated and the index of tests, see the implementation document [implementation/entrypoints/cgp_getter](../../implementation/entrypoints/cgp_getter.md).

## Public pages derived from this document

This document feeds two public pages: [`use_field`](https://contextgeneric.dev/docs/reference/providers/use_field) and its alias page [`with_field`](https://contextgeneric.dev/docs/reference/providers/with_field), which carries the `WithField` wiring example. The alias family itself is documented in [with_provider.md](with_provider.md). A change here is propagated to both, per the [synchronization rule](../../../AGENTS.md#the-synchronization-rule).
