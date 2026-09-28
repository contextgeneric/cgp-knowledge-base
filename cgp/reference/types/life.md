# `Life`

`Life<'a>` is a zero-sized type that lifts a lifetime into a type, so a lifetime parameter of a CGP
trait can travel through machinery that accepts only types.

## Purpose

`Life` exists because CGP's wiring is parameterized by types, yet a CGP trait may carry a lifetime
parameter of its own. The dependency marker [`IsProviderFor`](../traits/is_provider_for.md) takes a
tuple of the trait's generic parameters as one type argument, so the compiler can match a provider
against the exact instantiation it is asked about. A lifetime cannot sit directly in that tuple,
since a tuple's members must be types, so each lifetime parameter is first turned into a type.
`Life<'a>` is that conversion.

Without it, a component that borrows, such as one declaring `fn get_reference(&self) -> &'a T`,
could not record its `'a` in the marker. `Life` lets the lifetime ride through `IsProviderFor` as
`(Life<'a>, T)`. The macros insert it automatically for lifetime-carrying components, so a user sees
it in generated code and in errors about provider resolution, and writes it in one place: the
[`check_components!`](../macros/check_components.md) entry for such a component.

## Definition

`Life` is a tuple struct wrapping one `PhantomData` over a raw pointer to a borrowed unit:

```rust
pub struct Life<'a>(pub PhantomData<*mut &'a ()>);
```

It holds no runtime data; it only carries `'a` in the type system, and it is in the prelude. The
phantom type `*mut &'a ()` decides how `Life<'a>` behaves under subtyping. A `*mut T` is invariant
in `T`, so `Life<'a>` is invariant in `'a`: a `Life<'long>` is neither a subtype nor a supertype of
a `Life<'short>`, and a function returning its `Life<'l>` argument as a `Life<'s>` fails with
`lifetime may not live long enough`, while the same function over a `PhantomData<&'l ()>` compiles.
The lifetime is therefore exact wherever subtyping could apply, as in a provider struct holding a
`PhantomData<Life<'a>>`. Trait resolution matches lifetimes exactly whatever the variance, so the
choice governs values and types containing `Life`, not which impl the compiler selects.

The raw pointer has a side effect: `Life<'a>` is neither `Send` nor `Sync`, and neither is any
struct holding a `PhantomData<Life<'a>>`, such as the provider struct `#[cgp_new_provider]` (or
`#[cgp_impl(new …)]`) declares for a lifetime-generic provider. This rarely matters, because `Life`
and provider structs appear only at the type level and are never sent between threads, but a bound
like `Provider: Send` on such a provider fails with
``error[E0277]: `*mut &'static ()` cannot be sent between threads safely``.

## Behavior

`Life` has no methods and implements no traits; its behavior is to occupy a type position. In a
component with a lifetime, the lifetime is collected into the `IsProviderFor` tuple as `Life<'a>`,
so the provider's dependency reads the same way it would for a type parameter. The provider trait,
its blanket impl, and every impl that satisfies it agree on the same `(Life<'a>, T)` shape, which is
what lets a borrowing component be wired and checked like any other.

### Writing it, and what goes wrong

A reader writes `Life` in a check and nowhere else. A `check_components!` entry names a component's
parameters in the form the marker records them, so a lifetime component is checked as
`ReferenceGetterComponent: (Life<'a>, Config)`, with `'a` declared on the table as
`<'a> App<'a> { … }`. A bare `('a, Config)` is rejected, since the compiler reads `'a` as a
trait-object type without a trait and reports
`error: at least one trait is required for an object type`. A provider struct declared by hand over a lifetime matches the macro's shape by holding a
`PhantomData<Life<'a>>`; a `PhantomData<&'a ()>` also satisfies the unused-parameter rule, but it is
covariant and leaves the struct `Send` and `Sync`.

