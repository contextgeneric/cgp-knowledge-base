# The CGP Patterns book

This document is the knowledge base's record of and plan for the **CGP Patterns book**: which of its
chapters are current, why it cannot be updated gradually, and how its chapters route readers to the
website. The plan is to keep the book, annotate its stale chapters, and link it forward, all in the
book's own repository.

The website treats the book as a
[legacy resource](AGENTS.md#leave-legacy-resources-off-public-pages), so no public page links or
recommends it; this record stays for the book's repository.

- **URL**: <https://patterns.contextgeneric.dev/>
- **Source**: [`cgp-patterns`](https://github.com/contextgeneric/cgp-patterns), an
  [mdBook](https://rust-lang.github.io/mdBook/) whose chapters live in `content/`
- **Last updated**: its content 2025-05-09, for the v0.4.0 release. On the book's `v0.8.0` branch,
  not yet merged, the introduction's *The State of This Book* section says which chapters are
  current and which predate the syntax; the published `main` still shows *Work In Progress*
- **Library pin**: `cgp = "0.4.0"`, four minor versions behind v0.8.0
- **Status**: **Outdated** in part: 7 of 19 written chapters are current, 12 are not
- **Written**: 19 chapters of a 47-entry table of contents; the other 28 entries link nowhere

The record sits in `website/` because
[information-architecture.md](information-architecture.md#the-sites-job-and-the-properties-around-it)
decides what each public property owns, and the plan is a routing decision between two of them. If the
book is revived as a maintained property, it graduates to its own section with a document per chapter.

## What the search data says the book is worth

**The book earns 308 clicks a year from 19 pages; the main site earns 672 from 91**, in the export
[seo.md](seo.md#what-was-measured) is written against. Its traffic is concentrated:

| Chapter | Impressions | Clicks | CTR | Position |
|---|---|---|---|---|
| `blanket-implementations.html` | 12,232 | **237** | 1.94% | 6.8 |
| `(index)`, the introduction | 1,809 | 27 | 1.49% | 7.2 |
| `provider-traits.html` | 2,351 | 20 | 0.85% | 12.4 |
| `provider.html` | 330 | 6 | 1.82% | 12.3 |
| every other chapter | 9,000 approx. | 18 total | — | 9–21 |

**One chapter is 77% of the book**, and it earns most of the blanket-implementation query family, the
project's best term: 2,019 impressions and 110 clicks a year at position 5.8.

## The chapters split in two, and the traffic is in the current half

**Seven chapters use no CGP macros and are current; twelve show wiring the library has since removed
or replaced.** No modern idiom (`#[cgp_impl]`, `#[cgp_fn]`, `#[implicit]`, `#[uses]`) appears anywhere
in the book.

- **Current (7 chapters, about 1,300 lines):** `introduction`, `context`, `consumer`, `provider`,
  `blanket-implementations`, `impl-side-dependencies`, `provider-traits`. They include both
  best-performing pages and need only a forward link.
- **Lightly stale (3 chapters, about 1,760 lines):** `consumer-provider-link`, `provider-delegation`,
  and `debugging-support` use `HasCgpProvider`, removed in v0.6.0; their arguments stand.
- **Fully stale (9 chapters, about 5,300 lines):** `component-macros`, `associated-types`,
  `error-handling`, `delegated-error-raiser`, `error-reporting`, `error-wrapping`, `field-accessors`,
  `generic-accessor-providers`, and `use-field-pattern` show `#[cgp_context]` (removed in v0.7.0), the
  inside-out `#[cgp_provider]` and `#[cgp_new_provider]` form (superseded by `#[cgp_impl]` in v0.6.0),
  and in two cases `symbol!` (now `Symbol!`).
- **Unwritten (28 entries):** Component Presets; Trait-Generic Providers and its four sub-chapters;
  Provider Composition and its two; Inner; Builder; Dispatcher; Generic Data Types; Async Generic;
  Fully Abstract Programs; the five Domain-Specific Patterns; and the eight Related Concepts. Each is
  written `[Title]()`, so mdBook renders it as an unlinked line. Separately, 22 title-only stub files
  in `content/`, such as `monad.md`, are referenced by nothing.

**Only the introduction links out**, three times to the site; the other eighteen chapters send their
readers nowhere, including the 237 a year who finish *Blanket Implementations* one sentence from CGP's
central argument.

**CI compiles every snippet against one pinned `cgp` version**, with `cargo test` and `mdbook test`.
The modern idioms do not exist in 0.4.0, so bumping the pin breaks all twelve stale chapters at once,
and rewriting one chapter fails CI until the pin moves. **There is no gradual path**: the choice is a
single rewrite of about 5,300 lines, or keeping the pin and telling readers the truth. This plan
chooses the second.

## The four decisions

- **Keep the book.** Retiring or redirecting it discards the project's best-performing page, and its
  seven current chapters derive CGP from plain Rust at a pace the site's
  [explanation tier](writing-guides/explanation.md) deliberately does not attempt.
- **Do not finish it.** The site has written nearly all the unwritten material: *Related Concepts* is
  the [Comparisons](pages/comparisons.md) section, *Trait-Generic Providers* the
  [Reference](pages/reference.md)'s `providers/` group, and *Builder*, *Dispatcher*, and *Generic Data
  Types* are [Concepts](pages/concepts.md) pages. A second version would split the effort and compete
  with the site in search.
- **Annotate and route rather than rewrite.** Each stale chapter gets a short dated note naming the
  constructs it predates and where the current account lives, the remedy
  [AGENTS.md](AGENTS.md#do-not-rewrite-history) sanctions for a misleading post.
- **Route forward from the current half too**, where the readers are.

## The routing map

Each chapter's note points at the page that now owns its material. Every destination was verified on
the website's `v0.8.0` branch on 2026-09-21, so **the notes cannot land until that branch merges**.

| Book chapter | Current home on the site |
|---|---|
| Context, Consumer, Provider, Provider Traits, Linking Consumers with Providers | `docs/concepts/consumer-and-provider-traits` |
| Blanket Implementations | `docs/concepts/coherence`, `docs/reference/glossary#blanket-implementation`, `docs/reference/macros/blanket_trait` |
| Impl-side Dependencies | `docs/concepts/impl-side-dependencies` |
| Provider Delegation | `docs/reference/macros/delegate_components`, `docs/concepts/aggregate-providers` |
| Debugging Support | `docs/concepts/check-traits`, `docs/cargo-cgp/`, `docs/reference/errors` |
| Component Macros | `docs/reference/macros/cgp_component`, `docs/reference/macros/cgp_impl` |
| Associated Types | `docs/concepts/abstract-types`, `docs/reference/macros/cgp_type` |
| Error Handling and its three sub-chapters | `docs/concepts/modular-error-handling`, `docs/reference/components/has_error_type`, `can_raise_error`, `can_wrap_error` |
| Field Accessors, Generic Accessor Providers, The `UseField` Pattern | `docs/concepts/implicit-arguments`, `docs/reference/attributes/implicit`, `docs/reference/macros/cgp_auto_getter`, `docs/reference/providers/use_field` |
| Component Presets *(unwritten)* | `docs/concepts/namespaces`, `docs/reference/macros/cgp_namespace` |
| Trait-Generic Providers *(unwritten)* | `docs/reference/providers/with_provider`, `use_context`, `use_type`, `use_delegate` |
| Provider Composition *(unwritten)* | `docs/concepts/higher-order-providers` |
| Builder, Dispatcher, Generic Data Types *(unwritten)* | `docs/concepts/extensible-records`, `dispatching`, `extensible-variants` |
| Async Generic *(unwritten)* | `docs/concepts/send-bounds` |
| Fully Abstract Programs *(unwritten)* | `docs/concepts/modularity-hierarchy` |
| Runtime *(unwritten)* | `docs/reference/components/has_runtime` |
| Related Concepts, all eight *(unwritten)* | `docs/comparisons/`: dependency injection, ML modules, algebraic effects, dynamic dispatch, type classes, and the rest |

## How it relates to the knowledge base

An agent revising a chapter reads the internal document that owns its material:

- **The first two sections:** [consumer-and-provider-traits](../cgp/concepts/consumer-and-provider-traits.md)
  and [coherence](../cgp/concepts/coherence.md).
- **Blanket Implementations and Impl-side Dependencies:**
  [impl-side-dependencies](../cgp/concepts/impl-side-dependencies.md) and the
  [`#[blanket_trait]`](../cgp/reference/macros/blanket_trait.md) reference.
- **Provider Delegation:** [`delegate_components!`](../cgp/reference/macros/delegate_components.md) and
  [aggregate-providers](../cgp/concepts/aggregate-providers.md).
- **Debugging Support:** [check-traits](../cgp/concepts/check-traits.md), the
  [debugging guide](../cgp/guides/debugging.md), and [cargo-cgp/](../cargo-cgp/README.md).
- **Component Macros:** [`#[cgp_component]`](../cgp/reference/macros/cgp_component.md) and
  [`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md).
- **Associated Types:** [abstract-types](../cgp/concepts/abstract-types.md).
- **The error chapters:** [modular-error-handling](../cgp/concepts/modular-error-handling.md).
- **The accessor chapters:** [implicit-arguments](../cgp/concepts/implicit-arguments.md) and
  [`#[implicit]`](../cgp/reference/attributes/implicit.md).
- **Unwritten entries:** *Component Presets* is [namespaces](../cgp/concepts/namespaces.md), and
  *Related Concepts* is [related-work/](../related-work/README.md).

A B-3 note dates each construct from the [removal ledger](../releases/README.md) rather than from
memory, and [seo.md](seo.md) holds the traffic figures the plan rests on.

## The work, in order

These changes remain, all in the `cgp-patterns` repository. **The book's status lands with the
release**: its `v0.8.0` branch, whose introduction states which chapters are current, is reviewed
against the release and merged with it, so the published book stops calling itself a work in
progress. The rest are ordered by value per minute. **B-1 and B-3 wait for the website's `v0.8.0`
branch to merge**, because their destinations 404 until then; B-4 and B-5 do not.

**B-1: link forward from the four chapters that have readers.** *Blanket Implementations* (237
clicks), the introduction (27), *Provider Traits* (20), and *Provider* (6) carry 290 of the book's 308
annual clicks. Add a short "where this goes next" line to each, pointing at its page in the map, with
no banner or apology, since these chapters are current. **This is the cheapest high-value change
available to the project**, and it is the forward link [seo.md](seo.md#the-off-site-metadata-is-under-set)
asks for.

**B-3: add the dated note to the twelve stale chapters**, naming the constructs each predates and
linking its row in the map. Write each by hand: mdBook has no banner mechanism, and a preprocessor
would be site machinery for a one-off.

**B-4: fix `HasCgpProvider` in the three lightly stale chapters.** First check that the replacement
compiles against the 0.4.0 pin; if it does not, the three keep the B-3 note instead.

**B-5: retire the unwritten table of contents.** Delete the 28 destinationless entries from
`SUMMARY.md` and the 22 unreferenced stub files, and replace the affected sections with a short note
pointing at the site; a table of contents advertising chapters that will never be written
misrepresents the book. `create-missing = false` means mdBook will not generate the stubs, not that it
needs them.

## What must not happen

- **Do not redirect the book to the site.** It would discard 308 clicks a year and the project's
  strongest position on its best term for pages with no search history.
- **Do not bump the `cgp` pin without rewriting the twelve chapters in the same change**, because CI
  compiles every snippet.
- **Do not fix a stale chapter by deleting it.** The error-handling and field-accessor chapters are
  the fullest treatment the project has written of those subjects; a dated note keeps the explanation
  while disowning the syntax.
- **Do not write the unwritten chapters.** They belong to the site.
- **Do not link the book into this knowledge base.** The [one-way link rule](AGENTS.md#the-one-way-link-rule)
  covers every public property.

## Maintaining it

Revisit this document when the `v0.8.0` branch merges, since B-1 and B-3 become doable; when a new
Search Console export is taken, since the plan rests on the book's traffic concentration; and if the
book is revived, which reopens "annotate and route". Keep the chapter inventory in step with
`content/SUMMARY.md`, the part most easily left behind.
