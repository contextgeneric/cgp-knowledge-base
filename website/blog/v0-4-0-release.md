# CGP v0.4.0 Release: Unlocking Easier Debugging, Extensible Presets, and More

The release that made CGP debuggable. It introduces `IsProviderFor`, `CanUseComponent`, and
`check_components!` — the machinery that still underpins every readable CGP error today — alongside
the preset system and the first datatype-generic support, both of which have since been replaced.

- **URL** — <https://contextgeneric.dev/blog/v0-4-0-release>
- **Source** — [blog/2025-05-09-v0.4.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-05-09-v0.4.0-release.md)
- **Published** — 9 May 2025, tagged `release`
- **Release** — [v0.4.0](../../releases/v0-4-0.md)
- **Status** — Historical

## What it covers

The headline is debugging, and the post is candid that this had been the barrier to adoption: before
v0.4.0, an unsatisfied dependency produced an error with the cause hidden, which the
[launch post](early-preview-announcement.md) had proposed to fix by patching `rustc`. This release
found a way to do it in the library instead.

The technique is `IsProviderFor<Component, Context, Params>`, an empty marker trait carried as a
supertrait on every provider trait and implemented for each provider under the *same* `where` bounds
it used to implement the provider trait. Because the bounds ride along on a trait the compiler will
report, the missing dependency is named rather than swallowed. `CanUseComponent` is the context-side
companion, and `check_components!` turns both into a compile-time assertion that a context's wiring
actually holds. `delegate_and_check_components!` fuses wiring and checking for simple cases. Making
this work required providers to be annotated, which is why `#[cgp_provider]` and `#[cgp_new_provider]`
became mandatory in this release.

The post then covers four more areas. `cgp_type!` becomes the attribute `#[cgp_type]`, with new
default naming. `#[cgp_context]` is introduced to generate a context's provider struct and its
`HasCgpProvider` impl. The getter macros gain `&str`, `Option<&T>`, and slice handling, generic
parameters, and getter combinators for reaching nested fields. `#[cgp_component]` gains the short
positional form and support for associated `const` items. `#[derive(HasFields)]` arrives as the first
step toward datatype-generic programming, and the Greek-letter abbreviations (`π`, `ω`, `ι`, `ε`) are
introduced to shorten type-level lists in error messages. `#[blanket_trait]` is added for trait
aliases. The `Async` trait drops its `'static` bound.

The longest section introduces **presets**: `cgp_preset!` with `#[cgp::re_export_imports]`, supporting
multiple inheritance between presets through macro-level key copying, an `override` keyword for
conflicts, and single inheritance into a context through `#[cgp_context(Components: Preset)]`. The
post frames presets as merging type-level lookup tables and compares them to prototypal rather than
class-based inheritance, noting that CGP has no subtyping so inheritance exists on the provider side
only.

## How it relates to the knowledge base

The debugging machinery is the durable part and is fully documented:
[`IsProviderFor`](../../cgp/reference/traits/is_provider_for.md),
[`CanUseComponent`](../../cgp/reference/traits/can_use_component.md),
[`check_components!`](../../cgp/reference/macros/check_components.md), and
[`delegate_and_check_components!`](../../cgp/reference/macros/delegate_and_check_components.md), with
the reasoning behind lazy wiring in [check traits](../../cgp/concepts/check-traits.md). The whole
error story this release opened is now carried further by
[`cargo-cgp`](../../cargo-cgp/README.md) and catalogued class by class in
[cgp/errors/](../../cgp/errors/README.md).

The preset section is the origin of what is now [namespaces](../../cgp/concepts/namespaces.md), and
its framing of component delegation as a mergeable type-level lookup table is still the right mental
model — only the mechanism changed. The nested-getter example is
[`ChainGetters`](../../cgp/reference/providers/chain_getters.md) with
[`WithProvider`](../../cgp/reference/providers/with_provider.md). `#[derive(HasFields)]` is now
[`#[derive(HasFields)]`](../../cgp/reference/derives/derive_has_fields.md) under
[extensible records](../../cgp/concepts/extensible-records.md), and the Greek letters are decoded in
[type-level primitives](../../cgp/reference/types/cons.md). `#[blanket_trait]` is
[`#[blanket_trait]`](../../cgp/reference/macros/blanket_trait.md).

## Where it diverges from CGP v0.8.0

- **The whole preset system is gone.** `cgp_preset!`, `#[cgp::re_export_imports]`, `override`, and
  `#[wrap_provider]` no longer exist. Their replacement is
  [namespaces](../../cgp/concepts/namespaces.md) via
  [`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md), the `#[prefix(...)]` registration
  attribute, and the `namespace` statement in
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md). The
  [v0.8.0 draft](v0-8-0-release.md) explains why: presets supported only single inheritance into a
  context, and the macro-based multiple inheritance was fragile because macros cannot see types.
- **`#[cgp_context]` and `HasCgpProvider` are gone.** Deprecated in v0.6.0, removed in v0.7.0. A
  context now implements [`DelegateComponent`](../../cgp/reference/traits/delegate_component.md)
  directly, so the `{Context}Components` struct this release introduced is no longer generated or
  needed.
- **`#[cgp_provider]` is no longer what you write.** It still exists and still derives
  `IsProviderFor`, but [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) supersedes it as the
  form to write, per [writing-providers](../../cgp/guides/writing-providers.md). Every provider
  snippet in this post is in the inside-out shape.
- **`check_components!` syntax changed.** The post's `check_components! { CanUsePerson for Person { ... } }`
  form was replaced in v0.7.0 by an optional `#[check_trait(...)]` attribute over a bare context name.
- **The Greek letters were revised.** `ι` was replaced by `ζ` in v0.5.0 to avoid `rustc`'s
  `confusable_idents` warning, and `Char` was renamed [`Chars`](../../cgp/reference/types/chars.md).
- **`Async` was removed entirely** in v0.5.0, not merely relaxed; see
  [send-bounds](../../cgp/concepts/send-bounds.md) for the pattern that replaced it.
- **One typo to not copy:** the `#[blanket_trait]` example is annotated `#[trait_alias]`, a name that
  never existed.

## Maintaining it

Leave it alone. Of all the release notes this is the one whose *ideas* have aged best — the
`IsProviderFor` explanation is still accurate and is arguably clearer than any other prose on why the
trait exists — but its code is uniformly pre-`#[cgp_impl]`, pre-namespace, and pre-`#[cgp_fn]`, so
nothing in it should be quoted as current. When a piece needs to explain why CGP errors are readable,
draw the explanation from [check traits](../../cgp/concepts/check-traits.md) and write fresh code.
