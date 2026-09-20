# CGP Communication Strategy

This section guides public writing about CGP: what to lead with, how to explain unfamiliar ideas,
and how to preserve the author's voice.

Use it for landing pages, tutorials, READMEs, blog posts, talks, and threads. The technical sections
explain how CGP works; this section helps writers present it to a particular reader. Read
[AGENTS.md](AGENTS.md) for the authoring rules.

## The reader and the failure mode

These documents serve agents and human CGP advocates who know the technology but are new to
marketing, public communication, and developer relations. Explain that craft in plain language,
using a systems programmer's intuition where helpful. Technical expertise alone does not tell a
writer what an unfamiliar reader needs to hear.

The guidance prevents unsupported claims and generic copy. A claim CGP cannot support damages
trust, while fluent prose filled with vague praise loses the author's voice. Start with
[author-personality.md](author-personality.md): his stated preferences govern the rest of the
section.

## What this section is not

Publication planning and campaign records belong outside this repository. This section records
standing guidance about attention and framing, not schedules, channel assignments, or campaign
results.

Specific reactions to CGP are summarized without identifying the people who made them.
[evidence.md](evidence.md) records recurring objections and unsuccessful framings, without linking
threads or quoting identifiable readers. This follows the rule for a
[public repository](../AGENTS.md#this-repository-is-public). Published work that is not itself a
reaction to CGP remains citable.

## Two decisions that shape everything here

CGP uses a project voice on the website and a personal voice on the blog. The homepage,
documentation, and tutorials address the reader plainly, without first-person narration. Blog posts
use the author's first-person voice, including his uncertainties and personal history.
[voice-and-register.md](voice-and-register.md) explains the distinction and its exceptions.

CGP enhances Rust's trait system. Its identity should consistently show how it builds on ordinary
Rust, supports gradual adoption, and respects the reasons for Rust's existing rules. This framing
also addresses the concern about complexity recorded in [evidence.md](evidence.md).
[identity.md](identity.md) defines the settled wording.

## Principles from the non-technical craft

Write from the reader's current knowledge. The **curse of knowledge** is the difficulty experts
have remembering what an unfamiliar reader does not yet understand. It leads writers to introduce
an elegant mechanism before showing the problem it solves. Begin with a problem the reader can
recognize, then introduce the mechanism.

**Positioning** helps readers place CGP in a useful category. Readers interpret an unfamiliar tool
through concepts they already know, such as dependency injection or macros. Choose a clear opening
that states the benefit and the relevant difference from alternatives. Define craft terms as they
arise, using the [vocabulary](vocabulary.md#the-vocabulary-of-the-craft) for fuller explanations.

A clear opening gives one intended reader a reason to continue. Lead with a concrete idea and show
it through a real example or a before-and-after. Use consistent words across pieces so readers can
connect what they learn. Keep the entry focused, then provide the depth the subject needs and tell
readers what a long piece will cover.

Developer relations builds trust through accurate claims and useful help. Show what CGP does,
state its costs, represent alternatives fairly, and say when a simpler tool fits better. Use real
examples from other developers when available. Ask readers for a next step suited to their stage,
whether that is reading an explanation, trying a program, or contributing a component.

## The catalog

Read the [messaging brief](messaging-brief.md) before drafting, then consult the fuller documents
for the decisions your piece needs. For a first reading, follow the order below; read AI disclosure
when writing about provenance. Related subjects stay together so writers can find their reasoning
in one place.

- [The messaging brief](messaging-brief.md): The settled message, features, audience-specific pains,
  objections, costs, next steps, vocabulary, and publishing checks in one page.
- [The author's personality and preferences](author-personality.md): His observed writing habits
  and stated preferences. Read this before applying the other guidance; it governs conflicts.
- [Voice and register](voice-and-register.md): Project and author voices, paragraph structure,
  canonical examples, diagrams, code samples, and habits to avoid.
- [Writing styles](writing-styles.md): Direct sentences, clear subjects, alternatives to habitual
  em dashes, and plain English for agent-drafted pages, with before-and-after examples.
- [Identity](identity.md): Positioning, the settled tag line, the pitch that follows it, and the
  homepage feature set.
- [Readers](readers.md): Audience profiles, comprehension barriers, teaching responses, and ways
  to test assumptions through friction logs and reader conversations.
- [The message](message.md): The pains CGP addresses, its strengths, reader objections, and the
  limits beyond which a simpler tool fits better.
- [Vocabulary](vocabulary.md): Preferred, deferred, and avoided terms, plus definitions of the
  communication craft. It resolves wording disagreements.
- [Reader simulation](reader-simulation.md): A method for predicting what readers know, expect,
  and understand as a piece develops, then revising where those predictions fail.
- [Formats](formats.md): Guidance for posts, READMEs, talks, threads, and comparisons, including
  titles, search, discussion replies, next steps, and model drafts.
- [Evidence](evidence.md): Survey findings, relevant discussions, summarized CGP reception,
  evaluation signals, and dated sources for audience claims and communication methods.
- [AI disclosure](ai-disclosure.md): How to describe AI's role in documentation, revisions,
  tooling, tests, and the core library; review limits; and website provenance notes.

## Where this guidance gets spent

The [website section](../website/README.md) turns this strategy into page-specific guidance and
records of published work. Start with its [writing guides](../website/writing-guides/README.md)
when drafting for the site. The [homepage](../website/writing-guides/homepage.md) and
[tutorial](../website/writing-guides/tutorial.md) guides own those formats' detailed requirements.

Published pages also help test whether the guidance fits the author's work. The
[RustLab transcript](../website/blog/rustlab-2025-coherence.md) provides a delivered talk to learn
from, the [tutorial records](../website/tutorials/README.md) document teaching approaches, and the
[blog catalog](../website/blog/README.md) records the published corpus. Ground claims about what
works in examples and reception, keeping publication itself distinct from evidence of success.

## Relationship to related work

Read [related-work](../related-work/README.md) alongside this section when preparing a comparison.
Those documents explain an external idea faithfully, record what its users value or dislike, and
compare it with CGP. This section turns those findings into guidance for an audience. Use the
related-work document for the comparison's technical detail and this section for how to present it.
