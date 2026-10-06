# `ExtractField` and the extractor trait family

The extractor family is the set of traits that let an enum be matched one variant at a time, with
the still-possible variants tracked in the type so that a chain of extractions becomes a provably
exhaustive match without a wildcard arm.

## Purpose

The extractor family solves the problem of deconstructing a sum type generically and exhaustively. A
`match` on a concrete enum names every variant in one place; the extractor instead pulls variants
out one at a time, and each failed attempt narrows the set of remaining possibilities. The narrowing
happens in the type: a failed extraction hands back a *remainder* whose type has one more variant
marked impossible, and once every variant has been ruled out the remainder is an uninhabited type
that can be discharged unconditionally. This is how generic code can match an arbitrary enum,
variant by variant, and have the compiler confirm the match is complete.

The family pairs an accessor that turns a value into an extractor with a per-variant extraction
operation and a finalize step for the empty remainder. `HasExtractor` and its borrowed forms obtain
the extractor; `ExtractField<Tag>` tries one variant and returns either the payload or the shrunken
remainder; `FinalizeExtract` discharges the remainder once it is uninhabited. All but
`FinalizeExtractResult` are in the prelude; it is imported from `cgp::core::field::traits`. The
traits are implemented for an enum by
[`#[derive(ExtractField)]`](../derives/derive_extract_field.md), which generates the partial
companion enums they operate on.

## Definition

The family consists of three accessor traits, the extraction operation, and two finalize traits. The
accessors turn a value into an extractor in one of three ownership modes, owned, shared-reference,
and mutable-reference:

```rust
pub trait HasExtractor {
    type Extractor;
    fn to_extractor(self) -> Self::Extractor;
    fn from_extractor(extractor: Self::Extractor) -> Self;
}

pub trait HasExtractorRef {
    type ExtractorRef<'a> where Self: 'a;
    fn extractor_ref(&self) -> Self::ExtractorRef<'_>;
}

pub trait HasExtractorMut {
    type ExtractorMut<'a> where Self: 'a;
    fn extractor_mut(&mut self) -> Self::ExtractorMut<'_>;
}
```

`ExtractField<Tag>` is the extraction operation. It attempts to read the variant named by `Tag` out
of the extractor, returning `Ok(value)` if the runtime value is that variant or `Err(remainder)` if
it is not, where the remainder is the same extractor with that one variant ruled out:

```rust
pub trait ExtractField<Tag> {
    type Value;
    type Remainder;
    fn extract_field(self, _tag: PhantomData<Tag>) -> Result<Self::Value, Self::Remainder>;
}
```

`FinalizeExtract` discharges a remainder that has become uninhabited. Its method returns any type,
which is sound because no value exists to call it on. It is implemented for the empty
[`Void`](../types/either.md) type and for `Infallible`, both by matching on the empty value:

```rust
pub trait FinalizeExtract {
    fn finalize_extract<T>(self) -> T;
}

impl FinalizeExtract for Void {
    fn finalize_extract<T>(self) -> T { match self {} }
}

impl FinalizeExtract for Infallible {
    fn finalize_extract<T>(self) -> T { match self {} }
}
```

`FinalizeExtractResult` is the convenience wrapper that collapses the `Result` produced by the last
extraction. It is implemented for any `Result<T, E>` whose error half implements `FinalizeExtract`,
returning the `Ok` value and discharging the `Err`:

```rust
pub trait FinalizeExtractResult {
    type Output;
    fn finalize_extract_result(self) -> Self::Output;
}

impl<T, E> FinalizeExtractResult for Result<T, E>
where E: FinalizeExtract {
    type Output = T;
    fn finalize_extract_result(self) -> T {
        match self {
            Ok(value) => value,
            Err(remainder) => remainder.finalize_extract(),
        }
    }
}
```

## Behavior

