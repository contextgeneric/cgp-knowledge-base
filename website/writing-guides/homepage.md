# Writing the homepage

The CGP homepage has one job: **make the idea click, and make the reader want it** — leaving them able
to say what CGP does and why it might matter to them, then routed to the page that teaches it. It is not
a tutorial, not a reference, and not a feature catalogue, and this guide's central discipline is keeping
it from becoming any of those.

- **URL** — <https://contextgeneric.dev/>
- **Source** — [src/pages/index.tsx](https://github.com/contextgeneric/contextgeneric.dev/blob/main/src/pages/index.tsx)
  and [src/components/HomepageFeatures/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/src/components/HomepageFeatures)
- **Voice** — project voice throughout, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Governed by** — [identity.md](../../communication-strategy/identity.md) for the line, the frame, and
  the features; [message.md](../../communication-strategy/message.md) for the pains and capabilities;
  [readers.md](../../communication-strategy/readers.md) for who is reading

## What the page is for, stated precisely

The homepage's success condition is **comprehension that converts**, not conversion alone. A reader who
leaves able to explain CGP to a colleague — "it lets one trait have several implementations and each type
picks one, resolved at compile time" — has been served even if they do not click anything, because that
reader is the one who comes back and the one who repeats the description accurately. A reader who clicks
through excited but unable to say what CGP does will bounce off the first tutorial, and will describe CGP
wrongly in the meantime.

Two consequences follow, and they set this page apart from a conventional developer landing page. The
page must **actually explain something**, which means prose and code rather than a grid of adjectives.
And it must **not try to teach**, because the tutorials do that better and a homepage that starts
teaching becomes a bad tutorial. The line between the two is that explaining answers "what is this and
why", while teaching answers "how do I do it" — and the moment the page starts telling the reader what to
type, it has crossed over.

The page also carries the selling points, so comprehension is not its only output. The difference from a
feature grid is that **each capability appears as a beat in the argument rather than as a card in a
list**: the reader has just seen what CGP does, so "everything resolves at compile time and compiles to a
direct call" lands as an answer to a question they now have rather than as a claim they have no way to
evaluate.

## The two tiers

The page is built in two tiers with a hard boundary between them, because it serves two readers who share
no patience budget.

**Above the fold is a single screen that must stand entirely alone.** Roughly two-thirds of the readers
who ever see this page will see only this, so it has to deliver the whole pitch: the tag line, one
reassurance line, one piece of code that shows the novelty, and two links. Nothing above the fold may
depend on anything below it.

**Below the fold is a bounded essay** for the reader who kept scrolling — the one who is interested
enough to want the argument. It runs the idea from the constraint to the payoff to the cost, in a fixed
number of sections, and it hands off to dedicated pages the moment a section wants to go deeper. Its
length is capped by structure rather than by willpower, which is what the offload rule below is for.

## Above the fold

Four elements, in this order, and nothing else.

**The tag line, verbatim.** *"A language extension for Rust, with pluggable trait implementations at
compile-time."* It sits beneath the project name and is not paraphrased, reworded for the hero, or
replaced by something snappier. The current hero headline — *"Build modular Rust applications with
zero-cost abstractions"* — leads with the word
[identity.md](../../communication-strategy/identity.md) retires and must go.

**The reassurance line.** One sentence that heads off the two misreadings the tag line invites: that
"language extension" means a new language to learn, and that "pluggable" means a runtime framework.
*"Still ordinary Rust — a library on the stable toolchain, with no runtime cost, adopted one trait at a
time."* Put the install line (`cargo add cgp`) here too, because the evaluator is scanning for the
toolchain gamble and finding it immediately is worth more than the space it costs.

**The before/after code block.** This is the hook, and its content is fixed: **show the implementations
Rust rejects, then the same implementations under CGP.** Nothing else on the site says "this does
something the language cannot" as fast, and no amount of prose substitutes for the reader seeing an
`E0119` they recognize.

Four properties make the block work, and getting any of them wrong costs more than the block is worth.

**Demonstrate overlap, not the orphan rule.** These are two different failures with two different error
codes, and conflating them is the single easiest way to lose a precise reader. Two blanket impls of a
trait you own that could both match one type is `E0119`; implementing a *foreign* trait over an uncovered
type parameter is `E0210`, and it fails on its own rather than because of overlap. A "before" that writes
`impl<T: Display> serde::Serialize for T` is therefore not "legal on its own" from a downstream crate, and
labelling it `E0119` invites a correction in the first reply. **Use a trait the snippet itself defines**,
so the only error shown is the overlap and the claim is airtight.

**Keep the trait's shape the same on both sides.** The reader is comparing two versions of one program,
so any change other than the CGP machinery reads as sleight of hand. The verified candidate below stays
on rung 3 of the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) — the value stays in
`Self` — precisely so the before and after differ only by the annotations:

