# `#[use_provider]`

`#[use_provider]` writes the bound of a higher-order provider's inner provider for you, filling in
the context argument that a provider trait adds at its first position.

## Purpose

`#[use_provider]` keeps higher-order providers looking like ordinary providers. A higher-order
provider takes another provider as a generic parameter and delegates part of its work to it, such as
a `ScaledAreaCalculator` that multiplies whatever an `InnerCalculator` computes. Provider traits
move the original `Self` into a leading `Context` parameter, so the inner provider must be bound as
`InnerCalculator: AreaCalculator<Self>`, not `InnerCalculator: AreaCalculator`. That extra `<Self>`
surprises a reader, because the consumer trait it mirrors has no such parameter.

`#[use_provider]` lets the author leave it out. Writing
`#[use_provider(InnerCalculator: AreaCalculator)]` adds the `Self` argument and puts the completed
bound in the impl's `where` clause, so the source says `InnerCalculator: AreaCalculator` while the
generated code says `InnerCalculator: AreaCalculator<Self>`. This keeps the provider trait reading
like the consumer trait it came from, and it is the idiomatic way to declare a higher-order
provider's inner dependency.

The attribute supplies only the bound. The body still calls the inner provider as an associated
function, `InnerCalculator::area(self)`, passing the context explicitly, because the inner provider
is named directly rather than reached through the context's wiring. Calling `self.area()` instead
would dispatch to whatever provider the context itself wires for `AreaCalculator`, which is usually
not what a higher-order provider means.

## Syntax

`#[use_provider]` is an attribute on a [`#[cgp_impl]`](../macros/cgp_impl.md) or
[`#[cgp_fn]`](../macros/cgp_fn.md) definition. It takes a provider type, a colon, and one or more
provider-trait bounds joined by `+`:

```rust
#[use_provider(InnerCalculator: AreaCalculator)]
```

`InnerCalculator` is the provider type, usually a generic parameter of the impl, and
`AreaCalculator` is the provider trait whose context argument the macro fills in. The trait may
carry further generic arguments, which keep their order after the inserted `Self`.

One attribute binds one provider. Unlike [`#[uses]`](uses.md) and [`#[use_type]`](use_type.md), it
does not take a comma-separated list, because its bound list runs to the end of the attribute. The
two ways to express more are these:

- **Several bounds on one provider** are joined with `+`, as in
  `#[use_provider(Inner: TraitA + TraitB)]`.
- **Several providers** take one attribute each:

```rust
#[use_provider(A: AreaCalculator)]
#[use_provider(P: PerimeterCalculator)]
```

So stacking is the intended form here, not a fallback. Writing two pairs with a comma fails at the
comma with ``expected `+` ``, and leaving out the bound fails with ``expected `:` ``, since there is
no form without one.

On any other host, such as [`#[cgp_component]`](../macros/cgp_component.md), the attribute is not
collected and reaches the compiler as an unknown attribute.

## Syntax Grammar

The attribute argument is one provider type and the provider traits it must satisfy:

```ebnf
UseProviderArgs -> ProviderType `:` ( ProviderBound ( `+` ProviderBound )* `+`? )?

ProviderType    -> Type
ProviderBound   -> TypePath GenericArgs?
```

`ProviderType` is the type the inner provider occupies, and each `ProviderBound` is a provider trait
written without the leading context argument the attribute inserts. Two properties of these
productions explain every parse failure the attribute produces. A `ProviderBound` is a path with
plain generic arguments rather than a full `TypeParamBound`, so a turbofish or an associated-type
binding does not parse there and belongs in the host's own `where` clause. And the `+`-separated
list is parsed to the end of the attribute's input, so exactly one provider fits in one attribute
and a comma after the first pair reads as a missing `+`. The list may end with a `+`, and an empty
list parses to a vacuous bound.

## Expansion

