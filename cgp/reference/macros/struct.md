# `Struct!`

`Struct! { name: Type, … }` and `Struct!(Type, …)` build the type-level shape of a struct from the
body of a struct declaration: the same type that [`#[derive(HasFields)]`](../derives/derive_has_fields.md)
gives that struct as its `Fields`.

## Purpose

`Struct!` lets code name a record's shape in the syntax a Rust programmer already reads. Generic
code over extensible records works on [`HasFields`](../traits/has_fields.md) shapes, and a shape
written by hand is a [`Product!`](product.md) of [`Field`](../types/field.md) entries that restates
every field name as a [`Symbol!`](symbol.md):
`Product![Field<Symbol!("name"), String>, Field<Symbol!("age"), u8>]`. `Struct! { name: String, age: u8 }`
is the same type, written as the struct body it describes.

The macro is useful wherever a shape is named rather than derived: an associated-type binding such
as `T: HasFields<Fields = Struct! { … }>`, the self type of an impl over a shape, a wiring entry, or
a dispatch key. It is also the form [`cargo-cgp`](../cargo-cgp.md) prints a shape in, both in a
diagnostic and in `cargo cgp expand`, so a shape the tool shows can be copied back into code.

`Struct!` builds a type, never a value. A value of the shape is built with
[`product!`](product.md) or taken from a struct with `ToFields`.

## Syntax

The body is the inside of a struct declaration, in one of two forms:

```rust
Struct! { name: String, age: u8 }   // the body of `struct S { … }`
Struct!(u64, String)                // the body of `struct S(…);`
Struct! {}                          // an empty body
```

**The form is read from the entries, not from the delimiter.** A procedural macro never sees the
delimiter it was invoked with, so `Struct!(a: u8)` is the named form and `Struct! { u8, bool }` is
the tuple form. The conventional spelling is braces for named fields and parentheses for a tuple
body, and that is the spelling cargo-cgp prints. An entry is named when it starts with an
identifier followed by a single `:`, so a path type such as `core::marker::PhantomData<u8>` is a
positional field.

A field name may be a raw identifier, and its tag is the name without the `r#`, as the derive tags
it: `Struct! { r#type: u8 }` keys its field by `Symbol!("type")`. Either form accepts a trailing
comma. Field types are ordinary Rust types, including generic parameters, references with
lifetimes, and associated-type projections.

The parts of a struct body that a shape has no use for are rejected at parse time with a spanned
error:

- **Attributes:** any attribute on a field, including a `///` doc comment.
- **Visibility:** `pub`, `pub(crate)`, or any other visibility on a field.
- **An unnamed field:** the `_` field name.
- **Duplicate names:** a field name given twice, comparing names without `r#`.
- **Mixed forms:** a body with both `name: Type` entries and bare types.
- **A value:** a literal where a type belongs, as in `Struct! { a: 1 }`.

## Syntax Grammar

The body is either a list of named fields or a list of types:

```ebnf
StructInput -> NamedFields | TupleFields

NamedFields -> ( NamedField ( `,` NamedField )* `,`? )?

NamedField  -> IDENTIFIER `:` Type

TupleFields -> ( Type ( `,` Type )* `,`? )?
```

`IDENTIFIER` includes raw identifiers and excludes `_`. `Type` is the Rust grammar's type
production. The empty body matches both alternatives, and both give the same type.

## Expansion

`Struct!` expands exactly as `#[derive(HasFields)]` expands the same body, because the macro runs
the derive's encoder. Named fields become `Field` entries keyed by `Symbol!`, in declaration order:

```rust
// before
Struct! { name: String, age: u8 }
```

```rust
// after
Cons<Field<Symbol!("name"), String>, Cons<Field<Symbol!("age"), u8>, Nil>>
```

Positional fields become `Field` entries keyed by [`Index<N>`](../types/index.md):

```rust
// before
Struct!(u64, String)
```

```rust
// after
Cons<Field<Index<0>, u64>, Cons<Field<Index<1>, String>, Nil>>
```

Two bodies are special, both following the derive. A body with **exactly one positional field** is
that field's type, with no `Field` wrapper and no list, so `Struct!(u64)` is `u64`, as the `Fields`
of `struct Wrap(u64);` is. A trailing comma does not change this: `Struct!(u64,)` is `u64` too. An
**empty body** is `Nil`, the shape of a unit struct. A single *named* field is not unwrapped:
`Struct! { value: u64 }` is the one-element list `Cons<Field<Symbol!("value"), u64>, Nil>`.

