# CGP release history

This directory holds one document per official CGP release: what it introduced, what it broke, and —
the question the whole section exists to answer — **how much of it still stands today**. A construct
that shipped in v0.3.0 may be current, may have been renamed twice, or may have been deleted
outright, and an agent reading old code, an old blog post, or an old book chapter needs to know which
before it can interpret what it is looking at.

## Why a release history is worth keeping

The rest of this base deliberately [documents the present](../AGENTS.md#document-the-present-not-the-history):
a reference document describes how a construct works now, with no trace of how it got there. That rule
keeps those documents readable, but it leaves a real gap, because CGP's public material is full of
history that a reader cannot date from the text alone. Almost every blog post on the
[website](../website/blog/README.md) predates the current release, the
[CGP Patterns book](https://patterns.contextgeneric.dev/) has not been updated for some time, and
codebases in the wild are pinned to whatever version they adopted. Meeting `#[cgp_context]`,
`cgp_preset!`, or `HasAsyncErrorType` in any of them raises the same question, and this is where the
answer lives.

So this section is the base's one sanctioned home for the historical view. The rule elsewhere is
unchanged: a reference document still describes only current behavior, and a construct that no longer
exists is deleted from it rather than annotated. What a release document adds is the **timeline** —
when a construct arrived, what it was called at each point, and where it went.

## The removal ledger

The fastest way to date an unfamiliar construct is this table. Each row names something that shipped
in a release and no longer exists under that name, with where it went. Every entry is verified against
the [`cgp`](https://github.com/contextgeneric/cgp) source at the relevant tag.

| Construct | Shipped in | Fate |
|---|---|---|
| `#[derive_component]` | [v0.1.0](v0-1-0.md) | Renamed `#[cgp_component]` in [v0.2.0](v0-2-0.md) |
| `define_components!` | [v0.1.0](v0-1-0.md) | Renamed `cgp_preset!` in [v0.2.0](v0-2-0.md), removed in [v0.8.0](v0-8-0.md) |
| `HasField::Field` | [v0.1.0](v0-1-0.md) | Renamed `HasField::Value` in [v0.2.0](v0-2-0.md) |
| `HasInner` / `cgp-inner` | [v0.1.0](v0-1-0.md) | Removed in [v0.5.0](v0-5-0.md), superseded by `UseField` |
| `Async`, `MaybeSend`, `MaybeSync`, `MaybeStatic` | [v0.2.0](v0-2-0.md) | `'static` dropped in [v0.4.0](v0-4-0.md); removed in [v0.5.0](v0-5-0.md) |
| `DelegateTo` | [v0.2.0](v0-2-0.md) | Renamed `UseDelegate` within [v0.2.0](v0-2-0.md) |
| `symbol!` (lowercase) | [v0.2.0](v0-2-0.md) | Renamed `Symbol!` in [v0.5.0](v0-5-0.md) |
| `cgp_type!` (function macro) | [v0.3.0](v0-3-0.md) | Became the `#[cgp_type]` attribute in [v0.4.0](v0-4-0.md) |
| `HasAsyncErrorType`, `CanRaiseAsyncError`, `CanWrapAsyncError` | [v0.3.0](v0-3-0.md)/[v0.3.1](v0-3-1.md) | Removed in [v0.5.0](v0-5-0.md) with `Async` |
| `HasComponents` | pre-[v0.4.0](v0-4-0.md) | Renamed `HasProvider` then `HasCgpProvider` in [v0.4.0](v0-4-0.md), removed in [v0.6.0](v0-6-0.md) |
| `#[trait_alias]` | [v0.4.0](v0-4-0.md) | Renamed `#[blanket_trait]` within [v0.4.0](v0-4-0.md) |
| `#[new_cgp_provider]` | [v0.4.0](v0-4-0.md) | Renamed `#[cgp_new_provider]` within [v0.4.0](v0-4-0.md) |
| `#[cgp_context]` | [v0.4.0](v0-4-0.md) | Deprecated in [v0.6.0](v0-6-0.md), removed in [v0.7.0](v0-7-0.md) |
| `cgp_preset!`, `#[cgp::re_export_imports]`, `IsPreset` | [v0.4.0](v0-4-0.md) | Removed in [v0.8.0](v0-8-0.md), superseded by [namespaces](../cgp/concepts/namespaces.md) |
| `#[wrap_provider]` | [v0.4.1](v0-4-1.md) | Removed in [v0.8.0](v0-8-0.md) with the rest of the preset system |
| `{Type}Of` type alias | [v0.4.0](v0-4-0.md) | Removed in [v0.7.0](v0-7-0.md), superseded by `#[use_type]` |
| `Char` | [v0.4.0](v0-4-0.md) | Renamed `Chars` in [v0.5.0](v0-5-0.md) |
| `ι` field abbreviation | [v0.4.0](v0-4-0.md) | Replaced by `ζ` in [v0.5.0](v0-5-0.md) |
| `#[cgp_dispatch]` | [v0.5.0](v0-5-0.md) | Renamed `#[cgp_auto_dispatch]` within [v0.5.0](v0-5-0.md) |
| `PartialFoo` generated types | [v0.4.2](v0-4-2.md) | Prefixed to `__PartialFoo` in [v0.5.0](v0-5-0.md) |
| `#[cgp_inherit]` | [v0.6.0](v0-6-0.md) | Removed in [v0.8.0](v0-8-0.md) with the presets it inherited from |
| `ProvideType` / `TypeComponent` | pre-[v0.7.0](v0-7-0.md) | Renamed `TypeProvider` / `TypeProviderComponent` in [v0.7.0](v0-7-0.md) |
| `#[use_type(Trait::Type)]` separator | [v0.7.0](v0-7-0.md) | Changed to `#[use_type(Trait.Type)]` in [v0.8.0](v0-8-0.md) |
| `#[use_namespace]`, then `#[namespace]` | never released | Both are mid-development names for [v0.8.0](v0-8-0.md)'s `#[prefix]` |

Three constructs are still present but demoted rather than removed, which is a distinction worth
keeping: [`#[cgp_provider]` and `#[cgp_new_provider]`](../cgp/reference/macros/cgp_provider.md) work
but are what you read rather than write since
[`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md) arrived in [v0.6.0](v0-6-0.md);
[`UseDelegate`](../cgp/reference/providers/use_delegate.md) and
[`#[derive_delegate]`](../cgp/reference/attributes/derive_delegate.md) remain the mechanism CGP's own
error and handler components are defined with, but the `open` statement supersedes them for new code
as of [v0.8.0](v0-8-0.md); and getter traits remain useful in the narrow cases
[reading-context-fields](../cgp/guides/reading-context-fields.md) names, having lost the general case
to [`#[implicit]`](../cgp/reference/attributes/implicit.md) arguments in [v0.7.0](v0-7-0.md).

## The catalog

Twelve documents, oldest first. Each names its git tag and date, links to its announcement post and
that post's [internal document](../website/blog/README.md), and closes with what still stands.

- [v0.1.0](v0-1-0.md) — 2 September 2024. The first publication to crates.io, three months before the
  paradigm was announced. Components, wiring, fields, and errors are all recognizably present under
  older names.
- [v0.2.0](v0-2-0.md) — 8 December 2024. The pre-launch cleanup: `#[derive_component]` becomes
  `#[cgp_component]`, and the type-level vocabulary — `Cons`/`Nil`, `Either`/`Void`, `Field`,
  `Product!`, `Sum!` — arrives essentially in its final form.
- [v0.3.0](v0-3-0.md) — 8 January 2025. The first release after the public launch: abstract types,
  the getter macros, `CanWrapError`, and the error and runtime crates.
- [v0.3.1](v0-3-1.md) — 16 January 2025. A patch release adding the async error aliases, all of which
  were removed two releases later.
- [v0.4.0](v0-4-0.md) — 9 May 2025. The release that made CGP debuggable, and the largest by change
  count: `IsProviderFor`, `check_components!`, presets, `#[cgp_context]`, and the first
  datatype-generic support.
- [v0.4.1](v0-4-1.md) — 14 June 2025. The `cgp-handler` crate, introducing the computation family
  that most of CGP's later abstractions are built on.
- [v0.4.2](v0-4-2.md) — 7 July 2025. Extensible records and variants: the builder and visitor
  patterns, and safe enum upcasting and downcasting.
- [v0.5.0](v0-5-0.md) — 12 October 2025. The stabilization release: `#[derive(CgpData)]`,
  `#[cgp_auto_dispatch]`, monadic computation, and the removal of the `Async` trait.
- [v0.6.0](v0-6-0.md) — 26 October 2025. `#[cgp_impl]` and direct delegation on the context, which
  together are why current CGP reads like ordinary Rust.
- [v0.6.1](v0-6-1.md) — 1 February 2026. Implicit context types, `#[check_providers]`, and associated
  types in getter traits.
- [v0.7.0](v0-7-0.md) — 28 February 2026. The ergonomics release: `#[cgp_fn]`, `#[implicit]`,
  `#[uses]`, `#[extend]`, `#[use_provider]`, `#[use_type]`, and the removal of `#[cgp_context]`.
- [v0.8.0](v0-8-0.md) — **unreleased**, in development at `0.8.0-alpha`. Namespaces and paths, the
  `open` statement, the removal of presets, and the adoption of `cargo-cgp`.

There is **no v0.7.1**. It was planned as a minor namespace release, grew past that, and was
renumbered to v0.8.0; the draft announcement written under the old number is documented at
[website/blog/v0-8-0-release.md](../website/blog/v0-8-0-release.md).

## What counts as a release, and where the facts come from

A document exists here for every tag in [`cgp`](https://github.com/contextgeneric/cgp) that names a
published version. The pre-release tags — `v0.4.1-alpha`, the four `v0.5.0` betas, `v0.6.0-beta`,
`v0.8.0-alpha` — get no document of their own; the work in them is recorded against the release it
shipped in.

Every claim in these documents is verified against the tag rather than taken from a summary, because
the summaries disagree with the code in at least two places. The repository's
[CHANGELOG.md](https://github.com/contextgeneric/cgp/blob/main/CHANGELOG.md) heads its most recent
entry **"v0.6.2 (2026-03-01)"** for work that actually shipped as **v0.7.0 on 2026-02-28** — the
release was renumbered when its breaking changes were counted, and the heading was never updated. And
that same changelog credits v0.5.0 with a `MatchStr` trait that had already been deleted before the
tag was cut. Read the changelog for the shape of a release and the tagged source for what it contains.

## Adding a release document

When a version is tagged, add its document following the shape of the existing ones: a one-sentence
summary, a framed list of identifying facts, then **what it introduced**, **what it changed or
removed**, and **how it relates to the current release**. Update the removal ledger above with
anything the release renamed or deleted, add the entry to the catalog, register the document in
[../summary.md](../summary.md), and add or revise the announcement post's document under
[../website/blog/](../website/blog/README.md) so the two point at each other. There is no `AGENTS.md`
here — the base-wide [../AGENTS.md](../AGENTS.md) governs these documents, with the single exception
that this is the one section allowed to describe the past.
