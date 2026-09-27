# `#[extend_where(...)]`

`#[extend_where(...)]` adds `where` predicates to the trait a [`#[cgp_fn]`](../macros/cgp_fn.md)
generates, so a bound becomes part of the trait's definition rather than only its implementation.

## Purpose

`#[extend_where(...)]` puts a `where` clause on the trait a `#[cgp_fn]` generates, not only on its
impl. By default `#[cgp_fn]` treats the function's own `where` clause as impl-side dependencies: the
predicates go on the generated impl and stay out of the trait. That is usually right, but sometimes
a bound belongs on the trait itself, such as a constraint on one of the trait's generic parameters
that anyone naming the trait must meet. `#[extend_where(...)]` promotes such a predicate onto the
trait.

It complements [`#[extend]`](extend.md). `#[extend(...)]` adds supertrait bounds, as in
`pub trait Foo: Bar`, and `#[extend_where(...)]` adds `where` predicates, as in
`pub trait Foo where T: Bar`. Both put a requirement on the trait; they differ in which position the
bound occupies, and so in what the bound can say.

## Syntax

`#[extend_where(...)]` takes a comma-separated list of full `where` predicates:

```rust
#[extend_where(Scalar: Clone)]
```

Each entry names its own subject. [`#[uses]`](uses.md) and [`#[extend]`](extend.md) take bounds and
attach them to `Self`, while `#[extend_where(...)]` takes predicates on any type, including
associated-type equalities, higher-ranked predicates, and bounds on the trait's generic parameters.
Several predicates may be listed in one attribute or spread across several, and they accumulate.

`#[extend_where(...)]` is read only by [`#[cgp_fn]`](../macros/cgp_fn.md), the one host whose
written `where` clause is kept off the trait it generates.
[`#[cgp_component]`](../macros/cgp_component.md) needs no equivalent, because a `where` clause
written on its trait is already part of the trait, and [`#[cgp_impl]`](../macros/cgp_impl.md)
generates no trait at all. On either host the attribute is not collected and reaches the compiler as
``cannot find attribute `extend_where` in this scope``.

## Syntax Grammar

The attribute argument is a comma-separated list of `where` predicates:

```ebnf
ExtendWhereArgs -> WherePredicate ( `,` WherePredicate )* `,`?
```

`WherePredicate` is the Rust grammar's production for one entry of a `where` clause, and it is what
distinguishes this attribute from [`#[uses]`](uses.md) and [`#[extend]`](extend.md). Those take a
bound and attach it to `Self`, whereas a predicate names its own subject, so
`#[extend_where(Self::Output: Clone)]` and a higher-ranked
`#[extend_where(for<'a> &'a T: IntoIterator)]` can be written here and not there. The list may be
empty.

## Expansion

`#[extend_where(...)]` adds its predicates to the generated trait's `where` clause, and the same
predicates also appear on the impl, after the `#[extend]` and `#[uses]` bounds and before the
implicit-argument bounds. Given a generic `#[cgp_fn]` definition:

```rust
#[cgp_fn]
#[extend_where(Scalar: Clone)]
fn rectangle_area<Scalar>(
    &self,
    #[implicit] width: Scalar,
    #[implicit] height: Scalar,
) -> Scalar
where
    Scalar: Mul<Output = Scalar>,
{
    width * height
}
```

the macro emits a trait whose own `where` clause carries `Scalar: Clone`:

```rust
pub trait RectangleArea<Scalar>
where
    Scalar: Clone,
{
    fn rectangle_area(&self) -> Scalar;
}
```

The `Scalar: Mul<Output = Scalar>` predicate from the function's own `where` clause stays an
impl-side dependency, on the impl only. The `Scalar: Clone` predicate is the one promoted to the
trait, and it is repeated on the impl, which must meet whatever the trait requires.

## Examples

`#[extend_where(...)]` fits a generic parameter of a `#[cgp_fn]` trait that needs a visible bound.
The example above has the typical shape: a `Scalar`-generic area function whose trait requires
`Scalar: Clone` while keeping the multiplication bound on the impl.

What the promotion buys is enforcement where the trait is named, not a bound that callers inherit,
and the two are easy to confuse. A trait's `where` clause is a precondition on naming the trait, not
a fact made available to code that holds it. So a caller generic over `Scalar` must still write
`Scalar: Clone` in its own `where` clause, and naming `RectangleArea<NoClone>` for a type without
`Clone` is rejected with `E0277` and a `required by a bound in RectangleArea` note. Left on the impl
alone, the same unsatisfiable bound would be accepted silently: an impl-side bound only decides
where the impl applies, so `Ctx: RectangleArea<NoClone>` would be a predicate nothing can prove, and
nothing would complain until a concrete context was supplied. Removing that silence is the reason to
promote a predicate. Sparing callers a bound is not, and only a supertrait added with
[`#[extend]`](extend.md) does that.

## Related constructs

These constructs are the ones `#[extend_where]` works with:

- [`#[extend]`](extend.md): the supertrait sibling: both put a requirement on the generated trait.
- [`#[cgp_fn]`](../macros/cgp_fn.md): the only host, since only there is the written `where` clause
  kept off the trait.
- [`#[uses]`](uses.md): adds hidden impl-side bounds instead of trait-visible ones.
- [`#[impl_generics]`](impl_generics.md): the opposite placement, a parameter on the impl alone.

## Source

- Parsing: the `extend_where` field of `FunctionAttributes` in
  [crates/macros/cgp-macro-core/src/types/attributes/function.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/function.rs).
- Injection: the predicates are added to both the trait and the impl `where` clauses in
  [crates/macros/cgp-macro-core/src/types/cgp_fn/preprocessed.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_fn/preprocessed.rs).
- Implementation document (what the attribute injects into its host and the index of tests and
  snapshots):
  [implementation/asts/attributes/extend_where.md](../../implementation/asts/attributes/extend_where.md).
