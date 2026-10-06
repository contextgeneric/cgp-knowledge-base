# `Sum!`

`Sum![A, B, C]` builds a type-level sum type, a coproduct whose value is exactly one of the listed
types, which CGP uses to represent an enum's variants the way [`Product!`](product.md) represents a
struct's fields.

## Purpose

`Sum!` represents a choice among several types as a single type, so an enum's variants can be
handled generically. A [`Product!`](product.md) list holds a value for every element at once, like a
record; a `Sum!` holds a value for exactly one element, like a tagged union. It is sometimes called
an anonymous sum type or coproduct, and it mirrors the product: both are right-nested chains, but
the sum branches at each step where the product pairs.

That structure is what makes variant-by-variant operations possible. An enum's variants are exposed
as one sum type through [`HasFields`](../traits/has_fields.md), so a provider can match, dispatch
on, or construct any enum's variants without knowing the enum, by recursing over the branches. This
is the basis of CGP's [extensible variants](../../concepts/extensible-variants.md), where each
variant is handled by walking the chain rather than by a `match` against a fixed enum.

`Sum!` and `Product!` are used together. A struct's fields become a `Product!`, and an enum's
variants become a `Sum!` of the same kind of `Field<Tag, Value>` entries, so knowing one shape tells
you the other.

## Syntax

The macro takes a comma-separated list of types, which may be empty, and is used wherever a type is
expected:

```rust
Sum![u32, String, bool]
Sum![]   // the empty sum
```

Each listed type is one possible alternative, and a value of the sum carries exactly one of them.

## Syntax Grammar

The input is a possibly empty, comma-separated list of types:

```ebnf
SumInput -> ( Type ( `,` Type )* `,`? )?
```

`Type` is the Rust grammar's type production, and the list may be empty or end with a trailing
comma.

## Expansion

`Sum!` expands to a right-nested chain of `Either` ending in `Void`:

```rust
// before
Sum![A, B, C]
```

```rust
// after
Either<A, Either<B, Either<C, Void>>>
```

Both building blocks come from `cgp-field`, and they branch rather than pair.
[`Either<Head, Tail>`](../types/either.md) is an enum with two cases: `Left(Head)` selects the head
type, and `Right(Tail)` defers to the rest of the chain. So a value of
`Either<A, Either<B, Either<C, Void>>>` is `Left(..)` for an `A`, `Right(Left(..))` for a `B`, and
`Right(Right(Left(..)))` for a `C`. The chain ends in `Void`, an empty enum with no values, because
reaching that position would mean the value matched none of the alternatives. The macro folds the
types from right to left onto `Void`, so an empty `Sum![]` is `Void` itself, a type with no values.

Ending in `Void` rather than `Nil` is the essential difference from [`Product!`](product.md). An
empty record is a valid value, the unit struct `Nil`, but an empty choice is uninhabited, since
there is nothing to choose. `Void` plays the role of the never type here, marking the end of a sum.

The uninhabited `Void` is what gives generic variant handling compile-time exhaustiveness without a
wildcard arm. As an extractor rules each variant out it marks that variant `IsVoid`, whose payload
type is `Void`, so code that has handled every variant is left holding an extractor whose every
variant holds a `Void`. That value cannot exist, and it is discharged with an empty `match`, which
[`FinalizeExtract`](../traits/extract_field.md) wraps. Adding a variant without handling it leaves
that variant's payload inhabited, so the code stops compiling. A `match` on a `Sum!` value directly
closes the same way, with an empty match on its final `Void` arm.

## Examples

`Sum!` most often appears as the `Fields` of an enum that derives
[`HasFields`](../derives/derive_has_fields.md), where each branch is a
[`Field<Tag, Value>`](../types/field.md) pairing a variant name with its payload:

