# `HasErrorType`

`HasErrorType` is the abstract-type component that gives a context one shared abstract `Error` type,
so CGP code can fail without naming a concrete error type. `ErrorOf<Context>` is the alias for the
resolved type.

## Purpose

`HasErrorType` lets generic code return errors while the application chooses the error type. A
provider that can fail must produce some error, but it is generic over the context and cannot commit
to `anyhow::Error`, `std::io::Error`, or any other concrete type. Generic code therefore returns
`Result<T, Self::Error>`, or `ErrorOf<Context>`, and the context decides the concrete type once,
when it is wired.

Putting the error type on one trait is what lets errors compose across components. If each trait
declared its own associated `Error`, a context bounded by several of them would have several
unrelated error types. Instead every fallible trait imports the same `HasErrorType::Error`, so all
of them agree on one type. [`CanRaiseError` and `CanWrapError`](can_raise_error.md) build on this
shared type.

## Definition

`HasErrorType` is defined with [`#[cgp_type]`](../macros/cgp_type.md):

```rust
#[cgp_type]
#[prefix(@cgp.core.error in DefaultNamespace)]
pub trait HasErrorType {
    type Error: Debug;
}

pub type ErrorOf<Context> = <Context as HasErrorType>::Error;
```

The parts are these:

- **`Error`** is the context's abstract error. Its `Debug` bound lets generic code call `.unwrap()`
  and log errors without adding a constraint, and every concrete error wired in must implement
  `Debug`.
- **`#[cgp_type]`** makes the trait a full abstract-type component. It generates the provider trait
  `ErrorTypeProvider`, the key `ErrorTypeProviderComponent`, the blanket impls, and a
  [`UseType`](../providers/use_type.md) impl, all carrying the `Debug` bound.
- **[`#[prefix(@cgp.core.error in DefaultNamespace)]`](../attributes/prefix.md)** registers the
  component in `DefaultNamespace` under the path `@cgp.core.error`, so a context that joins that
  namespace can bind the error type at `@cgp.core.error.ErrorTypeProviderComponent`.
- **`ErrorOf<Context>`** is the short spelling of `<Context as HasErrorType>::Error`.

`HasErrorType` is in the prelude. `ErrorOf`, `ErrorTypeProvider`, and `ErrorTypeProviderComponent`
are not, and are imported from `cgp::core::error`.

## Behavior

A context sets its error type in one of three ways:

- **Implement the trait directly**, as in
  `impl HasErrorType for App { type Error = anyhow::Error; }`.
- **Wire `UseType<E>`**, as in `ErrorTypeProviderComponent: UseType<anyhow::Error>`, which the
  generated `UseType` impl supports.
- **Wire a backend provider** from the [error backends](../../../projects/error/README.md).
  `cgp-error-anyhow`, `cgp-error-eyre`, and `cgp-error-std` each provide a provider for this
  component, such as `UseAnyhowError`, that sets `Error` to the backend's type.

`HasErrorType` has no methods; it only declares the type. Constructing errors belongs to the traits
that import it: [`CanRaiseError`](can_raise_error.md) converts a source error into `Self::Error`,
and [`CanWrapError`](can_raise_error.md) adds detail to an existing one. Keeping the declaration
apart from construction lets a context choose its error type and its raising strategy independently.

## Examples

A component imports the abstract error, and a context fixes it to `String`:

```rust
use cgp::prelude::*;
use cgp::core::error::ErrorTypeProviderComponent;

#[cgp_component(Validator)]
#[use_type(HasErrorType.Error)]
pub trait CanValidate {
    fn validate(&self) -> Result<(), Error>;
}

pub struct App;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<String>,
    }
}
```

[`#[use_type(HasErrorType.Error)]`](../attributes/use_type.md) adds `HasErrorType` as a supertrait
of `CanValidate` and rewrites the bare `Error` to `<Self as HasErrorType>::Error`. `App` wires the
error type to `String`, which satisfies the `Debug` bound. The same choice can be written as a
direct impl:

```rust
impl HasErrorType for App {
    type Error = String;
}
```

## Related constructs

These constructs are the ones `HasErrorType` works with:

- [`#[cgp_type]`](../macros/cgp_type.md): defines it and generates its `UseType` impl.
- [`CanRaiseError` and `CanWrapError`](can_raise_error.md): construct and enrich the abstract error.
- [`HasType`](has_type.md): the tag-indexed abstract-type component whose `TypeProvider`s can also
  back this one through the generated `WithProvider` impl.
- [Error providers](../providers/error_providers.md) and the
  [error backends](../../../projects/error/README.md): ready-made providers.
- [Modular error handling](../../concepts/modular-error-handling.md): how these pieces form CGP's
  error strategy.

## Source

- The trait and the `ErrorOf` alias are defined in
  [crates/core/cgp-error/src/traits/has_error_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-error/src/traits/has_error_type.rs).
- The `#[cgp_type]` machinery it relies on lives in
  [crates/macros/cgp-macro-core/src/types/cgp_type/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_type/),
  and the underlying `HasType`/`TypeProvider`/`UseType` definitions are in
  [crates/core/cgp-type/src/](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-type/src/).
- The pluggable concrete error backends are in
  [crates/standalone/error/](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error/),
  documented in [projects/error/](../../../projects/error/README.md).
