# Context adapters

The context adapters pair a context with a value, or with a target type, so that the pair can be handed
to any Serde API that expects an ordinary `Serialize` value or `DeserializeSeed`. They are how an
application starts a serialization through its context, and how a provider hands a nested value back
to the context from inside a Serde compound serializer or access trait. Both live in
`cgp_serde::types`. Why providers need them is explained in
[re-entrant providers](../architecture/reentrant-providers.md#adapter-calls); this document records
the public API.

## `SerializeWithContext`

`SerializeWithContext` borrows a context and a value and implements `serde::Serialize` by calling the
context's `CanSerializeValue` for the value's type.

### Definition

```rust
pub struct SerializeWithContext<'a, Context, T> {
    pub context: &'a Context,
    pub value: &'a T,
}

impl<'a, Context, T> SerializeWithContext<'a, Context, T> {
    pub fn new(context: &'a Context, value: &'a T) -> Self;
}

impl<'a, Context, T> serde::Serialize for SerializeWithContext<'a, Context, T>
where
    Context: CanSerializeValue<T>;
```

### Behavior

Serializing the adapter calls `context.serialize(value, serializer)`, so the context's wiring for `T`
decides the output and every nested value re-enters the same wiring. Both fields are public, so a
provider may build the adapter with a struct literal as the library's own providers do. `T` is sized,
since the struct declares no `?Sized` bound.

The adapter is the entry point for serializing with an existing Serde format:

```rust
let json_a = serde_json::to_string(&SerializeWithContext::new(&AppA, &archive)).unwrap();
let json_b = serde_json::to_string(&SerializeWithContext::new(&AppB, &archive)).unwrap();
```

Nothing about the format has to know about CGP. The same adapter works with any function that accepts
a `Serialize` value, subject to the format limits the record and sequence providers impose, recorded in
[records](records.md#known-issues).

### Context dependencies

`Context: CanSerializeValue<T>`, which in turn needs whatever the provider wired for `T` needs.

### Pairing

The deserializing counterpart is [`DeserializeWithContext`](#deserializewithcontext).

## `DeserializeWithContext`

`DeserializeWithContext` borrows a context and names a target type, and implements
`serde::de::DeserializeSeed` by calling the context's `CanDeserializeValue` for that type.

### Definition

```rust
pub struct DeserializeWithContext<'a, Context, Value> {
    pub context: &'a Context,
    pub phantom: PhantomData<Value>,
}

impl<'a, Context, Value> DeserializeWithContext<'a, Context, Value> {
    pub fn new(context: &'a Context) -> Self;
}

impl<'de, 'a, Context, Value> DeserializeSeed<'de> for DeserializeWithContext<'a, Context, Value>
where
    Context: CanDeserializeValue<'de, Value>;
```

### Behavior

Deserializing through the seed calls `context.deserialize(deserializer)` and returns the `Value`. A
seed rather than a `Deserialize` impl is needed because Serde's `Deserialize` has no receiver to carry
state, while `DeserializeSeed` exists for exactly that; the context is the state.

Serde's convenience functions such as `serde_json::from_str` take a `Deserialize` type and cannot
accept a seed, so deserializing from outside means constructing the format's own deserializer and
driving the seed with it:

```rust
let mut deserializer = serde_json::Deserializer::from_str(r#"{"a":5,"b":"y"}"#);
let value: Rec = DeserializeWithContext::new(&app).deserialize(&mut deserializer).unwrap();
```

The call needs `serde::de::DeserializeSeed` in scope. The JSON crate wraps this pattern, together with
the end-of-input check the example above omits, in its [deserialization providers](json.md).

### Context dependencies

`Context: CanDeserializeValue<'de, Value>`.

### Pairing

The serializing counterpart is [`SerializeWithContext`](#serializewithcontext).

## Source

- [`crates/cgp-serde/src/types/serialize_with_context.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/types/serialize_with_context.rs) — `SerializeWithContext`.
- [`crates/cgp-serde/src/types/deserialize_with_context.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/types/deserialize_with_context.rs) — `DeserializeWithContext`.

## Public material derived from this

The "Wiring an application" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), where the two applications produce
their JSON, and the rustdoc for both types.
