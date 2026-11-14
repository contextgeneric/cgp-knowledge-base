# Website writing guides

This directory holds the guides for **authoring the pages of the CGP website**: one guide per kind of
page, saying what that page is for, what goes on it, in what order, and what must not go on it. The
guides are prescriptive and forward-looking: they describe how a page **should be written**, not how the
current page happens to be written, because they exist to serve a redesign of the site rather than to
document it.

## How a writing guide differs from a page document

The website section holds two kinds of internal document, and confusing them is the easiest mistake to
make here. A **page document** (everything under [blog/](../blog/README.md),
[tutorials/](../tutorials/README.md), and the records in [pages/](../pages/README.md)) is a
record *about a page that exists*: what it currently says, which knowledge-base documents own its
material, how far its code has drifted, and what a revision must preserve. A **writing guide** is a
specification *for a page that is being written or rewritten*: the job the page has to do, its structure,
its voice, and the rules a draft is checked against.

The two are complementary and are read in a fixed order. Given a task, find the writing guide for the
*kind* of page, then the page document for the *specific* page. The guide tells you what the page should
become; the document tells you what it is now and what constraints it already carries. When they
disagree about a page's shape, the guide is the intent and the document records the gap, which is the
normal state during a redesign, and the gap is worth naming in the page document rather than silently
resolving.

## What every guide here assumes

Five decisions are settled across the whole site and are not re-argued in each guide. They come from
[communication-strategy/](../../communication-strategy/README.md), and a guide that contradicts them is
a defect in the guide.

**The website speaks in the project voice; the blog speaks in the author's.** Pages under `docs/` and
the front page are plain, addressed to the reader, with no first-person narration and no opinion
attributed to a person. Blog posts, including the
[release announcement](release-announcement.md), are first-person and personally candid. The one
standing exception on the docs side is the sponsorship section of the Contribute page, which is written
in the author's own voice and must stay that way. The full model is
[voice-and-register.md](../../communication-strategy/voice-and-register.md).

**CGP enhances Rust's trait system rather than replacing it.** Every page reinforces that frame, from
the tag line down to a feature title, which is why "a superset of ordinary traits", "a library on stable
Rust", and a sympathetic account of what the trait system already does are essential rather than
defensive. See [identity.md](../../communication-strategy/identity.md).

**Every page names Context-Generic Programming, and echoes the tag line rather than repeating it.**
A page names the project in full once, in its opening paragraph, beside a plain description, and
relates a short form of the tag line to what it explains, such as "CGP enables pluggable trait
implementations in Rust", or leaves the line out where it does not fit. Only a page that presents the
project states the line whole, and a generated category index carries the name in its
`_category_.json` description. The skill pages and the published blog posts are exempt. The rule and
its short forms belong to
[identity.md](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page); each
guide says only where its kind of page carries them.

**Every page is written in natural style by default.** Each public page, the front page and every
docs page alike, follows natural-writing, the style in the `point-first-writing` skill in which each
sentence picks up from the last and transitions say how the points connect, so the whole site reads
as one connected explanation. A guide may name another style for its kind of page, and none does.
The documents in this knowledge base, these guides included, stay in point-first style.

**Detailed explanation lives on its own page.** The site's long-standing habit is for an explanation to
outgrow whatever container it starts in. The rule is to plan for that rather than fight it: when a
section wants to become an essay, the essay becomes a dedicated page and the shorter surface links to
it. Each guide therefore names the pages its subject offloads to, so the destination exists before the
overflow does.

## The catalog

Register a new guide here in the same change that adds it, and in [../../summary.md](../../summary.md).

- [homepage.md](homepage.md): the landing page, covering its two-tier structure, the settled before/after
  example that carries the hook together with the copy that sells it and the properties a replacement
  must keep, the bounded essay beneath it, the dedicated documentation pages the essay offloads to, the
  Overview's specification as the feature tour, and the routing at the end.
- [explanation.md](explanation.md): the understanding-oriented Concepts pages, which the homepage
  offloads to, covering what every one owes its reader, how a concept document is rewritten into one, the specs
  for the three roles the homepage names, and where the pages sit in the docs tree.
