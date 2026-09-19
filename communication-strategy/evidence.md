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
to judgment rather than verdicts, and the section on reading the reaction treats publication itself as the real
measurement. Community attention also moves, which makes this document a sync target in its own right:
when the survey or the discourse shifts, the guidance resting on it must be revisited. **The planning
of publication — what ships when, to which channel, and what came of it — is managed outside this
repository**, so this document carries the distilled conclusions and never a campaign.

## What the Rust community worries about — and what it rewards

The clearest signal is the annual survey, and it names two costs to concede and one benefit to lean on.
The [2025 State of Rust survey](https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results),
published in March 2026 from 7,156 responses, reports that slow compilation is still the leading
productivity problem, named as a big problem by 27.9% of respondents, and that 41.6% worry the
language may become too complex, down from 45.2% the year before. Debugging is still a top complaint,
named as a big problem by 19.9%, though it slipped from second to fourth place among the problems. The
[2024 survey](https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/) also asked
developers to prioritize the project's work, and they ranked runtime performance second only to fixing
compiler bugs. Three moves follow.

**Concede compile-time cost and verbose diagnostics early and plainly.** They are the community's live
sore spots, and a reader is actively scanning a new abstraction for whether it worsens them. A piece
that stays silent on them reads as naive or evasive. On the diagnostics, the concession now travels
with a response — [`cargo-cgp`](../cgp/reference/cargo-cgp.md) reshapes the recognized error classes to
lead with the root cause — though it remains a young pre-release, so the concession is paired with the
fix rather than retired.

**Treat "this adds complexity" as the most dangerous perception a piece can leave.** Complexity is one
of the community's two most-named fears for the language's future, so "still ordinary Rust", gradual
adoption, and problem-first restraint are not merely pleasant framings — they are the direct answer to
the audience's stated anxiety, and the empirical reason the
[enhances-not-replaces frame](identity.md) is the project's core positioning rather than a hedge.

