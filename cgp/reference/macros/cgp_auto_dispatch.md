# `#[cgp_auto_dispatch]`

`#[cgp_auto_dispatch]` takes a trait implemented separately for each payload type and generates an
implementation of it for any extensible enum of those types, which matches the current variant and
calls the trait method on its payload.

## Purpose

`#[cgp_auto_dispatch]` handles the common case of a trait with one impl per type that should also
work on an enum of those types. Without it, a programmer writes a `match` arm per variant, or wires
the [dispatch combinators](../providers/dispatch_combinators.md) by hand: a matcher, a per-variant
computer, and the field-handler machinery. The macro generates both the per-variant computer each
method needs and the enum-level blanket impl that runs the matcher. The programmer writes only the
trait, its per-payload impls, and the derive that makes the enum extensible.

The macro is the highest-level entry point to the [dispatching](../../concepts/dispatching.md)
pattern, and it fits when the per-variant behavior is exactly "call the same method on the payload".
It generates the same matcher wiring that
[`dispatch_combinators`](../providers/dispatch_combinators.md) describes, so the result behaves like
a hand-written dispatch. When the per-variant behavior is more elaborate, or the dispatch must be
wired into a context's components rather than implemented on the enum, use the combinators directly.
The generated impl calls its matcher with a unit context and code, so no context can override how
one variant is handled. The macro is for retrofitting an existing per-type trait onto an enum; an
operation designed from the start to be configured per context is a
[`#[cgp_component]`](cgp_component.md) wired with the combinators.

## Syntax

`#[cgp_auto_dispatch]` is written above a trait definition. It takes no arguments, and any tokens
given as an argument are ignored:

```rust
#[cgp_auto_dispatch]
pub trait HasArea {
    fn area(&self) -> f64;
}
```

The trait may carry generic parameters. Each method may take `self` by value, by shared reference,
or by mutable reference, may take further arguments by value or by reference, and may be `async`.

The macro rejects three shapes at expansion time, each with its own message:

- **A trait item other than a method**: an associated type or constant fails with
  `Only function items are allowed in a dispatch trait`.
- **A method without a `self` receiver**: the receiver is the enum value being matched, so its
  absence fails with `Dispatcher method must have a self argument`.
- **A method with a type or const generic parameter**: the generated impl would need a quantified
  bound Rust lacks, so it fails with
  `Dispatch trait methods cannot contain non-lifetime generic parameters …`. Lifetime parameters are
  allowed.

Supertraits parse but break the expansion, as Known issues explains.

## Expansion

The macro keeps the trait unchanged and appends two kinds of item: one blanket impl of the trait for
a fresh type parameter named `__Variants__`, and, for each method, one free function that
[`#[cgp_computer]`](cgp_computer.md) turns into a per-variant computer.

### The per-variant computer

Each method becomes a function that calls the method on the payload. For the `HasArea` trait above,
the macro emits:

```rust
#[cgp_computer(ComputeArea)]
fn area<'__a__, __Variants__: HasArea>(__Variants__: &'__a__ __Variants__) -> f64 {
    __Variants__.area()
}
```

The computer is named `Compute` followed by the method name in PascalCase, so `area` yields
`ComputeArea`. It is generic over any `__Variants__: HasArea`, so it applies to every payload type
that implements the trait. It borrows the payload for a fresh lifetime `'__a__`, mirroring the
`&self` receiver, and the same lifetime is given to any elided reference in the arguments or the
return type.

### The enum-level blanket impl

The blanket impl implements the trait for every `__Variants__` by running a matcher over the
per-variant computer:

```rust
impl<__Variants__> HasArea for __Variants__
where
    MatchWithValueHandlersRef<ComputeArea>:
        for<'__a__> Computer<(), (), &'__a__ __Variants__, Output = f64>,
    __Variants__: HasExtractor,
{
    fn area(&self) -> f64 {
        <MatchWithValueHandlersRef<ComputeArea> as Computer<_, _, _>>::compute(
            &(),
            ::core::marker::PhantomData::<()>,
            self,
        )
    }
}
```

