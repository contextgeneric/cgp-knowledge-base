# Dynamic dispatch, dynamic typing, and prototypal inheritance

Dynamically typed languages resolve almost everything at runtime. A method call is *dynamically
dispatched* to an implementation chosen from the receiver, an object's behavior is looked up in a
*vtable* or a method dictionary, code is written in *duck-typed* style that trusts a value to respond
to the messages sent to it, and shared behavior is inherited by *delegation* along a prototype chain.
CGP reproduces the openness all of this buys: many interchangeable implementations behind one
interface, behavior assembled by delegation, defaults inherited from a shared table, and provider code
that reads as if it sends messages to an object. But CGP resolves every bit of it at compile time into
direct, monomorphized calls, so its vtable is a type-level table erased before the program runs and its
delegation chain is walked by the type checker rather than the CPU.

## Purpose

Dynamic dispatch decouples a call site from the implementation it invokes, so one piece of code works
over many implementations chosen later. When code calls `shape.area()`, dynamic dispatch lets the
receiver decide the concrete implementation rather than fixing it where the call is written, which is
what makes polymorphism, plugins, and open extension possible. Dynamically typed languages take this to
its limit. Nothing about the receiver's type is fixed at compile time, so a value is whatever it can
*do*, behavior is shared by pointing one object at another, and the whole program is malleable at
runtime. The appeal is flexibility and immediacy: write against an interface without declaring it,
extend without recompiling, explore in a REPL.

CGP performs the same decoupling, and the knowledge base already draws the connection. The
[`delegate_components!`](../cgp/reference/macros/delegate_components.md) reference introduces a
context's wiring as "a type-level table, analogous to an object's method table (vtable)", and the
[bypassing coherence](../cgp/concepts/coherence.md) concept adds that, unlike a real vtable, CGP's
resolution is static and compiles down to direct calls with no runtime table. Both paradigms answer the
question "how does a call reach an implementation chosen elsewhere?", dynamic languages by looking it up
at runtime and CGP by resolving it at compile time through the trait system. This document meets the
reader who thinks in objects, messages, vtables, and prototypes, and shows where CGP's static mirror of
those mechanisms lands. It is the object-oriented, dynamic-language counterpart to the type-theoretic
[type classes](type-classes.md) and [ML modules](ml-modules.md) comparisons. The *type-system* side of
duck typing, structural versus nominal typing, is developed in [row polymorphism](row-polymorphism.md),
so this document leans on that one for the shape theory and keeps its own focus on dispatch, delegation,
and the feel of the code.

## The concept in depth

Dynamic languages layer several ideas that are worth keeping distinct: *dynamic typing* and the *duck
typing* style it enables, *dynamic dispatch* as the runtime resolution of a call, the *vtable* and
method-dictionary machinery that implements it, and *prototypal inheritance* as the runtime sharing of
behavior by delegation. The subsections build up in that order and close on the property of delegation,
that `self` stays bound to the original object, which lines up with CGP most precisely.

### Dynamic typing and duck typing

