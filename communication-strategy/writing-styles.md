# Writing styles: habits to prefer or avoid

This document fixes the *mechanical* habits an agent defaults to when writing prose, as opposed to the
*audience and positioning* guidance the rest of this section carries or the *paragraph-and-list*
structure the [`dual-reader-prose`](https://github.com/contextgeneric/cgp-skills) skill governs. Where
those ask "does this sound like the author" and "can both a scanner and a deep reader follow this,"
this document asks a plainer question: does this sentence do real work, or is it a shape the model
reached for because it fits almost any content? The first two sections below are checkable by pattern
and apply everywhere prose is written in this base or on the site, agent-drafted or not, because a
cleft sentence or a crutch em dash reads as generated in a reference document exactly as it does on a
landing page. The third section is a stricter register for a narrower case, and it says where that
narrower case starts.

## Cleft and pseudo-cleft inversions

**Avoid the pseudo-cleft**, a sentence of the shape "[gerund phrase or abstract noun phrase] is
[exactly/precisely] what [the real subject] [verb]s" or its mirror, "What [the real subject] [verb]s
is [the point]." Two examples, both caught in a single draft of
[the `#[cgp_component]` reference page](https://github.com/contextgeneric/cgp-website/blob/main/docs/reference/macros/cgp_component.md):

> Making room for several implementations is exactly what an ordinary Rust trait denies you.
>
> Moving `Self` out of the way is what lets more than one implementation coexist.

Say it plainly instead, with the real actor as the grammatical subject:

> `#[cgp_component]` makes it possible for several overlapping implementations of one capability to be
> defined at once, which an ordinary Rust trait flatly rejects.
>
> Moving `Self` out of the way lets more than one implementation coexist.

The second pair keeps the same meaning and the same length, which is the tell: the cleft was decorative
rather than necessary. A gerund-first sentence is not itself the problem: "Moving `Self` out of the
way lets more than one implementation coexist" still opens on a gerund and reads fine. The problem is
specifically the "is (exactly/precisely) what" or "What … is" hinge, which exists only to point back at
a subject the sentence could have named directly.

**Why the model reaches for it.** The construction is a *pseudo-cleft*, a standard device in edited
essay and explainer prose for foregrounding a claim before its subject, and that register is
overrepresented in the text a language model is trained on relative to how often the device earns its
place. It is also a low-commitment sentence opener. "Making room for several implementations is exactly
what" commits to almost nothing about the coming content and slots in front of nearly any claim, which
is what makes it a tic rather than a deliberate choice. And it dresses up a plain restatement with the
cadence of an insight, the structural cousin of the vocabulary-level inflation
[voice-and-register.md](voice-and-register.md#the-register-plain-unhurried-and-specific) already warns
against: the sentence sounds more considered than the content underneath it actually is.

**The check**: read a draft for any sentence matching "…-ing … is (exactly |precisely )?what…", "What …
(is|does) is …", or "… is what (lets|makes|means|allows) …", and rewrite it so the real subject leads.
If the rewrite says the same thing in the same space, the cleft was never earning its keep.

## Em dashes

**Avoid the em dash as a default connector.** It is the punctuation a model reaches for whenever it
has not decided how two clauses relate, because it can join an aside, a definition, a pivot, or two
independent clauses without committing to which relationship is meant. That is exactly why it shows up
as often as it does in agent-written prose, including throughout this base's own existing documents.
Overuse flattens every relationship in a paragraph into the same mark, so a reader has to work out from
context what a period, colon, or conjunction would have told them directly.

The fix is to name what the dash is actually doing and use the punctuation built for that job.

- **A parenthetical aside**, a related but non-essential remark, reads better in parentheses, set off
  by commas, or moved into its own sentence. *Before:* "the type the capability actually runs against —
  the **context**, which supplies whatever values an implementation needs as its own fields — then
  picks the provider." *After:* "The type the capability actually runs against is called the
  **context**. It supplies whatever values an implementation needs as its own fields, then picks the
  provider."
- **A definitional appositive**, naming what the preceding noun is, reads better after a colon.
  *Before:* "A provider is one of those targets — a zero-sized type such as `RectangleArea`." *After:*
  "A provider is one of those targets: a zero-sized type such as `RectangleArea`."
- **An abrupt pivot or contrast** reads better as a new sentence opening on "But," or joined with
  "though" or "yet." *Before:* "…without anyone naming which implementation applies — but it also
  means…" *After:* "…without anyone naming which implementation applies. But it also means…"
- **Two independent clauses joined for effect** read better as two sentences, or joined with "and,"
  "so," or a semicolon when the link is genuinely tight. *Before:* "Wiring is lazy — a context can
  compile while wired wrong." *After:* "Wiring is lazy: a context can compile while wired wrong." A
  colon fits better than a period here, because the second clause explains the first rather than merely
  following it. Naming the relationship, not just removing the dash, is the actual fix.
- **Setting up a list or an elaboration** reads better after a colon, which is what a colon is for.

This is a rule for prose written from now on, not a mandate to sweep the base. Nearly every existing
document here uses em dashes freely, including ones written before this rule existed, and rewriting them
wholesale would be exactly the kind of unscoped sweep [../AGENTS.md](../AGENTS.md#prose-mechanics)
already warns against for line-wrapping. Clean up an em dash when you are already revising the sentence
it sits in; leave the rest alone.

## Plain, direct English for agent-drafted content

This section is narrower than the two above and says so up front: it governs content an agent drafts
from a blank page, not content an agent only revises. [ai-disclosure.md](ai-disclosure.md) already
draws this line for a different reason, and it is the right line here too. The reference pages, the
concepts, the guides, the error catalog, and any other public page an agent writes first fall under
this section. A blog post or a tutorial does not: there, per
[ai-disclosure.md](ai-disclosure.md#revision-of-human-written-drafts), the author writes the first
draft and an agent only revises it against the knowledge base, so the author's own voice, recorded in
[author-personality.md](author-personality.md), governs instead. When it is unclear which case a page
is in, check that document's own record of how the page was made.

Write agent-drafted content in simple, direct English, close to the discipline behind
[ASD-STE100](https://www.asd-ste100.org/) (Simplified Technical English), the aerospace industry's
standard for writing a maintenance manual a reader can follow without native fluency in English. CGP's
own reference reader fits that description: fluent in Rust, not necessarily fluent in English idiom.
Borrow the standard's discipline rather than its literal controlled word list, which this base has no
machinery to enforce: one idea per sentence, a plain subject and verb, and a word the reader already
knows over one they would have to look up.

Six habits follow from that discipline, and each is worth naming on its own because each is a specific
thing to catch in a draft.

- **No metaphors.** Say what a thing does, not what it resembles. "Unlock CGP's capabilities for a
  trait" describes the effect through a lock-and-key image the reader has to translate; "give a trait
  CGP's capabilities" says the same thing directly.
- **No wordplay.** A pun depends on a reader already knowing two meanings of one word, which is exactly
  the kind of shared cultural knowledge a non-native reader may not have. If a phrase is doing double
  duty for cleverness, keep only the meaning the sentence needs.
- **No rare expressions or idioms, common or not.** An idiom's meaning does not live in its words, so a
  reader translating one literally learns nothing from it, however familiar the phrase feels to a native
  speaker. This base's own documents lean on "load-bearing" as a stand-in for "essential" or "necessary
  for the rest to work" in dozens of places; say "essential" or name what would break without it
  instead. "Belt and suspenders" for redundant safeguards is the same problem: say "two independent
  checks for the same mistake."
- **Dry, technical language: minimal jargon, plain word choice.** Keep the words a domain genuinely
  needs, such as this base's own *provider*, *context*, and *wiring*, but define each on first use, per
  [vocabulary.md](vocabulary.md) and the
  [reference writing guide](../website/writing-guides/reference.md#what-must-not-be-on-a-reference-page),
  which already require this for a different reason. Prefer the common word to the impressive one
  everywhere else, per
  [voice-and-register.md](voice-and-register.md#the-register-plain-unhurried-and-specific): this section
  asks for the same habit held to a stricter standard, because the reader here cannot be assumed to know
  an uncommon English word even when a native speaker would.
- **Prefer active voice.** A passive sentence hides who or what performs the action and asks the reader
  to recover it from context, a cost a non-native reader pays more than a native one does. "The provider
  is chosen once, during compilation" hides the actor; "the compiler chooses the provider once, at
  compile time" names it. When no single actor exists, name the closest one: the macro, the compiler, or
  the trait solver, rather than defaulting to the passive because naming the actor takes one more word.
- **No sentence that stacks several clauses with dashes and colons.** A colon may still introduce one
  plain clause or a short list, which is a normal use of a colon rather than a complex structure. What
  to avoid is chaining more than one dash- or colon-joined clause into a single sentence. *Before:* "A
  component is self-targeted when the capability is about the `Self` type — `CanGreet`, `HasErrorType`,
  every getter — and parameter-targeted when it is about a type parameter while `Self` only decides:
  `CanEncodeValue<Value>`, `CanCalculateArea<Shape>`." *After:* "A component is self-targeted when the
  capability is about the `Self` type. Examples are `CanGreet`, `HasErrorType`, and every getter. A
  component is parameter-targeted when the capability is about a type parameter and `Self` only
  decides. Examples are `CanEncodeValue<Value>` and `CanCalculateArea<Shape>`."

**The check**: before publishing agent-drafted content, read it for a figurative phrase (a metaphor, a
pun, an idiom), a passive verb with no named actor, an uncommon word with a common substitute, and a
sentence carrying more than one dash- or colon-joined clause. Fix each on sight rather than waiting for
a second pass, because each is a small, local edit that does not change the sentence's meaning.

## Checking a draft

Run all three checks together, because they catch different symptoms of the same underlying habit: a
shape or a word chosen for its generic applicability rather than for what the sentence actually needs
to say. Scan for the cleft patterns above and rewrite each with the real subject leading. Scan for em
dashes and, for each one, name the relationship it stands in for and pick the mark built for that
relationship: a colon, a period, a conjunction, or parentheses. And, for agent-drafted content, scan for
figurative language, unnamed passive actors, and stacked dash- or colon-joined clauses, and fix each
directly. None of the three checks requires understanding the subject matter, which is what makes them
worth running even on a document you did not write.

When you notice a new pattern with the same shape (generically applicable, decorative rather than
necessary, recurring across drafts), add it here in the same change and in the same form: name the
pattern, show a real before and after, say briefly why the model reaches for it, and give the check that
catches it.
