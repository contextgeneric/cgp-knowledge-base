# Higher-order provider layer failure (surfaced)

A checked higher-order provider whose dependency is unmet surfaces the real leaf bound (`E0277`)
like any [check-trait failure](check-trait-failure.md), but the diagnostic's shape also tells you
*which layer* of the provider stack failed, and reading that shape is the difference between fixing
the wrapper and fixing what it wraps.

## What triggers it

This class arises when a [higher-order provider](../../concepts/higher-order-providers.md) (a
provider parameterized by another provider) is wired onto a context that cannot meet a dependency in
one of its layers, and the wiring is checked. The outer provider carries its own impl-side
dependency, and the inner provider it wraps carries a different one; the context may satisfy either,
both, or neither. When exactly one layer's dependency is unmet, the check still fails, and the
question a reader must answer is which layer to fix.

```rust
#[cgp_impl(new BaseArea)]
impl AreaCalculator
where
    Self: HasBaseArea, // the INNER layer's dependency
{ /* … */ }

#[cgp_impl(new ScaledArea<Inner>)]
#[use_provider(Inner: AreaCalculator)]
impl<Inner> AreaCalculator
where
    Self: HasScaleFactor, // the OUTER layer's dependency
{ /* … */ }

#[derive(HasField)]
pub struct Rectangle {
    pub scale_factor: f64, // present: the outer layer is satisfied
    // no `base_area`:      the inner layer is not
}

delegate_components! {
    Rectangle { AreaCalculatorComponent: ScaledArea<BaseArea> }
}

check_components! {
    Rectangle { AreaCalculatorComponent }
}
```

## The raw diagnostic

This section describes plain `cargo check`, the fallback when `cargo-cgp` is not on hand. This is a
**surfaced** class: a `help:` note names the unmet leaf as in a
[check-trait failure](check-trait-failure.md). The rest of the diagnostic differs by layer, so the
shape tells the two cases apart.

When the **inner** layer fails, stable prints two `E0277` blocks. The first reports
`BaseArea: AreaCalculator<Rectangle>` is not satisfied, with the
[near-contradiction](../../guides/debugging.md) hint that `AreaCalculator<__Context__>` is
"conditionally implemented" for `BaseArea`: the generic impl exists but is inapplicable here. The
second is `Rectangle: CanUseComponent<AreaCalculatorComponent>`, whose `help:` names the missing
`HasField<Symbol<9, Chars<'b', …>>>`. Its `unsatisfied trait bound introduced here` caret lands on the
inner provider's `Self: HasBaseArea`, and its chain runs through `BaseArea`'s `IsProviderFor` and,
after a `1 redundant requirement hidden` note, through `ScaledArea<BaseArea>`'s. The nightly
`cargo-cgp` pins prints only the second block, so there the chain alone marks the inner layer.

When the **outer** layer fails, the compiler prints one shorter `E0277` block, the same
`CanUseComponent` headline. Its `help:` names the missing `HasField<Symbol<12, Chars<'s', …>>>`, its caret
lands on the outer provider's `Self: HasScaleFactor`, and its chain runs from
`ScaledArea<BaseArea>`'s `IsProviderFor` straight to `CanUseComponent`, without a redundancy note or the
inner `BaseArea`, since the outer layer fails before it delegates inward.

## Where the root cause is

The root cause is **present** in the `help:` note of the `CanUseComponent` block in both cases. The
failing layer shows first in the `unsatisfied trait bound introduced here` caret, on the `where` clause
of the provider whose dependency is unmet, and then in the chain: both providers' `IsProviderFor` with a
redundancy note for an inner failure, the outer provider's alone for an outer one. The intermediate block
of the inner case points inward too, but a reader skips it to reach the block with the leaf.

## How cargo-cgp presents it

`cargo-cgp` reshapes both cases into one `[CGP-E001]` headline over one `root cause:` tree, and the tree's
shape shows the layer. An inner failure ends at `` [CGP-E110] missing field `base_area` on `Rectangle` ``
beneath two `[CGP-E102]` hops, `ScaledArea<BaseArea>` then `BaseArea`, and a `[CGP-E104]` hop for
`HasBaseArea`. An outer failure ends at `` [CGP-E110] missing field `scale_factor` on `Rectangle` `` beneath
one `[CGP-E102]` hop, with the inner provider never named. The tree does not state the layer in words, so
a reader infers inner or outer from the depth.

Checked with `#[check_providers(...)]`, each failing layer is its own `[CGP-E002]` block, whose tree starts
at that layer
([`check_providers_layer`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/higher-order-provider-layer/check_providers_layer.rs)).
The [cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) defines the codes.

## Resolving it

Supply what the named leaf needs at that layer: `base_area` for the inner failure, `scale_factor` for the
outer. The stack `ScaledArea<BaseArea>` is correct in both cases, so the delegation does not change.

To locate the layer in a deep stack, use the `#[check_providers(...)]` form of
[`check_components!`](../../reference/macros/check_components.md). It asserts `IsProviderFor` on each named
provider, so a dependency missing only from the outer wrapper errors on that line alone, and one missing from
the inner provider errors on both. The [debugging guide](../../guides/debugging.md) prescribes this move.

## Backing fixtures

- [`checks/higher-order-provider-layer/higher_order_inner_dependency.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/higher-order-provider-layer/higher_order_inner_dependency.rs):
  `ScaledArea<BaseArea>` on a `Rectangle` with `scale_factor` but no `base_area`: the inner layer fails, with two `[CGP-E102]` hops.
- [`checks/higher-order-provider-layer/higher_order_outer_dependency.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/higher-order-provider-layer/higher_order_outer_dependency.rs):
  the mirror, with `base_area` but no `scale_factor`: one `[CGP-E102]` hop, and the inner provider absent.
- [`checks/higher-order-provider-layer/deep_nesting.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/higher-order-provider-layer/deep_nesting.rs):
  a deeply nested stack whose tree descends through every layer to the missing field.
- [`checks/higher-order-provider-layer/scaled_area_1.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/higher-order-provider-layer/scaled_area_1.rs):
  an inner-layer failure, whose tree shows the layer without naming it.
- [`checks/higher-order-provider-layer/scaled_area_2.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/higher-order-provider-layer/scaled_area_2.rs):
  the outer layer of a higher-order provider fails.

## Related

- [Check-trait failure (surfaced)](check-trait-failure.md): the single-layer form of the same
  surfaced diagnostic; this class is what it looks like when the failing provider wraps another.
- [Verbose dependency cascade](verbose-cascade.md): the sibling class whose intermediate
  provider-trait blocks are the same noise this class also emits for an inner failure.
- [`check_components!`](../../reference/macros/check_components.md) and its
  `#[check_providers(...)]` form: the macro this class is expressed through and the tool that
  localizes the layer by hand.
- [`IsProviderFor`](../../reference/traits/is_provider_for.md) and
  [`#[use_provider]`](../../reference/attributes/use_provider.md): the supertrait that carries each
  layer's `where` clause into the chain, and the attribute that completes the inner provider's
  bound.
- [Higher-order providers](../../concepts/higher-order-providers.md) and
  [Debugging CGP compile errors](../../guides/debugging.md): the concept this class fails in, and
  the playbook that prescribes `#[check_providers]`.
