# Messaging brief: the strategy on one page

This document compresses the communication strategy into the facts a writer needs at hand while
drafting: the line, the frame, the features, the pain to lead with for each reader, the objections and
their answers, the boundary, the costs to concede, the ask for each stage, the words to use and avoid,
and the rules and checks every piece passes through. It is a summary, not a source. Every entry is
taken from a fuller document in this section, and when the two disagree the fuller document is right
and this page is corrected.

Read this page before writing any public copy about CGP. Read the document it points to before
writing anything longer than a thread. The reasoning behind each entry lives there, and a writer who
knows only the entry will misapply it at the first case the entry did not anticipate.

## The line, and the two lines after it

The tag line is settled, and every piece opens with it or echoes it. The two lines that follow are the
order in which to spend a reader's next seconds. The full argument, and the five positioning decisions
the line follows from, are in [identity.md](identity.md#the-positioning-in-the-order-it-was-decided).

- **Tag line** — *A language extension for Rust, with pluggable trait implementations at
  compile-time.*
- **Reassurance line** — *Still ordinary Rust — a library on the stable toolchain, with no runtime
  cost, adopted one trait at a time.* This is the homepage guide's copy. It answers the two misreadings
  the tag line invites, a new language to learn and a runtime framework.
- **Breadth line** — beyond swappable trait implementations, CGP adds abstract types a context
  chooses for itself, so an error type or a runtime stops being a parameter every layer has to carry,
  plus extensible records and variants and a family of composable handlers.

**The frame under all three: CGP extends Rust's trait system and does not replace it.** A CGP trait is
still a trait, a consumer trait can be implemented directly with no CGP machinery, and a project can
use CGP in one module and stay otherwise vanilla. Name the paradigm only after a concrete benefit has
landed, and always beside a plain descriptor.

## The five headline features

These are the only features a front page shows, in this order, each as a title and one or two
sentences. The wording is fixed in [identity.md](identity.md#the-headline-feature-set).

| Feature | The sentence |
|---|---|
| One Interface, Many Implementations | Write many interchangeable implementations of the same interface and choose between them per application, with the overlapping and orphan implementations Rust normally forbids made safe because every choice is explicit and local. |
| Zero-Cost Abstraction | Everything is resolved at compile time and compiles down to direct calls, so the flexibility costs nothing at runtime and unused providers never reach the binary. |
| Type-Safe Wiring | All wiring is checked at compile time, so a missing dependency is a build error rather than a runtime failure — and it runs entirely in safe Rust, with no `dyn`, `Any`, or reflection. |
| Abstract Over Every Dependency | Write core logic that names its error type, runtime, and I/O abstractly and let each context supply the concrete choice — which keeps the core `no_std`-friendly, from embedded systems and kernels to WebAssembly. |
| Still Ordinary Rust | CGP is a superset of ordinary traits that you adopt one piece at a time: providers read like normal impls and implicit arguments like normal parameters, so a codebase can use it in one corner and stay otherwise vanilla. |

## The pain to lead with, by reader

Open on a problem the reader already has, then let the fix arrive as relief. Name the reader first,
then pick the row. The entries are developed with code in
[message.md](message.md#the-problems-cgp-removes), and the readers in [readers.md](readers.md).

| Reader | Lead with |
|---|---|
| Broad public audience, first-contact skimmer | Two blanket impls Rust rejects outright, shown with the real `E0119` |
| Trait-heavy working developer | Implementing a trait for a type you do not own, with no newtype |
| Pragmatic majority | Mock in tests, real thing in production, without `dyn` or a framework |
| Anyone asking why two contexts | Your second application already exists, spelled as a feature flag |
| Systems and ML-module reader | Swap the error type or runtime by changing one line |
| Deep call graph maintainer | Stop threading a dozen generic parameters through every layer |
| Evaluator | Break up a trait that grew into a monolith |
| Framework and library author | Generic over a type's structure, with no runtime reflection |
| Anyone who heard the errors are unusable | A compile error read through `cargo cgp check` |

## The objections, and the one-line answers

Concede the real part first, then locate the difference. These are the objections a piece meets most
often; the full set, with the reasoning behind each answer, is in
[message.md](message.md#the-objections-readers-bring).

| Objection | Answer |
|---|---|
| This is dependency injection, and DI is heavy and magic | Compile-time, reflection-free, with no container: the container is the type system. |
| Values appear from nowhere | Nothing is resolved automatically. The provider is named in a wiring table. |
| Coherence exists for a reason | Agreed. CGP is incoherent at the definition level and coherent at the use site: each context names exactly one provider. |
| Too clever, over-engineered | For one implementation, use a plain trait. CGP earns its keep when they multiply. |
| I only have one application | Then the per-context payoff is not there yet. The overlap and orphan escapes still are, and your test harness is the second context. |
| So a CGP trait can only have one method? | No. A component trait takes as many items as any trait. Grouping is a reuse trade-off you price. |
| Won't I get a context per configuration? | Only for the axis where a wrong combination must be impossible. Generics and enums still collapse the rest. |
| Macros are magic | The wiring is a table you read, and `cargo cgp expand` prints the expansion. Debugging generated code is a real cost. |
| Why not just traits, generics, or an enum? | Often right. For one implementation, or a small closed set, the plain tool wins. CGP is the tier above, adopted deliberately. |
| I can't tell which code runs on a call | There is one hop, and it is static. The wiring table is the one greppable place naming the provider for each component. |
| What about compile times? | They go up, and no number is quoted without a source. Work done at compile time is work not done at runtime, or not checked at all. |
| The errors are a wall of generated types | They are. A check localizes them and `cargo cgp check` leads with the root cause for the classes it recognizes, and the tool is a v0.1.0-alpha. |
| It's immature | It is. It is also a superset of ordinary traits, so it can be adopted in one corner and stepped back from. |
| There's a learning curve | There is. The first useful step, an operation written as a function and used with no wiring, needs only ordinary Rust. |

## The boundary, and the costs to concede every time

The boundary sentence: *use CGP when a trait needs more than one implementation and the choice
belongs to the context, and not before.* The alternatives and where each wins are in
[message.md](message.md#when-not-to-reach-for-cgp).

Four costs are stated beside the benefit in every piece, in plain words and in the same passage. They
are the register in [voice-and-register.md](voice-and-register.md).

- **More machinery than a plain trait**, and for a trait with one implementation a plain trait is the
  right tool.
- **Compile-time work**, with no magnitude claimed.
- **Verbose raw diagnostics**, with `cargo cgp check` named as the mitigation and its v0.1.0-alpha
  status conceded in the same sentence.
- **A learning curve**, with the first step shrunk rather than the curve denied.

CGP's agent skill answers three of these costs and is mentioned only beside them: in a cost section,
a boundary discussion, or a page about maturity. It never appears in the tag line, a feature, a hook,
or an opening. Say it reduces the cost, not that it removes it. The rule is in
[message.md](message.md#the-one-mitigation-that-spans-three-of-these).

## The ask, by stage

Each piece ends with one call to action, matched to the reader's stage. The ladder is in
[formats.md](formats.md#the-conversion-ladder).

- **First-contact skimmer** — the Quickstart, or a runnable example.
- **Working developer** — the tutorial closest to their pain.
- **Evaluator** — the honest maturity discussion and a real system built with CGP.
- **Enthusiast** — the book and the contribution path.

## Words

The full list, with the reasons, is in [vocabulary.md](vocabulary.md). The rows below are the ones
that most often go wrong.

| Avoid | Say instead |
|---|---|
| modular, paradigm, as a lead word | a language extension, pluggable trait implementations |
| magic, automatically resolves, finds | explicit, named in one readable place |
| a DI framework, a reflection system | compile-time reflection-free dependency injection, compile-time structural reflection |
| blazingly fast, zero-cost abstraction in prose | compiled to a direct call, no vtable, nothing in the binary for an unused provider |
| no boilerplate | moves the wiring into one readable place |
| replaces traits, a new language | a superset of ordinary traits, a library on stable Rust |
| capability, for CGP's own constructs | trait, method, operation, trait dependency |
| solved, fixed, for the errors | leads with the root cause for the classes it recognizes |
| AI-native, AI-first | CGP publishes an agent skill, said beside a cost |
| context, unqualified, when the shape changes | value context, environmental context, application context |

## The rules that apply to every piece

Five rules hold regardless of format, and each has a document behind it.

- **The website speaks as the project and the blog speaks as the author.** No first person on a docs
  page, no corporate "we" anywhere. [voice-and-register.md](voice-and-register.md).
- **Never fabricate evidence, and never disparage another tool.** No invented benchmark, adoption
  figure, or quotation. Represent every alternative as its own users would, and name where it is the
  better choice. [AGENTS.md](AGENTS.md#honesty-is-the-strategy).
- **Distil what readers say about CGP; never point at who said it.** Record the recurring objection,
  not the thread or the commenter. [evidence.md](evidence.md).
- **Say which shape an example is in when the shape changes.** A value context, an environmental
  context, or an application context, self-targeted or parameter-targeted. Nothing in a signature
  marks the difference. [vocabulary.md](vocabulary.md#qualifying-a-context-and-a-target).
- **Reuse one of the four canonical examples before inventing one.** The encoder pair, the greeter,
  the email swap, and the area calculation, each with its shape recorded.
  [voice-and-register.md](voice-and-register.md#show-it-canonical-examples-diagrams-and-diffs).

## The four checks before publishing

Run them in this order, per [voice-and-register.md](voice-and-register.md#checking-a-draft).

1. **Did a person write it?** A paragraph that could have been generated from the topic alone says
   nothing specific. Name the construct, quote the error, show the line.
2. **Is the cost stated?** Find it. If it is missing, the piece is overselling.
3. **Delete every intensifier** that can go without changing the meaning.
4. **Does the voice match the surface?** Project voice on the site, the author's on the blog, no
   corporate "we".

## Where the rest is

- [author-personality.md](author-personality.md) — who the author is as a writer. It wins any conflict.
- [voice-and-register.md](voice-and-register.md) and [writing-styles.md](writing-styles.md) — how the
  prose sounds, and the sentence shapes to avoid.
- [identity.md](identity.md) — the line, the frame, and the features, argued.
- [readers.md](readers.md) — who reads, and what stops them following.
- [message.md](message.md) — pains, strengths, objections, and the boundary, with code.
- [vocabulary.md](vocabulary.md) — the word list and the glossary of the craft.
- [reader-simulation.md](reader-simulation.md) — modeling the reader sentence by sentence.
- [formats.md](formats.md) — the playbook for each artifact, with worked drafts.
- [evidence.md](evidence.md) — the citable facts, and how CGP has been received.
- [ai-disclosure.md](ai-disclosure.md) — what the project says about how it is made.
