# Reader simulation: modeling the reader's mind as you write

Revise prose by predicting what a particular reader will understand after each passage, then fixing
where that prediction differs from the intended meaning.

Treat these predictions as editing hypotheses. They help expose missing explanations, confusing
wording, and unsupported claims, but they do not substitute for feedback from readers.

## What this adds, and where it sits

Use reader simulation after checking the draft's structure and style. [readers.md](readers.md)
defines audience profiles, [writing-styles.md](writing-styles.md) guides sentence choices, and the
`point-first-writing` skill guides paragraphs and sections. This method checks how those choices
work together as a reader moves through the text.

The method draws on reading research without claiming to measure a reader's mind. Its
[research section](#the-science-this-rests-on) keeps those sources beside the method. Audience
claims still belong in [evidence.md](evidence.md); the scientific references here explain the
editing approach rather than establish facts about CGP's readers.

## The model reader you simulate

Choose one reader with a specific task and level of knowledge. The default is a
[working Rust developer](readers.md#the-working-rust-developer) who knows Rust but is new to CGP
and wants a reason to use it. Change that default when the format targets another profile.

Separate knowledge of Rust from knowledge of CGP. A reader may understand traits and generics
without knowing what a provider or wiring table is. Connect each new CGP idea to something already
established. Explain Rust prerequisites when the chosen profile needs them rather than assuming
that every Rust developer knows blanket implementations equally well.

Adjust explicitness to the reader and the task. Research on prior knowledge and text cohesion
shows that the usefulness of supplied explanations can vary with readers' knowledge and reading
strategies. The practical rule here is to make unfamiliar CGP relationships explicit while avoiding
unnecessary lessons on Rust concepts the reader already understands.

## The loop: predict, compare, repair

Review each sentence and paragraph through this sequence:

1. **Predict:** What can this reader understand, infer, or reasonably question at this point?
2. **Compare:** Does that match what the passage needs to establish?
3. **Repair:** Supply the missing step, change the wording or order, or defer material that arrives
   too early.

Change the cause of confusion rather than adding reassurance. Calling wiring "simple" does not
explain it; showing how a context selects a provider can.

## The six variables to track

Use these categories to diagnose a passage. They overlap and are not numerical measurements, but
each suggests a different kind of revision.

### Common ground: what the reader now knows

Check that the passage builds on knowledge the reader plausibly has. **Common ground** includes
the chosen prerequisites and the facts and terms already introduced. A term such as
`DelegateComponent` needs an explanation before it can support another explanation.

Repair missing context at the point it is needed. Introduce the term, connect it to a known idea,
or replace it with a description. The given-new approach in
[Clark and Haviland](#the-science-this-rests-on) informs this check: readers need a connection
between familiar and new information.

### Working memory: how much the reader holds at once

Reduce the effort needed to connect parts of a sentence. Long interruptions between a subject and
verb, ambiguous pronouns, and several unexplained terms make readers retain unresolved information
while processing more text.

Split a sentence when its structure obscures the idea. Resolve one dependency before adding
another, move a long qualification, or repeat a noun when a pronoun is unclear. Cognitive-load
research motivates reducing avoidable difficulty; it does not establish a fixed number of terms
that every CGP reader can hold.

### The model under construction: what the reader is building, and whether it is right

Check the explanation the reader could reconstruct from the passage. Reading involves connecting
text with prior knowledge, as described by the
[construction-integration model](#the-science-this-rests-on). An incomplete explanation may leave
readers unable to proceed; a misleading one may make later material harder to understand.

Prevent a likely misinterpretation where the wording introduces it. If "dependency injection"
could suggest a runtime container, explain that CGP resolves provider selection at compile time.
Use the [objection guidance](message.md#the-objections-readers-bring) to identify relevant
misreadings without assuming every reader has them.

### Expectation: what the reader now predicts comes next

Make each transition follow from the question the passage has raised. A problem should lead to its
consequence or solution; a claim should receive its promised explanation. An abrupt topic change
needs a reason the reader can see.

Use expectation research as a prompt to inspect transitions, not as proof that every surprise is
bad. [Levy's work](#the-science-this-rests-on) models difficulty in syntactic comprehension.
Applying it to paragraph organization is a writing heuristic: prepare a change of direction and
name its relationship to the preceding point.

### Stance: trust, skepticism, and interest

Check whether a clear sentence also makes a credible claim. A reader can understand a sentence
and still reject its exaggeration, hidden cost, or unfair comparison. Use
[evidence.md](evidence.md) for observed objections and [readers.md](readers.md) for the intended
reader's concerns.

Replace unsupported assurance with a specific claim and its limit. State costs where they matter,
represent Rust and other tools fairly, and remove praise that adds no information. Follow
[voice-and-register.md](voice-and-register.md).

### Energy: the reader's remaining willingness to continue

Remove effort that does not advance the explanation. Repeated definitions, decorative sentences,
and paragraphs that merely restate a point give readers more work without more understanding.

Use "reader energy" as a metaphor for attention, not a quantity the simulation can measure. Keep
necessary depth, provide a clear route through long material, and cut avoidable rereading. A
shorter passage helps only when it retains the steps the reader needs.

## The placement rules the simulation implies

Arrange sentences so readers can identify the subject, action, and connection to the preceding
point. These edits draw on [Gopen and Swan](#the-science-this-rests-on):

- **Connect familiar information to new information.** Begin from a known subject where possible,
  then explain what the reader needs to add to it.
- **Use openings for orientation and endings for emphasis.** Make the connection visible early
  and avoid burying important information inside an aside.
- **Keep the subject near its verb.** Move long interruptions elsewhere.
- **Put actions in verbs.** Prefer "the macro generates a provider trait" to "the generation of a
  provider trait is performed by the macro."
- **Keep the paragraph's subject clear.** Change grammatical subjects when the explanation needs
  it, while making the relationship between them explicit.
- **Put short material before long qualifications where that helps.** Avoid making readers hold
  a complex opening while waiting for its main clause.

Keep the paragraph's main point first. Sentence-final emphasis can reinforce that point, but it
must not become a reason to delay the paragraph's conclusion. Apply these habits with judgment;
word order alone cannot make a missing explanation clear.

## Word choice as a lever on the reader's state

Choose words for both their meaning and the interpretation they invite. A technically valid term
can still imply the wrong mechanism to an unfamiliar reader.

Use a term's associations only when they help. "Modular" may suggest a runtime framework to some
readers, so [identity.md](identity.md) keeps it out of the lead description. Prefer a specific
phrase such as "provider selection at compile time" when it supplies the intended meaning.

Name the thing being discussed. "The wiring table" gives more information than "the machinery",
and a named provider is easier to locate than "the implementation" when several are in view.
Research on concrete words informs this preference, but specificity and context still matter: an
unexplained error code is not clearer merely because it is concrete.

Prefer familiar words and define necessary technical terms. A precise uncommon term can earn its
place, but unnecessary vocabulary adds another thing to learn. Use the same term for the same idea
rather than introducing synonyms that may look like different constructs.

Introduce new terms gradually. Aim for one new term at a time in introductory passages, connect it
to a familiar idea, and use it before adding another. This is an editing guideline rather than a
universal limit on what a paragraph can contain.

## Running the loop against your own fluency

Review from the reader's available knowledge rather than the writer's full understanding. The
**curse of knowledge** is the difficulty of recognizing what someone without your knowledge needs
explained. A fluent draft can skip steps precisely because the writer finds them obvious.

Run a separate reading pass after drafting. For each CGP term or inference, identify the earlier
explanation or prerequisite that supports it. If that support is missing, add it or move the
passage. Read paragraph openings alone as well: they should form a clear account without relying
on details that the scan skips.

Use reader feedback to correct the simulation. A predicted misunderstanding is a reason to inspect
or test the text, not evidence that readers actually misunderstood it. The observation practices
in [readers.md](readers.md#keeping-the-model-observed) help check those predictions.

## A worked pass

Explain wiring to a Rust developer who has already learned what contexts, components, and
providers are. Assume they have not met the generated delegation traits.

This draft introduces implementation details before explaining their purpose:

> Because `DelegateComponent` resolves the provider for each component key during monomorphization,
> and the consumer trait's blanket impl uses the context's provider choice, a call to `greet()`
> dispatches statically to the wired provider. This makes CGP zero-cost.

The opening requires knowledge the assumed reader lacks. It combines a generated trait, a
component key, and a blanket impl before explaining the selection being made. The runtime-cost
claim arrives after those terms, leaving the reader little basis for assessing it.

The revision starts with the choice the reader makes:

> A context selects a provider for each component through a wiring table written with
> `delegate_components!`. Rust resolves this selection at compile time, so `person.greet()` uses
> a direct call to the selected provider. The selection requires no runtime lookup.

The revision connects known roles before introducing the macro name. It explains when selection
happens and limits the runtime claim to that selection. The generated traits can appear later,
once the reader understands what they implement; see
[the wiring-table teaching guidance](readers.md#the-wiring-table-and-its-machinery).

## Running the method: the checklist

After the structural and style checks, review the draft in this order:

1. **Name the reader.** Specify their task, Rust knowledge, and CGP knowledge.
2. **Check the available context.** Find terms and inferences that lack an introduction or a
   justified prerequisite.
3. **Diagnose the passage.** Check common ground, working memory, the developing model,
   expectation, stance, and willingness to continue.
4. **Repair the cause.** Add a missing step, simplify the sentence, qualify the claim, or change
   the order.
5. **Reread the surrounding text.** Check transitions and remove repetition introduced by the fix.
6. **Test uncertain predictions.** Use reader feedback where the simulation cannot settle whether
   an explanation works.

## The science this rests on

The references below inform the editing method; they do not validate this checklist as a predictive
model of CGP readers. Distinguish original research, writing advice, and secondary summaries.
Keep claims within each source's scope, and use actual reader feedback to judge the resulting prose.

- **The reader-expectation approach**, which supplies the placement rules and the reader-energy framing:
  George D. Gopen and Judith A. Swan, The Science of Scientific Writing, *American Scientist* (1990)
  ([PDF](https://www.usenix.org/sites/default/files/gopen_and_swan_science_of_scientific_writing.pdf)),
  and George D. Gopen,
  [reader-expectation research](https://georgegopen.com/reader-expectation-research/).
- **The given-new contract**, which supplies the common-ground variable and old-before-new: Herbert H.
  Clark and Susan E. Haviland,
  [Comprehension and the Given-New Contract](http://www.web.stanford.edu/~clark/1970s/Clark,%20H.H.%20_%20Haviland,%20S.E.%20_Comprehension%20and%20the%20given-new%20contract_%201977.pdf)
  (1977).
- **Audience design and common ground**, the theory-of-mind basis for writing from shared rather than
  privileged knowledge: Herbert H. Clark and colleagues, summarized at
  [Audience design](https://en.wikipedia.org/wiki/Audience_design).
- **Cognitive load theory**, which supplies the working-memory variable and the intrinsic/extraneous
  split: John Sweller and colleagues, overview at
  [Cognitive load](https://en.wikipedia.org/wiki/Cognitive_load).
- **The construction-integration model and the situation model**, which supply the model-under-construction
  variable: Walter Kintsch, summarized in
  [Kintsch and Rawson, Comprehension](https://sites.pitt.edu/~perfetti/PDF/Kintsch%20&%20Rawson.pdf).
- **Surprisal and expectation-based comprehension**, which supply the expectation variable and lexical
  predictability: Roger Levy,
  [Expectation-based syntactic comprehension](https://www.mit.edu/~rplevy/papers/levy-2008-cognition.pdf)
  (2008), building on John Hale (2001).
- **The reverse cohesion effect**, which supplies the split-reader rule: Danielle S. McNamara and
  colleagues, on how prior knowledge changes how much cohesion a text should carry
  ([overview](https://www.researchgate.net/publication/233347242_Reversing_the_Reverse_Cohesion_Effect_Good_Texts_Can_Be_Better_for_Strategic_High-Knowledge_Readers)).
- **The concreteness effect and dual coding**, which supply the concrete-word rule: the finding that
  concrete words are processed and remembered better than abstract ones, from Allan Paivio's dual-coding
  work onward ([overview](https://en.wikipedia.org/wiki/Dual-coding_theory)).
- **The curse of knowledge and arcs of coherence**, which supply the de-biasing procedure and much of the
  register: Steven Pinker, *The Sense of Style* (2014), and
  [The Curse of Knowledge](https://www.psychologicalscience.org/observer/the-curse-of-knowledge-pinker-describes-a-key-cause-of-bad-writing).

## Keeping this document current

Update the method when its audience assumptions or supporting guidance changes. Check
[readers.md](readers.md), [vocabulary.md](vocabulary.md), [writing-styles.md](writing-styles.md),
and [voice-and-register.md](voice-and-register.md) together.

Revise research claims when the evidence warrants it. Present the rules as practical guidance with
limits, and distinguish a useful editing hypothesis from a demonstrated improvement in readers'
understanding.
