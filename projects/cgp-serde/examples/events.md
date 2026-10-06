# `events`

A batch of chat events, an enum whose variants hold records, written to JSON and read back by two
applications that encode bytes and dates differently, then read by each with the other's choices to
show that an encoding lives in the wiring rather than in the data.

- **Source**:
  [crates/cgp-serde-examples/examples/events.rs](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-examples/examples/events.rs)
- **Run**: `cargo run -p cgp-serde-examples --example events`; its test runs with
  `cargo test -p cgp-serde-examples --example events`
- **Needs**: nothing beyond the build
- **Result**: prints both applications' JSON, that each reads its own JSON back, and the error each
  gives reading the other's; the test asserts all of them

## Records inside variants inside a record

A chat client syncs a batch of events with a server. Each event is one of several kinds, so it is an
enum deriving `CgpVariant`, and each kind carries a record deriving `CgpData`. The batch is a record
holding a `Vec` of events:

```rust
#[derive(Debug, PartialEq, CgpData)]
pub struct Posted {
    pub message_id: u64,
    pub author_id: u64,
    pub date: DateTime<Utc>,
    pub encrypted_data: Vec<u8>,
}

#[derive(Debug, PartialEq, CgpVariant)]
pub enum ChatEvent {
    Posted(Posted),
    Edited(Edited),
    Reacted(Reacted),
    HistoryCleared,
}

#[derive(Debug, PartialEq, CgpData)]
pub struct SyncBatch {
    pub device_key: Vec<u8>,
    pub events: Vec<ChatEvent>,
}
```

`Edited` holds a `message_id`, a `date`, and new `encrypted_data`; `Reacted` holds a `message_id`,
an `author_id`, and an `emoji: String`. The emoji is a `String` rather than a `char`, because many
emoji are several Unicode scalar values: the example's 👍🏽 is two. `HistoryCleared` carries no data,
so it has no fields, and `CgpVariant` gives it the payload `Nil`; see
[variants](../reference/variants.md). None of the types derives anything from Serde, and none names
an encoding.

## Two applications, three different entries

`ServerApp` stores batches compactly and `InspectorApp` writes them for people to read. Both are
fieldless environmental contexts that open both serialization components and key their entries on
the value type. The server's table:

```rust
delegate_components! {
    ServerApp {
        open {
            ValueSerializerComponent,
            ValueDeserializerComponent,
        };

        @ValueSerializerComponent.<'a, T> &'a T: SerializeDeref,
        @ValueSerializerComponent.[i64, u64, String]: UseSerde,
        @ValueSerializerComponent.Nil: SerializeUnit,
        @ValueSerializerComponent.Vec<u8>: SerializeBase64,
        @ValueSerializerComponent.DateTime<Utc>: SerializeTimestamp,
        @ValueSerializerComponent.[Posted, Edited, Reacted, SyncBatch]: SerializeRecordFields,
        @ValueSerializerComponent.ChatEvent: SerializeVariantFields,
        @ValueSerializerComponent.Vec<ChatEvent>: SerializeIterator,

        @ValueDeserializerComponent.[i64, u64, String]: UseSerde,
        @ValueDeserializerComponent.Nil: SerializeUnit,
        @ValueDeserializerComponent.Vec<u8>: SerializeBase64,
        @ValueDeserializerComponent.DateTime<Utc>: SerializeTimestamp,
        @ValueDeserializerComponent.[Posted, Edited, Reacted, SyncBatch]: DeserializeRecordFields,
        @ValueDeserializerComponent.ChatEvent: DeserializeVariantFields,
        @ValueDeserializerComponent.Vec<ChatEvent>: DeserializeExtend,
    }
}
```

The source spreads each entry over two lines. `InspectorApp` wires `SerializeHex` where the server
wires `SerializeBase64`, `SerializeRfc3339Date` where it wires `SerializeTimestamp`, and has no
`i64` entry, which only the timestamp encoding needs. The other entries are the same in both tables.

Every type the traversal reaches has an entry in each direction: the three records and the batch
through the [record providers](../reference/records.md), `ChatEvent` through the
[variant providers](../reference/variants.md), the `Vec` of events through
[`SerializeIterator` and `DeserializeExtend`](../reference/collections.md), the reference entry that
iterating the `Vec` needs, and `Nil` for `HistoryCleared`. Each context checks all of them with two
`check_components!` tables, the deserializing one with `Life<'de>`.

## Writing and reading through the adapters

