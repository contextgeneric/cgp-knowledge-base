# CGP Communication Strategy

This directory holds the guidance for writing anything public-facing about CGP — a landing page, a
tutorial, a README, a blog post, a talk, a thread. Where the rest of the knowledge base records what
CGP *is*, this section records how to *present* it: which ideas to lead with, how to frame what will
feel unfamiliar, which misunderstandings to head off, and — the point this section now organizes
itself around — **how to sound like the person whose project this is**.

## The reader and the failure mode

These documents are written by agents, but their readers are as much human as machine, and the human
reader is a **CGP advocate**: someone who understands CGP deeply and wants it to reach people. The
defining assumption about that reader is that their expertise is lopsided — strong in the technology,
often near-zero in the disciplines that decide whether the technology is ever heard about. A gifted CGP
practitioner is not automatically a good explainer of CGP, and is usually the opposite, because of the
curse of knowledge. So the section teaches the non-technical craft to a reader who has never studied
it, spelling out what a marketer takes for granted and anchoring it in terms a systems programmer
already trusts.

The failure mode this section exists to prevent has two halves, and they pull in opposite directions.
One is **hype**: a claim CGP cannot support, shown to the audience most able to catch it, which costs
more than saying nothing. The other, subtler and now more common, is **voicelessness**: fluent,
confident, adjective-rich copy that no human wrote and no reader trusts. An agent following
generic marketing advice reliably produces the second, which is why
[author-personality.md](author-personality.md) sits at the head of the section and governs everything
below it.

## Two decisions that shape everything here

**CGP speaks in a layered voice.** The website — homepage, docs, tutorials — speaks as the project:
plain, addressed to the reader, no first-person narration. The blog speaks as the author: first-person,
personal, candid to a degree most projects would not allow. That split is deliberate, and the
inconsistency between a docs page and a blog post is a feature, because a reader can tell which one is
a person talking. [voice-and-register.md](voice-and-register.md) works it out at the paragraph level.

**CGP enhances Rust's trait system; it does not replace it.** This is the frame every level of the
identity reinforces, from the tag line down to a feature title, and it is not a hedge bolted onto a
bolder claim — it is the accurate description and the one that earns this audience. It also has
empirical backing: the community's named fear for Rust's future is growing complexity, so "still
ordinary Rust", gradual adoption, and a sympathetic account of what the trait system already does are
answers to a stated anxiety rather than pleasant framings. [identity.md](identity.md) carries the
frame; [evidence.md](evidence.md) carries the evidence.

## Principles from the non-technical craft

