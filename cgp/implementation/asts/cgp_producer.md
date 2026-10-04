# The `cgp_producer` AST stack

The `cgp_producer` stack is the two AST types `#[cgp_producer]` moves through, `ItemCgpProducer` and
`PreprocessedCgpProducer`, ending in the `EvaluatedHandlerFn` intermediate representation (IR) it
shares with `#[cgp_computer]`. Data flows in one direction: an optional provider-name `Ident` plus a
`syn::ItemFn` become `ItemCgpProducer`, which `preprocess`es into `PreprocessedCgpProducer`, whose
`eval` builds the IR out of `cgp-macro-core` AST nodes for the entrypoint to lower. The
[entrypoint document](../entrypoints/cgp_producer.md) covers what the macro emits; this document
covers the types.

## `ItemCgpProducer`

`ItemCgpProducer` is the raw input stage: the attribute's optional provider name and the annotated
function. Its `preprocess` runs the producer's signature checks, each a private `check_*` method that
rejects through `Error::new_spanned` (no parameters, not `async`, no generic parameters), rejects an
`impl Trait` anywhere in the return type through the `find_impl_trait` visitor, and then resolves
the two facts the next stage needs. The provider name is the attribute identifier, or the function
name in PascalCase from `derive_provider_ident`, which unraws a raw identifier and spans the result
on the function identifier. The output type is the return type, read as `()` when omitted, by the
shared `return_type` helper.

## `PreprocessedCgpProducer`

`PreprocessedCgpProducer` holds the resolved provider name, the function, and the output type. Its
`eval` builds the [`EvaluatedHandlerFn`](cgp_computer.md#evaluatedhandlerfn) IR:

- the provider as an `ItemCgpProvider` with `new` set and `ProducerComponent` given explicitly as
  its component, wrapping a `Producer<__Context__, __Code__>` impl whose `produce` calls the
  function, with its boundary tokens re-spanned onto the function identifier by
  `override_item_span`;
- the wiring as a `DelegateTable` mapping all eight handler components to `PromoteProducer<Self>`
  with the `:` operator.

Both nodes are built with `parse_internal!` from quoted tokens, naming every CGP item through the
crate's `exports` markers.

## Tests

- The stages are exercised end to end by the snapshots and behavioral tests indexed in the
  [entrypoint document](../entrypoints/cgp_producer.md).
- The rejections `preprocess` enforces are pinned, with their messages, by
  [parser_rejections/cgp_producer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/cgp_producer.rs).

## Source

- The stack lives in
  [cgp-macro-extra-core/src/types/cgp_producer/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/types/cgp_producer/):
  `ItemCgpProducer` and its checks in `item.rs`, `PreprocessedCgpProducer` and its `eval` in
  `preprocessed.rs`.
- The shared helpers `derive_provider_ident` and `return_type` are in
  [cgp-macro-extra-core/src/functions/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/functions/),
  and `find_impl_trait` in
  [cgp-macro-extra-core/src/visitors/find_impl_trait.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-core/src/visitors/find_impl_trait.rs).
- The IR it lowers through is [the `cgp_provider` stack](cgp_provider.md) and
  [the `delegate_component` stack](delegate_component.md).
