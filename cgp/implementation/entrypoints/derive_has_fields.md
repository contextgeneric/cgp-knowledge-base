# `#[derive(HasFields)]` — implementation

`#[derive(HasFields)]` gives a struct or enum a whole-shape view by emitting the representation impls — `HasFields`, `HasFieldsRef`, `FromFields`, `ToFields`, `ToFieldsRef` — that describe the type as a single type-level product (for a struct) or sum (for an enum). This document covers how that codegen works; for the accepted syntax and the full expansion, read the reference document [reference/derives/derive_has_fields.md](../../reference/derives/derive_has_fields.md).

## Entry point

The macro is driven by the `derive_has_fields` function in [cgp-macro-lib/src/derive_has_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/derive_has_fields.rs). Unlike the other data derives it dispatches on shape at the entry point: it parses the input as a `syn::Item` and branches on `struct` versus `enum`, rejecting anything else with a spanned "expect body to be either a struct or enum" error:

```rust
let impls = match item {
    Item::Struct(item_struct) => ItemCgpRecord { item_struct }.to_has_fields_impls()?,
    Item::Enum(item_enum)     => derive_has_fields_impls_from_enum(&item_enum)?,
    _ => return Err(/* struct or enum */),
};
```

The struct path goes through `ItemCgpRecord`; the enum path calls the enum codegen helper directly.

## Pipeline

There is no multi-stage transform. Both paths call a single codegen helper — `derive_has_fields_impls_from_struct` for a struct, `derive_has_fields_impls_from_enum` for an enum — that emits the five representation impls. The [`cgp_data` AST stack](../asts/cgp_data.md) documents `ItemCgpRecord` and the `Symbol`/`Index` field-tag types.

## Generated items

The derive emits five impls and leaves the type definition untouched. The load-bearing part is the `Fields` associated type: a struct's fields become a [`Product`](../../reference/macros/product.md) of [`Field<Tag, Value>`](../../reference/types/field.md) entries over the `Cons`/`Nil` list, and an enum's variants become a [`Sum`](../../reference/macros/sum.md) of `Field<Symbol!("Variant"), Payload>` entries over the `Either`/`Void` list. Named fields and variant names are keyed by [`Symbol!`](../../reference/macros/symbol.md); tuple fields by [`Index<N>`](../../reference/types/index.md).

```rust
// struct → product
impl HasFields for Person {
    type Fields = Cons<Field<Symbol!("name"), String>, Cons<Field<Symbol!("age"), u8>, Nil>>;
}
// enum → sum, terminated by Void
impl HasFields for Shape {
    type Fields = Either<Field<Symbol!("Circle"), Circle>, Either<Field<Symbol!("Rectangle"), Rectangle>, Void>>;
}
```

Alongside the shape type, the derive emits `HasFieldsRef` (the same product/sum with each value borrowed under a fresh `'__a` lifetime) and the three conversions: `ToFields` builds the product/sum from a value, `FromFields` destructures it back, and `ToFieldsRef` builds the borrowed form. For a struct the conversions read `self.<field>.into()` into a `Cons(…)` chain and pattern-match `Cons(…)` back into `Self { … }`; for an enum they match each concrete variant to its `Either` arm and back. The product list is built by `item_fields_to_product_type` in the `product.rs` submodule and the sum list by `variants_to_sum_type` in `sum.rs`; the entries are chained right-associatively.

## Behavior and corner cases

A **single-field tuple struct** (a newtype) is special-cased: its `Fields` is the inner type directly, not a one-element `Cons<Field<Index<0>, _>, Nil>`, and the conversions pass the single value straight through. A tuple struct with more than one field is not special-cased — its fields are keyed by `Index<N>` and chained into the usual product.

A **unit struct** produces `Nil` as its `Fields`, and its conversions round-trip through the empty product.

The type's **generic parameters and `where` clause** are threaded onto all five impls. A borrowed field type appears verbatim in the product, and `HasFieldsRef` layers its own `'__a` borrow on top — so a field of type `&'a Name` becomes `&'__a &'a Name` in `FieldsRef<'__a>`. The `HasFieldsRef` associated type carries the `where Self: '__a` bound that every borrowed representation needs.

An **enum** accepts every variant shape, because the `HasFields` path only *describes* a variant rather than deconstructing it, and so does not impose the single-unnamed-field requirement that the extractor and `FromVariant` derives do. `variants_to_sum_type` runs each variant's own `syn::Fields` through the same `item_fields_to_product_type` helper the struct path uses, which is what makes the four shapes fall out of one rule: a unit variant becomes `Nil`, a single-unnamed-field variant becomes its payload type directly (the newtype special case applied inside a variant), a multi-field tuple variant becomes a product keyed by `Index<N>`, and a named-field variant becomes a product keyed by `Symbol!`. The conversions follow: `derive_from_field_params` and `extract_variant_args` destructure and rebuild whichever shape each variant has, so a mixed-shape enum round-trips. The consequence worth stating is that `#[derive(HasFields)]` alone succeeds on an enum where the umbrella `#[derive(CgpData)]` would fail.

## Error spans

