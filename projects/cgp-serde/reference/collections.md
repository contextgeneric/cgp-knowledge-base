# Collection providers

The collection providers encode a collection as a Serde sequence, handing each item back to the context
so the items follow the context's wiring. `SerializeIterator` writes anything iterable by reference, and
`DeserializeExtend` reads a sequence into any collection that can be extended item by item. Both are
[adapter re-entries](../architecture/reentrant-providers.md#adapter-calls): they pass each item to a
Serde compound API wrapped together with the context.

## `SerializeIterator`

`SerializeIterator` serializes any collection that can be iterated by reference as a sequence of its
items.

### Definition

```rust
#[cgp_impl(new SerializeIterator)]
impl<Value> ValueSerializer<Value>
where
    for<'a> &'a Value: IntoIterator,
    Self: for<'a> CanSerializeValue<<&'a Value as IntoIterator>::Item>,
{ ... }
```

Both bounds are higher-ranked because the item type depends on the lifetime of the borrow, which is
also why the item dependency is written in the `where` clause rather than with
[`#[uses]`](../../../cgp/reference/attributes/uses.md).

### Behavior

The provider opens a sequence without declaring its length, then serializes each item the collection
yields when iterated by reference, through
[`SerializeWithContext`](context-adapters.md#serializewithcontext). With JSON, a `Vec<u64>` or a
`BTreeSet<u64>` becomes an array, and a `Vec<Vec<u64>>` whose inner vectors are also wired to
`SerializeIterator` becomes a nested array. A fixed-size array works too, wired through a type alias
because square brackets cannot be written as a key segment.

The item type is whatever iterating `&Value` yields, which is usually a reference. `Vec<T>`, slices,
and sets yield `&T`, so the context needs an entry for `&T`, conventionally the generic
`<'a, T> &'a T: SerializeDeref` that forwards every reference to the context's wiring for `T`; see
[re-entrant providers](../architecture/reentrant-providers.md#what-re-entry-requires-of-a-context).
A map yields a tuple of references, so a `BTreeMap<String, u64>` asks the context to serialize
`(&String, &u64)`. The library has no provider for tuples, so the tuple has to be wired to `UseSerde`,
and the map is written as a sequence of pairs, `[["a",1]]`, whose keys and values bypass the context.

### Context dependencies

`CanSerializeValue<I>` for each item type `I` the collection yields by reference, for every lifetime.

### Pairing

The deserializing counterpart is [`DeserializeExtend`](#deserializeextend).

### Known issues

- **Length-prefixed formats reject the output.** The sequence is started without a length, so postcard
  fails with `SerializeSeqLengthUnknown`, even for collections whose length is known.
- **Maps are written as sequences of pairs.** No provider serializes a map as a Serde map, and the
  pairs need a tuple provider the library does not have.
- **Recursive collections fail to compile.** A type that contains a collection of itself makes the
  item dependency cycle back to the type, which the trait solver reports as `E0275`.

## `DeserializeExtend`

`DeserializeExtend` deserializes a sequence into any collection that has a default value and can be
extended with items, deserializing each item through the context.

### Definition

```rust
pub struct DeserializeExtend;

#[cgp_impl(DeserializeExtend)]
#[uses(CanDeserializeValue<'de, Item>)]
impl<'de, Value, Item> ValueDeserializer<'de, Value>
where
    Value: Default + IntoIterator<Item = Item> + Extend<Item>,
{ ... }
```

`DeserializeExtendVisitor` and the seed it uses for each item, `DeserializeExtendSeed`, are private.
The seed has the same shape as [`DeserializeWithContext`](context-adapters.md#deserializewithcontext).
The `IntoIterator` bound only names the collection's item type; the provider never iterates.

### Behavior

The provider asks the deserializer for a sequence, starts from `Value::default()`, and extends the
collection with each item as it is deserialized, one at a time. Any collection meeting the bounds
works: a `Vec<u64>`, and also a `BTreeSet<u64>`, where `[3,1,3]` deserializes to `{1, 3}` because the
set's own `Extend` discards the duplicate. Input that is not a sequence fails with the deserializer's
type error; with JSON, an object gives `invalid type: map, expected sequence`.

The items are deserialized through the context, so a `Vec<&'a Coord>` whose `&'a Coord` items are wired
to [`DeserializeAndAllocate`](allocation.md) fills itself with references into an arena.

### Context dependencies

`CanDeserializeValue<'de, Item>` for the collection's item type.

### Pairing

The serializing counterpart is [`SerializeIterator`](#serializeiterator).

### Known issues

- **Maps are read as sequences of pairs.** A map's `IntoIterator` item is a key-value tuple, so a
  `BTreeMap<String, u64>` reads `[["a",1]]` once the tuple `(String, u64)` is wired to `UseSerde`, and
  rejects the JSON object `{"a":1}` with `invalid type: map, expected sequence`. This matches what
  `SerializeIterator` writes, but not the map form a Serde-derived type uses.

## Source

- [`crates/cgp-serde/src/providers/iterator.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/iterator.rs) — `SerializeIterator`.
- [`crates/cgp-serde/src/providers/extend.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/extend.rs) — `DeserializeExtend`, its visitor, and its seed.

## Public material derived from this

The "Writing serializers" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the rustdoc for both providers.