A dynamically typed language checks types at runtime, and *duck typing* is the programming style this
permits: an object's usability is decided by the methods and properties it has, not by a class it
declares or an interface it implements. The maxim is "if it walks like a duck and quacks like a duck,
then it is a duck". A function that calls `x.quack()` works for *any* `x` that responds to `quack`,
with no declared relationship between them ([*Duck typing*, Wikipedia](https://en.wikipedia.org/wiki/Duck_typing)).
Code written this way sends messages to a value and trusts it to respond, deferring the question "does
it have this method?" to the moment the call runs. Python, Ruby, JavaScript, and Smalltalk are the
canonical homes of the style, and its whole appeal is that an interface need never be spelled out: you
write the calls, and any object that can service them qualifies.

### Dynamic dispatch and late binding

Dynamic dispatch is the runtime selection of which implementation a method call invokes, based on the
receiver. Also called *late binding*, it resolves the association between a call and the code it runs at
runtime rather than at compile time, and it is what lets a single interface invoke different methods
depending on the object's actual type ([*Dynamic dispatch*, Wikipedia](https://en.wikipedia.org/wiki/Dynamic_dispatch)).
Smalltalk gave the purest form. Every call is a *message send*, resolved by a `send` operation that
takes the receiver and the message name and, *at call time*, consults the receiver's class method
dictionary to find the method to run. Statically typed object languages such as C++, Java, and Rust
offer the same late binding for methods marked virtual, dispatching on the single receiver. A few
languages (CLOS, Julia) generalize to *multiple dispatch*, choosing on the runtime types of several
arguments at once.

### Vtables and method dictionaries

A vtable stores the method implementations used for dynamic calls. Rust's trait-object pointers
pair a pointer to the value with a pointer to a vtable containing the relevant method pointers.
The call therefore follows an indirect route, as described in the
[Rust Reference](https://doc.rust-lang.org/reference/types/trait-object.html).

Indirect dispatch can limit optimization, but its cost depends on the call and compiler.
Devirtualization can recover a direct call when the target is known. Dynamic-language runtimes
also optimize property and method lookup; V8's hidden classes help it identify object layouts.
The [V8 documentation](https://v8.dev/docs/hidden-classes) describes that mechanism. A comparison
of dispatch mechanisms alone does not establish a performance ranking for whole programs.

### Prototypal inheritance and delegation

Prototype-based languages share behavior not through classes but by *delegation*. An object holds a link
to another object, its prototype, and a message the object does not handle is forwarded to the
prototype, walking a chain until the message is answered or the chain ends. Henry Lieberman introduced
this model in 1986 and the Self language realized it. It needs no classes: an object is a blueprint for
others, and behavior is inherited by pointing at it
([Lieberman, *Using Prototypical Objects to Implement Shared Behavior in Object-Oriented Systems*](https://web.media.mit.edu/~lieber/Lieberary/OOP/Delegation/Delegation.html)).
JavaScript is its most widely used descendant. Every object has a `[[Prototype]]` link,
`Object.create(proto)` sets it, and a property lookup walks the prototype chain, with an own property
*shadowing* an inherited one ([MDN, *Inheritance and the prototype chain*](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain)).
Lua expresses the same idea through the `__index` metamethod, and a missing method can even be caught
by a fallback hook: Ruby's `method_missing`, Python's `__getattr__`, Lua's `__index` function.

The property that distinguishes *delegation* from mere forwarding is the one that matters most for CGP:
`self` stays bound to the original receiver. When an object delegates a message to its prototype and the
prototype's method refers to `self`, that `self` denotes the object that *originally received* the
message, not the prototype the method was found on ([Lieberman 1986](https://web.media.mit.edu/~lieber/Lieberary/OOP/Delegation/Delegation.html)).
This is what makes delegation a form of inheritance rather than plain message forwarding. The delegate
supplies the *behavior*, but the original object remains the *identity* that behavior runs against, so a
method inherited from a prototype still sees the receiver's own state. Forwarding, by contrast, rebinds
`self` to the object the message was passed to, and loses that connection. This rule is the hinge on
which the CGP comparison turns.

## How CGP expresses it

CGP reproduces dynamic dispatch, vtables, and prototypal delegation, but resolves each at compile time.
What is a runtime lookup in a dynamic language is a type-resolution step in CGP that monomorphizes to a
direct call. A [component](../cgp/reference/macros/cgp_component.md) is the interface, a
[provider](../cgp/reference/macros/cgp_impl.md) is an implementation, the context's
[wiring table](../cgp/reference/macros/delegate_components.md) is its vtable, and
[aggregate providers](../cgp/concepts/aggregate-providers.md) and
[namespaces](../cgp/concepts/namespaces.md) are its delegation chain. The correspondence is close
construct by construct, and it breaks in exactly one place, that everything is static, which is the
source of both what CGP gains and what it gives up.

### CGP code reads like a duck-typed program

The most immediate resemblance is stylistic. A CGP provider is written against an unknown context and
reads like duck-typed code that sends messages to a receiver and trusts it to respond. A provider calls
methods on `self` and reads values from it without naming a concrete type or declaring the interface it
depends on in its signature:

```rust
#[cgp_impl(new GreetHello)]
#[uses(HasName)]
impl Greeter {
    fn greet(&self) {
        println!("Hello, {}!", self.name());
    }
}
```

The body `self.name()` is a message send to a context whose type is not written down. With an
[`#[implicit]`](../cgp/reference/attributes/implicit.md) argument the dynamic feel is stronger still: a
value appears from the context, as an unbound name would in Ruby or Python:

```rust
#[cgp_fn]
pub fn greet(&self, #[implicit] name: &str) -> String {
    format!("Hello, {name}!")
}
```

This is unlike ordinary statically typed Rust, where calling `x.name()` demands a concrete `x: Person`
or a spelled-out bound `fn greet<C: HasName>(c: &C)` that names the trait in the signature. CGP moves
the bound into [`#[uses]`](../cgp/reference/attributes/uses.md) and abstracts the context away, so the
provider body carries *less* visible type ceremony than a plain generic function and reads as if it were
duck-typed: assume the context has a `name`, and greeting works. The decisive difference is *when* the
trust is discharged. A duck-typed program finds out at runtime whether the object responds, and fails with
an `AttributeError` or `NoMethodError` if not. CGP finds out at compile time, because trait resolution
and [`check_components!`](../cgp/reference/macros/check_components.md) check the `#[uses(HasName)]`
dependency and the field access. That is Ruby's `respond_to?` guard moved to compile time and made
total. The field-based half of this is structural rather than merely stylistic: an `#[implicit]`
argument or a [`#[cgp_auto_getter]`](../cgp/reference/macros/cgp_auto_getter.md) resolves against *any*
context carrying a matching field, the duck-typing-as-a-type-system idea that
[row polymorphism](row-polymorphism.md) develops in full. CGP code looks duck-typed on the surface while
its resolution stays static and, at the wiring, nominal. The greeter here wires a **value context**: the
`Person` that is greeted carries the `name` field.

### Static dispatch with the flexibility of dynamic dispatch

CGP delivers the openness of dynamic dispatch (one interface, many implementations, the choice made
late) but resolves the choice at compile time and compiles it to a direct call. A caller writes
`context.area()` against the `CanCalculateArea` consumer trait without naming an implementation, exactly
as a dynamic call names a method and lets the receiver decide. The difference is that CGP's "receiver
decides" happens during type checking. The consumer-trait blanket impl generated by
[`#[cgp_component]`](../cgp/reference/macros/cgp_component.md) routes the call through the context's
[`DelegateComponent`](../cgp/reference/traits/delegate_component.md) table to the wired provider, and
the compiler resolves the whole routing and [monomorphizes it to a direct call](../cgp/concepts/coherence.md):
no fat pointer, no vtable load, no indirect jump. Rust already offers *real* dynamic dispatch through
`dyn Trait`, and CGP is its static sibling. Both let an implementation be chosen after the calling code
is written; one pays a runtime vtable indirection to do it and the other resolves it away entirely.
Where a component carries a generic parameter, CGP even reproduces *multiple* dispatch: the
[`open` statement](../cgp/reference/macros/delegate_components.md) selects a provider per value of a
type argument, dispatching on the context *and* that argument the way multimethods dispatch on several
runtime types, but decided at compile time.

### `DelegateComponent` is a compile-time vtable

The type-level table a context carries is a vtable that exists only during compilation. Each
[`DelegateComponent<Key>`](../cgp/reference/traits/delegate_component.md) impl on a context maps one
component key to the provider that implements it, precisely as a vtable slot maps a method to its
implementation:

```rust
delegate_components! {
    Rectangle {
        AreaCalculatorComponent: RectangleArea,
    }
}

// expands to the type-level table entry:
// impl DelegateComponent<AreaCalculatorComponent> for Rectangle {
//     type Delegate = RectangleArea;
// }
```

A wiring table resembles a vtable in its selection role, but its entries are trait impls mapping
component keys to provider types. Components may contain several methods, associated types, and
consts, so a component entry is not necessarily one method slot. The compiler resolves the table
without a runtime lookup.

Static wiring can coexist with runtime trait objects. A dyn-compatible consumer trait can be used
as `dyn CanCalculateArea`, including in a heterogeneous collection of concrete CGP contexts.
Each concrete context still uses its own static provider selection inside that dynamic call.

### Component delegation is delegation, with `self` bound

CGP's delegation chain is delegation in Lieberman's exact sense, because the context stays bound to the
original as lookup walks the chain. An [aggregate provider](../cgp/concepts/aggregate-providers.md)
bundles a group of component wirings, and a context delegates a whole group to it in one entry, so
resolution walks from the context through the bundle to a leaf provider:

```rust
delegate_components! {
    new GeometryComponents {
        AreaCalculatorComponent: RectangleArea,
        PerimeterCalculatorComponent: RectanglePerimeter,
    }
}

delegate_components! {
    Rectangle {
        [AreaCalculatorComponent, PerimeterCalculatorComponent]: GeometryComponents,
    }
}
```

When `rect.area()` resolves, the lookup walks `Rectangle`, then `GeometryComponents`, then
`RectangleArea`, and the *context stays `Rectangle`* at every step. The
[aggregate providers](../cgp/concepts/aggregate-providers.md) concept states outright that "the
context argument is `Rectangle` at every step; `GeometryComponents` appears only in the `Self`/delegate
position, never as the `Context`", so the leaf provider reads its fields and finds its trait dependencies
on `Rectangle`, the real context, not on the bundle. That is delegation's defining property. The
delegate chain supplies the *behavior* while `self`, the context, remains the original *identity* that
behavior runs against, never rebound to the prototype the method was found on. The
[`UseContext`](../cgp/reference/providers/use_context.md) provider is the same relationship pointed the
other way, letting a provider route a call back to the context's own wiring: the prototype consulting
its delegator. On the axis that separates delegation from forwarding, CGP's delegation *is* delegation,
resolved statically.

### Namespaces are shared prototypes with open slots, not shadowable ones

A CGP namespace is a shared table of wirings that many contexts inherit, which is the prototype's job.
But the override rule differs from JavaScript's, and the difference matters enough to state precisely.
In a prototype chain an own property *shadows* an inherited one. In CGP, **a key the namespace binds is
not overridable**: joining a namespace generates a forwarding impl covering every key the namespace
answers, so a direct entry for one of those keys overlaps it and is rejected with `E0119`
([namespaces](../cgp/concepts/namespaces.md)). What a context may supply is a *path the namespace routes
to but leaves unbound*, an open slot the namespace deliberately left for each context to fill:

```rust
delegate_components! {
    AppA {
        namespace DefaultNamespace;      // inherit every wiring the namespace binds

        @test.ShowImplComponent.u64:     // fill a slot the namespace routes but does not bind
            ShowWithDisplay,
    }
}
```

Namespaces inherit from one another, so a base namespace can be extended into a richer one that
contexts downstream pick up. The child may add entries and reroute subtrees the parent leaves open,
but it may not redefine a key the parent binds, which the same `E0119` catches:

```rust
cgp_namespace! {
    new ExtendedNamespace: DefaultNamespace {
        @cgp.core.error => @app,         // reroute an open subtree to the app's own entries
    }
}
```

`ExtendedNamespace` resolves everything `DefaultNamespace` does plus its own entries. The lookup that
walks these layers is the [`RedirectLookup`](../cgp/reference/providers/redirect_lookup.md) provider
tracing a type-level path, which is the prototype chain being walked, and the redirect that fires when a
key is not bound directly is the compile-time analogue of an `__index` or `method_missing` fallback.
The closer object-oriented analogy is therefore an abstract base class rather than a prototype: the
namespace fixes what every context agrees on and declares abstract slots each context must fill, and it
does not let a child silently redefine a concrete inherited member. As with everything else in CGP, the
chain is walked by trait resolution during compilation rather than by property lookup at runtime, so the
inheritance pays nothing at runtime and cannot be mutated once the program is built.

## What users like and dislike

Dynamic dispatch and dynamic typing are loved for the immediacy and flexibility they give, and the
praise is consistent across their communities. Duck typing lets a function work over any object that
responds to the messages it sends, which programmers value for *flexibility and reuse* (no interface to
declare, no hierarchy to fit into) and for *shorter code* and *rapid prototyping*, the reasons Ruby and
Python developers reach for it ([SitePoint, *Making Ruby Quack*](https://www.sitepoint.com/making-ruby-quack-why-we-love-duck-typing/);
[GeeksforGeeks, *Type Systems*](https://www.geeksforgeeks.org/python/type-systemsdynamic-typing-static-typing-duck-typing/)).
Dynamic dispatch is what makes polymorphism and open extension work, and prototypal inheritance is
prized for its malleability. Objects can be created, linked, and modified at runtime, behavior can be
shared without a class hierarchy, and a running program can be reshaped live. Metaprogramming hooks such
as `method_missing` and `__getattr__` let a single object answer messages it was never written to
handle, which powers proxies, DSLs, and ORMs.

The complaints are the mirror image of that flexibility, and they cluster on safety and cost. Because
type checks are deferred, a mistake surfaces as a *runtime error* (an `AttributeError`, a
`NoMethodError`, an "undefined is not a function") discovered only when the offending line runs, which
makes refactoring hazardous and large systems harder to trust. The standard mitigation is to add tests,
type annotations, or a `respond_to?` guard before the call
([DevGex, *Duck Typing*](https://devgex.com/en/article/00035033); [SitePoint](https://www.sitepoint.com/making-ruby-quack-why-we-love-duck-typing/)).
Dynamic dispatch has a *performance cost*. Indirect calls can limit optimization, though devirtualization and inline caches may reduce the
cost. Dynamic runtimes also use hidden classes to optimize property lookup ([V8, *Hidden Classes*](https://v8.dev/docs/hidden-classes)). Prototypal
inheritance draws its own gripes: a mutable prototype chain is easy to get confused about, and
JavaScript's `this` binding, the very self-binding that makes delegation work, is a notorious source of
bugs when a method is detached from its receiver. And tooling suffers throughout, since an IDE cannot
reliably know what a value responds to when its type is not fixed.

## How CGP compares

Dynamic dispatch supports runtime choice, including mixed collections of implementations.
Dynamically typed languages also allow programs to accept objects without an explicit interface
declaration, and mutable object systems can change behavior while running. Those freedoms are
useful for interactive work and runtime extensibility.

Dynamic typing can defer unsupported-operation errors until execution. That cost does not apply
to every form of dynamic dispatch: Rust checks a trait object's interface at compile time.
Runtime lookup and indirect calls also have costs, though optimizations can reduce them.
Prototype mutation and call-dependent `this` binding add separate reasoning demands, as the
[MDN guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain)
explains.

CGP moves implementation selection into compilation and requires declarations and wiring to express
it. The learning cost includes tracing consumer traits through provider tables; the compile-time
cost includes trait resolution and monomorphization. Static wiring itself cannot discover plugins,
replace a provider on a live value, or handle an undeclared operation. Those features need other
runtime mechanisms, which CGP code can use alongside its wiring.

CGP's raw diagnostics expose generated traits and types.
[`cargo cgp check`](../cargo-cgp/reference/usage.md) leads with the root cause for the classes it recognizes,
and the tool is a v0.1.0-alpha that does not yet reshape every class. The
[Modularity Hierarchy](../cgp/concepts/modularity-hierarchy.md) compares these costs with ordinary
traits, generics, and trait objects.

### Where the other approach fits

Runtime dispatch fits implementations chosen while the program runs, such as mixed collections or
runtime-selected services. Dynamic object systems additionally support changing object behavior
and intercepting otherwise unknown messages. Plugin loading requires an appropriate loading and
interface mechanism as well as dispatch; a vtable alone does not provide it.

Rust's `dyn Trait` is useful for runtime polymorphism and can coexist with CGP. A context may hold a
trait object, or a dyn-compatible consumer trait may be used as a trait object. CGP wiring fits
implementation choices known at build time, where reusable providers justify the additional tables.

## Presenting CGP to someone who knows this

Separate dynamic dispatch, dynamic typing, and prototype mutation before mapping them to CGP.
Rust trait objects select implementations at runtime while checking their interfaces statically.
A missing-method failure associated with duck typing is not a cost of every dynamically dispatched
call.

Use the vtable analogy for selection, with its limits stated immediately. CGP wiring maps component
keys to provider types and is resolved statically; a component can group multiple items. Provider
bodies run at runtime, and static calls are not guaranteed to inline. The receiver remains the
original context through delegation, while namespaces customize unbound paths rather than shadowing
bound entries.

Present static and dynamic dispatch as composable. A dyn-compatible consumer trait can be used as a
trait object, and a context can hold runtime-selected services. CGP wiring itself does not implement
plugin loading or live rebinding. Avoid blanket performance rankings without measurements.

## Sources

The public version of this document is the website's
[dynamic-dispatch comparison page](https://contextgeneric.dev/docs/comparisons/dynamic-dispatch), ported per the
[comparison page guide](../website/writing-guides/related-work.md); a change here updates that page
in the same change.

The account of the related work draws on standard references for dynamic dispatch and object models,
the primary literature on prototype-based programming, and cited community writing for sentiment. The
CGP snippets are drawn from the knowledge base's [aggregate providers](../cgp/concepts/aggregate-providers.md),
[namespaces](../cgp/concepts/namespaces.md), and [consumer/provider](../cgp/concepts/consumer-and-provider-traits.md)
material, and the namespace override rule from the namespaces concept and the
[override-conflict error class](../cgp/errors/wiring/namespace-override-conflict.md).

- [*Dynamic dispatch* (Wikipedia)](https://en.wikipedia.org/wiki/Dynamic_dispatch) and [*Virtual method table* (Wikipedia)](https://en.wikipedia.org/wiki/Virtual_method_table) — late binding as runtime resolution of a call, Smalltalk's message-send `send`, single versus multiple dispatch, and the per-class vtable of function pointers reached through an object's vtable pointer.
- [*Duck typing* (Wikipedia)](https://en.wikipedia.org/wiki/Duck_typing) — an object's usability decided by the methods and properties it has rather than a declared class or interface.
- [geo-ant, *Rust Dyn Trait Objects and Fat Pointers*](https://geo-ant.github.io/blog/2023/rust-dyn-trait-objects-fat-pointers/) and [*Trait objects*, The Rust Programming Language Book](https://doc.rust-lang.org/book/ch18-02-trait-objects.html) — Rust's own dynamic dispatch as a data-pointer/vtable-pointer fat pointer, and the vtable's contents, the runtime counterpart to CGP's compile-time table.
- [Lieberman, *Using Prototypical Objects to Implement Shared Behavior in Object-Oriented Systems* (OOPSLA 1986)](https://web.media.mit.edu/~lieber/Lieberary/OOP/Delegation/Delegation.html) — delegation as forwarding unhandled messages to a prototype, and the defining rule that `self` stays bound to the original receiver, which distinguishes delegation from forwarding and matches CGP's context binding.
- [MDN, *Inheritance and the prototype chain*](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain) — JavaScript's `[[Prototype]]` link, `Object.create`, prototype-chain lookup, and own-property shadowing, the shadowing rule CGP namespaces do not share.
- [*Maps (Hidden Classes) in V8*](https://v8.dev/docs/hidden-classes) — hidden classes and inline caches descending from the Self language's maps and polymorphic inline caches, the engineering that dynamic dispatch's runtime cost demands.
- [SitePoint, *Making Ruby Quack — Why We Love Duck Typing*](https://www.sitepoint.com/making-ruby-quack-why-we-love-duck-typing/), [GeeksforGeeks, *Type Systems: Dynamic, Static & Duck Typing*](https://www.geeksforgeeks.org/python/type-systemsdynamic-typing-static-typing-duck-typing/), and [DevGex, *Duck Typing*](https://devgex.com/en/article/00035033) — community sentiment on what duck typing and dynamic typing buy (flexibility, brevity, rapid development) and cost (runtime errors, the `respond_to?` guard, refactoring hazards).
