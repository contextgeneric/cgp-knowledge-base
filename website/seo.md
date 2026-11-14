# Search and agent discoverability

This document is the CGP website's **search strategy**: what twelve months of Google Search Console
data say about how the site is found, which terms it can honestly win, how the v0.8.0 relaunch is
shaped so its new pages are found, and how the same material reaches coding agents. Its central
finding is that the site is shown and not chosen, so a page's title and description are the levers,
not its rank.

It is a **specification**, in the sense [README.md](README.md#two-kinds-of-document-here) draws.
[information-architecture.md](information-architecture.md) decides which pages exist and where a
reader goes next; this document decides how a reader who is not on the site arrives.

## What this document owns, and what it must not touch

**Search visibility is a question of placement, not of wording.** The communication strategy settles
every public claim: [identity.md](../communication-strategy/identity.md) owns the tag line, the frame,
the headline features, and
[the naming rule](../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page);
[vocabulary.md](../communication-strategy/vocabulary.md) owns the terms; and
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) owns the rules for a
page's title and opening. This document decides where that wording is placed: which page owns which
question, what goes in a title tag and a meta description, and what the surfaces outside the site
carry.

Three standing rules bind it, and a recommendation that breaks one is a defect here:

- **Honesty is the strategy.** The techniques make real content findable. Keyword-stuffed copy, pages
  written to catch a query, and claims about search performance beyond the data are excluded.
