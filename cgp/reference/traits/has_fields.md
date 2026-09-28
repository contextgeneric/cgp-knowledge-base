# `HasFields`

`HasFields` exposes a type's whole field structure as one type-level shape: a
[`Product`](../macros/product.md) for a struct and a [`Sum`](../macros/sum.md) for an enum.
`HasFieldsRef` gives the borrowed view, and `ToFields`, `FromFields`, and `ToFieldsRef` convert
between a value and that shape.

## Purpose

`HasFields` describes a type's entire shape as one type. Where [`HasField<Tag>`](has_field.md) gives
one field by name, `HasFields` gives a single associated `Fields` type listing every field, each
tagged with its name. Generic code folds over that one type: serialization, builders, conversions,
and the extensible-record and extensible-variant machinery all work on `Fields` rather than on
fields one at a time.

The two traits are complementary. `HasField` is indexed access through many small impls, for
dependency injection where a provider wants one value. `HasFields` is a single impl enumerating the
full shape, for an algorithm that processes the type as a record or a tagged union. The two are
complementary, and a type that wants both indexed access and structural processing derives both with
[`#[derive(HasField, HasFields)]`](../derives/derive_has_fields.md).

The conversion traits make the view two-way. `ToFields` turns an owned value into its `Fields`
shape, `FromFields` rebuilds the value from the shape, and `ToFieldsRef` borrows the value as a
shape of references. Together they let generic code decompose a concrete type into its anonymous
structural form, transform it, and reconstruct the concrete type.

## Definition

The two core traits each carry a single associated type and nothing else. `HasFields` names the
owned shape, and `HasFieldsRef` names the borrowed shape, parameterized by a lifetime:

```rust
pub trait HasFields {
    type Fields;
}

pub trait HasFieldsRef {
    type FieldsRef<'a>
    where
        Self: 'a;
}
```

For a struct, `Fields` is a [`Product`](../macros/product.md), a `Cons`/`Nil` chain of
[`Field<Tag, Value>`](../types/field.md) entries, each value carrying its type-level name tag. For
an enum, `Fields` is a [`Sum`](../macros/sum.md): an `Either`/`Void` chain of `Field<Tag, …>`
entries, one per variant. A variant with one unnamed field carries its payload type directly, a unit
variant carries `Nil`, and any other variant carries its fields as a nested product. Named fields
and variants are tagged by [`Symbol!`](../macros/symbol.md); tuple fields by `Index<N>`.
`FieldsRef<'a>` is the same shape with each value borrowed for `'a`.

The three conversion traits each supertrait one of the two shape traits and add a single method.
`ToFields` and `FromFields` build on `HasFields`, while `ToFieldsRef` builds on `HasFieldsRef`:

```rust
pub trait ToFields: HasFields {
    fn to_fields(self) -> Self::Fields;
}

pub trait FromFields: HasFields {
    fn from_fields(fields: Self::Fields) -> Self;
}

pub trait ToFieldsRef: HasFieldsRef {
    fn to_fields_ref<'a>(&'a self) -> Self::FieldsRef<'a>
    where
        Self: 'a;
}
```

`to_fields` consumes the value to produce the shape, `from_fields` rebuilds the value from the
shape, and `to_fields_ref` borrows the value to produce a shape of references, for when the value
must be kept. All five traits are in the prelude.

## Behavior

