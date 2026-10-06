# `#[derive(ExtractField)]`

`#[derive(ExtractField)]` derives just the incremental-extractor machinery for an enum: partial
companion enums plus the `HasExtractor`, `HasExtractorRef`, `HasExtractorMut`, `PartialData`,
`FinalizeExtract`, and `ExtractField` impls that let the enum be matched one variant at a time.

## Purpose

`#[derive(ExtractField)]` gives an enum a type-checked, variant-by-variant extractor without the
rest of the extensible-data machinery. It is the building block that supplies the *deconstruction*
half of a variant: converting a value to an extractor, pulling one variant out at a time, and
carrying the still-unmatched variants forward in a *remainder* whose type shrinks with each attempt.
It exists as a standalone derive for cases where you want the extractor alone, though most code
reaches for [`#[derive(CgpVariant)]`](derive_cgp_variant.md) or
[`#[derive(CgpData)]`](derive_cgp_data.md), which include this output.

The extractor's distinguishing property is that remaining possibilities are tracked in the type. The
derive generates *partial* companion enums whose type parameters record, per variant, whether that
variant is still possible or has been ruled out. Each failed extraction returns a remainder with one
more variant marked impossible; once all are impossible, the remainder is an empty type that can be
discharged unconditionally. This is how a chain of extractions becomes a provably exhaustive match
without a wildcard arm.

The operation is exposed through `ExtractField`, generated per variant, together with `HasExtractor`
(and its borrowed and mutable forms) to obtain an extractor, and `FinalizeExtract` to discharge the
empty remainder.

## Syntax

The derive is applied to an enum and takes no arguments:

```rust
use cgp::prelude::*;

#[derive(ExtractField)]
pub enum Shape {
    Circle(Circle),
    Rectangle(Rectangle),
}
```

Each variant's name becomes a type-level string `Symbol!` used as the variant's `Tag`, and its
payload type becomes its value type. A variant carries either one unnamed payload, as
`Circle(Circle)` does, or no fields at all, written `Closed`, `Closed()`, or `Closed {}`, whose
payload is [`Nil`](../types/cons.md), the empty product [`#[derive(HasFields)]`](derive_has_fields.md)
gives it. A variant with several fields or with named fields is a compile error, and a struct is
rejected with ``expected `enum` ``. Generic parameters on
the enum are carried onto the generated impls. The derive emits the same extractor impls that the variant path of
[`#[derive(CgpData)]`](derive_cgp_data.md) emits: it is that slice in isolation, with no `HasFields`
representation traits and no [`FromVariant`](../traits/from_variant.md) constructors.

## Expansion

`#[derive(ExtractField)]` expands into two partial companion enums and the traits that drive them.
The symbols below are abbreviated as `Symbol!("Name")` in place of the full
`Symbol<Len, Chars<...>>` form. Starting from:

```rust
#[derive(ExtractField)]
pub enum Shape {
    Circle(Circle),
    Rectangle(Rectangle),
}
```

it first emits the owned partial enum `__PartialShape` and the borrowed partial enum
`__PartialRefShape`. Each variant's payload is wrapped in a `MapType` marker, where `IsPresent`
keeps the payload and `IsVoid` maps it to the empty [`Void`](../types/either.md) type; the borrowed
form adds a `MapTypeRef` parameter that selects shared or mutable references:

```rust
pub enum __PartialShape<__F0__: MapType, __F1__: MapType> {
    Circle(<__F0__ as MapType>::Map<Circle>),
    Rectangle(<__F1__ as MapType>::Map<Rectangle>),
}

pub enum __PartialRefShape<'__a__, __R__: MapTypeRef, __F0__: MapType, __F1__: MapType> {
    Circle(<__F0__ as MapType>::Map<<__R__ as MapTypeRef>::Map<'__a__, Circle>>),
    Rectangle(<__F1__ as MapType>::Map<<__R__ as MapTypeRef>::Map<'__a__, Rectangle>>),
}
```

It then emits `PartialData` (both partial enums target `Shape`) and the extractor accessors.
`HasExtractor` yields an owned extractor with every variant present; `HasExtractorRef` and
`HasExtractorMut` yield borrowed extractors over `__PartialRefShape` with `IsRef`/`IsMut`:

```rust
impl HasExtractor for Shape {
    type Extractor = __PartialShape<IsPresent, IsPresent>;
    fn to_extractor(self) -> Self::Extractor {
        match self {
            Self::Circle(value) => __PartialShape::Circle(value),
            Self::Rectangle(value) => __PartialShape::Rectangle(value),
        }
    }
    fn from_extractor(extractor: Self::Extractor) -> Self {
        match extractor {
            __PartialShape::Circle(value) => Self::Circle(value),
            __PartialShape::Rectangle(value) => Self::Rectangle(value),
        }
    }
}

impl HasExtractorRef for Shape {
    type ExtractorRef<'__a__> = __PartialRefShape<'__a__, IsRef, IsPresent, IsPresent> where Self: '__a__;
    fn extractor_ref(&self) -> Self::ExtractorRef<'_> { /* ... */ }
}
// plus HasExtractorMut over __PartialRefShape<'__a__, IsMut, IsPresent, IsPresent>
```

