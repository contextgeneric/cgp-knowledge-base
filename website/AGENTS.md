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

**One page is a sanctioned exception, and only one.** The
[AI disclaimer page](https://contextgeneric.dev/docs/ai/disclaimer) links to the knowledge base
repository, because the base is the subject it is disclosing: its argument is that CGP's documentation
is written against a public record whose rules and history a reader can go and check, and that argument
cannot be made while hiding the record. Neither reason behind the one-way rule applies there — the link
is a public GitHub URL that resolves for everyone, and exposing the material is the point rather than
an accident. The exception is to the repository as a whole, not to individual documents: that page links
the base's front door, never a path into a particular file, because a reader following a deep link lands
in prose written for agents with no idea what they are reading.

**The published agent skill is a second exception, and it is a different kind.** The skill pages under
`docs/ai/skills/` cite this base by deep GitHub URL roughly ninety times, and those links are
deliberate rather than tolerated: the pages *are* prose written for agents, the reader has been told so
before reaching them, and a reader who follows one lands exactly where the skill intended. That
exception is bounded to those pages, which nobody hand-writes — see
[the section below](#the-agent-skill-is-published-as-a-snapshot). No page you write may link here.

Two mechanics follow from the base's [link conventions](../AGENTS.md#writing-links). A link to a
published page is its live URL under `https://contextgeneric.dev`, since that is where a reader meets
it. A link to a page's *source file* is a GitHub URL on `main` in the
[`contextgeneric.dev`](https://github.com/contextgeneric/contextgeneric.dev) repository, never a
relative `../../cgp-website/...` path; when you need to *read* that file, prefer the local sibling
checkout at `../cgp-website`, per [sibling-projects.md](../sibling-projects.md).

## The agent skill is published as a snapshot

**The pages under `docs/ai/skills/` other than `index.md` are symlinks into the
[`cgp-skills`](https://github.com/contextgeneric/cgp-skills) repository, checked out as a submodule at
`docs/ai/skills/cgp-skills/` and pinned to one revision. Three rules govern them, and all three cut
against habits that are correct everywhere else on this site.**

**Never edit one.** They are symlinks: editing a page edits the skill's working tree in another
repository, where the change will either be lost or land somewhere nobody expected. A correction to the
skill is made in `cgp-skills` — which is itself built from this base, so a correction usually starts
here and propagates out, per [cgp/AGENTS.md](../cgp/AGENTS.md#what-the-synchronization-rule-means-here).

**Never bump the submodule pointer.** Advancing the snapshot is the author's decision, taken
deliberately and occasionally; it is not part of a skill change and not a tidy-up an agent performs on
its way past. A skill change lands in `cgp-skills` and stops there.

**Assume the snapshot is current, and do not read it.** When you need to know what the skill says, read
the `../cgp-skills` checkout, never the copy under `docs/`. The copy may be several revisions behind,
and treating it as a source is how a stale claim gets laundered back into this base as though it were
fact.

This is a standing exception to the [synchronization rule](../AGENTS.md#the-synchronization-rule), so it
is worth saying plainly why the exception is safe. **The snapshot exists for search visibility**, so
that a developer looking for CGP's agent skill finds it on the project's own site rather than only in a
GitHub repository. Against that purpose a lag of a few revisions costs nothing, while the usual cost of
staleness — a reader trusting a document that no longer matches the code — is carried by the page
itself, which tells the reader the repository is canonical. **A snapshot that lags is therefore not a
defect and needs no issue, no note, and no fix.**

## Consult communication-strategy before writing public prose

**Every change to website content is public writing, and public writing is governed by
[communication-strategy/](../communication-strategy/README.md).** That section is not optional advice
here; it is the specification for how CGP is presented, and the website is the single largest surface
it applies to. A page revised without it will drift out of the project's voice, reach for a framing the
audience has already rejected, or make a claim the Rust community will read as overselling.

**Start with the page's writing guide, when one exists.** The
[writing-guides/](writing-guides/README.md) subsection turns that strategy into a specification per
*kind* of page — what the page is for, what goes on it, in what order, and what must never appear —
and it is the more specific instrument, so it governs the page's shape where it speaks. When the task
is adding or moving a page rather than revising one, read
[information-architecture.md](information-architecture.md) first instead: it decides which surface a
page belongs to and what the reader does next, and a page placed without it will sit somewhere no
reader's path goes. Read the guide, then the page's own document for what the page currently is, then
the strategy documents below
for the material.

Which strategy document to read depends on what you are writing, and the mapping is worth stating
once. Read [author-personality.md](../communication-strategy/author-personality.md) and
[voice-and-register.md](../communication-strategy/voice-and-register.md) before any prose, because
the site speaks in the project voice while the blog speaks in the author's, and getting that wrong is
the most visible way a draft can be off-voice. Reach for
[formats.md](../communication-strategy/formats.md) for the playbook matching the artifact — the launch
post, the deep-dive, the README, the talk, the thread, the comparison — since it fixes the opening
move, the length, the dismissal to preempt, and the call to action. Reach for
[readers.md](../communication-strategy/readers.md) to name the single reader a page is written for
before outlining it, and for the
[comprehension barriers](../communication-strategy/readers.md#the-comprehension-barriers) that fix the
order in which concepts may be introduced to that reader. Reach for
[vocabulary.md](../communication-strategy/vocabulary.md) for which term to use and which to defer, so
the whole site reads as one voice, and [identity.md](../communication-strategy/identity.md) for any
line that describes CGP in one sentence, for the enhances-not-replaces frame, and for the headline
feature set. And reach for [message.md](../communication-strategy/message.md) whenever a page makes a
claim about what CGP is good for — its four halves are the pain, the capability, the objection, and
the boundary, and a page should satisfy all four.

The section's own governing rule applies unchanged: **honesty is the strategy**. Never publish an
invented benchmark, adoption figure, or quotation; never disparage another crate or language to
elevate CGP; and concede a genuine cost beside the benefit wherever the audience will look for it.

## Layer the depth; do not omit the advanced material

**A website page covers everything its subject supports. The layered structure exists to control the
*order* a reader meets things in, never to decide what gets left out.** This is the rule most easily
broken while trying to be kind to a beginner, and breaking it costs more than the kindness is worth: a
reader who needs an advanced form and cannot find it concludes the form does not exist, or that the page
cannot be trusted for anything they have not already verified elsewhere.

The obligation is sharpest on a [reference page](writing-guides/reference.md), where it is not a
preference but the section's contract. The site reference is
[canonical](writing-guides/reference.md#the-site-reference-is-canonical) — there is no fuller public
source to fall through to — so **a construct's page must cover every syntax form the macro accepts,
every option, and every default**, including the forms an author judges rare, legacy, or advanced. A
form that parses and is not on the page is a hole, exactly as a construct with no page at all is. When a
form is legacy, say so and say what replaced it; when it is advanced, put it lower on the page. Neither
is a reason to drop it.

The same rule governs the other tiers with their own thresholds. An
[explanation page](writing-guides/explanation.md) is about one idea rather than one construct, so it
carries the idea completely — including the parts that are hard — and links to the reference for the
mechanics it does not owe. A [tutorial](writing-guides/tutorial.md) is the one place selection is
legitimate, because a tutorial is defined by a teaching path and a beginner audience; even there, what
is left out is deferred to a linked page rather than left unmentioned.

Where the tension is real, resolve it with **structure rather than omission**. The reference page's
[layered descent](writing-guides/reference.md#the-layered-page) already provides the mechanism: a
beginner stops after *Usage* and *Examples*, and everything an advanced reader needs sits below,
marked. Move an advanced form down the page, put a grammar in its own section low on the page, mark a machinery
section as advanced. But keep it on the page.

Two habits make this checkable. **Enumerate against the parser, not against the previous draft**: a page
covering four of a macro's six accepted forms usually got there by copying an internal document that
covered four, so the count comes from the source. And **say when forms combine**, since a page that
documents each form in its own subsection quietly implies they are alternatives; if they compose, show
one example that composes them.

The knowledge base itself needs no such rule. Its documents are written for agents, so they always carry
everything, and this rule exists because the website is the one surface where a reader's inexperience is
a live consideration and "leave it out" is therefore a tempting answer.

## Verify code against current CGP, and never against a blog post

Any code that appears on a website page is bound by the [synchronization rule](../AGENTS.md#the-synchronization-rule)
exactly as a reference document's Expansion is: invoke the `/cgp` skill, verify the snippet against the
`cgp` source or its tests, and prefer the idioms the [guides](../cgp/guides/README.md) teach. The
richest source of already-verified snippets is [examples/](../examples/README.md), which exists partly
to be quoted, so draw on it rather than writing new code that then needs its own verification.

**The website repository carries a Rust crate whose job is to hold that verification, and a page you
write or revise puts its code there.** `example-code/` is a crate mirroring the `docs/` tree one file
per page — `docs/concepts/coherence.md` against `tests/concepts/coherence.rs` — so the check on a
snippet stops being "an agent compiled this once" and becomes "`cargo test` in that directory is
green". It is not part of the site: nothing renders it, no page links it, and its own
[README](https://github.com/contextgeneric/contextgeneric.dev/blob/main/example-code/README.md)
carries the conventions — one module per heading, elided bodies filled in with a comment saying so,
rejected snippets as `compile_fail` doctests, duplication between files preferred over a shared helper
neither page shows.

Three things about it are worth knowing before you reach for it. **It is filled in lazily**: a page
gets its file when someone writes, revises, or reviews that page, so a missing file means nobody has
been through that page yet rather than that the page is unverified. **It does not replace
`cargo cgp expand`** for a listing that shows *generated* code, which the crate can only check the
shape of. And **it is the website's alone** — the knowledge base's own snippets are not mirrored
there, since they are verified against the source directly and a second copy would be one more thing
to keep in step.

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

Three actions are legitimate instead, and outside the one case settled below the choice between them
belongs to the user rather than to you. A post may be **annotated**, with a short note at the top
pointing readers to current material — appropriate when a post is heavily read and actively misleading. A
post may be **superseded**, by writing a new post and updating the older one's pointer. Or the drift may
simply be **recorded here**, in the post's internal document, and left alone — which is the default, and
the right choice for release notes, whose whole value is historical. When a post is genuinely a
**published draft** rather than a finished artifact, the ordinary editing rules apply again; the
document for such a post says so explicitly.

One case is settled and needs no further authorization: **when a [deep dive](deep-dives/README.md) is
published, a pointer to it is added at the top of the post it grew out of.** That edit adds a link and
changes no claim, so it leaves the record intact while routing a reader who arrives from a search result
to the maintained version. Two things are *not* settled by it: a published post's **`slug` is never
changed**, because moving a live URL breaks every inbound link to it, and no snippet in the post is
rewritten.

Pages under `docs/` are the opposite case: they describe CGP as it is now, carry no date, and are
covered by document-the-present in full. Correct them in place, without a changelog note.

## The redesign lands on a release branch, all at once

**The site redesign is not published incrementally. It is written on the `v0.8.0` branch of the website
repository and goes live when that branch merges, together with the v0.8.0 release.** Two rules follow
and both are absolute while the campaign runs.

**Never commit redesign work to `main`.** The site deploys to GitHub Pages from `main` on every push,
so a page landed there publishes immediately — which would put a half-rebuilt site in front of readers
and spend the release's attention on it. The branch is also how previous releases were staged, so this
is the project's existing habit rather than a new one.

**Write every page as though v0.8.0 has already shipped.** Version pins name `0.8.0`, prose describes
the library as it is on that branch, and nothing hedges about an unreleased version or an alpha. The
whole site becomes true on the day the branch merges, which is what makes the two events one event. The
`0.8.0-alpha` pre-release the ecosystem repositories currently track is a fact about today rather than
about the site being written.

The corollary is that a correction which should reach readers *before* the release — something on the
live site that is actively wrong — is the one kind of change that goes to `main` as well, and is then
carried onto the branch. Raise it rather than deciding alone, since it costs a deploy of the current
site.

## Who drafts a page, and who reads it before it publishes

Agents draft the pages; the author reads the surfaces where voice and framing decide the outcome. That
split is a decision rather than a default, and it exists because this section's whole apparatus is
built to prevent [voiceless machine prose](../communication-strategy/README.md) and the redesign is
roughly a hundred pages of it.

**The author reads, in full, before publication:** the front page, every page of the *Concepts*
explanation tier, the reference index, the AI disclosure page, and every blog post. Most of these
carry the voice, make the argument, and are what a first-contact reader meets, so an off-voice paragraph
in one of them costs more than a wrong sentence anywhere else. The disclosure page is on the list for a
different reason: a wrong sentence there is a false claim about the project rather than about CGP, and
it is the page whose entire value is that it is accurate.

This list is the authoritative one, and it is quoted elsewhere — in
[tasks.md](tasks.md) and in
[ai-disclosure.md](../communication-strategy/ai-disclosure.md#the-two-claims-that-are-easiest-to-get-wrong),
which turns it into a public claim. Change it here and check those in the same edit.

**Everything else ships on the guides plus a spot check.** The construct reference is the bulk of the
work and the lowest risk: it is a mechanical port from internal documents that are already written and
verified, into the project voice, against a fixed six-section template. Draft it, check it against its
guide's five draft checks, and sample rather than read it end to end. Where a ported page turns out to
need a judgement call rather than a transformation — a *When to use it* section with no internal
guide behind it, a *Common Mistakes* entry that reads as a warning about the library — flag it for reading
rather than deciding alone.

## Disclosing AI use on a page

The site carries one page describing how AI is used across the project, and **a page written with AI
assistance links to the section of it that matches how that page was made.** The policy, the four levels,
and the wording are in
[ai-disclosure.md](../communication-strategy/ai-disclosure.md); what belongs here is the mechanics.

**One line at the foot of the page**, linking the specific section rather than the page as a whole, so
the note says which arrangement applies. A reference page and a blog post describe different things and
get different sentences. The note is a provenance fact rather than a warning, which is why it goes at the
bottom: at the top it primes a reader to discount everything beneath it.

**New pages only, and never a retroactive sweep.** A page written or substantially rewritten from now on
carries the note. An existing page does not get one unless the user asks, because attaching a note to a
page whose actual provenance nobody has checked is a guess presented as a disclosure — worse than the
silence it replaces. The older pages are not undisclosed in the meantime: the
[new-website post](blog/new-website.md) records that the site's text was LLM-refined throughout, which is
partial cover rather than a closed gap, since it speaks to refinement of what existed then rather than to
authorship or to anything added since.

**Record which level applies in the page's internal document**, since that is where the site's provenance
is already kept and the fact will not be recoverable from the page later.

**A scaffolded stub carries no note; it gets one when it is written.** A placeholder that already tells
the reader it is unwritten has disclosed the only thing about it worth disclosing, and stacking a
provenance note under a "not written yet" admonition tells them nothing further. The note is part of
filling the page in, not part of creating the placeholder.

**This is the website only, for now.** Other repositories get their disclosure after the redesign is
published, as separate work; do not add notes to another project's README or documentation in the
meantime.

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

For a page written or substantially rewritten from now on, the identifying facts at the top also carry
**how it was made** — which of the four levels in
[ai-disclosure.md](../communication-strategy/ai-disclosure.md) applies, in a few words. This is the only
place that fact survives: it is not recoverable from the page later, and the provenance note the page
carries names a level without saying who decided it applied. Omit it for pages that predate the rule
rather than guessing.

A tutorial document replaces the divergence section with the teaching contract the tutorial is under:
its objective, its prerequisites, the concepts it introduces and in what order, and the level of
explanation it pitches at. [tutorials/README.md](tutorials/README.md) states that shape in full.

A **writing guide** does not follow this template at all, because it describes a page that may not
exist yet rather than one that does. A guide states the job that kind of page has to do, its
structure section by section, what must never appear on it, how a draft is checked, and — where the
current page falls short of the guide — a concrete list of the gaps, so a redesign has a checklist.
[writing-guides/README.md](writing-guides/README.md) states the distinction in full.

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
[blog/README.md](blog/README.md), [tutorials/README.md](tutorials/README.md),
[writing-guides/README.md](writing-guides/README.md), or the catalog in [README.md](README.md) for a
top-level document — and in [../summary.md](../summary.md), in the same change that creates it.
Adding a page to the website means adding its document here in that same change; a page with no
internal document has no recorded provenance, which is the failure this section exists to prevent.

**A ported catalog is the one exception, and it is recorded as one entry rather than one per page.**
The Reference and Concepts sections each mirror a catalog in this base one page at a time, so a public
page's provenance is already fully determined by the internal document it was ported from and the
section's shared conventions — seventy-eight near-identical documents saying so would carry no
information and would go stale as a body. Each section therefore gets a single entry in
[site-structure.md](site-structure.md) covering the mapping, the conventions, and the current state,
and a page that needs something said about it *specifically* gets a paragraph inside that entry. This
exception reaches a section built by porting a catalog; it does not reach a page written on its own,
which still gets its own document.

Adding a page of a *kind* the site has not published before means adding a writing guide for it too,
before the page rather than after, since the guide is what a later revision is checked against.

Three documents track the redesign rather than a page, and all three are updated as work lands.
[information-architecture.md](information-architecture.md) carries the target page inventory, so a page
that is added, moved, or repurposed loses its **new** or **moved** marker there in the same change.
[redesign-queue.md](redesign-queue.md) is the defect list and [tasks.md](tasks.md) is the plan built on
it — the queue says what is wrong with a page, the plan says where the fix lands, what blocks it, and in
what order. For both: **remove** a completed entry rather than marking it done, and delete the document
once it is empty, per
[document-the-present](../AGENTS.md#document-the-present-not-the-history).
