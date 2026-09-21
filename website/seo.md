# Search and agent discoverability

This document is the CGP website's **SEO strategy**: why the site currently ranks badly for its own
name, which search terms it can realistically win, how the v0.8.0 relaunch should be shaped so that
the new pages are found, and how the same material reaches the coding agents that are now a second
audience for it.

It is a **specification** rather than a page record, in the sense
[README.md](README.md#two-kinds-of-document-here) draws: it describes what should be true of the site
rather than what is true of one page today. It sits beside
[information-architecture.md](information-architecture.md) — that document decides which pages exist
and where a reader goes next, and this one decides how a reader who is not already on the site ever
arrives.

## What this document owns, and what it must not touch

**Search visibility here is a question of placement, not of wording.** The wording of every public
claim is already settled elsewhere and is not reopened for search: the tag line, the frame, and the
headline features belong to
[identity.md](../communication-strategy/identity.md), the terms belong to
[vocabulary.md](../communication-strategy/vocabulary.md), and the titles-and-search rules for a page
already exist in
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search). This document
decides where that settled wording is *placed* — which page owns which question, what goes in a
title tag, what goes in a meta description, which first paragraph orients a reader who arrived from a
search result — and it covers the surfaces outside the site that the communication strategy does not
reach at all.

Three of the base's standing rules bind it especially tightly, and a recommendation that breaks one
is a defect in this document rather than a trade worth making.

**Honesty is the strategy**, unchanged. The techniques below are the ones that work by making the
site's real content findable. Keyword-stuffed copy, pages written to catch a query rather than to
answer it, and claims about search traffic the project does not measure are all excluded, the last by
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) specifically.