Every CGP name in the expansion is emitted fully qualified, so the macro works in a module that
imports only the macro itself.

## Examples

A function generic over any struct with a given shape bounds the shape directly. Here `Person`
derives its shape, and `rebuild` turns a value of that shape back into any type with the same
`Fields`:

```rust
use cgp::prelude::*;

#[derive(Debug, PartialEq, HasFields)]
pub struct Person {
    pub name: String,
    pub age: u8,
}

pub fn rebuild<T>(fields: Struct! { name: String, age: u8 }) -> T
where
    T: FromFields<Fields = Struct! { name: String, age: u8 }>,
{
    T::from_fields(fields)
}

let person: Person = rebuild(product!["Carol".to_owned().into(), 25u8.into()]);
assert_eq!(person.age, 25);
```

`product!` builds the value, and each `.into()` wraps a field value in its `Field`, with the tag
inferred from the `Struct!` type. A value of the shape also comes from an existing struct:
`let fields: Struct! { name: String, age: u8 } = person.to_fields();`.

A shape is an ordinary type, so a trait can be implemented for it, and a context can wire a
component per shape with an `open` statement:

```rust
delegate_components! {
    App {
        open ShapeDescriberComponent;

        @ShapeDescriberComponent.Struct! { x: f64, y: f64 }: DescribePoint,
        @ShapeDescriberComponent.Struct!(u8, u16): DescribePair,
    }
}
```

## Related constructs

These constructs are the ones `Struct!` relates to:

- [`Enum!`](enum.md): the enum counterpart, building a [`Sum!`](sum.md) of variants whose payloads
  follow the `Struct!` rules.
- [`Product!`](product.md): the list `Struct!` expands to, and the form to write when a shape has
  no `Struct!` spelling.
- [`Field`](../types/field.md), [`Symbol!`](symbol.md), and [`Index`](../types/index.md): the entry
  and the two tags a shape is built from.
- [`#[derive(HasFields)]`](../derives/derive_has_fields.md) and [`HasFields`](../traits/has_fields.md):
  the derive whose encoder `Struct!` runs, and the trait whose `Fields` it names.
- [`cargo-cgp`](../cargo-cgp.md): prints shapes in this form, in diagnostics and in
  `cargo cgp expand`.

## Known issues

These corner cases follow from the encoding or from how other tools see the expansion:

- **A one-element positional list has no `Struct!` spelling.** `Struct!(T)` is `T` by the newtype
  rule, so the list `Cons<Field<Index<0>, T>, Nil>` is written
  `Product![Field<Index<0>, T>]`. cargo-cgp prints it that way for the same reason.
- **The shape is a type, not a value.** `Struct! { a: 1 }` is rejected with
  `expected a type: a type-level shape lists field types, not values`. Build a value with
  `product!` or `ToFields`.
- **Clippy's `type_complexity` lint fires on ordinary shapes.** Clippy measures the expanded type,
  where every field name is a nested `Symbol<N, Chars<…>>` chain, so a shape nested inside another
  type in a signature can exceed the lint's threshold. A type alias for the shape, or
  `#[allow(clippy::type_complexity)]`, silences it.
- **`#[use_type]` does not rewrite an alias inside the body.** In an item that imports `Error`
  with `#[use_type(HasErrorType.Error)]`, a bare `Error` written inside `Struct! { … }` is left
  bare and fails with `E0425`. Write the qualified `<Self as HasErrorType>::Error` there. The
  [`#[use_type]` Known issues](../attributes/use_type.md#known-issues) describe the defect.

## Source

- Entry point: `Struct` in
  [crates/macros/cgp-macro-lib/src/struct_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/struct_type.rs).
- AST type: `StructType` in
  [crates/macros/cgp-macro-core/src/types/shape/struct_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/shape/struct_type.rs).
- Body parsing and validation: `parse_shape_fields` and `validate_shape_fields` in
  [crates/macros/cgp-macro-core/src/functions/shape/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/functions/shape).
- Encoder shared with the derive: `item_fields_to_product_type` in
  [crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/product.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/product.rs).
- Internal walkthrough (the form detection, the validation, and the index of tests):
  [implementation/entrypoints/struct.md](../../implementation/entrypoints/struct.md).
