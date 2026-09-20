# C++ policy-based design, CRTP, and concepts

C++ policy-based design composes host behavior from policy types, making it a close comparison for CGP providers, higher-order providers, and context wiring.

## Purpose

Policy-based design lets a class vary independent parts of its behavior without a runtime virtual
interface or a hand-written class for every combination. A host template chooses policy types for
operations such as ownership, checking, or output. CRTP supplies a related way for reusable behavior
to access the host, and concepts can express the requirements on template arguments.

CGP offers comparable static selection in Rust. The useful differences are declared provider
traits, generic-body checking under bounds, and dependencies obtained through a shared context.
Those differences should be explained without implying that C++ lacks named constraints, aliases,
default policies, or host-aware composition.

## The concept in depth

Policy-based design lets a host class vary independent aspects of its behavior through template
arguments. A smart pointer might parameterize ownership and checking, while a greeting program
might parameterize its message and output destination. The resulting types fix those choices at
compile time, avoiding virtual dispatch for the policy calls.

### Policies and the host class

A host composes its policies by inheriting from them or holding their values. This greeting example
uses an output policy and a language policy:

```cpp
template <typename OutputPolicy, typename LanguagePolicy>
class HelloWorld : private OutputPolicy, private LanguagePolicy {
public:
    void run() const {
        this->write(this->message());
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

The English and German instantiations are distinct types with different message implementations.
The `this->` qualifiers make the member lookups depend on the template instantiation, where the
compiler can find the inherited policy members. The calls can be inlined, but choosing policies
statically does not itself guarantee inlining.

### Policy interfaces can be implicit or constrained

An unconstrained host expresses its requirements through the operations its body uses. In the
example, the policies must supply compatible `message` and `write` members. A class can satisfy
those requirements without declaring that it implements a particular interface.

C++20 concepts can give those requirements explicit names. Policy-based design therefore does not
require an undocumented interface: a host can constrain its policy arguments and report a failed
requirement before its body is instantiated. The distinction from Rust traits concerns both
structural matching and how the generic body is checked.

### CRTP gives a base access to its derived object

CRTP passes the derived class as an argument to its base template. The base can then call a derived
member through a cast to that known type:

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

`Base<D1>` and `Base<D2>` call their respective `impl` methods without virtual dispatch. A policy or
mixin can use the same technique when it needs access to its host. The cast relies on the object
having the expected derived type. C++23's explicit object parameters offer another way to express
some of these member functions, without repeating the CRTP inheritance pattern.

The two base instantiations do not form a shared runtime interface. A heterogeneous collection
needs another representation, such as a virtual interface, type erasure, or a `std::variant` for a
closed set of alternatives. CRTP alone does not choose that representation.

### Concepts state requirements without fully checking a generic body

A concept names a predicate over template arguments. Here, `Hashable` requires a hash expression
whose result is convertible to `std::size_t`:

```cpp
template<typename T>
concept Hashable = requires(T a) {
    { std::hash<T>{}(a) } -> std::convertible_to<std::size_t>;
};

template<Hashable T>
void f(T) {}
```

Constraint satisfaction determines whether a candidate is eligible for particular arguments.
It does not prove that every operation in the template body follows from the stated constraints.
A body can use an additional dependent member that works for one argument and fails for another.
C++ checks nondependent constructs when the template is defined; dependent checks can wait until
instantiation. The [C++ draft's template name-resolution rules](https://eel.is/c++draft/temp.res)
describe that split.

## How CGP expresses it

CGP declares policy interfaces as traits and supplies implementations through provider types.
Applications can select providers through context wiring or pass them explicitly as type
parameters. Rust checks the generic implementation against its declared bounds in either form.

### Providers are policies; the context is the host

The greeting can declare its message and output interfaces separately, then implement each choice
as a provider:

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

`HasMessage` and `CanWrite` are the interfaces that `run` uses. Their generated provider traits,
`MessageProvider` and `Writer`, let named types supply alternative implementations. A provider type
can implement more than one component, and a component can contain more than one operation; the
split here makes the message and output choices independent.

Contexts select those choices in wiring tables:

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

EnglishApp.run();   // Hello, World!
GermanApp.run();    // Hallo Welt!
```

`EnglishApp` and `GermanApp` are fieldless **environmental contexts**. Their role is to choose
behavior; an application with runtime configuration could store it in context fields. Both
compositions use static provider selection, so policy calls need no runtime lookup or vtable.
Whether the optimizer inlines a particular call remains a separate question.

The `#[uses(HasMessage, CanWrite)]` declaration states the generic dependencies of `run`.
`check_components!` then checks that each concrete context supplies the requested components and
their dependencies. This separates checking the reusable body from checking an application's
assembly.

### Policies as type parameters are higher-order providers

