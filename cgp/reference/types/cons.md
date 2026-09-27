# `Cons` and `Nil`

`Cons<Head, Tail>` and `Nil` are the two cells of CGP's product list, a recursive, right-nested
type-level list that generic code folds over to handle any struct's fields one at a time.

## Purpose

`Cons` and `Nil` represent an ordered sequence of types as a single type, so a collection of fields
can be handled generically. A plain tuple holds several things at once but cannot be taken apart
element by element in generic code; a recursive list can. Pairing a head with the rest of the list,
and ending with an empty marker, gives an *anonymous product type*: a record-shaped value whose
structure a provider can walk without knowing the struct it came from.

The list makes field-by-field operations uniform across every struct. A struct's fields are exposed
as one list type through [`HasFields`](../traits/has_fields.md), so a provider that recurses over
`Cons` and `Nil` can iterate over, transform, read, or rebuild any struct's fields. Each step
handles the `Head` and recurses into the `Tail` until it reaches `Nil`. This recursion over two
cases, a pair or the empty list, is the mechanism behind builders, extractors, and field mappers
alike.

`Cons` and `Nil` are the building blocks, and the [`Product!`](../macros/product.md) macro is how a
list of them is written: `Product![A, B, C]` is sugar for the nested `Cons` chain, and
`product![a, b, c]` builds a matching value. The elements are most often [`Field`](field.md) entries
pairing a name with a value, so a struct's layout is a `Product!` of `Field` cells.

## Definition

`Cons` is a tuple struct holding the first element and the rest of the list, and `Nil` is a unit
struct marking the end:

```rust
#[derive(Eq, PartialEq, Clone, Default, Debug)]
pub struct Cons<Head, Tail>(pub Head, pub Tail);

#[derive(Eq, PartialEq, Clone, Default, Debug)]
pub struct Nil;
```

`Head` is the first element's type and `Tail` is the rest of the list, another `Cons` or `Nil` at
the end. Both positional fields are public, so `Cons(head, tail)` builds a cell and `.0` and `.1`
reach its parts. `Nil` carries no data: as a `Tail` it ends the chain, and on its own it is the
empty list. Both derive `Eq`, `PartialEq`, `Clone`, `Default`, and `Debug`, so a list of values
implementing these traits gets them structurally: equality compares element by element, and
`Default` gives the list of defaults.

## Behavior

A list of any length is a `Cons` chain ending in `Nil`, nested to the right. `Product![A, B, C]` is
`Cons<A, Cons<B, Cons<C, Nil>>>`, and `Product![]` is `Nil`. The matching value is
`Cons(a, Cons(b, Cons(c, Nil)))`, an ordinary owned value; nothing about the list is boxed or
virtual, and the structure is flat data laid out by nesting.

Generic code consumes the list by recursing on its two cases. An impl for `Nil` supplies the base
case, and an impl for `Cons<Head, Tail>` supplies the step, usually requiring `Tail` to implement
the same trait so the recursion ends at `Nil`. This pair of impls is the standard shape of any
operation that folds over a product, and it lets the field machinery handle a struct of any width
without per-field code.

## Examples

The product list appears most visibly as the `Fields` of a struct that derives
[`HasFields`](../derives/derive_has_fields.md), where `Product!` hides the `Cons`/`Nil` chain:

```rust
use cgp::prelude::*;

#[derive(HasFields)]
pub struct Person {
    pub name: String,
    pub age: u8,
}

// generated:
// impl HasFields for Person {
//     type Fields = Product![
//         Field<Symbol!("name"), String>,
//         Field<Symbol!("age"), u8>,
//     ];
//     // i.e. Cons<Field<Symbol!("name"), String>,
//     //          Cons<Field<Symbol!("age"), u8>, Nil>>
// }
```

A list type and a matching value can also be written directly:

```rust
use cgp::prelude::*;

type Row = Product![u32, String, bool];
let row: Row = product![1, "hi".to_string(), true];
// Row == Cons<u32, Cons<String, Cons<bool, Nil>>>
// row == Cons(1, Cons("hi".to_string(), Cons(true, Nil)))
```

## Related constructs

These constructs are the ones `Cons` and `Nil` relate to:

- [`Either`/`Void`](either.md): the sum counterpart, with the same right-nested shape but branching
  at each step and ending in the uninhabited `Void`.
- [`Product!`](../macros/product.md): the macro that writes a `Cons` list.
- [`Field`](field.md): the usual element, tagged by a [`Symbol!`](../macros/symbol.md) name or an
  [`Index`](index.md) position.
- [`#[derive(HasFields)]`](../derives/derive_has_fields.md) and
  [`HasFields`](../traits/has_fields.md): assign a struct its list and expose it.
- [`Chars`](chars.md): the character list inside a `Symbol`, a specialized form of this list.
- [Product operations](../traits/product_ops.md): `AppendProduct`, `ConcatProduct`, and `MapFields`,
  which transform product lists.

## Source

- `Cons<Head, Tail>` is defined in
  [crates/core/cgp-base-types/src/types/cons.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/cons.rs)
  and `Nil` in
  [crates/core/cgp-base-types/src/types/nil.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/nil.rs).
- The `Product!`/`product!` macros that fold elements onto this list are under
  [crates/macros/cgp-macro-core/src/types/product/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/product/),
  and the `HasFields` trait whose `Fields` is such a list is in
  [crates/core/cgp-field/src/traits/has_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_fields.rs).

## Public pages derived from this document

The public reference is organized one page per type, so this document feeds two pages:
[`Cons`](https://contextgeneric.dev/docs/reference/types/cons) and
[`Nil`](https://contextgeneric.dev/docs/reference/types/nil), both under `types/`. A change here is
propagated to each of them, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping and the granularity
rule behind it are recorded in [website/site-structure.md](../../../website/site-structure.md).
