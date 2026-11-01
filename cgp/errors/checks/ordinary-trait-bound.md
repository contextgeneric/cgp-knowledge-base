# Unsatisfied ordinary trait bound

A provider's impl-side dependency is an *ordinary* Rust trait bound (a standard-library, foreign, or
plain user trait such as `Eq`, `Clone`, `Ord`, or `From<X>`, not a CGP trait) and the concrete type
the context supplies for an abstract type or generic parameter does not implement it, so a check
surfaces the failure as `E0277` naming that ordinary bound.

## What triggers it

This class is the ordinary-trait cousin of a [check-trait failure](check-trait-failure.md): the
mechanism is the same lazy wiring, but the unmet leaf is a plain Rust trait rather than a `HasField`
or a CGP component. A provider lists a `where`-clause bound that is an ordinary trait applied to an
abstract type or an impl generic (`Scalar: Eq`, `Item: Ord`, `T: Clone`) and the context wires a
concrete type that does not satisfy it. Because
[wiring](../../reference/macros/delegate_components.md) is lazy, the entry is accepted without
checking the bound; it fails only when the wiring is exercised.

The canonical case is an ordinary bound on an abstract type. `CompareScalars` needs the context's
`Scalar` type to be `Eq`, and the context wires `Scalar` to `f64`, which is `PartialEq` but not
`Eq`:

```rust
#[cgp_type]
pub trait HasScalarType {
    type Scalar;
}

#[cgp_component(ScalarEquality)]
#[use_type(HasScalarType.Scalar)]
pub trait CanCompareScalars {
    fn scalars_equal(&self, a: &Scalar, b: &Scalar) -> bool;
}

#[cgp_impl(new CompareScalars)]
#[use_type(HasScalarType.Scalar)]
impl ScalarEquality
where
    Scalar: Eq, // ordinary trait bound — rewritten to <Self as HasScalarType>::Scalar: Eq
{
    fn scalars_equal(&self, a: &Scalar, b: &Scalar) -> bool {
        a == b
    }
}

delegate_components! {
    App {
        ScalarTypeProviderComponent: UseType<f64>, // f64: !Eq
        ScalarEqualityComponent: CompareScalars,
    }
}
```

The same failure arises wherever CGP or Rust accepts a generic trait bound, which is what makes the
class broad. An ordinary bound on an **impl generic** in `delegate_components!` behaves identically:
a generic context `<T> Wrapper<T>` that wires its abstract type to `T` carries the provider's
`Scalar: Eq` bound as `T: Eq`, unconditionally accepted, and checking `Wrapper<f64>` surfaces
`f64: Eq` at that one instantiation. The bound may equally sit on an explicit `impl<T>` generic in
`#[cgp_impl]`, on a `#[cgp_fn]` `#[extend_where]` clause, or on a `for … in … where` loop: anywhere
an ordinary bound rides on a parameter the context ultimately fills. CGP lowers the bound faithfully
and cannot see that the wired type violates it, so it defers to the compiler.

## The raw diagnostic

This section describes plain `cargo check`, the fallback when `cargo-cgp` is not on hand. This is a
**surfaced** class, and the **primary** error is the leaf itself: `` the trait bound `f64: Eq` is not satisfied ``,
with the caret on the checked entry labelled `` the trait `Eq` is not implemented for `f64` ``. Beneath it,
a `help:` lists the standard types that implement the trait (`i128`, `i16`, `i32`, …), rather than the
"but trait `HasField<other>` is implemented" hint a missing field produces.

The position of the cause tells this class from a [check-trait failure](check-trait-failure.md). A missing
`HasField` roots the primary error at `Ctx: CanUseComponent<Component>` and puts the leaf in a `help:`. An
ordinary bound roots it at the leaf, and `CanUseComponent` appears only in a `note`. The scaffolding between
is the same: `` required for `CompareScalars` to implement `IsProviderFor<ScalarEqualityComponent, App>` ``,
pointing at the `Scalar: Eq` bound, then `CanUseComponent`, then the bound in the generated `__CheckApp`
trait.

