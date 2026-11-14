# Website writing guides

This directory holds one guide per kind of page on the CGP website: what the page is for, what goes on
it and in what order, and what must not. The guides are prescriptive: they say how a page should be
written, while each page's record says what the page is now, as
[the section README](../README.md#records-and-specifications) describes. Read the guide for the page's
kind first, then the page's record.

## What every guide here assumes

Five decisions hold across the site, taken from
[communication-strategy/](../../communication-strategy/README.md); a guide that contradicts one is
wrong:

- **Voice:** pages under `docs/` and the front page speak in the plain project voice, addressed to
  the reader, without first-person narration or an opinion attributed to a person; blog posts, the
  [release announcement](release-announcement.md) included, are first-person and candid in the
  author's voice. The Contribute page's sponsorship section is the one docs exception and stays in
  the author's voice. See [voice-and-register.md](../../communication-strategy/voice-and-register.md).
- **Frame:** CGP enhances Rust's trait system rather than replacing it, so "a superset of ordinary
  traits", "a library on stable Rust", and a sympathetic account of the trait system are essential
  on every page. See [identity.md](../../communication-strategy/identity.md).
- **Name:** every page names Context-Generic Programming in full once, in its opening paragraph, and
  relates a short form of the tag line to its content or leaves the line out; only a page that
  presents the project states the line whole, and a generated category index carries the name in its
  `_category_.json` description. The skill pages and the published blog posts are exempt.
  [identity.md](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page)
  owns the rule and its short forms; each guide says where its kind carries them.
- **Style:** every public page is written in natural-writing's natural style, unless its guide names
  another, and none does; the guides themselves stay in point-first style.
- **Offloading:** when a section outgrows its page, the explanation becomes a dedicated page that the
  shorter surface links, so each guide names the pages its subject offloads to.

## The catalog

Register a new guide here in the same change that adds it, and in [../../summary.md](../../summary.md).

- [homepage.md](homepage.md): the landing page: its two tiers, the settled before-and-after example
  and what a replacement must keep, the bounded essay, the pages it offloads to, and the checks.
- [explanation.md](explanation.md): the Concepts pages: what each owes its reader, how a concept
  document becomes one, and the three pages the homepage offloads to.
- [tutorial.md](tutorial.md): the tutorials: the two registers, what each owes its reader, the
  Diátaxis rules kept and rejected, and the teaching contract a record states.
- [release-announcement.md](release-announcement.md): the release posts, in the author's voice: the
  two readers, the clear lead, the parts, the breaking-changes obligation, and what publication fixes.
- [project.md](project.md): the Projects section: the page kinds, the example page as a short
  tutorial, the reference and limitations pages, the link map, and verification against the
  project's repository.
- [tooling.md](tooling.md): the pages for a program the reader runs: the section shape, quoting real
  output from the release the site ships with, the Linux-only rule, and the concession on errors.
- [reference.md](reference.md): the construct reference: the layered page, the granularity and
  consolidations, re-pointed links, the conventions the port follows, and the error catalog and
  glossary pages.
- [orientation.md](orientation.md): the routing pages: the Introduction, the Overview, the
  Quickstart and its ten-minute target, Resources, and the Contribute page.
- [knowledge-base.md](knowledge-base.md): the pages explaining the public knowledge base: their
  exception to the one-way link rule, the four-page shape, the how-to pages, and why prompt templates
  wait until tested.
- [related-work.md](related-work.md): the comparison pages: the port from the related-work documents,
  the page shape, writing about another community's tool, and verifying code in two languages.

The AI disclosure page has no guide here: it is specified with the policy it publishes, in
[ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-page-on-the-website).

## The reading map

**Before revising a page, read the shared set below and the row for the page's kind.** Each row names
the sections of the communication strategy and of [seo.md](../seo.md) its kind of page draws on, so a
writer reads those rather than every document. A row is the minimum: when a page makes a claim the
row's sections do not cover, such as a new argument for what CGP is good for, read the document that
owns the claim in full.

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

- **Guide:** [homepage.md](homepage.md) for the front page, and
  [orientation.md](orientation.md#the-overview) for the Overview.
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

- **Guide:** [orientation.md](orientation.md), which the AI section's overview also follows.
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

A guide governs a page kind's shape and content, not the CGP facts on the page or the site's
mechanics. Every snippet and claim about CGP follows the
[synchronization rule](../../AGENTS.md#the-synchronization-rule) and is verified against the source
and the `/cgp` skill, drawing on [examples/](../../examples/README.md) where possible. The build,
navigation, and deployment constraints are in [site.md](../site.md#how-the-site-is-built); a guide
that would need new site machinery raises it with the user, because the project
[decided against it](../blog/new-website.md). The rules for all website work are in
[../AGENTS.md](../AGENTS.md).
