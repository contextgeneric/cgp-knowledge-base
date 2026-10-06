# Variant providers

The variant providers serialize and deserialize an enum generically, by walking its variants, so an
enum needs no serialization-specific derive and no dependency on `serde` or `cgp-serde`.
`SerializeVariantFields` writes an enum in Serde's externally tagged form, `{"Variant": payload}`,
and `DeserializeVariantFields` reads it back. They are separate structs, like the
[record providers](records.md), because they walk the enum through different CGP traits.
[`SerializeUnit`](#serializeunit), the provider for the payload of a variant with no fields, is
documented here too.

Both rest on CGP's [extensible variants](../../../cgp/concepts/extensible-variants.md). An enum's
variant list comes from [`HasFields`](../../../cgp/reference/traits/has_fields.md), as a sum of
`Field<Tag, Payload>` entries, and each variant's name is a type-level string the providers turn
into a `&'static str` through [`StaticString`](../../../cgp/reference/traits/static_format.md). Both
directions need only `#[derive(HasFields)]`, which emits the `FromFields` and `ToFieldsRef` impls
the providers call; [`#[derive(CgpVariant)]`](../../../cgp/reference/derives/derive_cgp_variant.md)
and [`#[derive(CgpData)]`](../../../cgp/reference/derives/derive_cgp_data.md) include it.

**Every variant must hold one unnamed payload or no fields**, the shapes `CgpVariant` accepts. A
payload is any type the context wires: a record, a scalar, a collection, or another enum. A variant
with no fields, written `Closed`, `Closed()`, or `Closed {}`, carries the payload `Nil`, and the
context's wiring for `Nil` decides its format. Wired to `SerializeUnit`, every one of these forms
is written `{"Closed":null}`, which differs from what Serde's derive writes for each of them in JSON
and RON; see [Known issues](#known-issues). A variant may also hold `()`, as `Empty(())`, whose
format the context's wiring for `()` decides in the same way. An enum that derives only `HasFields`
may also have multi-field tuple or struct-style variants, whose payloads are anonymous products;
wiring it to either provider compiles until the enum is used, then reports a missing entry for that
payload type.

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
`CanSerializeValue<Payload>`. A variant with no fields appears in the list as `Field<Tag, Nil>`
rather than as a reference, since the borrowed view of an empty product has nothing to borrow, so a
second `Either` case serializes it through the context as `&Nil` and requires
`CanSerializeValue<Nil>`. The `Void` case is uninhabited, so the match over the variants is
exhaustive by its type.

### Behavior

The provider borrows the enum's variant list with `to_fields_ref`, finds the active variant, and
calls `serialize_newtype_variant` with the variant's name, its declaration position as the index,
and the payload wrapped in
[`SerializeWithContext`](../architecture/reentrant-providers.md#adapter-calls). With JSON,
`Shape::Circle(Circle { radius: 3 })` serializes to `{"Circle":{"radius":3}}` and
`Shape::Label("hi".into())` to `{"Label":"hi"}`. This is exactly what Serde's derive writes for the
same enum, in JSON and, for payloads that are not records, in RON and postcard. RON writes the
variant around its payload, `Label("x")`, and postcard writes the index followed by the payload,
`[1, 5]` for the second variant holding `5`.

A variant with no fields is written the same way, as a newtype variant holding the context's
encoding of `Nil`. With `Nil` wired to [`SerializeUnit`](#serializeunit), `Status::Closed` is
`{"Closed":null}` in JSON and `Closed(())` in RON, and `Status::Archived {}`, the fourth variant, is
`[3]` in postcard, the index with nothing after it. Serde's derive writes each empty form its own
way, and only postcard agrees:

| Variant | Serde's derive, JSON | Serde's derive, RON | Both, postcard |
|---|---|---|---|
| `Closed` | `"Closed"` | `Closed` | `[1]` |
| `Paused()` | `{"Paused":[]}` | `Paused()` | `[2]` |
| `Archived {}` | `{"Archived":{}}` | `Archived()` | `[3]` |

The enum name the format receives is the last segment of `core::any::type_name` without its generic
arguments, such as `Token` for `Token<'a>`, because `HasFields` carries no type name and RON rejects
a name that is not an identifier. The name never decides which variant is written. Both providers
pass the same name.

### Context dependencies

The context must implement `CanSerializeValue<P>` for the payload type `P` of every variant, which
is `Nil` for a variant with no fields.

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
- **A recursive enum fails to compile with `E0275`**, as a recursive record does; see [re-entrant
  providers](../architecture/reentrant-providers.md#what-re-entry-requires-of-a-context).
- **A variant with no fields does not match Serde's derive in JSON or RON**, as the table under
  Behavior shows. `serde_json` still reads the provider's `{"Closed":null}` into a unit variant
  `Closed` of a Serde-derived mirror, but not `{"Paused":null}` into `Paused()` or
  `{"Archived":null}` into `Archived {}`. postcard writes the same bytes on both sides.

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

The provider calls `deserialize_enum` and reads the variant identifier first. A text format gives
the identifier as a name, which is compared against each variant name in declaration order without
being copied; a binary format gives the declaration index. The provider then reads the payload with
`newtype_variant_seed` and a
[`DeserializeWithContext`](../architecture/reentrant-providers.md#adapter-calls) seed, places it in
the matching arm of the variant list, and builds the enum with `from_fields`. The `'de` lifetime
reaches the payload, so `Token<'a>` reads `{"Word":"hello"}` with `"hello"` borrowed from the input.
Escaped variant names and input read through an `io::Read` both work, and so does a name the format
hands over as bytes.

`deserialize_enum` also takes the list of variant names, as a `&'static [&'static str]`, which
cannot be built from the type-level variant list on stable Rust. The provider passes an empty list.
`serde_json`, RON, and postcard ignore it, and the provider's own unknown-variant error lists the
names instead, but a format that reads the list would see none.

The provider rejects input in these cases, each reported through the format's own error:

- **An unknown variant**:
  ``unknown variant `Square`, expected one of `Circle`, `Rectangle`, `Label`, `Empty` ``, the same
  wording Serde's derive uses.
- **An index out of range**, from a binary format:
  `variant index 9 out of range, expected one of …`. postcard reports any custom error as
  `SerdeDeCustom`, so the message is lost there.
- **A bare variant name**, such as `"Closed"`, the form Serde's derive writes for a unit variant:
  `invalid type: unit variant, expected newtype variant`, whatever the context wires for the
  payload. Serde's forms for the other empty variants, `{"Paused":[]}` and `{"Archived":{}}`, fail
  in the payload's provider; with `SerializeUnit`, as
  `invalid type: sequence, expected unit at line 1 column 10` and
  `invalid type: map, expected unit at line 1 column 12`.
- **A payload of the wrong type**: the payload provider's error; with JSON, `{"Label":5}` gives
  ``invalid type: integer `5`, expected a string``.
- **Anything that is not one variant**: `serde_json` reports an empty object, a second variant, an
  array, a number, or `null` as `expected value`.

### Context dependencies

The context must implement `CanDeserializeValue<'de, P>` for the payload type `P` of every variant,
which is `Nil` for a variant with no fields.

### Pairing

The serializing counterpart is [`SerializeVariantFields`](#serializevariantfields).

### Known issues

- **The variant list given to the format is empty**, as described under Behavior; a format that
  relies on it is untested.
- **Only Serde's externally tagged representation is supported.** There is no internally tagged,
  adjacently tagged, or untagged form, and none of the JSON or RON forms Serde's derive writes for
  a variant with no fields is accepted; such a variant is read only as a newtype variant holding the
  context's encoding of `Nil`. In postcard the two agree.
- **A recursive enum fails to compile with `E0275`**, as for serializing.

## `SerializeUnit`

`SerializeUnit` writes any value as Serde's unit and reads a unit back as the type's `Default`. It
is the provider for `Nil`, the payload the CGP variant derives give a variant with no fields.

### Definition

```rust
pub struct SerializeUnit;

#[cgp_impl(SerializeUnit)]
impl<Value> ValueSerializer<Value> { ... }

#[cgp_impl(SerializeUnit)]
impl<'de, Value> ValueDeserializer<'de, Value>
where
    Value: Default,
{ ... }
```

### Behavior

The serializer ignores the value and calls `serialize_unit`, which JSON writes as `null`, RON as
`()`, and postcard as nothing. The deserializer calls `deserialize_unit` and returns
`Value::default()`. It rejects anything that is not a unit, so `{"Closed":{}}` fails with
`invalid type: map, expected unit at line 1 column 10`. Because the serializer accepts any value,
wiring it for a type that carries data drops that data, so it should be wired only for a type with
nothing to write, such as `Nil`.

### Context dependencies

None. It writes and reads the unit itself.

### Pairing

One struct serves both directions, and the two agree on the unit.

## Wiring the pair

A context wires both providers per enum type with the `open` statement of
[`delegate_components!`](../../../cgp/reference/macros/delegate_components.md), alongside an entry
for every payload type, including `Nil` when a variant has no fields. This context reads and writes
a `Shape` whose payloads are two records, a `String`, and the `Nil` of an empty variant:

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
    Empty,
}

pub struct App;

delegate_components! {
    App {
        open {
            ValueSerializerComponent,
            ValueDeserializerComponent,
        };

        @ValueSerializerComponent.[u64, String]: UseSerde,
        @ValueSerializerComponent.Nil: SerializeUnit,
        @ValueSerializerComponent.[Circle, Rectangle]: SerializeRecordFields,
        @ValueSerializerComponent.Shape: SerializeVariantFields,

        @ValueDeserializerComponent.[u64, String]: UseSerde,
        @ValueDeserializerComponent.Nil: SerializeUnit,
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

With `Nil` wired to `SerializeUnit`, `Shape::Empty` is written `{"Empty":null}`. A variant that
holds `()` instead, as `Empty(())`, is written however the context writes `()`: `UseSerde` writes
the same `{"Empty":null}`, as Serde's derive writes that variant, while a context that wires `()` to
a provider writing an empty map writes `{"Empty":{}}`, and each context rejects the other's form. A
missing payload entry is reported with the payload as its root cause: without the `Nil` entry,
`cargo cgp check` reports
``[CGP-E107] context `App` does not contain any delegate entry for `@ValueDeserializerComponent.Nil` ``,
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
- [`crates/cgp-serde/src/providers/unit.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/unit.rs):
  `SerializeUnit`.

## Public material derived from this

The three provider pages in the `reference/providers/` pages of the
[cgp-serde project section](../../../website/projects/cgp-serde.md), and the rustdoc for
`SerializeVariantFields`, `DeserializeVariantFields`, and `SerializeUnit`.
