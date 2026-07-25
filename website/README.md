# The CGP Website

This directory is the knowledge base's **meta-documentation for the public CGP website**, the Docusaurus
site published at <https://contextgeneric.dev> from the
[`contextgeneric.dev`](https://github.com/contextgeneric/contextgeneric.dev) repository. It documents
nothing about CGP itself. Instead it records, for every page the site publishes, what that page says,
how current it is against the CGP the rest of this base describes, and which knowledge-base documents
an agent should read before touching it. An agent asked to write or revise a website page starts here,
finds the internal document for that page, and follows its links outward.

## Why this section exists

The website and the knowledge base have opposite audiences, and that asymmetry is the whole reason for
this directory. The website is **public-facing**: it is read by Rust developers evaluating CGP, and
every link on it must resolve for someone who has never heard of this repository. The knowledge base is
**internal**: it is written by and for agents, it assumes the `/cgp` skill, and it records unfinished
work and known defects that no public page should surface. A website page therefore **cannot link into
the knowledge base**, and this creates a gap — the agent maintaining a page needs the background,
provenance, and current-version facts that only the base holds.

These documents close that gap from the other side. Each one is the knowledge base's record *about* a
website page: it names the page, links to it publicly, and links inward to the reference documents,
concepts, examples, and communication-strategy guidance that the page's content rests on. The website
stays self-contained for its readers; the agent gets a map from any page back to the material behind
it.

The second job these documents do is **track drift**. Almost every blog post on the site predates the
current v0.8.0 release of CGP, and several of them teach syntax the library no longer accepts —
`#[cgp_context]`, `cgp_preset!`, the `Async` trait, `ProvideType`, `symbol!`. A reader can still learn
the ideas from those posts, but an agent must never mine them for current syntax, and must never
"fix" a historical post by silently rewriting it. Each blog document therefore carries an explicit
divergence section naming exactly what is stale, so an agent can quote a post's *ideas* with
confidence while knowing which of its *code* is dead.

## How the website is organized

The site is a stock [Docusaurus](https://docusaurus.io/) installation with three content areas plus a
custom front page, and the navigation bar exposes four of them: Tutorials, Docs, Blog, and AI. The
build is deliberately unmodified — no plugins, no custom React beyond the landing page — a choice the
[new-website post](blog/new-website.md) explains, and one that matters here because it means a
contributor's work is almost entirely writing Markdown.

The **`docs/` tree** holds the reference-style pages: an Introduction, a feature Overview, a Resources
list, a Contribute page, the two tutorial series, and an AI section carrying an inlined copy of the
`/cgp` agent skill. The **`blog/` tree** holds every announcement, release note, deep dive, and talk
transcript, each with an author and a tag drawn from a fixed set (`release`, `deepdive`,
`walkthrough`). The **front page and static assets** live under `src/` and `static/`. This section
mirrors that shape: [site-structure.md](site-structure.md) covers the configuration, navigation, and
every non-blog, non-tutorial page; [blog/](blog/README.md) holds one document per blog post; and
[tutorials/](tutorials/README.md) holds one document per tutorial series.

## The catalog

The three entries below are the section's own subdivisions, each with its own index that catalogs the
documents beneath it. The authoring rules for everything here — including the one-way link rule, the
obligation to consult [communication-strategy](../communication-strategy/README.md) before writing
public prose, and how to record drift — live in [AGENTS.md](AGENTS.md).

- [site-structure.md](site-structure.md) — the site's configuration, navigation, deployment, and
  front page, plus one entry per standalone page: the Introduction, the Overview, Resources,
  Contribute, and the AI skills page.
- [blog/](blog/README.md) — one internal document per published blog post, each recording what the
  post covers, which knowledge-base documents own its material, and how its code and claims diverge
  from CGP v0.8.0. The index carries the chronological catalog and a drift summary.
- [tutorials/](tutorials/README.md) — one internal document per tutorial series, recording the
  series' objective, the concepts it introduces in order, the prerequisites it assumes, and the level
  of explanation it pitches at, so a revision keeps the same teaching contract.

## Reading a page's document before changing the page

The workflow for any website change runs inward before it runs outward. Find the page's document in
one of the three catalogs above and read it, because it names the material the page rests on and the
constraints the page is already under. Follow its links into the [reference](../cgp/reference/README.md)
and [concepts](../cgp/concepts/README.md) for the semantics the page describes, into
[examples/](../examples/README.md) for code that is already verified against current CGP, and into
[communication-strategy/](../communication-strategy/README.md) for how the claim should be framed for
a public audience. Only then write. When the change alters what the page covers or moves it further
from — or closer to — current CGP, revise the page's document in the same change, per the
[synchronization rule](../AGENTS.md#the-synchronization-rule).
