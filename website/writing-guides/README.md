# Website writing guides

This directory holds the guides for **authoring the pages of the CGP website** — one guide per kind of
page, saying what that page is for, what goes on it, in what order, and what must not go on it. The
guides are prescriptive and forward-looking: they describe how a page **should be written**, not how the
current page happens to be written, because they exist to serve a redesign of the site rather than to
document it.

## How a writing guide differs from a page document

The website section holds two kinds of internal document, and confusing them is the easiest mistake to
make here. A **page document** — everything under [blog/](../blog/README.md),
[tutorials/](../tutorials/README.md), and the entries in [site-structure.md](../site-structure.md) — is a
record *about a page that exists*: what it currently says, which knowledge-base documents own its
material, how far its code has drifted, and what a revision must preserve. A **writing guide** is a
specification *for a page that is being written or rewritten*: the job the page has to do, its structure,
its voice, and the rules a draft is checked against.

The two are complementary and are read in a fixed order. Given a task, find the writing guide for the
*kind* of page, then the page document for the *specific* page. The guide tells you what the page should
become; the document tells you what it is now and what constraints it already carries. When they
disagree about a page's shape, the guide is the intent and the document records the gap — which is the
normal state during a redesign, and the gap is worth naming in the page document rather than silently
resolving.

## What every guide here assumes

Three decisions are settled across the whole site and are not re-argued in each guide. They come from
[communication-strategy/](../../communication-strategy/README.md), and a guide that contradicts them is
a defect in the guide.

**The website speaks in the project voice; the blog speaks in the author's.** Pages under `docs/` and
the front page are plain, addressed to the reader, with no first-person narration and no opinion
attributed to a person. Blog posts — including the
[release announcement](release-announcement.md) — are first-person and personally candid. The one
standing exception on the docs side is the sponsorship section of the Contribute page, which is written
in the author's own voice and must stay that way. The full model is
[voice-and-register.md](../../communication-strategy/voice-and-register.md).

**CGP enhances Rust's trait system rather than replacing it.** Every page reinforces that frame, from
the tag line down to a feature title, which is why "a superset of ordinary traits", "a library on stable
Rust", and a sympathetic account of what the trait system already does are load-bearing rather than
defensive. See [identity.md](../../communication-strategy/identity.md).

**Detailed explanation lives on its own page.** The site's long-standing habit is for an explanation to
outgrow whatever container it starts in. The rule is to plan for that rather than fight it: when a
section wants to become an essay, the essay becomes a dedicated page and the shorter surface links to
it. Each guide therefore names the pages its subject offloads to, so the destination exists before the
overflow does.

## The catalog

Register a new guide here in the same change that adds it, and in [../../summary.md](../../summary.md).

- [homepage.md](homepage.md) — the landing page: its two-tier structure, the settled before/after
  example that carries the hook together with the copy that sells it and the properties a replacement
  must keep, the bounded essay beneath it, the dedicated documentation pages the essay offloads to, and
  the routing at the end.
- [explanation.md](explanation.md) — the understanding-oriented pages the homepage offloads to, a page
  type the site does not yet have: what every one owes its reader, how a concept document is rewritten
  into one, per-page specs for the four planned pages, and where they sit in the docs tree.
- [tutorial.md](tutorial.md) — the tutorials: the two registers a CGP tutorial can be written in, what
  every tutorial owes its reader, which Diátaxis rules to adopt and which to reject, and the teaching
  contract a new tutorial must record.
- [release-announcement.md](release-announcement.md) — the blog's most repeated artifact and the only
  page type here written in the *author's* voice: the two readers a release post serves, the
  one-change rule, the seven-part shape, the breaking-changes obligation, and what publication fixes
  permanently.
- [deep-dive.md](deep-dive.md) — the multi-page living documents that grow out of the longest blog
  posts: why they are new artifacts rather than edits, how the author's voice converts to the
  project's without losing the concessions, how to split into pages, and the obligation to track the
  live code base rather than the post.
- [reference.md](reference.md) — the canonical per-construct reference, ported from the knowledge
  base's internal reference: the layered descent that serves beginner through advanced on one page,
  the granularity and the four consolidations, where every internal link is re-pointed, and the
  external Rust documentation to link for concepts a page assumes.

The six guides above cover every page type the site publishes or plans. A seventh is now owed rather than
merely possible: the site has no spec for its **orientation pages**, the Introduction and Resources,
whose job is routing rather than teaching and changes once the [explanation tier](explanation.md)
exists — and the redesign adds a Quickstart, which is a page of a kind the site has not published and
which [AGENTS.md](../AGENTS.md) therefore requires a guide for *before* the page rather than after. It is
task O1 in [tasks.md](../tasks.md).

Two planned pages are deliberately specified elsewhere rather than here, and knowing that stops a later
agent hunting for a missing guide. *Project status* is specified inside
[explanation.md](explanation.md#project-status-and-adoption-risk), and the **AI disclosure page** inside
[ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-page-on-the-website). Both are
single project-meta pages rather than kinds the site will publish repeatedly, and in the second case the
policy and the page are one subject — splitting them across two documents would guarantee that the page
and the practice it describes drift apart.

## Where a guide's authority stops

A writing guide governs the shape and content of a page type; it does not govern the CGP facts on the
page or the mechanics of the site. Every code snippet and every claim about CGP is bound by the
[synchronization rule](../../AGENTS.md#the-synchronization-rule) and must be verified against the source
and the `/cgp` skill, drawing where possible on [examples/](../../examples/README.md), which exists
partly to be quoted. The site's build, navigation, and deployment constraints — the stock-Docusaurus
policy, the autogenerated sidebar, `onBrokenLinks: throw` — live in
[site-structure.md](../site-structure.md), and a guide that would require new site machinery is
proposing something the project has
[explicitly decided against](../blog/new-website.md) and should raise it with the user rather than
assume it.

The rules that bind all website work regardless of page type — the one-way link rule, the prohibition on
rewriting published posts, never taking current syntax from a blog post — are in
[../AGENTS.md](../AGENTS.md) and apply to everything here.
