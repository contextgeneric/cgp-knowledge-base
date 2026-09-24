# `UseSerde`

`UseSerde` is the bridge from cgp-serde back to Serde: it serializes or deserializes a value through
the value type's own `Serialize` or `Deserialize` impl. It is how a context reuses every existing Serde
impl, including the ones in the standard library and in third-party crates, without writing a provider
for them.

## `UseSerde`

`UseSerde` implements both serialization components for any value type that already implements the
matching Serde trait.

### Definition

```rust
pub struct UseSerde;

#[cgp_impl(UseSerde)]
impl<Value> ValueSerializer<Value>
where
    Value: serde::Serialize,
{ ... }

#[cgp_impl(UseSerde)]
impl<'a, Value> ValueDeserializer<'a, Value>
where
    Value: serde::Deserialize<'a>,
{ ... }
```

### Behavior

The provider ignores the context and calls the Serde impl directly, so the output is exactly what plain
Serde would produce. That makes it the usual choice for the scalar leaves of a context's table, such as
`u64`, `i64`, `String`, and `bool`, where the application has no reason to choose an encoding.

It also means the context's wiring stops at a value handed to `UseSerde`. A type whose `Serialize` impl
is used serializes its fields through that impl, not through the context, so the context's other
choices do not reach inside it. A struct deriving Serde's `Serialize` with a `data: Vec<u8>` field,
wired to `UseSerde` in a context that wires `Vec<u8>` to `SerializeHex`, still serializes `data` as the
array `[1,2]`. A type whose fields should follow the context's choices is wired to
[`SerializeFields`](records.md) instead.

`UseSerde` is also the only way the library encodes an enum, since no provider handles an enum
generically; the enum must implement Serde's traits itself.

The deserializing impl passes Serde's `'de` lifetime straight through, so `UseSerde` can produce a
value that borrows from the input when the Serde impl does. Wiring `&'a str` to `UseSerde` deserializes
a borrowed string, with the restriction that the input must be able to lend it; see
[`DeserializeWithFromStr`](conversions.md#deserializewithfromstr), which relies on exactly this.

### Context dependencies

None. `UseSerde` is a leaf provider.

### Pairing

The same struct implements both directions.

## Source

- [`crates/cgp-serde/src/providers/serde.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/serde.rs) — `UseSerde`.

## Public material derived from this

The "Writing serializers" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the rustdoc for `UseSerde`.
