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
know. They differ in *what the surroundings are* and *how the value is found*. Scala searches for contextual values by type and scope; Haskell
`ImplicitParams` selects named implicit bindings. CGP reads a field or resolves a wiring entry from the context that is already
threaded through every provider. The heart of the comparison is showing a reader that CGP's context *is*
their implicit environment, made a first-class and explicitly wired type.

## The concept in depth

Implicit value parameters and type-class dictionaries have different binding rules.
Scala uses contextual search for `using` parameters, Haskell's `ImplicitParams` uses named bindings,
and ordinary Haskell type classes select globally available instances. Keep those mechanisms
separate when comparing them with context fields and wiring.

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

Type-class resolution supplies dictionaries without an explicit argument at each call.
Haskell ordinarily uses global instances; Scala also uses scope and priority rules. The
[type classes](type-classes.md) comparison develops dictionary passing and the distinction between
coherence and global instance uniqueness.

### Coherence and instance selection

Coherence concerns agreement between valid resolutions; global uniqueness is one way to support it.
Haskell ordinarily favors a global instance for a class and its type arguments, while extensions
control overlap. Orphan instances are permitted by GHC but discouraged, unlike Rust's orphan rule.
Scala allows different givens for the same requested type in different scopes.

CGP keeps Rust's coherence checks. Distinct provider types allow interchangeable implementations,
and a context selects one through wiring. A second conflicting entry for the same context and key
is still rejected. Compare selection mechanisms rather than describing CGP as incoherent.

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

Both Haskell monads and CGP contexts can determine associated choices. Different monads can
select different error types, just as different contexts can. A CGP consumer trait can expose an
abstract-type requirement as a supertrait so callers need not restate that bound. The type
dependency remains, but it need not be an independent generic parameter.

### Components and wiring make instance selection explicit

A component's consumer trait plays the interface role, while providers supply interchangeable
implementations selected through wiring. Separate provider marker types let implementations coexist
without conflicting Rust impls. Scala can also select alternative givens by scope, while Haskell
ordinarily uses a global instance. The [modular serialization](../examples/modular-serialization.md)
example shows reusable providers for the same target. The provider structs are separate because
each also implements a deserializer:

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
Error messages when resolution fails are often opaque. Haskell's `ImplicitParams` has the documented restrictions above: the constraints leak into every signature, no
default can be given, and the monomorphism restriction interferes. And coherence itself, though it makes
resolution safe, is a persistent source of friction. Global instance choices and orphan-instance conventions influence module structure in Haskell;
`newtype` wrappers distinguish alternative interpretations. Scala uses different scope rules.

## How CGP compares

Implicit resolution reduces argument passing but requires readers to trace the selected binding.
Scala's givens can come from local scope, imports, or implicit scope, so understanding a call may
require following the search rules. The
[Scala reference](https://docs.scala-lang.org/scala3/reference/contextual/using-clauses.html)
describes how arguments are supplied. Haskell's `ImplicitParams` makes dependencies visible as
constraints, which must propagate until a binding supplies them; its inference restrictions can
also affect behavior. See the
[GHC User's Guide](https://ghc.gitlab.haskell.org/ghc/doc/users_guide/exts/implicit_parameters.html).

Global type-class instances favor a canonical interpretation of a type. In Haskell, an alternative
ordering or rendering often needs a `newtype` to distinguish it from the existing instance.
That trade differs from Scala's scoped selection. The
[coherence analysis by Yang](https://blog.ezyang.com/2014/07/type-classes-confluence-coherence-global-uniqueness/)
separates global uniqueness from coherence and confluence.

CGP requires component declarations and provider selection through wiring or declared defaults.
This adds code to maintain and trait-resolution work during compilation. Tracing a selection can
also require following delegation through several tables. Raw diagnostics expose generated traits
and types: [`cargo cgp check`](../cargo-cgp/reference/usage.md) leads with the root cause for the classes it
recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every class. The
[Modularity Hierarchy](../cgp/concepts/modularity-hierarchy.md) weighs these costs against simpler forms.

### Where the other approach fits

Implicit resolution fits code that benefits from the surrounding language's instance conventions
or local contextual bindings. Haskell type classes work well for a canonical ordering or rendering;
Scala's givens support contextual choices without a separate CGP-style wiring table. Within Rust,
an ordinary trait is sufficient when one implementation per type expresses the intended behavior.

CGP helps when Rust code needs separately reusable implementations and explicit choices per context.
Those benefits must justify its additional declarations. It does not replace the scope rules or
inference mechanisms of Scala and Haskell.

## Presenting CGP to someone who knows this

Distinguish the binding rules before using the implicit-parameter analogy. Scala resolves givens
through scope and priority rules, Haskell's `ImplicitParams` uses named bindings, and ordinary Haskell
type classes favor global instances. Scala can select different implementations of the same requested
type in different scopes; do not attribute Haskell's usual global uniqueness to Scala.

Explain CGP as selection through context types and wiring, not the removal of coherence. Separate
provider types allow reusable alternatives to coexist while Rust still rejects overlapping impls.
Wiring, defaults, and delegation determine the provider; the caller's lexical scope does not.

Use associated types and functional dependencies to explain a type determined by a context.
Different Haskell monads can determine different error types, just as different CGP contexts can.
The relationship avoids an independent parameter but does not erase the type dependency. Explicit
wiring is traceable, though following several delegation layers can still take work.

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
- [Type classes: confluence, coherence and global uniqueness (ezyang's blog)](https://blog.ezyang.com/2014/07/type-classes-confluence-coherence-global-uniqueness/) and [Coherence of Type Class Resolution (Bottu et al.)](https://xnning.github.io/papers/coherence-class.pdf) — the distinctions between coherence, confluence, and global instance uniqueness.
- [`mtl` — `Control.Monad.Error.Class`](https://hackage.haskell.org/package/mtl/docs/Control-Monad-Error-Class.html) — the `MonadError e m | m -> e` functional dependency the abstract-type comparison rests on.