Exercised by calling the consumer method, the same wiring produces the
[hidden `E0599`](../hidden/unsatisfied-dependency.md), which never mentions `f64: Eq`, because the method probe
drops a nested bound of any kind.

## Where the root cause is

The root cause is **present at the very top** of the checked output, and the caret lands on the checked entry.
The diagnostic does not say which wired type is at fault when the bound is on an abstract type: the leaf names
`f64` and a note names `Scalar: Eq`, so the reader connects them through the
`ScalarTypeProviderComponent: UseType<f64>` wiring.

## How cargo-cgp presents it

`cargo-cgp` **keeps rustc's headline uncoded**, ``error[E0277]: the trait bound `f64: Eq` is not satisfied``,
since it already states the cause. It rewrites the scaffolding below into a dependency tree: `[CGP-E101]`
consumer hop, `[CGP-E102]` provider hop, then ``[CGP-E117] the trait bound `f64: Eq` is not satisfied``. This
is the one surfaced check class without a `[CGP-E0xx]` headline.

The [hidden method-call form](../hidden/unsatisfied-dependency.md) differs: its raw `E0599` buries the bound, so
the tool recovers it under `[CGP-E001]` over a ``root cause: [CGP-E117] the trait bound `f64: Eq` is not satisfied``
tree. The [cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) defines the codes.

The tree stops at the bound, without saying that `f64` is what `Scalar` resolves to, so following the
abstract-type component to its `UseType<…>` entry remains the reader's step.

## Resolving it

Make the concrete type satisfy the trait. Wire the abstract type, or instantiate the generic, to a type that
does (an integer for `Eq` instead of `f64`), or derive or implement the trait on a type you own. When the bound
is stricter than the behavior needs, relax the provider's `where` clause.

## Backing fixtures

- [`checks/ordinary-trait-bound/ordinary_bound_unsatisfied.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/ordinary-trait-bound/ordinary_bound_unsatisfied.rs):
  `Scalar: Eq` on a context wiring `Scalar` to `f64`, checked; the headline stays uncoded over the tree.
- [`checks/ordinary-trait-bound/generic_context_ordinary_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/ordinary-trait-bound/generic_context_ordinary_bound.rs):
  the same through impl generics: `<T> Wrapper<T>` checked at `Wrapper<f64>`.
- [`checks/ordinary-trait-bound/borrowed_detail.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/ordinary-trait-bound/borrowed_detail.rs):
  wrapping an error with a borrowed detail through a wrapper that needs `'static` details.

The hidden (method-call) form of the same mistake is
[`hidden/unsatisfied-dependency/ordinary_bound_unsatisfied_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/ordinary_bound_unsatisfied_call.rs),
cataloged with the [hidden unsatisfied dependency](../hidden/unsatisfied-dependency.md) class.

## Related

- [Check-trait failure (surfaced)](check-trait-failure.md): the sibling surfaced class whose leaf is
  a CGP trait (`HasField`, a component); contrast the leaf's *kind* (an ordinary trait here) and its
  *position* (the primary error here, a `help:` note there).
- [Unsatisfied dependency (hidden)](../hidden/unsatisfied-dependency.md): the `E0599` form this
  takes when reached by a method call, where the ordinary bound is suppressed just like any other
  leaf.
- [Verbose dependency cascade](verbose-cascade.md): when several providers share the unmet ordinary
  bound, this diagnostic multiplies the same way.
- [`E0277`](../error_codes/e0277.md): the Rust error code this class is reported under, and its
  `Sized` special case.
- [`#[use_type]`](../../reference/attributes/use_type.md),
  [`#[cgp_type]`](../../reference/macros/cgp_type.md), and
  [`check_components!`](../../reference/macros/check_components.md): the abstract-type import, the
  abstract-type component, and the check that surfaces the bound.
- [Debugging CGP compile errors](../../guides/debugging.md): the `E0277` entry in the decoder.
