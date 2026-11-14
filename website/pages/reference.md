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
a hand-written index as its category link and seven subdirectories by what a construct *is*. The
groups with a written Overview (`macros/`, `attributes/`, `derives/`, `providers/`, and `traits/`)
link it as their category page; the rest use a `generated-index`. Two pages document no construct:
the [compile-errors page](compile-errors.md) and the [glossary](glossary.md).

The groups and their layout:

- **`macros/`:** twenty-two pages. The three argument-free macros, `#[async_trait]`,
  `#[cgp_auto_dispatch]`, and `#[cgp_auto_getter]`, get no grammar section, matching the
  [internal rule](../../cgp/AGENTS.md#syntax-grammar-conventions); it is the only place the template
  loses a part.
- **`attributes/`:** ten pages, including `#[default_impl(...)]`, `#[impl_generics(...)]`, and
  `#[prefix(...)]`, each moved out of the page that once documented it.
- **`derives/`:** eight pages.
- **`components/`:** seventeen pages, one per component: `has_error_type`, `can_raise_error`,
  `can_wrap_error`, `has_type`, `has_runtime`, `has_runtime_type`, `runner`, and `send_runner`, plus
  a nine-page `handler/` subsection (`handler`, `computer`, `try_computer`, `producer`,
  `async_computer`, `computer_ref`, `try_computer_ref`, `handler_ref`, `async_computer_ref`) with its
  own overview. These use the **built-in-component variant** of the layered page: a *Definition*
  section after *Overview* shows the trait and explains each attribute on it, linking the attribute's
  page, and there is no *Under the hood*, per
  [writing-guides/reference.md](../writing-guides/reference.md#the-layered-page).
- **`providers/`:** fifty pages: sixteen singletons, including the five `With…` aliases
  (`WithContext`, `WithType`, `WithField`, `WithFieldRef`, `WithDelegatedType`), each given a page for
  the `WithProvider<Inner>` spelling a reader looks up by name, and the subsections `error/` (7), `handler/` (13), `dispatch/` (11),
  and `monad/` (3), each with an overview. For `WithFieldRef` and `WithDelegatedType`, the alias page
  carries the wiring form and example while the inner provider's page keeps the mechanism.
- **`traits/`:** fifty-seven construct pages in eleven importance-ordered subdirectories mirroring the
  internal trait families: `wiring` (3), `field-access` (6), `shape` (5), `builder` (7), `optional`
  (8), `variant` (7), `casting` (4), `type-level` (7), `namespace` (3), `formatting` (3), and `monad`
  (4). A top-level overview and one per subdirectory make twelve overviews; the group's
  `_category_.json` links the top-level one, and `sidebar_position` carries the ordering. Every trait
  page adds a *Definition* after *Overview* showing the trait's own item and explaining each element,
  and keeps *Under the hood* for how the macros generate and consume it. Each page states where its
  traits are imported from, because about half are not in the prelude.
- **`types/`:** eleven construct pages and an overview, flat with no subdirectory, in importance
  order: `phantom_data`, `field`, `index_type` (the `Index` type, renamed because `index.md` is the
  overview), `life`, the lists `cons`, `nil`, `either`, `void`, `chars`, and `path_cons`, and `mref`
  last. Each list family's explanation lives on its head cell (`Cons`, `Either`, `Chars`,
  `PathCons`). The overview frames `mref` as the one ordinary runtime type among the building blocks.

**Three decisions from the one-page-per-construct split are settled:**

- **Markers stay with their trait.** `IsPresent` and the other six are types implementing `MapType` or
  `MapTypeRef`, not constructs, so the index's *Looking for a name you don't see?* table routes them.
- **A construct documented inside another page moves to its own page** in the directory its kind
  belongs to.
- **The `example-code` mirror splits with the pages,** since a mirror file naming a page that no
  longer exists is worse than none.

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

## Conventions the port must follow

These mechanics are settled; copy them rather than rediscover them.

- **Generated machinery notice.** A construct the macros generate opens with an `:::info` block
  between the summary and *Overview*, saying the reader is not expected to use it, which macro
  produces or consumes it, and that the page explains what that macro emits. Twenty-four `traits/`
  pages carry one; the `types/` pages do not, because their overview already frames them as building
  blocks. It shares position and shape with the *Legacy — read, don't write* notice on
  `attributes/derive_delegate.md`, and a page carries at most one; the test is in
  [writing-guides/reference.md](../writing-guides/reference.md#say-when-a-construct-is-machinery-the-macros-generate).
- **Titles and descriptions.** Every page carries a `description`. A page whose heading is a
  construct name also carries a search-facing `title`, while its `h1` stays the name, such as
  `` # `#[cgp_component]` ``; the `sidebar_label` is untouched. A page whose heading is already what a
  reader searches, such as every Concepts and Comparisons page, carries a `description` only. Without
  a `description`, Docusaurus takes the first line, which on a construct page is mostly punctuation.
  [seo.md](../seo.md) holds the reasoning and measurement. The rules:
  - Put the construct name first and keep the title under about 45 characters; a description has
    about 155 before a search result cuts it.
  - Do not name CGP in a page's own title, because the suffix `| CGP — Context-Generic Programming`
    carries it; the exception is a page whose subject is CGP, such as the disclosure page or the
    skill.
  - A page covering two constructs names both and drops the job phrase, as `#[cgp_provider]` and
    `#[cgp_new_provider]` do.
  - Write each description from the page's own summary line.
  - Escape apostrophes in single-quoted YAML (`'a context''s wiring table'`); an unescaped one fails
    the build with an error naming the wrong line.
- **Anchors come from heading text,** because the MDX setup rejects `{#custom-id}`, so section
  headings cannot be reworded freely.
- **One shared provenance note** closes every reference page, a written index included: "An AI agent
  wrote this page using the CGP knowledge base. Its content was verified against the library's
  source. See How AI is used in this project.", the last phrase linking the disclosure's
  documentation section (see [AGENTS.md](../AGENTS.md#disclosing-ai-use-on-a-page)). Other footers
  follow its sentence structure: "revised" for a revision alone, "wrote and revised" for both;
  tooling pages keep their claims about verification against the tool; a footer never attributes
  verification to a person or agent the record does not name. Pages without a note and the skill
  snapshot are outside this convention.
- **`## Formal grammar` is its own section** after *Under the hood*, citing the Rust Reference's
  notation page.
- **Snippets are compiled.** Every example compiles against `cgp` 0.8.0 with a `check_components!`
  assertion per wired context, and a page documenting a failure quotes the message the compiler
  actually produced.
- **Expansions are checked with `cargo cgp expand`,** `--lib --item` on each item the page shows (for
  a component: the consumer trait, the provider trait, the wired context, and the provider; for a
  `#[cgp_fn]`: the generated trait), never copied from the internal document. Treat a remembered path
  expansion as suspect: an `@`-path key's tail is a generic parameter, not `Nil`, and `expand`
  resugars unevenly, returning an `open` header's redirect target as `Path!(@Component)` while the
  per-entry key stays a raw `PathCons` list, so a page showing both says so.
- **Every page closes with *The ideas behind it*,** after *Related constructs* and before *Source*:
  two or three entries, never more, each naming a Concepts page and what it adds in a phrase. The page
  keeps its own one-sentence summaries, so the list is a route onward, not a substitute.
- **A mention of `cargo cgp check` links** <https://contextgeneric.dev/docs/cargo-cgp/check>, not the
  tool's repository.
- **Gloss "context" on first use, on every page, above the advanced line,** with the canonical clause
  from [vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each),
  "the type the method runs on, which supplies the values it needs as its fields", or a variant that
  file permits: "the type the implementation runs against", "the type the code runs against", "the
  type it runs against", or, on abstract-type pages, "the type that implements the trait". A new
  variant goes into vocabulary.md first, and the clause never says "capability", per
  [vocabulary.md](../../communication-strategy/vocabulary.md#words-and-framings-to-avoid). The full account is
  on the concept page, reached through the sidebar. It is the convention most easily dropped.
  - Six pages are exempt because they never use the word above the advanced line: `Product!`,
    `Sum!`, `Struct!`, `Enum!`, `Path!`, and `#[async_trait]`. `Symbol!` is not exempt.
  - A mechanical check must allow the phrase to wrap across lines and its permitted variants, and
    must ignore `MyContext` inside code blocks.
- **Sidebar labels carry no backticks,** because a `sidebar_label` is plain text; keep the backticks
  in the `#` heading.
- **An admonition's title is a heading on its own line.** Write `:::info`, a blank line, then
  `### Still being written`; on this installation `:::info Still being written` is not a directive,
  and the block renders as three plain paragraphs without a build error. The bracket form
  `:::info[Still being written]` renders but was not chosen; the heading form makes the title a link
  target and a table-of-contents entry.

## Maintaining it

- The pages and the internal reference are bound by the
  [synchronization rule](../../AGENTS.md#the-synchronization-rule) in both directions: a change to a
  macro updates the code, the internal document, and the page. A page that disagrees with its
  internal document is the defect.
- Update the counts above when a page is added or split.
