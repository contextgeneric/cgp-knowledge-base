# Variant providers

The variant providers serialize and deserialize an enum generically, by walking its variants, so an
enum needs no serialization-specific derive and no dependency on `serde` or `cgp-serde`.
`SerializeVariantFields` writes an enum in Serde's externally tagged form, `{"Variant": payload}`,
and `DeserializeVariantFields` reads it back. They are separate structs, like the
[record providers](records.md), because they walk the enum through different CGP traits.

Both rest on CGP's [extensible variants](../../../cgp/concepts/extensible-variants.md). An enum's
variant list comes from [`HasFields`](../../../cgp/reference/traits/has_fields.md), as a sum of
`Field<Tag, Payload>` entries, and each variant's name is a type-level string the providers turn into
a `&'static str` through [`StaticString`](../../../cgp/reference/traits/static_format.md). Both
directions need only `#[derive(HasFields)]`, which emits the `FromFields` and `ToFieldsRef` impls the
providers call;
[`#[derive(CgpVariant)]`](../../../cgp/reference/derives/derive_cgp_variant.md) and
[`#[derive(CgpData)]`](../../../cgp/reference/derives/derive_cgp_data.md) include it.

**Every variant must hold exactly one unnamed payload**, the shape `CgpVariant` requires. A payload
is any type the context wires: a record, a scalar, a collection, or another enum. A unit-like
variant is written with a `()` payload, as `Empty(())`, and the context's wiring for `()` decides
its format. An enum that derives only `HasFields` may have unit, tuple, or struct-style variants,
whose payloads are `Nil` or an anonymous product; wiring it to either provider compiles until the
enum is used, then reports a missing entry for that payload type.

## `SerializeVariantFields`

`SerializeVariantFields` serializes an enum as a newtype variant, with the variant's payload
serialized through the context.

### Definition

```rust
pub struct SerializeVariantFields;

#[cgp_impl(SerializeVariantFields)]
impl<Value> ValueSerializer<Value>
where
    Value: ToFieldsRef,
    for<'a> Value::FieldsRef<'a>: VariantsSerializer<Self>,
{ ... }
```

`VariantsSerializer` is a private trait implemented for the borrowed variant list. Its `Either` case
requires, for each `Field<Tag, &Payload>`, that `Tag: StaticString` and that the context implements
`CanSerializeValue<Payload>`; its `Void` case is uninhabited, so the match over the variants is
exhaustive by its type.

### Behavior