- **The site stays a stock Docusaurus installation.** Every recommendation is front matter, Markdown,
  static files, or configuration already present; the one accepted addition,
  [Algolia DocSearch](#the-decisions-this-needs), is the author's decision, as
  [site.md](site.md#how-the-site-is-built) requires.
- **The site never links into this knowledge base outside its two sanctioned surfaces**, under the
  [one-way link rule](AGENTS.md#the-one-way-link-rule), including from a machine-read file such as
  `llms.txt`.

## What was measured

**The data is a Google Search Console performance export for 2025-09-19 to 2026-09-18**, Web search,
for a domain property that includes `patterns.contextgeneric.dev` and the `www` host. The raw export
stays out of this repository under the rule in
[readers.md](../communication-strategy/readers.md#keeping-the-model-observed). Two limits apply:

- **The query table is capped at 1,000 rows**, which account for 12,266 of the property's 130,836
  impressions, so about nine impressions in ten cannot be inspected.
- **The tables disagree by aggregation**: the Pages table totals 980 clicks against 130,836
  impressions, the Devices and daily tables 970 against 121,685. Site-wide rates use the daily table,
  per-page figures the Pages table, and neither is reconciled.

The site was checked against the repository and the live site on 2026-09-21. On 2026-11-08 the
`v0.8.0` branch holds 378 Markdown sources, 18 of them the published skill pages, and its build lists
393 sitemap URLs; the difference is the pages Docusaurus generates without a source.

**Only Google is measured**, so every claim here is about Google unless it says otherwise; the
[hand check](#repeating-the-hand-check) on other engines has not been made. **Check a hand search
against the export before acting on it:** searches by hand suggested the site failed to rank for its
name, missed blanket implementations, and lost traffic in the February 2026 migration, and the export
contradicts all three.

## The diagnosis

The findings below, ordered by what they cost, show a presentation problem rather than a ranking
one, and the stale blog posts that rank are the one place search success does harm.

### The site is shown constantly and clicked rarely

**The property drew 121,685 impressions and 970 clicks over twelve months, a click-through rate of
0.80%.** May 2026 alone contributed 40,568 impressions at 0.21% and position 17.1, Google briefly
showing the site for queries it does not answer. **Excluding May, the year runs at 1.09%** (886 clicks
against 81,117 impressions), and 1.09% is the baseline the work is measured against. Average position
was 13.07 on desktop, which carries 110,290 impressions, and 8.22 on mobile.

The failure concentrates in the longest posts, while the front page converts at five times the
average at a similar position:

| Page | Impressions | Clicks | CTR | Position |
|---|---|---|---|---|
| `/blog/extensible-datatypes-part-4/` | 7,894 | 6 | 0.08% | 14.3 |
| `/blog/extensible-datatypes-part-2/` | 11,340 | 10 | 0.09% | 14.3 |
| `/blog/cgp-serde-release/` | 7,499 | 10 | 0.13% | 16.8 |
| `/blog/rustlab-2025-coherence/` | 5,111 | 7 | 0.14% | 10.3 |
| `/blog/hypershell-release/` | 21,194 | 186 | 0.88% | 12.8 |
| `/` | 7,874 | 307 | 3.90% | 8.9 |

That is **a presentation problem rather than a ranking problem**: pages with a clear title and a real
description are chosen. Clicks also concentrate: the front page (307) and the patterns book's
blanket-implementations chapter (237) are 55% of the Pages table's 980.

### Derived descriptions made the worst snippets

**A page without a `description` in its front matter gets one derived from its first line of
Markdown**, which on a reference page was a heading made mostly of punctuation and on a blog post a
sentence such as *"This is the second part of the blog series"*. On 2026-09-21 only 13 of 278 sources
set one.

**Six pages still render a derived description**: Resources, Contribute, Hello World, and the three
area-calculation pages. Each shows the first source line of its opening paragraph, cut mid-sentence
where the source wraps. The published skill pages are not the site's to edit. The conventions,
including the YAML apostrophe that fails the build, are in
[the reference guide](writing-guides/reference.md#conventions-the-port-must-follow).

A post's description is metadata rather than a claim, so writing one does not reach the
[dated-artifact rule](AGENTS.md#do-not-rewrite-history); the wording rules that keep it from implying
currency are in [blog/README.md](blog/README.md#publication-conventions). A description does not rank
a page; it supplies the snippet a reader judges before clicking.

### The longest titles are truncated before they say anything

**A result shows roughly the first 60 characters**, and titles ran to 161 characters on 2026-09-21,
the longest on the posts with the worst click-through rates. Published posts keep their titles under
the [dated-artifact rule](AGENTS.md#do-not-rewrite-history). A new page avoids the problem with a
front-matter `title`, which can differ from its heading, under
[the title rules](#titles-and-descriptions-are-the-per-page-levers-and-docusaurus-separates-them).

### The pages that rank are the pages that have gone stale

**The blog is 61 of the 110 pages with impressions, 90,978 of the impressions, and 336 of the clicks;
the whole `docs/` tree is 19 pages, 2,624 impressions, and 18 clicks.** The four extensible-datatypes
posts alone carry 41,746 impressions, and every one predates `#[cgp_impl]`, `#[implicit]`, and the
`open` statement, so here search success does harm; [blog/README.md](blog/README.md#reading-the-drift-at-a-glance)
records the drift. The live [Introduction](pages/introduction.md) still calls the blog the most
up-to-date resource. The `v0.8.0` branch rewrites it, but a reader from a search result may never pass
through the Introduction, since
[most readers do not arrive at the homepage](information-architecture.md#most-readers-do-not-arrive-at-the-homepage).

### Five dead URLs still draw impressions into 404s

**The Zola-to-Docusaurus migration moved every documentation URL under `/docs/` and left nothing at
the old addresses**: `/overview/`, `/tutorials/hello/`, `/resources/`, `/contribute/`, and `/tutorials/`
drew 1,934 impressions and 10 clicks a year at positions 6.5 to 8, and each returned 404 on
2026-09-21. The blog's URLs survived unchanged.

The `v0.8.0` branch carries seven static stubs under `static/`, one for each of these paths and for
the dead feed paths `/feed/` and `/atom`, each with a canonical link and a meta refresh. GitHub Pages
cannot issue a 301, so a stub is all that is available without a plugin; they reach readers at the
merge. The `www` host redirects correctly.

### The name is won, and the acronym is unwinnable

**The site ranks first for its own name, which has almost no volume**: *context generic programming*
at position 1.1 and 46.6%, *cgp rust* at 1.3 and 37.5%, 112 impressions together in a year against
805 for *rust blanket implementation* alone. **The acronym is a different product's**: *cgp* drew 736
impressions and no clicks at position 12.0, and queries containing it total 1,698 impressions at
1.4%, against 16.7% for the full term, because *cgp zero* and similar queries look for another CGP.

**The site title is `CGP — Context-Generic Programming`, at the author's decision**, so every page
renders as `{Page} | CGP — Context-Generic Programming`, with the acronym where truncation leaves it.
This document recommended against it; what it buys is that a reader who searched *cgp rust* sees the
term they typed. Since the suffix carries the acronym, a page's own title does not repeat it, except
on a page whose subject is CGP itself, such as the disclosure page and the published skill.

**Roughly 2,900 impressions a year go to queries the site cannot serve**, such as *generic
programming* (970 impressions, one click), *v0*, *implicit*, *serde*, and *rust context*, so the
impression total overstates the site's reach.

### The off-site metadata is under-set

**The crate manifests are set**: `homepage` points at the site, and five keywords and the
`rust-patterns` and `no-std` categories, inherited from `[workspace.package]`, place every publishable
crate in crates.io's and lib.rs's browse surfaces.

**What remains needs repository settings, which only the author can change.** Read on GitHub on
2026-11-08:

- **The `cgp` repository's description reads "Context-Generic Programming: modular programming
  paradigm for Rust"**, the framing
  [identity.md](../communication-strategy/identity.md#using-modular-as-a-supporting-word) retires. Its
  topics are `functional-programming`, `modular-programming`, and `rust`.
- **`cargo-cgp`, `cgp-examples`, and `contextgeneric.dev` have no description.** `cgp-skills`
  describes itself as "Prompts and instructions for LLM-assisted coding for CGP" rather than as CGP's
  agent skill, the name
  [vocabulary.md](../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each)
  gives it.
- **No member repository other than `cgp` has topics**, and of the others only `cgp-serde` sets a
  homepage, its release post rather than its Projects pages.

**The front page names the project first, at the author's decision.** Its title is
*Context-Generic Programming (CGP) - Pluggable trait implementations for Rust*, with no site-name
suffix: the page sets the tag and `og:title` with `@docusaurus/Head`, because passing `title` to
`Layout` renders `{title} | {siteTitle}`. Its description opens with the settled tag line verbatim.
The page is recorded in [pages/front-page.md](pages/front-page.md).

### The pages that would answer the high-intent queries are not published yet

**The site appears for the vocabulary the strategy targets, at good positions, and converts none of
it**: *rust coherence* drew 24 impressions and no clicks at position 8.0, and *rust conflicting
implementations of trait*, *rust trait orphan rule*, and *rust dependency injection* are the same. A
small count means the query is rare or the site ranks too low to be seen; the export cannot say which.
The pages that answer them, `/docs/concepts/coherence` and `/docs/reference/`, exist only on the
`v0.8.0` branch, which is why the relaunch is the first real attempt to make the documentation
findable.

## The strategy

### What good would look like

**The name and the blanket-implementation family already rank, so the targets are about being
chosen.** Each is an outcome a later export can confirm:

- **Click-through rate rises from 1.09% toward the front page's 3.9%** at unchanged position. This is
  the single measurable target, and it needs no ranking change.
- **The `docs/` tree stops being a rounding error**, from eighteen clicks a year against the blog's
  336.
- **A reader searching the problem rather than the project** (conflicting implementations, `E0119`,
  compile-time dependency injection, a foreign trait for a foreign type) **finds a page that answers
  it.**
- **A reader arriving from any of those searches lands on a current page**, not a 2025 post teaching
  `#[cgp_context]`.

None sets a date or predicts a volume, and
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search)'s rule against
unmeasured search claims binds the rest.

### Raise the click-through rate before trying to raise the rank

**This is the strategy's organizing decision.** At 81,117 impressions and 1.09% outside May, much of
the site's visibility is wasted, and recovering it needs no links, authority, or ranking change: only
a title a reader can parse and a description that says what the page is for. **Not every impression
is winnable**: the 2,900 a year from queries the site cannot answer stay unclicked whatever the
title, so the target is a better rate, not a multiple of today's traffic. The per-page title and
description work is therefore the main work; the redirect stubs, the off-site metadata, and the agent
surfaces are worthwhile but smaller.

### The relaunch is the event, and it only happens once

**The site goes from 40 published URLs to several hundred, nearly all new, and Google crawls each in
the state it merges in**; on the blog's evidence, that first title and description stay for years. So
every recommendation is cheaper before the merge. **The relaunch is URL-additive**: the existing
documentation paths are unchanged and
[information-architecture.md](information-architecture.md#the-target-page-inventory) keeps the
Overview where it is, so the only broken history is the migration's, which the stubs repair.

### The patterns book is the best-performing property, not a competitor

**The book earns 308 clicks from 19 pages; the main site earns 672 from 91.** Its
blanket-implementations chapter, at 12,232 impressions, 237 clicks, and position 6.8, is the most
successful page in the property. [patterns-book.md](patterns-book.md) holds its record and plan. Three
consequences follow:

- **Do not redirect it or fold it into the site.** It works, and no page would inherit its readers.
- **Link it forward.** Its blanket-implementations chapter offers the current page for the same idea,
  B-1 in [patterns-book.md](patterns-book.md#the-work-in-order), the cheapest high-value link
  available.
- **Read it as evidence about titles.** A chapter called *Blanket Implementations* wins *rust blanket
  implementation*.

**docs.rs and lib.rs** rightly win part of *cgp rust* for a reader who wants an API listing, and the
crate's `homepage` routes that reader to the site. **`maybevoid.com/projects/cgp/`**, the author's
older site, appears for the full term; what happens to it is
[the author's call](#the-decisions-this-needs).

### Own the name by saying it where it means something

**The [naming rule](../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page)
places the name for the reader, not for search.** Each page other than the skill pages and the
published posts names Context-Generic Programming once in its opening paragraph, linked to the
Introduction, so a reader from a search result knows what the page belongs to. The name already ranks
first, so the search benefit is a by-product. It is **one mention, not a density target**, in a
sentence written for the page's explanation.

### The tag line orients the reader; the features carry the searchable words

**The settled tag line is not a keyword asset.** It answers *what is this*, and almost nobody types it:
the branded queries total 112 impressions a year. Never rewrite it for search or repeat it for
density. The short form the naming rule asks for, such as "CGP enables pluggable trait
implementations in Rust", tells the reader what CGP adds and carries no query.

**The five headline features are where searchable language legitimately lives**, because each names a
problem someone types. This mapping is the strategy's core: the features are
[identity.md](../communication-strategy/identity.md#the-headline-feature-set)'s set in its order, the
middle column the query family each can honestly answer, and the right the page that owns it.

| Headline feature | The query family it answers | Measured volume | The page that owns it |
|---|---|---|---|
| One Interface, Many Implementations | conflicting implementations, `E0119`, overlapping impls | not yet ranking | `docs/concepts/coherence` |
| Zero-Cost Abstraction | static dispatch versus `dyn`, avoiding vtables | not yet ranking | `docs/comparisons/dynamic-dispatch` |
| Type-Safe Wiring | compile-time dependency injection, DI without a container | not yet ranking | `docs/comparisons/dependency-injection` |
| Abstract Over Every Dependency | abstract error type, generic over the runtime, `no_std` core | not yet ranking | `docs/concepts/modular-error-handling` |
| Still Ordinary Rust | blanket implementation, extension trait | **1,781 impressions/yr, position 4–5** | `docs/concepts/coherence`, the glossary |

**The blanket-implementation family is the proven one**: six variants total 1,781 impressions and
106 clicks at positions 4.0 to 5.1. The Concepts page and the glossary entry inherit it rather than
compete with the book for it. Three more families have owners: **the orphan rule and the newtype
dance** belong to `docs/concepts/coherence`; **the comparison vocabulary** (type classes, ML modules,
implicit parameters, algebraic effects, policy-based design) to the comparison pages; and **`rust
dsl`**, 771 impressions and 25 clicks at position 7.0 plus 314 for its variants, to the index of the
[Hypershell project section](projects/hypershell.md).

**One page per question**: where two pages could answer a query, one answers it and the other links,
as [the base's link rule](../AGENTS.md#writing-links) already applies to explanations.

### Comparisons are the most valuable unproven pages on the site

**The eleven comparison pages are CGP's best untested search asset.** A reader searching "Rust type
classes" or "dependency injection in Rust without a framework" has a specific, low-competition,
high-intent question, and the site carries a long, sourced page for each. Their guide requires what
makes such a page rank: a `description`, and
[a title in the compared concept's own name](writing-guides/related-work.md#placement-navigation-and-bookkeeping),
because that reader arrives with a vocabulary rather than a problem. They are also the pages most
likely to be quoted elsewhere, the only link-building the project should do, so protect them.

### Titles and descriptions are the per-page levers, and Docusaurus separates them

Two mechanics, verified against Docusaurus's documentation on 2026-09-21, settle how the work is done:

- **A page's front-matter `title` sets the metadata and can differ from its heading.** Docusaurus
  inserts a title only when the Markdown has no heading, so a page keeping its `#[cgp_component]`
  heading can carry a `title` written for a search result. `sidebar_label` stays separate and is
  [plain text without backticks](writing-guides/reference.md#conventions-the-port-must-follow).
- **A page's front-matter `description` sets both `meta name="description"` and `og:description`**,
  and falls back to the first line of content when omitted.

Four rules keep the writing tractable:

- **Keep the title under roughly 60 characters**, with the distinguishing word first.
- **Reference and construct pages get the construct name plus its job**, name first.
- **Concept and tutorial pages get problem-oriented titles**, as
  [formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) prescribes.
- **Every description is a sentence about that page, written once, not a template**; a generic one
  tells the reader nothing, and the engine replaces it with a fragment of the text.

### Adding a page is almost never the answer, and the data says which three cases to consider

**A new page is justified when a reader arriving on a query has a question the site answers and no
page owns, never by query volume alone**, as [What must never be done](#what-must-never-be-done) sets.
The three clusters with real traffic get three answers:

- **Blanket implementations (25 queries, 2,019 impressions, 110 clicks, position 5.8) need no new
  page.** The [book's chapter](https://patterns.contextgeneric.dev/blanket-implementations.html) wins
  the query, `docs/concepts/coherence` answers the question behind it, and the glossary hands the term
  to the Rust Reference. The work is two changes: the chapter links forward (B-1 in
  [patterns-book.md](patterns-book.md#the-work-in-order)), and the coherence page carries a title in
  the reader's words, *blanket implementation* rather than `E0119`, which draws 11 impressions against
  2,019. A standalone "what is a blanket implementation" page would re-teach Rust, which the
  [reference guide](writing-guides/reference.md#linking-three-destinations-and-one-prohibition) rules
  out, and break the [Concepts section's one-to-one mirroring](pages/concepts.md).
- **Domain-specific languages (20 queries, 1,432 impressions, 36 clicks, position 7.7) have a page
  planned, and it should come sooner.** The Hypershell post wins *rust dsl* and converts at 3.2%, but
  *shell scripting vs rust* and its variants, 293 impressions, earn no clicks. That is the strongest
  evidence for writing the [Hypershell section](projects/hypershell.md) first among the libraries,
  with its comparison with shell scripts.
- **The context cluster is a watch item, not a page.** *rust context* draws 453 impressions at
  position 7.1 and 0.44%, for readers the export cannot identify; only *rust context pattern* (11
  impressions, 3 clicks, position 4.0) suggests CGP is relevant. Decide at the next export.

**Nothing else in the data supports a page**: the serde, comparison-vocabulary, provider-pattern, and
macro clusters sit at positions 24 to 36 with no clicks, partly because the pages that answer them are
unpublished.

### The internal linking is already right, and it is doing more work than usual here

**Internal links are how a crawler finds a page nothing external links to, which is nearly every page
the relaunch adds**, and Google's
[guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) still counts
it among the fundamentals. The redesign provides it, and a later change must not undo it: the sidebar
is generated from the directory tree, every reference page closes with *Related constructs* and *The
ideas behind it*, Concepts pages route into Comparisons, many pages link the glossary, and the section
indexes are hand-written. **Link with the words the destination is about**, never "here" or "this
page".

## Coding agents are the second audience

**An agent finds CGP through surfaces other than a search engine, and CGP is better placed there
than its search performance suggests.** Two channels behave differently.

**Retrieval at coding time** serves an agent that must write correct CGP:

- **docs.rs**, the default for any Rust crate. Every publishable `cgp` library crate warns on a missing
  doc comment and CI fails on warnings, each construct's rustdoc links its website page, and the crate
  README routes readers to the site.
- **Context7**, which carried CGP as `/contextgeneric/cgp` with 528 snippets on 2026-09-21, drawn
  from the repository, with the retired "modular programming paradigm" line as its description. A
  `context7.json` in the repository controls what is indexed, and the entry can be resubmitted.
- **The published agent skill**, which needs no work; [cgp-skills](https://github.com/contextgeneric/cgp-skills)
  is published on the site and on GitHub.
- **The knowledge base**, which a user points an agent at; the site's
  [knowledge-base pages](pages/knowledge-base.md) teach that use, so it needs no discoverability work
  beyond them.
- **The site itself**, fetched directly, which is why the
  [named opening](#own-the-name-by-saying-it-where-it-means-something) and one page per question
  matter for an agent too.

**Model priors** form from GitHub, published writing, and forum discussion, which the site cannot
configure. The only practice is the project's existing one: publish, be cited, and keep the vocabulary
stable, which [vocabulary.md](../communication-strategy/vocabulary.md) enforces.

### `llms.txt`, and why it is worth a file but not an argument

**Almost nothing reads it.** Ahrefs analysed 137,210 domains in May 2026: 28% publish an `llms.txt`,
97% of those files received no traffic that month, and 96% of the requests that arrived came from
bots. Google's
[guidance on generative AI features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
states that Google Search does not use it, and no major model provider has committed to reading it.

**So the case for one is agent convenience, not visibility**: a cheap map of the site's sections for
an agent already there. If it is published, it is generated from the sidebar, links only public
pages, is advertised nowhere, and is never presented as a ranking technique.

## What was checked and is not worth acting on

Three things were examined and deliberately left alone:

- **Structured data.** Google's AI features need no schema.org markup, and a documentation site has no
  eligible rich-result type; a proposal to add JSON-LD should say what result it expects.
- **The generated listing pages.** The blog index, archive, author and tag listings, category indexes,
  and their pagination are navigational on a site of a few hundred pages and cost nothing; the
  sitemap plugin excludes anything marked `noindex` if that changes.
- **Page performance.** The site is statically generated, ships almost no JavaScript beyond the
  landing page, and enables `@docusaurus/faster`.

## What must never be done

Five techniques are excluded, each by a rule the project already holds:

- **No keyword stuffing, and no page written to catch a query.** Repeating the name, the tag line, or
  its short form for density is stuffing too; the
  [naming rule](../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page) asks
  for one mention of each.
- **No rewriting the tag line, the feature titles, or a construct's name for search.**
  [identity.md](../communication-strategy/identity.md) owns that wording.
- **No claim about search performance beyond what the export shows.** It covers Google only, its query
  table is capped, and a rise after a change does not prove the change caused it.
- **No bulk-generated pages.** The site discloses its AI assistance; generating pages to occupy
  queries is the line between documentation and spam.
- **No site machinery added quietly.** A plugin or third-party service is the author's decision, as
  [Algolia DocSearch](#the-decisions-this-needs) was.

## Measurement

**Search Console is in place, and it is not analytics**: it places no script on the site, sees no
visitor, and reports only what Google knows about its own index, so the stock-Docusaurus policy is
untouched. [evidence.md](../communication-strategy/evidence.md#what-the-search-data-shows-about-demand)
summarizes the export for the communication strategy. Bing Webmaster Tools works the same way, is not
set up, and would be the only view of Bing and the engines built on its index.

Four signals are worth watching, each tied to a target in
[What good would look like](#what-good-would-look-like):

- **Site-wide CTR at constant position**, against the 1.09% baseline rather than the raw 0.80%,
  checking a later period for its own anomaly first.
- **Clicks to `/docs/`**, eighteen a year against the blog's 336.
- **Clicks on the problem queries** (*rust coherence*, conflicting implementations, dependency
  injection), at zero against 41 impressions.
- **Whether the dead URLs stop appearing** once the stubs reach the live site.

**Establish the baseline before the relaunch merges**, because a before-and-after taken across it
cannot be attributed: export on the merge day, keep the raw files outside this repository, and
summarize the change here.

**IndexNow** submits changed URLs to Bing and the engines sharing its index through a key file at the
site root and a ping per URL. That matters because
[Kagi builds its results](https://help.kagi.com/kagi/search-details/search-sources.html) from its own
crawler plus the major providers. It is a build step rather than a plugin, worth nothing until the
relaunch has something new to announce.

### Repeating the hand check

Search Console covers Google alone, so the other engines are checked by hand. Search
**"Context-Generic Programming"**, **"CGP Rust"**, **"rust blanket implementation"**, **"rust
conflicting implementations E0119"**, **"rust compile time dependency injection"**, and **"rust type
classes"** on Bing and Kagi; record the position of any `contextgeneric.dev` or
`patterns.contextgeneric.dev` result and the exact title shown for it; and note which other CGP
property appears instead. Record the date and the engine beside each finding, and put anything that
changes the guidance into this document rather than into a log.

## The work, in order

**The click-through work comes first, because presentation is what the site is losing on.** Every
reference, comparison, tooling, project, AI, and Concepts page and every blog post carries a written
description, and every construct's reference page and both concept pages that needed one carry a
search-facing title. The six pages that still render a derived description each get one in the same
edit as the page's [named opening](#own-the-name-by-saying-it-where-it-means-something), before the
merge fixes its first impression.

**The metadata repairs are done except the GitHub repository settings**, which only the author can
change. The crate manifests are set, and the redirect stubs, `robots.txt`, and the site and
front-page titles reach readers at the merge.

**The agent surfaces and the hand check follow, and neither blocks anything**: a `context7.json` in
the `cgp` repository, an optional `llms.txt`, and the hand check on Bing and Kagi.

**The relaunch-day submission is the only item that cannot be done early**: confirming that the live
sitemap lists every URL and taking a Search Console export as the baseline, which belongs on the
release checklist in
[writing-guides/release-announcement.md](writing-guides/release-announcement.md#publishing-and-what-happens-afterwards)
beside re-pinning the tutorials' `cgp` version. DocSearch follows the relaunch.

## The decisions this needs

Two decisions are taken, and two remain open:

- **Algolia DocSearch is accepted, for after the relaunch.** Several hundred pages need a search, and
  DocSearch is free for open-source documentation and ships inside `preset-classic`; it needs a
  DocSearch application and a configuration block.
- **Search Console is in place.**
- **Bing Webmaster Tools is open**, for the same reasons as Search Console.
- **`maybevoid.com/projects/cgp/` is open**: whether the author's older site redirects, links forward,
  or stays. It belongs to the author alone, and nothing waits on it.

## Keeping this document current

**Measurements expire**: every figure carries the export or the date it came from, and a re-check
replaces the finding rather than appending to it, per
[document-the-present](../AGENTS.md#document-the-present-not-the-history). **Techniques expire faster**,
so re-read a recommendation that rests on a cited study against its source before acting on it again.
Revisit the document when the relaunch merges, when a new export is taken, when a section is added to
the site, and when a hand check on another engine disagrees with Google's data.
