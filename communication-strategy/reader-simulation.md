# Reader simulation: modeling the reader's mind as you write

This document gives an agent a method for writing and revising CGP prose by running a forward model of
the reader's mind: after each sentence, estimate the reader's mental state, and treat any bad state the
estimate predicts as the signal to edit. Reading and writing are the same process run in opposite
directions, so writing a sentence well means predicting how a reader will process it. The method is
theory of mind applied to prose: model the other mind, detect where your text puts it into a state you
did not intend, and repair the text rather than the reader.

## What this adds, and where it sits

This document is the **dynamic** companion to the section's three static ones, and it is worth being
precise about the division so an agent knows which to open. [readers.md](readers.md) is the audience
*model*: who reads about CGP and what each already knows. [writing-styles.md](writing-styles.md) is a
set of sentence *shapes* to prefer or avoid. The
[`point-first-writing`](https://github.com/contextgeneric/cgp-skills) skill fixes paragraph and section
*structure*. This document is the *method* that uses all three at once: it says how to simulate a
particular reader's state as it changes sentence by sentence, so that a word choice, a clause order, or
a claim is judged by the state it leaves the reader in rather than by a rule it obeys. A draft can pass
every structural check and still leave the reader confused, overloaded, or unconvinced, and this is the
document for catching that.

The method rests on a body of reading science rather than on taste, and the
[grounding section](#the-science-this-rests-on) below cites it. That makes this the one strategy
document whose external citations live in it rather than in [evidence.md](evidence.md), because its
subject *is* that external science while evidence.md is scoped to facts about the CGP audience. The
[AGENTS.md](AGENTS.md) rule to concentrate citations still holds for every audience claim; it does not
reach the scientific foundation this document imports.

## The model reader you simulate

**Simulate one specific reader, not an average, and for CGP that reader has split knowledge: high prior
knowledge in Rust, near-zero prior knowledge in CGP.** The default is the working Rust developer who is
also a skeptic, because [readers.md](readers.md#the-working-rust-developer) shows that writing which
satisfies that reader rarely loses anyone else. Naming the reader is the first act of the simulation,
because the same sentence leaves two different readers in two different states, and a state prediction
is meaningless until you fix whose state it is.

The split matters more than it first appears, because it changes how much to spell out. Reading research
finds a **reverse cohesion effect**: readers low in prior knowledge understand more from highly explicit
text that connects every step, while readers high in prior knowledge can learn more from text that
leaves gaps for them to bridge, because the act of bridging builds a stronger memory
([McNamara](#the-science-this-rests-on)). The CGP reader sits on both sides of that finding at once.
They are high-knowledge about Rust, so an explanation that re-teaches traits or generics bores them and
spends their patience. They are low-knowledge about CGP, so every CGP idea, term, and inference must be
connected explicitly, with no gap left for them to bridge, because they have nothing to bridge it with.
The rule that falls out is to **write CGP's own ideas with maximum cohesion and lean on the reader's
Rust knowledge for everything else**: never explain a blanket impl, always explain what a provider is.

## The loop: predict, compare, repair

**Run the same three steps on every sentence and every paragraph.** First, predict the reader's mental
state after they process the text, along the variables in the next section. Second, compare that
predicted state against the state you intended them to be in. Third, where the two differ, repair the
text, not by adding reassurance but by changing what put the reader in the wrong state. This is the loop
a person runs unconsciously when they write well, and an agent runs it badly by default because of the
curse of knowledge, so an agent must run it explicitly. The rest of this document names what to predict,
how to move it, and how to run the loop honestly against your own fluency.

## The six variables to track

**Model the reader's state as six variables, and update your estimate of each after every sentence.**
They are not independent, and a single edit often moves several, but tracking them apart turns a vague
sense that a paragraph is off into a specific diagnosis and a specific fix. Each variable below
names what it is, the science that describes it, and the edit signal a bad value gives you.

### Common ground: what the reader now knows

Track the growing set of facts and terms the reader holds, and never write a sentence that depends on
something not yet in that set. Language production is an act of **audience design**: a writer builds each
sentence to be interpretable from what is common ground with the reader and not from what is only in the
writer's own head ([Clark](#the-science-this-rests-on)). The mechanism underneath is the **given-new
contract**: a reader takes the part of a sentence you present as already-known, searches memory for a
matching antecedent, attaches the new part to it, and stalls when the search fails
([Clark and Haviland](#the-science-this-rests-on)). So a sentence that opens on `DelegateComponent`
before the reader holds it presents a "given" with no antecedent, and the reader stops to look for one
they do not have. The edit signal is any term, construct, or claim used before the text put it in common
ground: introduce it first, or route around it.

### Working memory: how much the reader holds at once

Track the number of live items the reader must keep in mind to parse the current sentence, and keep it
low, because working memory is small and every held item spends it. **Cognitive load theory** splits the
load a text imposes into three kinds ([Sweller](#the-science-this-rests-on)). *Intrinsic* load is the
inherent difficulty of the idea, and CGP's ideas are intrinsically heavy. *Extraneous* load is the load
added by how the text is written rather than by the idea: a subject held far from its verb, a pronoun
whose referent is three clauses back, a term the reader must decode mid-sentence. *Germane* load is the
useful work of building understanding. Because intrinsic load is already high for CGP, the writer's whole
job on this variable is to drive extraneous load to zero so the reader's limited capacity is spent on the
idea. The edit signal is any sentence that forces the reader to hold more than two or three unresolved
items: split it, resolve one item before introducing the next, or move a heavy clause to the end.

### The model under construction: what the reader is building, and whether it is right

Track the mental picture of CGP the reader is assembling, and check that each paragraph adds a correct
piece rather than a wrong one. A reader does not store your sentences; they build a **situation model**,
an integrated mental model of the thing the text describes, by combining the text with their prior
knowledge ([Kintsch](#the-science-this-rests-on)). Two failures live here, and the second is worse than
the first. A paragraph can fail to add a piece, leaving the model incomplete. Or a paragraph can add a
*wrong* piece, and a wrong piece is expensive because later text has to detect and demolish it before it
can build the right one. CGP has a specific wrong model the reader will build unless you prevent it: that
wiring is a runtime container that resolves dependencies while the program runs, imported from the
dependency-injection frameworks the word "modular" evokes
([message.md](message.md#the-objections-readers-bring)). The edit signal is any passage that lets a wrong
model form: name the correct picture early and rule out the wrong one in the same sentence, as
"resolved at compile time and compiled to a direct call" does.

### Expectation: what the reader now predicts comes next

Track what the reader expects to read next, because a continuation they predicted is nearly free to
process and one they did not predict costs effort. **Surprisal theory** measures the processing cost of a
word or a turn as its improbability in context: the less expected it is, the more effort it takes to
integrate ([Levy, Hale](#the-science-this-rests-on)). This does not mean avoid surprise; it means *pay
for* the surprises the argument needs and refuse the ones it does not. An
unsignposted jump to a new topic is an unpaid surprise and spikes cost. A genuine turn in the argument is
a surprise worth paying for, and you pay for it by setting it up, so the reader half-expects it before it
lands. This is why [point-first-writing](https://github.com/contextgeneric/cgp-skills) puts the point
first and names the relationship between sentences: a stated connective lowers the surprisal of the
sentence after it. The edit signal is a sentence the reader could not have seen coming and was not
prepared for: add the setup, or the connective, that makes it expected.

### Stance: trust, skepticism, and interest

Track the reader's attitude, not only their comprehension, because a sentence they understand perfectly
can still move them from open to hostile. The CGP reader is a skeptic by default
([readers.md](readers.md)), and the Rust audience punishes overclaiming on sight
([message.md](message.md)), so predict how a claim *lands* and not only whether it parses. An intensifier
stacked on a true statement, a cost left unstated where the reader expects one, or a competitor
described unfairly each spikes distrust, and distrust, once spiked, discounts everything after it. A
conceded cost, a sympathetic account of what Rust already does, or a claim stated in its smaller honest
form repairs it. The edit signal is any sentence whose predicted effect is "this is being sold to me":
state the smaller true claim, or concede the cost in the same passage, per
[voice-and-register.md](voice-and-register.md).

### Energy: the reader's remaining willingness to continue

Track how much attention the reader has left, because it is finite and every extraneous cost spends it.
The reader-expectation research frames good structure as the conservation of a limited **reader energy**:
prose that forces rereading, that separates subject from verb, or that hides the action depletes a budget
the reader would rather spend on the idea ([Gopen and Swan](#the-science-this-rests-on)). A reader who
runs out does not send feedback; they close the tab, and for CGP's first-contact reader that decision
comes in seconds ([readers.md](readers.md)). The edit signal is a passage that spends energy without
advancing understanding: a paragraph that restates, a sentence that decorates, a term defined twice.

## The placement rules the simulation implies

**Six placement rules move the working-memory and expectation variables cheaply, and they are the
reader-expectation approach stated as edits.** They operate one level below
[point-first-writing](https://github.com/contextgeneric/cgp-skills), inside the sentence rather than
across paragraphs, and they come from the finding that readers look for particular kinds of content in
particular positions and are slowed when it is elsewhere ([Gopen and Swan](#the-science-this-rests-on)).

Put **old information before new**. Open a sentence with something already in common ground, so the
reader has an anchor before the new material arrives, and let the new material follow. This is the
given-new contract applied to word order, and it is the single highest-value habit here.

Put the **linkage in the topic position and the emphasis in the stress position**. Readers read the start
of a sentence as its connection to what came before, and the end as its most important content. So put the
backward link at the front and the point you want remembered at the end, and never bury the point in the
middle where the reader does not look for it.

Keep the **subject next to its verb**. A reader holds the subject in working memory until the verb
arrives, so a long interruption between them spends the budget on bookkeeping. Move the interruption out.

Put the **action in the verb**. When the real action of a sentence sits in a noun, the sentence reads as
static and the reader works to recover what happened. "The macro generates a provider trait" costs less
than "the generation of a provider trait is performed by the macro", per
[writing-styles.md](writing-styles.md#say-it-straight-the-real-subject-doing-the-real-thing).

Keep the **subject consistent across a passage**. A reader follows a passage as the story of a
protagonist, so switching the grammatical subject every sentence forces them to re-find whose story it is.
Decide what a paragraph is about and keep it in the subject position.

Put **light before heavy**. When two things can go in either order, put the short one first and the long
one last, because a reader holds a short opening more easily than a long one while waiting for the
sentence to resolve.

## Word choice as a lever on the reader's state

**A single word choice moves the reader's state, so choose the word by the state it produces, not only by
its meaning.** This is where the method goes past the plain-word advice in
[voice-and-register.md](voice-and-register.md): a word can be plain and correct and still put the reader
in the wrong state. Four effects make word choice a mental-state lever.

A word activates a **schema**, and the wrong schema builds the wrong model. Every term brings its
associations into the reader's mind, and those associations are the situation model forming before your
sentence finishes. "Modular" activates the dependency-injection-framework schema and the runtime cost the
reader files with it, which is why [identity.md](identity.md) retires it as a lead word. Choose the word
whose associations are the model you want, and the framing decision in
[vocabulary.md](vocabulary.md#words-and-framings-to-avoid) is this effect applied term by term.

A **concrete word costs less and lasts longer** than an abstract one. Readers process concrete words and
named things faster and remember them better, because a concrete word is encoded as both language and
image while an abstract word is only language ([the concreteness effect](#the-science-this-rests-on)). So
"the wiring table" beats "the machinery", a named provider beats "an implementation", and a quoted
`error[E0119]` beats "the errors can be confusing". This is the same instinct
[voice-and-register.md](voice-and-register.md#the-register-plain-unhurried-and-specific) states as
concrete-over-abstract, with the reason it works.

A **common word in an expected slot is nearly free**. Word predictability is the lexical case of
surprisal: a frequent word where the reader expected it costs almost nothing, while a rare word, or a
common word used in an unexpected sense, spikes cost ([Levy](#the-science-this-rests-on)). Prefer the
common word the reader already holds, and when a precise uncommon word earns its place, spend the cost
knowingly rather than by accident.

A **new term is a chunk the reader must build and hold**, so ration new terms and reuse them exactly.
Introduce at most one new term in a passage, define it on first use with an anchor a Rust programmer
already holds, and then use the same word for the same idea every time after, because a synonym reads as a
second thing rather than the same one. This is **message discipline** from
[vocabulary.md](vocabulary.md), and the reason it matters is that every new term spends a working-memory
slot the reader needs for the idea.

## Running the loop against your own fluency

**The curse of knowledge is the reason an agent must run this loop explicitly rather than trust its
instinct, because the agent's instinct is the expert's.** The curse of knowledge is the difficulty of
imagining what it is like not to know something you know, and it is the best single explanation for why a
fluent writer produces prose a newcomer cannot follow: the expert's knowledge is chunked differently, so
the steps that need spelling out feel too obvious to state ([Pinker](#the-science-this-rests-on); the
glossary entry is in [vocabulary.md](vocabulary.md#the-vocabulary-of-the-craft)). An agent writing CGP
holds the whole system at once, which makes its untuned prediction of the reader's state systematically
too high: it predicts the reader knows what a provider is, expects the turn the argument takes, and
carries the term that was defined two documents ago.

The correction is a deliberate procedure rather than more care. **Re-read the draft as the model reader
who holds only the common ground the text has established so far**, and at each sentence ask what that
reader knows at that exact point, not what you know. Where a term, an inference, or a leap is not yet
supported by the text above it, that is a curse-of-knowledge failure, and the fix is to supply the
missing step or defer the sentence. Run this pass as a separate reading from the drafting, because trying
to draft and de-bias at the same time fails. Two mechanical checks make it concrete: read only the
first sentence of each paragraph and confirm the story holds with no unexplained term, and for any CGP
term on the page, find the sentence earlier that put it in common ground.

## A worked pass

The value of the method is easiest to see on a real repair, so here is one paragraph simulated sentence by
sentence. The example explains what wiring does, written for the model reader who knows Rust and has met
the word "provider" once.

A first draft an agent produces under the curse of knowledge:

> Because `DelegateComponent` resolves the provider for each component key during monomorphization, and
> the consumer trait's blanket impl is parameterized over the provider the context's delegation table
> selects, a call to `greet()` dispatches statically to the wired provider. This is what makes CGP
> zero-cost.

Simulating the model reader through it predicts a bad state on every variable. **Common ground** breaks at
the first word: `DelegateComponent` is a given with no antecedent, so the reader stalls at the start.
**Working memory** overflows, because "component key", "the consumer trait's blanket impl", and "the
provider the context's delegation table selects" are three undefined chunks held at once. **The model
under construction** takes a wrong piece or no piece, and the density reads as ceremony, so **stance**
fires the skeptic's "over-engineered". The point that would have helped, zero runtime cost, sits correctly
in the stress position of the last sentence, but the reader reaches it without a model to attach it to, so
it lands on nothing. The paragraph is accurate and nearly unreadable.

The repair changes what put the reader in that state, not the tone:

> A context lists which provider supplies each capability, in a small table you write with
> `delegate_components!`. Rust resolves that table at compile time, so a call like `person.greet()`
> compiles to a direct call to the chosen provider. Nothing is looked up while the program runs.

Simulating the reader through the repair predicts the intended state. The first sentence opens on "A
context", which is in common ground, and puts the new material after it, satisfying old-before-new; its
one new thing is concrete and named, the table `delegate_components!`. Working memory holds one item at a
time. The situation model takes a correct piece, the third sentence rules out the runtime-lookup wrong
model before it can form, and the reassurance about runtime cost now lands because the reader has the
mechanism to attach it to. The machinery the first draft led with, `DelegateComponent` and the
blanket impl, is not dumbed away; it is deferred to where a reader who wants it has a model to hang it on,
per [readers.md](readers.md#the-wiring-table-and-its-machinery).

## Running the method: the checklist

Run these checks on a draft, in this order, after the structural checks the
[`point-first-writing`](https://github.com/contextgeneric/cgp-skills) skill and
[writing-styles.md](writing-styles.md) prescribe, because this pass assumes those have already passed.

Name the reader, and hold that reader for the whole pass. A state prediction is meaningless until you fix
whose state it is, and the default is the working Rust developer who is also a skeptic.

Read as that reader with only the common ground established so far, and stop at the first term, inference,
or claim the text has not yet supported. That is the curse-of-knowledge check, and it catches the most
failures.

For each of the six variables, find the sentence where its predicted value goes bad, and repair what put
it there: a given with no antecedent, more than a few held items, a wrong model forming, an unpaid
surprise, a claim that reads as a sale, a passage that spends energy without advancing.

Check the placement inside sentences: old before new, linkage in front and emphasis at the end, subject
by its verb, action in the verb, one consistent subject, light before heavy.

Check the words, not only the sentences: no word activating a wrong schema, the concrete word over the
abstract one, the common word over the rare one, and at most one new term per passage, defined once and
then reused exactly.

## The science this rests on

The method above is an engineering summary of a body of reading and language science, cited here so a
reader can check the claims. This is the section that grounds every "the reader will" statement in the
document.

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

This document goes stale in two ways, and both are worth watching. It is coupled to the documents it
directs: the model reader is [readers.md](readers.md), the words a schema activates are in
[vocabulary.md](vocabulary.md), the sentence shapes it presumes are in
[writing-styles.md](writing-styles.md), and the register it serves is in
[voice-and-register.md](voice-and-register.md), so a change to any of those can change what this method
tells a writer to do. And its scientific grounding is a body of research that advances, so a finding that
is revised or overturned is a reason to revise the rule that rests on it. Record the science honestly:
these are strong, well-replicated effects used as engineering guidance, not laws, and a rule here earns
its place by making CGP prose measurably easier to read, not by citing a study.
