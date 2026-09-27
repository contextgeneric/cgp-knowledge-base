# `UseDefault`

`UseDefault` is a zero-sized marker provider for a component whose implementation comes entirely from the consumer trait's default method bodies.

## Purpose

`UseDefault` names the choice "use the trait's own defaults" in wiring. A component trait may give its methods default bodies, and `#[cgp_component]` carries those bodies to the provider trait. When every method has a usable default, a provider only needs to exist so the component can be wired. `UseDefault` is the shared name for that empty provider, so authors do not invent a one-off marker each time.

Unlike [`UseContext`](use_context.md), [`UseFields`](use_fields.md), or [`UseField`](use_field.md), `UseDefault` gets no generated impls. The author writes each impl, usually as an empty [`#[cgp_impl]`](../macros/cgp_impl.md) block, which is the explicit opt-in: `UseDefault` serves exactly the components it has an impl for.

## Definition

`UseDefault` is a unit struct defined in `cgp-component`:

```rust
pub struct UseDefault;
```

It is not in the prelude and is imported from `cgp::core::component`.

## Behavior

An empty provider impl for `UseDefault` inherits every default body. For these two traits:

```rust
#[cgp_getter]
pub trait HasName {
    fn name(&self) -> &str {
        "John"
    }
}

#[cgp_component(Greeter)]
#[extend(HasName)]
pub trait CanGreet {
    fn greet(&self) -> String {
        format!("Hello, {}!", self.name())
    }
}
```

the impls are:

```rust
#[cgp_impl(UseDefault)]
impl NameGetter {}

#[cgp_impl(UseDefault)]
#[uses(HasName)]
impl Greeter {}
```

The first makes `UseDefault` a `NameGetter` whose `name` returns `"John"`. The second makes it a `Greeter` whose `greet` formats around `self.name()`. The `Greeter` impl still needs [`#[uses(HasName)]`](../attributes/uses.md): the supertrait becomes a predicate on the provider trait, but a generic impl must prove it, and without the bound the impl fails with `E0277`. Each `#[cgp_impl]` also generates the matching [`IsProviderFor`](../traits/is_provider_for.md) impl.

## Examples

This context wires both components to `UseDefault`:

```rust
use cgp::prelude::*;
use cgp::core::component::UseDefault;

#[cgp_getter]
pub trait HasName {
    fn name(&self) -> &str {
        "John"
    }
}

#[cgp_component(Greeter)]
#[extend(HasName)]
pub trait CanGreet {
    fn greet(&self) -> String {
        format!("Hello, {}!", self.name())
    }
}

#[cgp_impl(UseDefault)]
impl NameGetter {}

#[cgp_impl(UseDefault)]
#[uses(HasName)]
impl Greeter {}

pub struct App;

delegate_components! {
    App {
        [
            NameGetterComponent,
            GreeterComponent,
        ]:
            UseDefault,
    }
}

check_components! {
    App {
        NameGetterComponent,
        GreeterComponent,
    }
}
```

`App.greet()` returns `"Hello, John!"` from the two default bodies alone.

## Related constructs

These constructs are the ones `UseDefault` works with:

- [`#[cgp_impl]`](../macros/cgp_impl.md) — writes its empty impls.
- [`#[cgp_component]`](../macros/cgp_component.md) — carries default bodies to the provider trait, which is what an empty impl inherits.
- [`#[uses]`](../attributes/uses.md) — states the bounds a default body relies on.
- [`UseContext`](use_context.md), [`UseFields`](use_fields.md), and [`UseField`](use_field.md) — providers whose impls are generated.
- [`delegate_components!`](../macros/delegate_components.md) and [`check_components!`](../macros/check_components.md) — wire and check it.

## Source

- The struct is defined in [crates/core/cgp-component/src/providers/use_default.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/providers/use_default.rs) and re-exported in [crates/core/cgp-component/src/providers/mod.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/providers/mod.rs); the file contains only the bare struct, with no macro-generated impls.
