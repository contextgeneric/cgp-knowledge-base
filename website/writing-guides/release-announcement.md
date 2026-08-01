# Writing a release announcement

A release announcement tells readers what changed and why it matters. It is the site's most repeated
artifact — nine of the seventeen published posts are version releases — and it is the **first page type
specified here that speaks in the author's voice** rather than the project's, which changes more about
how it is written than the subject does.

- **Where it lives** — `blog/<date>-v<version>-release.md`, or a directory with an `index.md` when the
  post carries images
- **Voice** — the author's, first-person, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Status once published** — a dated historical record; see
  [Publishing, and what happens afterwards](#publishing-and-what-happens-afterwards)

## The two readers, and the tension between them

A release post is read by two audiences with opposite needs, and almost every way it can go wrong is a
failure to serve one of them.

The **existing user** wants to know what changed, whether anything they depend on broke, and what they
have to do about it. They are scanning for a construct name and a migration path, and they will not read
an introduction to CGP.

The **first-contact reader** arrives from a link aggregator, where the release post *is* the submission,
and has never heard of CGP. Every substantial post CGP has published was submitted to the Rust subreddit,
Lobsters, and Hacker News ([evidence.md](../../communication-strategy/evidence.md)), so a release
announcement is routinely somebody's first page — and the reception of those threads is where most of
what the project knows about its own framing comes from.

The tension is real and cannot be resolved by writing for the average of the two. The resolution is
**structural**: a release post opens on the *problem* the release addresses, which serves both readers at
once — the newcomer meets a concrete Rust pain rather than a changelog, and the existing user learns
immediately what the release is about. Orientation for the newcomer is then **one paragraph and a link**,
never a re-introduction to the paradigm. Migration detail for the existing user is a clearly-marked
section they can jump to. Neither reader is asked to wade through the other's material.

## Lead with one change

**A release post is about one thing.** Even when a release contains a dozen changes, the post leads with
the single most important one and treats the rest as a list at the end. This is the site's existing and
correct habit — the v0.8.0 draft is titled *"Grouping components with namespaces and paths"* and spends
its length on that one feature — and it is what makes a release post readable rather than a rendered
changelog.

Length follows the size of that one change rather than the size of the release: the v0.4.1 post runs
under 800 words because it introduces one crate, and the v0.5.0 post runs to nearly 5,000 because it
introduces a family of ideas and removes a trait. Neither is wrong. What is wrong is a post whose length
is set by the number of entries rather than by the weight of the lead.

The title carries this: **`CGP vX.Y.Z - <the one thing>`**, naming the change in plain words. A title that
says only "CGP v0.8.0 released" wastes the whole pitch for the aggregator audience, for whom the title is
often all they read.

## The shape

Seven parts, in this order. Only the front matter and the discussion links are mechanical; the rest is
the argument.

**Front matter.** `slug` (always — without one, Docusaurus publishes under a dated path rather than a
flat URL), `authors: [soares]`, and `tags: [release]`. A post that is also a deep dive carries
`deepdive` too. The full conventions, including the tag set, are in
[blog/README.md](../blog/README.md).

**The opening and the truncate marker.** Two or three sentences saying what shipped and what it is for,
then `{/* truncate */}`. This is the excerpt shown on the blog index and in previews, so it must stand
alone. Docusaurus warns on a post that omits the marker.

**Discussion links.** A short section linking the Reddit, Lobsters, Hacker News, and GitHub Discussion
threads. Added after submission rather than before, and worth doing every time: it is how a reader who
arrives later finds the conversation, and it is what makes the reception traceable for
[evidence.md](../../communication-strategy/evidence.md).

**The problem.** The heart of the post, and the part to spend effort on. Show what was painful before the
release, in code, at enough length that the reader feels it. The v0.8.0 draft does this best on the
site — it builds a social-media app's wiring table until it is visibly unmanageable, and only then
introduces namespaces — and its own internal document notes that this motivation section is the strongest
part of the draft and needs no change. **Problem before construct** is the same ordering every other CGP
surface uses, and it matters most here, because a feature announced without its motivation reads as
churn.

**The change.** What the release adds, shown on the same example. Use the modern idioms the
[guides](../../cgp/guides/README.md) teach, since a release post is the most-copied code on the site.
Name the constructs, link to the reference or docs.rs for their full syntax, and resist teaching the
paradigm around them.

**Breaking changes and migration.** A clearly-marked section naming every removal and rename with what
replaced it, taken from the release's entry in [releases/](../../releases/README.md) — whose **removal
ledger** dates every renamed or deleted construct and is the source of truth for this section. State
breakage plainly. A reader who discovers a removal from a compiler error rather than from the
announcement has been let down in the way that costs the most trust.

**What's next, and what is unfinished.** The author's closing register: what the release does not yet do,
what is coming, and what he would like input on. This is not filler — it is where several of the site's
best passages live, and it is the part that invites the reader into the project rather than at it.

## The voice, and what it permits here

This is the first guide for a page written in the **author's voice**, and the difference from the project
voice is not decoration. Read [author-personality.md](../../communication-strategy/author-personality.md)
before drafting; four of its habits matter especially here.

**First person, and personal where it is true.** "I want to be transparent about", "I have a feeling
that", "here is a little backstory" — these belong in a release post and would be wrong on a docs page.
The Hypershell post's aside about naming the project after a 2012 experiment is the register.

**Concede at length, not tactically.** The Hypershell post's Disadvantages section names the learning
curve, the error messages, the inability to load programs dynamically, and slow compile times — and on
the last one admits the evidence is only "rough experiments". A release post that names what the release
does not fix, and says plainly where the author is uncertain, is doing the thing that makes the rest
believable.

**Declare the length.** A long post opens with an estimated reading time and a section-by-section
preview. Depth is welcome; ambushing the reader with it is not.

**Enthusiasm attaches to sharing, not to the capability.** "I am thrilled to introduce" is the author's
own sentence and is fine. "Blazingly fast" and "incredibly powerful" are not, and the
[avoid list](../../communication-strategy/vocabulary.md) applies to a release post exactly as it applies
to a landing page.

## What must not be in a release announcement

**No re-introduction to CGP.** One paragraph of orientation and a link. A post that teaches the paradigm
before announcing the release has buried its own subject, and the tutorials do it better.

**No changelog dump.** The exhaustive list belongs in the repository's changelog and in
[releases/](../../releases/README.md). A post that leads with an enumerated list has no lead.

**No silent breakage.** Every removal and rename is named, with its replacement.

**No unbenchmarked performance claim.** "Faster" needs a number that can be cited, and CGP's honest claim
is almost always about compile-time-versus-runtime placement rather than speed.

**No claim that the release has shipped when it has not.** The v0.8.0 draft currently opens by saying
v0.8.0 "has been released", which is false until it is, and is the kind of error that is easy to leave in
a draft written months ahead.

## Publishing, and what happens afterwards

Five mechanical items go with publication, and the v0.8.0 draft's document records all five going wrong
at once, which is why they are listed rather than assumed. **Set the real date in the filename**, since
it fixes both the URL and the post's position in the index. **Set the `slug`.** **Repoint the
announcement bar** in `docusaurus.config.ts`, which is hardcoded and will otherwise keep promoting the
previous release. **Add the discussion links** once the post is submitted. And **register the post's
internal document** under [blog/](../blog/README.md) in the same change, per
[AGENTS.md](../AGENTS.md) — a post with no document has no recorded provenance.

A release is also the largest attention event the project gets, which has two consequences for what
travels with it. **Whatever the announcement links to should be ready before it publishes**, because a
release post is routinely a first-contact reader's landing page and the traffic does not come back — this
is the reason the v0.8.0 announcement and the site relaunch are
[one event](../AGENTS.md#the-redesign-lands-on-a-release-branch-all-at-once) rather than two. And
**nothing substantial publishes beside it.** Two significant pieces released together compete for the
same readers on the same day, in channels ranked by recency, so the second mostly takes attention from
the first and neither result says anything useful about how its framing landed. Space other writing out
after the release rather than bundling it in.

Then the post becomes **a dated artifact and is not edited into agreement with later releases**. This is
the rule that most distinguishes a release post from every other page specified in this directory: a docs
page describes the present and is corrected in place forever, while a release announcement records what
was true at a moment, and rewriting its snippets would make it claim the release shipped features it did
not. Drift is recorded in the post's internal document instead, and the
[blog catalog](../blog/README.md) carries a summary of the breaking changes that account for most of it
across the archive.

Two legitimate exceptions exist, and both belong to the user rather than to an agent. A heavily-read post
that is actively misleading may be **annotated** with a short dated note pointing at current material. A
post may be **superseded** by a later one, with a pointer added. Neither is a licence to rewrite.

## Checking a draft

**Read the title and the excerpt alone.** For much of the aggregator audience that is the whole post, so
they must name the one change in plain words and be intelligible to someone who has never heard of CGP.

**Find the problem section, and check it comes before the construct.** If the release's feature appears
before the pain it addresses, the post reads as churn.

**Find the breaking-changes section** and check it against the removal ledger in
[releases/](../../releases/README.md). A missing removal is the most damaging omission available here.

**Check that a newcomer is oriented in one paragraph** — not zero, and not five.

**Check the voice is the author's**, and that the closing section says something honest about what is
unfinished.

**Verify every snippet** against the source and the `/cgp` skill, and prefer the modern idioms — a
release post's code is the most widely copied on the site, and eight of the seventeen existing posts now
teach a provider form the project no longer recommends.
