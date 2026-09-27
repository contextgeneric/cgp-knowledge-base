# `UseDelegate<Components>`

`UseDelegate<Components>` is a zero-sized provider that dispatches a component with an extra generic
parameter to a different inner provider for each value of that parameter, reading the choice from
the `Components` table.

> **Legacy:** `UseDelegate`, the [`#[derive_delegate]`](../attributes/derive_delegate.md) attribute that generates its impl, and the [`UseDelegate<new ...>` nested-table wiring](../macros/delegate_components.md) form the legacy dispatch mechanism. The `open` statement of [`delegate_components!`](../macros/delegate_components.md) does the same per-type dispatch in the context's own table, with no separate table type, no wrapper, and no `#[derive_delegate]`, because it rides the [`RedirectLookup`](redirect_lookup.md) impl every [`#[cgp_component]`](../macros/cgp_component.md) already has. Prefer `open` in new code. `UseDelegate` stays for compatibility and is expected to be deprecated once `open` is shown to cover every dispatch case.

## Purpose

`UseDelegate` chooses a provider by a type argument rather than by the component alone. An ordinary
lookup finds a component's provider in the context's
[delegation table](../traits/delegate_component.md). When the trait has an extra parameter, such as
a `SourceError` to convert, a `Shape` to measure, or an `Input` to compute over, the right provider
often depends on that parameter's concrete type. `UseDelegate` performs this second lookup: it uses
the parameter as the key into its own table, so one wiring entry fans out to a provider per type.

This keeps providers small and non-overlapping. Instead of one provider that handles every `Shape`,
each shape gets its own provider, and `UseDelegate` routes each concrete shape to it. `UseDelegate`
is CGP's default dispatcher; other dispatcher types, such as the handler family's
`UseInputDelegate`, key on other parameters.

## Definition

`UseDelegate` is defined in `cgp-component` and is in the prelude:

```rust
pub struct UseDelegate<Components>(pub PhantomData<Components>);
```

`Components` is the lookup table, a type with a
[`DelegateComponent`](../traits/delegate_component.md) entry for each value of the dispatched
parameter. It is held in `PhantomData` and never constructed.

## Behavior

`UseDelegate` has no impls of its own. A component opts in with
`#[derive_delegate(UseDelegate<Param>)]`, which makes `#[cgp_component]` generate an impl keyed on
`Param`. For this component:

```rust
#[cgp_component(AreaCalculator)]
#[derive_delegate(UseDelegate<Shape>)]
pub trait CanCalculateArea<Shape> {
    fn area(&self, shape: &Shape) -> f64;
}
```

the generated impl is, with its generics renamed for reading:

```rust
impl<Context, Shape, Components, Delegate> AreaCalculator<Context, Shape>
    for UseDelegate<Components>
where
    Components: DelegateComponent<(Shape), Delegate = Delegate>,
    Delegate: AreaCalculator<Context, Shape>,
{
    fn area(context: &Context, shape: &Shape) -> f64 {
        Delegate::area(context, shape)
    }
}
```

The lookup is one `DelegateComponent` query. `(Shape)` is the bare type `Shape`, not a one-element
tuple, so the table is keyed directly on each shape; `UseDelegate<(A, B)>` keys on a real tuple of
two parameters. Every other parameter passes through to the delegate unchanged. The impl is paired
with an `IsProviderFor` impl, so a missing dependency in the chosen provider reaches the
[check traits](../../concepts/check-traits.md).

A component can dispatch on different parameters through different dispatchers by repeating
`#[derive_delegate]`, one per dispatcher type, as the handler components do with `UseDelegate<Code>`
and `UseInputDelegate<Input>`. The `open` statement needs no second dispatcher: its redirect appends
every type parameter to the lookup path, so a key can name one segment per parameter.

## Examples

This context wires the area component through a nested table:

```rust
use cgp::prelude::*;

#[cgp_component(AreaCalculator)]
#[derive_delegate(UseDelegate<Shape>)]
pub trait CanCalculateArea<Shape> {
    fn area(&self, shape: &Shape) -> f64;
}

pub struct Rectangle {
    pub width: f64,
    pub height: f64,
}

pub struct Circle {
    pub radius: f64,
}

#[cgp_impl(new RectangleArea)]
impl AreaCalculator<Rectangle> {
    fn area(&self, shape: &Rectangle) -> f64 {
        shape.width * shape.height
    }
}

#[cgp_impl(new CircleArea)]
impl AreaCalculator<Circle> {
    fn area(&self, shape: &Circle) -> f64 {
        core::f64::consts::PI * shape.radius * shape.radius
    }
}

pub struct MyApp;

delegate_components! {
    MyApp {
        AreaCalculatorComponent:
            UseDelegate<new AreaCalculatorComponents {
                Rectangle: RectangleArea,
                Circle: CircleArea,
            }>,
    }
}

check_components! {
    MyApp {
        AreaCalculatorComponent: [Rectangle, Circle],
    }
}
```

`MyApp` delegates `AreaCalculatorComponent` to `UseDelegate<AreaCalculatorComponents>`, and the
inner table, defined in place by `new`, maps `Rectangle` to `RectangleArea` and `Circle` to
`CircleArea`. So `MyApp` implements `CanCalculateArea<Rectangle>` through one provider and
`CanCalculateArea<Circle>` through the other. With `open AreaCalculatorComponent;` and the entries
`@AreaCalculatorComponent.Rectangle: RectangleArea` and
`@AreaCalculatorComponent.Circle: CircleArea`, the same wiring needs neither the inner table nor
`#[derive_delegate]`.

## Related constructs

These constructs are the ones `UseDelegate` works with:

- [`#[derive_delegate]`](../attributes/derive_delegate.md): generates its impl for a component.
- [`delegate_components!`](../macros/delegate_components.md): wires it through a nested table, and
  offers the `open` statement that replaces it.
- [`DelegateComponent`](../traits/delegate_component.md): the table trait it reads.
- [`UseDelegatedType`](use_delegated_type.md): the same lookup yielding a type.
- [Handler combinators](handler_combinators.md): `UseInputDelegate`, the dispatcher keyed on a
  handler's input.

## Source

- The struct is defined in
  [crates/core/cgp-component/src/providers/use_delegate.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/providers/use_delegate.rs).
- The `UseDelegate` provider impl is generated from the `#[derive_delegate]` directive parsed in
  [crates/macros/cgp-macro-core/src/types/attributes/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/attributes/)
  and emitted by the `#[cgp_component]` pipeline in
  [crates/macros/cgp-macro-core/src/types/cgp_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_component/).
- The nested-table wiring is handled by `delegate_components!` in
  [crates/macros/cgp-macro-core/src/types/delegate_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/delegate_component/).
- For how it is generated and the index of tests, see the implementation document
  [implementation/asts/attributes/derive_delegate.md](../../implementation/asts/attributes/derive_delegate.md).
