# Writing a release announcement

A release announcement tells readers what changed and why it matters. It is the blog's most repeated
artifact, and the **only page type specified here that speaks in the author's voice** rather than the
project's, which changes more about how it is written than the subject does.

- **Where it lives**: `blog/<date>-v<version>-release.md`, or a directory with an `index.md` when the
  post carries images
- **Voice**: the author's, first-person, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Status once published**: a dated historical record; see
  [Publishing, and what happens afterwards](#publishing-and-what-happens-afterwards)
- **Reading**: the shared set and [the release post's row](README.md#the-release-post) of the
  reading map

## The two readers, and the tension between them

**A release post serves two readers with opposite needs.** The **existing user** scans for a construct
name and a migration path: what changed, what broke, and what to do about it. The **first-contact
reader** arrives from a link aggregator, where the release post is the submission, and has never heard
of CGP; every substantial CGP post has been submitted to the Rust subreddit, Lobsters, and Hacker News
([evidence.md](../../communication-strategy/evidence.md)).

**The resolution is structural, not an average of the two.** The post opens on the *problem* the
release addresses, which gives the newcomer a concrete Rust pain and tells the existing user at once
what the release is about. Orientation for the newcomer is **one paragraph and a link**: it names
**Context-Generic Programming** in full beside a plain description, links the Introduction, and uses or
echoes the tag line, as
[the naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page)
asks of a post before it publishes. Migration detail is a clearly marked section the existing user can
jump to.

## Give the release a clear lead

**A release post needs a clear argument, with a concrete problem that makes its main feature worth
reading about.** That does not require the longest explanation first: short announcements about
tooling and documentation can come before a technical walkthrough readers may skip, as the v0.8.0 post
does at the author's request, with namespaces still its main worked example. Connect several
announcements through the release's purpose, focused on what readers gain and where they can try it,
rather than giving every changelog entry an equal explanation.

**Length follows the depth the main explanation needs, not the number of release entries.**

**The title names the news in plain words**: `CGP vX.Y.Z - <the main improvement>`, or a short set of
independent improvements when those form the opening, matching what readers meet first. "CGP v0.8.0
released" wastes the pitch. A search result shows roughly the first sixty characters, so the
improvement must fit inside them, per
[seo.md](../seo.md#the-longest-titles-are-truncated-before-they-say-anything).

## The shape

The parts below build the announcement. Short tooling and documentation sections may sit before the
main problem-and-solution walkthrough. Only the front matter and the discussion links are mechanical.

- **Front matter**: `slug` (always, or Docusaurus publishes under a dated path), `authors: [soares]`,
  `tags: [release]`, and a written `description` saying what the release is for, since a derived one
  is cut from the first source line. A post that is also a deep dive carries `deepdive` too. The tag
  set and other conventions are in [blog/README.md](../blog/README.md).
- **The opening and the truncate marker**: two or three sentences saying what shipped and what it is
  for, then `{/* truncate */}`. The excerpt shows on the blog index and in previews, so it stands
  alone; Docusaurus warns on a post without the marker.
- **Discussion links**: a short section linking the Reddit, Lobsters, Hacker News, and GitHub
  Discussion threads, added after submission, so a later reader finds the conversation and the
  reception stays traceable for [evidence.md](../../communication-strategy/evidence.md).
- **The problem**, the heart of the post: what was painful before the release, in code, at enough
  length that the reader feels it. Repeated declarations may be shortened without losing the reasoning.
  The v0.8.0 post's [record](../blog/v0-8-0-release.md) holds the causal progression a revision must
  preserve. **Problem before construct** matters most here, because a feature announced without its
  motivation reads as churn.
- **The change**: what the release adds, on the same example, in the modern idioms the
  [guides](../../cgp/guides/README.md) teach, since a release post is the site's most-copied code. Name
  the constructs and link the reference or docs.rs for their syntax, without teaching the paradigm
  around them.
- **Breaking changes and migration**: a clearly marked section naming every removal and rename with
  its replacement, from the release's entry in [releases/](../../releases/README.md), whose **removal
  ledger** is the source of truth. State breakage plainly; a reader who learns of a removal from a
  compiler error has been let down at the highest cost in trust.
- **What's next, and what is unfinished**: what the release does not yet do, what is coming, and what
  the author would like input on, which invites the reader into the project.

## The voice, and what it permits here

**Read [author-personality.md](../../communication-strategy/author-personality.md) before drafting**;
four of its habits matter most here:

- **First person, and personal where it is true**: "I want to be transparent about", "here is a little
  backstory". The Hypershell post's aside about the project's name is the register.
- **Concede at length, not tactically.** Name what the release does not fix and where the author is
  uncertain, as the Hypershell post's Disadvantages section does down to "rough experiments" for
  compile times; that is what makes the rest believable.
- **Declare the length**: a long post opens with an estimated reading time and a section-by-section
  preview.
- **Enthusiasm attaches to sharing, not to the feature.** "I am thrilled to introduce" is fine;
  "blazingly fast" and "incredibly powerful" are not, per the
  [avoid list](../../communication-strategy/vocabulary.md).

## What must not be in a release announcement

- **No re-introduction to CGP**: one paragraph of orientation and a link.
- **No changelog dump.** The exhaustive list belongs in the repository's changelog and
  [releases/](../../releases/README.md); a post that leads with a list has no lead.
- **No silent breakage**: every removal and rename is named with its replacement.
- **No unbenchmarked performance claim.** "Faster" needs a citable number, and CGP's honest claim is
  almost always about compile-time-versus-runtime placement rather than speed.
- **No hedged or pre-release wording.** On the release branch, write official versions as already
  shipped, per [the branch rules](../AGENTS.md#the-redesign-lands-on-a-release-branch-all-at-once); the
  post and site publish only after both releases exist, and that gate stays out of the draft.

## Publishing, and what happens afterwards

**Publication has mechanical steps; check each explicitly:**

- **Set the real date in the filename**, which fixes the URL and the post's place in the index.
- **Set the `slug`.**
- **Repoint the announcement bar** in `docusaurus.config.ts`, which is hardcoded.
- **Add the discussion links** once the post is submitted.
- **Register the post's internal document** under [blog/](../blog/README.md) in the same change, per
  [AGENTS.md](../AGENTS.md).

**Two items belong to the release rather than the post:**

- **Re-pin the `cgp` version wherever the site names it**: every tutorial's `Cargo.toml` snippet, and
  the `example-code` crate, which takes `cgp` from the repository's `main` until the release is on
  crates.io. A pin to a version crates.io lacks is right on the branch and broken the moment a reader
  copies it, so the pin and the release ship together.
- **Confirm the sitemap and submit it**, per [seo.md](../seo.md#the-work-in-order), the one search task
  that cannot be done early.

**A release is the project's largest attention event**, so whatever the announcement links to is ready
before it publishes, which is why the v0.8.0 announcement and the site relaunch are
[one event](../AGENTS.md#the-redesign-lands-on-a-release-branch-all-at-once). And **nothing substantial
publishes beside it**: two pieces released together compete for the same readers in channels ranked by
recency, and neither result says how its framing landed. Space other writing out after the release.

**Then the post becomes a dated artifact, not edited into agreement with later releases**: rewriting
its snippets would make it claim the release shipped features it did not. Drift is recorded in the
post's internal document, and the [blog catalog](../blog/README.md) summarizes the breaking changes
behind most of it. Two exceptions belong to the user, not an agent: a heavily read, actively
misleading post may be **annotated** with a short dated note pointing at current material, and a post
may be **superseded** by a later one with a pointer added. Neither licenses a rewrite.

## Checking a draft

- **Read the title and the excerpt alone.** For much of the aggregator audience that is the whole post,
  so they name the release's practical improvements in plain words, intelligible without CGP.
- **Find the problem section**, and check it comes before the construct.
- **Find the breaking-changes section** and check it against the removal ledger in
  [releases/](../../releases/README.md); a missing removal is the most damaging omission here.
- **Check that a newcomer is oriented in one paragraph**, not zero and not five.
- **Check the voice is the author's**, and that the closing says something honest about what is
  unfinished.
- **Verify every snippet** against the source and the `/cgp` skill, in the modern idioms, since many
  older posts teach a provider form the project no longer recommends, per the
  [blog catalog](../blog/README.md).
