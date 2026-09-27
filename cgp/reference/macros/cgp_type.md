# `#[cgp_type]`

`#[cgp_type]` defines an abstract-type component, a trait carrying a single associated type, by
extending [`#[cgp_component]`](cgp_component.md) and generating the extra constructs that let a
context choose the concrete type through wiring, most notably a [`UseType`](../providers/use_type.md)
blanket impl.

## Purpose

`#[cgp_type]` makes associated types swappable across contexts the same way `#[cgp_component]` makes
behavior swappable. An abstract type in CGP is just a trait with one associated type, such as
`trait HasScalarType { type Scalar; }`, that lets generic code refer to `Self::Scalar` without
committing to a concrete type. On its own such a trait is wired like any other component, but
choosing the concrete type would otherwise mean writing a provider impl by hand for every type you
want to plug in. `#[cgp_type]` removes that friction.

**The macro's value is the extra constructs it layers on top of the component expansion.** Every
abstract-type provider follows the same trivial shape ("the associated type *is* this concrete
type"), so `#[cgp_type]` can generate that shape once and for all as a
[`UseType`](../providers/use_type.md) blanket impl. A context then names the concrete type directly
in its wiring (`UseType<String>`) instead of defining a bespoke provider. This is the same convenience
relationship that `#[cgp_getter]` has to `UseField`: a general-purpose provider parameterized by the
thing the context wants to supply.

Direct implementation remains available and is often the clearest choice. An abstract type can always
be implemented straight on a concrete context through its consumer trait, which is barely more verbose
than wiring `UseType`, and is the most transparent way to show that a CGP abstract type is nothing
more than a vanilla Rust trait with an associated type.

**Choose an abstract type deliberately.** A type that only flows through a field a provider reads
is better inferred with [`#[impl_generics]`](../attributes/impl_generics.md) on a `#[cgp_fn]`, which
declares and wires nothing; an abstract type is needed once the type must appear in a trait's own
signature, or once two traits must agree on it. A trait carrying a method beside the type it
produces is an ordinary [`#[cgp_component]`](cgp_component.md), and a type whose only job is to be a
getter's return type is shorter as an associated type on a
[`#[cgp_auto_getter]`](cgp_auto_getter.md) trait. [Naming a type
dependency](../../guides/naming-a-type-dependency.md) carries the full decision.

## Syntax

**The macro is applied to a trait that contains exactly one associated type and nothing else.** Any
other item count or kind fails with `type trait should contain exactly one associated type item`. The
associated type may carry bounds, but a generic associated type or one with a `where` clause fails
with `generic associated type and where clause are not supported`. The simplest form takes no
argument:

```rust
#[cgp_type]
pub trait HasScalarType {
    type Scalar;
}
```

Like `#[cgp_component]`, the component needs a provider trait name, and **`#[cgp_type]` derives one
from the associated type's name**, not the trait's. The default provider name is the associated type
name with a `TypeProvider` suffix, so `Scalar` yields the provider `ScalarTypeProvider` and the
component name `ScalarTypeProviderComponent`. You can override it by passing a provider name, as
with `#[cgp_component]`:

```rust
#[cgp_type(ProvideScalar)]
pub trait HasScalarType {
    type Scalar;
}
```

**A wiring key guessed from the trait name does not exist.** `HasScalarType` yields
`ScalarTypeProviderComponent`, not `HasScalarTypeComponent`, so an entry naming the latter fails
with ``E0425: cannot find type `HasScalarTypeComponent` in this scope``.

**The trait may carry generic parameters**, handled exactly as `#[cgp_component]` handles them: they
follow the context in the provider trait, enter the `IsProviderFor` params tuple, and extend the
`RedirectLookup` path, so a context chooses the type per parameter value through `open` or
[`#[derive_delegate]`](../attributes/derive_delegate.md).
`pub trait HasLabelType<Kind> { type Label; }` lets a context that declares
`open LabelTypeProviderComponent;` wire `@LabelTypeProviderComponent.u32: UseType<String>`. A
`?Sized` parameter is accepted and threaded through every item, though `open` cannot key an unsized
type, since a path segment must be sized. The companion attributes of `#[cgp_component]` apply
unchanged, so [`#[prefix(...)]`](../attributes/prefix.md) registers the abstract type into a
namespace, as CGP's own [`HasErrorType`](../components/has_error_type.md) does.

A bound on the associated type is preserved everywhere the type appears in the expansion. For
example, `type Scalar: Copy;` carries the `Copy` bound onto the generated provider trait and into the
`where` clauses of the generated provider impls.

**A self-referential bound is rewritten rather than rejected.** A bound that names the associated
type it constrains, as `type Scalar: Mul<Output = Self::Scalar> + Clone;` does, stays as written on
the consumer and provider traits, where `Self::Scalar` still means what it says. When the bound is
copied onto the `UseType` and `WithProvider` impls, every `Self::Scalar` inside it is rewritten to the
free parameter, so their `where` clause reads `Scalar: Mul<Output = Scalar> + Clone`. Without that
rewrite the copied bound would name an associated type of the wrong `Self`.

## Syntax Grammar

The attribute argument of `#[cgp_type]` uses the same grammar as
[`#[cgp_component]`](cgp_component.md)'s `CgpComponentArgs`: a bare provider name or the keyed
`name`/`provider`/`context` form.

```ebnf
CgpTypeArgs -> CgpComponentArgs    // see #[cgp_component]
```

The only difference from `#[cgp_component]` is the default applied when `provider` is omitted:
instead of failing, the macro derives the provider name from the *associated type's* name with a
`TypeProvider` suffix (so `type Scalar;` yields `ScalarTypeProvider`). All other keys and their
defaults behave exactly as documented for `#[cgp_component]`.

## Expansion

`#[cgp_type]` expands to the full `#[cgp_component]` output for the trait, followed by two
abstract-type provider impls. The component part is exactly what `#[cgp_component(ScalarTypeProvider)]`
would produce for an associated-type trait:

- the consumer trait and the provider trait;
- the consumer and provider blanket impls;
- the `ScalarTypeProviderComponent` marker;
- the standard `UseContext` and `RedirectLookup` provider impls;
- one impl per [`#[derive_delegate]`](../attributes/derive_delegate.md) or
  [`#[prefix]`](../attributes/prefix.md) attribute, since the trait's companion attributes are
  collected exactly as `#[cgp_component]` collects them.

The difference from a behavioral component is that every blanket impl forwards the *associated type*
rather than a method; see [`#[cgp_component]`](cgp_component.md) for that core shape.

**The first extra construct is the [`UseType`](../providers/use_type.md) blanket impl, which is the
heart of `#[cgp_type]`.** It implements the provider trait for `UseType<Scalar>` by setting the
abstract associated type to the generic parameter `Scalar`. Starting from:

```rust
#[cgp_type]
pub trait HasScalarType {
    type Scalar;
}
```

the macro generates:

```rust
impl<Scalar, __Context__> ScalarTypeProvider<__Context__> for UseType<Scalar> {
    type Scalar = Scalar;
}
```

This says that `UseType<T>` is a provider that supplies `T` as the abstract type. Wiring a context's
`ScalarTypeProviderComponent` to `UseType<f64>` therefore implements `HasScalarType` for that context
with `Scalar = f64`, with no bespoke provider needed. If the associated type carries a bound, that
bound is copied into the impl's `where` clause, so the concrete type must satisfy it.

**The second extra construct is a `WithProvider` impl**, which adapts the foundational
[`HasType`/`TypeProvider`](../components/has_type.md) machinery into this component. It implements the
provider trait for `WithProvider<__Provider__>` whenever `__Provider__` is a `TypeProvider` for the
component:

```rust
impl<__Provider__, Scalar, __Context__> ScalarTypeProvider<__Context__>
    for WithProvider<__Provider__>
where
    __Provider__: TypeProvider<__Context__, ScalarTypeProviderComponent, Type = Scalar>,
{
    type Scalar = Scalar;
}
```

The `HasType`/`TypeProvider` relationship this builds on is CGP's single built-in abstract-type
component: `HasType<Tag>` is the consumer trait, `TypeProvider` is its provider trait, and `UseType` is
itself a `TypeProvider`
(`impl<Context, Tag, Type> TypeProvider<Context, Tag> for UseType<Type> { type Type = Type; }`). The
`WithProvider` impl lets a `#[cgp_type]` component be backed by a generic `TypeProvider`, so the same
`UseType<T>` value satisfies both the built-in `HasType` and any user-defined `#[cgp_type]`
component.

As with the other macros, each generated provider impl is paired with a matching `IsProviderFor`
impl carrying the same bounds, and the desugarings above are the exact shape the macro emits.

## Examples

A complete use defines the abstract type, wires a concrete type through `UseType`, and consumes
`Self::Scalar` in generic code:

```rust
use cgp::prelude::*;

#[cgp_type]
pub trait HasScalarType {
    type Scalar: Copy;
}

pub struct App;

delegate_components! {
    App {
        ScalarTypeProviderComponent: UseType<f64>,
    }
}

check_components! {
    App {
        ScalarTypeProviderComponent,
    }
}

fn zero<Context>() -> Context::Scalar
where
    Context: HasScalarType,
    Context::Scalar: Default,
{
    Default::default()
}
```

`App` wires `ScalarTypeProviderComponent` to `UseType<f64>`, so the generated `UseType` blanket impl
makes `App` implement `HasScalarType` with `Scalar = f64`. The `Copy` bound on the associated type
sits in the `UseType` impl's `where` clause, so it is enforced wherever `App: HasScalarType` is
required, and the `check_components!` block requires it at the wiring. Without the check, wiring
`UseType<String>` would compile until the first use, because wiring is lazy; with it, the mistake is
reported as `String: Copy` not being satisfied.

The abstract type can equally be implemented directly on a concrete context, bypassing both
`delegate_components!` and `UseType`:

```rust
impl HasScalarType for App {
    type Scalar = f64;
}
```

This direct form is only marginally longer than the wired form, and is the most approachable for
readers new to CGP, since it makes plain that an abstract-type component is an ordinary trait with
an associated type.

## Related constructs

`#[cgp_type]` is the abstract-type specialization of [`#[cgp_component]`](cgp_component.md),
inheriting its full expansion and provider-name override syntax while keying the default name off
the associated type. It relates to these constructs:

- The [`UseType`](../providers/use_type.md) provider is its central generated construct, the
  type-level analogue of the [`UseField`](../providers/use_field.md) provider that
  [`#[cgp_getter]`](cgp_getter.md) generates.
- CGP's foundational [`HasType`/`TypeProvider`](../components/has_type.md) component backs it through
  the generated `WithProvider` impl.
- [`delegate_components!`](delegate_components.md) wires an abstract-type component,
  [`check_components!`](check_components.md) checks it, and [`#[use_type]`](../attributes/use_type.md)
  imports it into other definitions.
- [`#[cgp_auto_getter]`](cgp_auto_getter.md) can declare an abstract type inline when its only role is
  to be a getter's return type.

## Known issues

**An associated type named after the trait that bounds it shadows that trait.** In
`type Database: Database`, the bound resolves to the associated type being declared, a nearer
binding, rather than to the trait in scope. Because the generated `UseType` and `WithProvider` impls
lift the associated type into a free parameter, the compiler reports
``E0404: expected trait, found type parameter `Database` ``, which reads as though the author had
written a generic parameter. This is ordinary Rust name resolution rather than a macro defect; name
the two apart, as in `type Db: Database`.

## Source

- Entry point: `cgp_type` in
  [crates/macros/cgp-macro-lib/src/cgp_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_type.rs),
  which extracts the single associated type, derives the default `{Type}TypeProvider` provider name
  from the associated type's identifier, runs the `#[cgp_component]` `preprocess → eval` pipeline,
  and converts the result into `ItemCgpType`.
- Logic:
  [crates/macros/cgp-macro-core/src/types/cgp_type/item.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_type/item.rs),
  which validates the trait shape (`extract_item_type_from_trait`) and builds the `UseType` and
  `WithProvider` provider impls.
- Runtime `HasType`, `TypeProvider`, and `UseType` definitions:
  [crates/core/cgp-type/src/](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-type/src/)
  (`traits/has_type.rs` and `impls/use_type.rs`).
- Internal walkthrough (the pipeline stages, the function that synthesizes each generated item, the
  corner-case handling, and the index of tests and expansion snapshots):
  [implementation/entrypoints/cgp_type.md](../../implementation/entrypoints/cgp_type.md).