- [tutorial.md](tutorial.md): the tutorials, covering the two registers a CGP tutorial can be written in, what
  every tutorial owes its reader, which Diátaxis rules to adopt and which to reject, and the teaching
  contract a new tutorial must record.
- [release-announcement.md](release-announcement.md): the blog's most repeated artifact and the only
  page type here written in the *author's* voice, covering the two readers a release post serves, the
  clear lead, the placement of short announcements before a long walkthrough, the announcement's
  parts, the breaking-changes obligation, and what publication fixes permanently.
- [project.md](project.md): the Projects section, which ports the internal project sections to the
  site, covering the seven page kinds, the example page written as a short tutorial with its orientation block,
  walkthrough, named pattern, and verified change to try, one reference page per project construct, the
  limitations page, the link map, and why project code is verified against its own repository rather
  than the `example-code` crate.
- [tooling.md](tooling.md): the pages documenting a program the reader *runs* rather than a construct
  they write, covering why a tool's page fails differently from a construct's, the nine-page section
  shape with its reading, editor, and lookup pages, the obligation to quote real output from the program the page
  shows, writing against the release the site ships with, the Linux-only rule, and the version-free
  concession every claim about the error experience carries.
- [reference.md](reference.md): the canonical per-construct reference, ported from the knowledge
  base's internal reference, covering the layered descent that serves beginner through advanced on one page,
  the granularity and the four consolidations, where every internal link is re-pointed, the
  external Rust documentation to link for concepts a page assumes, and the two non-construct pages the
  section carries, the error catalog and the glossary.
- [orientation.md](orientation.md): the pages whose job is routing rather than teaching, covering the
  Introduction, the Quickstart, Resources, and the Contribute page. What separates orientation from
  the homepage, a tutorial, an explanation and a reference; what each of the four pages is for; the
  Quickstart's ten-minute activation target and the boundary that keeps it from becoming a second
  Hello World; the version pin that ties it to the release; and the Contribute page's routes, with
  the sponsorship section and the acknowledgement left in the author's hands.
- [knowledge-base.md](knowledge-base.md): the pages explaining the public knowledge base, covering
  why they are the second sanctioned exception to the one-way link rule and how far it reaches, the
  four-page shape that keeps the process page apart from the two how-to pages, what a how-to page
  owes its reader as the site's first of the kind, and why prompt templates wait until they have
  been tested.
- [related-work.md](related-work.md): the comparison pages, ported from the internal
  [related-work](../../related-work/README.md) documents for a reader who already knows type classes,
  dependency injection, ML modules, effects, or another related idea, covering the four transformations the port
  makes, above all retiring the positioning section and applying it as structure, the page shape from
  the *In your terms* table to the section where the other tool wins, the rules for writing about
  another community's tool, and the verification of code in two languages.

The guides above cover every page type the site publishes or plans, and each one precedes its pages,
because [AGENTS.md](../AGENTS.md) requires a guide for a new *kind* of page ahead of the page rather
than after it.

One project-meta page is deliberately specified elsewhere rather than here, and knowing that stops a
later agent hunting for a missing guide: the **AI disclosure page**, specified inside
[ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-page-on-the-website). It is a single
project-meta page rather than a kind the site will publish repeatedly, and the policy and the page are
one subject, so splitting them across two documents would guarantee that the page and the practice it
describes drift apart.

## The reading map

**Before revising a page, read the shared set below and the row for the page's kind.** The rows are
how a writer meets [../AGENTS.md](../AGENTS.md)'s rule to read the shared set and the kind's row
before drafting: each names the sections of the strategy and of [seo.md](../seo.md) that its kind of page
draws on, so a writer reads those rather than all of it, about 255 KB. A row is the minimum. When a
page makes a claim the row's sections do not cover, such as a new argument for what CGP is good for,
read the document that owns the claim in full.

### Every page kind

Every row starts from the same reading:

- **The strategy in brief:** [messaging-brief.md](../../communication-strategy/messaging-brief.md),
  whole.