The impl always requires `__Variants__: HasExtractor`, because matching needs an extensible enum. It
calls the matcher with a unit context `&()` and a unit code `PhantomData::<()>`, since the
per-variant logic depends only on the payload. The call names the provider trait with inferred
arguments, `Computer<_, _, _>`, so it stays unambiguous in a module that also imports the consumer
trait `CanCompute`.

The matcher comes from the value-handler family, so the per-variant computer receives the bare
payload. The method's receiver and whether it takes further arguments decide which one:

| Receiver | No further arguments | Further arguments |
|---|---|---|
| `&self` | `MatchWithValueHandlersRef` | `MatchFirstWithValueHandlersRef` |
| `&mut self` | `MatchWithValueHandlersMut` | `MatchFirstWithValueHandlersMut` |
| `self` | `MatchWithValueHandlers` | `MatchFirstWithValueHandlers` |

A method with further arguments passes the matcher a pair of the receiver and a tuple of the
arguments. For `contains(&self, x: f64, y: f64) -> bool`, the impl selects
`MatchFirstWithValueHandlersRef`:

```rust
// where MatchFirstWithValueHandlersRef<ComputeContains>:
//     for<'__a__> Computer<(), (), (&'__a__ __Variants__, (f64, f64)), Output = bool>
fn contains(&self, arg_0: f64, arg_1: f64) -> bool {
    <MatchFirstWithValueHandlersRef<ComputeContains> as Computer<_, _, _>>::compute(
        &(),
        ::core::marker::PhantomData::<()>,
        (self, (arg_0, arg_1)),
    )
}
```

An `async` method uses `AsyncComputer` in both the bound and the call, and `.await`s the result. A
by-value `self` method with no borrowed argument or return needs no lifetime, so its bound has no
`for<…>` quantifier.

## Examples

This example makes an enum extensible with `CgpData`, marks two traits with `#[cgp_auto_dispatch]`,
and implements each trait on the payload types alone:

```rust
use cgp::prelude::*;

#[derive(CgpData)]
pub enum Shape {
    Circle(Circle),
    Rectangle(Rectangle),
}

pub struct Circle { pub radius: f64 }
pub struct Rectangle { pub width: f64, pub height: f64 }

#[cgp_auto_dispatch]
pub trait HasArea {
    fn area(&self) -> f64;
}

impl HasArea for Circle {
    fn area(&self) -> f64 { core::f64::consts::PI * self.radius * self.radius }
}

impl HasArea for Rectangle {
    fn area(&self) -> f64 { self.width * self.height }
}

#[cgp_auto_dispatch]
pub trait CanScale {
    fn scale(&mut self, factor: f64);
}

impl CanScale for Circle {
    fn scale(&mut self, factor: f64) { self.radius *= factor; }
}

impl CanScale for Rectangle {
    fn scale(&mut self, factor: f64) { self.width *= factor; self.height *= factor; }
}

fn main() {
    let mut shape = Shape::Rectangle(Rectangle { width: 2.0, height: 2.0 });
    assert_eq!(shape.area(), 4.0); // MatchWithValueHandlersRef
    shape.scale(2.0);              // MatchFirstWithValueHandlersMut
    assert_eq!(shape.area(), 16.0);
}
```

`Shape` gains both traits without an impl of its own. The generated bound requires every variant's
payload to implement the trait, so forgetting an impl for one variant is a compile error where the
enum's method is used. The [extensible shapes](../../../examples/extensible-shapes.md) example
develops this macro further, with argument-taking methods, and compares the generated wiring with
the combinators used directly.

## Related constructs

These constructs are the ones `#[cgp_auto_dispatch]` builds on:

