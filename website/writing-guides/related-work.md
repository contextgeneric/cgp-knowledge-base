# Writing a comparison page

A comparison page explains CGP to a reader who already knows a related idea from another language or
paradigm, such as type classes, dependency injection, ML modules, C++ policies, algebraic effects, or
reflection. It maps CGP into that reader's vocabulary, shows the two side by side in code, states what
each costs, and says plainly where the reader's own tool is the better choice. The pages are ported
from the internal [related-work](../../related-work/README.md) comparisons, and this guide fixes what
changes in the port.

- **Where they live**: `docs/comparisons/`, a top-level category labelled **Comparisons**, directly
  after Concepts in the sidebar
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from**: [related-work/](../../related-work/README.md), one internal document per page,
  which stays the source of truth
- **Records**: one record, [pages/comparisons.md](../pages/comparisons.md), for the whole section, per
  the [ported-catalog exception](../../AGENTS.md#registering-a-document-and-adding-a-section)
- **Reading**: the shared set and [the comparison pages' row](README.md#comparison-pages) of the
  reading map

## What the page is for

**A comparison page serves a reader who arrives with a working mental model**, one of the profiles in
[readers.md](../../communication-strategy/readers.md#readers-by-prior-mental-model), and already holds
most of CGP's structure under other names. The fastest way to teach that reader is to name the
correspondence, then mark where it breaks.

**It succeeds when the reader can state, in their own vocabulary, what CGP does, what it does not do
that their tool does, and where their tool remains the better choice.** A reader left believing CGP is
their tool with a feature switched off will read the first difference as a defect; one left believing
CGP replaces their tool has been started on an argument the project does not want.

## How it differs from an explanation page

A comparison page is understanding-oriented, so the [explanation guide](explanation.md) supplies its
base rules: name the question and the page's extent, show code as illustration, state the cost, and
end by routing. Four things set it apart:

- **The organizing question looks outward**: how CGP relates to the idea the reader knows. Most of the
  page explains another system, faithfully enough that its own community would recognize the account.
- **It cites sources.** A claim about how Scala resolves a `given` is a claim about someone else's
  system, credible only when traceable to its documentation and literature.
- **It shows code in another language**, compiled against a named toolchain before publication, which
  the website's Rust-only verification crate cannot do.
- **Two communities read it**: the Rust reader evaluating CGP, and the compared tool's practitioners,
  who find the page through their own vocabulary. Write every sentence about their tool as if its
  maintainers are reading.

## Derived from the internal comparison, and what changes

**A comparison page is ported rather than written fresh**, because the internal document already
carries the faithful account, the compiled snippets, the cited sentiment, and the honest boundary. Four
transformations make the port, and the first decides whether it is publishable:

- **Retire the positioning section, and apply it instead.** The internal *Presenting CGP to someone
  who knows this* section is the project's playbook for persuading the reader, and is never published
  as prose. Its vocabulary map becomes the *In your terms* table; the expectations it says to correct
  become *What to expect that differs*, written as facts about CGP; and the framings it says to avoid
  become checks under [Checking a draft](#checking-a-draft).
- **Compress the concept refresher.** The internal *The concept in depth* section teaches an agent the
  compared idea; the public reader already knows it. Keep the terms the comparison needs, one cited
  snippet per sub-concept, and a link to the primary source. The test, and the port's one judgement
  call: a practitioner skims it without irritation, and a curious Rust reader can still follow.
- **Re-point every link**, per the
  [one-way rule](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links): a
  concept to its Concepts page, a reference link to its reference page, an example to the tutorial
  or Projects example page with the same scenario or inlined code, a blog record to the live post,
  and a communication-strategy link dropped. A point drawn from the
  [unpublished incoherent-Rust draft](../blog/incoherent-rust-today.md) is never cited: attribute it
  to the [RustLab transcript](../blog/rustlab-2025-coherence.md) where the transcript makes it,
  state it as the project's own analysis where it does not, and otherwise hold it until the post
  publishes.
- **Keep the Sources section**, including the sentence recording which toolchain compiled each family
  of snippets, since it says what was verified and what was transcribed.

The [synchronization rule](../../AGENTS.md#the-synchronization-rule) binds the page to its internal
document: a change to a CGP construct or to the compared tool updates both in the same change, and a
public page that disagrees with its internal document is the one in error.

## The page shape

Every comparison page has the same sections in the same order, so a reader of one can skim the next.
The titles below are jobs; a page's headings may name the compared tool.

- **Orientation**, two or three sentences: CGP in one sentence, naming Context-Generic Programming in
  full beside a short form of the tag line and linking the Introduction, related to the compared idea
  where it meets it, per the
  [naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page); who
  the page is for, what it covers, and how far it goes, because the pages are long.
- **In your terms**, a short table mapping the reader's interface, implementation, resolution step,
  constraint, and environment onto component, provider, wiring, impl-side dependency, and context.
  "Context" is glossed here on first use, with the canonical gloss from
  [vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each).
- **The idea, briefly**: the compressed refresher, each sub-concept with one cited snippet in the
  tool's own language, and what its users value, stated as they would. Name the version where behavior
  is version-specific.
- **How CGP expresses it**: the same problems in CGP beside those snippets, saying where the two align
  and part. State which of CGP's three shapes each snippet wires, per
  [vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target).
- **What each approach costs**, both sides in one section. The compared tool's costs as its community
  states them, cited; CGP's ordinary costs (the wiring, the declarations, the compile-time work, and the
  raw diagnostics), with the canonical sentence copied unchanged: `cargo cgp check` leads with the root
  cause for the classes it recognizes, and the tool does not yet reshape every class.
- **Where the other tool is the better choice**, its own section, never folded into the costs.
- **What to expect that differs**: the expectations the positioning section says to correct, as plain
  facts about CGP (it does not infer a provider from scope, a provider receives the context rather than
  a continuation, the structure is a type rather than a descriptor, the container is the type system),
  each followed by why CGP is arranged that way.
- **Where to go next**: the Concepts page behind the comparison, the tutorial or Projects example page
  that puts it to work, and the neighbouring comparison a reader of this one likely knows.
- **Sources**: the internal document's framed list, re-pointed, opening with the toolchain sentence.

The page closes with the provenance note in the wording the reference and Concepts pages share,
adding that its CGP code was verified against the library's source and its other snippets against
the toolchains named in Sources, per
[ai-disclosure.md](../../communication-strategy/ai-disclosure.md#linking-to-it-from-a-page).

## Writing about another community's tool

**Never disparage the compared tool, and assume its maintainers are reading**, per the
[base-wide rule](../../AGENTS.md#this-repository-is-public). The internal
documents faithfully record what users dislike about their tools, so three habits keep the port
honest:

- **Attribute opinion as opinion**: a cited report of why a community steers away from a practice, not
  a jab at the tool.
- **Prefer the tool's own documentation for its own limits**: quoting GHC's manual on overlapping
  instances is fairer than paraphrasing a complaint.
- **Cut the sentence that reads as mockery**, even when it is true.

**The enhances-not-replaces frame survives the comparison.** Internal shorthand such as "dependency
injection without a container" can read on the site as CGP replacing the reader's tool or Rust's
traits, so every page's orientation states that CGP is a library on stable Rust, that a consumer trait
is an ordinary trait, and that the comparison is about where the ideas meet, per
[identity.md](../../communication-strategy/identity.md).

**Qualify bridge terms** in the sentence that uses them, per
[vocabulary.md](../../communication-strategy/vocabulary.md#words-and-framings-to-avoid): compile-time
structural reflection, the resume-in-place fragment of effect handlers, compile-time and
reflection-free dependency injection.

**Hold the vocabulary line.** Introduce the compared tool's term once, in the refresher, then let the
CGP side speak CGP. Never call a CGP construct a capability, even on the capabilities page.

**Distil reactions to CGP; never link or quote them.** Sentiment about the compared tool is cited;
sentiment about CGP is summarized without a thread or a name, per the
[evidence rule](../../communication-strategy/evidence.md).

## Code and verification

**CGP code goes in the website's `example-code` crate**, at `tests/comparisons/<page>.rs`, one file per
page and one module per heading, per the crate's [conventions](../site.md#the-example-code-crate),
with `tests/comparisons_tests.rs` as the section's entry point. A snippet shown as rejected by Rust,
such as overlapping impls failing with `E0119`, is a `trybuild` compile-fail fixture under
`tests/compile_fail/comparisons/`. Every wired context carries a `check_components!` assertion. Draw
CGP snippets from the internal document, which takes them from [examples/](../../examples/README.md),
in the modern idioms the [guides](../../cgp/guides/README.md) teach.

**Foreign snippets are compiled against a named toolchain before publication**, recorded in the
page's Sources sentence, per the
[related-work rules](../../related-work/writing-guide.md#compile-the-foreign-snippets-and-record-the-toolchain).
A snippet that cannot be run, because the feature is a proposal or a research fork, says so beside
the code.

**Say when a syntax is version-specific**, naming the older form, as the internal documents do: OCaml's
`match ... with effect` from 5.3, Scala's colon-form `given` from 3.6, Zig's lowercase type tags from
0.14.

## The index page

**The category has a hand-written index, because a reader holding one background needs routing to one
page.** It says what the section is for in two sentences, naming Context-Generic Programming, then
routes by background with a short table from *what you know* to *the page to read*, grouped as the
internal [catalog](../../related-work/README.md) groups them, with Rust's own proposals and C++
policy-based design first. It closes with what every page shares: a mapping into the reader's terms,
code side by side, costs on both sides, and where their tool wins.

## Placement, navigation, and bookkeeping

**The section is `docs/comparisons/`, labelled *Comparisons***, linked to its index page, at the
position [site.md](../site.md) records. The label and the URL use the reader's word, matching
`concepts` and `tutorials`; "related work" names the internal directory and stays there.

**Page titles use the compared concept's name**, because that is what the reader searches for, with a
`description` naming the reader the page serves. The problem-oriented titles
[formats.md](../../communication-strategy/formats.md#titles-first-lines-and-search) prescribes for
explanations do not fit, since this reader arrives with a vocabulary rather than a problem.

**Publishing the section adds a public claim**: the author reads every page's *What each approach
costs* and *Where the other tool is the better choice* in full before publication, per the
[authorship rule](../../communication-strategy/ai-disclosure.md#the-two-claims-that-are-easiest-to-get-wrong),
and the [disclosure page](../pages/ai-disclaimer.md) says so.

## What must not be on a comparison page

- **No positioning prose**: nothing telling the reader which intuitions to build on, which analogy to
  accept, or which expectation to drop.
- **No knowledge-base links**, and no citation of an unpublished draft.
- **No disparagement of the compared tool, its language, or its community.**
- **No claim that CGP is the compared tool**: not "an effect system", "a reflection system", "a DI
  framework", "specialization for stable Rust", "templates done right", or "gives Rust capabilities"
  without the qualifier. Each makes the reader look for a feature CGP lacks.
- **No re-teaching of CGP fundamentals**: one orientation paragraph and a link; the Concepts tier
  carries the argument.
- **No mention of agent support.** The cost section names the diagnostics and the wiring and links
  *Modularity Hierarchy*, one of the three places
  [message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these)
  states the agent skill beside the costs; a dozen pages each mentioning AI would read together as the
  AI-led pitch the strategy rules out.
- **No first-person narration.** Ground a judgement that rests on the author's choice, and link the
  [transcript](../blog/rustlab-2025-coherence.md) or post where he makes it.
- **No unverified snippet in either language.**

## Checking a draft

- **Read the page as a maintainer of the compared tool.** Every sentence about their tool is one they
  would accept as fair, with its source visible; cut or attribute any other.
- **Find the positioning that leaked**: any sentence telling the reader what to think of their own
  tool belongs to the internal document.
- **Check the four framings**: grep for "effect system", "reflection system", "DI framework",
  "specialization", "templates", and "capabilit", and confirm each occurrence is qualified or about the
  compared tool.
- **Find the section where the other tool wins**; if it is missing or folded into the costs, the page
  oversells to the audience least tolerant of it.
- **Check the frame**: the orientation says CGP is a library on stable Rust and consumer traits are
  ordinary traits, and nothing later implies the reader should abandon their tool.
- **Grep for links into the knowledge base and for the incoherent-Rust draft.**
- **Verify every snippet**: CGP code compiles in the `example-code` mirror with a check per wired
  context; foreign code compiles against the toolchain named in Sources, and that sentence is present.
- **Check the shape statements and the gloss**: every CGP snippet names its context shape, and
  "context" is glossed on first use in *In your terms*.