It emits a `FinalizeExtract` impl for the all-`IsVoid` configuration of each partial enum. Because
that configuration is uninhabited, `finalize_extract` can return any type by matching on the empty
value:

```rust
impl FinalizeExtract for __PartialShape<IsVoid, IsVoid> {
    fn finalize_extract<__T__>(self) -> __T__ { match self {} }
}
// plus the borrowed __PartialRefShape<'__a__, __R__, IsVoid, IsVoid>
```

Finally it emits, per variant, an `ExtractField` impl available only when that variant's marker is
`IsPresent`. Calling it returns `Ok(value)` if the runtime value is that variant, or
`Err(remainder)` where the remainder has that variant flipped to `IsVoid`:

```rust
impl<__F1__: MapType> ExtractField<Symbol!("Circle")> for __PartialShape<IsPresent, __F1__> {
    type Value = Circle;
    type Remainder = __PartialShape<IsVoid, __F1__>;
    fn extract_field(self, _: PhantomData<Symbol!("Circle")>) -> Result<Circle, Self::Remainder> {
        match self {
            __PartialShape::Circle(value) => Ok(value),
            __PartialShape::Rectangle(value) => Err(__PartialShape::Rectangle(value)),
        }
    }
}
// plus ExtractField for "Rectangle", and the borrowed variants over __PartialRefShape
```

The `FinalizeExtract` trait itself is defined in the field crate (with blanket impls for `Void` and
`Infallible`); the derive supplies the all-void impl on the partial enums. The companion
`FinalizeExtractResult` trait, also in the field crate, is what `finalize_extract_result` calls to
collapse an `Ok`/empty-`Err` result into the value.

**A variant with no fields carries `Nil` and is matched with braces.** For
`Status { Active(u64), Closed }`, the partial enums hold `Nil` like any payload type, and each
accessor matches `Self::Closed { .. }`, which matches all three empty forms, and fills in a payload,
since the variant has no field to move or borrow:

```rust
// in to_extractor
Self::Closed { .. } => __PartialStatus::Closed(Nil),
// in from_extractor
__PartialStatus::Closed(_) => Self::Closed {},
// in extractor_ref
Self::Closed { .. } => __PartialRefStatus::Closed(&Nil),
// in extractor_mut
Self::Closed { .. } => __PartialRefStatus::Closed(Box::leak(Box::new(Nil))),
```

