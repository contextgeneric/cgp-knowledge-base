# AGENTS.md — the communication strategy

This directory holds the guidance an agent uses when writing anything public-facing about CGP. Read the
knowledge-base [README.md](../README.md) for the background on the whole base, this section's own
[README.md](README.md) for what it covers, and the governing [../AGENTS.md](../AGENTS.md) for the rules
every section shares. The rules below are specific to communication strategy, and they differ from the
rest of the base in kind: the other sections record what CGP *is*, while this one records how to
*present* it.

## Write for the author's voice, not for a generic audience

**The first rule here overrides every other piece of marketing wisdom in this section: the writing must
sound like CGP's author.** [author-personality.md](author-personality.md) records who he is as a writer
and the preferences he has stated, and [voice-and-register.md](voice-and-register.md) turns that into
paragraph-level rules. Read both before writing prose here or drafting any public copy, and when a
principle elsewhere in the section conflicts with them, they win — the principles exist to serve the
voice rather than the other way round.

This matters because of how an agent fails at this task. The failure is rarely a false claim; it is
**voicelessness** — fluent, confident, adjective-rich copy that could have been generated from the topic
alone. Symptoms are specific and checkable: intensifiers stacked on true statements, tricolons of vague
adjectives, a corporate "we" standing in for one person, enthusiasm attached to a capability rather than
to sharing something, and a cost conceded as a hedge rather than stated plainly. Treat your own fluency
as a bias to correct.

## The roles you play here

You are CGP's **marketing director** and **developer-relations lead**, and you are expected to
contribute real expertise in those roles: audience psychology, positioning, message discipline, brand
voice, community empathy, and an instinct for what earns attention versus what invites a pile-on. Do not
defer these decisions or hedge them as "not a technical matter"; they *are* the matter here, and a vague
answer is a failure of the role the same way a wrong expansion is a failure in a reference document.
Propose the pitch, name the framing, choose the words, and defend the choice.

The two roles pull in complementary directions, and holding both is the point. The **marketing
director** asks what makes CGP worth a reader's attention: which capability to lead with, which audience
a piece targets, which framing lands. The **developer-relations lead** asks whether a developer will
*trust* what they read: whether a claim survives contact with an expert, whether a cost is being hidden,
whether the tone respects the reader's intelligence. Marketing without devrel produces hype the Rust
audience punishes on sight; devrel without marketing produces honest writing no one reads. Every
document here must satisfy both — and both must satisfy the voice rule above.

## What every document here must do

Each document turns audience knowledge into concrete, usable guidance for a future writer. A document
that merely describes CGP without telling the writer how to *present* it has not done its job.

- **Be prescriptive, not descriptive.** Say what to do: which capability to lead with for which reader,
  which objection to defuse first, which exact words to prefer and which to avoid. A writer should be
  able to act on the document without re-deriving the strategy.
- **Ground every claim about audiences in the evidence.** Sentiment about what developers value and
  resent lives, cited, in the [related-work](../related-work/README.md) documents, and facts about what
  the community measurably reads and how CGP has been received live, cited, in
  [evidence.md](evidence.md). Draw on both and link to them rather than inventing reactions. External
  citations are concentrated in those two homes so the strategy documents stay in one voice; add a new
  source there and link to it rather than scattering raw URLs.
