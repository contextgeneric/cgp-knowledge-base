# `Life`

`Life<'a>` is a zero-sized type that lifts a lifetime into a type, so a lifetime parameter of a CGP trait can travel through machinery that accepts only types.

## Purpose

`Life` exists because CGP's wiring is parameterized by types, yet a CGP trait may carry a lifetime parameter of its own. The dependency marker [`IsProviderFor`](../traits/is_provider_for.md) takes a tuple of the trait's generic parameters as one type argument, so the compiler can match a provider against the exact instantiation it is asked about. A lifetime cannot sit directly in that tuple, since a tuple's members must be types, so each lifetime parameter is first turned into a type. `Life<'a>` is that conversion.

Without it, a component that borrows, such as one declaring `fn get_reference(&self) -> &'a T`, could not record its `'a` in the marker, and the wiring could not tell one lifetime instantiation from another. `Life` lets the lifetime ride through `IsProviderFor` as `(Life<'a>, T)`. The macros insert it automatically for lifetime-carrying components, so a user rarely writes it but sees it in generated code and in errors about provider resolution.

## Definition

`Life` is a tuple struct wrapping one `PhantomData` over a raw pointer to a borrowed unit:

```rust
pub struct Life<'a>(pub PhantomData<*mut &'a ()>);
```

It holds no runtime data; it only carries `'a` in the type system. The phantom type `*mut &'a ()` is chosen for how `Life<'a>` behaves under subtyping. A `*mut T` is invariant in `T`, so `Life<'a>` is invariant in `'a`: a `Life<'long>` is neither a subtype nor a supertype of a `Life<'short>`. Invariance is right here because the lifetime serves as an exact identity in the marker, and a variant `Life` would let the compiler coerce one instantiation into another and pick the wrong provider.

The raw pointer has a side effect: `Life<'a>` is neither `Send` nor `Sync`, and neither is any struct holding a `PhantomData<Life<'a>>`, such as the provider struct `#[cgp_new_provider]` declares for a lifetime-generic provider. This rarely matters, because `Life` and provider structs appear only at the type level and are never sent between threads, but a bound like `Provider: Send` on such a provider fails.

## Behavior

`Life` has no methods and implements no traits; its behavior is to occupy a type position. In a component with a lifetime, the lifetime is collected into the `IsProviderFor` tuple as `Life<'a>`, so the provider's dependency reads the same way it would for a type parameter. The provider trait, its blanket impl, and every impl that satisfies it agree on the same `(Life<'a>, T)` shape, which is what lets a borrowing component be wired and checked like any other.

## Examples

`Life` appears in the code generated for a component whose consumer trait carries a lifetime. Given a borrowing getter component:

```rust
use cgp::prelude::*;

#[cgp_component(ReferenceGetter)]
pub trait HasReference<'a, T: 'a + ?Sized> {
    fn get_reference(&self) -> &'a T;
}
```

the generated provider trait records the lifetime in its marker as the type `Life<'a>` rather than a bare `'a`:

```rust
// generated, in readable form:
// pub trait ReferenceGetter<'a, __Context__, T: 'a + ?Sized>:
//     IsProviderFor<ReferenceGetterComponent, __Context__, (Life<'a>, T)>
// {
//     fn get_reference(__context__: &__Context__) -> &'a T;
// }
```

Every impl that wires this component, whether `UseContext`, a field getter, or a hand-written provider, carries the same `(Life<'a>, T)` tuple, so the lifetime is preserved through resolution. A `check_components!` entry for it writes the parameters the same way, as `ReferenceGetterComponent: (Life<'a>, str)`.

## Related constructs

These constructs are the ones `Life` relates to:

- [`IsProviderFor`](../traits/is_provider_for.md) — whose parameter tuple receives each lifetime as `Life<'a>`.
- [`#[cgp_component]`](../macros/cgp_component.md) and the provider macros — emit `Life` when a trait or provider declares a lifetime.
- [`Index`](index.md) and [`Symbol`](chars.md) — the other lifts that make a non-type addressable in trait resolution, a `usize` and a string.

## Source

- The type is defined in [crates/core/cgp-field/src/types/life.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/types/life.rs).
- The macro logic that wraps a trait's lifetime parameters in `Life` for the `IsProviderFor` tuple is in [crates/macros/cgp-macro-core/src/functions/is_provider_params.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/is_provider_params.rs), with the same lifting in a provider struct's `PhantomData` in [crates/macros/cgp-macro-core/src/types/empty_struct.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/empty_struct.rs) and in a provider impl's `IsProviderFor` in [crates/macros/cgp-macro-core/src/types/cgp_provider/provider_impl_args.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_provider/provider_impl_args.rs).
- For how it is generated and the index of tests, see the implementation document [implementation/functions/parse/is_provider_params.md](../../implementation/functions/parse/is_provider_params.md).