**The site stays a stock Docusaurus installation.** Everything recommended below as work is front
matter, Markdown, static files, or configuration already present. Two proposals would cross that
line, and both are flagged as [decisions for the author](#the-decisions-this-needs) rather than
applied — per [site-structure.md](site-structure.md#how-the-site-is-built), an agent adding site
machinery is working against a stated policy.

**The site may still never link into this knowledge base.** Nothing here changes the
[one-way link rule](AGENTS.md#the-one-way-link-rule), including for a file such as `llms.txt` that is
written for machines.

## What was measured, and what was not

Every claim below about the site itself was checked against the repository and the live site on
**2026-09-21**, and those checks are reproducible: the live URLs were fetched over HTTP, the metadata
was read out of the built HTML under `build/`, and the counts were taken over the `docs/` and `blog/`
trees on the `v0.8.0` branch. Three denominators recur below and they are not the same number: **278**
Markdown sources under `docs/` and `blog/`, **291** built HTML pages, and **292** sitemap URLs. The
difference is the pages Docusaurus generates without a source file — the front page, the blog index
and its pagination, the tag and author listings, and three category indexes. The external sources
cited below — Google's guidance on generative AI
features, the Ahrefs study, Kagi's account of its own sources, and Context7's submission
documentation — were read on the same day.

The **ranking observations are weaker evidence and must be read as such.** They come from a single
search index — the one available to the agent that wrote this document — on 2026-09-21. Bing,
DuckDuckGo, and Mojeek all refused automated queries (a geographic redirect that did not carry the
query, a CAPTCHA, and an HTTP 403 respectively), and Kagi requires a subscription, so none of them
was checked. A manual check across Google, Bing, and Kagi is therefore **work this document does not
do**, listed as [S1](#the-work-in-order), and the method for it is in
[Repeating the measurement](#repeating-the-measurement). Treat the rankings below as one index's view
that happens to agree with what the author already observed, not as a measurement of the web.

## The diagnosis

Seven findings explain the current state. The first is larger than the rest together, and it is not
the one the project's own diagnosis started from; the two after it are the ones that are cheapest to
repair. The last two are constraints to work within rather than defects to fix.

### The migration dropped the documentation half of the site out of the index

**The Zola-to-Docusaurus migration moved every documentation URL under `/docs/` and left nothing
behind at the old addresses, so the pages search engines still have on file now return 404.** The
site's pre-migration URLs are recoverable from the Internet Archive, and each one was fetched on
2026-09-21:

| Pre-migration URL | Status today | Current address |
|---|---|---|
| `/overview/` | 404 | `/docs/overview` |
| `/tutorials/` | 404 | `/docs/tutorials/hello` |
| `/tutorials/hello/` | 404 | `/docs/tutorials/hello` |
| `/contribute/` | 404 | `/docs/contribute` |
| `/resources/` | 404 | `/docs/resources` |
| `/feed/` | 404 | `/blog/rss.xml` |
| `/atom` | 404 | `/blog/atom.xml` |

That this is not a historical curiosity is the important part: a site-restricted search on
2026-09-21 returned `contextgeneric.dev/tutorials/hello/` and `contextgeneric.dev/overview/` as
current results, so those dead URLs are what an index still holds and what a reader following a
search result still lands on. **Every blog URL survived the migration unchanged**, which is the
control that makes the diagnosis legible: the blog kept its history and is what ranks, the
documentation lost its history and does not.

The repair is seven static HTML files under `static/`, each carrying a canonical link and a meta
refresh to the new address. GitHub Pages cannot issue a 301, so a static stub is the whole of what is
available without adding a plugin, and it is what the official redirects plugin would generate
anyway.

### The homepage's title tag sells the framing the project retired

The built homepage carries
`<title>Modular programming paradigm for Rust | Context-Generic Programming</title>`, because
`src/pages/index.tsx` passes the configured `tagline` as the page's own title and Docusaurus appends
the site title after it. The strongest single piece of metadata the site has therefore leads with the
words [identity.md](../communication-strategy/identity.md#using-modular-as-a-supporting-word)
specifically retires, and pushes the project's actual name to the end of a line that search results
truncate.

[C1](tasks.md#c--corrections) replaces the configured tagline, so it repairs the title tag as a side
effect — which is worth knowing, because C1 has been carried as a cosmetic correction and it is not
one. Two things it does not repair sit in the same file: the homepage's `<meta name="description">`,
which is hand-written and repeats the retired line, and the choice to use the tagline as the title at
all, which [F1](tasks.md#f--the-front-page) should make deliberately rather than inherit.

### The full term appears as boilerplate rather than as content

The author's hypothesis is right in substance and worth stating precisely, because the precise
version changes the fix. **The term "Context-Generic Programming" appears in every page's title tag
and navigation bar, and in the body prose of 11 of the site's 278 pages.** It is present in the
rendered HTML of all of them, and absent from the part of the page that carries meaning.

Navigation and title furniture is weak evidence of what a page is about, precisely because it is
identical on every page of the site, so a name that appears only there is a name the site has never
actually used. The fix is not to add the term to 267 pages. It is to enforce a rule the
communication strategy already carries —
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search)
requires every page to orient an unfamiliar reader in its first paragraph, with a short description
of CGP and a link to an introduction, because a reader may arrive from anywhere. The
[Comparisons](site-structure.md#comparisons) pages do this correctly and were written most recently;
the [Reference](site-structure.md#reference) pages mostly do not. Enforcing it is both the reader fix
and the search fix, which is the only kind of SEO work this document endorses.

### Most pages have no description, and some have a broken one

**Only 13 of 278 source pages set a `description` in their front matter, and the descriptions
Docusaurus derives for the rest are frequently useless.** Docusaurus falls back to the first line of
Markdown content, which on a reference page is a heading made mostly of punctuation. Sixty of the 291
built pages carry a missing or under-50-character description, and the failures are not subtle:

- `docs/reference/macros/cgp_component` → ``[cgp_component]` ``
- `docs/reference/macros/cgp_provider` → ``[cgpprovider] & #[cgpnew_provider]` ``
- `docs/reference/types/mref` → `'A`

Per section, `description` coverage is 12 of 12 on Comparisons, 1 of 199 on Reference, 0 of 19 on
Concepts, and 0 of 17 on the blog. The pattern is chronological rather than accidental: the
Comparisons guide requires a `description` and the others do not, so the section written last is the
only one that has them.

A description does not rank a page. It supplies the snippet a human reads before deciding to click,
and a snippet reading ``[cgp_component]` `` is a page nobody clicks.

### The acronym is unwinnable, and "CGP Rust" is the branded query

A search for **CGP** alone returned, in order: a UK educational publisher, the US Government
Publishing Office's catalog, Wikipedia's disambiguation page, a police corps, an EPA construction
permit, and a charitable-giving association. Nothing Rust-related appeared. That competition is
decades old and institutional, and no amount of on-site work moves it.

**"CGP Rust" is the query to own, and the site does not own it either.** On that query the results
were led by `docs.rs/cgp`, two `lib.rs` crate pages, a third-party Medium article, and the GitHub
repository, with `contextgeneric.dev` eighth and the patterns book ninth. On the full term
**"Context-Generic Programming"** the homepage ranked *last* of nine results, behind the GitHub
repository, the same Medium article, a Lobsters thread, Wikipedia's *Generic programming*, an
unrelated arXiv paper on *Context-Oriented Programming*, and the author's own older site at
`maybevoid.com`.

Two things follow. The project's other properties are not competitors but they are absorbing the
attention, which makes the [off-site metadata](#the-off-site-metadata-is-under-set) below a lever
rather than a tidy-up. And the near-miss of *Context-Oriented Programming* — a real, older,
unrelated paradigm — is a permanent fact about the name that the site cannot rank its way out of; it
can only be answered by the name and the plain descriptor always travelling together, which
[identity.md](../communication-strategy/identity.md#why-each-word-of-the-line-is-there) already
requires.

### The off-site metadata is under-set

The surfaces that currently outrank the site are ones the project controls, and their metadata is
thin. Checked on 2026-09-21:

- **The `cgp` crate sets no `homepage`**, so neither crates.io nor lib.rs links
  `contextgeneric.dev` at all. Those are high-authority pages with 103,133 total downloads behind
  them, and the link is one line of `Cargo.toml`.
- **It sets one keyword, `cgp`**, of the five crates.io permits, and **no `categories`**, which are
  what place a crate in the browse-and-recommend surfaces of crates.io and lib.rs.
- **The GitHub repository's description still reads "Context-Generic Programming: modular programming
  paradigm for Rust"** — the retired line again, on the property that currently outranks the site for
  the site's own name, with 248 stars behind it. Its topics are `functional-programming`,
  `modular-programming`, `rust`.
- **Every other repository in the organization has no description, no homepage, and no topics** —
  including `cargo-cgp`, `cgp-skills`, `cgp-knowledge-base`, and `contextgeneric.dev`.

None of this is website work, which is the only reason it has gone unowned. It is also the cheapest
work on the list.

### The pages that would answer the high-intent queries are not published yet

Searches for the questions CGP actually answers — conflicting implementations and `E0119`, compile-time
dependency injection in Rust, implementing a foreign trait for a foreign type, blanket
implementations — returned no `contextgeneric.dev` result on any of them. On "rust blanket
implementation" the third result was the independently written
[greyblake article](https://www.greyblake.com/blog/alternative-blanket-implementations-for-single-rust-trait/)
that [evidence.md](../communication-strategy/evidence.md) already cites as proof developers hand-roll
CGP's pattern, and the sixth was a file inside a pull request against the `cgp-patterns` repository.

The reason is simple and temporary: **those pages exist only on the `v0.8.0` branch.**
`/docs/concepts/coherence` and `/docs/reference/` both return 404 on the live site today. The live
site publishes 40 URLs; the branch builds 292. The material that would win these queries is written
and unpublished, which makes the relaunch the whole opportunity.

## The strategy

### What good would look like

**The target is stated in queries rather than in positions, because positions are not something this
project can promise itself.** Four outcomes would mean the work below succeeded, and each is
checkable by hand in a minute:

- A search for **"Context-Generic Programming"** returns `contextgeneric.dev` first, rather than
  ninth behind an unrelated arXiv paper.
- A search for **"CGP Rust"** returns the site above `docs.rs` and `lib.rs`, which currently carry a
  reader who wanted the documentation to an API listing that the project itself describes as thin.
- A reader who searches the **problem** rather than the project — conflicting implementations,
  `E0119`, compile-time dependency injection in Rust, implementing a foreign trait for a foreign
  type — finds a page on the site that answers it, where today none of those queries returns one.
- A reader who lands on the site from any of those searches **arrives on a page that is current**,
  which today is not what happens; see the next section but one.

Nothing here sets a date or a volume, and no claim below should acquire one:
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) forbids asserting
search traffic the project does not measure, and the project does not measure it.

### The relaunch is the event, and it only happens once

**The site is about to go from 40 published URLs to roughly 292, all of them new.** Nothing about
that is reversible cheaply: the pages will be crawled in the state they merge in, the first
impressions of each will be formed from the title and description they carry that day, and a page
that publishes with a broken snippet keeps it until someone notices. Every recommendation below is
therefore cheaper before the merge than after, and the ordering in [The work](#the-work-in-order)
reflects that.

One property of the relaunch is worth stating because it removes a risk that would otherwise dominate
this document: **it is URL-additive.** The existing documentation paths — `/docs/overview`,
`/docs/contribute`, `/docs/resources`, `/docs/tutorials/hello` — are unchanged by the redesign, and
[information-architecture.md](information-architecture.md#the-target-page-inventory) settled that the
Overview stays where it is rather than moving. The one page that moves is *Project status*, which is
being lifted out of the Introduction and has never had a URL of its own. So the relaunch adds history
rather than breaking it, and the only broken history is the migration's, which
[S2](#the-work-in-order) repairs.

### The pages that rank are the pages that have gone stale

**The site's best-ranking pages teach syntax the compiler no longer accepts, and that is the one place
where search success is currently doing harm.** It follows directly from the migration: the blog kept
its URLs and its history, so the blog is what an index has, and
[blog/README.md](blog/README.md#reading-the-drift-at-a-glance) records that of seventeen posts, eight
write every provider inside-out, seven show the removed `#[cgp_context]`, and four use the removed
`Async` trait. A site-restricted search for CGP's own central idea returned the v0.4.0 release post
third, and that post teaches presets and `#[cgp_context]`, both of which the library has since
removed.

The live [Introduction](site-structure.md#introduction) makes it worse by telling readers that "the
most accurate and up-to-date resources concerning CGP are currently available in the form of our blog
posts", which was true before the tutorials existed. That sentence is already rewritten on the
`v0.8.0` branch, so the internal routing is fixed; **what the branch cannot fix is a reader who
arrives from a search result and never passes through the Introduction at all**, which
[information-architecture.md](information-architecture.md#most-readers-do-not-arrive-at-the-homepage)
establishes is most of them.

Three things follow, and only the first is unambiguously this document's to recommend. **The relaunch
is the remedy**, because the Concepts and Reference pages are written to answer the same questions
and can take those queries over once they exist — which is another reason the metadata work below is
worth doing before the merge rather than after. **The sanctioned deep-dive pointer helps where it
applies**: [AGENTS.md](AGENTS.md#do-not-rewrite-history) already settles that a published post gains a
pointer to the deep dive that supersedes it, and that pointer is exactly what a reader arriving from a
search result needs. And **annotating the remaining stale posts is the author's decision, not an
agent's** — the same rule allows a short dated note at the top of a post that is heavily read and
actively misleading, and the release posts are the clearest candidates, but nothing here should treat
that as a default.

### The site is not competing with itself, but it looks like it is

**Four other surfaces rank for CGP's terms, all of them the project's own, and the strategy is to
route rather than to compete.** Each should answer the question it is best at and hand the reader
forward to the canonical page for everything else.

- **The [patterns book](https://patterns.contextgeneric.dev/)** ranks for "blanket implementation"
  and other teaching terms, and the site itself describes it as not recently updated. It teaches from
  first principles without reference to the crate's constructs, which is a real job no other property
  does — so it stays, and what it needs is a forward link from each chapter to the current page for
  that term. That is a change in the `cgp-patterns` repository.
- **`docs.rs` and `lib.rs`** win "CGP Rust" today and will keep winning some of it, which is correct
  for a reader who wants an API listing. Setting the crate's `homepage`, per
  [the off-site finding](#the-off-site-metadata-is-under-set), is what turns that result into a route
  to the site instead of a dead end.
- **`maybevoid.com/projects/cgp/`**, the author's own older site, ranked seventh for the full term —
  above `contextgeneric.dev`. Whether it redirects, links forward, or stays as it is, is the author's
  call; it is listed here because it is the one competing property nobody would think to check.
- **The published agent skill** duplicates the `cgp-skills` repository by design, and
  [AGENTS.md](AGENTS.md#the-agent-skill-is-published-as-a-snapshot) states the reason as search
  visibility — so that a developer looking for the skill finds it on the project's own site. That is
  a deliberate acceptance of duplicate content across two domains, the cost is that a search engine
  picks one of them, and the decision has already been taken and needs no revisiting here.

### Own the name by saying it where it means something

The rule is one sentence: **every page's first paragraph names Context-Generic Programming once, in
prose, and links the Introduction.** This is already required by
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) for reader reasons,
it is what the Comparisons pages already do, and it is the single highest-value sweep available
because it converts 267 pages from boilerplate-only to content-bearing on the project's own name.

Two constraints keep it honest. It is **one mention, not a density target** — a second is a reader
cost with no search benefit. And the sentence is the settled descriptor from
[identity.md](../communication-strategy/identity.md#the-tag-line) or a short paraphrase of it, not a
line written to catch a query; the Comparisons pages' opening is the model, and every reference page
already carries a similar obligation in the [`context` gloss](site-structure.md#conventions-the-port-must-follow).

### The tag line is positioning; the features are the search surface

**The settled tag line is not a keyword asset and must not be turned into one.** "A language
extension for Rust, with pluggable trait implementations at compile-time" answers *what is this*, and
it is what a reader needs on arrival. But almost nobody types it: it contains no error code, no
problem, and no alternative technology's name, and the three words carrying real search demand in it
— Rust, trait, compile-time — are among the most contested in the language's documentation. Rewriting
it for search would trade the project's message discipline for nothing, and
[identity.md](../communication-strategy/identity.md#the-tag-line) forbids inventing a new descriptor
per piece anyway.

**The five headline features are where searchable language legitimately lives**, because each one is
a problem someone types into a search box, and each already has a page that owns it. The mapping
below is the strategy's core: the left column is the settled feature wording from
[identity.md](../communication-strategy/identity.md#the-headline-feature-set), the middle is the
query family it can honestly answer, and the right is the page that should rank for it.

| Headline feature | The query family it answers | The page that owns it |
|---|---|---|
| One Interface, Many Implementations | conflicting implementations, `E0119`, overlapping impls, one trait many implementations | `docs/concepts/coherence` |
| Zero-Cost Abstraction | static dispatch versus `dyn`, zero-cost dependency injection, avoiding vtables | `docs/comparisons/dynamic-dispatch` |
| Type-Safe Wiring | compile-time dependency injection in Rust, DI without a container or reflection | `docs/comparisons/dependency-injection` |
| Abstract Over Every Dependency | abstract error type, generic over the runtime, keeping a core `no_std`-friendly | `docs/concepts/modular-error-handling` |
| Still Ordinary Rust | blanket implementation, extension trait, adopting a pattern incrementally | `docs/concepts/coherence`, the glossary |

Two further families have no feature to hang off and matter as much. **The orphan rule and the
newtype dance** — implementing a foreign trait for a foreign type — is the second-best opening the
[message](../communication-strategy/message.md#the-problems-cgp-removes) offers and belongs to
`docs/concepts/coherence` alongside the first. And **the comparison vocabulary** — type classes, ML
modules, implicit parameters, algebraic effects, policy-based design — is a family of eleven queries
the site now answers and nothing else in Rust does.

The discipline this table imposes is **one page per question**. Where two pages could answer a query,
one of them should answer it and the other should link, which is the same rule
[AGENTS.md](../AGENTS.md#writing-links) already applies to explanations and is what keeps two pages
from competing for one result.

### Comparisons are the most valuable pages on the site

**The eleven comparison pages are the best SEO asset CGP has, and they were built for a different
reason entirely.** A reader searching "Rust type classes" or "dependency injection in Rust without a
framework" has a specific, low-competition, high-intent question, and the site now carries a long,
sourced, honestly-argued page for each. Their guide already requires the two things that make such a
page rank and keep ranking: a `description` in the front matter, and
[a title in the compared concept's own name](writing-guides/related-work.md#placement-navigation-and-bookkeeping)
rather than a problem-oriented one, because that reader arrives with a vocabulary rather than a
problem.

The practical consequence is that this section needs nothing done to it and should be protected. When
the [section where the other tool wins](writing-guides/related-work.md#the-page-shape) survives the
author's read, it is also the section most likely to be quoted by someone else, which is the only
form of link-building the project should ever do.

### Titles and descriptions are the per-page levers, and Docusaurus separates them

Two mechanics settle how this is done, both verified against Docusaurus's own documentation on
2026-09-21.

**A page's front-matter `title` sets the metadata and can differ from its heading.** Docusaurus
inserts a title at the top of a document only when the Markdown has no heading of its own, so a page
that keeps its `#[cgp_component]` heading can carry a `title` written for a search result. That
is the lever the reference section needs: the heading a reader wants when they already know the name,
and a title tag that says what the construct is for when they do not. `sidebar_label` remains
separate and unchanged — it is [plain text and carries no
backticks](site-structure.md#conventions-the-port-must-follow).

**A page's front-matter `description` sets both `meta name="description"` and `og:description`**, and
falls back to the first line of content when omitted, which is what produces the broken snippets
above. It is one line per page and there is no substitute for writing it.

Three rules make the sweep tractable across 291 pages. **Reference and construct pages get the
construct name plus its job**, keeping the name first because that is what the reader searched.
**Concept and tutorial pages get problem-oriented titles**, which
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) already prescribes.
And **every description is a sentence about the page, written once, not a template** — a description
that could belong to any page tells a reader nothing and will simply be replaced by the engine with
a fragment of the text.

### Repair the terms the project has already half-won

Two terms are already working and neither points at the site. **"Blanket implementation"** surfaces
the patterns book and a pull-request file from `cgp-patterns`, while the glossary at
`docs/reference/glossary` has an anchored definition for it that nothing outside the site links —
and that will not be reachable at all until the branch merges. **"Coherence"** and **"orphan rule"** are answered on the site by
`docs/concepts/coherence`, whose title — *Bypassing coherence* — does not contain the words a reader
in trouble types, which are "conflicting implementations" and `E0119`.

The fix for both is a title and description that use the reader's words while the heading keeps the
project's, which is exactly what the mechanic above allows. The
[patterns book](https://patterns.contextgeneric.dev/) is a separate property and ranks on its own; it
should link forward to the site's current page for each term it covers, which is a change in that
repository rather than this one.

### The internal linking is already right, and it is doing more work than usual here

**Internal links are how a crawler finds a page that nothing external links to, which describes every
page the relaunch adds.** Google's own
[guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) puts
findability through internal links among the fundamentals that still apply, and on this site it is
close to the only mechanism available: 235 of the 292 URLs will publish with no inbound link from
anywhere on the web.

The redesign has already done this work for other reasons, and the effect is worth naming so that a
later change does not undo it. The sidebar is autogenerated from the directory tree, so no page is
orphaned. Every reference page closes with *Related constructs* and a *The ideas behind it* list
into Concepts. Fourteen Concepts pages route into Comparisons. The glossary sweep added 289 links
across 136 pages. Both section indexes are hand-written rather than generated, which means the
highest-level pages actually say what is beneath them.

The one rule to hold is the one the base already applies to prose: **link with the words the
destination is about**, not with "here" or "this page", because the anchor text is the clearest
signal a linking page gives about what it is pointing at.

## Coding agents are the second audience

**An agent writing Rust does not use a search engine the way a person does, so the surfaces that
reach it are different ones, and CGP is better placed than its search ranking suggests.** Two
channels matter and they behave differently.

**Retrieval at coding time** is what an agent does when it has already been told to use CGP, or has
found it, and needs to write correct code. Four surfaces serve it today:

- **docs.rs** is the default surface for any Rust crate, and CGP's is weak by the project's own
  admission — it reports 50% of the crate documented, and the crate README tells readers the
  constructs are "still mostly undocumented within Rustdoc". [X2](tasks.md#x--cross-cutting) already
  owns fixing the README; the rustdoc gap behind it is larger and is the project's own call.
- **Context7** already carries CGP as `/contextgeneric/cgp` with 528 indexed snippets, drawn from the
  repository rather than from the website, and its description repeats the retired "modular
  programming paradigm" line. A `context7.json` in the repository controls which folders are indexed,
  and the entry can be resubmitted so that the description and the indexed material match the
  library's current state.
- **The published agent skill** is CGP's genuine differentiator here and needs no work: a project
  that ships a skill teaching an assistant its vocabulary, idioms, and diagnostics is answering this
  audience directly, and [cgp-skills](https://github.com/contextgeneric/cgp-skills) is already
  published on the site and on GitHub.
- **The site itself**, fetched directly, which is why the [first-paragraph rule](#own-the-name-by-saying-it-where-it-means-something)
  and one-page-per-question matter as much for an agent as for a person: both are answering "is this
  page about the thing I asked".

**Model priors** are what an agent knows before it reads anything, and they are formed from GitHub,
published writing, and forum discussion rather than from anything the site can configure. There is no
technique here, only the project's existing practice: publish, be cited, and keep the vocabulary
stable so that the same words describe the same things across every surface. Message discipline,
which [vocabulary.md](../communication-strategy/vocabulary.md) already enforces for readers, turns out
to be the mechanism that makes a model's recall of CGP consistent too.

### `llms.txt`, and why it is worth a file but not an argument

**The evidence is that almost nothing reads it.** Ahrefs analysed 137,210 domains in May 2026 and
found that 28% publish an `llms.txt`, that **97% of those files received zero traffic that month**,
and that 96% of the requests which did arrive came from bots rather than people. The sample is sites
using Ahrefs' own analytics, so it is skewed toward the search-aware end of the web — which makes the
finding stronger rather than weaker, since those are the sites most likely to have published the file
deliberately. Google's own
[guidance on optimizing for generative AI features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
states that Google Search does not use `llms.txt` or other special markup of that kind, and no major
model provider has committed to reading it.

**So the honest case for publishing one is agent convenience, not visibility.** A single file listing
the site's sections with one line each costs almost nothing, is trivially regenerable, and gives an
agent that has already reached the site a map of 292 pages without crawling them. That is a real
benefit to a real user. What it is not is a ranking technique, and a recommendation that presented it
as one would be exactly the kind of claim this project does not make. If it is published, it is
generated from the sidebar rather than hand-maintained, it links only public pages, and nothing on
the site advertises it.

## What was checked and is not worth acting on

Three things a reader of this document would reasonably raise were examined and deliberately left
alone. Recording them is cheaper than having each one re-opened.

**Structured data.** Google states that no special schema.org markup is required for its AI features,
and a documentation site has no eligible rich-result type to gain from adding any. There is nothing
to do here, and a future proposal to add JSON-LD should be asked what result it expects.

**The thirteen generated listing pages.** The sitemap carries `/blog`, `/blog/archive`,
`/blog/authors`, the tag listings, three category indexes, and their pagination. They duplicate
content that exists elsewhere, which on a large site is worth pruning. On a 292-page site it is not:
they are navigational, they cost nothing, and Docusaurus's sitemap plugin already excludes anything
marked `noindex` if that ever changes.

**Page performance.** The site is statically generated, ships almost no JavaScript beyond the
landing page, and already enables `@docusaurus/faster`. Performance is not among this site's
problems, and the stock-Docusaurus policy is what keeps it that way.

## What must never be done

Five techniques are excluded, and each is excluded by a rule the project already holds rather than by
taste.

**No keyword stuffing, and no page written to catch a query.** The site's pages exist because a
reader needs them, and a page that exists because a query exists is the thing every search engine's
guidelines and this project's own honesty rule both rule out.

**No rewriting the tag line, the feature titles, or a construct's name for search.**
[identity.md](../communication-strategy/identity.md) owns that wording, and message discipline across
surfaces is worth more than any single query.

**No claim about search traffic the project does not measure.** This is already
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search)'s rule, and it binds
this document too: nothing here asserts a volume, a ranking change, or a conversion.

**No bulk-generated pages.** The site is already written with AI assistance and discloses it; the
line between that and generating pages to occupy queries is the line between documentation and spam,
and it is not a line the project should test.

**No site machinery added quietly.** A plugin, an analytics script, or a third-party search service
is a decision for the author, and the two candidates are in the next section rather than in the work
list.

## Measurement, without becoming a site that tracks people

**The project cannot tell whether any of this worked, and the reason is a decision rather than an
oversight.** [evidence.md](../communication-strategy/evidence.md) records search data as unavailable
because the site has no analytics and adding them would reopen the stock-Docusaurus policy.

**Search Console and Bing Webmaster Tools are not analytics, and the distinction is the whole
point.** Neither places a script on the site, neither sees a visitor, and neither changes what a
reader loads: both report what the search engine already knows about its own index — which queries
showed a page, which pages are indexed, which are excluded and why. Verification is a static file in
`static/` or a DNS record, so the stock-Docusaurus policy is untouched. For a site whose central
diagnosis above is *"the index still holds URLs that 404"*, this is also the only instrument that
would have caught the problem.

Adopting either is the author's call, listed below. If it is adopted, the
[evidence.md](../communication-strategy/evidence.md) entry saying search data is unavailable becomes
wrong in the same change, per the
[synchronization rule](../AGENTS.md#the-synchronization-rule).

**IndexNow** is the adjacent mechanism worth knowing about: a key file at the site root plus a ping
per changed URL submits to Bing and the engines sharing its index, which matters for CGP because
[Kagi builds its results](https://help.kagi.com/kagi/search-details/search-sources.html) from its own
Teclis crawler plus API calls to the major providers. It is a build-step change rather than a plugin,
and it is worth nothing until the relaunch has something new to announce.

### Repeating the measurement

The ranking half of this document should be re-checked by hand, because it was not verifiable
automatically. The method is: search **"Context-Generic Programming"**, **"CGP Rust"**, **"rust
blanket implementation"**, **"rust conflicting implementations E0119"**, **"rust compile time
dependency injection"**, and **"rust type classes"** on Google, Bing, and Kagi; record the position of
any `contextgeneric.dev` result and the exact title shown for it; and note which other CGP property
appears instead. Record the date and the engine beside each finding, and put anything that changes the
guidance into this document rather than into a log.

## The work, in order

Ten items, ordered so that the cheap repairs land before the relaunch carries them. They are
proposed as a task group and are **not yet in [tasks.md](tasks.md)**, which uses single-letter IDs
and would need a new `S` group; adding them there is a planning decision for the author rather than
something this document should do unilaterally.

- **S1 — check the rankings by hand**, per [the method above](#repeating-the-measurement). Everything
  else here is worth doing regardless of the result, so this does not block anything; it exists so the
  document's weakest evidence gets replaced by the author's own.
- **S2 — the seven redirect stubs.** Static HTML under `static/`, one per
  [dead pre-migration URL](#the-migration-dropped-the-documentation-half-of-the-site-out-of-the-index),
  each with a canonical link and a meta refresh. *Lands in:* the website repository. The largest single
  recovery available and the only item here that is repairing damage rather than adding reach.
- **S3 — a `description` on every page.** One line of front matter per page, starting with the 60
  pages whose derived description is missing or broken, and with the reference group, where coverage is
  1 in 199. *Lands in:* `docs/`, `blog/`.
- **S4 — a search-facing `title` on the pages whose heading is a construct name.** Keeps the `h1` and
  the `sidebar_label` as they are, per
  [the mechanic above](#titles-and-descriptions-are-the-per-page-levers-and-docusaurus-separates-them).
  *Lands in:* `docs/reference/`, and the concept pages whose title does not use the reader's words —
  *Bypassing coherence* above all.
- **S5 — the first-paragraph orientation sweep**, naming CGP once in prose with a link to the
  Introduction on every page that does not already. Reader work first, search work second.
- **S6 — the homepage's own metadata.** The hand-written description in `src/pages/index.tsx` is
  outside [C1](tasks.md#c--corrections)'s scope and carries the retired line; it is fixed with the
  rest of the front page in [F1](tasks.md#f--the-front-page).
- **S7 — the off-site metadata.** Set `homepage`, expand `keywords` to five, and add `categories` in
  the `cgp` crate's manifest; replace the GitHub repository description with the settled line and widen
  its topics; give the sibling repositories a description and a homepage. *Lands in:* the
  [`cgp`](https://github.com/contextgeneric/cgp) repository and the organization's GitHub settings.
  Cheapest item on the list, and the only one that touches the properties currently outranking the
  site.
- **S8 — `robots.txt` and the sitemap declaration.** The site serves no `robots.txt` today, so nothing
  points a crawler at `/sitemap.xml`. *Lands in:* `static/robots.txt`.
- **S9 — the relaunch-day submission.** On the day the branch merges: confirm `/sitemap.xml` serves
  all 292 URLs, submit it wherever the
  [measurement decision](#the-decisions-this-needs) lands, and ping IndexNow if it is adopted. This is
  the one item that cannot be done early, and the one most easily forgotten because everything around
  it is finished by then.
- **S10 — the agent surfaces.** A `context7.json` in the `cgp` repository and a resubmission so the
  indexed description matches the current one; optionally an `llms.txt` generated from the sidebar, on
  the [stated grounds](#llmstxt-and-why-it-is-worth-a-file-but-not-an-argument) and no others.

Three of these overlap work already planned and should be folded into it rather than done twice: S6
belongs to F1, S7 belongs beside [X2](tasks.md#x--cross-cutting), and S3 and S4 are cheapest done per
section while someone is already in it. One of them belongs on a different list entirely: S9 is a
release-checklist item, and the release checklist is the one in
[writing-guides/release-announcement.md](writing-guides/release-announcement.md#publishing-and-what-happens-afterwards)
that already carries re-pinning the tutorials' `cgp` version.

## The decisions this needs

Three questions are the author's rather than an agent's, and none of them blocks the work above.

**Whether to verify the site with Search Console and Bing Webmaster Tools.** The argument is
[above](#measurement-without-becoming-a-site-that-tracks-people): no script, no visitor data, no
plugin, and the only instrument that would have caught the 404s. The cost is a relationship with two
search companies and a static verification file.

**Whether to add site search.** The relaunch publishes roughly 292 pages with no way to search them.
Algolia DocSearch is free for open-source documentation and ships inside `preset-classic` rather than
as an added plugin, but it is a third-party service on every page, which is the part that needs a
decision.

**Whether to adopt the `S` task group** in [tasks.md](tasks.md), or to fold these items into the
existing groups and drop the numbering.

## Keeping this document current

This document goes stale in two ways, and they need different responses. **Its measurements expire**:
every ranking and count above carries the date it was taken, and a re-check replaces the finding
rather than appending to it, per
[document-the-present](../AGENTS.md#document-the-present-not-the-history). **Its techniques expire
faster than most of this base's subject matter**, because search engines change and the surfaces
agents read are two years old at most — so a recommendation that rests on a cited study should be
re-read against its source before it is acted on a second time, and one that rests on a vendor's
practice should be checked against that vendor's current documentation.

Revisit it when the relaunch merges, which is when most of the work above either happened or did not;
when a new section is added to the site, since one page per question is the rule it has to fit; and
when the author's hand-checked rankings disagree with what is recorded here, in which case the
author's check wins and this document is corrected.
