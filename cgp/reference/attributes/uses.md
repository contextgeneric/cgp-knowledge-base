# `#[uses(...)]`

`#[uses(...)]` adds `Self` trait bounds to a provider's `where` clause, written to read like a `use` import of the traits the body depends on.

## Purpose

`#[uses(...)]` makes impl-side dependencies look like imports rather than trait bounds. A provider often calls methods of traits defined elsewhere, such as another [`#[cgp_fn]`](../macros/cgp_fn.md) trait, a [`#[cgp_component]`](../macros/cgp_component.md) consumer trait, or an ordinary trait such as `Display`, and to do so it must require the context to implement them. In plain Rust that is a `where Self: SomeTrait` clause, which is uncommon in everyday code and reads as machinery rather than intent.

`#[uses(RectangleArea)]` instead reads as "this function uses the `RectangleArea` trait", mirroring a `use` statement that brings a name into scope. The attribute lists the traits the body relies on, and the macro turns them into a `Self` bound on the generated impl, so the body can call their methods on `self` as if they had been imported. That is why `#[uses]` is recommended over hand-written `Self` bounds: it states what the provider needs in the vocabulary of imports.

## Syntax

`#[uses(...)]` takes a comma-separated list of trait bounds:

```rust
#[uses(RectangleArea, CanCalculateArea)]
```

Each entry names a trait, optionally with generic arguments: `RectangleArea` becomes `Self: RectangleArea`, and `CanCompute<Code, Input>` becomes `Self: CanCompute<Code, Input>`. The trait need not be a CGP construct; `#[uses(Display)]` and `#[uses(AsRef<[u8]>)]` are accepted and preferred over the equivalent `where Self:` clauses. It also need not matter how the trait was defined, whether with [`#[cgp_fn]`](../macros/cgp_fn.md), [`#[cgp_component]`](../macros/cgp_component.md), or by hand.

List a provider's dependencies in one attribute, as `#[uses(RectangleArea, CanCalculateArea)]`, so they read as a single import list. Entries split across several `#[uses(...)]` attributes on one item accumulate too, but reserve a second attribute for a real reason rather than as the default.

The idiomatic entry is the simple `Trait<Params>` form, but an entry may be any bound a `where` clause accepts on `Self`, including an associated-type equality (`HasErrorType<Error = anyhow::Error>`) or a higher-ranked bound, and it lands on the impl verbatim. Use that generality sparingly. To pin an abstract type to a concrete one, prefer [`#[use_type]`](use_type.md)'s equality form, `#[use_type(HasErrorType.{Error = anyhow::Error})]`, which adds the bound and also rewrites bare mentions of the type. To place a bound on a generated trait rather than only its impl, use [`#[extend_where]`](extend_where.md) on `#[cgp_fn]`.

`#[uses(...)]` is accepted on [`#[cgp_fn]`](../macros/cgp_fn.md) and [`#[cgp_impl]`](../macros/cgp_impl.md), the two hosts with an impl to attach bounds to. It is not accepted on [`#[cgp_component]`](../macros/cgp_component.md), where a trait dependency is a supertrait written with [`#[extend]`](extend.md).

## Syntax Grammar

The attribute argument is a comma-separated list of bounds:

```ebnf
UsesArgs -> TypeParamBound ( `,` TypeParamBound )* `,`?
```

`TypeParamBound` is the Rust grammar's bound production, wider than the `Trait<Args>` form the attribute is normally written with: a lifetime, a `?Sized`, and an associated-type equality all parse, though Rust itself rejects some of them as a bound on `Self`. The list may be empty, and entries from every occurrence of the attribute are collected before the bound is built, so `#[uses(A, B)]` and `#[uses(A)] #[uses(B)]` emit the same thing.

## Expansion

`#[uses(...)]` adds one `Self` predicate for the listed bounds to the generated impl's `where` clause, and changes nothing about the trait definition. Given two `#[cgp_fn]` traits where the second depends on the first:

```rust
#[cgp_fn]
fn rectangle_area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
    width * height
}

#[cgp_fn]
#[uses(RectangleArea)]
fn scaled_rectangle_area(&self, #[implicit] scale_factor: f64) -> f64 {
    self.rectangle_area() * scale_factor * scale_factor
}
```

