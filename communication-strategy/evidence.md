# Evidence: what the community reads, and how CGP has landed

Use published findings and summarized CGP reception to choose useful openings, explain costs, and
evaluate public writing.

This document holds the section's external sources for audience claims and communication methods.
[Related-work](../related-work/README.md) holds the sources for comparisons with other technologies.
Link general audience claims to published evidence. Summarize reactions to CGP without linking
threads or quoting identifiable readers, following the
[public-repository rule](../AGENTS.md#this-repository-is-public).

Treat engagement as an imperfect signal. Small samples and limited visibility cannot establish what
the whole community thinks, and silence does not prove a lack of interest. Distinguish measured
findings, observed patterns, and strategic judgments. Revisit guidance when its evidence changes.
Publication schedules and campaign results are managed outside this repository.

## What the Rust community worries about — and what it rewards

Rust surveys support addressing compilation cost, debugging, and complexity directly. The
[2025 survey](https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/), published in
March 2026, collected 7,156 completed responses. Its productivity chart reports slow compilation as
a big problem for 27.29% and debugging for 19.90% of respondents to that question. Concern about
complexity was 41.6%, compared with 45.2% in 2024. These findings describe survey respondents, not
all Rust developers.

The [2024 survey](https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/) also
reports performance as employers' second most common reason for investing in Rust, after building
correct software. This supports discussing runtime cost, without establishing how any particular
CGP message will perform.

State compilation and diagnostic costs beside the benefits of abstraction. Pair the diagnostic
concession with [`cargo-cgp`](../cgp/reference/cargo-cgp.md), using the canonical wording:
`cargo cgp check` leads with the root cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every class.

Show why the added abstraction is useful before introducing it. The concern about complexity
supports the [enhances-not-replaces framing](identity.md): explain CGP through ordinary Rust,
gradual adoption, and a concrete problem. This is a strategic inference from the survey, not a
measured preference for that wording.

Explain runtime cost precisely. CGP resolves wiring at compile time and uses static dispatch;
that mechanism supports a specific claim about dispatch overhead. Avoid implying that every
program using CGP is faster.

## The conversations that draw attention

Connect CGP to a relevant technical discussion only where the connection can be explained
accurately. These topics provide candidate openings, not a ranking backed by comparable engagement
measurements:

- **Orphan rules and overlapping implementations:** The
  [rust-orphan-rules repository](https://github.com/Ixrec/rust-orphan-rules) documents design
  problems and trade-offs. This is the preferred general opening because it lets a before-and-after
  show a concrete limitation and CGP's provider-based solution.
- **Async and function coloring:** The
  [function-coloring discussion](https://www.thecodedmessage.com/posts/async-colors/) and
  [async-trait issue](https://github.com/rust-lang/rust/issues/103854) offer context for
  [CGP's `Send` recovery](../cgp/concepts/send-bounds.md). Keep the connection narrow: CGP does
  not remove function coloring.
- **Error handling:** The choice between concrete error types and libraries such as `anyhow` and
  `thiserror` offers a practical opening for CGP's abstract error type. Use the
  [modular-error-handling explanation](../cgp/concepts/modular-error-handling.md) to state the
  benefit without claiming a measured level of audience interest.
- **Reflection and compile-time introspection:** The Rust project's
  [reflection and comptime goal](https://goals.rust-lang.org/2026/reflection-and-comptime.html)
  records a landed MVP and further experimental work, including validation with reflection
  libraries such as `facet` and `bevy_reflect`. Present CGP's type-level structural reflection as
  available on stable Rust and potentially complementary. Do not imply a settled future language
  design or stabilization date.
- **Dictionary passing and context-carried implementations:** Nadrieril's
  [dictionary-passing](https://nadrieril.github.io/blog/2026/03/20/dictionary-passing-style.html)
  and [traits carrying values](https://nadrieril.github.io/blog/2026/03/22/what-if-traits-carried-values.html)
  posts, Boxy's [An Incoherent Rust](https://www.boxyuwu.blog/posts/an-incoherent-rust/), and Tyler
  Mandry's [context and capabilities](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/)
  proposal provide a relevant comparison for the
  [language-design reader](readers.md#the-language-design-and-compiler-team-reader). Present CGP
  as a working desugaring of part of this design space. It neither supplies the formalization
  those efforts seek nor migrates the existing trait ecosystem. The comparison itself, including
  specialization and Cairo, is worked out in
  [related-work/rust-language-proposals.md](../related-work/rust-language-proposals.md).
- **AI-assisted development:** Discuss CGP's published
  [agent skill](https://github.com/contextgeneric/cgp-skills) beside the costs of wiring,
  vocabulary, and diagnostics, as prescribed in [message.md](message.md#the-objections-readers-bring).
  Readers can try it and judge its help. Its existence does not prove that it removes those costs,
  and AI support should not lead the pitch.

The 2025 survey suggests that some learning questions may be moving to LLM tools. Its authors infer
this from open answers and shifts in community participation. Treat that as context for agent
support, not as a measurement of CGP users or evidence that the skill solves their difficulties.

## What the search data shows about demand

Google Search Console gives the project one measured view of what readers look for, and the
finding worth carrying into public writing is which vocabulary they use. Over the twelve months to
2026-09-18 the domain property drew 121,685 impressions and 970 clicks, and its largest non-branded
term by far was the **blanket-implementation family**: six query variants totalling 1,781 impressions
and 106 clicks at average positions between 4.0 and 5.1. The page earning most of them is a chapter of
the [CGP Patterns book](https://patterns.contextgeneric.dev/).

Two conclusions follow for this section, and both are narrow. **Blanket implementations are the
entry point readers actually search for**, which supports leading with that idea for a general Rust
audience and is independent evidence for the hand-rolled-workaround finding below. And **the
project's own name has almost no search demand** — *context generic programming* and *cgp rust*
together drew 112 impressions in a year, at average positions of 1.1 and 1.3 — which is measured
support for [identity.md](identity.md#why-each-word-of-the-line-is-there)'s rule that the name always
travels with a plain descriptor. The bare acronym drew 736 impressions and no clicks at all.

These are Google figures for one property over one year. They describe what reached this site, not
what the Rust community wants, and the query table is capped at 1,000 rows, so roughly nine
impressions in ten are long-tail queries nobody can inspect.

## The pains are real — and developers already hand-roll the fix

An independently published workaround shows that CGP addresses a problem developers encounter.
The [alternative blanket implementations article](https://www.greyblake.com/blog/alternative-blanket-implementations-for-single-rust-trait/)
uses marker types and a helper trait to allow otherwise-overlapping implementations to coexist.
That resembles CGP's central mechanism and provides a concrete comparison for a reader who suspects
unnecessary abstraction.

Use the workaround to explain the benefit of packaging a reusable technique. It establishes that
someone needed the pattern, and the search data above establishes that people look for the underlying
idea in volume; neither proves that CGP is the best solution for every instance.

Dependency injection provides another comparison, but the trade-offs depend on the design. A
runtime container may use `Arc<dyn Trait>` to resolve an object graph. CGP instead selects providers
through per-context wiring and static dispatch. Explain that difference without generalizing all
DI crates as runtime containers or dismissing their design choices. Consult
[related-work/dependency-injection.md](../related-work/dependency-injection.md) for the comparison.

Public trait signatures can expose implementation details. The
[Rust traits and dependency injection article](https://jmmv.dev/2022/04/rust-traits-and-dependency-injection.html)
explains the cost of exposing types needed by an injection interface. CGP's impl-side dependencies
provide a useful contrast where a dependency can stay inside an implementation. They do not make a
private type usable in a public method signature.

## CGP's own reception, and the lessons in it

The recorded reception of CGP is small and mixed-to-skeptical. The observations below summarize
recurring reactions without identifying readers. They guide revisions but do not quantify the
opinions of the wider Rust community.

Lobsters and the Rust subreddit have provided more substantive discussion than Hacker News in the
project's observed reception. Low engagement on Hacker News alone says little about the idea:
visibility, timing, and titles also affect it. Use comment content with context rather than treating
vote counts as a verdict.

These objections recur and suggest specific responses:

- **Verbosity and an unclear motivating problem:** Readers, including experienced Rust programmers,
  ask what justifies the declarations and wiring. Lead with a concrete problem and a
  before-and-after before naming the paradigm.
- **Difficulty tracing control flow:** Readers want to know which implementation a method invokes.
  Show how the wiring table names a provider and how to follow that choice. A searchable table
  helps navigation but does not eliminate indirection.
- **Similarity to prior work:** Readers compare CGP with aspect-oriented programming, COM, or ML
  modules. Use [related-work](../related-work/README.md) to explain both the resemblance and the
  limits of the comparison.
- **An uninformative name:** "Context-generic programming" does not explain its benefit to an
  unfamiliar reader. Pair the name with a plain description. Structural-typing analogies can help,
  provided the piece explains that CGP remains nominal and wired.
- **An inferred single-item restriction:** Teaching feedback records readers interpreting
  single-method examples as a limit on component traits. Show a working multi-item component
  before discussing grouping, and distinguish macro support from advice about provider reuse.
- **Overstated ergonomics:** Readers expect compiler errors to require understanding generated
  code. Teach the desugaring and present `cargo-cgp` as a response to that difficulty, with its
  limits intact. The canonical concession is: `cargo cgp check` leads with the root cause for the
  classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every class.
  Reception of the tool is not established here; do not invent community praise.

Show generated Rust early enough to prepare readers for debugging. The ergonomics objection
supports the [teaching requirement](readers.md#the-comprehension-barriers) to make the desugaring
understandable, rather than promising that readers will never need it.

The recorded sample covers posts across the [blog catalog](../website/blog/README.md), including
releases, deep dives, and the DSL announcement submitted to the same general venues. This breadth
helps identify recurring objections, but does not make the sample representative. Long-form pieces
can introduce CGP as well as document it.

RustLab 2025 provides a delivered talk to reuse. The Florence presentation has a
[recording](https://www.youtube.com/watch?v=gXIfP-W9074), slides, and a
[published transcript](../website/blog/rustlab-2025-coherence.md). Build future talks from that
material and the [format guidance](formats.md). Publishing a transcript also makes the explanation
searchable and readable without watching a video. These artifacts establish that the conference
format has been used, without measuring adoption or proving its effectiveness.

Use dependency injection as an opening only for readers who find that comparison useful. Rust
already supports lightweight injection through traits and generics, and a framework-oriented pitch
can obscure the particular problem CGP solves. Concrete use also helps evaluators: the
[Hermes SDK](https://github.com/informalsystems/hermes-sdk/) supplies a substantial system to
examine. Its presentation on the site is tracked in the
[redesign queue](../website/redesign-queue.md).

## Where the profiles gather

Choose the channel, intended reader, and opening together. Use the [reader profiles](readers.md)
as a working model, then revise that model from actual responses. These are presentation choices,
not measured demographic assignments to venues.

General channels need a clear description and a concrete example. Lobsters and the Rust subreddit
have hosted useful CGP discussion; *This Week in Rust* offers another distribution route. Treat
Hacker News as an uncertain opportunity rather than the basis of a plan. Address the motivating
problem and make implementation selection visible before readers dismiss the code as verbosity.

Specialist readers need comparisons suited to their existing knowledge. Functional-programming
and type-system audiences can use the relevant one-liners in [message.md](message.md). Evaluators
need detailed explanations and comparisons that state maturity, costs, and practical use.

Language-design readers need a precise contribution to a design question. A general announcement
alone is unlikely to provide it. Explain the fragment CGP implements, the desugaring it supplies,
and the problems it leaves unresolved. Relevance to a live discussion matters more than a broad
claim that CGP validates a language proposal.

## What we watch, and what counts as a result

Use a signal that matches the reader's stage in the
[conversion ladder](formats.md#the-conversion-ladder). The stages move from awareness to trying,
using, and recommending the tool; [craft sources](#sources-for-the-craft-this-section-borrows)
provide the background. Keep campaign measurements and logs outside this repository, and bring back
findings that change the guidance.

Track these signals where they are available:

- **Awareness: questions prompted by the opening.** Read the first ten replies, distinguish
  how-questions from dismissals, and compare their proportions. Note replies that fit neither
  group and samples with fewer replies. This is a rough framing check, not a measure of adoption;
  it is the only measurement recorded as used so far.
- **Activation: time to a running program.** The Quickstart target is a reader with Rust installed
  reaching a working result in under ten minutes using only the page. Measure with a
  [friction log](readers.md#keeping-the-model-observed) on a clean machine. The target is owned by
  [the orientation-page guide](../website/writing-guides/orientation.md), which the page is written
  against. Hello World and the first tutorial part use the same measure with longer budgets.
- **Adoption: recurring questions from people writing code.** Summarize patterns from GitHub
  Discussions, Discord, and the subreddit. Investigate the page that should answer each question.
  If confusion persists after a revision, examine both the explanation and the construct.
- **Advocacy: independent writing and components.** Count contributions and unsolicited writing
  when they occur, and record which subjects they cover. These indicate engagement beyond reading;
  they do not by themselves establish widespread adoption.
- **Search: available through Google Search Console, for Google only.** The site has no analytics
  and needs none for this: Search Console places no script on the site and reports what Google
  already knows about its own index. A twelve-month export to 2026-09-18 is summarized below and
  analyzed in the website section's [SEO strategy](../website/seo.md). Nothing equivalent exists for
  Bing, Kagi, or Brave, so claims about those engines still rest on hand checks. Keep raw exports
  outside this repository.

Establish a baseline before attributing a change to a piece. Collect a signal only when it can
inform a decision. Update the standing guidance when findings change it; repeated confirmation
belongs in the external measurement record, if needed, rather than adding detail here.

## Reading the reaction

Use replies to test whether the opening communicates the intended benefit. Questions about how
CGP achieves a result suggest that readers understood enough to investigate. Dismissals about
verbosity, unclear control flow, prior art, or an opaque name suggest places to revisit. They may
also express a real cost or a poor fit, so do not assume every objection is a wording failure.

Try a candidate opening with its intended audience and revise from the response. Check whether the
problem is clear, whether the comparison is accurate, and whether a limitation needs stating.
Summarize changed conclusions in the patterns above without reproducing threads or identifying
commenters. Publication planning and detailed results remain outside this repository.

Space substantial publications apart to reduce competition for the same readers. Simultaneous
posts can divide attention and make their results harder to interpret. Treat spacing as part of
the external publication plan.

## Sources, and when each was last checked

Check a source before using its claim in public, and update its verification date. The table records
what each source supports and how it was checked. "Read" means the claim was checked against the
page; "link resolved" confirms only that the page existed. Retain the earlier date for sources that
have not been checked again.

| Source | Supports | Last checked |
|---|---|---|
| [2025 State of Rust survey](https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results) | the compilation, complexity, debugging, and LLM-tooling findings | 2026-09-20, article and relevant charts read |
| [2024 State of Rust survey](https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/) | performance as a reason employers invest in Rust | 2026-09-20, read |
| [Ixrec/rust-orphan-rules](https://github.com/Ixrec/rust-orphan-rules) | the orphan rule as a durable frustration | 2026-09-19, link resolved |
| [Function-coloring debate](https://www.thecodedmessage.com/posts/async-colors/) | the async attachment point | 2026-09-19, link resolved |
| [`Send` bounds and `dyn` issue](https://github.com/rust-lang/rust/issues/103854) | the async-trait friction | 2026-09-19, link resolved |
| [Reflection and comptime project goal](https://goals.rust-lang.org/2026/reflection-and-comptime.html) | the reflection goal, landed MVP, and experimental scope | 2026-09-20, read |
| [Dictionary-passing style](https://nadrieril.github.io/blog/2026/03/20/dictionary-passing-style.html) | the language-design conversation | 2026-09-19, link resolved |
| [What if traits carried values](https://nadrieril.github.io/blog/2026/03/22/what-if-traits-carried-values.html) | the language-design conversation | 2026-09-19, link resolved |
| [An Incoherent Rust](https://www.boxyuwu.blog/posts/an-incoherent-rust/) | the language-design conversation | 2026-09-19, link resolved |
| [Context and capabilities](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/) | the language-design conversation | 2026-09-19, link resolved |
| [cgp-skills](https://github.com/contextgeneric/cgp-skills) | the agent skill exists and is published | 2026-09-19, link resolved |
| [Alternative blanket implementations](https://www.greyblake.com/blog/alternative-blanket-implementations-for-single-rust-trait/) | developers hand-roll CGP's marker-struct pattern | 2026-09-19, link resolved |
| [Rust traits and dependency injection](https://jmmv.dev/2022/04/rust-traits-and-dependency-injection.html) | trait-based injection leaks internal types into a public API | 2026-09-19, link resolved |
| [RustLab 2025 recording](https://www.youtube.com/watch?v=gXIfP-W9074) | the talk exists and is public | 2026-09-19, link resolved |
| [Hermes SDK](https://github.com/informalsystems/hermes-sdk/) | a substantial system built with CGP | 2026-09-19, link resolved |

### Sources for the craft this section borrows

Use these sources for the communication methods applied elsewhere in the section. Link to this
list when using a method. "Summary read" records consultation of a published summary rather than
verification against the full original work.

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
