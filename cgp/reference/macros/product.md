# `Product!` and `product!`

`Product![A, B, C]` builds a type-level list, a heterogeneous list of types encoded in the type
system, and the lowercase `product![a, b, c]` builds a value of that type.

## Purpose

`Product!` represents an ordered sequence of types as a single type, so a collection of fields can
be handled generically. CGP uses it to describe the shape of a struct: its fields, in order, as one
type. Such a list is sometimes called an anonymous product type, because like a tuple it holds
several things at once. Unlike a tuple, it is a recursive `Cons`/`Nil` list that generic code can
take apart one element at a time.

That recursion is what makes field-by-field operations possible. A struct's fields are exposed as
one list type through [`HasFields`](../traits/has_fields.md), so a provider can iterate over,
transform, or rebuild any struct's fields without knowing the struct, by recursing over `Cons` and
`Nil`. Generic code cannot take a plain tuple apart this way.

`Product!` and `product!` are the type and value halves of the same idea. `Product!` produces a type
and is used in type position, such as an associated type, a bound, or a `type` alias. `product!`
produces a value of the matching type and is used in expression position. The uppercase and
lowercase names mirror Rust's split between a struct type and a struct literal.

## Syntax

Both macros take a comma-separated list, which may be empty. `Product!` takes types, and `product!`
takes expressions:

```rust
Product![u32, String, bool]                // a type
product![1u32, "hi".to_string(), true]     // a value of that type
Product![]                                 // the empty list type
```

The two lists line up by position, so the value `product!` builds has the type `Product!` builds
over the corresponding element types.

## Syntax Grammar

The two macros take a possibly empty, comma-separated list, of types for `Product!` and of
expressions for `product!`:

```ebnf
ProductInput -> ( Type ( `,` Type )* `,`? )?

ProductExpr  -> ( Expression ( `,` Expression )* `,`? )?
```

`ProductInput` is the grammar of the type macro `Product!`, and `ProductExpr` that of the value
macro `product!`. `Type` and `Expression` are Rust grammar productions, and both lists may be empty
or end with a trailing comma.

## Expansion

`Product!` expands to a right-nested chain of `Cons` ending in `Nil`:

```rust
// before
Product![A, B, C]
```

```rust
// after
Cons<A, Cons<B, Cons<C, Nil>>>
```

Both building blocks come from `cgp-base-types`. [`Cons<Head, Tail>`](../types/cons.md) is the tuple
struct `Cons<Head, Tail>(pub Head, pub Tail)`, holding the first element and the rest of the list;
chaining it through `Tail` and ending with the unit struct `Nil` gives a list of any length. The
macro folds the elements from right to left onto `Nil`, so an empty `Product![]` is `Nil`.

The value macro `product!` expands the same way, using the `Cons` tuple-struct constructor:

```rust
// before
product![a, b, c]
```

```rust
// after
Cons(a, Cons(b, Cons(c, Nil)))
```

Because `Cons` is a real tuple struct and `Nil` a real unit struct, the result is an ordinary owned
value whose type is exactly what `Product!` builds over the elements' types.

## Examples

`Product!` most often appears as the `Fields` of a struct that derives
[`HasFields`](../derives/derive_has_fields.md), where each element is a
[`Field<Tag, Value>`](../types/field.md) pairing a field name with its type:

```rust
use cgp::prelude::*;

#[derive(HasFields)]
pub struct Person {
    pub name: String,
    pub age: u8,
}

// generated, among other impls:
// impl HasFields for Person {
//     type Fields = Product![
//         Field<Symbol!("name"), String>,
//         Field<Symbol!("age"), u8>,
//     ];
// }
```

The field names are [`Symbol!`](symbol.md) type-level strings, so the whole list is a type-level
description of `Person`'s layout that generic code can walk to build, read, or transform a `Person`.
The derive emits the same list again for `HasFieldsRef`, with each value a `&'a` reference, along
with the `ToFields`, `ToFieldsRef`, and `FromFields` conversions.

The one place `Product!` is written by hand in ordinary code is a handler pipeline, where the list
is the program and its steps run left to right:

```rust
delegate_components! {
    MyContext {
        ComputerComponent:
            PipeHandlers<Product![
                Multiply<Symbol!("foo")>,
                Add<Symbol!("bar")>,
                Multiply<Symbol!("baz")>,
            ]>,
    }
}
```

With `Multiply<Tag>` and `Add<Tag>` reading a `u64` field named by `Tag`, `MyContext` computes
`((input * foo) + bar) * baz`. Everywhere else the list is generated: never write the `Cons` chain
out, let `#[derive(HasFields)]` produce a struct's shape, and prefer a tuple or a struct when no
generic code recurses over the list.

A list type and a matching value can also be written directly:

```rust
type Row = Product![u32, String, bool];
let row: Row = product![1, "hi".to_string(), true];
```

## Related constructs

These constructs are the ones `Product!` relates to:

- [`Sum!`](sum.md): the counterpart for enum variants, with the same right-nested shape but
  branching with `Either` and ending in `Void`.
- [`Cons`](../types/cons.md): the list cell `Product!` expands to, with its terminator `Nil`.
- [`Field`](../types/field.md): the usual element type, tagged by a [`Symbol!`](symbol.md) name or
  an [`Index`](../types/index.md) position.
- [`#[derive(HasFields)]`](../derives/derive_has_fields.md): assigns a struct its `Product!` of
  fields; the per-field tags come from [`#[derive(HasField)]`](../derives/derive_has_field.md).
- [`Chars`](../types/chars.md): the character list inside `Symbol!`, a specialized form of this
  `Cons`/`Nil` structure.
- [Product operations](../traits/product_ops.md): `AppendProduct`, `ConcatProduct`, and `MapFields`,
  which transform product lists at the type level.

## Known issues

These corner cases report themselves in ways that do not name the cause:

- **The two macros differ only in case.** `Product!` in expression position fails inside the type
  parser with ``expected one of: `for`, parentheses, `fn`, …``, a list of type tokens, and
  `product!` in type position expands to the constructor call `Cons(u32, …)`, which rustc rejects as
  `E0214`, ``parenthesized type parameters may only be used with a `Fn` trait``.
- **A one-element list is still a list.** `Product![T]` is `Cons<T, Nil>`, a distinct type from `T`.
- **Element order is part of the type.** `Product![A, B]` and `Product![B, A]` are unrelated. A
  name-tagged field list is consumed by name, so this matters little there, but a handler pipeline's
  order is its execution order.

## Source

- Entry points: `Product` and `product` in
  [crates/macros/cgp-macro-lib/src/product.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/product.rs).
- Type form: the `ProductType` construct in
  [crates/macros/cgp-macro-core/src/types/product/product_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/product/product_type.rs),
  whose `eval` right-folds the elements with `Cons` onto `Nil`.
- Value form: `ProductExpr` in
  [crates/macros/cgp-macro-core/src/types/product/product_expr.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/product/product_expr.rs),
  which does the same fold with the `Cons(..)` constructor.
- Runtime types:
  [crates/core/cgp-base-types/src/types/cons.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/cons.rs)
  (`Cons<Head, Tail>`) and
  [crates/core/cgp-base-types/src/types/nil.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/nil.rs)
  (`Nil`).
- Internal walkthrough (the parse-and-`eval` pipeline shared by both forms, the right-fold onto
  `Nil`, and the index of tests):
  [implementation/entrypoints/product.md](../../implementation/entrypoints/product.md).
