# Traits without coherence

Several trait systems let one type have more than one implementation of a trait, and each must then
decide which implementation a use of the trait gets. This document compares five of them on that
question alone: Cairo's named impls, Scala's `given` instances, OCaml's modular implicits, Haskell's
overlapping and incoherent instances, and Boxy's sketch of an incoherent Rust. They give three
families of answer: infer the choice from what is in scope, name it at each call, or fix it on a type.
CGP takes the third, by fixing the choice on a context type, and it does so while every Rust impl it
generates still passes Rust's coherence checks.

## Purpose

Rust's coherence rules give every trait lookup one answer, and every system here gives that up for
the freedom to have several implementations. They then meet the same three problems. Two call sites
can resolve the same type differently. A change of imports can change the choice. And a data
structure such as a hash table, which needs every operation on one value to agree on one `Hash`,
loses that agreement unless the design restores it some other way. Comparing the systems on these
problems shows which answer each family gives and what each answer costs.

The document serves the
[language-design reader](../communication-strategy/readers.md#the-language-design-and-compiler-team-reader)
first, since the incoherent-Rust discussion is choosing among these answers now, and the reader who
knows one of the systems second. Each system keeps its full account in its own comparison, linked
from its section: [Rust's own proposals](rust-language-proposals.md) for Boxy's sketch and the other
Rust designs, [type classes](type-classes.md) for Haskell, [implicit parameters](implicit-parameters.md)
for Scala, and [ML modules](ml-modules.md) for modular implicits. Only Cairo has no comparison of its
own, so its section here is the longest. The analysis of Cairo's resolution is the project's own; it
first appeared in the author's unpublished draft that the
[website record](../website/blog/incoherent-rust-today.md) describes.

## The concept in depth

The five systems share a starting point: implementations that can overlap, and a rule for choosing
among them. They differ in where that rule looks. Haskell keeps a global search and relaxes its
uniqueness in exceptional cases. Cairo, Scala, and modular implicits search what is in scope at the
call. Boxy's sketch names the impl at the call and, for types such as `HashMap`, fixes it on the type.

### Uniqueness with exceptions in Haskell

Haskell resolves instances globally and expects one instance per class and type, so its departures
from coherence are extensions that the programmer opts into per instance. An instance marked
`OVERLAPPABLE` or `OVERLAPPING` may coexist with a more or less specific one, and resolution commits
only to a match that is strictly more specific than every other:

```haskell
{-# LANGUAGE FlexibleInstances #-}
import Prelude hiding (Show, show)
import Data.List (intercalate)

class Show a where
  show :: a -> String

instance {-# OVERLAPPABLE #-} Show a => Show [a] where   -- lists in general
  show xs = "[" ++ intercalate "," (map show xs) ++ "]"

instance {-# OVERLAPPING #-} Show [Char] where           -- but strings specially
  show s = s
```

An instance marked `INCOHERENT` goes further: resolution may commit to it even when a more specific
instance could later apply, so two parts of a program can resolve one constraint to different
dictionaries. GHC's manual warns that overlap alone "can give rise to incoherence (different instance
choices are made in different parts of the program)", and that its optimiser "assumes that
type-classes are coherent", so it may replace one dictionary argument with another of the same type
([GHC User's Guide, *Instance declarations and resolution*](https://ghc.gitlab.haskell.org/ghc/doc/users_guide/exts/instances.html)).
Haskell's answer to the three problems is therefore to keep them rare: the default is one instance,
and the extensions that break it carry the manual's warnings. The
[type classes](type-classes.md#overlapping-instances) comparison covers both extensions in full.

### Inference from scope in Cairo

Cairo, the smart-contract language of Starknet, borrows Rust's surface syntax but gives every impl a
name and drops the requirement that an impl be unique. Its design discussion states that Cairo has "no
orphan rules nor uniqueness demand"
([Cairo design discussion #2744](https://github.com/starkware-libs/cairo/discussions/2744)). An impl
follows the form `impl Name of Trait<…>`, and the trait takes every type as an explicit parameter,
with no implicit `Self`. The corelib's `Serde` shows the form, with `@T` a snapshot of a `T` and
`felt252` the field element of Cairo's prime field, of modulus 2^251 + 17·2^192 + 1:

```cairo
pub trait Serde<T> {
    fn serialize(self: @T, ref output: Array<felt252>);
    fn deserialize(ref serialized: Span<felt252>) -> Option<T>;
}
```

Two impls of one trait for one type coexist, even in one module, and a call may name the one it
wants. A generic impl takes the impls it depends on as parameters, either named, as
`impl Inner: Describe<T>`, or anonymous, as `+Drop<T>`
([Cairo Book, *Traits in Cairo*](https://www.starknet.io/cairo-book/ch08-02-traits-in-cairo.html);
[*Generic Data Types*](https://www.starknet.io/cairo-book/ch08-01-generic-data-types.html)):

```cairo
trait Describe<T> {
    fn describe(self: @T) -> felt252;
}

mod decimal {
    pub impl U8Decimal of super::Describe<u8> {
        fn describe(self: @u8) -> felt252 { 10 }
    }
}

mod hex {
    pub impl U8Hex of super::Describe<u8> {
        fn describe(self: @u8) -> felt252 { 16 }
    }
}

impl ArrayDescribe<T, impl Inner: Describe<T>, +Drop<T>> of Describe<Array<T>> {
    fn describe(self: @Array<T>) -> felt252 {
        let mut total = 0;
        for x in self.span() {
            total += Inner::describe(x);
        };
        total
    }
}

mod uses_decimal {
    use super::Describe;
    use super::decimal::U8Decimal;
    pub fn run() -> felt252 {
        let xs: Array<u8> = array![1, 2];
        xs.describe()       // ArrayDescribe with U8Decimal: 20
    }
}

mod uses_hex {
    use super::Describe;
    use super::hex::U8Hex;
    pub fn run() -> felt252 {
        let x: u8 = 1;
        x.describe()        // U8Hex: 16
    }
}
```

The caller does not pass the impls: the compiler infers each one from the impls visible at the call,
including the `Inner` impl that `ArrayDescribe` needs. So the imports decide the choice. The two
modules above resolve `Describe<u8>` differently because they import different impls; a module that
imports both fails with `E2313`, "Trait `Describe::<u8>` has multiple implementations", and one that
imports neither fails with "Trait has no implementation in context". A caller must also import every
impl in the chain a generic impl needs, here `U8Decimal` for `ArrayDescribe`. A glob import shortens
the list, but it brings in every impl in the module, so a module holding both `U8Decimal` and `U8Hex`
makes the call fail with the same `E2313`.

Cairo's answer to the three problems is the caller's imports. Two call sites in one project can use
different impls for one type, and the project has no single place that fixes the choice.

### Scoped givens in Scala

Scala 3 resolves a `using` parameter from the `given` instances in scope, and it ranks candidates
rather than requiring one. A given may be defined for a type and resolved at each call:

```scala
trait Comparator[A]:
  def compare(x: A, y: A): Int

given Comparator[Int]:
  def compare(x: Int, y: Int): Int = x - y

def max[A](x: A, y: A)(using c: Comparator[A]): A =
  if c.compare(x, y) > 0 then x else y

max(1, 2)     // Comparator[Int] resolved and passed implicitly
```

Where several givens fit, the rules decide by nesting and specificity: a given nested more deeply
wins, where Scala 2 reported an ambiguity, and an ambiguity found in a recursive step propagates to
the caller as an error
([Scala 3 Reference, *Changes in Implicit Resolution*](https://docs.scala-lang.org/scala3/reference/changed-features/implicit-resolution.html)).
Scala 3 also separates given imports from ordinary ones: a wildcard `import A.*` brings in everything
but givens, and `import A.given` brings in the givens, so that "it is made clearer where givens in
scope are coming from"
([*Importing Givens*](https://docs.scala-lang.org/scala3/reference/contextual/given-imports.html)).
Scala's answer is scope with explicit ranking, and its redesign narrowed what an import can bring in.
The [implicit parameters](implicit-parameters.md) comparison covers `given` and `using` in full.

### Modular implicits in OCaml

The modular-implicits proposal extends OCaml with module parameters that the compiler fills from the
modules declared `implicit` in scope. An implicit functor composes an instance for lists from one for
their elements:

```ocaml
module type Show = sig
  type t
  val show : t -> string
end

let show {S : Show} x = S.show x

implicit module Show_int = struct
  type t = int
  let show x = string_of_int x
end

implicit module Show_list {S : Show} = struct
  type t = S.t list
  let show x = "[" ^ String.concat ", " (List.map S.show x) ^ "]"
end

let () =
  print_endline (show 5);           (* resolves Show_int *)
  print_endline (show [1; 2; 3])    (* resolves Show_list(Show_int) *)
```

Different scopes may hold different implicit modules for one type, and resolution rejects a choice
that is ambiguous rather than ranking the candidates, so the programmer passes the module explicitly
there ([White, Bour & Yallop, *Modular implicits*](https://arxiv.org/abs/1512.01895)). The snippet
follows the proposal paper; the extension exists only as an
[experimental fork](https://github.com/ocamllabs/ocaml-modular-implicits) and cannot run on released
OCaml. Its answer is scope without ranking, and the [ML modules](ml-modules.md#modular-implicits)
comparison covers it with the module system it extends.

### Naming at the call, and fixing on the type, in Boxy's sketch

Boxy's *An Incoherent Rust* drops Rust's coherence rules for traits declared `incoherent trait`,
names each impl, and passes the impl where a bound needs one:

```rust
impl Name<T> = Trait<T> for T { /* ... */ }

function::<T + TraitImpl<T>>(/* ... */)
```

The syntax is the post's sketch, not a proposal, and does not compile. Naming at the call removes
inference, so imports cannot change a choice, but every call site states it. For the hash-table
problem the post moves the bounds onto the type, as `struct HashMap<K: Hash + Eq, V> { ... }`, so
that "once a value of HashMap is constructed the same Hash/Eq impls will always be used for that
value, as which impl is used is part of the HashMap type itself"
([Boxy, *An Incoherent Rust*](https://www.boxyuwu.blog/posts/an-incoherent-rust/)). The sketch thus
uses two answers: naming at the call in general, and fixing the choice on a type where every
operation must agree. [Rust's own proposals](rust-language-proposals.md#named-and-incoherent-impls)
covers it with the rest of the Rust discussion.

## How CGP expresses it

CGP fixes the choice on a type for every trait it manages: the context type. A provider is a named
impl, implemented for a marker type the crate owns, so two providers of one component for one type
coexist without overlapping in Rust's eyes. A context's `delegate_components!` table then picks one
provider per component and dispatch key, and every use through that context gets the same one. The
snippets wire an **environmental context**, `App`, for a parameter-targeted component.

The Cairo serializer translates in two ways. The direct translation makes the element's provider a
parameter of a [higher-order provider](../cgp/concepts/higher-order-providers.md), bound with
[`#[use_provider]`](../cgp/reference/attributes/use_provider.md), and the caller assembles the chain
that Cairo infers:

```rust
#[cgp_component(ValueSerializer)]
pub trait CanSerializeValue<T> {
    fn serialize(&self, value: &T, output: &mut Vec<u64>);
}

#[cgp_impl(new VecSerdeWith<Inner>)]
#[use_provider(Inner: ValueSerializer<T>)]
impl<T, Inner> ValueSerializer<Vec<T>> {
    fn serialize(&self, value: &Vec<T>, output: &mut Vec<u64>) {
        output.push(value.len() as u64);
        for item in value {
            Inner::serialize(self, item, output);
        }
    }
}

// The caller names the whole chain.
<VecSerdeWith<PairSerdeWith<U8Serde, BoolSerde>> as ValueSerializer<App, Vec<(u8, bool)>>>::serialize(
    &App, &value, &mut output,
);
```

Idiomatic CGP moves the choice to the context instead. The provider asks the context for the
element's serializer with [`#[uses]`](../cgp/reference/attributes/uses.md), and the context's table
answers once, for every caller:

```rust
#[cgp_impl(new VecSerde)]
#[uses(CanSerializeValue<T>)]
impl<T> ValueSerializer<Vec<T>> {
    fn serialize(&self, value: &Vec<T>, output: &mut Vec<u64>) {
        output.push(value.len() as u64);
        for item in value {
            self.serialize(item, output);
        }
    }
}

delegate_components! {
    App {
        open ValueSerializerComponent;

        @ValueSerializerComponent.<T> Vec<T>: VecSerde,
        @ValueSerializerComponent.<A, B> (A, B): PairSerde,
        @ValueSerializerComponent.u8: U8Serde,
        @ValueSerializerComponent.bool: BoolSerde,
    }
}

check_components! {
    App {
        ValueSerializerComponent: Vec<(u8, bool)>,
    }
}
```

Code that serializes through `App` imports only the consumer trait `CanSerializeValue`. The
[`open`](../cgp/reference/macros/delegate_components.md) statement dispatches the component per value
type, and the table is the one place a reader looks to learn which provider each type gets. Against
the three problems, every call through one context agrees; imports do not select providers; and the
hash-table agreement follows from the context, as in Boxy's `HashMap`, but for every component at
once. A second context, such as an `AppB` with another `u8` provider, makes a different choice with
the same providers.

CGP does not relax Rust's coherence to do this. Each provider implements the provider trait for its
own type, and each table entry is an ordinary impl of `DelegateComponent` for the context, so a second
entry for the same context and key is rejected with `E0119`, as any overlapping impl is. The
[coherence](../cgp/concepts/coherence.md) concept describes the move in full.

## What users like and dislike

Each answer has its advocates and its critics, and the criticisms are the ones each design's own
documentation anticipates:

- **Haskell:** global resolution with one instance is valued because it makes a `Set` of an ordered
  type safe without thought; the overlap and incoherence extensions are widely treated as a last
  resort, as GHC's warnings suggest. The [type classes](type-classes.md#what-users-like-and-dislike)
  comparison gathers the sentiment.
- **Scala:** implicit resolution is valued for removing boilerplate, and Scala 2's single `implicit`
  keyword was hard enough to teach that Scala 3 renamed it to `given` and `using` and separated given
  imports, as the [implicit parameters](implicit-parameters.md#what-users-like-and-dislike)
  comparison records.
- **Cairo:** named impls give the freedom Rust's orphan rule withholds. The cost the project's
  analysis finds is that the caller imports the whole chain of impls, and that imports decide the
  choice.
- **Modular implicits:** the proposal has no users to report, since it has not shipped in OCaml; its
  paper rejects ambiguous choices rather than ranking them.
- **Boxy's sketch:** its own post names the costs it would need to settle: syntax, ergonomics for
  deriving incoherent traits, migration of the ecosystem, and whether the complexity is worth it.

## How CGP compares

CGP gives the per-context choice of the third family on stable Rust, and its price is that the
choice must be written down. Against **inference from scope**, CGP never searches: a context names
every provider it uses, so a program cannot pick up a different impl by importing one, and it also
cannot leave the choice to the compiler. Against **naming at each call**, CGP names the choice once
per context rather than per call; generic code only states the consumer trait it needs. Against
**Haskell's global uniqueness**, CGP allows any number of providers for one type, each selected
deterministically, where Haskell's overlap extensions trade that determinism away.

CGP's costs are its ordinary ones. The component and its providers need declarations, the wiring is
code somebody writes, and compile-time work and raw diagnostics are trait-solver output over
generated types: `cargo cgp check` leads with the root cause for the classes it recognizes, and the
tool does not yet reshape every class. CGP also reaches only the traits defined as components, so it
cannot give `serde::Serialize` a second impl without a parallel component, where a language feature
would apply to every trait. And it cannot nest choices: a scope inside a program cannot override the
context's wiring for the code it encloses, which Scala's nesting rule and scoped impls allow.

The other systems are the better fit in their own settings. Scala's givens and Cairo's inference
keep small programs free of wiring, where a single choice per type is all the program needs. Haskell's
global instances give the same answer everywhere with no table, which is what most code wants. And a
language change, unlike a library, would reach existing traits.

## Presenting CGP

Place CGP in the family that fixes the choice on a type, and name the type: the context. A reader
who knows Cairo or Scala expects the compiler to find an impl in scope, and CGP never does, so say it
early and give the reason: the choice lives in one table, so imports cannot change it and every use
through a context agrees. A reader who knows Boxy's `HashMap` answer has already met the idea, applied
to one type; CGP applies it to every component a context wires.

Say that CGP keeps Rust's coherence rules. "Incoherent" describes the provider traits' freedom to
have several implementations, not the impls Rust checks, and a reader who hears that CGP is
incoherent looks for the soundness problems of Haskell's `INCOHERENT` instances, which CGP does not
have. The [implicit parameters](implicit-parameters.md#coherence-and-instance-selection) comparison
states the same rule: compare selection mechanisms rather than describing CGP as incoherent.

For the language-design reader, the comparison is a finding about the design space rather than a
pitch. The three families trade the same goods: inference costs predictability, naming at each call
costs repetition, and fixing on a type costs a declaration. CGP is evidence of what the third family
is like to use at scale, with its verbosity stated beside its predictability. If an incoherent Rust
adopts inference or scoped impls, the question CGP raises is whether the language should also offer
a way to fix the choices for a whole program in one place.

## Sources

The public version of this document is the website's
[traits-without-coherence comparison page](https://contextgeneric.dev/docs/comparisons/traits-without-coherence),
to be ported per the [comparison page guide](../website/writing-guides/related-work.md#pages-that-compare-several-systems);
a change here updates that page in the same change.

The Cairo snippets were compiled and run with Cairo 2.21.0 (`cairo-run`, from nixpkgs), and the
`Serde` trait is quoted from that release's corelib, which also states the field modulus. The Haskell
snippet is the [type classes](type-classes.md) comparison's, compiled there with GHC 9.10; the Scala
snippet is the [implicit parameters](implicit-parameters.md) comparison's, compiled there with Scala
3.8.4. The modular-implicits snippet follows the proposal paper and cannot run on released OCaml, and
Boxy's syntax is a sketch that does not compile. The CGP snippets were compiled and run against `cgp`
0.8.0, with a `check_components!` assertion on `App`.

- [Cairo Book: *Traits in Cairo*](https://www.starknet.io/cairo-book/ch08-02-traits-in-cairo.html)
  and [*Generic Data Types*](https://www.starknet.io/cairo-book/ch08-01-generic-data-types.html):
  the `impl Name of Trait` form, named and anonymous impl parameters, and the compiler's inference
  of impls.
- [Cairo design discussion #2744](https://github.com/starkware-libs/cairo/discussions/2744): Cairo's
  lack of orphan rules and of a uniqueness requirement.
- [GHC User's Guide: *Instance declarations and resolution*](https://ghc.gitlab.haskell.org/ghc/doc/users_guide/exts/instances.html):
  the overlap and incoherence pragmas and the manual's warnings about them.
- [Scala 3 Reference: *Changes in Implicit Resolution*](https://docs.scala-lang.org/scala3/reference/changed-features/implicit-resolution.html)
  and [*Importing Givens*](https://docs.scala-lang.org/scala3/reference/contextual/given-imports.html):
  the nesting and specificity rules, propagated ambiguity, and the separate given imports.
- [White, Bour & Yallop, *Modular implicits*](https://arxiv.org/abs/1512.01895) and the
  [experimental fork](https://github.com/ocamllabs/ocaml-modular-implicits): implicit module
  parameters, implicit functors, and the rejection of ambiguous choices.
- [Boxy, *An Incoherent Rust*](https://www.boxyuwu.blog/posts/an-incoherent-rust/): named impls,
  impls passed in bounds, the `HashMap` bounds moved onto the type, and the open costs.
- The [record of the unpublished incoherent-Rust draft](../website/blog/incoherent-rust-today.md):
  the analysis of Cairo's resolution and the direct and idiomatic CGP translations, here stated as
  the project's own.