- [Dispatch combinators](../providers/dispatch_combinators.md): the value-handler matchers it wires,
  `MatchWithValueHandlers` with its `Ref`/`Mut` and `First` variants; use them directly for richer
  per-variant behavior or context-wired dispatch.
- [`#[cgp_computer]`](cgp_computer.md): emits each per-variant function as a
  [`Computer`](../components/computer.md) provider.
- [`#[derive(CgpData)]`](../derives/derive_cgp_data.md): makes the enum extensible, supplying
  [`HasExtractor`](../traits/extract_field.md) and [`HasFields`](../traits/has_fields.md).
- [Dispatching](../../concepts/dispatching.md): the concept this macro automates.

## Known issues

**The per-method helper function takes the method's name.** Each method's per-variant function is
emitted as a free function with the method's own name (`fn area`) in the module that declares the
trait, so a module that already holds an item of that name fails with
``E0428: the name `area` is defined multiple times``, followed by argument-count and type errors
from the clash. The correct behavior would be to emit the helper under a generated name that
cannot collide, since only the `ComputeArea` provider needs to be visible. Until then,
declare the trait in a module without a clashing item.

**The blanket impl covers every type implementing `HasExtractor`.** A hand-written impl of the
trait for a type outside that set, such as each payload struct, coexists with it, but one for
another extensible enum fails with ``E0119: conflicting implementations of trait `HasArea` ``.

**A missing variant impl or derive is reported at the call, not at its cause.** Omitting the impl
for one payload fails where the enum's method is called, with
``E0599: the method `area` exists for reference `&Shape`, but its trait bounds were not satisfied``,
whose notes list the matcher's unsatisfied `Computer` bounds without naming the variant. Omitting
`#[derive(CgpData)]` gives the same headline, with a note that `HasExtractor` must be implemented.

Type and const generic parameters on a method are rejected by design. The blanket impl would need a
bound quantified over the method's type parameter, guaranteeing that every payload satisfies it for
every instantiation, and Rust has no such bound. A generic method must be dispatched with the
combinators directly.

A supertrait on the dispatch trait makes the expansion fail to compile. The blanket impl implements
the trait for every `__Variants__` but never requires the supertrait, so Rust rejects it with
`E0277` (the trait bound `__Variants__: Supertrait` is not satisfied) at the attribute, unless the
supertrait already holds for every type. The correct behavior would be to add
`__Variants__: Supertrait` to the blanket impl's `where` clause. Until then, declare the dependency
on each method's payload impls instead of as a supertrait.

A method whose signature needs two distinct lifetimes also fails to compile. The macro collects
every lifetime the bound must quantify, such as a named `'a` on the receiver and the `'__a__` it
assigns to an elided argument, but emits a `for<…>` quantifier for only the last one. So
`fn lookup<'a>(&'a self, key: &str) -> &'a str` fails with `E0261` (use of undeclared lifetime name
`'__a__`). The correct behavior would be a single `for<'a, '__a__>` quantifier over all of them.
Naming every reference with the same lifetime, or eliding them all, avoids the problem.

## Source

- Entry point: `cgp_auto_dispatch` in
  [crates/macros/cgp-extra-macro-lib/src/entrypoints/cgp_auto_dispatch.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro-lib/src/entrypoints/cgp_auto_dispatch.rs),
  forwarded from the proc-macro shim in
  [crates/macros/cgp-extra-macro/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro/src/lib.rs)
  and re-exported through
  [crates/main/cgp-extra/src/prelude.rs](https://github.com/contextgeneric/cgp/blob/main/crates/main/cgp-extra/src/prelude.rs).
- Matchers it generates:
  [crates/extra/cgp-dispatch/src/providers/matchers/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-dispatch/src/providers/matchers/).
- Internal walkthrough (the blanket-impl and per-variant-computer helpers, the matcher selection,
  the lifetime elaboration, and the index of behavioral tests):
  [implementation/entrypoints/cgp_auto_dispatch.md](../../implementation/entrypoints/cgp_auto_dispatch.md).
