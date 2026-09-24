# Record providers

The record providers serialize and deserialize a struct generically, by walking its fields, so a struct
needs no serialization-specific derive and no dependency on `serde` or `cgp-serde`. `SerializeFields`
writes a struct as a map and `DeserializeRecordFields` reads one back. They are separate structs rather
than one provider serving both directions, because they walk the struct through different CGP traits.

Both rest on CGP's [extensible records](../../../cgp/concepts/extensible-records.md). A struct's field
list comes from [`HasFields`](../../../cgp/reference/traits/has_fields.md), and each field's name is a
type-level string that the providers turn into a `&'static str` through
[`StaticString`](../../../cgp/reference/traits/static_format.md). The derives each direction needs are:

- **Serializing** — `HasFields` and `HasField`, so the provider can list the fields and read each one.
- **Deserializing** — `HasFields` and `BuildField`, so the provider can list the fields and fill them
  in through the optional builder.
- **Both** — [`#[derive(CgpData)]`](../../../cgp/reference/derives/derive_cgp_data.md), which derives
  all three.

Only structs with named fields work. A tuple struct keys its fields by `Index<N>`, which does not
implement `StaticString`, so wiring one to either provider fails to compile. No provider in the library
handles an enum generically; an enum is encoded only through `UseSerde`, from its own Serde impl.

## `SerializeFields`

`SerializeFields` serializes a struct as a map from each field's name to its value, serializing every
value through the context.

### Definition

```rust
#[cgp_impl(new SerializeFields)]
impl<Value> ValueSerializer<Value>
where
    Value: HasFields,
    Value::Fields: FieldsSerializer<Self, Value>,
{ ... }
```

`FieldsSerializer` is a private trait implemented for CGP's type-level field list. Its `Cons` case
requires, for each `Field<Tag, FieldValue>` in the list, that `Tag: StaticString`, that
`Value: HasField<Tag, Value = FieldValue>`, and that the context implements
`CanSerializeValue<FieldValue>`; its `Nil` case ends the map.

### Behavior

