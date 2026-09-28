# `HasBuilder` and the builder trait family

The builder family is the set of traits that let a record be assembled one field at a time, with
field presence tracked at the type level so that a value can be finalized only once every field is
set.

## Purpose

The builder family solves the problem of constructing a record incrementally and generically, where
the fields are not all known at the same place in the code and the construction must still be
checked at compile time. A plain struct literal requires every field to be supplied at once; these
traits instead start from an empty *partial* value and add fields to it one by one, with each
addition advancing a type-level record of which fields are present. The payoff is that finalizing an
incomplete value is a compile error, not a runtime panic, the trait that turns a partial value back
into the concrete struct is implemented only for the fully-present configuration.

The family is built around a single primitive, `UpdateField`, that changes one field's storage from
one state to another. Everything else is either a wrapper over that primitive (`BuildField` sets an
absent field present, `TakeField` removes a present field) or an entry/exit point for the whole
process (`HasBuilder`/`IntoBuilder` start a build, `FinalizeBuild` ends one). The traits are in the
prelude, except `TakeField` and `CanBuildFrom`, which are imported from `cgp::core::field::traits`
and `cgp::core::field::impls`. They are implemented for a struct by
[`#[derive(BuildField)]`](../derives/derive_build_field.md), which also generates the partial
companion type they operate on.

## Definition

The family divides into entry points, the update primitive, two wrappers over it, and the finalize
step. The entry points obtain a partial value to build into. `HasBuilder` produces an empty one and
`IntoBuilder` produces a fully-present one from an existing value:

```rust
pub trait HasBuilder {
    type Builder;
    fn builder() -> Self::Builder;
}

pub trait IntoBuilder {
    type Builder;
    fn into_builder(self) -> Self::Builder;
}
```

`UpdateField<Tag, M>` is the primitive every field operation reduces to. It changes the field named
by `Tag` from its current marker, `Mapper`, to the new marker `M`, both [`MapType`](map_type.md)
markers. `Output` is the partial value with the field in state `M`, and the method returns the
field's old value alongside it:

```rust
pub trait UpdateField<Tag, M: MapType> {
    type Value;
    type Mapper: MapType;
    type Output;
    fn update_field(
        self,
        _tag: PhantomData<Tag>,
        value: M::Map<Self::Value>,
    ) -> (<Self::Mapper as MapType>::Map<Self::Value>, Self::Output);
}
```

The `M::Map<Self::Value>` argument and the `Mapper::Map<Self::Value>` first return component are the
field's value as it is *stored* under each marker: `IsPresent` stores the value itself, `IsNothing`
stores `()`. So updating an absent field to present takes the real value in and returns `()` as the
old value; the reverse takes `()` in and returns the real value.

The target marker `M` is not inferred from the value passed. A `String` argument could be the storage
of more than one marker, so `builder.update_field(PhantomData::<Symbol!("first_name")>, value)` on a
fresh `Person` builder fails with ``error[E0284]: type annotations needed for `((), __PartialPerson<_, IsNothing>)` ``
and the note ``cannot satisfy `<_ as MapType>::Map<String> == String` ``. A direct call names the
marker, as `UpdateField::<Symbol!("first_name"), IsPresent>::update_field(builder, PhantomData, value)`;
`BuildField` and `TakeField` below pin it, which is one reason they exist.

`BuildField<Tag>` and `TakeField<Tag>` are the two directions of that transition, each defined once
in the field crate as a blanket impl over `UpdateField`. `BuildField` is the `IsNothing → IsPresent`
direction, set a currently-absent field, and `TakeField` is the `IsPresent → IsNothing` direction,
remove a currently-present field:

```rust
pub trait BuildField<Tag> {
    type Value;
    type Output;
    fn build_field(self, _tag: PhantomData<Tag>, value: Self::Value) -> Self::Output;
}

impl<Context, Tag> BuildField<Tag> for Context
where
    Context: UpdateField<Tag, IsPresent, Mapper = IsNothing>,
{
    type Value = Context::Value;
    type Output = Context::Output;
    fn build_field(self, tag: PhantomData<Tag>, value: Self::Value) -> Self::Output {
        self.update_field(tag, value).1
    }
}

pub trait TakeField<Tag> {
    type Value;
    type Remainder;
    fn take_field(self, _tag: PhantomData<Tag>) -> (Self::Value, Self::Remainder);
}

impl<Context, Tag> TakeField<Tag> for Context
where
    Context: UpdateField<Tag, IsNothing, Mapper = IsPresent>,
{
    type Value = Context::Value;
    type Remainder = Context::Output;
    fn take_field(self, tag: PhantomData<Tag>) -> (Self::Value, Self::Remainder) {
        self.update_field(tag, ())
    }
}
```

`PartialData` records which concrete struct a partial value targets, and `FinalizeBuild`, a subtrait
of `PartialData`, turns the partial value back into that struct:

```rust
pub trait PartialData {
    type Target;
}

pub trait FinalizeBuild: PartialData {
    fn finalize_build(self) -> Self::Target;
}
```

## Behavior

