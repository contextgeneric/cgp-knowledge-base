# The `shape` AST stack

The `shape` stack is the pair of AST types behind the [`Struct!`](../entrypoints/struct.md) and
[`Enum!`](../entrypoints/enum.md) macros, together with the two helper functions that read and
check a shape's fields. Each type holds the `syn` form a declaration of the same body would hold, a
`syn::Fields` for `StructType` and a list of `syn::Variant` for `EnumType`, so that its `eval` can
run the [`#[derive(HasFields)]`](../entrypoints/derive_has_fields.md) encoder unchanged. The
entrypoint documents cover what the macros produce; this document covers the types.

## `StructType`

`StructType` holds `fields: syn::Fields`. Its `Parse` impl is a call to `parse_shape_fields`, and its
`eval` calls `item_fields_to_product_type(&self.fields, &TokenStream::new())`, passing no reference
prefix because a shape names owned field types. The derive passes `&'__a` there to build its
borrowed `FieldsRef` shape; a user writes the borrow into each field type instead.

```rust
// Struct!(u64, String) parses to
Fields::Unnamed(FieldsUnnamed { unnamed: [u64, String], .. })
// and evals to
Cons<Field<Index<0>, u64>, Cons<Field<Index<1>, String>, Nil>>
```

## `EnumType`

`EnumType` holds `variants: Punctuated<Variant, Comma>`. Its `Parse` impl reads one variant at a time
through a local `parse_variant`, collecting the names to reject a duplicate, and builds each
`syn::Variant` with no attributes and no discriminant. Its `eval` calls
`variants_to_sum_type(&self.variants, &TokenStream::new())`.

`parse_variant` exists because `syn::Variant::parse` discards a `pub` and accepts a discriminant,
both of which a shape must reject. It reads the attributes, the visibility check, the name, the
fields through `syn`'s `FieldsNamed` or `FieldsUnnamed` parser, and the discriminant check, in that
order, and runs `validate_shape_fields` on the fields.

## `parse_shape_fields`

`parse_shape_fields`, in
[functions/shape/parse_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/shape/parse_fields.rs),
reads a `Struct!` body into a `syn::Fields`. It loops over the comma-separated entries, classifying
each with `peek_named_entry` before parsing it with `Field::parse_named` or `Field::parse_unnamed`,
and rejects an entry whose form differs from the first. An empty body is `Fields::Unit`. It ends by
calling `validate_shape_fields`.

`peek_named_entry` works on a fork so it consumes nothing. It skips the entry's outer attributes and
visibility, then reads the entry as named when the next tokens are an identifier or `_` followed by
a single `:`, excluding `::`. On the same fork it also reports a literal where the field type should
start, which is the one validation that must happen before `syn`'s type parser would fail with a
less useful message.

## `validate_shape_fields`

`validate_shape_fields`, in
[functions/shape/validate_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/shape/validate_fields.rs),
rejects, in field order, a field attribute (through `reject_non_empty_attributes`), any visibility
other than `Visibility::Inherited`, the `_` name, and a name seen earlier in the same body. Names are
compared after `unraw`, matching the `Symbol::from_ident` tagging that would otherwise give two
fields the same tag. Both macros call it, so a field rule cannot differ between a `Struct!` body and
an `Enum!` variant.

## Tests

- [shape_macro_parsing/struct_form.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/shape_macro_parsing/struct_form.rs)
  pins the form `StructType` reads each body as.
- [shape_macro_parsing/enum_variants.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/shape_macro_parsing/enum_variants.rs)
  pins the shape `EnumType` gives each variant.
- [parser_rejections/struct_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/struct_macro.rs)
  and
  [parser_rejections/enum_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/enum_macro.rs)
  pin every rejection message of `parse_shape_fields`, `validate_shape_fields`, and `parse_variant`.
- The `shape_macros` target of `cgp-tests` pins what `eval` produces; its files are indexed in the
  [`Struct!`](../entrypoints/struct.md#tests) and [`Enum!`](../entrypoints/enum.md#tests) entrypoint
  documents.

## Source

- The AST types live in
  [cgp-macro-core/src/types/shape/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/shape):
  `StructType` in `struct_type.rs`, and `EnumType` with `parse_variant` in `enum_type.rs`.
- The helpers live in
  [cgp-macro-core/src/functions/shape/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/functions/shape),
  and `reject_non_empty_attributes` in
  [cgp-macro-core/src/functions/reject_attributes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/reject_attributes.rs).
- The encoders they call are documented under
  [`#[derive(HasFields)]`](../entrypoints/derive_has_fields.md).
