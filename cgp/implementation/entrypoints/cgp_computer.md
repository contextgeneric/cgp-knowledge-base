# `#[cgp_computer]`: implementation

`#[cgp_computer]` turns a plain function into a [`Computer`](../../reference/components/computer.md)
(or `AsyncComputer`) provider: it evaluates the function into an intermediate representation (IR)
of a provider impl that calls the function and a wiring table that promotes the rest of the handler
family from that base, then lowers the IR through `cgp-macro-core`. This document covers how the
macro is built; for the accepted syntax and the full expansion a user sees, read the reference
document [reference/macros/cgp_computer.md](../../reference/macros/cgp_computer.md).

## Entry point

The macro is the `cgp_computer` function in
[cgp-macro-extra-lib/src/cgp_computer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/cgp_computer.rs),
forwarded from the proc-macro shim in `cgp-macro-extra`. It parses the body into a `syn::ItemFn`
and the attribute into an `Option<Ident>`, builds an `ItemCgpComputer`, and runs
`preprocess()?.eval()?` to get an `EvaluatedHandlerFn`, the IR it shares with
[`#[cgp_producer]`](cgp_producer.md). A lib-local helper then lowers the IR: the function
unchanged, `ItemCgpProvider::lower` for the provider, and `DelegateTable::eval` for the wiring. The
stages live in `cgp-macro-extra-core` and are documented in the
[`cgp_computer` AST stack](../asts/cgp_computer.md).

`#[cgp_auto_dispatch]` uses the same stages: its IR holds one `ItemCgpComputer` per dispatch
method, which its entrypoint runs through this pipeline instead of emitting a nested
`#[cgp_computer]` attribute.

## Pipeline

The pipeline is two stages followed by the IR's own lowering, and it reads two independent facts
off the signature:

