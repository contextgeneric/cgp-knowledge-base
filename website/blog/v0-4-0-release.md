# CGP v0.4.0 Release: Unlocking Easier Debugging, Extensible Presets, and More

The release that made CGP debuggable: `IsProviderFor`, `CanUseComponent`, and `check_components!`,
which still underpin every readable CGP error, beside the preset system and the first datatype-generic
support, both since replaced.

- **URL**: <https://contextgeneric.dev/blog/v0-4-0-release>
- **Source**: [blog/2025-05-09-v0.4.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-05-09-v0.4.0-release.md)
- **Published**: 9 May 2025, tagged `release`
- **Release**: [v0.4.0](../../releases/v0-4-0.md)
- **Status**: Historical

## What it covers

**Debugging is the headline**, and the post says it had been the barrier to adoption: an unsatisfied
dependency produced an error with its cause hidden, which the
[launch post](early-preview-announcement.md) had proposed to fix by patching `rustc`. The release
fixed it in the library. `IsProviderFor<Component, Context, Params>` is an empty marker trait carried
as a supertrait on every provider trait and implemented under the same `where` bounds as the provider,
so the compiler names the missing dependency. `CanUseComponent` is its context-side companion,
`check_components!` turns both into a compile-time assertion, and `delegate_and_check_components!`
fuses wiring and checking. This made `#[cgp_provider]` and `#[cgp_new_provider]` mandatory.

The other changes:

- `cgp_type!` becomes the attribute `#[cgp_type]`, with new default naming.
- `#[cgp_context]` generates a context's provider struct and its `HasCgpProvider` impl.
- The getter macros gain `&str`, `Option<&T>`, and slice handling, generic parameters, and getter
  combinators for nested fields.
- `#[cgp_component]` gains the positional form and associated `const` items.
- `#[derive(HasFields)]` starts datatype-generic programming, and the Greek letters (`π`, `ω`, `ι`,
  `ε`) shorten type-level lists in error messages.
- `#[blanket_trait]` adds trait aliases, and the `Async` trait drops its `'static` bound.

**The longest section introduces presets**: `cgp_preset!` with `#[cgp::re_export_imports]`, multiple
inheritance between presets by macro-level key copying, an `override` keyword for conflicts, and
single inheritance into a context through `#[cgp_context(Components: Preset)]`. The post frames presets
as merging type-level lookup tables, likened to prototypal rather than class-based inheritance, and
notes that CGP has no subtyping, so inheritance exists on the provider side only.

## How it relates to the knowledge base

- **Debugging:** [`IsProviderFor`](../../cgp/reference/traits/is_provider_for.md),
  [`CanUseComponent`](../../cgp/reference/traits/can_use_component.md),
  [`check_components!`](../../cgp/reference/macros/check_components.md), and
  [`delegate_and_check_components!`](../../cgp/reference/macros/delegate_and_check_components.md),
  with lazy wiring explained in [check traits](../../cgp/concepts/check-traits.md); the error story
  continues in [`cargo-cgp`](../../cargo-cgp/README.md) and [cgp/errors/](../../cgp/errors/README.md).
- **Presets:** the origin of [namespaces](../../cgp/concepts/namespaces.md); the mergeable lookup-table
  model still holds, and only the mechanism changed.
- **Getters:** the nested-getter example is
  [`ChainGetters`](../../cgp/reference/providers/chain_getters.md) with
  [`WithProvider`](../../cgp/reference/providers/with_provider.md).
- **Data:** [`#[derive(HasFields)]`](../../cgp/reference/derives/derive_has_fields.md) under
  [extensible records](../../cgp/concepts/extensible-records.md); the Greek letters are decoded in
  [type-level primitives](../../cgp/reference/types/cons.md).
- **Aliases:** [`#[blanket_trait]`](../../cgp/reference/macros/blanket_trait.md).

## Where it diverges from CGP v0.8.0

- **The whole preset system is gone.** `cgp_preset!`, `#[cgp::re_export_imports]`, `override`, and
  `#[wrap_provider]` no longer exist. Their replacement is
  [namespaces](../../cgp/concepts/namespaces.md) via
  [`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md), the `#[prefix(...)]` registration
  attribute, and the `namespace` statement in
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md). The
  [v0.8.0 draft](v0-8-0-release.md) explains why: presets supported only single inheritance into a
  context, and the macro-based multiple inheritance was fragile because macros cannot see types.
- **`#[cgp_context]` and `HasCgpProvider` are gone.** `HasCgpProvider` was removed in v0.6.0, and
  `#[cgp_context]` deprecated in v0.6.0 and removed in v0.7.0. A context implements
  [`DelegateComponent`](../../cgp/reference/traits/delegate_component.md) directly, so the
  `{Context}Components` struct this release introduced is no longer generated or needed.
- **`#[cgp_provider]` is no longer what you write.** It still exists and still derives
  `IsProviderFor`, but [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) supersedes it, per
  [writing-providers](../../cgp/guides/writing-providers.md). Every provider snippet here is
  inside-out.
- **`check_components!` syntax changed.** The post's `check_components! { CanUsePerson for Person { ... } }`
  form was replaced in v0.7.0 by an optional `#[check_trait(...)]` attribute over a bare context name.
- **The Greek letters were revised.** `ι` was replaced by `ζ` in v0.5.0 to avoid `rustc`'s
  `confusable_idents` warning, and `Char` was renamed [`Chars`](../../cgp/reference/types/chars.md).
- **`Async` was removed entirely** in v0.5.0, not merely relaxed; see
  [send-bounds](../../cgp/concepts/send-bounds.md) for the pattern that replaced it.
- **One stale name to not copy:** the `#[blanket_trait]` example is annotated `#[trait_alias]`, the
  macro's name during development before v0.4.0 shipped it as `#[blanket_trait]`; no release carries
  it.

## Maintaining it

Leave it alone. Its `IsProviderFor` explanation is still accurate and arguably the clearest prose on
why the trait exists, but its code predates `#[cgp_impl]`, namespaces, and `#[cgp_fn]`. To explain why
CGP errors are readable, draw from [check traits](../../cgp/concepts/check-traits.md) and write fresh
code.