`#[use_provider]` changes nothing in the body; it completes the bound and adds it to the `where`
clause. Take this higher-order provider, where `ScaledAreaCalculator` scales the area an inner
calculator produces:

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_impl(new ScaledAreaCalculator<InnerCalculator>)]
#[use_provider(InnerCalculator: AreaCalculator)]
impl<InnerCalculator> AreaCalculator {
    fn area(&self, #[implicit] scale_factor: f64) -> f64 {
        InnerCalculator::area(self) * scale_factor * scale_factor
    }
}
```

The attribute takes `InnerCalculator: AreaCalculator`, inserts `Self` as the trait's first argument,
and adds the result to the impl's `where` clause. After this step the impl is the same as writing
the `<Self>` by hand:

```rust
#[cgp_impl(new ScaledAreaCalculator<InnerCalculator>)]
impl<InnerCalculator> AreaCalculator
where
    InnerCalculator: AreaCalculator<Self>,
{
    fn area(&self, #[implicit] scale_factor: f64) -> f64 {
        InnerCalculator::area(self) * scale_factor * scale_factor
    }
}
```

The provider rewrite of [`#[cgp_impl]`](../macros/cgp_impl.md) then turns `Self` into the context,
and the bound reaches the provider's `IsProviderFor` impl as well. Because that bound names the
component's own provider trait, [`#[cgp_provider]`](../macros/cgp_provider.md) also adds the
matching `InnerCalculator: IsProviderFor<…>` bound, which is how a dependency missing inside the
inner provider surfaces through the wrapper.

`#[cgp_fn]` works the same way. Here a function binds a provider and calls it:

```rust
#[cgp_fn]
#[use_provider(RectangleAreaCalculator: AreaCalculator)]
fn rectangle_area(&self) -> f64 {
    RectangleAreaCalculator::area(self)
}
```

This expands to the blanket impl with the completed bound, where the macro supplied the `<Self>`:

```rust
trait RectangleArea {
    fn rectangle_area(&self) -> f64;
}

impl<__Context__> RectangleArea for __Context__
where
    RectangleAreaCalculator: AreaCalculator<Self>,
{
    fn rectangle_area(&self) -> f64 {
        RectangleAreaCalculator::area(self)
    }
}
```

In both hosts the body is untouched, so it calls the inner provider as an associated function and
passes `self` as the context.

## Examples

A complete higher-order provider starts from the base component and a concrete provider:

```rust
use cgp::prelude::*;

#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_impl(new RectangleAreaCalculator)]
impl AreaCalculator {
    fn area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
        width * height
    }
}
```

`ScaledAreaCalculator` then wraps any inner calculator and scales its result, declaring the inner
dependency with `#[use_provider]`:

```rust
#[cgp_impl(new ScaledAreaCalculator<InnerCalculator>)]
#[use_provider(InnerCalculator: AreaCalculator)]
impl<InnerCalculator> AreaCalculator {
    fn area(&self, #[implicit] scale_factor: f64) -> f64 {
        let base_area = InnerCalculator::area(self);
        base_area * scale_factor * scale_factor
    }
}
```

A context can now wire `AreaCalculatorComponent` to `ScaledAreaCalculator<RectangleAreaCalculator>`,
which computes the rectangle's area through `RectangleAreaCalculator` and scales it. The author
never wrote `InnerCalculator: AreaCalculator<Self>`. The
[area calculation](../../../examples/area-calculation.md) example develops this provider in full.

## Related constructs

These constructs are the ones `#[use_provider]` works with:

- [`#[cgp_impl]`](../macros/cgp_impl.md) and [`#[cgp_fn]`](../macros/cgp_fn.md): the two hosts.
- [`#[uses]`](uses.md): the counterpart for a bound on the context itself rather than on a separate
  provider.
- [Higher-order providers](../../concepts/higher-order-providers.md): the pattern this attribute
  serves.
- [`#[cgp_provider]`](../macros/cgp_provider.md): adds the `IsProviderFor` counterpart of an
  inner-provider bound.
- [`check_components!`](../macros/check_components.md): whose `#[check_providers(...)]` form checks
  each layer of a higher-order provider separately.

## Source

- Parsing: `UseProviderAttribute` in
  [crates/macros/cgp-macro-core/src/types/attributes/use_provider/attribute.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/use_provider/attribute.rs);
  its `to_type_param_bounds` inserts the context type as each trait's first argument, and
  `to_provider_bounds` builds the `where` predicate.
- Bound insertion: `add_type_param_bounds` in `attributes.rs`, which appends one predicate per
  attribute.
- Collection and application: collected for `#[cgp_impl]` in
  `types/attributes/cgp_impl_attributes.rs` and for `#[cgp_fn]` in `types/attributes/function.rs`,
  and applied in `types/cgp_impl/item.rs` and `types/cgp_fn/preprocessed.rs`.
- Implementation document (the internal AST type, the bound completion, and the index of tests and
  snapshots):
  [implementation/asts/attributes/use_provider.md](../../implementation/asts/attributes/use_provider.md).