A higher-order provider keeps policy choices local to a parameterized implementation. The greeting
can use the familiar `HelloWorld<WriteToStdout, GermanMessage>` shape:

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

App.run();   // Hallo Welt!
```

`W` must implement `Writer` for the context, and `M` must implement `MessageProvider` for it.
The `#[use_provider]` attributes declare those bounds and allow calls such as `W::write(self, ...)`.
Only `RunnerComponent` is wired on `App`; the inner provider choices are explicit arguments to
`HelloWorld`.

A generic CGP function can take providers in the same way. Its provider parameters become parameters
of the generated consumer trait, which the caller can specify explicitly:

```rust
#[cgp_fn]
#[use_provider(W: Writer)]
#[use_provider(M: MessageProvider)]
pub fn hello<W, M>(&self) {
    W::write(self, M::message(self))
}

<App as Hello<WriteToStdout, EnglishMessage>>::hello(&App);   // Hello, World!
```

Explicit parameters suit a provider that must fix an inner choice locally. Context wiring suits
dependencies that several providers should obtain from the application's shared choices. The
[Modularity Hierarchy](../cgp/concepts/modularity-hierarchy.md) explains when the additional control of
a higher-order provider is useful.

A manually declared provider struct can default an inner parameter to
[`UseContext`](../cgp/reference/providers/use_context.md), forwarding that dependency through the
context's wiring. The `new` declarations above do not introduce defaults automatically. This is a
CGP forwarding convention; C++ can also express policies that obtain behavior through their host.

### Providers access the context without an inheritance cast

Inside `#[cgp_impl]`, `self` refers to the context on which the operation runs. The macro rewrites
that source form into a provider implementation with an explicit context parameter. A provider can
request a field through an implicit argument:

```rust
#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self, #[implicit] name: &str) -> String {
        format!("Hello, {name}!")
    }
}
```

`GreetHello` asks its context for `name`; it does not contain a `name` field itself. A `Person` that
stores the field and wires the greeter is a **value context**. The generated field-access bounds
make the requirement explicit to Rust's type checker.

This addresses a need that CRTP often serves: reusable behavior accessing the host's data. The
mechanism is different. CGP passes the context to provider functions, so there is no inheritance
relationship or base-to-derived cast in this correspondence.

### Generic bodies and concrete wiring have separate checks

Rust checks a generic provider body using the bounds available at its definition. For example,
`run` can rely on the `HasMessage` and `CanWrite` bounds declared by `#[uses]`. If it calls an
operation that needs an additional bound, the generic definition must supply that requirement.
This is stronger than merely checking whether particular C++ arguments satisfy a concept whose
requirements may not cover the body's dependent uses.

A valid generic provider may still be unusable with a particular context. The context might lack a
field, another component, or a required relationship between associated types.
[`check_components!`](../cgp/reference/macros/check_components.md) forces that dependency check for the
listed components. A wiring table alone does not validate every possible use, and the resulting
diagnostics can still involve generated traits and Rust's trait solver.

### Wiring gathers choices under a context type

Context wiring lets generic consumers name the interfaces they need without enumerating the
application's provider types. Adding another independently selected component can leave those
consumer signatures unchanged. The choices remain visible together in `delegate_components!`.

C++ aliases and default template arguments already reduce repetition in policy-heavy types.
CGP's distinction is how dependencies are addressed: a provider can ask the shared context for a
component while the application selects its implementation elsewhere. Explicit provider parameters
remain available when that indirection is undesirable. The
[dependency injection](dependency-injection.md) comparison examines this arrangement from the
application's side.

## What users like and dislike

