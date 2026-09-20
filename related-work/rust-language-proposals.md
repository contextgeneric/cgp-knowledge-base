# Rust's own proposals: specialization, named impls, and contexts

Rust has debated relaxing its coherence rules for a decade, and the debate has produced three lines of
design: *specialization*, which lets a more specific impl override a blanket one; *named or incoherent
impls* and the *dictionary-passing* account of traits that would let a program carry several impls of
one trait and pass them explicitly; and *contexts and capabilities*, which would let a function or impl
require a value from an enclosing scope without a parameter. CGP is a library that ships a fragment of
each on stable Rust today, at the cost of explicit wiring and a single context type. A Rust reader
compares CGP to these before anything else, so the comparison has to be precise about what each proposal
would give the language, what CGP gives instead, and where CGP falls short of them.

## Purpose

Every proposal here answers a limitation of coherence that Rust programmers hit in ordinary work. The
overlap rule rejects two blanket impls that could both apply to one type. The orphan rule forbids
implementing a foreign trait for a foreign type. And a trait impl has no way to reach a value from its
caller's environment except through `Self` or a global. Specialization targets the first, named impls
target the first two, and contexts and capabilities target the third. None of them has shipped.
Specialization has been unstable since 2016 with a known soundness hole, the named-impl and
dictionary-passing designs are blog posts and design sketches, and contexts and capabilities is a
proposal from 2021 that its author framed as a research direction.

