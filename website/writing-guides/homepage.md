# Writing the homepage

The CGP homepage has one job: **make the idea click, and make the reader want it**, leaving them able
to say what CGP does and why it might matter to them, then routing them to the page that teaches it.
It is not a tutorial, a reference, or a feature catalogue, and this guide's central discipline is
keeping it from becoming any of those.

- **URL**: <https://contextgeneric.dev/>
- **Source**: [src/pages/index.tsx](https://github.com/contextgeneric/contextgeneric.dev/blob/main/src/pages/index.tsx)
  and [src/components/HomepageFeatures/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/src/components/HomepageFeatures)
- **Record**: [pages/front-page.md](../pages/front-page.md), for what the built page holds and how
  its code is tested
- **Voice**: project voice throughout, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md), in natural style, so
  the essay reads as one argument
- **Governed by**: [identity.md](../../communication-strategy/identity.md) for the line, the frame, and
  the features; [message.md](../../communication-strategy/message.md) for the pains and strengths;
  [readers.md](../../communication-strategy/readers.md) for who is reading
- **Reading**: the shared set and [the front page's row](README.md#the-front-page-and-the-overview)
  of the reading map

## What the page is for

**The success condition is comprehension that converts.** A reader who leaves able to explain CGP to
a colleague ("it lets one trait have several implementations and each type picks one, resolved at
compile time") has been served even without a click; a reader who clicks through excited but unable
to say what CGP does bounces off the first tutorial.

So the page **explains** with prose and code rather than a grid of adjectives, and it **does not
teach**: explaining answers "what is this and why", teaching answers "how do I do it", and the page
crosses over the moment it tells the reader what to type. It also carries the selling points, each
**tied to what the reader has just seen**, so a strength lands as an answer to a question the reader
now has.

## The two tiers

The page has two tiers with a hard boundary between them, because its two readers share no patience
budget.

**Above the fold is one screen that stands entirely alone.** Nielsen Norman Group's
[eyetracking research](https://www.nngroup.com/articles/scrolling-and-attention/) puts 57% of viewing
time above the fold and 74% within the first two screenfuls, so this screen delivers the whole pitch,
and nothing in it depends on anything below.

**Below the fold is a bounded essay** for the reader interested enough to want the argument. It runs
from the constraint to the payoff to the cost in a fixed number of sections, and the
[offload rule](#the-offload-rule-and-the-pages-it-offloads-to) caps its length.

## Above the fold

Four elements, in this order, and nothing else; the `E0119` quoted under the rejected block belongs to
the code element.

- **The name, then the tag line, verbatim.** The hero names **Context-Generic Programming** in text,
  so readers and search engines can read it, and states the tag line whole beneath it, per the
  [naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page):
  *"A language extension for Rust, with pluggable trait implementations at compile-time."* Never
  paraphrase it or replace it with a headline; one that leads with "modular" uses the word
  identity.md retires.
- **The reassurance line, with the install line.** *"Still ordinary Rust: a library on the stable
  toolchain, with provider selection resolved at compile time, adopted one trait at a time."*,
  verbatim from [identity.md](../../communication-strategy/identity.md#the-pitch-that-follows-the-line),
  which heads off reading "language extension" as a new language and "pluggable" as a runtime
  framework. `cargo add cgp` sits beside it, because the evaluator scans for the toolchain gamble.
- **The before/after code block**, the hook: the implementations Rust rejects, then the same
  implementations under CGP. [The example](#the-example-and-how-to-sell-it) specifies it.
- **Two links, no more:** the **Quickstart** for the reader ready to try, and the page's own **cost
  section** for the reader deciding on risk, since that section states the project's maturity. A third
  link dilutes both; the enthusiast finds the blog. The GitHub star widget may stay, since it is
  social proof rather than a call to action.

**The layout puts the code in the first screen.** The hero copy sits on the left and the hero
illustration on the right at about 280 px, with modest vertical padding. Between the phone layout and
1240 px the art shrinks to about 200 px and the title steps down, so the title keeps one line. The two
code blocks follow in a band of their own, side by side so a reader compares them line by line, with
the caption under them. The targets, measured with a screenshot rather than estimated, are the whole
first screen at 1920×1080, the caption's quote included, and the tops of both blocks at 1440×900. On
a phone the blocks stack and only the hero copy fits the first screen. Do not shrink the hero art to a
small logo, and do not put the blocks in tabs, which hide the comparison.

**Each block is an editor window that states its verdict.** The title bar carries a cross or a tick
beside the label ("Rust accepts only one of these", "With CGP, both compile"), and the changed lines
read like a diff, with a tint and a gutter mark in the window's own red or green, so a reader who
cannot tell red from green still sees the difference. The rejected window numbers its lines and
quotes rustc's `E0119` beneath the block without the location line, so the error names lines 7 and 11
as the page numbers them. The lines run to about 70 characters, so below 1360 px the code sets a
little smaller and below 1240 px the windows stack, and neither scrolls sideways.

## The example, and how to sell it

**The example is settled: a trait the snippet defines, implemented twice over two ordinary Rust
bounds that overlap, then wired per type.** It is `CanEncode` over `Display` and `AsRef<[u8]>`, with
the providers `EncodeAsText` and `EncodeAsBytes` and wiring for `u64`, `String`, and `Vec<u8>`; the
text is in `index.tsx` between its `front-page:` markers and compiled in the website's
`tests/front_page.rs`. Most of the page's attention falls on these twenty lines, so they carry the
pitch, the proof, and the answer to the first objection.

**The caption is two sentences**: what changed, then the informed objection pre-empted.

> Both implementations compile, because each one now has a name, and each type names the one it uses, so
> a call to `encode()` is as unambiguous as it ever was. Coherence is not repealed; it is scoped.

Everything else a writer wants to add above the fold (why coherence exists, what the wiring table is,
what it costs at runtime) belongs to the essay or to
[*Why CGP exists*](explanation.md#why-cgp-exists); adding it here is the most common way the block
gets ruined. The copy keeps three properties:

- **The first block is labelled as a refusal, not a mistake**, so the reader feels the program is
  reasonable and the language says no.
- **The comment says `String` out loud**, which turns "impls might overlap" into a fact the reader
  checks in one second.
- **`error[E0119]` is quoted verbatim**, which makes the claim checkable.

### Replacing it

The example is settled, not sacred, but a replacement keeps every property below, and a candidate
failing one is worse than what it replaces:

- **The trait is defined in the snippet**, so the failure is unambiguously the overlap rule: a
  blanket impl of a foreign trait, such as `impl<T: Display> serde::Serialize for T`, fails with the
  orphan rule's `E0210` on its own.
- **The two bounds overlap on a type the reader names without being told**, needing no domain, as
  `String` is both `Display` and `AsRef<[u8]>`; the escape a reader reaches for, a newtype or a marker
  struct with a helper trait, is
  [independently reinvented](../../communication-strategy/evidence.md), so the CGP version arrives as
  relief.
- **The trait's shape is identical across the pair**, which keeps the example on tier 3 of the
  [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md); any other change reads as
  sleight of hand.
- **The bodies are identical and shown**, one line each, so the only difference is the annotations and
  the wiring; a `/* ... */` would invite the suspicion the block exists to remove.
- **The wiring shows at least two providers, one of them used twice**, which shows a provider is
  reusable logic rather than a renamed impl, and it wires the type whose ambiguity caused the error,
  answering "which one does `String` get?".
- **The real error code appears verbatim.**

Two presentation choices stay with it. The bounds sit in `#[uses(Display)]` and `#[uses(AsRef<[u8]>)]`,
the idiom the [guides](../../cgp/guides/declaring-dependencies.md) prescribe, which also shows the
attribute carrying an ordinary Rust trait; do not rewrite them to `where Self: Display`. And the block
is a fragment without imports, `main`, or a call site, but it must compile once the imports are
restored; a program to run belongs in the Hello World tutorial.

Compile a replacement before it ships, in `tests/front_page.rs` with its compile-fail fixture, as
[the page's record](../pages/front-page.md) describes, and change the page and the test in the same
commit.

### Which shape it is, and why that matters here

**The block is the retrofit shape**: a value context, since `String` and `u64` are the data being
encoded, with the component targeting `Self`. It is the **least representative of CGP's three
shapes**; most CGP code is the application shape, and the fully modular shape moves the target into a
parameter, per [vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target)
and the [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md).

**The trade is kept, and is not reopened each redesign.** Only this shape lets the before and after
differ by nothing but the annotations while failing with a real `E0119`. It costs representativeness,
and the site pays that back by **teaching the application shape second**: on the explanation path at
the end of essay section 1 and on [*How CGP works*](explanation.md#how-cgp-works), and on the teaching
path in the applied tutorial, placed second in the tutorial order for this reason. A change to either
is a change to this trade.

**Do not use the word "context" anywhere in the hero**, apart from the project's name. At the
retrofit shape the context and the target are the same type, so calling `String` a context
contradicts the gloss every other page gives; "each type names the implementation it uses" is enough.

### What it deliberately does not show

Each omission is repaid elsewhere, and naming them stops a revision from cramming one in:

- **Two applications choosing differently for the same type**, repaid by
  [*Modularity Hierarchy*](explanation.md#when-to-use-cgp-and-when-not). Do not put the fully modular
  shape above the fold: it changes the trait to `CanEncodeValue<Value>`, breaking the shape rule, and
  needs `open` and `@`-path syntax the reader has no grounding for.
- **The orphan rule dissolved.** The block wires types the snippet does not own, legal only because it
  owns the trait; moving the value out of `Self` dissolves that limit too, in one sentence of the
  essay.
- **Everything past trait implementations**, which section 3 of the essay repays in a sentence each.

## Below the fold: the bounded essay

Five sections, in this order, each answering one question and stopping. The titles below are jobs
rather than required headings, but the order is the order in which the questions occur to a reader.

**The bands alternate between the page and a tint, and each section takes the layout that fits it.**
The hero is tinted and the code band is not; sections 1, 3, and 5 take the tint and 2 and 4 the page,
so no gap needs a rule. Section 1 sets its title in a narrow column beside its prose, section 2 the
cards two to a row, section 3 three linked tiles, section 4 the costs in a framed panel, and section 5
one card per reader. Above 996 px, section 1's title and section 4's heading and lead stay in view
beside their longer columns; on a phone they stack. The gaps come from a spacing scale in the page's
stylesheet.

**1. Why Rust only lets you do this once, and what CGP changes.** Explain, sympathetically and
correctly, that the trait system doubles as dependency injection (a generic impl requires
`where T: Display` without the caller naming it) and that this works only if every lookup finds the
same implementation, so coherence is *correct*. This is where the enhances-not-replaces frame is
earned. Name the workaround without CGP, a newtype per case or a marker struct and a helper trait, and
link *Bypassing coherence*. Then state the move: the implementation's `Self` becomes a type the
implementing crate owns, so neither rule bites, and coherence is **restored locally**, because each
wired type names one provider; the caption already says this, so the section explains it rather than
repeating it.

The section ends where the page crosses from the retrofit shape to the application shape, and it says
so in one sentence: *"so far the wired type has been the data, which gets one choice for the whole
program; the move that makes the choice yours is to wire a type you define to stand for your
application, and because it is yours, you can define as many as you like."* That is the first use of
the word **context** on the page, per
[vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target) and the
[comprehension barrier](../../communication-strategy/readers.md). The page names a context without
showing one in code, a deliberate departure from readers.md: the section's last sentence links
[*Consumer and provider traits*](explanation.md#how-cgp-works), which shows an application and its
test wiring different providers, because a second example would add a domain to learn and does not
fit the space.

**2. What that buys you.** The first four headline features from
[identity.md](../../communication-strategy/identity.md#the-headline-feature-set), in its order and with
its titles verbatim, as one illustrated card each: one or two sentences anchored to what the reader
has seen, the illustration beside the text, and the whole card linking the page that
[seo.md](../seo.md#the-tag-line-orients-the-reader-the-features-carry-the-searchable-words) maps the
feature to. A line under the cards links the Overview. The fifth feature, *Still Ordinary Rust*, gets
no card, because the reassurance line states it. Say "per application" rather than "per context",
except on a card pointing back at the hero, which says "each type". Draw the wording from
[message.md](../../communication-strategy/message.md#the-strengths-worth-advertising) and keep its
rules: Type-Safe Wiring names `check_components!` or a use of the component, because a wiring entry
alone checks nothing, and Abstract Over Every Dependency carries portability, leaving the signature
payoff to section 3.

**3. It goes further than trait implementations.** One sentence each for abstract types a context
chooses, extensible records and variants, and the composable handler family, repaying the tag line's
"trait implementations" undersell; no elaboration. The abstract-types sentence carries the **payoff**,
matching the [breadth line](../../communication-strategy/identity.md#the-pitch-that-follows-the-line):
an error type or a runtime stops being a parameter every layer carries.

**4. What it costs.** Not optional and not softened, written as part of describing the thing
accurately rather than as a hedge. It is the page's highest-trust element and **the one place on the
site that states the project's maturity**.

- **Content:** one lead sentence that a plain trait is the right tool for a single implementation,
  then the costs: more declarations; compile-time work; verbose raw errors, with the `cargo cgp check`
  qualification word for word; a young ecosystem; and learning time, with the agent skill beside it.
  The maturity statement says CGP is young, its ecosystem small and community support limited, so an
  adopter of a mission-critical project should expect to investigate some problems alone; its raw
  errors can be hard to read, and `cargo-cgp` is itself an early release; code an assistant writes
  still needs the reader's review. The section ends advising a try on a small part of a project whose
  implementation choices already vary, linking *Modularity Hierarchy*.
- **Layout:** a description list rather than a table, each short label in a column of its own beside
  one sentence, with a rule between rows, and the heading and lead in a column beside the rows; on a
  phone each label sits above its sentence.
- **Agent support:** mentioned here and nowhere else on the page, in one clause, as a smaller cost
  rather than a solved one, linking the skill. Never in the hero, the reassurance line, a card, or a
  feature title: a landing page that leads on AI is read as chasing attention by this audience. The
  rule is [message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these)'s,
  with the wording to avoid in
  [vocabulary.md](../../communication-strategy/vocabulary.md#words-and-framings-to-avoid).

**5. Where to start.** The only section with more than two links, matched to the reader by the
[conversion ladder](../../communication-strategy/formats.md#the-conversion-ladder): the Quickstart and
the first tutorial to try it; the explanation pages for the argument; *Modularity Hierarchy* and the
Projects pages for an evaluator, who looks for a real system; the Overview, the comparisons, and the
blog for depth; and the Contribute page for the enthusiast. Each card links its main page beside a
reason written as a complete action sentence, so a reader follows the path from trying CGP to
understanding it or evaluating adoption.

## The offload rule, and the pages it offloads to

**A section that wants a second code block, a second example, or a paragraph of mechanism has outgrown
the homepage.** The material moves to a dedicated page, and the section keeps one paragraph and a
link. The project's maturity is never offloaded. The four destinations exist, and their guides own
their specifications:

- **Why CGP exists**, published as *Bypassing coherence*, the long form of sections 1 and 2 and the
  page linked most: [explanation.md](explanation.md#why-cgp-exists).
- **How CGP works**, published as *Consumer and provider traits* with *Impl-side dependencies*:
  [explanation.md](explanation.md#how-cgp-works).
- **When to use CGP, and when not**, published as *Modularity Hierarchy*, where the cost section hands
  a skeptic: [explanation.md](explanation.md#when-to-use-cgp-and-when-not).
- **The Overview**, the feature tour and the destination of sections 2 and 3:
  [orientation.md](orientation.md#the-overview).

## Images, metadata, and provenance

**The page keeps its art.** The hero and feature illustrations were made with image models, as the
[new-website post](../blog/new-website.md) records, at a quality an agent cannot draw in code, so a
revision reuses them. A new illustration matches the set: flat geometric vector shapes in the site's
four reds (deep maroon `#7a1614`, crimson `#b8312c`, coral `#e8837a`, pale pink `#f6d3cd`), soft drop
shadows, a plain white background, and no text. Until it exists, a placeholder drawn to the same brief
stands in, and the release checklist carries its replacement. Every raster image ships as WebP at
twice its display size, and the page's images stay under about 150 KB together.

**Every image reads in both themes.** The feature illustrations sit in rounded frames that read as
tiles on the dark theme, and the dark theme dims them and the hero art a little so their white
backgrounds do not glare. They are decorative beside their titles, so their alt text is empty; the
hero's alt text names the project.

**A shared link carries the name and the tag line.** `themeConfig.image` is a 1200×630 social card
made from the hero illustration with the name, the tag line, and the site address; its generator is in
the website's `scripts/`, and the card changes whenever the tag line does.

**The page carries no provenance line**, the one exception to the
[provenance rule](../../communication-strategy/ai-disclosure.md#linking-to-it-from-a-page), because it
presents the project; the disclosure page names the exception, and the page's record states how it was
made.

## What must not be on the homepage

- **No teaching sequence**, such as "first add this dependency, then define this trait"; the tutorials
  do that.
- **No construct reference**: no table of macros, attribute list, or syntax grammar.
- **No paradigm name as the hook.** The name heads the hero once, as identification beside the tag
  line; the hero never pitches "context-generic programming" or "a new paradigm" as the reason to read
  on, because the name does not say what CGP does.
- **No coherence theory above the fold.** Section 1 explains coherence once the reader has seen an
  `E0119`; opening on it loses the pragmatist.
- **No feature the strategy retires**, such as "Modular Component System" or "Highly Expressive
  Macros", and no "modular" as a lead word, per [identity.md](../../communication-strategy/identity.md).

## Checking a draft

Run these checks in order:

1. **Read only above the fold**: the name and tag line, the reassurance, the contrast, two links. If a
   reader stopping there could not say what CGP does, nothing below matters.
2. **Find the cost section**; without one the page oversells to the audience least tolerant of it.
3. **Check the frame**: the page explains what Rust already does, correctly and sympathetically, and
   presents coherence as a guarantee before improving on it.
4. **Count the sections and the links**: five sections below the fold and two links above it. A sixth
   section needs offloading; a third hero link is one too many.
5. **Read the copy aloud** and run natural-writing's checks, the
   [voice document's four checks](../../communication-strategy/voice-and-register.md#checking-a-draft),
   and the [messaging brief's words to avoid](../../communication-strategy/messaging-brief.md#words).
6. **Look at the rendered page** at 1920×1080, 1440×900, and 390×844 in both themes, and at 1280 and
   1024 in Firefox, which shows the scrollbars Chrome's headless captures hide. The first screen meets
   the layout's targets, no code window scrolls sideways, every image reads in both themes, the images
   total under about 150 KB, the page ends at its routing section, the font files stay within about
   100 KB together, and no character the page sets falls outside their subsets.
7. **Verify every snippet** against the source and the `/cgp` skill, and compile the hero block rather
   than reading it; its nearest counterparts are tier 3 of the
   [modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) and the
   [modular serialization](../../examples/modular-serialization.md) example.
