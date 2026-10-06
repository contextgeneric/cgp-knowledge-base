# Testing

cgp-serde's tests live in one crate, `cgp-serde-tests`, in three kinds. Four **example tests**
each wire one scenario end to end and double as the library's only runnable examples. The
**provider suites** test one provider family in depth, one concern per file, against exact output.
The **compile-fail tests** pin wiring the providers reject, with its exact diagnostics. This
document records what each pins, which tests pin a known issue, and which parts of the library no
test exercises. On the `v0.8.0` branch, `cargo test --workspace` passes every test; the library
crates carry no tests and no doc tests of their own.

## The example tests

Each example test defines its own data types and contexts and is documented as an example in
[examples/](examples/README.md):

| File | Scenario | Runtime assertion | Compile-time checks |
|---|---|---|---|
| `basic.rs` | A `Payload` round-tripped through JSON by the `try_compute` JSON providers, with bytes as hex | the exact JSON string, and equality after the round trip | serializer and deserializer for all four value types |
| `messages.rs` | The two-application demo: `AppA` with hex and RFC 3339, `AppB` with base64 and timestamps | both pretty-printed JSON documents, exactly | serializer for all seven value types, for each context |
| `arena.rs` | Deserializing a `Payload<'a>` into an arena through the layered allocation crates | equality with the expected value | the arena getter, and the deserializer for four value types |
| `arena_simplified.rs` | The same with a test-local getter and `DeserializeAndAllocate`, as in the announcement post | equality with the expected value | the deserializer for four value types, plus a second table repeating one of them |

