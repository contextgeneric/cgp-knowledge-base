# Writing the homepage

The CGP homepage has one job: **make the idea click, and make the reader want it**, leaving them able
to say what CGP does and why it might matter to them, then routed to the page that teaches it. It is not
a tutorial, not a reference, and not a feature catalogue, and this guide's central discipline is keeping
it from becoming any of those.

- **URL**: <https://contextgeneric.dev/>
- **Source**: [src/pages/index.tsx](https://github.com/contextgeneric/contextgeneric.dev/blob/main/src/pages/index.tsx)
  and [src/components/HomepageFeatures/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/src/components/HomepageFeatures)
- **Voice**: project voice throughout, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md), in natural-writing's
  natural style: each sentence picks up from the last, and the essay reads as one argument
- **Governed by**: [identity.md](../../communication-strategy/identity.md) for the line, the frame, and
  the features; [message.md](../../communication-strategy/message.md) for the pains and strengths;
  [readers.md](../../communication-strategy/readers.md) for who is reading
- **Reading**: the shared set and [the front page's row](README.md#the-front-page-and-the-overview)
  of the reading map

## What the page is for, stated precisely

The homepage's success condition is **comprehension that converts**, not conversion alone. A reader who
leaves able to explain CGP to a colleague ("it lets one trait have several implementations and each type
picks one, resolved at compile time") has been served even if they do not click anything, because that
reader is the one who comes back and the one who repeats the description accurately. A reader who clicks
through excited but unable to say what CGP does will bounce off the first tutorial, and will describe CGP
wrongly in the meantime.

Two consequences follow, and they set this page apart from a conventional developer landing page. The
page must **actually explain something**, which means prose and code rather than a grid of adjectives.
And it must **not try to teach**, because the tutorials do that better and a homepage that starts
teaching becomes a bad tutorial. The line between the two is that explaining answers "what is this and
why", while teaching answers "how do I do it", and the moment the page starts telling the reader what to
type, it has crossed over.

The page also carries the selling points, so comprehension is not its only output. The difference from a
feature grid is that **each strength is tied to what the reader has just seen**: the reader has seen
what CGP does, so "provider selection resolves at compile time into a direct call" lands as an answer
to a question they now have rather than as a claim they have no way to evaluate.

The essay starts with the ambiguity for `String`, then explains why trait lookup needs coherence.
It introduces providers through the encoder names readers have just seen before explaining how each
application selects one. Its routing cards use complete action sentences so readers can follow the
path from trying CGP to understanding it or evaluating adoption.

## The two tiers

The page is built in two tiers with a hard boundary between them, because it serves two readers who share
no patience budget.

**Above the fold is a single screen that must stand entirely alone.** Most of the attention this page
ever gets lands here: Nielsen Norman Group's
[eyetracking research](https://www.nngroup.com/articles/scrolling-and-attention/) puts 57% of viewing
time above the fold and 74% within the first two screenfuls, so this screen has to deliver the whole
pitch: the project's name and the tag line, one reassurance line, one piece of code that shows the
novelty, and two links. Nothing above the fold may depend on anything below it.

**Below the fold is a bounded essay** for the reader who kept scrolling, the one who is interested
enough to want the argument. It runs the idea from the constraint to the payoff to the cost, in a fixed
number of sections, and it hands off to dedicated pages the moment a section wants to go deeper. Its
length is capped by structure rather than by willpower, which is what the offload rule below is for.

## Above the fold

Four elements, in this order, and nothing else. The compiler's error quoted under the rejected block
belongs to the code element rather than adding a fifth.

**The project's name, then the tag line, verbatim.** The hero names the project in text as
**Context-Generic Programming**, so a reader and a search engine can read it rather than only see it
in the logo image, and the tag line beneath it is the plain description the
[naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page) asks
the name to stand beside: *"A language extension for Rust, with pluggable trait implementations at
compile-time."* The front page presents the project, so it states the line whole, and the line is
not paraphrased, reworded for the hero, or replaced by something snappier. A headline in its place,
such as one that leads with "modular", uses the word
[identity.md](../../communication-strategy/identity.md) retires.

**The reassurance line.** One sentence that heads off the two misreadings the tag line invites: that
"language extension" means a new language to learn, and that "pluggable" means a runtime framework.
*"Still ordinary Rust: a library on the stable toolchain, with provider selection resolved at compile
time, adopted one trait at a time."*, verbatim from
[identity.md](../../communication-strategy/identity.md#the-pitch-that-follows-the-line). Put the install line (`cargo add cgp`) here too, because the evaluator is scanning for the
toolchain gamble and finding it immediately is worth more than the space it costs.

**The before/after code block.** This is the hook, and its content is fixed: **show the implementations
Rust rejects, then the same implementations under CGP.** Nothing else on the site says "this does
something the language cannot" as fast, and no amount of prose substitutes for the reader seeing an
`E0119` they recognize. The example is settled, and it comes with copy that has to sit around it; both
are in [The example, and how to sell it](#the-example-and-how-to-sell-it) below, which is the longest
section of this guide because the block carries more of the page's weight than everything else combined.

**Two links, no more.** The **Quickstart** for the reader ready to try, and a link down to the
page's own **cost section** for the reader deciding on risk, since that section is where the site
states the project's maturity.
Two calls to action are the maximum, matched to the two readers who reach this page in numbers; a third
dilutes both. Do not add a third for the enthusiast, who will find the blog. The Quickstart is install
and one working program with no concepts, and it is deliberately smaller than the
[Hello World tutorial](../tutorials/hello-world.md), which teaches an idea.

The GitHub star widget may stay; it is social proof rather than a call to action and does not compete
for the click.

**The layout puts the code in the first screen.** The hero copy (the name, the tag line, the
reassurance line, the install line, and the two links) sits on the left, with the hero illustration
on the right at about 280 px and modest vertical padding. Between the phone layout and 1240 px, where
the code blocks stack, the art shrinks to about 200 px and the title steps down, so the title keeps
one line and the first block still starts high on the screen. The two code blocks follow directly in a
band of their own, side by side, so a reader compares them line by line, with the caption under
them. The target is the whole first screen at 1920×1080, the caption's quote included, so that screen
ends on the page's conclusion, and the tops of both blocks at 1440×900, which is enough to see the
contrast; measure both with a screenshot rather than estimating. On a phone the blocks stack and only
the hero copy fits the first screen, which is acceptable because the copy stands alone. Do not shrink
the hero art to a small logo to save height, and do not put the blocks in tabs, which hide the
comparison they exist to show.

**Each block is set as an editor window that states its verdict.** The title bar carries a cross or a
tick beside the label ("Rust accepts only one of these", "With CGP, both compile"), and the changed
lines read like a diff, with a tint and a gutter mark in the window's own red or green, so the two
windows differ for a reader who cannot tell red from green. The rejected window numbers its lines
and quotes rustc's `E0119` beneath the block, without the location line, so the error names lines 7
and 11 as the page numbers them. The windows' lines run to about 70 characters, so side by side they
need about 1240 px: below 1360 px the code sets a little smaller, and below 1240 px the windows
stack, so neither scrolls sideways. Check those widths in Firefox, which shows the scrollbars that
Chrome's headless captures hide.

## The example, and how to sell it

The example is settled: **a trait the snippet defines, implemented twice over two ordinary Rust bounds
that overlap, then wired per type.** The concrete pair is `Display` and `AsRef<[u8]>` on a `CanEncode`
trait, and the whole of it (both blocks, the caption, and the sentences that must sit around them) is
below. It is the highest-leverage twenty lines on the site: most of the attention the homepage ever
gets falls on this block, per the research cited above, so it has to carry the pitch, the proof, and
the pre-emption of the first objection on its own.

### The code

Two blocks side by side, the first labelled as what Rust refuses and the second as the same program
under CGP. This is the verified form: the first block fails with exactly the error it claims, and the second
compiles and runs against `cgp` `0.8.0` once the two imports (`core::fmt::Display` and
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
#[cgp_component(Encoder)]     // generates the provider trait Encoder
pub trait CanEncode {
    fn encode(&self) -> Vec<u8>;
}

#[cgp_impl(new EncodeAsText)] // a provider: one named implementation
#[uses(Display)]
impl Encoder {
    fn encode(&self) -> Vec<u8> { self.to_string().into_bytes() }
}

#[cgp_impl(new EncodeAsBytes)]
#[uses(AsRef<[u8]>)]
impl Encoder {
    fn encode(&self) -> Vec<u8> { self.as_ref().to_vec() }
}

// Each type names the implementation it uses:
delegate_components! { u64     { EncoderComponent: EncodeAsText } }
delegate_components! { String  { EncoderComponent: EncodeAsText } }
delegate_components! { Vec<u8> { EncoderComponent: EncodeAsBytes } }
```

### The copy that sells it

**The block does not work without its caption, and the caption is two sentences.** The first names what
changed, the second pre-empts the informed objection:

> Both implementations compile, because each one now has a name, and each type names the one it uses, so
> a call to `encode()` is as unambiguous as it ever was. Coherence is not repealed; it is scoped.

That is the whole sell above the fold. Everything else a writer wants to add here (why coherence exists,
what the wiring table is, what it costs at runtime) belongs to the essay below or to
[*Why CGP exists*](explanation.md#why-cgp-exists), and adding it here is the most common way this block
gets ruined.

Three properties of the *copy* matter as much as the code. **Label the first block as a refusal, not as a
mistake**: the reader must feel that the program is reasonable and the language is saying no, because
that is the feeling the whole page converts. **Say `String` out loud in the comment**, since naming the
witness is what turns "impls might overlap" into a fact the reader checks in their head in one second.
And **quote `error[E0119]` verbatim**, because it is the detail that makes the claim checkable and a
reader who has hit it recognizes it instantly.

### Why this example and not another

**The overlap is visceral and needs no domain.** Every Rust programmer knows `String` is both `Display`
and `AsRef<[u8]>`, so the conflict is self-evident from bounds the reader already holds, with no invented
domain types, no crate to introduce, nothing to take on trust. An example built on a plausible business
trait would spend half its lines establishing the setup before the conflict could even be seen.

**The reader has wanted this.** "Encode anything printable one way and anything byte-like another" is a
thing developers try and are refused, and the escape they reach for (a newtype per case, or a marker
struct plus a helper trait) is
[independently reinvented and blogged](../../communication-strategy/evidence.md). The block's real job is
recognition, so the CGP version arrives as relief from a workaround the reader has written rather than as
a feature they must be talked into wanting.

**The bodies are shown rather than elided, and they are identical on both sides.** One line each costs
almost nothing and buys the block's central proof: the *only* difference between the two programs is the
annotations and the wiring, so CGP moved the choice and not the code. A `/* ... */` here would leave the
reader wondering what was quietly changed inside, which is exactly the suspicion the block exists to
remove.

**The trait's shape is unchanged across the pair.** The example stays on tier 3 of the
[modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md), where the encoded value stays in `Self`,
so the before and after differ only by the machinery. Any change beyond that reads as sleight of hand to
a reader comparing two versions of one program, and above the fold there is no room to narrate one.

**Three wiring lines, not two.** Two entries prove the first provider was not simply discarded; the third
does two further jobs. One provider serving both `u64` and `String` shows that a provider is reusable
logic rather than a renamed per-type impl, which forecloses "I could have written two ordinary impls".
And wiring `String`, the very type whose ambiguity caused the error, closes the loop the first block
opened, answering "so which one does `String` get?" with "the one you name."

**The bounds move into `#[uses]`, and that is a second small win.** `#[uses(Display)]` and
`#[uses(AsRef<[u8]>)]` are what the [guides](../../cgp/guides/declaring-dependencies.md) prescribe, and
they apply to ordinary Rust traits exactly as they do to CGP traits, which the block quietly
demonstrates, since a reader who assumed the attribute was CGP-only machinery sees it carrying `Display`.
Parity survives the move because the bound stays in the reader's eye-line, one line above the impl,
naming the same trait they just read in `impl<T: Display>`. Do not rewrite it back to
`where Self: Display`: the shorter form is the idiom, and the point that the attribute is not
CGP-specific is worth a line of the page's most valuable space.

**It is a fragment rather than a program.** The imports are omitted and no `main` or call site is shown,
because a complete example would need half again the vertical space and bury the contrast. That is a
presentation choice rather than a licence to be approximate: the fragment still has to compile once the
imports are restored. A program the reader runs belongs in the Hello World tutorial.

### Which shape it is, and why that matters here

**The block is the retrofit shape**, a value context (`String` and `u64` are the data being encoded)
with the component targeting `Self`. Say so in the meta record even though the page never uses the
terms, because it is the **least representative of CGP's three shapes** and a writer needs to know that
deliberately. Most CGP code is the *application* shape, where `Self` is a type you define and the
operation is about the application; and the fully modular shape moves the target into a parameter. The
vocabulary is in
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target) and the
technical account in the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md).

The retrofit shape is kept above the fold anyway, and the trade is worth stating so it is not reopened
every redesign. It buys the two things nothing else buys in twenty lines: the before and after differ by
nothing but the annotations, and the failure is a real `E0119` the reader recognizes. It costs
representativeness, and it costs two transitions that the essay below must then carry.

**The site pays that cost back by teaching the application shape second.** Because the hero is a value
context and so is the Hello World tutorial, a reader's first two contacts both show the shape least CGP
code is in, so the surfaces immediately downstream are where the common shape has to arrive. On the
explanation path that is the end of essay section 1, which introduces a context in prose, and
[*How CGP works*](explanation.md#how-cgp-works), where the `App`/`TestApp` example shows one in code;
on the teaching path it is the applied tutorial, which is placed second in the tutorial order for this
reason and is naturally environmental. Keeping the hero as it is depends on those two doing their
job, so a change to either is a change to this trade.

**Do not use the word "context" anywhere in the hero**, apart from the project's name above the tag
line, which is a name rather than the term. At the retrofit shape the context and the target are the
same type, so calling `String` a context, while true, contradicts the gloss every other page gives,
and a reader who meets that contradiction concludes they have misunderstood something. "Each type
names the implementation it uses" says everything the block needs.

### What it deliberately does not show

Three things are missing from the block, each on purpose, and each has a named place where it is repaid.
Naming them here is what stops a well-meaning revision from cramming one in.

**Two applications choosing differently for the same type.** At the retrofit shape the wired type *is* the
context, so `String` commits to one provider globally and the block shows per-*type* choice rather than
per-*application* choice. That is repaid in full by
[*Modularity Hierarchy*](explanation.md#when-to-use-cgp-and-when-not). **Do not try to put the fully
modular shape above the fold**: it changes the trait to `CanEncodeValue<Value>`, which is precisely the shape change the parity
rule forbids, and it adds `open` and `@`-path wiring syntax the reader has no grounding for. The
[launch-post model draft](../../communication-strategy/formats.md) does run at that shape and is right to,
because a post has the paragraph of narration this block does not.

**The orphan rule dissolved.** The block quietly wires three types the snippet does not own, which is
legal because the snippet owns the trait. That is exactly the limit of tier 3: the wiring must live
in a crate owning either the trait or the type. CGP dissolves that too, by moving the value out of `Self`,
and that is one sentence in the essay rather than a second code block.

**Everything past trait implementations.** No abstract types, no extensible data, no handlers, no
dependency injection. Section 3 of the essay repays the tag line's breadth debt in one sentence each; the
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

A replacement must be compiled before it ships, not eyeballed. The website's `example-code` crate
compiles the block in `tests/front_page.rs`, with a `check_components!` assertion per wired type, which
is how the wiring is confirmed to resolve rather than merely parse, and holds the rejected block as a
compile-fail fixture whose snapshot shows the `E0119`. The page's code lives as strings in
`src/pages/index.tsx`, which no compiler reads, so the same test file reads `index.tsx`, takes each
block from between its marker comments, and fails when it differs from the compiled text. The
rejected block starts at its fixture's first line, so the quoted `E0119` names the lines the page
numbers, and another test compares the quote with the fixture's snapshot, without its location
line; a re-blessed snapshot therefore changes the quote too. Change the page and the test in the
same commit.

## Below the fold: the bounded essay

Five sections, in this order, each answering one question and stopping. The section titles below are
jobs rather than required headings, but the order is not negotiable, because it is the order in which
the questions occur to a reader.

**Each section takes the layout that fits its content, and the bands alternate between the page and
a tint.** The hero is tinted and the code band is not; then sections 1, 3, and 5 take the tint and
sections 2 and 4 the page, so every section meets a change of background and no gap needs a rule.
Section 1 sets its title in a narrow column beside its prose, section 2 sets the feature cards two
to a row, section 3 sets three linked tiles, section 4 sets the costs in a framed panel, and
section 5 sets one card per reader, the whole card linking its main page beside a reason. Above
996 px, section 1's title and section 4's heading and lead stay in view beside their longer columns
while a reader scrolls; on a phone they stack above them. The gaps come from a spacing scale in the
page's stylesheet, so a later change keeps the rhythm.

**1. Why Rust only lets you do this once, and what CGP changes.** Explain, sympathetically and
correctly, that Rust's trait system doubles as a dependency-injection mechanism (a generic impl can
require `where T: Display` without the caller naming it, and the compiler resolves that and everything
beneath it), and that this only works if every lookup finds the same implementation. Coherence is
therefore *correct*, and the overlap and orphan rules are what buy it. This section is where the
enhances-not-replaces frame is earned: a reader who believes the page respects Rust will follow the
rest. Name the workaround a reader reaches for without CGP, a newtype per case or a marker struct and a
helper trait, and link *Bypassing coherence*.

The section then states the move, in one idea: the implementation's `Self` becomes something the
implementing crate always owns, so a provider implements *its own* named type rather than a foreign
trait, and neither rule bites. Then the other half, which matters just as much: **coherence is
restored locally**, because each wired type names exactly one provider, so a call site is as
unambiguous as it ever was. The code band's caption already states this as "coherence is not
repealed; it is scoped", so the section explains the sentence rather than repeating it.

**The section ends where the page crosses from the retrofit shape to the application shape, and it
must say so.** Everything above it wires the *data*; every other page on the site wires an
*application*, and nothing in a signature marks the change: no parameter appears, so a reader simply
notices at some point that they no longer know what is being wired. One sentence closes it: *"so far
the wired type has been the data, which gets one choice for the whole program; the move that makes the
choice yours is to wire a type you define to stand for your application, and because it is yours, you
can define as many as you like."* That sentence is also the first legitimate use of the word
**context** on the page, and it should be introduced there rather than earlier, because this is the
point at which it means something the reader can check. The two transitions and the reasoning behind
them are specified in
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target) and the
[comprehension barrier](../../communication-strategy/readers.md).

**The page names a context without showing one in code.** [readers.md](../../communication-strategy/readers.md)
asks a writer to explain an application context by showing what it selects and stores, and the front
page departs from that on purpose: the section's last sentence links
[*Consumer and provider traits*](explanation.md#how-cgp-works), which shows an application and its test
wiring different providers, and the page keeps the hero's block as its only code. A second example
would add a domain the reader must learn, and a realistic one does not fit the two lines the page could
spare. Weigh both before putting a second example on the page.

**2. What that buys you.** Here the strengths appear as the first four headline features, one illustrated
card each, so the page states them once rather than as prose beats followed by a row of cards that
repeats them. Each card has the feature's title, one or two sentences anchored to something the
reader has now seen, and its illustration, and the whole card links to the page that answers it; a
line under the cards links the Overview, the section's destination. The cards sit two to a row, each
illustration beside its text, so two sentences stay readable at the page's width and the four cards
make an even grid. Prefer "per application" to "per context" throughout this
section: it is concrete, it needs no vocabulary, and it is true of the shape
section 1 has just introduced. A card that points back at the hero's block says "each type", because
the hero wires types rather than applications. Draw the wording from
[message.md](../../communication-strategy/message.md#the-strengths-worth-advertising), and keep three
of its rules: Type-Safe Wiring names `check_components!` or a use of the component, because a wiring
entry alone does not check a provider's needs; Abstract Over Every Dependency carries portability,
while section 3's abstract-types sentence keeps the signature payoff; and the feature titles stay
verbatim.

**3. It goes further than trait implementations.** One short section repaying the tag line's known debt,
that "trait implementations" undersells the reach. One sentence each for abstract types a context chooses
for itself, extensible records and variants, and the composable handler family. Resist elaborating; each
of the three is a linked page's worth of material and none of it belongs here.

The abstract-types sentence should carry the **payoff and not only the mechanism**, matching the
[breadth line](../../communication-strategy/identity.md#the-pitch-that-follows-the-line) it
compresses: a type the application chooses means an error type or a runtime *stops being a parameter
every layer has to carry*. "A context chooses it for itself" describes the construct and lands on a
reader who already wants a type swappable; the parameter clause names what it removes and lands on a
reader whose signatures have filled up, which is the larger group and the one this section is
otherwise silent for. One clause is enough: the [Overview](../site-structure.md) repeats it in its
breadth list, the *Abstract types* Concepts page explains the mechanism, and the pain behind it is
an entry in [message.md](../../communication-strategy/message.md#the-problems-cgp-removes) for a
piece that has room to show a before and after.

**4. What it costs.** The cost section is not optional and is not softened. It is more machinery than a
plain trait; for a trait with one implementation a plain trait is the right tool; the compile-time
work is real; the raw diagnostics are verbose, `cargo cgp check` leads with the root cause for the
classes it recognizes, and the tool does not yet reshape every class. This section is the single highest-trust
element on the page, and the register to write it in is the author's own: state the cost as part of
describing the thing accurately, not as a hedge appended to a pitch.

**Set the costs as labelled statements in two columns.** An evaluator scans this section, so each
cost is a short label in a column of its own beside one sentence, with a rule between rows, after one
sentence that says a plain trait is the right tool for a single implementation: more declarations,
compile-time work, verbose raw errors with the `cargo cgp check` qualification word for word, a young
ecosystem, and learning time with the agent skill beside it. The rows form a description list rather
than a table, because each pairs one label with one statement, and on a phone each label sits above
its sentence. The section's heading and its lead sit in a column beside the rows, and the advice to
try CGP on a small part of a project follows the list.

**It is also the one place on the site that states the project's maturity**, so it carries what an
evaluator reads for. CGP is young: its ecosystem is small and community support is limited, so an
adopter of a mission-critical project should expect to investigate some problems alone. Learning its
patterns takes time, and its raw errors can be hard to read; `cargo-cgp`, which helps with them, is
itself an early release. Code an assistant writes still needs the reader's review. And the way to
try it is on a small part of a project whose implementation choices already vary. Keep that
frankness rather than softening it into marketing, because it does more persuasive work for the
evaluator than any claim on the page.

This is also **the only place on the page where agent support may be mentioned**, and one clause is the
budget. Three of the costs just named (the learning curve, the diagnostics, and the volume of wiring)
are mechanical work over a written-down vocabulary, and CGP publishes an agent skill that reduces all
three for a reader who works with an assistant. Say it as a smaller cost rather than a solved one, in
the same breath as the cost itself, and link the skill rather than elaborating. It must not appear in
the hero, the reassurance line, the feature cards, or a feature title: a landing page that leads on
AI in 2026 is read as chasing attention by exactly the audience this page is written for. The full
rule is in
[message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these) and
the wording to avoid in
[vocabulary.md](../../communication-strategy/vocabulary.md#words-and-framings-to-avoid).

**5. Where to start.** The routing section, and the only place on the page with more than two links.
Match the destination to the reader per the conversion ladder in
[formats.md](../../communication-strategy/formats.md): the Quickstart and then the first tutorial for
someone ready to try, the explanation pages for someone who wants the argument in full,
*Modularity Hierarchy* and the Projects pages for someone weighing adoption, since an evaluator looks
for a real system using CGP, the Overview, the comparisons, and the blog for depth, and the contribute
page for the enthusiast.

**The first four headline features from
[identity.md](../../communication-strategy/identity.md#the-headline-feature-set) are section 2's
cards**, in identity.md's order. The fifth, *Still Ordinary Rust*, gets no card, because the
reassurance line above the fold states it verbatim and a card would repeat it. The links follow the
feature-to-page table in
[seo.md](../seo.md#the-tag-line-orients-the-reader-the-features-carry-the-searchable-words):

| Feature | Links to | Illustration |
| --- | --- | --- |
| One Interface, Many Implementations | *Bypassing coherence* | `one-interface-many-implementations` |
| Zero-Cost Abstraction | the dynamic-dispatch comparison | `zero-cost-abstraction` |
| Type-Safe Wiring | the dependency-injection comparison | `type-safe-wiring` |
| Abstract Over Every Dependency | *Modular error handling* | `abstract-over-every-dependency` |

The illustrations are covered in [Images, metadata, and provenance](#images-metadata-and-provenance) below.

## The offload rule, and the pages it offloads to

**A section that wants a second code block, a second example, or a paragraph of mechanism has outgrown
the homepage.** When that happens, the material moves to a dedicated documentation page and the homepage
section keeps one paragraph plus a link. This is the rule that keeps the essay bounded, and it only works
if the destination pages exist, so the redesign must create them rather than discovering the need
mid-draft.

Four pages are the destinations. Three are pages of the site's **explanation** tier, the Concepts
section, distinct from the tutorials that teach and the reference that specifies, and the fourth is
the Overview. **[explanation.md](explanation.md) is the guide for the first three**, and it carries a
fuller spec for each than the summaries below, together with which Concepts page plays each role.
The project's maturity is not offloaded: the cost section states it on the page itself.

- **Why CGP exists**, published as *Bypassing coherence*: the long-form version of sections 1 and 2,
  covering how Rust's trait system resolves dependencies, why coherence is necessary, what the overlap
  and orphan rules cost in practice, the workarounds developers reach for, and the
  `Self`-becomes-a-parameter move with local coherence restored. Built from
  [coherence](../../cgp/concepts/coherence.md) and
  [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), with the
  [RustLab transcript](../blog/rustlab-2025-coherence.md) as the model for how to build the argument.
  This is the page the homepage links to most often.
- **How CGP works**, published as *Consumer and provider traits* with *Impl-side dependencies* beside
  it: the mechanism for a reader who wants to see through the macros, covering the two generated
  traits, the wiring table, and the plain Rust an expansion produces, ending on why none of it costs
  anything at runtime. Built from the same two concepts plus
  [impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md), and the natural home for a
  [`cargo cgp expand`](../../cgp/reference/cargo-cgp.md) output.
- **When to use CGP, and when not**, published as *Modularity Hierarchy*: the boundary as a page the
  homepage can point a skeptic at, taken from
  [message.md](../../communication-strategy/message.md#when-not-to-reach-for-cgp) and the
  [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md). It is where the cost section on
  the homepage hands off to.
- **Overview**: the fourth destination, and the **feature tour**: the five headline features walked
  through with a compiled example each, then the breadth features named with a link each, which
  makes it the destination for both section 2 and section 3 of the essay.
  [The section below](#the-overview-the-feature-tour) specifies it.

### The Overview, the feature tour

**The Overview shows each feature working, states where it stops, and sends the reader to the page
that explains it.** Its job resolves the site's three disagreeing feature lists rather than merely
reconciling them: the front page carries the curated five from
[identity.md](../../communication-strategy/identity.md#the-headline-feature-set), four as illustrated
cards and the fifth in its reassurance line, and the Overview expands each of the five with an
example, then names the breadth features the tag line only gestures at, one line each with a link to
its Concepts page. The breadth features get no examples, because a first-time reader shown
namespaces, handlers, and extensible data in code beside the five meets more constructs than the
tour can explain. It is a docs page that presents the project, so its opening paragraph names
Context-Generic Programming and states the tag line whole, per the
[naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page). It
is written in natural style, like every page on the site: each section starts from a problem the
reader may have and leads from it to the example and its limit, so a reader who followed a front-page
card reads one connected explanation of that feature.

The page has these parts, in this order:

- **Opening:** the problem the tour answers, the name and the tag line, what the tour covers, that
  the examples are fragments of compiled programs, a pointer for a newcomer to *Still Ordinary
  Rust*, the simplest form, and a link to the Quickstart for a reader who wants to run one.
- **The five headline features**, under the heading *Key features*, with identity.md's titles word
  for word and in its order, so a reader who follows a front-page card finds its section under the
  same name.
- **Beyond choosing implementations:** a list of abstract types, extensible records and variants,
  composable handlers, namespaces, and higher-order providers, each in one or two sentences with its
  Concepts page and without code. The abstract-types item carries the payoff that section 3's clause
  names: the error type stops being a parameter that every layer carries.
- **The problems it solves:** a table from each problem in
  [message.md](../../communication-strategy/message.md#the-problems-cgp-removes), in the reader's
  words, to the Concepts page that answers it, in two columns, since the sections above show the
  problems that have an example. This table is the page's problems half, which the framework
  author's path in
  [information-architecture.md](../information-architecture.md#how-each-reader-moves-through-the-site)
  starts from.
- **When a plain trait is enough:** the costs in two short paragraphs, pointing to *Type-Safe
  Wiring* for the raw errors rather than repeating the `cargo-cgp` qualification stated there, and
  the agent skill beside the learning time; a link to the front page's cost section for the
  project's maturity, which the Overview does not restate; and *Modularity Hierarchy*.
- **Where to go next:** the Quickstart and Hello World, the Concepts pages, the comparisons, and the
  reference.

**Each headline feature section opens with the problem, shows one compiled example, states the
limit, and links onward.** The example stays within about fifteen lines. The opening says once that
every example leaves out the imports, the definitions it does not need to show, and each context's
check, and the Type-Safe Wiring section names `delegate_and_check_components!` as the one-step form.
The limit is the condition the strategy pairs with the strength, such as wiring that checks nothing
until a component is used or checked. The problem is stated fairly: where plain Rust already handles
a case, such as an application type implementing a trait directly, the section says so before
showing what CGP adds. The link goes to the page
[seo.md](../seo.md#the-tag-line-orients-the-reader-the-features-carry-the-searchable-words) names as
the owner of the feature's questions, because the Overview introduces a subject and the owner
explains it.

**The headline features run one scenario.** They use the profile-picture scenario under the names the
`cgp` README uses, listed among the
[canonical examples](../../communication-strategy/voice-and-register.md#show-it-canonical-examples-diagrams-and-diffs),
so the reader follows one realistic application through all five. The code is compiled
in the website's `example-code` crate at `tests/overview.rs`, and a quoted diagnostic is bound for recapture like every other quote on the
site.

**What stays off the page:** a construct reference, a second explanation of what a Concepts page
already explains, and the project's maturity, which the front page's cost section states.

**Checking a draft.** Read the page from start to finish and run natural-writing's checks: each
section should lead from its problem to its example and limit, and each sentence pick up from the
last. Check that each feature title matches identity.md, that each headline feature section has its
problem, example, limit, and link, that the breadth list shows no code, that the table covers every
problem in message.md, that every snippet matches `tests/overview.rs`, and that the page passes the
naming check. Then look at the rendered page at phone width in both themes, where long signatures
scroll inside their block.

## Images, metadata, and provenance

**The page keeps its art and keeps it light.** The hero illustration and the feature illustrations
were made with image models, as the [new-website post](../blog/new-website.md) records, and their
quality is above what an agent can draw in code, so a revision reuses them rather than redrawing
them. A new illustration matches the set: flat geometric vector shapes in the site's four reds (deep
maroon `#7a1614`, crimson `#b8312c`, coral `#e8837a`, pale pink `#f6d3cd`), soft drop shadows, a plain
white background, and no text. Until it exists, a placeholder drawn to the same brief stands in, and
the release checklist carries its replacement. Every raster image ships as WebP at twice its display
size, and the page's images stay under about 150 KB together.

**Every image reads in both themes.** The feature illustrations have white backgrounds, so each sits
in a rounded frame that reads as a tile on the dark theme, and the dark theme dims them and the hero
art a little, so their white backgrounds do not glare. They are decorative beside their titles,
so their alt text is empty; the hero illustration's alt text names the project.

**A shared link carries the name and the tag line.** The site's `themeConfig.image` is a 1200×630
social card made from the hero illustration with the name, the tag line, and the site address beside
it. Its generator lives in the website's `scripts/`, because the card must change whenever the tag
line does.

**The page carries no provenance line.** It is the one exception to the
[provenance rule](../../communication-strategy/ai-disclosure.md#linking-to-it-from-a-page): the front
page presents the project, and the disclosure page, which the site's AI section links, names the
exception and describes how the page was made. The page's record in
[site-structure.md](../site-structure.md) still states how it was made.

## What must not be on the homepage

Five things are excluded by the page's job rather than by taste, and each is a temptation with an obvious
home elsewhere.

**No teaching sequence.** No "first add this dependency, then define this trait". The moment the page
tells the reader what to type, it is competing with the tutorials and losing.

**No construct reference.** No table of macros, no attribute list, no syntax grammar. A reader who wants
to know what `#[uses]` does is past the homepage.

**No paradigm name as the hook.** The project's name heads the hero as identification, with the tag
line as its description, and that is its one appearance. It is never the hook: the hero does not
pitch "context-generic programming" or "a new paradigm" as the reason to read on, because the name
does not tell an unfamiliar reader what CGP does, and the tag line and the code block do.

**No coherence theory above the fold.** Section 1 explains coherence because the reader has just seen an
`E0119` and wants to know why the rule exists. Opening on it, before the code that motivates it, loses
the pragmatist immediately.

**No feature the strategy retires.** In particular, titles such as "Modular Component System" and
"Highly Expressive Macros" lead with words that cost more attention than they win, and "modular" as a
lead word is [specifically retired](../../communication-strategy/identity.md).

## Checking a draft

Run seven checks, in this order.

**Read only above the fold and ask whether it stands alone**: the name and the tag line,
reassurance, the contrast, two links. If a reader stopping there could not say what CGP does, the
hook has failed and nothing below matters.

**Find the cost section.** If there isn't one, the page is overselling to the audience least tolerant of
it.

**Check the frame.** Does the page explain what Rust already does, correctly and sympathetically, before
improving on it? A draft that opens by describing coherence as a limitation rather than as a guarantee
has the frame backwards.

**Count the sections and the links.** Five sections below the fold, two links above it. A sixth section
means something needs offloading; a third hero link means one of them is not needed.

**Read the copy aloud in natural style.** Run natural-writing's checks, the
[voice document's four checks](../../communication-strategy/voice-and-register.md#checking-a-draft),
and the [messaging brief's words to avoid](../../communication-strategy/messaging-brief.md#words).

**Look at the rendered page.** Take screenshots at 1920×1080, 1440×900, and 390×844 in both themes,
and at laptop 1280 and tablet 1024 widths in Firefox, which shows scrollbars, so a code window that
scrolls sideways is visible. The first screen meets the layout's targets, every image reads in both
themes, the images total under
about 150 KB, and the page ends at its routing section, with no provenance line. The site's font files
stay within about 100 KB together, and every character the page sets is in their subsets, so none is
drawn from a fallback face.

**Verify every snippet** against the source and the `/cgp` skill, preferring code already verified in
[examples/](../../examples/README.md). For the hero block specifically, compile it rather than reading it:
its nearest counterparts are tier 3 of the
[modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) and the
[modular serialization](../../examples/modular-serialization.md) example, and the six properties a
replacement must keep are in [Replacing it](#replacing-it).
