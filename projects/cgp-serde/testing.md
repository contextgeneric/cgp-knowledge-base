# Testing

cgp-serde's tests live in one crate, `cgp-serde-tests`, and consist of four runtime tests, each paired
with compile-time wiring checks. This document records what each test pins, what the checks assert, and
which parts of the library no test exercises. On the `v0.8.0` branch, `cargo test --workspace` passes
all four tests; the library crates carry no tests and no doc tests of their own.

## What each test pins

Each test file defines its own data types and contexts, so the files double as the library's only
runnable examples, and each is documented as one in [examples/](examples/README.md):

| File | Scenario | Runtime assertion | Compile-time checks |
|---|---|---|---|
| `basic.rs` | A `Payload` round-tripped through JSON by the `try_compute` JSON providers, with bytes as hex | the exact JSON string, and equality after the round trip | serializer and deserializer for all four value types |
| `messages.rs` | The two-application demo: `AppA` with hex and RFC 3339, `AppB` with base64 and timestamps | none; both outputs are printed | serializer for all seven value types, for each context |
| `arena.rs` | Deserializing a `Payload<'a>` into an arena through the layered allocation crates | equality with the expected value | the arena getter, and the deserializer for four value types |
| `arena_simplified.rs` | The same with a test-local getter and `DeserializeAndAllocate`, as in the announcement post | equality with the expected value | the deserializer for four value types, plus a second table repeating one of them |

All four use `serde_json` as the format and `cgp-error-anyhow` for the error type where one is needed.
The checks use [`check_components!`](../../cgp/reference/macros/check_components.md), and list
deserializer entries with `Life<'de>`, as
[wiring a context](guides/wiring-a-context.md#check-every-value-type) recommends. Where a module holds
two tables for one context they carry explicit `#[check_trait]` names; `messages.rs` checks two
different contexts and relies on the derived names.

Two of the tests carry wiring or checks that add nothing. `arena.rs` opens `TryComputerComponent` and
wires both JSON codes although it deserializes through `deserialize_json_string`, which bypasses them.
`arena_simplified.rs` checks deserializing `Coord` in a table of its own that its second table already
covers. The [arena](examples/arena.md#known-issues) and
[simplified arena](examples/arena-simplified.md#known-issues) examples record both.

## What is exercised

The tests run these providers, in the directions listed:

- **Asserted output** — `UseSerde`, `SerializeString` (serializing), `SerializeHex`,
  `SerializeFields`, `DeserializeRecordFields`, `DeserializeExtend`, `DeserializeAndAllocate` in both
  forms, `AllocateWithArena` with `HasArena` wired through `UseField`, `SerializeToJsonString`,
  `DeserializeFromJsonString` over `DeserializeFromJsonReader`, and `deserialize_json_string`.
- **Run but not asserted** — `SerializeDeref`, `SerializeIterator`, and the serializing side of
  `SerializeBase64`, `SerializeRfc3339Date`, and `SerializeTimestamp`, all in `messages.rs`. A
  regression in any of them would still pass, as long as the output serialized at all.

## What is untested

No test exercises these, so their behavior is recorded in the reference from probes rather than from
the repository's own tests:

- **Providers never run** — `SerializeBytes`, `TryDeserializeBytes`, `SerializeWithDisplay`,
  `DeserializeWithFromStr`, `SerializeFrom`, `TrySerializeFrom`, and `DeserializeDefault`.
- **Directions never run** — deserializing with `SerializeString`, `SerializeBase64`,
  `SerializeRfc3339Date`, and `SerializeTimestamp`.
- **Inputs never used** — `DeserializeFromJsonReader` with a `SliceRead` or `IoRead`, and any format
  other than JSON.
- **Failure paths** — no test feeds invalid input, so none of the error messages recorded in the
  reference (missing and duplicate fields, invalid hex, out-of-range conversions) is pinned.
- **Compile failures** — there are no compile-fail tests, so the diagnostics in
  [debugging wiring](guides/debugging-wiring.md) are not pinned either.

Several of the defects in [issues.md](issues.md) sit in exactly these untested providers, which is how
they went unnoticed.

## Source

- [`crates/cgp-serde-tests/src/tests/`](https://github.com/contextgeneric/cgp-serde/tree/v0.8.0/crates/cgp-serde-tests/src/tests)
  — the four test files.

## Public material derived from this

None yet.
