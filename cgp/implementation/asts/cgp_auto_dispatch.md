# The `cgp_auto_dispatch` AST stack

The `cgp_auto_dispatch` stack is the AST types `#[cgp_auto_dispatch]` moves through:
`ItemCgpAutoDispatch`, `PreprocessedCgpAutoDispatch` with one `DispatchMethod` per method, and the
`EvaluatedCgpAutoDispatch` intermediate representation (IR). Data flows in one direction: a
`syn::ItemTrait` becomes `ItemCgpAutoDispatch`, which `preprocess`es into
`PreprocessedCgpAutoDispatch`, whose `eval` builds the IR; the entrypoint then runs each per-method
`ItemCgpComputer` in that IR through [the `cgp_computer` stack](cgp_computer.md). The
[entrypoint document](../entrypoints/cgp_auto_dispatch.md) covers what the macro emits; this
document covers the types and the lifetime visitor they rely on.

## `ItemCgpAutoDispatch`

`ItemCgpAutoDispatch` is the raw input stage: the annotated trait. Its `preprocess` walks the trait's
items in order, rejecting a non-method item through `Error::new_spanned`, and constructs a
`DispatchMethod` for each method, which is where every per-method check and the lifetime naming
happen.

## `DispatchMethod` and `DispatchReceiver`

`DispatchMethod` is one method, checked to have a shape the macro can dispatch and with its
signature's elided lifetimes named. Its constructor rejects a type or const generic parameter, a
missing `self` receiver, and a typed receiver such as `self: Box<Self>`, then records:

- the receiver as a `DispatchReceiver`: `Owned`, or `Ref`/`Mut` carrying the receiver's lifetime,
  which is the one the method names or the reserved `'__a__` when elided;
- the argument types after the receiver, with each elided lifetime named by a fresh
  `'__a1__`, `'__a2__`, …;
- the return type, with each elided lifetime named by the receiver's lifetime, or for a by-value
  `self` by the single lifetime the arguments use, found with `collect_lifetimes`;
- the lifetimes it introduced, which neither the trait nor the method declares;
- the per-variant computer's name, `Compute` plus the unrawed method name in PascalCase, from
  `derive_computer_ident`.

The two derivations then read that one elaborated signature. `to_blanket_impl_item` produces the
blanket impl's method, with its arguments rebound as `arg_i`, and the `where` predicate bounding the
selected matcher; the bound is quantified in one `for<…>` over the method's own lifetime parameters
followed by the introduced ones. `to_computer` produces the method's `ItemCgpComputer`: a helper
function `__compute_{method}__` whose generics are the trait's and the method's, merged with
`cgp-macro-core`'s `merge_generics`, with the introduced lifetimes and
`__Variants__: Trait<…>` inserted ahead of them.

```rust
// fn label(&self, suffix: &str) -> &str;  becomes, as the helper the IR hands to #[cgp_computer]:
fn __compute_label__<'__a__, '__a1__, __Variants__: CanLabel>(
    __Variants__: &'__a__ __Variants__,
    (arg_0): (&'__a1__ str),
) -> &'__a__ str {
    __Variants__.label(arg_0)
}
```

## `ElaborateElidedLifetimes`

`ElaborateElidedLifetimes` is the `VisitMut` pass that names elided lifetimes: a reference written
without one and the placeholder `'_`, at any depth of a type. In `fresh` mode it gives each one a new
`'__a{n}__` and records it, which is how the argument types follow the compiler's rule that elided
inputs are distinct; in `fixed` mode it gives each one a given lifetime, which is how the return type
takes the receiver's. It does not descend into a function-pointer type or the `Fn(..)` sugar, which
bind their own elided lifetimes. Its read-only companion `collect_lifetimes` lists the distinct
lifetimes a set of types names, skipping the same two positions.

## `PreprocessedCgpAutoDispatch`

`PreprocessedCgpAutoDispatch` holds the trait and its `DispatchMethod`s. Its `to_blanket_impl`
inserts `__Variants__` as the leading impl generic, collects one method and one matcher predicate
from each `DispatchMethod`, adds `__Variants__: HasExtractor` and, when the trait has any,
`__Variants__: Supertraits`, and re-spans the impl's boundary tokens onto the trait identifier with
`override_item_span`. Its `eval` packages that impl, the trait, and each method's `ItemCgpComputer`
into the IR.

## `EvaluatedCgpAutoDispatch`

`EvaluatedCgpAutoDispatch` is the IR: the trait, emitted unchanged; the blanket impl; and the
`ItemCgpComputer`s, in method order. Each computer entry is what the macro would otherwise emit as a
`#[cgp_computer(Compute{Method})]` helper, and the entrypoint runs it through the computer stack's
`preprocess` and `eval` and lowers the resulting `EvaluatedHandlerFn`.

## Tests

- The stages are exercised end to end by the snapshots and behavioral tests indexed in the
  [entrypoint document](../entrypoints/cgp_auto_dispatch.md), including the lifetime-naming tests
  `named_lifetimes.rs` and `elided_lifetimes.rs`.
- The rejections `preprocess` and `DispatchMethod` enforce are pinned, with their messages, by
  [parser_rejections/cgp_auto_dispatch.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/cgp_auto_dispatch.rs).

## Source

- The stack lives in
  [cgp-macro-extra-core/src/types/cgp_auto_dispatch/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/types/cgp_auto_dispatch/):
  `ItemCgpAutoDispatch` in `item.rs`, `DispatchMethod` and `DispatchReceiver` in `method.rs`,
  `PreprocessedCgpAutoDispatch` in `preprocessed.rs`, and `EvaluatedCgpAutoDispatch` in
  `evaluated.rs`.
- `ElaborateElidedLifetimes` and `collect_lifetimes` are in
  [cgp-macro-extra-core/src/visitors/elaborate_lifetimes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-core/src/visitors/elaborate_lifetimes.rs),
  and `derive_computer_ident` in
  [cgp-macro-extra-core/src/functions/provider_ident.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-core/src/functions/provider_ident.rs).
- The per-method computers continue through [the `cgp_computer` stack](cgp_computer.md).