```rust
use cgp::prelude::*;

#[derive(HasFields)]
pub enum Shape {
    Circle(f64),
    Rectangle { width: f64, height: f64 },
}

// generated, among other impls:
// impl HasFields for Shape {
//     type Fields = Sum![
//         Field<Symbol!("Circle"), f64>,
//         Field<Symbol!("Rectangle"), Product![
//             Field<Symbol!("width"), f64>,
//             Field<Symbol!("height"), f64>,
//         ]>,
//     ];
// }
```

The variant names are [`Symbol!`](symbol.md) strings, and the same list is written
[`Enum! { Circle(f64), Rectangle { width: f64, height: f64 } }`](enum.md). A variant's payload follows its fields: a
single unnamed field is the payload type itself, a struct-like variant nests a
[`Product!`](product.md) of its named fields, several unnamed fields nest a `Product!` keyed by
[`Index`](../types/index.md), and a unit variant's payload is `Nil`. Generic code walks the `Sum!`
to find which variant a value holds, and walks a nested `Product!` to reach that variant's fields.

`Sum!` has no everyday hand-written use: let `#[derive(CgpData)]` or `#[derive(HasFields)]`
generate an enum's list, never write the `Either` chain out, and prefer a plain `enum` and `match`
when the variant set is closed and consumed in one place.

A sum type can also be written directly:

```rust
type Token = Sum![u32, String, bool];
```

## Related constructs

These constructs are the ones `Sum!` relates to:

- [`Product!`](product.md): the record counterpart, pairing with [`Cons`](../types/cons.md) and
  ending in `Nil`.
- [`Enum!`](enum.md): writes a `Sum!` of named variants as an enum body.
- [`Either`](../types/either.md): the sum cell `Sum!` expands to, with its terminator `Void`.
- [`Field`](../types/field.md): the usual branch type, tagged by a [`Symbol!`](symbol.md) variant
  name.
- [`#[derive(HasFields)]`](../derives/derive_has_fields.md): assigns an enum its `Sum!` of variants.
- [`#[derive(CgpVariant)]`](../derives/derive_cgp_variant.md) and
  [`#[derive(FromVariant)]`](../derives/derive_from_variant.md): the extensible-variant derives that
  build on this representation.

## Known issues

These corner cases concern the sum shape and the derives that produce it:

- **The empty sum is uninhabited.** `Sum![]` is `Void`, so a function returning one never returns.
- **A one-element sum is still a wrapper.** `Sum![T]` is `Either<T, Void>`, a distinct type from `T`.
- **Variant order is part of the type**, though the operations that consume a derived list match on
  the name tags, and a cast between two enums works through that name matching.
- **Only `#[derive(HasFields)]` accepts every variant shape.** The variant derives,
  [`#[derive(CgpData)]`](../derives/derive_cgp_data.md), `CgpVariant`, `ExtractField`, and
  `FromVariant`, accept a variant with one unnamed field or with no fields, whose payload is `Nil`.
  They reject a multi-field or struct-like variant with fields with
  `Expected variant to contain exactly one unnamed field, or no fields`, because constructing or
  extracting a variant hands over its payload as one value. A richer payload is wrapped in its own
  struct, as `Rectangle(Rectangle)`.

## Source

- Entry point: `Sum` in
  [crates/macros/cgp-macro-lib/src/sum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/sum.rs),
  forwarding to the `SumType` construct in
  [crates/macros/cgp-macro-core/src/types/sum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/sum.rs),
  whose `eval` right-folds the types with `Either` onto `Void`.
- Runtime types: `Either<Head, Tail>` and `Void`, both in
  [crates/core/cgp-field/src/types/sum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/types/sum.rs).
- The enum `HasFields` derive that emits a `Sum!` of `Field<Symbol!("..."), _>` branches:
  [crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/sum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/sum.rs).
- Internal walkthrough (the parse-and-`eval` pipeline, the right-fold onto `Void`, and the index of
  tests): [implementation/entrypoints/sum.md](../../implementation/entrypoints/sum.md).
