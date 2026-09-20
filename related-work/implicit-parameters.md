# Implicit parameters

Implicit parameters are function arguments the compiler supplies from the surrounding context instead
of the caller passing them by hand. Scala's `given`/`using` and Haskell's `ImplicitParams` are the
direct forms, and the type-class resolution both languages build on is the same idea generalized. CGP
shares the goal of threading context through code without explicit plumbing, but it supplies the values
from a context's fields and wiring rather than from a compiler-driven search. That trade gives up
automatic resolution and gains the freedom to have many overlapping implementations.

## Purpose

Some values are needed everywhere and interesting nowhere: a configuration object, a logger, a
comparison strategy, an error type, an execution environment. Passing them explicitly through every
function that transitively needs them clutters signatures and forces intermediate functions to accept
parameters they only forward. Implicit parameters remove that clutter. The caller omits such an
argument, the compiler fills it in from what is in scope, and the value propagates through a call chain
without appearing at every call. The declaration still records the dependency in the type; only the
*passing* becomes invisible.

CGP resolves the same tension with [impl-side dependencies](../cgp/concepts/impl-side-dependencies.md)
and [implicit arguments](../cgp/concepts/implicit-arguments.md), which is why the comparison is
illuminating rather than incidental. Both CGP and the implicit-parameter languages want code deep in a
call graph to obtain what it needs from its surroundings without every caller in between having to
know. They differ in *what the surroundings are* and *how the value is found*. Scala and Haskell search
an implicit scope by type. CGP reads a field or resolves a wiring entry from the context that is already
threaded through every provider. The heart of the comparison is showing a reader that CGP's context *is*
their implicit environment, made a first-class and explicitly wired type.

## The concept in depth

