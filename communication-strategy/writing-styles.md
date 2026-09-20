# Writing styles: habits to prefer or avoid

Write sentences that state a clear point, name the relevant subject, and explain how ideas connect.

Use this guide for sentence-level revision. The `point-first-writing` skill covers paragraph and
section structure, [voice-and-register.md](voice-and-register.md) covers the project's and author's
voices, and [vocabulary.md](vocabulary.md) fixes CGP terminology. Use
[reader-simulation.md](reader-simulation.md) to check what a reader can understand from the result.

## Say it straight: the real subject, doing the real thing

Name the subject early and give it a direct verb. A sentence about `#[implicit]` should explain
what the attribute does before discussing its resemblance to ordinary parameters.

These examples show common ways to make the subject and action clearer:

| Indirect | Direct |
| --- | --- |
| “Reading values from the context is what implicit arguments make easier.” | “Implicit arguments read values from context fields.” |
| “`#[implicit]` makes a field read look like a parameter.” | “`#[implicit]` reads a context field through a parameter declaration.” |
| “Whether to split the component is the author's decision.” | “The author decides whether to split the component.” |

Lead each paragraph with its point, then supply the explanation and qualifications. Read the
opening sentences in sequence: they should give a coherent account without requiring the reader
to search the supporting details for the conclusion.

Keep qualifications that establish scope or evidence. “Early tests suggest” and “for this context”
can be necessary parts of a claim. Direct wording must not turn a possibility into a guarantee or
an observation into a universal rule.

## Cleft and pseudo-cleft inversions

Replace constructions such as “is exactly what” and “What ... does is” when they only repeat the
subject. The direct form usually states the same point with fewer words:

| Indirect | Direct |
| --- | --- |
| “Choosing a provider is exactly what the wiring table does.” | “The wiring table selects a provider.” |
| “What the macro generates is a trait and a blanket impl.” | “The macro generates a trait and a blanket impl.” |
| “Separating provider types is what allows the implementations to coexist.” | “Separating provider types allows the implementations to coexist.” |

An opening action phrase can remain the subject. “Separating provider types allows the
implementations to coexist” already states its point directly. The unnecessary restatement is
the problem, not the grammatical form of the subject.

Searches for “is what,” “is exactly what,” and “What ... is” can locate candidates for revision.
Read each sentence before changing it, then check that the surrounding paragraph still connects.
A mechanical replacement can remove words while leaving the point unclear.

## Em dashes

Replace prose em dashes with punctuation or words that explain the relationship between clauses.
Choose the replacement by what the dash does:

| Relationship | Prefer | Example |
| --- | --- | --- |
| Aside | Parentheses, commas, or a separate sentence | “The provider (a zero-sized marker) names the implementation.” |
| Definition or explanation | A colon | “Wiring is lazy: a table entry alone does not check every dependency.” |
| Contrast | “But,” “though,” or “yet” | “The table compiles, but using the component reveals a missing bound.” |
| Consequence | “So” or “because,” when supported | “The check fails because the context lacks the required field.” |
| Related full clauses | Separate sentences or a suitable conjunction | “The context selects the provider. The compiler resolves the call.” |
| List introduction | A colon | “The provider needs two fields: width and height.” |

Do not introduce a causal claim merely to replace punctuation. If the source only places two facts
together, “so” may assert more than it supports. Separate sentences preserve the distinction.

An em dash may separate a list item's subject from its description when used consistently.
A colon serves the same purpose. Apply the prose rule within the description, and revise existing
dashes only in passages already within the task's scope.

## Plain, direct English for agent-drafted content

Use literal, accessible English when an agent writes the first draft. This applies to reference
pages, concepts, guides, and other agent-authored documentation. When revising a human draft,
preserve the author's voice and follow [author-personality.md](author-personality.md). Check the
page's provenance record when the distinction is unclear; [ai-disclosure.md](ai-disclosure.md)
defines the authorship arrangements.

Assume technical knowledge does not imply familiarity with English idioms. Keep the domain terms
needed to explain CGP, define them when the intended reader needs it, and use familiar words around
them. Useful habits include:

- **Use literal descriptions:** Replace “unlock the feature” with “enable the feature” or name the
  operation the feature permits.
- **Remove wordplay and idioms:** Write “essential” for “load-bearing” and “two checks for the same
  mistake” for “belt and suspenders.”
- **Prefer active voice:** “The compiler resolves the provider” names the actor. Keep passive voice
  when the actor is unknown or irrelevant and the sentence remains clear.
- **Separate substantial points:** Split sentences carrying several claims, especially when
  nested asides or repeated colons interrupt the subject and verb.
- **Use precise verbs:** Distinguish “must,” “should,” “can,” and “may.” Preserve the original
  requirement, recommendation, ability, or uncertainty.
- **Keep negation's scope:** “Some requests do not fail” does not mean “every request succeeds.”
  Prefer a verb or phrase that states what is absent, such as “lacks” or “without.”

Explain technical analogies only when they help teach a concept. State the literal mechanism and
the analogy's limits, following [voice-and-register.md](voice-and-register.md). This differs from
using an unexplained metaphor as a substitute for the mechanism.

## Checking a draft

Read the whole passage before scanning for individual words. Then check the revision in this order:

1. **Point and subject:** Does each paragraph open with its point? Does each sentence name what
   acts, changes, or is required?
2. **Meaning:** Are conditions, exceptions, evidence, uncertainty, and obligations preserved?
3. **Connections:** Do sentence order and conjunctions explain how the points relate?
4. **Directness:** Can a redundant “what” construction, delayed subject, or filler phrase be removed?
5. **Punctuation:** Does each replacement for a dash express the intended relationship?
6. **Plain English:** Can an idiom, decorative phrase, or uncommon word be replaced accurately?

Reread the result after local edits. A clearer sentence can still leave a repeated claim or a
transition pointing to the wrong idea. Pattern searches help locate candidates; they do not prove
that a revision works or that prose was written by an agent.

Add recurring problems here when they need guidance beyond the existing rules. State the problem,
give an accurate before-and-after example, and explain how to check for it. Avoid speculative
accounts of why a language model produced the wording.
