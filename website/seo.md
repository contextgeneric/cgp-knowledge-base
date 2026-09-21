# Search and agent discoverability

This document is the CGP website's **SEO strategy**: what twelve months of Google Search Console data
say about how the site is actually found, which search terms it can realistically win, how the v0.8.0
relaunch should be shaped so that the new pages are found, and how the same material reaches the
coding agents that are now a second audience for it.

It is a **specification** rather than a page record, in the sense
[README.md](README.md#two-kinds-of-document-here) draws: it describes what should be true of the site
rather than what is true of one page today. It sits beside
[information-architecture.md](information-architecture.md) — that document decides which pages exist
and where a reader goes next, and this one decides how a reader who is not already on the site ever
arrives.

## What this document owns, and what it must not touch

**Search visibility here is a question of placement, not of wording.** The wording of every public
claim is already settled elsewhere and is not reopened for search: the tag line, the frame, and the
headline features belong to [identity.md](../communication-strategy/identity.md), the terms belong to
[vocabulary.md](../communication-strategy/vocabulary.md), and the titles-and-search rules for a page
already exist in
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search). This document
decides where that settled wording is *placed* — which page owns which question, what goes in a title
tag, what goes in a meta description, which first paragraph orients a reader who arrived from a search
result — and it covers the surfaces outside the site that the communication strategy does not reach at
all.

Three of the base's standing rules bind it especially tightly, and a recommendation that breaks one is
a defect in this document rather than a trade worth making.

**Honesty is the strategy**, unchanged. The techniques below are the ones that work by making the
site's real content findable. Keyword-stuffed copy, pages written to catch a query rather than to
answer it, and claims about search performance beyond what the data shows are all excluded.

