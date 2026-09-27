# `DelegateComponent`

`DelegateComponent<Key>` is the core wiring trait: it turns a type into a compile-time table that maps each `Key` to one `Delegate` type, so a component lookup can resolve to the provider that handles it.

## Purpose

`DelegateComponent` records, at the type level, which provider a context chose for a component. A CGP component separates the consumer trait callers use from the provider trait implementers write, which leaves open which provider supplies the behavior for a given context. `DelegateComponent` stores that choice: one impl per entry, with the component's marker as the key and the provider as the value.

Think of it as a type-level map carried on the `Self` type. Implementing `DelegateComponent<Key>` sets the entry at `Key`; writing the bound `Self: DelegateComponent<Key>` and projecting `Self::Delegate` reads it back. Keys and values are both types, so the lookup happens during type-checking and costs nothing at runtime.

The same table serves two jobs:

- **Wiring.** When the key is a component marker, the provider blanket impl from [`#[cgp_component]`](../macros/cgp_component.md) reads the entry, so the context inherits the provider trait and then the consumer trait.
- **Dispatch tables.** When the key is any other type, such as a shape, a tag, or a path, the table is plain data that a provider such as [`UseDelegate`](../providers/use_delegate.md) or [`RedirectLookup`](../providers/redirect_lookup.md) reads.

## Definition

`DelegateComponent` has one associated type and no methods:

```rust
pub trait DelegateComponent<Key: ?Sized> {
    type Delegate;
}
```

`Self` is the table, the type that owns the entry. `Key` is the type being looked up; it is `?Sized`, so an unsized marker can serve as a key. `Delegate` is the value stored at that key: a provider, or another table. The trait is in the prelude.

The trait carries no `#[diagnostic::on_unimplemented]` attribute. A lookup with no entry is reported by the compiler as ``the trait `DelegateComponent<FooComponent>` is not implemented for `App` ``, and [cargo-cgp](../cargo-cgp.md) turns such errors into CGP-specific messages.

## Behavior

A type holds one independent impl per key. Rust forbids two impls of the same trait with the same `Self` and `Key`, so each key maps to exactly one value, which makes the table a real map.

The impls are almost never written by hand. [`delegate_components!`](../macros/delegate_components.md) turns each `Key: Value` entry into `impl DelegateComponent<Key> for Target { type Delegate = Value; }`, and emits beside it an [`IsProviderFor`](is_provider_for.md) impl that forwards the chosen provider's dependencies, so an unmet requirement stays diagnosable.

The provider blanket impl is the reader. For a component `Foo`, it implements the provider trait for any type `P` with `P: DelegateComponent<FooComponent>`, forwarding each method to `<P as DelegateComponent<FooComponent>>::Delegate`. The table read is literally how a call is routed.

A lookup is shallow: one read yields the immediate `Delegate`, which may itself be a table. An [aggregate provider](../../concepts/aggregate-providers.md) declared with `new` holds its own table, so a context can delegate a group of components to the bundle, and each component's blanket impl reads through to the bundle's entry. Keys can also be type-level paths: the `open` statement and namespaces store entries keyed on `PathCons` lists, and [`RedirectLookup`](../providers/redirect_lookup.md) reads one with a single lookup on the whole path.

## Examples

This context wires one component:

```rust
use cgp::prelude::*;

#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}

#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self) {
        println!("Hello!");
    }
}

pub struct App;

delegate_components! {
    App {
        GreeterComponent: GreetHello,
    }
}
```

The wiring expands to one entry, alongside its `IsProviderFor` forwarding impl:

```rust
impl DelegateComponent<GreeterComponent> for App {
    type Delegate = GreetHello;
}
```

The provider blanket impl reads the entry and gives `App` the `Greeter` provider trait, and the consumer blanket impl then gives it `CanGreet`, so `App.greet()` type-checks.

A table keyed on other types is plain data:

```rust
delegate_components! {
    new AreaComponents {
        Rectangle: RectangleArea,
        Circle: CircleArea,
    }
}

fn area_provider<Shape>() -> PhantomData<<AreaComponents as DelegateComponent<Shape>>::Delegate>
where
    AreaComponents: DelegateComponent<Shape>,
{
    PhantomData
}
```

The bound is the read, and the projection is the value: `RectangleArea` for `Shape = Rectangle`, `CircleArea` for `Shape = Circle`. A `UseDelegate<AreaComponents>` provider performs the same read when it dispatches on a shape.

## Related constructs

These constructs are the ones `DelegateComponent` works with:

- [`delegate_components!`](../macros/delegate_components.md) — writes its impls, one per entry.
- [`#[cgp_component]`](../macros/cgp_component.md) — generates the provider blanket impl that reads it.
- [`IsProviderFor`](is_provider_for.md) — the forwarding impl emitted beside each entry.
- [`CanUseComponent`](can_use_component.md) — requires both an entry and a valid delegate.
- [`UseDelegate`](../providers/use_delegate.md) and [`RedirectLookup`](../providers/redirect_lookup.md) — providers that read tables keyed on other types.

## Source

- The trait is defined in [crates/core/cgp-component/src/traits/delegate_component.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/traits/delegate_component.rs) and re-exported through the macro prelude in [crates/core/cgp-component/src/macro_prelude.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/macro_prelude.rs).
- The impls are generated by `delegate_components!`, whose codegen lives in [crates/macros/cgp-macro-core/src/types/delegate_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/delegate_component/); entry mapping and the `DelegateComponent`/`IsProviderFor` impl construction are in `mapping/eval.rs`.
- The provider blanket impl that reads the table is emitted by the `#[cgp_component]` codegen in [crates/macros/cgp-macro-core/src/types/cgp_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_component/).
- For how it is generated and the index of tests, see the implementation document [implementation/entrypoints/cgp_component.md](../../implementation/entrypoints/cgp_component.md).
