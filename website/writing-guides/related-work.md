# Writing a comparison page

A comparison page explains CGP to a reader who already knows a related idea from another language or
paradigm: type classes, dependency injection, ML modules, C++ policies, algebraic effects,
reflection. It maps CGP into the vocabulary that reader already holds, shows the two side by side in
code, states what each costs, and says plainly where the reader's own tool is the better choice. The
pages are ported from the internal [related-work](../../related-work/README.md) comparisons, and
this guide fixes what changes in the port.

- **Where they live** — `docs/comparisons/`, a top-level category labelled **Comparisons**, placed
  directly after Concepts in the sidebar
- **Voice** — project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from** — [related-work/](../../related-work/README.md), one internal document per page,
  which stays the source of truth
- **Scale** — eleven pages plus a hand-written index, shipped with the v0.8.0 relaunch
- **Records** — one entry in [site-structure.md](../site-structure.md) for the whole section, per
  the [ported-catalog exception](../AGENTS.md#registering-a-document)

## What the page is for

A comparison page serves the reader who arrives with a working mental model and wants to know where
CGP fits in it. [readers.md](../../communication-strategy/readers.md#readers-by-prior-mental-model)
profiles these readers: the functional-programming practitioner, the enterprise dependency-injection
developer, the dynamic-language developer, the framework author, and the language-design reader.
Each already holds most of CGP's structure under other names, so the fastest way to teach them is to
name the correspondence and then mark the places where it breaks.

The success condition is that the reader can state, in their own vocabulary, three things: what CGP
does, what it does not do that their tool does, and where their tool remains the better choice. A
page that leaves the reader believing CGP is a version of their tool with a feature switched off has
failed, because the first construct that behaves differently will read as a defect. A page that
leaves them believing CGP replaces their tool has failed for the opposite reason, and for this
audience it has also started an argument the project does not want.

## How it differs from an explanation page

A comparison page is understanding-oriented and read away from a keyboard, so the
[explanation guide](explanation.md) supplies its base rules: name the question and the page's extent
up front, show code as illustration, state the cost, and end by routing. Four things set it apart,
and they are why it needs a guide of its own.

**The organizing question looks outward.** A Concepts page asks *why does CGP work this way*; a
comparison page asks *how does CGP relate to the idea I already know*. The subject of most of the
page is therefore something other than CGP, and the page has to explain it faithfully enough that
its own community would recognize the account.

**It cites sources.** No other page type on the site carries a bibliography. A comparison page does,
because a claim about how Scala resolves a `given` or how Lean orders instances is a claim about
someone else's system, and its credibility rests on being traceable to that system's documentation
and literature.

**It shows code in another language.** Foreign snippets are claims about that language and are
compiled against a named toolchain before they are published, which the website's Rust-only
verification crate cannot do for them.

**Two communities read it.** The Rust reader evaluating CGP is one audience; the practitioners of
the compared tool, who will find the page by searching for their own vocabulary, are the other.
Every sentence about the compared tool is written as if its maintainers are reading, because some
will be.

## Derived from the internal comparison, and what changes

The internal documents already carry the faithful account, the compiled snippets, the cited
sentiment, and the honest boundary, so **a comparison page is ported rather than written fresh**.
Four transformations turn one into the other, and the first is the one that decides whether the port
is publishable at all.

**Retire the positioning section, and apply it instead.** Every internal document closes with
*Presenting CGP to someone who knows this*, and that section is the project's playbook for
persuading the reader. It is never published as prose: a reader who is told which of their
intuitions to build on and which expectations to defuse is being read the marketing plan. Its
content becomes the page's structure. The vocabulary map it opens with becomes the *In your terms*
table near the top of the page. The expectations it says to correct become the *What to expect that
differs* section, written to the reader as facts about CGP rather than as advice about the reader.
The framings it says to avoid become checks on the draft, listed under
[Checking a draft](#checking-a-draft).

**Compress the concept refresher.** The internal *The concept in depth* section exists so that an
agent can learn the compared idea well enough to write about it. The public reader already knows it.
The section shrinks to the terms the comparison needs, one cited snippet per sub-concept, and a link
to the primary source for the rest. This is the one judgement call the port carries, and the test is
whether a practitioner would skim it without irritation while a curious Rust reader could still
follow the comparison from it.

**Re-point every link.** The internal documents link into concepts, the reference, examples, the
communication strategy, and the website records, none of which a public page may link, per the
[one-way rule](../AGENTS.md#the-one-way-link-rule). A concept link becomes its Concepts page, a
reference link becomes its reference page, an example link becomes the tutorial or deep dive
carrying the same scenario or the code is inlined, a blog record becomes the live post, and a
communication-strategy link is dropped. One case needs care: two internal documents draw on the
[record of the unpublished incoherent-Rust draft](../blog/incoherent-rust-today.md), which cannot
be cited. Attribute those points to the [RustLab transcript](../blog/rustlab-2025-coherence.md)
where it makes them, state them as the project's own analysis where it does not, and otherwise hold
them until that post publishes as task B2.

**Keep the Sources section.** Citations are what let the page survive a skeptic who prefers the
other tool, and the sentence recording which toolchain compiled each family of snippets stays
because it says honestly what was verified and what was transcribed.

The internal document remains the source of truth, and the
[synchronization rule](../../AGENTS.md#the-synchronization-rule) binds both: a change to a CGP
construct or to the compared tool updates the internal document and the public page in the same
change, and a public page that disagrees with its internal document is a defect in the public page.

## The page shape

Every comparison page descends through the same sections in the same order, so a reader who has read
one can skim the next by habit. The section titles below are jobs; the headings on the page name the
compared tool where that reads better.

**Orientation.** Two or three sentences. Say what CGP is in one sentence, with the settled
descriptor from [identity.md](../../communication-strategy/identity.md) and a link to the
Introduction, since this page may be a reader's first contact. Say who the page is for and what it
covers, and say how far it goes, because these pages are long.

**In your terms.** A short table mapping the reader's vocabulary onto CGP's: their interface, their
implementation, their resolution step, their constraint, and their environment against component,
provider, wiring, impl-side dependency, and context. This is the hook for the reader who knows the
tool, and it is where "context" is glossed on first use, with the canonical gloss from
[vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each).

**The idea, briefly.** The compressed refresher: the sub-concepts the comparison needs, each with
one cited snippet in the tool's own language, and what its users value about it, stated as they
would state it. Name the version where behavior is version-specific.

**How CGP expresses it.** The same problems in CGP, shown beside the snippets above, with prose
saying where the two align and where they part. State which of CGP's three shapes each snippet
wires, because the comparisons span all three and the internal document already records it; the
qualifiers and the misreadings they prevent are in
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target).

**What each approach costs.** Both sides, in one section. The compared tool's costs are stated as
its own community states them, with the citation. CGP's costs are the ordinary ones, stated in the
author's plain register: the wiring, the declarations, the compile-time work, and the raw
diagnostics, with the canonical sentence copied rather than paraphrased: `cargo cgp check` leads
with the root cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not yet
reshape every class.

**Where the other tool is the better choice.** Its own section, never folded into the costs. Every
internal document names these cases, and they are the sentences that earn the page its credibility
with both audiences.

**What to expect that differs.** The expectations the internal positioning section says to correct,
written as plain facts about CGP: it does not infer a provider from scope, a provider returns
exactly once, the structure is a type rather than a descriptor, the container is the type system.
Each is followed by why CGP is arranged that way, so the difference reads as a design choice rather
than a gap.

**Where to go next.** Route to the Concepts page carrying the idea behind the comparison, the
tutorial or deep dive that puts it to work, and the neighbouring comparison a reader of this one is
likely to know.

**Sources.** The framed list from the internal document, re-pointed where an entry was internal,
opening with the toolchain sentence.

The page closes with the provenance note, in the wording the reference and Concepts pages share,
with one addition: a comparison page's CGP code was verified against the library's source and its
other snippets against the toolchains named in Sources. The mechanics are in
[AGENTS.md](../AGENTS.md#disclosing-ai-use-on-a-page).

## Writing about another community's tool

**Never disparage the compared tool, and assume its maintainers are reading.** This is the
[base-wide rule](../../AGENTS.md#this-repository-is-public) and the
[communication strategy's guardrail](../../communication-strategy/AGENTS.md#honesty-is-the-strategy),
and a comparison page is where it is most easily breached, because the internal documents
faithfully record what users dislike about Spring, Scala implicits, `ImplicitParams`, and Lean's
instance search. Three habits keep the port honest. **Attribute opinion as opinion**: "Spring's
community steers toward constructor injection because field injection hides dependencies" is a cited
report, while "Spring hides your dependencies" is a jab. **Prefer the tool's own documentation for
its own limits**: GHC's manual warns that overlapping instances can give rise to incoherence, and
quoting the manual is fairer than paraphrasing a complaint. **Cut the sentence that reads as
mockery** even when it is true. The internal document may keep it; the page does not.

**The enhances-not-replaces frame must survive the comparison.** Phrases that are accurate
internally, such as "a type-class system without coherence" or "dependency injection without a
container", can read on the site as CGP replacing the reader's tool or replacing Rust's traits.
Every page states in its orientation that CGP is a library on stable Rust, that a consumer trait is
an ordinary trait, and that the comparison is about where the ideas meet rather than which to
abandon. The frame is settled in [identity.md](../../communication-strategy/identity.md).

**Qualify bridge terms.** "Structural typing", "duck typing", "dependency injection", "reflection",
and "effect system" are the words readers reach for, and each names something CGP does only in part.
Use them to meet the reader and qualify them in the same sentence, per
[vocabulary.md](../../communication-strategy/vocabulary.md#words-and-framings-to-avoid):
compile-time structural reflection, the exactly-once fragment of effect handlers, compile-time and
reflection-free dependency injection.

**Hold the vocabulary line.** Introduce the compared tool's term once, in the refresher, and then
let the CGP side speak CGP. Never call a CGP construct a capability, even on the capabilities page,
whose whole argument is why the word does not fit.

**Distil reactions to CGP; never link or quote them.** The internal documents do not cite reactions
to CGP, and a page must not add any. Community sentiment about the compared tool is cited; sentiment
about CGP is summarized without a thread or a name, per the
[evidence rule](../../communication-strategy/evidence.md).

## Code and verification

**CGP code goes in the website's `example-code` crate**, at `tests/comparisons/<page>.rs`, one
file per page and one module per heading, following the crate's
[conventions](../site-structure.md#the-example-code-crate). The section needs its own
integration-test entry point, `tests/comparisons_tests.rs`, declaring the module tree the way the
other sections' entry points do. A snippet the page shows as rejected by
Rust, such as the overlapping impls that fail with `E0119`, is a `trybuild` compile-fail fixture
under `tests/compile_fail/comparisons/`. Every wired context carries a `check_components!`
assertion, which is what confirms the wiring resolves rather than merely parses. Draw CGP snippets
from the internal document, which already takes them from [examples/](../../examples/README.md),
and prefer the modern idioms the [guides](../../cgp/guides/README.md) teach.

**Foreign snippets are compiled against a named toolchain before publication**, and the toolchain
and version are recorded in the page's Sources sentence, per the
[related-work rules](../../related-work/AGENTS.md#compile-the-foreign-snippets-and-record-the-toolchain).
The verification crate cannot hold them, so the page's own record is where a later reviewer learns
what was checked. A snippet that cannot be run, because the feature exists only as a proposal or a
research fork, says so beside the code.

**Say when a syntax is version-specific**, with the older form named, so a reader meeting it
elsewhere is not misled: OCaml's `match ... with effect` from 5.3, Scala's colon-form `given` from
3.6, Zig's lowercase type tags from 0.14. The internal documents carry these notes and the port
keeps them.

## The index page

The category needs a hand-written index rather than a generated list, because a reader arrives
holding one background and needs to be routed to one page. The index opens by saying what the
section is for in two sentences, then routes by the reader's background: a short table from *what
you know* to *the page to read*, grouped as the internal [catalog](../../related-work/README.md)
groups them, with the two pages a Rust reader compares CGP to first, Rust's own proposals and C++
policy-based design, listed first. It closes by saying what every page shares, so a reader knows the
shape before opening one: a mapping into their terms, code side by side, costs on both sides, and
where their tool wins.

## Placement, navigation, and bookkeeping

The section is a new top-level category at `docs/comparisons/`, labelled **Comparisons** in its
`_category_.json` and linked to its index page rather than a generated index. It sits directly after
Concepts, which moves Reference, `cargo-cgp`, and AI down one position each; the renumbering lands
with the section. The label and the URL both use the reader's word, matching `concepts` and
`tutorials` beside them; "related work" names the internal directory and the academic habit it
borrows from, and stays there. The order and the reader paths it serves are in
[information-architecture.md](../information-architecture.md).

Page titles use the compared concept's name, because that is what the reader searches for, with a
`description` in the front matter naming the reader the page serves. Problem-oriented titles, which
[formats.md](../../communication-strategy/formats.md#titles-first-lines-and-search) prescribes for
explanations, do not fit here: the reader is not arriving with a problem but with a vocabulary.

The section ships with the v0.8.0 relaunch. It is new content rather than a defect in an existing
page, so it was planned as post-release work like the deep dives, and it was written on the release
branch instead once the sources proved close enough to port in one pass. Publishing it changed a
public claim: the author reads the *What each approach costs* and *Where the other tool is the better
choice* sections of every comparison page in full before publication, per the
[authorship rule](../AGENTS.md#who-drafts-a-page-and-who-reads-it-before-it-publishes), and the
[disclosure page](../site-structure.md#ai-disclaimer) says so.

## What must not be on a comparison page

**No positioning prose.** Nothing that tells the reader which of their intuitions to build on, which
analogy to accept, or which expectation to drop. The page states facts and lets the reader place
them.

**No knowledge-base links**, per the one-way rule, and no citation of an unpublished draft.

**No disparagement of the compared tool, its language, or its community**, however faithfully the
internal document records the complaint.

**No claim that CGP is the compared tool.** Not "an effect system", not "a reflection system", not
"a DI framework", not "specialization for stable Rust", not "templates done right", and not "gives
Rust capabilities" without the qualifier. Each of these is a framing the internal document names as
one to avoid, and each makes the reader look for a feature CGP lacks.

**No re-teaching of CGP fundamentals.** One orientation paragraph and a link. The Concepts tier
carries the argument, and a comparison page that derives the consumer/provider split from scratch
has become a worse copy of *Consumer and provider traits*.

**No mention of agent support.** The cost section names the diagnostics and the wiring as costs and
stops. The agent skill that reduces them is stated in the four places
[tasks.md](../tasks.md#two-threads-that-run-through-several-tasks) fixes, and the cost section links
the *Modularity Hierarchy* page, which is one of them, rather than repeating the mitigation. Twelve
pages that each mention AI beside their costs would read, taken together, as the AI-led pitch the
strategy rules out.

**No first-person narration.** Where a judgement rests on the author having made a choice, ground it
and link the [transcript](../blog/rustlab-2025-coherence.md) or post where he makes it.

**No unverified snippet in either language.**

## Where the current pages stand

All eleven pages and the index are written, and the section's record in
[site-structure.md](../site-structure.md#comparisons) carries the current state: the two code
adaptations the port made (the encoder pair in place of `cgp-serde`'s providers, and a local field
writer in place of a quotation of `cgp-serde`'s source), the claims that will decay on their own, and
the mirror layout. Fourteen Concepts pages route to the comparison for their idea from their onward
reading. What remains against this guide is the author's read of each page's two judging sections.

**Two sources depend on the unpublished incoherent-Rust draft**, and the pages ported from them follow
the rule under [Derived from the internal comparison](#derived-from-the-internal-comparison-and-what-changes):
the Rust proposals page states the Cairo reading, the context-as-dictionary framing, and the
single-context limits as the project's analysis, and attributes to the RustLab transcript what the
transcript makes; the algebraic-effects page keeps the coeffects pointer as a pointer. When B2
publishes the post, both pages gain a citation.

## Checking a draft

**Read the page as a maintainer of the compared tool.** Every sentence about their tool should be
one they would accept as fair, with its source visible. A sentence they would object to is cut or
attributed.

**Find the positioning that leaked.** Any sentence telling the reader what to think of their own
tool, which analogy to accept, or which expectation to drop belongs to the internal document. The
page states CGP's behavior and stops.

**Check the four framings.** Grep the draft for "effect system", "reflection system", "DI
framework", "specialization", "templates", and "capabilit", and confirm each occurrence is qualified
or is about the compared tool rather than about CGP.

**Find the section where the other tool wins.** If it is missing or folded into the costs, the page
is overselling to the audience least tolerant of it.

**Check the frame.** The orientation says CGP is a library on stable Rust and that consumer traits
are ordinary traits, and nothing later implies the reader should abandon their tool or that CGP
replaces Rust's.

**Grep for links into the knowledge base and for the incoherent-Rust draft.** One surviving `../../`
link or one citation of the draft is a broken or an improper page.

**Verify every snippet.** CGP code compiles in the `example-code` mirror with a check per wired
context; foreign code compiles against the toolchain named in Sources, and the sentence naming that
toolchain is present.

**Check the shape statements and the gloss.** Every CGP snippet says which context shape it wires,
and "context" is glossed on first use in the *In your terms* table.
