# Writing a tutorial

A CGP tutorial's job is to get a reader to a working program and one durable idea, in a single sitting,
without asking them to hold anything they have not been shown. The tutorials are the only maintained,
sequenced teaching material on the site, which makes them the highest-value pages to keep current and the
first place a newcomer should be routed.

- **URL** — <https://contextgeneric.dev/docs/tutorials/>
- **Source** — [docs/tutorials/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/tutorials)
- **Voice** — project voice, with the teaching "we" ("we start by defining the component"), per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Governed by** — [readers.md](../../communication-strategy/readers.md) for the reader and the
  comprehension barriers; [vocabulary.md](../../communication-strategy/vocabulary.md) for which words may
  appear when

## Tutorials are independent and named for an outcome

**Each tutorial stands alone.** There is no required order through the section, no numbered curriculum,
and no tutorial that assumes the reader has finished another. A tutorial restates the little it needs —
the prelude import, the two-line context struct — and gets on with its own subject. This costs some
repetition and buys the thing that matters more: every tutorial is an entry point, so a reader arriving
from a search result, a forum reply, or an agent's suggestion lands somewhere that works.

**Title a tutorial for what the reader will have done, not for the construct it introduces.** "Swap an
implementation per context" over "Using `#[cgp_component]`"; "Make your error type abstract" over
"Abstract types". The construct is what the tutorial teaches; the outcome is why anyone opens it. Naming
by construct also quietly turns the section into a reference index, which is not what it is for.

Tutorials may overlap deliberately, and several already do — the same `#[cgp_fn]` and `#[implicit]`
ground is covered by both existing series. That is not duplication to be eliminated. Two tutorials may
teach the same concept through different problems, in different registers, at different depths, and a
reader who bounced off one may land on the other. What is *not* acceptable is two tutorials teaching the
same concept with different vocabulary or different idioms, since that reads as incoherence rather than
as choice.

## The two registers

CGP tutorials come in two registers. Both are first-class, both teach the same concepts, and they exist
because readers learn differently — one wants to understand the machine, the other wants to build the
thing. Choose the register before outlining, because it changes almost every subsequent decision.

**The first-principles register** teaches a complex concept through a deliberately simple example. Its
subject is the *idea*, and the example — rectangles and circles, a greeting, an area calculation — is
chosen to be so small that nothing distracts from the mechanism. It derives each construct as the
solution to a problem the reader has just watched fail, shows what the construct desugars to, and expects
the reader to leave able to explain *why* each step was necessary. The
[area-calculation series](../tutorials/area-calculation.md) is the model, and this is the register that
family continues in as it grows to cover checking, namespaces, handlers, and extensible data.

**The applied register** teaches by building something real. Its subject is the *thing* — a web backend,
a CLI, a serializer — and CGP is the material it is built from rather than the topic. It does not derive
constructs from first principles or show desugarings; it shows a working design, names the construct doing
each job, and links out to the first-principles tutorial or the reference for readers who want the
mechanism. Its reader is the developer who evaluates a technology by seeing a realistic system in it, and
who will not sit through a rectangle. The site has no tutorial in this register yet, and that is the
larger of its two gaps.

Three rules keep the registers from blurring. **Do not mix them within one tutorial** — a first-principles
tutorial that suddenly hand-waves a construct breaks its own contract, and an applied tutorial that stops
to derive coherence loses the reader it was written for. **State the register in the opening paragraph**,
so a reader can leave immediately if it is the wrong one for them: "we will build this up from plain Rust
functions, one step at a time" versus "we will build a working balance-and-transfer API, and link out to
the details as we go". And **make the two discoverable from each other**, since the reader who bounces off
one is exactly the reader the other was written for.

Applied tutorials draw their scenarios from [examples/](../../examples/README.md), which is where the
verified end-to-end programs live — the [money-transfer API](../../examples/money-transfer-api.md), the
[social media app](../../examples/social-media-app.md), the
[shell-scripting DSL](../../examples/shell-scripting-dsl.md), and the rest. An example is the progression
with the teaching prose stripped out; an applied tutorial is that progression with the prose put back.
Draw from there rather than inventing a scenario that then needs its own verification.

## What every tutorial owes its reader

Six obligations hold in both registers. They are adopted from Diátaxis, which the project
[cites approvingly](../blog/new-website.md), and they are the part of that framework CGP takes wholesale.

**Show the destination first.** Open by saying what the reader will have at the end — a working program
that does a specific thing — so they can decide whether to spend the time and can tell when they have
arrived.

