# String and byte providers

The string and byte providers encode text and binary data directly through Serde's string and byte
methods, without calling back into the context. `SerializeString` handles anything that is a string,
`SerializeBytes` anything that is a byte slice, and `TryDeserializeBytes` builds a value from bytes by a
fallible conversion. They are leaf providers: a context reaches them for the text and binary types at
the bottom of its data, and several of the context's other choices, such as the hex and base64
[encodings](encodings.md), end in a string that one of these providers, or `UseSerde`, writes out.

## `SerializeString`

`SerializeString` serializes anything viewable as a `str` as a Serde string, and deserializes an owned
`String`.

### Definition

```rust
pub struct SerializeString;

#[cgp_impl(SerializeString)]
impl<Value> ValueSerializer<Value>
where
    Value: AsRef<str>,
{ ... }

#[cgp_impl(SerializeString)]
impl<'a> ValueDeserializer<'a, String> { ... }
```

`SerializeString` also implements Serde's `Visitor` with `Value = String`, accepting both `visit_str`
and `visit_string`, which is what the deserializing impl hands to `deserialize_string`.

### Behavior

Serializing writes the string with `serialize_str`, so `String`, `&str`, `Box<str>`, and any other
`AsRef<str>` type produce a plain string; with JSON, `"x\ny"` is written with its newline escaped. A
borrowed `&'a str` is served by wiring that type itself, since `str` cannot be wired on its own:
`@ValueSerializerComponent.<'a> &'a str: SerializeString`.

Deserializing produces only `String`. It accepts a borrowed or an owned string from the deserializer,
so escaped JSON strings work: `"a\nb"` deserializes to a string containing a newline. Any other input
is a type error from the deserializer; with JSON, the number `5` fails with an
`invalid type: integer ..., expected string` error.

### Context dependencies

None.

### Pairing

The same struct implements both directions, with the deserializing side limited to `String`.

## `SerializeBytes`

`SerializeBytes` serializes anything viewable as a byte slice with Serde's byte method, and
deserializes any value constructible from a borrowed byte slice.

### Definition

```rust
pub struct SerializeBytes;

#[cgp_impl(SerializeBytes)]
impl<Value> ValueSerializer<Value>
where
    Value: AsRef<[u8]>,
{ ... }

#[cgp_impl(SerializeBytes)]
impl<'a, Value> ValueDeserializer<'a, Value>
where
    Value: From<&'a [u8]>,
{ ... }
```

`SerializeBytes` also implements Serde's `Visitor` with `Value = &'a [u8]`, and that visitor implements
only `visit_borrowed_bytes`.

### Behavior

Serializing calls `serialize_bytes`, so the output depends on how the format represents bytes. A binary
format may write them compactly; JSON has no byte type, and `serde_json` writes a byte slice as an
array of numbers, so `vec![1, 2, 3]` becomes `[1,2,3]`.

Deserializing asks for bytes and accepts them only when the deserializer can lend them for the input's
lifetime. With `serde_json` reading from a string, an unescaped JSON string is lent as its raw bytes,
so `"abc"` deserializes to `[97, 98, 99]`. Everything else fails: a JSON array, which is what
serializing produced, fails with `invalid type: sequence, expected bytes`, and a string with an escape
sequence fails with `invalid type: byte array, expected bytes`, because `serde_json` has to copy it and
offers owned bytes, which the visitor does not accept.

### Context dependencies

None.

### Pairing

The same struct implements both directions, but the two do not round-trip through JSON. See
[`TryDeserializeBytes`](#trydeserializebytes) for a fallible conversion from bytes.

### Known issues

- **The JSON output cannot be read back.** Serializing writes an array and deserializing rejects one.
- **Owned bytes are rejected.** The visitor implements only `visit_borrowed_bytes`, so an escaped JSON
  string, and any deserializer that cannot lend its input, such as one reading from an `io::Read`,
  fails. The value type is also bound to `From<&'de [u8]>`, which ties it to the input's lifetime even
  when it copies the bytes, as `Vec<u8>` does.

## `TryDeserializeBytes`

`TryDeserializeBytes` deserializes a value from a borrowed byte slice by a fallible `TryFrom`
conversion.

### Definition

```rust
#[cgp_impl(new TryDeserializeBytes)]
impl<'a, Value> ValueDeserializer<'a, Value>
where
    Value: TryFrom<&'a [u8], Error: Display>,
{ ... }
```

### Behavior

The provider reads bytes exactly as `SerializeBytes` does, through the same borrowed-only visitor, and
then converts them with `TryFrom`, reporting a failed conversion's `Display` message as a Serde custom
error. A fixed-size array is the typical target: `[u8; 3]` deserializes from the JSON string `"abc"`,
and from `"ab"` fails with `could not convert slice to array`.

A fixed-size array cannot be written directly as a key segment in `delegate_components!`, because
square brackets are the path-grouping syntax; wire a type alias instead, such as
`type Digest = [u8; 32];` and `@ValueDeserializerComponent.Digest: TryDeserializeBytes`.

### Context dependencies

None.

### Pairing

No serializing counterpart. A value that is `AsRef<[u8]>` serializes through
[`SerializeBytes`](#serializebytes), and a fixed-size array through
[`SerializeIterator`](collections.md) or `UseSerde`.

### Known issues

- **Owned bytes are rejected**, for the same reason as `SerializeBytes`.

## Source

- [`crates/cgp-serde/src/providers/string.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/string.rs) — `SerializeString` and its visitor.
- [`crates/cgp-serde/src/providers/bytes.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/bytes.rs) — `SerializeBytes`, `TryDeserializeBytes`, and the byte visitor.

## Public material derived from this

The "Writing serializers" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the rustdoc for the three
providers.
