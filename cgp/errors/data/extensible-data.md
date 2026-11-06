# Extensible data

An operation on an extensible record or enum (a builder, an extractor, a cast, or a provider that
builds or matches one) is applied to a value whose fields or variants are not in the state the
operation needs, or to a type that lacks the data derive it needs, so the compiler rejects a bound on
a generated partial type (`E0277`, `E0271`, `E0599`, or `E0308`).

## What triggers it

CGP's extensible-data operations track each field's or variant's state in a type. A data derive
generates a **partial** companion for each struct and enum, `__PartialPerson<F0, F1>` for a
`Person { first_name, last_name }`, with one [`MapType`](../../reference/traits/map_type.md) marker
parameter per field or variant: `IsPresent` for a field a builder holds or a variant an extractor
may still yield, `IsNothing` for a field not yet set, `IsVoid` for a variant ruled out, and
`IsOptional` for a field an optional builder holds as an `Option`. Every
[builder](../../reference/traits/has_builder.md) and
[extractor](../../reference/traits/extract_field.md) operation, and every
[cast](../../reference/traits/cast.md) built on them, is implemented only for the marker
configurations where it is valid, so an operation applied in the wrong state has no impl. The
failure is an [acceptable](../../implementation/AGENTS.md#documenting-how-a-macros-expansion-can-fail-to-compile)
one: the derive cannot know which operations the program will apply, and the compiler checks each one
against the state the program reaches. The shapes differ in which state is wrong.

### A field set twice, or taken before it is set

A builder accepts a field only while it is unset, and gives one back only once it is set:

```rust
#[derive(CgpData)]
pub struct Person {
    pub first_name: String,
    pub last_name: String,
}

let _ = Person::builder()
    .build_field(PhantomData::<Symbol!("first_name")>, "Alice".to_owned())
    .build_field(PhantomData::<Symbol!("first_name")>, "Bob".to_owned()); // set twice
```

The same mistake reaches a builder through a merge: `build_from` copies every field of its source,
so two sources that share a field set it twice, and a `BuildWithHandlers` list with two steps for
one field does the same. An optional builder's `set` has the matching rule: it needs the field held
as optional, which a core builder from `builder()` never does until `to_optional()` converts it.

### A field the struct does not declare

`build_field` for a field the struct lacks, or a `build_from` or `BuildAndMergeOutputs` source that
carries a field the target lacks (often a field renamed on one side), names a field the builder has
no slot for.

### A builder finalized too early

`finalize_build` is implemented only once every field is set, so a builder finalized with a field
unset fails, and so does a `BuildWithHandlers` list without a step for one field.

### A variant extracted twice, or a match left incomplete

An extractor yields each variant once, and its remainder finalizes only once every variant is ruled
out. Extracting a variant from a remainder that already ruled it out fails, as does finalizing a
remainder that may still hold a variant, the mistake a `MatchWithHandlers` list without an arm for
one variant makes:

```rust
delegate_components! {
    App {
        ComputerComponent: MatchWithHandlers<
            Product![ExtractFieldAndHandle<Symbol!("Circle"), HandleFieldValue<ComputeArea>>],
        >, // no arm for `Shape::Rectangle`
    }
}
```

### Casts between enums that do not match

An upcast needs every variant of the source in the target, and a downcast every variant of the
target in the source, each with the same payload type. A variant one side lacks, or a variant whose
payload type differs, has no conversion:

```rust
#[derive(CgpData)]
pub enum Small {
    Foo(u64),
    Bar(String),
}

#[derive(CgpData)]
pub enum Big {
    Foo(u64), // no `Bar`
}

let _: Big = Small::Foo(1).upcast(PhantomData::<Big>);
```

Constructing an enum by a tag it lacks (`Shape::from_variant(PhantomData::<Symbol!("circle")>, …)`)
fails the same way. So does calling `downcast` on the remainder an earlier downcast returns: the
remainder is an extractor, not the enum, and an extractor takes `downcast_fields`.

### A missing data derive, or a missing `Default`

Each operation needs the traits a derive supplies: `HasFields` (from `#[derive(HasFields)]`) to walk
a shape, `HasExtractor` (from `#[derive(ExtractField)]`) to match an enum, `HasBuilder` (from
`#[derive(BuildField)]`) to build a struct. An operation on a type without the derive fails, whether
it is called directly (`upcast`, `build_from` from a source without `HasFields`), required by a
provider's bound, or required by a `#[cgp_auto_dispatch]` trait called on an enum without
`#[derive(CgpData)]`. The defaulted operations (`build_with_default`, `finalize_with_default`) also
need `Default` for every field they leave unset.

### A view of every lifetime on a borrowed enum

A bound that needs a borrowed view of an enum's fields for every lifetime
(`for<'b> Value::FieldsRef<'b>: Debug`) holds only for an enum that outlives every borrow, which an
enum with a lifetime parameter does not, as [`HasFieldsRef`](../../reference/traits/has_fields.md)
records under its Known issues.

## The raw diagnostic

The compiler reports the bound the operation could not satisfy, on the generated partial type, so
the message names the operation's trait and the marker list rather than the mistake. This is a
surfaced class in that the cause is encoded in the output, but it is never stated. Its shapes:

- **`E0271` on a builder's marker**: a field set twice or taken while unset reads
  ``type mismatch resolving `<__PartialPerson<…> as UpdateField<…>>::Mapper == IsNothing` ``, with
  ``note: expected this to be `IsNothing` `` on the derive.
- **`E0277` on a partial type**: a missing field reads
  ``the trait bound `__PartialEmployee<IsPresent, IsNothing>: UpdateField<…>` is not satisfied``,
  followed by the `UpdateField` impls that exist, one per declared field; an incomplete match reads
  ``the trait bound `__PartialShape<IsVoid, IsPresent>: FinalizeExtract` is not satisfied``, with a
  help naming the configuration that does implement it; a cast's missing variant reads
  ``the trait bound `Big: FromVariant<Symbol<3, …>>` is not satisfied``.
- **`E0599`**: a finalize too early reads "no method named `finalize_build` found", labelled with the
  partial type, and a missing derive reads "the method `upcast` exists for enum `Small`, but its
  trait bounds were not satisfied", with a note that `HasFields` must be implemented.
- **`E0308`**: a variant extracted twice is a mismatched argument type, labelled with the two tags'
  lengths (``expected `9`, found `6` ``), because the remainder's only applicable `ExtractField` impl
  is for the other variant.

Field and variant names appear as `Symbol<N, Chars<…>>` spines, elided behind a long-type file. Stable
`rustc` and the nightly `cargo-cgp` pins can report one mistake at different bounds: through a check
the stable compiler may stop at the provider (`BuildAndSetField<…>: Computer<…>` for a field set
twice), a merge's stray field is an `UpdateField` bound on stable and a `FieldsBuilder` bound on the
nightly, and `build_with_default` with an unset field names `Port: Default` on stable and only the
`CanFinalizeWithDefault` bound on the nightly.

## Where the root cause is

The cause is in the partial type's marker list and the tag of the failing bound. The markers follow
the struct's fields or the enum's variants in declaration order, so
`__PartialPerson<IsPresent, IsNothing>` says `first_name` is set and `last_name` is not, and the tag
(`Symbol<10, …>`, decoded as `first_name`) names the field the operation wanted. A reader who knows the encoding can recover the
mistake, but no line states it. Two shapes carry less: an `E0599` "no method named" names only the
method and the partial type, and a missing `Default` on the nightly names no field at all.

## How cargo-cgp presents it

The tool's walk descends CGP's extensible-data traits and reads the presence markers, so a failure it
resolves states the field or variant at fault (see
[Typed resolution: leaves and labels](../../../cargo-cgp/implementation/typed-resolution/leaves.md#decoding-classifying-and-rendering-a-leaf)).
Each cause has its own tree code in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md):

- `[CGP-E118]`: ``field `host` of `Config` is already set``.
- `[CGP-E119]`: ``field `port` of `Config` is not set``.
- `[CGP-E120]`: ``missing variant `Bar` on `Big` ``.
- `[CGP-E121]`: ``variant `Rectangle` of `Shape` is not extracted``.
- `[CGP-E122]`: ``variant `Foo` on `FooBarBaz` has type `u32`, but `u64` is required``.
- `[CGP-E123]`: `` `Shape` does not implement `HasFields` ``.
- `[CGP-E124]`: ``variant `Circle` of `Shape` is already extracted``.
- `[CGP-E125]`: ``field `foo` of `Context` is not optional``.
- `[CGP-E126]`: `` an extractor of `FooBarBaz` does not implement `HasExtractor` ``, for a builder
  or an extractor given where its struct or enum belongs.
- `[CGP-E110]`: ``missing field `timeout` on `App` ``, the ordinary missing-field leaf, for a field
  a builder operation names that the struct lacks.
- `[CGP-E117]`: ``the trait bound `Port: Default` is not satisfied``, the ordinary bound a defaulted
  finalize needs for a field left unset.

The headline states the cause after the code its anchor gives:

- **Through a check or a consumer call**, the block keeps the consumer class
  (``[CGP-E001] field `port` of `Config` is not set``), its tree running through the builder or
  matcher provider to the cause.
- **A call to one of CGP's data operations** takes the extensible-data class:
  ``[CGP-E050] missing variant `Bar` on `Big` ``. The call may be made on a constructed value, on a
  builder or an extractor that a chain of data operations produced
  (`Person::builder().build_field(…)`), on a remainder a pattern binds (`Err(remainder)`), or by a
  type-relative path (`Server::build_with_default(…)`): the tool types the value through the
  operations that built it. This covers the shapes rustc reports before the operation's bounds are
  checked, an `E0599` "no method named `finalize_build`" and an `E0308` on the tag of a variant
  extracted twice.
- **A `#[cgp_auto_dispatch]` call** on an enum without the derive keeps the blanket-trait class:
  ``[CGP-E003] `Shape` does not implement `HasFields` and `HasExtractor` ``.

A missing derive gets a `help` naming it, the traits one type lacks merged into one attribute
(`` add `#[derive(HasFields, ExtractField)]` to `Shape` ``), and a missing variant gets a near miss
when the enum has a similar one. A builder or extractor in the wrong place, and a field an optional
builder's `set` needs optional, get a `help` naming the method to call with the `use` its trait
needs, since the data traits are not in the prelude
(`` call `downcast_fields` in place of `downcast` on an extractor, with `use cgp::core::field::impls::CanDowncastFields;` in scope ``).
The tree names a builder or an extractor in words, as in
``trait impl `BuildField<Symbol!("host")>` for the builder of `Config` with `host` and `port` set``,
though a provider step whose input is a partial value still shows its generated type, and the
defaulted finalize's chain names the internal `TransformMapDefault` transform. A matcher's provider
method called directly through its path takes the provider class, as
``[CGP-E002] variant `Rectangle` of `Shape` is not extracted``. The lifetime shape passes through as
rustc wrote it.

## Resolving it

Each shape has its own fix, named by the cause:

- **A field set twice**: drop one of the two settings, or one source's copy of the field.
- **A field not set**: set it before the operation, or add a step for it to the builder list.
- **A field the struct lacks**: add it to the struct, or rename it on the side that misspells it.
- **A variant left unextracted**: extract it before finalizing, or add an arm for it to the matcher.
- **A cast that does not match**: add the missing variant, align the payload types, or cast to an
  enum whose variants match.
- **A variant extracted twice**: handle the variant where it was first extracted, or extract
  another one from the remainder.
- **A field an optional builder needs optional**: call `to_optional()` on the builder first, or set
  the field with `build_field`.
- **A builder or an extractor in the wrong place**: call the operation it takes, as the `help`
  names (`downcast_fields` on a remainder).
- **A missing derive**: add the derive the `help` names; `#[derive(CgpData)]` supplies all of them.
- **A missing `Default`**: implement `Default` for the field's type, or set the field before the
  defaulted finalize.

## Notes for tooling

The tool types a data operation's value from the operations' signatures, since the emitter cannot
read typeck results (see
[Typed resolution: the call-site anchor](../../../cargo-cgp/implementation/typed-resolution/call-site.md#calls-to-extensible-data-operations)).
A value that does not come from a data operation, a constructor, a literal, or a binding the tool
reads (a field access, a generic function's result) stays untyped, and so does a tag written with a
computed const argument (`Index<{ 0 + 0 }>`), so such a call passes through as rustc wrote it. A
call by a name a data operation shares (`builder`, `set`) is read as one only when the data trait is
in scope at the call, as the compiler's own method lookup requires.

## Backing fixtures

These fixtures pin the class, one group per shape:

- [`data/extensible-data/build_field_twice.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_field_twice.rs):
  a `build_field` chain setting `first_name` twice; `[CGP-E050]` over `[CGP-E118]`.
- [`data/extensible-data/build_field_twice_braced_tag.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_field_twice_braced_tag.rs)
  and
  [`build_field_twice_computed_tag.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_field_twice_computed_tag.rs):
  a tuple struct's field set twice through `Index<{ 0 }>`, `[CGP-E050]` over `[CGP-E118]`, and
  through the computed `Index<{ 0 + 1 }>`, whose tag the tool does not read, so rustc's `E0271`
  stays.
- [`data/extensible-data/builder_field_set_twice.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/builder_field_set_twice.rs):
  a `BuildWithHandlers` list setting `host` twice, behind a check; `[CGP-E118]`.
- [`data/extensible-data/build_from_overlapping_sources.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_from_overlapping_sources.rs):
  two `build_from` sources sharing `bar`; `[CGP-E050]` over `[CGP-E118]`.
- [`data/extensible-data/take_field_absent.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/take_field_absent.rs):
  `take_field` on an empty builder; `[CGP-E050]` over `[CGP-E119]`.
- [`data/extensible-data/set_optional_on_core_builder.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/set_optional_on_core_builder.rs):
  `set` on a builder that is not optional; `[CGP-E050]` over `[CGP-E125]`, with the
  `to_optional` `help`.
- [`data/extensible-data/build_field_unknown.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_field_unknown.rs):
  `build_field` for a field `Person` lacks; `[CGP-E050]` over `[CGP-E110]`.
- [`data/extensible-data/build_from_field_not_in_target.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_from_field_not_in_target.rs):
  a `build_from` source carrying `surname`, which the target lacks; `[CGP-E050]` over
  `[CGP-E110]`.
- [`data/extensible-data/build_and_merge_extra_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_and_merge_extra_field.rs)
  and
  [`build_and_merge_missing_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_and_merge_missing_field.rs):
  a `BuildAndMergeOutputs` output carrying a field the target lacks, extra or renamed, behind a
  check; ``[CGP-E001] missing field … on `App` ``.
- [`data/extensible-data/finalize_build_premature.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_build_premature.rs):
  `finalize_build` with `last_name` unset, an `E0599` "no method named"; `[CGP-E050]` over
  `[CGP-E119]`.
- [`data/extensible-data/builder_missing_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/builder_missing_field.rs):
  a `BuildWithHandlers` list without a step for `port`, behind a check; `[CGP-E119]`.
- [`data/extensible-data/extract_field_twice.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/extract_field_twice.rs):
  `Circle` extracted from a remainder that ruled it out, an `E0308`; `[CGP-E050]` over
  `[CGP-E124]`.
- [`data/extensible-data/finalize_extract_early.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_extract_early.rs):
  a remainder finalized with `Circle` left; `[CGP-E050]` over `[CGP-E121]`.
- [`data/extensible-data/matcher_missing_arm_check.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/matcher_missing_arm_check.rs):
  a `MatchWithHandlers` list without an arm for `Rectangle`, behind a check; `[CGP-E121]`.
- [`data/extensible-data/matcher_missing_arm.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/matcher_missing_arm.rs):
  the same matcher's provider method called directly through its path; `[CGP-E002]` over
  `[CGP-E121]`, rustc's repeat dropped.
- [`data/extensible-data/upcast_missing_variant.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_missing_variant.rs):
  an upcast into `Big`, which lacks `Small`'s `Bar`; `[CGP-E050]` over `[CGP-E120]`.
- [`data/extensible-data/downcast_missing_source_variant.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/downcast_missing_source_variant.rs):
  a downcast into `FooQux`, whose `Qux` the source lacks; `[CGP-E050]` over `[CGP-E120]`.
- [`data/extensible-data/upcast_payload_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_payload_mismatch.rs):
  an upcast whose `Foo` payloads differ; `[CGP-E050]` over `[CGP-E122]`.
- [`data/extensible-data/downcast_on_remainder.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/downcast_on_remainder.rs):
  `downcast` called on a remainder, which needs `downcast_fields`; `[CGP-E050]` over
  `[CGP-E126]`, with the `downcast_fields` `help`.
- [`data/extensible-data/from_variant_wrong_case.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/from_variant_wrong_case.rs):
  `from_variant` by the tag `circle` for `Circle`; `[CGP-E050]` over `[CGP-E120]` with its near
  miss, its two reports merged.
- [`data/extensible-data/extract_field_wrong_case.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/extract_field_wrong_case.rs):
  `extract_field` by the tag `circle` on an extractor; `[CGP-E050]` over `[CGP-E120]` with the near
  miss from the extractor's enum.
- [`data/extensible-data/from_variant_bound_missing_variant.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/from_variant_bound_missing_variant.rs):
  a plain function bounded on a variant `Big` lacks; rustc's headline kept, with its "similar impl"
  help resugared from the fragments rustc splits it into.
- [`data/extensible-data/from_variant_without_derive.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/from_variant_without_derive.rs):
  `from_variant` on an enum that does not derive `FromVariant`; `[CGP-E050]` over `[CGP-E123]` with
  the derive `help`, not a missing variant.
- [`data/extensible-data/derive_help_kinds.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/derive_help_kinds.rs):
  a struct's extractor, an enum's builder, and an upcast from `Option<u64>`; `[CGP-E123]` with no
  derive `help`, since no derive the type could take supplies the trait.
- [`data/extensible-data/borrowed_extractors_finalized_early.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/borrowed_extractors_finalized_early.rs):
  a reference and a mutable reference extractor finalized early; one `[CGP-E121]` block whose chain
  names each extractor by its borrow.
- [`pass-through/build_field_wrong_value_type.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/build_field_wrong_value_type.rs):
  `build_field` given a value of the wrong type; rustc's `E0308` is left as rustc wrote it, since no
  field state explains it.
- [`data/extensible-data/has_fields_bound_without_derive.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/has_fields_bound_without_derive.rs):
  a provider bound on `HasFields`, on a context without the derive; `[CGP-E123]` with the derive
  `help`.
- [`data/extensible-data/auto_dispatch_missing_derive.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/auto_dispatch_missing_derive.rs):
  a `#[cgp_auto_dispatch]` call on an enum without the derive; `[CGP-E003]` over two `[CGP-E123]`
  causes, with the derive `help`.
- [`data/extensible-data/build_from_source_without_has_fields.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_from_source_without_has_fields.rs)
  and
  [`upcast_source_without_has_fields.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_source_without_has_fields.rs):
  a `build_from` or `upcast` source without `HasFields`; `[CGP-E050]` over `[CGP-E123]` with the
  derive `help`.
- [`data/extensible-data/build_with_default_without_default.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_with_default_without_default.rs)
  and
  [`finalize_with_default_without_default.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_with_default_without_default.rs):
  a defaulted build or finalize whose unset `port` has no `Default`; `[CGP-E050]` over the
  `[CGP-E117]` bound `Port: Default`.
- [`data/extensible-data/transform_map_fields_missing_marker.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/transform_map_fields_missing_marker.rs):
  a field transform without a conversion for one marker; rustc's headline, which names it, kept.
- [`data/extensible-data/fields_ref_for_all_lifetimes.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/fields_ref_for_all_lifetimes.rs):
  a bound on a borrowed field view for every lifetime, on an enum with a lifetime; an `E0477` passed
  through.

## Related

- [Extensible records](../../concepts/extensible-records.md) and
  [extensible variants](../../concepts/extensible-variants.md): the builder and extractor patterns
  these operations implement.
- [`MapType`](../../reference/traits/map_type.md): the presence markers the partial types carry.
- [`HasBuilder`](../../reference/traits/has_builder.md),
  [`ExtractField`](../../reference/traits/extract_field.md), and
  [the casts](../../reference/traits/cast.md): the operations and where each misuse surfaces.
- [`#[derive(CgpData)]`](../../reference/derives/derive_cgp_data.md): the derive that generates the
  partial types and every trait these operations need.
- [Check-trait failure](../checks/check-trait-failure.md): the class a data mistake behind a provider
  reaches through, when a check asserts the component.
- [`E0277`](../error_codes/e0277.md), [`E0271`](../error_codes/e0271.md),
  [`E0599`](../error_codes/e0599.md), and [`E0308`](../error_codes/e0308.md): the Rust error codes
  this class is reported under.
