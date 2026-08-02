# Information architecture

This document states what the CGP website is *for*, which pages should exist, what job each one does,
and how a reader moves between them. It is the design the site is being rebuilt toward, and it is the
document the [writing guides](writing-guides/README.md) assume: each of those specifies one kind of
page, and this one holds the shape they add up to.

It is deliberately distinct from [site-structure.md](site-structure.md), and the pair is easy to
confuse. **site-structure.md records the site as built** — the Docusaurus configuration, the current
navigation, the deployment, and one entry per page that exists today. **This document states the site as
intended** — including pages that do not exist yet and jobs that are currently done by the wrong page.
Where they disagree, that disagreement is the redesign, and the work it implies is listed in
[redesign-queue.md](redesign-queue.md).

## The site's job, and the properties around it

The website's job is to take a reader from never having heard of CGP to being able to use it, and to
make the honest case for doing so at each step. It is not the only place CGP is documented, and getting
the boundaries right matters more than it might seem, because three of the site's four routes into CGP
currently lead somewhere unmaintained.

Four public properties carry CGP's documentation, and each owns something the others should not
duplicate. **contextgeneric.dev** is the front door and the home of orientation, teaching, the project's
public argument for itself, and — a recent decision — the **canonical construct reference**.
**[docs.rs/cgp](https://docs.rs/cgp)** carries the crate's API signatures, but documenting the `cgp`
crate has been an open goal since the [launch post](blog/early-preview-announcement.md) and the entry is
thin, so the site does not defer to it; see
[writing-guides/reference.md](writing-guides/reference.md). The
**[CGP Patterns book](https://patterns.contextgeneric.dev/)** teaches CGP from first principles without
reference to the `cgp` crate's specific constructs, which makes it the depth a motivated reader
graduates into — though it has not been updated for some time, and the site currently says so.
**[cgp-skills](https://github.com/contextgeneric/cgp-skills)** is the agent skill, published on the site
as a copy under `docs/ai/` whose source of truth lives elsewhere.

The one-way link rule constrains all of this: the site may cite these public properties and never the
[knowledge base](README.md), which is why the provenance of every page has to be recorded here rather
than on the page itself.

## Most readers do not arrive at the homepage

The single most consequential fact about this site's architecture is that its front door is not the
front page. Every substantial post CGP has published was submitted to the Rust subreddit, Lobsters, and
Hacker News, and those submissions link to the **post**, not the homepage; search traffic lands on
whichever tutorial or post matches the query. The homepage is what a reader visits *after* something
else has interested them, or never.

Two design consequences follow, and they shape everything below.

**Every page is a landing page.** A blog post, a tutorial, or an explanation page may be a reader's
first contact with CGP, so each must orient a cold reader in its first screen — what CGP is, in one
sentence, with a link — before assuming any context. This is cheap to do and currently done unevenly.

**Routing matters more than hierarchy.** A reader who lands mid-site will not go looking for a sidebar;
they follow links in the prose. So the architecture is carried by deliberate onward links at the end of
each page far more than by the navigation tree, and a page that ends without routing has dropped its
reader wherever they happened to stop.

## The four routes in, and why three of them fail

A reader who wants to learn CGP currently has four routes, and only one is maintained. This is the
architecture's central defect and the redesign's main target.

The **Introduction** is orientation and routing — it defines CGP with the `Hash` example, states the
project's maturity frankly, and points onward. It works, except that it currently points readers at the
blog as the most current material, which was true before the tutorials existed.

The **blog** carries the most depth and is the least current. Of seventeen posts, eight write providers
inside-out, seven show the removed `#[cgp_context]`, and four use the removed `Async` trait. Its ideas
remain valuable and several posts are the only prose anywhere on the questions they work through, but a
newcomer sent there lands on syntax the compiler rejects.

The **book** teaches from first principles and has not been updated for a while, which the Introduction
itself concedes.

The **tutorials** are the only maintained, sequenced teaching material on the site, which makes them
where a newcomer should be sent first — and there are two of them.

The redesign's answer is not to fix the blog, which is a dated record and must not be rewritten, but to
**stop routing newcomers into it** and to build out the two tiers that can carry them: the tutorials,
and a new explanation tier that gives a reader the argument without requiring them to write code.

## The surfaces and what each is for

Six surfaces make up the site, and each has one job. A page that does two jobs is usually two pages.

The **front page** makes the idea click and carries the selling points, then routes. It teaches nothing
and specifies nothing. Its spec is [writing-guides/homepage.md](writing-guides/homepage.md).

The **explanation tier** — a new category, `Concepts` — answers *why* for a reader who is not writing
code: why Rust cannot share these implementations, what CGP actually generates, how each of its ideas
works, and where each one stops paying. It carries one page per idea, mirroring the internal
[cgp/concepts/](../cgp/concepts/README.md) catalog. Its spec is
[writing-guides/explanation.md](writing-guides/explanation.md).

The **tutorials** teach a reader to do something, in two registers: first-principles, which derives
constructs from problems using deliberately simple examples, and applied, which builds something real
and links out for the mechanism. Its spec is [writing-guides/tutorial.md](writing-guides/tutorial.md).

The **blog** is the author's voice and the project's record: releases, announcements, and talk
transcripts. It is where depth and candour live, and once published a post is a dated artifact.

The **deep dives** are the multi-page living documents that grow out of the longest posts. They differ
from the blog in the two ways that matter: they are under `docs/`, so they are corrected in place
forever, and they are split into pages a reader can finish. The post they grow from is not edited. Their
spec is [writing-guides/deep-dive.md](writing-guides/deep-dive.md).

The **reference** explains one construct completely, for a reader who already knows the name of what
they need. It is the largest surface on the site at roughly seventy pages, it is derived from the
knowledge base's internal reference rather than written fresh, and it is canonical rather than a
supplement to rustdoc. Its spec is [writing-guides/reference.md](writing-guides/reference.md).

**Orientation pages** — the Introduction and Resources — route rather than teach. Their readers arrive
already interested and want to be sent somewhere, not persuaded.

**Project pages** — Contribute, the planned Project status, and the planned AI disclosure page — speak
about the project rather than about CGP. Contribute is the one page carrying the author's own voice on
the site, in its sponsorship section, and that must stay; the disclosure page carries the second
permitted instance, for the sentence taking responsibility for what the project publishes, since
accountability is something a person can say and a project cannot.

## The target page inventory

The table below is the site as intended. Pages marked **new** do not exist; pages marked **moved** exist
but under the wrong parent or doing the wrong job.

**Almost all of it arrives at once.** The redesign is written on the website repository's `v0.8.0`
branch and publishes when that branch merges alongside the v0.8.0 release, so the site does not pass
through a state where half of this inventory exists — which is what makes a target this large safe to
commit to. The one exception is the deep dives, which land afterwards. The mechanics are in
[AGENTS.md](AGENTS.md#the-redesign-lands-on-a-release-branch-all-at-once) and the sequencing in
[tasks.md](tasks.md).

**Front page** — the hook and the bounded essay. Present, needs rewriting.

**Concepts** (new category, 18 pages plus an index) — present, and **being filled in**

This is the explanation tier, and its shape is now **one page per idea** rather than the four curated
pages this document originally planned. The category is labelled *Concepts*, sits at `docs/concepts/`
between Tutorials and Reference, and mirrors the internal
[cgp/concepts/](../cgp/concepts/README.md) catalog one to one — the same relationship the reference
section has to `cgp/reference/`. All eighteen are scaffolded and one,
*Consumer and provider traits*, is written; the current state is recorded in
[site-structure.md](site-structure.md).

The three explanation pages this document named are not lost, but they are no longer separate
artifacts: *Why CGP exists* is **Bypassing coherence**, *How CGP works* is **Consumer and provider
traits** together with **Impl-side dependencies**, and *When to use CGP, and when not* is **How much
CGP to use**, the modularity hierarchy rendered as a decision guide. The trade is that the tier now
covers every idea rather than the four a homepage essay offloads to, at the cost of the curation that
made those four a short reading path — which the section's index page is what restores.

- *Project status and adoption risk* — **moved**, out of the Introduction, and now **without a settled
  home**: it is project meta rather than a CGP idea, so it does not belong among the concepts. Under
  **Project** beside Contribute is the obvious placement and is not yet decided. The evaluator's page,
  and it must stay linkable directly from above the fold.
- *Overview* — present, **repurposed**, and staying where it is. The feature tour: every high-level CGP
  capability walked through in more detail than any other surface carries. This is the page the front
  page's capability beats and its "it goes further than trait implementations" section offload to, which
  is the job that keeps it from overlapping its neighbours — the concepts explain one idea each, and the
  Overview covers the breadth. It is no longer capped at five features, since the curated five are the
  *front page's* constraint and this page is where they are expanded and the breadth capabilities added.
  It is no longer moved into a new category, which also retires the `slug: /overview` requirement the
  move would have carried.

**Tutorials**, in the order a reader meets them rather than the order they were written
- *Hello World* — present. First contact, five minutes, one durable idea.
- *An applied tutorial* — **new**, and second on purpose. Building something real from an
  [example](../examples/README.md), for the reader who evaluates a technology by seeing a realistic
  system in it. It sits here rather than last because it is the site's first **environmental context**:
  the front page's hero block and Hello World both wire a value context, which is the shape least CGP
  code is actually in, so this is where a reader meets a type standing for an application before their
  habits form.
- *Area calculation* (3 parts) — present. The first-principles series.
- *Checking and debugging* — **new**. Lazy wiring, `check_components!`, and `cargo cgp check`. The
  largest gap in the teaching material and the natural next part of the area-calculation family.

**Reference** (new category, 75 pages plus an index) — present, and **being filled in**
- One page per construct, grouped as `macros/`, `attributes/`, `derives/`, `components/`, `providers/`,
  `traits/`, and `types/`. All are scaffolded; four are written. Ported from the internal reference,
  and recorded in [site-structure.md](site-structure.md).
- A hand-written *index* page that names the handful of constructs a newcomer needs before listing the
  rest by job — present, and not an autogenerated list. It is also where the section's completeness is
  visible, since every construct has an entry here even where the page behind it is a stub.
- An *error catalog* page — scaffolded, **still to be written**. The compile errors CGP produces after
  codegen, organized by the internal catalog's hidden-versus-surfaced axis, so a reader who hits a
  wiring failure has somewhere on the site to look it up. One page rather than seventeen, drawn from
  [cgp/errors/](../cgp/errors/README.md), and the reason every reference page's *Gotchas* section can
  stay construct-specific instead of re-explaining the same failure.
- *Tooling* — **new**, a sibling section rather than part of the reference, covering `cargo-cgp`.

**Deep dives** (new category) — **after the release**, unlike everything else in this inventory
- *Hypershell* — **new**, six pages. The type-level DSL.
- *Extensible data types* — **new**, seven pages. Records, variants, and their internals.
- *cgp-serde* — **new**, five pages. Serde as components.

Each grows out of a long blog post that stays where it is; the plans are in
[deep-dives/](deep-dives/README.md) and the page type is specified in
[writing-guides/deep-dive.md](writing-guides/deep-dive.md). They are the one part of the target the
v0.8.0 relaunch does not carry, because they are the largest discretionary body of work on the list and
their readers are already served, if imperfectly, by the posts they grow out of.

**Orientation**
- *Quickstart* — **new**. Install and one working program, with no concepts and nothing to understand:
  the low-commitment landing the front page and every launch post ask for. It is deliberately smaller
  than *Hello World*, which teaches an idea; this page only proves the thing runs.
- *Introduction* — present, narrowed. Keeps the definition and the routing; loses the maturity section
  to *Project status* and stops sending newcomers to the blog.
- *Resources* — present, needs correcting. The ecosystem index, currently omitting `cargo-cgp`.

**Project**
- *Contribute* — present and current.

**Further depth** — links out to the [book](https://patterns.contextgeneric.dev/) and the
repositories. [docs.rs](https://docs.rs/cgp) is linked once from Resources rather than from each
reference page.

**Blog** — 17 posts, plus the unfinished v0.8.0 draft, one draft on a branch, and one planned post; the
owed writing is B1 and B2 in [tasks.md](tasks.md). The blog is the one surface this inventory does not
try to specify in advance: a post is a dated statement rather than a page with a job, so posts are listed
as they are written rather than planned into the target.

**AI** — the section carries CGP's relationship with coding agents in both directions, and the two
directions are different subjects that must be named apart rather than blended.
- *Using CGP with coding agents* — present as the inlined skill copy, regenerated from `cgp-skills`
  rather than edited. This is a **capability**: what CGP offers a reader who works with an assistant.
- *AI disclaimer* — present. The disclosure page: the four levels from agent-written documentation
  through revised drafts and non-imported code to the hand-written core library, and the destination
  every AI-assisted page's provenance note links to. This is a **fact about the project**, and it is the
  answer a reader wants before they trust the rest of the site. Specified in
  [ai-disclosure.md](../communication-strategy/ai-disclosure.md) rather than in a writing guide, since
  it is one project-meta page rather than a kind the site will publish repeatedly, and recorded in
  [site-structure.md](site-structure.md).

The section stays at `docs/ai/`, labelled "AI Assisted Development", which reads correctly for both
pages; the unmerged rename to `docs/ai-assisted-development/` would move both URLs to no benefit. The
alternative placement — the disclosure page under **Project** beside Contribute — is defensible and was
not chosen, because a reader looking for provenance looks under AI first.

## Navigation and sidebar order

The navigation bar carries Tutorials, Docs, Blog, and AI, plus a GitHub link, and the redesign adds no
new top-level entry — the explanation tier sits under Docs, because a reader looking for "why" looks in
the documentation rather than in a fifth menu. Keeping the bar at four also respects the
[stock-Docusaurus policy](site-structure.md), since the sidebar is autogenerated from the `docs/`
directory tree and a new category is a directory with a `_category_.json` rather than site machinery.

The sidebar order should follow the order a reader needs things rather than the order the project thinks
about them: **Introduction**, **Quickstart**, **Overview**, then **Tutorials**, then **Concepts**, then
**Reference**, then **Deep dives**, then **Tooling**, **Resources**, **Contribute**, and **AI**.
Reference sits after Tutorials because a reader reaches for it once they are writing code rather than
while learning. The Quickstart sits second because the Introduction is the docs root and cannot be
displaced, and because a reader who wants to see CGP run should meet it before any argument.

Concepts sits between Tutorials and Reference rather than before Tutorials, which is a departure from
what this document originally planned and is worth stating with its reason. A four-page curated tier
could reasonably precede the tutorials, since a reader arriving from the homepage has just been told
*why* and wants the argument. Eighteen pages cannot: a reader who meets the whole idea catalog before
writing a line reads it as the amount of theory CGP demands up front, which is the impression the
project can least afford to give. Placing the section after Tutorials makes it what a reader reaches
for once a construct has raised a question, and its index page is what preserves the short reading path
the curated four would have been.

Two naming rules follow. **Do not label the category "Explanation"** — that is vocabulary for the people
organizing documentation, not for the people reading it, and Diátaxis advises against exposing its own
terms in navigation. And **prefer *Concepts* to *Understanding CGP*** now that the section mirrors an
idea catalog rather than carrying four essays: it names the same thing more plainly, and it matches the
word the knowledge base already uses for these documents, so the internal and public names agree.

## How each reader moves through the site

The [reader profiles](../communication-strategy/readers.md) describe who arrives; this section describes
where each of them should end up. A page that cannot be placed on one of these paths probably should not
exist.

The **first-contact skimmer** arrives at a blog post or the front page, gives it seconds, and either
bounces or takes one low-commitment step. Their path is short by design: hook → *Quickstart* → *Hello
World*. Everything else on the site is downstream of a decision they have not made yet, so the only ask is
the Quickstart, which exists precisely because this reader will spend two minutes and not twenty.

The **working developer** arrives with a problem and wants to know whether CGP solves it. Their path is
front page → *Why CGP exists* → *Hello World* → *Area calculation* → *Checking and debugging* → the
reference, which is where they live once they are writing code. The checking tutorial is
load-bearing on this path: it is where a reader either learns to read a CGP error or decides the
language is not worth it.

The **evaluator** reads for risk. Their path is front page → *Project status* → *When to use CGP* →
Resources, and what persuades them is candour plus social proof. The single most valuable thing the site
can do for this reader is present the [Hermes SDK](https://github.com/informalsystems/hermes-sdk/) as
the real system CGP was built for, rather than as one line at the bottom of a link list.

The **type-system and functional-programming reader** wants the mechanism and the intellectual argument.
Their path is *Why CGP exists* → *How CGP works* → the blog deep dives and the
[RustLab transcript](blog/rustlab-2025-coherence.md), which is the best thing on the site for them.

The **framework and library author** wants to know whether CGP solves generic-over-structure code. Their
path is the Overview's problems → the applied tutorial → the *Extensible data types* deep dive → the
[examples](../examples/README.md). This is the least well-served reader, because that material lives
only in four blog posts whose code has drifted, and they stay under-served through the relaunch: the
deep dive is what fixes it properly and it lands afterwards. Until then the applied tutorial is what
this reader gets, which is a reason to draw its scenario from an example that exercises extensible
data rather than from an arbitrary one.

The **enthusiast** is ready to go deep and contribute. Their path is the blog → the book → Contribute,
and the top rung of that ladder is publishing components of their own, which is the outcome the
Contribute page argues for.

## Placing a new page

Three questions settle where a page goes, and asking them in order avoids most mistakes. **What is the
reader doing while they read it?** Nothing → explanation tier; following along at a keyboard → tutorial;
looking one thing up → not this site, use docs.rs. **Is it dated?** A statement about a moment — a
release, an announcement, a talk — is a blog post and becomes a historical record the day it publishes;
a statement about how things are is a docs page and is corrected in place forever. **Whose voice?** The
author's first person means the blog, with the Contribute page's sponsorship section as the one standing
exception.

Three obligations come with the answer. Adding a page means adding its internal document in the same
change, per [AGENTS.md](AGENTS.md), because a page with no document has no recorded provenance. Adding a
page of a *kind* the site has not published before means writing its
[writing guide](writing-guides/README.md) first, since the guide is what later revisions are checked
against. And a page written with AI assistance carries a
[provenance note](AGENTS.md#disclosing-ai-use-on-a-page) at its foot, with the level recorded in its
document — new pages only, never a retroactive sweep.

## What this document does not decide

Visual design, the feature illustrations, and the theme are outside its scope; the project's
[stated policy](blog/new-website.md) is to keep the Docusaurus installation stock and spend the time on
Markdown instead. It also does not decide the *content* of any page — that belongs to the writing guides
and to [communication-strategy/](../communication-strategy/README.md). What it decides is which pages
exist, what each is for, and where a reader goes next.

## Keeping it current

This document leads the site rather than following it, so it goes stale in a particular way: not when the
site changes, but when a page is added, moved, or repurposed **without** the change being reflected here
first. Revisit it whenever a page's job changes, whenever a new page type appears, and whenever a reader
path is found not to work — the last of which is evidence from
[evidence.md](../communication-strategy/evidence.md) rather than a matter of taste. As entries in
[redesign-queue.md](redesign-queue.md) are completed, the corresponding "new" and "moved" markers above
should disappear, and when the inventory here matches [site-structure.md](site-structure.md) the redesign
is finished.
