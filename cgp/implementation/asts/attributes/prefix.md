# `#[prefix]` — the AST stack

`#[prefix(@app in DefaultNamespace)]` on a `#[cgp_component]` trait registers the component into a namespace under a path prefix. It is a modifier attribute collected by the component host; this page covers its AST type and the namespace impl it builds, and the shared collection mechanism lives in the [attribute-modifier overview](README.md). For the user-facing syntax and expansion, read the reference document [reference/attributes/prefix.md](../../../reference/attributes/prefix.md).

## `PrefixAttribute`

The attribute parses into a `PrefixAttribute`: a `path` (a `UniPath`, the `@`-sigil dotted path whose segments are `PathElement`s, without per-segment generics or grouping forms), the `in` keyword, and a `namespace` (a `PathWithTypeArgs`, so the namespace may be a qualified path and may carry generic arguments). Parsing reads the three in order. `CgpComponentAttributes::parse` collects one `PrefixAttribute` per `#[prefix]` attribute into its `prefixes` vector during the host's `preprocess` stage, which is why the attribute repeats.

## `to_namespace_impl` — the registration impl

`PrefixAttribute::to_namespace_impl(component_name)` emits one impl of the namespace trait for the component marker, whose `Delegate` is a `RedirectLookup` down the prefix path with the marker appended:

```rust
// #[prefix(@app in DefaultNamespace)] on a component whose marker is GreeterComponent:
impl<__Components__> DefaultNamespace<__Components__> for GreeterComponent {
    type Delegate = RedirectLookup<
        __Components__,
        PathCons<Symbol!("app"), PathCons<GreeterComponent, Nil>>,
    >;
}
```

Three steps produce it. The namespace path gains a trailing `__Components__` type argument. The prefix path gains the component marker as its last element through `UniPath::append_type`, which is why the attribute takes a prefix rather than a full path. And the marker's own type generics, if the `name:` key gave it any, are copied onto the impl with `__Components__` inserted at position 0; the `parse_internal!` re-parse normalizes lifetime ordering, per the note in [implementation/README.md](../../README.md). `EvaluatedCgpComponent::to_prefix_impls` maps every collected attribute through this method, and `to_item_impls` appends the results after the standard `UseContext`, `RedirectLookup`, and `UseDelegate` provider impls.

The impl is built from quasi-quoted tokens and is not re-spanned, unlike the `#[default_impl]` registration and the `delegate_components!` entries; see Known issues.

## Known issues

The namespace impl carries the macro `call_site` span. Two `#[prefix]` attributes naming the same namespace each emit an impl of that namespace's trait for the same marker, and the resulting `E0119` puts both carets on the `#[cgp_component]` attribute, so the diagnostic does not say which of the two registrations is the duplicate. Re-spanning the emitted impl onto the attribute's path token with `override_item_span`, as `#[default_impl]` does onto its key, would move the carets to the two `#[prefix]` lines. The library suite does not yet pin this conflict or its span with a fixture.

## Tests

The namespace snapshots exercise the emitted impl across the path encodings and the repeat form:

- [namespaces/namespace_type_path.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/namespace_type_path.rs) and [namespaces/namespace_symbol_path.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/namespace_symbol_path.rs) pin a type segment and a `Symbol` segment in the prefix path.
- [namespaces/namespace_multi.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/namespace_multi.rs) pins two `#[prefix]` attributes on one component, one namespace impl each.
- [namespaces/prefix_default_namespace.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/prefix_default_namespace.rs) pins a nested prefix into `DefaultNamespace`, and shows the marker appended after a prefix that already named it.
- [namespaces/multi_param_namespace.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/multi_param_namespace.rs) wires a prefixed component with a lifetime and two type parameters by full path, checking that only the type parameters take part in the path.
- [namespaces/namespace_basic.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/namespace_basic.rs) is the canonical end-to-end case: a prefixed component, a joining context, and a `check_components!` over the result.

## Source

- `PrefixAttribute`, its parser, and `to_namespace_impl` are in [cgp-macro-core/src/types/attributes/prefix.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/prefix.rs); `UniPath` and `PathElement` are in [cgp-macro-core/src/types/path/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/path/).
- The collector is `CgpComponentAttributes` in [cgp_component_attributes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/cgp_component_attributes.rs); emission is `to_prefix_impls` in [cgp_component/evaluated/item.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_component/evaluated/item.rs).
- The host that drives it: [entrypoints/cgp_component.md](../../entrypoints/cgp_component.md).
