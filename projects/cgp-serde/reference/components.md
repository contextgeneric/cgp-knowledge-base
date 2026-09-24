# The serialization components

cgp-serde's two components restate Serde's `Serialize` and `Deserialize` with the encoded type moved
out of `Self` and into a `Value` parameter. `Self` becomes an environmental context that carries the
wiring and is passed to every method, and a context chooses a provider for each value type it
encodes. Both are ordinary [`#[cgp_component]`](../../../cgp/reference/macros/cgp_component.md)
components, so each generates a consumer trait, a provider trait, and a `…Component` wiring key. Why
the value moves into a parameter is set out in the [architecture](../architecture/README.md); this
document records what the two components are.

Both components live in `cgp_serde::components`. Callers use the consumer traits, providers implement
the provider traits, and contexts wire the component keys, per
[consumer and provider traits](../../../cgp/concepts/consumer-and-provider-traits.md).

## `CanSerializeValue`

`CanSerializeValue<Value>` serializes a value of type `Value` into any Serde `Serializer`, with the
context choosing how.

### Definition

```rust
#[cgp_component(ValueSerializer)]
#[derive_delegate(UseDelegate<Value>)]
pub trait CanSerializeValue<Value: ?Sized> {
    fn serialize<S>(&self, value: &Value, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer;
}
```

The macro generates the provider trait `ValueSerializer<Context, Value: ?Sized>` and the wiring key
`ValueSerializerComponent`. A provider written with [`#[cgp_impl]`](../../../cgp/reference/macros/cgp_impl.md)
implements it in consumer-trait shape, as `impl<Value> ValueSerializer<Value>` with `self` meaning the
context.

### Behavior

The method has the same shape as `serde::Serialize::serialize` with two changes: the value arrives as a
`&Value` argument rather than as `self`, and `&self` is the context. The serializer is still generic
and consumed, so a provider can use every Serde `Serializer` method, and the result is whatever the
serializer returns.

`Value` is declared `?Sized`, so the trait itself admits an unsized value such as `str`. No provider in
the library accepts one, though: every provider's impl declares its `Value` parameter without `?Sized`,
so the implicit `Sized` bound applies. Wiring `str` to `UseSerde` fails to compile with
"the size for values of type `str` cannot be known at compilation time", and so does forwarding a
`&str` to `str` through `SerializeDeref`. A borrowed string is serialized by wiring `&'a str` itself to
`SerializeString` instead.

### Context dependencies

None of its own. A context implements the consumer trait for a value type by wiring
`ValueSerializerComponent` to a provider for it, most often per type through the `open` statement of
[`delegate_components!`](../../../cgp/reference/macros/delegate_components.md).

### Pairing

The deserializing counterpart is [`CanDeserializeValue`](#candeserializevalue).

## `CanDeserializeValue`

`CanDeserializeValue<'de, Value>` deserializes a value of type `Value` from any Serde
`Deserializer<'de>`, with the context choosing how.

### Definition

```rust
#[cgp_component(ValueDeserializer)]
#[derive_delegate(UseDelegate<Value>)]
pub trait CanDeserializeValue<'de, Value> {
    fn deserialize<D>(&self, deserializer: D) -> Result<Value, D::Error>
    where
        D: serde::Deserializer<'de>;
}
```

The macro generates the provider trait `ValueDeserializer<'de, Context, Value>` and the wiring key
`ValueDeserializerComponent`.

### Behavior

The method has the same shape as `serde::Deserialize::deserialize`, plus `&self` for the context. The
`'de` lifetime is Serde's: it is the lifetime of the input, and a value that borrows from the input,
such as a `&'de str`, can be produced only when the deserializer can lend data for `'de`. `Value` is
sized, since the method returns it.

Because `'de` is a parameter of the component, it takes part in the component's identity. CGP lifts a
component's lifetime parameters into [`Life`](../../../cgp/reference/types/life.md) wherever they must
stand as a type, so a [`check_components!`](../../../cgp/reference/macros/check_components.md) entry
names each value type together with the lifetime:

```rust
check_components! {
    #[check_trait(CanDeserializeApp)]
    <'de> App {
        ValueDeserializerComponent: [
            (Life<'de>, u64),
            (Life<'de>, String),
        ],
    }
}
```

The per-type wiring does not mention the lifetime: `@ValueDeserializerComponent.u64: UseSerde` keys on
the value type alone.

### Context dependencies

None of its own, as for `CanSerializeValue`.

### Pairing

The serializing counterpart is [`CanSerializeValue`](#canserializevalue).

## The legacy `UseDelegate` dispatch

Both components carry `#[derive_delegate(UseDelegate<Value>)]`, which generates an impl of each provider
trait for [`UseDelegate`](../../../cgp/reference/providers/use_delegate.md), so a context can also
dispatch per value type through a nested `UseDelegate<new … { … }>` table. That is the form the
published 0.2.0 release and the announcement post use. The `open` statement dispatches through the
`RedirectLookup` impl every component already has and needs no attribute, per
[dispatching per type](../../../cgp/guides/dispatching-per-type.md), and every context on the `v0.8.0`
branch uses it. The attribute therefore serves only downstream code that still builds `UseDelegate`
tables.

## Calling the components

Code with a context in hand calls the consumer traits like any method:
`context.serialize(&value, serializer)` and `context.deserialize(deserializer)`. Code that must pass a
value to a Serde API wraps it instead, in
[`SerializeWithContext` or `DeserializeWithContext`](context-adapters.md), and the JSON crate adds
[convenience providers](json.md) on top. Inside a provider the same calls re-enter the context for
nested values, as [re-entrant providers](../architecture/reentrant-providers.md) describes.

## Source

- [`crates/cgp-serde/src/components/serialize.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/components/serialize.rs) — `CanSerializeValue`.
- [`crates/cgp-serde/src/components/deserialize.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/components/deserialize.rs) — `CanDeserializeValue`.

## Public material derived from this

The "Serialization as a component" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the rustdoc for both traits.
