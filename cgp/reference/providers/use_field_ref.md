# `UseFieldRef`

`UseFieldRef<Tag, Value>` is a zero-sized foundational field getter that reads the field named by
`Tag` and borrows it through `AsRef` as a `&Value`, for a getter that returns a type the field can
be borrowed as.

## Purpose

`UseFieldRef` serves a getter returning `&T` where the context stores something that implements
`AsRef<T>`, such as a wrapper around `T`. It reads the field at `Tag` and calls `as_ref()`, so the
getter's signature names the borrowed type `Value` while the context owns another type.

The common borrowed views do not need it. The getter macros already convert these return types, so a
plain [`UseField`](use_field.md) works for them:

- `&str` from a `String` field, through `.as_str()`.
- `&[T]` from any `'static` field implementing `AsRef<[T]>`, through `.as_ref()`.
- `Option<&T>` from an `Option<T>` field, and `Option<&str>` from an `Option<String>` field.

`UseFieldRef` is for the remaining case, a getter returning `&T` for a sized `T` that the field is
not but can borrow as.

It implements only the foundational [`FieldGetter`](../traits/has_field.md) and `MutFieldGetter`,
not any getter component's own provider trait. So it is wired to a getter through
[`WithProvider`](with_provider.md), by its alias `WithFieldRef`, unlike `UseField`, for which
`#[cgp_getter]` generates a direct impl.

## Definition

`UseFieldRef` is defined in `cgp-field`:

```rust
pub struct UseFieldRef<Tag, Value>(pub PhantomData<(Tag, Value)>);

pub type WithFieldRef<Tag, Value> = WithProvider<UseFieldRef<Tag, Value>>;
```

`Tag` names the field, and `Value` is the type the getter exposes. Neither name is in the prelude;
both are imported from `cgp::core::field::impls`.

## Implementations

`UseFieldRef<Tag, Value>` implements `FieldGetter` by reading the field and borrowing it:

```rust
impl<Context, OutTag, Tag, Value> FieldGetter<Context, OutTag> for UseFieldRef<Tag, Value>
where
    Context: HasField<Tag, Value: AsRef<Value> + 'static>,
{
    type Value = Value;

    fn get_field(context: &Context, _tag: PhantomData<OutTag>) -> &Value {
        context.get_field(PhantomData).as_ref()
    }
}
```

The stored field type must implement `AsRef<Value>` and be `'static`. As with `UseField`, `OutTag`,
the component's marker, is ignored. The `MutFieldGetter` impl requires `HasFieldMut<Tag>` with a
field type implementing both `AsRef<Value>` and `AsMut<Value>`, and returns `as_mut()`. Unlike
`UseField`, `UseFieldRef` implements no `TypeProvider`.

## Examples

This getter returns `&Config` while the context stores a wrapper:

```rust
use cgp::prelude::*;
use cgp::core::field::impls::WithFieldRef;

pub struct Config {
    pub port: u16,
}

pub struct StoredConfig(pub Config);

impl AsRef<Config> for StoredConfig {
    fn as_ref(&self) -> &Config {
        &self.0
    }
}

#[cgp_getter]
pub trait HasConfig {
    fn config(&self) -> &Config;
}

#[derive(HasField)]
pub struct App {
    pub config: StoredConfig,
}

delegate_components! {
    App {
        ConfigGetterComponent: WithFieldRef<Symbol!("config"), Config>,
    }
}
```

The provider reads the `config` field, a `StoredConfig`, and returns `&Config` through its
`AsRef<Config>` impl.

## Related constructs

These constructs are the ones `UseFieldRef` works with:

- [`UseField`](use_field.md): reads the field as its own type, with the getter macros' built-in
  conversions.
- [`FieldGetter`, `MutFieldGetter`, and `HasField`](../traits/has_field.md): the traits it
  implements and reads.
- [`WithProvider`](with_provider.md): the adapter behind `WithFieldRef`.
- [`#[cgp_getter]`](../macros/cgp_getter.md): defines the getter components it serves.
- [`ChainGetters`](chain_getters.md): another foundational `FieldGetter` wired through
  `WithProvider`.

## Source

- The `UseFieldRef` struct, its `WithFieldRef` alias, and the `FieldGetter` and `MutFieldGetter`
  impls are in
  [crates/core/cgp-field/src/impls/use_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/use_ref.rs).
- The `HasField` and `FieldGetter` traits are in
  [crates/core/cgp-field/src/traits/has_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field.rs),
  and `HasFieldMut`/`MutFieldGetter` are in
  [crates/core/cgp-field/src/traits/has_field_mut.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field_mut.rs).

## Public pages derived from this document

This document feeds two public pages:
[`use_field_ref`](https://contextgeneric.dev/docs/reference/providers/use_field_ref), which keeps
the foundational mechanism, and its alias page
[`with_field_ref`](https://contextgeneric.dev/docs/reference/providers/with_field_ref), which
carries the wiring form and worked example, since `UseFieldRef` is wired only through the
`WithFieldRef` alias. The alias family itself is documented in [with_provider.md](with_provider.md).
A change here is propagated to both, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule).