Promoting CGP well depends on a body of knowledge that has nothing to do with CGP, and this section
makes it explicit for a reader who has never needed it. The terms of art are defined, with a
programmer's analogy for each, in the
[vocabulary of the craft](vocabulary.md#the-vocabulary-of-the-craft). What follows are the principles
themselves, stated plainly.

The one to internalize before all others is the **curse of knowledge**: the more completely you
understand CGP, the worse your instinct for explaining it to someone who does not. Expertise erases the
memory of confusion, so the expert leads with the mechanism they find elegant, uses vocabulary that is
precise to them and opaque to everyone else, and skips the motivating problem because it feels too
obvious to say. Nearly every failure this section warns against traces back to it, and the correction
is always the same: write for the reader's current knowledge, not your own.

From **marketing** comes the discipline of getting the right idea into the right head in the right
words, and its first law is that the reader — not the author — decides what a thing *is*. A reader
meeting CGP does not build an understanding from scratch; they pattern-match it in seconds to the
nearest category they know ("oh, it's a DI framework", "it's macro magic"), and that snap category, not
your careful explanation, is what they remember and repeat. Positioning is choosing that category for
them before they choose a dismissive one, which is why the wording of a one-liner matters out of all
proportion to its length. Four consequences recur: **lead with the benefit, not the feature**;
**attention is scarce and adversarial**, so the first line carries most of the message; **framing
decides the reaction**, because the same true fact worded two ways produces opposite responses; and
**differentiation answers "why this and not that"**.

From **public communication** comes clarity and consistency at scale, and it rewards nearly the
opposite of what technical writing trains: precision and completeness, the virtues of a specification,
bury the point in a pitch. Write for **one reader**, not everyone. Prefer **clarity over
completeness** — one vivid idea a reader keeps beats five accurate ideas they forget. Make it
**concrete, and make it a story**, because a before-and-after on real code outperforms any adjective.
And keep **one voice**, using the same words for the same ideas, so scattered pieces reinforce one
another. CGP qualifies the completeness principle in one way worth flagging: it governs the *entry* to
a piece rather than its depth, because long-form depth is part of this project's voice, and the rule
that makes length work is to declare it up front rather than to cut it.

From **developer relations** comes the recognition that this audience has been marketed to badly its
whole career and has grown expert at detecting it, so the rules invert: it rewards restraint and
punishes hype, and its trust, once lost, is not won back by the next post. **Honesty is not a
constraint on the strategy but the strategy itself** — an overclaim, a strawman of a competing tool, or
a hidden cost does more damage than silence, because the reader who catches it discounts everything
else. **Show, don't tell**, and let peers do the telling, since social proof persuades where self-praise
cannot. **Concede the costs**, including where a simpler tool is the better choice. **Meet developers
where they are**, since condescension and hype both read as disrespect. **Match the ask to the reader's
stage**. And **beware the pile-on**, whose defence is the same as the honest move.

## The catalog

The section is deliberately small: eight documents, each dense, so a writer reads a whole subject in one
place rather than assembling it from cross-links. Read them in this order the first time. The authoring
rules live in [AGENTS.md](AGENTS.md).

- [The author's personality and preferences](author-personality.md) — who CGP's author is as a writer,
  the habits evidenced by his published work, and the preferences he has stated. **Read this first**;
  every other document is downstream of it, and where a rule elsewhere conflicts with it, this one wins.
- [Voice and register](voice-and-register.md) — the layered voice model (project on the site, author on
  the blog), the sentence-level register, the four structural moves that make CGP prose work, and the
  habits that mark a draft as machine-written.
- [Identity](identity.md) — the settled tag line analyzed word by word, the enhances-not-replaces frame,
  the pitch that must follow the line, and the curated headline feature set for a front page.
- [Readers](readers.md) — the audience model: who reads about CGP by Rust experience, by imported mental
  model, and by role; plus the comprehension barriers that stop a willing reader from following, and the
  teaching move that lowers each.
- [The message](message.md) — everything a piece says about CGP: the concrete pains it removes, the
  capabilities worth advertising, the objections readers bring and how to answer each, and the boundary
  beyond which a plainer tool wins. Four views of one reader, kept together so an edit to one checks the
  others.
- [Vocabulary](vocabulary.md) — the canonical word list: which term to use for each idea, which to defer,
  which to avoid and why; plus the glossary of the non-technical craft. This document resolves any
  phrasing disagreement between the others.
- [Formats](formats.md) — per-artifact playbooks for the launch post, deep-dive, README, talk, thread,
  and comparison, the ready answers for a discussion thread, the conversion ladder, and annotated model
  drafts showing the whole apparatus at work.
- [Evidence](evidence.md) — the citable facts: what the Rust community measurably worries about and
  rewards, which conversations draw attention, how CGP's own posts and talk were received, and the
  lessons in that reception. The section's single home for external citations.

## Where this guidance gets spent

Nearly all of it ends up on the public website, so [website/](../website/README.md) is the practical
companion to this section, and the traffic runs both ways.

Read **outward** from here when writing: the website's
[writing guides](../website/writing-guides/README.md) turn this guidance into per-page-type
instructions, and the [homepage guide](../website/writing-guides/homepage.md) and
[tutorial guide](../website/writing-guides/tutorial.md) are where the homepage and tutorial playbooks
actually live. The rest of that section documents <https://contextgeneric.dev> page by page — one
document per blog post, one per tutorial series, one for the configuration and standalone pages — each
recording which document here governs its framing.

Read **inward** to here when the question is whether the guidance still matches reality. The website's
per-page documents record what the project has actually published and how it landed, which makes them a
source of evidence rather than only a destination for advice: the
[RustLab transcript](../website/blog/rustlab-2025-coherence.md) is a delivered instance of the talk
playbook, the [tutorial documents](../website/tutorials/README.md) record teaching contracts that
[readers.md](readers.md) predicts, and the [blog catalog](../website/blog/README.md) is the fullest
inventory of what has been said publicly in CGP's name. A claim here about "what works" should be
checkable against something published there.

## Relationship to related work

This section is the natural companion to [related-work/](../related-work/README.md), and the two are
read together when preparing public writing. A related-work document explains one external idea —
dependency injection, type classes, reflection — faithfully, records what its users like and dislike,
and positions CGP against it; a communication-strategy document generalizes across those comparisons
into audience-level guidance. When a related-work document records a sentiment — that Rust developers
reach for Dagger to escape reflection's runtime cost, say — this section turns it into a reader trait an
author can plan around. Read the matching related-work document for the depth of a comparison; read
here for the shape of the audience.
