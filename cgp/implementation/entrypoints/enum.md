# `Enum!`: implementation

`Enum!` is a function-like macro that turns the body of an enum declaration into that enum's
type-level `HasFields` shape. This document covers how the macro reads the variants and why its
expansion matches `#[derive(HasFields)]` by construction; for the accepted syntax and the full
expansion a user sees, read the reference document
[reference/macros/enum.md](../../reference/macros/enum.md).

## Entry point

The macro is driven by the thin `Enum` function in
[cgp-macro-lib/src/enum_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/enum_type.rs),
which parses the body into an `EnumType`, calls its `eval`, and emits the result:

```rust
let enum_type: EnumType = parse2(body)?;
Ok(enum_type.eval()?.to_token_stream())
```

Every rejection happens while parsing `EnumType`. The AST type is documented in the
[`shape` AST stack](../asts/shape.md).

## Pipeline

The macro is a parse-then-`eval` step, following [`Struct!`](struct.md). Parsing reads the body into
the `Punctuated<syn::Variant, Comma>` an enum declaration holds, and `eval` hands that list to
`variants_to_sum_type`, the encoder [`#[derive(HasFields)]`](derive_has_fields.md) runs on an
enum's own variants. Lowering into the derive's input form is again what keeps the two from
drifting: there is one encoder, and it encodes each variant's payload with the same
`item_fields_to_product_type` a `Struct!` body goes through.

## Generated items

`Enum!` emits a single type, a sum of one `Field` entry per variant, ending in `Void`:

```rust
// Enum! { Empty, Circle(u32), Triangle { base: u32 } }
Either<
    Field<Symbol!("Empty"), Nil>,
    Either<
        Field<Symbol!("Circle"), u32>,
        Either<Field<Symbol!("Triangle"), Cons<Field<Symbol!("base"), u32>, Nil>>, Void>,
    >,
>
```

An empty body emits `Void`. The encoder emits `Either`, `Field`, `Void`, and the payload's own names
through the [export markers](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/exports.rs).

## Behavior and corner cases

**Each variant is read by a local parser, not by `syn::Variant::parse`.** `syn`'s variant parser
parses and silently discards a visibility, since it is meant for a declaration where the compiler
reports a misplaced `pub` later, and it accepts a discriminant. `parse_variant` therefore reads the
variant itself: it rejects any attribute with `reject_non_empty_attributes`, rejects a `pub` before
it can be discarded, reads the name, and rejects a `=` discriminant after the fields. The fields
inside the variant's braces or parentheses are read by `parse_variant_fields`, the loop that reads a
`Struct!` body with the form fixed by the delimiter instead of detected. Each entry therefore goes
through the same keyword and literal checks and the same `validate_shape_fields`, so a field rule
and its message hold identically inside a variant. An entry whose form contradicts the delimiter,
such as `V { u8 }` or `V(a: u8)`, is rejected with a message naming the delimiter's form.

**A variant's delimiter is visible, so it keeps its Rust meaning.** Unlike the `Struct!` invocation
delimiter, the parentheses or braces after a variant name are tokens inside the body. Braces
therefore always hold named fields and parentheses positional ones, and no content-based detection
is needed or applied.

**Duplicate variant names are rejected,** compared without `r#`, as Rust rejects them in a
declaration. Two entries with the same tag would make every per-variant lookup ambiguous.

**The payload rules come from the encoder.** A unit variant, `V()`, and `V {}` all carry `Nil`, one
positional field carries its bare type, several carry an `Index`-keyed product, and named fields
carry a `Symbol!`-keyed product. The equivalences this produces, such as `V { a: u32 }` being
`V(Struct! { a: u32 })`, are what lets cargo-cgp print a variant list in its shortest spelling.

## Known issues

**An alias imported with `#[use_type]` is not rewritten inside the body**, for the reason recorded
in [`Struct!`](struct.md#known-issues) and under
[`#[use_type]`](../asts/attributes/use_type.md#known-issues).

## Snapshots

`Enum!` has no `snapshot_*!` macro, since it emits a single type rather than items. Its expansion
is pinned by the type-equality tests listed under Tests.

## Tests

The `shape_macros` target of `cgp-tests` pins the expansion by type equality, and `cgp-macro-tests`
pins the variant parsing and every rejection.

- [shape_macros/enum_basic.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/enum_basic.rs):
  the expansion against `Sum!` and the raw `Either` chain, the empty body as `Void`, a trailing
  comma, and a raw variant name.
- [shape_macros/enum_variant_shapes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/enum_variant_shapes.rs):
  the payload of each variant shape, and the equivalences `V` = `V()` = `V {}` = `V(Nil)`,
  `V { a: u32 }` = `V(Struct! { a: u32 })`, `V(A, B)` = `V(Struct!(A, B))`, and
  `V(T)` = `V(Struct!(T))`, with a `TypeId` check that positional and named payloads differ.
- [shape_macros/enum_derive_parity.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/enum_derive_parity.rs):
  a macro feeds one body to both `#[derive(HasFields)]` and `Enum!` and asserts the types agree,
  across every variant shape, raw names, empty payloads, and an empty enum, plus a generic enum and
  the borrowed `FieldsRef` shape.
- [shape_macros/enum_round_trip.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/enum_round_trip.rs):
  values of an `Enum!` type move through `ToFields` and `FromFields`, and values built by hand from
  `Either` and `Field` rebuild each variant.
- [shape_macros/enum_with_variant_derives.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/enum_with_variant_derives.rs):
  a `#[derive(CgpData)]` enum named by its shape in a bound, agreeing with `FromVariant`.
- [shape_macros/struct_through_macro_rules.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_through_macro_rules.rs)
  and
  [shape_macros/struct_hygiene.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_hygiene.rs):
  variants forwarded through `macro_rules!` fragments, and `Enum!` with no imports.
- [shape_macro_parsing/enum_variants.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/shape_macro_parsing/enum_variants.rs):
  calls the `EnumType` parser directly and asserts each variant keeps its declared shape, an
  empty field list in parentheses or braces included.
- [parser_rejections/enum_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/enum_macro.rs):
  pins the message for a variant attribute, a `pub` variant, a discriminant, a duplicate variant,
  the field rejections inside named and positional variants (a literal and a keyword name
  included), and a field form that contradicts the variant's delimiter.

## Source

- Entry point: `Enum` in
  [cgp-macro-lib/src/enum_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/enum_type.rs),
  registered as the `Enum!` proc macro in
  [cgp-macro/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro/src/lib.rs).
- `EnumType` AST type and its `parse_variant` helper:
  [cgp-macro-core/src/types/shape/enum_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/shape/enum_type.rs),
  documented in [asts/shape.md](../asts/shape.md).
- Field validation: `validate_shape_fields` in
  [cgp-macro-core/src/functions/shape/validate_fields.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/shape/validate_fields.rs).
- Encoder: `variants_to_sum_type` in
  [cgp-macro-core/src/types/cgp_data/derive_has_fields/sum.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/sum.rs).