the second definition's trait is unchanged, and its impl gains a `Self: RectangleArea` predicate beside the `HasField` bound of the implicit `scale_factor` argument:

```rust
pub trait ScaledRectangleArea {
    fn scaled_rectangle_area(&self) -> f64;
}

impl<__Context__> ScaledRectangleArea for __Context__
where
    Self: RectangleArea,
    Self: HasField<Symbol!("scale_factor"), Value = f64>,
{
    fn scaled_rectangle_area(&self) -> f64 {
        let scale_factor: f64 =
            self.get_field(PhantomData::<Symbol!("scale_factor")>).clone();

        self.rectangle_area() * scale_factor * scale_factor
    }
}
```

The bound lands on the impl only, never on the trait: it is an impl-side dependency, hidden from anyone who merely uses `ScaledRectangleArea`. So `#[uses(RectangleArea)]` means the same as `where Self: RectangleArea` written on the function, differing only in where the predicate sits in the `where` clause, as [`#[cgp_fn]`](../macros/cgp_fn.md#expansion) records. On `#[cgp_fn]`, the `#[uses]` bounds share one `Self:` predicate with any [`#[extend]`](extend.md) bounds.

Inside [`#[cgp_impl]`](../macros/cgp_impl.md) the behavior is the same: the bounds are added to the impl's `where` clause as a `Self` predicate, and the provider rewrite then turns `Self` into the context. So a provider can import a `#[cgp_fn]` trait and call it:

```rust
#[cgp_impl(new RectangleAreaCalculator)]
#[uses(RectangleArea)]
impl AreaCalculator {
    fn area(&self) -> f64 {
        self.rectangle_area()
    }
}
```

This adds `__Context__: RectangleArea` to the `RectangleAreaCalculator` impl and its `IsProviderFor` impl, so `area` can call `self.rectangle_area()`, and a check reports the dependency by name when a context lacks it.

## Examples

`#[uses(...)]` is the natural way to build an operation on a CGP component. Given an `AreaCalculator` component, a scaled-area function imports its consumer trait without knowing which provider a context wires:

```rust
use cgp::prelude::*;

#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_fn]
#[uses(CanCalculateArea)]
pub fn scaled_area(&self, #[implicit] scale_factor: f64) -> f64 {
    self.area() * scale_factor * scale_factor
}
```

The attribute adds `Self: CanCalculateArea` to the generated `ScaledArea` impl, so the body may call `self.area()`. Any context that implements `CanCalculateArea`, through whatever `AreaCalculator` provider it wires, gains `scaled_area`, because the dependency is on the consumer trait rather than on a provider.

## Related constructs

These constructs are the ones `#[uses]` works with:

- [`#[extend]`](extend.md) — the `pub use` counterpart: it adds public supertraits where `#[uses]` adds hidden impl-side bounds.
- [`#[cgp_fn]`](../macros/cgp_fn.md) and [`#[cgp_impl]`](../macros/cgp_impl.md) — the two hosts.
- [`#[use_type]`](use_type.md) — imports an abstract associated type, and pins one with its equality form.
- [`#[use_provider]`](use_provider.md) — the counterpart for an inner provider's bound in a higher-order provider.
- [`#[implicit]`](implicit.md) — brings in a context field as an argument.
- [`#[extend_where]`](extend_where.md) — makes a bound part of a `#[cgp_fn]` trait's definition.

## Source

- Parsing: [crates/macros/cgp-macro-core/src/types/attributes/uses.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/uses.rs) (the `UsesAttributes` type).
- Dispatch: [crates/macros/cgp-macro-core/src/types/attributes/function.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/function.rs) for `#[cgp_fn]` and [crates/macros/cgp-macro-core/src/types/attributes/cgp_impl_attributes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/cgp_impl_attributes.rs) for `#[cgp_impl]`.
- Injection: the impl `where` clause is built in [crates/macros/cgp-macro-core/src/types/cgp_fn/preprocessed.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_fn/preprocessed.rs) and [crates/macros/cgp-macro-core/src/types/cgp_impl/item.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_impl/item.rs).
- Implementation document (the internal AST type, what the attribute injects into each host, and the index of tests and snapshots): [implementation/asts/attributes/uses.md](../../implementation/asts/attributes/uses.md).
