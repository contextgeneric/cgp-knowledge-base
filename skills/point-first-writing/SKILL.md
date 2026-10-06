---
name: point-first-writing
description: >
  Write explanatory prose that serves both scanners and deep readers. Use when
  writing or revising documentation, guides, code comments, or other
  substantive prose, when deciding whether a section should be prose or a list,
  and when turning bullet-heavy output into readable text.
---

# Point-First Writing

Lead every paragraph with its point, then explain and support it. Use prose
when the content develops an argument and lists when it presents a set of
items. This structure lets readers scan for the main ideas or read straight
through for the full reasoning.

## Write for Scanners and Deep Readers

Support scanning and close reading in the same text. A reader may scan to find
a relevant section, then read it closely for the explanation.

**Scanners** use headings, paragraph openings, and lists to find what they need.
They should be able to read the openings alone and understand the argument.
Long paragraphs and delayed conclusions make them search for the point.

**Deep readers** follow the reasoning from one point to the next. They need
evidence, explanations, and transitions that show how the points connect.
An argument broken into loose bullets leaves them to infer those connections.

## Lead With the Point

State each paragraph's point in its opening sentence, then add explanation,
evidence, or consequences. A scanner can stop after the opening and still
understand the claim. A deep reader can continue to learn why it holds.

Give each paragraph one main point. Keep its explanation and evidence together,
and start a new paragraph when the next idea needs its own introduction. Merge
short paragraphs that merely fragment one explanation. A complex argument can
span several paragraphs, each developing a distinct part.

Use the simplest sentence shape that keeps the point first. The opening may
include a reason, or the next sentence may supply it. These examples show both
forms:

- "The reader can stop here because the opening already states the point."
- "The reader can stop here. The opening already states the point."

Lead each section with its conclusion, then give support in order of
importance. A reader who stops partway through should leave with the main idea.
Saving the conclusion for the end makes the reader reconstruct the argument.

Test the structure by reading only the first sentence of each paragraph in
order. Those sentences should form a clear account on their own. Move a point
forward when it appears too late. Add context when an opening depends on
details that this reading skips.

## Use Prose for Arguments and Lists for Sets

Use prose to explain how claims support a conclusion and lists to present
distinct items or steps. Connected sentences let readers follow the reasoning.
Lists make items easy to find and procedures easy to follow.

Use lists for sections that present tasks, open issues, related documents,
references, prerequisites, changed files, or options. Give each item a bullet,
or use numbered steps when the reader must act in order. Writing these sets
as paragraphs makes readers extract the items from sentences.

Use a table when readers need to compare the same attributes across items.
For example, place original and revised wording in adjacent columns so readers
can compare each pair directly.

Give list items a consistent shape and keep their descriptions brief. Usually
each item needs a subject and a short description, separated by a colon or an
em dash. Omit the description when the name suffices, as in a list of changed
files. Move extended explanations into nearby prose.

Turn a list of claims into prose when the reasoning between them explains the
point. Separate bullets make readers supply those connections. If the form
remains uncertain, try a paragraph. Keep a list when the paragraph would merely
enumerate its items.

Introduce every list with a sentence that explains what its items share or
why they matter. Add a sentence afterward when readers need an interpretation
or next action. A heading helps readers find the list, but the lead-in explains
its purpose.

## Use Counts Only When They Help the Reader

Omit counts and ordinal words whose only purpose is to tally the points in a
text. "There are 21 items" gives the reader a total without explaining the
items. Calling points "first", "second", and "third" gives their position
without showing how they relate.

Refer to each item by its subject. Write "the cache layer" or "the retry
logic" so the reader can identify it without looking up its position. Use
"also" for an addition and "then", "next", or "once" for a time sequence.

Keep numbers that report findings, guide action, locate information, or state
a limit. "Three requests failed" reports a result. Numbered steps show the
order the reader must follow, and "the first sentence of a paragraph"
identifies a location. Each gives information the reader can use.

## Use Headings and Bold to Show Structure

Use headings for changes of topic and bold for terms readers need to find
again. Both help scanning when they mark meaningful structure. Excessive
headings, emphasis, and nesting interrupt the argument without clarifying it.

Add a heading where the topic changes, and use transitions to connect the
sections. A useful transition states how the preceding point leads to the
next. Avoid headings that stand in for that explanation and sentences that
merely announce the next topic. Use nested headings or lists only when the
hierarchy helps readers understand the content.

Bold important terms on first use, with at most two emphasized phrases per
section. Repeated emphasis makes it harder to tell what matters. Bold list
subjects and opening labels in parallel rules serve as consistent formatting,
so they do not count toward that limit.

## Ground the Point