The example writes through
[`SerializeWithContext`](../reference/context-adapters.md#serializewithcontext) and reads by
driving a [`DeserializeWithContext`](../reference/context-adapters.md#deserializewithcontext) seed
with a `serde_json::Deserializer`, so `serde_json`'s errors come back unchanged and neither context
wires error components:

```rust
fn from_json<Context>(context: &Context, json: &str) -> Result<SyncBatch, serde_json::Error>
where
    Context: for<'de> CanDeserializeValue<'de, SyncBatch>,
{
    let mut deserializer = serde_json::Deserializer::from_str(json);
    let batch = DeserializeWithContext::new(context).deserialize(&mut deserializer)?;
    deserializer.end()?;
    Ok(batch)
}
```

A matching `to_json` writes pretty-printed JSON. `main` prints what both produce, and the example's
test asserts the same values.

## Output

Each application writes the batch with its own choices at every level, inside the enum as well as
inside the records. The first event, from the server and then from the inspector:

```json
{"Posted": {"message_id": 1, "author_id": 2, "date": 1762179300, "encrypted_data": "SGVsbG8="}}
{"Posted": {"message_id": 1, "author_id": 2, "date": "2025-11-03T14:15:00+00:00", "encrypted_data": "48656c6c6f"}}
```

The example prints the documents pretty-printed; the lines above are condensed. The `device_key` is
`"ZGV2aWNlLTc="` from the server and `"6465766963652d37"` from the inspector, `Reacted` keeps its
emoji as written, and `HistoryCleared` is `{"HistoryCleared": null}` from both, since both wire
`Nil` to [`SerializeUnit`](../reference/variants.md#serializeunit). Serde's derive would write the
bare name `"HistoryCleared"` instead. Each application reads its own document back into a batch
equal to the original. The dates are whole seconds, because a Unix timestamp drops anything finer,
so a date with milliseconds would not survive the server's round trip.

## Reading the other application's JSON

**Each application then reads the other's document, and the two directions fail differently.** The
inspector reading the server's JSON fails on the first field, because base64 is not hex:

```text
Invalid character 'Z' at position 0 at line 2 column 30
```

The server reading the inspector's JSON does not fail there. The hex string `"6465766963652d37"`
uses only characters base64 allows and has a valid length, so the server decodes it as base64 into
different bytes, without an error. It fails only at the first date, which is a string where it
expects a number:

```text
invalid type: string "2025-11-03T14:15:00+00:00", expected i64 at line 8 column 43
```

An encoding is not self-describing, and nothing in the data types records which one was used. Two
ends of a channel must therefore wire the same choices, and a mismatch can pass unnoticed until a
value happens not to fit.

## Try a change

**Removing the server's `Nil` entry for reading makes every type that contains an event fail its
check.** Delete `@ValueDeserializerComponent.Nil: SerializeUnit` from `ServerApp` and the
`(Life<'de>, Nil)` entry from its deserializer check, then run `cargo cgp check`. The check fails on
the three types that contain an event, and the tool names the missing entry as the root cause:

```text
error[E0277]: [CGP-E001] the consumer traits `CanDeserializeValue<ChatEvent>`, `CanDeserializeValue<Vec<ChatEvent>>`, and `CanDeserializeValue<SyncBatch>` are not implemented for context `ServerApp`
    = note: root cause: [CGP-E107] context `ServerApp` does not contain any delegate entry for `@ValueDeserializerComponent.Nil`
```

The dependency chain below the root cause runs from `SyncBatch` through the `Vec` and `ChatEvent`,
then down each variant of `Enum! { … }` to `HistoryCleared(Nil)`. No struct holds a `Nil`, so the
entry is needed only because an event may be `HistoryCleared`.

## What it demonstrates

- The record and variant providers together, in both directions: see
  [records](../reference/records.md) and [variants](../reference/variants.md).
- A context's choices reaching through an enum into the records its variants hold: see
  [re-entrant providers](../architecture/reentrant-providers.md).
- A variant with no fields, whose `Nil` payload the context wires: see
  [variants](../reference/variants.md#wiring-the-pair).
- Encodings as a wiring decision both ends of a channel must share: see
  [component design](../architecture/component-design.md).

## Known issues

- **The shared entries are repeated**, as in [`messages`](messages.md#known-issues): the library
  publishes no namespace of defaults.
- **The batch works only in self-describing formats.** The records inside the variants are written
  as maps without a length, so postcard rejects the batch and RON shows the records in map syntax;
  see [records](../reference/records.md#known-issues).

## Public material derived from this

The `examples/events` page of the
[cgp-serde project section](../../../website/projects/cgp-serde.md).
