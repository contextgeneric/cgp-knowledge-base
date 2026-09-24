# Using a format

cgp-serde works with a Serde format through the format's ordinary `Serializer` and `Deserializer`, so
using one is a matter of handing it a context-aware value. This guide shows how to do that with
`serde_json`, which formats work, and how to write the deserialization entry point a format lacks. Why
the approach works for any format is explained in [the bridge to Serde](../architecture/serde-bridge.md).

## Serialize with any format

**Wrap the value and the context in `SerializeWithContext` and pass it wherever the format expects a
`Serialize` value.** No format needs changes and no per-format code exists:

```rust
let compact = serde_json::to_string(&SerializeWithContext::new(&app, &archive))?;
let pretty = serde_json::to_string_pretty(&SerializeWithContext::new(&app, &archive))?;
let ron = ron::to_string(&SerializeWithContext::new(&app, &archive))?;
```

The format's own error comes back, since the adapter involves none of CGP's error handling. A context
that wants serialization to be a wireable operation raising its own error type uses
[`SerializeToJsonString`](../reference/json.md#serializetojsonstring) through `try_compute` instead,
which produces compact JSON only.

## Deserialize with `serde_json`

`serde_json` has three entry points in cgp-serde, and the choice depends on where the input comes from
and whether the result borrows from it:

- **`deserialize_json_string`** — the convenience method from
  [`CanDeserializeJsonString`](../reference/json.md#candeserializejsonstring). Takes a `&str`, needs no
  handler wiring, and cannot produce a value that borrows from the input string. Annotate the result's
  type, since the method takes no turbofish.
- **`DeserializeFromJsonReader`** — the [reader provider](../reference/json.md#deserializefromjsonreader),
  wired under `@TryComputerComponent.<T> DeserializeJson<T>` and called with `try_compute`. Takes any
  `serde_json` reader: a `StrRead` for strings, a `SliceRead` for bytes, or an `IoRead` for an
  `io::Read`, and can borrow from a `StrRead` or `SliceRead` input.
- **The seed directly** — build a `serde_json::Deserializer`, drive a
  [`DeserializeWithContext`](../reference/context-adapters.md#deserializewithcontext) seed with it, and
  call `end` to reject trailing input. Needs no error components at all.

The first two need the context's error components, and the seed needs none; see
[wiring a context](wiring-a-context.md#wire-the-error-components-when-the-json-providers-are-used).

## Choose a format that fits the output

**Self-describing text formats work with the library as it stands; length-prefixed binary formats do
not yet.** Two properties of the output decide it:

- **Records are maps.** Structs serialized through `SerializeFields` arrive at the format as maps, so
  JSON is unaffected and RON writes `{"a":1}` rather than its struct syntax. Deserializing expects a
  map in return.
- **Lengths are unknown.** Records and collections are started without a length, so postcard rejects
  them with `SerializeSeqLengthUnknown`. Any format that must write a length before the elements has
  the same problem.

`SerializeBytes` adds a third, JSON-specific limit: it writes bytes as a JSON array but reads them only
from an unescaped string, so bytes do not round-trip through JSON. Wire a text encoding such as
[`SerializeHex` or `SerializeBase64`](../reference/encodings.md) for binary data in a text format.

## Write the deserialization entry point for another format

**A format without cgp-serde helpers needs only the few lines the seed pattern takes.** Build the
format's deserializer, drive the seed, and check for trailing input if the format supports it. With
RON:

```rust
let mut deserializer = ron::Deserializer::from_str(&text)?;
let value: Rec = DeserializeWithContext::new(&app).deserialize(&mut deserializer)?;
deserializer.end()?;
```

To make the entry point a wireable operation, write a `TryComputer` provider on the model of
`DeserializeFromJsonReader`: it takes the format's input, deserializes through the context, and raises
the format's error with `CanRaiseError`.

## Public material derived from this

The usage section of the repository README, and the format list on the page about what the library does
not do in the planned [cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md).
