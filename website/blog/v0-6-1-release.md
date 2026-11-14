# CGP v0.6.1 Release: Improving Ergonomics and Debugging

A three-feature release, all three still current: implicit context types in `#[cgp_impl]`, the
`#[check_providers]` attribute, and associated types in getter traits.

- **URL**: <https://contextgeneric.dev/blog/v0-6-1-release>
- **Source**: [blog/2026-02-01-v0.6.1-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2026-02-01-v0.6.1-release.md)
- **Published**: 1 February 2026, tagged `release`
- **Release**: [v0.6.1](../../releases/v0-6-1.md)
- **Status**: Historical

## What it covers

- **Implicit context types**, the headline: `impl Greeter where Self: HasName` replaces
  `impl<Context> Greeter for Context where Context: HasName`. The post argues the generic parameter was
  overhead unrelated to the logic, and that without it a provider reads like a method on a class,
  which lowers the barrier for readers from object-oriented languages.
- **`#[check_providers(...)]`:** a `check_components!` block checks that each named provider is valid
  for the component and context, not that the context can use it. With `ScaledArea<RectangleArea>`
  wired, a plain check says the composition is broken; checking `RectangleArea` and
  `ScaledArea<RectangleArea>` separately places a missing `width` field in the inner provider.
- **Associated types in getter traits:** a getter declares `type Name: Display;` and infers it from
  the field, for `#[cgp_auto_getter]` and `#[cgp_getter]`, where a separate `#[cgp_type]` trait was
  needed before.
- **An AI disclaimer** at the top: co-authored by Claude Haiku from a human draft and reviewed by the
  author, the only post that says so; the [new-website post](new-website.md) discusses the practice.

## How it relates to the knowledge base

- **Implicit context:** the preferred header in
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md);
  [writing-providers](../../cgp/guides/writing-providers.md) omits `for Context` except where a
  lifetime or HRTB forces it. The post's OOP argument is the one
  [readers.md](../../communication-strategy/readers.md#the-comprehension-barriers) makes about the
  prerequisite ladder, answered in the design.
- **Layer checks:** `#[check_providers]` is in
  [`check_components!`](../../cgp/reference/macros/check_components.md); the technique is in
  [check traits](../../cgp/concepts/check-traits.md) and [debugging](../../cgp/guides/debugging.md),
  and the error class is
  [higher-order-provider-layer](../../cgp/errors/checks/higher-order-provider-layer.md). The composed
  provider is a [higher-order provider](../../cgp/concepts/higher-order-providers.md).
- **Getter types:** [`#[cgp_auto_getter]`](../../cgp/reference/macros/cgp_auto_getter.md) and
  [`#[cgp_getter]`](../../cgp/reference/macros/cgp_getter.md).

## Where it diverges from CGP v0.8.0

Little, which makes it the most quotable release note on the site, though still to be checked:

- **The `#[cgp_impl]` "before" snippets are the stale ones.** Half the code is deliberately old;
  quote only the "after" side.
- **`InnerCalculator: AreaCalculator<Self>` in the `where` clause** is now written
  [`#[use_provider(InnerCalculator: AreaCalculator)]`](../../cgp/reference/attributes/use_provider.md),
  which fills in the `Self` argument, per
  [declaring-dependencies](../../cgp/guides/declaring-dependencies.md).
- **`Self: HasRectangleFields` in the `where` clause** is now
  [`#[uses(HasRectangleFields)]`](../../cgp/reference/attributes/uses.md), and the getter trait would
  usually give way to [`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments reading
  `width` and `height`, both arriving in v0.7.0.
- **`check_components! { CanUseRectangle for Rectangle { ... } }`** is the pre-v0.7.0 syntax; the
  current form names the context alone with an optional `#[check_trait(...)]` attribute.
- **The abstract-type example writes `Self::Name`**, where
  [`#[use_type]`](../../cgp/reference/attributes/use_type.md) now imports the bare alias, per
  [importing-abstract-types](../../cgp/guides/importing-abstract-types.md).

## Maintaining it

Leave it alone. Its `#[check_providers]` explanation is the clearest published statement of an
easily missed debugging technique; point at it when writing about diagnosing composed providers,
beside [`cargo-cgp`](../../cargo-cgp/README.md), which postdates it and is the first tool to reach for.
