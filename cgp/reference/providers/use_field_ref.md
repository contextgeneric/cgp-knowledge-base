# `UseFieldRef`

`UseFieldRef<Tag, Value>` is a zero-sized foundational field getter that reads a field named by `Tag` and borrows it through `AsRef`/`AsMut` to produce a `&Value`, for a getter whose return type is a type the field is stored as something else and borrowed to.

## Purpose

`UseFieldRef` exists for a getter that returns `&T` for some type the context does not store directly but can borrow to through `AsRef`. It reads the field at `Tag` and calls `as_ref()`, so the getter's signature can name the borrowed type `Value` while the context stores a type that implements `AsRef<Value>` — a `&Config` from a stored `Arc<Config>`, for example.

The common borrowed-view getters do not need `UseFieldRef`, and this is the first thing to know about it. When a getter's return type is one of the shorthands the getter macros recognize — `&str` or `&[u8]` — the [`#[cgp_getter]`](../macros/cgp_getter.md)-generated [`UseField`](use_field.md) implementation already borrows for you: it reads the field and calls `as_str()` or `as_ref()`, so a `&str` getter over a `String` field and a `&[u8]` getter over a `Vec<u8>` field are wired with a plain [`UseField`](use_field.md). `UseFieldRef` is for the remaining case, a getter returning `&T` for a sized `T` the field is not stored as but is `AsRef<T>`.

`UseFieldRef` implements the provider-side [`FieldGetter`](../traits/has_field.md) rather than a getter component's own provider trait, so it is wired to a getter component by wrapping it in [`WithProvider`](with_provider.md) through its `WithFieldRef` alias. This distinguishes it from [`UseField`](use_field.md), for which `#[cgp_getter]` generates a getter-component implementation directly. As with every CGP provider, `UseFieldRef<Tag, Value>` carries no runtime value; it is a `PhantomData`-only marker named in wiring.

## Definition

`UseFieldRef` is a phantom-typed struct parameterized by the field tag and the borrowed value type, defined in `cgp-field`:

```rust
pub struct UseFieldRef<Tag, Value>(pub PhantomData<(Tag, Value)>);

pub type WithFieldRef<Tag, Value> = WithProvider<UseFieldRef<Tag, Value>>;
```

`Tag` names the field, as in [`UseField`](use_field.md), and `Value` is the type the getter exposes — the type the stored field can be borrowed as via `AsRef<Value>`. The `WithFieldRef<Tag, Value>` alias wraps the provider in [`WithProvider`](with_provider.md), and it is the form wired to a getter component, since the bare `UseFieldRef` provides the foundational `FieldGetter` rather than the getter's provider trait. Neither `UseFieldRef` nor `WithFieldRef` is re-exported through `cgp::prelude`; reach them through `cgp::core::field::impls`.

## Implementations

`UseFieldRef<Tag, Value>` implements the provider-side getter [`FieldGetter`](../traits/has_field.md) by reading the field at `Tag` and dereferencing it to `&Value`:

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

The `where` clause carries the defining constraint: the context's field at `Tag` must implement `AsRef<Value>`, so the stored type can be borrowed as the exposed type. As in `UseField`, `OutTag` is the tag the component asks under and is ignored; the field is read at `Tag`. The body reads the field and calls `as_ref()`. The `'static` bound on the field type lets Rust infer the borrow's lifetime through the `AsRef` call.

`UseFieldRef` also implements the mutable getter [`MutFieldGetter`](../traits/has_field.md), requiring the field type to implement both `AsRef<Value>` and `AsMut<Value>` and returning `&mut Value` via `as_mut()`. Because these are `FieldGetter` implementations rather than a getter component's provider trait, the [`WithProvider`](with_provider.md) adapter behind `WithFieldRef` is what turns `UseFieldRef` into a provider a getter component can be wired to. Unlike `UseField`, `UseFieldRef` does not implement [`TypeProvider`](../components/has_type.md), because its purpose is borrowed field access rather than abstract-type resolution.

## Examples

A getter returns `&Config` while the context stores the config in a wrapper that borrows as `Config`. The wrapper implements `AsRef<Config>`, so `WithFieldRef` reads it and borrows through it:

```rust
use cgp::prelude::*;
use cgp::core::field::impls::WithFieldRef; // not re-exported through the prelude

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

`App` wires `ConfigGetterComponent` to `WithFieldRef<Symbol!("config"), Config>`. The provider reads the `config` field, a `StoredConfig`, and because `StoredConfig: AsRef<Config>`, returns `&Config` from `as_ref()`. The getter exposes the borrowed `Config` view while the context owns the `StoredConfig`.

## Related constructs

`UseFieldRef` is the foundational `AsRef`-borrowing counterpart of [`UseField`](use_field.md): both read a field named by `Tag` and implement the provider-side [`FieldGetter`](../traits/has_field.md)/[`MutFieldGetter`](../traits/has_field.md) traits over [`HasField`](../traits/has_field.md), but `UseFieldRef` adds a `Value` parameter and exposes `&Value` via `AsRef`/`AsMut` instead of the field's own type, and it is wired through [`WithProvider`](with_provider.md) rather than directly. The common `&str` and `&[u8]` borrowed getters need no `UseFieldRef`, because `#[cgp_getter]` bakes the `as_str()`/`as_ref()` step into the generated [`UseField`](use_field.md) implementation for those return types. It reads fields produced by [`#[derive(HasField)]`](../derives/derive_has_field.md), keyed by tags from [`Symbol!`](../macros/symbol.md) or `Index<N>`, and is wired to a getter defined with [`#[cgp_getter]`](../macros/cgp_getter.md). Its `WithFieldRef` alias is one of the named wrappers around [`WithProvider`](with_provider.md). For chaining getters across nested contexts, see [`ChainGetters`](chain_getters.md), another foundational `FieldGetter` wired through `WithProvider`.

## Source

- The `UseFieldRef` struct, its `WithFieldRef` alias, and the `FieldGetter` and `MutFieldGetter` impls are in [crates/core/cgp-field/src/impls/use_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/use_ref.rs).
- The `HasField` and `FieldGetter` traits are in [crates/core/cgp-field/src/traits/has_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field.rs), and `HasFieldMut`/`MutFieldGetter` are in [crates/core/cgp-field/src/traits/has_field_mut.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field_mut.rs).
