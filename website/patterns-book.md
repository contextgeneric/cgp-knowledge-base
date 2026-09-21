# The CGP Patterns book

This document is the knowledge base's record of and plan for the **CGP Patterns book**, the project's
second public documentation property: what it contains, which half of it has gone stale, why it cannot
be updated gradually, and how its chapters should route readers to the material the website now
carries.

- **URL** — <https://patterns.contextgeneric.dev/>
- **Source** — [`cgp-patterns`](https://github.com/contextgeneric/cgp-patterns), an
  [mdBook](https://rust-lang.github.io/mdBook/) whose chapters live in `content/`
- **Last updated** — its content 2025-05-09, for the v0.4.0 release; its introduction revised since,
  per B-2 below
- **Library pin** — `cgp = "0.4.0"`, four releases behind the published library
- **Status** — **Outdated** in part: 7 of 19 written chapters are current, 12 are not
- **Written** — 19 chapters of a 47-entry table of contents; the other 28 entries link nowhere

## Why this document exists, and why it sits here

**The book is the only public CGP property with no record in this knowledge base.** It is absent from
[sibling-projects.md](../sibling-projects.md), from the base [README](../README.md)'s project list, and
from every section catalog — while being, per the measurements below, the best-performing set of pages
the project publishes. That gap is what this document closes.

It sits in `website/` rather than in a section of its own because
[information-architecture.md](information-architecture.md#the-sites-job-and-the-properties-around-it)
already frames the four public properties carrying CGP's documentation and decides what each owns, and
because the whole of the plan below is a routing decision between two of them. If the book is ever
revived as an actively maintained property, it should graduate to its own section with a document per
chapter; while the plan is "annotate and route", one document is the proportionate form.

## What the search data says the book is worth

**The book earns 308 clicks a year from 19 pages; the main site earns 672 from 91.** Per page it
outperforms everything else the project publishes, and the measurement comes from the same twelve-month
Search Console export the [SEO strategy](seo.md#what-was-measured) is written against.

Its traffic is concentrated to an unusual degree:

| Chapter | Impressions | Clicks | CTR | Position |
|---|---|---|---|---|
| `blanket-implementations.html` | 12,232 | **237** | 1.94% | 6.8 |
| `(index)` | 1,809 | 27 | 1.49% | 7.2 |
| `provider-traits.html` | 2,351 | 20 | 0.85% | 12.4 |
| `provider.html` | 330 | 6 | 1.82% | 12.3 |
| every other chapter | 9,000 approx. | 18 total | — | 9–21 |

Two notes on reading that table. The index **is** the introduction — mdBook renders `introduction.md`
as `index.html`, so they are one page rather than two. And **one chapter is 77% of the book**:
*Blanket Implementations* also carries the term the whole project performs best on: the blanket-implementation query family is 2,019 impressions and 110 clicks at
average position 5.8, and this page is what earns most of it.

## The finding that shapes the plan

**The book splits cleanly in two, and the traffic is in the half that has not gone stale.** Seven
written chapters use no CGP macros at all — they teach the ideas from plain Rust, and plain Rust has
not changed. Twelve chapters show wiring, and every one of them shows constructs the library has since
removed or replaced.

The project's current public line, that the book "has not been updated for some time", is therefore
wrong in both directions at once: it undersells seven chapters that are perfectly current, and
under-warns about twelve that teach three removed constructs.

### The chapter inventory

**Current — no CGP macros, nothing stale (7 chapters, ~1,300 lines).** `introduction`, `context`,
`consumer`, `provider`, `blanket-implementations`, `impl-side-dependencies`, `provider-traits`. These
are the book's first two sections plus the opening of its third, they include both of its
best-performing pages, and they need a forward link and nothing else.

**Lightly stale — one removed name each (3 chapters, ~1,760 lines).** `consumer-provider-link`,
`provider-delegation`, `debugging-support` use `HasCgpProvider`, removed in v0.7.0. Their arguments
stand; only the name is dead.

**Fully stale — the removed wiring stack (9 chapters, ~5,300 lines).** `component-macros`,
`associated-types`, `error-handling`, `delegated-error-raiser`, `error-reporting`, `error-wrapping`,
`field-accessors`, `generic-accessor-providers`, `use-field-pattern` show `#[cgp_context]` (removed
v0.7.0), the inside-out `#[cgp_provider]`/`#[cgp_new_provider]` form (superseded by `#[cgp_impl]` in
v0.6.0), and in two cases `symbol!` (now `Symbol!`). None of them shows `#[cgp_impl]`, `#[cgp_fn]`,
`#[implicit]`, or `#[uses]` — **no modern idiom appears anywhere in the book.**

**Unwritten — 28 entries that link nowhere.** Component Presets; Trait-Generic Providers and its four
sub-chapters; Provider Composition and its two; Inner; Builder; Dispatcher; Generic Data Types; Async
Generic; Fully Abstract Programs; the five Domain-Specific Patterns; and the eight Related Concepts.
Each is written `[Title]()` with an empty destination, so mdBook renders it as an unlinked line.

Separately, **22 title-only stub files sit in `content/` unreferenced by the table of contents** —
`monad.md` is the seven bytes `# Monad`, `dependency-injection.md` is `# Dependency Injection`, and so
on. They are leftovers from a planned structure rather than anything mdBook needs; nothing points at
them and nothing builds them.

### The book sends its readers nowhere

**Eighteen chapters in nineteen link nowhere.** The introduction now points at the site three times,
after B-2; every other chapter links out not at all. So the book's 308 annual clicks — including the
237 that land on *Blanket Implementations*, a chapter one sentence away from CGP's central argument —
still arrive at a closed property and leave from it.

This is the finding that makes B-1 below the highest-value change left in this document, and it is
independent of everything else here: it would be worth doing even if no chapter had gone stale. **It
cannot be done yet**, because three of its four destinations are Concepts pages that return 404 until
the `v0.8.0` branch merges — which is the one scheduling fact about this plan most easily got wrong.

### Why the book cannot be updated a chapter at a time

**CI compiles every snippet in the book against one pinned `cgp` version.** The workflow runs
`cargo test` and `mdbook test`, so the book's code is verified in a way the blog's never was — which is
an asset, and also the constraint that decides the plan. The pin is `cgp = "0.4.0"`, and the modern
idioms do not exist in 0.4.0: `#[cgp_impl]` arrived in v0.6.0 and `#[cgp_fn]`, `#[implicit]`, and
`#[uses]` in v0.7.0.

So **bumping the pin breaks all twelve stale chapters at once**, and rewriting one chapter into current
syntax fails CI until the pin moves. There is no gradual path. The choice is a single rewrite of
roughly 5,300 lines, or leaving the pin where it is and telling readers the truth. This document
recommends the second.

## The four decisions

**Keep the book.** Retiring or redirecting it would discard the project's best-performing page and the
one query family it is a recognized answer for. The seven current chapters also do a job no page on the
website does: they derive CGP from plain Rust at a pace the site's
[explanation tier](writing-guides/explanation.md) deliberately does not attempt.

**Do not finish it.** The 25 unwritten chapters were planned before the website had a documentation
tree, and the site has since written nearly all of that material: *Related Concepts* is now the
eleven-page [Comparisons](site-structure.md#comparisons) section, *Trait-Generic Providers* is the
`providers/` group of the [Reference](site-structure.md#reference), and *Builder*, *Dispatcher*, and
*Generic Data Types* are [Concepts](site-structure.md#concepts) pages. Writing them again in the book
would duplicate the site, split the project's effort, and put two versions of each idea into search
results competing with each other.

**Annotate and route rather than rewrite.** Each stale chapter gets a short dated note at its top
saying which constructs it predates and where the current account lives. This is the same remedy
[AGENTS.md](AGENTS.md#do-not-rewrite-history) sanctions for a misleading published post, and for the
same reason: the chapter remains a readable explanation of an idea, while the reader is told not to
copy its code.

**Route forward from the current half too.** The seven clean chapters are where the readers actually
are, and a reader finishing *Blanket Implementations* is one sentence away from CGP's central argument.
That link is the single highest-value change in this document.

## The routing map

Each chapter's note points at the page that now owns its material. Every destination below was verified
to exist on the website repository's `v0.8.0` branch on 2026-09-21, so **the notes cannot land until
that branch merges** — which makes this work a natural follow-on to the relaunch rather than something
to do before it.

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
| Related Concepts, all seven *(unwritten)* | `docs/comparisons/` — dependency injection, ML modules, algebraic effects, dynamic dispatch, type classes, and the rest |

## How it relates to the knowledge base

The map above sends a *reader* to a public page. An agent revising a chapter needs the internal
document that owns the material, and this is the section the website directory exists for.

The book's subjects map onto the base as follows. Its first two sections rest on
[consumer-and-provider-traits](../cgp/concepts/consumer-and-provider-traits.md) and
[coherence](../cgp/concepts/coherence.md); *Blanket Implementations* and *Impl-side Dependencies* on
[impl-side-dependencies](../cgp/concepts/impl-side-dependencies.md) and the
[`#[blanket_trait]`](../cgp/reference/macros/blanket_trait.md) reference; *Provider Delegation* on
[`delegate_components!`](../cgp/reference/macros/delegate_components.md) and
[aggregate-providers](../cgp/concepts/aggregate-providers.md); *Debugging Support* on
[check-traits](../cgp/concepts/check-traits.md), the [debugging guide](../cgp/guides/debugging.md), and
[cargo-cgp/](../cargo-cgp/README.md); *Component Macros* on
[`#[cgp_component]`](../cgp/reference/macros/cgp_component.md) and
[`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md); *Associated Types* on
[abstract-types](../cgp/concepts/abstract-types.md); the error chapters on
[modular-error-handling](../cgp/concepts/modular-error-handling.md); and the accessor chapters on
[implicit-arguments](../cgp/concepts/implicit-arguments.md) and
[`#[implicit]`](../cgp/reference/attributes/implicit.md). Of the unwritten entries, *Component Presets*
is now [namespaces](../cgp/concepts/namespaces.md) and the whole *Related Concepts* section is
[related-work/](../related-work/README.md).

**Two documents do specific jobs for this plan.** The
[removal ledger](../releases/README.md) dates every construct the book teaches and the library has
since dropped, so it is what a B-3 note cites rather than a guess about when `#[cgp_context]` went
away. And [seo.md](seo.md) holds the measurement the plan rests on, so a change in the book's traffic
profile is recorded there and read back here.

## The work, in order

Five changes remain, all in the `cgp-patterns` repository. They are ordered by value per minute. B-2
has landed: the introduction's *Work In Progress* section, which promised a completed book that will
not arrive, is now an honest account of which chapters are current and which predate the syntax, and
the duplicated sentence fragment and the `www` link went with it.

**B-1 and B-3 both wait for the `v0.8.0` branch to merge**, because their destinations are Concepts
pages that 404 until then. B-4, B-5, and B-6 do not.

**B-1 — link forward from the four chapters that have readers.** *Waits for the merge*, since its
destinations do not exist publicly until then. *Blanket Implementations* (237
clicks), the introduction that renders as the index (27), *Provider Traits* (20), and *Provider* (6)
carry 290 of the book's 308 annual clicks between them. Add a short "where this
goes next" line to each, pointing at the site page from the map above. No banner and no apology on
these four: they are current, and the link is an invitation rather than a warning. **This is the
cheapest high-value change available to the project**, and it is the one
[S7](tasks.md#s--search-and-agent-discoverability) refers to.

**B-3 — add the dated note to the twelve stale chapters.** One short block at the top of each, naming
the constructs it predates and linking its row in the map above. Hand-written per chapter rather than
generated: mdBook has no banner mechanism, and a preprocessor would be site machinery for a one-off.

**B-4 — fix `HasCgpProvider` in the three chapters that only carry that.** `consumer-provider-link`,
`provider-delegation`, and `debugging-support` are otherwise sound, and the name is dead rather than
merely dated. Check whether the replacement compiles against the 0.4.0 pin before attempting it; if it
does not, these three keep the B-3 note instead and nothing is lost.

**B-5 — retire the unwritten table of contents.** Delete the 28 destinationless entries from
`SUMMARY.md` and the 22 unreferenced stub files, and replace the affected sections with a short note
pointing at the site. A table of contents advertising 28 chapters that will never be written
misrepresents the book to every reader who opens it, and the stub files are leftovers that nothing
references — `create-missing = false` means mdBook will not generate them, not that it needs them.

**B-6 — decide the book's standing line, once.** The website, the crate README, and the book's own
introduction each describe the book's status in their own words, and all three currently say some
version of "not recently updated". One sentence should be settled and used in all three, and it should
distinguish the current chapters from the stale ones rather than tarring both. This is a
[communication-strategy](../communication-strategy/README.md) decision in the project voice, and it
belongs with whoever writes [S7](tasks.md#s--search-and-agent-discoverability).

## What must not happen

**Do not redirect the book to the site.** It would discard 308 clicks a year and the project's
strongest position on its best term, in exchange for pages that have no search history at all.

**Do not bump the `cgp` pin without rewriting the twelve chapters in the same change.** CI compiles
every snippet, so a bump turns the whole book red and the failure is not incremental to repair.

**Do not fix a stale chapter by deleting it.** The ideas in the error-handling and field-accessor
chapters are the fullest treatment the project has ever written of those subjects, and the site's pages
are shorter by design. A dated note preserves the explanation while disowning the syntax.

**Do not write the unwritten chapters.** They belong to the site now, and the decision above is what
stops the two properties competing.

**Do not link the book into this knowledge base.** The [one-way link rule](AGENTS.md#the-one-way-link-rule)
covers every public property, not only contextgeneric.dev.

## Maintaining it

Revisit this document when the `v0.8.0` branch merges, since the routing map's destinations go live
then and B-1 and B-3 become doable; when a new Search Console export is taken, since the concentration
of the book's traffic is the premise of the whole plan and a shift in it would change the ordering; and
if the book is ever revived, in which case the "annotate and route" decision is reopened and this
document is replaced by a section.

Record `cgp-patterns` in [sibling-projects.md](../sibling-projects.md) as the book's checkout, and keep
the chapter inventory above in step with `content/SUMMARY.md` — it is the part most easily left behind,
and the part the plan rests on.
