# `#[cgp_producer]`: implementation

`#[cgp_producer]` turns a no-argument function into a
[`Producer`](../../reference/components/producer.md) provider: it evaluates the function into the
same intermediate representation (IR) `#[cgp_computer]` uses, a provider impl plus a wiring table
that promotes the whole handler family from it, and lowers that IR through `cgp-macro-core`. This
document covers how the macro is built; for the accepted syntax and the full expansion, read the
reference document [reference/macros/cgp_producer.md](../../reference/macros/cgp_producer.md).

## Entry point

The macro is the `cgp_producer` function in
[cgp-macro-extra-lib/src/cgp_producer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/cgp_producer.rs),
forwarded from the proc-macro shim in `cgp-macro-extra`. It parses the body into a `syn::ItemFn`
and the attribute into an `Option<Ident>`, builds an `ItemCgpProducer`, and runs
`preprocess()?.eval()?` to get an `EvaluatedHandlerFn`. It then lowers that IR with the helper it
shares with `#[cgp_computer]`, which emits the function, the lowered provider, and the evaluated
wiring table. The stages live in `cgp-macro-extra-core` and are documented in the
[`cgp_producer` AST stack](../asts/cgp_producer.md).

## Pipeline

The pipeline is two stages followed by the IR's own lowering:

- **`preprocess`** validates the signature against a producer's constraints and resolves the
  provider name and output type. Each constraint is a `check_*` method that rejects with
  `Error::new_spanned`, so the caret covers the whole offending parameter list or generic list:
  - **No parameters**: a producer takes no input and no `self` receiver ("Producer functions
    cannot have parameters").
  - **Not `async`**: the `Producer` trait is synchronous ("Producer functions cannot be async").
  - **No generic parameters**, lifetimes included: the generated impl declares only the reserved
    context and code parameters, so any other parameter would be unconstrained ("Producer
    functions must have empty generic parameters").
  - **No `impl Trait` in the return type**, at any depth: it would become the impl's `Output`
    associated type, where `impl Trait` is not allowed ("Producer functions cannot return
    `impl Trait`").
- **`eval`** builds the IR: the provider as a `cgp-macro-core` `ItemCgpProvider` (with `new` set
  and the component given explicitly as `ProducerComponent`), and the promotion wiring as a
  `DelegateTable` parsed from quoted tokens.
- **Lowering**: `ItemCgpProvider::lower` and `DelegateTable::eval` produce the final items, the same
  calls `#[cgp_new_provider]` and `delegate_components!` make on their own input.

The provider name is the attribute identifier when one is given, otherwise the function name in
PascalCase from `derive_provider_ident`, which unraws the name first so `r#loop` names `Loop`, and
spans the derived name on the function identifier.

## Generated items

The macro emits the original function unchanged, then the lowered provider, then the lowered
wiring. The IR's provider impl introduces the reserved `__Context__` and `__Code__` parameters,
ignores both in its `produce` body, and calls the function:

```rust
// IR for `#[cgp_producer] fn magic_number() -> u64 { 42 }`, as an ItemCgpProvider with `new`:
impl<__Context__, __Code__> Producer<__Context__, __Code__> for MagicNumber {
    type Output = u64;

    fn produce(_context: &__Context__, _code: ::core::marker::PhantomData<__Code__>) -> Self::Output {
        magic_number()
    }
}
```

Lowering it adds the `IsProviderFor<ProducerComponent, __Context__, (__Code__)>` impl and declares
`pub struct MagicNumber;`. The IR's wiring table routes all eight handler components to the single
`PromoteProducer<Self>` bundle with the `:` operator, so each lowers to a `DelegateComponent` impl
with that bundle as its `Delegate` plus the matching `IsProviderFor` forwarding impl. The eight
include `ComputerComponent`, which `#[cgp_computer]` never delegates because there the computer
*is* the base. Every CGP name is emitted through an `exports` marker, so the expansion resolves with
only `cgp` in scope.

The provider impl's boundary tokens (its `impl` keyword and its body) are re-spanned onto the
function identifier with `override_item_span`, so an error on the impl, such as a conflict with
another provider of the same name, points at the function rather than the whole attribute.

## Behavior and corner cases

An **omitted return type** defaults to `()`. There is no `Result` analysis: the `Output` associated
type is the return type verbatim, whether or not it is a `Result`, so a fallible shape returns a
`Result` output wrapped in `Ok`.

The signature checks are the macro's only rejections, and each one rejects rather than
reinterprets. This is stricter than `#[cgp_computer]`, which accepts parameters, `async`, and
generics.

## Snapshots

The expansion is pinned in the `handlers` target:

- [handlers/producer_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/producer_macro.rs)
  (`expand_magic_number`): the canonical expansion, a provider named after its function.
- [handlers/producer_macro_output.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/producer_macro_output.rs)
  (`expand_named_producer`): an explicit provider name.

There is no snapshot of a raw function name or a unit return; both are pinned behaviorally below.

## Tests

The behavioral tests exercise the generated provider across the handler family:

- [handlers/producer_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/producer_macro.rs):
  an input-free function called as `produce`, `compute`, `try_compute`, `compute_async`, and
  `handle` plus their `…Ref` variants, all yielding the same value.
- [handlers/producer_macro_output.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/producer_macro_output.rs):
  an explicit name, an omitted return type, and a `Result` return that `try_compute` hands back as
  `Ok(Err(..))`.
- [handlers/raw_function_names.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/raw_function_names.rs):
  a function named `r#loop` names its provider `Loop`.
- [handlers/macros_without_prelude.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/handlers/macros_without_prelude.rs):
  the macro invoked by path in a module without `cgp::prelude::*`.

The failure cases pin each rejection and its message with `assert_macro_rejects_with`:

- [parser_rejections/cgp_producer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/cgp_producer.rs)
  covers a parameter, a `self` receiver, an `async` function, a generic parameter, an
  `impl Trait` return type, and a path as the provider name.

`cargo-cgp`'s
[`ok/handler_function_macros.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/handler_function_macros.rs)
fixture pins the fully expanded code in its `.expand.rs`, and
[`ok/cross_crate_dispatch_enum.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/cross_crate_dispatch_enum.rs)
calls a producer defined in another crate.

## Source

- Entry point: `cgp_producer` in
  [cgp-macro-extra-lib/src/cgp_producer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/cgp_producer.rs),
  with the shared IR lowering in
  [cgp-macro-extra-lib/src/handler_fn.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/handler_fn.rs),
  forwarded from the proc-macro shim in
  [cgp-macro-extra/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra/src/lib.rs).
- The stages: [the `cgp_producer` AST stack](../asts/cgp_producer.md), in
  [cgp-macro-extra-core/src/types/cgp_producer/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/types/cgp_producer/).
- The IR is lowered by [`#[cgp_new_provider]`](cgp_new_provider.md)'s `ItemCgpProvider` and
  [`delegate_components!`](delegate_components.md)'s `DelegateTable`.
- The input-carrying sibling macro is [`#[cgp_computer]`](cgp_computer.md).
