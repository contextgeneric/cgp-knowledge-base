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
one field does the same.

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
remainder that may still hold a variant, which is what a `MatchWithHandlers` list without an arm for
one variant does:

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
fails the same way.

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
nightly, and a defaulted finalize's unset field names `Port: Default` on stable and only the
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
[Typed resolution: walking to the root cause](../../../cargo-cgp/implementation/typed-resolution-walk.md)).
Each cause has its own tree code in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md):

- `[CGP-E118]`: ``field `host` of `Config` is already set``.
- `[CGP-E119]`: ``field `port` of `Config` is not set``.
- `[CGP-E120]`: ``missing variant `Bar` on `Big` ``.
- `[CGP-E121]`: ``variant `Rectangle` of `Shape` is not extracted``.
- `[CGP-E122]`: ``variant `Foo` on `FooBarBaz` has type `u32`, but `u64` is required``.
- `[CGP-E123]`: `` `Shape` does not implement `HasFields` ``.
- `[CGP-E110]`: ``missing field `timeout` on `App` ``, the ordinary missing-field leaf, for a field
  a builder operation names that the struct lacks.

The headline states the cause after the code its anchor gives:

- **Through a check or a consumer call**, the block keeps the consumer class
  (``[CGP-E001] field `port` of `Config` is not set``), its tree running through the builder or
  matcher provider to the cause.
- **A call to one of CGP's data operations** on a constructed value (`upcast`, `downcast`) takes the
  extensible-data class: ``[CGP-E050] missing variant `Bar` on `Big` ``.
- **A `#[cgp_auto_dispatch]` call** on an enum without the derive keeps the blanket-trait class:
  ``[CGP-E003] `Shape` does not implement `HasFields` and `HasExtractor` ``.

A missing derive gets a `help` naming it, the traits one type lacks merged into one attribute
(`` add `#[derive(HasFields, ExtractField)]` to `Shape` ``), and a missing variant gets a near miss
when the enum has a similar one. The tree names a builder or an extractor in words, as in
``trait impl `BuildField<Symbol!("host")>` for the builder of `Config` with `host` and `port` set``,
though a provider step whose input is a partial value still shows its generated type.

A failing call on a builder or an extractor that is itself the result of a call (a `build_field`
chain, a `finalize_build`), on a remainder bound by a pattern (`Err(remainder)`), or by a
type-relative path (`Server::build_with_default(…)`) passes through as rustc wrote it, with only
the field names resugared to `Symbol!`. Four of them never name the cause, and are listed under
[hidden root cause](../../../cargo-cgp/issues/hidden-root-cause.md). The lifetime shape passes
through too.

## Resolving it

Each shape has its own fix, named by the cause:

- **A field set twice**: drop one of the two settings, or one source's copy of the field.
- **A field not set**: set it before the operation, or add a step for it to the builder list.
- **A field the struct lacks**: add it to the struct, or rename it on the side that misspells it.
- **A variant left unextracted**: extract it before finalizing, or add an arm for it to the matcher.
- **A cast that does not match**: add the missing variant, align the payload types, or cast to an
  enum whose variants match.
- **A missing derive**: add the derive the `help` names; `#[derive(CgpData)]` supplies all of them.
- **A missing `Default`**: implement `Default` for the field's type, or set the field before the
  defaulted finalize.

## Notes for tooling

