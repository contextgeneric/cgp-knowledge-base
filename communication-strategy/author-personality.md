# The author's personality and preferences

This document records who CGP's author is as a writer — the temperament, habits, and stated
preferences behind everything the project publishes — so that a piece written by an agent reads as
something he would have written rather than as generic technical marketing. Every other document in
this section is downstream of this one: when a rule elsewhere conflicts with what is recorded here,
this document wins, because the rules exist to serve the voice rather than the other way round.

## Why this document exists at all

Most communication guidance is written as if a project had no author, and CGP is the opposite case.
CGP is one person's decade-long line of work, published under his name, in the first person, with his
career considerations and his uncertainties left in the text. A strategy document that optimizes for
an abstract "Rust audience" without accounting for that will reliably produce copy he rejects — not
because it is wrong, but because it is nobody's. The default failure mode of an agent writing here is
a fluent, confident, adjective-rich register that no human wrote and no reader trusts, and the
defence against it is a written record of what the actual author sounds like.

The record has two sources, and both are checkable. The first is the published corpus — the
[blog posts](../website/blog/README.md), the [RustLab transcript](../website/blog/rustlab-2025-coherence.md),
and the site's [docs pages](../website/site-structure.md) — read as evidence of habit rather than as
instruction. The second is a set of preferences the author stated directly while this section was
being re-authored, which are recorded below as decisions rather than inferences. Where the two
disagree, the stated preference governs, because the corpus includes copy the author himself
describes as placeholder.

## Who he is

