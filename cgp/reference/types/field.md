# `Field`

`Field<Tag, Value>` is the named entry of CGP's structural data, pairing a `Value` with a type-level `Tag` that records the entry's name at no runtime cost.

## Purpose

`Field` lets a field's name and value travel together as one type, so generic code knows not only what a struct holds but what each piece is called. A bare [`Product!`](../macros/product.md) list such as `Product![String, u8]` records only the types and their order; it cannot tell `name: String` from any other `String`. Wrapping each element as `Field<Symbol!("name"), String>` attaches the name as a phantom type, so a struct's structural representation describes itself and a provider walking the list can match on the tag to find the field it wants.

The tag is a phantom type because the name is needed only at compile time, for trait resolution and dispatch. A `Field<Tag, Value>` is exactly as large as its `Value`, since `PhantomData<Tag>` takes no space. This is the string-as-type device that [`Symbol!`](../macros/symbol.md) provides for names and [`Index`](index.md) for positions; `Field` is where the tag meets the value it labels.

`Field` fills both structural lists. A struct's [`HasFields`](../traits/has_fields.md) representation is a `Product!` of `Field` entries, one per field, and an enum's is a [`Sum!`](../macros/sum.md) of `Field` entries, one per variant, whose `Value` is the variant's payload.

## Definition

`Field` is a two-parameter struct holding the value beside a phantom tag:

```rust
pub struct Field<Tag, Value> {
    pub value: Value,
    pub phantom: PhantomData<Tag>,
}
```

`Tag` is the entry's type-level name. It appears only inside `PhantomData<Tag>`, and it is usually a type-level string such as `Symbol!("name")` for a named field or variant, or a type-level number such as `Index<0>` for a tuple position. `Value` is the entry's type, and `value` is the only data the struct stores.

## Behavior

A `Field` is built from its value alone, because the tag is fixed by the target type. The `From<Value>` impl fills `value` and sets `phantom`, so `let f: Field<Symbol!("name"), String> = "Alice".to_string().into();` works, with the tag inferred from the annotation. This is why generated `HasFields` code builds each entry with a plain `.into()`.

The remaining impls defer to the value and ignore the tag, so a `Field` compares and prints like its `Value`. `Debug` forwards to the value's `Debug` without showing the tag, and `PartialEq` and `Eq` compare only `value`, each requiring the matching bound on `Value`. Code that needs the name reads it from the `Tag` parameter through trait resolution, such as matching a `Field<Symbol!("name"), _>` against a `HasField<Symbol!("name")>` bound, never from stored data.

## Examples

`Field` most often appears in the `HasFields` representation a derive generates, where each struct field becomes one entry tagged by its name:

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
// }
```

A single `Field` can be built from its value, with the tag supplied by the annotation:

```rust
use cgp::prelude::*;

let name: Field<Symbol!("name"), String> = "Alice".to_string().into();
assert_eq!(name.value, "Alice");
```

A tuple struct with two or more fields tags its entries by position instead, as in `Field<Index<0>, u32>`. A tuple struct with exactly one field is the exception: its representation is the field's type itself, with no `Field` wrapper and no list, so `struct Wrap(u32)` has `Fields = u32`. A one-field tuple variant likewise has its bare field type as the payload inside its variant's `Field`.

## Related constructs

These constructs are the ones `Field` relates to:

- [`Product!`](../macros/product.md) and [`Sum!`](../macros/sum.md) — the lists `Field` entries fill, built from [`Cons`/`Nil`](cons.md) and [`Either`/`Void`](either.md).
- [`Symbol!`](../macros/symbol.md) and [`Index`](index.md) — produce the tag for a named entry and a positional one.
- [`#[derive(HasFields)]`](../derives/derive_has_fields.md) and [`HasFields`](../traits/has_fields.md) — assign and expose a type's list of entries.
- [`HasField`](../traits/has_field.md), derived by [`#[derive(HasField)]`](../derives/derive_has_field.md) — single-field access against a matching tag.

## Source

- `Field<Tag, Value>` and its `From`, `Debug`, `PartialEq`, and `Eq` impls are defined in [crates/core/cgp-field/src/types/field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/types/field.rs).
- It is consumed by the field machinery: [`HasFields`](../traits/has_fields.md) in [crates/core/cgp-field/src/traits/has_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_fields.rs), with the record and variant conversion traits in [crates/core/cgp-field/src/traits/from_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/from_fields.rs) and [crates/core/cgp-field/src/traits/to_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/to_fields.rs).
- The derive that emits `Product!`/`Sum!` lists of `Field` entries is under [crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/).
