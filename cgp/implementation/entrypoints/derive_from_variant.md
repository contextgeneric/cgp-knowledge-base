# `#[derive(FromVariant)]` — implementation

`#[derive(FromVariant)]` emits just the variant-construction slice of the variant machinery: one `FromVariant` impl per variant, so an enum can be built generically from any single variant addressed by a type-level tag. This document covers how that codegen works; for the accepted syntax and the full expansion, read the reference document [reference/derives/derive_from_variant.md](../../reference/derives/derive_from_variant.md).

## Entry point

The macro is driven by the `derive_from_variant` function in [cgp-macro-lib/src/derive_from_variant.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/derive_from_variant.rs). It parses the input into a `syn::ItemEnum`, wraps it in an `ItemCgpVariant`, and calls `to_from_variant_impls` — the same method the enum path of `#[derive(CgpData)]` uses for its constructor slice:

```rust
let variant = ItemCgpVariant { item_enum };
let item_impls = variant.to_from_variant_impls()?;
```

Applying the derive to a non-enum item fails at `syn::parse2`.

## Pipeline

There is no multi-stage transform. `ItemCgpVariant::to_from_variant_impls` forwards to the single codegen helper `derive_from_variant_from_enum`, which walks the enum's variants and emits one constructor impl each. The [`cgp_data` AST stack](../asts/cgp_data.md) documents `ItemCgpVariant` and the `Symbol` field-tag type.

## Generated items

The derive emits one [`FromVariant`](../../reference/traits/from_variant.md) impl per variant and nothing else — no companion type and no presence tracking, making it the simplest derive in the family. Each impl is keyed by the [`Symbol!`](../../reference/macros/symbol.md) of the variant's name, takes the variant's payload as the associated `Value`, and wraps it in the variant:

```rust
impl FromVariant<Symbol!("Circle")> for Shape {
    type Value = Circle;
    fn from_variant(_tag: PhantomData<Symbol!("Circle")>, value: Self::Value) -> Self { Self::Circle(value) }
}
```

The `PhantomData<Tag>` argument exists only to let a caller select which variant to build when several `FromVariant` impls are in scope. The `FromVariant` trait itself is defined in the field crate; the derive supplies only the per-variant impls.

## Behavior and corner cases

The enum's generic parameters are threaded onto every impl. This derive emits no `HasFields` representation impls and no extractor — those come from [`#[derive(HasFields)]`](derive_has_fields.md) and [`#[derive(ExtractField)]`](derive_extract_field.md); `FromVariant` is purely the construction slice, included wholesale by [`#[derive(CgpVariant)]`](derive_cgp_variant.md) and [`#[derive(CgpData)]`](derive_cgp_data.md).

## Error spans

Each per-variant impl is re-spanned onto the variant it constructs, so a coherence conflict (`E0119`) with a hand-written `FromVariant` impl lands its caret on the variant the user wrote rather than on the whole `#[derive(FromVariant)]`. `derive_from_variant_from_enum` passes each finished impl through [`override_item_span`](../README.md#spans-aim-generated-items-at-the-token-the-user-wrote), moving only the `impl`/`{ … }` boundary — the mechanism the [`#[derive(HasField)]`](derive_has_field.md#error-spans) doc explains in full.

## Known issues

**The codegen names the payload type as `Self::Value`, so a variant called `Value` makes the expansion invalid.** `derive_from_variant_from_enum` writes the `from_variant` parameter as `value: Self::Value`, and inside an impl for an enum that path can resolve to either the trait's associated type or a variant of the same name — so `rustc` rejects the expansion with `ambiguous associated item`, with its headline on the derive attribute and a `note` pointing at the user's own variant — because the impl is written `for` the user's enum, the colliding variant keeps its own span and the error stays actionable, unlike the extractor's. Writing the projection as `<Self as FromVariant<Tag>>::Value` would remove the ambiguity, and doing so is the fix; the interpolated `#variant_type` on the `type Value =` line is already unambiguous, so only the parameter's type needs changing. [`#[derive(ExtractField)]`](derive_extract_field.md#known-issues) has the same defect across five names and [`#[derive(HasFields)]`](derive_has_fields.md) across two, so an enum deriving the whole family has seven names it cannot use. Pinned by [invalid_expansion/reserved_variant_names.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/invalid_expansion/reserved_variant_names.rs).

Like the extractor derive, `#[derive(FromVariant)]` requires every variant to be a single-unnamed-field tuple variant. A fieldless, multi-field, or struct-style variant makes the macro fail with "Expected variant to contain exactly one unnamed field," with no per-variant opt-out. The requirement is described alongside the extractor's in [`derive_extract_field`](derive_extract_field.md#known-issues), and the reference document records its user-visible form.

## Snapshots

`snapshot_derive_from_variant!` pins this derive's output on its own, and because the derive emits nothing but the per-variant impls, that snapshot is the whole of it:

- [extensible_variants/from_variant_derive.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_variants/from_variant_derive.rs) — two variants, showing the constructor slice with no companion type and no presence tracking.

The same impls also appear inside the variant expansion pinned by the `snapshot_derive_cgp_data!` snapshots indexed in [derive_cgp_data.md's Snapshots section](derive_cgp_data.md#snapshots), which is where the generic and variantless enum shapes are covered.

## Tests

- [from_variant_derive.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_variants/from_variant_derive.rs) calls `from_variant` from a function generic over the tag, which is the capability the derive exists for and which a concrete `Shape::Circle(..)` call site cannot express.
- The behavioral variant tests in [crates/tests/cgp-tests/tests/extensible_variants/](https://github.com/contextgeneric/cgp/tree/main/crates/tests/cgp-tests/tests/extensible_variants/) — notably [variant_dispatch.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/extensible_variants/variant_dispatch.rs) — construct enums through the generated `from_variant`.
- [parser_rejections/derive_from_variant.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/derive_from_variant.rs) pins the single-unnamed-field requirement: the derive rejects a fieldless, a multi-field, and a struct-style variant.
- [invalid_expansion/reserved_variant_names.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/invalid_expansion/reserved_variant_names.rs) pins the reserved-variant-name defect recorded under Known issues, capturing the emitted `Self::…` paths as a string snapshot so the test compiles even though the code it describes would not.

## Source

- Entry point: `derive_from_variant` in [cgp-macro-lib/src/derive_from_variant.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/derive_from_variant.rs).
- Codegen: `ItemCgpVariant::to_from_variant_impls` in [cgp-macro-core/src/types/cgp_data/variant.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/variant.rs), which delegates to `derive_from_variant_from_enum` in [cgp-macro-core/src/types/cgp_data/derive_from_variant.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_from_variant.rs); the AST types are documented in [asts/cgp_data.md](../asts/cgp_data.md).
- The `FromVariant` trait is defined in [crates/core/cgp-field/src/traits/from_variant.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/from_variant.rs).
