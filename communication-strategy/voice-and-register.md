# Voice and register

This document fixes *how CGP sounds* — which voice each surface speaks in, and what the prose does at
the sentence level — so that the site, the blog, and the READMEs read as one project written by
people rather than as assembled copy. It is the craft companion to
[author-personality.md](author-personality.md): that document records who the author is, and this one
turns it into rules a writer can apply to a paragraph.

## The layered voice

CGP speaks in two voices, and which one a piece uses is decided by its surface rather than by its
subject. **The website speaks as the project; the blog speaks as the author.** This is a deliberate
split rather than an accident of who wrote what, and getting it wrong is the most visible way a draft
can be off-voice.

**The project voice** is what the homepage, the docs pages, the tutorials, and the READMEs use. It
addresses the reader as "you", refers to the project as "CGP", and uses "we" only in the teaching
sense a tutorial needs — "we start by defining the component" — never as a corporate collective
speaking about its own achievements. It carries no first-person narration, no personal history, and
no opinion attributed to a person. It is plain and unhurried, and it makes claims that anyone
maintaining the project could stand behind, because those pages outlive any single author's framing.

**The author voice** is what the blog uses, and it is first-person, personal, and candid. It says "I
think", "I want to be transparent about", "I have a feeling that"; it recounts how something came
about; it names uncertainties the project voice would have to state impersonally. This is where CGP's
strongest trust-building material lives, and it should not be flattened into the project voice for
consistency's sake — the inconsistency between a blog post and a docs page is a feature, because a
reader can tell which one is a person talking.