- **The reader:** [naming the reader](../../communication-strategy/readers.md#naming-the-reader-is-the-first-decision-in-a-piece),
  the first decision for any page.
- **The words:**
  [the terms](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each),
  including the canonical `cargo-cgp` qualification and the names of the knowledge base and the agent
  skill, and [the words to avoid](../../communication-strategy/vocabulary.md#words-and-framings-to-avoid).
- **The voice:** [author-personality.md](../../communication-strategy/author-personality.md),
  [voice-and-register.md](../../communication-strategy/voice-and-register.md), and
  [writing-styles.md](../../communication-strategy/writing-styles.md), whole.
- **The name and the tag line:**
  [the naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page),
  with [Own the name](../seo.md#own-the-name-by-saying-it-where-it-means-something) and
  [The tag line orients the reader](../seo.md#the-tag-line-orients-the-reader-the-features-carry-the-searchable-words)
  for what it means for search.
- **The front matter:**
  [the title and description levers](../seo.md#titles-and-descriptions-are-the-per-page-levers-and-docusaurus-separates-them)
  and [the titles and openings rules](../../communication-strategy/formats.md#titles-first-lines-and-search).
- **Provenance:** [the provenance note](../../communication-strategy/ai-disclosure.md#linking-to-it-from-a-page).

The skill pages have no row: they are published from the agent skill, nobody revises them here, and
the naming rule exempts them.

### The front page and the Overview

- **Guide:** [homepage.md](homepage.md), including
  [the offload rule](homepage.md#the-offload-rule-and-the-pages-it-offloads-to) for the Overview.
- **Style:** natural style for both, as for every page.
- **Strategy:** [identity.md](../../communication-strategy/identity.md), whole;
  [message.md](../../communication-strategy/message.md)'s
  [lead with the pain](../../communication-strategy/message.md#lead-with-the-pain-not-the-paradigm),
  [the problems](../../communication-strategy/message.md#the-problems-cgp-removes),
  [the strengths](../../communication-strategy/message.md#the-strengths-worth-advertising),
  [the objections](../../communication-strategy/message.md#the-objections-readers-bring), and
  [when not to reach for CGP](../../communication-strategy/message.md#when-not-to-reach-for-cgp);
  [readers by role](../../communication-strategy/readers.md#readers-by-role-and-point-of-contact);
  [the conversion ladder](../../communication-strategy/formats.md#the-conversion-ladder); and
  [CGP's reception](../../communication-strategy/evidence.md#cgps-own-reception-and-the-lessons-in-it).
- **SEO:** [the off-site metadata](../seo.md#the-off-site-metadata-is-under-set), for the front page's
  own title, and [raise the click-through rate](../seo.md#raise-the-click-through-rate-before-trying-to-raise-the-rank).

### Concept pages

- **Guide:** [explanation.md](explanation.md), in natural style.
- **Strategy:**
  [the frame](../../communication-strategy/identity.md#the-frame-the-whole-identity-serves-enhances-not-replaces);
  [lead with the pain](../../communication-strategy/message.md#lead-with-the-pain-not-the-paradigm),
  [the problems](../../communication-strategy/message.md#the-problems-cgp-removes), and
  [the objections](../../communication-strategy/message.md#the-objections-readers-bring);
  [readers by Rust experience](../../communication-strategy/readers.md#readers-by-rust-experience) and
  [the comprehension barriers](../../communication-strategy/readers.md#the-comprehension-barriers);
  [qualifiers](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target) and
  [deferred terms](../../communication-strategy/vocabulary.md#terms-to-defer-and-how-to-reveal-them);
  and [reader-simulation.md](../../communication-strategy/reader-simulation.md), whole.
- **SEO:** [adding a page](../seo.md#adding-a-page-is-almost-never-the-answer-and-the-data-says-which-three-cases-to-consider),
  for the coherence page's title, and
  [the internal linking](../seo.md#the-internal-linking-is-already-right-and-it-is-doing-more-work-than-usual-here).

### Tutorials

- **Guide:** [tutorial.md](tutorial.md).
- **Strategy:**
  [readers by Rust experience](../../communication-strategy/readers.md#readers-by-rust-experience),
  [the comprehension barriers](../../communication-strategy/readers.md#the-comprehension-barriers),
  and [the teaching discipline](../../communication-strategy/readers.md#the-teaching-discipline-this-points-to);
  [qualifiers](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target) and
  [deferred terms](../../communication-strategy/vocabulary.md#terms-to-defer-and-how-to-reveal-them);
  [lead with the pain](../../communication-strategy/message.md#lead-with-the-pain-not-the-paradigm);
  [the conversion ladder](../../communication-strategy/formats.md#the-conversion-ladder);
  [what we watch](../../communication-strategy/evidence.md#what-we-watch-and-what-counts-as-a-result),
  for the activation measure; and
  [reader-simulation.md](../../communication-strategy/reader-simulation.md), whole.
- **SEO:** the shared set.

### Reference pages, the glossary, and the error catalog

- **Guide:** [reference.md](reference.md).
- **Strategy:** [qualifiers](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target),
  [deferred terms](../../communication-strategy/vocabulary.md#terms-to-defer-and-how-to-reveal-them),
  and, for the glossary, [the public page it feeds](../../communication-strategy/vocabulary.md#the-public-page-this-feeds);
  [the comprehension barriers](../../communication-strategy/readers.md#the-comprehension-barriers);
  and [when not to reach for CGP](../../communication-strategy/message.md#when-not-to-reach-for-cgp).
- **SEO:** [adding a page](../seo.md#adding-a-page-is-almost-never-the-answer-and-the-data-says-which-three-cases-to-consider),
  for one page per question, and
  [the internal linking](../seo.md#the-internal-linking-is-already-right-and-it-is-doing-more-work-than-usual-here).

### `cargo-cgp` pages

- **Guide:** [tooling.md](tooling.md), in natural style.
- **Strategy:** [reading the error messages](../../communication-strategy/readers.md#reading-the-error-messages);
  [the compile-error problem](../../communication-strategy/message.md#read-a-cgp-compile-error-without-decoding-a-wall-of-generated-types),
  [the objections](../../communication-strategy/message.md#the-objections-readers-bring), and
  [the agent skill's placement](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these).
- **SEO:** [coding agents](../seo.md#coding-agents-are-the-second-audience).

### Comparison pages

- **Guide:** [related-work.md](related-work.md).
- **Strategy:**
  [the comparison piece](../../communication-strategy/formats.md#the-comparison-or-positioning-piece);
  [audience-tuned one-liners](../../communication-strategy/message.md#audience-tuned-one-liners),
  [the objections](../../communication-strategy/message.md#the-objections-readers-bring), and
  [when not to reach for CGP](../../communication-strategy/message.md#when-not-to-reach-for-cgp);
  [readers by prior mental model](../../communication-strategy/readers.md#readers-by-prior-mental-model);
  [the bridge terms](../../communication-strategy/vocabulary.md#the-name-and-the-communitys-bridge-terms);
  and [CGP's reception](../../communication-strategy/evidence.md#cgps-own-reception-and-the-lessons-in-it).
- **SEO:** [the comparisons](../seo.md#comparisons-are-the-most-valuable-unproven-pages-on-the-site).

### Projects pages

- **Guide:** [project.md](project.md).
- **Strategy:** [the strengths](../../communication-strategy/message.md#the-strengths-worth-advertising)
  and [when not to reach for CGP](../../communication-strategy/message.md#when-not-to-reach-for-cgp);
  [readers by role](../../communication-strategy/readers.md#readers-by-role-and-point-of-contact), for
  the evaluator; [qualifiers](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target);
  and [the canonical examples](../../communication-strategy/voice-and-register.md#show-it-canonical-examples-diagrams-and-diffs),
  for the exception Projects pages hold.
- **SEO:** [adding a page](../seo.md#adding-a-page-is-almost-never-the-answer-and-the-data-says-which-three-cases-to-consider),
  for the Hypershell section's measured demand.

### Orientation pages: the Introduction, the Quickstart, and Resources

- **Guide:** [orientation.md](orientation.md).
- **Strategy:** [the tag line](../../communication-strategy/identity.md#the-tag-line) and
  [the pitch](../../communication-strategy/identity.md#the-pitch-that-follows-the-line);
  [the objections](../../communication-strategy/message.md#the-objections-readers-bring) and
  [when not to reach for CGP](../../communication-strategy/message.md#when-not-to-reach-for-cgp);
  [readers by role](../../communication-strategy/readers.md#readers-by-role-and-point-of-contact);
  [the conversion ladder](../../communication-strategy/formats.md#the-conversion-ladder); and
  [what we watch](../../communication-strategy/evidence.md#what-we-watch-and-what-counts-as-a-result),
  for the Quickstart's activation target.
- **SEO:** [the stale pages that rank](../seo.md#the-pages-that-rank-are-the-pages-that-have-gone-stale),
  for the Introduction's routing, and
  [the derived descriptions](../seo.md#derived-descriptions-made-the-worst-snippets).

### The Contribute page

- **Guide:** [orientation.md](orientation.md#the-contribute-page), whose sponsorship section stays
  in the author's voice, per [What every guide here assumes](#what-every-guide-here-assumes).
- **Strategy:**
  [contributions from outside the project](../../communication-strategy/ai-disclosure.md#contributions-from-outside-the-project)
  and [the contributor directing an agent](../../communication-strategy/readers.md#the-contributor-directing-an-agent);
  [the conversion ladder](../../communication-strategy/formats.md#the-conversion-ladder), for the
  enthusiast; and [the stated preferences](../../communication-strategy/author-personality.md#stated-preferences),
  for the sponsorship section.
- **SEO:** [the derived descriptions](../seo.md#derived-descriptions-made-the-worst-snippets).

### The knowledge-base pages and the AI disclosure page

- **Guide:** [knowledge-base.md](knowledge-base.md), and for the disclosure page
  [its specification](../../communication-strategy/ai-disclosure.md#the-page-on-the-website).
- **Strategy:** [ai-disclosure.md](../../communication-strategy/ai-disclosure.md), whole;
  [the reader who doubts agent-written documentation](../../communication-strategy/readers.md#the-reader-who-doubts-agent-written-documentation)
  and [the contributor directing an agent](../../communication-strategy/readers.md#the-contributor-directing-an-agent).
- **SEO:** [coding agents](../seo.md#coding-agents-are-the-second-audience).

### The release post

- **Guide:** [release-announcement.md](release-announcement.md), in the author's voice.
- **Strategy:** [the tag line](../../communication-strategy/identity.md#the-tag-line),
  [the pitch](../../communication-strategy/identity.md#the-pitch-that-follows-the-line), and
  [the headline features](../../communication-strategy/identity.md#the-headline-feature-set);
  [the strengths](../../communication-strategy/message.md#the-strengths-worth-advertising),
  [the objections](../../communication-strategy/message.md#the-objections-readers-bring), and
  [the agent skill's placement](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these);
  [the blog deep-dive](../../communication-strategy/formats.md#the-blog-deep-dive) and
  [the launch post](../../communication-strategy/formats.md#the-link-aggregator-launch-post);
  [CGP's reception](../../communication-strategy/evidence.md#cgps-own-reception-and-the-lessons-in-it)
  and [where the profiles gather](../../communication-strategy/evidence.md#where-the-profiles-gather);
  and [revision of human-written drafts](../../communication-strategy/ai-disclosure.md#revision-of-human-written-drafts).
- **SEO:** [the truncated titles](../seo.md#the-longest-titles-are-truncated-before-they-say-anything)
  and [the work, in order](../seo.md#the-work-in-order), for the relaunch-day submission.

## Where a guide's authority stops

A writing guide governs the shape and content of a page type; it does not govern the CGP facts on the
page or the mechanics of the site. Every code snippet and every claim about CGP is bound by the
[synchronization rule](../../AGENTS.md#the-synchronization-rule) and must be verified against the source
and the `/cgp` skill, drawing where possible on [examples/](../../examples/README.md), which exists
partly to be quoted. The site's build, navigation, and deployment constraints (the stock-Docusaurus
policy, the autogenerated sidebar, `onBrokenLinks: throw`) live in
[site.md](../site.md#how-the-site-is-built), and a guide that would require new site machinery is
proposing something the project has
[explicitly decided against](../blog/new-website.md) and should raise it with the user rather than
assume it.

The rules that bind all website work regardless of page type (the one-way link rule, the prohibition on
rewriting published posts, never taking current syntax from a blog post) are in
[../AGENTS.md](../AGENTS.md) and apply to everything here.