A build is a sequence of `UpdateField`-driven state changes that only finalizes at the all-present
configuration. The entry point fixes the starting state: `HasBuilder::builder()` returns the partial
type with every field marker `IsNothing` (an empty value where each field is stored as `()`), while
`IntoBuilder::into_builder(self)` returns it with every marker `IsPresent` (a full value carrying
the real fields). Each `build_field` call flips one marker from `IsNothing` to `IsPresent` by
calling the generated `update_field` and keeping only its `Output`; each `take_field` does the
reverse and also hands back the removed value.

Presence lives entirely in the type. The derive generates the partial struct with one `MapType`
parameter per field, and the marker in each position decides whether that field's slot holds the
value (`IsPresent`), holds `()` (`IsNothing`), or holds the empty `Void` type (`IsVoid`). Because
`BuildField` requires `Mapper = IsNothing` and `TakeField` requires `Mapper = IsPresent`, the
compiler rejects building a field that is already set or taking one that is absent. The derive also
emits a [`HasField`](has_field.md) impl on the partial type gated on `IsPresent`, so a field that
has been set can be read back out of a still-incomplete value.

Each misuse surfaces on the `UpdateField` bound behind the directional trait, never as a message about
presence. On a two-field `Person { first_name: String, last_name: String }` deriving `BuildField`:

```rust
// Building `first_name` twice.
let _ = Person::builder()
    .build_field(PhantomData::<Symbol!("first_name")>, "Alice".to_owned())
    .build_field(PhantomData::<Symbol!("first_name")>, "Bob".to_owned());

// Taking `first_name` from an empty builder.
let _ = Person::builder().take_field(PhantomData::<Symbol!("first_name")>);

// Setting a field `Person` does not declare.
let _ = Person::builder().build_field(PhantomData::<Symbol!("age")>, 42_u8);
```

The first fails with `E0271`,
``type mismatch resolving `<__PartialPerson<IsPresent, IsNothing> as UpdateField<Symbol<10, …>, IsPresent>>::Mapper == IsNothing` ``,
with ``note: expected this to be `IsNothing` `` pointing at the derive; the first `IsPresent` in the
partial type is the only sign the field is already set. The second is the mirror image, `E0271` on
`Mapper == IsPresent` for `__PartialPerson<IsNothing, IsNothing>`. The third is `E0277`,
``the trait bound `__PartialPerson<IsNothing, IsNothing>: UpdateField<Symbol<3, …'a'…'g'…'e'…>, IsPresent>` is not satisfied``,
followed by a help listing the `UpdateField` impls that do exist, one per declared field.

Finalizing is what makes the tracking load-bearing. The derive provides exactly one `FinalizeBuild`
impl, on the all-`IsPresent` configuration of the partial type, so `finalize_build` is in scope only
when every field is present; calling it on a partial value with any `IsNothing` field fails to
compile. `PartialData::Target` is implemented for *every* configuration and names the struct being
built, which is how generic builder code knows the destination type before the build is complete.
Finalizing a `Person` with only `first_name` set fails with
``error[E0599]: no method named `finalize_build` found for struct `__PartialPerson<__F0__, __F1__>` ``,
labelled ``method not found in `__PartialPerson<IsPresent, IsNothing>` ``, so the marker list is the
diagnostic. A fieldless `struct Empty {}` has a companion with no markers, and
`Empty::builder().finalize_build()` compiles at once.

The derive's output for that `Person` shows every piece. `cargo cgp expand` gives the companion and
the entry and exit impls:

```rust
pub struct __PartialPerson<__F0__: MapType, __F1__: MapType> {
    pub first_name: <__F0__ as MapType>::Map<String>,
    pub last_name: <__F1__ as MapType>::Map<String>,
}
impl<__F0__: MapType, __F1__: MapType> PartialData for __PartialPerson<__F0__, __F1__> {
    type Target = Person;
}
impl FinalizeBuild for __PartialPerson<IsPresent, IsPresent> {
    fn finalize_build(self) -> Self::Target {
        Person {
            first_name: self.first_name,
            last_name: self.last_name,
        }
    }
}
impl HasBuilder for Person {
    type Builder = __PartialPerson<IsNothing, IsNothing>;
    fn builder() -> Self::Builder {
        __PartialPerson {
            first_name: (),
            last_name: (),
        }
    }
}
impl IntoBuilder for Person {
    type Builder = __PartialPerson<IsPresent, IsPresent>;
    fn into_builder(self) -> Self::Builder {
        __PartialPerson {
            first_name: self.first_name,
            last_name: self.last_name,
        }
    }
}
```

and one `UpdateField` impl per field, in which only that field's marker moves:

```rust
impl<
    __M1__: MapType,
    __M2__: MapType,
    __F1__: MapType,
> UpdateField<Symbol!("first_name"), __M2__> for __PartialPerson<__M1__, __F1__> {
    type Value = String;
    type Mapper = __M1__;
    type Output = __PartialPerson<__M2__, __F1__>;
    fn update_field(
        self,
        _tag: ::core::marker::PhantomData<Symbol!("first_name")>,
        value: __M2__::Map<Self::Value>,
    ) -> (__M1__::Map<Self::Value>, Self::Output) {
        (
            self.first_name,
            __PartialPerson {
                first_name: value,
                last_name: self.last_name,
            },
        )
    }
}
```