```rust
// Before — Rust allows only one. `String` satisfies both bounds,
// so the compiler has no principled way to choose:
pub trait CanEncode {
    fn encode(&self) -> Vec<u8>;
}

impl<T: Display> CanEncode for T { /* ... */ }
impl<T: AsRef<[u8]>> CanEncode for T { /* ... */ }   // error[E0119]
```

```rust
// After — both compile, because each implementation has its own name:
#[cgp_component(Encoder)]
pub trait CanEncode {
    fn encode(&self) -> Vec<u8>;
}

#[cgp_impl(new EncodeWithDisplay)]
impl Encoder where Self: Display { /* ... */ }

#[cgp_impl(new EncodeBytes)]
impl Encoder where Self: AsRef<[u8]> { /* ... */ }

// ...and each type says which one it uses:
delegate_components! { Uuid    { EncoderComponent: EncodeWithDisplay } }
delegate_components! { Payload { EncoderComponent: EncodeBytes } }
```

**End on wiring that shows both providers in use.** The wiring line answers the reader's immediate next
thought — "then how does the compiler know which one" — and showing *two* entries answers it better than
one, because a single entry looks like the other provider was discarded. Without this, the reader's
conclusion is that CGP has made the program ambiguous rather than that it has made the choice explicit.

**Quote the real error code.** `error[E0119]` is the detail that makes the claim checkable, and a reader
who has hit it recognizes it instantly.

Two caveats belong in the page's prose rather than in the block. Rung 3 keeps the **orphan rule** — the
`delegate_components!` entries must live in a crate owning either the trait or the type — and CGP dissolves
that too, by moving the value out of `Self` into a parameter. That is worth one sentence in the essay
below, not a second code block above the fold. And the code is **illustrative rather than runnable**:
eliding the bodies costs nothing, whereas a complete example would need three times the vertical space and
bury the contrast. Runnable code belongs in the quickstart and the tutorials.

**Two links, no more.** The quickstart or first tutorial for the reader ready to try, and the honest
status page for the reader deciding on risk. Two calls to action are the maximum, matched to the two
readers who reach this page in numbers; a third dilutes both. Do not add a third for the enthusiast —
they will find the blog.

The current page's GitHub star widget may stay; it is social proof rather than a call to action and does
not compete for the click.

## Below the fold: the bounded essay

Six sections, in this order, each answering one question and stopping. The section titles below are jobs
rather than required headings, but the order is not negotiable, because it is the order in which the
questions occur to a reader.

**1. Why Rust only lets you do this once.** Explain, sympathetically and correctly, that Rust's trait
system doubles as a dependency-injection mechanism — a generic impl can require `where T: Display`
without the caller naming it, and the compiler resolves that and everything beneath it — and that this
only works if every lookup finds the same implementation. Coherence is therefore *correct*, and the
overlap and orphan rules are what buy it. This section is where the enhances-not-replaces frame is
earned: a reader who believes the page respects Rust will follow the rest.

