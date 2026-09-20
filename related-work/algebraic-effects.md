# Algebraic effects and handlers

Algebraic effects and handlers separate side-effecting *operations* (throwing, reading state,
yielding, awaiting) from the *handlers* that interpret them, so one piece of effectful code can run
under many interpretations. A handler may capture the rest of the computation as a continuation and
resume it zero, one, or many times. CGP shares the split between an operation and its interpretation,
and the idea of choosing the interpretation from the surroundings, but its closest correspondence is with handlers that resume in place. CGP selects providers
statically per context and does not expose a captured continuation. This is a structural comparison,
not an effect-typing or termination guarantee.

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
ordinary function, and the context's type chooses it at compile time. This document explains
that boundary and the related environment-passing pattern. It also leans on the
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
  useful for nondeterminism and backtracking (try both branches). Generators and cooperative
  schedulers can instead suspend and later resume a continuation once. This *multi-shot*
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

Tail-resumptive handlers provide the closest comparison to CGP. They resume exactly once in tail
position, so the operation can run in place without capturing the rest of the computation.
[Xie et al.](https://www.microsoft.com/en-us/research/wp-content/uploads/2020/07/evidently-5f0b7dbc1a998.pdf)
identify dynamic binding as the canonical example. Evidence-passing implementations can make
handler selection efficient by passing evidence of the selected handler, as developed in
[Generalized Evidence Passing](https://xnning.github.io/papers/multip.pdf).

CGP uses a related separation of operation and implementation, with selection resolved through
Rust traits. This is a comparison of programming structure, not a claim that CGP implements the
same effect calculus or dynamic scoping rules. The [capabilities](capabilities.md) page explores
the related view of computations declaring what they require from an environment.

## How CGP expresses it

CGP represents an operation with a consumer trait and its implementation with a provider.
The examples use environmental contexts: types representing applications and supplying the
implementations for self-targeted components. Supporting declarations and imports are omitted
where they do not affect the comparison.

### Components declare operations; providers implement them

A component declares an operation independently of its implementation. A context then selects a
provider through wiring:

```rust
#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}

#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self) {
        println!("Hello!");
    }
}

delegate_components! { App { GreeterComponent: GreetHello } }
```

`CanGreet` declares `greet`, `GreetHello` implements it, and `App` selects that implementation.
The provider receives the context rather than a continuation. If the method returns normally,
its caller continues once at the call site. Like any Rust function, the method can also panic or
diverge; CGP does not enforce termination or an exactly-once return guarantee.

### Context fields supply an environment value

CGP's [implicit arguments](../cgp/concepts/implicit-arguments.md) let nested implementations read
values from a shared context. This resembles a reader effect whose handler supplies an environment
value:

```rust
#[cgp_fn]
pub fn greet(&self, #[implicit] name: &str) -> String {
    format!("Hello, {name}!")
}
```

The `name` argument comes from the context's field. Koka's `ask` example supplies a value through
an installed handler; CGP supplies it through `self`. The similarity is that intermediate callers
do not forward the individual value. The difference is selection: a CGP field dependency is
resolved against a context type, without dynamic handler installation. The
[implicit parameters](implicit-parameters.md) comparison develops that distinction.

### Raising an error constructs a value

CGP's error components choose how to construct an error, while Rust's `Result` controls propagation.
This provider can produce an error without fixing the context's concrete error type:

```rust
#[cgp_component(Loader)]
#[use_type(HasErrorType.Error)]
pub trait CanLoad {
    fn load(&self, path: &str) -> Result<String, Error>;
}

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

The context chooses both the error type and the provider used for each source error type:

```rust
delegate_components! {
    App {
        open ErrorRaiserComponent;

        ErrorTypeProviderComponent: UseType<String>,
        LoaderComponent: LoadOrFail,

        @ErrorRaiserComponent.String: RaiseFrom,
    }
}
```

`Self::raise_error(...)` returns an error value; the surrounding `return Err(...)` exits `load`.
A caller can then propagate that result with `?`. An aborting effect handler instead abandons the
captured continuation. CGP's wiring supplies error-construction behavior without adding that
control-flow mechanism. [Modular error handling](../cgp/concepts/modular-error-handling.md) explains
the error components in detail.

### Dependency checks verify the selected providers

A provider's impl-side dependencies state the traits and fields it needs from a context.
For example, `LoadOrFail` requires `CanRaiseError<String>`. A check verifies those requirements
transitively for the selected implementation:

```rust
check_components! {
    App {
        LoaderComponent,
    }
}
```

The compiler rejects this check if `App` cannot satisfy a required dependency. This resembles
checking that required operations have implementations, but it is not an effect-row check.
CGP does not track every effect a provider body can perform: the body may still print, mutate
state, or panic through ordinary Rust APIs. The
[impl-side dependencies](../cgp/concepts/impl-side-dependencies.md) page explains the guarantee.

### Configuring abstract types through the same wiring

CGP wiring can select associated types as well as operation implementations. This independent
configuration chooses the context's error type:

```rust
use cgp::core::error::ErrorTypeProviderComponent;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<anyhow::Error>,
    }
}
```

The same table can therefore select error-construction behavior and the concrete `Error` type.
This follows from Rust's associated types and CGP's
[abstract-type components](../cgp/concepts/abstract-types.md). It is an additional use of the wiring
mechanism, separate from the comparison with handlers interpreting operations.

### A related theoretical view: coeffects

Coeffects offer another way to describe CGP's declared context dependencies. An effect describes
what a computation does; a coeffect describes what it requires from its environment.
[Petricek's coeffects work](https://tomasp.net/coeffects/) develops that distinction. CGP's field
and trait requirements suggest such a comparison, but CGP does not implement a coeffect calculus.

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
control-flow opacity*. The concept may be unfamiliar, and following control from a `perform` to the handler that catches it is as hard as reasoning about a
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

Effect handlers separate operation use from interpretation and support reusable control-flow
abstractions. Their flexibility also makes control flow less local: understanding a `perform` may
require locating the handler and following its resumption behavior. The
[Ante language's account](https://antelang.org/blog/why_effects/) discusses both the modularity
benefit and the difficulty of following effects across a program.

Handler costs depend on the language and the resumption pattern. General handlers may capture
continuations, while tail-resumptive handlers admit simpler compilation. The evidence-passing
research documents those implementation choices and their performance trade-offs
([Xie and Leijen](https://xnning.github.io/papers/multip.pdf)). OCaml additionally restricts
continuations to one use and reports unhandled effects at runtime. Effect-typed languages move
that handling check into the type system.

CGP requires component declarations, wiring, and compile-time trait resolution. It also requires
readers to learn the consumer/provider split. Its raw diagnostics expose generated types:
[`cargo cgp check`](../cargo-cgp/reference/usage.md) leads with the root cause for the classes it recognizes,
and the tool is a v0.1.0-alpha that does not yet reshape every class. CGP does not provide
continuation handling, effect typing, or checked algebraic laws for its operations. The
[Modularity Hierarchy](../cgp/concepts/modularity-hierarchy.md) weighs its machinery against simpler
Rust abstractions.

### Where the other approach fits

Effect handlers fit abstractions that need access to the suspended computation, such as a
scheduler, generator, or backtracking interpreter. The chosen language must support the required
resumption pattern; one-shot handlers do not provide multi-shot search directly. CGP wiring alone
cannot supply this control over a continuation.

CGP can still participate in asynchronous Rust programs. Its
[async handler family](../cgp/concepts/handlers.md) uses Rust futures and `async`/`await`, and its
[type-level DSLs](../cgp/concepts/type-level-dsls.md) select interpreters through providers. These
constructs compose ordinary Rust computations; they do not add general algebraic effect handlers.

## Presenting CGP to someone who knows this

Use the operations-and-implementations correspondence, then state the continuation boundary.
A component declares operations and a provider implements them, but a provider receives the context
rather than a captured continuation. Normal return continues the caller once; Rust panic and
divergence remain possible. Do not describe this as an enforced exactly-once guarantee.

Keep dependency checking distinct from effect typing. `check_components!` verifies declared
transitive dependencies, not every effect performed by a method body. Reader-style field access
resembles supplying an environment, but CGP does not install dynamically scoped handlers.

Separate one-shot suspension from multi-shot resumption. Schedulers and generators can use one-shot
continuations; backtracking may require multiple resumptions. CGP wiring supplies neither mechanism,
though CGP providers can use Rust's async support. Wiring entries have no handler-stack order, but
provider composition and ordinary operations can still be order-sensitive.

## Sources

The public version of this document is the website's
[algebraic-effects comparison page](https://contextgeneric.dev/docs/comparisons/algebraic-effects), ported per the
[comparison page guide](../website/writing-guides/related-work.md); a change here updates that page
in the same change.

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
