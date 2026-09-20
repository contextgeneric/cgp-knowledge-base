# The author's personality and preferences

Preserve CGP's author's voice by following his stated preferences and learning from his published
writing.

This document governs the rest of the communication strategy. When another rule conflicts with a
preference recorded here, correct that rule. [voice-and-register.md](voice-and-register.md) turns
this account into instructions for individual passages.

## Why this document exists at all

CGP's public writing should reflect its author, Soares Chen. He writes personally about his work,
uncertainties, and limits. General marketing advice can produce accurate but impersonal copy that
he would not write. This document gives writers a more specific basis for their choices.

Stated preferences take priority over observed habits. The
[blog corpus](../website/blog/README.md), [RustLab transcript](../website/blog/rustlab-2025-coherence.md),
and [site pages](../website/site-structure.md) provide evidence of habits. The preferences below
record decisions the author gave directly. Keep the distinction clear: published copy can include
placeholder wording, and an observed pattern need not govern every future piece.

## Who he is

Soares's work combines practical modular programming with an interest in programming-language
theory. In the [RustLab transcript](../website/blog/rustlab-2025-coherence.md), he describes more
than twenty years of programming, substantial Haskell and JavaScript experience, and work on Rust
AI inference infrastructure at [Tensordyne](https://www.tensordyne.ai/).

CGP grew from his work on the [Hermes IBC relayer](https://github.com/informalsystems/hermes) at
[Informal Systems](https://informal.systems/), beginning around July 2022. A large `ChainHandle`
trait led him to use blanket implementations for dependency injection; that work developed into the
[Hermes SDK](https://github.com/informalsystems/hermes-sdk/). His earlier projects included a
JavaScript component system and a Haskell algebraic-effects library using implicit parameters.
The [launch post](../website/blog/early-preview-announcement.md) records this background.

Use this background where it explains a choice. His writing can discuss row polymorphism, tagless
final, or the expression problem when readers know those ideas. He also develops CGP largely in his
own time, so public writing should remain candid about capacity and invite readers to help direct
his effort without promising coverage he cannot provide.

## How he writes, as evidenced by the corpus

His published work favors detailed explanations with a clear entry. The
[Hypershell announcement](../website/blog/hypershell-release.md) runs to roughly 16,500 words and
opens with a reading-time estimate and a section preview. Keep the introduction focused, explain
what a long piece covers, and allow the subject the depth it needs.

He establishes the problem before introducing a construct. The RustLab talk explains global trait
lookup and why coherence is necessary before presenting CGP's approach. The
[v0.8.0 draft](../website/blog/v0-8-0-release.md) shows a growing wiring table before introducing
namespaces, and the [area tutorial](../website/tutorials/area-calculation.md) introduces constructs
as answers to problems readers have just encountered. Explain existing tools fairly before showing
where CGP helps.

He discusses costs as part of explaining the technology. The Hypershell post covers learning,
diagnostics, dynamic loading, and compile times, and distinguishes rough experiments from firm
findings. The Introduction acknowledges adoption risk, and the
[new-website post](../website/blog/new-website.md) describes the limits of LLM-produced design.
Preserve known costs even when omitting them would make the pitch easier.

He credits related work and qualifies comparisons. His writing distinguishes CGP from tagless
final and acknowledges influences including Servant, `unsynn`, Haskell typeclasses, and Kani.
Describe an alternative accurately before explaining the difference; avoid turning that difference
into unsupported superiority.

He uses personal history to explain why a project exists. The Hypershell post recounts the earlier
project behind its name, and the launch post connects CGP to his attempts at modular programming.
Use these accounts when relevant rather than inventing an origin story for a pitch.

He addresses readers warmly and asks for direction. He thanks them for reading, asks which problem
domains they want covered, and acknowledges that he cannot cover them all. Enthusiasm belongs in
this voice when it expresses pleasure in sharing the work, without inflating a feature claim.

He explains his strategy directly when it matters. The Hypershell post describes enabling
developers who value modularity to build reusable components for developers who do not. It also
explains his reasons for steering CGP away from web frameworks. Use these stated motivations where
relevant instead of supplying a more convenient story.

## Stated preferences

The author's stated preferences govern recurring choices in public writing:

- **Match voice to the page.** The homepage, documentation, and tutorials speak as the project,
  addressing the reader plainly without first-person narration. Blog posts use his personal voice.
  Preserve the personal sponsorship section on the
  [Contribute page](https://contextgeneric.dev/docs/contribute).
- **Keep the settled tag line and framing.** CGP is "a language extension for Rust, with pluggable
  trait implementations at compile-time." Show how it enhances Rust's trait system, including
  ordinary direct implementations and gradual adoption. [identity.md](identity.md) owns the wording.
- **Give the homepage a clear purpose.** Help readers understand CGP and its benefits, then direct
  them to teaching material. Follow the [homepage guide](../website/writing-guides/homepage.md).
- **Move extended explanations to dedicated pages.** When a homepage section needs essay-length
  treatment, link to an explanation page. Writing guides should identify that destination.
- **Use frameworks selectively.** Apply useful ideas from Diátaxis and other methods without
  treating every rule as binding. CGP tutorials may explain internals when readers need that
  understanding to trust the macros.
- **Support both tutorial approaches.** First-principles tutorials use simple examples, such as
  [area calculation](../website/tutorials/area-calculation.md). Applied tutorials build something
  practical without explaining every mechanism. Both are valid; follow the
  [tutorial guide](../website/writing-guides/tutorial.md).
- **Improve placeholder copy when editing it.** Replace inflated phrases such as "a beautiful
  overhaul redesign" with direct wording. This permits local improvements, not an unsolicited
  site-wide rewrite. Preserve personal passages and the rules for dated posts in
  [voice-and-register.md](voice-and-register.md#improving-copy-that-is-already-published).
- **Disclose the production process plainly.** State what AI did, the limits of review, and the
  author's responsibility. Follow [ai-disclosure.md](ai-disclosure.md) for the different levels;
  do not turn disclosure into a boast, apology, or debate about legitimacy.

## What this means for an agent writing in his name

Review a draft for choices the author would recognize as his own. Give explanations the space they
need and make their scope clear at the start. Explain the existing approach fairly before
introducing CGP. State the relevant cost alongside the benefit in plain words.

Prefer a concrete concession to a reassuring hedge. "This is more machinery than a plain trait
needs" names a cost. "While there is a modest learning curve, the benefits are substantial" leaves
both the cost and the benefit vague.

Keep claims within the available evidence. Do not invent benchmarks, adoption figures, or claims
that developers love a feature. Remove intensifiers that add praise without information, and let
the specific claim carry the point.

## Keeping this document current

Update this account when new writing or direct feedback changes it. A substantial post with a
different register may qualify an observed habit; a stated preference can change a rule. If the
author rejects a draft produced from this guidance, use that feedback to correct the guidance as
well as the draft.

Continue to label preferences and observations separately. A stated preference is binding. An
observed habit describes the corpus and allows departures where a new piece needs them.
