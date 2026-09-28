# Optional and defaulted field extensions

The optional-field extensions are the traits and providers that let a record be finalized even when
some fields were never set, by filling the gaps from `Default` or treating them as optional, rather
than requiring every field to be present.

## Purpose

These extensions solve the problem that the core builder family is deliberately strict: a partial
record can be turned back into its concrete struct only once every field has been set, because
[`FinalizeBuild`](has_builder.md) is implemented solely on the all-`IsPresent` configuration of the
partial type. That strictness is exactly what catches a missing field at compile time, but it is too
rigid for records where some fields have sensible defaults or are genuinely allowed to be absent.
The traits in `cgp-field-extra` relax it in two controlled ways, filling unset fields with
`Default::default()`, and tracking each field as an `Option` so absence is a runtime condition
rather than a compile error, while reusing the same `UpdateField`-driven machinery underneath.

The whole layer is built by composing three core mechanisms rather than inventing new ones. It
reuses [`UpdateField`](has_builder.md) to move individual fields between states,
[`TransformMapFields`](map_type.md) to re-wrap every field of a partial record at once, and the
[`MapType`](map_type.md) markers `IsPresent`, `IsNothing`, and `IsOptional` to name what state each
field is in. The extensions are therefore best understood as a small set of `TransformMap` natural
transformations plus the entry-point traits that drive them, layered on top of the builder and
extractor traits in core.

All of these are imported from `cgp::extra::field::impls`; none is in the prelude.

## Definition

The layer splits into two complementary operations, defaulted finalization and optional fields, that
share the same underlying transform pattern. Defaulted finalization fills any unset field from
`Default` so a record can be completed without setting everything; the optional-field traits convert
a builder so every field becomes an `Option`, allow those optional slots to be set and replaced
individually, and finalize either by requiring presence with an error or by defaulting. The
`TransformMap` markers `TransformMapDefault` and `TransformOptional` carry the actual per-field
conversions, and the entry-point traits `CanBuildWithDefault`, `CanFinalizeWithDefault`,
`HasOptionalBuilder`, `ToOptional`, `SetOptional`, and `FinalizeOptional` expose them as usable
operations.

### `TransformMapDefault`: filling unset fields from `Default`

`TransformMapDefault` is the [`TransformMap`](map_type.md) natural transformation that re-wraps
every field into `IsPresent`, supplying `Default::default()` wherever a field has no value. It is a
zero-sized marker with one impl per source marker, each describing how a field in that state becomes
a present value:

```rust
pub struct TransformMapDefault;

impl<T> TransformMap<IsPresent, IsPresent, T> for TransformMapDefault {
    fn transform_mapped(value: T) -> T { value }
}

impl<T: Default> TransformMap<IsNothing, IsPresent, T> for TransformMapDefault {
    fn transform_mapped(_value: ()) -> T { T::default() }
}

impl<T: Default> TransformMap<IsOptional, IsPresent, T> for TransformMapDefault {
    fn transform_mapped(value: Option<T>) -> T { value.unwrap_or_default() }
}
```

A field that is already present passes through unchanged; a field that is `IsNothing` (never set)
becomes its type's default; and a field that is `IsOptional` becomes the contained value or, when
empty, the default. Because all three target `IsPresent`, applying this transform across a record
leaves every field present, which is precisely the configuration `FinalizeBuild` accepts.

Only the `IsPresent` impl is free of the `Default` bound, so what needs `Default` depends on the
builder. On a core builder it is every field still `IsNothing`; a core builder with every field set
converts whatever its field types. On an optional builder it is every field, set or not, because a set
field is still `IsOptional` and goes through the third impl.

### `CanFinalizeWithDefault`: finalize, defaulting whatever is unset

`CanFinalizeWithDefault` finalizes a partial record into its target struct, defaulting any field
that is not present. It is implemented for any partial value whose fields can be transformed by
`TransformMapDefault` into the all-present configuration that `FinalizeBuild` then consumes:

```rust
pub trait CanFinalizeWithDefault {
    type Output;
    fn finalize_with_default(self) -> Self::Output;
}

impl<Builder, Output> CanFinalizeWithDefault for Builder
where
    Builder: TransformMapFields<TransformMapDefault, IsPresent>,
    Builder::Output: FinalizeBuild<Target = Output>,
{
    type Output = Output;
    fn finalize_with_default(self) -> Output {
        self.transform_map_fields().finalize_build()
    }
}
```

The body is the layer's core motion: `transform_map_fields` walks the record and applies
`TransformMapDefault` to every field, producing an all-`IsPresent` partial value, and
`finalize_build` turns that into the concrete struct. The strict presence check still applies, but
it always succeeds, because the transform guarantees presence before `finalize_build` is reached.
The impl applies to a core builder as well as an optional one: `Context::builder()` with only `foo`
built finalizes this way to the same value as the optional builder with only `foo` set.

A field type with no `Default` is reported without being named when the call is a method call. With
`pub struct Port(pub u16);` lacking `Default`:

```rust
#[derive(CgpData)]
pub struct Server {
    pub host: String,
    pub port: Port,
}

let _ = Server::builder()
    .build_field(PhantomData::<Symbol!("host")>, "localhost".to_owned())
    .finalize_with_default();
```

