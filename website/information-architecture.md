# Information architecture

This document states what the CGP website is *for*, which pages it has, what job each does, and how a
reader moves between them. It is the shape the [writing guides](writing-guides/README.md) assume: each
guide specifies one kind of page, and this document holds what they add up to.

[site.md](site.md) and the [page records](pages/README.md) **record the site as built**; this document
**states the site as intended**, including pages that do not exist yet. Where they disagree, that
disagreement is the redesign, and each page's record states the work it implies.

## The site's job, and the properties around it

**The site takes a reader from never having heard of CGP to being able to use it, making the honest
case at each step.** Four public properties carry CGP's documentation, and each owns what the others
must not duplicate:

- **contextgeneric.dev:** the front door, orientation, teaching, the project's public argument, and
  the **canonical construct reference**.
- **[docs.rs/cgp](https://docs.rs/cgp):** the crate's API signatures. The site does not defer to it;
  see [writing-guides/reference.md](writing-guides/reference.md).
- **The [CGP Patterns book](https://patterns.contextgeneric.dev/):** CGP from first principles, without
  the `cgp` crate's constructs, and a [legacy resource](AGENTS.md#leave-legacy-resources-off-public-pages)
  the site leaves out.
- **[cgp-skills](https://github.com/contextgeneric/cgp-skills):** the agent skill, published on the site
  as a copy under `docs/ai/` whose source lives in that repository.

The site may cite these and never this [knowledge base](README.md), outside the bounds of the
[one-way link rule](AGENTS.md#the-one-way-link-rule), which is why each page's provenance is recorded
here rather than on the page.

## Most readers do not arrive at the homepage

**The site's front door is not its front page.** Every substantial post was submitted to the Rust
subreddit, Lobsters, and Hacker News, which link the post, and search traffic lands on whichever page
matches the query. The front page is what a reader visits after something else interested them, or
never. Three consequences follow:

- **Every page is a landing page.** Each orients a cold reader in its first screen, saying what CGP is
  in one sentence with a link, before assuming any context.
- **Routing matters more than hierarchy.** A reader who lands mid-site follows links in the prose, not
  the sidebar, so each page ends by routing its reader onward; a page that ends without routing drops
  its reader where they stopped.
- **Newcomers are not routed into the blog.** It carries the most depth and the least current code,
  and a post is a dated record that is not rewritten, so newcomers go to the tutorials and Concepts.

## The surfaces and what each is for

Each surface has one job, and a page that does two jobs is usually two pages:

- **Front page:** makes the idea click, carries the selling points, and routes; it teaches and
  specifies nothing. Spec: [writing-guides/homepage.md](writing-guides/homepage.md).
- **Concepts:** answers *why* for a reader who is not writing code, one page per idea, mirroring
  [cgp/concepts/](../cgp/concepts/README.md). Spec: [writing-guides/explanation.md](writing-guides/explanation.md).
- **Comparisons:** maps CGP into the vocabulary of a paradigm the reader already holds, states what
  each side costs, and says where the reader's own tool is the better choice; one page per
  [related-work](../related-work/README.md) document. Spec:
  [writing-guides/related-work.md](writing-guides/related-work.md).
- **Tutorials:** teach a reader to do something, in two registers: first-principles, deriving
  constructs from problems with simple examples, and applied, building something real and linking out
  for the mechanism. Spec: [writing-guides/tutorial.md](writing-guides/tutorial.md).
- **Blog:** the author's voice and the project's record (releases, announcements, talk transcripts);
  a published post is a dated artifact.
- **Projects section:** CGP's patterns in real programs, one section per library or demonstration,
  ported from [projects/](../projects/README.md) with each example expanded into a short tutorial. It
  is under `docs/`, so its pages are corrected in place. Spec:
  [writing-guides/project.md](writing-guides/project.md); blueprint: [projects/README.md](projects/README.md).
- **Reference:** explains one construct completely, for a reader who knows its name; the largest
  surface, derived from the internal reference, and canonical rather than a supplement to rustdoc.
  Spec: [writing-guides/reference.md](writing-guides/reference.md).
- **Orientation pages** (the Introduction, the Quickstart, and Resources): route rather than teach,
  for readers already interested. Spec: [writing-guides/orientation.md](writing-guides/orientation.md).
- **Project pages** (Contribute and the AI disclosure page): speak about the project rather than
  about CGP. Contribute's sponsorship section is the one place the author's own voice stands on the
  site, and the disclosure page's sentence taking responsibility for what the project publishes is the
  second, since accountability is something a person can say and a project cannot.

**Keep the two similar names apart:** a *project page* speaks about the CGP project; a page under
`docs/projects/` is a *Projects page*, never a *project page*.

## The target page inventory

Every page below exists on the `v0.8.0` branch unless marked **new**, and each section's record
under [pages/](pages/README.md) or [projects/](projects/README.md) holds its pages and counts. The
redesign publishes at once when that branch merges with the release, under
[AGENTS.md](AGENTS.md#the-redesign-lands-on-a-release-branch-all-at-once); only the Projects section
lands afterwards.

- **Front page:** the hook and the bounded essay.
- **Overview**, staying at its current path: the feature tour. The five headline features each get a
  compiled example; the breadth features get a list linking their Concepts pages and no code, because
  a first-time reader meets too many constructs otherwise; a table maps the problems readers bring to
  the pages that answer them. It is what the front page's feature cards offload to.
- **Concepts:** one page per idea, with a hand-written index that restores a short reading path. The
  three essays once planned are now pages: *Why CGP exists* is *Bypassing coherence*, *How CGP works*
  is *Consumer and provider traits* with *Impl-side dependencies*, and *When to use CGP* is *Modularity
  Hierarchy*.
- **Tutorials**, in the order a reader meets them:
  - *Hello World*: first contact, one durable idea.
  - *An applied tutorial*: **new**, and second on purpose. It builds something real from an
    [example](../examples/README.md) and is the site's first **environmental context**, after a front
    page and a Hello World that wire a value context, so a reader meets a type that stands for an
    application before their habits form.
  - *Area calculation*: the first-principles series, ending with *Checking and debugging*, which
    carries one mis-wiring through `check_components!` and `cargo cgp check`.
- **Comparisons**, placed after Concepts: labelled *Comparisons* because "related work" is the
  internal directory's word, not a reader's.
- **Reference**, grouped as `macros/`, `attributes/`, `derives/`, `components/`, `providers/`,
  `traits/`, and `types/`, with a hand-written index that names what a newcomer needs first and
  reaches every construct, an error catalog page, and a glossary.
- **Tooling** at `docs/cargo-cgp/`, a sibling section rather than part of the reference, labelled for
  the tool; its error-codes page is where the error catalog sends a reader holding a `[CGP-Exxx]`
  code.
- **Projects**, after the release: the index, cgp-examples, Hypershell, and cgp-serde partly written,
  and the error backends **new**. It replaces three deep dives planned earlier, as
  [projects/README.md](projects/README.md#what-the-section-replaces) maps.
- **Orientation:** the *Quickstart*, which only proves CGP runs and stays smaller than Hello World,
  with its boundary in [writing-guides/orientation.md](writing-guides/orientation.md); the
  *Introduction*, narrowed to the definition and the routing, with no maturity section, since the
  front page's cost section states the maturity; and *Resources*, the ecosystem index.
- **Project:** *Contribute*.
- **Further depth:** links out to the repositories, never to the legacy book. docs.rs is linked once,
  from Resources.
- **Blog:** not planned in advance; a post is a dated statement rather than a page with a job.
- **AI**, at `docs/ai/` labelled "AI-Assisted Development", in this order:
  - *Overview*: the section's landing page, one heading per direction.
  - *Using CGP with coding agents*: the inlined skill, regenerated from `cgp-skills`; a **feature**.
  - *The knowledge base*: four pages. *How CGP's Documentation Is Written* is a **fact about the
    project**; *Using the Knowledge Base with Your Agent* and *Contributing to CGP with an Agent* are
    **features**. They and the disclaimer are the only hand-written pages that link into this base.
  - *AI disclaimer*: the four levels of AI involvement, and the destination of every provenance note,
    so it closes the section. Specified in [ai-disclosure.md](../communication-strategy/ai-disclosure.md).

**The AI section keeps its two directions apart**: what CGP offers a reader working with an assistant
is a feature, and how CGP is built is a fact about the project, and a page that blends them reads as a
pitch or as a disclosure dressed up. The section stays at `docs/ai/`, because renaming it would move
every URL for no benefit, and the disclaimer stays in it rather than beside Contribute, because a
reader looking for provenance looks under AI first. **The navigation bar's "AI" entry is the one place
the site leads with the word**, tolerated as a label under
[message.md](../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these) on the
condition that nothing else above the fold does.

## Navigation and sidebar order

**The navigation bar carries Tutorials, Docs, Blog, and AI, plus a GitHub link, and gets no new
entry**: a reader looking for *why* looks in the documentation, and the sidebar is autogenerated from
the `docs/` tree, so a new category is a directory with a `_category_.json`, within the
[stock-Docusaurus policy](site.md#how-the-site-is-built).

**The sidebar follows the order a reader needs things:** Introduction, Quickstart, Overview,
Tutorials, Concepts, Comparisons, Reference, Projects, Tooling, Resources, Contribute, and AI.

- **The Quickstart is second** because the Introduction is the docs root, and a reader who wants to
  see CGP run should meet it before any argument.
- **Concepts follows Tutorials**, because a reader who meets eighteen idea pages before writing a line
  reads them as the theory CGP demands up front; after the tutorials, they are what a reader reaches
  for once a construct raises a question.
- **Comparisons sits beside Concepts**, because both are read away from the keyboard, and a Concepts
  page is where a reader with a prior model finds its comparison.
- **Reference follows them**, because a reader reaches for it once writing code.

**Name the category *Concepts*, never *Explanation* or *Understanding CGP***: "explanation" is the
documentation organizer's word, which Diátaxis advises against exposing, and *Concepts* matches the
knowledge base's own name for these documents.

## How each reader moves through the site

The [reader profiles](../communication-strategy/readers.md) describe who arrives; these paths say
where each should end up. A page that fits no path probably should not exist.

- **First-contact skimmer:** a post or the front page → *Quickstart* → *Hello World*. The only ask is
  the Quickstart, because this reader spends two minutes, not twenty.
- **Working developer:** front page → *Bypassing coherence* → *Hello World* → *Area calculation* →
  *Checking and debugging* → the reference, where they live once writing code. The checking tutorial
  is where this reader learns to read a CGP error or gives up.
- **Evaluator:** the front page's cost section → *Modularity Hierarchy* → Resources → the Projects
  index and the libraries' limitations pages. Candour and the Projects section, real systems the site
  hosts, persuade them; the [Hermes SDK](https://github.com/informalsystems/hermes-sdk/) is a
  [legacy resource](AGENTS.md#leave-legacy-resources-off-public-pages) the site leaves out.
- **Type-system and functional-programming reader:** *Bypassing coherence* → *Consumer and provider
  traits* → the comparison for the paradigm they know → the Hypershell section, the deep-dive posts,
  and the [RustLab transcript](blog/rustlab-2025-coherence.md), the best thing on the site for them.
- **Language-design reader:** the *Rust's own proposals* comparison → the RustLab transcript → the
  incoherent-Rust post once it publishes. The comparison is this reader's only orientation surface.
- **Dependency-injection, dynamic-language, or C++ reader:** the matching comparison first, instead of
  *Bypassing coherence*, then the working developer's path from *Hello World*.
- **Framework and library author:** the Overview's problems → the applied tutorial → the *Extensible
  records* and *Extensible variants* Concepts pages → the `builder` and `expression` example pages.
  The example pages land after the release, so until then the tutorial and the two Concepts pages
  carry this reader, which is a reason to draw the tutorial's scenario from an example that exercises
  extensible data.
- **Enthusiast:** the blog → Concepts → Contribute, whose top rung is publishing components of their
  own; one who wants to change CGP continues to *Contributing to CGP with an Agent*, the site's only
  guide to contributing code.
- **Reader who doubts agent-written documentation:** a provenance note or the AI section → the
  disclaimer → *How CGP's Documentation Is Written* → the knowledge base repository, persuaded by a
  process they can check rather than an assurance.
- **Working developer with an assistant:** the agent skill → *Using the Knowledge Base with Your
  Agent*, once a question outgrows the skill.

## Placing a new page

Three questions, asked in order, settle where a page goes:

1. **What is the reader doing while reading it?** Nothing: Concepts, or Comparisons when the subject
   is an idea from outside CGP the reader holds. Following along at a keyboard: a tutorial, or
   Projects when the subject is a program a project ships. Looking one thing up: the reference, or a
   project's reference when the name belongs to that project.
2. **Is it dated?** A statement about a moment (a release, an announcement, a talk) is a blog post; a
   statement about how things are is a docs page, corrected in place.
3. **Whose voice?** The author's first person means the blog, with Contribute's sponsorship section
   as the one standing exception.

The obligations that come with a new page, its record, a guide for a new kind, and its provenance
note, are in [AGENTS.md](AGENTS.md).

## What this document does not decide

**It decides which pages exist, what each is for, and where a reader goes next**, and nothing else.
The theme is in [visual-design.md](visual-design.md), within the
[policy of keeping Docusaurus stock](blog/new-website.md), and each page's content belongs to its
writing guide and the [communication strategy](../communication-strategy/README.md).

## Keeping it current

**This document leads the site**, so it goes stale when a page is added, moved, or repurposed without
being reflected here first. Revisit it whenever a page's job changes, a new kind of page appears, or
[evidence](../communication-strategy/evidence.md) shows a reader path not working. Remove a **new**
marker when its page lands; the redesign is finished when this inventory matches the page records.
