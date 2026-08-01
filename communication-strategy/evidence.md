# Evidence: what the community reads, and how CGP has landed

This document grounds the section's claims about the audience in citable facts — where the Rust
community's attention actually sits, what CGP's own public reception has been, and what both imply for
the hooks and channels a piece should choose. It is the section's **single home for external
citations**: every other document links here for the evidence behind an audience claim, the way they
link to [related-work](../related-work/README.md) for the evidence behind a concept claim.

Its two halves are sourced differently, and the asymmetry is deliberate rather than sloppy. Claims
about **the Rust community in general** are linked to the published work they come from — a survey, an
article, a repository — because that is what keeps them checkable. Claims about **how CGP itself has
been received** are distilled instead: the finding is recorded, the thread it came from is not, and no
sentence is quoted in a way that identifies the reader who wrote it. That rule comes from
[this repository being public](../AGENTS.md#this-repository-is-public), and it costs less than it
appears to, because what a writer needs from a reaction is the pattern rather than the instance.

A caution on reading it. Public engagement metrics are noisy, and absence of discussion is not proof
of absence of interest. The findings are strong enough to steer framing decisions, but they are inputs
to judgment rather than verdicts, and the closing section treats publication itself as the real
measurement. Community attention also moves, which makes this document a sync target in its own right:
when the survey or the discourse shifts, the guidance resting on it must be revisited. **The planning
of publication — what ships when, to which channel, and what came of it — is managed outside this
repository**, so this document carries the distilled conclusions and never a campaign.

## What the Rust community worries about — and what it rewards

The clearest signal is the annual survey, and it names two costs to concede and one benefit to lean on.
The [2024 State of Rust survey](https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/)
reports that slow compile times remain the perennial top pain, that subpar debugging support is among
the leading tooling complaints, and that 45.2% of respondents named the language's growing *complexity*
as a worry for its future — while, asked to prioritize the project's work, developers ranked runtime
performance second only to fixing compiler bugs. Three moves follow.

**Concede compile-time cost and verbose diagnostics early and plainly.** They are the community's live
sore spots, and a reader is actively scanning a new abstraction for whether it worsens them. A piece
that stays silent on them reads as naive or evasive. On the diagnostics, the concession now travels
with a response — [`cargo-cgp`](../cgp/reference/cargo-cgp.md) reshapes the recognized error classes to
lead with the root cause — though it remains a young pre-release, so the concession is paired with the
fix rather than retired.

**Treat "this adds complexity" as the most dangerous perception a piece can leave.** Complexity is the
community's named fear for the language's future, so "still ordinary Rust", gradual adoption, and
problem-first restraint are not merely pleasant framings — they are the direct answer to the audience's
stated anxiety, and the empirical reason the
[enhances-not-replaces frame](identity.md) is the project's core positioning rather than a hedge.

**Lean hard on zero runtime cost.** The survey shows the community explicitly prizes runtime
performance, so "resolved at compile time and compiled to a direct call" lands as an answer to
something they already care about rather than as an abstract virtue.

## The conversations that draw attention

Some topics reliably draw the community's attention, and a piece that attaches CGP to a live
conversation borrows its energy — provided the attachment is honest.

- **The orphan rule and overlapping implementations.** A durable, recurring frustration, with a
  repository dedicated to cataloguing its design problems
  ([Ixrec/rust-orphan-rules](https://github.com/Ixrec/rust-orphan-rules)) and a steady stream of posts
  on the newtype workaround. This is CGP's strongest attachment point because the pain is concrete and
  widely felt, and it is the reason the front-page and launch-post hooks lead here rather than on the
  mock-in-tests story.
- **Async and function coloring.** The
  [function-coloring debate](https://www.thecodedmessage.com/posts/async-colors/) recurs whenever async
  Rust is discussed, and async `fn` in traits carries its own well-known friction around
  [`Send` bounds and `dyn`](https://github.com/rust-lang/rust/issues/103854). CGP's handler family and
  its [`Send`-recovery pattern](../cgp/concepts/send-bounds.md) touch this, but the honest attachment
  is narrow — CGP does not remove function coloring, and a piece must not imply it does.
- **Error handling.** The `anyhow`-versus-`thiserror` question is among the most-written-about topics in
  Rust, and CGP's abstract error type speaks to it directly. A strong, low-controversy hook for the
  working developer.
- **Reflection and compile-time introspection.** A live, high-attention, officially-pursued area:
  `facet` drew wide interest, `bevy_reflect` is established, and the Rust project has a
  [reflection-and-comptime goal](https://rust-lang.github.io/rust-project-goals/2026/reflection-and-comptime.html)
  with a landed MVP. CGP's compile-time structural reflection sits squarely in this conversation, which
  makes it timely — but because first-class reflection is coming to the language, position CGP as
  *available today* and *type-level and checked*, complementary to the built-in facility rather than a
  competitor the language will absorb.
- **Dictionary-passing style, incoherence, and context and capabilities.** The closest match to CGP's
  own thesis that the language-design conversation has produced, and the newest. Nadrieril's posts on
  [elaborating Rust traits to dictionary-passing style](https://nadrieril.github.io/blog/2026/03/20/dictionary-passing-style.html)
  and [what if traits carried values](https://nadrieril.github.io/blog/2026/03/22/what-if-traits-carried-values.html),
  Boxy's [An Incoherent Rust](https://www.boxyuwu.blog/posts/an-incoherent-rust/), and Tyler Mandry's
  earlier [context and capabilities](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/)
  together sketch a Rust in which incoherent implementations are legal and a context carries the
  capabilities a function needs. CGP is a working implementation of a subset of exactly that, on stable
  Rust, today. This is the one conversation where CGP is not analogous to the subject but an instance of
  it, and it reaches the **language-design reader** profile in
  [readers.md](readers.md#the-language-design-and-compiler-team-reader), who is otherwise unreachable
  through the general channels. The attachment is honest only if it is modest: CGP covers a fragment,
  it does nothing for the formalization goal these efforts are actually pursuing, and it cannot migrate
  the existing trait ecosystem. Lead with what it *does* supply — a desugaring path that exists — and
  concede the rest in the same breath.
- **AI-assisted development.** Not a conversation to attach a hook to, and worth naming here anyway,
  because it changes the arithmetic behind CGP's most-cited costs rather than adding a capability. The
  wiring volume, the vocabulary, and the diagnostics are the three things readers say deter them, and
  all three are mechanical work that an agent with the [`/cgp` skill](https://github.com/contextgeneric/cgp-skills)
  absorbs — which is a checkable claim, since the skill is published and a reader can attach it and see.
  Where this belongs is beside the costs, per
  [message.md](message.md#the-objections-readers-bring), never as a lead: a project that opens on AI in
  2026 is heard as chasing attention, and this audience punishes that faster than any other.

## The pains are real — and developers already hand-roll the fix

The most persuasive evidence for a capability is that developers reinvent CGP's mechanism on their own,
and for the central one they demonstrably do. The pattern CGP is built on — zero-sized marker types
plus a helper trait, so several otherwise-overlapping blanket implementations can coexist — has been
[independently discovered and blogged](https://www.greyblake.com/blog/alternative-blanket-implementations-for-single-rust-trait/)
by a Rust author who reached it to work around the exact "no two blanket impls may overlap" limitation
CGP exists to lift, describing the hand-rolled version as "3 extra lines to link things together".

This is the single most useful fact in this document. The strongest capability to advertise is not one
the reader must be talked into wanting, but one they have already built by hand and would rather not
maintain. Point to the reinvention as evidence and the "isn't this over-engineered" reflex softens,
because the reader recognizes their own workaround.

The neighbouring pains are evidenced too. The dependency-injection crates Rust does have stay niche,
and the structural reason is worth stating without singling any of them out: a runtime container
resolves an object graph, so it reaches for `Arc<dyn Trait>` and binds one implementation per
interface. Both are the right design for what a container is doing, and both are exactly the costs
per-context wiring does not pay — so the honest pitch to that reader is "many implementations per
context, no `dyn`", made as a description of a different trade rather than as a complaint about
theirs. And even hand-rolled trait-based DI leaks: as a
[widely-cited post](https://jmmv.dev/2022/04/rust-traits-and-dependency-injection.html) documents, any
type named in a public trait's method signature must itself be public, so trait-based injection quietly
breaks encapsulation — the concrete cost CGP's impl-side dependencies avoid.

## CGP's own reception, and the lessons in it

CGP's ideas do get discussed, the reception is niche and runs mixed-to-skeptical, and the five patterns
below are what the skepticism reliably clusters on. They are recorded as findings rather than as
citations, per the sourcing rule at the top of this document — the pattern is what a writer can act on,
and the thread it came from is not this repository's to reproduce.

Reading the reception correctly starts with knowing which venue to trust. The substantive discussion
happens on Lobsters and the Rust subreddit rather than on Hacker News, where a submission is
hit-or-miss and draws almost no engagement unless it reaches the front page — so a low score there
reflects a title and a posting hour far more than the idea's reception, and must not be reasoned from.
Vote counts on the venues that do discuss CGP are small, and the comment threads are nonetheless
substantive enough to read patterns out of.

Five patterns recur, and each maps to guidance elsewhere.

- **Verbosity, and "what problem justifies this."** The most common reaction by a distance is that CGP
  reads as heavy boilerplate, and it comes from experienced Rust programmers as readily as from
  newcomers — including readers who report being unable to follow the sample code and asking what
  concrete problem warrants the machinery. This is the over-engineering reflex firing in the wild, and
  it confirms the prescription: lead with a concrete pain and a before/after, never with the paradigm.
- **Traceability of control flow.** A distinct and repeated objection is that the indirection makes a
  codebase hard to navigate, because a reader cannot tell which code a method call will actually enter.
  This is not the generic macros-are-magic complaint but a specific worry about following execution,
  and the answer is that the wiring table is the one explicit, greppable place naming the provider for
  each component.
- **"Isn't this just X reinvented."** Knowledgeable readers reach for prior art — aspect-oriented
  programming, COM, the ML module system — as a skeptical frame. These deserve the honest engagement the
  [related-work](../related-work/README.md) documents supply, not deflection, because the reader making
  the comparison is exactly the one who can be won or lost on it.
- **The name does not communicate.** Readers say plainly that "context-generic programming" obscures
  more than it conveys and that coining a phrase makes the idea harder rather than easier to grasp, and
  they reach instead for "structural typing" or "duck typing for statically-typed code" to name what
  they think is being described. This is field validation of the rule that a name is not a pitch, and it
  surfaces bridge terms worth using in body copy — with the caveat that CGP is nominal-and-wired rather
  than truly structural.
- **Do not overstate the ergonomics.** When CGP claims a reader need not understand its internals, the
  standing answer is that the first compilation error will force them to understand the desugaring
  anyway — and that is correct. This is the complaint CGP has answered most directly since:
  [`cargo-cgp`](../cgp/reference/cargo-cgp.md) exists specifically to un-hide and lead with the root
  cause, so a piece meeting this objection can point to a deliberate response rather than only conceding
  the cost. The tool is new — v0.1.0-alpha — and has no reception of its own; do not manufacture any,
  and present it as the deliberate answer to a recorded complaint rather than as something the community
  already praises.

That last pattern also explains why showing the desugaring is treated as a
[teaching requirement](readers.md#the-comprehension-barriers) rather than an optional appendix: the
objection is right that a reader will eventually meet the generated code, so a tutorial that shows it
early is being accurate rather than indulgent.

Two facts about the sample are worth holding before concluding anything from one reaction. Every
substantial post since the launch has been submitted to the same three venues, several also opening a
GitHub discussion, so the reception evidence spans the whole [blog catalog](../website/blog/README.md)
rather than one or two threads. And it is worth noticing *what* drew submission effort: the deep dives
and the DSL announcement were judged worth the same push as the releases, which says the project
already treats long-form as distribution rather than as documentation.

**The conference channel has now been used, and it worked.** CGP was presented at RustLab 2025 in
Florence, and the talk exists as a [recording](https://www.youtube.com/watch?v=gXIfP-W9074), a slide
deck, and a [full transcript published as a blog post](../website/blog/rustlab-2025-coherence.md).
Three things follow. The talk playbook in [formats.md](formats.md) is no longer hypothetical — a
delivered talk exists that follows it closely — so a future talk should be built from that one rather
than from first principles. **Publishing the transcript is itself a reusable move**: it converts an
ephemeral, unindexable artifact into something linkable, quotable, and readable by people who will
never watch a video, and it costs almost nothing once the talk is written. And a conference gives a
project something the link aggregators do not, which is a room that has already decided to listen for
forty minutes — the one format where the evaluator can be reached at depth.

Two further lessons come from outside that discussion and still hold. "Dependency injection" is not a
safe general hook, because idiomatic Rust already does lightweight DI with traits and generics and a
large part of the audience treats DI *frameworks* as an unwanted import. And social proof is worth
building: comparable success stories in adjacent ecosystems turned on a flagship adopter, so CGP's most
convincing answer to the evaluator's "is anyone really using this" is a real, non-trivial system built
with it and shown as a worked example, not more argument. The
[Hermes SDK](https://github.com/informalsystems/hermes-sdk/) is that system, and it is currently
undersold — it appears in a bare list at the bottom of the site's Resources page.

## Where the profiles gather

Attention is channel-specific, so the hook should be chosen for where a piece will appear, matching the
[reader profiles](readers.md) to the room. The pragmatic majority and the first-contact skimmer dominate
the general channels, and for CGP the discussion has actually landed on Lobsters and the Rust
subreddit, with the weekly *This Week in Rust* as steady distribution; Hacker News is worth submitting
to but hit-or-miss, and should never be a plan's linchpin. In those channels a front-page tag line and a
concrete before/after must do the work, and the verbosity, traceability, and "just macros" framings must
be preempted in the opening lines. The type-system and functional-programming audience gathers in more
specialized corners, where the audience-tuned one-liners in [message.md](message.md) land without
translation. The evaluator reads long-form: a design document, a detailed write-up, a comparison table,
where candour about maturity and cost is what persuades. Pick the channel, then the reader, then the
hook — in that order.

The **language-design reader** is the exception to all of this, and the exception is worth stating
because the general channels cannot reach them. Compiler-team members and the people writing Rust's
design posts do not evaluate a crate from an aggregator submission; they are reached by a piece that
engages a live design question on its own terms, at their level of precision, and concedes the parts
CGP does not solve. That is a rare and perishable opportunity rather than a standing channel — it
exists only while a matching conversation is live — which is why the attachment points above are worth
watching and why a piece written for one is worth writing while the conversation still is.

## Reading the reaction

Because attention is empirical, the real grade of any hook is the reaction it draws, so treat
publication as a measurement rather than a conclusion. A hook is working when it draws questions about
*how* CGP achieves something; it is failing when the top replies are the dismissals this audience
actually reaches for — "verbose / over-engineered", "I can't tell what code runs", "isn't this just AOP
/ COM / ML modules reinvented", "the name tells me nothing", alongside the imported "just macros" and
"another DI framework". Those replies are signal rather than noise: they mean the framing let the reflex
fire before the novel part landed, and the fix is upstream, in the opening lines. Float a candidate hook
where the target reader gathers, watch which dismissal it attracts, and revise toward the framing that
draws the *how* question instead.

What comes back from that is revised into the patterns above rather than logged. **Publication planning
and its results are managed outside this repository**, so this document holds the standing conclusion —
which framings misfire, and what to do instead — and never a record of a campaign or of who said what.
When a reaction changes the conclusion, change the pattern; when it merely confirms one, nothing needs
writing down.

One further consequence of publication being a measurement is that measurements interfere with each
other. Several pieces released at once compete for the same readers on the same day, in channels whose
ranking is time-weighted, so a second post published beside a first mostly takes attention from it —
which both wastes the smaller piece and makes each result unreadable as evidence. Space substantial
publications out, and treat that spacing as part of the plan rather than as a delay in it.
