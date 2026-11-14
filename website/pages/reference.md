# Reference

The reference is the site's canonical construct reference, one page per named construct, ported from
the internal reference.

- **URL:** <https://contextgeneric.dev/docs/reference/>
- **Source:** [docs/reference/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/reference)
- **Status:** Current: the index and every construct page are written, and every group has its
  `example-code` mirror
- **How it was made:** ported by an agent from [cgp/reference/](../../cgp/reference/README.md); level
  one of the four in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md)

## What it covers

The reference is the site's largest surface and is [canonical](../writing-guides/reference.md)
rather than a supplement to docs.rs: the completeness obligation is against the index, so no
construct is missing from the site. It is a top-level category at `docs/reference/`, position 7, with
a hand-written index as its category link and seven subdirectories by what a construct *is*, each of
which links a written overview as its category page. Two pages document no construct:
the [compile-errors page](compile-errors.md) and the [glossary](glossary.md).

The groups and their layout:

- **`macros/`:** twenty-two pages; the three argument-free macros have no grammar section.
- **`attributes/`:** ten pages, including `#[default_impl(...)]`, `#[impl_generics(...)]`, and
  `#[prefix(...)]`.
- **`derives/`:** eight pages.
- **`components/`:** seventeen pages, one per component: `has_error_type`, `can_raise_error`,
  `can_wrap_error`, `has_type`, `has_runtime`, `has_runtime_type`, `runner`, and `send_runner`, plus
  a nine-page `handler/` subsection (`handler`, `computer`, `try_computer`, `producer`,
  `async_computer`, `computer_ref`, `try_computer_ref`, `handler_ref`, `async_computer_ref`) with its
  own overview. These use the guide's
  [built-in-component variant](../writing-guides/reference.md#the-layered-page).
- **`providers/`:** fifty pages: sixteen singletons, including the five `With…` aliases
  (`WithContext`, `WithType`, `WithField`, `WithFieldRef`, `WithDelegatedType`), and the subsections
  `error/` (7), `handler/` (13), `dispatch/` (11), and `monad/` (3), each with an overview.
- **`traits/`:** fifty-seven construct pages in eleven importance-ordered subdirectories mirroring the
  internal trait families: `wiring` (3), `field-access` (6), `shape` (5), `builder` (7), `optional`
  (8), `variant` (7), `casting` (4), `type-level` (7), `namespace` (3), `formatting` (3), and `monad`
  (4). A top-level overview and one per subdirectory make twelve overviews; the group's
  `_category_.json` links the top-level one, and `sidebar_position` carries the ordering. Every trait
  page carries the guide's [Definition section](../writing-guides/reference.md#the-layered-page) and
  states where its traits are imported from.
- **`types/`:** eleven construct pages and an overview, flat with no subdirectory, in importance
  order: `phantom_data`, `field`, `index_type` (the `Index` type, renamed because `index.md` is the
  overview), `life`, the lists `cons`, `nil`, `either`, `void`, `chars`, and `path_cons`, and `mref`
  last. Each list family's explanation lives on its head cell (`Cons`, `Either`, `Chars`,
  `PathCons`). The overview frames `mref` as the one ordinary runtime type among the building blocks.

**Every page with code has an `example-code` mirror** under `tests/reference/`, compiled with a
`check_components!` assertion per wired context, with rejected snippets as fixtures. `UseFieldRef` has
no mirror of its own, since its wireable example lives on `with_field_ref`; `use_delegated_type`'s
mirror covers the direct `TypeProviderComponent` form, and its alias form lives on
`with_delegated_type`. The `types/` overview shows no code and has no file.

## How it relates to the knowledge base

Each page derives from [cgp/reference/](../../cgp/reference/README.md), which stays the source of
truth; [writing-guides/reference.md](../writing-guides/reference.md) holds the porting procedure and
the six-section layered descent.

**The mapping is one internal document to one or more pages, depending on the group.** In `macros/`,
`attributes/`, `components/`, and `providers/` the file names match and most relative links port
unchanged. In `derives/`, `traits/`, and `types/` the site's
[one page per named construct](../writing-guides/reference.md#granularity-one-page-per-named-construct)
splits a family document across pages: `traits/has_builder.md` feeds seven, `traits/extract_field.md`
six, `traits/optional_fields.md` eight. Each internal document names the pages it feeds in a note
under its Source section. The special cases:

- `derives/derive_cgp_record.md` and `derives/derive_cgp_variant.md` both come from
  [derive_cgp_data.md](../../cgp/reference/derives/derive_cgp_data.md).
- `cgp_provider.md` covers `#[cgp_new_provider]` too, the one surviving consolidation.
- The internal `type_level_spines.md` is split into one page per list type.
- The internal `chars.md`, which documents `Chars` and `Symbol`, feeds the `chars` page; the `Symbol`
  type stays on the [`Symbol!`](../../cgp/reference/macros/symbol.md) macro page.
- The internal `index.md` becomes `index_type.md`.
- `PhantomData` has no internal document; its page is authored on the site.
- `use_field.md` became `use_field`, `use_field_ref`, and `use_fields`.

The [guides](../../cgp/guides/README.md) fold into each page's *When to use it*:
[writing providers](../../cgp/guides/writing-providers.md) and
[sizing a component](../../cgp/guides/sizing-a-component.md) supply most of two, and
[naming a type dependency](../../cgp/guides/naming-a-type-dependency.md) the
`#[impl_generics]`-versus-abstract-type decision on `#[cgp_fn]`. Implementation documents become
GitHub source links. The shared running example is the `Rectangle` area calculation from
[area calculation](../../examples/area-calculation.md), a **value context, self-targeted**, chosen
because a reference page illustrates a construct rather than teaching a design.

## Conventions

The page shape, its variants, the front matter, the "context" gloss, the provenance note, and the
verification every page follows are specified once in
[writing-guides/reference.md](../writing-guides/reference.md#conventions-the-port-must-follow).

## Maintaining it

- The pages and the internal reference are bound by the
  [synchronization rule](../../AGENTS.md#the-synchronization-rule) in both directions: a change to a
  macro updates the code, the internal document, and the page. A page that disagrees with its
  internal document is the defect.
- Update the counts above when a page is added or split, as the guide's
  [granularity rule](../writing-guides/reference.md#granularity-one-page-per-named-construct) says.