**The site stays a stock Docusaurus installation.** Everything recommended below as work is front
matter, Markdown, static files, or configuration already present. The one addition the project has
accepted — [Algolia DocSearch](#the-decisions-this-needs) — is a decision the author has taken rather
than one an agent applied, which is the rule
[site-structure.md](site-structure.md#how-the-site-is-built) sets.

**The site may still never link into this knowledge base.** Nothing here changes the
[one-way link rule](AGENTS.md#the-one-way-link-rule), including for a file such as `llms.txt` that is
written for machines.

## What was measured

**The project has Google Search Console, and this document is written against twelve months of its
data** — a performance export covering **2025-09-19 to 2026-09-18**, Web search, for a domain property
that includes `patterns.contextgeneric.dev` and the `www` host as well as the main site. That export
is the evidence every ranking claim below rests on, and it is worth saying plainly that it replaced an
earlier draft's guesses: several conclusions reached by searching the web by hand were **wrong**, and
are corrected in [the section after this one](#what-the-search-data-overturned).

The export is raw measurement, so it stays out of this repository under the rule in
[readers.md](../communication-strategy/readers.md#keeping-the-model-observed); what belongs here are
the findings. Two limits on it matter when reading the numbers. **The query table is capped at 1,000
rows**, which account for 12,266 of the property's 130,836 impressions, so roughly nine impressions in
ten come from long-tail or anonymized queries that cannot be inspected. And **Search Console's tables
disagree by aggregation** — the Pages table totals 980 clicks against 130,836 impressions where the
Devices and daily tables total 970 against 121,685 — so each figure below is cited with the table it
came from rather than reconciled. Site-wide rates use the daily table; per-page figures use the Pages
table.

Everything about the site itself was checked against the repository and the live site on
**2026-09-21**: the live URLs were fetched over HTTP, the metadata was read out of the built HTML
under `build/`, and the counts were taken over the `docs/` and `blog/` trees on the `v0.8.0` branch.
Three denominators recur and they are not the same number: **278** Markdown sources under `docs/` and
`blog/`, **291** built HTML pages, and **292** sitemap URLs. The difference is the pages Docusaurus
generates without a source file — the front page, the blog index and its pagination, the tag and
author listings, and three category indexes. The external sources cited below were read on the same
day.

**Only Google is measured.** Search Console says nothing about Bing, Kagi, or Brave, so every claim
here is a claim about Google unless it says otherwise, and a hand check on the other engines is
[S1](#the-work-in-order).

## What the search data overturned

Three conclusions reached by searching the web by hand were wrong, and correcting them changes what
the work should be. They are recorded rather than quietly replaced, because the way they went wrong is
the useful part: one search index was treated as the web.

**The site is not failing to rank for its own name. It ranks first, and the name has no volume.** The
query *context generic programming* sits at average position **1.1** with a **46.6% click-through
rate**, and *cgp rust* at position **1.3** with 37.5%. Between them they drew **112 impressions in
twelve months**. The name is already won, and winning it is worth almost nothing.

**The property does rank for the blanket-implementation family, and that family is its largest source
of clicks.** *rust blanket implementation* alone is 805 impressions at position 4.0 for 60 clicks, and
the page earning most of the family is the patterns book's `blanket-implementations.html`: 12,232
impressions, **237 clicks**, position 6.8. That is more clicks than any page on the main site except
the front page.

**The migration did not cost the project its traffic.** Clicks ran at **69 a month in the five months
before** the February 2026 migration and **66 a month in the six months after**. The dead URLs are
real and still draw impressions, but they are a small, cheap repair rather than the dominant problem
an earlier draft of this document claimed.

## The diagnosis

Eight findings explain the current state, ordered by what the data says they cost. The first is the
one the whole strategy turns on, and it is not a ranking problem.

### The site is shown constantly and clicked rarely

**The property drew 121,685 impressions and 970 clicks over twelve months — a click-through rate of
0.80%.** That is the headline number, and it reframes everything: CGP's pages are being *put in front
of people* at scale and are not being chosen. Average position was 13.07 on desktop, which carries
110,290 of those impressions, against 8.22 on mobile.

**One month distorts that figure and the honest version is better.** May 2026 alone contributed 40,568
impressions — a third of the year — at a 0.21% click-through rate and an average position of 17.1,
which is the signature of Google briefly showing the site for a mass of queries it does not answer.
**Excluding May, the year runs at 1.09%**: 886 clicks against 81,117 impressions. Use 1.09% as the
baseline the work below is measured against, and read the annual 0.80% as depressed by an event nobody
controlled.

Per page the failure is stark, and it concentrates in the longest posts:

| Page | Impressions | Clicks | CTR | Position |
|---|---|---|---|---|
| `/blog/extensible-datatypes-part-4/` | 7,894 | 6 | 0.08% | 14.3 |
| `/blog/extensible-datatypes-part-2/` | 11,340 | 10 | 0.09% | 14.3 |
| `/blog/cgp-serde-release/` | 7,499 | 10 | 0.13% | 16.8 |
| `/blog/rustlab-2025-coherence/` | 5,111 | 7 | 0.14% | 10.3 |
| `/blog/hypershell-release/` | 21,194 | 186 | 0.88% | 12.8 |
| `/` | 7,874 | 307 | 3.90% | 8.9 |

The front page converts at five times the site average and the Hypershell post at rather more than the
other long posts, which is the shape of a **presentation problem rather than a ranking problem**: at
roughly the same position, pages with a clear title and a real description are chosen and pages
without one are not. The two findings that follow are the mechanism.

A second reading of the same table matters for the relaunch: **clicks are concentrated in two pages.**
The front page (307) and the patterns book's blanket-implementations chapter (237) are 55% of all 980
clicks. The other 108 pages share the rest.

### Most pages have no description, and some have a broken one

**Only 13 of 278 source pages set a `description` in their front matter, and the descriptions
Docusaurus derives for the rest are frequently useless.** Docusaurus falls back to the first line of
Markdown content, which on a reference page is a heading made mostly of punctuation. Sixty of the 291
built pages carry a missing or under-50-character description, and the failures are not subtle:

- `docs/reference/macros/cgp_component` → ``[cgp_component]` ``
- `docs/reference/macros/cgp_provider` → ``[cgpprovider] & #[cgpnew_provider]` ``
- `docs/reference/types/mref` → `'A`

Per section, `description` coverage was 12 of 12 on Comparisons, 1 of 199 on Reference, 0 of 19 on
Concepts, and 0 of 17 on the blog. The pattern was chronological rather than accidental: the
Comparisons guide requires a `description` and the others do not, so the section written last was the
only one that had them. That gap is now closed where it was doing damage. **Every page under `docs/` renders a usable
description**, except the published skill snapshot, which the site does not own. Fifty-five pages were
written by hand — the `macros/`, `attributes/` and `derives/` groups, plus the fourteen `traits/` and
`types/` pages whose derived description was a bare phrase or, in one case, empty — and three
generated category indexes gained one through their `_category_.json`. The conventions are in
[site-structure.md](site-structure.md#conventions-the-port-must-follow).

**What is left is a smaller thing than it looks.** The remaining pages carry a *derived* description:
their own first sentence, which Docusaurus uses when the front matter omits one. Replacing those with
written sentences is a real gain but a much smaller one than replacing ``[cgp_component]` `` was, and
it is worth spending on the pages that carry impressions rather than uniformly.

**Which is why the blog was done next.** All seventeen posts now carry a written description, because
the blog draws three quarters of the property's impressions and its derived snippets were the worst on
the site: the second extensible-datatypes post, at 11,340 impressions and a 0.09% click-through rate,
advertised itself as *"This is the second part of the blog series… You can read the first part here"*,
and the v0.7.0 post's derived snippet stripped the backticks from its identifiers and offered
`#[cgpfn]`. A post's description is metadata rather than a claim, so writing one does not reach the
[dated-artifact rule](AGENTS.md#do-not-rewrite-history); the wording rules that keep it from implying
currency are in [blog/README.md](blog/README.md#publication-conventions).

A description does not rank a page. It supplies the snippet a human reads before deciding to click, and
at 121,685 impressions a year the snippet is where the site's visibility is being spent.

### The longest titles are truncated before they say anything

Page titles run to **161 characters** at the extreme, against an average of 48. The four longest all
belong to the posts with the worst click-through rates above:

- *CGP v0.5.0 Release: Auto dispatchers, extensible datatype improvements, monadic computation, RTN emulation, modular serde, and more* — 161 characters
- *Programming Extensible Data Types in Rust with CGP - Part 1: Modular App Construction and Extensible Builders* — 139

A search result shows roughly the first 60. A reader scanning ten results sees *"Programming
Extensible Data Types in Rust with CGP - Part 1: Modular…"* and has to work out whether it answers
their question from a fragment that is mostly setup. These are published blog posts, so their titles
are [not rewritten](AGENTS.md#do-not-rewrite-history) — but every page the relaunch adds is a chance
not to repeat it, and a front-matter `title` can differ from a page's heading, which is the lever
[below](#titles-and-descriptions-are-the-per-page-levers-and-docusaurus-separates-them).

### The pages that rank are the pages that have gone stale

**The blog is 61 of the 110 pages with impressions, 90,978 of the impressions, and 336 of the clicks;
the entire `docs/` tree is 19 pages, 2,624 impressions, and 18 clicks.** Search traffic to this project
is, to a first approximation, blog traffic — and
[blog/README.md](blog/README.md#reading-the-drift-at-a-glance) records that of seventeen posts, eight
write every provider inside-out, seven show the removed `#[cgp_context]`, and four use the removed
`Async` trait.

The four extensible-datatypes posts alone carry 41,746 impressions. Every one of them predates
`#[cgp_impl]`, `#[implicit]`, and the `open` statement. **This is the one place where search success is
currently doing harm**, and the live [Introduction](site-structure.md#introduction) compounds it by
telling readers that "the most accurate and up-to-date resources concerning CGP are currently available
in the form of our blog posts". That sentence is already rewritten on the `v0.8.0` branch, so the
internal routing is fixed; what the branch cannot fix is a reader who arrives from a search result and
never passes through the Introduction at all, which
[information-architecture.md](information-architecture.md#most-readers-do-not-arrive-at-the-homepage)
establishes is most of them.

### Five dead URLs still draw impressions into 404s

**The Zola-to-Docusaurus migration moved every documentation URL under `/docs/` and left nothing behind
at the old addresses.** Search Console still records impressions against those addresses, and each was
fetched on 2026-09-21:

| Pre-migration URL | Impressions | Clicks | Position | Status today | Current address |
|---|---|---|---|---|---|
| `/overview/` | 723 | 1 | 7.07 | 404 | `/docs/overview` |
| `/tutorials/hello/` | 495 | 0 | 8.03 | 404 | `/docs/tutorials/hello` |
| `/resources/` | 456 | 4 | 7.29 | 404 | `/docs/resources` |
| `/contribute/` | 236 | 5 | 6.55 | 404 | `/docs/contribute` |
| `/tutorials/` | 24 | 0 | 6.58 | 404 | `/docs/tutorials/hello` |

That is **1,934 impressions and 10 clicks a year landing on a 404**, at positions between 6.5 and 8 —
better positions than most of the site earns. The `www` host adds three more of the same paths at 94
impressions each; `www` itself redirects correctly, so those are the same pre-migration URLs seen under
a second hostname rather than a live duplicate-host problem. The blog's URLs survived the migration
unchanged, which is why the blog kept its history.

The repair is five static HTML files under `static/`, each carrying a canonical link and a meta
refresh. GitHub Pages cannot issue a 301, so a static stub is the whole of what is available without
adding a plugin, and it is what the official redirects plugin would generate anyway. Two feed paths,
`/feed/` and `/atom`, are also dead and cost nothing to stub alongside them.

### The name is won, and the acronym is unwinnable

*context generic programming* is position 1.1 and *cgp rust* is position 1.3, so the branded work is
done. What the data adds is the size of the prize: **112 impressions in a year**, against 805 for
*rust blanket implementation* alone.

The acronym behaves as expected and is worth abandoning explicitly. **`cgp` drew 736 impressions and
zero clicks** at position 12.0, and a hand search returns a UK educational publisher, the US Government
Publishing Office's catalog, and an EPA construction permit. It is shown and never chosen, and no
on-site work changes that.

**The acronym has seven times the impressions of the full term and a twelfth of the intent**, which is
the sharpest way to read this data and the answer to whether the site should chase it. Queries
containing *cgp* are 67 queries, 1,698 impressions and 23 clicks — a 1.4% click-through rate — while
the six queries containing the full term are 245 impressions and 41 clicks, at 16.7%. The composition
explains the gap: *cgp zero*, *char cgp*, *chap cgp*, *chapt cgp*, *zero cgp* and *cgp community
edition* together draw some 430 impressions and **no clicks at all**, because they are people looking
for a different CGP. The acronym queries that do convert, *cgp rust* and *cgp community*, already rank
at 1.3 and 3.8.

**So putting the acronym in the site title would optimize for impressions the site cannot convert, and
it would not display anyway.** Seventy-two of 285 titles already exceed the roughly 60 characters a
result shows, so the site-name suffix is being truncated already; appending `(CGP)` to the end of it
puts the acronym in the first thing cut. On `#[cgp_component] — define a component | Context-Generic
Prog…` it would never appear.

**The author's decision was to put the acronym in the suffix anyway, in the one form that survives
truncation.** The site title is now `CGP — Context-Generic Programming`, so every page renders as
`{Page} | CGP — Context-Generic Programming` and the acronym sits immediately after the separator,
where it is shown rather than cut. The full term follows it, so a search for the full term still
matches even where the display truncates.

That decision was taken against the recommendation above and is recorded as the author's, with the
evidence intact, because the evidence remains what it is: the acronym's volume is mostly a different
product. What the change buys is that a reader searching *cgp rust* or *cgp dsl* sees the term they
typed in every result, which is a click-through argument rather than a matching one.

**It also settled a question it created.** Fifteen reference titles had been given the acronym on the
reasoning that a page's own title is the displayed part — `Symbol! — CGP type-level strings`. With the
suffix carrying it, those rendered the acronym twice in one title, which reads as stuffing rather than
information, so they were reverted. The titles that still carry it twice are the ones whose *subject*
is CGP, such as the disclosure page and the published skill, where the repetition is in the boilerplate
half and the page's own words are meaningful on their own.

Several other high-impression queries are the same phenomenon — the site appearing for something it
does not answer. *generic programming* drew 970 impressions and one click at position 13.4; *v0* 394
and none; *implicit* 238 and none; *serde* 133 and none; *rust context* 453 impressions and two clicks.
**Roughly 2,900 impressions a year are spent on queries the site cannot serve**, which is worth knowing
because it means the impression total overstates the site's real reach.

### The full term appears as boilerplate rather than as content

**The term "Context-Generic Programming" appears in every page's title tag and navigation bar, and in
the body prose of 11 of the site's 278 pages.** It is present in the rendered HTML of all of them, and
absent from the part of the page that carries meaning.

Navigation and title furniture is weak evidence of what a page is about, precisely because it is
identical on every page of the site, so a name that appears only there is a name the site has never
actually used. Given that the name already ranks first, this is **not** the urgent item an earlier
draft made it; it is a reader-orientation obligation that
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) already imposes, and
it earns its place below on that basis rather than on a search one.

### The off-site metadata is under-set

The surfaces that share these queries are ones the project controls, and their metadata was thin. The
crate manifests have since been repaired: `homepage` now points at the site, so crates.io and lib.rs
link it for the first time; the single `cgp` keyword has become five; and the crates carry the
`rust-patterns` and `no-std` categories that place them in the browse-and-recommend surfaces. All 27
published manifests inherit them from `[workspace.package]`.

**What remains needs repository settings rather than a commit**, and only the author can change it:

- **The `cgp` repository's description still reads "Context-Generic Programming: modular programming
  paradigm for Rust"** — the framing
  [identity.md](../communication-strategy/identity.md#using-modular-as-a-supporting-word) retires, on
  the project's most-linked property, with 248 stars behind it. Its topics are `functional-programming`,
  `modular-programming`, `rust`.
- **Every other repository in the organization has no description, no homepage, and no topics** —
  including `cargo-cgp`, `cgp-skills`, `cgp-knowledge-base`, and `contextgeneric.dev`.

The homepage's own metadata was the last of it and is now fixed. It had passed the configured
`tagline` as its page title, which Docusaurus appends the site name to — a 119-character title whose
every distinguishing word fell past what a result shows — and its hand-written description still
carried the retired framing.

**The front page is the one page that names the project first**, at the author's decision: its title
is *Context-Generic Programming (CGP) - Pluggable trait implementations for Rust*, with no site-name
suffix after it. Docusaurus's own formatter cannot produce that — passing `title` to `Layout` renders
`{title} | {siteTitle}`, so the project name could only ever come last — so the page sets the tag
directly with `@docusaurus/Head`, and sets `og:title` with it so a shared link carries the same words.
That is React on the landing page, which is where the
[stock-Docusaurus policy](site-structure.md#how-the-site-is-built) already allows it, and it changes
no other page. The trade is that a result shows roughly the first sixty characters, so the name and
the acronym display in full while the claim after them is cut; on a page that already ranks first for
both branded queries, spending the visible characters on the name is a judgement about recognition
rather than about matching. The description opens with the settled tag line verbatim.

What remains for [F1](tasks.md#f--the-front-page) is the page itself rather than its metadata.

### The pages that would answer the high-intent queries are not published yet

**The site already appears for the vocabulary the strategy targets, at good positions, and converts
none of it.** This corrects a claim made from hand searching, which found no `contextgeneric.dev`
result and concluded there was none:

| Query | Impressions | Clicks | Position |
|---|---|---|---|
| `rust coherence` | 24 | 0 | 8.0 |
| `rust blanket trait implementation` | 23 | 1 | 6.1 |
| `rust conflicting implementations of trait` | 10 | 0 | 11.8 |
| `rust trait orphan rule` | 5 | 0 | 24.0 |
| `rust dependency injection` | 2 | 0 | 6.5 |

Two readings of that table are both available and the export cannot separate them. **Search Console
only records a query where the site actually appeared**, so a small impression count means the site
rarely showed for it — which may be because the query is rare, or because the site ranks too low to be
seen for a common one. Nothing here establishes that few people search for `E0119`; it establishes that
CGP is barely in front of the ones who do.

What is unambiguous is the conversion: **at position 8.0 for *rust coherence*, the site earned zero
clicks all year.** That is the same presentation failure as everywhere else, on exactly the queries the
Concepts pages are written to answer.

The pages that would answer them properly are also **not published yet**: `/docs/concepts/coherence`
and `/docs/reference/` both return 404 on the live site, because they exist only on the `v0.8.0`
branch. The live site publishes 40 URLs; the branch builds 292. The entire `docs/` tree currently earns
18 clicks a year against the blog's 336, so the relaunch is not adding pages to a section that is
already working — it is the first serious attempt to make the documentation half of the site findable
at all.

## The strategy

### What good would look like

**Two of the four targets an earlier draft set were already met, which is itself the finding.** The
name ranks first and the blanket-implementation family ranks fourth. What remains is stated in
outcomes that the Search Console export can actually confirm a year from now:

- **Click-through rate rises from 1.09% toward the front page's 3.9%**, at unchanged position, taking
  the May-excluded figure as the baseline. This is the single measurable target, it is largely within
  the project's control, and nothing about it requires ranking better.
- **The `docs/` tree stops being a rounding error.** Eighteen clicks a year against the blog's 336 is
  the gap the relaunch exists to close.
- **A reader searching the problem rather than the project** — conflicting implementations, `E0119`,
  compile-time dependency injection, foreign trait for a foreign type — **finds a page on the site that
  answers it**, where today none of those queries returns one.
- **A reader arriving from any of those searches lands on a page that is current**, rather than on a
  2025 post teaching `#[cgp_context]`.

Nothing here sets a date or predicts a volume. The export makes it possible to check each of these
against measurement rather than impression, which is new, and
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search)'s rule against
asserting unmeasured search claims still binds everything else.

### Raise the click-through rate before trying to raise the rank

**This is the strategy's organizing decision, and the data supports it — with a ceiling worth stating
in the same breath.** At 81,117 impressions and 1.09% outside the May anomaly, the site's problem is
not only that Google withholds visibility; a large part of the visibility already granted is being
wasted, and recovering it needs no links, no authority, and no ranking change. It needs a title a
reader can parse and a description that says what the page is for.

The ceiling is that **not every impression is winnable.** At least 2,900 impressions a year, in the
visible part of the query table alone, come from queries the site cannot answer — *generic
programming*, *cgp*, *v0*, *serde* — and no title changes those into clicks. The invisible nine tenths
of the impressions almost certainly contain far more of the same. So the target below is a better
click-through rate, not a specific multiple of today's traffic, and a projection of the form "0.80% to
2% would triple it" is arithmetic rather than a forecast.

Everything else in this section is downstream of that. The per-page title and description work is the
main event rather than housekeeping; the relaunch's value is that it adds 235 pages that can start with
both; and the redirect stubs, the off-site metadata, and the agent surfaces are worthwhile but smaller.

### The relaunch is the event, and it only happens once

**The site is about to go from 40 published URLs to roughly 292, all of them new.** The pages will be
crawled in the state they merge in, and the title and description they carry that day is what a reader
sees for as long as nobody revisits them — which, on the evidence of the blog, is years. Every
recommendation below is cheaper before the merge than after.

One property of the relaunch removes a risk that would otherwise dominate this document: **it is
URL-additive.** The existing documentation paths — `/docs/overview`, `/docs/contribute`,
`/docs/resources`, `/docs/tutorials/hello` — are unchanged by the redesign, and
[information-architecture.md](information-architecture.md#the-target-page-inventory) settled that the
Overview stays where it is. The one page that moves is *Project status*, which has never had a URL of
its own. So the relaunch adds history rather than breaking it, and the only broken history is the
migration's, which the seven redirect stubs under `static/` have already repaired.

### The patterns book is the best-performing property, not a competitor

**The book earns 308 clicks from 19 pages; the main site earns 672 from 91.** Per page it outperforms
everything else the project publishes, and its blanket-implementations chapter is the single most
successful page in the whole property. The book's own record and the plan for it are in
[patterns-book.md](patterns-book.md), which is where the chapter-level detail lives. That changes how it should be treated: it is not a stale
property to route around but the one piece of CGP writing that has demonstrably found its audience.

Three consequences follow, and the first is the one to resist. **Do not redirect it or fold it into the
site** — whatever it is doing, it works, and the reference section has no page that would inherit those
readers. **Do link it forward**: a reader landing on the book's blanket-implementations chapter should
be offered the current page for the same idea, which is a change in the `cgp-patterns` repository and
the cheapest high-value link on this list. And **read it as evidence about titles**: a chapter called
*Blanket Implementations* wins a query called *rust blanket implementation*, which is the whole of the
[title argument](#titles-and-descriptions-are-the-per-page-levers-and-docusaurus-separates-them) in one
example.

Two smaller surfaces belong in the same frame. **`docs.rs` and `lib.rs`** win part of *cgp rust* and
should, for a reader who wants an API listing; setting the crate's `homepage` turns that result into a
route to the site. And **`maybevoid.com/projects/cgp/`**, the author's older site, appears on a hand
search for the full term; whether it redirects, links forward, or stays is the author's call, and it is
listed because it is the one competing property nobody would think to check.

### Own the name by saying it where it means something

Every page's first paragraph should name Context-Generic Programming once, in prose, and link the
Introduction. The justification is now a **reader** one rather than a search one, since the name
already ranks first: this is what
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) requires so that a
page arriving cold orients its reader, it is what the Comparisons pages already do, and the search
benefit is a by-product.

The sweep goes wrong in two ways, and both are cheap to avoid. It is **one mention, not a density
target**. And the sentence is the
settled descriptor from [identity.md](../communication-strategy/identity.md#the-tag-line) or a short
paraphrase, not a line written to catch a query.

### The tag line is positioning; the features are the search surface

**The settled tag line is not a keyword asset and must not be turned into one.** "A language extension
for Rust, with pluggable trait implementations at compile-time" answers *what is this*, and it is what
a reader needs on arrival. The data confirms that almost nobody types it or anything like it: the
branded queries together are 112 impressions a year. Rewriting it for search would trade the project's
message discipline for nothing, and
[identity.md](../communication-strategy/identity.md#the-tag-line) forbids inventing a new descriptor
per piece anyway.

**The five headline features are where searchable language legitimately lives**, because each names a
problem someone types, and each already has a page. The mapping below is the strategy's core: the
feature wording is the settled set from
[identity.md](../communication-strategy/identity.md#the-headline-feature-set), the middle column is the
query family it can honestly answer, and the right is the page that should own it. Where the export
shows real volume, it is given.

| Headline feature | The query family it answers | Measured volume | The page that owns it |
|---|---|---|---|
| One Interface, Many Implementations | conflicting implementations, `E0119`, overlapping impls | not yet ranking | `docs/concepts/coherence` |
| Still Ordinary Rust | blanket implementation, extension trait | **1,781 impressions/yr, position 4–5** | `docs/concepts/coherence`, the glossary |
| Type-Safe Wiring | compile-time dependency injection, DI without a container | not yet ranking | `docs/comparisons/dependency-injection` |
| Zero-Cost Abstraction | static dispatch versus `dyn`, avoiding vtables | not yet ranking | `docs/comparisons/dynamic-dispatch` |
| Abstract Over Every Dependency | abstract error type, generic over the runtime, `no_std` core | not yet ranking | `docs/concepts/modular-error-handling` |

**The blanket-implementation family is the proven one and it belongs to "Still Ordinary Rust"**, which
is the feature the strategy added last and for the most defensive reason. Six query variants —
*rust blanket implementation*, *rust blanket impl*, *blanket implementation rust*, *blanket
implementation*, *blanket implementations*, *rust blanket implementations* — total 1,781 impressions
and 106 clicks at positions 4.0 to 5.1. That is the one term where the project is a recognized answer,
and the new Concepts page and glossary entry should be written to inherit it rather than to compete
with the book for it.

Two further families have no feature to hang off and matter as much. **The orphan rule and the newtype
dance** belongs to `docs/concepts/coherence` alongside the first row. And **the comparison vocabulary**
— type classes, ML modules, implicit parameters, algebraic effects, policy-based design — is eleven
queries the site now answers and nothing else in Rust does.

One more family shows in the data and has no page: **`rust dsl` drew 771 impressions and 25 clicks at
position 7.0**, plus *dsl rust* and *dsl in rust* for another 314 impressions. The Hypershell post is
what ranks, and the [Hypershell deep dive](deep-dives/hypershell.md) is the page that should inherit it
when it lands — which is a reason to prefer it over the other two deep dives when capacity appears.

The discipline the table imposes is **one page per question**. Where two pages could answer a query,
one answers it and the other links, which is the same rule
[AGENTS.md](../AGENTS.md#writing-links) already applies to explanations.

### Comparisons are the most valuable unproven pages on the site

**The eleven comparison pages are the best SEO asset CGP has that has not been tested yet.** A reader
searching "Rust type classes" or "dependency injection in Rust without a framework" has a specific,
low-competition, high-intent question, and the site now carries a long, sourced, honestly-argued page
for each. Their guide already requires the two things that make such a page rank and keep ranking: a
`description` in the front matter, and
[a title in the compared concept's own name](writing-guides/related-work.md#placement-navigation-and-bookkeeping)
rather than a problem-oriented one, because that reader arrives with a vocabulary rather than a
problem.

They are also the section most likely to be quoted by someone else, which is the only form of
link-building the project should ever do. The section needs nothing done to it and should be protected.

### Titles and descriptions are the per-page levers, and Docusaurus separates them

Two mechanics settle how the click-through work is done, both verified against Docusaurus's own
documentation on 2026-09-21.

**A page's front-matter `title` sets the metadata and can differ from its heading.** Docusaurus inserts
a title at the top of a document only when the Markdown has no heading of its own, so a page that keeps
its `#[cgp_component]` heading can carry a `title` written for a search result. That is the lever the
reference section needs: the heading a reader wants when they already know the name, and a title tag
that says what the construct is for when they do not. `sidebar_label` remains separate and unchanged —
it is [plain text and carries no backticks](site-structure.md#conventions-the-port-must-follow).

**A page's front-matter `description` sets both `meta name="description"` and `og:description`**, and
falls back to the first line of content when omitted, which is what produces the broken snippets above.
It is one line per page and there is no substitute for writing it.

Writing 291 titles and descriptions is tractable only with rules decided in advance, and these four
are the ones the data supports. **Keep the title under roughly 60 characters**,
which is what a result shows, and put the distinguishing word first. **Reference and construct pages
get the construct name plus its job**, keeping the name first because that is what the reader searched.
**Concept and tutorial pages get problem-oriented titles**, which
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) already prescribes.
And **every description is a sentence about that page, written once, not a template** — a description
that could belong to any page tells a reader nothing and will be replaced by the engine with a fragment
of the text.

### Adding a page is almost never the answer, and the data says which three cases to consider

**The question "should we add a page for the term that works?" has a specific answer here, and for the
biggest term it is no.** The test a new page has to pass is the one
[What must never be done](#what-must-never-be-done) sets: a page is justified when a reader arriving on
that query has a question the site answers and no page owns, never by query volume alone. Applied to
the three query clusters that carry real traffic, it produces three different answers.

**Blanket implementations — 25 queries, 2,019 impressions, 110 clicks, average position 5.8 — needs no
new page.** It is the project's largest non-branded term by a wide margin, and three things already
answer it. The [patterns book's chapter](https://patterns.contextgeneric.dev/blanket-implementations.html)
wins the query today and is the property's best-performing page. `docs/concepts/coherence` is *about*
overlapping blanket implementations and why Rust rejects them, which is precisely the question behind
the query. And the glossary defines the term and hands it to the Rust Reference, which is the site's
standing rule for a Rust concept it does not own.

So the work is to connect what exists rather than to add to it, and it is already on the list in two
places. **The book chapter should link forward** to the current page for the idea, which is the
cheapest high-value link available, is part of [S7](tasks.md#s--search-and-agent-discoverability), and
is specified as B-1 in [patterns-book.md](patterns-book.md#the-work-in-order).
And **the coherence page needs a title carrying the reader's words**, which is
[S4](tasks.md#s--search-and-agent-discoverability) — with one correction to what that task originally
assumed. The words are *blanket implementation*, not `E0119`: the blanket family is 2,019 impressions a
year against 11 for *rust conflicting implementations of trait*. A page arguing that Rust allows only
one blanket implementation per trait can say so in its title honestly, because that is what it argues.

A fourth possibility is worth naming and rejecting. **A standalone "what is a blanket implementation in
Rust" page would be re-teaching Rust**, which the
[reference guide](writing-guides/reference.md#linking-three-destinations-and-one-prohibition) rules out
and the glossary already handles by linking Rust's own documentation. It would also break the
[Concepts section's one-to-one mirroring](site-structure.md#concepts) of the internal catalog, since no
internal concept document covers it. The reader arriving on that query is better served by a page that
answers the question *behind* it.

**Domain-specific languages — 20 queries, 1,432 impressions, 36 clicks, average position 7.7 — has a
page planned and should have it sooner.** The Hypershell post wins *rust dsl* (771 impressions,
position 7.0) and converts at 3.2%, and 293 of those impressions are a comparison intent it serves
badly: *shell scripting vs rust*, *rust vs shell scripting*, and *cargo vs shell scripting* together
earn zero clicks. The owner is the [Hypershell deep dive](deep-dives/hypershell.md), which is
[DD1](tasks.md#d--the-deep-dives-and-the-code-they-quote) and post-release. **This is the strongest
evidence available for doing DD1 before DD2 and DD3**, which is otherwise a free choice, and it is a
reason to give one of its pages the shell-scripting comparison the post's readers are evidently
looking for.

**The context cluster is a watch item, not a page.** *rust context* draws 453 impressions at position
7.1 and converts at 0.44%, and the intent behind it cannot be read from the export: it may be
context-generic programming, an async context, a context object, or something unrelated. The one signal
worth keeping is *rust context pattern* — 11 impressions, 3 clicks, **27% click-through at position
4.0** — which suggests a reader using those words does find CGP relevant. That is a handful of
impressions and no basis for building. Watch it in the next export and decide then.

**Nothing else in the data supports a page.** The serde, comparison-vocabulary, provider-pattern, and
macro clusters each appear at average positions between 24 and 36 with zero clicks, which is the shape
of a site surfacing far down for something it does not answer rather than an opportunity. The
comparison vocabulary is the exception that proves it: those eleven pages exist and are unpublished, so
the queries they will answer cannot show in this export at all.

### The internal linking is already right, and it is doing more work than usual here

**Internal links are how a crawler finds a page that nothing external links to, which describes every
page the relaunch adds.** Google's own
[guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) puts
findability through internal links among the fundamentals that still apply, and on this site it is
close to the only mechanism available: 235 of the 292 URLs will publish with no inbound link from
anywhere on the web.

The redesign has already done this work for other reasons, and the effect is worth naming so a later
change does not undo it. The sidebar is autogenerated from the directory tree, so no page is orphaned.
Every reference page closes with *Related constructs* and a *The ideas behind it* list into Concepts.
Fourteen Concepts pages route into Comparisons. The glossary sweep added 289 links across 136 pages.
Both section indexes are hand-written rather than generated.

The one rule to hold is the one the base already applies to prose: **link with the words the
destination is about**, not with "here" or "this page", because the anchor text is the clearest signal
a linking page gives about what it points at.

## Coding agents are the second audience

**An agent writing Rust does not use a search engine the way a person does, so the surfaces that reach
it are different ones, and CGP is better placed than its search performance suggests.** Two channels
matter and they behave differently.

**Retrieval at coding time** is what an agent does when it has already been told to use CGP, or has
found it, and needs to write correct code. Four surfaces serve it today:

- **docs.rs** is the default surface for any Rust crate, and CGP's is weak by the project's own
  admission — it reports 50% of the crate documented, and the crate README tells readers the constructs
  are "still mostly undocumented within Rustdoc". [X2](tasks.md#x--cross-cutting) already owns fixing
  the README; the rustdoc gap behind it is larger and is the project's own call.
- **Context7** already carries CGP as `/contextgeneric/cgp` with 528 indexed snippets, drawn from the
  repository rather than from the website, and its description repeats the retired "modular programming
  paradigm" line. A `context7.json` in the repository controls which folders are indexed, and the entry
  can be resubmitted so the description and the indexed material match the library's current state.
- **The published agent skill** is CGP's genuine differentiator here and needs no work: a project that
  ships a skill teaching an assistant its vocabulary, idioms, and diagnostics is answering this audience
  directly, and [cgp-skills](https://github.com/contextgeneric/cgp-skills) is already published on the
  site and on GitHub.
- **The site itself**, fetched directly, which is why the
  [first-paragraph rule](#own-the-name-by-saying-it-where-it-means-something) and one-page-per-question
  matter as much for an agent as for a person: both are answering "is this page about the thing I
  asked".

**Model priors** are what an agent knows before it reads anything, and they are formed from GitHub,
published writing, and forum discussion rather than from anything the site can configure. There is no
technique here, only the project's existing practice: publish, be cited, and keep the vocabulary stable
so that the same words describe the same things across every surface. Message discipline, which
[vocabulary.md](../communication-strategy/vocabulary.md) already enforces for readers, turns out to be
the mechanism that makes a model's recall of CGP consistent too.

### `llms.txt`, and why it is worth a file but not an argument

**The evidence is that almost nothing reads it.** Ahrefs analysed 137,210 domains in May 2026 and found
that 28% publish an `llms.txt`, that **97% of those files received zero traffic that month**, and that
96% of the requests which did arrive came from bots rather than people. The sample is sites using
Ahrefs' own analytics, so it is skewed toward the search-aware end of the web — which makes the finding
stronger rather than weaker, since those are the sites most likely to have published the file
deliberately. Google's own
[guidance on optimizing for generative AI features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
states that Google Search does not use `llms.txt` or other special markup of that kind, and no major
model provider has committed to reading it.

**So the honest case for publishing one is agent convenience, not visibility.** A single file listing
the site's sections with one line each costs almost nothing, is trivially regenerable, and gives an
agent that has already reached the site a map of 292 pages without crawling them. That is a real
benefit to a real user. What it is not is a ranking technique, and a recommendation that presented it
as one would be exactly the kind of claim this project does not make. If it is published, it is
generated from the sidebar rather than hand-maintained, it links only public pages, and nothing on the
site advertises it.

## What was checked and is not worth acting on

Three things a reader of this document would reasonably raise were examined and deliberately left
alone. Recording them is cheaper than having each one re-opened.

**Structured data.** Google states that no special schema.org markup is required for its AI features,
and a documentation site has no eligible rich-result type to gain from adding any. There is nothing to
do here, and a future proposal to add JSON-LD should be asked what result it expects.

**The thirteen generated listing pages.** The sitemap carries `/blog`, `/blog/archive`,
`/blog/authors`, the tag listings, three category indexes, and their pagination. They duplicate content
that exists elsewhere, which on a large site is worth pruning. On a 292-page site it is not: they are
navigational, they cost nothing, and Docusaurus's sitemap plugin already excludes anything marked
`noindex` if that ever changes.

**Page performance.** The site is statically generated, ships almost no JavaScript beyond the landing
page, and already enables `@docusaurus/faster`. Performance is not among this site's problems, and the
stock-Docusaurus policy is what keeps it that way.

## What must never be done

Five techniques are excluded, and each by a rule the project already holds rather than by taste.

**No keyword stuffing, and no page written to catch a query.** The site's pages exist because a reader
needs them, and a page that exists because a query exists is what every search engine's guidelines and
this project's own honesty rule both rule out.

**No rewriting the tag line, the feature titles, or a construct's name for search.**
[identity.md](../communication-strategy/identity.md) owns that wording, and message discipline across
surfaces is worth more than any single query.

**No claim about search performance beyond what the export shows.** The data covers Google only, its
query table is capped, and it says nothing about causation; a rise after a change is not proof the
change caused it.

**No bulk-generated pages.** The site is already written with AI assistance and discloses it; the line
between that and generating pages to occupy queries is the line between documentation and spam.

**No site machinery added quietly.** A plugin or a third-party service is a decision for the author,
taken deliberately, as [Algolia DocSearch](#the-decisions-this-needs) was.

## Measurement

**Search Console is in place, so the question is no longer whether to measure but what to watch.**
[evidence.md](../communication-strategy/evidence.md) records search data as unavailable under the
site's no-analytics policy; that entry is now wrong and is corrected in the same change as this
document, per the [synchronization rule](../AGENTS.md#the-synchronization-rule).

The distinction that makes this compatible with the site's posture is worth keeping written down.
**Search Console is not analytics.** It places no script on the site, sees no visitor, and changes
nothing a reader loads: it reports what Google already knows about its own index. Verification is a
static file or a DNS record, so the stock-Docusaurus policy is untouched. The same is true of Bing
Webmaster Tools, which is not yet set up and which would be the only way to see anything about Bing,
Kagi, and the engines built on Bing's index.

Four things are worth watching, and each maps to a target in
[What good would look like](#what-good-would-look-like):

- **Site-wide CTR at constant position.** The one number that says whether the title and description
  work paid off. Take **1.09%** as the baseline, not the raw annual 0.80%, and check whether a future
  period carries its own anomaly before comparing.
- **Clicks to `/docs/`.** Eighteen a year today, against the blog's 336.
- **Clicks on the problem queries** — `rust coherence`, conflicting implementations, dependency
  injection — which stand at zero today against 41 impressions, and which are the clearest test of
  whether the Concepts and Comparisons pages did their job.
- **Whether the dead URLs stop appearing** now that the stubs are in `static/`, which is the check
  that the redirects work.

**Establish the baseline before the relaunch merges**, because the relaunch changes the page count
sevenfold and a before-and-after taken across it cannot be attributed to anything. Export once on the
day the branch merges and keep the raw files outside this repository, summarizing what changes here.

**IndexNow** is the adjacent mechanism worth knowing about: a key file at the site root plus a ping per
changed URL submits to Bing and the engines sharing its index, which matters because
[Kagi builds its results](https://help.kagi.com/kagi/search-details/search-sources.html) from its own
Teclis crawler plus API calls to the major providers. It is a build-step change rather than a plugin,
and it is worth nothing until the relaunch has something new to announce.

### Repeating the hand check

Search Console covers Google alone, so the other engines are checked by hand. The method is: search
**"Context-Generic Programming"**, **"CGP Rust"**, **"rust blanket implementation"**, **"rust
conflicting implementations E0119"**, **"rust compile time dependency injection"**, and **"rust type
classes"** on Bing and Kagi; record the position of any `contextgeneric.dev` or
`patterns.contextgeneric.dev` result and the exact title shown for it; and note which other CGP
property appears instead. Record the date and the engine beside each finding, and put anything that
changes the guidance into this document rather than into a log.

## The work, in order

The tasks carry **S** identifiers in [tasks.md](tasks.md), which holds the plan: what each one lands
in, what blocks it, and what done means. An identifier named here and missing there has landed, since
that document removes an entry rather than marking it done. This section says only why they are ordered
as they are.

**The click-through work came first, because the data says presentation is what the site is losing
on**, and its valuable half is done: every page in the `macros/`, `attributes/` and `derives/` groups,
the fourteen `traits/` and `types/` pages whose derived snippet was unusable, and all seventeen blog
posts now carry a written description, a search-facing title, or both — fifty-five pages plus the blog,
chosen because they were where the impressions were. The pages left render a derived description that
is serviceable, so the remainder of S3 and S4 is worth sorting by impressions rather than swept, and
whatever of it gets done must land before the merge, since the merge is what fixes each page's first
impression.

**The metadata repairs are done.** The seven dead URLs are stubbed, `robots.txt` is published, the
crate manifests carry `homepage`, five keywords, and the `rust-patterns` and `no-std` categories across
all 27 published crates, and every page now renders as `{Page} | CGP — Context-Generic Programming`,
with the homepage carrying its own hand-written title because it is the one page whose own name should
come first. What is left is the GitHub repository settings, which only the author can change.

**The sweeps and the surfaces follow.** S5 is the first-paragraph orientation pass, S10 the agent
surfaces, S1 the hand check on Bing and Kagi. None of them blocks anything.

**S9 is the only item that cannot be done early**: the relaunch-day submission, which belongs on the
release checklist in
[writing-guides/release-announcement.md](writing-guides/release-announcement.md#publishing-and-what-happens-afterwards)
beside re-pinning the tutorials' `cgp` version.

## The decisions this needs

The measurement and site-search questions this document originally asked are both settled. One
question remains, and it concerns another property rather than this site.

**Algolia DocSearch is accepted, for later.** The relaunch publishes roughly 292 pages with no way to
search them, and DocSearch is free for open-source documentation and ships inside `preset-classic`
rather than as an added plugin. It is the author's decision, taken; it does not block the relaunch, and
it needs a DocSearch application and a configuration block when it happens. It is **S11** in
[tasks.md](tasks.md).

**Search Console is in place**, which settles the measurement question this document originally asked.
Bing Webmaster Tools is not, and adding it is the same shape of decision with the same argument behind
it: no script, no visitor data, and the only view of the engines Google's data cannot see.

**What remains open is `maybevoid.com/projects/cgp/`** — whether the author's older site redirects,
links forward, or stays as it is. It is a small thing, it belongs to the author alone, and nothing in
the work list waits on it.

## Keeping this document current

This document goes stale in two ways, and they need different responses. **Its measurements expire**:
every figure above carries the export or the date it came from, and a re-check replaces the finding
rather than appending to it, per
[document-the-present](../AGENTS.md#document-the-present-not-the-history). **Its techniques expire
faster than most of this base's subject matter**, because search engines change and the surfaces agents
read are two years old at most — so a recommendation resting on a cited study should be re-read against
its source before it is acted on a second time.

Revisit it when the relaunch merges, which is when most of the work either happened or did not; when a
new export is taken, since the baseline above is what the next one is compared against; when a new
section is added to the site, since one page per question is the rule it has to fit; and when a hand
check on another engine disagrees with what Google's data shows here.
