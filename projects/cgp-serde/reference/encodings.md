# Encoding providers

The `cgp-serde-extra` crate provides four encodings that an application commonly wants to choose per
context: bytes as hexadecimal or base64 text, and a `DateTime<Utc>` as an RFC 3339 string or a Unix
timestamp. Each is one struct implementing both directions, and each converts to an intermediate
`String` or `i64` that it then encodes through the context, a
[direct re-entry](../architecture/reentrant-providers.md#direct-calls). These are the providers that
make the two-application demo differ: one context wires hex and RFC 3339, the other base64 and
timestamps. The crate depends on `hex`, `base64`, and `chrono`, and every provider is imported from
`cgp_serde_extra::providers`.

## `SerializeHex`

`SerializeHex` encodes bytes as a lowercase hexadecimal string and decodes them back.

### Definition

```rust
pub struct SerializeHex;

#[cgp_impl(SerializeHex)]
#[uses(CanSerializeValue<String>)]
impl<Value> ValueSerializer<Value>
where
    Value: ToHex,
{ ... }

#[cgp_impl(SerializeHex)]
#[uses(CanDeserializeValue<'de, String>)]
impl<'de, Value> ValueDeserializer<'de, Value>
where
    Value: FromHex<Error: Display>,
{ ... }
```

`ToHex` and `FromHex` are the `hex` crate's traits, implemented for byte containers such as `Vec<u8>`
and, for `FromHex`, fixed-size byte arrays.

### Behavior

Serializing writes the bytes as lowercase hexadecimal through the context's wiring for `String`, so
`b"hi"` becomes `"6869"`. Deserializing reads a `String` through the context and decodes it, reporting
the `hex` crate's error message on bad input: `"6G"` fails with `Invalid character 'G' at position 1`.
Uppercase input is accepted, as the `hex` crate accepts it.

### Context dependencies

`CanSerializeValue<String>` and `CanDeserializeValue<'de, String>`, usually wired to `UseSerde` or
`SerializeString`.

### Pairing

The same struct implements both directions, and the two round-trip.

## `SerializeBase64`

`SerializeBase64` encodes bytes as a standard, padded base64 string and decodes them into a `Vec<u8>`.

### Definition

```rust
pub struct SerializeBase64;

#[cgp_impl(SerializeBase64)]
#[uses(CanSerializeValue<String>)]
impl<Value> ValueSerializer<Value>
where
    Value: AsRef<[u8]>,
{ ... }

#[cgp_impl(SerializeBase64)]
#[uses(CanDeserializeValue<'de, String>)]
impl<'de> ValueDeserializer<'de, Vec<u8>> { ... }
```

### Behavior

Both directions use the standard alphabet with padding. Serializing writes `b"hi"` as `"aGk="`;
deserializing reads `"aGk="` back, and rejects the unpadded `"aGk"` with `Invalid padding`. The
deserializing side produces only `Vec<u8>`, while the serializing side accepts any `AsRef<[u8]>`.

### Context dependencies

`CanSerializeValue<String>` and `CanDeserializeValue<'de, String>`.

### Pairing

The same struct implements both directions, and the two round-trip for `Vec<u8>`.

### Known issues

- **Only the standard padded alphabet is supported.** There is no URL-safe or unpadded variant, and no
  way to choose one.

## `SerializeRfc3339Date`

`SerializeRfc3339Date` encodes a `DateTime<Utc>` as an RFC 3339 string and decodes one back.

### Definition

```rust
pub struct SerializeRfc3339Date;

#[cgp_impl(SerializeRfc3339Date)]
#[uses(CanSerializeValue<String>)]
impl ValueSerializer<DateTime<Utc>> { ... }

#[cgp_impl(SerializeRfc3339Date)]
#[uses(CanDeserializeValue<'de, String>)]
impl<'de> ValueDeserializer<'de, DateTime<Utc>> { ... }
```

### Behavior

Serializing uses `chrono`'s `to_rfc3339`, which writes a `+00:00` offset and keeps sub-second
precision when the value has any: 14:15 on 3 November 2025 is `"2025-11-03T14:15:00+00:00"`, and the
same instant plus 250 milliseconds is `"2025-11-03T14:15:00.250+00:00"`. Deserializing accepts any
RFC 3339 offset and converts to UTC, so `"2025-11-03T16:15:00+02:00"` reads as 14:15 UTC. Input that
is not a full RFC 3339 timestamp fails with `chrono`'s message; a bare date such as `"2025-11-03"`
gives `premature end of input`.

### Context dependencies

`CanSerializeValue<String>` and `CanDeserializeValue<'de, String>`.

### Pairing

The same struct implements both directions, and the two round-trip, with a non-UTC offset normalized
to UTC.

## `SerializeTimestamp`

`SerializeTimestamp` encodes a `DateTime<Utc>` as a Unix timestamp in whole seconds and decodes one
back.

### Definition

```rust
pub struct SerializeTimestamp;

#[cgp_impl(SerializeTimestamp)]
#[uses(CanSerializeValue<i64>)]
impl ValueSerializer<DateTime<Utc>> { ... }

#[cgp_impl(SerializeTimestamp)]
#[uses(CanDeserializeValue<'de, i64>)]
impl<'de> ValueDeserializer<'de, DateTime<Utc>> { ... }
```

### Behavior

Serializing writes the number of whole seconds since the Unix epoch through the context's wiring for
`i64`, so 14:15 UTC on 3 November 2025 becomes `1762179300`. Any sub-second part is dropped, so a value
with 250 milliseconds serializes to the same number and does not round-trip exactly. Deserializing
reads an `i64` and builds the instant; a timestamp outside the range `chrono` can represent fails with
`invalid timestamp`.

### Context dependencies

`CanSerializeValue<i64>` and `CanDeserializeValue<'de, i64>`. A context that has no `i64` field still
needs an `i64` entry, which is why the demo's second application wires `i64` where the first does not.

### Pairing

The same struct implements both directions, and the two round-trip for values with no sub-second part.

### Known issues

- **Sub-second precision is lost.** The timestamp is whole seconds, with no millisecond or nanosecond
  variant.

## Source

- [`crates/cgp-serde-extra/src/providers/hex.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-extra/src/providers/hex.rs) — `SerializeHex`.
- [`crates/cgp-serde-extra/src/providers/base64.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-extra/src/providers/base64.rs) — `SerializeBase64`.
- [`crates/cgp-serde-extra/src/providers/date.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-extra/src/providers/date.rs) — `SerializeRfc3339Date`.
- [`crates/cgp-serde-extra/src/providers/timestamp.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-extra/src/providers/timestamp.rs) — `SerializeTimestamp`.

## Public material derived from this

The "Wiring an application" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), where the two applications differ by
these providers, and the rustdoc for all four.
