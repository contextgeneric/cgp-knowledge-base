# Writing a provider

A new cgp-serde provider is an ordinary CGP provider for one or both serialization components, and the
general rules for writing one are in [writing providers](../../../cgp/guides/writing-providers.md) and
[declaring dependencies](../../../cgp/guides/declaring-dependencies.md). This guide adds what is
specific to cgp-serde: how to structure a provider pair, how to hand nested values back to the context,
how to report errors, and the choices the library's own [known defects](../README.md#status-and-gaps)
show to avoid.

## Start from an example

A provider that encodes a `Duration` as whole milliseconds shows the default shape. It converts to an
intermediate type, `u64`, and asks the context to encode that, so the final representation of the
number stays a wiring choice:

```rust
pub struct SerializeMillis;

#[cgp_impl(SerializeMillis)]
#[uses(CanSerializeValue<u64>)]
impl ValueSerializer<Duration> {
    fn serialize<S>(&self, value: &Duration, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let millis = u64::try_from(value.as_millis()).map_err(S::Error::custom)?;
        self.serialize(&millis, serializer)
    }
}

#[cgp_impl(SerializeMillis)]
#[uses(CanDeserializeValue<'de, u64>)]
impl<'de> ValueDeserializer<'de, Duration> {
    fn deserialize<D>(&self, deserializer: D) -> Result<Duration, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let millis = self.deserialize(deserializer)?;
        Ok(Duration::from_millis(millis))
    }
}
```

A context wires it like any library provider, alongside an entry for `u64` in each direction, and a
`Duration` of 1,500 milliseconds round-trips through JSON as `1500`. The code needs
`serde::ser::Error` in scope for `S::Error::custom`.

## Structure the provider

**Implement both directions on one struct when they are one decision.** Declare the struct once, then
write each direction as a separate [`#[cgp_impl]`](../../../cgp/reference/macros/cgp_impl.md) naming
it, as above. A context then names the same provider in both tables, and the two directions cannot
disagree about the format. Use `#[cgp_impl(new Name)]` only for a provider that implements one
direction, since `new` declares the struct and a second `new` would declare it twice.

**Follow the library's naming convention.** Name a struct that implements both directions, or only
serialization, `Serialize…`, and a struct that implements only deserialization `Deserialize…`; see
[component design](../architecture/component-design.md#one-struct-both-directions).

**Write the header in consumer-trait shape.** `impl<Value> ValueSerializer<Value>` with `self` as the
context, per the [`#[cgp_impl]` guide](../../../cgp/guides/writing-providers.md); the explicit
`impl<Context, Value> ValueSerializer<Value> for Context` form in the announcement post is only needed
when the context must be named.

## Hand nested values back to the context

**Encode anything that is not a leaf through the context.** A provider that encodes a nested value
itself, by calling Serde's impl or by writing the bytes directly, fixes that value's encoding for every
application. Asking the context keeps it a wiring choice, which is the property the whole library rests
on; see [re-entrant providers](../architecture/reentrant-providers.md).

There are two ways to do it, and the choice depends on who performs the nested call:

- **Converting to another type** — call `self.serialize(&converted, serializer)` or
  `self.deserialize(deserializer)` directly, and declare the dependency with `#[uses]`, as
  `SerializeMillis` does for `u64`.
- **Passing items to a Serde compound API** — wrap each one in
  [`SerializeWithContext`](../reference/context-adapters.md#serializewithcontext) for
  `serialize_element` or `serialize_entry`, or pass a
  [`DeserializeWithContext`](../reference/context-adapters.md#deserializewithcontext) seed to
  `next_element_seed` or `next_value_seed`.

When the nested type depends on a borrow's lifetime, as an iterator's items do, write the dependency as
a higher-ranked bound in the `where` clause, `Self: for<'a> CanSerializeValue<…>`, since `#[uses]`
does not express one.

**Never re-enter the context for the type you are handling.** A provider for `String` that asks the
context to serialize a `String` depends on itself, which fails to compile with `E0275`. When a provider
needs another provider for the same type, take it as a type parameter, as
[`DeserializeDefault<Provider>`](../reference/default-values.md) does, and bind it with
[`#[use_provider]`](../../../cgp/reference/attributes/use_provider.md).

## Report errors through Serde

**Report a failure with the format's own error, not with CGP's error components.** Map it with
`S::Error::custom` or `D::Error::custom`, from `serde::ser::Error` and `serde::de::Error`, using any
error that implements `Display`. The format adds its position to the message, and the error reaches the
caller the same way a failure inside Serde's own impls does. CGP's
[error handling](../../../cgp/concepts/modular-error-handling.md) belongs at the boundary, where the
[JSON providers](../reference/json.md) raise the finished `serde_json::Error` into the context's error
type; see [the bridge to Serde](../architecture/serde-bridge.md#where-errors-are-reported).

## Avoid the library's known pitfalls

Several of the library's own providers have defects that a new provider can avoid by construction:

- **Re-enter for owned intermediate types.** Ask the context for a `String` rather than a `&'de str`
  unless the result must borrow from the input. `DeserializeWithFromStr` asks for a borrowed string and
  therefore rejects JSON strings that must be unescaped, and all reader input.
- **Accept owned data in visitors.** A visitor that implements `visit_borrowed_bytes` should also
  implement `visit_bytes`, and likewise for strings. `SerializeBytes` implements only the borrowed form
  and rejects anything the deserializer must copy.
- **Declare lengths when they are known.** Pass `Some(len)` to `serialize_seq` or `serialize_map` when
  the collection knows its length. The library's record and sequence providers pass `None`, which
  length-prefixed binary formats reject.
- **Make the two directions agree.** Check that what the serializer writes is what the deserializer
  accepts. `SerializeBytes` writes a JSON array and reads only a string.

## Test the provider

Assert the provider's wiring with [`check_components!`](../../../cgp/reference/macros/check_components.md)
in a test context, listing the deserializing side with `Life<'de>`, and round-trip at least one value
through a real format. The library's own gaps in both are recorded in [testing.md](../testing.md).

## Public material derived from this

The "Writing serializers" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and a contributor section of the
repository README.
