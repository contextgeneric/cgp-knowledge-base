# `Either` and `Void`

`Either<Head, Tail>` and `Void` are the two cells of CGP's sum list, a recursive, right-nested type-level choice that generic code walks to handle any enum's variants one branch at a time.

## Purpose

`Either` and `Void` represent a choice among several types as a single type, so an enum's variants can be handled generically. The product list, [`Cons`/`Nil`](cons.md), holds a value for every element at once; the sum list holds a value for exactly one branch, like a tagged union. Branching at each step and ending with an uninhabited marker gives an *anonymous sum type*, or coproduct, whose structure a provider can walk without knowing the enum it came from.

The sum list makes variant-by-variant operations uniform across every enum. An enum's variants are exposed as one sum type through [`HasFields`](../traits/has_fields.md), so a provider that recurses over `Either` and `Void` can match, dispatch on, or construct any enum's variants. This is the basis of CGP's [extensible variants](../../concepts/extensible-variants.md), where each variant is reached by walking the branches rather than by a `match` against a fixed enum.

`Either` and `Void` are the building blocks, and the [`Sum!`](../macros/sum.md) macro is how a chain of them is written: `Sum![A, B, C]` is sugar for the nested `Either` chain ending in `Void`. The branches are most often [`Field`](field.md) entries pairing a variant name with its payload.

## Definition

`Either` is a two-case enum that selects the head or defers to the rest of the chain, and `Void` is an empty enum with no values:

```rust
#[derive(Eq, PartialEq, Debug, Clone)]
pub enum Either<Head, Tail> {
    Left(Head),
    Right(Tail),
}

#[derive(Eq, PartialEq, Debug, Clone)]
pub enum Void {}
```

`Head` is the current branch's type and `Tail` is the rest of the chain, another `Either` or `Void` at the end. `Left(Head)` carries a value of the head type, and `Right(Tail)` carries a value that belongs further down. `Void` has no variants and therefore no values. Both derive `Eq`, `PartialEq`, `Debug`, and `Clone`, so a sum of values implementing these traits gets them.

## Behavior

A sum of any width is an `Either` chain ending in `Void`, nested to the right. `Sum![A, B, C]` is `Either<A, Either<B, Either<C, Void>>>`, and `Sum![]` is `Void`. A value picks its branch by depth: `Left(a)` is an `A`, `Right(Left(b))` a `B`, and `Right(Right(Left(c)))` a `C`. The `Void` position can never be reached, because `Void` has no values, so the chain is closed at its end.

Generic code consumes the sum by recursing on its two cases, branching where a fold over the product list pairs. A `Left` is handled as the head, and a `Right` defers to an impl on the `Tail`, recursing until a `Left` is found. The base case is `Void`, and this is where the sum differs from the product: a product ends in [`Nil`](cons.md), an empty record that can be constructed, while a sum ends in the uninhabited `Void`, because an empty choice has no value to pick. `Void` plays the role of the never type, marking the end of a sum.

The uninhabitedness of `Void` is essential to the extractor machinery. After an extractor has tried every variant of a sum and matched none, the leftover value has type `Void`, which cannot exist. [`FinalizeExtract`](../traits/extract_field.md) for `Void` turns it into any type with an empty `match self {}`, so a fully handled extraction is total at compile time, with no unreachable branch at runtime. A constructible terminator like `Nil` could not be discharged this way.

## Examples

The sum list appears most visibly as the `Fields` of an enum that derives [`HasFields`](../derives/derive_has_fields.md), where `Sum!` hides the `Either`/`Void` chain:

```rust
use cgp::prelude::*;

#[derive(HasFields)]
pub enum Shape {
    Circle(f64),
    Rectangle { width: f64, height: f64 },
}

// generated:
// impl HasFields for Shape {
//     type Fields = Sum![
//         Field<Symbol!("Circle"), f64>,
//         Field<Symbol!("Rectangle"), Product![
//             Field<Symbol!("width"), f64>,
//             Field<Symbol!("height"), f64>,
//         ]>,
//     ];
//     // i.e. Either<Field<Symbol!("Circle"), f64>,
//     //          Either<Field<Symbol!("Rectangle"), _>, Void>>
// }
```

A sum type can also be written directly, and a value picks one branch by its nesting depth:

```rust
use cgp::prelude::*;

type Token = Sum![u32, String, bool];
// Token == Either<u32, Either<String, Either<bool, Void>>>

let t: Token = Either::Right(Either::Left("hi".to_string())); // the String branch
```

## Related constructs

These constructs are the ones `Either` and `Void` relate to:

- [`Cons`/`Nil`](cons.md) — the product counterpart, pairing at each step and ending in the constructible `Nil`.
- [`Sum!`](../macros/sum.md) — the macro that writes an `Either` chain.
- [`Field`](field.md) — the usual branch, tagged by a [`Symbol!`](../macros/symbol.md) variant name.
- [`#[derive(HasFields)]`](../derives/derive_has_fields.md) and [`HasFields`](../traits/has_fields.md) — assign an enum its sum and expose it.
- [The extractor family](../traits/extract_field.md) — whose `FinalizeExtract` relies on `Void` to close a total variant match.

## Source

- `Either<Head, Tail>` and `Void` are both defined in [crates/core/cgp-field/src/types/sum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/types/sum.rs).
- The `Sum!` macro that folds types onto this list is the `SumType` construct in [crates/macros/cgp-macro-core/src/types/sum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/sum.rs).
- `FinalizeExtract for Void`, which discharges the uninhabited remainder of an extraction, is in [crates/core/cgp-field/src/traits/extract_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/extract_field.rs), and the enum `HasFields` derive that emits a `Sum!` of `Field` branches is in [crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/sum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/sum.rs).

## Public pages derived from this document

The public reference is organized one page per type, so this document feeds two pages: [`Either`](https://contextgeneric.dev/docs/reference/types/either) and [`Void`](https://contextgeneric.dev/docs/reference/types/void), both under `types/`. A change here is propagated to each of them, per the [synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping and the granularity rule behind it are recorded in [website/site-structure.md](../../../website/site-structure.md).
