# `Index`

`Index<const I: usize>` encodes a `usize` at the type level, giving a tuple-struct field a
type-level name based on its position, the way [`Symbol!`](../macros/symbol.md) names a field by its
string.

## Purpose

`Index` exists because CGP keys every field by a type tag, and a tuple-struct field has only a
position, not a name to turn into a [`Symbol!`](../macros/symbol.md). For positional fields to use
the same trait-resolution machinery as named ones, the position must become a type. `Index<I>` is
that type: it carries a `usize` as a const parameter and nothing else, so `Index<0>`, `Index<1>`,
and `Index<2>` are three distinct types standing for the first, second, and third fields.

Encoding the position as a type lets positional access resolve through traits. A context can carry a
`HasField<Index<0>>` impl for its first field beside a `HasField<Index<1>>` impl for its second, and
the compiler picks the right one from the tag, exactly as it would for two different `Symbol!`
names. A field is keyed by `Symbol!` when it has a name and by `Index` when it has only a position.

`Index` is a zero-sized marker whose only job is to make a number available at the type level. It
appears as a [`HasField`](../traits/has_field.md) tag, as the `Tag` of a [`Field`](field.md) entry
in a tuple struct's [`HasFields`](../traits/has_fields.md) list, and inside `PhantomData` wherever a
positional name is needed at compile time.

## Definition

`Index` is a zero-sized struct with a single const parameter:

```rust
#[derive(Eq, PartialEq, Clone, Copy, Default)]
pub struct Index<const I: usize>;
```

`I` is the position the type stands for, so `Index<0>` is the field at offset zero. The struct has
no fields, so the number lives entirely in the type. The derived `Default`, `Clone`, and `Copy` make
a value trivially available, and `Eq`/`PartialEq` treat any two values of the same `Index<I>` as
equal, since there is nothing to differ.

`Index<I>` implements `Display` and `Debug`, and both print `I`, so `Index<0>` displays as `0`.

## Behavior

A tuple struct keys each field by `Index<N>`, counting from zero. When it derives
[`HasField`](../derives/derive_has_field.md), the generated impls use `Index<0>` for `.0`,
`Index<1>` for `.1`, and so on. A tuple struct with two or more fields also uses these tags in its
[`HasFields`](../traits/has_fields.md) representation, a `Product!` of `Field<Index<N>, _>` entries.
A tuple struct with exactly one field is the exception there: its `Fields` is the field's type
itself, with no `Field<Index<0>, _>` wrapper, although its `HasField<Index<0>>` impl still exists.

Access by index resolves entirely at compile time, because the position lives in the type. There is
no bounds check and no runtime indexing, and an out-of-range index is a type error rather than a
panic: `Index<5>` on a three-field struct has no matching `HasField` impl. `Index` is in the prelude.

### Writing it, and what goes wrong

`Index<N>` is the tag for a tuple position and a [`Symbol!`](../macros/symbol.md) the tag for a named
field, and the derive generates the right one for each, so `Index` is written by hand only to tag a
positional field outside a derive or to read one through `get_field`. In an error, a missing
`HasField<Index<2>>` bound names the third field of a tuple struct.

The two mistakes are a position the struct lacks and a string where a number belongs. Reading
`*point.get_field(PhantomData::<Index<5>>)` on `pub struct Point(pub f64, pub f64, pub f64);` fails
with ``error[E0277]: the trait bound `Point: cgp::prelude::HasField<cgp::prelude::Index<5>>` is not satisfied``,
and the help lines list the three `HasField<Index<0>>` to `HasField<Index<2>>` impls the struct does
have, so an off-by-one index surfaces the same way. `Symbol!("0")` is a string tag, never generated
for a tuple field, so reading it on `Pair` fails with
``error[E0277]: the trait bound `Pair: cgp::prelude::HasField<cgp::prelude::Symbol<1, cgp::prelude::Chars<'0', Nil>>>` is not satisfied``.

## Examples

A tuple struct that derives `HasField` gets one impl per position:

```rust
use cgp::prelude::*;

#[derive(HasField)]
pub struct Pair(pub u32, pub String);

// generated for the first field, beside a matching `HasFieldMut<Index<0>>` impl:
// impl HasField<Index<0>> for Pair {
//     type Value = u32;
//     fn get_field(&self, key: ::core::marker::PhantomData<Index<0>>) -> &Self::Value {
//         &self.0
//     }
// }
```

A field is then read by passing its `Index` tag, with the position fixed at compile time:

```rust
use cgp::prelude::*;

let pair = Pair(7, "hi".to_string());
assert_eq!(*pair.get_field(PhantomData::<Index<0>>), 7);
```

The number an `Index` carries is also visible through `Display`:

```rust
assert_eq!(Index::<2>.to_string(), "2");
```

## Related constructs

These constructs are the ones `Index` relates to:

- [`Symbol!`](../macros/symbol.md): the name tag for named fields and enum variants, the counterpart
  of a position.
- [`HasField`](../traits/has_field.md), derived by
  [`#[derive(HasField)]`](../derives/derive_has_field.md): single-field access keyed by the tag.
- [`Field`](field.md) and [`HasFields`](../traits/has_fields.md): where the tag names each entry of
  a multi-field tuple struct's list.

## Source

- `Index<const I: usize>` and its `Display` and `Debug` impls are defined in
  [crates/core/cgp-field/src/types/index.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/types/index.rs).
- The `#[derive(HasField)]` codegen that tags tuple-struct fields with `Index<N>` is under
  [crates/macros/cgp-macro-core/src/types/cgp_data/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_data/),
  and the `HasField` trait it targets is in
  [crates/core/cgp-field/src/traits/has_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field.rs).

## Public pages derived from this document

This document feeds the public [`Index`](https://contextgeneric.dev/docs/reference/types/index_type)
page, which is named `index_type` on the site because `index.md` there is the Types section
overview. A change here is propagated to it, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping is recorded in
[website/site-structure.md](../../../website/site-structure.md).