fails with
``error[E0599]: the method `finalize_with_default` exists for struct `__PartialServer<IsPresent, IsNothing>`, but its trait bounds were not satisfied``,
whose notes stop at ``__PartialServer<IsPresent, IsNothing>: TransformMapFields<TransformMapDefault, IsPresent>``
(followed by the autoref'd `&` and `&mut` variants) and mention neither `port` nor `Default`. The same
`Server` on an optional builder with both fields set fails the same way, on
`__PartialServer<IsOptional, IsOptional>`. Reached through a `where` clause instead, as through
`CanBuildWithDefault` below, rustc follows the chain and names the root cause.

### `CanBuildWithDefault`: build from a source, defaulting the rest

`CanBuildWithDefault<Source>` constructs the target struct by copying every field of a `Source`
record into it and defaulting every remaining field. It chains the core
[`CanBuildFrom`](has_builder.md) copy step into a defaulted finalize:

```rust
pub trait CanBuildWithDefault<Source> {
    fn build_with_default(source: Source) -> Self;
}

impl<Source, Target, Builder> CanBuildWithDefault<Source> for Target
where
    Target: HasBuilder<Builder = Builder>,
    Builder: CanBuildFrom<Source>,
    Builder::Output: CanFinalizeWithDefault<Output = Target>,
{
    fn build_with_default(source: Source) -> Target {
        Target::builder().build_from(source).finalize_with_default()
    }
}
```

The pipeline reads top to bottom: start an empty builder for the target with
[`HasBuilder`](has_builder.md), copy across every field of the source, each of which must exist in the target, with
`build_from`, then finalize with defaults for the fields the source did not supply. This is the
field-level "widening cast", turning a `Point2d` into a `Point3d` whose extra `z` is `0`, for
instance, without naming any field explicitly.

The widening runs one way. `build_from` walks the *source's* fields and builds each into the target,
so every source field must exist on the target: a `LabeledPoint2d { x, y, label }` fails with
``error[E0277]: the trait bound `__PartialPoint3d<IsPresent, IsPresent, IsNothing>: UpdateField<Symbol<5, …label…>, IsPresent>` is not satisfied``,
noted as required through `CanBuildFrom<LabeledPoint2d>` and `CanBuildWithDefault<LabeledPoint2d>`,
rather than dropping `label`. A target field the source lacks is the case the defaulted finalize
fills, and when its type has no `Default`, the bound chain here names it: building the `Server`
above from a `Host { host: String }` fails with
``error[E0277]: the trait bound `Port: Default` is not satisfied``, noted as
``required for `TransformMapDefault` to implement `TransformMap<IsNothing, IsPresent, Port>` `` and
then through `TransformMapFields`, `CanFinalizeWithDefault`, and `CanBuildWithDefault<Host>`.

### `ToOptional` and `TransformOptional`: re-wrap every field as `Option`

`ToOptional` converts a partial record so every field is wrapped in `IsOptional`, and
`TransformOptional` is the `TransformMap` that performs the per-field conversion. Where
`TransformMapDefault` targets `IsPresent`, `TransformOptional` targets `IsOptional`, mapping a
present value to `Some` and an absent field to `None`:

```rust
pub struct TransformOptional;

impl<T> TransformMap<IsPresent, IsOptional, T> for TransformOptional {
    fn transform_mapped(value: T) -> Option<T> { Some(value) }
}

impl<T> TransformMap<IsNothing, IsOptional, T> for TransformOptional {
    fn transform_mapped(_value: ()) -> Option<T> { None }
}

pub trait ToOptional {
    type Output;
    fn to_optional(self) -> Self::Output;
}

impl<Context> ToOptional for Context
where
    Context: TransformMapFields<TransformOptional, IsOptional>,
{
    type Output = Context::Output;
    fn to_optional(self) -> Self::Output { self.transform_map_fields() }
}
```

After `to_optional`, the partial type's every field marker is `IsOptional`, so each field's storage
is an `Option`. A field already set becomes `Some`, an unset field becomes `None`, and from then on
every field can be assigned or reassigned freely, because an `IsOptional` slot can always be
overwritten.

`TransformOptional` has no impl from `IsOptional`, so an already-optional builder cannot be converted
again. `Context::optional_builder().to_optional()` fails with
``error[E0599]: the method `to_optional` exists for struct `__PartialContext<IsOptional, IsOptional>`, but its trait bounds were not satisfied``,
noting the unmet ``TransformMapFields<TransformOptional, IsOptional>`` bound. Unlike
`TransformMapDefault`, it carries no `Default` bound, so the conversion applies to every field type.

### `HasOptionalBuilder`: start an all-optional builder

`HasOptionalBuilder` is the entry point that hands back a fresh builder in which every field is
already optional. It composes `HasBuilder::builder()` with `ToOptional`, so the resulting builder
starts with every field `None`:

```rust
pub trait HasOptionalBuilder {
    type Builder;
    fn optional_builder() -> Self::Builder;
}

impl<Context, Builder> HasOptionalBuilder for Context
where
    Context: HasBuilder,
    Context::Builder: ToOptional<Output = Builder>,
{
    type Builder = Builder;
    fn optional_builder() -> Self::Builder { Self::builder().to_optional() }
}
```

This is the usual starting point for the optional-field workflow: `Context::optional_builder()`
gives a builder whose fields can be set in any order and any number of times, deferring the decision
about which fields must ultimately be present until finalization.

### `SetOptional`: set or replace an optional field

`SetOptional<Tag>` sets the value of an optional field, optionally returning whatever value it
replaced. It is implemented for any context whose `Tag` field is in the `IsOptional` state and stays
there after the update:

```rust
pub trait SetOptional<Tag> {
    type Value;
    fn set(self, _tag: PhantomData<Tag>, value: Self::Value) -> Self;
    fn set_optional(
        self,
        _tag: PhantomData<Tag>,
        value: Self::Value,
    ) -> (Option<Self::Value>, Self);
}

impl<Context, Tag> SetOptional<Tag> for Context
where
    Context: UpdateField<Tag, IsOptional, Mapper = IsOptional, Output = Context>,
{
    type Value = Context::Value;
    fn set(self, tag, value) -> Self { self.set_optional(tag, value).1 }
    fn set_optional(self, tag, value) -> (Option<Self::Value>, Self) {
        self.update_field(tag, Some(value))
    }
}
```

Both methods reduce to a single `UpdateField` call that writes `Some(value)` into the `IsOptional`
slot. The crucial detail is that the field's marker is `IsOptional` both before and after, the
`Mapper = IsOptional, Output = Context` bounds keep the builder's type unchanged, so a field can be
set repeatedly, and `set_optional` returns the previous `Option` while `set` discards it. This is
what makes the optional builder freely mutable, in contrast to the core `build_field` that consumes
an absent slot exactly once.

Calling `set` on a core builder fails both pins. `Context::builder().set(PhantomData::<Symbol!("foo")>, "foo".to_owned())`
reports two `E0271` errors on `__PartialContext<IsNothing, IsNothing>`, one resolving
`…>::Mapper == IsOptional` and one resolving `…>::Output == __PartialContext<IsNothing, IsNothing>`,
the second noting it found `__PartialContext<IsOptional, IsNothing>`.

### `FinalizeOptional`: finalize, erroring on a genuinely missing field

`FinalizeOptional` finalizes an optional builder into its concrete struct, succeeding only if every
field holds a value and otherwise returning an error that names a missing field. Unlike
`CanFinalizeWithDefault`, it does not substitute defaults, absence is a recoverable runtime error
rather than a silent fill:

```rust
pub trait FinalizeOptional: PartialData {
    fn finalize_optional(self) -> Result<Self::Target, &'static str>;
}
```

The implementation walks the target's [`HasFields`](has_fields.md) list, so the record needs
`HasFields` as well as the builder, which `#[derive(CgpData)]` supplies. The public impl hands the
builder to a private helper trait implemented over the field list and finalizes the result:

```rust
impl<ContextA, ContextB, Target> FinalizeOptional for ContextA
where
    ContextA: PartialData<Target = Target>,
    Target: HasFields,
    Target::Fields: FinalizeOptionalImpl<ContextA, Output = ContextB>,
    ContextB: FinalizeBuild<Target = Target>,
{
    fn finalize_optional(self) -> Result<Self::Target, &'static str> {
        let context = Target::Fields::finalize_optional(self)?;
        Ok(context.finalize_build())
    }
}
```

For each `Cons` cell the helper first recurses into the rest, then moves the field from `IsOptional`
to `IsNothing` with `UpdateField` to take the `Option` out; a `Some` is written back as `IsPresent`
with `BuildField`, and a `None` returns `Err(Tag::VALUE)`, the field's name as a static string
through `Tag: StaticString`. `Nil` returns the context unchanged. Only when every field has a value
does `finalize_build` run and the result come back as `Ok`.

A core builder is rejected: `Context::builder().finalize_optional()` fails with
``error[E0599]: the method `finalize_optional` exists for struct `__PartialContext<IsNothing, IsNothing>`, but its trait bounds were not satisfied``,
and its notes list only unmet `PartialData` bounds on the autoref'd `&` and `&mut` receivers, with
nothing about `IsOptional`.

The recursion handles the rest of the list before the current field, so fields are checked from last
to first. With several fields unset, the error names the last of them in declaration order: an
optional builder for `struct Context { foo: String, bar: u64 }` with nothing set returns
`Err("bar")`.

## Behavior

Two finalization strategies sit on top of the same optional builder, differing only in how they
treat a field that was never set. After `optional_builder` and a series of `set` calls, calling
`finalize_with_default` completes the record by defaulting every unset field, whereas calling
`finalize_optional` completes it only if nothing is missing and otherwise reports the missing field
by name. The choice is made at the finalize call site, not when the builder is created, so the same
builder value can be finalized either way depending on whether absence should be tolerated.

The defaulted path and the optional path reuse the identical `transform_map_fields` recursion with
different markers, which is why their behavior is so symmetric. `CanFinalizeWithDefault` drives
`TransformMapDefault` toward `IsPresent`; `ToOptional` drives `TransformOptional` toward
`IsOptional`. Both walk the same field list, both rebuild the partial type one field at a time
through `UpdateField`, and neither changes a value's runtime layout beyond wrapping or unwrapping an
`Option` or substituting a default. The strict, all-present `FinalizeBuild` from core remains the
only way a partial value becomes a concrete struct; these extensions simply guarantee the
all-present configuration is reached before it is invoked.

### Choosing between the paths, and their pitfalls

Moving to this layer gives up the core builder's compile-time completeness check, which is the
trade to weigh before reaching for it. With the core builder a missing field is a compile error; on
an optional builder it is an `Err` from `finalize_optional` or a silently substituted default from
`finalize_with_default`, and nothing in the result distinguishes a field set to its default from one
left unset. The layer suits fields that arrive unpredictably, such as parsed configuration or a value
assembled over several passes; a hand-written builder remains better when finalizing should validate,
when fields depend on each other, or when a default is computed rather than `Default::default()`.

The optional builder's type records nothing about what has been set, since every field stays
`IsOptional` from start to finish. That is what permits setting a field more than once, and it is why
finalizing must check at run time. `SetOptional::set_optional` returns `(previous, builder)`, in that
order, the previous value as an `Option`; there is no operation that unsets a field, so a field left
alone stays `None`. A field whose own type is already `Option<T>` takes an `Option<T>` argument and is
stored as `Option<Option<T>>`, the outer layer being the builder's presence tracking, which is easy
to conflate with the field's own optionality when reading an error.

`ToOptional` is one-way. A field already set survives the conversion as `Some`, which distinguishes
it from starting over with `optional_builder()`, and no `from_optional` exists: returning to a strict
configuration means finalizing, through `FinalizeOptional` or `CanFinalizeWithDefault`. Relaxing a
complete value is `into_builder()` followed by `to_optional()`, which makes every field `Some`.

`FinalizeOptional`'s error is a `&'static str` naming one field, enough to report which field is
missing and not a structured value to match on. Because the walk checks the last declared field
first and stops at the first `None`, reordering a struct's fields changes which missing field is
named, which a test asserting on the name depends on.

`CanBuildWithDefault::build_with_default` is an associated function on the target,
`Point3d::build_with_default(source)`, and it offers no step at which to set a field by hand; a build
that copies some fields and sets others writes the three calls out. Its enum analogue, widening a
variant set rather than a field set, is [`CanUpcast`](cast.md). When both types are the author's own
and the conversion is written once, a hand-written `From` impl is clearer, requires nothing of either
type, and can choose values other than `Default`.

`TransformMapDefault` and `TransformOptional` are markers named only in a
`TransformMapFields<Marker, Target>` bound, which is where an operation says which conversion it
drives; a caller of `finalize_with_default` or `to_optional` never names them. A conversion neither
covers, one that validates, logs, or fills from something other than `Default`, is a marker of one's
own implementing [`TransformMap`](map_type.md) once per source state it accepts.

## Examples

The optional-field workflow starts an all-optional builder, sets fields freely, and finalizes with
one of the two strategies. Setting a field that already holds a value reports the replaced value,
and finalizing with defaults fills whatever was never set:

```rust
use cgp::prelude::*;
use cgp::extra::field::impls::{
    CanFinalizeWithDefault, FinalizeOptional, HasOptionalBuilder, SetOptional,
};

#[derive(CgpData)]
pub struct Context {
    pub foo: String,
    pub bar: u64,
}

fn all_set() {
    let builder = Context::optional_builder()
        .set(PhantomData::<Symbol!("foo")>, "foo".to_owned())
        .set(PhantomData::<Symbol!("bar")>, 42);

    let (replaced, builder) =
        builder.set_optional(PhantomData::<Symbol!("foo")>, "bar".to_owned());
    assert_eq!(replaced, Some("foo".to_owned()));

    let context = builder.finalize_optional().unwrap();
    assert_eq!(context.foo, "bar");
    assert_eq!(context.bar, 42);
}

fn bar_defaulted() {
    let context = Context::optional_builder()
        .set(PhantomData::<Symbol!("foo")>, "foo".to_owned())
        .finalize_with_default();
    assert_eq!(context.foo, "foo");
    assert_eq!(context.bar, 0);
}
```

In `all_set`, every field is present, so `finalize_optional` succeeds, and `set_optional` returns
the value it replaced. In `bar_defaulted`, `bar` is never set, and `finalize_with_default` fills it
from `Default`.

Had the second case used `finalize_optional` instead, it would have returned `Err("bar")` because
`bar` was never set, rather than defaulting it to `0`.

The defaulted-build path constructs a wider record from a narrower one in a single call, defaulting
the fields the source lacks:

```rust
use cgp::prelude::*;
use cgp::extra::field::impls::CanBuildWithDefault;

#[derive(Debug, Clone, Eq, PartialEq, CgpData)]
struct Point2d {
    x: u64,
    y: u64,
}

#[derive(Debug, Clone, Eq, PartialEq, CgpData)]
struct Point3d {
    x: u64,
    y: u64,
    z: u64,
}

fn widen() {
    let point_3d = Point3d::build_with_default(Point2d { x: 1, y: 2 });
    assert_eq!(point_3d, Point3d { x: 1, y: 2, z: 0 });
}
```

`build_with_default` copies `x` and `y` from the source through `build_from`, then defaults the
unmatched `z` to `0` during the defaulted finalize.

## Related constructs

These extensions layer directly on the core builder family in [`HasBuilder`](has_builder.md):
`CanBuildWithDefault` chains its `CanBuildFrom` copy step and `HasBuilder` entry point, and every
finalize path ultimately calls `FinalizeBuild`. They are driven by the [`MapType`](map_type.md)
machinery, `TransformMapDefault` and `TransformOptional` are `TransformMap` natural transformations,
and `TransformMapFields` is the recursion that applies them across a whole record, re-marking each
field's `IsPresent`/`IsNothing`/`IsOptional` state. `SetOptional` and `FinalizeOptional` reduce to
the same `UpdateField` primitive used by the core `BuildField` and `TakeField`. The partial types
these operate on are generated by [`#[derive(BuildField)]`](../derives/derive_build_field.md) (also
exposed through `#[derive(CgpData)]`). The enum-side counterpart that takes fields apart variant by
variant is [`ExtractField`](extract_field.md).