CGP occupies the same design space from the library side, which is why its author's own writing engages
these proposals directly ([RustLab 2025 talk](https://contextgeneric.dev/blog/rustlab-2025-coherence);
[evidence.md](../communication-strategy/evidence.md#the-conversations-that-draw-attention)). The
[coherence](../cgp/concepts/coherence.md) concept describes CGP's move as writing implementations
incoherently against a provider type and restoring coherence per context, and that is a desugaring of
what named impls and scoped contexts would express as syntax. This document lays the proposals out as
their authors present them, shows the CGP counterpart of each, and states the two places where CGP
cannot follow: it cannot infer an impl from scope, and it cannot nest bindings dynamically. The reader it
serves most is the [language-design reader](../communication-strategy/readers.md#the-language-design-and-compiler-team-reader),
for whom CGP is interesting as evidence rather than as a tool.

## The concept in depth

The proposals share a starting point, Rust's coherence rules as the Reference states them, and diverge
in which rule they relax and how. The subsections take them in the order the ideas were published:
coherence itself, specialization, the dictionary-passing account and the named-impl proposals built on
it, contexts and capabilities, and finally Cairo, a Rust-like language that shipped named impls and
shows what the design costs in practice.

### Coherence as Rust states it

Rust's Reference gives the two rules that every proposal here relaxes. The *orphan rule* says that an
`impl<P1..=Pn> Trait<T1..=Tn> for T0` is valid only if `Trait` is a local trait, or at least one of the
types `T0..=Tn` is a local type and no uncovered type parameter appears before it. The *overlap rule*
says two implementations overlap, and are rejected, when "there is a non-empty intersection of the traits
the implementation is for" and "the implementations can be instantiated with the same type"
([Rust Reference, *Implementations*](https://doc.rust-lang.org/reference/items/implementations.html);
[RFC 2451](https://rust-lang.github.io/rfcs/2451-re-rebalancing-coherence.html)). Together they
guarantee that any trait lookup, anywhere in a program, finds exactly one impl. That guarantee is what
lets generic code resolve `T: Hash` transitively without the caller naming an impl, and it is what makes
a `HashMap<K, V>` sound: every insert and lookup agrees on one `Hash for K`. The
[type classes](type-classes.md) comparison covers why coherence exists in the broader type-class
tradition; this document takes it as given and looks at what Rust has considered doing about its cost.

### Specialization: let the specific impl win

RFC 1210, *impl specialization*, proposes allowing two impls to overlap when one is *strictly more
specific* than the other, and letting the compiler pick the specific one. Its motivation is threefold:
performance, because a specialized impl can supply a fast path for a concrete case while a blanket impl
covers the rest; code reuse, because a blanket impl marked `default` can be refined per type without
forcing every type through the same bounds; and groundwork for "efficient inheritance" patterns. The
RFC's own example refines a blanket `AddAssign`:

```rust
impl<R, T: Add<R> + Clone> AddAssign<R> for T {
    default fn add_assign(&mut self, rhs: R) {
        let tmp = self.clone() + rhs;
        *self = tmp;
    }
}
```

A more specific impl for a type that can update in place then overrides `add_assign` without the clone.
The `default` keyword is mandatory on any item that may be overridden, so that "if you see an impl that
applies to a type and the relevant item is not marked `default`, you know that the definition you're
looking at is the one that will apply" ([RFC 1210](https://rust-lang.github.io/rfcs/1210-impl-specialization.html)).

Specialization has never stabilized, and the tracking issue is explicit about why. The full
`specialization` feature "as implemented currently is *unsound*, which means that it can cause Undefined
Behavior without `unsafe` code", because dispatch information about lifetimes is erased before code
generation, so an impl that is more specific only through a lifetime bound such as `T: 'static` cannot
be chosen reliably. The `min_specialization` subset "avoids most of the pitfalls" and is what the
standard library uses internally, but the issue, open since February 2016, remains labelled as needing
deep research, with none of its sub-issues resolved
([tracking issue #31844](https://github.com/rust-lang/rust/issues/31844)).

Specialization also does not address the problem CGP starts from, and the reason is worth stating
precisely because "just prefer the specialized impl" is the first thing a Rust reader proposes. Two
impls of equal generality, `Hash for T: Display` and `Hash for T: AsRef<[u8]>`, are not ordered by
specificity, so specialization rejects them just as coherence does. And even where an ordering exists,
generic code can bind the blanket impl through a bound that never mentions `Hash` at all, so by the
time the concrete type is known the specialization is invisible, and the chain of generic callers can be
arbitrarily deep. The RustLab 2025 talk builds this argument on the hash-table problem and concludes that
specialization, even stabilized, would permit neither equally general overlapping impls nor orphan
impls ([RustLab transcript](../website/blog/rustlab-2025-coherence.md)).

### Dictionary passing: traits as structs, impls as values

A second line of thought treats the trait system as sugar over *dictionary passing*, the elaboration
Haskell compilers perform and the [type classes](type-classes.md) comparison describes. Nadrieril's
*Elaborating Rust Traits to Dictionary-Passing Style* (March 2026) works it out for Rust: a trait
becomes a struct of function pointers, an impl becomes a value of that struct, and a trait bound becomes
an argument the caller passes:

```rust
struct Clone<Self> {
    clone: fn(&Self) -> Self,
}

const CLONE_U32: Clone<u32> = Clone { clone: |x: &u32| *x };
```

A generic impl such as `impl<T: Clone> Clone for Vec<T>` becomes a `const` function from a `Clone<T>`
dictionary to a `Clone<Vec<T>>` dictionary. The post frames trait solving as the process that supplies
these proofs, and it names the open problems honestly: how to handle associated-type equality
constraints, whether the elaborated program recurses excessively, and what conditions beyond individual
proof justification are needed for soundness. It also identifies coherence as the point of friction,
since a global impl can constrain a caller in ways the caller cannot see
([Nadrieril, *Dictionary-passing style*](https://nadrieril.github.io/blog/2026/03/20/dictionary-passing-style.html)).
The value of the framing for this comparison is that once impls are values, *choosing* an impl is
passing a different value, which is exactly the freedom coherence forbids.

### Incoherent Rust: named impls passed as bounds

Boxy's *An Incoherent Rust* proposes to drop the coherence rules and replace them with explicit impl
selection. The motivating problem is *ecosystem evolution*: once a foundational crate such as `serde`
establishes the trait impls for common types, an alternative serialization library cannot gain adoption,
because downstream crates cannot implement the competing trait for types they do not own. The proposal
sketches naming an impl and passing it where a bound is required:

```rust
impl Name<T> = Trait<T> for T { /* ... */ }

function::<T + TraitImpl<T> + OtherTraitImpl<T>>(/* ... */)
```

A trait declared `incoherent trait` may have several overlapping impls, and the impl used becomes part
of the type signature, much as the `K: Hash` bound is part of `HashMap`'s definition. The post answers
the two classic justifications for coherence on their own terms. The `HashMap` problem is solved by
moving the `Hash` and `Eq` bounds onto the type definition, so every operation on one map agrees on one
impl. The associated-type soundness problem is solved because the impl is part of the type, so two
values typed with different impls cannot be silently transmuted into one another. It then names the
remaining challenges as substantial: syntax, ergonomics for deriving incoherent traits, migration of the
existing ecosystem, and whether the complexity is worth it
([Boxy, *An Incoherent Rust*](https://www.boxyuwu.blog/posts/an-incoherent-rust/)).

### Contexts and capabilities: values from the enclosing scope

Tyler Mandry's 2021 *Contexts and capabilities in Rust* addresses a different limitation: a function or
impl cannot reach a value from its caller's environment, such as an allocator, an executor, or a logger,
except by threading it as a parameter or storing it in a global. Threading is tedious and impossible
through code you do not control, and thread-locals cannot hold stack-allocated values. The proposal
sketches a `with` clause on a declaration that names the context it requires, and a `with` block at a
call site that supplies it:

```rust
fn deserialize<'a>(bytes: &[u8]) -> Result<&'a Foo, Error>
with
    arena::basic_arena: &'a arena::BasicArena,
{
    arena::basic_arena.alloc(Foo::from_bytes(bytes)?)
}

with arena::basic_arena = &arena::BasicArena::new() {
    let foo: &Foo = deserialize(bytes)?;
}
```

The distinctive power is *context-dependent trait impls*: an impl valid only when a given capability is
in scope, so a type may implement `Deserialize` inside a `with` block and not outside it. The mechanism
compiles to ordinary function arguments, so it is zero-cost, and it guarantees statically that the
context is available. The open questions the post raises concern thread boundaries and scope validity
([Mandry, *Contexts and capabilities*](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/)).
The proposal borrows the word "capability" from a security model whose other properties it does not
claim; the [capabilities](capabilities.md) comparison separates the senses.
Nadrieril's follow-up, *What If Traits Carried Values*, connects the two lines by extending dictionary
passing so that a trait bound may carry a runtime value as well as methods, with the impl
`impl<'a> Deserialize for &'a Foo where arena: &'a BasicArena` as the worked case. It names the
difficulties that follow: a trait would have to distinguish several ownership modes for the carried
value, the same type could satisfy a trait differently depending on scope, which threatens types such
as `HashSet` that rely on consistency, and methods that capture implicit values become closures rather
than function pointers ([Nadrieril, *What If Traits Carried Values*](https://nadrieril.github.io/blog/2026/03/22/what-if-traits-carried-values.html)).

### Cairo: a Rust-like language that shipped named impls

Cairo, the smart-contract language of StarkNet, borrows Rust's surface syntax and gives every impl a
name, so it is the nearest thing to a shipped Incoherent Rust. Its book states the rule: "after `impl`,
we put a name for the implementation, then use the `of` keyword, and then specify the name of the trait"
([Cairo Book, *Traits in Cairo*](https://www.starknet.io/cairo-book/ch08-02-traits-in-cairo.html)). A
generic function may take an impl as an explicit parameter, either named or anonymous:

```rust
// Cairo
fn largest_list<T, impl TDrop: Drop<T>>(l1: Array<T>, l2: Array<T>) -> Array<T> { /* ... */ }

fn smallest_element<T, +PartialOrd<T>, +Copy<T>, +Drop<T>>(list: @Array<T>) -> T { /* ... */ }
```

The `+Drop<T>` form is the anonymous spelling of `impl TDrop: Drop<T>`
([Cairo Book, *Generic Data Types*](https://www.starknet.io/cairo-book/ch08-01-generic-data-types.html)).
A caller does not pass the impl: "There is no need to specify the concrete type of T because it is
inferred by the compiler", and the compiler likewise infers the impl from those visible at the call
site. That inference is the design decision that matters for the comparison. CGP's author examines it
in the unpublished draft that the [website record](../website/blog/incoherent-rust-today.md) describes,
and reads it as the cost of resolving from scope rather than from a declared context: because
resolution depends on which impls are imported, the set of imports decides which implementation a call
uses, a caller must import the whole chain of intermediate impls a generic impl needs, and two call
sites in one project may resolve the same type differently.

## How CGP expresses it

CGP is a desugaring of these proposals into stable Rust, and the correspondence is close enough to state
construct by construct. A named impl is a provider. An incoherent trait bound is a consumer-trait bound
on the context. Passing an impl explicitly is a higher-order provider. A capability is a field of the
context, read by an implicit argument. And the `with` block that binds everything is the definition of a
context type and its wiring. What the proposals would add to the language, CGP adds as a library, with
the single restriction that every binding lives in one place: the context.

### A named impl is a provider

The thing Boxy's proposal names with `impl Name<T> = Trait<T> for T` is what CGP calls a provider. The
[consumer/provider split](../cgp/concepts/consumer-and-provider-traits.md) gives every implementation
its own zero-sized type, so two overlapping impls of one trait coexist because each implements the
provider trait for its own name. The [coherence](../cgp/concepts/coherence.md) concept shows the two
`Serialize` blanket impls Rust rejects and their CGP form, taken from `cgp-serde`:

```rust
pub struct UseSerde;

#[cgp_impl(UseSerde)]
impl<Value> ValueSerializer<Value>
where
    Value: serde::Serialize,
{ /* value.serialize(serializer) */ }

pub struct SerializeBytes;

#[cgp_impl(SerializeBytes)]
impl<Value> ValueSerializer<Value>
where
    Value: AsRef<[u8]>,
{ /* serializer.serialize_bytes(value.as_ref()) */ }
```

`UseSerde` and `SerializeBytes` are named impls in exactly the proposal's sense. They overlap on
`String`, they are selected by name, and a crate that owns neither `serde::Serialize` nor `String` may
define more, because the provider trait is always implemented for a type the crate owns. This is the
overlap and orphan relief specialization cannot give, since the two providers are equally general and
neither is more specific than the other. The `ValueSerializer` component is parameter-targeted and the
contexts that wire it are **environmental contexts**, applications such as `AppA` and `AppB`.

### An incoherent bound resolves through the context, not at each call site

Boxy's `function::<T + TraitImpl<T>>` passes the impl at every call. CGP instead lets generic code
require the *consumer* trait on the context and defers the choice to wherever the context is defined.
A provider that needs to serialize a field's type asks the context with
[`#[uses]`](../cgp/reference/attributes/uses.md), and the context's
[`delegate_components!`](../cgp/reference/macros/delegate_components.md) table answers once for the
whole program that uses that context. Two applications may answer differently:

```rust
delegate_components! {
    AppA {
        open ValueSerializerComponent;
        @ValueSerializerComponent.Vec<u8>: SerializeHex,
    }
}

delegate_components! {
    AppB {
        open ValueSerializerComponent;
        @ValueSerializerComponent.Vec<u8>: SerializeBase64,
    }
}
```

This is the proposal's incoherence with a different resolution point. Boxy and Cairo resolve at the
call site (explicitly, or from what is in scope); CGP resolves at the context, so every call through
`AppA` agrees. That is also how CGP answers the `HashMap` soundness concern the proposals must address
separately: a context selects one provider per component, so all code sharing a context agrees on one
impl, which is the property the proposal recovers by moving `Hash` onto the type definition. The
[type classes](type-classes.md) comparison develops this as "incoherent instances made deterministic".

### Passing an impl explicitly is a higher-order provider

Where the proposals and Cairo let a caller pass an impl as a parameter, CGP has
[higher-order providers](../cgp/concepts/higher-order-providers.md). A provider takes another provider
as a type parameter and binds it with [`#[use_provider]`](../cgp/reference/attributes/use_provider.md),
which is Cairo's `impl TDrop: Drop<T>` as a Rust generic:

```rust
#[cgp_impl(new ScaledArea<InnerCalculator>)]
#[use_provider(InnerCalculator: AreaCalculator)]
impl<InnerCalculator> AreaCalculator {
    fn area(&self, #[implicit] scale_factor: f64) -> f64 {
        InnerCalculator::area(self) * scale_factor * scale_factor
    }
}
```

A context wires `AreaCalculatorComponent: ScaledArea<RectangleArea>`, naming the inner impl the way a
Cairo caller would have the compiler infer it. The difference is again where the choice lives. CGP's
author's draft compares the two directly and notes that assembling providers explicitly at every call
site, Cairo-style, is possible in CGP but tedious, and that idiomatic CGP defers the assembly to the
context, which is more verbose up front and more predictable at scale. Higher-order providers are the
exception for the cases where a provider must override its inner choice locally, and they default their
inner parameter to [`UseContext`](../cgp/reference/providers/use_context.md) so the context's wiring is
the fallback.

### A capability is a context field; the `with` block is the context

Mandry's `with arena: &BasicArena` clause declares a value the function needs from its environment. CGP
declares the same thing as an [implicit argument](../cgp/concepts/implicit-arguments.md), which reads a
field of the context every provider already receives as `self`. The greeter from the
[Hello World tutorial](../website/tutorials/hello-world.md) is the smallest instance:

```rust
#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self, #[implicit] name: &str) -> String {
        format!("Hello, {name}!")
    }
}
```

The `with` block that supplies the capability becomes a context type carrying the field, and the
binding happens when a value of that type is constructed:

```rust
#[derive(HasField)]
pub struct App {
    pub name: String,
}

delegate_components! {
    App {
        GreeterComponent: GreetHello,
    }
}

let app = App { name: "World".to_owned() };
app.greet();   // "Hello, World!"
```

`App` is the context, and constructing it is the `with` binding. The `cgp-serde` deserializer that
takes an arena from its context is the same pattern at the scale of Mandry's own example, and the
[coherence](../cgp/concepts/coherence.md) concept names it as the library-level form of the
contexts-and-capabilities proposal. Two properties of the proposal carry over exactly: the binding is
zero-cost, since a field read compiles to a load, and it is checked statically, since a missing field is
a compile error that [`check_components!`](../cgp/reference/macros/check_components.md) names at the
wiring site. The `App` here is an **environmental context** with one field, and `GreetHello` is
self-targeted.

### The context is the dictionary

The dictionary-passing account and CGP meet in one observation the author's draft develops at length:
the context *is* the top-level dictionary. In Nadrieril's elaboration every dictionary is a value passed
alongside the data. In CGP every provider receives the context, and the context's wiring table is a
type-level record of dictionaries, one `DelegateComponent` entry per component. The draft lowers a CGP
program to a dictionary-passing form in which the context becomes a struct whose fields are the other
dictionaries, and observes an almost one-to-one correspondence between a `delegate_components!` entry
and a field of that struct. The arrangement has a practical consequence the proposals have to solve
separately: because every dictionary reaches the others through the context, a graph of dependencies
with cycles resolves without an instantiation order, since the context is one stable root from which all
of them are reachable. That is the same property that lets CGP wire a table in any order, which the
[ML modules](ml-modules.md) comparison contrasts with manual functor application.

### What CGP cannot express

The proposals reach two places CGP does not, and both follow from CGP being a library with a single
context type. The first is *inference from scope*. Cairo and the named-impl proposal let the compiler
pick an impl from those visible at a call site; CGP has no such search, and a context must name every
provider it uses. The second is *nested, dynamically scoped bindings*. Mandry's `with` blocks nest, and
Nadrieril's *scoped impls* would let an inner scope override an outer impl for the code it encloses. In
CGP every binding lives at the one place the concrete context is defined, so an inner scope cannot
shadow a provider without defining a new context type, and the author's draft observes that supporting
it would push CGP toward something resembling inheritance between contexts. A third limit concerns
ownership: a provider receives the context as `&self`, so a capability that must be `&mut` or owned
needs interior mutability or cloning rather than the ownership-aware design the proposals discuss. The
draft argues the first two restrictions are also a discipline, since all bindings for a context are
readable in one place, but it presents them as restrictions.

## What users like and dislike

Coherence is valued in the Rust community for concrete reasons, and any proposal to relax it has to
answer them. It makes `HashMap` and `BTreeMap` sound without the programmer thinking about it, it lets
generic code resolve bounds transitively with no impl named, and it gives library authors a semver story:
adding an impl cannot break a downstream crate's resolution. The proposals themselves take these as
constraints. Boxy's post spends much of its length on the `HashMap` and associated-type soundness
arguments, and Nadrieril's on what beyond individual proofs is needed for soundness.

The dislikes are equally concrete and long-standing. The orphan rule is a durable frustration, documented
in a repository of design notes devoted to it and to the workarounds it forces
([Ixrec, *rust-orphan-rules*](https://github.com/Ixrec/rust-orphan-rules)). Developers hand-roll CGP's
own marker-struct technique to get around the overlap rule
([Greyblake, *Alternative blanket implementations for a single Rust trait*](https://www.greyblake.com/blog/alternative-blanket-implementations-for-single-rust-trait/)).
Specialization's tracking issue has been open for ten years with a soundness hole nobody has closed, and
the standard library's own use of `min_specialization` shows the demand is real. And the
ecosystem-evolution problem Boxy names, that `serde`'s position is entrenched partly because the orphan
rule prevents alternatives from covering the same types, is a complaint about the ecosystem's shape
rather than about any one program. Against the newer proposals the recurring objections are complexity,
migration of the existing ecosystem, and the risk of losing the guarantees coherence gives for free.
Specialization has an accepted RFC and no path to stabilization; the named-impl, dictionary-passing, and
capability designs have not reached an RFC at all.

## How CGP compares

CGP delivers a fragment of each proposal on stable Rust, and the trade is explicitness for availability.
Against *specialization*, CGP permits equally general overlapping impls and orphan impls, which
specialization does not, and it has no soundness problem, because no impl is chosen implicitly for
generic code; the cost is that a context names its provider where specialization would pick the most
specific impl automatically. Against *named impls*, CGP has them today as providers, resolved at the
context rather than at each call, which loses call-site flexibility and gains agreement across everything
that shares a context. Against *contexts and capabilities*, CGP supplies values from a context's fields
with the same zero cost and static check, but only through `&self`, and only from one flat context
rather than nested `with` blocks. Against *dictionary passing*, CGP is the same arrangement expressed in
types, with the context as the root dictionary.

The costs beyond the two structural limits are the ordinary CGP costs. The provider trait has to be
defined through [`#[cgp_component]`](../cgp/reference/macros/cgp_component.md), so CGP cannot retrofit
an existing foreign trait such as `serde::Serialize` without a parallel component, where a language
change would apply to every trait. The wiring is code somebody writes and reads, where a language
feature would infer it. And the raw diagnostics are trait-solver output over generated types.
`cargo cgp check` leads with the root cause for the classes it recognizes, and the tool is a
v0.1.0-alpha that does not yet reshape every class. Where a program's need is exactly a specialized fast
path for one type under a blanket impl, `min_specialization` on nightly, or a manual dispatch trick on
stable, is the smaller tool. Where the need is several equally valid impls chosen per application, impls
for types the program does not own, or environment values reaching deep code without parameters, CGP is
the only one of these that can be used today, and its explicitness is the price of that.

## Presenting CGP to someone who knows this

A Rust reader who has followed these proposals holds the exact vocabulary CGP needs, so use it. A
**provider is a named impl**, a **consumer-trait bound on the context is an incoherent trait bound**, a
**higher-order provider is an impl passed as a parameter**, an **implicit argument is a capability**, and
**defining a context and its wiring is the `with` block**. Then say the one sentence that positions CGP
correctly: CGP is a library-level desugaring of a fragment of these proposals, available on stable Rust
now, with all bindings declared in one place. That framing invites the reader to check the claim against
designs they already know rather than to learn a new paradigm.

Correct two expectations before they mislead. The first is *inference*. A reader who knows Cairo or the
named-impl sketch expects the compiler to pick an impl from scope, and CGP never does; the wiring table
is written by hand. Present that as the reason CGP avoids the fragility the author's own draft finds in
Cairo, where imports decide resolution and two call sites can disagree, and as the same move the
[type classes](type-classes.md) comparison describes: incoherence made deterministic by naming. The
second is *scope*. A reader who knows contexts and capabilities expects nested `with` blocks that shadow
each other, and CGP's bindings are flat. Say so, and say that the author's own analysis treats this as
both a limitation and a discipline.

For the language-design reader specifically, the concessions are the contribution. This reader wants to
know what a working implementation of a fragment of Incoherent Rust reveals about the design: that a
single top-level context makes dependency instantiation and cyclic dependencies tractable, that resolving
at the context rather than the call site preserves the `HashMap`-style agreement the proposals otherwise
have to recover, that `&self`-only access is a real restriction on capabilities, and that nested scoping
does not fit the single-context model. Write those as findings, with the code that demonstrates them,
rather than as a pitch. The author's draft closes by saying that if these features land in the language,
much of the CGP library becomes unnecessary, and that this was always the goal. That is the sentence
this reader trusts most, and a piece for them should be willing to say it.

The framing to avoid is "CGP is specialization for stable Rust". It is not. It does not pick a more
specific impl, it does not touch existing traits, and it asks for wiring specialization would infer. A
reader who arrives expecting `default fn` will feel misled. Say instead that CGP addresses the two
problems specialization leaves open, equally general overlap and orphans, by naming implementations and
choosing them per context, and let the reader who wanted specialization decide whether that is the
problem they have.

## Sources

The account of the related work draws on the Rust Reference and RFCs, the specialization tracking
issue, the design posts by Boxy, Nadrieril, and Tyler Mandry, the Cairo book, and the knowledge base's
record of CGP's author's own engagement with the discussion. The CGP snippets are taken from the
[coherence](../cgp/concepts/coherence.md) concept, the [area calculation](../examples/area-calculation.md)
example, and the [Hello World tutorial](../website/tutorials/hello-world.md).

- [Rust Reference — *Implementations*](https://doc.rust-lang.org/reference/items/implementations.html) and [RFC 2451 — re-rebalancing coherence](https://rust-lang.github.io/rfcs/2451-re-rebalancing-coherence.html) — the orphan rule with its local-type and uncovered-parameter conditions, and the overlap rule.
- [RFC 1210 — impl specialization](https://rust-lang.github.io/rfcs/1210-impl-specialization.html) and [tracking issue #31844](https://github.com/rust-lang/rust/issues/31844) — the strictly-more-specific rule, the `default` keyword, the `AddAssign` example, the lifetime-dispatch soundness hole, and the `min_specialization` subset that remains the usable fragment.
- [Boxy, *An Incoherent Rust*](https://www.boxyuwu.blog/posts/an-incoherent-rust/) — named impls, `incoherent trait`, impls passed in bounds, the ecosystem-evolution motivation, and the `HashMap` and associated-type soundness answers.
- [Nadrieril, *Elaborating Rust Traits to Dictionary-Passing Style*](https://nadrieril.github.io/blog/2026/03/20/dictionary-passing-style.html) and [*What If Traits Carried Values*](https://nadrieril.github.io/blog/2026/03/22/what-if-traits-carried-values.html) — traits as structs and impls as values, the coherence friction, the open soundness questions, and the extension that carries values with the ownership, scoping, and closure problems it raises.
- [Mandry, *Contexts and capabilities in Rust*](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/) — the `with` clause and block, context-dependent trait impls, the zero-cost compilation to ordinary arguments, and the open thread-safety questions.
- [Cairo Book — *Traits in Cairo*](https://www.starknet.io/cairo-book/ch08-02-traits-in-cairo.html) and [*Generic Data Types*](https://www.starknet.io/cairo-book/ch08-01-generic-data-types.html) — the `impl Name of Trait` syntax, named and anonymous impl parameters, and compiler inference of the impl.
- [Ixrec, *rust-orphan-rules*](https://github.com/Ixrec/rust-orphan-rules) and [Greyblake, *Alternative blanket implementations for a single Rust trait*](https://www.greyblake.com/blog/alternative-blanket-implementations-for-single-rust-trait/) — the orphan rule as a durable frustration and the hand-rolled marker-struct workaround for overlap.
- [RustLab 2025 — *How to stop fighting with coherence*](https://contextgeneric.dev/blog/rustlab-2025-coherence) (record in [website/blog/rustlab-2025-coherence.md](../website/blog/rustlab-2025-coherence.md)) and the [record of the unpublished incoherent-Rust draft](../website/blog/incoherent-rust-today.md) — CGP's author's own argument for why specialization does not solve overlap, the context-as-dictionary framing, the limitations of the single-context approach, and the reading of Cairo.