Policy-based design is valued for independently configurable behavior without virtual dispatch.
Alexandrescu's *Modern C++ Design* develops that approach through policy-based library designs;
the [book overview](https://en.wikipedia.org/wiki/Modern_C%2B%2B_Design) summarizes the motivation.
CRTP serves reusable static behavior, while concepts make argument requirements visible in code.

Implicit policy requirements and errors inside instantiated bodies are recurring concerns in
accounts of the technique, including the
[policy-based design overview](https://en.wikipedia.org/wiki/Policy-based_design). Concepts address
part of that problem by naming and checking constraints. They do not establish that those
constraints cover all dependent operations used by a body. The
[C++ draft](https://eel.is/c++draft/temp.res) distinguishes definition-time and instantiation-time
checks; the comparison must preserve both.

Policy-heavy types can become verbose, but aliases and default arguments reduce repetition.
Instantiation work and code size remain possible costs. CRTP also relies on the correct derived
object relationship for its cast; passing the context explicitly gives CGP a different access
mechanism rather than an automatically repaired form of inheritance.

## How CGP compares

C++ policies compose structurally, so existing classes with compatible operations can often be
used directly. Concepts improve the interface declaration and diagnostics, but dependent errors
can still appear during body instantiation. Many policy combinations can increase compilation
work and code size. Aliases and defaults contain long parameter lists without changing the
underlying types.

CGP requires declared provider traits and implementations for them. That gives generic bodies
checked contracts, but adapting an existing type can require an impl or wrapper. Wiring introduces
more declarations than a small set of ordinary Rust generic parameters. Following a dependency may
also require reading several component and provider mappings.

CGP shares the costs of monomorphized generic code, including compilation work and potentially
larger binaries. Its generated types can make trait errors difficult to read;
[`cargo cgp check`](../cargo-cgp/reference/usage.md) explains the error classes it recognizes. These costs
belong alongside the benefits of independently selected implementations.

A C++ host with a few policies and a convenient alias may already provide all the needed
composition. Templates also support inheritance-based contributions to object layout and C++'s
broader template metaprogramming facilities. CGP does not add fields from a provider to a context or
reproduce that language's template system.

Rust still supplies const generics and constant evaluation when CGP is in use. The boundary is
therefore not that CGP programs can compute only with types; it is that CGP's provider wiring is a
particular composition mechanism within Rust. For a small Rust API, ordinary traits and generics
can be the simpler choice.

Runtime selection needs an additional representation in either language. Virtual interfaces or
type erasure in C++, and trait objects in Rust, can support open sets of runtime implementations.
Variants and enums can represent closed sets. The [dynamic dispatch](dynamic-dispatch.md) page
explains how static wiring and runtime polymorphism can coexist.

## Presenting CGP to someone who knows this

Start with the familiar `HelloWorld<WriteToStdout, GermanMessage>` composition, then show the
alternative of wiring independent choices on a context. A provider plays a policy's role, a
component supplies its declared interface, and a context supplies runtime data and application
choices. These are role mappings, not exact equivalences between templates and traits.

Use checking to explain the difference precisely. Concepts can name policy requirements and
reject unsuitable arguments; nondependent template constructs are checked at definition.
Dependent body uses can still require instantiation, and a concept need not describe all of them.
Rust checks a generic provider body against available bounds, while `check_components!` checks
whether a concrete context supplies the transitive requirements. Do not promise uniformly short
diagnostics or imply that wiring alone validates every component.

State the tradeoffs beside the benefits. CGP requires provider trait impls, does not inherit
provider fields into the context, and introduces declarations that a small generic API may not
need. Rust const generics and constant evaluation remain available. C++ aliases, defaults, and
host-aware policies already solve related problems; `UseContext` is a CGP convention, not a
capability impossible to express in C++.

Explain runtime choices separately. Neither static policy selection nor CGP wiring alone provides
a heterogeneous runtime interface, but both can coexist with dynamic dispatch or a closed sum of
alternatives. Static selection removes a dispatch requirement; it does not guarantee inlining or
identical machine code.

## Sources

The C++ snippets are adapted from the reference examples from Wikipedia and cppreference. They were
compiled and run with GCC 15.2.0 in C++23 mode, with standard-library headers and small drivers added
where omitted. The greeting qualifies inherited member calls with `this->` for dependent-base lookup.
The CGP snippets were compiled against `cgp` `0.8.0-alpha` with a `check_components!` assertion per
wired context.

These references support the C++ mechanisms and example origins:

- [C++ working draft, *Name resolution*](https://eel.is/c++draft/temp.res) and [*Constraints and concepts*](https://eel.is/c++draft/temp.constr): dependent lookup, template checking, and constraint satisfaction.
- [Wikipedia, *Modern C++ Design*](https://en.wikipedia.org/wiki/Modern_C%2B%2B_Design): Alexandrescu's book, the policy and host-class vocabulary, and the exponential-combinations argument.
- [Wikipedia, *Policy-based design*](https://en.wikipedia.org/wiki/Policy-based_design): the `HelloWorld` example, policies as a compile-time strategy pattern, and implicit interfaces in unconstrained hosts.
- [Wikipedia, *Curiously recurring template pattern*](https://en.wikipedia.org/wiki/Curiously_recurring_template_pattern) and [cppreference, *CRTP*](https://en.cppreference.com/w/cpp/language/crtp): the pattern's mechanism, static polymorphism, the C++23 deducing-`this` alternative, and the distinct types produced by CRTP instantiations.
- [cppreference, *Constraints and concepts*](https://en.cppreference.com/w/cpp/language/constraints): concept syntax, satisfaction checked at instantiation, and the improvement in diagnostics.


The public [comparison page](https://contextgeneric.dev/docs/comparisons/policy-based-design) follows the
[comparison page guide](../website/writing-guides/related-work.md); factual and example corrections
are kept in sync with this record.