`__M1__` is unconstrained, so the impl applies whatever state the field is in, and `__F1__` passes
through untouched, which is why fields can be built in any order. The companion drops the struct's
own attributes, so it has none of the record's derives (`Debug`, `Clone`, and so on); the field
attributes are a different matter, under [Known issues](#known-issues).

## Examples

The family is normally driven through `builder()`, a series of `build_field` calls, and
`finalize_build`, with `build_from` (from the field crate's `CanBuildFrom`, itself layered on
`BuildField`) copying every shared field from another record in one step:

```rust
use cgp::prelude::*;
use cgp::core::field::impls::CanBuildFrom;

#[derive(HasFields, BuildField)]
pub struct FooBar {
    pub foo: u64,
    pub bar: String,
}

#[derive(BuildField)]
pub struct FooBarBaz {
    pub foo: u64,
    pub bar: String,
    pub baz: bool,
}

fn extend(foo_bar: FooBar) -> FooBarBaz {
    FooBarBaz::builder()
        .build_from(foo_bar)
        .build_field(PhantomData::<Symbol!("baz")>, true)
        .finalize_build()
}
```

`builder()` starts with every marker `IsNothing`, `build_from` sets `foo` and `bar`, and
`build_field` sets `baz`. Each step changes the partial type, and `finalize_build` type-checks only
because every marker has reached `IsPresent`. Reordering the steps so that `finalize_build` ran
before `baz` was set would be a compile error rather than a runtime failure.

**`CanBuildFrom` bounds its *source* on `HasFields + IntoBuilder`, which is why the source above
derives [`HasFields`](has_fields.md) as well as the builder.** `build_from` recurses over
`Source::Fields` to know which fields to copy, so a source deriving only `#[derive(BuildField)]` has
a builder of its own and still cannot be merged into anything, the failure is an unsatisfied
`HasFields` bound on the source type rather than anything about the target:
``the trait bound `FooBar: HasFields` is not satisfied``, noted as
``required for `__PartialFooBaz<IsNothing, IsNothing>` to implement `CanBuildFrom<FooBar>` ``. The
target needs only the builder.

## Related constructs

The struct-side derive that generates the partial type and all these impls is
[`#[derive(BuildField)]`](../derives/derive_build_field.md), whose doc shows the exact expanded
code. The presence markers `IsPresent`, `IsNothing`, and `IsVoid` are [`MapType`](map_type.md)
implementations, and the partial type's `MapType` parameters are what record per-field state. Fields
already set on a partial value are read back through [`HasField`](has_field.md). The enum
counterparts to this family are the extractor traits in [`extract_field`](extract_field.md), which
deconstruct a value variant by variant, and [`FromVariant`](from_variant.md), which constructs an
enum from a single variant. The conceptual overview that ties this family into the
[extensible builder pattern](../../concepts/extensible-records.md) is in
[extensible records](../../concepts/extensible-records.md), worked through in the
[application builder](../../../examples/application-builder.md) example.

## Known issues

The partial companion type keeps the original struct's field attributes. A helper attribute
belonging to another derive on the same struct, such as `#[serde(rename = "x")]`, therefore fails to
compile on the companion with
``cannot find attribute `serde` ``. The fix is for the derive to strip such attributes from the companion while keeping `#[cfg]` and documentation; see [`#[derive(BuildField)]`](../derives/derive_build_field.md#known-issues).

## Source

- The traits are defined in
  [crates/core/cgp-field/src/traits/has_builder.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_builder.rs)
  (`HasBuilder`, `IntoBuilder`),
  [build_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/build_field.rs)
  (`BuildField`, `FinalizeBuild`),
  [update_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/update_field.rs)
  (`UpdateField`),
  [take_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/take_field.rs)
  (`TakeField`), and
  [partial_data.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/partial_data.rs)
  (`PartialData`).
- The `MapType` markers are in
  [crates/core/cgp-field/src/impls/map_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/map_type.rs),
  and `CanBuildFrom` in
  [crates/core/cgp-field/src/impls/build_from.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/build_from.rs).
- For how it is generated and the index of tests, see the implementation document
  [implementation/entrypoints/derive_build_field.md](../../implementation/entrypoints/derive_build_field.md).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **7 pages**
rather than one:
[`has_builder`](https://contextgeneric.dev/docs/reference/traits/builder/has_builder),
[`into_builder`](https://contextgeneric.dev/docs/reference/traits/builder/into_builder),
[`update_field`](https://contextgeneric.dev/docs/reference/traits/builder/update_field),
[`build_field`](https://contextgeneric.dev/docs/reference/traits/builder/build_field),
[`take_field`](https://contextgeneric.dev/docs/reference/traits/builder/take_field),
[`partial_data`](https://contextgeneric.dev/docs/reference/traits/builder/partial_data),
[`finalize_build`](https://contextgeneric.dev/docs/reference/traits/builder/finalize_build). A
change here is propagated to each of them, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping and the granularity
rule behind it are recorded in [website/site-structure.md](../../../website/site-structure.md).
