# Algebraic effects and handlers

Algebraic effects and handlers separate side-effecting *operations* (throwing, reading state,
yielding, awaiting) from the *handlers* that interpret them, so one piece of effectful code can run
under many interpretations. A handler may capture the rest of the computation as a continuation and
resume it zero, one, or many times. CGP shares the split between an operation and its interpretation,
and the idea of choosing the interpretation from the surroundings, but it keeps only the fragment in
which the continuation is used exactly once and in place. The literature identifies that fragment as
dynamic binding, and CGP resolves it statically per context rather than dynamically down a call stack.

## Purpose

Algebraic effects let code perform an effect without fixing how the effect is carried out. A function
that reads a configuration value, logs a message, throws an error, suspends for I/O, or makes a
nondeterministic choice normally commits to a concrete mechanism: a global, a `Result`, a monad, a
callback. That commitment leaks into its type and forces every caller to accommodate it. With
algebraic effects the function instead *performs an operation* named by an abstract effect, and a
*handler* installed somewhere up the call stack gives the operation its meaning. The same code runs
against a real logger in production, a collector in a test, and a no-op in a benchmark, with only the
handler changing.

CGP draws the same separation between a [consumer trait and its providers](../cgp/concepts/consumer-and-provider-traits.md),
so the comparison deserves care. Both paradigms expose an operation as an interface a caller invokes
without naming an implementation, and both supply the implementation from the surroundings. They
diverge on *what a handler may do* and *how the surroundings choose it*. An effect handler receives
the continuation and holds real control-flow power, and dynamic scope chooses it. A CGP provider is an
ordinary function, and the context's type chooses it at compile time. This document shows where that
line falls and why CGP sits on the side of it that coincides with dynamic binding. It also leans on the
[row polymorphism](row-polymorphism.md) comparison, because the effect systems that type these
operations use the row types that document covers.

## The concept in depth

Algebraic effects come in layers that are worth keeping distinct: the *operations* that name an
effect, the *equational theory* that classically justifies the word "algebraic", the *handlers* that
interpret operations by taking the continuation, the *effect system* that types which operations a
computation may perform, and the language designs (Koka, OCaml, Flix, Eff) that realize these to
different degrees. The subsections build up in that order, and the final one isolates the single
fragment CGP corresponds to.

### Operations, effects, and the equational theory

