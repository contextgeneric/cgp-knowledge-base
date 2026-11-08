# Search and agent discoverability

This document is the CGP website's **SEO strategy**: what twelve months of Google Search Console data
say about how the site is found, which search terms it can realistically win, how the v0.8.0 relaunch
should be shaped so that its new pages are found, and how the same material reaches the coding agents
that are a second audience for it.

It is a **specification** rather than a page record, in the sense
[README.md](README.md#two-kinds-of-document-here) draws: it describes what should be true of the site
rather than what is true of one page today. It sits beside
[information-architecture.md](information-architecture.md): that document decides which pages exist
and where a reader goes next, and this one decides how a reader who is not already on the site
arrives.

## What this document owns, and what it must not touch

**Search visibility here is a question of placement, not of wording.** The communication strategy
settles the wording of every public claim, and search does not reopen it:
[identity.md](../communication-strategy/identity.md) owns the tag line, the frame, the headline
features, and [the naming rule](../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page)
that puts the project's name, and a short form of the tag line where it fits, on each web page;
[vocabulary.md](../communication-strategy/vocabulary.md) owns the terms; and
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) owns the rules for a
page's title and opening. This document decides where that settled wording is *placed*: which page
owns which question, what goes in a title tag and a meta description, and what the surfaces outside
the site, which the communication strategy does not reach, should carry.

Three of the base's standing rules bind it, and a recommendation that breaks one is a defect in this
document rather than a trade worth making:

- **Honesty is the strategy.** The techniques below work by making the site's real content findable.
  Keyword-stuffed copy, pages written to catch a query rather than to answer it, and claims about
  search performance beyond what the data shows are excluded.