The provider opens a map without declaring its length and writes one entry per field, in declaration
order. Each key is the Rust field name exactly as written, and each value is the field's value wrapped
in [`SerializeWithContext`](../architecture/reentrant-providers.md#adapter-calls), so the context
chooses its encoding. With JSON, a struct `Rec { a: 1, b: "x".into() }` whose field types are wired to
`UseSerde` serializes to `{"a":1,"b":"x"}`. The provider writes a map through `serialize_map` rather
than a struct through `serialize_struct`, which is what a derived `Serialize` impl calls, and every
field is written under its Rust name.

### Context dependencies

The context must implement `CanSerializeValue<F>` for the type `F` of every field, which in practice
means an entry in its serialization table for each field type the struct uses.

### Pairing

The deserializing counterpart is [`DeserializeRecordFields`](#deserializerecordfields). The two agree
on the format: a map keyed by Rust field names.

### Known issues

- **Length-prefixed formats reject the output.** The map is started without a length, so postcard fails
  with `SerializeSeqLengthUnknown` on every struct.
- **Formats with struct syntax see a map.** RON writes `{"a":1,"b":"x"}` rather than `(a:1,b:"x")`.
- **Serde's field attributes have no equivalent.** No field can be renamed, skipped, or flattened.

## `DeserializeRecordFields`

`DeserializeRecordFields` deserializes a struct from a map, deserializing each field's value through the
context and collecting the fields in CGP's optional builder until every one is present.

### Definition

```rust
pub struct DeserializeRecordFields;

#[cgp_impl(DeserializeRecordFields)]
impl<'de, Record, Builder> ValueDeserializer<'de, Record>
where
    Record: HasOptionalBuilder<Builder = Builder> + HasFields,
    Record::Fields: HandleMapEntry<'de, Self, Builder>,
    Builder: FinalizeOptional<Target = Record>,
{ ... }
```

`HasOptionalBuilder` and `FinalizeOptional` come from `cgp::extra::field::impls`, and `HasOptionalBuilder`
is implemented for every type that has a builder, which `#[derive(BuildField)]` provides. The optional
builder holds each field as an `Option`, so its type stays the same as fields arrive in whatever order
the input gives them. `HandleMapEntry` and `MapVisitor` are private. `HandleMapEntry`'s `Cons` case
requires, for each field, that `Tag: StaticString`, that the context implements
`CanDeserializeValue<'de, FieldValue>`, and that the builder can set that field.

### Behavior

The provider asks the deserializer for a map and reads it entry by entry. For each key it compares the
key against each field name in declaration order. On a match it deserializes the value through
[`DeserializeWithContext`](../architecture/reentrant-providers.md#adapter-calls) and stores it in the
builder; if no field matches, it skips the value. When the map ends it finalizes the builder, which
succeeds only if every field was set. The input's key order does not matter.

The provider rejects input in these cases, each with a Serde custom error:

- **A field is missing** — `missing field: b`, raised after the whole map is read.
- **A field appears twice** — `duplicate field: a`, raised at the second occurrence.
- **The input is not a map** — the deserializer's own type error; with JSON, an array gives
  `invalid type: sequence, expected map`.

An unknown key is accepted silently, and its value is skipped without being deserialized. Every key
is read as an owned `String` and compared against each field name in turn.

### Context dependencies

The context must implement `CanDeserializeValue<'de, F>` for the type `F` of every field. A struct
with a lifetime works the same way: `Cluster<'a>`, with a `coords: Vec<&'a Coord>` field, needs an
entry for `Vec<&'a Coord>`, and the arena example wires the `&'a Coord` items it contains to
`DeserializeAndAllocate`.

### Pairing

The serializing counterpart is [`SerializeFields`](#serializefields).

### Known issues

- **A missing field is always an error.** CGP's optional builder can also finalize by defaulting unset
  fields, through `CanFinalizeWithDefault` in
  [optional fields](../../../cgp/reference/traits/optional_fields.md), but the provider finalizes with
  `FinalizeOptional` and offers no way to choose the other. cgp-serde's own `DeserializeDefault` does
  not help, because it substitutes the default for a `null` value rather than for an absent field.
- **Unknown keys cannot be rejected.** There is no equivalent of Serde's `deny_unknown_fields`.
- **The sequence form of a struct is rejected.** Serde's derive also accepts a struct written as a
  sequence of its field values in declaration order.
- **Every key is allocated.** Serde's derive matches keys against literals without allocating; the
  cost of the difference has not been measured.

## Wiring the pair

A context wires both providers per struct type with the `open` statement of
[`delegate_components!`](../../../cgp/reference/macros/delegate_components.md), alongside an entry for
every field type. This context round-trips a `Payload` through JSON, encoding its `Vec<u8>` field as
hex:

```rust
#[derive(CgpData)]
pub struct Payload {
    pub quantity: u64,
    pub message: String,
    pub data: Vec<u8>,
}

pub struct App;

delegate_components! {
    App {
        open {
            ValueSerializerComponent,
            ValueDeserializerComponent,
        };

        @ValueSerializerComponent.u64: UseSerde,
        @ValueSerializerComponent.String: SerializeString,
        @ValueSerializerComponent.Vec<u8>: SerializeHex,
        @ValueSerializerComponent.Payload: SerializeFields,

        @ValueDeserializerComponent.[u64, String]: UseSerde,
        @ValueDeserializerComponent.Vec<u8>: SerializeHex,
        @ValueDeserializerComponent.Payload: DeserializeRecordFields,
    }
}

check_components! {
    #[check_trait(CanSerializePayload)]
    App {
        ValueSerializerComponent: [u64, String, Vec<u8>, Payload],
    }
}

check_components! {
    #[check_trait(CanDeserializePayload)]
    <'de> App {
        ValueDeserializerComponent: [
            (Life<'de>, u64),
            (Life<'de>, String),
            (Life<'de>, Vec<u8>),
            (Life<'de>, Payload),
        ],
    }
}
```

The deserialization check lists each value type with a [`Life<'de>`](../../../cgp/reference/types/life.md)
in front, because the component's `'de` lifetime is one of its parameters and CGP lifts it into a type
for the check.

`Payload { quantity: 42, message: "hello".into(), data: vec![1, 2, 3] }` serializes to
`{"quantity":42,"message":"hello","data":"010203"}` and deserializes back to the same value. The
providers come from `cgp_serde::providers`, except `SerializeHex`, which comes from
`cgp_serde_extra::providers`.

## Related documents

- [Reflection](../../../related-work/reflection.md) compares `SerializeFields` with Serde's derive, facet,
  and Rust's reflection proposal, including the observation that the field-list recursion still
  monomorphizes per struct, so it saves authoring duplication rather than binary size.
- [Re-entrant providers](../architecture/reentrant-providers.md) explains the adapter both providers
  use to hand each field back to the context.

## Source

- [`crates/cgp-serde/src/providers/fields.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/fields.rs) — `SerializeFields` and `FieldsSerializer`.
- [`crates/cgp-serde/src/providers/record.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/record.rs) — `DeserializeRecordFields`, `MapVisitor`, and `HandleMapEntry`.

## Public material derived from this

The "Writing serializers" page of the planned [cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md),
and the rustdoc for `SerializeFields` and `DeserializeRecordFields`.