Give each claim the context the reader needs to judge it. "The debugging
technique works" leaves its evidence and scope unclear. If experiments support
the claim, "Early experiments show that this debugging technique catches most
regressions before review" tells the reader what worked and where the finding
comes from.

Supply missing context close to the claim it qualifies:

- **Source:** Where a finding comes from, such as "The profiler traces show" or
  "Users reported".
- **Scope:** Where the claim holds, such as "For batches under a hundred rows"
  or "In the current release".
- **Link:** How the claim connects to the previous point, such as "this
  technique" or "That failure explains".

Keep context that adds information, and cut framing that adds nothing. "Early
experiments show that" identifies evidence. "It is the case that" delays the
claim without helping the reader assess it. Use only the evidence and scope
that the source material supports.

## Connect and Qualify the Points

Make the relationship between points clear as the argument develops. Split a
sentence that carries several substantial points, then name the connection
where the reader needs it. A new sentence gives each point room for support.
Short, closely related clauses can stay together with a conjunction.

Choose a connective that expresses the relationship you mean:

- **Consequence:** "So", "Therefore", "As a result".
- **Contrast:** "But", "However", "Even so".
- **Addition:** "Also", "In addition".
- **Restatement:** "That is", "In other words".
- **Example:** "For example", "In particular".
- **Alternative:** "Otherwise", "Either way".

Use connectives where the relationship needs clarification. Starting every
sentence with "Therefore" or "However" makes a paragraph labored. Let clear
sequence carry the argument elsewhere, and prefer common words to formal ones
such as "Moreover" or "Nonetheless".

Keep separate points out of trailing clauses that hide their relationship.
A semicolon, dash, or trailing "which" can attach a new claim without
explaining why it follows. Split the sentence or use a conjunction that states
the link.

Choose verbs that preserve whether a claim states a fact, gives an instruction,
or describes a possibility. For an obligation, write "The caller must free the
buffer" instead of "The caller is responsible for freeing the buffer". Use
these distinctions when choosing the verb:

- **Requirement:** "Must".
- **Recommendation:** "Should".
- **Permission:** "May".
- **Ability:** "Can".
- **Possibility:** "May", "might", or "can", according to the meaning.
- **Expected outcome:** "Will", or "would" when the outcome is conditional.
- **Present state:** "Is" or "are".

Preserve uncertainty when choosing a more direct verb. Changing "may fail" to
"will fail" strengthens the claim. Likewise, adding "so" asserts a consequence
that adjacent statements alone may not support.

Carry negation on the verb or in a phrase that states what is missing. Use
"does not" for an action that does not happen, "cannot" for inability, "lacks"
for a missing property, or "without" for an absent condition. For example,
"The API lacks a batched call" names the subject more directly than "There is
no batched call". Avoid bare "no" before a noun, while keeping fixed
expressions such as "no longer" and "a no-op".

Keep the scope of a negation intact when moving it. "Not every request fails"
can become "Some requests do not fail". Changing it to "Every request succeeds"
would change which cases the claim covers.

## Write in Plain English

Use familiar words and direct sentences so readers can concentrate on the
ideas. Preserve the meaning and technical detail while removing language that
makes either harder to follow.

Prefer the common word when it says the same thing. Write "use" for
"utilize", "show" for "demonstrate", and "help" for "facilitate". Cut filler
such as "in order to", "it is important to note that", and "the fact that".

Keep sentences short enough to follow without rereading. Split a long sentence
at the change of point, then make the relationship clear. Prefer active voice
and name the actor: "The compiler checks the type" tells the reader who acts.

Replace metaphors, idioms, and wordplay with their literal meaning. "Turn the
feature on" gives a direct instruction where "unlock the feature" asks the
reader to interpret an image. Likewise, use "essential" for "load-bearing"
and "two checks for the same mistake" for "belt and suspenders". Figurative
language can confuse readers who do not share the expression or association.

Keep technical terms the subject needs, and define them on first use. Prefer
common words elsewhere. Readers who understand the subject should be able to
follow the explanation without learning unnecessary vocabulary.

## Name the Real Subject

Name the actor early and give it a direct verb. An opening that delays the
actor makes the reader work out who does what before they can assess the
point. Check especially for sentences that use "what" to restate their own
subject or end by naming who owns a decision.

Replace "is exactly what" and "What ... is" constructions with direct
statements when they add words without adding meaning. Compare the original
sentences with their revisions:

| Original | Revision |
| --- | --- |
| "Reducing the number of clicks is exactly what the new checkout does." | "The new checkout reduces the number of clicks." |
| "What the cache stores is the last ten results." | "The cache stores the last ten results." |