**Deliver a result early, and often.** Every step should produce something the reader can run and see.
The [Hello World tutorial](../tutorials/hello-world.md) gets to a printing program before it explains
anything, and that ordering is the reason it works.

**Narrate what will happen, and point out what to notice.** "You will see", "notice that `greet` works
unchanged on both", "the compiler will reject this, and the error is worth reading". These are the
sentences that turn a sequence of steps into an experience the reader is being guided through, and they
are what makes a tutorial feel supervised rather than transcribed.

**Carry one running example the whole way.** Switching examples per concept resets the reader's context
each time and prevents understanding from compounding. One domain, developed.

**Aim for perfect reliability.** A tutorial the reader cannot make work is worse than no tutorial. Pin the
`cgp` version in the `Cargo.toml` snippet, and pin **the version the tutorial's code is written against** —
currently `"0.8.0"`, not the `"0.7.0"` the Hello World tutorial still carries. Where that release has not
yet been published, the pin resolves only when it does, so re-pinning every tutorial belongs on the
[release checklist](release-announcement.md#publishing-and-what-happens-afterwards) and a tutorial going
live ahead of its release needs a one-line note giving the git dependency instead. Where a step
intentionally fails to compile, say so before it happens.

**Give one path.** Do not offer options, alternatives, or "you could also". A tutorial is not the place
for a decision; the [guides](../../cgp/guides/README.md) are, and the tutorial can link there.

## What CGP takes from Diátaxis, and what it rejects

Diátaxis's first rule for tutorials is *don't try to teach*, and its second is that a tutorial is not the
place for explanation. **CGP rejects both, deliberately, and the reason is specific rather than a general
preference for depth.**

CGP is implemented as procedural macros, so a reader's first honest reaction to `#[cgp_fn]` is *what did
that generate, and what is it costing me?* This is not idle curiosity — it is the correct instinct of a
Rust programmer, and it has been stated in public: a skeptic in CGP's own release discussion pointed out
that "when I hit a compilation error, I'm going to have to understand the desugaring", and they were
right ([evidence.md](../../communication-strategy/evidence.md)). A tutorial that withholds the desugaring
does not spare the reader the machinery; it defers the machinery to the first compile error, where it will
arrive without a guide. **Showing what a construct generates is therefore part of teaching it, not a
digression from teaching it.**

So the rule for CGP is narrower than Diátaxis's and firmer than a preference. **A first-principles
tutorial must show the plain-Rust equivalent of what it teaches, in a clearly marked section, and that
section may be optional to read but is not optional to write.** The two existing tutorials both do this
and are better for it: Hello World's "Behind the Scenes" appendix shows a hand-written `HasName` getter
trait and a blanket impl, and area-calculation's "How it works" section shows the same for `#[cgp_fn]`
and `#[uses]`. An **applied** tutorial does not carry a desugaring section — its reader did not come for
the mechanism — but it must link to the first-principles tutorial or explanation page that does.

Two further Diátaxis prohibitions are also relaxed, and for related reasons. **Abstraction is allowed
where it is the subject**: a first-principles tutorial's whole point is the idea behind the code, so
"this is what lets two contexts choose differently" belongs in it. And **a construct's motivation is not
optional**, because a CGP construct shown without the problem it solves reads as ceremony — which is the
single most common complaint the project receives.

The other Diátaxis ideas are adopted without qualification, as the six obligations above.

## The two orderings that carry a tutorial

Two orderings do most of the pedagogical work in CGP tutorials, and an unwary addition breaks them more
easily than anything else. They are what the
[area-calculation teaching contract](../tutorials/area-calculation.md) exists to protect.

**The problem always precedes the construct.** Every step opens with code that is unsatisfactory for a
stated reason, and the construct arrives as the fix. Area-calculation earns its length this way: it writes
`scaled_rectangle_area` threading parameters it does not use, then groups the fields into a struct and
finds the methods coupled to one type, then adds a second shape and finds the code duplicated, then tries
two blanket impls and **shows the compiler error** — and only then does `#[cgp_component]` appear. A
reader who has felt each problem forgives the machinery; a reader who has not forgives none.

**The explicit form always precedes the sugar.** Providers are called by name — `RectangleArea::area(&rect)`
— before any wiring exists; the consumer trait is implemented by hand before `delegate_components!`
replaces it; the plain-Rust blanket impl is shown before `#[cgp_fn]` is trusted. This is what makes the
sugar read as an abbreviation for something the reader has already written rather than as magic, and it is
the same instinct as the desugaring rule above applied to the body of the tutorial rather than its
appendix.

Both orderings are properties of the first-principles register. An applied tutorial inverts the second one
by necessity — it starts from the idiomatic form, because that is what the reader would write — and
compensates by linking to the tutorial that derives it.

## Which constructs, in which order, and in whose words

A tutorial introduces constructs in the order the
[prerequisite ladder](../../communication-strategy/readers.md#the-comprehension-barriers) allows, and
the ladder is unforgiving near the bottom. Lead with the forms that show no generics and no
traits: [`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md) with
[`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments and
[`#[derive(HasField)]`](../../cgp/reference/derives/derive_has_field.md) are the gentlest possible entry,
because the reader writes a function and a struct and gets a working program with no wiring at all. Then
[`#[uses]`](../../cgp/reference/attributes/uses.md), read as importing a capability. Then, when a second
implementation is genuinely needed, [`#[cgp_component]`](../../cgp/reference/macros/cgp_component.md) and
[`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md), then
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md), and only after that the
higher-order and abstract-type constructs.

Three constructs must never appear in introductory material: the inside-out
[`#[cgp_provider]`](../../cgp/reference/macros/cgp_provider.md) shape, which forces the reader to hold an
inversion of `self` before they can read a body; and
[`DelegateComponent`](../../cgp/reference/traits/delegate_component.md) and
[`IsProviderFor`](../../cgp/reference/traits/is_provider_for.md), which are the mechanism rather than the
model. Describe the wiring table with a plain analogy — a settings map, a lookup table — and say that it
is resolved at compile time and compiles away, which doubles as the zero-cost reassurance.

Every tutorial writes the **modern idioms** the [guides](../../cgp/guides/README.md) teach, because a
tutorial is where a reader forms their habits and teaching a legacy form means teaching a dialect they
must unlearn. In particular: `#[cgp_impl]` with the header `impl Trait` and no `for Context`, an
`#[implicit]` argument rather than a getter trait declared only to read a field, `#[uses]` rather than a
hand-written `where Self:` bound, `#[use_type]` rather than a supertrait plus `Self::Type`, and the `open`
statement rather than a `UseDelegate` table. Where a tutorial deliberately shows the explicit form first,
per the ordering above, it must say plainly that the sugar is the idiom and the explicit form is the
explanation.

Vocabulary is introduced on the same schedule. Defer "consumer trait", "provider trait", "component", and
"wiring" until the moment each becomes necessary, and defer "coherence", "orphan rule", "blanket impl",
and "monomorphization" further still — introducing each through the problem it names rather than as a term
to learn. [vocabulary.md](../../communication-strategy/vocabulary.md) is the authority on which word and
which gloss.

### Say which shape the tutorial's example is in

**Every tutorial states, in its own internal document, which of CGP's three shapes its running example
uses**, and a tutorial that crosses from one to another says so in the prose. Both existing series use a
**value context** whose capability targets `Self`: `Person` is the thing being greeted, `Rectangle` is the
thing whose area is computed. That is the right choice for a first tutorial, because the wired type is
something the reader can see and hold — but it is not the shape most CGP code is written in, which is an
**environmental context**: a type standing for the application, with the capability about the application
rather than about data.

The obligation is narrow and cheap. A tutorial need not teach the qualifiers or use the words, and an
introductory one should not; what it must not do is let a reader generalize from a value context and then
meet an application context with nothing marking the change, since nothing in a signature marks it — no
parameter appears, and the reader is left unable to say what a context is. An applied tutorial, whose
scenario is a real system, is almost always in the environmental shape and should introduce the context as
"a type that stands for this application, which is where its choices live" the first time it appears.
Whether such a context has fields is incidental and worth saying: some carry a database pool, and some are
an empty `struct App;` whose whole job is to be a name the wiring hangs off. The vocabulary and the
misreadings it prevents are in
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target); the
underlying account is the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md).

**This is also why the applied tutorial comes second in the section rather than last.** A reader's first
two contacts with CGP — the front page's hero block and Hello World — both wire a value context, which is
deliberate in each case and leaves the site having taught only the least representative shape. The applied
tutorial is naturally environmental, so placing it directly after Hello World is what gets the common
shape in front of a reader before their habits form; the alternative, reaching it after three parts of
area calculation, means most readers never do. The ordering is fixed in
[information-architecture.md](../information-architecture.md#the-target-page-inventory) and the trade it
pays for is stated in the [homepage guide](homepage.md#which-shape-it-is-and-why-that-matters-here).

## Errors, checking, and the tooling

**Every tutorial that wires a context must teach that wiring is lazy, and must show the reader what a
failure looks like before they cause one.** This is the largest gap in the current material: neither
existing tutorial mentions [`check_components!`](../../cgp/reference/macros/check_components.md),
neither explains that a mis-wired context compiles until the component is used, and neither mentions
[`cargo-cgp`](../../cgp/reference/cargo-cgp.md) — so a reader who mis-wires meets a wall of generated
types at a call site with no idea that either mitigation exists.

The obligation has three parts. **Say that wiring is lazy** and that a check turns a latent gap into an
error at the wiring site. **Show one deliberate failure**: remove a field a provider needs, show the raw
error's shape without pasting a screenful of it, then show the same failure through `cargo cgp check`
naming the missing field. And **set the expectation honestly** — raw CGP diagnostics can be verbose, a
check localizes them, `cargo cgp check` leads with the root cause for the classes it recognizes, and the
tool is an early pre-release that does not yet reshape every class. Pretending the diagnostics are as
smooth as the surface syntax costs more trust than admitting they are not.

This material earns its own tutorial in the first-principles register, and writing it is the clearest next
addition to the section. Until it exists, every tutorial that reaches
`delegate_components!` should carry at least the short version.

## Recording the teaching contract

Adding a tutorial to the site means adding its document under [../tutorials/](../tutorials/README.md) in
the same change, and that document records the **teaching contract** a later revision must not break: the
objective, the prerequisites — including what the tutorial deliberately does *not* assume — the concept
sequence with the reason for any non-obvious ordering, and the level of explanation. A tutorial whose
contract is not written down will be damaged by the first well-meaning addition, because the ramp it
depends on is invisible in the prose.

Two things belong in every contract and are worth stating explicitly. The **register** — first-principles
or applied — because it determines whether a desugaring section is required. And the **payoff position**:
the step where the reader sees why the whole tutorial was worth doing. In Hello World that is the second
context, and moving it earlier removes the motivation while moving it later loses the reader; every
tutorial has such a step, and naming it protects it.

## What must not be in a tutorial

**No exhaustive syntax.** A tutorial shows the forms it uses and links to the
[reference](../../cgp/reference/README.md) for the rest. Listing every accepted form of a macro turns the
page into a specification and buries the path.

**No decisions.** No "you could also use", no comparison of alternatives, no advice on when to prefer one
construct over another — that is what the [guides](../../cgp/guides/README.md) are for, and a tutorial
that offers a choice leaves the reader stalled.

**No internals for their own sake.** The desugaring section shows the plain Rust a construct generates,
which the reader can read. It does not show `IsProviderFor`, the generated blanket impls, or the
`Symbol<…>` spine, which the reader cannot yet.

**No unmotivated construct.** If a tutorial introduces something the reader has not been given a reason to
want, either the motivation is missing or the construct does not belong in this tutorial.

**No first-person narration.** The tutorials are project voice. The author's voice, with its history and
its candour, belongs on the blog.

## Where the current tutorials stand

Two series exist and both are sound. [Hello World](../tutorials/hello-world.md) is a well-judged
five-minute first contact whose two-level split — a shallow body and an optional desugaring appendix — is
its main craft; its only defect is the stale version pin, and its main risk is additions, since its value
is that it is short enough to finish. [Area calculation](../tutorials/area-calculation.md) is the site's
best teaching material and the clearest execution of both orderings above; it shows the compiler error
that motivates the consumer/provider split, and it calls providers explicitly before any wiring exists.

Three gaps are worth writing down as the section's work queue. There is **no tutorial on checking and
debugging**, which is the highest-value addition and the natural next part of the area-calculation family.
There is **no tutorial in the applied register**, so the reader who evaluates by seeing a realistic system
has nowhere to go on the site — and, per the ordering above, no reader meets an application context
either. And **no tutorial mentions `cargo-cgp`**, despite it being the project's direct answer to the
obstacle most cited by readers who walked away.

## Checking a draft

Run five checks before publishing.

**Read only the code blocks, in order, and ask whether they build to a working program.** If a reader
following only the code lands somewhere broken, the tutorial has failed its reliability obligation
regardless of how good the prose is.

**Find each construct's motivating problem.** Every construct should be preceded by code that is
unsatisfactory for a stated reason. A construct that appears without one is ceremony.

**Check the register is consistent** — first-principles throughout with a desugaring section, or applied
throughout with links out. A draft that drifts between them serves neither reader.

**Check what is deferred.** No `#[cgp_provider]`, no `DelegateComponent`, no `IsProviderFor`, no coherence
theory before the error that motivates it, and no vocabulary introduced before the concept needs it.

**Verify every snippet and the version pin** against the source and the `/cgp` skill, drawing on
[examples/](../../examples/README.md) for code that is already verified.
