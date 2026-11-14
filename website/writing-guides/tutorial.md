# Writing a tutorial

A CGP tutorial gets a reader to a working program and one durable idea, in a single sitting, without
asking them to hold anything they have not been shown. The tutorials are the site's only maintained,
sequenced teaching material, so they are the highest-value pages to keep current and the first place
to route a newcomer.

- **URL**: <https://contextgeneric.dev/docs/tutorials/>
- **Source**: [docs/tutorials/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/tutorials)
- **Voice**: project voice, with the teaching "we" ("we start by defining the component"), per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Governed by**: [readers.md](../../communication-strategy/readers.md) for the reader and the
  comprehension barriers; [vocabulary.md](../../communication-strategy/vocabulary.md) for which words may
  appear when
- **Records**: one teaching-contract document per series under [../tutorials/](../tutorials/README.md)
- **Reading**: the shared set and [the tutorials' row](README.md#tutorials) of the reading map

## Tutorials are independent and named for an outcome

**Each tutorial stands alone**: no required order, no numbered curriculum, and none that assumes
another is finished. It restates the little it needs, such as the prelude import and the two-line
context struct, so every tutorial is an entry point for a reader arriving from a search, a forum reply,
or an agent's suggestion.

**Title a tutorial for what the reader will have done, not for the construct it introduces**: "Swap an
implementation per context" over "Using `#[cgp_component]`". Naming by construct turns the section into
a reference index.

**Its opening paragraph names Context-Generic Programming** once, beside a plain description and linked
to the Introduction, and where the outcome is a choice of implementation, relates a short form of the
tag line to it, per the
[naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page). Its
front matter carries a written `description`, and `docs/tutorials/_category_.json`'s `description`
carries the name for the generated index.

**Tutorials may overlap deliberately**, teaching one concept through different problems, registers, or
depths, so a reader who bounced off one may land on another. Two tutorials teaching the same concept
with different vocabulary or idioms is not acceptable, since it reads as incoherence.

## The two registers

**Choose the register before outlining**, because it changes almost every later decision. Both are
first-class and teach the same concepts, for readers who learn differently.

**The first-principles register** teaches a complex concept through a deliberately small example, such
as a greeting or an area calculation. Its subject is the idea: it derives each construct as the fix
for a problem the reader has just watched fail, shows what the construct desugars to, and leaves the
reader able to explain why each step was necessary. The
[area-calculation series](../tutorials/area-calculation.md) is the model, and that family continues
in this register as it grows to cover checking, namespaces, handlers, and extensible data.

**The applied register** teaches by building something real, such as a web backend, a CLI, or a
serializer, with CGP as the material rather than the topic. It shows a working design, names the
construct doing each job, and links to the first-principles tutorial or the reference for the
mechanism, without derivations or desugarings. Its reader evaluates a technology by seeing a realistic
system in it and will not sit through a rectangle.

Three rules keep the registers apart:

- **Do not mix them within one tutorial.**
- **State the register in the opening paragraph**, so a reader can leave if it is the wrong one: "we
  will build this up from plain Rust functions, one step at a time" against "we will build a working
  balance-and-transfer API, and link out to the details as we go".
- **Make the two discoverable from each other.**

**A Projects example page is the applied register's narrower use outside this section**, per
[project.md](project.md#the-example-page): it walks through a program a project already ships and
links here for the construction, while a tutorial is independent, named for an outcome, and builds its
program step by step. An applied tutorial whose scenario a project also ships ends by linking that
project's example page.

**Applied tutorials draw their scenarios from [examples/](../../examples/README.md)**, the verified
end-to-end programs, such as the [money-transfer API](../../examples/money-transfer-api.md), the
[social media app](../../examples/social-media-app.md), and the
[shell-scripting DSL](../../examples/shell-scripting-dsl.md). An example is the progression without the
teaching prose; an applied tutorial puts the prose back, rather than inventing a scenario that needs
its own verification.

## What every tutorial owes its reader

Six obligations hold in both registers, adopted from Diátaxis, which the project
[cites approvingly](../blog/new-website.md):

- **Show the destination first**: what the reader will have at the end, so they can decide whether to
  spend the time and tell when they have arrived.
- **Deliver a result early, and often**: every step produces something the reader can run and see.
- **Narrate what will happen, and point out what to notice**: "notice that `greet` works unchanged on
  both", "the compiler will reject this, and the error is worth reading".
- **Carry one running example the whole way**, so understanding compounds.
- **Aim for perfect reliability.** Pin the `cgp` version in the `Cargo.toml` snippet to the version the
  code is written against, `"0.8.0"` on the release branch. A pin to an unpublished release resolves
  only when it ships, so re-pinning every tutorial belongs to the
  [release](release-announcement.md#publishing-and-what-happens-afterwards), and a tutorial going live
  ahead of its release gives the git dependency in a one-line note. Where a step intentionally fails to
  compile, say so before it happens.
- **Give one path**: no options or "you could also"; the [guides](../../cgp/guides/README.md) hold the
  decisions, and the tutorial can link them.

## What CGP takes from Diátaxis, and what it rejects

**CGP rejects Diátaxis's rules that a tutorial should not teach or explain**, for a specific reason. A
Rust programmer's first honest reaction to a CGP macro is *what did that generate, and what is it
costing me?*, and the first compile error forces them to understand the desugaring anyway
([evidence.md](../../communication-strategy/evidence.md)). A tutorial that withholds it defers the
machinery to that error, where it arrives without a guide.

**So a first-principles tutorial must show the plain-Rust equivalent of what it teaches, in a clearly
marked section that may be optional to read but is not optional to write.** An applied tutorial
carries no desugaring section, but links the first-principles tutorial or explanation page that does.

Two further prohibitions are relaxed:

- **Abstraction is allowed where it is the subject**: "this is what lets two contexts choose
  differently" belongs in a first-principles tutorial.
- **A construct's motivation is not optional**, because a construct shown without its problem reads as
  ceremony, the project's most common complaint.

The rest of Diátaxis is adopted without qualification, as the six obligations above.

## The two orderings that carry a tutorial

Two orderings do most of the teaching, and an unwary addition breaks them more easily than anything
else; the [area-calculation teaching contract](../tutorials/area-calculation.md) exists to protect
them.

**The problem always precedes the construct.** Every step opens with code that is unsatisfactory for a
stated reason, and the construct arrives as the fix, including a compiler error shown before the
construct that resolves it. A reader who has felt each problem forgives the machinery.

**The explicit form always precedes the sugar.** Providers are called by name before any wiring
exists, the consumer trait is implemented by hand before `delegate_components!` replaces it, and the
plain-Rust blanket impl is shown before `#[cgp_fn]` is trusted, so the sugar reads as an abbreviation
of something the reader has written.

Both are properties of the first-principles register. An applied tutorial starts from the idiomatic
form, because that is what the reader would write, and links the tutorial that derives it.

## Which constructs, in which order, and in whose words

**Introduce constructs in the order the
[prerequisite ladder](../../communication-strategy/readers.md#the-comprehension-barriers) allows.**
Lead with the forms that show no generics and no traits:
[`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md) with
[`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments and
[`#[derive(HasField)]`](../../cgp/reference/derives/derive_has_field.md), which give a working program
with no wiring. Then [`#[uses]`](../../cgp/reference/attributes/uses.md), read as importing a trait.
Then, when a second implementation is genuinely needed,
[`#[cgp_component]`](../../cgp/reference/macros/cgp_component.md) and
[`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md), then
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md), and only after that the
higher-order and abstract-type constructs.

**Three constructs never appear in introductory material**: the inside-out
[`#[cgp_provider]`](../../cgp/reference/macros/cgp_provider.md) shape, which forces the reader to hold
an inversion of `self`, and [`DelegateComponent`](../../cgp/reference/traits/delegate_component.md) and
[`IsProviderFor`](../../cgp/reference/traits/is_provider_for.md), the mechanism rather than the model.
Describe the wiring table with a plain analogy, such as a lookup table, and say it is resolved at
compile time and compiles away, which doubles as the zero-cost reassurance.

**Every tutorial writes the modern idioms the [guides](../../cgp/guides/README.md) teach**, because a
tutorial is where a reader forms habits: `#[cgp_impl]` with the header `impl Trait` and no
`for Context`, an `#[implicit]` argument rather than a getter trait declared only to read a field,
`#[uses]` rather than a hand-written `where Self:` bound, `#[use_type]` rather than a supertrait plus
`Self::Type`, and the `open` statement rather than a `UseDelegate` table. Where a tutorial shows the
explicit form first, it says plainly that the sugar is the idiom and the explicit form the explanation.

**Vocabulary follows the same schedule.** Defer "consumer trait", "provider trait", "component", and
"wiring" until each becomes necessary, and "coherence", "orphan rule", "blanket impl", and
"monomorphization" further still, introducing each through the problem it names.
[vocabulary.md](../../communication-strategy/vocabulary.md) decides the word and the gloss.

### Say which shape the tutorial's example is in

**Every tutorial states, in its own internal document, which of CGP's three shapes its running example
uses**, and a tutorial that crosses from one to another says so in the prose. A **value context**, the
thing being greeted or measured, suits a first tutorial because the reader can see and hold it, but
most CGP code wires an **environmental context**: a type standing for the application, with operations
about the application rather than about data.

**The obligation is narrow.** An introductory tutorial need not teach the qualifiers or use the words,
but must not let a reader generalize from a value context and then meet an application context with
nothing marking the change, since no signature marks it. An applied tutorial, almost always
environmental, introduces its context as "a type that stands for this application, which is where its
choices live" the first time it appears, and says whether it has fields, since some carry a database
pool and some are an empty `struct App;`. The vocabulary is in
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target), and the
underlying account in the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md).

**This is why the applied tutorial comes second in the section rather than last.** A reader's first two
contacts with CGP, the front page's hero block and Hello World, both wire a value context, so placing
the naturally environmental applied tutorial directly after Hello World shows the common shape before
the reader's habits form. The order is fixed in
[information-architecture.md](../information-architecture.md#the-target-page-inventory), and the trade it
pays for is in the [homepage guide](homepage.md#which-shape-it-is-and-why-that-matters-here).

## Errors, checking, and the tooling

**Every tutorial that wires a context teaches that wiring is lazy, and shows a failure before the
reader causes one.** A reader who mis-wires unwarned meets a wall of generated types at a call site,
with no idea that [`check_components!`](../../cgp/reference/macros/check_components.md) or
[`cargo-cgp`](../../cgp/reference/cargo-cgp.md) exists. The obligation has three parts:

- **Say that wiring is lazy**, and that a check turns a latent gap into an error at the wiring site.
- **Show one deliberate failure**: remove a field a provider needs, show the raw error's shape without
  pasting a screenful, then the same failure through `cargo cgp check` naming the missing field.
- **Set the expectation honestly**: raw CGP diagnostics can be verbose, a check localizes them,
  `cargo cgp check` leads with the root cause for the classes it recognizes, and the tool does not yet
  reshape every class.

The checking-and-debugging part of the [area-calculation series](../tutorials/area-calculation.md)
carries one mis-wiring through all three diagnostics. Every other tutorial that reaches
`delegate_components!` carries at least the short version and links there.

## Recording the teaching contract

**Adding a tutorial adds its document under [../tutorials/](../tutorials/README.md) in the same
change**, recording the teaching contract a revision must not break: the objective, the prerequisites
including what the tutorial deliberately does not assume, the concept sequence with the reason for any
non-obvious ordering, and the level of explanation. Two more items belong in every contract:

- **The register**, which decides whether a desugaring section is required.
- **The payoff position**: the step where the reader sees why the tutorial was worth doing, which
  moving earlier robs of its motivation and moving later loses the reader to. A multi-part series
  records one payoff per part, rising from basic to advanced, and a part added later records its own.

## What must not be in a tutorial

- **No exhaustive syntax.** Show the forms the tutorial uses and link the
  [reference](../../cgp/reference/README.md) for the rest.
- **No decisions**: no "you could also use", no comparison of alternatives, no advice on when to prefer
  one construct over another; that is the [guides](../../cgp/guides/README.md)' job.
- **No internals for their own sake.** The desugaring section shows the plain Rust a construct
  generates, never `IsProviderFor`, the generated blanket impls, or the `Symbol<…>` list.
- **No unmotivated construct.** Either the motivation is missing or the construct belongs elsewhere.
- **No first-person narration**; the author's voice belongs on the blog.

## Checking a draft

- **Read only the code blocks, in order**, and check they build to a working program.
- **Find each construct's motivating problem**: code that is unsatisfactory for a stated reason, before
  the construct.
- **Check the register is consistent**: first-principles throughout with a desugaring section, or
  applied throughout with links out.
- **Check what is deferred**: no `#[cgp_provider]`, `DelegateComponent`, or `IsProviderFor`, no
  coherence theory before the error that motivates it, and no vocabulary before the concept needs it.
- **Verify every snippet and the version pin** against the source and the `/cgp` skill, drawing on
  [examples/](../../examples/README.md) for code that is already verified.
