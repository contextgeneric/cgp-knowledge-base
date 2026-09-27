# `#[cgp_producer]`

`#[cgp_producer]` turns a function with no parameters into a [`Producer`](../components/producer.md)
provider: it generates the provider struct, the provider impl, and the wiring that returns the
produced value from every handler shape.

## Purpose

`#[cgp_producer]` defines a handler that takes no input, such as one returning a constant. It is the
input-less sibling of [`#[cgp_computer]`](cgp_computer.md): the author writes a plain function, and
the macro builds the provider struct and impl around it. Where `#[cgp_computer]` implements a
[`Computer`](../components/computer.md), `#[cgp_producer]` implements a
[`Producer`](../components/producer.md), whose method takes only the context and the `Code` tag.

A single producer serves the whole handler family, because a handler that ignores its input behaves
like a producer. The macro therefore wires the generated provider into every member of the family.
One `#[cgp_producer]` function answers `produce`, `compute`, `try_compute`, `compute_async`,
`handle`, and the `…Ref` variants, and each returns the same produced value.

## Syntax

`#[cgp_producer]` is applied to a free function and takes an optional provider name:

```rust
#[cgp_producer]
fn magic_number() -> u64 {
    42
}

#[cgp_producer(TheAnswer)]
fn magic_number() -> u64 {
    42
}
```

The provider's name defaults to the function name in PascalCase, so `magic_number` produces
`MagicNumber`, and an explicit argument is used verbatim. The return type becomes the producer's
output.

The function must have the shape a producer can take, and the macro rejects each departure with an
error pointing at the offending part of the signature:

- **Parameters**: a producer takes no input and no receiver, so any parameter fails with
  `Producer functions cannot have parameters`.
- **`async`**: the `Producer` trait is synchronous, so an `async` function fails with
  `Producer functions cannot be async`.
- **Generic parameters**: the generated impl has no place for them, so they fail with
  `Producer functions must have empty generic parameters`.

## Syntax Grammar

The attribute argument is a single optional provider name:

```ebnf
CgpProducerArgs -> ProviderName?

ProviderName    -> IDENTIFIER
```

An omitted name defaults to the function name in PascalCase. The annotated function is plain Rust,
constrained to a producer's shape as Syntax describes.

## Expansion

The macro emits three items: the original function unchanged, a `#[cgp_new_provider]` impl of
[`Producer`](../components/producer.md) that calls the function, and a `delegate_components!` block
that wires the rest of the handler family to the
[`PromoteProducer`](../providers/handler_combinators.md) bundle. Given:

```rust
#[cgp_producer]
pub fn magic_number() -> u64 {
    42
}
```

the macro emits the function followed by:

```rust
#[cgp_new_provider]
impl<__Context__, __Code__> Producer<__Context__, __Code__> for MagicNumber {
    type Output = u64;

    fn produce(_context: &__Context__, _code: PhantomData<__Code__>) -> Self::Output {
        magic_number()
    }
}

delegate_components! {
    MagicNumber {
        [
            ComputerComponent,
            ComputerRefComponent,
            TryComputerComponent,
            TryComputerRefComponent,
            AsyncComputerComponent,
            AsyncComputerRefComponent,
            HandlerComponent,
            HandlerRefComponent,
        ]:
            PromoteProducer<Self>,
    }
}
```

The `#[cgp_new_provider]` attribute declares the `MagicNumber` struct and derives its
`IsProviderFor` impl. The context and code parameters use the reserved names `__Context__` and
`__Code__`, and `produce` ignores both and calls the function.

The `delegate_components!` block maps all eight handler components to
[`PromoteProducer<Self>`](../providers/handler_combinators.md), an aggregate provider built for a
producer base. Inside that bundle, `ComputerComponent` goes to `Promote<Self>`, which discards the
computer's input and calls `produce`, and the remaining components are forwarded to
`PromoteComputer<Self>`, which derives them from that computer. So every handler shape returns the
produced value, whatever input it is given.

The expansion has one form. Unlike `#[cgp_computer]`, the macro does not look for a `Result` return,
so there is one base trait and one bundle for every `#[cgp_producer]` function. A `Result` output is
returned as a plain value, wrapped in `Ok` by the fallible shapes.

## Examples

This example defines a producer and a context that supplies the error type the fallible shapes need,
then reads the value through each handler shape:

```rust
use cgp::prelude::*;
use cgp::core::error::ErrorTypeProviderComponent;
use cgp::extra::handler::{Computer, Handler, Producer, TryComputer};

#[cgp_producer]
pub fn magic_number() -> u64 {
    42
}

pub struct App;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<String>,
    }
}

fn main() {
    assert_eq!(MagicNumber::produce(&App, PhantomData::<()>), 42);
    assert_eq!(MagicNumber::compute(&App, PhantomData::<()>, ()), 42);
    assert_eq!(MagicNumber::try_compute(&App, PhantomData::<()>, "ignored"), Ok(42));

    // The future resolves to Ok(42).
    let _future = MagicNumber::handle(&App, PhantomData::<()>, ());
}
```

The computer and handler shapes accept an input of any type and ignore it. The fallible shapes need
the context's error type to form their `Result`, which is why `App` wires
`ErrorTypeProviderComponent`, but they always return `Ok`.

## Related constructs

These constructs are the ones `#[cgp_producer]` builds on or parallels:

- [`Producer`](../components/producer.md): the component the macro implements, part of the family
  described in [handlers](../../concepts/handlers.md).
- [`#[cgp_computer]`](cgp_computer.md): the counterpart for a function with parameters, producing a
  [`Computer`](../components/computer.md).
- [`#[cgp_fn]`](cgp_fn.md): the same function-to-construct idea for a blanket-impl trait.
- [`#[cgp_new_provider]`](cgp_new_provider.md): the attribute the generated impl is emitted through.
- [`PromoteProducer`](../providers/handler_combinators.md): the bundle that lifts the producer into
  the whole family, wired through [`delegate_components!`](delegate_components.md).

## Source

- Entrypoint:
  [crates/macros/cgp-extra-macro/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro/src/lib.rs),
  forwarding to the implementation in
  [crates/macros/cgp-extra-macro-lib/src/entrypoints/cgp_producer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro-lib/src/entrypoints/cgp_producer.rs).
- `Producer` trait:
  [crates/extra/cgp-handler/src/components/produce.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/components/produce.rs);
  the `PromoteProducer` bundle in
  [crates/extra/cgp-handler/src/providers/promote_all.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/providers/promote_all.rs).
- Internal walkthrough (the signature validation, the generated items, and the index of behavioral
  tests):
  [implementation/entrypoints/cgp_producer.md](../../implementation/entrypoints/cgp_producer.md).
