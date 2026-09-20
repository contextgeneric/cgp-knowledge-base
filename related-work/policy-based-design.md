# C++ policy-based design, CRTP, and concepts

Policy-based design is the C++ technique of building a class from interchangeable *policy* classes
supplied as template parameters, so that a *host* class such as
`SmartPtr<T, OwnershipPolicy, CheckingPolicy>` composes its behavior at compile time from parts a user
chooses. The curiously recurring template pattern (CRTP) is its companion idiom for static
polymorphism, and C++20 concepts are the language's answer to the implicit, duck-typed interfaces both
rely on. CGP's context, providers, and wiring table are the same compile-time composition with the same
zero runtime cost. CGP differs in declaring the interface a policy must meet as a trait, checking the
composition where the provider is written rather than where the host is instantiated, and gathering
every choice into one wired context rather than a parameter list repeated at every use.

## Purpose

Policy-based design solves the problem of letting one class support many combinations of behavior
without runtime dispatch or a class per combination. Andrei Alexandrescu named the technique in *Modern
C++ Design* (2001): decompose a class's behavior into orthogonal *policies*, each a small class that
implements one aspect (how to allocate, how to check, how to convert), and write the main class as a
template that takes the policies as parameters and derives from or holds them. "A library or module can
support an exponential number of different behavior combinations, resolved at compile time"
([Wikipedia, *Modern C++ Design*](https://en.wikipedia.org/wiki/Modern_C%2B%2B_Design)). Wikipedia
describes it as "a compile-time variant of the strategy pattern"
([Wikipedia, *Policy-based design*](https://en.wikipedia.org/wiki/Policy-based_design)): where the
strategy pattern selects an algorithm through a virtual call at runtime, a policy selects it through a
template argument at compile time, and the compiler inlines the result.

This is the comparison a C++ programmer reaches for first when they meet CGP, and it is a close one. A
CGP [context](../cgp/concepts/consumer-and-provider-traits.md) is a host class, a
[provider](../cgp/reference/macros/cgp_impl.md) is a policy class, and a
[`delegate_components!`](../cgp/reference/macros/delegate_components.md) table is the template
argument list that selects the policies, resolved at compile time and monomorphized to direct calls
exactly as a template instantiation is. The systems programmer who already trusts templates to be
zero-cost will trust CGP's wiring for the same reason. The differences are in what the two systems make
explicit and when they check it, and those differences are where C++'s own evolution, from duck-typed
templates to concepts, has been heading.

## The concept in depth

The technique has three parts that C++ programmers use together. *Policies* are the interchangeable
parts and the *host class* is what composes them. *CRTP* is how a base template reaches its derived
class statically, which is how a policy or a mixin calls back into the class it is part of. *Concepts*
are the C++20 addition that turns a template's implicit requirements into a checked, named interface.
The subsections take them in that order, with the pieces of the C++ language each depends on.

### Policies and the host class

A policy class implements one aspect of behavior, and a host class template takes its policies as type
parameters and composes them, typically by inheriting from them. The Wikipedia example composes a
greeting from an output policy and a language policy:

```cpp
template <typename OutputPolicy, typename LanguagePolicy>
class HelloWorld : private OutputPolicy, private LanguagePolicy {
public:
    void run() const {
        write(message());
    }
};

class WriteToStdout {
protected:
    void write(std::string&& message) const {
        std::println("{}", message);
    }
};

class EnglishMessage {
protected:
    [[nodiscard]] std::string message() const noexcept { return "Hello, World!"; }
};

class GermanMessage {
protected:
    [[nodiscard]] std::string message() const noexcept { return "Hallo Welt!"; }
};

int main() {
    HelloWorld<WriteToStdout, EnglishMessage> helloWorld;
    helloWorld.run();

    HelloWorld<WriteToStdout, GermanMessage> helloWorld2;
    helloWorld2.run();
}
```

`HelloWorld<WriteToStdout, GermanMessage>` is a distinct type from
`HelloWorld<WriteToStdout, EnglishMessage>`, each with its own inlined `run`. The host's `run` body
calls `write` and `message` without knowing which policy supplies them, and the compiler checks that the
chosen policies do supply them only when `run` is instantiated. Alexandrescu's book develops the same
shape at length for a `SmartPtr` whose ownership, checking, storage, and conversion are each a policy,
which is where the technique's power and its costs both show
([Wikipedia, *Modern C++ Design*](https://en.wikipedia.org/wiki/Modern_C%2B%2B_Design)).

### The policy interface is implicit

A policy has no declared interface. The host calls `message()` and `write(...)`, and any class that
happens to have members with those names and compatible types qualifies. Wikipedia states the
consequence plainly: "the policy interface doesn't have a direct, explicit representation in code, but
rather is defined implicitly, via duck typing, and must be documented separately and manually"
([Wikipedia, *Policy-based design*](https://en.wikipedia.org/wiki/Policy-based_design)). The same
structural rule governs every C++ template, and it is the source of the classic template failure mode:
a policy missing a member produces an error at the point of use inside the host's body, after
instantiation, phrased in terms of the substituted types rather than the requirement that was violated.
The [row polymorphism](row-polymorphism.md) comparison places this duck typing in the wider structural
versus nominal landscape; here it matters as the property concepts were added to repair.

### CRTP: a base that knows its derived class

The curiously recurring template pattern lets a base class template call into the class deriving from
it, statically. The derived class passes itself as the base's template argument, and the base reaches it
with a `static_cast`:

```cpp
template <class Derived>
struct Base {
    void name() { static_cast<Derived*>(this)->impl(); }
protected:
    Base() = default;
};

struct D1 : public Base<D1> { void impl() { std::puts("D1::impl()"); } };
struct D2 : public Base<D2> { void impl() { std::puts("D2::impl()"); } };
```

Jim Coplien coined the name in 1995, and the pattern is C++'s realization of F-bounded polymorphism
([Wikipedia, *Curiously recurring template pattern*](https://en.wikipedia.org/wiki/Curiously_recurring_template_pattern)).
Its purpose is static polymorphism: `Base` exposes an interface and each derived class implements it,
with no virtual call, because `Derived` is known at compile time. Policies and mixins use CRTP whenever
they need the host's own type, for instance to return `*this` as the derived type or to read the host's
data. C++23's *deducing this* (`void name(this auto&& self) { self.impl(); }`) removes the manual
template parameter and cast for the common case ([cppreference, *CRTP*](https://en.cppreference.com/w/cpp/language/crtp)).
The pattern's well-known limit is homogeneity: `Base<D1>` and `Base<D2>` are unrelated types, so a
`std::vector<Base*>` cannot hold both, and a program that needs a heterogeneous collection is back to
virtual functions.

### Concepts: making the requirements explicit

C++20 concepts give a template's requirements a name and let the compiler check them before entering
the body. A concept is a named predicate over types, and a `requires` clause or a constrained parameter
attaches it to a template:

```cpp
template<typename T>
concept Hashable = requires(T a) {
    { std::hash<T>{}(a) } -> std::convertible_to<std::size_t>;
};

template<Hashable T>
void f(T) {}
```

The gain is in diagnostics and in intent. Without concepts, calling `std::sort` on a list iterator
produces dozens of lines about an invalid binary expression deep inside the algorithm; with concepts the
error reads that the `RandomAccessIterator` concept was not satisfied, at the call
([cppreference, *Constraints and concepts*](https://en.cppreference.com/w/cpp/language/constraints)).
A policy-based host can constrain its policy parameters with concepts and so give the implicit policy
interface the explicit representation Wikipedia says it lacks. What concepts do *not* change is when the
body is checked. Satisfaction "is checked by substituting the parameter mapping and template arguments
into the expression", at instantiation, and a template body is still not verified against its concepts
at definition. A host may use a member its concept never mentions and compile until a policy without
that member is substituted. This is the instantiation-time checking that separates templates from
traits, and the [reflection](reflection.md) comparison meets the same property in Zig's `comptime`.

## How CGP expresses it

CGP is policy-based design with the policy interface declared as a trait, the composition gathered into
a wired context, and the checking moved to the provider's definition. The correspondence is construct
for construct, and the differences fall out of Rust's trait system doing the job that C++ templates
leave to duck typing.

### Providers are policies; the context is the host

Each policy becomes a provider of a component, and the host becomes a context that wires one provider
per component. The greeting example in CGP declares the two policy interfaces as components, writes each
policy as a provider, and writes the host's `run` as a function over any context that supplies both:

```rust
#[cgp_component(MessageProvider)]
pub trait HasMessage {
    fn message(&self) -> String;
}

#[cgp_component(Writer)]
pub trait CanWrite {
    fn write(&self, message: String);
}

#[cgp_impl(new EnglishMessage)]
impl MessageProvider {
    fn message(&self) -> String {
        "Hello, World!".to_owned()
    }
}

#[cgp_impl(new GermanMessage)]
impl MessageProvider {
    fn message(&self) -> String {
        "Hallo Welt!".to_owned()
    }
}

#[cgp_impl(new WriteToStdout)]
impl Writer {
    fn write(&self, message: String) {
        println!("{message}");
    }
}

#[cgp_fn]
#[uses(HasMessage, CanWrite)]
pub fn run(&self) {
    self.write(self.message());
}
```

Two hosts are two contexts, each selecting its policies in a wiring table where the C++ version passes
them as template arguments:

```rust
pub struct EnglishApp;
pub struct GermanApp;

delegate_components! {
    EnglishApp {
        MessageProviderComponent: EnglishMessage,
        WriterComponent: WriteToStdout,
    }
}

delegate_components! {
    GermanApp {
        MessageProviderComponent: GermanMessage,
        WriterComponent: WriteToStdout,
    }
}

check_components! { EnglishApp { MessageProviderComponent, WriterComponent } }
check_components! { GermanApp { MessageProviderComponent, WriterComponent } }

EnglishApp.run();   // Hello, World!
GermanApp.run();    // Hallo Welt!
```

`EnglishApp` and `GermanApp` are **environmental contexts**, fieldless types whose only job is to carry
the choice, exactly as `HelloWorld<WriteToStdout, EnglishMessage>` is a type whose only job is to fix
the policies. Both compositions resolve at compile time, both monomorphize `run` per host, and both emit
a direct call to the chosen `message` and `write`. The difference is in the declarations around them.
`HasMessage` and `CanWrite` are the policy interfaces written down, which the C++ version documents
"separately and manually", and `#[uses(HasMessage, CanWrite)]` is the host stating which policies its
body relies on.

### Policies as type parameters are higher-order providers

The wiring table is not the only place CGP can put a policy choice. C++ passes policies as template
parameters of the host, and CGP has the same form in the
[higher-order provider](../cgp/concepts/higher-order-providers.md): a provider whose type parameters
are other providers, bound with [`#[use_provider]`](../cgp/reference/attributes/use_provider.md). The
`HelloWorld` host template translates almost token for token:

```rust
#[cgp_component(Runner)]
pub trait CanRun {
    fn run(&self);
}

#[cgp_impl(new HelloWorld<W, M>)]
#[use_provider(W: Writer)]
#[use_provider(M: MessageProvider)]
impl<W, M> Runner {
    fn run(&self) {
        W::write(self, M::message(self))
    }
}

pub struct App;

delegate_components! {
    App {
        RunnerComponent: HelloWorld<WriteToStdout, GermanMessage>,
    }
}

check_components! { App { RunnerComponent } }

App.run();   // Hallo Welt!
```

The wiring entry names the C++ instantiation as a Rust type:
`HelloWorld<WriteToStdout, GermanMessage>` on both sides. The `#[use_provider(W: Writer)]` bound is the
concept the C++ version lacks, spelled out: it says `W` must implement the `Writer` provider trait for
this context, and it fills in the context argument so the body can call `W::write(self, ...)` as an
associated function. The policies in this form are not wired on the context at all. They are chosen
where the type is written, exactly as template arguments are, and a context could wire the English and
the German instantiation to two different components without either policy being a component of its
own.

The same shape works on a function, which is the closer reading of a C++ function template that takes
policy types. A [`#[cgp_fn]`](../cgp/reference/macros/cgp_fn.md) may be generic over providers, and its
generic parameters move onto the generated trait, so the caller instantiates it the way C++ instantiates
a template:

```rust
#[cgp_fn]
#[use_provider(W: Writer)]
#[use_provider(M: MessageProvider)]
pub fn hello<W, M>(&self) {
    W::write(self, M::message(self))
}

<App as Hello<WriteToStdout, EnglishMessage>>::hello(&App);   // Hello, World!
```

CGP therefore offers both placements, and choosing between them is the design decision the rest of this
document is about. Passing policies as type parameters keeps the choice at the instantiation site and
repeats it wherever the type is named, which is the C++ arrangement with its costs and its flexibility.
Wiring the policies as components on the context, as the first example does, names each choice once and
lets generic code require only the traits it uses. The [modularity hierarchy](../cgp/concepts/modularity-hierarchy.md)
places the higher-order form at its top tier and recommends it for the cases where a provider must fix
an inner choice locally rather than defer to the context. A higher-order provider may also give its
inner parameter the default [`UseContext`](../cgp/reference/providers/use_context.md), which routes the
inner call back to whatever the context wires for that component, per the
[higher-order providers](../cgp/concepts/higher-order-providers.md) concept. That is a default template
argument whose default is "whatever the host is wired with", and it has no C++ counterpart. The default
is written on the struct declaration (`pub struct HelloWorld<W, M = UseContext>(PhantomData<(W, M)>)`),
so a provider that wants one declares its struct by hand and drops the `new` keyword from `#[cgp_impl]`.

### `#[cgp_impl]` is CRTP with the cast done for you

A CGP provider's body refers to the context as `self` and `Self`, which is exactly what CRTP arranges
for a base class through `static_cast<Derived*>(this)`. The [`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md)
macro rewrites a provider written in consumer-trait shape into a provider-trait impl whose `Self` is the
provider's own marker and whose context is an explicit parameter, so the `self` a provider body uses is
the context, not the provider. A policy that needs the host's data reads it as an
[implicit argument](../cgp/concepts/implicit-arguments.md):

```rust
#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self, #[implicit] name: &str) -> String {
        format!("Hello, {name}!")
    }
}
```

In CRTP terms, `GreetHello` is the base template, the context is `Derived`, and the `#[implicit]`
argument is `static_cast<Derived*>(this)->name` with the cast replaced by a `HasField` bound the
compiler checks. C++23's deducing `this` reaches a similar ergonomics for member functions; CGP reaches it
for every provider, and it never has the CRTP hazard of passing the wrong derived class, because the
context is supplied by the wiring rather than named at each derivation.

### Checked at definition, not at instantiation

The deepest difference is when a mistake surfaces. A C++ host body is checked when it is instantiated
with concrete policies, and even with concepts the body is not verified against the concept at
definition. A CGP provider is checked when it is written. The `#[uses(HasMessage, CanWrite)]` bounds are
the whole contract `run` may rely on, and a call to a method outside them is an error at `run`'s
definition, for every context at once. The instantiation-time question that remains, whether a
particular context supplies what its providers need, is what
[`check_components!`](../cgp/reference/macros/check_components.md) answers, and it answers it at the
wiring site with the missing dependency named rather than inside a monomorphized body. This is the
modular checking that traits give and templates do not, the same property the
[type classes](type-classes.md) and [reflection](reflection.md) comparisons draw out against Haskell's
neighbors and Zig's `comptime`.

### One wired context instead of a repeated parameter list

A policy-based host carries its policies in its type, so every place that names the host names the
policies: `SmartPtr<Widget, RefCounted, NoChecking, DefaultStorage>` appears wherever such a pointer is
declared, and a helper generic over the host repeats the parameter list. Alexandrescu's book spends
effort on typedefs and default policies to contain this. CGP can reproduce that arrangement with a
higher-order provider, as the previous section shows, and it carries the same cost there: a
`HelloWorld<WriteToStdout, GermanMessage>` is named wherever it is used. The alternative CGP adds is to
wire the policies as components on the context, so the choices live in one `delegate_components!` table
on a context type that is named once, and code generic over the context requires only the traits it uses
through `#[uses]`. Adding a policy to a host is then a new wiring line rather than a new template
parameter threaded through every signature that mentions the host. The
[dependency injection](dependency-injection.md) comparison develops this centralization from the
container side; here it is the answer to the parameter-list growth that policy-heavy C++ is known for,
and the higher-order form remains available for the policy a provider must pin locally.

### What CGP does not do

Two things the C++ idioms offer have no CGP counterpart, and one thing they share deserves a plain
statement. Policies compose *structurally*: any class with the right members is a policy, and a host can
take a policy written by someone who never saw the host's interface. CGP providers must implement a
declared provider trait, so a provider is written against a component that already exists, and an
existing type cannot be dropped in as a policy without an impl. Templates also express computations CGP
cannot: a policy may contribute *data members* and *types* by inheritance, and template metaprogramming
can compute over values, where CGP's type-level machinery is limited to types and its abstract types to
associated types a context selects. And both systems monomorphize, so neither offers a heterogeneous
collection of hosts with different policies; C++ falls back to virtual functions and CGP to Rust's
`dyn Trait` for that, as the [dynamic dispatch](dynamic-dispatch.md) comparison describes.

## What users like and dislike

Policy-based design is valued for exactly the property CGP shares with it: composition with no runtime
cost. Users cite the ability to support many behavior combinations from a few small classes, the
inlining the compiler performs once policies are fixed, and the separation of orthogonal concerns into
units that can be tested and reused independently ([Wikipedia, *Modern C++ Design*](https://en.wikipedia.org/wiki/Modern_C%2B%2B_Design)).
CRTP is valued for static polymorphism without virtual calls and for mixins that add behavior to a class
without a runtime hierarchy. Concepts are valued for turning a page of substitution-failure output into
one line naming the unsatisfied requirement, and for documenting a template's intent in code.

The complaints are the familiar costs of C++ templates. The policy interface is implicit and must be
documented by hand, so a wrong policy fails deep inside the host with an error about substituted types
rather than about the requirement ([Wikipedia, *Policy-based design*](https://en.wikipedia.org/wiki/Policy-based_design)).
Long parameter lists spread through every signature that names a policy-heavy host. Every combination of
policies is a distinct type, so code generic over the host must itself be a template, and heterogeneous
collections need a separate virtual interface. CRTP adds its own hazards: the derived class passed to
the wrong base, the base constructed on its own, and a base that cannot see members of a derived class
that is still incomplete ([Wikipedia, *Curiously recurring template pattern*](https://en.wikipedia.org/wiki/Curiously_recurring_template_pattern)).
Concepts improve diagnostics but leave template bodies checked only at instantiation, so a host can
compile against one policy and fail against the next ([cppreference, *Constraints and concepts*](https://en.cppreference.com/w/cpp/language/constraints)).
Compile times grow with the number of instantiations, which is the same cost CGP's monomorphized wiring
carries.

## How CGP compares

CGP and policy-based design agree on the fundamentals and differ on what is declared and when it is
checked. Both compose a type's behavior from interchangeable parts chosen at compile time. Both
monomorphize the result to direct calls. Both give up runtime selection and heterogeneous collections.
On *interface*, C++ policies are structural and implicit where CGP components are declared traits, so
CGP demands an impl for every provider and in exchange has a named contract the compiler enforces and a
place, the component, to document it. On *checking*, C++ checks a host body at instantiation, with
concepts improving the message but not the timing, where CGP checks a provider body at its definition
against its `#[uses]` bounds and checks a context's completeness at its wiring with
`check_components!`. On *composition*, C++ carries the policy choices in the host's type and repeats
them wherever the host is named. CGP can do the same through a higher-order provider, and it adds the
option of gathering the choices into one wiring table on a context named once, with the
higher-order form kept for a policy a provider must pin locally.

The costs on CGP's side are real. A provider needs a component to implement, so CGP cannot accept an
arbitrary existing type as a policy the way a template accepts any class with the right members. Its
type-level programming is narrower than template metaprogramming, and its policies cannot contribute
data members to the host by inheritance. Its raw diagnostics are trait-solver output over generated
types, which a C++ programmer will recognize as the same species as a template error. `cargo cgp check`
leads with the root cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not
yet reshape every class. And the wiring table is more ceremony than a template argument list for a host
with one or two policies. Where a class has a few orthogonal policies and its users name the
instantiation in one place, a policy-based template is the smaller tool. Where the number of choices
grows, where generic code over the host should not repeat them, where the interface a policy must meet
should be checked rather than documented, or where the same operation needs overlapping implementations
that a single set of template parameters cannot express, CGP's declared components and wired contexts
are the better fit, and they come with the definition-time checking C++ templates have never had.

## Presenting CGP to someone who knows this

A C++ programmer who has used policy-based design already holds CGP's structure, so map the vocabulary
and then name the two improvements. A **provider is a policy class**, a **component is the policy
interface written down**, a **context is the host class**, a **higher-order provider is a host class
template with its policies as type parameters**, the **wiring table is the template argument list**,
`#[cgp_impl]` **is CRTP with the cast done for you**, and `check_components!` **is the concept check
that also verifies the body**. Show `HelloWorld<WriteToStdout, GermanMessage>` written as a
higher-order provider early, because it is the one CGP construct this reader will recognize without any
translation. Framed this way, CGP is the compile-time composition they trust
from templates, with the same zero-cost result, and two things they have wanted from templates for
twenty years: an explicit interface for each policy, and errors at the definition rather than the
instantiation.

Lead with the diagnostics, because this reader has paid for the alternative. Show a wrong policy in C++
failing inside the host body and the same mistake in CGP failing at `#[uses]` or at
`check_components!` with the missing trait named. Then state the trade honestly: CGP asks for an impl
per provider where a template accepts any class with the right members, and its wiring is a table rather
than an argument list. A C++ reader who has maintained a policy-heavy library will hear the table as
relief from repeated parameter lists rather than as ceremony, so say that too.

Correct two expectations. This reader may expect to drop an existing class in as a policy with no
declaration, and CGP requires a provider impl for a component. And this reader may expect template-style
value computation or data-member contribution from a policy, and CGP's type level is types and
associated types only. Say plainly that CGP is composition of behavior and of abstract types, not a
metaprogramming language, and point the reader who wants a heterogeneous collection to `dyn Trait`, the
same move they would make from templates to virtual functions.

Avoid presenting CGP as "templates done right". Templates are a more general mechanism, and this reader
knows it. Present CGP as policy-based design with declared interfaces, definition-time checking, and a
centralized wiring table, on a language whose trait system already does the checking templates leave to
instantiation. That is a claim a C++ programmer can verify in an afternoon, and it is the one that holds.

## Sources

The public version of this document is the website's
[policy-based-design comparison page](https://contextgeneric.dev/docs/comparisons/policy-based-design), ported per the
[comparison page guide](../website/writing-guides/related-work.md); a change here updates that page
in the same change.

The account of the related work draws on the standard references for the three C++ idioms and their
documented costs. The C++ snippets are the reference examples from Wikipedia and cppreference, compiled
with GCC 15.3 in C++23 mode; the CGP greeting examples, in both the context-wired and the higher-order
form, were compiled and run against the current `cgp` source at `0.8.0-alpha`, and the `GreetHello`
provider is the
[Hello World tutorial](../website/tutorials/hello-world.md)'s example in `#[cgp_impl]` form.

- [Wikipedia — *Modern C++ Design*](https://en.wikipedia.org/wiki/Modern_C%2B%2B_Design) — Alexandrescu's book, the policy and host-class vocabulary, the `SmartPtr` motivation, and the exponential-combinations argument.
- [Wikipedia — *Policy-based design*](https://en.wikipedia.org/wiki/Policy-based_design) — the `HelloWorld` example, the description of policies as a compile-time strategy pattern, and the statement that the policy interface is implicit and duck-typed.
- [Wikipedia — *Curiously recurring template pattern*](https://en.wikipedia.org/wiki/Curiously_recurring_template_pattern) and [cppreference — *CRTP*](https://en.cppreference.com/w/cpp/language/crtp) — the pattern's definition and origin, the `static_cast` mechanism, static polymorphism, the C++23 deducing-`this` alternative, and the homogeneous-container limitation.
- [cppreference — *Constraints and concepts*](https://en.cppreference.com/w/cpp/language/constraints) — concept and `requires` syntax, satisfaction checked by substitution at instantiation, and the improvement in diagnostics over unconstrained templates.