All five impls come from [`#[derive(HasFields)]`](../derives/derive_has_fields.md); the trait
modules define only the bare traits. The derive names the borrowed shape's lifetime `'__a`, so a
field that is itself a reference gains a second one: `name: &'a str` appears in `FieldsRef<'__a>` as
`&'__a &'a str`. The conversions it emits for a struct are one `Cons` chain each:

```rust
impl FromFields for Config {
    fn from_fields(Cons(host, Cons(port, Nil)): Self::Fields) -> Self {
        Self {
            host: host.value,
            port: port.value,
        }
    }
}
impl ToFields for Config {
    fn to_fields(self) -> Self::Fields {
        Cons(self.host.into(), Cons(self.port.into(), Nil))
    }
}
```

For an enum, `to_fields` matches each variant onto its `Either` arm and `from_fields` matches down
the chain, ending in `Either::Right(rest) => match rest {}` on the `Void` terminator. `HasFields`
accepts every variant shape, where the extractor derives need one unnamed payload per variant. A struct produces a `Product!` of its fields and an enum a
`Sum!` of its variants. A single-field tuple struct is special: its `Fields` is the inner type
directly, so `struct Wrap(u32)` has `Fields = u32`, not a one-element product.

The conversions are mechanical inverses of one another. `to_fields` folds the concrete value into a
`Cons` chain (or an `Either` arm for an enum), `from_fields` pattern-matches that chain back into
the concrete fields, and `to_fields_ref` builds the same `Cons` chain over borrows. Because
`from_fields` and `to_fields` round-trip through the identical `Fields` type, generic code can
decompose a value, operate on the structural form, and rebuild the value with the guarantee that the
shapes line up by construction.

## Examples

Deriving `HasFields` lets generic code treat any type as a record without naming its concrete type,
and a value can be round-tripped through its `Fields` shape:

```rust
use cgp::prelude::*;

#[derive(HasField, HasFields)]
pub struct Config {
    pub host: String,
    pub port: u16,
}

fn round_trip(config: Config) -> Config {
    // Product![Field<Symbol!("host"), String>, Field<Symbol!("port"), u16>]
    let fields = config.to_fields();

    Config::from_fields(fields)
}
```

For an enum the shape is a sum. A `Shape` enum with `Circle { radius: f64 }` and
`Rectangle { width: f64, height: f64 }` variants has
`Fields = Either<Field<Symbol!("Circle"), Product![…]>, Either<Field<Symbol!("Rectangle"), Product![…]>, Void>>`,
and the same `to_fields` and `from_fields` move a `Shape` in and out of it. Generic algorithms bound
`Context: HasFields` (or `ToFields`/`FromFields`) and process `Context::Fields` structurally, which
is how the extensible-data machinery operates over arbitrary contexts.

## Related constructs

`HasFields` is the structural counterpart to [`HasField`](has_field.md): `HasField` gives indexed,
single-field access for dependency injection, while `HasFields` gives the whole-shape view. All five
impls are generated by [`#[derive(HasFields)]`](../derives/derive_has_fields.md). The `Fields` shape
is built from [`Product`](../macros/product.md) for structs and [`Sum`](../macros/sum.md) for enums,
with each entry a [`Field<Tag, Value>`](../types/field.md) tagged by
[`Symbol!`](../macros/symbol.md).

## Source

- The trait definitions are in
  [crates/core/cgp-field/src/traits/has_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_fields.rs)
  (`HasFields`, `HasFieldsRef`),
  [crates/core/cgp-field/src/traits/to_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/to_fields.rs)
  (`ToFields`, `ToFieldsRef`), and
  [crates/core/cgp-field/src/traits/from_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/from_fields.rs)
  (`FromFields`).
- The `Field`, `Cons`/`Nil`, `Either`/`Void` building blocks live under
  [crates/core/cgp-field/src/types/](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-field/src/types/).
- The derive that emits the impls is in
  [crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/).
- For how it is generated and the index of tests, see the implementation document
  [implementation/entrypoints/derive_has_fields.md](../../implementation/entrypoints/derive_has_fields.md).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **5 pages**
rather than one: [`has_fields`](https://contextgeneric.dev/docs/reference/traits/shape/has_fields),
[`has_fields_ref`](https://contextgeneric.dev/docs/reference/traits/shape/has_fields_ref),
[`to_fields`](https://contextgeneric.dev/docs/reference/traits/shape/to_fields),
[`from_fields`](https://contextgeneric.dev/docs/reference/traits/shape/from_fields),
[`to_fields_ref`](https://contextgeneric.dev/docs/reference/traits/shape/to_fields_ref). A change
here is propagated to each of them, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping and the granularity
rule behind it are recorded in [website/site-structure.md](../../../website/site-structure.md).
