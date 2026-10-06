# `Struct!`: implementation

`Struct!` is a function-like macro that turns the body of a struct declaration into that struct's
type-level `HasFields` shape. This document covers how the macro reads the body and why its
expansion matches `#[derive(HasFields)]` by construction; for the accepted syntax and the full
expansion a user sees, read the reference document
[reference/macros/struct.md](../../reference/macros/struct.md).

## Entry point

The macro is driven by the thin `Struct` function in
[cgp-macro-lib/src/struct_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/struct_type.rs),
which parses the body into a `StructType`, calls its `eval`, and emits the result:

```rust
let struct_type: StructType = parse2(body)?;
Ok(struct_type.eval()?.to_token_stream())
```

Every rejection happens while parsing `StructType`, before any type is built. The AST type and the
helpers it calls are documented in the [`shape` AST stack](../asts/shape.md).

## Pipeline

The macro is a parse-then-`eval` step, the same shape as [`Product!`](product.md). Parsing reads the
body into a `syn::Fields`, the form a struct declaration holds, through `parse_shape_fields`, which
decides between the named and tuple forms and validates the fields. `eval` then hands that
`syn::Fields` to `item_fields_to_product_type`, the encoder
[`#[derive(HasFields)]`](derive_has_fields.md) runs on a struct's own fields.