A component whose type parameter is `?Sized` works at an unsized argument such as `str`. Its params
tuple, `(Life<'a>, str)`, is then unsized too, and both `IsProviderFor`, which declares
`Params: ?Sized`, and a table's forwarding impl, which declares `__Params__: ?Sized`, accept it, so
the component resolves through a table like any other. One limitation does surface on components
with a lifetime, and it is not `Life`'s own: a higher-order provider over a lifetime component loses
the inner-provider `IsProviderFor` counterpart, recorded in the
[`#[cgp_provider]` Known issues](../macros/cgp_provider.md#known-issues).

## Examples

`Life` appears in the code generated for a component whose consumer trait carries a lifetime, and
in the check for it. A borrowing getter component, wired on a context that holds a borrow:

```rust
use cgp::prelude::*;

#[cgp_component(ReferenceGetter)]
pub trait HasReference<'a, T: 'a + ?Sized> {
    fn get_reference(&self) -> &'a T;
}

pub struct Config {
    pub name: String,
}

#[cgp_impl(new GetConfig)]
#[uses(HasField<Symbol!("config"), Value = &'a Config>)]
impl<'a> ReferenceGetter<'a, Config> {
    fn get_reference(&self) -> &'a Config {
        self.get_field(PhantomData::<Symbol!("config")>)
    }
}

#[derive(HasField)]
pub struct App<'a> {
    pub config: &'a Config,
}

delegate_components! {
    <'a> App<'a> {
        ReferenceGetterComponent: GetConfig,
    }
}

check_components! {
    <'a> App<'a> {
        ReferenceGetterComponent: (Life<'a>, Config),
    }
}
```

The generated provider trait records the lifetime in its marker as the type `Life<'a>` rather than a
bare `'a`:

```rust
pub trait ReferenceGetter<
    'a,
    __Context__,
    T: 'a + ?Sized,
>: IsProviderFor<ReferenceGetterComponent, __Context__, (Life<'a>, T)> {
    fn get_reference(__context__: &__Context__) -> &'a T;
}
```

Every impl that wires this component, whether `UseContext`, the table's forwarding impl, or a
hand-written provider, carries the same `(Life<'a>, T)` tuple, so the lifetime is preserved through
resolution.

The same component wired at the unsized target `str` resolves through the table and can be called:

```rust
#[cgp_impl(new GetName)]
#[uses(HasField<Symbol!("name"), Value = &'a str>)]
impl<'a> ReferenceGetter<'a, str> {
    fn get_reference(&self) -> &'a str {
        self.get_field(PhantomData::<Symbol!("name")>)
    }
}

#[derive(HasField)]
pub struct Borrowed<'a> {
    pub name: &'a str,
}

delegate_components! {
    <'a> Borrowed<'a> {
        ReferenceGetterComponent: GetName,
    }
}

check_components! {
    <'a> Borrowed<'a> {
        ReferenceGetterComponent: (Life<'a>, str),
    }
}

pub fn demo_unsized() {
    let text = String::from("demo");
    let borrowed = Borrowed { name: &text };

    let name: &str = borrowed.get_reference();
    assert_eq!(name, "demo");
}
```

## Related constructs

These constructs are the ones `Life` relates to:

- [`IsProviderFor`](../traits/is_provider_for.md): whose parameter tuple receives each lifetime as
  `Life<'a>`.
- [`#[cgp_component]`](../macros/cgp_component.md) and the provider macros: emit `Life` when a
  trait or provider declares a lifetime.
- [`check_components!`](../macros/check_components.md): where a check names `Life` in a
  parameter tuple.
- [`Index`](index.md) and [`Symbol`](chars.md): the other lifts that make a non-type addressable in
  trait resolution, a `usize` and a string.

## Source

- The type is defined in
  [crates/core/cgp-field/src/types/life.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/types/life.rs).
- The macro logic that wraps a trait's lifetime parameters in `Life` for the `IsProviderFor` tuple
  is in
  [crates/macros/cgp-macro-core/src/functions/is_provider_params.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/is_provider_params.rs),
  with the same lifting in a provider struct's `PhantomData` in
  [crates/macros/cgp-macro-core/src/types/empty_struct.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/empty_struct.rs)
  and in a provider impl's `IsProviderFor` in
  [crates/macros/cgp-macro-core/src/types/cgp_provider/provider_impl_args.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_provider/provider_impl_args.rs).
- For how it is generated and the index of tests, see the implementation document
  [implementation/functions/parse/is_provider_params.md](../../implementation/functions/parse/is_provider_params.md).
