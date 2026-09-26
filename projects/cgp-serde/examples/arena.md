# `arena`

Borrowed `&'a Coord` values deserialized from JSON into an arena, through the library's layered
allocation crates, so that the allocator is a wiring entry rather than code inside the deserializer.

- **Source** — [crates/cgp-serde-tests/src/tests/arena.rs](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-tests/src/tests/arena.rs)
- **Run** — `cargo test -p cgp-serde-tests arena::`
- **Needs** — nothing beyond the build
- **Result** — passes; asserts that the deserialized `Payload` has id 8 and the two expected
  coordinates

## The same scenario, with the library's providers

This test deserializes the same JSON as [`arena_simplified`](arena-simplified.md), and differs in two
ways. It defines no provider or getter of its own, and imports the layered items instead:

```rust
use cgp_serde_alloc::providers::DeserializeAndAllocate;
use cgp_serde_alloc::traits::AllocatorComponent;
use cgp_serde_typed_arena::providers::AllocateWithArena;
use cgp_serde_typed_arena::traits::ArenaGetterComponent;
```

Its data types also derive only the field traits each direction needs, rather than `CgpData`.
Deserializing a record needs `HasFields` to list the fields and `BuildField` to fill them, per
[derive-free records](../architecture/derive-free-records.md#what-a-struct-still-opts-into), and the
containing struct is named `Payload` where the simplified test says `Cluster`:

```rust
#[derive(Debug, PartialEq, Eq, HasFields, BuildField)]
pub struct Payload<'a> {
    pub id: u64,
    pub coords: Vec<&'a Coord>,
}
```

`Coord` derives the same two traits. The context is unchanged: `App<'a>`, an environmental context with
one field holding a borrowed `&'a Arena<Coord>`.

## Wiring the three layers

The context wires each layer of the allocation support separately, as
[context services](../architecture/context-services.md#the-layers) describes: the deserializer for the
borrowed type, the allocation component it calls, and the arena getter that component reads.

```rust
delegate_components! {
    <'a> App<'a> {
        // ... open statement and error entries ...
        ArenaGetterComponent: UseField<Symbol!("arena")>,
        AllocatorComponent: AllocateWithArena,

        @ValueDeserializerComponent.u64: UseSerde,
        @ValueDeserializerComponent.[Coord, <'b> Payload<'b>]: DeserializeRecordFields,
        @ValueDeserializerComponent.<'b> &'b Coord: DeserializeAndAllocate,
        @ValueDeserializerComponent.<'b> Vec<&'b Coord>: DeserializeExtend,
        // ... JSON entries ...
    }
}
```

The two service entries are plain mappings. [`HasArena`](../reference/allocation.md#hasarena) is a
[`#[cgp_getter]`](../../../cgp/reference/macros/cgp_getter.md) component, so the context names the field
that supplies the arena with [`UseField`](../../../cgp/reference/providers/use_field.md). The entry is
not keyed per type, so every `HasArena<'a, T>` lookup reads the one `arena` field, which suits a context
with a single arena. A context with an arena per type opens the getter and keys it on `T`, as the
[allocation reference](../reference/allocation.md#hasarena) shows.

The allocator is the layer this test exists to show. [`CanAlloc`](../reference/allocation.md#canalloc)
is wired to [`AllocateWithArena`](../reference/allocation.md#allocatewitharena), and
[`DeserializeAndAllocate`](../reference/allocation.md#deserializeandallocate) calls it without knowing
what an arena is. Swapping the allocator therefore means changing the `AllocatorComponent` entry and
nothing in the deserializer.

Leaving out the allocator entry shows how the layers fail. A probe kept the getter and the
deserializer entries but dropped `AllocatorComponent: AllocateWithArena`, then checked the borrowed
type:

```rust
check_components! {
    #[check_trait(CanDeserializeApp)]
    <'de, 'a> App<'a> {
        ValueDeserializerComponent: (Life<'de>, &'a Coord),
    }
}
```

`cargo cgp check` failed on that entry and named the omitted component:

```text
error[E0277]: [CGP-E001] the consumer trait `CanDeserializeValue<&Coord>` is not implemented for context `App<'_>`
  = note: root cause: [CGP-E107] context `App<'_>` does not contain any delegate entry for `AllocatorComponent`
```

The chain beneath it runs through `DeserializeAndAllocate` to the `CanAlloc<Coord>` that provider
requires. A service a provider takes from the context is reported like any other missing entry, and
the fix is the allocator entry.

## Checking the getter and the deserializer

One table checks the getter at its lifetime and value type, and a second checks every value type the
deserializer handles:

```rust
check_components! {
    #[check_trait(CanUseApp)]
    <'a> App<'a> {
        ArenaGetterComponent:
            (Life<'a>, Coord),

    }
}
```

The getter component has a lifetime and a type parameter, so its check entry is a tuple with the
lifetime lifted into [`Life`](../../../cgp/reference/types/life.md). The second table, `CanDeserializeApp`,
lists `u64`, `Coord`, `&'a Coord`, and `Payload<'a>`, each paired with `Life<'de>`. Neither table checks
`AllocatorComponent` on its own, but the check on `&'a Coord` reaches it, as the probe above shows.

## Deserializing

The test builds the arena and the context and calls
[`deserialize_json_string`](../reference/json.md#candeserializejsonstring), exactly as the simplified
test does, and the resulting `Payload<'_>` borrows its coordinates from the arena.

## What it demonstrates

- The layered allocation crates, where the allocator is a wiring choice: see
  [context services](../architecture/context-services.md) and [allocation](../reference/allocation.md),
  whose wiring section is drawn from this test.
- A getter component wired to a field with `UseField`, and checked with `Life`: see
  [`HasArena`](../reference/allocation.md#hasarena).
- The minimum derives for deserializing a record: see
  [records](../reference/records.md).
- The form the top-level [modular serialization example](../../../examples/modular-serialization.md)
  teaches.

## Known issues

- **The JSON handler entries are dead wiring.** The table opens `TryComputerComponent` and wires
  `SerializeJson` to `SerializeToJsonString` and `DeserializeJson<T>` to `DeserializeFromJsonString`, but
  the test calls `deserialize_json_string`, which does not go through them. A probe with those entries,
  the `TryComputerComponent` opening, and their imports removed built and deserialized the same
  `Payload`. The `SerializeJson` entry could not work if called, because the context wires no
  serializers; wiring is lazy, so an entry nothing uses compiles. The `DeserializeJson<T>` entry does
  work: in a probe, `try_compute(PhantomData::<DeserializeJson<Payload<'_>>>, json)` on a context with
  the same deserialization wiring and that one handler entry deserialized the same value. See [issues.md](../issues.md#housekeeping).

## Public material derived from this

The "Arena-allocating deserialization" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), which should teach this form.