Reusing the derive's input form is the design choice the rest of the macro follows from. The macro
lowers into the representation the derive already consumes, rather than encoding shapes a second
time, so there is one encoder and the `Struct!` expansion cannot drift from the derived `Fields`.
The same idea, applied to another macro's AST rather than to a derive's input, is the
[lowering pattern](../README.md#lowering-through-another-macros-ir) the extra-feature macros use.

## Generated items

`Struct!` emits a single type, the derive's encoding of the body:

```rust
// Struct! { name: String, age: u8 }
Cons<Field<Symbol!("name"), String>, Cons<Field<Symbol!("age"), u8>, Nil>>

// Struct!(u64, String)
Cons<Field<Index<0>, u64>, Cons<Field<Index<1>, String>, Nil>>
```

A tuple body with exactly one field emits that field's type, an empty body emits `Nil`, and the
encoder emits `Cons`, `Field`, `Index`, and `Nil` through the
[export markers](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/exports.rs).

## Behavior and corner cases

**The form is read from the entries, because the delimiter is not visible.** A procedural macro
receives only the tokens inside its invocation, so `Struct!(a: u8)` and `Struct! { a: u8 }` are the
same input. `parse_shape_fields` classifies each entry on a fork: it skips the entry's attributes
and visibility, so that those reach their own rejection, and then reads the entry as named when an
identifier (or `_`) is followed by a single `:`. The `:` test needs a guard. `syn` peeks
`Token![:]` successfully on the first half of a `::`, so without the `!peek2(Token![::])` check a
path type such as `core::marker::PhantomData<u8>` would be read as a field named `core`. Every entry
must take the form of the first, or the macro reports that the forms are mixed.

**A forwarded `$ty:ty` fragment is classified correctly.** A type passed through a `macro_rules!`
`$ty:ty` fragment arrives wrapped in a token group with no visible delimiter. Such a group never
starts with an identifier followed by `:`, so it is read as a positional field, and a named entry
built from `$name:ident : $ty:ty` keeps its plain identifier and colon.

**The fields are parsed by `syn`'s own struct-body parsers, then checked.** Named entries go through
`Field::parse_named` and positional ones through `Field::parse_unnamed`, the functions `syn` uses
inside a struct declaration, and the result is wrapped in `Fields::Named` or `Fields::Unnamed` with
a default delimiter token. Those parsers accept more than a shape can use, so
`validate_shape_fields` then rejects field attributes (reusing `reject_non_empty_attributes`, which
`delegate_components!` also uses), any visibility, the `_` name (which `parse_named` accepts as part
of its `_: struct { … }` anonymous-field syntax), and duplicate names compared without `r#`.

**Two likely mistakes get their own messages, caught on the same fork.** Without these checks,
both would fail inside `syn`'s type parser with a message listing every token a type may start with,
which names neither mistake:

- **A keyword as a field name.** `peek(Ident)` does not match a keyword, so `Struct! { type: u8 }`
  would be classified as positional. A keyword (peeked with `Ident::peek_any`) followed by a single
  `:` therefore reports `` `type` is a keyword: write the field name as `r#type` ``, or
  `` `self` cannot be a field name `` for the four keywords with no raw form (`self`, `Self`,
  `super`, `crate`).
- **A value in a type position.** After the field name and its colon for a named entry, a literal
  token reports `expected a type: a type-level shape lists field types, not values`, the likely
  mistake of reading `Struct! { a: 1 }` as a struct literal.

**The newtype and empty rules come from the encoder.** `item_fields_to_product_type` returns a
single positional field's type unwrapped and folds an empty field list to `Nil`, so `Struct!(T)` is
`T` and `Struct! {}` is `Nil`, exactly as for a derived struct. An empty body is held as
`Fields::Unit`, which the encoder treats like any empty list.

**Spans follow the derive.** A named field's tag is built with `Symbol::from_ident`, whose
`quote_spanned!` gives the tag's angle brackets, commas, character literals, and length literal the
field name's span. The `Symbol`, `Chars`, and `Nil` paths themselves come from the export markers,
which emit them at the call site. No resolvable reference therefore lands on the field name's
range, so go-to-definition on a field name should not offer those types, though this has not been
checked in an editor. Each field type keeps its own tokens, so a type error inside a field lands on
the type the user wrote. The `Cons` and `Field` wrappers are built with `quote!` and sit at the
invocation's span. The expansion is a single type rather than an impl, so the
[error-span](../README.md#spans-aim-generated-items-at-the-token-the-user-wrote) re-spanning that
item-emitting macros need does not apply.

## Known issues

**An alias imported with `#[use_type]` is not rewritten inside the body.** The substitution visitor
of [`#[use_type]`](../asts/attributes/use_type.md#known-issues) does not descend into macro tokens,
so a bare `Error` inside a `Struct!` is left unresolved. The defect belongs to `#[use_type]` and
affects every type-level macro; it is recorded there.

## Snapshots

`Struct!` has no `snapshot_*!` macro, since it emits a single type rather than items. Its expansion
is pinned by the type-equality tests listed under Tests, which compare it with hand-written lists
and with the derive.

## Tests

The `shape_macros` target of `cgp-tests` pins the expansion by type equality, and `cgp-macro-tests`
pins the form detection and every rejection.

- [shape_macros/struct_named.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_named.rs):
  the named form against `Product!` and the raw `Cons` chain, the empty body, a trailing comma, a
  single named field staying a list, raw identifiers, nesting, compound field types, and generic
  and projected field types.
- [shape_macros/struct_tuple.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_tuple.rs):
  the `Index`-keyed tuple form, the empty tuple body, the newtype rule with and without a trailing
  comma, and path, `dyn`, function-pointer, and `Self` types read as positional fields.
- [shape_macros/struct_delimiter_agnostic.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_delimiter_agnostic.rs):
  each body gives the same type under parentheses, braces, and brackets.
- [shape_macros/struct_derive_parity.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_derive_parity.rs):
  a macro feeds one body to both `#[derive(HasFields)]` and `Struct!` and asserts the types agree,
  across named, tuple, newtype, raw, and empty bodies, plus generic structs and the borrowed
  `FieldsRef` shape.
- [shape_macros/struct_inequality.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_inequality.rs):
  `TypeId` checks that field order, the named versus positional key, and the newtype rule each
  change the type.
- [shape_macros/struct_round_trip.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_round_trip.rs):
  values of a `Struct!` type move through `ToFields` and `FromFields`, and a `product!` value built
  by hand rebuilds the struct.
- [shape_macros/struct_in_signatures.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_in_signatures.rs):
  a shape in bounds, argument and return types, an associated type, an impl self type with the
  brace form, a `UseType` wiring entry, and a `#[cgp_component]`/`#[cgp_impl]` signature whose
  `Self` is rewritten inside the macro body.
- [shape_macros/struct_through_macro_rules.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_through_macro_rules.rs):
  fields forwarded through `$name:ident` and `$ty:ty` fragments keep their form.
- [shape_macros/struct_hygiene.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/struct_hygiene.rs):
  the macros expand in a module with no imports.
- [shape_macros/open_dispatch_key.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/shape_macros/open_dispatch_key.rs):
  a shape in both forms keys an `open` dispatch entry and a `check_components!` entry.
- [shape_macro_parsing/struct_form.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/shape_macro_parsing/struct_form.rs):
  calls the `StructType` parser directly and asserts the form each body is read as, including path
  types beginning with `::` or `a::`.
- [parser_rejections/struct_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/struct_macro.rs):
  pins the message for an attribute, a doc comment, each visibility, the `_` name, a keyword name
  (with and without a raw form), duplicate and raw-duplicate names, both orders of mixed forms, and
  a literal in a type position.

## Source

- Entry point: `Struct` in
  [cgp-macro-lib/src/struct_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/struct_type.rs),
  registered as the `Struct!` proc macro in
  [cgp-macro/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro/src/lib.rs).
- `StructType` AST type:
  [cgp-macro-core/src/types/shape/struct_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/shape/struct_type.rs),
  documented in [asts/shape.md](../asts/shape.md).
- Form detection and validation: `parse_shape_fields` and `validate_shape_fields` in
  [cgp-macro-core/src/functions/shape/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/functions/shape).
- Encoder: `item_fields_to_product_type` in
  [cgp-macro-core/src/types/cgp_data/derive_has_fields/product.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_fields/product.rs).
