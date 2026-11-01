# Verbose dependency cascade

One mistake deep in a dependency graph surfaces at every provider that transitively needs it, so the
compiler prints far more error blocks than there are mistakes, and the reader's task is to find the
one root cause among the repeats.

## What triggers it

This class is the *volume* form of a [surfaced check-trait failure](check-trait-failure.md): it
arises whenever several components share a transitive dependency and that dependency is unmet. A
chain of providers (`ProvideBaz` depends on `CanBar`, `ProvideBar` on `CanFoo`, `ProvideFoo` on a
`name` field) is wired onto a context missing that field, and all three components are checked
together.

```rust
#[cgp_impl(new ProvideFoo)]
impl Foo where Self: HasName { /* needs the `name` field */ }

#[cgp_impl(new ProvideBar)]
#[uses(CanFoo)]              // depends on Foo
impl Bar { /* … */ }

#[cgp_impl(new ProvideBaz)]
#[uses(CanBar)]             // depends on Bar
impl Baz { /* … */ }

#[derive(HasField)]
pub struct App { pub age: u8 } // no `name` field

delegate_components! {
    App { FooComponent: ProvideFoo, BarComponent: ProvideBar, BazComponent: ProvideBaz }
}

check_components! {
    App { BazComponent, BarComponent, FooComponent }
}
```

## The raw diagnostic

This section describes plain `cargo check`, the fallback when `cargo-cgp` is not on hand. The block count reflects the
depth of the graph, not the number of mistakes: three chained components over one missing field produce **six** `E0277`
blocks of two kinds. Each checked component gives a `CanUseComponent<…Component>` block whose `help:` names the missing
`HasField<Symbol<4, Chars<'n', …>>>` for `App`. The deeper components add **intermediate** blocks
(`ProvideBar: Bar<App>`, `ProvideFoo: Foo<App>`) that name only an inner provider trait. The nightly `cargo-cgp` pins
prints three blocks for the same program, one intermediate `ProvideFoo: IsProviderFor<FooComponent, App>` and two
`CanUseComponent`, per
[which compiler the raw diagnostic describes](../README.md#which-compiler-the-raw-diagnostic-describes).

Two pieces of rustc machinery are easy to misread. Each intermediate block carries the
[near-contradiction](../../guides/debugging.md) pair, ``help: the trait `Bar<App>` is not implemented for `ProvideBar` ``
and ``help: the trait `Bar<__Context__>` is conditionally implemented for `ProvideBar` ``: the generic impl exists but does
not hold for `App`, because a bound deeper in its chain fails. And `= note: N redundant requirements hidden` collapses
obligations already printed, rather than omitting a distinct cause.

Direct consumer calls instead of a check give one `E0599` per call, none reaching the cause on stable: the
[hidden](../hidden/unsatisfied-dependency.md) failure, multiplied.

## Where the root cause is

The root cause is **present and repeated**, in every `CanUseComponent` block's `help:`. Find it by structure rather than
position: **look for a block whose `help:` names a concrete missing item (a `HasField`, an abstract type) rather than a
provider trait like `ProvideFoo: Foo<App>`.** When components are checked with the foundational one last, as in the
fixture, the last block is such a block, but the order does not guarantee it.

## How cargo-cgp presents it

`cargo-cgp` collapses the cascade to one block. It drops the intermediate blocks, resolves each checked component to a
`root cause:` tree, and coalesces the components that share a cause: the headline states it
(`` [CGP-E001] missing field `name` on `App` ``), the caret sits on the first check entry, each other entry is labelled
"also required here", and one tree follows. An editor shows one diagnostic with related locations, and cargo's count reads
one error. A component rustc surfaced provider-side is still classed as the consumer its check entry asserts.

The tool can merge these because it holds the compilation's diagnostics until all have arrived, then groups those that
share a root cause. It groups one cause at a time rather than on the whole set, so it reaches one omission met at several
instantiations: each check entry stops at the first unmet leaf on its branch while a call reaches them all, and no two of
those sets are equal. The [cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) defines the codes.

## Resolving it

Fix the one root cause and every block goes. The difficulty is isolation, so the
[debugging guide](../../guides/debugging.md) prescribes two moves: check one suspect component in its own
`check_components!` block, or bisect a large table by commenting entries out.

## Backing fixtures

- [`checks/verbose-cascade/dependency_cascade.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/dependency_cascade.rs):
  a three-deep provider chain over one missing `name` field, checked across all three components, in one coalesced block.
- [`checks/verbose-cascade/density_3.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/density_3.rs):
  two components over one missing `height`, the second depending on the first, coalesced.
- [`checks/verbose-cascade/density_1.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/density_1.rs):
  a missing field two components below the checked one.
- [`checks/verbose-cascade/density_2.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/density_2.rs):
  the same transitive-path burden as density_1, one layer deeper.
- [`checks/verbose-cascade/parallel_consumers.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/parallel_consumers.rs):
  two independent consumers coalesced on one cause via parallel (non-subsuming) chains.

## Related

- [Check-trait failure (surfaced)](check-trait-failure.md): the single-cause diagnostic this class
  multiplies.
- [Higher-order provider layer failure (surfaced)](higher-order-provider-layer.md): a sibling class
  that emits the same intermediate provider-trait noise blocks, there to distinguish an inner-layer
  failure from an outer one.
- [Unsatisfied dependency (hidden)](../hidden/unsatisfied-dependency.md): the same root cause seen
  through consumer-trait calls, where each block hides the cause instead of surfacing it.
- [Debugging CGP compile errors](../../guides/debugging.md): why the error count tells you nothing
  about the number of mistakes, and how to isolate the one link.
- [`check_components!`](../../reference/macros/check_components.md) and
  [`IsProviderFor`](../../reference/traits/is_provider_for.md).