Keep an opening action phrase when the action itself is the subject.
"Reducing clicks helps users finish checkout" already states its point
directly.

Move a delayed decision-maker to the front of the sentence. Write "The owner
decides whether to ship the release" for "Whether to ship the release is the
owner's call". Check similar endings such as "is up to the team" or "is the
maintainer's responsibility". Use "should decide" only when the sentence
recommends who should decide.

Retain source and scope when making a sentence direct. Removing "Early
experiments show that" would hide the claim's basis and make a preliminary
finding sound established.

## Choose Punctuation That Explains the Link

Replace em dashes in prose with punctuation or words that express the intended
relationship. A dash can mark an aside, a definition, or a contrast, leaving
the reader to infer which one applies. Choose the replacement by its job:

- **Aside:** Use parentheses or commas, or give the aside its own sentence.
- **Definition or elaboration:** Use a colon, as in "The cache holds one thing:
  the last ten results."
- **Contrast:** Start a new sentence with "But", or join clauses with "though"
  or "yet".
- **Related full clauses:** Use separate sentences, or join them with "and",
  "because", or "so" as the meaning requires.
- **List introduction:** Use a colon.

Preserve the intended relationship when replacing a dash. If low cost explains
why a check runs frequently, "The check is cheap — it runs on every save"
becomes "The check is cheap, so it runs on every save". The word "so" makes
the consequence explicit.

Use an em dash to separate a list item's subject from its description when
that format helps scanning. A colon after a bold subject serves the same
purpose. Keep the separator consistent within each list, and apply the prose
rule inside descriptions. For example:

- **Design proposal** — the accepted design and the alternatives it rejected.
- **Rollout plan** — the staged schedule and the owner of each stage.
- **Incident review** — the outage that motivated the change.

## Revise by Reading the Whole Text

Read the whole text before editing so you can judge its structure and claims.
Search can locate words, but it cannot tell whether a paragraph makes several
points, a verdict lacks support, or a list belongs in prose.

Cut and reorganize as well as rewriting sentences. Remove repetition and
unnecessary explanations. Move conclusions forward, combine paragraphs that
make one point, and split those that make several. Preserve the meaning while
making the argument easier to follow.

Check that each rewrite preserves the original claim. Keep its conditions,
exceptions, uncertainty, and obligations. A shorter sentence that changes any
of these needs another revision, and a factual correction needs support from
the source material.

Reread the surrounding paragraphs after each change. A revision can leave a
connective pointing to the wrong idea, repeat an earlier claim, or require a
different transition. Continue until a reading pass reveals nothing further
to improve.

## Keep Code Comments Brief and Accurate

Keep each comment focused on what the reader needs at that line. Move a long
explanation to the relevant Markdown document and leave a short pointer in the
code. Brief comments keep the code visible and reduce the prose that must stay
in sync with it.

Check a comment's claim against the code before polishing it. Delete comments
that only restate the code. When a comment and the code disagree, determine
which is wrong, correct it within the task's scope, and report what changed.
Making an inaccurate comment more fluent makes the error harder to notice.

## Check the Revision

Read the revised text in full, then use these checks to find anything the
reading missed:

- **Paragraph openings:** Read only the first sentences in order. They should
  state the points and form a clear account.
- **Paragraph scope:** Give each paragraph one main point, keeping its support
  together. Merge fragments and remove repetition.
- **Lists and tables:** Use lists for sets or procedures, tables for comparisons,
  and prose for arguments. Introduce each list and add a follow-up when needed.
- **Counts:** Remove totals and ordinal labels that only tally the content.
- **Headings and bold:** Keep formatting that marks real structure or helps
  readers find key terms. Remove excessive emphasis and nesting.
- **Grounding:** Supply missing evidence, scope, or context without adding
  unsupported claims.
- **Sentences and connections:** Split overloaded sentences and make unclear
  relationships explicit. Remove connectives where sequence already suffices.
- **Claim strength:** Use verbs that distinguish facts, requirements,
  recommendations, possibilities, and expected outcomes.
- **Meaning:** Preserve conditions, exceptions, uncertainty, obligations, and
  the scope of negations. Check that added links reflect the source material.
- **Negation:** Replace bare "no" before a noun with a verb or phrase that
  states what is missing, except in fixed expressions.
- **Plain language:** Cut filler and replace unnecessary jargon, metaphors,
  idioms, and wordplay with direct wording.
- **Subjects:** Rewrite redundant "what" constructions and delayed actors so
  the real subject leads.
- **Em dashes:** Replace prose dashes according to their meaning. Keep them as
  consistent separators between list subjects and descriptions.
- **Comments:** Verify claims against the code and remove redundant comments.
