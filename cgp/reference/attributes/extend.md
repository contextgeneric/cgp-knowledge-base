# `#[extend(...)]`

`#[extend(...)]` adds the given trait bounds as supertraits of the generated trait, making them a
public part of the trait's interface rather than a hidden impl-side dependency.

## Purpose

`#[extend(...)]` adds supertraits to a CGP trait through an import-like attribute. A supertrait is a
bound every implementor must satisfy and every user may rely on. In
[`#[cgp_fn]`](../macros/cgp_fn.md), the function's own `where` clause becomes impl-side dependencies
and stays out of the generated trait, so there is no place to write a supertrait by hand;
`#[extend(...)]` fills that gap by putting its bounds on the trait itself.

The contrast with [`#[uses]`](uses.md) is the point. Both accept the same bound syntax and both read
like imports, but they import into different places. `#[uses(...)]` adds a hidden bound to the impl
only, a private dependency callers never see. `#[extend(...)]` adds a supertrait to the trait, a
public requirement that becomes part of the contract. So `#[extend(...)]` is the `pub use` of
`#[uses(...)]`: one imports a trait for the implementation's own use, and the other re-exports it as
part of what the trait guarantees.

The pairing also decides which supertraits `#[extend(...)]` is for:

- **A method supertrait**, such as `HasName` or `CanCalculateArea`, that a trait depends on without
  naming its associated types in its own signatures. This is what `#[extend]` is for. In
  [`#[cgp_component]`](../macros/cgp_component.md), prefer `#[extend(HasName)]` over the native
  `pub trait CanGreet: HasName`: the native `:` syntax reads as inheritance from a parent class to
  programmers from object-oriented languages, while `#[extend]` reads as the trait import a CGP
  supertrait actually is. In `#[cgp_fn]`, `#[extend]` is the only way to add a method supertrait.
- **An abstract-type component** whose associated type the signatures use, such as
  [`HasErrorType`](../components/has_error_type.md) through its `Error`. Prefer
  [`#[use_type]`](use_type.md) for these; it adds the supertrait and also rewrites the bare type
  name.

## Syntax

`#[extend(...)]` takes a comma-separated list of trait bounds, usually in the simple form
`Trait<Params>`:

```rust
#[extend(HasName)]
```

Each entry becomes a supertrait of the generated trait, carrying any generic arguments through.
Several bounds may be listed in one attribute or spread across several `#[extend(...)]` attributes,
and they accumulate.

`#[extend(...)]` is accepted on [`#[cgp_fn]`](../macros/cgp_fn.md), on
[`#[cgp_component]`](../macros/cgp_component.md), and on the macros that share its attribute
collector: [`#[cgp_type]`](../macros/cgp_type.md), [`#[cgp_getter]`](../macros/cgp_getter.md), and
[`#[cgp_auto_getter]`](../macros/cgp_auto_getter.md). It is not accepted on
[`#[cgp_impl]`](../macros/cgp_impl.md), because a provider impl has no trait definition of its own;
its supertraits belong to the component's trait. There the attribute is passed through untouched and
fails with ``cannot find attribute `extend` in this scope``, and since the bound never reaches the
impl, a body calling the supertrait's method fails beside it with `E0599` (the method exists but its
trait bounds were not satisfied). Moving the bound to [`#[uses]`](uses.md), or onto the component's
trait, fixes both.

## Syntax Grammar

The attribute argument is a comma-separated list of bounds:

```ebnf
ExtendArgs -> TypeParamBound ( `,` TypeParamBound )* `,`?
```

This is the production [`#[uses]`](uses.md) accepts, the Rust `TypeParamBound`, so a lifetime, a
`?Sized`, or an associated-type equality parses as readily as a trait name, though Rust rejects a
relaxed supertrait: `#[extend(?Sized)]` fails with
`relaxed bounds are not permitted in supertrait bounds`. The list may be empty,
and every occurrence's entries are collected together. The two attributes differ in where the bounds
land, not in what they accept.

## Expansion

On `#[cgp_fn]`, `#[extend(...)]` adds each bound as a supertrait of the generated trait, and the
same bound appears on the impl's `where` clause so the implementation can rely on it. The example
below uses an abstract-type trait, `HasScalarType`, because it makes both placements visible in one
signature; in real code such a supertrait is better declared with [`#[use_type]`](use_type.md), and
`#[extend]` kept for method supertraits. Given:

```rust
pub trait HasScalarType {
    type Scalar: Clone + Mul<Output = Self::Scalar>;
}

#[cgp_fn]
#[extend(HasScalarType)]
fn rectangle_area(
    &self,
    #[implicit] width: Self::Scalar,
    #[implicit] height: Self::Scalar,
) -> Self::Scalar {
    width * height
}
```

the macro emits a trait with `HasScalarType` as a supertrait, and an impl requiring both
`Self: HasScalarType` and the `HasField` bounds of the implicit arguments:

