# Conversion providers

The conversion providers encode a value by converting it to another type and asking the context to
encode that type instead. `SerializeWithDisplay` and `DeserializeWithFromStr` go through a string,
`SerializeFrom` and `TrySerializeFrom` go through any type related by `Into` or `TryInto`, and
`SerializeDeref` goes through the value a smart pointer points to. Each is a
[direct re-entry](../architecture/reentrant-providers.md#direct-calls): the converted value is
encoded by whatever the context wires for its type, so the final representation stays a wiring choice.

## `SerializeWithDisplay`

`SerializeWithDisplay` serializes any `Display` value as the string it formats to.

### Definition

```rust
#[cgp_impl(new SerializeWithDisplay)]
#[uses(CanSerializeValue<String>)]
impl<Value> ValueSerializer<Value>
where
    Value: Display,
{ ... }
```

### Behavior

The provider formats the value with `to_string` and serializes the result through the context's wiring
for `String`. A `Celsius(21.5)` whose `Display` writes `21.5C` serializes to the JSON string `"21.5C"`.
The formatted string is always allocated.

### Context dependencies

`CanSerializeValue<String>`. Wiring `String` itself to `SerializeWithDisplay` makes the provider depend
on itself, which fails to compile with `E0275`.

### Pairing

The deserializing counterpart is [`DeserializeWithFromStr`](#deserializewithfromstr), which parses the
string back with `FromStr`.

## `DeserializeWithFromStr`

`DeserializeWithFromStr` deserializes any `FromStr` value by parsing a string.

### Definition

```rust
#[cgp_impl(new DeserializeWithFromStr)]
#[uses(CanDeserializeValue<'a, &'a str>)]
impl<'a, Value> ValueDeserializer<'a, Value>
where
    Value: FromStr<Err: Display>,
{ ... }
```

### Behavior

The provider asks the context for a `&'de str` borrowed from the input, then parses it, reporting a
parse failure's `Display` message as a Serde custom error. With `&'a str` wired to `UseSerde`, a `u64`
wired to this provider deserializes from the JSON string `"42"`, and `"x"` fails with
`invalid digit found in string`.

Asking for a borrowed string means the input must be able to lend one, and the failure comes before
any parsing. A JSON string that `serde_json` has to unescape into a new buffer cannot be lent: with the
workspace's `serde_json` 1.0.143, `"4\"2"`, whose middle character is an escaped quote, fails with
`invalid type: string "4\"2", expected a borrowed string`, and an escaped newline fails the same way.
Not every escape triggers it: in the same probe, `"\u0034\u0032"` was accepted and parsed as `42`. A
deserializer that reads from an `io::Read` can never lend its input, so there even the plain `"42"`
fails with the same message.

### Context dependencies

`CanDeserializeValue<'de, &'de str>`, usually satisfied by wiring `<'a> &'a str` to `UseSerde`.

### Pairing

The serializing counterpart is [`SerializeWithDisplay`](#serializewithdisplay).

### Known issues

- **Some escaped strings, and all reader input, fail.** Re-entering for a borrowed `&'de str` rather
  than an owned `String` rejects any string the deserializer cannot lend. Parsing needs only a
  temporary `&str`, so the borrowed requirement is stricter than the provider's work demands.

## `SerializeFrom`

`SerializeFrom<Target>` serializes a value by converting it into `Target`, and deserializes a value by
converting from `Target`.

### Definition

```rust
pub struct SerializeFrom<Target>(pub PhantomData<Target>);

#[cgp_impl(SerializeFrom<Target>)]
#[uses(CanSerializeValue<Target>)]
impl<Value, Target> ValueSerializer<Value>
where
    Value: Clone + Into<Target>,
{ ... }

#[cgp_impl(SerializeFrom<Source>)]
#[uses(CanDeserializeValue<'a, Source>)]
impl<'a, Value, Source> ValueDeserializer<'a, Value>
where
    Source: Into<Value>,
{ ... }
```

### Behavior

Serializing clones the value, converts the clone with `Into`, and serializes the result through the
context. The clone is needed because `Into` consumes its input while the provider holds only a
reference. Deserializing reads a `Target` through the context and converts it with `Into`. The type
parameter plays opposite roles in the two directions: a `u32` serialized as `SerializeFrom<u64>` goes
through `u64`, while a `u32` deserialized as `SerializeFrom<u8>` reads a `u8` and widens it. A context
wiring the same type in both directions usually needs two different parameters, since `Into` rarely
holds both ways.

### Context dependencies

`CanSerializeValue<Target>` to serialize, and `CanDeserializeValue<'de, Target>` to deserialize.

### Pairing

The same struct implements both directions. [`TrySerializeFrom`](#tryserializefrom) is the fallible
form.

### Known issues

- **Serializing requires `Clone`**, and clones the whole value on every call.

## `TrySerializeFrom`

`TrySerializeFrom<Target>` is the fallible form of `SerializeFrom`, converting with `TryInto` and
reporting a failed conversion as a Serde error.

### Definition

```rust
pub struct TrySerializeFrom<Target>(pub PhantomData<Target>);

#[cgp_impl(TrySerializeFrom<Target>)]
#[uses(CanSerializeValue<Target>)]
impl<Value, Target> ValueSerializer<Value>
where
    Value: Clone + TryInto<Target, Error: Display>,
{ ... }

#[cgp_impl(TrySerializeFrom<Source>)]
#[uses(CanDeserializeValue<'a, Source>)]
impl<'a, Value, Source> ValueDeserializer<'a, Value>
where
    Source: TryInto<Value, Error: Display>,
{ ... }
```

### Behavior

The directions mirror `SerializeFrom`, with the conversion's `Display` message reported through the
serializer's or deserializer's `Error::custom`. A `u16` serialized as `TrySerializeFrom<u8>` writes `7`
for `7`, and for `300` fails with `out of range integral type conversion attempted`; an `i8`
deserialized as `TrySerializeFrom<u64>` reads `5`, and fails on `500` with the same message.

### Context dependencies

`CanSerializeValue<Target>` to serialize, and `CanDeserializeValue<'de, Target>` to deserialize.

### Pairing

The same struct implements both directions.

### Known issues

- **Serializing requires `Clone`**, as for `SerializeFrom`.

## `SerializeDeref`

`SerializeDeref` serializes a smart pointer or reference as the value it points to.

### Definition

```rust
#[cgp_impl(new SerializeDeref)]
#[uses(CanSerializeValue<Value::Target>)]
impl<Value> ValueSerializer<Value>
where
    Value: Deref,
{ ... }
```

### Behavior

The provider dereferences the value and serializes the target through the context, so `Box<u64>`
serializes exactly as `u64` does. Its main use is the generic entry
`@ValueSerializerComponent.<'a, T> &'a T: SerializeDeref`, which forwards every reference to the
context's wiring for the referenced type. [`SerializeIterator`](collections.md) needs that entry,
because iterating a borrowed collection yields references; see
[re-entrant providers](../architecture/reentrant-providers.md#what-re-entry-requires-of-a-context).

The target must be sized, because no provider accepts an unsized value, so `&str` and `&[T]` cannot be
forwarded this way; see [the components](components.md#canserializevalue).

### Context dependencies

`CanSerializeValue<Value::Target>`.

### Pairing

No deserializing counterpart. Deserializing into a reference needs somewhere for the value to live,
which is the job of [`DeserializeAndAllocate`](allocation.md) or of a borrowed type deserialized from
the input directly.

## Source

- [`crates/cgp-serde/src/providers/display.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/display.rs) — `SerializeWithDisplay` and `DeserializeWithFromStr`.
- [`crates/cgp-serde/src/providers/from.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/from.rs) — `SerializeFrom`.
- [`crates/cgp-serde/src/providers/try_from.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/try_from.rs) — `TrySerializeFrom`.
- [`crates/cgp-serde/src/providers/deref.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/deref.rs) — `SerializeDeref`.

## Public material derived from this

The "Writing serializers" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the rustdoc for the five
providers.