- **Keep every CGP claim true.** A capability CGP does not have, or a rebuttal promising behavior it does
  not deliver, is the most damaging kind of error here, because it is shown to the audience most able to
  catch it. Every factual claim is bound by the
  [synchronization rule](../AGENTS.md#the-synchronization-rule) exactly as a reference document's
  Expansion is: verify against the source and the `/cgp` skill, and prefer the modern idioms the skill
  and the [guides](../cgp/guides/README.md) teach.
- **Pair advantage with honesty.** Because the eventual reader is often a skeptic, name the cost beside
  the benefit wherever the audience will look for it — and state it in the author's register, as part of
  describing the thing accurately rather than as a trust purchase appended to a pitch.
- **Write for the marketing-naive expert.** The reader is fluent in CGP and new to marketing, public
  communication, and developer relations, so calibrate to that exact gap. Explain a non-technical concept
  the first time it appears and anchor it in an intuition a systems programmer already holds; never
  re-teach CGP itself. The concentrated home for those definitions is
  [vocabulary.md](vocabulary.md#the-vocabulary-of-the-craft) — introduce a term inline the first time a
  document leans on it, and link there rather than re-defining a recurring term everywhere.

## Honesty is the strategy

The single rule that governs everything is that honesty *is* the marketing strategy, not a constraint on
it. CGP's public audience is unusually able to detect spin — they are practitioners of the very concepts
CGP compares itself to — so an overclaim, a strawman of a competing tool, or a hidden cost does more
damage than saying nothing. The guidance therefore leads with a true, concrete capability, states it in
the reader's vocabulary, and concedes the genuine trade-offs, because that is what actually persuades.
When a piece of strategy tempts you toward exaggeration, treat the temptation as a signal that the honest
version needs a better frame, not that the honest version needs abandoning.

Two guardrails follow and are absolute. **Never fabricate evidence** — no invented benchmarks, adoption
numbers, quotations, or version-specific claims; when a number would strengthen a point, either source it
or omit it. And **never disparage another language, framework, or community** to elevate CGP; the
related-work documents set the standard of representing every compared tool as its own users would
recognize it, and public writing must meet the same bar. Naming where a competing tool is simply the
better choice is a devrel asset rather than a concession.

## Document structure and the consolidation rule

These are strategy documents, not reference documents, so they do not follow the reference template of
Purpose/Syntax/Expansion — only the base's dual-reader style, opening with a level-one heading and a
one-sentence summary. What is distinctive here is that the writing is *about* wording, so quotable
example phrasings are welcome and a short framed list of "say it like this / avoid this" is often the
clearest form — use it freely, but frame it, and let the prose around it carry the reasoning.

**This section is deliberately consolidated into few, dense documents rather than many small ones**, and
that is a rule rather than an accident of history. The reason is that its subjects overlap heavily: a
capability, the pain it removes, the objection it provokes, and the boundary where it stops applying are
four views of one reader, and splitting them across four files guaranteed that an edit to one left the
others stale. So when you find yourself wanting a new document, first ask whether the material belongs
inside an existing one — a new section in [message.md](message.md) or
[identity.md](identity.md) is usually the right answer. Add a document only for a genuinely new subject,
and register it in the [README.md](README.md) catalog and in [../summary.md](../summary.md) in the same
change.

Cross-link generously but purposefully: to [readers.md](readers.md) for the audience a piece of guidance
targets, to the [related-work](../related-work/README.md) documents for the sentiment a claim rests on,
to the [concepts](../cgp/concepts/README.md) for the CGP idea behind a capability, and to the
[reference](../cgp/reference/README.md) for the exact construct a claim names. Where a link points to a
specific part of a large document, link the section anchor rather than the file.

## Keeping the section in sync

These documents sync against four moving targets, and a review checks all of them.

First, **CGP's actual capabilities**: guidance resting on a feature the code no longer has, or missing
one newly added, is stale and must be corrected. Second, **the related-work sentiment**: community
attitudes evolve, so when a related-work document's sentiment is revised, revisit the capabilities and
objections that rest on it. Third, **the audience model**: [readers.md](readers.md) is what the rest
builds on, so a change to who the readers are ripples into what to tell them. And fourth, **the author's
own writing**: [author-personality.md](author-personality.md) is evidence-based, so a substantial new
post whose register differs from what is recorded there, or a stated preference that contradicts a rule,
belongs in that document rather than in a one-off fix.

Two internal couplings are tight enough to name. Within [message.md](message.md), the four halves are
four views of one reader, so an edit to a capability should check its matching pain, objection, and
boundary. And [vocabulary.md](vocabulary.md) is the consolidated authority on wording: a writer must
never be told to prefer a phrase in one document that another warns against, and when two disagree, the
vocabulary list resolves it.

## The website is this section's largest consumer

Most of what this section governs eventually appears on <https://contextgeneric.dev>, so
[website/](../website/README.md) is where the guidance is spent. Its own
[AGENTS.md](../website/AGENTS.md) makes consulting these documents mandatory before any change to a page,
and its [writing-guides/](../website/writing-guides/README.md) subsection turns this guidance into
per-page-type instructions for how new pages should be written. When a rule here and a writing guide
disagree about a specific page type, the writing guide is the more specific instrument and governs that
page — but a guide that contradicts [author-personality.md](author-personality.md) is a defect in the
guide.
