# `Enum!`

`Enum! { Variant(Type), … }` builds the type-level shape of an enum from the body of an enum
declaration: the same type that [`#[derive(HasFields)]`](../derives/derive_has_fields.md) gives that
enum as its `Fields`.

## Purpose

`Enum!` lets code name a variant set's shape in the syntax of an enum. An enum's
[`HasFields`](../traits/has_fields.md) shape is a [`Sum!`](sum.md) of [`Field`](../types/field.md)
entries, one per variant, tagged by the variant name, and written by hand it restates every name
as a [`Symbol!`](symbol.md):
`Sum![Field<Symbol!("Circle"), f64>, Field<Symbol!("Square"), f64>]`. `Enum! { Circle(f64), Square(f64) }`
is the same type, written as the enum body it describes.

The macro is useful wherever an extensible variant's shape is named rather than derived: a bound
such as `T: FromFields<Fields = Enum! { … }>`, an impl over a shape, or a wiring entry. It is also
the form [`cargo-cgp`](../cargo-cgp.md) prints a variant list in, so a shape the tool shows can be
copied back into code. Like [`Struct!`](struct.md), it builds a type, never a value.

Reach for it only where code names a shape. An enum the author owns gets its shape from
`#[derive(HasFields)]` or `#[derive(CgpData)]`, and restating it as an `Enum!` beside it is a second
copy that can drift. A choice among types that are not named variants stays a [`Sum!`](sum.md), and
a closed variant set consumed in one place is clearer as a plain `enum` with a `match`.

## Syntax

The body is the inside of an enum declaration. Each variant takes one of the three Rust variant
shapes:

```rust
Enum! {
    Empty,                                  // a unit variant
    Circle(f64),                            // positional fields
    Rectangle { width: f64, height: f64 },  // named fields
}
```

Inside the body, a variant's delimiter is visible to the macro, so it keeps its Rust meaning:
parentheses hold positional fields and braces hold named fields. The delimiter of the `Enum!`
invocation itself is not significant. A variant name may be a raw identifier, tagged without the
`r#`, and the list accepts a trailing comma.

The parts of an enum body that a shape has no use for are rejected at parse time with a spanned
error:

- **Attributes:** any attribute on a variant, such as `#[default]` or a doc comment.
- **Visibility:** `pub` on a variant.
- **Discriminants:** a `= value` after a variant.
- **Duplicate names:** a variant name given twice.
- **Field problems:** every rule [`Struct!`](struct.md#syntax) applies to its fields, applied to
  each variant's fields.

## Syntax Grammar

The body is a list of variants, each a name with an optional field list:

```ebnf
EnumInput   -> ( Variant ( `,` Variant )* `,`? )?

Variant     -> IDENTIFIER ( `(` TupleFields `)` | `{` NamedFields `}` )?
```

`IDENTIFIER` includes raw identifiers. `TupleFields` and `NamedFields` are the
[`Struct!` productions](struct.md#syntax-grammar), so a variant's fields follow exactly the rules of
a `Struct!` body of the same form.

## Expansion

`Enum!` expands exactly as `#[derive(HasFields)]` expands the same body, because the macro runs the
derive's encoder. Each variant becomes a `Field` entry keyed by its name, and the entries are
chained into a sum ending in `Void`:

```rust
// before
Enum! { Circle(f64), Square(f64) }
```

```rust
// after
Either<Field<Symbol!("Circle"), f64>, Either<Field<Symbol!("Square"), f64>, Void>>
```

A variant's payload is its fields, encoded by the [`Struct!`](struct.md#expansion) rules:

| Variant | Payload |
| --- | --- |
| `Empty`, `Empty()`, or `Empty {}` | `Nil` |
| `Circle(f64)` | `f64`, the bare type |
| `Pair(u32, u32)` | `Struct!(u32, u32)`, an `Index`-keyed product |
| `Rect { width: f64, height: f64 }` | `Struct! { width: f64, height: f64 }`, a `Symbol!`-keyed product |

So several spellings are the same type. `V`, `V()`, `V {}`, and `V(Nil)` are one variant, and
`V { a: u32 }` is `V(Struct! { a: u32 })`. cargo-cgp relies on this when it prints a variant list,
choosing the shortest spelling. An empty body is `Void`, the shape of an enum with no variants.

## Examples

A function bounded on an enum's shape converts a value built in that shape into the enum. Here
`Value` derives the whole variant family, and `from_shape` works for any enum with the same
variants:

```rust
use cgp::prelude::*;

#[derive(Debug, PartialEq, CgpData)]
pub enum Value {
    Int(u64),
    Text(String),
}

pub fn from_shape<T>(fields: Enum! { Int(u64), Text(String) }) -> T
where
    T: FromFields<Fields = Enum! { Int(u64), Text(String) }>,
{
    T::from_fields(fields)
}

assert_eq!(from_shape::<Value>(Either::Left(Field::from(7))), Value::Int(7));
```

A value of the shape selects its variant by nesting `Either::Left` and `Either::Right`, and
`Field::from` wraps the payload, with the variant tag inferred from the `Enum!` type.

## Related constructs

These constructs are the ones `Enum!` relates to:

- [`Struct!`](struct.md): the struct counterpart, whose rules encode each variant's payload.
- [`Sum!`](sum.md): the sum `Enum!` expands to, and the form to write when a variant list has no
  `Enum!` spelling.
- [`Field`](../types/field.md) and [`Symbol!`](symbol.md): the entry and the tag each variant
  becomes.
- [`#[derive(HasFields)]`](../derives/derive_has_fields.md) and [`HasFields`](../traits/has_fields.md):
  the derive whose encoder `Enum!` runs, and the trait whose `Fields` it names.
- [`#[derive(CgpVariant)]`](../derives/derive_cgp_variant.md) and
  [`#[derive(FromVariant)]`](../derives/derive_from_variant.md): the variant derives that build on
  this representation.
- [`cargo-cgp`](../cargo-cgp.md): prints variant lists in this form.

## Known issues

These corner cases concern the shapes `Enum!` can describe and how other tools see them:

- **Every variant shape is accepted, but the variant derives need one positional field.**
  `Enum!` describes any variant, as `#[derive(HasFields)]` does. The derives that construct and
  extract variants, `#[derive(CgpVariant)]`, `#[derive(FromVariant)]`, and `#[derive(ExtractField)]`,
  accept only variants with exactly one positional field, so a shape with unit or multi-field
  variants has no generic constructor or extractor.
- **A variant name must be an identifier.** A sum whose entries are tagged by `Index<N>` or by a
  `Symbol!` that is not an identifier has no `Enum!` spelling, and is written with `Sum!`.
- **Clippy's `type_complexity` lint and the `#[use_type]` gap** apply as they do to
  [`Struct!`](struct.md#known-issues).

## Source

- Entry point: `Enum` in
  [crates/macros/cgp-macro-lib/src/enum_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/enum_type.rs).
- AST type: `EnumType` in
  [crates/macros/cgp-macro-core/src/types/shape/enum_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/shape/enum_type.rs).
- Field validation shared with `Struct!`: `validate_shape_fields` in
  [crates/macros/cgp-macro-core/src/functions/shape/validate_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/shape/validate_fields.rs).
- Encoder shared with the derive: `variants_to_sum_type` in
  [crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/sum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/sum.rs).
- Internal walkthrough (the variant parsing, the validation, and the index of tests):
  [implementation/entrypoints/enum.md](../../implementation/entrypoints/enum.md).
