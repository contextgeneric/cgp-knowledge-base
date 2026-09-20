# Identity: the tag line, the pitch, and the headline features

Present CGP consistently through its settled tag line, a concrete pitch, and a focused set of
headline features.

These descriptions express the same identity at different lengths. Each must show what CGP adds
to Rust, why a reader would use it, and where its benefits stop.

## The positioning, in the order it was decided

Choose the positioning before writing the tag line. Work through alternatives, differences,
benefits, audience, and category in that order. The method comes from the
[communication sources](evidence.md#sources-for-the-craft-this-section-borrows); CGP's decisions are:

1. **Alternatives:** Plain traits and generics, enums, `dyn Trait`, newtypes, hand-written provider
   patterns, dependency-injection libraries, or waiting for a language feature. Each fits some
   problems better; [message.md](message.md#when-not-to-reach-for-cgp) explains where.
2. **Differences:** CGP gives implementations separate provider types and lets contexts select
   them. Providers can declare dependencies without adding them to the consumer interface, and
   contexts can choose associated types without passing each as a separate generic parameter.
   These mechanisms use ordinary traits on stable Rust.
3. **Benefits:** Readers can select implementations per application, extend behavior for foreign
   target types through providers, and keep implementation dependencies out of intermediate
   signatures. Wiring resolves statically. Abstract dependencies can also help keep a reusable
   core independent of a particular runtime or error library.
4. **Audience:** These benefits matter to developers managing interchangeable implementations,
   library authors extending foreign types, and maintainers passing dependencies through deep
   call graphs. They offer less to code with a single fixed implementation or a small, closed set
   of alternatives. See [readers.md](readers.md).
5. **Category:** Describe CGP as a *language extension for Rust*. This conveys its scope while
   making clear that it adds to Rust. "A language" or "a superset of Rust" overstates what a macro
   library provides. Dependency injection and type-class comparisons belong in explanations for
   readers who know those ideas.

The category names CGP's role, while the rest of the tag line names its central benefit and when
implementation selection happens. A comparison with an alternative should explain the relevant
difference without implying that the alternative lacks every feature in this list.

## The tag line

Use the settled descriptor at first contact:

> A language extension for Rust, with pluggable trait implementations at compile-time.

Put it beneath the project name on the homepage and README, and use or echo it in talks and posts.
Keep the wording consistent. If readers repeatedly misinterpret it, use that reception to reassess
the shared guidance rather than inventing a new descriptor for each piece. Follow
[evidence.md](evidence.md) when interpreting those reactions.

## The frame the whole identity serves: enhances, not replaces

CGP extends Rust's trait system. A consumer trait remains an ordinary trait, can be implemented
directly, and can coexist with code that does not use CGP. Explain those facts early so readers
understand that adoption can begin with one component.

CGP also composes with familiar ways of representing variation. A context may contain generics,
enums, or trait objects while selecting its providers statically. Developers choose which
variations deserve separate context types and which belong inside a context. See
[the configuration objection](message.md#the-objections-readers-bring).

Explain Rust's existing mechanisms fairly before showing what CGP adds. "A library on stable Rust"
and "adopt it one component at a time" support both accuracy and gradual adoption. Follow the
[voice guidance](voice-and-register.md) when presenting these claims.

## Why each word of the line is there

Each phrase answers a different first-contact question:

- **"A language extension for Rust"** identifies the category. CGP provides macros and library
  constructs that expand to ordinary Rust; it does not require a compiler fork or a new Rust
  grammar.
- **"Pluggable"** names interchangeable implementations selected per context. "Reusable" alone
  misses that distinction because ordinary traits already support reuse. Keep "pluggable" in
  the tag line even where "swappable" is useful in an explanation.
- **"Trait implementations"** connects the unfamiliar idea to a Rust abstraction the reader knows.
- **"At compile-time"** explains when selection happens. It prevents "pluggable" from implying a
  runtime container, dynamically loaded plugin, or vtable lookup.

Introduce the name *context-generic programming* after giving it a concrete meaning. The name
alone does not tell an unfamiliar reader what the tool does, as the reception summarized in
[evidence.md](evidence.md) illustrates.

Use the pitch to explain the breadth the tag line omits. Abstract types, extensible data, and
handlers matter, but listing them all in the descriptor would obscure its central benefit.

### Using "modular" as a supporting word

Keep "modular" out of the lead description. It names a broad design quality without showing the
problem CGP solves, and some readers associate it with runtime dependency-injection frameworks.
When it helps later in a piece, qualify the meaning: explicit wiring resolved at compile time,
without runtime dispatch overhead. The [redesign queue](../website/redesign-queue.md) tracks
site wording that needs to match this guidance.

## The pitch that follows the line

Follow the tag line with reassurance, a concrete example, and enough breadth for the format. The
homepage and README use a short identity block; a problem-led article can establish the motivating
problem before that block. The point is to make the benefit clear before teaching the mechanism.

The reassurance line explains how CGP fits into a Rust project:

> Still ordinary Rust: a library on the stable toolchain, with provider selection resolved at
> compile time, adopted one trait at a time.

The breadth line explains what else the same approach supports:

> Beyond interchangeable implementations, CGP adds abstract types chosen by each context, so error
> and runtime types need not be separate parameters through every layer. It also supports
> extensible records and variants, and composable handlers.

Keep the payoff beside the mechanism. An associated type is determined by its context, so callers
need not pass it as an independent type parameter. This does not remove all generics or bounds.
The reasoning is in
[impl-side dependencies](../cgp/concepts/impl-side-dependencies.md#type-dependencies-and-why-they-need-no-parameter).
The [extensible-data](../cgp/concepts/extensible-records.md) and
[handler](../cgp/concepts/handlers.md) documents explain the rest of the breadth claim.

Choose one problem the reader recognizes and show how CGP addresses it. Rejected overlapping impls,
newtype wrappers, and a growing trait are candidate openings in
[message.md](message.md#the-problems-cgp-removes). Keep a short format focused on that example;
longer pieces can develop the broader description.

State the relevant cost before asking the reader to act. CGP adds declarations, wiring, and concepts
to learn; a plain trait is usually clearer for a single implementation. Introduce the paradigm name
beside its plain descriptor, then offer the next step appropriate to the reader, following
[formats.md](formats.md#the-conversion-ladder).

## The headline feature set

Use these features in this order on a full feature panel. Each gets a title and one or two
sentences. Keep the panel within four to six features; use the longer
[message document](message.md#the-strengths-worth-advertising) for domain-specific explanations.

| Feature | Public wording |
| --- | --- |
| One Interface, Many Implementations | Write interchangeable implementations of one interface and choose between them per application. Separate provider types let implementations coexist while each application makes its choice explicit. |
| Zero-Cost Abstraction | CGP resolves provider selection at compile time and uses direct calls, without a runtime container or vtable lookup. Unused providers do not require runtime instances. |
| Type-Safe Wiring | Check wiring at compile time so missing dependencies fail the build. CGP connects providers through ordinary Rust traits, without requiring runtime reflection or dynamic dispatch. |
| Abstract Over Every Dependency | Write core logic against abstract error, runtime, and I/O dependencies, then let each context supply them. This supports a `no_std`-friendly core when the chosen implementations support it. |
| Still Ordinary Rust | Adopt CGP one component at a time. Providers use familiar impl syntax, implicit arguments resemble parameters, and consumer traits can still be implemented directly. |

Use "per application" where it makes a first-contact example concrete. A context need not represent
an entire application; explain its actual role when introducing the code, following
[vocabulary.md](vocabulary.md#qualifying-a-context-and-a-target).

Keep the verification claim precise. A delegation entry alone does not check its provider's
dependencies. Show `check_components!` or an appropriate combined wiring check to verify the
selection explicitly; use also forces type checking. See
[check traits](../cgp/concepts/check-traits.md).

### What the set deliberately leaves out

Leave "Dependency Injection" out of the general feature panel. Explain its benefits through
checked wiring and abstract dependencies, then use the DI comparison where the reader's background
makes it helpful. Avoid importing assumptions about a runtime container.

Put domain-specific benefits in the material linked from the panel. Error handling, runtime choice,
trait decomposition, and alternatives to dynamic dispatch develop the headline features rather
than competing with them. The [homepage guide](../website/writing-guides/homepage.md) specifies the
panel's place on the page; the [redesign queue](../website/redesign-queue.md) tracks site changes.

### Phrasing rules for feature titles

Name the concrete strength in a feature title. Avoid leading with "modular", "macros", or "magic".
Use familiar Rust terms such as "zero-cost", "type-safe", and `no_std` only where the accompanying
sentence explains the scope. State the benefit and the qualifier together.

Keep portability in the dependency feature and signature simplification in the breadth line. The
former addresses the systems programmer choosing a runtime or platform. The latter addresses the
maintainer whose intermediate layers repeat type parameters. Separating them keeps each short
while the longer [message](message.md) explains both.

## Keeping this document in sync

Propagate changes to shared wording in the same edit. Check [formats.md](formats.md),
[messaging-brief.md](messaging-brief.md), and [vocabulary.md](vocabulary.md), then the
[homepage guide](../website/writing-guides/homepage.md) and
[site records](../website/site-structure.md). Use [evidence.md](evidence.md) to reassess audience
assumptions and the [synchronization rule](../AGENTS.md#the-synchronization-rule) to check technical
claims against the source.
