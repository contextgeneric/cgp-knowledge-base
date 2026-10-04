# The `cgp_computer` AST stack

The `cgp_computer` stack is the AST types `#[cgp_computer]` moves through: `ItemCgpComputer`, the
`MaybeResultType` it reads the return type with, and `PreprocessedCgpComputer`, ending in
`EvaluatedHandlerFn`, the intermediate representation (IR) the computer and producer macros share.
Data flows in one direction: an optional provider-name `Ident` plus a `syn::ItemFn` become
`ItemCgpComputer`, which `preprocess`es into `PreprocessedCgpComputer`, whose `eval` builds the IR
out of `cgp-macro-core` AST nodes for the entrypoint to lower. The
[entrypoint document](../entrypoints/cgp_computer.md) covers what the macro emits; this document
covers the types.

## `ItemCgpComputer`

`ItemCgpComputer` is the raw input stage: the attribute's optional provider name and the annotated
function. `#[cgp_auto_dispatch]` constructs one directly, per dispatch method, as part of its own IR,
so it is also the computer pipeline's entry for code that is not a written `#[cgp_computer]`.

Its `preprocess` reads everything the expansion depends on. It resolves the provider name (the
attribute identifier, or `derive_provider_ident`'s unrawed PascalCase of the function name), walks
the parameters, rejecting a `self` receiver and any `impl Trait` in a parameter type, and records
each remaining parameter's type with a positional `arg_i` identifier spanned on that parameter. It
then reads the return type with the shared `return_type` helper, rejects any `impl Trait` in it,
re-parses it as a `MaybeResultType`, and records whether the function is `async`.

## `MaybeResultType`

`MaybeResultType` is a `Parse` type that answers one question about a return type: is it the bare
`Result<T, E>`? It forks the input and checks whether the first token is the identifier `Result`.
If it is, it demands exactly `<`, a type, `,`, a type, and `>`, recording the error type, and turns
any failure into the error "A `Result` return type must be written as `Result<T, E>`, naming its
error type" on the `Result` token. Otherwise it parses any type and records no error type. The
re-parse runs on the user's own return-type tokens with `parse2`, so an error keeps the span of the
offending token.

## `PreprocessedCgpComputer`

`PreprocessedCgpComputer` holds the resolved provider name, the function, the positional input
identifiers and types, the output type, and the two flags `is_async` and `is_fallible`. Its `eval`
builds the IR. The base impl carries the function's generics with `__Context__` and `__Code__`
appended, implements `Computer` (or `AsyncComputer` for an `async` function) over the parenthesized
input types, and calls the function from `compute` (or `.await`s it from `compute_async`); its
boundary tokens are re-spanned onto the function identifier by `override_item_span`. The wiring is a
`DelegateTable` routing the remaining handler components, with the `->` operator, to the bundle the
two flags select: `PromoteComputer`, `PromoteTryComputer`, `PromoteAsyncComputer`, or
`PromoteHandler`, each applied to `Self`.

## `EvaluatedHandlerFn`

`EvaluatedHandlerFn` is the IR both function macros evaluate into, made of `cgp-macro-core` AST nodes
rather than emitted macro invocations:

- `item_fn`: the annotated function, emitted unchanged;
- `provider`: the base impl as an `ItemCgpProvider` with `new` set and its component given
  explicitly, the node `#[cgp_new_provider]` would build from the same impl;
- `delegate_table`: the promotion wiring as a `DelegateTable`, the node `delegate_components!` would
  parse from the same body.

The entrypoint lowers it with the owning types' own methods, `ItemCgpProvider::lower` and
`DelegateTable::eval`, through a helper in `cgp-macro-extra-lib` that both function macros and the
dispatch macro call, so the expansion is the final code in one step.

## Tests

- The stages are exercised end to end by the snapshots and behavioral tests indexed in the
  [entrypoint document](../entrypoints/cgp_computer.md).
- The rejections `preprocess` and `MaybeResultType` enforce are pinned, with their messages, by
  [parser_rejections/cgp_computer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/cgp_computer.rs).

## Source

- The stack lives in
  [cgp-macro-extra-core/src/types/cgp_computer/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/types/cgp_computer/):
  `ItemCgpComputer` in `item.rs`, `MaybeResultType` in `maybe_result.rs`, and
  `PreprocessedCgpComputer` with its `eval` in `preprocessed.rs`.
- `EvaluatedHandlerFn` is in
  [cgp-macro-extra-core/src/types/handler_fn/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/types/handler_fn/),
  and its lowering in
  [cgp-macro-extra-lib/src/handler_fn.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/handler_fn.rs).
- The shared helpers `derive_provider_ident` and `return_type` are in
  [cgp-macro-extra-core/src/functions/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/functions/),
  and `find_impl_trait` in
  [cgp-macro-extra-core/src/visitors/find_impl_trait.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-core/src/visitors/find_impl_trait.rs).
- The IR it lowers through is [the `cgp_provider` stack](cgp_provider.md) and
  [the `delegate_component` stack](delegate_component.md).