Extraction proceeds variant by variant against a shrinking remainder until that remainder is
uninhabited. The derive generates a partial companion enum with one [`MapType`](map_type.md)
parameter per variant; the marker in each position decides whether that variant's payload is present
(`IsPresent`) or has been mapped to the empty `Void` type (`IsVoid`). `to_extractor` starts the
chain at the all-`IsPresent` configuration, where every variant is still possible. Each
`extract_field` call is available only when the requested variant's marker is `IsPresent`; it
matches on the value, returning the payload if it is that variant, or returning the remainder with
that one marker flipped to `IsVoid` if it is not.

Exhaustiveness is proven at the type level rather than by a wildcard. As variants are ruled out, the
remainder's markers turn to `IsVoid` one by one, and `IsVoid` maps each payload slot to `Void`. When
every marker is `IsVoid`, every arm of the partial enum holds a `Void`, so the whole type is
uninhabited. The derive supplies a `FinalizeExtract` impl on exactly that all-`IsVoid`
configuration, which is sound only because the value cannot exist: `match self {}` has no arms to
write. A caller therefore reaches `finalize_extract` (directly, or through `finalize_extract_result`
on the last `Result`) only after trying every variant, and the compiler accepts the discharge with
no wildcard arm.

The three accessor traits differ only in ownership. `HasExtractor` consumes the value and yields an
owned extractor whose payloads are owned; the `from_extractor` method reverses `to_extractor` for an
unmatched value, as a plain variant-for-variant `match`. `HasExtractorRef` and `HasExtractorMut`
borrow the value and yield a borrowed extractor over a *second* companion enum,
`__PartialRef{Name}`, which carries a lifetime and a `MapTypeRef` marker (`IsRef` or `IsMut`) that
maps each payload slot to a shared or mutable reference, so a value can be matched without being
moved. The derive emits the per-variant `ExtractField` impls and the all-`IsVoid` `FinalizeExtract`
impl on that enum too, generic over the `MapTypeRef` marker, so a borrowed chain narrows and
finalizes exactly as an owned one does. Both companions implement [`PartialData`](has_builder.md)
with `Target` naming the original enum.

`cargo cgp expand` on a two-variant `Shape { Circle(Circle), Rectangle(Rectangle) }` shows the two
companions and the `Circle` extraction:

```rust
pub enum __PartialShape<__F0__: MapType, __F1__: MapType> {
    Circle(<__F0__ as MapType>::Map<Circle>),
    Rectangle(<__F1__ as MapType>::Map<Rectangle>),
}
pub enum __PartialRefShape<'__a__, __R__: MapTypeRef, __F0__: MapType, __F1__: MapType> {
    Circle(<__F0__ as MapType>::Map<<__R__ as MapTypeRef>::Map<'__a__, Circle>>),
    Rectangle(<__F1__ as MapType>::Map<<__R__ as MapTypeRef>::Map<'__a__, Rectangle>>),
}
impl<__F1__: MapType> ExtractField<Symbol!("Circle")>
for __PartialShape<IsPresent, __F1__> {
    type Value = Circle;
    type Remainder = __PartialShape<IsVoid, __F1__>;
    fn extract_field(
        self,
        _tag: ::core::marker::PhantomData<Symbol!("Circle")>,
    ) -> Result<Self::Value, Self::Remainder> {
        match self {
            __PartialShape::Circle(value) => Ok(value),
            __PartialShape::Rectangle(value) => Err(__PartialShape::Rectangle(value)),
        }
    }
}
```

`HasExtractorRef` for `Shape` sets `ExtractorRef<'a>` to
`__PartialRefShape<'a, IsRef, IsPresent, IsPresent>`, and `HasExtractorMut` sets `ExtractorMut<'a>`
to the same enum with `IsMut`.

### Where each mistake surfaces

Every misuse of a chain is a compile error, and the messages name the partial types rather than the
mistake, so each is worth recognizing by shape. On the `Shape` above:

