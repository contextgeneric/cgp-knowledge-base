# `#[impl_generics]` — the AST stack

`#[impl_generics(Name: Display)]` on a `#[cgp_fn]` adds generic parameters to the generated blanket impl alone, so a type a context fixes through a field is inferred rather than exposed on the trait. It is a modifier attribute collected by the function host; this page covers how it is parsed and what the host injects, and the shared collection mechanism lives in the [attribute-modifier overview](README.md). For the user-facing syntax and expansion, read the reference document [reference/attributes/impl_generics.md](../../../reference/attributes/impl_generics.md).

## The `impl_generics` field of `FunctionAttributes`

The attribute does not have an AST type of its own. `FunctionAttributes::parse` matches the `impl_generics` identifier and parses the argument with `Punctuated::<GenericParam, Comma>::parse_terminated` into the `impl_generics: Vec<GenericParam>` field, extending it on each occurrence, so the attribute repeats and its lists concatenate. Because the entries are [`syn::GenericParam`](https://docs.rs/syn/latest/syn/enum.GenericParam.html), a lifetime, a const parameter, a bounded type parameter, and a parameter default all parse; the default is rejected later by the compiler, as the host's [Failure modes](../../entrypoints/cgp_fn.md#failure-modes) record.

## What the host injects

`PreprocessedItemCgpFn::to_item_impl` builds the blanket impl from the function's own generics, inserts `__Context__` at position 0, then extends the parameter list with `attributes.impl_generics`. The emitted order is therefore `__Context__`, the function's own generics, the attribute's parameters, and `syn::Generics::to_tokens` prints lifetimes first, so a lifetime declared in the attribute lands ahead of `__Context__` in the output. `to_item_trait` never consults the field, which is the whole point: the trait is emitted without the parameters.

Nothing constrains the parameters except the `HasField<…, Value = T>` bounds the implicit arguments append to the impl's `where` clause, so a parameter absent from every implicit argument's type is rejected by the compiler as unconstrained. That and the two other compiler-deferred failures, a parameter named after the function and a parameter default, are on the [host's page](../../entrypoints/cgp_fn.md#failure-modes).

## Tests

- [generic_components/fn_impl_generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/generic_components/fn_impl_generics.rs) pins the expansion: the parameter on the impl with its inline bound, absent from the trait, and pinned by the implicit argument's field bound; a second `#[cgp_fn]` then consumes the capability through `#[uses]` and drives a runtime assertion.
- No library fixture pins the unconstrained-parameter (`E0207`), name-clash (`E0404`), or default-parameter rejections; each is a plain compiler error on the emitted impl.

## Source

- Parsing: the `impl_generics` arm of `FunctionAttributes::parse` in [cgp-macro-core/src/types/attributes/function.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/function.rs).
- Injection: `to_item_impl` in [cgp-macro-core/src/types/cgp_fn/preprocessed.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_fn/preprocessed.rs).
- The host that drives it: [entrypoints/cgp_fn.md](../../entrypoints/cgp_fn.md).