## Source

- The extensions are defined in `cgp-field-extra`: `CanBuildWithDefault`, `CanFinalizeWithDefault`,
  and `TransformMapDefault` in
  [crates/extra/cgp-field-extra/src/impls/build_default.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-field-extra/src/impls/build_default.rs);
  `FinalizeOptional` in
  [crates/extra/cgp-field-extra/src/impls/finalize_optional.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-field-extra/src/impls/finalize_optional.rs);
  `SetOptional` in
  [crates/extra/cgp-field-extra/src/impls/set_optional.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-field-extra/src/impls/set_optional.rs);
  and `HasOptionalBuilder`, `ToOptional`, and `TransformOptional` in
  [crates/extra/cgp-field-extra/src/impls/to_optional.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-field-extra/src/impls/to_optional.rs).
- They build on the core traits in
  [crates/core/cgp-field/src/traits/](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-field/src/traits/)
  (`UpdateField`, `BuildField`, `FinalizeBuild`, `PartialData`, `HasFields`, `TransformMap`,
  `TransformMapFields`) and the `MapType` markers in
  [crates/core/cgp-field/src/impls/map_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/map_type.rs).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **8 pages**
rather than one:
[`has_optional_builder`](https://contextgeneric.dev/docs/reference/traits/optional/has_optional_builder),
[`to_optional`](https://contextgeneric.dev/docs/reference/traits/optional/to_optional),
[`set_optional`](https://contextgeneric.dev/docs/reference/traits/optional/set_optional),
[`finalize_optional`](https://contextgeneric.dev/docs/reference/traits/optional/finalize_optional),
[`can_finalize_with_default`](https://contextgeneric.dev/docs/reference/traits/optional/can_finalize_with_default),
[`can_build_with_default`](https://contextgeneric.dev/docs/reference/traits/optional/can_build_with_default),
[`transform_map_default`](https://contextgeneric.dev/docs/reference/traits/optional/transform_map_default),
[`transform_optional`](https://contextgeneric.dev/docs/reference/traits/optional/transform_optional).
A change here is propagated to each of them, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping and the granularity
rule behind it are recorded in [website/site-structure.md](../../../website/site-structure.md).
