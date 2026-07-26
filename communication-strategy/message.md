# The message: pains, capabilities, objections, and limits

This document carries everything a piece actually *says* about CGP: the concrete problems it removes,
the capabilities worth advertising, the objections readers bring, and the boundary beyond which a
plainer tool wins. These four were once separate documents, and consolidating them is deliberate —
they are four views of one reader. The person who feels "I can't swap my mock for the real thing",
hears "compile-time dependency injection", asks "isn't DI heavy and magical?", and needs to be told
"for one implementation, use a plain trait" is the same person, and a claim edited in one view almost
always needs the same edit in the other three.

## Lead with the pain, not the paradigm

The ordering rule governs every piece and is worth stating before any content. **Open on a problem
the reader already has, then let the capability arrive as relief.** "Here is the thing you fight every
week, gone" persuades where "look what CGP can do" does not, and the difference is most pronounced
with the pragmatic majority who are scanning for whether the machinery is justified. Reach for the
problem that matches the reader, per [readers.md](readers.md), before reaching for any capability.

Three habits make an entry work. Lead with the **workaround the reader recognizes**, not the
mechanism, so the CGP version arrives as relief rather than as a new thing to learn. Keep the
**before/after small and honest** — a few lines on ordinary-looking code, where the "before" is what
the reader would genuinely write rather than a strawman. And **name the limit in the same breath**,
because every entry below is also a place a reader could over-apply CGP, and the honest boundary is
what makes the win believable.

