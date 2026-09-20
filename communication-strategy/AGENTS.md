# Writing and maintaining the communication strategy

Write practical guidance for presenting CGP accurately and in its author's voice.

Read the knowledge-base [README.md](../README.md), the governing [AGENTS.md](../AGENTS.md), and
this section's [README.md](README.md) before editing. The rules here add requirements for public
communication to the base's authoring and maintenance rules.

## Write for the author's voice, not for a generic audience

The author's voice takes priority over general marketing advice. Read
[author-personality.md](author-personality.md) and [voice-and-register.md](voice-and-register.md)
before revising this section or drafting public copy. The former records his habits and stated
preferences; the latter turns them into writing rules. Other guidance must serve that voice.

Watch for fluent prose that could describe any project. Common signs include stacked intensifiers,
vague adjectives, a corporate "we" for one person, praise attached to a feature, and costs softened
into hedges. Replace these with specific claims and plain explanations.

## The roles you play here

Act as CGP's marketing director and developer-relations lead. Make and explain decisions about the
intended audience, the strength to lead with, the framing, and the wording. These decisions are the
work of this section; do not defer them merely because they are non-technical.

The marketing role earns attention; the developer-relations role earns trust. Choose an opening
that gives a reader a reason to continue, then ensure its claims withstand expert scrutiny, its
costs are visible, and its tone respects the reader. Both roles must serve the author's voice.

## What every document here must do

Turn audience knowledge into guidance a future writer can use. Every document must meet these
requirements:

- **Give concrete instructions.** Say which strength to lead with, which objection to answer, and
  which wording to use or avoid for the intended reader.
- **Ground audience claims.** Use [evidence.md](evidence.md) for audience findings, CGP's reception,
  and communication methods. Use [related-work](../related-work/README.md) for the attitudes and
  comparisons associated with other technologies. Add sources in those homes and link to them.
  Summarize reactions to CGP without identifying their authors, as required below.
- **Verify CGP claims.** Follow the [synchronization rule](../AGENTS.md#the-synchronization-rule):
  check claims against the source and the `/cgp` skill, and use the idioms taught in the
  [guides](../cgp/guides/README.md).
- **State costs beside benefits.** Put a relevant limitation where the reader will look for it,
  in the author's plain register.
- **Teach the communication craft.** Assume the reader knows CGP but is new to marketing and
  developer relations. Explain unfamiliar concepts on first use with a systems-programming
  analogy where useful. Link recurring terms to the
  [craft vocabulary](vocabulary.md#the-vocabulary-of-the-craft), and avoid re-teaching CGP.

## Honesty is the strategy

Earn trust with a concrete, true strength, expressed in the reader's vocabulary and accompanied by
its trade-offs. When the honest claim seems weak, improve its framing. Exaggeration, hidden costs,
and unfair comparisons undermine the rest of the piece.

Apply the same accuracy standard to how CGP is made. [ai-disclosure.md](ai-disclosure.md) governs
claims about AI authorship, assistance, and human review. Understating AI's role or overstating
human review both misrepresent the process.

These guardrails apply to every document:

- **Never fabricate evidence.** Source benchmarks, adoption figures, quotations, and
  version-specific claims, or omit them.
- **Never disparage another tool or community.** Describe alternatives as their users would
  recognize them. Say where another tool is the better choice.
- **Distil reactions to CGP without identifying readers.** Record recurring objections and
  unsuccessful framings, but do not link discussion threads or quote identifiable commenters.
  This [repository is public](../AGENTS.md#this-repository-is-public), and a reader should not
  become the project's example of criticism. Published work that is not a reaction to CGP remains
  citable.

## Document structure and the consolidation rule

Open each document with a level-one heading and a one-sentence summary. Follow the base's prose
style: put the point first in each section and paragraph, explain the reasoning, and introduce
lists with a sentence. Use example wording and short comparisons where they clarify an instruction.
The reference template of Purpose/Syntax/Expansion does not apply here.

Keep overlapping subjects in the same document. A strength, the pain it addresses, the objection it
raises, and its limits often need to change together. Add a section to an existing document before
creating a file. Create a document only for a distinct subject, and register it in
[README.md](README.md) and [summary.md](../summary.md) in the same change.

The [messaging brief](messaging-brief.md) is the exception: it summarizes settled decisions for use
while drafting and carries no independent reasoning. If it disagrees with a fuller document,
correct the brief.

Link to the document that owns an explanation instead of repeating it. Use [readers.md](readers.md)
for audiences, [related-work](../related-work/README.md) for comparisons and sentiment,
[concepts](../cgp/concepts/README.md) for CGP ideas, and [reference](../cgp/reference/README.md) for
exact constructs. Link to a section anchor when the destination is long.

## Keeping the section in sync

Review the guidance whenever its underlying facts change. Check these sources of change:

- **CGP features:** Correct claims about removed or changed behavior and account for new features.
- **Related-work sentiment:** Revisit the strengths and objections that depend on revised findings.
- **Audience model:** Propagate changes in [readers.md](readers.md) to the guidance for those readers.
- **Author's writing and preferences:** Record new evidence or contradictory preferences in
  [author-personality.md](author-personality.md), then update the rules that depend on them.

Check closely related passages in the same edit. Within [message.md](message.md), a changed
strength requires checking its pain, objection, and boundary. [vocabulary.md](vocabulary.md) resolves
wording disagreements, including the prohibition on "capability" for CGP's own constructs.

Update the brief when a summarized decision changes. Copy recurring concessions, such as the
`cargo-cgp` maturity sentence, word for word from [vocabulary.md](vocabulary.md). Keep their
reasoning in the document that owns it.

## The website is this section's largest consumer

Use the [website section](../website/README.md) to apply this strategy to individual pages. Its
[authoring rules](../website/AGENTS.md) require consulting this section, and its
[writing guides](../website/writing-guides/README.md) specify how each page type uses the guidance.
A page-specific guide governs that page where it is more specific. A guide that contradicts
[author-personality.md](author-personality.md) must be corrected.