```rust
// Extracting `Circle` again from the remainder of a failed `Circle` attempt.
if let Err(remainder) = shape.to_extractor().extract_field(PhantomData::<Symbol!("Circle")>) {
    let _ = remainder.extract_field(PhantomData::<Symbol!("Circle")>);
}

// Finalizing with `Circle` still possible, directly and through the `Result`.
match shape.to_extractor().extract_field(PhantomData::<Symbol!("Rectangle")>) {
    Ok(rect) => rect.width,
    Err(remainder) => remainder.finalize_extract(),
}
let rect = shape
    .to_extractor()
    .extract_field(PhantomData::<Symbol!("Rectangle")>)
    .finalize_extract_result();
```

Extracting a variant twice is `error[E0308]: mismatched types`, labelled
``expected `9`, found `6` ``: with only the `Rectangle` impl left applicable, rustc settles on it and
reports the tag argument, the numbers being the two names' lengths in their `Symbol` types. A
three-variant enum leaves two impls, so the same mistake is reported differently there. Finalizing
early directly is
``error[E0599]: no method named `finalize_extract` found for enum `__PartialShape<__F0__, __F1__>` ``,
labelled ``method not found in `__PartialShape<IsPresent, IsVoid>` ``, so the marker still
`IsPresent` is the variant left to try. Through the `Result` it is
``error[E0599]: the method `finalize_extract_result` exists for enum `Result<Rectangle, __PartialShape<IsPresent, IsVoid>>`, but its trait bounds were not satisfied``,
noting ``__PartialShape<IsPresent, IsVoid>: FinalizeExtract``. Calling `finalize_extract_result`
without importing `FinalizeExtractResult` is
``error[E0599]: no method named `finalize_extract_result` found for enum `Result<T, E>` ``, with a
help line naming the trait to import. And comparing a whole extraction result,
`assert_eq!(shape.to_extractor().extract_field(PhantomData::<Symbol!("Circle")>), Ok(circle))`, fails
with `E0369` (``binary operation `==` cannot be applied to type `Result<Circle, __PartialShape<IsVoid, IsPresent>>` ``)
and `E0277` (``doesn't implement `Debug` ``), because the companions carry none of the enum's derives.

### Using the family, and where it stops

The family is for code that handles one variant each independently, or that cannot name the enum; a
concrete `match` is shorter, clearer, already exhaustive, and generates nothing, and `matches!` or
`if let` answers which variant a value holds. Hand-written chains are rare in practice: the
[dispatch combinators](../providers/dispatch_combinators.md) generate the chain from the enum's own
variant list, which also keeps "add a variant" from breaking every call site, since a hand-written
chain stops compiling the moment the final remainder becomes inhabited again. That breakage is the
guarantee, not a defect.

Pick the weakest accessor that works: `extractor_ref` for reading, `extractor_mut` for changing a
payload in place (the value stays mutably borrowed while the extractor or a payload from it lives),
and `to_extractor` only when a payload must be moved out. A borrowed chain cannot move a payload out,
and neither borrowed accessor has a `from_extractor`, which is rarely missed since the value was never
consumed; `from_extractor` itself accepts only the all-possible extractor, so a narrowed one has no
way back. An extractor type is a generated companion, so a signature returning `Self::Extractor` exposes a
generated name in a public API. The owned and borrowed extractors are different enums, so code generic over "an extractor"
is generic over the extractor type with `ExtractField` bounds, and a signature holding an
`ExtractorRef<'a>` or `ExtractorMut<'a>` usually spells its lifetime out. Extractions may be written in
any order, since each step moves only its own variant's marker, but every variant must be tried
before the remainder finalizes. Absence is `IsVoid` here and `IsNothing` in a builder; the two are not
interchangeable, and an error naming the wrong one usually means record and variant machinery have
been crossed.

`FinalizeExtractResult`'s bound is on the `Result`'s error type alone, so it also collapses any
`Result` whose error is `Infallible` or `Void`, which occasionally resolves where a reader did not
expect it. It returns the `Ok` value with no runtime branch left to fail.

## Examples

The family is normally driven through `to_extractor`, a chain of `extract_field` calls, and
`finalize_extract_result` to discharge the impossible remainder at the end:

```rust
use cgp::prelude::*;
use cgp::core::field::traits::FinalizeExtractResult;

pub struct Circle {
    pub radius: f64,
}

pub struct Rectangle {
    pub width: f64,
    pub height: f64,
}

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
                .finalize_extract_result();
            rect.width * rect.height
        }
    }
}
```

The first failed extraction returns a remainder with `Circle` ruled out. After the second, both
markers are `IsVoid`, so its type is uninhabited and `finalize_extract_result` is accepted with no
wildcard arm. Adding a third variant to `Shape` would make this function fail to compile until the
new variant is handled, because the remainder after two extractions would no longer be uninhabited.

## Related constructs

The enum-side derive that generates the partial enums and all these impls is
[`#[derive(ExtractField)]`](../derives/derive_extract_field.md), whose doc shows the exact expanded
code. The presence markers `IsPresent` and `IsVoid` are [`MapType`](map_type.md) implementations,
and the empty remainder bottoms out in the [`Void`](../types/either.md) type that anchors the sum
list. The construction counterpart, which puts a variant *into* an enum rather than taking one out,
is [`FromVariant`](from_variant.md). The struct analogue of the whole family is the builder family
in [`has_builder`](has_builder.md), which assembles a record field by field instead of
deconstructing a variant. The conceptual overview that frames this family is
[extensible variants](../../concepts/extensible-variants.md), worked through in the
[expression interpreter](../../../examples/expression-interpreter.md) example.

## Known issues

The partial companion enum keeps the original enum's variant attributes, so a helper attribute
belonging to another derive, such as `#[serde(rename = "x")]`, fails to compile on the companion
with
``cannot find attribute `serde` ``. See [`#[derive(ExtractField)]`](../derives/derive_extract_field.md#known-issues).

**The borrowed extractor accepts only `'static` enums in a bound for every lifetime.** A bound such
as `for<'a> E::ExtractorRef<'a>: …` fails for an enum with a lifetime, such as
`Token<'a> { Word(&'a str), Number(u64) }`, with `E0477`, for the same reason as
[`HasFieldsRef`](has_fields.md#known-issues): `ExtractorRef<'a>` declares `where Self: 'a`. Getting
the extractor some other way does not help, because the derived partial enum itself carries the
requirement: `__PartialRefToken<'__a__, 'a: '__a__, …>` declares that the enum's lifetime outlives
the borrow, and each payload is wrapped in `MapTypeRef::Map<'a, T: 'a>`. The by-reference
dispatchers do not need the bound for every lifetime: they take their input as `&'a Input`, which
makes `'a` a parameter of the impl, and the type `&'a Input` itself implies `Input: 'a`.

## Source

- The traits `ExtractField`, `HasExtractor`, `HasExtractorRef`, `HasExtractorMut`,
  `FinalizeExtract`, and `FinalizeExtractResult` are all defined in
  [crates/core/cgp-field/src/traits/extract_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/extract_field.rs),
  with `PartialData` in
  [partial_data.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/partial_data.rs).
- The `MapType` markers are in
  [crates/core/cgp-field/src/impls/map_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/map_type.rs)
  and the `MapTypeRef` markers in
  [map_type_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/map_type_ref.rs).
- For how it is generated and the index of tests, see the implementation document
  [implementation/entrypoints/derive_extract_field.md](../../implementation/entrypoints/derive_extract_field.md).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **6 pages**
rather than one:
[`extract_field`](https://contextgeneric.dev/docs/reference/traits/variant/extract_field),
[`has_extractor`](https://contextgeneric.dev/docs/reference/traits/variant/has_extractor),
[`has_extractor_ref`](https://contextgeneric.dev/docs/reference/traits/variant/has_extractor_ref),
[`has_extractor_mut`](https://contextgeneric.dev/docs/reference/traits/variant/has_extractor_mut),
[`finalize_extract`](https://contextgeneric.dev/docs/reference/traits/variant/finalize_extract),
[`finalize_extract_result`](https://contextgeneric.dev/docs/reference/traits/variant/finalize_extract_result).
A change here is propagated to each of them, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping and the granularity
rule behind it are recorded in [website/site-structure.md](../../../website/site-structure.md).
