# CGP v0.6.1 Release: Improving Ergonomics and Debugging

A focused three-feature release: `#[cgp_impl]` gains implicit context types, `check_components!` gains
the `#[check_providers]` attribute for isolating a broken layer of a composed provider, and getter
traits gain their own associated types. All three survive in current CGP.

- **URL** — <https://contextgeneric.dev/blog/v0-6-1-release>
- **Source** — [blog/2026-02-01-v0.6.1-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2026-02-01-v0.6.1-release.md)
- **Published** — 1 February 2026, tagged `release`
- **Release** — [v0.6.1](../../releases/v0-6-1.md)
- **Status** — Historical

## What it covers

**Implicit context types** are the headline. Where a provider previously had to declare
`impl<Context> Greeter for Context where Context: HasName`, it can now write
`impl Greeter where Self: HasName` and let the macro insert the parameter. Its framing of why that
matters is worth noting: the generic parameter was cognitive overhead unrelated to the logic, and
removing it makes a provider read like a method on a class, which lowers the barrier for developers
arriving from an object-oriented background.

**`#[check_providers(...)]`** changes what a `check_components!` block asserts. Instead of checking
that a *context* can use a component, it checks that each named *provider* is a valid provider for
that component and context. The post's example is the case this exists for: with
`ScaledArea<RectangleArea>` wired to a context, a plain check reports that the composition is broken
without saying which layer, while checking `RectangleArea` and `ScaledArea<RectangleArea>` separately
localizes a missing `width` field to the inner provider alone.

**Associated types in getter traits** remove a two-trait dance. A getter whose return type should vary
per context previously needed a separate `#[cgp_type]` trait alongside it; now the getter can declare
`type Name: Display;` directly and have it inferred from the field, for both `#[cgp_auto_getter]` and
`#[cgp_getter]`.

The post carries an **AI disclaimer** at the top, stating that it was co-authored by Claude Haiku from
a human draft and reviewed by the human author — the only post that does so explicitly, though the
[new-website post](new-website.md) discusses the practice generally.

## How it relates to the knowledge base

All three features are current. The implicit context form is what
[`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) documents as the preferred header, and
[writing-providers](../../cgp/guides/writing-providers.md) prescribes omitting `for Context` except
where a lifetime or HRTB forces it. `#[check_providers]` is documented within
[`check_components!`](../../cgp/reference/macros/check_components.md), and the layer-isolation
technique it enables is the debugging playbook in [check traits](../../cgp/concepts/check-traits.md)
and [debugging](../../cgp/guides/debugging.md); the error class it diagnoses has its own entry as
[higher-order-provider-layer](../../cgp/errors/checks/higher-order-provider-layer.md). Getter
associated types are covered in
[`#[cgp_auto_getter]`](../../cgp/reference/macros/cgp_auto_getter.md) and
[`#[cgp_getter]`](../../cgp/reference/macros/cgp_getter.md). The composed provider in the running
example is a [higher-order provider](../../cgp/concepts/higher-order-providers.md).

The post's stated motivation — that generic syntax is a barrier for readers from an OOP background —
is the same argument [readers.md](../../communication-strategy/readers.md#the-comprehension-barriers) makes
about the prerequisite ladder, and the release is a good illustration of the project responding to it
in the design rather than only in the prose.

## Where it diverges from CGP v0.8.0

Little, which makes this the most quotable release note on the site — though not quotable enough to
skip checking.

- **The `#[cgp_impl]` "before" snippets are the stale ones.** The post's before-and-after contrast
  means half its code is deliberately old; quote only the "after" side.
- **`InnerCalculator: AreaCalculator<Self>` in the `where` clause** is now written
  [`#[use_provider(InnerCalculator: AreaCalculator)]`](../../cgp/reference/attributes/use_provider.md),
  which fills in the `Self` argument, per
  [declaring-dependencies](../../cgp/guides/declaring-dependencies.md).
- **`Self: HasRectangleFields` in the `where` clause** is now
  [`#[uses(HasRectangleFields)]`](../../cgp/reference/attributes/uses.md), and the getter trait itself
  would usually be replaced by [`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments
  reading `width` and `height` directly — both changes arriving in v0.7.0, one release later.
- **`check_components! { CanUseRectangle for Rectangle { ... } }`** uses the pre-v0.7.0 syntax; the
  current form names the context alone with an optional `#[check_trait(...)]` attribute.
- **The abstract-type example writes `Self::Name`**, where
  [`#[use_type]`](../../cgp/reference/attributes/use_type.md) now imports the bare alias, per
  [importing-abstract-types](../../cgp/guides/importing-abstract-types.md).

## Maintaining it

Leave it alone. Its `#[check_providers]` explanation is the clearest published statement of a
debugging technique that is easy to miss, and it is worth pointing at from any future writing about
diagnosing composed providers — alongside [`cargo-cgp`](../../cargo-cgp/README.md), which did not
exist when this was written and is now the first tool to reach for.