The shared payload `&Nil` is a promoted constant. Rust does not promote `&mut Nil`, so the mutable
payload leaks a `Box<Nil>`, which never allocates because `Nil` is zero-sized. `Box` is the one name
the expansion takes from the caller's scope, since `cgp` links no `alloc`; see
[Known issues](#known-issues). Every borrowed payload is therefore a reference, as for a newtype
variant, so the borrowed matchers, whose handlers dereference the payload, work on empty variants
too.

The key takeaway is that `to_extractor` yields `__PartialShape<IsPresent, IsPresent>`, each failed
`extract_field` returns a remainder with one more `IsVoid`, and at `__PartialShape<IsVoid, IsVoid>`
the value is uninhabited, so once every variant has been tried, the compiler knows the match is
exhaustive.

## Examples

The extractor is driven through `to_extractor`, a chain of `extract_field` calls, and
`finalize_extract_result` to discharge the impossible remainder:

```rust
use cgp::prelude::*;
use cgp::core::field::traits::FinalizeExtractResult;

#[derive(ExtractField)]
pub enum Shape {
    Circle(Circle),
    Rectangle(Rectangle),
}

fn area(shape: Shape) -> f64 {
    match shape.to_extractor().extract_field(PhantomData::<Symbol!("Circle")>) {
        Ok(circle) => core::f64::consts::PI * circle.radius * circle.radius,
        Err(remainder) => {
            let rect = remainder
                .extract_field(PhantomData::<Symbol!("Rectangle")>)
                .finalize_extract_result();   // remainder is now empty; cannot fail
            rect.width * rect.height
        }
    }
}
```

After the second extraction the remainder type has both markers `IsVoid`, so
`finalize_extract_result` is accepted with no wildcard arm.

## Related constructs

`#[derive(ExtractField)]` is one slice of the variant output of
[`#[derive(CgpData)]`](derive_cgp_data.md) and [`#[derive(CgpVariant)]`](derive_cgp_variant.md);
those derives include it alongside the [`#[derive(FromVariant)]`](derive_from_variant.md)
constructors and [`#[derive(HasFields)]`](derive_has_fields.md) representation traits. Its struct
analogue is [`#[derive(BuildField)]`](derive_build_field.md), the incremental builder. The trait it
generates is the [`ExtractField`](../traits/extract_field.md) trait. The generated code stores
variants in [`sum`](../macros/sum.md)-shaped partial enums ([`Either`/`Void`](../types/either.md))
and switches on the [`MapType`](../traits/map_type.md) markers `IsPresent`/`IsVoid`.

## Known issues

**Five variant names are reserved, and using one fails to compile.** The generated impls name their
associated types through `Self::…` (`Self::Value` in every `ExtractField` impl, `Self::Remainder` in
its return type, and `Self::Extractor`, `Self::ExtractorRef`, and `Self::ExtractorMut` in the three
accessor impls), so a variant called `Value`, `Remainder`, `Extractor`, `ExtractorRef`, or
`ExtractorMut` makes that path ambiguous between the variant and the associated type. The compiler
reports `ambiguous associated item`, and this derive's version of the error is the opaque one in the
family: both the headline *and* the `"… could refer to the variant defined here"` note land on the
`#[derive(ExtractField)]` attribute, so nothing in the output names the variant to rename. The
reason is that these impls are written for the generated `__Partial…` companion enums rather than
for your enum, and the companion's variant identifiers are rebuilt by the codegen, so they carry the
derive's span. The sibling derives collide on your own enum's variants and do point a note at them.
The correct behavior would be for the codegen to write the associated type as
`<Self as ExtractField<Tag>>::Value` rather than `Self::Value`, which would remove the ambiguity;
until then, renaming the variant is the only fix. [`#[derive(HasFields)]`](derive_has_fields.md)
reserves `Fields` and `FieldsRef` for the same reason, so an enum deriving the whole family must
avoid all seven names.

**A partial enum carries none of the enum's own attributes.** The companion enums are generated
without the derives on the original, so a `Result<Value, Remainder>` returned by `extract_field` is
neither `Debug` nor `PartialEq` even when the enum is both, and cannot be compared or printed as a
whole. This mirrors the record side's companion struct.

**A variant attribute that belongs to another derive breaks the build.** The companion enums clear
the enum's attributes but keep each variant's, so a helper attribute such as
`#[serde(rename = "x")]` on a variant lands on `__PartialShape`, which does not derive `Serialize`.
The compiler rejects it with
``cannot find attribute `serde` in this scope``. An enum therefore cannot combine `#[derive(ExtractField)]`, or `CgpVariant` or `CgpData`, with a derive whose variant helper attributes it uses. The correct behavior would be to clear variant attributes on the companion enums as well. The record side has the same defect for field attributes; see [`#[derive(BuildField)]`](derive_build_field.md).

The derive accepts only variants with one unnamed field or no fields. A multi-field variant like
`Pair(A, B)` or a struct-style variant with fields like `Named { x: A }` causes the macro to fail
with `Expected variant to contain exactly one unnamed field, or no fields`. There is no way to opt a
variant out of the requirement, so an enum with such a variant cannot derive the extractor at all;
wrap its fields in a struct to make it a newtype variant.

**A `no_std` crate needs `Box` in scope to derive over a variant with no fields.** The mutable
extractor builds such a variant's `&mut Nil` with `Box::leak(Box::new(Nil))`, writing `Box` bare so
it resolves where the derive is used, because `cgp` links no `alloc` and cannot name `Box` itself.
A `std` crate has `Box` in its prelude. A `no_std` crate without it fails with
``cannot find type `Box` in this scope``, with the caret on the empty variant and a `help` that
suggests the import; `extern crate alloc; use alloc::boxed::Box;` fixes it. The class is recorded
in the error catalog as an
[out-of-scope generated name](../../errors/lowering/out-of-scope-generated-name.md).

## Source

- Entry point: `derive_extract_field` in
  [crates/macros/cgp-macro-lib/src/derive_extract_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/derive_extract_field.rs),
  which builds an `ItemCgpVariant` and calls `to_extract_field_items()`.
- Codegen: that method, in
  [crates/macros/cgp-macro-core/src/types/cgp_data/variant.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/variant.rs),
  composes the helpers in the
  [`derive_extractor/`](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_extractor/)
  submodule (`extractor_enum.rs`, `has_extractor_impl.rs`, `partial_data.rs`,
  `finalize_extract_impl.rs`, `extract_field_impls.rs`).
- Runtime traits: `ExtractField`, `HasExtractor`/`HasExtractorRef`/`HasExtractorMut`,
  `FinalizeExtract`, and `FinalizeExtractResult` in
  [crates/core/cgp-field/src/traits/extract_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/extract_field.rs),
  `PartialData` in `partial_data.rs`, and the `MapType`/`MapTypeRef` markers in
  `crates/core/cgp-field/src/impls/`.
- Internal walkthrough (the extractor helpers, the corner-case handling, and the index of tests and
  expansion snapshots):
  [implementation/entrypoints/derive_extract_field.md](../../implementation/entrypoints/derive_extract_field.md).
