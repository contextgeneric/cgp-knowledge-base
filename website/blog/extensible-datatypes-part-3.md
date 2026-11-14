# Extensible Data Types, Part 3: Implementing Extensible Records

The series' internals for records: partial records, the `MapType` presence markers, the build and
take traits, and the type-level machinery that merges one struct into another. It is the most detailed
published account of the mechanism and the closest the site has to implementation documentation.

- **URL**: <https://contextgeneric.dev/blog/extensible-datatypes-part-3>
- **Source**: [blog/2025-07-12-extensible-datatypes-part-3.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-07-12-extensible-datatypes-part-3.md)
- **Published**: 12 July 2025, tagged `deepdive`
- **Release**: [v0.4.2](../../releases/v0-4-2.md)
- **Status**: Historical
- **Notice**: a note at the top of the post, written on the website's `v0.8.0` branch, links the *Extensible records* Concepts page and the reference, since the post explains internals rather than a project; it is the sanctioned edit in [../AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#blog-posts) and changes no claim

## What it covers

**The opening states the problem CGP's version solves: constraint propagation.** It draws on
Haskell's datatype-generic programming and [*Abstracting extensible data types: or, rows by any
other name*](https://dl.acm.org/doi/10.1145/3290325). Two generic functions with their own row
constraints cannot compose into a third that inherits both, because Rust has no constraint kinds:
the caller restates every constraint, and a composed function cannot be exported as a value. CGP
represents functions as *types*, so `ConcatOutputs<FirstNameToString, LastNameToString>` is a type
alias whose constraints are inferred and enforced lazily at use. This is the sharpest statement of
*why* CGP represents computations as types, and the passage most worth reusing verbatim; it needs no
syntax.

The walkthrough builds up in order:

- **Reading:** `HasField` keyed by a type-level tag.
- **Partial records:** a generated struct with one `MapType` marker per field, `IsPresent` mapping a
  field's type to itself and `IsNothing` to `()`, so `PartialPerson<IsPresent, IsNothing>` is a
  `Person` with only `first_name`.
- **Building:** `HasBuilder` gives the all-absent value, `BuildField` fills one field and returns a
  builder whose type records it, and `FinalizeBuild` converts an all-present record. Finalization is
  separate because each `BuildField` impl is generic in the other fields' markers and cannot know it
  is last, which avoids a combinatorial explosion of impls.
- **Merging:** `IntoBuilder` turns a struct into an all-present partial record, `TakeField` removes
  one field returning the value and a remainder, and `HasFields` exposes the field list.
  `CanBuildFrom` recurses over the list through a private `FieldsBuilder` helper until `Nil`, traced
  type by type for `Employee::builder().build_from(person)`.
- **Builder dispatchers:** `BuildWithHandlers` initializes an empty partial record, pipes it through
  handlers with `PipeHandlers`, as Hypershell does, and finalizes; `BuildAndMerge` and
  `BuildAndSetField` adapt a provider to contribute a record or one field, `MapFields` maps a
  type-level list, and `BuildAndMergeOutputs` is assembled from them.
- **Hiding a constraint:** when a type alias would leak an internal constraint to its callers, define
  the wrapper as a provider struct and hide the constraint behind a `DelegateComponent` impl with
  `delegate_components!`.

## How it relates to the knowledge base

- **Concept and traits:** [extensible records](../../cgp/concepts/extensible-records.md);
  [`HasField`](../../cgp/reference/traits/has_field.md),
  [`HasFields`](../../cgp/reference/traits/has_fields.md),
  [`HasBuilder`](../../cgp/reference/traits/has_builder.md),
  [`MapType`](../../cgp/reference/traits/map_type.md),
  [`AppendProduct` / `MapFields`](../../cgp/reference/traits/product_ops.md), and
  [`CanBuildFrom`](../../cgp/reference/traits/cast.md); the list types
  [`Cons` / `Nil`](../../cgp/reference/types/cons.md) and [`Field`](../../cgp/reference/types/field.md).
- **Dispatchers and derive:** the [dispatch
  combinators](../../cgp/reference/providers/dispatch_combinators.md), the [handler
  combinators](../../cgp/reference/providers/handler_combinators.md), and
  [`#[derive(BuildField)]`](../../cgp/reference/derives/derive_build_field.md), now reached through
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md).
- **The arguments:** constraint propagation is the missing *why* behind
  [higher-order providers](../../cgp/concepts/higher-order-providers.md) and
  [type-level DSLs](../../cgp/concepts/type-level-dsls.md): representing computations as types is the
  only way to compose constraint-carrying functions without constraint kinds. The constraint-hiding
  technique is the reasoning behind [aggregate providers](../../cgp/concepts/aggregate-providers.md).

## Where it diverges from CGP v0.8.0

- **`PartialPerson` is now `__PartialPerson`.** v0.5.0 added the `__Partial` prefix to keep generated
  types out of the user's namespace; every partial-record name here lacks it.
- **`BuildField` is no longer a primitive.** v0.5.0 introduced `UpdateField`, and `BuildField` became a
  blanket impl over it, turning an `IsNothing` field into `IsPresent`; the post's base operation is one
  layer out of date.
- **The `MapType` markers gained `IsOptional`** in v0.5.0, with the optional builder and
  `finalize_with_default`; see [optional fields](../../cgp/reference/traits/optional_fields.md). The
  post lists these as future work.
- **`#[derive(BuildField)]` alone is no longer the usual derive**, superseded by
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md).
- **Every provider is inside-out**, with `#[cgp_provider]`/`#[cgp_new_provider]` rather than
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md).
- **The "future extensions" have largely shipped**: defaults, overriding, and the optional builder
  arrived in v0.5.0, so read that section as a historical wish list, not current gaps.
- **One typo:** the `build_from` walkthrough annotates the final `.finalize_build()` with `// Person`
  where the value built is an `Employee`.

## Maintaining it

Leave it alone. Its trait signatures are close enough to current to pass for reference documentation,
which is why the divergences matter: take current shapes from
[extensible records](../../cgp/concepts/extensible-records.md) and the trait references.