Implicit parameters appear in several forms that a reader may not distinguish, and the comparison to
CGP is clearest when they are kept apart. There is the direct implicit *value* parameter (Scala's
`using`, Haskell's `ImplicitParams`), and there is the type-class mechanism (Scala's `given` type
classes, Haskell's `class` and `instance`), which is implicit resolution specialized to finding an
implementation for a type. Both rest on the compiler searching a scope by type, and both are governed by
*coherence*, the property that makes CGP's approach fundamentally different.

### Context parameters in Scala (`using` and `given`)

Scala 3 lets a parameter list be marked `using`, which makes its arguments contextual: the caller may
omit them, and the compiler supplies a matching `given` value from scope. A function that needs a
`Config` everywhere in a rendering pipeline declares it once with `using` and never threads it again:

```scala
case class Config(port: Int, baseUrl: String)

def renderWebsite(path: String)(using config: Config): String =
    "<html>" + renderWidget(List("cart")) + "</html>"    // config passed implicitly

def renderWidget(items: List[String])(using config: Config): String = ???
```

A `given` value in scope is what the compiler injects for a `using` parameter, and the caller writes
nothing:

```scala
given Config = Config(8080, "docs.scala-lang.org")

renderWebsite("/home")     // the given Config is supplied automatically
```

The mechanism generalizes to type classes, which is its most common use. A `given` can be defined *for
a type*, and a method with a `using` parameter of that type resolves the right instance from the types
at the call site. Scala 3.6 changed the syntax for a given with a body from `given Comparator[Int] with`
to a colon form; the older form is still accepted but is to be phased out
([Scala 3 Reference, *Given Instances*](https://docs.scala-lang.org/scala3/reference/contextual/givens.html)):

```scala
trait Comparator[A]:
  def compare(x: A, y: A): Int

given Comparator[Int]:
  def compare(x: Int, y: Int): Int = x - y

def max[A](x: A, y: A)(using c: Comparator[A]): A =
  if c.compare(x, y) > 0 then x else y

max(1, 2)     // Comparator[Int] resolved and passed implicitly
```

Scala uses this one mechanism for both dependency injection and type classes. A `using Config` is DI,
and a `using Comparator[A]` is a type class, which is why the language's implicits sit at the
intersection of two related-work topics; see also [dependency injection](dependency-injection.md).
Rust's own *contexts and capabilities* proposal is the nearest thing to a `using Config` parameter for
Rust, and [Rust's own proposals](rust-language-proposals.md) compares it to CGP directly.
Scala 2 wrote all of this with the single `implicit` keyword, and Scala 3 renamed it to `given` and
`using` because the old keyword was overloaded and hard to teach.

### Implicit parameters in Haskell (`ImplicitParams`)

Haskell's `ImplicitParams` extension is the more literal form of the same idea. A function can name a
dynamically bound variable `?x` of some type, which appears as a constraint `(?x :: t)` on its
signature and is filled from the binding in scope. The GHC User's Guide illustrates it with a sort that
takes its comparison as an implicit parameter. The guide's version assumes a hypothetical `sortBy` over
a `Bool` comparator; the version below uses the real `Data.List.sortBy` and compiles with GHC 9.10:

```haskell
{-# LANGUAGE ImplicitParams #-}
import Data.List (sortBy)

sort :: (?cmp :: a -> a -> Ordering) => [a] -> [a]
sort = sortBy ?cmp
```

The constraint propagates to any caller that does not bind it, so a function built on `sort` inherits
its `?cmp` without restating the intent:

```haskell
least :: (?cmp :: a -> a -> Ordering) => [a] -> a
least xs = head (sort xs)
```

A `let` binding supplies the value, discharges the constraint, and makes the function below it
ordinary:

```haskell
min' :: Ord a => [a] -> a
min' = let ?cmp = compare in least
```

`ImplicitParams` is the honest baseline for the comparison but a cautionary one, because modern
Haskell barely uses it. The constraints leak into every signature, so the parameters are not very
"implicit". There is no way to declare a default. The guide adds two further restrictions: an implicit
parameter may not appear in the context of a class or instance declaration, and GHC applies the
monomorphism restriction to implicit parameters, so an unsignatured binding is not generalized over them
([GHC User's Guide, *Implicit parameters*](https://ghc.gitlab.haskell.org/ghc/doc/users_guide/exts/implicit_parameters.html)).
Haskell programmers reach instead for the `Reader` monad to thread an environment, or, far more often,
for type classes.

### Type classes as implicit dictionary passing

Type classes are the mechanism Haskell and Scala use for the implicit-resolution job in practice, and
understanding them as *implicit dictionary passing* is what connects them to CGP. A `class` declares an
interface, an `instance` provides it for a type, and when a function constrained by the class is called,
the compiler finds the instance for the concrete type and passes it as a hidden argument: a
*dictionary* of the instance's methods. The constraint `Ord a =>` is elaborated into an extra parameter
carrying the `Ord` dictionary. Simplified from the Prelude:

```haskell
class Ord a where
  compare :: a -> a -> Ordering

instance Ord Int where
  compare x y = ...   -- the compiler builds and passes an Ord Int dictionary
```

The resolution is *type-directed and automatic*: the programmer names the constraint, and the compiler
searches for the matching instance by type, with no explicit selection. This is exactly the convenience
CGP gives up and the reason it can do something type classes cannot, so the next point is the pivot of
the whole comparison. The [type classes](type-classes.md) comparison develops the mechanism and its
extensions in full.

### Coherence: one instance, globally

*Coherence* governs type-class and implicit resolution, and CGP deliberately abandons it. Coherence
means that for a given type there is exactly one instance, and every resolution anywhere in the program
finds the same one. It is what makes automatic resolution safe. Because the compiler always finds the
same `Ord Int`, it can inject it silently without the programmer worrying that a different `Ord Int`
might be chosen elsewhere and make two pieces of code disagree. Haskell enforces this with the
orphan-instance convention and by rejecting overlapping instances by default. Scala's implicits are
coherent in the common case and rely on scoping and priority rules at the edges.

The price of coherence is the price CGP was built to escape. Because there can be only one `Ord Int`,
a program cannot have two legitimate orderings of `Int` as first-class instances. The standard
workaround wraps the type in a `newtype` so a second instance attaches to a distinct type. And a module
cannot add an instance for a type and class it does not own. These are the same overlap and orphan
restrictions Rust's own coherence imposes, described from the CGP side in
[bypassing coherence](../cgp/concepts/coherence.md). The comparison to CGP therefore comes down to a
single trade. Implicit resolution buys automatic, type-directed selection at the cost of one global
instance per type. CGP buys many overlapping per-context implementations at the cost of selecting them
explicitly.

## How CGP expresses it

CGP threads context through code and lets deep code read what it needs, but it does so through the
context that is already the `Self` of every provider, not through a scope search. The value a Scala
`using` parameter or a Haskell implicit parameter carries is, in CGP, a field of the context or an entry
in its wiring. The context is passed to every provider as the receiver, so nothing is threaded by hand.
Two CGP constructs map onto the two forms of implicit parameter.
[`#[implicit]`](../cgp/reference/attributes/implicit.md) arguments correspond to implicit *value*
parameters, and a [component](../cgp/concepts/consumer-and-provider-traits.md) with its wiring
corresponds to a type class.

### Implicit arguments are implicit value parameters

An `#[implicit]` argument is written as an ordinary function parameter but is supplied from the
context's fields rather than by the caller. That is the shape of a Scala `using` parameter, except the
source is a struct field rather than a `given` in scope. A function that needs a width and a height
reads them as implicit arguments, and any context carrying those fields supplies them:

```rust
#[cgp_fn]
pub fn rectangle_area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
    width * height
}
```

Where Scala's `renderWebsite` obtains its `Config` from an implicit `given`, this function obtains
`width` and `height` from the context threaded through it as `self`. The parallel is close enough that
CGP's own name for the feature, *implicit arguments*, is the word Scala and Haskell use, and the
desugaring is the same idea: the parameter disappears from the public signature and is bound from the
surroundings before the body runs. The difference is where "the surroundings" live. A `using` parameter
searches the implicit scope by type. An `#[implicit]` argument reads the context field of the matching
name, so resolution is by *field*, decided when the context is defined, not by a compiler search at the
call site. The snippet wires a **value context**: the type carrying `width` and `height` is the rectangle
itself. The [area calculation](../examples/area-calculation.md) example develops it.

### A shared context value is a threaded environment

When several pieces of code must agree on one value, Scala uses a single `given Config` in scope and
Haskell the `Reader` monad. CGP has them all read the same field or the same
[abstract type](../cgp/concepts/abstract-types.md) from the shared context. A configuration value read
by many providers is injected once, and every provider that names it receives the same one with no
coordination between them, exactly as one `given Config` serves an entire Scala call graph. CGP's shared
error type is the canonical instance. Every fallible provider imports the context's error type with
`#[use_type(HasErrorType.Error)]` and names it as the bare `Error`, so all of them agree on one type the
context supplies once. That is the type-level echo of a threaded `Reader` environment, resolved at
compile time and costing nothing at run time.

### Abstract types are implicit type parameters

The correspondence runs one level up as well, and a reader from these languages recognizes this half
fastest, because they have solved the same problem with the same trick. An
[abstract type](../cgp/concepts/abstract-types.md) is a type the context determines rather than a
parameter a caller supplies. Haskell's `mtl` achieves the same with a functional dependency:
`class MonadReader r m | m -> r` says the environment type is *fixed by* the monad, and
`MonadError e m | m -> e` says the same for the error type. An associated type family
(`class HasError m where type Error m`) states it more directly still, and is the closest thing in
either language to a `#[cgp_type]` component:

```haskell
class Monad m => MonadError e m | m -> e where
  throwError :: e -> m a
```

```rust
#[cgp_type]
pub trait HasErrorType {
    type Error: Debug;
}
```

Both exist for the same reason, and it is not swappability. A plain type *parameter* propagates:
`runJob :: (MonadError e m, MonadReader r m) => ...` carries `e` and `r` through every intermediate
signature that merely passes a value along, exactly as a Rust generic function's `where` clause does.
Making the type determined by the context, whether by a functional dependency, an associated type, or a
CGP abstract type, stops it propagating, because a determined type is an *output* rather than an input.
This is the type-level face of the tension the value-level section above describes, and it is worth
naming to a reader who has written `mtl`-style code: they already know why the functional dependency is
there.

Two differences follow the same axes as the value case. On *selection*, an `mtl` instance for a given
monad is unique, so the environment type is fixed once for that monad program-wide, whereas CGP's is a
wiring entry and two contexts may bind the same abstract type differently. On *propagation*, CGP hides
more. Haskell's constraint list still grows outward, since a caller of a `MonadError e m =>` function
carries that constraint too. A CGP consumer trait declares the abstract-type trait as a supertrait, so a
caller bounding on the consumer gets it implied without restating it. The type stops propagating in both;
in CGP the *bound* stops as well.

### Components and wiring are type classes without coherence

A CGP component is a type class, a provider is an instance, and wiring is the resolution step. Because
a provider's `Self` is its own marker type, many providers for the same component coexist without
violating coherence, which type-class instances cannot do. The `Comparator[Int]` that Scala can define
only once, or the `Ord Int` that Haskell pins globally, becomes in CGP any number of interchangeable
providers, each selected per context. The [modular serialization](../examples/modular-serialization.md)
example makes the contrast concrete. `UseSerde`, `SerializeBytes`, and `SerializeWithDisplay` all
serialize a `String` and overlap freely, where the equivalent overlapping type-class instances would be
rejected. The `cgp-serde` source declares the first two provider structs separately, because each also
implements a deserializer:

```rust
pub struct UseSerde;

#[cgp_impl(UseSerde)]
impl<Value> ValueSerializer<Value>
where
    Value: serde::Serialize,
{ /* ... */ }

pub struct SerializeBytes;

#[cgp_impl(SerializeBytes)]
impl<Value> ValueSerializer<Value>
where
    Value: AsRef<[u8]>,
{ /* ... */ }
```

These providers wire an **environmental context**, and the component is parameter-targeted: `Self` is an
application such as `AppA`, and the serialized value is the `Value` parameter. The cost of the freedom
is the flip side of the type-class trade. CGP will not *find* the provider for you by type. A context
names its choice in a [`delegate_components!`](../cgp/reference/macros/delegate_components.md) table,
where Scala and Haskell would resolve the instance from the type. What CGP loses in automatic resolution
it gains in the ability to have `AppA` serialize a `Vec<u8>` as hexadecimal and `AppB` as base64: two
coherent local choices where a global instance would force one answer on both.

## What users like and dislike

Implicit parameters and the type classes built on them are among the most loved and most criticized
features of the languages that have them, and both reactions are instructive. Users value the erasure of
boilerplate. A `Config`, a comparator, or an execution context threads through a deep call graph without
appearing at every call, and type classes let one generic function work over any type that has an
instance, resolved automatically. Scala programmers build whole architectures on implicits, from
type-class derivation to context propagation to dependency injection, precisely because the mechanism is
so general. Haskell's type classes are widely regarded as one of the cleanest solutions to ad-hoc
polymorphism in any language.

The dislike is the mirror image of the same generality: implicit resolution is hard to follow. The
recurring Scala complaint is that a value appears "from nowhere", and tracking down *which* `given` was
selected, or why an expected one was not, is a notorious time sink. Scala 2's single overloaded
`implicit` keyword made it worse, which is what Scala 3 split apart to address
([Baeldung, *Scala 3 Implicit Redesign*](https://www.baeldung.com/scala/scala-3-implicit-redesign)).
Error messages when resolution fails are often opaque. Haskell's `ImplicitParams` is disliked enough to
be effectively abandoned, for the concrete reasons above: the constraints leak into every signature, no
default can be given, and the monomorphism restriction interferes. And coherence itself, though it makes
resolution safe, is a persistent source of friction. The orphan rule forces awkward module structure, and
the one-instance-per-type limit forces `newtype` wrappers whenever a second interpretation of a type is
wanted.

## How CGP compares

CGP makes the opposite trade from implicit resolution on the two axes that matter. On *resolution*,
implicit parameters are automatic and type-directed while CGP wiring is explicit: Scala and Haskell find
the instance for you, and CGP asks you to name it in a table. On *coherence*, implicit parameters are
coherent while CGP is not. The languages guarantee one instance per type and forbid overlap and orphans.
CGP permits unlimited overlapping providers and per-context choice by moving `Self` to a provider
marker. Each side pays for what the other gets. The implicit-parameter languages get zero-boilerplate
resolution and pay with the one-instance restriction and the "where did this come from" opacity. CGP
gets many local implementations and explicit, greppable wiring and pays with the wiring itself: there is
no automatic search, so the choice must be written down.

Neither trade is strictly better, and honest positioning names where each wins. When a program wants one
canonical instance per type (one `Ord`, one `Show`, one serialization) and values automatic resolution
above all, type classes are the better tool, and fighting their coherence with CGP-style machinery would
be over-engineering. When a program needs several interchangeable implementations, per-deployment or
per-context choice, or must implement a behavior for types and traits it does not own, CGP's explicit
wiring is the better tool, and the coherence it discards was the very thing in the way. For CGP's
intended audience, explicit resolution is also a feature rather than a cost. The wiring table is the one
place selection is decided, so the "spooky" resolution that dogs implicits is replaced by a lookup a
reader can point at.

## Presenting CGP to someone who knows this

A reader fluent in implicits or type classes already holds most of CGP's conceptual furniture, so name
the correspondence outright. A **component is a type class**, a **provider is an instance**, **wiring
is instance resolution**, an **`#[implicit]` argument is a `using` parameter** whose value comes from a
context field, and an **abstract type is a functional dependency or an associated type family**: the
type the context determines rather than one a caller passes. The context itself is the implicit
environment they already reason about, the `Reader` they thread or the set of `given`s in scope, reified
as a single explicit type that every provider receives. Framed this way, CGP is their own implicit
machinery with the resolution step made visible, not a foreign paradigm.

Correct one expectation up front: automatic resolution. This reader will assume CGP finds the provider
by type the way their compiler finds an instance, and it does not. Wiring is written by hand in a table.
Present that as the deliberate consequence of the feature they will find most striking, rather than as a
missing feature: because CGP does not resolve by type, it is free of coherence, so it can host the
overlapping instances their language forbids. Lead with the pain coherence causes them, the `newtype`
dance to get a second `Ord`, the orphan-rule contortions to add an instance for a foreign type, and the
single global choice forced on unrelated code, and show that each disappears when providers are distinct
marker types selected per context. For the Scala reader, the resonant pitch is "implicits without the
mystery": the value still arrives without being threaded by hand, but *which* implementation was chosen
is a line in a wiring table rather than the outcome of a scope search, so the debugging nightmare they
know is designed out. For the Haskell reader, the pitch is "type classes without the orphan rule, and
overlapping instances made legal".

One further move earns this reader disproportionately, because it shows CGP solving a problem they have
solved themselves. Point at the *type* level and name the functional dependency. A reader who has
written `MonadError e m | m -> e` knows exactly why the environment type must be determined by the monad
rather than passed alongside it, and an abstract type is that discipline made the default and chosen per
context. Framed that way, "one generic parameter instead of a dozen" restates a technique they already
trust rather than claiming cleverness for CGP.

Avoid promising that CGP "just finds the right implementation". It does not, and a reader sold on
automatic resolution will feel misled the first time they write a `delegate_components!` entry. Set the
expectation honestly (you name the provider, once, per context) and pair it with what that explicitness
buys: no ambiguity, no hidden priority rules, no coherence straitjacket, and the same
implementation-hiding decoupling delivered through a table they can read. A reader who has spent an
afternoon debugging an implicit resolution will hear the trade as a good one.

## Sources

The public version of this document is the website's
[implicit-parameters comparison page](https://contextgeneric.dev/docs/comparisons/implicit-parameters), ported per the
[comparison page guide](../website/writing-guides/related-work.md); a change here updates that page
in the same change.

The account of the related work draws on the official language documentation, primary references on
type-class semantics, and community writing on the ergonomics of implicits. The Haskell snippets were
compiled with GHC 9.10 and the Scala snippets with Scala 3.8.4.

- [Scala 3 Book — Context Parameters](https://docs.scala-lang.org/scala3/book/ca-context-parameters.html) and [Scala 3 Reference — Given Instances](https://docs.scala-lang.org/scala3/reference/contextual/givens.html) — the authoritative description of `using` clauses and `given` instances, type-directed resolution, and the Scala 3.6 change from `given ... with` to the colon syntax.
- [Scala 3 Implicit Redesign (Baeldung)](https://www.baeldung.com/scala/scala-3-implicit-redesign) — the rename from Scala 2's overloaded `implicit` keyword to `given`/`using` and the reasons for it.
- [GHC User's Guide — Implicit Parameters](https://ghc.gitlab.haskell.org/ghc/doc/users_guide/exts/implicit_parameters.html) and [Implicit parameters (HaskellWiki)](https://wiki.haskell.org/Implicit_parameters) — the `?x` constraint syntax, `let` binding, propagation, the class-context restriction, and the monomorphism-restriction interaction that keep the feature little used.
- [Type class (Wikipedia)](https://en.wikipedia.org/wiki/Type_class) and [Implementing, and Understanding Type Classes (okmij.org)](https://okmij.org/ftp/Computation/typeclass.html) — type classes as dictionary-passing elaboration and how instances are resolved.
- [Type classes: confluence, coherence and global uniqueness (ezyang's blog)](https://blog.ezyang.com/2014/07/type-classes-confluence-coherence-global-uniqueness/) and [Coherence of Type Class Resolution (Bottu et al.)](https://xnning.github.io/papers/coherence-class.pdf) — the definition of coherence and why it constrains instances to one per type.
- [`mtl` — `Control.Monad.Error.Class`](https://hackage.haskell.org/package/mtl/docs/Control-Monad-Error-Class.html) — the `MonadError e m | m -> e` functional dependency the abstract-type comparison rests on.
