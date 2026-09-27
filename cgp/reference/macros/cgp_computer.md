# `#[cgp_computer]`

`#[cgp_computer]` turns a plain function into a [`Computer`](../components/computer.md) provider: it
generates the provider struct, the provider impl, and the wiring that fills in the rest of the
handler family by promotion.

## Purpose

`#[cgp_computer]` lets a handler be written as an ordinary Rust function. A handler is normally a
provider struct with impls across [`Computer`](../components/computer.md),
[`TryComputer`](../components/try_computer.md), `AsyncComputer`, and
[`Handler`](../components/handler.md), each carrying the same `context`, `code`, and `input`
plumbing. For a computation as small as adding two numbers, that plumbing outweighs the computation.
The macro plays the role for handlers that [`#[cgp_fn]`](cgp_fn.md) plays for blanket-impl traits:
the author writes only the function, and the macro builds the provider around it.

One function definition yields a provider that serves every handler shape. The macro reads two facts
from the function's signature: whether it is `async`, and whether it returns a `Result`. From those
it picks a base trait to implement and a [promotion bundle](../providers/handler_combinators.md)
that derives the other traits from that base. The resulting provider answers `compute`,
`try_compute`, `compute_async`, `handle`, and their `…Ref` variants.

## Syntax

`#[cgp_computer]` is applied to a free function and takes an optional provider name:

```rust
#[cgp_computer]
fn add(a: u64, b: u64) -> u64 {
    a + b
}

#[cgp_computer(MyAdder)]
fn add(a: u64, b: u64) -> u64 {
    a + b
}
```

The provider's name defaults to the function name in PascalCase, so `add` produces `Add`, and an
explicit argument is used verbatim. The rest of the function maps onto the handler in these ways:

- **Parameters** become the handler's input.
- **The return type** becomes the handler's output, and decides between the value and `Result`
  bundles.
- **Generic parameters and the `where` clause** carry over to the generated impl.
- **`async`** selects the asynchronous base trait.

A function with a `self` receiver is rejected with `Computer functions cannot have a receiver`. A
handler provider has no receiver of its own, because the handler machinery passes the context in as
a separate argument.

## Syntax Grammar

The attribute argument is a single optional provider name:

```ebnf
CgpComputerArgs -> ProviderName?

ProviderName    -> IDENTIFIER
```

An omitted name defaults to the function name in PascalCase. The annotated function itself is plain
Rust; the macro reads its shape to choose the base trait and bundle, as Expansion describes.

## Expansion

The macro emits three items: the original function unchanged, a `#[cgp_new_provider]` impl of a base
handler trait that calls the function, and a `delegate_components!` block that wires the other
handler components to a promotion bundle. Two independent choices decide the base trait and the
bundle, as this table shows:

| Function | Base trait | Bundle for the other components |
|---|---|---|
| synchronous, returns a value | `Computer` | `PromoteComputer<Self>` |
| synchronous, returns `Result<T, E>` | `Computer` | `PromoteTryComputer<Self>` |
| `async`, returns a value | `AsyncComputer` | `PromoteAsyncComputer<Self>` |
| `async`, returns `Result<T, E>` | `AsyncComputer` | `PromoteHandler<Self>` |

### The synchronous, value-returning case

A synchronous function returning a plain value implements [`Computer`](../components/computer.md).
Given:

```rust
#[cgp_computer]
fn add(a: u64, b: u64) -> u64 {
    a + b
}
```

the macro emits the function followed by:

```rust
#[cgp_new_provider]
impl<__Context__, __Code__> Computer<__Context__, __Code__, (u64, u64)> for Add {
    type Output = u64;

    fn compute(
        _context: &__Context__,
        _code: PhantomData<__Code__>,
        (arg_0, arg_1): (u64, u64),
    ) -> Self::Output {
        add(arg_0, arg_1)
    }
}

delegate_components! {
    Add {
        [
            ComputerRefComponent,
            TryComputerComponent,
            TryComputerRefComponent,
            AsyncComputerComponent,
            AsyncComputerRefComponent,
            HandlerComponent,
            HandlerRefComponent,
        ] ->
            PromoteComputer<Self>,
    }
}
```

The input type is the function's parameter types written inside parentheses, and the body
destructures it back into arguments. Two parameters give the tuple `(u64, u64)`. A single parameter
gives `(u64)`, which is the type `u64` itself rather than a one-element tuple, so a one-argument
computer is called with the bare value. No parameters give `()`.

The `#[cgp_new_provider]` attribute declares the `Add` struct and derives its `IsProviderFor` impl,
as it does for any provider. The context and code parameters use the reserved names `__Context__`
and `__Code__`. The `delegate_components!` block forwards every other handler component to
[`PromoteComputer<Self>`](../providers/handler_combinators.md), which derives `TryComputer`,
`AsyncComputer`, `Handler`, and the `…Ref` variants from the `Computer` impl. So `Add` answers
`compute`, `try_compute`, `compute_async`, and `handle`, each computing `a + b`.

### Returning a `Result`

A synchronous function returning `Result` keeps `Computer` as its base, with the `Result` as its
`Output`, and switches the bundle to
[`PromoteTryComputer<Self>`](../providers/handler_combinators.md). That bundle treats the `Result`
as success or failure rather than as a plain value, so `try_compute` and `handle` propagate the
`Err`. Given:

```rust
#[cgp_computer]
fn add_with_error(a: u64, b: u64) -> Result<u64, String> {
    a.checked_add(b).ok_or_else(|| "Overflow".to_string())
}
```

the `Computer` impl has `Output = Result<u64, String>`, and the other components forward to
`PromoteTryComputer<Self>`. The detection is purely syntactic, and Known issues lists the spellings
it misses.

### Asynchronous functions

An `async` function implements `AsyncComputer` instead: the generated method is `compute_async`, and
it `.await`s the function call. A value-returning async function forwards the other components to
[`PromoteAsyncComputer<Self>`](../providers/handler_combinators.md), and one returning `Result`
forwards them to [`PromoteHandler<Self>`](../providers/handler_combinators.md). Both forward only
`AsyncComputerRefComponent`, `HandlerComponent`, and `HandlerRefComponent`, because the synchronous
members of the family cannot be derived from an async base.

### Generics and references

The function's generic parameters and bounds move onto the generated impl, ahead of `__Context__`
and `__Code__`. For example:

```rust
#[cgp_computer]
pub fn add_generic<T: core::ops::Add<Output = T>>(a: T, b: T) -> T {
    a + b
}
```

produces an impl over `<T: Add<Output = T>, __Context__, __Code__>`, so the provider `AddGeneric` is
itself generic over `T`. A reference parameter is preserved in the input type:
`fn to_string_ref<Value: Display>(value: &Value) -> String` becomes a `Computer` whose input is
`&Value`. The `PromoteComputer` bundle's `PromoteRef` entries then let it serve the `…Ref`
components too.

## Examples

This example defines a computer and a context that supplies the error type the fallible shapes need,
then calls every handler shape on the one provider:

```rust
use cgp::prelude::*;
use cgp::core::error::ErrorTypeProviderComponent;
use cgp::extra::handler::{AsyncComputer, Computer, Handler, TryComputer};

#[cgp_computer]
fn add(a: u64, b: u64) -> u64 {
    a + b
}

pub struct App;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<String>,
    }
}

fn main() {
    assert_eq!(Add::compute(&App, PhantomData::<()>, (1, 2)), 3);
    assert_eq!(Add::try_compute(&App, PhantomData::<()>, (1, 2)), Ok(3));

    // Both futures resolve to the same result: 3 and Ok(3).
    let _future = Add::compute_async(&App, PhantomData::<()>, (1, 2));
    let _future = Add::handle(&App, PhantomData::<()>, (1, 2));
}
```

Because `add` returns a plain `u64`, `try_compute` and `handle` always succeed. Defining
`add_with_error` instead makes the same calls return `Err("Overflow")` when the addition overflows,
with no change at the call sites.

## Related constructs

These constructs are the ones `#[cgp_computer]` builds on or parallels:

- [`Computer`](../components/computer.md): the component the macro implements, or `AsyncComputer`
  for an `async` function; the family is described in [handlers](../../concepts/handlers.md).
- [`#[cgp_producer]`](cgp_producer.md): the counterpart for a function with no input, producing a
  [`Producer`](../components/producer.md).
- [`#[cgp_fn]`](cgp_fn.md): the same function-to-construct idea for a blanket-impl trait rather than
  a handler provider.
- [`#[cgp_new_provider]`](cgp_new_provider.md): the attribute the generated impl is emitted through.
- [Promotion bundles](../providers/handler_combinators.md): `PromoteComputer`, `PromoteTryComputer`,
  `PromoteAsyncComputer`, and `PromoteHandler`, wired through
  [`delegate_components!`](delegate_components.md) to fill in the family.

## Known issues

The choice between the value and `Result` bundles is made from the return type's tokens, not its
meaning. A return type counts as a `Result` only when it is written as the bare path `Result<T, E>`,
with `Result` as its only segment and exactly two arguments. Any other spelling is treated as a
plain value: `core::result::Result<u64, String>`, `io::Result<u64>`, and `anyhow::Result<u64>` all
select `PromoteComputer`, so `try_compute` and `handle` wrap the whole result in `Ok` instead of
propagating its error.

A one-argument alias written as `Result<u64>`, such as the one `use anyhow::Result;` brings into
scope, fails outright. The macro expects a second argument and reports
``expected `,` ``. Write the full `Result<T, E>` form in the signature of a fallible computer.

## Source

- Entrypoint:
  [crates/macros/cgp-extra-macro/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro/src/lib.rs),
  forwarding to the implementation in
  [crates/macros/cgp-extra-macro-lib/src/entrypoints/cgp_computer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro-lib/src/entrypoints/cgp_computer.rs).
- `Result`-versus-value detection: the `MaybeResultType` parser in
  [crates/macros/cgp-extra-macro-lib/src/parse/maybe_result.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro-lib/src/parse/maybe_result.rs).
- Base `Computer`/`AsyncComputer` traits:
  [crates/extra/cgp-handler/src/components/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-handler/src/components/);
  the promotion bundles in
  [crates/extra/cgp-handler/src/providers/promote_all.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/providers/promote_all.rs).
- Internal walkthrough (the sync/async and value/`Result` branching, the generated items, and the
  index of behavioral tests):
  [implementation/entrypoints/cgp_computer.md](../../implementation/entrypoints/cgp_computer.md).
