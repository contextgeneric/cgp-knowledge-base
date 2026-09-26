# `arena_simplified`

Borrowed `&'a Coord` values deserialized from JSON into an arena that the context holds, with the
arena getter and the allocating deserializer defined in the test itself. This is the form the
announcement post shows, and the post's "Full Example" link leads to the `main` branch's version of
the test, which wires the same choices through a `UseDelegate` table.

- **Source** — [crates/cgp-serde-tests/src/tests/arena_simplified.rs](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-tests/src/tests/arena_simplified.rs)
- **Run** — `cargo test -p cgp-serde-tests arena_simplified`
- **Needs** — nothing beyond the build
- **Result** — passes; asserts that the deserialized `Cluster` has id 8 and the two expected
  coordinates

## A deserializer that takes the arena from its context

The test defines its own getter and deserializer. The getter is a
[`#[cgp_auto_getter]`](../../../cgp/reference/macros/cgp_auto_getter.md) trait, which reads the field
named `arena` by blanket impl, and the deserializer imports it with `#[uses]`:

```rust
#[cgp_auto_getter]
pub trait HasArena<'a, T: 'a> {
    fn arena(&self) -> &&'a Arena<T>;
}

#[cgp_impl(new DeserializeAndAllocate)]
#[uses(HasArena<'a, Value>, CanDeserializeValue<'de, Value>)]
impl<'de, 'a, Value> ValueDeserializer<'de, &'a Value> {
    fn deserialize<D>(&self, deserializer: D) -> Result<&'a Value, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let value = self.deserialize(deserializer)?;
        let value = self.arena().alloc(value);

        Ok(value)
    }
}
```

The provider deserializes the owned value through the context, then moves it into the arena and returns
the reference. The getter returns `&&'a Arena<T>` because it returns a reference to the field, and the
field is itself a borrowed arena; that outer `'a` is what lets the allocated coordinates outlive the
context; see [context services](../architecture/context-services.md#the-lifetimes).

## The context carries the arena

`App<'a>` is an environmental context that carries data: one field, a borrowed arena the caller creates
first. The data types derive `CgpData`, and `Cluster<'a>` holds its coordinates by reference:

```rust
#[derive(Debug, PartialEq, Eq, CgpData)]
pub struct Cluster<'a> {
    pub id: u64,
    pub coords: Vec<&'a Coord>,
}

#[derive(HasField)]
pub struct App<'a> {
    pub arena: &'a Arena<Coord>,
}
```

The table routes each type the input reaches, with every borrowed key carrying its own lifetime,
independent of the table's `<'s>`:

```rust
delegate_components! {
    <'s> App<'s> {
        open {ValueDeserializerComponent};

        @ValueDeserializerComponent.u64: UseSerde,
        @ValueDeserializerComponent.[Coord, <'a> Cluster<'a>]: DeserializeRecordFields,
        @ValueDeserializerComponent.<'a> &'a Coord: DeserializeAndAllocate,
        @ValueDeserializerComponent.<'a> Vec<&'a Coord>: DeserializeExtend,
        // ... error entries ...
    }
}
```

The `Vec<&'a Coord>` field goes to [`DeserializeExtend`](../reference/collections.md#deserializeextend),
which deserializes each item through the context, so each `&'a Coord` reaches the local
`DeserializeAndAllocate`. The key syntax is covered in
[wiring a context](../guides/wiring-a-context.md#write-keys-for-references-lifetimes-and-arrays).

## Deserializing from a JSON string

The error entries, `UseAnyhowError` and `RaiseAnyhowError`, are there for
[`deserialize_json_string`](../reference/json.md#candeserializejsonstring), which raises `serde_json`
errors into the context. The method calls its provider directly rather than through a `TryComputer`
entry, so the context wires no handler, and the target type is given by annotating the result:

```rust
let arena = Arena::new();
let app = App { arena: &arena };

let deserialized: Cluster<'_> = app.deserialize_json_string(&serialized).unwrap();
```

The method cannot produce a value that borrows from its input string. `Cluster` borrows from the arena
instead, so it is exactly what the method can return.

## What it demonstrates

- A deserializer drawing a runtime service from its context: see
  [context services](../architecture/context-services.md).
- A borrowed value deserialized with a lifetime independent of the input's: see
  [`DeserializeAndAllocate`](../reference/allocation.md#deserializeandallocate), whose library form this
  test's local provider collapses.
- Keys and checks for a context and value types that carry lifetimes: see
  [components](../reference/components.md#candeserializevalue).

Folding the arena into the deserializer is what makes this form short, and it is also its limit: the
allocator is fixed inside the provider rather than chosen by wiring. The [layered form](arena.md)
separates the two with the library's own crates, and the top-level
[modular serialization example](../../../examples/modular-serialization.md) teaches that form.

## Known issues

- **The first check duplicates the second.** The test's `CanUseApp` table checks
  `ValueDeserializerComponent` at `(Life<'a>, Coord)`, which its `CanDeserializeApp` table already
  covers for every `'de`. The table has the same name and shape as the getter check in the
  [layered test](arena.md), which checks `ArenaGetterComponent`, but here the getter is a blanket
  trait with no component to check. See [issues.md](../issues.md#housekeeping).
- **The getter could be an implicit argument.** `HasArena` exists only for the provider to read a field
  of its own context, the case the
  [reading-context-fields guide](../../../cgp/guides/reading-context-fields.md) gives to an
  [`#[implicit]`](../../../cgp/reference/attributes/implicit.md) argument. A probe confirmed that a
  provider taking `#[implicit] arena: &&'a Arena<Value>` in place of the `HasArena` import deserializes
  the same `Cluster`. The library's own `HasArena` is a different case, since it is a wired getter
  whose field a context chooses per type.

## Public material derived from this

The contrast with the layered form on the "Arena-allocating deserialization" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), which should teach the
[layered form](arena.md) and use this one only to show what the layering buys.