```rust
pub trait RectangleArea: HasScalarType {
    fn rectangle_area(&self) -> Self::Scalar;
}

impl<__Context__> RectangleArea for __Context__
where
    Self: HasScalarType,
    Self: HasField<Symbol!("width"), Value = Self::Scalar>
        + HasField<Symbol!("height"), Value = Self::Scalar>,
{
    fn rectangle_area(&self) -> Self::Scalar {
        let width: Self::Scalar =
            self.get_field(PhantomData::<Symbol!("width")>).clone();
        let height: Self::Scalar =
            self.get_field(PhantomData::<Symbol!("height")>).clone();

        width * height
    }
}
```

The two placements each have a job. On the trait, the supertrait makes `Self::Scalar` resolve and
tells callers that every `RectangleArea` is also a `HasScalarType`. On the impl, it lets the
implementation use the associated type. This double placement is the difference from
[`#[uses]`](uses.md), which adds to the impl only. On `#[cgp_fn]`, the `#[extend]` bounds share one
`Self:` predicate with any `#[uses]` bounds.

On [`#[cgp_component]`](../macros/cgp_component.md), `#[extend(...)]` is exactly equivalent to
writing the supertrait natively. The definition

```rust
#[cgp_component(Greeter)]
#[extend(HasName)]
pub trait CanGreet {
    fn greet(&self);
}
```

is the same as `pub trait CanGreet: HasName`. The component macro then treats the supertrait as it
treats any: it stays on the consumer trait and becomes a `Context: HasName` predicate on the
provider trait and on every generated impl, as
[`#[cgp_component]`](../macros/cgp_component.md#expansion) shows. Because a trait's `where` bound is
not implied for its implementations, every provider of the component must prove `Context: HasName`
itself: a `#[cgp_impl]` provider for `Greeter` without `#[uses(HasName)]` fails at its own
definition with ``E0277 the trait bound `__Context__: HasName` is not satisfied``, whether or not its
body calls `name()`. So `#[extend]` guarantees the supertrait to callers of `CanGreet`, not to the
providers that implement it. Although `#[extend]` generates nothing the language cannot already
spell here, it is still the preferred form, because it presents
the bound as an import and keeps the `use`/`pub use` pairing with `#[uses]` consistent.

## Examples

This `#[cgp_fn]` trait depends on an abstract type the context provides, so it works for any context
that defines a `Scalar` type and has `width` and `height` fields of that type:

```rust
use cgp::prelude::*;
use core::ops::Mul;

pub trait HasScalarType {
    type Scalar: Clone + Mul<Output = Self::Scalar>;
}

#[cgp_fn]
#[extend(HasScalarType)]
pub fn rectangle_area(
    &self,
    #[implicit] width: Self::Scalar,
    #[implicit] height: Self::Scalar,
) -> Self::Scalar {
    width * height
}

#[derive(HasField)]
pub struct Rectangle {
    pub width: f64,
    pub height: f64,
}

impl HasScalarType for Rectangle {
    type Scalar = f64;
}
```

Because `HasScalarType` is a supertrait of `RectangleArea`, `Self::Scalar` is usable in the
signature and body. `Rectangle` implements `HasScalarType` with `Scalar = f64` and derives
`HasField` for both fields, so it satisfies every bound and gains `rectangle_area`.

## Related constructs

These constructs are the ones `#[extend]` works with:

- [`#[uses]`](uses.md): the `use` counterpart, adding hidden impl-side bounds with the same syntax.
- [`#[cgp_fn]`](../macros/cgp_fn.md) and [`#[cgp_component]`](../macros/cgp_component.md): the main
  hosts; `#[cgp_type]`, `#[cgp_getter]`, and `#[cgp_auto_getter]` accept it too.
- [`#[use_type]`](use_type.md): the preferred form for an abstract-type supertrait, which also
  rewrites the bare type name.
- [`#[extend_where]`](extend_where.md): adds `where` predicates, rather than supertraits, to a
  `#[cgp_fn]` trait.

## Source

- Parsing: for `#[cgp_fn]` in
  [crates/macros/cgp-macro-core/src/types/attributes/function.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/function.rs)
  (the `extend` field of `FunctionAttributes`); for `#[cgp_component]` and the macros built on it in
  [crates/macros/cgp-macro-core/src/types/attributes/cgp_component_attributes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/cgp_component_attributes.rs),
  which appends the bounds to the trait's supertraits.
- For `#[cgp_fn]`: the bounds are added to the trait's supertraits and the impl's `where` clause in
  [crates/macros/cgp-macro-core/src/types/cgp_fn/preprocessed.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_fn/preprocessed.rs).
- Implementation document (what the attribute injects into each host and the index of tests and
  snapshots):
  [implementation/asts/attributes/extend.md](../../implementation/asts/attributes/extend.md).