The provider borrows the enum's variant list with `to_fields_ref`, finds the active variant, and calls
`serialize_newtype_variant` with the variant's name, its declaration position as the index, and the
payload wrapped in [`SerializeWithContext`](../architecture/reentrant-providers.md#adapter-calls).
With JSON, `Shape::Circle(Circle { radius: 3 })` serializes to `{"Circle":{"radius":3}}` and
`Shape::Label("hi".into())` to `{"Label":"hi"}`. This is exactly what Serde's derive writes for the
same enum, in JSON and, for payloads that are not records, in RON and postcard. RON writes the variant
around its payload, `Label("x")`, and postcard writes the index followed by the payload, `[1, 5]` for
the second variant holding `5`.

The enum name the format receives is the last segment of `core::any::type_name` without its generic
arguments, such as `Token` for `Token<'a>`, because `HasFields` carries no type name and RON rejects
a name that is not an identifier. The name never decides which variant is written.

### Context dependencies

The context must implement `CanSerializeValue<P>` for the payload type `P` of every variant.

### Pairing

The deserializing counterpart is [`DeserializeVariantFields`](#deserializevariantfields). The two
agree on the format: an externally tagged newtype variant.

### Known issues

- **Only `'static` enums are accepted.** The provider's bound on `FieldsRef<'a>` must hold for every
  lifetime, and `FieldsRef<'a>` requires `Value: 'a`, which Rust can only prove for every `'a` when
  `Value` is `'static`. An enum such as `Token<'a> { Word(&'a str), Number(u64) }` wired to the
  provider fails with `E0477`, "the type `Token<'a>` does not fulfill the required lifetime", and a
  call with a non-`'static` value fails with `E0597`. `Token<'static>` works. The fix needs a
  borrowing per-variant accessor in `cgp` whose associated type carries no lifetime, the way
  `HasField` does for records; see [issues.md](../issues.md#defects).
- **A record payload is rejected by postcard**, because records are written without a length; see
  [records](records.md#known-issues).
- **A recursive enum fails to compile with `E0275`**, as a recursive record does; see
  [re-entrant providers](../architecture/reentrant-providers.md#what-re-entry-requires-of-a-context).

## `DeserializeVariantFields`

`DeserializeVariantFields` deserializes an enum from an externally tagged newtype variant,
deserializing the payload through the context and building the enum with `FromFields`.

### Definition

```rust
pub struct DeserializeVariantFields;

#[cgp_impl(DeserializeVariantFields)]
impl<'de, Value> ValueDeserializer<'de, Value>
where
    Value: FromFields,
    Value::Fields: VariantsDeserializer<'de, Self>,
{ ... }
```

`VariantsDeserializer` is private. Its `Either` case requires, for each `Field<Tag, Payload>`, that
`Tag: StaticString` and that the context implements `CanDeserializeValue<'de, Payload>`.

### Behavior

The provider calls `deserialize_enum` and reads the variant identifier first. A text format gives the
identifier as a name, which is compared against each variant name in declaration order without being
copied; a binary format gives the declaration index. The provider then reads the payload with
`newtype_variant_seed` and a [`DeserializeWithContext`](../architecture/reentrant-providers.md#adapter-calls)
seed, places it in the matching arm of the variant list, and builds the enum with `from_fields`. The
`'de` lifetime reaches the payload, so `Token<'a>` reads `{"Word":"hello"}` with `"hello"` borrowed
from the input. Escaped variant names and input read through an `io::Read` both work.

The provider rejects input in these cases, each reported through the format's own error:

- **An unknown variant**: ``unknown variant `Square`, expected one of `Circle`, `Rectangle`, `Label`, `Empty` ``,
  the same wording Serde's derive uses.
- **An index out of range**, from a binary format: `variant index 9 out of range, expected one of …`.
  postcard reports any custom error as `SerdeDeCustom`, so the message is lost there.
- **A bare variant name**, such as `"Empty"`: `invalid type: unit variant, expected newtype variant`,
  whatever the context wires for `()`.
- **A payload of the wrong type**: the payload provider's error; with JSON, `{"Label":5}` gives
  ``invalid type: integer `5`, expected a string``.
- **Anything that is not one variant**: `serde_json` reports an empty object, a second variant, an
  array, a number, or `null` as `expected value`.

### Context dependencies

The context must implement `CanDeserializeValue<'de, P>` for the payload type `P` of every variant.

### Pairing

The serializing counterpart is [`SerializeVariantFields`](#serializevariantfields).

### Known issues

- **Only Serde's externally tagged representation is supported.** There is no internally tagged,
  adjacently tagged, or untagged form, and the bare-string form Serde's derive uses for a unit
  variant is rejected; a unit-like variant is `Empty(())`, written as the context writes `()`.
- **A recursive enum fails to compile with `E0275`**, as for serializing.

## Wiring the pair

A context wires both providers per enum type with the `open` statement of
[`delegate_components!`](../../../cgp/reference/macros/delegate_components.md), alongside an entry
for every payload type, including `()` when a variant holds one. This context reads and writes a
`Shape` whose payloads are two records, a `String`, and `()`:

```rust
#[derive(CgpData)]
pub struct Circle {
    pub radius: u64,
}

#[derive(CgpData)]
pub struct Rectangle {
    pub width: u64,
    pub height: u64,
}

#[derive(CgpVariant)]
pub enum Shape {
    Circle(Circle),
    Rectangle(Rectangle),
    Label(String),
    Empty(()),
}

pub struct App;

delegate_components! {
    App {
        open {
            ValueSerializerComponent,
            ValueDeserializerComponent,
        };

        @ValueSerializerComponent.[u64, String, ()]: UseSerde,
        @ValueSerializerComponent.[Circle, Rectangle]: SerializeRecordFields,
        @ValueSerializerComponent.Shape: SerializeVariantFields,

        @ValueDeserializerComponent.[u64, String, ()]: UseSerde,
        @ValueDeserializerComponent.[Circle, Rectangle]: DeserializeRecordFields,
        @ValueDeserializerComponent.Shape: DeserializeVariantFields,
    }
}

check_components! {
    #[check_trait(CanSerializeShape)]
    App {
        ValueSerializerComponent: Shape,
    }
}

check_components! {
    #[check_trait(CanDeserializeShape)]
    <'de> App {
        ValueDeserializerComponent: (Life<'de>, Shape),
    }
}
```

With `()` wired to `UseSerde`, `Shape::Empty(())` is written `{"Empty":null}`, as Serde's derive
writes it. A context that wires `()` to a provider writing an empty map writes `{"Empty":{}}`
instead, and each context rejects the other's form. A missing payload entry is reported with the
payload as its root cause: without the `()` entry, `cargo cgp check` reports
``[CGP-E107] context `App` does not contain any delegate entry for `@ValueDeserializerComponent.()` ``,
with a dependency chain through each variant of `Enum! { … }`.

## Related documents

- [Records](records.md) documents the record providers that usually serialize a variant's payload.
- [Re-entrant providers](../architecture/reentrant-providers.md) explains the adapter both providers
  use to hand the payload back to the context.
- [Extensible variants](../../../cgp/concepts/extensible-variants.md) explains the sum-of-variants
  shape the providers walk.

## Source

- [`crates/cgp-serde/src/providers/variant_fields.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/variant_fields.rs):
  `SerializeVariantFields` and `VariantsSerializer`.
- [`crates/cgp-serde/src/providers/variant.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/variant.rs):
  `DeserializeVariantFields`, its visitor and identifier seed, `VariantsDeserializer`, and the enum
  name helper.

## Public material derived from this

The two provider pages in the `reference/providers/` pages of the
[cgp-serde project section](../../../website/projects/cgp-serde.md), and the rustdoc for
`SerializeVariantFields` and `DeserializeVariantFields`.