- **`preprocess`** resolves the provider name, rebinds each parameter positionally as `arg_i`
  (keeping only its type), reads the return type, and records whether the function is `async` and
  whether it returns `Result<T, E>`. It rejects a `self` receiver ("Computer functions cannot have
  a receiver") and `impl Trait` anywhere in a parameter type ("Computer function parameters cannot
  use `impl Trait`; declare a generic parameter instead") or in the return type ("Computer
  functions cannot return `impl Trait`"), each through `Error::new_spanned`. The `impl Trait`
  search is the `find_impl_trait` visitor.
- **`eval`** builds the IR from those facts: the provider impl as an `ItemCgpProvider` with `new`
  set and its component given explicitly (`ComputerComponent` or `AsyncComputerComponent`), and
  the promotion wiring as a `DelegateTable` parsed from quoted tokens.
- **Lowering** turns the IR into the final items, exactly as `#[cgp_new_provider]` and
  `delegate_components!` would on the same input.

The two facts choose the expansion:

- **Sync vs. async**: `async` selects an `AsyncComputer` base with an `async fn compute_async` that
  `.await`s the call, instead of a `Computer` base with `compute`.
- **Value vs. `Result`**: the return type is re-parsed as a `MaybeResultType`, a speculative parser
  that reports whether it is written as the bare `Result<T, E>`. This choice does not change the
  base impl (the `Output` associated type is the return type verbatim); it only selects the
  promotion bundle.

## Generated items

The macro emits the original function unchanged, then the lowered provider (the base impl, its
`IsProviderFor` impl, and the provider struct), then the lowered wiring. The IR's base impl writes
the parameter types inside parentheses as the input type and destructures it back into the
positional bindings before calling the function:

```rust
// IR for `#[cgp_computer] fn add(a: u64, b: u64) -> u64 { a + b }`, as an ItemCgpProvider with `new`:
impl<__Context__, __Code__> Computer<__Context__, __Code__, (u64, u64)> for Add {
    type Output = u64;

    fn compute(
        _context: &__Context__,
        _code: ::core::marker::PhantomData<__Code__>,
        (arg_0, arg_1): (u64, u64),
    ) -> Self::Output {
        add(arg_0, arg_1)
    }
}
```

The function's own generics and `where` clause carry over onto the impl, and the reserved
`__Context__` and `__Code__` parameters are appended after them, so a generic function stays
generic in its provider. The IR's wiring table routes every remaining handler component to a
promotion bundle with the `->` operator, chosen by the two facts:

- **sync, value** → `PromoteComputer<Self>`, over the seven non-`Computer` components.
- **sync, `Result`** → `PromoteTryComputer<Self>`, over the same seven components.
- **async, value** → `PromoteAsyncComputer<Self>`, over the smaller async set
  (`AsyncComputerRefComponent`, `HandlerComponent`, `HandlerRefComponent`).
- **async, `Result`** → `PromoteHandler<Self>`, over the same async set.

The async branches delegate fewer components because the synchronous members of the family are not
derivable from an async base. Every CGP name is emitted through an `exports` marker, so the
expansion resolves with only `cgp` in scope and no local item can capture a name.

The base impl's boundary tokens are re-spanned onto the function identifier with
`override_item_span`, so an error on the impl, such as two computers declaring the same provider,
points at the function rather than the whole attribute. The provider name derived from the function
is spanned on the function identifier too.

## Behavior and corner cases

**Parameter patterns are discarded.** Each input is rebound positionally as `arg_i`, so a `mut`
binding or a destructuring pattern in the source signature is replaced by a plain binding, and the
function itself keeps its own pattern.

**The input type is parenthesized, not always a tuple.** The parameter types are joined with commas
and no trailing comma, so two parameters give the tuple `(u64, u64)`, a single parameter gives
`(u64)`, which is the type `u64` itself, and no parameters give `()`.

**A reference parameter is kept verbatim**, so `fn f(value: &Value)` has the input type `&Value`.
The `PromoteComputer` bundle's `…Ref` entries then make the provider serve the `…Ref` components as
well.

**The `Result` detection is purely syntactic, by design.** `MaybeResultType` forks the token stream
and checks whether the return type's first token is the identifier `Result`. If it is, the parser
demands exactly `<`, a type, `,`, a type, and `>`, and anything else after `Result`, such as the
one-argument alias `Result<u64>`, is rejected with "A `Result` return type must be written as
`Result<T, E>`, naming its error type". If the first token is not `Result`, any type is accepted as
the value case, so a qualified `core::result::Result<u64, String>` is a plain value and its error is
wrapped in `Ok` rather than propagated. Only the bare two-argument form selects the fallible
bundles; the reference states this as the macro's rule.

**A raw function name is unrawed** before it becomes the provider name, so `r#type` names `Type`.

An **omitted return type** defaults to `()`, so a unit-returning function produces a value-case
`Computer` with `Output = ()`.

## Failure modes

**A `Result` error type that differs from the context's fails at the call.** The fallible bundles
pass the function's `Err` through unconverted, so `try_compute` and `handle` require the context's
abstract error type to equal the function's. The macro has no view of the context it will be called
with, so it defers the mismatch to the compiler, which reports `E0271` at the call with a note
pointing at the function's return type:

```rust
#[cgp_computer]
fn checked_add(a: u64, b: u64) -> Result<u64, String> { /* … */ }

// App wires ErrorTypeProviderComponent: UseType<()>, so this fails with E0271:
CheckedAdd::try_compute(&App, PhantomData::<()>, (1, 2));
```

The class is described under [E0271](../../errors/error_codes/e0271.md), and the `cargo-cgp` fixture
[`acceptable/types/computer_result_error_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/types/computer_result_error_mismatch.rs)
pins it.

## Known issues

**A type parameter that appears only in the return type is unconstrained.** The function's generics
move onto the base impl, whose trait arguments carry only the input type, so a parameter used only
in the output, as in `fn parse<T: FromStr>(value: String) -> Option<T>`, is constrained by neither
the trait arguments nor the self type, and the impl fails with `E0207`, its caret on the `T` the user
wrote. Accepting such a function would need the provider struct itself to be generic over the
output-only parameters (`Parse<T>`), which changes how it is named and wired, so the macro does not
yet do it; a function like this has to be written as a hand-made `Computer` provider. The
[unconstrained generic](../../errors/wiring/unconstrained-generic.md) class covers the error, and the
`cargo-cgp` fixture
[`acceptable/lowering/computer_output_only_type_parameter.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/lowering/computer_output_only_type_parameter.rs)
pins it.

**Argument-position `impl Trait` is rejected rather than lowered.** It is sugar for an anonymous
generic parameter, which the macro otherwise accepts, so the correct behavior would be to rewrite
each one into a fresh named type parameter. The macro rejects it with a spanned error instead.

## Snapshots

Each expansion variant is pinned in the `handlers` target:

- [handlers/computer_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro.rs):
  the synchronous value case (`expand_add`), the synchronous `Result` case
  (`expand_add_with_error`), and a generic function with a trait bound (`expand_add_generic`).
- [handlers/handler_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/handler_macro.rs):
  the async value (`expand_async_add`) and async `Result` (`expand_async_add_with_error`) cases.
- [handlers/computer_macro_named.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro_named.rs):
  an explicit provider name.
- [handlers/computer_macro_arity.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro_arity.rs):
  no parameters (`()` input) and one parameter (the parenthesized bare type).
- [handlers/computer_macro_generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro_generics.rs):
  a `where` clause, a lifetime parameter, and a const generic parameter.
- [handlers/computer_macro_output.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro_output.rs):
  an omitted return type, and a qualified `core::result::Result` that selects `PromoteComputer`.

There is no snapshot of a reference parameter or a raw function name; both are pinned behaviorally.

## Tests

The behavioral tests exercise the generated provider across the handler family:

- [handlers/computer_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro.rs):
  a synchronous infallible function, a `Result`-returning function, a reference parameter, and a
  generic function, each called as `compute`, `try_compute`, `compute_async`, and `handle` plus
  their `…Ref` variants.
- [handlers/handler_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/handler_macro.rs):
  `async` functions (value, `Result`, and reference) reached through the async promotion into
  `Handler`.
- [handlers/computer_macro_arity.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro_arity.rs):
  zero and one parameters, a `mut` binding, and a destructuring pattern.
- [handlers/computer_macro_generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro_generics.rs),
  [handlers/computer_macro_named.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro_named.rs),
  [handlers/computer_macro_output.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro_output.rs):
  the generic, named, unit-return, and qualified-`Result` providers called through the family.
- [handlers/computer_macro_visibility.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/computer_macro_visibility.rs):
  a `pub fn` computer in a child module used from its parent.
- [handlers/raw_function_names.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/raw_function_names.rs):
  a function named `r#type` names its provider `Type`.
- [handlers/macros_without_prelude.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/macros_without_prelude.rs):
  the macro invoked by path in a module without `cgp::prelude::*` that declares its own `Computer`.
- [handlers/pipe_computers.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/pipe_computers.rs),
  [handlers/pipe_handlers.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/pipe_handlers.rs):
  `#[cgp_computer]` providers composed through `PipeHandlers`.
- [dispatching/compose.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/compose.rs):
  `#[cgp_computer]` field-reader providers composed into a higher-order provider.
- [monadic_handlers/ok_monadic.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/monadic_handlers/ok_monadic.rs),
  [monadic_handlers/err_monadic.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/monadic_handlers/err_monadic.rs),
  [monadic_handlers/ok_err_monadic_trans.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/monadic_handlers/ok_err_monadic_trans.rs):
  `#[cgp_computer]` providers chained through the monadic combinators.

The failure cases pin each rejection and its message with `assert_macro_rejects_with`:

- [parser_rejections/cgp_computer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/cgp_computer.rs)
  covers a `self` receiver, a one-argument `Result<u64>` alias, an `impl Trait` parameter and
  return type, and a path as the provider name.

`cargo-cgp`'s
[`ok/handler_function_macros.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/handler_function_macros.rs)
pins the fully expanded code of each shape in its `.expand.rs`, and
[`ok/cross_crate_dispatch_enum.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/cross_crate_dispatch_enum.rs)
calls computers defined in another crate. The two compile-failure fixtures are linked under Failure
modes and Known issues.

## Source

- Entry point: `cgp_computer` in
  [cgp-macro-extra-lib/src/cgp_computer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/cgp_computer.rs),
  with the shared IR lowering in
  [cgp-macro-extra-lib/src/handler_fn.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/handler_fn.rs),
  forwarded from the proc-macro shim in
  [cgp-macro-extra/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra/src/lib.rs).
- The stages, including `MaybeResultType`: [the `cgp_computer` AST stack](../asts/cgp_computer.md),
  in
  [cgp-macro-extra-core/src/types/cgp_computer/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/types/cgp_computer/).
- The IR is lowered by [`#[cgp_new_provider]`](cgp_new_provider.md)'s `ItemCgpProvider` and
  [`delegate_components!`](delegate_components.md)'s `DelegateTable`.
- The input-less sibling macro is [`#[cgp_producer]`](cgp_producer.md).