All four use `serde_json` as the format and `cgp-error-anyhow` for the error type where one is
needed. The checks use [`check_components!`](../../cgp/reference/macros/check_components.md), and
list deserializer entries with `Life<'de>`, as
[wiring a context](guides/wiring-a-context.md#check-every-value-type) recommends. Where a module
holds two tables for one context they carry explicit `#[check_trait]` names; `messages.rs` checks
two different contexts and relies on the derived names.

Two of the tests carry wiring or checks that add nothing. `arena.rs` opens `TryComputerComponent`
and wires both JSON codes although it deserializes through `deserialize_json_string`, which bypasses
them. `arena_simplified.rs` checks deserializing `Coord` in a table of its own that its second table
already covers. The [arena](examples/arena.md#known-issues) and
[simplified arena](examples/arena-simplified.md#known-issues) examples record both.

## The provider suites

**Each suite fixes one context and one set of data types, and asserts exact text.** The data types
derive only `CgpData`, and the suite's `check_components!` tables list every type in both
directions. The lockfile pins `serde_json`, `ron`, and `postcard`, so error messages are compared
whole, positions included. The shared helpers in `support/` run a value through a context and a
format:

- **`to_json` and `from_json`**: serialize compactly, and deserialize from a string, rejecting
  trailing input.
- **`from_json_reader`**: deserialize through an `io::Read`, which cannot lend borrowed data. It
  needs the value to deserialize for every input lifetime, so a test of a borrowed type drives the
  reader itself.
- **`assert_json_round_trip`**: assert the exact JSON and that it reads back to the same value.
- **`to_ron`, `from_ron`, `to_postcard`, and `from_postcard`**: the same for RON and postcard.

### Records

The `records/` suite tests [`SerializeRecordFields` and
`DeserializeRecordFields`](reference/records.md) through one context, `App`, plus a second context
in `context_choice.rs`:

- **`round_trip.rs`**: fields in declaration order; a one-field record; an empty record as `{}`;
  every leaf type, including `Option` as a value and as `null`; edge values (`u64::MAX`,
  `i64::MIN`, an empty string, escapes, and non-ASCII text); a nested record and a `Vec` of records,
  empty and not.
- **`deserialize_input.rs`**: keys in any order; unknown keys skipped whatever they hold; escaped
  keys; input through an `io::Read`; and the exact errors for a missing field, a duplicate field, a
  wrong field type, a sequence, and trailing input.
- **`context_choice.rs`**: the same record under two contexts, with its `Vec<u8>` field written as
  hex by one and base64 by the other, both read back.
- **`lifetimes.rs`**: a record with `&'a str` fields serialized from local strings, deserialized
  borrowing from a string, and rejected through an `io::Read` with
  `expected a borrowed string`.
- **`generic.rs`**: one `<T> Pair<T>` entry serving `Pair<u64>` and `Pair<Point>`.
- **`serde_compat.rs`**: a mirror struct with Serde's derive reads what the providers write, and the
  providers read what it writes.
- **`formats.rs`**: RON round-trips a record in map syntax, and postcard rejects one.

### Variants

The `variants/` suite tests [`SerializeVariantFields` and
`DeserializeVariantFields`](reference/variants.md) through one context, `App`, plus second contexts
in `unit_payload.rs` and `nesting.rs`:

- **`round_trip.rs`**: every variant of a four-variant enum tagged with its name; a one-variant
  enum; the first, middle, and last of ten variants.
- **`payloads.rs`**: scalar, `Option` (a value and `null`), collection (empty and not), byte, and
  enum payloads, each following the context's choice for its type.
- **`unit_payload.rs`**: a `()` payload written as `null` through `UseSerde` and as `{}` through a
  provider the test defines; each context rejecting the other's form; and the bare variant name
  rejected under both.
- **`deserialize_input.rs`**: the unknown-variant message listing every name; an escaped variant
  name; input through an `io::Read`; a variant name handed over as bytes, through Serde's `value`
  deserializers, matched and, when unknown, escaped in the error; and the exact errors for an empty
  object, two variants, a value that is not an enum, a wrong payload type, and trailing input.
- **`nesting.rs`**: enums in a record and a `Vec`; the same payload written as hex by one context
  and base64 by another.
- **`lifetimes.rs`**: a borrowed payload deserialized from a string, and `Token<'static>`
  serialized.
- **`formats.rs`**: RON round trips, including a generic enum, whose name RON validates; postcard
  writes and reads the declaration index, rejects an index out of range, and rejects a record
  payload.
- **`serde_compat.rs`**: an enum with Serde's derive agrees with the providers in JSON in both
  directions, and in RON and postcard for payloads that are not records.

## The compile-fail tests

**`tests/compile_fail.rs` runs [`trybuild`](https://docs.rs/trybuild) over `tests/compile_fail/`**,
each case a small program the providers reject, with its rustc output pinned in a `.stderr` file.
The output depends on the toolchain, so the files are regenerated with `TRYBUILD=overwrite` after
the pinned toolchain changes:

- **`variant_serializer_needs_static.rs`**: `Token<'a>` wired to `SerializeVariantFields` fails
  with `E0477`.
- **`recursive_enum.rs`**: an enum holding a `Box` of itself fails with `E0275`.
- **`recursive_record.rs`**: a record holding a `Vec` of itself fails with `E0275`.

## Tests that pin a known issue

**A test that pins a known issue asserts the current behavior and says so in its doc comment**, so
a fix fails it and names the entry in [issues.md](issues.md) to remove:

- **A missing `Option` field is an error**: `deserialize_input.rs`, per
  [records](reference/records.md#known-issues-1).
- **The sequence form of a record is rejected**: `deserialize_input.rs`, per the same section.
- **Records are maps to RON, and postcard rejects them**: the records suite's `formats.rs`, and the
  variants suite's `formats.rs` for a record payload, per
  [records](reference/records.md#known-issues) and the length entry in issues.md.
- **The variant serializer needs a `'static` enum**: `variant_serializer_needs_static.rs`, per
  [variants](reference/variants.md#known-issues).
- **Recursive types overflow the trait solver**: `recursive_enum.rs` and `recursive_record.rs`, per
  [re-entrant providers](architecture/reentrant-providers.md#what-re-entry-requires-of-a-context).

## What is exercised

The tests run these providers, in the directions listed:

- **Asserted output**: `UseSerde`, `SerializeString` (serializing), `SerializeHex`,
  `SerializeBase64`, `SerializeRecordFields`, `DeserializeRecordFields`, `SerializeVariantFields`,
  `DeserializeVariantFields`, `SerializeDeref`,
  `SerializeIterator`, `DeserializeExtend`, the serializing side of `SerializeRfc3339Date` and
  `SerializeTimestamp`, `DeserializeAndAllocate` in both forms, `AllocateWithArena` with `HasArena`
  wired through `UseField`, `SerializeToJsonString`, `DeserializeFromJsonString` over
  `DeserializeFromJsonReader`, and `deserialize_json_string`.
- **Formats**: JSON throughout, RON and postcard for records and enums.

## What is untested

No test exercises these, so their behavior is recorded in the reference from probes rather than from
the repository's own tests:

- **Providers never run**: `SerializeBytes`, `TryDeserializeBytes`, `SerializeWithDisplay`,
  `DeserializeWithFromStr`, `SerializeFrom`, `TrySerializeFrom`, and `DeserializeDefault`.
- **Directions never run**: deserializing with `SerializeString`, `SerializeRfc3339Date`, and
  `SerializeTimestamp`.
- **Inputs never used**: `DeserializeFromJsonReader` with a `SliceRead` or `IoRead`.
- **Failure paths outside the record and variant providers**: no test feeds invalid input to any
  other provider, so their error messages in the reference (invalid hex, out-of-range conversions,
  bad timestamps) are not pinned.
- **Most diagnostics**: the compile-fail tests pin rustc's raw output for three cases. The other
  diagnostics in [debugging wiring](guides/debugging-wiring.md), and every `cargo cgp check`
  rewrite, are not pinned.

Several of the defects in [issues.md](issues.md) sit in exactly these untested providers, which is
how they went unnoticed.

## Source

- [`crates/cgp-serde-tests/src/tests/`](https://github.com/contextgeneric/cgp-serde/tree/v0.8.0/crates/cgp-serde-tests/src/tests):
  the four example tests, the `records/` and `variants/` suites, and the `support/` helpers.
- [`crates/cgp-serde-tests/tests/`](https://github.com/contextgeneric/cgp-serde/tree/v0.8.0/crates/cgp-serde-tests/tests):
  the compile-fail runner and its cases.

## Public material derived from this

The one sentence on the `limitations` page of the
[cgp-serde project section](../../website/projects/cgp-serde.md) saying that the library is lightly
tested.
