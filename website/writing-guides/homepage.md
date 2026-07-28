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
`E0119` they recognize. The example is settled, and it comes with copy that has to sit around it; both
are in [The example, and how to sell it](#the-example-and-how-to-sell-it) below, which is the longest
section of this guide because the block carries more of the page's weight than everything else combined.

**Two links, no more.** The **Quickstart** for the reader ready to try, and the honest
[project status page](explanation.md#project-status-and-adoption-risk) for the reader deciding on risk.
Two calls to action are the maximum, matched to the two readers who reach this page in numbers; a third
dilutes both. Do not add a third for the enthusiast — they will find the blog. The Quickstart is a page
the redesign creates — install and one working program, no concepts — and it is deliberately smaller than
the [Hello World tutorial](../tutorials/hello-world.md), which teaches an idea. Until it exists, this link
points at Hello World.

The current page's GitHub star widget may stay; it is social proof rather than a call to action and does
not compete for the click.

## The example, and how to sell it

The example is settled: **a trait the snippet defines, implemented twice over two ordinary Rust bounds
that overlap, then wired per type.** The concrete pair is `Display` and `AsRef<[u8]>` on a `CanEncode`
trait, and the whole of it — both blocks, the caption, and the sentences that must sit around them — is
below. It is the highest-leverage twenty lines on the site: two-thirds of the readers who ever see the
homepage see this block and nothing beneath it, so it has to carry the pitch, the proof, and the
pre-emption of the first objection on its own.

### The code

Two blocks in sequence, the first labelled as what Rust refuses and the second as the same program under
CGP. This is the verified form: the first block fails with exactly the error it claims, and the second
compiles and runs against `cgp` `0.8.0-alpha` once the two imports (`core::fmt::Display` and
`cgp::prelude::*`) are added back.

```rust
// Rust allows only one of these. `String` is both `Display` and
// `AsRef<[u8]>`, so the compiler has no principled way to choose.
pub trait CanEncode {
    fn encode(&self) -> Vec<u8>;
}

impl<T: Display> CanEncode for T {
    fn encode(&self) -> Vec<u8> { self.to_string().into_bytes() }
}

impl<T: AsRef<[u8]>> CanEncode for T {          // error[E0119]
    fn encode(&self) -> Vec<u8> { self.as_ref().to_vec() }
}
```

```rust
#[cgp_component(Encoder)]
pub trait CanEncode {
    fn encode(&self) -> Vec<u8>;
}

#[cgp_impl(new EncodeAsText)]
#[uses(Display)]
impl Encoder {
    fn encode(&self) -> Vec<u8> { self.to_string().into_bytes() }
}

#[cgp_impl(new EncodeAsBytes)]
#[uses(AsRef<[u8]>)]
impl Encoder {
    fn encode(&self) -> Vec<u8> { self.as_ref().to_vec() }
}

// Both compile. Each type names the implementation it uses:
delegate_components! { u64     { EncoderComponent: EncodeAsText } }
delegate_components! { String  { EncoderComponent: EncodeAsText } }
delegate_components! { Vec<u8> { EncoderComponent: EncodeAsBytes } }
```

### The copy that sells it

**The block does not work without its caption, and the caption is two sentences.** The first names what
changed, the second pre-empts the informed objection:

> Both implementations compile, because each one now has a name — and each type names the one it uses, so
> a call to `encode()` is as unambiguous as it ever was. Coherence is not repealed; it is scoped.

That is the whole sell above the fold. Everything else a writer wants to add here — why coherence exists,
what the wiring table is, what it costs at runtime — belongs to the essay below or to
[*Why CGP exists*](explanation.md#why-cgp-exists), and adding it here is the most common way this block
gets ruined.

Three properties of the *copy* matter as much as the code. **Label the first block as a refusal, not as a
mistake** — the reader must feel that the program is reasonable and the language is saying no, because
that is the feeling the whole page converts. **Say `String` out loud in the comment**, since naming the
witness is what turns "impls might overlap" into a fact the reader checks in their head in one second.
And **quote `error[E0119]` verbatim**, because it is the detail that makes the claim checkable and a
reader who has hit it recognizes it instantly.

### Why this example and not another

**The overlap is visceral and needs no domain.** Every Rust programmer knows `String` is both `Display`
and `AsRef<[u8]>`, so the conflict is self-evident from bounds the reader already holds — no invented
domain types, no crate to introduce, nothing to take on trust. An example built on a plausible business
trait would spend half its lines establishing the setup before the conflict could even be seen.

**The reader has wanted this.** "Encode anything printable one way and anything byte-like another" is a
thing developers try and are refused, and the escape they reach for — a newtype per case, or a marker
struct plus a helper trait — is
[independently reinvented and blogged](../../communication-strategy/evidence.md). The block's real job is
recognition, so the CGP version arrives as relief from a workaround the reader has written rather than as
a capability they must be talked into wanting.

**The bodies are shown rather than elided, and they are identical on both sides.** One line each costs
almost nothing and buys the block's central proof: the *only* difference between the two programs is the
annotations and the wiring, so CGP moved the choice and not the code. A `/* ... */` here would leave the
reader wondering what was quietly changed inside, which is exactly the suspicion the block exists to
remove.

**The trait's shape is unchanged across the pair.** The example stays on rung 3 of the
[modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) — the encoded value stays in `Self` —
so the before and after differ only by the machinery. Any change beyond that reads as sleight of hand to
a reader comparing two versions of one program, and above the fold there is no room to narrate one.

**Three wiring lines, not two.** Two entries prove the first provider was not simply discarded; the third
does two further jobs. One provider serving both `u64` and `String` shows that a provider is reusable
logic rather than a renamed per-type impl, which forecloses "I could have written two ordinary impls".
And wiring `String` — the very type whose ambiguity caused the error — closes the loop the first block
opened, answering "so which one does `String` get?" with "the one you name."

**The bounds move into `#[uses]`, and that is a second small win.** `#[uses(Display)]` and
`#[uses(AsRef<[u8]>)]` are what the [guides](../../cgp/guides/declaring-dependencies.md) prescribe, and
they apply to ordinary Rust traits exactly as they do to CGP capabilities — which the block quietly
demonstrates, since a reader who assumed the attribute was CGP-only machinery sees it carrying `Display`.
Parity survives the move because the bound stays in the reader's eye-line, one line above the impl,
naming the same trait they just read in `impl<T: Display>`. Do not rewrite it back to
`where Self: Display`: the shorter form is the idiom, and the point that the attribute is not
CGP-specific is worth a line of the page's most valuable space.

**It is a fragment rather than a program.** The imports are omitted and no `main` or call site is shown,
because a complete example would need half again the vertical space and bury the contrast. That is a
presentation choice rather than a licence to be approximate — the fragment still has to compile once the
imports are restored. A program the reader runs belongs in the Hello World tutorial.

### Which shape it is, and why that matters here

**The block is the retrofit shape**: a value context — `String` and `u64` are the data being encoded —
with the capability targeting `Self`. Say so in the meta record even though the page never uses the
terms, because it is the **least representative of CGP's three shapes** and a writer needs to know that
deliberately. Most CGP code is the *application* shape, where `Self` is a type you define and the
capability is about the application; and the fully modular shape moves the target into a parameter. The
vocabulary is in
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target) and the
technical account in the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md).

The retrofit shape is kept above the fold anyway, and the trade is worth stating so it is not reopened
every redesign. It buys the two things nothing else buys in twenty lines: the before and after differ by
nothing but the annotations, and the failure is a real `E0119` the reader recognizes. It costs
representativeness, and it costs two transitions that the essay below must then carry.

**Do not use the word "context" anywhere in the hero.** At the retrofit shape the context and the target
are the same type, so calling `String` a context — while true — contradicts the gloss every other page
gives, and a reader who meets that contradiction concludes they have misunderstood something. "Each type
names the implementation it uses" says everything the block needs.

### What it deliberately does not show

Three things are missing from the block, each on purpose, and each has a named place where it is repaid.
Naming them here is what stops a well-meaning revision from cramming one in.

**Two applications choosing differently for the same type.** At the retrofit shape the wired type *is* the
context, so `String` commits to one provider globally and the block shows per-*type* choice rather than
per-*application* choice. That is repaid in essay section 2 and in full by
[*Why CGP exists*](explanation.md#why-cgp-exists). **Do not try to put the fully modular shape above the
fold**: it changes the trait to `CanEncodeValue<Value>`, which is precisely the shape change the parity
rule forbids, and it adds `open` and `@`-path wiring syntax the reader has no grounding for. The
[launch-post model draft](../../communication-strategy/formats.md) does run at that shape and is right to,
because a post has the paragraph of narration this block does not.

**The orphan rule dissolved.** The block quietly wires three types the snippet does not own, which is
legal because the snippet owns the trait — and that is exactly the limit of rung 3: the wiring must live
in a crate owning either the trait or the type. CGP dissolves that too, by moving the value out of `Self`,
and that is one sentence in the essay rather than a second code block.

**Everything past trait implementations.** No abstract types, no extensible data, no handlers, no
dependency injection. Section 4 of the essay repays the tag line's breadth debt in one sentence each; the
block stays on the one thing it can prove in twenty lines.

### Replacing it

The example is settled, not sacred, but a replacement has to keep six properties, and a candidate failing
any one of them is worse than what it replaces.

The trait is **defined in the snippet**, so the failure shown is unambiguously the overlap rule. This is
the property most easily lost: `impl<T: Display> serde::Serialize for T` is an *orphan-rule* failure
(`E0210`) that fails on its own rather than because of overlap, so a "before" written against a foreign
trait and labelled `E0119` invites a correction in the first reply. The two bounds **overlap on a type
the reader can name without being told**. The **trait's shape is identical** across the pair. The
**bodies are identical** across the pair, and short enough to show. The wiring shows **at least two
providers with at least one of them used twice**. And the **real error code** appears verbatim.

A replacement must be compiled before it ships, not eyeballed — the current one was, together with a
`check_components!` assertion per wired type, which is how the wiring is confirmed to resolve rather than
merely parse.

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
locally**, because each wired type names exactly one provider, so a call site is as unambiguous as it ever
was. State it as "coherence is not repealed — it is scoped", because that sentence pre-empts the informed
objection in eight words.

**This section is also where the page crosses from the retrofit shape to the application shape, and it
must say so.** Everything above it wires the *data*; every other page on the site wires an *application*,
and nothing in a signature marks the change — no parameter appears, so a reader simply notices at some
point that they no longer know what is being wired. One sentence closes it: *"so far the wired type has
been the data, which gets one choice for the whole program; the move that makes the choice yours is to
wire a type you define to stand for your application — and because it is yours, you can define as many as
you like."* That sentence is also the first legitimate use of the word **context** on the page, and it
should be introduced there rather than earlier, because this is the point at which it means something the
reader can check. The two transitions and the reasoning behind them are specified in
[explanation.md](explanation.md).

**3. What that buys you.** Here the capabilities appear, as prose beats rather than cards, each two or
three sentences: many implementations chosen per application; no runtime cost, because a wired call
monomorphizes to a direct call; dependencies that are explicit and compiler-checked; and still ordinary
Rust, adopted incrementally. Prefer "per application" to "per context" throughout this section — it is
concrete, it needs no vocabulary, and it is true of the shape section 2 has just introduced. Draw the
wording from
[message.md](../../communication-strategy/message.md#the-capabilities-worth-advertising) and keep each
beat anchored to something the reader has now seen.

**4. It goes further than trait implementations.** One short section repaying the tag line's known debt —
that "trait implementations" undersells the reach. One sentence each for abstract types a context chooses
for itself, extensible records and variants, and the composable handler family. Resist elaborating; each
of the three is a linked page's worth of material and none of it belongs here.

The abstract-types sentence should carry the **payoff and not only the mechanism**, matching the
[breadth line](../../communication-strategy/identity.md#the-pitch-that-follows-the-line) it compresses: a
type the application chooses means an error type or a runtime *stops being a parameter every layer has to
carry*. "A context chooses it for itself" describes the construct and lands on a reader who already wants
a type swappable; the parameter clause names what it removes and lands on a reader whose signatures have
filled up, which is the larger group and the one this section is otherwise silent for. One clause is
enough — the [Overview](../site-structure.md) is where the argument is made in full, and the pain behind
it is an entry in [message.md](../../communication-strategy/message.md#the-problems-cgp-removes) for a
piece that has room to show a before and after.

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

Five pages are the destinations, and two of them exist today in some form. Together they form an
**explanation** tier the docs tree currently lacks, distinct from the tutorials that teach and the
reference that specifies. **[explanation.md](explanation.md) is the guide for writing them**, and it
carries a fuller spec for the first four than the summaries below — read it before drafting any of them.

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
- **Overview** — the fifth destination, and the one that already exists. It is the **feature tour**: every
  high-level CGP capability walked through in more detail than any other surface carries, which makes it
  the destination for both section 3 and section 4 of the essay. That job resolves the site's three
  disagreeing feature lists rather than merely reconciling them: the front page carries the curated five
  from [identity.md](../../communication-strategy/identity.md#the-headline-feature-set) as prose beats,
  and the Overview expands each one and adds the breadth capabilities the tag line only gestures at, so
  it is not competing with the front page's list and is not capped at five. Its problems half stays
  anchored to [message.md](../../communication-strategy/message.md#the-problems-cgp-removes).

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
[examples/](../../examples/README.md). For the hero block specifically, compile it rather than reading it:
its nearest counterparts are rung 3 of the
[modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) and the
[modular serialization](../../examples/modular-serialization.md) example, and the six properties a
replacement must keep are in [Replacing it](#replacing-it).
