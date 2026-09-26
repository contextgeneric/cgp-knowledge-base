# `messages`

The two-application demo: one nested archive of encrypted messages serialized by two contexts that
differ in three wiring entries, producing JSON with hex bytes and RFC 3339 dates from one and base64
bytes and Unix timestamps from the other.

- **Source** — [crates/cgp-serde-tests/src/tests/messages.rs](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-tests/src/tests/messages.rs)
- **Run** — `cargo test -p cgp-serde-tests messages -- --nocapture`
- **Needs** — nothing beyond the build
- **Result** — passes; prints both JSON documents, shown under [Output](#output), and asserts nothing

## Nested data that derives only `CgpData`

The archive is three nested structs, each carrying a byte field or a date whose encoding the
applications want to choose. The innermost shows the pattern:

```rust
#[derive(CgpData)]
pub struct EncryptedMessage {
    pub message_id: u64,
    pub author_id: u64,
    pub date: DateTime<Utc>,
    pub encrypted_data: Vec<u8>,
}
```

`MessagesByTopic` holds an `encrypted_topic: Vec<u8>` and a `Vec<EncryptedMessage>`, and
`MessagesArchive` holds a `decryption_key: Vec<u8>` and a `Vec<MessagesByTopic>`. None of them names
an encoding.

## Two tables that differ in three entries

`AppA` and `AppB` are fieldless environmental contexts, each opening the serializing component and
keying its entries on the value type. Most of the two tables is shared:

```rust
delegate_components! {
    AppA {
        open {ValueSerializerComponent};

        @ValueSerializerComponent.<'a, T> &'a T: SerializeDeref,
        @ValueSerializerComponent.[u64, String]: UseSerde,
        @ValueSerializerComponent.Vec<u8>: SerializeHex,
        @ValueSerializerComponent.DateTime<Utc>: SerializeRfc3339Date,
        @ValueSerializerComponent.[Vec<EncryptedMessage>, Vec<MessagesByTopic>]: SerializeIterator,
        @ValueSerializerComponent.[MessagesArchive, MessagesByTopic, EncryptedMessage]: SerializeFields,
    }
}
```

`AppB` repeats the table with three changes, the only lines that decide the format:

```rust
@ValueSerializerComponent.[i64, u64, String]: UseSerde,
@ValueSerializerComponent.Vec<u8>: SerializeBase64,
@ValueSerializerComponent.DateTime<Utc>: SerializeTimestamp,
```

The two contexts wire `Vec<u8>` to overlapping providers with no conflict, because each choice is
coherent only within its own context; see
[bypassing coherence](../../../cgp/concepts/coherence.md#restoring-coherence-locally).

## Entries the traversal needs

Several entries serve the traversal rather than the data, because every provider re-enters the context
for each nested value; see
[re-entrant providers](../architecture/reentrant-providers.md#what-re-entry-requires-of-a-context).

- **Each vector of structs** needs an entry of its own, `SerializeIterator`, in addition to the entry
  for its item type, because the vector is a value type the traversal reaches.
- **The generic reference entry** forwards every `&'a T` to `SerializeDeref`, because iterating a
  borrowed `Vec<EncryptedMessage>` yields `&EncryptedMessage`.
- **`String`** is wired although no field is a `String`, because the hex, base64, and RFC 3339
  encodings each produce one and serialize it through the context.
- **`i64`** is wired in `AppB` although no field is an `i64`, because `SerializeTimestamp` converts the
  date to one and serializes it through the context.

Leaving out the `i64` entry is an instructive mistake. A probe built a reduced copy of `AppB`, covering
`EncryptedMessage` and its vector, wired the scalars without `i64` while keeping the timestamp
encoding, and checked the date and the message vector:

```rust
@ValueSerializerComponent.[u64, String]: UseSerde,
@ValueSerializerComponent.DateTime<Utc>: SerializeTimestamp,
```

`cargo cgp check` failed on both checked types and named the one entry the context omits:

```text
error[E0277]: [CGP-E001] the consumer traits `CanSerializeValue<DateTime<Utc>>` and `CanSerializeValue<Vec<EncryptedMessage>>` are not implemented for context `AppB`
  = note: root cause: [CGP-E107] context `AppB` does not contain any delegate entry for `@ValueSerializerComponent.i64`
```

The dependency chain it prints under the root cause runs from `SerializeIterator` through
`SerializeDeref` and `SerializeFields` to `SerializeTimestamp`, which asks the context for the `i64`.
The fix is the `i64` entry; see
[debugging wiring](../guides/debugging-wiring.md#a-type-the-traversal-reaches-has-no-entry).

## Serializing through the adapter

Each context checks all seven value types with a plain `check_components!` table, whose derived names,
`__CheckAppA` and `__CheckAppB`, do not collide. The test then hands each context and the same archive
to `serde_json` through the [`SerializeWithContext`](../reference/context-adapters.md#serializewithcontext)
adapter:

```rust
let serialized =
    serde_json::to_string_pretty(&SerializeWithContext::new(&AppA, &archive)).unwrap();
println!("serialized with A: {serialized}");
```

Because the adapter is an ordinary `Serialize` value, neither context wires error components: any
`serde_json::Error` comes back unchanged.

## Output

With `--nocapture`, the test prints the archive twice. Each document follows its context's choices at
every level of nesting; the first message shows the difference. From `AppA`:

```json
{
  "message_id": 1,
  "author_id": 2,
  "date": "2025-11-03T14:15:00+00:00",
  "encrypted_data": "48656c6c6f2066726f6d20527573744c616221"
}
```

and from `AppB`:

```json
{
  "message_id": 1,
  "author_id": 2,
  "date": 1762179300,
  "encrypted_data": "SGVsbG8gZnJvbSBSdXN0TGFiIQ=="
}
```

The top-level `decryption_key` follows the same choice, written as `"746f702d736563726574"` by `AppA`
and `"dG9wLXNlY3JldA=="` by `AppB`. Both full documents match the ones the announcement post shows,
although the post's "Full Example" link leads to the `main` branch's version of this test, which wires
the same choices through `UseDelegate` tables.

## What it demonstrates

- Two applications encoding the same foreign types differently: see the top-level
  [modular serialization example](../../../examples/modular-serialization.md), which owns the teaching
  version of this scenario.
- Wiring every type a traversal reaches, including intermediate and reference types: see
  [wiring a context](../guides/wiring-a-context.md#wire-every-type-the-traversal-reaches).
- The four encodings in `cgp-serde-extra`: see [encodings](../reference/encodings.md).
- Serializing with an unmodified Serde format: see
  [using a format](../guides/formats.md#serialize-with-any-format).

## Known issues

- **The test asserts nothing.** It prints both documents, so a regression in any provider it runs would
  still pass as long as serialization succeeded. It is the only test that runs `SerializeDeref`,
  `SerializeIterator`, `SerializeBase64`, `SerializeRfc3339Date`, and `SerializeTimestamp`, so none of
  them has an asserted output; see [testing.md](../testing.md#what-is-exercised).
- **The shared entries are repeated.** The library publishes no namespace of defaults, so the two
  tables spell out every entry they share; see
  [wiring a context](../guides/wiring-a-context.md#share-wiring-between-contexts) and
  [issues.md](../issues.md#missing-features).

## Public material derived from this

The payoff of the "Wiring an application" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md).
