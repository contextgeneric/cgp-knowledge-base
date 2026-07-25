# Extensible Data Types, Part 3: Implementing Extensible Records

The internals half of the series, walking through how extensible records actually work: partial
records, the `MapType` presence markers, the build and take traits, and the type-level machinery that
merges one struct into another. It is the most detailed published account of this mechanism and the
closest thing the site has to implementation documentation.

- **URL** — <https://contextgeneric.dev/blog/extensible-datatypes-part-3>
- **Source** — [blog/2025-07-12-extensible-datatypes-part-3.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-07-12-extensible-datatypes-part-3.md)
- **Published** — 12 July 2025, tagged `deepdive`
- **Release** — [v0.4.2](../../releases/v0-4-2.md)
- **Status** — Historical

## What it covers

The post opens with the theory it draws on — datatype-generic programming in Haskell and the paper
[*Abstracting extensible data types: or, rows by any other name*](https://dl.acm.org/doi/10.1145/3290325) —
and then states the problem CGP's version solves that those approaches leave open: **constraint
propagation**. Two generic functions each carrying their own row constraint cannot be composed into a
third that inherits both, because Rust has no constraint kinds; the caller must restate every
constraint by hand, and a composed function cannot be exported as a top-level value at all. CGP's
answer is to represent functions as *types* — providers — so that composing two providers into
`ConcatOutputs<FirstNameToString, LastNameToString>` is a type alias whose constraints are inferred
and enforced lazily at the point of use. This is the sharpest statement anywhere of *why* CGP
represents computations as types, and it generalizes far beyond extensible records.

The implementation walkthrough then builds up in order. `HasField` gives read access keyed by a
type-level tag. **Partial records** are a generated struct parameterized by one `MapType` marker per
field, where `IsPresent` maps a field's type to itself and `IsNothing` maps it to `()`, so
`PartialPerson<IsPresent, IsNothing>` is a `Person` with only `first_name` filled in. `HasBuilder`
produces the all-absent starting value, `BuildField` fills one field and returns a builder whose type
records the change, and `FinalizeBuild` converts an all-present partial record into the real struct.
The post explains why finalization is a separate step rather than folded into the last `build_field`:
each `BuildField` impl is generic in the other fields' markers, so it cannot know it is the last, and
that genericity is exactly what avoids a combinatorial explosion of impls.

The merge machinery is then built from the same parts in reverse. `IntoBuilder` turns a complete
struct into an all-present partial record, `TakeField` removes one field and returns the value plus a
remainder, and `HasFields` exposes the whole field list as a type-level product. `CanBuildFrom` ties
them together through a private `FieldsBuilder` helper that recurses over the field list, taking from
the source and building into the target one field at a time until the list is `Nil`. A step-by-step
trace of `Employee::builder().build_from(person)` shows every intermediate type.

The final section covers the builder dispatchers. `BuildWithHandlers` initializes an empty partial
record, pipes it through a list of handlers with `PipeHandlers`, and finalizes the result — reusing
the same piping mechanism as Hypershell. `BuildAndMerge` and `BuildAndSetField` adapt a provider to
contribute a whole record or a single field, `MapFields` maps a type-level list, and
`BuildAndMergeOutputs` is assembled from those pieces. The post closes with a technique worth
remembering: when a type alias would leak an internal constraint to its callers, define the wrapper as
a real provider struct and use `delegate_components!` to hide the constraint behind a
`DelegateComponent` impl.

## How it relates to the knowledge base

The concept is [extensible records](../../cgp/concepts/extensible-records.md). The traits are
documented individually as [`HasField`](../../cgp/reference/traits/has_field.md),
[`HasFields`](../../cgp/reference/traits/has_fields.md),
[`HasBuilder`](../../cgp/reference/traits/has_builder.md) for the builder family,
[`MapType`](../../cgp/reference/traits/map_type.md) for the presence markers,
[`AppendProduct` / `MapFields`](../../cgp/reference/traits/product_ops.md) for the list algebra, and
[`CanBuildFrom`](../../cgp/reference/traits/cast.md) for the merge. The spine types are
[`Cons` / `Nil`](../../cgp/reference/types/cons.md) and [`Field`](../../cgp/reference/types/field.md).
The dispatchers are in the [dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md)
and [handler combinators](../../cgp/reference/providers/handler_combinators.md). The derive is
[`#[derive(BuildField)]`](../../cgp/reference/derives/derive_build_field.md), now normally reached
through [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md).

The constraint-propagation argument in the opening is the most valuable part of the post for the rest
of the base, because it is the missing *why* behind
[higher-order providers](../../cgp/concepts/higher-order-providers.md) and
[type-level DSLs](../../cgp/concepts/type-level-dsls.md): representing computations as types is not a
stylistic choice but the only way to compose constraint-carrying functions in a language without
constraint kinds. The constraint-hiding technique at the end is the reasoning behind
[aggregate providers](../../cgp/concepts/aggregate-providers.md).

## Where it diverges from CGP v0.8.0

- **`PartialPerson` is now `__PartialPerson`.** v0.5.0 added the `__Partial` prefix to keep generated
  types out of the user's namespace. Every partial-record type name in this post is missing it.
- **`BuildField` is no longer a primitive.** v0.5.0 introduced `UpdateField`, and `BuildField` became
  a blanket impl over it, transforming an `IsNothing` field into `IsPresent`. The post's presentation
  of `BuildField` as the base operation is one layer out of date.
- **The `MapType` markers gained `IsOptional`** in v0.5.0, alongside the optional builder and
  `finalize_with_default`; see [optional fields](../../cgp/reference/traits/optional_fields.md). The
  post lists these as future work.
- **`#[derive(BuildField)]` alone is no longer the usual derive**, superseded by
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md).
- **Every provider is inside-out**, written with `#[cgp_provider]`/`#[cgp_new_provider]` rather than
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md).
- **The post's "future extensions" have largely shipped** — defaults, overriding, and the optional
  builder all arrived in v0.5.0 — so read that section as a historical wish list rather than as a
  statement of current gaps.
- **One typo:** the `build_from` walkthrough annotates the final `.finalize_build()` with `// Person`
  where the value being built is an `Employee`.

## Maintaining it

Leave it alone. The trait signatures it shows are close enough to current that a careless reader could
mistake them for reference documentation, which is precisely why the divergences above matter: consult
[extensible records](../../cgp/concepts/extensible-records.md) and the individual trait references for
the current shapes. The constraint-propagation argument, by contrast, does not depend on any syntax and
is the single passage from this series most worth reusing verbatim in new writing.