**2. What CGP changes.** The move, in one idea: the implementation's `Self` becomes something the
implementing crate always owns, so a provider implements *its own* named type rather than a foreign
trait, and neither rule bites. Then the other half, which matters just as much: **coherence is restored
locally**, because each context names exactly one provider, so a call site is as unambiguous as it ever
was. State it as "coherence is not repealed — it is scoped", because that sentence pre-empts the informed
objection in eight words.

**3. What that buys you.** Here the capabilities appear, as prose beats rather than cards, each two or
three sentences: many implementations chosen per context; no runtime cost, because a wired call
monomorphizes to a direct call; dependencies that are explicit and compiler-checked; and still ordinary
Rust, adopted incrementally. Draw the wording from
[message.md](../../communication-strategy/message.md#the-capabilities-worth-advertising) and keep each
beat anchored to something the reader has now seen.

**4. It goes further than trait implementations.** One short section repaying the tag line's known debt —
that "trait implementations" undersells the reach. One sentence each for abstract types a context chooses
for itself, extensible records and variants, and the composable handler family. Resist elaborating; each
of the three is a linked page's worth of material and none of it belongs here.

**5. What it costs.** The cost section is not optional and is not softened. It is more machinery than a
plain trait; for a capability with one implementation a plain trait is the right tool; the compile-time
work is real; the raw diagnostics are verbose, `cargo cgp check` leads with the root cause for the
classes it recognizes, and that tool is an early pre-release. This section is the single highest-trust
element on the page, and the register to write it in is the author's own: state the cost as part of
describing the thing accurately, not as a hedge appended to a pitch.

**6. Where to start.** The routing section, and the only place on the page with more than two links.
Match the destination to the reader per the conversion ladder in
[formats.md](../../communication-strategy/formats.md): the first tutorial for someone ready to try, the
explanation pages for someone who wants the argument in full, the status page for someone weighing
adoption, the blog for depth, and the contribute page for the enthusiast.

The five headline features from
[identity.md](../../communication-strategy/identity.md#the-headline-feature-set) may appear as a compact
strip somewhere between sections 3 and 4, if the visual design wants one. They are a scannable summary of
section 3 rather than a replacement for it, and if both exist the feature strip is the shorter of the two.

## The offload rule, and the pages it offloads to

**A section that wants a second code block, a second example, or a paragraph of mechanism has outgrown
the homepage.** When that happens, the material moves to a dedicated documentation page and the homepage
section keeps one paragraph plus a link. This is the rule that keeps the essay bounded, and it only works
if the destination pages exist — so the redesign must create them rather than discovering the need
mid-draft.

Four pages are the planned destinations, and only one of them exists today. Together they form an
**explanation** tier the docs tree currently lacks, distinct from the tutorials that teach and the
reference that specifies. **[explanation.md](explanation.md) is the guide for writing them**, and it
carries a fuller spec for each than the summaries below — read it before drafting any of the four.

- **Why CGP exists** — the long-form version of sections 1 and 2: how Rust's trait system resolves
  dependencies, why coherence is necessary, what the overlap and orphan rules cost in practice, the
  workarounds developers reach for, and the `Self`-becomes-a-parameter move with local coherence
  restored. Built from [coherence](../../cgp/concepts/coherence.md) and
  [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), with the
  [RustLab transcript](../blog/rustlab-2025-coherence.md) as the model for how to build the argument. This
  is the page the homepage links to most often and the most valuable one missing from the site.
- **How CGP works** — the mechanism for a reader who wants to see through the macros: the two generated
  traits, the wiring table, and the plain Rust an expansion produces, ending on why none of it costs
  anything at runtime. Built from the same two concepts plus
  [impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md), and the natural home for a
  [`cargo cgp expand`](../../cgp/reference/cargo-cgp.md) output.
- **When to use CGP, and when not** — the boundary as a page the homepage can point a skeptic at, taken
  from [message.md](../../communication-strategy/message.md#when-not-to-reach-for-cgp) and the
  [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md). Nothing on the site currently
  carries this, and its absence is why the cost section on the homepage has nowhere to hand off to.
- **Project status and adoption risk** — the maturity discussion the evaluator arrives looking for. This
  already exists as the "Current Status" section of the
  [Introduction page](../site-structure.md) and should become a page of its own so it can be linked
  directly from above the fold. Its frankness is a genuine asset and must not be softened when it moves;
  what should change is the stale year-stamp and the absence of any mention of
  [`cargo-cgp`](../../cargo-cgp/README.md).

The existing [Overview page](../site-structure.md) is the fifth destination and needs reconciling rather
than creating: its five features and five problems should be brought into agreement with
[identity.md](../../communication-strategy/identity.md#the-headline-feature-set) and
[message.md](../../communication-strategy/message.md#the-problems-cgp-removes), since today the site
carries three disagreeing feature lists — six on the homepage, five on the Overview, and five in the
strategy.

## What must not be on the homepage

Five things are excluded by the page's job rather than by taste, and each is a temptation with an obvious
home elsewhere.

**No teaching sequence.** No "first add this dependency, then define this trait". The moment the page
tells the reader what to type, it is competing with the tutorials and losing.

**No construct reference.** No table of macros, no attribute list, no syntax grammar. A reader who wants
to know what `#[uses]` does is past the homepage.

**No paradigm name as the hook.** "Context-generic programming" may appear once the reader understands
what CGP does — late in the essay, beside a plain descriptor — and never in the hero.

**No coherence theory above the fold.** Section 1 explains coherence because the reader has just seen an
`E0119` and wants to know why the rule exists. Opening on it, before the code that motivates it, loses
the pragmatist immediately.

**No feature the strategy retires.** In particular, "Modular Component System" and "Highly Expressive
Macros" — both currently on the page — lead with words that cost more attention than they win, and
"modular" as a lead word is
[specifically retired](../../communication-strategy/identity.md).

## Where the current page stands

The current homepage is a stock Docusaurus landing page and diverges from this guide in six concrete
ways, listed here so a redesign has a checklist rather than an impression. The **hero headline** leads
with "modular" and does not use the tag line. There is **no reassurance line and no install command**.
The **feature grid has six entries**, two of which lead with retired words, and it disagrees with the
Overview page. The **code example is the `std::Hash` illustration** — a good provocation, but it does not
show the rejected impl, so the reader never sees what Rust refuses, and it elides so much that the wiring
line carries no weight. The **problem cards are generic** ("No More Monolithic Traits", "Decouple
Dependencies") and are not anchored to anything the reader has seen. And there is **no cost section at
all**, which on a page for this audience is the most consequential omission of the six.

Two smaller notes. The closing "Ready to Get Started?" block is template filler and should become the
routing section described above. And the feature illustrations under `static/img/features/` are
LLM-generated placeholders per the [new-website post](../blog/new-website.md); they may stay, but their
captions are copy and are governed by this guide.

## Checking a draft

Run five checks, in this order.

**Read only above the fold and ask whether it stands alone** — tag line, reassurance, the contrast, two
links. If a reader stopping there could not say what CGP does, the hook has failed and nothing below
matters.

**Find the cost section.** If there isn't one, the page is overselling to the audience least tolerant of
it.

**Check the frame.** Does the page explain what Rust already does, correctly and sympathetically, before
improving on it? A draft that opens by describing coherence as a limitation rather than as a guarantee
has the frame backwards.

**Count the sections and the links.** Six sections below the fold, two links above it. A seventh section
means something needs offloading; a third hero link means one of them is not load-bearing.

**Verify every snippet** against the source and the `/cgp` skill, preferring code already verified in
[examples/](../../examples/README.md) — the serialization contrast has a worked counterpart in
[modular serialization](../../examples/modular-serialization.md).
