# cgp-serde reference

This directory documents every public item in the cgp-serde crates, grouped by family, with one
document per family following the entry template in
[../../AGENTS.md](../../AGENTS.md#reference-entries). The tables below list every item so a reader can
find a provider by what it handles, see what a context must wire for it, and know where to import it
from. Read the [architecture](../architecture/README.md) first for the ideas the providers share,
above all [re-entry](../architecture/reentrant-providers.md), which is what the "Re-enters for" column
refers to.

## Components, adapters, and other public items

The two components and their adapters live in the core crate; the remaining items belong to the JSON
and allocation crates. Each component is defined with `#[cgp_component]`, so it also has a provider
trait and a `…Component` wiring key.

| Item | Kind | Import from |
|---|---|---|
| `CanSerializeValue<Value: ?Sized>` / `ValueSerializer` / `ValueSerializerComponent` | component | `cgp_serde::components` |
| `CanDeserializeValue<'de, Value>` / `ValueDeserializer` / `ValueDeserializerComponent` | component | `cgp_serde::components` |
| `SerializeWithContext<'a, Context, T>` | adapter implementing `serde::Serialize` | `cgp_serde::types` |
| `DeserializeWithContext<'a, Context, Value>` | adapter implementing `serde::de::DeserializeSeed` | `cgp_serde::types` |
| `SerializeJson`, `DeserializeJson<T>` | `Code` types for the JSON `TryComputer` providers | `cgp_serde_json::code` |
| `CanDeserializeJsonString<T>` | blanket trait with `deserialize_json_string` | `cgp_serde_json::impls` |
| `CanAlloc<'a, T>` / `Allocator` / `AllocatorComponent` | component | `cgp_serde_alloc::traits` |
| `HasArena<'a, T>` / `ArenaGetter` / `ArenaGetterComponent` | getter component | `cgp_serde_typed_arena::traits` |

Both serialization components and `HasArena` also carry `#[derive_delegate(UseDelegate<…>)]`, which
generates the legacy `UseDelegate` dispatch impl. Contexts on the `v0.8.0` branch dispatch with the
`open` statement instead, which needs no attribute, per
[dispatching per type](../../../cgp/guides/dispatching-per-type.md).

## Serialization and deserialization providers

Every provider below implements `ValueSerializer`, `ValueDeserializer`, or both. The "Handles" column
gives the bounds on the value type, split by direction where a provider serves both. The "Re-enters
for" column is what the provider asks of the context, and so what the context must also wire.

| Provider | Crate | Direction | Handles | Re-enters for |
|---|---|---|---|---|
| `UseSerde` | `cgp-serde` | both | ser: `Value: Serialize`; de: `Value: Deserialize<'de>` | nothing |
| `SerializeString` | `cgp-serde` | both | ser: `Value: AsRef<str>`; de: `String` only | nothing |
| `SerializeBytes` | `cgp-serde` | both | ser: `Value: AsRef<[u8]>`; de: `Value: From<&'de [u8]>` | nothing |
| `TryDeserializeBytes` | `cgp-serde` | de | `Value: TryFrom<&'de [u8]>` | nothing |
| `SerializeWithDisplay` | `cgp-serde` | ser | `Value: Display` | `String` |
| `DeserializeWithFromStr` | `cgp-serde` | de | `Value: FromStr` | `&'de str` |
| `SerializeFrom<T>` | `cgp-serde` | both | ser: `Value: Clone + Into<T>`; de: `T: Into<Value>` | `T` |
| `TrySerializeFrom<T>` | `cgp-serde` | both | ser: `Value: Clone + TryInto<T>`; de: `T: TryInto<Value>` | `T` |
| `SerializeDeref` | `cgp-serde` | ser | `Value: Deref` | `Value::Target` |
| `SerializeIterator` | `cgp-serde` | ser | `for<'a> &'a Value: IntoIterator` | each item, a reference for `Vec` and slices |
| `DeserializeExtend` | `cgp-serde` | de | `Value: Default + IntoIterator<Item = Item> + Extend<Item>` | `Item` |
| `SerializeFields` | `cgp-serde` | ser | `Value: HasFields`, plus `HasField` per field | each field type |
| `DeserializeRecordFields` | `cgp-serde` | de | `Value: HasFields`, plus a builder | each field type |
| `DeserializeDefault<Provider>` | `cgp-serde` | de | `Value: Default`; `Provider` handles `Value` | nothing; calls `Provider` |
| `SerializeHex` | `cgp-serde-extra` | both | ser: `Value: ToHex`; de: `Value: FromHex` | `String` |
| `SerializeBase64` | `cgp-serde-extra` | both | ser: `Value: AsRef<[u8]>`; de: `Vec<u8>` only | `String` |
| `SerializeRfc3339Date` | `cgp-serde-extra` | both | `DateTime<Utc>` only | `String` |
| `SerializeTimestamp` | `cgp-serde-extra` | both | `DateTime<Utc>` only | `i64` |
| `DeserializeAndAllocate` | `cgp-serde-alloc` | de | `&'a Value` | owned `Value`, plus `CanAlloc<'a, Value>` |

Where a bound names an error type, such as `TryFrom`'s or `FromStr`'s, that error must implement
`Display`, because the provider reports it through Serde's `Error::custom`. Every provider is imported
from its crate's `providers` module, such as `cgp_serde::providers::SerializeFields` or
`cgp_serde_extra::providers::SerializeHex`.

## Other providers

Two further families implement components other than the serialization pair. The JSON providers
implement CGP's [`TryComputer`](../../../cgp/reference/components/try_computer.md) handler, and the
allocation provider implements `CanAlloc`.

| Provider | Crate | Implements | Requires of the context |
|---|---|---|---|
| `SerializeToJsonString` | `cgp-serde-json` | `TryComputer<Code, &Value>`, output `String` | `CanSerializeValue<Value>`, `CanRaiseError<serde_json::Error>` |
| `DeserializeFromJsonReader` | `cgp-serde-json` | `TryComputer<DeserializeJson<Value>, R>` for a `serde_json` reader `R` | `CanDeserializeValue<'de, Value>`, `CanRaiseError<serde_json::Error>` |
| `DeserializeFromJsonString<In = DeserializeFromJsonReader>` | `cgp-serde-json` | `TryComputer<Code, S>` for `S: AsRef<str>` | whatever `In` requires |
| `AllocateWithArena` | `cgp-serde-typed-arena` | `Allocator<'a, Value>` | `HasArena<'a, Value>` |

## The catalog

Register each reference document here, in [../README.md](../README.md), and in
[../../../summary.md](../../../summary.md) in the same change.

- [records.md](records.md) — `SerializeFields` and `DeserializeRecordFields`: serializing a struct as a
  map and reading one back through the optional builder, with no serialization-specific derive.

## Public material derived from this

The provider catalog of the repository README, and the "Writing serializers" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md).