- **The site stays a stock Docusaurus installation.** Every recommendation is front matter, Markdown,
  static files, or configuration already present. The one addition the project has accepted,
  [Algolia DocSearch](#the-decisions-this-needs), is the author's decision, as
  [site-structure.md](site-structure.md#how-the-site-is-built) requires.
- **The site never links into this knowledge base outside its two sanctioned surfaces.** Nothing here
  changes the [one-way link rule](AGENTS.md#the-one-way-link-rule) or widens its exceptions (the
  disclaimer and the `docs/ai/knowledge-base/` pages), including for a file such as `llms.txt` that
  is written for machines.

## What was measured

**The project has Google Search Console, and this document is written against twelve months of its
data**: a performance export covering **2025-09-19 to 2026-09-18**, Web search, for a domain property
that includes `patterns.contextgeneric.dev` and the `www` host as well as the main site. Every ranking
claim below rests on that export.

The export is raw measurement, so it stays out of this repository under the rule in
[readers.md](../communication-strategy/readers.md#keeping-the-model-observed); the findings belong
here. Two limits matter when reading the numbers. **The query table is capped at 1,000 rows**, which
account for 12,266 of the property's 130,836 impressions, so roughly nine impressions in ten come from
long-tail or anonymized queries that cannot be inspected. And **Search Console's tables disagree by
aggregation**: the Pages table totals 980 clicks against 130,836 impressions, where the Devices and
daily tables total 970 against 121,685. Each figure below is cited with the table it came from rather
than reconciled. Site-wide rates use the daily table; per-page figures use the Pages table.

The site itself was checked against the repository and the live site on **2026-09-21**: the live URLs
were fetched over HTTP, the metadata was read out of the built HTML, and the counts were taken over
the `docs/` and `blog/` trees of the `v0.8.0` branch, which then held 278 Markdown sources, 291 built
pages, and 292 sitemap URLs. On **2026-11-08** the branch holds 378 Markdown sources, 18 of them the
published skill pages, and its build lists 393 sitemap URLs. Docusaurus generates the difference
between sources and URLs without a source file: the front page, the blog index and its pagination,
the tag and author listings, and the category indexes.

**Only Google is measured.** Search Console says nothing about Bing, Kagi, or Brave, so every claim
here is about Google unless it says otherwise, and the [hand check](#repeating-the-hand-check) on the
other engines is S1.

**A hand search of one engine is not the web.** Before the export, searches by hand suggested that the
site failed to rank for its own name, did not rank for blanket implementations, and lost its traffic
in the February 2026 migration. The export shows the opposite on all three: the name ranks first, the
blanket-implementation family is the property's largest source of clicks, and clicks ran at 69 a month
in the five months before the migration and 66 a month in the six months after. Check a conclusion
from a hand search against the export before acting on it.

## The diagnosis

Eight findings explain the site's search performance, ordered by what the data says they cost. The
first is the one the whole strategy turns on, and it is not a ranking problem.

### The site is shown constantly and clicked rarely

**The property drew 121,685 impressions and 970 clicks over twelve months, a click-through rate of
0.80%.** CGP's pages are put in front of people at scale and are not chosen. Average position was
13.07 on desktop, which carries 110,290 of those impressions, against 8.22 on mobile.

**One month distorts that figure.** May 2026 alone contributed 40,568 impressions, a third of the
year, at a 0.21% click-through rate and an average position of 17.1, which is the signature of Google
briefly showing the site for many queries it does not answer. **Excluding May, the year runs at
1.09%**: 886 clicks against 81,117 impressions. Use 1.09% as the baseline the work below is measured
against.

Per page the failure concentrates in the longest posts:

| Page | Impressions | Clicks | CTR | Position |
|---|---|---|---|---|
| `/blog/extensible-datatypes-part-4/` | 7,894 | 6 | 0.08% | 14.3 |
| `/blog/extensible-datatypes-part-2/` | 11,340 | 10 | 0.09% | 14.3 |
| `/blog/cgp-serde-release/` | 7,499 | 10 | 0.13% | 16.8 |
| `/blog/rustlab-2025-coherence/` | 5,111 | 7 | 0.14% | 10.3 |
| `/blog/hypershell-release/` | 21,194 | 186 | 0.88% | 12.8 |
| `/` | 7,874 | 307 | 3.90% | 8.9 |

The front page converts at five times the site average, at a similar position, which is the shape of
a **presentation problem rather than a ranking problem**: pages with a clear title and a real
description are chosen, and pages without one are not. The next two findings are the mechanism.

**Clicks are also concentrated in two pages.** The front page (307) and the patterns book's
blanket-implementations chapter (237) are 55% of all 980 clicks in the Pages table. The other 108
pages share the rest.

### Derived descriptions made the worst snippets

**A page without a `description` in its front matter gets one derived from its first line of Markdown,
which on a reference page was a heading made mostly of punctuation.** On 2026-09-21, only 13 of 278
source pages set a description, and 60 of the 291 built pages carried a missing or under-50-character
one:

- `docs/reference/macros/cgp_component` → ``[cgp_component]` ``
- `docs/reference/macros/cgp_provider` → ``[cgpprovider] & #[cgpnew_provider]` ``
- `docs/reference/types/mref` → `'A`

The blog's derived snippets were as bad. The second extensible-datatypes post, at 11,340 impressions
and a 0.09% click-through rate, advertised itself as *"This is the second part of the blog series… You
can read the first part here"*, and the v0.7.0 post's snippet stripped the backticks from its
identifiers and offered `#[cgpfn]`.

**On 2026-11-08 every page sets a written description except 27**: the 19 Concepts pages, four of
the five tutorials, and the Introduction, Overview, Resources, and Contribute pages. Each of those
renders the first source line of its opening paragraph, which ends mid-sentence where the source
wraps, as in *"Rust's coherence rules keep trait lookup consistent across a program. For a given
trait, its"*, so each still needs a written one. The published skill pages are not the site's to
edit. The conventions, including the YAML apostrophe that fails the build, are in
[site-structure.md](site-structure.md#conventions-the-port-must-follow).

A post's description is metadata rather than a claim, so writing one does not reach the
[dated-artifact rule](AGENTS.md#do-not-rewrite-history); the wording rules that keep it from implying
currency are in [blog/README.md](blog/README.md#publication-conventions). A description does not rank
a page. It supplies the snippet a human reads before deciding to click, and at 121,685 impressions a
year the snippet is where the site's visibility is spent.

### The longest titles are truncated before they say anything

Page titles ran to **161 characters** at the extreme on 2026-09-21, against an average of 48. The
longest belong to the posts with the worst click-through rates above:

- *CGP v0.5.0 Release: Auto dispatchers, extensible datatype improvements, monadic computation, RTN emulation, modular serde, and more* (161 characters)
- *Programming Extensible Data Types in Rust with CGP - Part 1: Modular App Construction and Extensible Builders* (139)

A search result shows roughly the first 60 characters, so a reader sees *"Programming Extensible Data
Types in Rust with CGP - Part 1: Modular…"* and has to judge from a fragment that is mostly setup.
These are published posts, so their titles are [not rewritten](AGENTS.md#do-not-rewrite-history). A
new page can avoid the problem through a front-matter `title`, which can differ from the page's heading,
as [the title rules](#titles-and-descriptions-are-the-per-page-levers-and-docusaurus-separates-them)
describe.

### The pages that rank are the pages that have gone stale

**The blog is 61 of the 110 pages with impressions, 90,978 of the impressions, and 336 of the clicks;
the whole `docs/` tree is 19 pages, 2,624 impressions, and 18 clicks.** Search traffic to this project
is mostly blog traffic, and
[blog/README.md](blog/README.md#reading-the-drift-at-a-glance) records that of seventeen posts, eight
write every provider inside-out, seven show the removed `#[cgp_context]`, and four use the removed
`Async` trait.

The four extensible-datatypes posts alone carry 41,746 impressions, and every one predates
`#[cgp_impl]`, `#[implicit]`, and the `open` statement. **This is the one place where search success
does harm.** The live [Introduction](site-structure.md#introduction) compounds it by telling readers
that "the most accurate and up-to-date resources concerning CGP are currently available in the form
of our blog posts". The `v0.8.0` branch rewrites that sentence, which fixes the internal routing, but
a reader who arrives from a search result may never pass through the Introduction, and
[information-architecture.md](information-architecture.md#most-readers-do-not-arrive-at-the-homepage)
establishes that most readers arrive that way.

### Five dead URLs still draw impressions into 404s

**The Zola-to-Docusaurus migration moved every documentation URL under `/docs/` and left nothing at
the old addresses.** Search Console still records impressions against those addresses, and each
returned 404 when fetched on 2026-09-21:

| Pre-migration URL | Impressions | Clicks | Position | Current address |
|---|---|---|---|---|
| `/overview/` | 723 | 1 | 7.07 | `/docs/overview` |
| `/tutorials/hello/` | 495 | 0 | 8.03 | `/docs/tutorials/hello` |
| `/resources/` | 456 | 4 | 7.29 | `/docs/resources` |
| `/contribute/` | 236 | 5 | 6.55 | `/docs/contribute` |
| `/tutorials/` | 24 | 0 | 6.58 | `/docs/tutorials/hello` |

That is **1,934 impressions and 10 clicks a year landing on a 404**, at positions between 6.5 and 8,
better than most of the site earns. The `www` host adds three of the same paths at 94 impressions
each; `www` redirects correctly, so those are the same URLs under a second hostname rather than a
duplicate-host problem. The blog's URLs survived the migration unchanged, which is why the blog kept
its history.

The `v0.8.0` branch carries seven static stubs under `static/`, one for each of these paths and for
the dead feed paths `/feed/` and `/atom`, each with a canonical link and a meta refresh. GitHub Pages
cannot issue a 301, so a static stub is all that is available without a plugin, and it is what the
official redirects plugin would generate. They reach readers when the branch merges.

### The name is won, and the acronym is unwinnable

**The site ranks first for its own name, and the name has almost no search volume.** The query
*context generic programming* sits at average position **1.1** with a **46.6% click-through rate**,
and *cgp rust* at position **1.3** with 37.5%. Between them they drew **112 impressions in twelve
months**, against 805 for *rust blanket implementation* alone.

The acronym is not worth pursuing. **`cgp` drew 736 impressions and zero clicks** at position 12.0,
and a hand search returns a UK educational publisher, the US Government Publishing Office's catalog,
and an EPA construction permit. Queries containing *cgp* total 67 queries, 1,698 impressions, and 23
clicks (1.4%), while the six queries containing the full term total 245 impressions and 41 clicks
(16.7%). The acronym has seven times the impressions of the full term and a twelfth of its
click-through rate, because *cgp zero*, *char cgp*, *chap cgp*, *chapt cgp*, *zero cgp*, and *cgp
community edition* draw some 430 impressions from people looking for a different CGP. The acronym
queries that do convert, *cgp rust* and *cgp community*, already rank at 1.3 and 3.8.

**The site title carries the acronym anyway, at the author's decision, in the one place it survives
truncation.** It is `CGP — Context-Generic Programming`, so every page renders as
`{Page} | CGP — Context-Generic Programming`. The acronym sits right after the separator, where it is
shown rather than cut, and the full term follows it, so a search for the full term still matches.
The decision went against this document's recommendation, because the acronym's volume is mostly a
different product; what it buys is that a reader searching *cgp rust* sees the term they typed, which
is a click-through argument rather than a matching one. Since the suffix carries the acronym, a page's
own title does not repeat it, except on a page whose subject is CGP itself, such as the disclosure
page and the published skill.

Several other high-impression queries are the same phenomenon, the site appearing for something it
does not answer. *generic programming* drew 970 impressions and one click at position 13.4; *v0* 394
and none; *implicit* 238 and none; *serde* 133 and none; *rust context* 453 impressions and two clicks.
**Roughly 2,900 impressions a year go to queries the site cannot serve**, so the impression total
overstates the site's real reach.

### The full term appeared as boilerplate rather than as content

**On 2026-09-21, "Context-Generic Programming" appeared in every page's title tag and navigation bar,
and in the body prose of only 11 of the site's 278 pages.** A name identical on every page of a site
is weak evidence of what any page is about, so a name that appears only in that furniture is one the
site has not used. On 2026-11-08, 20 of the 360 hand-written sources contain the name. The
[naming rule](../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page)
requires it in the prose of every page except the skill pages and the published posts, for reader
orientation; [Own the name](#own-the-name-by-saying-it-where-it-means-something) says what that means
for search.

### The off-site metadata is under-set

**The crate manifests are set**: `homepage` points at the site, so crates.io and lib.rs link it, and
five keywords and the `rust-patterns` and `no-std` categories place the crates in the
browse-and-recommend surfaces. Every publishable crate inherits them from `[workspace.package]`.

**What remains needs repository settings rather than a commit**, and only the author can change it.
Read on GitHub on 2026-11-08:

- **The `cgp` repository's description reads "Context-Generic Programming: modular programming
  paradigm for Rust"**, the framing
  [identity.md](../communication-strategy/identity.md#using-modular-as-a-supporting-word) retires, on
  the project's most-linked property. Its homepage is the site, and its topics are
  `functional-programming`, `modular-programming`, and `rust`.
- **`cargo-cgp`, `cgp-examples`, and `contextgeneric.dev` have no description.** `cgp-skills`
  describes itself as "Prompts and instructions for LLM-assisted coding for CGP" rather than as CGP's
  agent skill, the name [vocabulary.md](../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each)
  gives it.
- **No member repository other than `cgp` has topics**, and of the others only `cgp-serde` sets a
  homepage: its release post, rather than its Projects pages.

**The front page is the one page that names the project first**, at the author's decision. Its title
is *Context-Generic Programming (CGP) - Pluggable trait implementations for Rust*, with no site-name
suffix. Passing `title` to Docusaurus's `Layout` renders `{title} | {siteTitle}`, so the page sets the
tag directly with `@docusaurus/Head`, and sets `og:title` with it so a shared link carries the same
words. That is React on the landing page, where the
[stock-Docusaurus policy](site-structure.md#how-the-site-is-built) already allows it. A result shows
roughly the first sixty characters, so the name and the acronym display in full while the claim after
them is cut; on a page that already ranks first for both branded queries, spending the visible
characters on the name is a judgement about recognition rather than matching. Its description opens
with the settled tag line verbatim, since the front page presents the project. The page itself is
[F1](tasks.md#f--the-front-page).

### The pages that would answer the high-intent queries are not published yet

**The site already appears for the vocabulary the strategy targets, at good positions, and converts
none of it:**

| Query | Impressions | Clicks | Position |
|---|---|---|---|
| `rust coherence` | 24 | 0 | 8.0 |
| `rust blanket trait implementation` | 23 | 1 | 6.1 |
| `rust conflicting implementations of trait` | 10 | 0 | 11.8 |
| `rust trait orphan rule` | 5 | 0 | 24.0 |
| `rust dependency injection` | 2 | 0 | 6.5 |

The export cannot say why these counts are small. **Search Console records a query only where the
site appeared**, so a small impression count may mean the query is rare or that the site ranks too
low to be seen for a common one. Nothing here establishes that few people search for `E0119`; it
establishes that CGP is rarely in front of the ones who do.

The conversion is unambiguous: **at position 8.0 for *rust coherence*, the site earned zero clicks all
year**, on exactly the queries the Concepts pages are written to answer.

The pages that would answer them are **not published yet**: `/docs/concepts/coherence` and
`/docs/reference/` returned 404 on the live site on 2026-09-21, because they exist only on the
`v0.8.0` branch. The live site published 40 URLs that day, and the branch's build lists 393 on
2026-11-08. The `docs/` tree earns 18 clicks a year against the blog's 336, so the relaunch is the
first serious attempt to make the documentation half of the site findable.

## The strategy

### What good would look like

**The name and the blanket-implementation family already rank, so the targets are about being
chosen.** Each is an outcome a Search Console export can confirm a year from now:

- **Click-through rate rises from 1.09% toward the front page's 3.9%**, at unchanged position, taking
  the May-excluded figure as the baseline. This is the single measurable target, it is largely within
  the project's control, and it requires no ranking change.
- **The `docs/` tree stops being a rounding error.** Eighteen clicks a year against the blog's 336 is
  the gap the relaunch exists to close.
- **A reader searching the problem rather than the project** (conflicting implementations, `E0119`,
  compile-time dependency injection, a foreign trait for a foreign type) **finds a page on the site
  that answers it.**
- **A reader arriving from any of those searches lands on a current page**, rather than on a 2025
  post teaching `#[cgp_context]`.

None of these sets a date or predicts a volume, and
[formats.md](../communication-strategy/formats.md#titles-first-lines-and-search)'s rule against
asserting unmeasured search claims binds everything else.

### Raise the click-through rate before trying to raise the rank

**This is the strategy's organizing decision.** At 81,117 impressions and 1.09% outside the May
anomaly, a large part of the visibility the site already has is wasted, and recovering it needs no
links, no authority, and no ranking change. It needs a title a reader can parse and a description
that says what the page is for.

**Not every impression is winnable.** At least 2,900 impressions a year, in the visible part of the
query table alone, come from queries the site cannot answer (*generic programming*, *cgp*, *v0*,
*serde*), and no title turns those into clicks. The invisible nine tenths of the impressions almost
certainly contain more of the same. So the target is a better click-through rate, not a multiple of
today's traffic; a projection such as "0.80% to 2% would triple it" is arithmetic rather than a
forecast.

The rest of this section follows from that decision. The per-page title and description work is the
main event rather than housekeeping, the relaunch matters because every page it adds can start with
both, and the redirect stubs, the off-site metadata, and the agent surfaces are worthwhile but
smaller.

### The relaunch is the event, and it only happens once

**The site goes from 40 published URLs to several hundred, nearly all of them new.** Google crawls each
page in the state it merges in, and the title and description it carries that day are what a reader
sees for as long as nobody revisits it, which, on the evidence of the blog, is years. Every
recommendation below is cheaper before the merge than after.

**The relaunch is URL-additive, which removes a risk that would otherwise dominate this document.** The
existing documentation paths (`/docs/overview`, `/docs/contribute`, `/docs/resources`,
`/docs/tutorials/hello`) are unchanged by the redesign, and
[information-architecture.md](information-architecture.md#the-target-page-inventory) keeps the
Overview where it is. The one page that moves is *Project status*, which has never had a URL of its
own. So the relaunch adds history rather than breaking it, and the only broken history is the
migration's, which the redirect stubs repair at the merge.

### The patterns book is the best-performing property, not a competitor

**The book earns 308 clicks from 19 pages; the main site earns 672 from 91.** Per page it outperforms
everything else the project publishes, and its blanket-implementations chapter, at 12,232 impressions,
237 clicks, and position 6.8, is the most successful page in the property.
[patterns-book.md](patterns-book.md) holds the book's record and the chapter-level plan.

Three consequences follow:

- **Do not redirect it or fold it into the site.** It works, and the reference section has no page
  that would inherit its readers.
- **Link it forward.** A reader landing on the book's blanket-implementations chapter should be
  offered the current page for the same idea. That is a change in the `cgp-patterns` repository, B-1
  in [patterns-book.md](patterns-book.md#the-work-in-order), and the cheapest high-value link
  available.
- **Read it as evidence about titles.** A chapter called *Blanket Implementations* wins a query
  called *rust blanket implementation*, which is the whole
  [title argument](#titles-and-descriptions-are-the-per-page-levers-and-docusaurus-separates-them) in
  one example.

Two smaller surfaces belong in the same frame. **docs.rs and lib.rs** win part of *cgp rust*, as they
should for a reader who wants an API listing, and the crate's `homepage` turns that result into a
route to the site. And **`maybevoid.com/projects/cgp/`**, the author's older site, appears on a hand
search for the full term; whether it redirects, links forward, or stays is
[the author's call](#the-decisions-this-needs).

### Own the name by saying it where it means something

**The [naming rule](../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page)
places the name, and its reason is the reader, not search.** Each page other than the skill pages and
the published posts names Context-Generic Programming once in its opening paragraph, beside a plain
description and linked to the Introduction, so a reader who arrives from a search result knows what
the page belongs to. The name already ranks first, so the search benefit is a by-product.

The rule goes wrong for search in two ways, and both are cheap to avoid. The name is **one mention,
not a density target**, and the sentence around it is written for the page's explanation, not to
catch a query.

### The tag line orients the reader; the features carry the searchable words

**The settled tag line is not a keyword asset.** "A language extension for Rust, with pluggable trait
implementations at compile-time" answers *what is this*, which a reader needs on arrival, and almost
nobody types it or anything like it: the branded queries together are 112 impressions a year. Never
rewrite it for search, and never repeat it to raise a page's density. The naming rule puts a short
form of it, such as "CGP enables pluggable trait implementations in Rust", on most pages because it
tells the reader what CGP adds, related to what that page explains; it is one mention, and it carries
no query the site needs to win.

**The five headline features are where searchable language legitimately lives**, because each names
a problem someone types, and each already has a page. The mapping below is the strategy's core: the
features are the settled set from
[identity.md](../communication-strategy/identity.md#the-headline-feature-set), in its order, the
middle column is the query family each can honestly answer, and the right is the page that should own
it. Measured volume is given where the export shows it.

| Headline feature | The query family it answers | Measured volume | The page that owns it |
|---|---|---|---|
| One Interface, Many Implementations | conflicting implementations, `E0119`, overlapping impls | not yet ranking | `docs/concepts/coherence` |
| Zero-Cost Abstraction | static dispatch versus `dyn`, avoiding vtables | not yet ranking | `docs/comparisons/dynamic-dispatch` |
| Type-Safe Wiring | compile-time dependency injection, DI without a container | not yet ranking | `docs/comparisons/dependency-injection` |
| Abstract Over Every Dependency | abstract error type, generic over the runtime, `no_std` core | not yet ranking | `docs/concepts/modular-error-handling` |
| Still Ordinary Rust | blanket implementation, extension trait | **1,781 impressions/yr, position 4–5** | `docs/concepts/coherence`, the glossary |

**The blanket-implementation family is the proven one, and it belongs to "Still Ordinary Rust".** Six
query variants (*rust blanket implementation*, *rust blanket impl*, *blanket implementation rust*,
*blanket implementation*, *blanket implementations*, *rust blanket implementations*) total 1,781
impressions and 106 clicks at positions 4.0 to 5.1. It is the one term where the project is a
recognized answer, and the Concepts page and glossary entry should be written to inherit it rather than
to compete with the book for it.

Two further families have no feature to hang off and matter as much. **The orphan rule and the newtype
dance** belongs to `docs/concepts/coherence` beside the first row. And **the comparison vocabulary**
(type classes, ML modules, implicit parameters, algebraic effects, policy-based design) is eleven
queries the comparison pages answer and nothing else in Rust does.

One more family has a page planned: **`rust dsl` drew 771 impressions and 25 clicks at position
7.0**, plus *dsl rust* and *dsl in rust* for another 314 impressions. The Hypershell post ranks for it,
and the index of the [Hypershell project section](projects/hypershell.md) should inherit it, which is
a reason to write that section first among the libraries.

The table imposes **one page per question**. Where two pages could answer a query, one answers it and
the other links, the rule [AGENTS.md](../AGENTS.md#writing-links) already applies to explanations.

### Comparisons are the most valuable unproven pages on the site

**The eleven comparison pages are CGP's best untested search asset.** A reader searching "Rust type
classes" or "dependency injection in Rust without a framework" has a specific, low-competition,
high-intent question, and the site carries a long, sourced, fairly argued page for each. Their guide
requires the two things that make such a page rank and keep ranking: a `description` in the front
matter, and
[a title in the compared concept's own name](writing-guides/related-work.md#placement-navigation-and-bookkeeping)
rather than a problem-oriented one, because that reader arrives with a vocabulary rather than a
problem.

They are also the section most likely to be quoted by someone else, which is the only form of
link-building the project should do. The section needs nothing done to it and should be protected.

### Titles and descriptions are the per-page levers, and Docusaurus separates them

Two mechanics settle how the click-through work is done, both verified against Docusaurus's
documentation on 2026-09-21:

- **A page's front-matter `title` sets the metadata and can differ from its heading.** Docusaurus
  inserts a title at the top of a document only when the Markdown has no heading of its own, so a
  page that keeps its `#[cgp_component]` heading can carry a `title` written for a search result.
  `sidebar_label` stays separate and is
  [plain text without backticks](site-structure.md#conventions-the-port-must-follow).
- **A page's front-matter `description` sets both `meta name="description"` and `og:description`**,
  and falls back to the first line of content when omitted, which produced the broken snippets above.

Four rules, decided in advance, keep the writing tractable:

- **Keep the title under roughly 60 characters**, which is what a result shows, and put the
  distinguishing word first.
- **Reference and construct pages get the construct name plus its job**, name first, because the
  name is what the reader searched.
- **Concept and tutorial pages get problem-oriented titles**, as
  [formats.md](../communication-strategy/formats.md#titles-first-lines-and-search) prescribes.
- **Every description is a sentence about that page, written once, not a template.** A description
  that could belong to any page tells a reader nothing, and the engine replaces it with a fragment of
  the text.

### Adding a page is almost never the answer, and the data says which three cases to consider

**A new page is justified when a reader arriving on a query has a question the site answers and no
page owns, never by query volume alone**, as [What must never be done](#what-must-never-be-done)
sets. Applied to the three query clusters that carry real traffic, the test gives three different
answers.

**Blanket implementations (25 queries, 2,019 impressions, 110 clicks, average position 5.8) needs no
new page.** Three things already answer it. The
[patterns book's chapter](https://patterns.contextgeneric.dev/blanket-implementations.html) wins the
query today. `docs/concepts/coherence` is *about* overlapping blanket implementations and why Rust
rejects them, which is the question behind the query. And the glossary defines the term and hands it
to the Rust Reference, which is the site's standing rule for a Rust concept it does not own.

So the work is to connect what exists, and it is on the list twice. **The book chapter links
forward**, which is part of [S7](tasks.md#s--search-and-agent-discoverability) and B-1 in
[patterns-book.md](patterns-book.md#the-work-in-order). And **the coherence page needs a title in the
reader's words**, which is [S4](tasks.md#s--search-and-agent-discoverability). Those words are
*blanket implementation*, not `E0119`: the blanket family is 2,019 impressions a year against 11 for
*rust conflicting implementations of trait*. A page arguing that Rust allows only one blanket
implementation per trait can say so in its title honestly, because that is what it argues.

**A standalone "what is a blanket implementation in Rust" page would re-teach Rust**, which the
[reference guide](writing-guides/reference.md#linking-three-destinations-and-one-prohibition) rules out
and the glossary handles by linking Rust's own documentation. It would also break the
[Concepts section's one-to-one mirroring](site-structure.md#concepts) of the internal catalog, since no
internal concept document covers it. The reader arriving on that query is better served by a page that
answers the question *behind* it.

**Domain-specific languages (20 queries, 1,432 impressions, 36 clicks, average position 7.7) has a
page planned and should have it sooner.** The Hypershell post wins *rust dsl* (771 impressions,
position 7.0) and converts at 3.2%, and 293 of those impressions are a comparison intent it serves
badly: *shell scripting vs rust*, *rust vs shell scripting*, and *cargo vs shell scripting* together
earn zero clicks. The owner is the [Hypershell project section](projects/hypershell.md), which is
[P2](tasks.md#p--the-projects-section-and-the-code-it-quotes). **This is the strongest evidence
available for writing Hypershell first among the libraries**, and it is why that section plans a
comparison with shell scripts, the page the post's readers are looking for.

**The context cluster is a watch item, not a page.** *rust context* draws 453 impressions at position
7.1 and converts at 0.44%, and the export cannot say what its readers want: context-generic
programming, an async context, a context object, or something unrelated. The one signal worth keeping
is *rust context pattern* (11 impressions, 3 clicks, **27% click-through at position 4.0**), which
suggests that a reader using those words finds CGP relevant. That is a handful of impressions and no
basis for building. Watch it in the next export and decide then.

**Nothing else in the data supports a page.** The serde, comparison-vocabulary, provider-pattern, and
macro clusters each appear at average positions between 24 and 36 with zero clicks, which is the
shape of a site surfacing far down for something it does not answer. The comparison vocabulary shows
why: those eleven pages exist but are unpublished, so the queries they will answer cannot show in this
export.

### The internal linking is already right, and it is doing more work than usual here

**Internal links are how a crawler finds a page that nothing external links to, which describes nearly
every page the relaunch adds.** Google's
[guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) counts
findability through internal links among the fundamentals that still apply, and on this site it is
close to the only mechanism available.

The redesign already provides it, for other reasons, and a later change must not undo it. The sidebar
is generated from the directory tree, so no page is orphaned. Every reference page closes with
*Related constructs* and a *The ideas behind it* list into Concepts. Fourteen Concepts pages route
into Comparisons, 195 pages link the glossary, and both section indexes are hand-written rather
than generated.

The one rule to hold is the one the base applies to prose: **link with the words the destination is
about**, not with "here" or "this page", because the anchor text is the clearest signal a linking page
gives about what it points at.

## Coding agents are the second audience

**An agent writing Rust does not use a search engine the way a person does, so different surfaces
reach it, and CGP is better placed there than its search performance suggests.** Two channels matter,
and they behave differently.

**Retrieval at coding time** is what an agent does when it has been told to use CGP, or has found it,
and needs to write correct code. These surfaces serve it:

- **docs.rs** is the default surface for any Rust crate. The published crate's rustdoc was sparse when
  checked on 2026-09-21, reporting half the crate documented. The release fixes that: every
  publishable `cgp` library crate warns on a missing doc comment and CI fails on warnings, each
  construct's rustdoc links its website page, and the crate README routes readers to the site.
- **Context7** carried CGP as `/contextgeneric/cgp` with 528 indexed snippets on 2026-09-21, drawn
  from the repository rather than from the website, and its description repeated the retired
  "modular programming paradigm" line. A `context7.json` in the repository controls which folders are indexed,
  and the entry can be resubmitted so the description and the indexed material match the library.
- **The published agent skill** needs no work. It teaches an assistant CGP's vocabulary, idioms, and
  diagnostics, and [cgp-skills](https://github.com/contextgeneric/cgp-skills) is published on the
  site and on GitHub.
- **The knowledge base** serves an agent whose user has pointed it there to learn or audit CGP in
  depth. The site's [knowledge-base pages](site-structure.md#knowledge-base) teach that use, and the
  base's README tells an outside agent what to read. The user chooses this surface rather than an
  agent discovering it, so it needs no discoverability work beyond those pages.
- **The site itself**, fetched directly, which is why the
  [named opening](#own-the-name-by-saying-it-where-it-means-something) and one page per question
  matter as much for an agent as for a person: both answer "is this page about the thing I asked".

**Model priors** are what an agent knows before it reads anything, formed from GitHub, published
writing, and forum discussion rather than anything the site can configure. There is no technique
here, only the project's existing practice: publish, be cited, and keep the vocabulary stable so that
the same words describe the same things on every surface. Message discipline, which
[vocabulary.md](../communication-strategy/vocabulary.md) enforces for readers, is also what makes a
model's recall of CGP consistent.

### `llms.txt`, and why it is worth a file but not an argument

**The evidence is that almost nothing reads it.** Ahrefs analysed 137,210 domains in May 2026 and found
that 28% publish an `llms.txt`, that **97% of those files received zero traffic that month**, and that
96% of the requests that did arrive came from bots rather than people. The sample is sites using
Ahrefs' own analytics, which skews toward the search-aware end of the web and makes the finding
stronger, since those sites are the most likely to have published the file deliberately. Google's
[guidance on optimizing for generative AI features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
states that Google Search does not use `llms.txt` or other special markup of that kind, and no major
model provider has committed to reading it.

**So the honest case for publishing one is agent convenience, not visibility.** A single file listing
the site's sections with one line each costs almost nothing, is easy to regenerate, and gives an agent
that has already reached the site a map of its pages without crawling them. That is a real benefit to
a real user, and it is not a ranking technique; a recommendation presenting it as one would make the
kind of claim this project does not make. If it is published, it is generated from the sidebar rather
than maintained by hand, it links only public pages, and nothing on the site advertises it.

## What was checked and is not worth acting on

Three things a reader of this document might raise were examined and deliberately left alone:

- **Structured data.** Google states that its AI features require no special schema.org markup, and
  a documentation site has no eligible rich-result type to gain from adding any. A future proposal to
  add JSON-LD should say what result it expects.
- **The generated listing pages.** The sitemap carries `/blog`, `/blog/archive`, `/blog/authors`, the
  tag listings, the category indexes, and their pagination. They duplicate content that exists
  elsewhere, which on a large site is worth pruning. On a site of a few hundred pages they are
  navigational and cost nothing, and Docusaurus's sitemap plugin already excludes anything marked
  `noindex` if that ever changes.
- **Page performance.** The site is statically generated, ships almost no JavaScript beyond the
  landing page, and enables `@docusaurus/faster`. Performance is not among the site's problems, and
  the stock-Docusaurus policy keeps it that way.

## What must never be done

Five techniques are excluded, each by a rule the project already holds:

- **No keyword stuffing, and no page written to catch a query.** The site's pages exist because a
  reader needs them. Repeating the name, the tag line, or a short form of it for density is stuffing
  too; [the naming rule](../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page)
  asks for one mention of each, and neither is a keyword to repeat.
- **No rewriting the tag line, the feature titles, or a construct's name for search.**
  [identity.md](../communication-strategy/identity.md) owns that wording, and message discipline across
  surfaces is worth more than any single query.
- **No claim about search performance beyond what the export shows.** The data covers Google only, its
  query table is capped, and it says nothing about causation; a rise after a change is not proof the
  change caused it.
- **No bulk-generated pages.** The site is written with AI assistance and discloses it; the line
  between that and generating pages to occupy queries is the line between documentation and spam.
- **No site machinery added quietly.** A plugin or a third-party service is the author's decision,
  taken deliberately, as [Algolia DocSearch](#the-decisions-this-needs) was.

## Measurement

**Search Console is in place, so the question is what to watch.**
[evidence.md](../communication-strategy/evidence.md#what-the-search-data-shows-about-demand)
summarizes this export for the communication strategy.

**Search Console is not analytics**, which is what makes it compatible with the site's posture. It
places no script on the site, sees no visitor, and changes nothing a reader loads: it reports what
Google already knows about its own index. Verification is a static file or a DNS record, so the
stock-Docusaurus policy is untouched. The same is true of Bing Webmaster Tools, which is not set up
and would be the only view of Bing, Kagi, and the engines built on Bing's index.

Four signals are worth watching, each tied to a target in
[What good would look like](#what-good-would-look-like):

- **Site-wide CTR at constant position.** The one number that says whether the title and description
  work paid off. Take **1.09%** as the baseline, not the raw annual 0.80%, and check whether a later
  period carries its own anomaly before comparing.
- **Clicks to `/docs/`.** Eighteen a year, against the blog's 336.
- **Clicks on the problem queries**: `rust coherence`, conflicting implementations, and dependency
  injection, which stand at zero against 41 impressions and are the clearest test of whether the
  Concepts and Comparisons pages do their job.
- **Whether the dead URLs stop appearing** once the stubs in `static/` reach the live site at the
  merge, which checks that the redirects work.

**Establish the baseline before the relaunch merges**, because the relaunch multiplies the page count
and a before-and-after taken across it cannot be attributed to anything. Export once on the day the
branch merges, keep the raw files outside this repository, and summarize what changes here.

**IndexNow** is the adjacent mechanism worth knowing: a key file at the site root plus a ping per
changed URL submits to Bing and the engines sharing its index, which matters because
[Kagi builds its results](https://help.kagi.com/kagi/search-details/search-sources.html) from its own
Teclis crawler plus API calls to the major providers. It is a build-step change rather than a plugin,
and it is worth nothing until the relaunch has something new to announce.

### Repeating the hand check

Search Console covers Google alone, so the other engines are checked by hand. Search
**"Context-Generic Programming"**, **"CGP Rust"**, **"rust blanket implementation"**, **"rust
conflicting implementations E0119"**, **"rust compile time dependency injection"**, and **"rust type
classes"** on Bing and Kagi; record the position of any `contextgeneric.dev` or
`patterns.contextgeneric.dev` result and the exact title shown for it; and note which other CGP
property appears instead. Record the date and the engine beside each finding, and put anything that
changes the guidance into this document rather than into a log.

## The work, in order

The tasks carry **S** identifiers in [tasks.md](tasks.md#s--search-and-agent-discoverability), which
holds the plan: what each lands in, what blocks it, and what done means. An identifier named here and
missing there has landed, since that document removes an entry rather than marking it done. This
section says only why they are ordered as they are.

**The click-through work comes first, because presentation is what the site is losing on.** Most of
it is in place: every reference, comparison, tooling, project, and AI page and every blog post carries
a written description, and every reference page for a construct carries a search-facing title. What
remains of S3 and S4 is the 27 pages that render a derived description and the Concepts titles, above
all `docs/concepts/coherence`. Each lands in the same edit as the page's
[named opening](#own-the-name-by-saying-it-where-it-means-something), which is S5, so a page is read
once, and all of it lands before the merge, which fixes each page's first impression.

**The metadata repairs are done except what only the author can change.** The crate manifests are
set, and the redirect stubs, `robots.txt`, and the site and front-page titles are on the `v0.8.0`
branch, reaching readers at the merge; the GitHub repository settings are S7.

**The agent surfaces and the hand check follow.** S10 is the agent surfaces and S1 the hand check on
Bing and Kagi. Neither blocks anything.

**S9 is the only item that cannot be done early**: the relaunch-day submission, which belongs on the
release checklist in
[writing-guides/release-announcement.md](writing-guides/release-announcement.md#publishing-and-what-happens-afterwards)
beside re-pinning the tutorials' `cgp` version. S11 follows the relaunch.

## The decisions this needs

Two decisions are taken, and two remain open:

- **Algolia DocSearch is accepted, for after the relaunch.** The relaunch publishes several hundred
  pages with no way to search them, and DocSearch is free for open-source documentation and ships
  inside `preset-classic` rather than as an added plugin. It needs a DocSearch application and a
  configuration block, and it is **S11** in [tasks.md](tasks.md).
- **Search Console is in place.**
- **Bing Webmaster Tools is open.** It is the same shape of decision as Search Console, with the same
  argument behind it: no script, no visitor data, and the only view of the engines Google's data
  cannot see.
- **`maybevoid.com/projects/cgp/` is open**: whether the author's older site redirects, links forward,
  or stays as it is. It belongs to the author alone, and nothing in the work list waits on it.

## Keeping this document current

This document goes stale in two ways, and they need different responses. **Its measurements expire**:
every figure carries the export or the date it came from, and a re-check replaces the finding rather
than appending to it, per [document-the-present](../AGENTS.md#document-the-present-not-the-history).
**Its techniques expire faster than most of this base's subject matter**, because search engines
change and the surfaces agents read are two years old at most, so re-read a recommendation resting on
a cited study against its source before acting on it a second time.

Revisit it when the relaunch merges, which is when most of the work either happened or did not; when a
new export is taken, since the baseline above is what the next one is compared against; when a section
is added to the site, since one page per question is the rule it has to fit; and when a hand check on
another engine disagrees with Google's data.