One page deliberately breaks the split and must keep breaking it. The
[Contribute page's](https://contextgeneric.dev/docs/contribute) sponsorship section is written in the
author's own voice and is frank about the project's finances, and that frankness is doing work no
neutral phrasing could do. When a docs page genuinely needs a person to say something — an admission
about capacity, a request for help, a statement about the project's direction — the right move is to
switch voice visibly for that passage rather than to launder it into project-speak.

Two mechanical rules keep the split clean. **Never write "we" where you mean the author**, because a
plural that stands for one person reads as an institution pretending to be a team; write "CGP" for
the project or switch to the author voice properly. And **never carry an opinion into the project
voice without grounding it** — "CGP is the best way to model this" belongs to a person, while "CGP
suits this case, and a plain trait suits that one" belongs to the project.

## The register: plain, unhurried, and specific

The register is the same in both voices, and the shortest description of it is *a knowledgeable
colleague explaining something carefully, with no sales pressure and nothing to prove*. It is not
terse — CGP's ideas do not compress well and the author does not try to compress them — but every
sentence is doing work. The three properties below are what make a draft sound right.

**Plain words, said once.** Prefer the common word to the impressive one and let a true claim stand
without an intensifier. "Redesigned the site" beats "a beautiful overhaul redesign"; "promising"
beats "genuinely promising"; "replaced by newer patterns" beats "gracefully superseded by more
intuitive and modern patterns". The test that catches nearly everything: if deleting an adjective or
adverb leaves the sentence's meaning intact, delete it. Inflation is the single clearest signal that
a sentence was machine-written, and this audience reads it as either padding or spin.

**Length where the idea needs it.** Brevity is not a virtue here. A long explanation is welcome when
the idea is genuinely long, and the author's own posts run to many thousands of words. What is *not*
welcome is ambushing the reader: a long piece states its length or its shape at the top, the way the
Hypershell post gives an estimated reading time and a section-by-section preview. Say how far this
goes, then go that far.

**Concrete over abstract, always.** A named construct beats "the machinery"; a compiler error quoted
verbatim beats "the errors can be confusing"; a wiring line the reader can grep for beats "explicit".
When a passage starts reaching for abstractions — flexibility, power, modularity, elegance — it has
usually lost hold of the specific thing it was describing, and the fix is to name that thing again.

## The moves that make CGP prose work

Four structural habits recur throughout the author's best writing, and a piece that uses them will
sound like CGP even if its sentences are ordinary.

**Explain the existing thing properly before improving on it.** The reader is a Rust programmer who
respects Rust, and an argument that opens by disparaging the trait system loses them in the first
paragraph. The RustLab talk is the model: it explains that Rust's trait system doubles as a
dependency-injection mechanism, that transitive resolution therefore requires globally unique
instances, and that [coherence](../cgp/concepts/coherence.md) is *correct* — and only then works
around it. Every CGP limitation story should be told this way, because CGP's whole frame is that it
[enhances rather than replaces](identity.md) what Rust already does.

**Put the problem before the construct.** Show code that is unsatisfactory for a stated reason, then
introduce the construct as the fix. This is the ordering the
[area-calculation tutorial](../website/tutorials/area-calculation.md) is built on and the one the
[v0.8.0 post](../website/blog/v0-8-0-release.md) uses for namespaces, and it is what stops a
construct reading as ceremony. A reader who has felt the problem will forgive a lot of machinery; a
reader who has not will forgive none.

**Show the explicit form before the sugar.** CGP's macros generate code, and Rust programmers do not
trust generated code they have not seen through. The habit that answers this is to write the thing by
hand first — call a provider by name before any wiring exists, implement the consumer trait manually
before `delegate_components!` replaces it, show the plain-Rust blanket impl that `#[cgp_fn]`
produces — so the sugar arrives as an abbreviation for something the reader has already read. This is
also why the desugaring appendix in the
[Hello World tutorial](../website/tutorials/hello-world.md) is load-bearing rather than optional
colour.

**Concede in the same passage as the claim, in plain words.** Not as a hedge appended to a pitch, but
as part of describing the thing accurately. "This is more machinery than a plain trait needs, and for
a capability with one implementation a plain trait is the right tool" is the register. "While there
is a modest learning curve, the benefits are substantial" is not — it concedes nothing and signals
that something is being sold.

## Words and habits to avoid

A short list of sentence-level failures accounts for most off-voice drafts, and each has a
replacement that is both truer and more persuasive with this audience.

- **Adjective and adverb inflation** — "genuinely", "truly", "simply", "seamlessly", "powerful",
  "beautiful", "comprehensive". Delete the intensifier and keep the claim.
- **Enthusiasm attached to a capability** — "blazingly fast", "incredibly flexible". The author's
  enthusiasm attaches to sharing something, not to how good it is; keep the claim measurable.
- **The tricolon of nothing** — "clean, modern, and maintainable". Three vague adjectives are weaker
  than one specific noun.
- **Hedge stacking** — "may potentially help to improve". Say what it does, or say you do not know.
- **Corporate "we"** for one person, and **"our users"** for an audience that is mostly still reading
  rather than using.
- **Claims nobody made** — invented benchmarks, adoption numbers, quotations, or "developers love".
  If a number would strengthen a point, source it or drop the point.
- **Disparaging another tool** to elevate CGP. Represent every alternative as its own users would
  recognize it; the author does this consistently and it is one of his most credible habits.

The words to avoid *about CGP specifically* — "magic", "automatically resolves", "no boilerplate",
"replaces traits", and the rest — are a separate list, kept with their replacements in
[vocabulary.md](vocabulary.md), because they concern accuracy rather than register.

## Improving copy that is already published

Much of the current site copy is placeholder in the exact sense the author uses: written or polished
by an LLM, not defended, and open to replacement whenever a writer can do better. That is a licence
to improve prose you are already editing, not a mandate to sweep the site — the same lazy-reflow
discipline the base applies to line wrapping applies here.

Two constraints bound the licence, and both come from
[the website rules](../website/AGENTS.md). A **published blog post is a dated artifact** and is not
rewritten into agreement with either current CGP or current voice; leave it as it stands and record
any drift in its internal document. A **docs page describes the present** and can be corrected in
place freely, with no changelog note. And whichever you are touching, the passages written in the
author's own voice — the sponsorship section, the frank maturity warning on the Introduction — are
not placeholder and are not to be smoothed out.

## Checking a draft

Run four checks before publishing anything, in this order, because the first two catch the failures
that matter most.

Read the draft asking **whether a person wrote it**. If a paragraph could have been generated from
the topic alone, it probably was, and the fix is to say the specific thing the paragraph was
gesturing at. Then read it asking **whether the cost is stated** — find the honest limitation, and if
there isn't one in the piece, either the piece is overselling or the limitation is somewhere the
reader will find it before you tell them.

Then check the mechanics. **Delete every intensifier** that can go without changing the meaning. And
**check the voice matches the surface**: first-person on the blog, project voice on the site, and no
accidental corporate "we" in either.
