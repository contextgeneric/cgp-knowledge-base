# AGENTS.md — the CGP website

This directory holds the knowledge base's meta-documentation for the public website at
<https://contextgeneric.dev>. Read [README.md](README.md) for what the section is and how the site is
organized, and the base-wide [../AGENTS.md](../AGENTS.md) for the rules every section shares — the
synchronization rule, verifying against the source, document-the-present, how links are written, and
how a document registers itself. The rules below add what is specific to this section, and they cover
two distinct activities that must not be confused: **maintaining these internal documents**, and
**maintaining the website itself**.

## The one-way link rule

The website may never link into the knowledge base, and this constraint governs everything else here.
A website page is read by the public; the knowledge base is internal agent documentation, full of
unfinished work, known defects, and vocabulary that assumes the `/cgp` skill. Publishing a link into it
would expose material that was never written for that audience and would break for every reader who
does not have this repository. So a website page cites only public resources: the
[`cgp`](https://github.com/contextgeneric/cgp) repository, [docs.rs](https://docs.rs/cgp), the
[CGP Patterns book](https://patterns.contextgeneric.dev/), other pages on the site itself, and ordinary
external sources.

Links run the other way instead. A document *here* links freely into the rest of the base and out to
the public page it describes, so an agent starting from a page always reaches the material behind it.
The practical consequence is that **the internal document is the only place a page's provenance can be
recorded**, which is why creating a page without creating its document leaves that provenance nowhere.

Two mechanics follow from the base's [link conventions](../AGENTS.md#writing-links). A link to a
published page is its live URL under `https://contextgeneric.dev`, since that is where a reader meets
it. A link to a page's *source file* is a GitHub URL on `main` in the
[`contextgeneric.dev`](https://github.com/contextgeneric/contextgeneric.dev) repository, never a
relative `../../cgp-website/...` path; when you need to *read* that file, prefer the local sibling
checkout at `../cgp-website`, per [sibling-projects.md](../sibling-projects.md).

## Consult communication-strategy before writing public prose

**Every change to website content is public writing, and public writing is governed by
[communication-strategy/](../communication-strategy/README.md).** That section is not optional advice
here; it is the specification for how CGP is presented, and the website is the single largest surface
it applies to. A page revised without it will drift out of the project's voice, reach for a framing the
audience has already rejected, or make a claim the Rust community will read as overselling.

Which document to read depends on what you are writing, and the mapping is worth stating once. Reach
for [formats.md](../communication-strategy/formats.md) for the playbook matching the artifact — the
launch post, the tutorial, the README and landing page, the talk, the thread, the comparison — since
it fixes the opening move, the length, the dismissal to preempt, and the call to action. Reach for
[reader-profiles.md](../communication-strategy/reader-profiles.md) to name the single reader a page is
written for before outlining it, and [technical-barriers.md](../communication-strategy/technical-barriers.md)
for the order in which concepts may be introduced to that reader. Reach for
[vocabulary.md](../communication-strategy/vocabulary.md) for which term to use and which to defer, so
the whole site reads as one voice, and [tag-lines.md](../communication-strategy/tag-lines.md) for any
line that describes CGP in one sentence. Reach for [selling-points.md](../communication-strategy/selling-points.md),
[problems-solved.md](../communication-strategy/problems-solved.md), and
[skepticism.md](../communication-strategy/skepticism.md) together whenever a page makes a claim about
what CGP is good for, because those three are three views of one reader and a page should satisfy all
of them. And reach for [positioning.md](../communication-strategy/positioning.md) wherever a page must
draw CGP's boundary honestly.

The section's own governing rule applies unchanged: **honesty is the strategy**. Never publish an
invented benchmark, adoption figure, or quotation; never disparage another crate or language to
elevate CGP; and concede a genuine cost beside the benefit wherever the audience will look for it.

## Verify code against current CGP, and never against a blog post

Any code that appears on a website page is bound by the [synchronization rule](../AGENTS.md#the-synchronization-rule)
exactly as a reference document's Expansion is: invoke the `/cgp` skill, verify the snippet against the
`cgp` source or its tests, and prefer the idioms the [guides](../cgp/guides/README.md) teach. The
richest source of already-verified snippets is [examples/](../examples/README.md), which exists partly
to be quoted, so draw on it rather than writing new code that then needs its own verification.

**Never take current syntax from an existing blog post.** Almost every post on the site predates
v0.8.0, and the drift is not cosmetic: posts published as recently as 2026 still show
`#[cgp_context]`, `cgp_preset!`, `#[cgp_inherit]`, `HasCgpProvider`, the `Async` trait, `ProvideType`,
`symbol!`, `Char`, and `#[cgp_provider]`-style inside-out provider impls, none of which are current.
Each blog document's divergence section names what is stale in that post; read it before quoting the
post's code anywhere.

When a construct's age is the question rather than one post's accuracy, the faster answer is the
**removal ledger** in [releases/](../releases/README.md), which dates every renamed or deleted
construct in one table and links to the release that changed it. Reach for it whenever a page, an
issue, or a reader's code uses something you do not recognize.

## Do not rewrite history

A published blog post is a dated artifact, and the base's [document-the-present](../AGENTS.md#document-the-present-not-the-history)
rule does **not** license editing one into agreement with current CGP. A release announcement records
what a release did at the time; rewriting its snippets to v0.8.0 syntax would make it claim that
v0.4.0 shipped features it did not, and would destroy the record the post exists to keep. Leave
published posts as they stand.

Three actions are legitimate instead, and the choice between them belongs to the user rather than to
you. A post may be **annotated**, with a short dated note at the top pointing readers to current
material — appropriate when a post is heavily read and actively misleading. A post may be
**superseded**, by writing a new post and updating the older one's pointer. Or the drift may simply be
**recorded here**, in the post's internal document, and left alone — which is the default, and the
right choice for release notes, whose whole value is historical. When a post is genuinely a
**published draft** rather than a finished artifact, the ordinary editing rules apply again; the
document for such a post says so explicitly.

Pages under `docs/` are the opposite case: they describe CGP as it is now, carry no date, and are
covered by document-the-present in full. Correct them in place, without a changelog note.

## The document template

Every document in this section follows one shape, so an agent can find the same fact in the same place
across all of them. Open with a level-one heading naming the page, then a one-sentence summary of what
the page is and where it currently stands. Follow with a short framed list of the page's identifying
facts — its live URL, its source file, its publication date and tags where it has them, and a one-word
status. Then develop these sections in prose:

- **What it covers** — the page's content and structure, at enough depth that an agent can decide
  whether it is the page they need without opening it.
- **How it relates to the knowledge base** — which documents own the material the page presents,
  linked. This is the section the whole directory exists for, so be generous: point at the reference
  document for each construct the page names, the concept for each idea it explains, the example that
  carries the same scenario in verified form, and the communication-strategy document that governs its
  framing.
- **Where it diverges from current CGP** — for a blog post or any dated page, the concrete list of
  constructs, names, and claims that no longer hold, each with what replaced it. Omit this section
  only for a page that is current.
- **Maintaining it** — what a revision must preserve and what it must not do.

A tutorial document replaces the divergence section with the teaching contract the tutorial is under:
its objective, its prerequisites, the concepts it introduces and in what order, and the level of
explanation it pitches at. [tutorials/README.md](tutorials/README.md) states that shape in full.

## Status vocabulary

Use exactly one of five words for a page's status, so the value is scannable and comparable across
documents. **Current** means the page describes CGP as it is now and its code compiles against v0.8.0.
**Historical** means the page is a dated record — a release note, an announcement — that is correct
about its own moment and is not expected to track the library. **Outdated** means the page presents
itself as current guidance but no longer is, which makes it a defect worth raising with the user.
**Draft** means the page is published but unfinished. **Superseded** means a later page has replaced
it and it is kept for the record.

## Registering a document

Register every new document in the catalog of its immediate index —
[blog/README.md](blog/README.md), [tutorials/README.md](tutorials/README.md), or the catalog in
[README.md](README.md) for a top-level document — and in [../summary.md](../summary.md), in the same
change that creates it. Adding a page to the website means adding its document here in that same
change; a page with no internal document has no recorded provenance, which is the failure this
section exists to prevent.