Soares Chen is CGP's creator, and the biography matters because it is load-bearing in his own
writing rather than decoration on it. He has been programming for over twenty years, has done
substantial functional programming in Haskell and JavaScript, and works as a software engineer at
[Tensordyne](https://www.tensordyne.ai/) building AI inference infrastructure in Rust. CGP grew out
of work begun in July 2022 on the [Hermes IBC relayer](https://github.com/informalsystems/hermes) at
[Informal Systems](https://informal.systems/), where a monolithic `ChainHandle` trait with dozens of
methods pushed him toward blanket impls as a form of dependency injection; that line of work became
the [Hermes SDK](https://github.com/informalsystems/hermes-sdk/). Before that he built a dynamic
component system in JavaScript and an algebraic-effects library in Haskell using implicit parameters.

Two things follow for a writer. He is interested in both the theory and the practice of programming
languages and is comfortable saying so, so a piece may reach for row polymorphism, tagless final, or
the expression problem without apology when the audience warrants it. And he develops CGP largely in
his own time while earning a living elsewhere, which is why his writing is candid about capacity and
why it repeatedly asks the community to direct his effort rather than promising to cover everything.

## How he writes, as evidenced by the corpus

**He is long-form and unapologetic about it.** The Hypershell announcement runs to roughly 16,500
words and opens with an estimated reading time and a paragraph-per-section preview so the reader
knows what they are committing to. The instinct is not to compress the idea until it fits a format
but to give the reader an honest map of a long journey. Where a marketing document would say "keep it
short," the accurate advice for this author is: keep the *entry* short, then let depth be depth, and
tell the reader up front how much of it there is.

**He builds the reader's model before he uses it.** The RustLab talk spends roughly ten slides
explaining how Rust's trait system performs global lookup, why transitive dependency injection
requires globally unique instances, and why coherence is therefore *correct* — and only then shows
how to work around it. The same shape recurs in the [v0.8.0 post](../website/blog/v0-8-0-release.md),
which shows a wiring table growing unmanageable before namespaces appear, and in the
[area-calculation tutorial](../website/tutorials/area-calculation.md), where every construct arrives
as the fix for a problem the reader has just watched happen. **The problem always precedes the
construct**, and the existing thing is explained sympathetically before it is worked around.

**He concedes costs at length, not tactically.** The Hypershell post carries a Disadvantages section
covering the learning curve, the error messages, the inability to load programs dynamically, and slow
compile times — the last of which he explains as far as he understands it and then admits he has only
"rough experiments" to go on. The [Introduction page](https://contextgeneric.dev/docs/) tells readers
that CGP is in "formative, early stages" and that adopting it carries risk. The
[new-website post](../website/blog/new-website.md) discloses that the design and much of the prose
were produced with LLM assistance and states plainly that a professional designer would have done
better. This is not the calculated concession that marketing guidance recommends as a trust purchase;
it is a disposition. A piece that omits a known cost is off-voice even when omitting it would be
strategically defensible.

**He is precise about related work and actively guards against flattering comparisons.** On tagless
final he writes that CGP "differs enough that I want to avoid people thinking they're identical," and
then names the difference. He credits Servant, `unsynn`, Haskell typeclasses, and Kani accurately and
without diminishing them. A comparison in his voice explains the other thing properly first, and the
place CGP differs is stated as a difference rather than as a victory.

**He tells the story behind things.** The Hypershell post pauses to explain that he started a project
by that name in 2012, that the idea did not last, and that the name is a homage. The launch
announcement recounts the `ChainHandle` trait and the twenty-year history of his attempts at modular
programming. These passages do real persuasive work — they establish that CGP is a considered
position rather than a novelty — but they read as someone talking, not as origin-story marketing.

**He is warm and direct with readers, and asks them for direction.** He thanks readers for reaching
the end, invites them to say which problem domains they want covered, and states openly that he
cannot cover every domain himself. Enthusiasm is allowed — "I am thrilled to introduce" is his own
sentence — but it attaches to the act of sharing something, never to a claim about how good it is.

**He is explicit about strategy when he has one.** The clearest example is the positioning thesis in
the Hypershell post: his role is to *enable developers who value modularity to produce reusable
components for developers who do not*, so that everyone benefits from CGP regardless of whether they
care about it. He also states why he steers CGP away from web frameworks, and the reason is partly
personal career strategy. A writer should treat this thesis as available material rather than
inventing a positioning story.

## Stated preferences

The decisions below were given directly by the author and govern the rest of this section. They are
recorded as rules because they settle questions that recur in almost every piece.

**The voice is layered: a project voice on the site, a personal voice on the blog.** The homepage,
the docs pages, and the tutorials speak as the project — plain, second-person where it addresses the
reader, without first-person narration. The blog is where he writes as himself, in the first person,
with the candour and the backstory. The one existing exception is worth preserving: the
[Contribute page's](https://contextgeneric.dev/docs/contribute) sponsorship section is written in his
own voice and is frank about money, and its frankness is the point. Do not homogenize it.

**The tag line is settled, and the frame is *enhances, not replaces*.** CGP is
*"a language extension for Rust, with pluggable trait implementations at compile-time"*, and every
piece should reinforce that CGP builds on Rust's existing trait system rather than substituting for
it. This is why "superset of ordinary traits," "a library on stable Rust," and "you can still
implement the trait directly" are load-bearing rather than defensive: they are the frame, not a
hedge. See [identity.md](identity.md).

**The homepage exists to make the idea click, and to carry the selling points — not to repeat the
tutorials or the reference.** A reader should leave the homepage understanding what CGP does and why
it is worth their attention, having been routed to the material that teaches it rather than taught
there. See [../website/writing-guides/homepage.md](../website/writing-guides/homepage.md).

**Long explanation belongs on its own page.** His essays tend to outgrow whatever container they
start in, and his instruction is to plan for that rather than fight it: when a homepage section wants
to become an essay, the essay becomes a dedicated documentation page and the homepage links to it.
A writing guide should therefore name the pages an essay will be offloaded to, not merely warn
against sprawl.

**Frameworks supply ideas, not rules.** Diátaxis is cited approvingly in his own
[new-website post](../website/blog/new-website.md), and his instruction is to take the applicable
ideas from it without following it strictly. Its prohibition on explaining inside a tutorial, in
particular, is not binding on CGP, whose readers need to see through the macros before they will
trust them. Treat any external methodology the same way.

**Tutorials come in two registers, both first-class.** One teaches complex concepts from first
principles using deliberately simple examples — the
[area-calculation](../website/tutorials/area-calculation.md) family, which will grow to cover more
advanced constructs. The other is hands-on and applied — building a real thing, such as a web app,
without walking through every detail of how CGP works. Both teach the same concepts to readers who
learn differently, and neither is a lesser form of the other. See
[../website/writing-guides/tutorial.md](../website/writing-guides/tutorial.md).

**The site's current copy is a placeholder where it reads as machine-written.** Phrases such as "a
beautiful overhaul redesign," "gracefully superseded by more intuitive and modern patterns," and
"this pioneering stage" are not defended; they stand in until better wording exists, and a writer
should replace them whenever they can do better. This is a licence to improve, not a mandate to
sweep. See [voice-and-register.md](voice-and-register.md).

**How the project is built is disclosed, in the same register as any other cost.** The
[new-website post](../website/blog/new-website.md) volunteered that the site's design, text, and images
were largely LLM-produced and said plainly that a professional designer would have done better — nobody
asked, and no part of it reads as apology or as boast. That instinct is now a policy, because the
project's use of AI is not uniform: it runs from agent-written documentation to a hand-written core
library, and the distinctions are the informative part rather than a detail one sentence can carry.
The levels, the wording, and the site page that carries them are in
[ai-disclosure.md](ai-disclosure.md). The habit to preserve is the one already on display — state what
was done, state its limit, take responsibility for the result, and do not argue about whether it was
legitimate.

## What this means for an agent writing in his name

The single most useful instruction is to write as though the author will read the draft and ask "did
I say this, or did a machine say it for me?" Three habits carry most of the distance. **Let the
explanation be as long as the idea requires, and say up front how long it will be** — brevity is not
a virtue here, but ambushing a reader with length is a vice. **Explain the existing thing properly
before improving on it**, because his readers are Rust programmers who respect the language and will
not follow an argument that begins by disparaging it. And **state the cost in the same passage as the
benefit, in plain words, without softening it into a hedge** — "this is more machinery than a plain
trait needs" is his register; "while there is a modest learning curve, the benefits are substantial"
is not.

Two habits to avoid are just as specific. Do not write confident claims he has not made and cannot
check: no invented benchmarks, no adoption figures, no "developers love." And do not stack
intensifiers onto true statements, because inflation is the surest signal that no human wrote the
sentence — the honest smaller claim is both his preference and the more persuasive one with this
audience.

## Keeping this document current

This document is evidence-based, so it goes stale when the evidence moves. Revisit it when the author
publishes a substantial new piece whose register differs from what is recorded here, when he states a
preference that contradicts a rule above, or when a piece written from this document is rejected —
that rejection is data, and the correction belongs here rather than in a one-off fix to the piece.
Record a stated preference as a stated preference and an observed habit as an observed habit, keeping
the two apart, because the first is binding and the second is a pattern that a new piece may
legitimately depart from.