**Lean hard on zero runtime cost.** The 2024 survey shows the community explicitly prizes runtime
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
  because it changes the arithmetic behind CGP's most-cited costs rather than adding a feature. The
  wiring volume, the vocabulary, and the diagnostics are the three things readers say deter them, and
  all three are mechanical work that an agent with the [`/cgp` skill](https://github.com/contextgeneric/cgp-skills)
  absorbs — which is a checkable claim, since the skill is published and a reader can attach it and see.
  Where this belongs is beside the costs, per
  [message.md](message.md#the-objections-readers-bring), never as a lead: a project that opens on AI in
  2026 is heard as chasing attention, and this audience punishes that faster than any other. The 2025
  survey adds one observation that bears on the mitigation without moving where it belongs: attendance
  at online and offline communities shifted by roughly three points, and the survey reads its open
  answers as a hint that questions are moving to LLM tooling. If so, a growing share of readers can
  check the claim for themselves.

## The pains are real — and developers already hand-roll the fix

The most persuasive evidence for a strength is that developers reinvent CGP's mechanism on their own,
and for the central one they demonstrably do. The pattern CGP is built on — zero-sized marker types
plus a helper trait, so several otherwise-overlapping blanket implementations can coexist — has been
[independently discovered and blogged](https://www.greyblake.com/blog/alternative-blanket-implementations-for-single-rust-trait/)
by a Rust author who reached it to work around the exact "no two blanket impls may overlap" limitation
CGP exists to lift, describing the hand-rolled version as "3 extra lines to link things together".

This is the single most useful fact in this document. The strongest thing to advertise is not one
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
[Hermes SDK](https://github.com/informalsystems/hermes-sdk/) is that system. How prominently the site
presents it is tracked in the website section's [redesign queue](../website/redesign-queue.md).

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

## What we watch, and what counts as a result

Publication is a measurement only if something is measured, so this section names one signal for each
stage of the [conversion ladder](formats.md#the-conversion-ladder) and says how each is read. It
defines the signals; the planning and the log of what shipped stay outside this repository, per the
rule at the top. Developer-relations practice frames the stages as a funnel from awareness through
activation and adoption to advocacy, and the sources are in
[the craft sources below](#sources-for-the-craft-this-section-borrows).

**Awareness: the question a hook draws.** A hook is working when the replies ask *how* CGP does
something and failing when the top replies are the dismissals listed in
[Reading the reaction](#reading-the-reaction). Read the first ten replies to a submission, sort them
into how-questions and dismissals, and treat the ratio as the result. It needs no tooling, and it is
the one measurement the project has taken so far.

**Activation: time to a running program.** The standard first-contact measure for a developer tool is
the time from landing on the documentation to a first working result. For CGP that is the Quickstart,
and the target it should hold is **a reader with Rust installed reaches a running program in under
ten minutes, following only the page**. The measure is a
[friction log](readers.md#keeping-the-model-observed) taken on a clean machine, not an analytics event,
and the orientation-page writing guide, task O1 in [the website plan](../website/tasks.md), owns the
target once it exists. Hello World and the first tutorial part carry the same measure with a longer
budget.

**Adoption: what readers ask once they are writing code.** Questions in GitHub Discussions, the
Discord server, and the subreddit say which construct or page fails a reader who got past first
contact. Record them as patterns, per the distil rule, and read each recurring question as a defect in
the page that should have answered it. A question that recurs after the page is fixed is a defect in
the construct.

**Advocacy: writing and components from other people.** The top rung of the ladder is a reader who
publishes a CGP component or writes about CGP unprompted, as the Contribute page asks them to.
Count these when they happen and record the pattern in what they chose to write about. They are the
only signal here that measures conviction rather than attention.

**Search: not measured, and said so.** Which pages readers land on from search would say which titles
work and which pains readers search for in their own words. The site is a stock Docusaurus
installation with no analytics, and adding any is a plugin decision that runs against the
[site's stated policy](../website/site-structure.md), so this signal is unavailable rather than
merely uncollected. Do not infer it from anything else. If the policy changes, this is the first
measurement to add, and a privacy-respecting aggregate is the only acceptable form.

Two rules keep the signals honest. **A signal is read against a baseline**, so the first reading of
each is recorded as the baseline before any change is credited to a piece. And **a signal changes a
conclusion above or it is not worth taking**: a measurement that only confirms a pattern needs no
record, per [Reading the reaction](#reading-the-reaction).

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

## Sources, and when each was last checked

Every external source this document cites is listed here with the claim it supports and the date it
was last checked. "Read" means the page was re-read and the claim confirmed against it on that date.
"Link resolved" means only that the page still exists; the claim itself was not re-read. Re-check a
row before quoting its claim in public, and update the date when you do.

| Source | Supports | Last checked |
|---|---|---|
| [2025 State of Rust survey](https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results) | the compile-time, complexity, debugging, and LLM-tooling findings | 2026-09-19, read |
| [2024 State of Rust survey](https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/) | the runtime-performance priority and the 45.2% complexity figure | 2026-09-19, link resolved |
| [Ixrec/rust-orphan-rules](https://github.com/Ixrec/rust-orphan-rules) | the orphan rule as a durable frustration | 2026-09-19, link resolved |
| [Function-coloring debate](https://www.thecodedmessage.com/posts/async-colors/) | the async attachment point | 2026-09-19, link resolved |
| [`Send` bounds and `dyn` issue](https://github.com/rust-lang/rust/issues/103854) | the async-trait friction | 2026-09-19, link resolved |
| [Reflection and comptime project goal](https://rust-lang.github.io/rust-project-goals/2026/reflection-and-comptime.html) | reflection as an officially pursued area | 2026-09-19, link resolved |
| [Dictionary-passing style](https://nadrieril.github.io/blog/2026/03/20/dictionary-passing-style.html) | the language-design conversation | 2026-09-19, link resolved |
| [What if traits carried values](https://nadrieril.github.io/blog/2026/03/22/what-if-traits-carried-values.html) | the language-design conversation | 2026-09-19, link resolved |
| [An Incoherent Rust](https://www.boxyuwu.blog/posts/an-incoherent-rust/) | the language-design conversation | 2026-09-19, link resolved |
| [Context and capabilities](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/) | the language-design conversation | 2026-09-19, link resolved |
| [cgp-skills](https://github.com/contextgeneric/cgp-skills) | the agent skill exists and is published | 2026-09-19, link resolved |
| [Alternative blanket implementations](https://www.greyblake.com/blog/alternative-blanket-implementations-for-single-rust-trait/) | developers hand-roll CGP's marker-struct pattern | 2026-09-19, link resolved |
| [Rust traits and dependency injection](https://jmmv.dev/2022/04/rust-traits-and-dependency-injection.html) | trait-based injection leaks internal types into a public API | 2026-09-19, link resolved |
| [RustLab 2025 recording](https://www.youtube.com/watch?v=gXIfP-W9074) | the talk exists and is public | 2026-09-19, link resolved |
| [Hermes SDK](https://github.com/informalsystems/hermes-sdk/) | the flagship real system built with CGP | 2026-09-19, link resolved |

### Sources for the craft this section borrows

The strategy documents borrow method from published work on technical communication and developer
relations, and those sources are concentrated here so the other documents stay in one voice. A
document that leans on one links to this list rather than citing it inline. "Summary read" means a
published summary of the source was read on that date rather than the source itself.

| Source | Used for | Last checked |
|---|---|---|
| April Dunford, *Obviously Awesome*, summarized in [Lenny's Newsletter](https://www.lennysnewsletter.com/p/summary-april-dunford-on-product) | the five-step order of positioning in [identity.md](identity.md#the-positioning-in-the-order-it-was-decided) | 2026-09-19, summary read |
| Phil Leggetter, [the AAARRRP framework](https://www.leggetter.co.uk/aaarrrp/) | the funnel stages behind [What we watch](#what-we-watch-and-what-counts-as-a-result) | 2026-09-19, summary read |
| [Time to hello world](https://instruqt.com/glossary/time-to-hello-world) | the activation measure | 2026-09-19, summary read |
| Nielsen Norman Group, [How Users Read on the Web](https://www.nngroup.com/articles/how-users-read-on-the-web/) and [Scrolling and Attention](https://www.nngroup.com/articles/scrolling-and-attention/) | the scanning and above-the-fold figures in the homepage guide | 2026-09-19, summary read |
| Mark Baker, [Every Page is Page One](https://everypageispageone.com/the-book/) | the titles-and-search rules in [formats.md](formats.md#titles-first-lines-and-search) | 2026-09-19, summary read |
| Richard Mayer's multimedia principles, summarized by [Devlin Peck](https://www.devlinpeck.com/content/mayers-principles-of-multimedia-learning) | the diagram rules in [voice-and-register.md](voice-and-register.md#show-it-canonical-examples-diagrams-and-diffs) | 2026-09-19, summary read |
| Google, [code samples](https://developers.google.com/style/code-samples) and the [samples style guide](https://googlecloudplatform.github.io/samples-style-guide/) | the code-sample rules in voice-and-register.md | 2026-09-19, summary read |
| *Docs for Developers* (Bhatti and others, 2021), described by the [publisher](https://www.ebooks.com/en-us/book/210383942/docs-for-developers/jared-bhatti/) | the friction-log practice in [readers.md](readers.md#keeping-the-model-observed) | 2026-09-19, summary read |
