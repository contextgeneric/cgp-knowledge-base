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
`handle`, and the `…Ref` variants, and each returns the same produced value. Its usual place is the
first step of a pipeline, as in `PipeHandlers<Product![MagicNumber, Double]>`, where it seeds the
value the later steps transform.

**The function cannot reach its context**, since it has no parameters at all, so a producer that
reads a field, names an abstract type, or calls another trait is a `Producer` provider written with
[`#[cgp_impl]`](cgp_impl.md). That covers most real producers, which leaves this macro for
constants and pure seeds. A step that should pass its input through unchanged is
[`ReturnInput`](../providers/handler_combinators.md) rather than a producer.

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
`MagicNumber`, and an explicit argument is used verbatim. A raw identifier loses its `r#` prefix
first, so `r#loop` produces `Loop`. The return type becomes the producer's
output, and an omitted return type is `()`.

The function must have the shape a producer can take, and the macro rejects each departure with an
error pointing at the offending part of the signature:

- **Parameters**: a producer takes no input and no receiver, so any parameter fails with
  `Producer functions cannot have parameters`.
- **`async`**: the `Producer` trait is synchronous, so an `async` function fails with
  `Producer functions cannot be async`.
- **Generic parameters**: the generated impl has no place for them, so they fail with
  `Producer functions must have empty generic parameters`.
- **`impl Trait` in the return type**: the generated impl's `Output` type cannot hold it, so it
  fails with ``Producer functions cannot return `impl Trait` ``.

## Syntax Grammar

The attribute argument is a single optional provider name:

```ebnf
CgpProducerArgs -> ProviderName?

ProviderName    -> IDENTIFIER
```

An omitted name defaults to the function name in PascalCase. The annotated function is plain Rust,
constrained to a producer's shape as Syntax describes.

## Expansion

The macro's expansion is three items: the original function unchanged, a `#[cgp_new_provider]` impl
of [`Producer`](../components/producer.md) that calls the function, and a `delegate_components!`
block that wires the rest of the handler family to the
[`PromoteProducer`](../providers/handler_combinators.md) bundle. The macro builds those two macros'
input itself and lowers it in place, so what it emits is their expansion with every CGP name fully
qualified, and the generated code needs no `use cgp::prelude::*` in scope. The form below shows that
input, which is the readable view. Given:

```rust
#[cgp_producer]
pub fn magic_number() -> u64 {
    42
}
```

the macro emits the function followed by the expansion of:

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
returned as a plain value, wrapped in `Ok` by the fallible shapes, so a producer returning
`Err("nope")` gives `try_compute` the value `Ok(Err("nope"))`: a success carrying an error, which
short-circuits nothing downstream. A production that can fail is a `TryComputer` or `Handler`
provider written by hand. The fallible shapes also need the context to wire
`ErrorTypeProviderComponent`, imported from `cgp::core::error`, while `produce` and `compute` do
not.

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
  [crates/macros/cgp-macro-extra/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra/src/lib.rs),
  forwarding to
  [crates/macros/cgp-macro-extra-lib/src/cgp_producer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/cgp_producer.rs).
- The parsing and codegen:
  [crates/macros/cgp-macro-extra-core/src/types/cgp_producer/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/types/cgp_producer/).
- `Producer` trait:
  [crates/extra/cgp-handler/src/components/produce.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/components/produce.rs);
  the `PromoteProducer` bundle in
  [crates/extra/cgp-handler/src/providers/promote_all.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/providers/promote_all.rs).
- Internal walkthrough (the signature validation, the generated items, and the index of behavioral
  tests):
  [implementation/entrypoints/cgp_producer.md](../../implementation/entrypoints/cgp_producer.md).