A call whose receiver is another call's result, a pattern binding, or a type-relative path needs
its receiver's type recovered before the walk can start, and the emitter cannot read typeck results
(see [Typed root-cause resolution](../../../cargo-cgp/implementation/typed-root-cause-resolution.md#boundaries-and-open-ends)).
Recovering it means typing the chain of data operations by hand, from the struct's `builder()` or a
constructor, through each operation's signature.

## Backing fixtures

These fixtures pin the class, one group per shape:

- [`data/extensible-data/build_field_twice.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_field_twice.rs):
  a `build_field` chain setting `first_name` twice; passed through.
- [`data/extensible-data/builder_field_set_twice.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/builder_field_set_twice.rs):
  a `BuildWithHandlers` list setting `host` twice, behind a check; `[CGP-E118]`.
- [`data/extensible-data/build_from_overlapping_sources.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_from_overlapping_sources.rs):
  two `build_from` sources sharing `bar`; passed through.
- [`data/extensible-data/take_field_absent.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/take_field_absent.rs):
  `take_field` on an empty builder; passed through.
- [`data/extensible-data/set_optional_on_core_builder.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/set_optional_on_core_builder.rs):
  `set` on a builder that is not optional; passed through.
- [`data/extensible-data/build_field_unknown.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_field_unknown.rs):
  `build_field` for a field `Person` lacks; passed through.
- [`data/extensible-data/build_from_field_not_in_target.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_from_field_not_in_target.rs):
  a `build_from` source carrying `surname`, which the target lacks; passed through.
- [`data/extensible-data/build_and_merge_extra_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_and_merge_extra_field.rs)
  and
  [`build_and_merge_missing_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_and_merge_missing_field.rs):
  a `BuildAndMergeOutputs` output carrying a field the target lacks, extra or renamed, behind a
  check; ``[CGP-E001] missing field … on `App` ``.
- [`data/extensible-data/finalize_build_premature.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_build_premature.rs):
  `finalize_build` with `last_name` unset; passed through.
- [`data/extensible-data/builder_missing_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/builder_missing_field.rs):
  a `BuildWithHandlers` list without a step for `port`, behind a check; `[CGP-E119]`.
- [`data/extensible-data/extract_field_twice.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/extract_field_twice.rs):
  `Circle` extracted from a remainder that ruled it out; passed through as an `E0308`.
- [`data/extensible-data/finalize_extract_early.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_extract_early.rs):
  a remainder finalized with `Circle` left; passed through.
- [`data/extensible-data/matcher_missing_arm_check.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/matcher_missing_arm_check.rs):
  a `MatchWithHandlers` list without an arm for `Rectangle`, behind a check; `[CGP-E121]`.
- [`data/extensible-data/matcher_missing_arm.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/matcher_missing_arm.rs):
  the same matcher's provider method called directly; passed through, its two identical reports
  merged.
- [`data/extensible-data/upcast_missing_variant.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_missing_variant.rs):
  an upcast into `Big`, which lacks `Small`'s `Bar`; `[CGP-E050]` over `[CGP-E120]`.
- [`data/extensible-data/downcast_missing_source_variant.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/downcast_missing_source_variant.rs):
  a downcast into `FooQux`, whose `Qux` the source lacks; `[CGP-E050]` over `[CGP-E120]`.
- [`data/extensible-data/upcast_payload_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_payload_mismatch.rs):
  an upcast whose `Foo` payloads differ; `[CGP-E050]` over `[CGP-E122]`.
- [`data/extensible-data/downcast_on_remainder.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/downcast_on_remainder.rs):
  `downcast` called on a remainder, which needs `downcast_fields`; passed through.
- [`data/extensible-data/from_variant_wrong_case.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/from_variant_wrong_case.rs):
  `from_variant` by the tag `circle` for `Circle`; passed through, its two identical reports merged.
- [`data/extensible-data/from_variant_bound_missing_variant.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/from_variant_bound_missing_variant.rs):
  a plain function bounded on a variant `Big` lacks; rustc's headline kept, with its "similar impl"
  help resugared from the fragments rustc splits it into.
- [`data/extensible-data/has_fields_bound_without_derive.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/has_fields_bound_without_derive.rs):
  a provider bound on `HasFields`, on a context without the derive; `[CGP-E123]` with the derive
  `help`.
- [`data/extensible-data/auto_dispatch_missing_derive.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/auto_dispatch_missing_derive.rs):
  a `#[cgp_auto_dispatch]` call on an enum without the derive; `[CGP-E003]` over two `[CGP-E123]`
  causes, with the derive `help`.
- [`data/extensible-data/build_from_source_without_has_fields.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_from_source_without_has_fields.rs)
  and
  [`upcast_source_without_has_fields.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_source_without_has_fields.rs):
  a `build_from` or `upcast` source without `HasFields`; passed through, the cause absent.
- [`data/extensible-data/build_with_default_without_default.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_with_default_without_default.rs)
  and
  [`finalize_with_default_without_default.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_with_default_without_default.rs):
  a defaulted build or finalize whose unset `port` has no `Default`; passed through, the cause
  absent.
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