An *effect* is a signature of *operations*, and a computation produces the effect by *performing* one
of them. Gordon Plotkin and John Power founded the idea: impure behavior arises from a set of
operations such as `get` and `put` for mutable state, `read` and `print` for I/O, and `raise` for
exceptions, rather than from an opaque notion of "side effect"
([Plotkin & Pretnar, *Handling Algebraic Effects*](https://homepages.inf.ed.ac.uk/gdp/publications/handling-algebraic-effects.pdf)).
The account is *algebraic* because each effect came with an *equational theory*: laws the operations
obey, such as the state laws relating `get` and `put`, whose free model induces the monad for that
effect ([Plotkin & Pretnar 2013](https://lmcs.episciences.org/705);
[Bauer & Pretnar, *Programming with Algebraic Effects and Handlers*](https://www.researchgate.net/publication/221671686_Programming_with_Algebraic_Effects_and_Handlers)).
This grounding is where the name comes from, but the practical languages below keep the
operations-and-handlers structure and drop the laws. That matters for the comparison, because CGP
keeps even less of the algebra than they do.

### Handlers and the continuation

A *handler* interprets the operations of an effect, and its defining power is that it receives the
*continuation*: the suspended rest of the computation from the point where the operation was
performed. When a computation performs `op(arg)`, control transfers to the nearest enclosing handler
for that operation, which receives both the argument and the continuation as a first-class, delimited
resumption ([Pretnar, *An Introduction to Algebraic Effects and Handlers*](https://www.eff-lang.org/handlers-tutorial.pdf)).
This generalizes an exception handler in one decisive way. An exception handler can only *abandon*
the computation, whereas an effect handler can *resume* it. Plotkin and Pretnar gave this its
semantics: a handler is a *model* of the effect's theory, and handling is the unique homomorphism from
the free model into it ([Plotkin & Pretnar, *Handlers of Algebraic Effects*](https://homepages.inf.ed.ac.uk/gdp/publications/Effect_Handlers.pdf)).

How many times a handler invokes the continuation determines the effect it realizes. The three cases
mark exactly where CGP can and cannot follow:

- **Zero times.** The handler discards the continuation and returns its own value. This is
  *exception* behavior: `raise` aborts to the handler and never comes back.
- **Once.** The handler resumes the continuation with a result. This is the *ordinary* case: reading
  state, dynamic binding, logging, or any function-like call that yields a value and lets the caller
  carry on.
- **Many times.** The handler resumes the continuation more than once. This is what makes effects
  powerful: nondeterminism and backtracking (try both branches), generators (yield and later resume),
  and cooperative scheduling and async/await (suspend, run something else, resume). This *multi-shot*
  resumption cannot be expressed as an ordinary function return.

### Effect typing: rows, sets, or nothing

An *effect system* records in a computation's type which effects it may perform, so an unhandled
effect can be caught statically. Languages differ sharply in whether they do this. Koka types effects
as a *row*: `<exn,div>` in a signature means the function may throw and diverge, and the row machinery
is the one surveyed in [row polymorphism](row-polymorphism.md), applied to effects instead of records
([Leijen, *Algebraic Effects for Functional Programming*](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/algeff-tr-2016-v2.pdf)).
Flix types effects as a *set* over a lattice and uses the result for *purity reflection*, so the
compiler knows when code is pure enough to parallelize or eliminate
([Madsen et al., *Programming with Purity Reflection*](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2023.18)).
At the other extreme, Eff and OCaml 5 track no effects in types at all. The OCaml manual says plainly
that "the compiler does not statically ensure that all the effects performed by the program are
handled", and an unhandled effect raises `Effect.Unhandled` at run time
([OCaml manual, *Effect handlers*](https://ocaml.org/manual/5.5/effects.html)). This static check is
the sharpest axis of variation among the languages, and the one where CGP's `check_components!` has
something precise to say.

### The concept in three languages

The same effect looks recognizably similar across the languages that implement it, which makes their
differences legible. Each snippet below was checked against the language's current documentation, and
the OCaml and Flix ones were compiled.

In **Koka**, an operation is declared as `ctl` (full control, may resume any number of times), `fun`
(tail-resumptive, resumes exactly once in place), or `val` (a constant). An effect that has a single
operation may be declared with the operation alone, and the effect takes the operation's name. A
handler is installed with `with`:

```koka
effect fun ask() : int      // one `fun` operation; the effect is also named `ask`

fun add-twice() : ask int
  ask() + ask()

fun main() : console ()
  with fun ask() 21         // install a handler that supplies 21
  println( add-twice() )    // 42
```

The Koka book describes `with fun ask() 21` as a "statically typed dynamic binding" and notes that a
`fun` operation "behaves just like a regular function without changing the control-flow"
([Koka book, *Tail-Resumptive Operations*](https://koka-lang.github.io/koka/doc/book.html#sec-opfun)).
A `ctl` operation is the multi-shot form. The book's `choice` handler resumes twice to collect every
outcome of a nondeterministic computation:

```koka
effect ctl choice() : bool

fun choice-all(action : () -> <choice|e> a) : e list<a>
  with handler
    return(x)    [x]
    ctl choice() resume(False) ++ resume(True)
  action()
```

If an effect is never handled, Koka keeps it in the row and the type checker demands that the
enclosing function declare it, so an unhandled effect is a *type error*.

In **OCaml 5**, an effect is declared by extending the extensible type `Effect.t`, performed with
`perform`, and handled with a `match` or `try` whose `effect` cases bind the continuation `k`, resumed
with `continue`. The `effect` pattern syntax arrived in OCaml 5.3; earlier code used the
`Effect.Deep.try_with` function, which still works:

```ocaml
open Effect

type _ Effect.t += Ask : int Effect.t

let add_twice () = perform Ask + perform Ask

let () =
  let result =
    match add_twice () with
    | v -> v
    | effect Ask, k -> Effect.Deep.continue k 21
  in
  print_int result   (* 42 *)
```

OCaml's continuations are **one-shot**. The manual states that "every captured continuation must be
resumed either with a `continue` or `discontinue` exactly once", and a second resume raises
`Continuation_already_resumed` ([OCaml manual](https://ocaml.org/manual/5.5/effects.html)). The
restriction was chosen because one-shot continuations are far cheaper and suffice for the concurrency
schedulers the feature was built for ([Sivaramakrishnan et al., *Retrofitting Effect Handlers onto OCaml*](https://kcsrk.info/slides/handlers_edinburgh.pdf)).

In **Flix**, an effect is declared with `eff`, appears in a function type after a backslash, and is
handled with `run ... with handler`. A handler clause for an operation receives the continuation as
its last parameter:

```flix
eff Ask {
    def ask(): Int32
}

def addTwice(): Int32 \ Ask =
    Ask.ask() + Ask.ask()

def main(): Unit \ IO =
    let result = run {
        addTwice()
    } with handler Ask {
        def ask(k) = k(21)
    };
    println(result)   // 42
```

Flix's set-based effect system makes `\ Ask` part of `addTwice`'s type, and `main` must discharge it,
which is why `main` carries only `\ IO` ([Flix documentation, *Effects and Handlers*](https://doc.flix.dev/effects-and-handlers.html)).

### The fragment CGP corresponds to: tail-resumptive handlers are dynamic binding

A handler that resumes the continuation exactly once, in tail position, does nothing
control-theoretic. It is dynamic binding. A handler is *tail-resumptive* when every operation clause
invokes the continuation in tail position, and the literature names its canonical example outright:
**the canonical tail-resumptive handler is dynamic binding**
([Xie et al., *Effect Handlers, Evidently*](https://www.microsoft.com/en-us/research/wp-content/uploads/2020/07/evidently-5f0b7dbc1a998.pdf)).
This matters for implementation, and for CGP, because such a handler never needs to capture the
continuation. The compiler can run the operation *in place* on the current stack and replace the
dynamic search for a handler with a constant-offset lookup into an *evidence vector* of handlers passed
down like a dictionary ([Xie & Leijen, *Generalized Evidence Passing for Effect Handlers*](https://xnning.github.io/papers/multip.pdf)).
The Koka book says the same of its `fun` operations: the compiler "uses (generalized) evidence passing
to pass down handler information to each call-site". So the efficient compilation of the exactly-once
fragment of effect handlers *is* dictionary passing. That is the fragment CGP occupies, directly, with
no dynamic search underneath and nothing else on top.

## How CGP expresses it

CGP reproduces the operations-and-handlers structure with its consumer/provider split, but every CGP
"handler" is an ordinary function that returns once, so CGP realizes only the exactly-once fragment. A
[component](../cgp/reference/macros/cgp_component.md) is the effect signature, a
[provider](../cgp/reference/macros/cgp_impl.md) is the handler, and
[wiring](../cgp/reference/macros/delegate_components.md) installs the handlers on a context. The
correspondence is exact for the tail-resumptive case and breaks cleanly wherever an effect would reach
for the continuation. The snippets below wire an **environmental context**: the `App` that installs a
`Loader` or a `Greeter` stands for an application, which is the shape an effect handler's dynamic scope
also stands for, and every component shown is self-targeted.

### Components are effect signatures; providers are tail-resumptive handlers

A CGP component declares operations the way an effect declares them, and a provider interprets them
the way a handler does, with one standing restriction: the interpretation is a plain function body.
Declaring a component names an operation without giving it meaning:

```rust
#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}
```

`CanGreet` is the effect signature and `greet` the operation. A provider written with
[`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md) is the handler, interpreting the operation for
any context. The structural match is one to one: signature, operation, handler, installation. But the
provider's body receives no continuation and cannot choose whether to resume. It computes a value and
returns, and the caller resumes in place, exactly once. In Koka's terms every CGP provider is a `fun`
operation and never a `ctl` one. There is no `resume` to call zero times or twice, because there is no
reified continuation at all.

### Reading from the context is dynamic binding, exactly

Context-value access is where the correspondence is exact rather than structural, because it is
dynamic binding on both sides. Koka's `with fun ask() 21` installs a tail-resumptive handler that
supplies a value to deeply nested code without threading it through every call. CGP's
[implicit arguments](../cgp/concepts/implicit-arguments.md) do the same by reading a field from the
context that every provider receives as `self`:

```rust
#[cgp_fn]
pub fn greet(&self, #[implicit] name: &str) -> String {
    format!("Hello, {name}!")
}
```

The context supplies `name`, not the caller, exactly as the enclosing `ask` handler supplies Koka's
`ask()` rather than `add-twice`'s caller. This is the same pattern the
[implicit parameters](implicit-parameters.md) comparison describes, and the equivalence is not a
loose analogy: the reader effect *is* the canonical tail-resumptive handler, and reading a context field
*is* CGP's whole realization of it. The two part ways on *how the value is found*. Koka searches the
dynamic handler stack, while CGP reads a field of a statically known context. That is the same
resolution split that separates CGP from every dynamically scoped mechanism.

### Raising an error looks like `raise` but passes a value, not control

CGP's error handling shows the boundary most sharply. It mimics the *selection* of an exception handler
while doing none of the *control transfer*.
[`CanRaiseError<SourceError>`](../cgp/reference/components/can_raise_error.md) reads like the `raise`
operation, and a provider raises without knowing the concrete error type:

```rust
#[cgp_impl(new LoadOrFail)]
#[uses(CanRaiseError<String>)]
#[use_type(HasErrorType.Error)]
impl Loader {
    fn load(&self, path: &str) -> Result<String, Error> {
        if path.is_empty() {
            return Err(Self::raise_error("empty path".to_owned()));
        }
        Ok(format!("contents of {path}"))
    }
}
```

The raise-and-wrap components dispatch per source type, so a context can route each source error to a
different strategy through the [`open` statement](../cgp/reference/macros/delegate_components.md):
`RaiseFrom` for a `String`, `DebugError` for a `ParseError`, as
[modular error handling](../cgp/concepts/modular-error-handling.md) describes. That reads like
installing one exception handler per exception type. But the resemblance stops at *selection*. An
effect `raise` is the *zero-resume* handler: it abandons the continuation and unwinds to the handler.
CGP's `raise_error` unwinds nothing. It *constructs and returns a value* of the abstract `Error` type,
and the actual abort is Rust's own `return` or `?` on the `Result`, entirely outside the wiring. CGP
selects the *interpretation* of the error, which is the handler-choice half, and leaves the *control
flow*, the continuation-discarding half, to `Result`. This is why CGP's dispatch is stricter than
OCaml's one-shot continuations: it is exactly-once, because the zero-resume case never reaches a CGP
provider at all.

### Impl-side dependencies are the effect row; `check_components!` is "all effects handled"

CGP records which traits a provider needs and verifies that a context supplies them, which lines up
with an effect system typing a row and demanding that it be discharged. A provider states its needs as
[impl-side dependencies](../cgp/concepts/impl-side-dependencies.md): the
`#[uses(CanRaiseError<String>)]` above, and every bound in a `where` clause. That list is the CGP
counterpart of the effect row `<exn>` Koka would infer for a function that performs `raise`. A generic
provider is even effect-*polymorphic* in a loose sense: the context type variable plays a role like
Koka's row variable, standing for "whatever else this context can do". And
[`check_components!`](../cgp/reference/macros/check_components.md) is the discharge check:

```rust
check_components! {
    App {
        LoaderComponent,
    }
}
```

This asserts that `App` supplies every trait `LoadOrFail` transitively needs, and it fails to compile
naming the missing one if not. That is Koka's guarantee that a program with an unhandled effect in its
row is a type error, and the opposite of OCaml's runtime `Effect.Unhandled`. CGP lands on the
statically checked end of the effect-typing axis, reached through trait resolution rather than a
dedicated effect system.

### Configuring abstract types through the same wiring

CGP extends the operations-and-handlers wiring to something effect systems do not touch: abstract
*types*. Alongside choosing the provider for an operation, a context chooses the concrete type behind an
[abstract type](../cgp/concepts/abstract-types.md), such as its `Error`, `Scalar`, or `Runtime`,
through the same [`delegate_components!`](../cgp/reference/macros/delegate_components.md) table, by
wiring a [`#[cgp_type]`](../cgp/reference/macros/cgp_type.md) component to
[`UseType<T>`](../cgp/reference/providers/use_type.md):

```rust
use cgp::core::error::ErrorTypeProviderComponent;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<anyhow::Error>,
    }
}
```

An effect handler interprets operations, which are values and computations. It has no notion of
supplying a *type member* the way `HasErrorType` supplies `Error`. CGP unifies both under one wiring
mechanism, so the table that says "raise errors this way" also says "and the error type is
`anyhow::Error`". This is a feature beyond the effect-handler analogy rather than a restatement of it.

### What CGP cannot express

The multi-shot power of effect handlers has no CGP analogue, and this is the honest limit of the
comparison. A provider is an ordinary function that returns once, so CGP cannot express any effect
whose handler resumes the continuation zero times or more than once. Generators, backtracking search,
cooperative scheduling, and async/await, the applications that motivate effect handlers in the first
place ([Kammar, Lindley & Oury, *Handlers in Action*](https://denotational.co.uk/publications/kammar-lindley-oury-handlers-in-action.pdf)),
all require capturing the continuation and lie outside CGP's model. CGP does have an
[async handler family](../cgp/concepts/handlers.md) and [type-level DSLs](../cgp/concepts/type-level-dsls.md)
that interpret a `Code` tag by dispatching to a provider, which is the closest CGP comes to the
operations-and-interpreters shape. Even there the interpretation is a straight call chain resolved at
compile time, not a captured continuation the handler controls. Async in CGP is Rust's own `async` and
`await` threaded through provider calls, not a handler that suspends and resumes a computation.

### A closer theoretical fit: coeffects

CGP's author has suggested, in the unpublished draft recorded in
[incoherent-rust-today.md](../website/blog/incoherent-rust-today.md), that the *coeffect* framework
describes CGP more precisely than the effect framework does. Where an effect describes what a
computation produces or performs, a coeffect describes what a computation *requires from its
environment* ([Petricek, *Coeffects*](https://tomasp.net/coeffects/)).
A CGP context carries exactly such requirements: the implementation choices and values a computation
depends on, resolved all at once when a concrete context is defined. This framing also explains the
abstract-type extension above, which an effect handler has no place for and a contextual requirement
does. The connection is a pointer rather than a developed account, and a piece written for a
type-theory audience may find it the more accurate word.

## What users like and dislike

Algebraic effects are among the most admired ideas in current language research, and practitioners
value them for consistent, concrete reasons. The headline benefit is the end of *function coloring*:
code between the operation and its handler needs no awareness of the effect, so effectful and pure
code compose without the `async`/`sync` or `IO`-tainted split that other approaches impose
([Abramov, *Algebraic Effects for the Rest of Us*](https://overreacted.io/algebraic-effects-for-the-rest-of-us/)).
Users also prize the clean separation between an effect's *interface*, its operations, and its
*semantics*, the handler, which makes the same code testable under a mock handler and runnable under a
real one. They prize the *composability* of stacking several handlers to combine independent effects,
which is widely contrasted with the pain of monad transformers
([*Why Algebraic Effects?*, Ante](https://antelang.org/blog/why_effects/)). Where the effects are
typed, as in Koka and Flix, the row or set in a signature is valued as documentation of what a function
may do, and Flix turns that information into automatic parallelization and dead-code elimination.

The complaints are equally consistent and fall into three clusters. The loudest is *unfamiliarity and
control-flow opacity*. The concept is new to most programmers, no mainstream language ships it, and
following control from a `perform` to the handler that catches it is as hard as reasoning about a
distant exception handler: the "which handler runs this?" problem
([Ante](https://antelang.org/blog/why_effects/)). The second is *performance*. General handlers must
capture continuations, and while optimizing compilers recover much of the cost for the tail-resumptive
case through evidence passing, non-tail handlers remain more expensive than native control flow
([Xie & Leijen 2021](https://xnning.github.io/papers/multip.pdf)). The third is specific to the
untyped designs: OCaml's decision to omit effect typing means a function's signature says nothing about
the effects it performs, an unhandled effect is a runtime crash rather than a compile error, and its
one-shot restriction rules out the multi-shot uses outright
([OCaml manual](https://ocaml.org/manual/5.5/effects.html)). Readers who reach effects from Haskell
know the type-class-based effect libraries (`mtl` and its successors), whose recurring frustration is
the *n² instances* problem: every handler must supply instances delegating all the *other* effects,
which handler-based systems avoid ([`fused-effects`](https://hackage.haskell.org/package/fused-effects);
[`effet`](https://hackage.haskell.org/package/effet)).

## How CGP compares

CGP and algebraic effects make opposite choices on the two axes that define the design space, *what a
handler may do* and *how it is chosen*, and the comparison is cleanest as that pair of trades. On
*handler power*, an effect handler holds the continuation and may resume it any number of times, which
buys generators, backtracking, and async. A CGP provider is a plain function that returns once, which
buys nothing control-theoretic but costs nothing either: the call monomorphizes to a direct jump with
no continuation to capture. On *handler selection*, an effect handler is chosen by *dynamic scope*, so
the nearest handler on the runtime stack wins and a program can install a fresh handler for the same
effect at any point. A CGP provider is chosen by the context's *type* at compile time, fixed once in a
wiring table and resolved through the trait system. That second axis places CGP much closer to type
classes and implicit parameters than to effects, which is why the [dependency injection](dependency-injection.md)
and [implicit parameters](implicit-parameters.md) comparisons cover ground this one leaves to them.
Evidence passing is the bridge between the two paradigms. Koka *compiles* dynamically scoped handlers
down to dictionary passing for the tail-resumptive case, and CGP is what results if that compiled form
is the only form there ever was: evidence passing chosen by types, with no dynamic search beneath it.

Two further divergences follow and deserve plain statement. First, an effect handler *stack* is
ordered and nesting matters. The innermost handler for an operation wins, and reordering handlers
changes results: state-over-nondeterminism and nondeterminism-over-state compute different things
([Kammar, Lindley & Oury 2013](https://denotational.co.uk/publications/kammar-lindley-oury-handlers-in-action.pdf)).
CGP's wiring is a *flat* table with one provider per component, resolved by type, with no dynamic
nesting to shadow an outer handler and no order to permute. Because the dispatch is exactly-once and
resume-in-place, the non-commutativity that makes handler order significant never arises. A CGP table
is a set of handlers, not a stack of them. Second, CGP keeps even less of the "algebraic" than the
practical effect languages do: it has no equational theory relating its operations. Since Koka, OCaml,
and Flix mostly drop the laws too, this is a shared simplification rather than a CGP-specific gap.

Neither design dominates, and honest positioning names where each wins. When a program needs the
continuation, for a scheduler, a generator, a backtracking solver, or a suspendable coroutine,
algebraic effects are the right and only tool of the two. Emulating them with CGP is not possible, not
merely awkward. When a program needs many interchangeable implementations of an operation chosen per
deployment, checked statically, compiled to direct calls, and extended to abstract types as well as
operations, and needs none of the continuation power, CGP delivers that on stable Rust, where an effect
system would require a language the platform does not have. The exactly-once fragment CGP restricts
itself to is not a crippled effect system. It is dynamic binding and dictionary passing, which is a
complete and useful thing in its own right, and CGP adds to it the static per-context selection and
abstract-type configuration that effect handlers do not offer.

## Presenting CGP to someone who knows this

A reader fluent in algebraic effects already holds most of CGP's structure, so map the vocabulary and
then mark the one boundary at once. A **component is an effect signature**, its methods are
**operations**, a **provider is a handler**, and **wiring installs the handlers** on a context. A
provider's `where` bounds are the **effect row** it performs, and **`check_components!` guarantees that
every effect is handled**, the static version of Koka's unhandled-effect type error rather than
OCaml's runtime crash. Reading a context field is **dynamic binding**, and here the correspondence is
exact rather than approximate: dynamic binding *is* the canonical tail-resumptive handler, and reading a
field is CGP's whole realization of it. Framed this way, CGP is the *tail-resumptive corner* of the
paradigm this reader knows, made static and type-directed.

Draw the continuation boundary before it misleads. This reader will assume a CGP provider can resume,
abort, or fork the computation the way a handler can, and it cannot. A provider is an ordinary function
that returns exactly once, so there is no `resume` to call zero times or twice, and every multi-shot
use they value (generators, async, backtracking) lies outside CGP entirely. Present that as the
deliberate location of CGP in the design space rather than as a missing feature: CGP takes the fragment
of effect handlers that the literature already identifies as dynamic binding, the fragment that compiles
to direct calls with no continuation capture, and builds everything on it. The pitch that lands is
"effect handlers minus the continuation, resolved by type instead of by dynamic scope, and extended to
abstract types", which turns what could read as a limitation into a precise and defensible design
choice. For the Koka or Flix reader, lean on the shared row intuition: their effect row and CGP's
impl-side dependencies are the same idea, and `check_components!` discharges it the same way their type
checker does. For the OCaml reader, the resonant point is that CGP recovers the *static* discharge
check their language chose to forgo, without effect typing bolted onto the language. For anyone who has
fought monad transformers or `mtl`'s n² instances, the framing is that CGP composes operations without
either: a flat table of per-context handlers, with no stacking order to get wrong.

Avoid calling CGP "an effect system". It has no continuations, no dynamic scope, and no effect kind in
the type system, and a reader sold on that framing will look for `resume` and feel misled when it is not
there. Say precisely what CGP is: the exactly-once, resume-in-place fragment of effect handlers, which
is dynamic binding, made into a compile-time, per-context, type-directed wiring mechanism that also
configures abstract types. A reader who knows how much effect-handler machinery exists to tame the
continuation will recognize that a paradigm which never captures one has bought real simplicity, and
will hear the trade as considered rather than as a shortfall.

## Sources

The account of the related work draws on the primary research literature on algebraic effects and their
compilation, the official documentation of Koka, OCaml, and Flix, and cited community writing for
sentiment. The Koka `ask` snippet was compiled with Koka 3.2.3 and the `choice` handler follows the
Koka book's own example; the OCaml snippet was compiled with OCaml 5.5.0 and the Flix snippet run with
Flix 0.76.0. The CGP snippets are drawn from
the knowledge base's [consumer/provider](../cgp/concepts/consumer-and-provider-traits.md),
[implicit arguments](../cgp/concepts/implicit-arguments.md), and
[modular error handling](../cgp/concepts/modular-error-handling.md) documents.

- [Plotkin & Pretnar, *Handling Algebraic Effects* (LMCS 2013)](https://homepages.inf.ed.ac.uk/gdp/publications/handling-algebraic-effects.pdf) ([journal page](https://lmcs.episciences.org/705)) and [*Handlers of Algebraic Effects* (ESOP 2009)](https://homepages.inf.ed.ac.uk/gdp/publications/Effect_Handlers.pdf) — the foundational account of effects as operations with an equational theory and handlers as models interpreting them through the continuation.
- [Pretnar, *An Introduction to Algebraic Effects and Handlers*](https://www.eff-lang.org/handlers-tutorial.pdf) and [Bauer & Pretnar, *Programming with Algebraic Effects and Handlers*](https://www.researchgate.net/publication/221671686_Programming_with_Algebraic_Effects_and_Handlers) — an accessible tutorial and the Eff language, an untyped research realization.
- [Leijen, *Algebraic Effects for Functional Programming* (Koka)](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/algeff-tr-2016-v2.pdf) and [The Koka Programming Language book](https://koka-lang.github.io/koka/doc/book.html) — Koka's row-typed effects, the `ctl`/`fun`/`val` operation kinds, the single-operation `effect fun` shorthand, the `with fun` handler form, the `choice` multi-resume example, and the statement that `fun` operations are compiled by evidence passing.
- [Xie et al., *Effect Handlers, Evidently* (ICFP 2020)](https://www.microsoft.com/en-us/research/wp-content/uploads/2020/07/evidently-5f0b7dbc1a998.pdf) ([ACM](https://dl.acm.org/doi/abs/10.1145/3408981)) and [Xie & Leijen, *Generalized Evidence Passing for Effect Handlers* (ICFP 2021)](https://xnning.github.io/papers/multip.pdf) — the result that the canonical tail-resumptive handler is dynamic binding, and the evidence-passing (dictionary-passing) compilation of the exactly-once fragment.
- [OCaml manual, *Effect handlers* (5.5)](https://ocaml.org/manual/5.5/effects.html) and [Sivaramakrishnan et al., *Retrofitting Effect Handlers onto OCaml* (PLDI 2021)](https://kcsrk.info/slides/handlers_edinburgh.pdf) — the `perform` and `match ... with effect` syntax introduced in 5.3, one-shot continuations and `Continuation_already_resumed`, the absence of effect typing, and the runtime `Effect.Unhandled`.
- [Flix documentation, *Effect System*](https://doc.flix.dev/effect-system.html) and [*Effects and Handlers*](https://doc.flix.dev/effects-and-handlers.html), with [Madsen et al., *Programming with Purity Reflection* (ECOOP 2023)](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2023.18) — Flix's set-based effect system, its `eff` and `run ... with handler` syntax, the `Unit \ IO` type of `main`, and purity reflection.
- [Kammar, Lindley & Oury, *Handlers in Action* (ICFP 2013)](https://denotational.co.uk/publications/kammar-lindley-oury-handlers-in-action.pdf) — handler composition, the significance of handler order, and the range of effects handlers express.
- [Petricek, *Coeffects: Context-aware programming languages*](https://tomasp.net/coeffects/) — the coeffect framework, which describes what a computation requires from its environment and is the closer theoretical fit CGP's author has pointed to.
- [Abramov, *Algebraic Effects for the Rest of Us*](https://overreacted.io/algebraic-effects-for-the-rest-of-us/) and [*Why Algebraic Effects?* (Ante)](https://antelang.org/blog/why_effects/) — community accounts of what users value (no function coloring, composability, interface/semantics separation) and dislike (novelty, control-flow opacity, performance).
- [`fused-effects`](https://hackage.haskell.org/package/fused-effects) and [`effet`](https://hackage.haskell.org/package/effet) — the type-class-based effect libraries and the `mtl` n²-instances problem, for the Haskell reader's point of comparison.
