# The `cgp_component` AST stack

The `cgp_component` stack is the sequence of AST types `#[cgp_component]` parses into and transforms
through: the two argument types, then the pipeline stages `ItemCgpComponent`,
`PreprocessedCgpComponent`, and `EvaluatedCgpComponent`. Each stage is a plain struct holding what
the next one needs, and the data flows one way: the args and a `syn::ItemTrait` form an
`ItemCgpComponent`, which `preprocess` turns into a `PreprocessedCgpComponent`, which `eval` turns
into an `EvaluatedCgpComponent`, whose `to_items` renders a `Vec<syn::Item>`. The
[entrypoint document](../entrypoints/cgp_component.md) covers what each stage produces; this
document covers the types.

## `CgpComponentRawArgs` and `CgpComponentArgs`

The attribute argument is parsed in two steps so that parsing and defaulting stay separate.
`CgpComponentRawArgs` records what the user wrote as three `Option`s, and `CgpComponentArgs` holds
the same three fields resolved.

`CgpComponentRawArgs` accepts either a bare provider identifier or a comma-separated `key: value`
list over the keys `provider`, `context`, and `name`:

```rust
#[cgp_component(AreaCalculator)]                            // bare form
#[cgp_component { provider: AreaCalculator, context: Cx }]  // keyed form
```

The bare form is taken only when the input is exactly one token, so anything longer is read as the
keyed form. A repeated key fails with `duplicate key is not allowed` and any other key with
`unknown key <key>`. The `name` key parses an `IdentWithTypeGenerics`, so a component name may
declare generic parameters, as in `name: AreaCalculatorComponent<Shape>`, and the marker struct is
then generic too.

`CgpComponentArgs` comes from the raw form through a `TryFrom` that applies the defaults: `provider`
is required (``the `provider` key must be given``), `context` defaults to `__Context__`, and `name`
defaults to the provider identifier with a `Component` suffix, spanned on that identifier. Its
`Parse` impl parses the raw form and runs the conversion, so an entry function can parse straight
into the resolved type. [`#[cgp_type]`](cgp_type.md) and [`#[cgp_getter]`](cgp_getter.md) instead
parse the raw form, fill in their own default provider name, and then convert.

## `ItemCgpComponent`

`ItemCgpComponent` is the input stage: the resolved args and the trait as written. Its `preprocess`
step first rejects a component-name parameter the trait does not declare
(`check_component_name_params`), then runs the [attribute collector](attributes/README.md)
`CgpComponentAttributes::preprocess`, which strips the CGP modifier attributes off the trait and
returns them as a structured record, so every later stage sees a plain `syn::ItemTrait` beside that
record.

## `PreprocessedCgpComponent`

`PreprocessedCgpComponent` holds the args, the cleaned trait, and the attributes, and owns the core
derivation. Its `eval` step builds the component marker struct (from the component name and its
generics), the provider trait together with the provider blanket impl, and the consumer blanket
impl. The provider trait and its blanket impl come from one call,
`to_provider_trait_and_blanket_impl`, so the two cannot disagree. The shapes they produce are
described in the [entrypoint document](../entrypoints/cgp_component.md).

## `EvaluatedCgpComponent`

`EvaluatedCgpComponent` is the final stage: the derived items plus the consumer trait, args, and
attributes needed to render the provider impls. Its `to_items` step emits the five core items in a
fixed order (consumer trait, consumer blanket impl, provider trait, provider blanket impl, marker
struct) and then the provider impls:

- the `UseContext` and `RedirectLookup` impls, always;
- one `UseDelegate` impl per [`#[derive_delegate]`](attributes/derive_delegate.md) attribute;
- one namespace impl per [`#[prefix]`](attributes/prefix.md) attribute.

The first three kinds each come paired with an `IsProviderFor` impl through `ItemProviderImpls`; the
`#[prefix]` impl implements a namespace trait and has no pair.

## Tests

- [cgp-macro-tests/tests/parser_rejections/cgp_component.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/cgp_component.rs)
  pins the rejection of a non-trait item, a const generic parameter, a repeated key, an unknown key,
  and a keyed form with no `provider`.
- The stage transforms are exercised end to end by the expansion snapshots indexed in the
  [entrypoint document's Snapshots section](../entrypoints/cgp_component.md#snapshots).

## Source

- The stack lives in
  [cgp-macro-core/src/types/cgp_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_component/):
  - the argument types in `args/` (`raw.rs` and `component_args.rs`);
  - `ItemCgpComponent` in `item.rs`;
  - `PreprocessedCgpComponent` in `preprocessed/`, one file per derived item;
  - `EvaluatedCgpComponent` in `evaluated/`, with the `UseContext` and `RedirectLookup` builders.
- The `self`/`Self` rewriting is done by the visitors in
  [cgp-macro-core/src/visitors/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/visitors/).