All five impls are keyed on the whole type, so each is re-spanned onto the struct or enum name the user wrote rather than left at the derive's `call_site` span. A coherence conflict (`E0119`) — a hand-written `HasFields` impl clashing with the derived one — therefore lands its caret on the type name instead of on the whole `#[derive(HasFields)]`. `derive_has_fields_impls_from_struct` and `derive_has_fields_impls_from_enum` pass each finished impl through [`override_item_span`](../README.md#spans-aim-generated-items-at-the-token-the-user-wrote), which moves only the `impl`/`{ … }` boundary — the mechanism the [`#[derive(HasField)]`](derive_has_field.md#error-spans) doc explains in full.

## Known issues

**The codegen names its associated types as `Self::Fields` and `Self::FieldsRef`, so those two variant names make the enum expansion invalid.** `from_fields` takes `rest: Self::Fields` and `to_fields_ref` returns `Self::FieldsRef<'__a>`; inside an impl for an enum either path can resolve to a variant of the same name, so `rustc` rejects the expansion with `ambiguous associated item`, with its headline on the derive attribute and a `note` pointing at the user's own variant — because these impls are written `for` the user's enum, the colliding variant keeps its own span and the error stays actionable, unlike the extractor's. Writing each as `<Self as HasFields>::Fields` would remove the ambiguity and is the fix. The variant derives add five further reserved names — see [`#[derive(ExtractField)]`](derive_extract_field.md#known-issues) — so an enum deriving the whole family has seven. A struct's *field* names are unaffected, since a field is not in the same namespace as an associated type. Pinned by [invalid_expansion/reserved_variant_names.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/invalid_expansion/reserved_variant_names.rs).

## Snapshots

Every `snapshot_derive_has_fields!` invocation across the suite is indexed here, since these snapshots all belong to this entrypoint. The struct expansion is owned by the `extensible_records` target and the enum expansion by `extensible_variants`:

- [extensible_records/struct_single_named_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_records/struct_single_named_field.rs) — the canonical struct expansion, one named field.
- [extensible_records/struct_two_named_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_records/struct_two_named_fields.rs) — a two-field `Cons<_, Cons<_, Nil>>` product.
- [extensible_records/struct_single_unnamed_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_records/struct_single_unnamed_field.rs) — the newtype special case, `Fields` = the inner type.
- [extensible_records/struct_tuple_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_records/struct_tuple_fields.rs) — a multi-field tuple struct keyed by `Index<N>`.
- [extensible_records/struct_generic.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_records/struct_generic.rs) — a generic struct with a `where` clause threaded onto each impl.
- [extensible_records/struct_generic_lifetime.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_records/struct_generic_lifetime.rs) — a lifetime plus type parameter, with the layered `&'__a &'a` borrow in `FieldsRef`.
- [extensible_records/struct_unit_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_records/struct_unit_field.rs) — a unit struct, `Fields` = `Nil`; the same file pins that `#[derive(HasField)]` on a unit struct emits nothing at all, with an empty snapshot.
- [extensible_variants/has_fields_enum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_variants/has_fields_enum.rs) — the canonical enum expansion, a `Sum!` of `Field<Symbol!("Variant"), Payload>`.
- [extensible_variants/has_fields_enum_generic.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_variants/has_fields_enum_generic.rs) — a generic enum with a lifetime and a reference-typed payload.
- [extensible_variants/has_fields_enum_shapes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_variants/has_fields_enum_shapes.rs) — all four variant shapes in one enum, pinning the unit-to-`Nil`, newtype-passthrough, `Index<N>`-product, and `Symbol!`-product mappings, with a round-trip per shape and one over the borrowed form.

## Tests

The snapshot tests above double as the coverage:

- Each pins one field-shape and, where paired with runtime assertions, round-trips a value through `to_fields`/`from_fields`.
- The `struct_single_unnamed_field` snapshot is the guard on the newtype special case.
- `struct_generic`/`struct_generic_lifetime` and `has_fields_enum_generic` guard the generic-threading behavior.
- [invalid_expansion/reserved_variant_names.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/invalid_expansion/reserved_variant_names.rs) pins the reserved-variant-name defect recorded under Known issues, capturing the emitted `Self::…` paths as a string snapshot so the test compiles even though the code it describes would not.

## Source

- Entry point: `derive_has_fields` in [cgp-macro-lib/src/derive_has_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/derive_has_fields.rs).
- The struct path calls `ItemCgpRecord::to_has_fields_impls` in [cgp-macro-core/src/types/cgp_data/record.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/record.rs); both paths land in the [derive_has_fields/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/) submodule, where `derive_struct.rs`/`derive_enum.rs` drive the five impls, `product.rs` (`item_fields_to_product_type`) builds the struct product, `sum.rs` (`variants_to_sum_type`) builds the enum sum, and the `from_fields_*`/`to_fields_*`/`to_fields_ref_*` files build the conversions. The AST types are documented in [asts/cgp_data.md](../asts/cgp_data.md).
- The `HasFields`, `HasFieldsRef`, `FromFields`, `ToFields`, and `ToFieldsRef` traits and the `Field`/`Either`/`Void` building blocks live under [crates/core/cgp-field/src/](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-field/src/).