All code here uses the modern idioms the `/cgp` skill and the [guides](../cgp/guides/README.md) teach
— a provider written with [`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md), values read with
[`#[implicit]`](../cgp/reference/attributes/implicit.md), wiring with
[`delegate_components!`](../cgp/reference/macros/delegate_components.md) — because a before/after
showing dated CGP teaches a dialect the reader must later unlearn.

## The problems CGP removes

### Give one interface many implementations that Rust rejects outright

The sharpest problem, and the one that best matches CGP's [tag line](identity.md), is that Rust
forbids two blanket implementations that could ever overlap — even when the programmer knows exactly
which should apply where. A developer who wants to serialize any `Display` type one way and any
`AsRef<[u8]>` type another hits a wall the language will not let them past, because `String`
satisfies both:

```rust
pub trait CanEncode {
    fn encode(&self) -> Vec<u8>;
}

// Legal on its own.
impl<T: core::fmt::Display> CanEncode for T { /* ... */ }

// error[E0119]: conflicting implementation — overlaps on every `T: Display + AsRef<[u8]>`.
impl<T: AsRef<[u8]>> CanEncode for T { /* ... */ }
```

Keep the demonstration on a trait the snippet defines. The overlap rule (`E0119`) and the orphan rule
(`E0210`) are different failures, and writing the "before" against a foreign trait such as
`serde::Serialize` shows the second while claiming the first — an error the readers worth winning will
correct in the first reply. CGP lifts both, but a piece should show one at a time.

CGP makes the two impls legal because each targets its own zero-sized provider type rather than the
trait itself, so the overlap rule never applies:

```rust
#[cgp_component(Encoder)]
pub trait CanEncode<Value> {
    fn encode(&self, value: &Value) -> Vec<u8>;
}

#[cgp_impl(new EncodeWithDisplay)]
impl<Value> Encoder<Value> where Value: core::fmt::Display { /* ... */ }

#[cgp_impl(new EncodeBytes)]
impl<Value> Encoder<Value> where Value: AsRef<[u8]> { /* ... */ }
```

Note that the value has moved out of `Self` into a parameter — the climb from rung 3 to rung 4 of the
[modularity hierarchy](../cgp/concepts/modularity-hierarchy.md), and the same move that dissolves the
orphan rule in the next entry. Narrate it rather than letting a reader spot it uncommented, because an
unexplained difference between a before and an after reads as sleight of hand.

Both compile, and a context names the one it wants. This is the entry for the **type-system reader**
and the strongest hook for the front page, since it shows something the language cannot do rather
than something it does awkwardly. The mechanics are [bypassing coherence](../cgp/concepts/coherence.md),
and the honest limit is that this is genuinely more machinery than a single trait needs — it earns its
place only when the several implementations are real.

### Implement a trait for a type you don't own — no newtype dance

The orphan rule is a pain sharp enough that Rust developers hand-roll CGP's own mechanism to escape
it: you cannot implement a foreign trait for a foreign type, so adding behavior to another crate's
type means wrapping it in a newtype and re-exposing every method you still need. This is not
theoretical — there is a repository cataloguing the rule's design problems, and one Rust author
[independently reinvented CGP's exact marker-struct pattern](evidence.md) to get around it, calling
the hand-rolled version "3 extra lines to link things together".

CGP dissolves the rule because a provider implements the *provider* trait for its own marker, not the
target trait for the foreign type, so a crate can add a capability to a type it does not own with no
wrapper. The pitch's power is recognition: the reader has written the three-line workaround and would
rather not maintain it. This lands with the **working and advanced developer**, and the honest limit
is that CGP does not repeal coherence globally — it keeps each choice explicit and per-context, and
where a program genuinely wants one instance program-wide, a coherent trait is the better fit.

### Mock in tests, run the real thing in production — without `dyn` or a framework

The most universally felt pain is swapping a real implementation for a fake across tests and
production. The usual routes each cost something: a `Box<dyn EmailSender>` pays runtime dispatch and
infects the type with a trait object; a generic `<E: EmailSender>` parameter threads through every
layer and multiplies as dependencies join; a dependency-injection crate brings machinery the Rust
community broadly distrusts ([evidence.md](evidence.md)). CGP makes the swap a single wiring line,
monomorphized to a direct call:

```rust
#[cgp_component(EmailSender)]
pub trait CanSendEmail {
    fn send_email(&self, to: &str, body: &str);
}

#[cgp_impl(new SendViaSmtp)]
impl EmailSender { /* connect and send over SMTP */ }

#[cgp_impl(new RecordEmails)]
impl EmailSender { /* push to a Vec so a test can assert on it */ }

delegate_components! { App     { EmailSenderComponent: SendViaSmtp } }
delegate_components! { TestApp { EmailSenderComponent: RecordEmails } }
```

`App` sends real mail and `TestApp` records it; neither pays for `dyn`, the swap is one greppable
line, and code calling `self.send_email(..)` never changes. This is the most legible entry for the
**working developer**, and it defuses the "why not just use traits" reflex by showing the case where a
plain generic would have proliferated. Two cautions: the choice is a line *you* write rather than one
CGP infers, and for a dependency with exactly one implementation a plain trait is still right. This
entry is also the one most likely to draw "I already solved that", so pair it with one of the two
above when the audience is skeptical.

### Swap your error type or runtime by changing one line

A quieter pain, felt hardest in libraries and reusable cores, is that fallible code commits to a
concrete error type early and then cannot easily change it, so moving from `anyhow::Error` to a custom
enum ripples through every signature. CGP makes the error type — or the runtime, or any cross-cutting
type — abstract, chosen by the same wiring that selects behavior:

```rust
delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<anyhow::Error>,
    }
}
```

Switching that line to a custom `AppError` retargets every fallible provider in the context, touching
no logic. This resonates with the **ML-module and systems reader** and underpins CGP's
[modular error handling](../cgp/concepts/modular-error-handling.md). The honest limit: CGP defers and
configures the type rather than sealing a representation the way an ML module does, and the wiring
keys live under `cgp::core::error` rather than the prelude, so a piece showing this should import them.

### Break up a trait that grew into a monolith

A pain that arrives with a codebase's age rather than its domain is the trait that accreted
responsibilities until every implementor must supply the whole surface and every change touches all of
them. This is where CGP itself came from — the `ChainHandle` trait with dozens of methods that
prompted the author's original work (see [author-personality.md](author-personality.md)) — which makes
it an entry with a true story behind it. CGP lets one large capability become a set of independently
wired components, each with its own providers, so an implementor supplies only what it uses and adding
a capability is adding a wiring line rather than editing a shared trait. This is the decoupling pitch
for the **framework author and the evaluator**, resting on the
[consumer/provider split](../cgp/concepts/consumer-and-provider-traits.md). The honest limit:
decomposition is a judgment call, and a small, stable trait with one implementation should stay a
plain trait.

### Write a framework over any type's structure — without runtime reflection

For the author of a serialization library, a builder, an ORM, or a configuration system, the recurring
pain is code that must work over the *shape* of a user's type without a general reflection facility
Rust lacks. CGP encodes fields and variants as type-level data the trait system resolves against, so a
framework written once recurses over any type that opts in with a derive, fully checked when written
and with nothing walked on each call — developed in
[extensible records](../cgp/concepts/extensible-records.md) and
[extensible variants](../cgp/concepts/extensible-variants.md). The honest limit, in the same breath:
it works only on types that derive the shape and does no runtime introspection, so the precise frame
is "compile-time structural reflection encoded in types" rather than "reflection for Rust".

### Keep a provider's dependencies out of your public API

A subtler pain felt by library authors is that trait-based dependency injection leaks: any type named
in a public trait's method signature must itself be public, so exposing a dependency through a generic
trait forces internal types into the public API, a cost
[documented with its source](evidence.md) in the Rust community. CGP keeps a provider's dependencies as
[impl-side constraints](../cgp/concepts/impl-side-dependencies.md) — declared through
[`#[uses]`](../cgp/reference/attributes/uses.md) and `#[implicit]` where the implementation lives
rather than in the consumer trait's signature — so the interface stays clean while the requirements
remain explicit and compiler-checked. This is narrower and more advanced than the others, so it belongs
in a piece aimed at library authors rather than in a general hook.

### Read a CGP compile error without decoding a wall of generated types

The pain that has done CGP the most adoption damage lives not in the language but in its errors: a
context missing one field a provider needs expands into screens of diagnostics naming `IsProviderFor`,
`CanUseComponent`, and a nested `Symbol<…>` spine the programmer never wrote, with the real cause
buried or — in the worst class — suppressed entirely. A developer who meets that wall on their first
mis-wire often concludes CGP is unusable and leaves, which is why this is the pain most worth showing
removed. Under plain `cargo check` the failure is an `E0277`/`E0599` cascade naming the traits but not
the missing field, the
[hidden unsatisfied-dependency class](../cgp/errors/hidden/unsatisfied-dependency.md). Through the
toolchain it becomes:

```text
$ cargo cgp check
error[E0277]: [CGP-E001] the consumer trait `CanCalculateArea` is not implemented for context `Rectangle`
   = note: root cause: [CGP-E106] missing field `height` on `Rectangle`
           this is required through the dependency chain:
             [CGP-E101] consumer trait impl `CanCalculateArea` for context `Rectangle`
             └─ [CGP-E102] provider trait impl `AreaCalculator` with context `Rectangle` for provider `RectangleArea`
               └─ [CGP-E106] missing field `height` on `Rectangle`
```

[`cargo-cgp`](../cgp/reference/cargo-cgp.md) turns on Rust's next-generation trait solver to un-hide
the suppressed cause, then leads with it and draws the dependency chain as a tree. The honest limit,
in the same breath: it is v0.1.0-alpha and reshapes the classes it recognizes while some, orphan-rule
errors among them, still pass through as the compiler wrote them.

### Choosing which problem to lead with

Name the dominant [reader profile](readers.md) for the channel first, then pick the problem that
reader feels most sharply: the rejected overlapping impls for the type-system reader, the orphan-rule
escape for the trait-heavy developer, the mock-in-tests swap for the pragmatic majority, the error-type
swap for the systems and ML-module reader, the monolith decomposition for the evaluator, the
structure-generic framework for the tooling author, and the readable-errors story for anyone who has
heard CGP's diagnostics are unusable. For a broad public audience, lead with the rejected-impls or
orphan-rule entries, because they show something Rust cannot do rather than something it does
awkwardly, which is the hardest framing to dismiss as astronaut architecture.

## The capabilities worth advertising

A capability is worth advertising when it is **true**, **framed for a specific reader**, and
**anchored to a pain above**. Dropping any of the three turns it into the kind of claim this audience
punishes. Two habits separate a pitch that lands from one that invites a pile-on: pair the advantage
with its cost whenever the audience is a skeptic, and prefer the concrete to the grand — "compiled to
a direct call" outperforms "fast", and "one interface with many implementations" outperforms
"flexible".

**Zero runtime cost** is the strongest broad capability: all of CGP's flexibility is resolved at
compile time and erased before the program runs. There is no container holding a graph, no reflection,
no vtable, no dynamic dispatch; a wired call monomorphizes to a direct function call, and a provider a
context does not use is not in the binary. Say it as *"resolved at compile time and compiled away — a
wired call is a direct call"*, *"no runtime container, no reflection, no vtable"*, or *"unused
providers are not in your binary"*. Skip "blazingly fast" and any comparative speed claim without a
benchmark; the honest and stronger claim is that there is no cost to compare. "Zero-cost abstraction"
is accurate but worn, so prefer the concrete phrasing outside a feature title.

**Overlapping and orphan implementations, made safe** is the standout for the type-system audience,
and it has a rare asset behind it: developers already reinvent CGP's mechanism by hand
([evidence.md](evidence.md)), so the pitch reminds a reader of a workaround they have written rather
than a capability they must be talked into wanting. Say it as *"type classes without the orphan
rule"*, *"implement a capability for a type you don't own, with no newtype wrapper"*, or *"the
incoherence is deliberate at the definition level and disciplined at the use site — every choice is a
line in a table, never a silent resolution"*. Never claim CGP is coherent or promise global
uniqueness: uniqueness is *per context*, and that scoping is the point.

**Swappable implementations chosen per context** is the most legible capability for the working
developer, and its whole risk is implying the choice is automatic. Say *"one interface, many
implementations — the context picks which one, and the choice is a line you can read"*. Never say CGP
"picks the right one"; the explicitness is the feature, and a reader sold on automatic resolution
feels misled at their first `delegate_components!` entry.

**Explicit, compiler-checked dependencies** answers the loudest complaint against DI frameworks
directly. A provider states what it needs through `#[uses]` and `#[implicit]` rather than hiding it, a
missing dependency is a compile error at the wiring site rather than a startup exception, and because
the dependencies live in the implementation they never force internal types into a public API. Say
*"a missing dependency is a compile error at the wiring site, not a runtime surprise"* and
*"`check_components!` is your container's startup validation, run at compile time instead of at boot"*.
Do not oversell the verification as effortless: the check is something you write, and its raw output
is verbose.

**First-class tooling for the errors** is the capability CGP could not honestly claim until recently,
and it is bound by an unusually load-bearing honesty rule because the reader can `cargo install` and
check within the hour. Say *"a dedicated checker that leads with the root cause — `cargo cgp check`
names the missing field instead of a wall of generated types"*, and always in the same breath that it
is a **v0.1.0-alpha** reshaping the core wiring errors but not yet every class. Never say CGP's errors
are "solved", "fixed", or "as clear as any other Rust error's".

**It reads like ordinary Rust, and you adopt it gradually** is the enhances-not-replaces
[frame](identity.md) as a capability, and it is what disarms the all-or-nothing fear. An `#[implicit]`
argument looks like a function parameter, a `#[cgp_impl]` provider looks like a trait impl, and a
consumer trait can be implemented directly with no CGP machinery at all. Say *"a superset of ordinary
traits — start with one component and leave the rest of your code unchanged"*. Do not claim "no
boilerplate"; CGP *moves* wiring into one readable place rather than erasing it.

**Abstract types chosen per context** lets generic code name an error type, a scalar, or a runtime
that each context fills in through the same wiring that selects behavior. Say *"generic code names the
type; the context chooses it"*. Do not conflate this with sealing — representation hiding is Rust's
module privacy, a distinction the [ML-module reader](../related-work/ml-modules.md) will look for.

**Generic over a type's structure, checked and free** is the framework author's capability: a type
opts in with a derive, its shape becomes type-level data, and generic code recurses over it with full
static checking. Say *"reflection's payoff without the runtime cost or the stringly-typed failures"*,
never "a reflection system", and state the opt-in derive requirement in the same breath.

**It works on stable Rust today** is plain but load-bearing for the evaluator and for the functional
programmer who assumes this expressiveness requires a different language. Say *"a library on stable
Rust — not a fork, not a nightly feature, not a proposal"*, and stop there: "production-proven at
scale" is a different claim that needs evidence the evaluator will notice is missing.

### Audience-tuned one-liners

The sharpest phrasings translate a capability into a reader's own idiom, letting them spend attention
only on what is new. Each is calibrated to one profile in [readers.md](readers.md) and grounded in the
matching [related-work](../related-work/README.md) comparison; using one on the wrong audience
misfires.

- **Scala or implicits reader:** "implicits without the mystery — the dependency still arrives without
  threading it through every call, but which implementation supplies it is a line in a wiring table,
  not a resolution search." ([implicit parameters](../related-work/implicit-parameters.md))
- **Haskell or type-class reader:** "type classes without the orphan rule, and overlapping instances
  made legal." ([type classes](../related-work/type-classes.md))
- **Spring, Guice, or Dagger reader:** "Dagger, taken further — compile-time-checked injection, with
  per-context choice a single global binding graph can't express."
  ([dependency injection](../related-work/dependency-injection.md))
- **Dynamic-language reader:** "duck typing that can't blow up at runtime, and dynamic dispatch that
  costs nothing." ([dynamic dispatch](../related-work/dynamic-dispatch.md))
- **OCaml or ML-module reader:** "functors with the plumbing automated — a declarative table instead of
  a hand-ordered functor chain." ([ML modules](../related-work/ml-modules.md))
- **Algebraic-effects reader:** "effect handlers minus the continuation, resolved by type instead of
  dynamic scope, and extended to abstract types."
  ([algebraic effects](../related-work/algebraic-effects.md))
- **Reflection or framework-author reader:** "compile-time reflection encoded in the type system —
  generic over a type's structure, checked when you write it, erased before it runs."
  ([reflection](../related-work/reflection.md))
- **PureScript or row-types reader:** "row polymorphism's extensibility, in a nominal systems language,
  opt-in per type." ([row polymorphism](../related-work/row-polymorphism.md))

## The objections readers bring

Skepticism is the default reaction to CGP rather than the exception, so the job is less to avoid
objections than to meet them before the reader raises them. They come from three sources, and telling
them apart decides the response. Some are **imported** from a paradigm CGP resembles, where the
reader's complaint is justified about the *other* tool and misapplied here. Some are **native** to the
Rust community's wariness of complexity and macros. And some point at **genuine costs** no wording can
spin away. The worst mistake is treating a justified objection as a misunderstanding to argue down;
the reader knows the difference, and the attempt destroys the trust everything else rests on.

### Imported from other paradigms

**"This is dependency injection, and DI is heavy, magic, and fails at runtime."** The complaint is
thoroughly justified about the reflection-based containers that provoked it and entirely misapplied to
CGP, which has no container, no reflection, and no runtime graph. Name the difference before the
category: say "compile-time, reflection-free dependency injection", state that the container *is* the
type system, and lead with the pains they resent — hidden dependencies, the startup exception, the
magic they cannot trace — showing CGP answers each by construction.

**"Implicit resolution is spooky — values appear from nowhere."** Justified about implicit resolution,
and it does not transfer, but for a reason a writer must state carefully, because the obvious
reassurance is a trap. CGP has no spooky resolution because it does not resolve automatically at all —
the provider is named in a wiring table. The misunderstanding to prevent here is the *opposite* of the
usual one: the reader may hope CGP "just finds" the implementation, and it does not.

**"Coherence exists for a reason — incoherent instances are dangerous."** The informed objection of
the reader most worth engaging, and it is justified in general: dropping coherence naively *is*
dangerous. Concede the general point and locate CGP's discipline precisely — deliberately incoherent
at the definition level and disciplined at the use site, so overlapping providers coexist but a
context names exactly one, explicitly and locally, and the choice can never be silently derailed. Do
not claim CGP is coherent. The [RustLab talk](../website/blog/rustlab-2025-coherence.md) is the model
answer, because it establishes that coherence is *correct* before working around it.

**"Extensible records mean gigantic error messages."** *Partly justified*, and one to concede: CGP's
structural operations, mis-wired, do surface as long generated-type-heavy errors. What CGP changes is
that the shape is opt-in per type rather than pervasive, and that a check forces a missing field to be
named at the wiring site. Do not claim the errors are clean; this reader has seen this movie.

**"Isn't this just an effect system / a reflection system?"** Both are misunderstandings a careless
pitch invites. The effects reader will look for continuations and CGP has none; the reflection reader
will look for a runtime query API and CGP has none. Neither is a real deficiency, but a writer who
calls CGP either thing creates the expectation and owns the disappointment. Name what CGP is with
precision — "the exactly-once, resume-in-place fragment of effect handlers", "compile-time structural
reflection encoded in the type system" — and state the limit up front.

**"Dynamic dispatch is flexible — won't a static version lose what makes it useful?"** *Justified and
to be granted fully*: CGP genuinely cannot do heterogeneous collections, plugins loaded at startup, or
live redefinition. Say plainly that runtime openness lives on the runtime side where `dyn Trait` and
the dynamic languages remain right, then offer what is on CGP's side: duck typing that cannot throw,
and dynamic dispatch that costs nothing. Frame its late binding as late to the *wiring site*.

### Native to the Rust audience

**"This is too clever / over-engineered."** A reasonable prior rather than a misunderstanding — most
abstractions that announce a paradigm do not earn their cost. The failure mode is answering it with
more enthusiasm about the paradigm, which confirms the fear. Answer with problem-first restraint: a
concrete pain shown gone on ordinary-looking code, and an explicit statement of when *not* to reach for
CGP. The reader who watches the author decline to apply CGP everywhere believes them about where it
does belong.

**"Macros are magic — I can't see what they generate."** *Partly justified*: generated code is harder
to inspect than hand-written code. Replace "magic" with "explicit" and point at the seams — the wiring
is a table you write and read, the dependencies are declared, the expansion is specified, and
[`cargo cgp expand`](../cgp/reference/cargo-cgp.md) prints it with CGP's type-level constructs
resugared. Concede that debugging generated code is a real cost; overclaiming transparency loses
exactly the reader you are addressing.

**"I can't tell which code actually runs on a method call."** A specific worry distinct from the macro
complaint, which appeared verbatim in CGP's own community discussion ([evidence.md](evidence.md)), and
is *partly justified*: CGP does add a hop between a consumer call and the provider answering it.
Concede the hop and point at the map: unlike runtime dispatch, the indirection is statically resolved
and explicit, and the `delegate_components!` table is a single greppable place naming exactly one
provider per component.

**"What does this do to compile times?"** Justified and specific. Concede the direction and decline to
invent a magnitude: CGP adds compile-time work, no number should be quoted that cannot be cited, and
the honest reframing is that resolution costing at compile time is resolution that would otherwise
cost at runtime or not be checked at all. The author's own
[Hypershell post](../website/blog/hypershell-release.md) is the model here — it explains what he has
observed, distinguishes fast library builds from slow executable instantiation, and admits the
evidence is rough.

**"The error messages are a wall of generated types."** Justified, the cost most likely to bite a real
user, and the one whose answer has changed. Concede the raw diagnostics, then point at
`check_components!` and at `cargo cgp check`, which un-hides the cause the default solver suppresses
and leads with it. Concede the tool's youth in the same breath — v0.1.0-alpha, core classes only —
because the reader can install it and check within the hour. **Dramatically better and actively
improving, not solved.**

**"Rust doesn't need dependency injection — that's a Java-ism."** The *native* version of the DI
objection, and *partly justified*: for many cases a trait-bounded generic genuinely is right and a DI
framework would be over-engineering, which is why Rust's DI crates stay niche
([evidence.md](evidence.md)). Agree rather than argue. Concede that Rust needs no DI *framework* and
that CGP is not one — it is the traits-and-generics approach the reader already endorses, carried to
the cases where doing it by hand stops scaling — then locate those cases concretely: overlapping impls
the coherence rules reject, a type you do not own, a public trait leaking internal types.

**"Why not just use traits, generics, or an enum?"** Often the right question. Concede the range where
the plainer tool wins and draw the line where CGP starts to pay, pointing at the
[modularity hierarchy](../cgp/concepts/modularity-hierarchy.md) as the map of when to climb.

**"It's immature — can I bet a codebase on it?"** The evaluator's central, justified concern, and it
cannot be answered by enthusiasm. Be honest that CGP is young, then lower the stakes truthfully: it is
a superset of ordinary traits, so it can be adopted in one corner and stepped back from, and it
imposes no runtime, so it does not lock a project into a framework's lifecycle. The site's
[Introduction page](https://contextgeneric.dev/docs/) already does this well and should not be
softened.

**"There's a learning curve."** Justified, and simply to be granted — denying it insults the reader.
Shrink the *first step* rather than the whole curve: the first useful thing, a capability defined as a
function and used with no wiring, takes only ordinary Rust knowledge, and the deeper machinery can be
learned as needed. The curve is real but not a cliff.

## When not to reach for CGP

Drawing CGP's boundary in public is a positioning asset rather than a concession, because the instinct
to sell a tool as universally better is exactly the instinct this audience punishes. The one principle
that settles most cases: **use CGP when a capability needs more than one implementation and the choice
belongs to the context — not before.** The full ladder is the
[modularity hierarchy](../cgp/concepts/modularity-hierarchy.md); this is its compression.

The recurring question is not "is CGP good" but "CGP or this other thing", so the guide below takes the
alternatives a reader actually weighs and concedes each one's home ground first.

- **A plain trait or generic.** Prefer it when a capability has one implementation, or one per type
  with a single global choice — this is most code. Reach for CGP when the implementations multiply,
  when the choice must differ per context, or when threading a generic through every layer has begun
  to hurt. CGP is a *superset* of this approach, so it is a climb rather than a rejection.
- **An enum.** Prefer it for a small, closed, known set of variants with fixed operations — a match is
  clearer than any machinery. Reach for [extensible variants](../cgp/concepts/extensible-variants.md)
  when the variant set is open or independent modules must each contribute one.
- **`dyn Trait` and runtime dispatch.** Prefer it when the set of implementations is not known until
  runtime; that openness is exactly what CGP gives up. Reach for CGP when the set *is* known at build
  time. This is a genuine either/or and a piece should say so.
- **A dependency-injection crate.** Prefer a runtime container only when you specifically want its
  lifecycle and object-graph semantics. Reach for CGP when you want compile-time-checked,
  reflection-free injection — and frame it as the traits-and-generics approach rather than a framework.
- **A generic-programming toolbelt like `frunk`.** Prefer the lighter library for a one-off `HList`
  manipulation. Reach for CGP's [extensible data](../cgp/concepts/extensible-records.md) when the
  structural machinery is part of a larger component-and-wiring design.
- **A hand-rolled macro.** Prefer a small bespoke macro when the generation is narrow. Reach for CGP
  when you find yourself reinventing its mechanism — which developers demonstrably do.
- **Waiting for a language feature.** Prefer waiting when a first-class facility would serve better and
  you can afford to; Rust's effects and reflection work is pursuing built-in versions of ground CGP
  covers. Reach for CGP when you need the capability now, on stable Rust — and say that CGP is
  complementary to what the language is building rather than a bet against it.

A few cases are not trade-offs but clear misfits, and saying so plainly is the most trust-building move
available. CGP cannot provide **runtime dynamism**. A capability with **exactly one implementation**
belongs in a plain trait. A **small closed variant set** belongs in an enum. And when a program
genuinely wants **one instance program-wide** — a single globally consistent `Ord` for a map key —
CGP's per-context choice is the wrong shape, and coherent type classes or a plain trait are safer.
Naming that last case is especially disarming to the advanced reader who raised the coherence
objection, because it shows CGP knows the limit of its own bargain.

Say it like this: *"For one implementation, use a trait. CGP earns its keep when you need several,
chosen per context."* *"If your set of implementations is known at compile time, CGP gives you the
decoupling of `dyn` with none of the cost. If it isn't, use `dyn`."* *"Reach for the lowest rung that
solves your problem; CGP is a rung you climb to deliberately, not a default."*

## Keeping this document honest

Every factual claim here is bound by the [synchronization rule](../AGENTS.md#the-synchronization-rule)
exactly as a reference document's Expansion is: verify against the source and the `/cgp` skill before
shipping, and prefer the idioms the [guides](../cgp/guides/README.md) teach. Because the four halves
are four views of one reader, an edit to a capability should check whether its matching pain, its
objection, and its boundary need the same edit. The wording rules the sections above apply are
consolidated in [vocabulary.md](vocabulary.md), which resolves any disagreement; the sentiment behind
each imported objection is cited in the [related-work](../related-work/README.md) documents, and the
audience facts in [evidence.md](evidence.md).
