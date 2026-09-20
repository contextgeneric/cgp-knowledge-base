# Capabilities: object capabilities, capability-based security, and effects as capabilities

"Capability" names at least five different things in programming, and a reader who asks for
"capabilities in Rust" rarely says which. In the object-capability model a capability is an unforgeable
reference that carries both the designation of a resource and the authority to use it, obtained only by
being handed it, in a system with no ambient authority. In operating systems and hardware the same idea
appears as kernel handles and tagged pointers, while Linux borrows the word for per-thread privilege
bits. In Pony a *reference capability* is an aliasing qualifier. In Effekt and Scala a capability is a
value a computation must hold to perform an effect,
tracked by the type system. And in the Rust community the word most often means an implicit value
such as an allocator or a runtime that a function should receive without a parameter. CGP offers
*capability-like* features in the last two senses: a provider names the traits and values it requires,
the context supplies them, and the compiler checks that every requirement is met. It is not a capability
system in the object-capability sense, because it does not remove ambient authority, its requirements
are not unforgeable tokens, and its provisioning is fixed per context type at compile time.

## Purpose

The comparison exists because the word is doing several jobs at once, and CGP resembles some of them
closely enough to be mistaken for all of them. Rust readers regularly say they would like the language
to offer "capabilities", meaning sometimes a way to pass an allocator or an executor implicitly,
sometimes a filesystem API that cannot escape a directory, sometimes a token type that proves a
peripheral is owned, and sometimes the security model of E or seL4. Those are different properties,
and a design can have one without the others. A reader meeting CGP for the first time sees a provider
that reads a value from its surroundings and a context that supplies it, and reaches for the word. The
resemblance is real for two of the senses and misleading for the rest, and this document exists to say
which is which.

The knowledge base already takes a position on the word. [vocabulary.md](../communication-strategy/vocabulary.md#words-and-framings-to-avoid)
retires "capability" for CGP's own constructs because it names a different thing in the
object-capability model and in Rust's contexts-and-capabilities proposal, and a declared trait bound is
not a sandbox. This document supplies the reasoning behind that rule in full: what each sense requires,
which requirements CGP meets, and a compact way to say "capability-like, but not a capability system"
to a reader who knows one of the senses well. The comparison leans on
[implicit parameters](implicit-parameters.md) for the value-passing side,
[algebraic effects](algebraic-effects.md) for the effects-as-capabilities side, and
[Rust's own proposals](rust-language-proposals.md) for the contexts-and-capabilities proposal.

## The concept in depth

The senses are best separated by the property each one insists on, because the word alone does not
tell them apart. The subsections take the object-capability model first, since it is the sense with a
precise definition and the one every other use borrows from, then the operating-system and hardware
realizations of the same model, then the two senses that share only the word, then effects as
capabilities, and finally the mixture of senses the Rust community uses. A table at the end gathers the
distinguishing properties.

### The object-capability model

A capability, in the sense Jack Dennis and Earl Van Horn introduced in 1966 and Mark Miller's
*Robust Composition* made precise for programming languages, is "a communicable, unforgeable token of
authority" that refers to an object together with the rights to use it
([Wikipedia, *Capability-based security*](https://en.wikipedia.org/wiki/Capability-based_security)).
The object-capability model identifies that token with an ordinary object reference. A capability is
"an unforgeable reference (in the sense of object references or protected pointers) that can be sent in
messages", and to hold the reference is to hold the authority
([Wikipedia, *Object-capability model*](https://en.wikipedia.org/wiki/Object-capability_model)). Miller,
Yee, and Shapiro call this Property A, *no designation without authority*: naming a resource and being
allowed to use it are the same act, so a capability system needs no shared namespace ([Miller, Yee & Shapiro, *Capability Myths Demolished*](https://papers.agoric.com/assets/pdf/papers/capability-myths-demolished.pdf)).

Two further properties define the model. The first is *no ambient authority*, Property D in the same
paper: a subject must select which authority it exercises, so a request either carries a capability or
fails. Unix file permissions are the paper's counterexample, because "the caller of a function such as
`open()` does not choose any credentials to present with the request; the request merely succeeds or
fails". The second is that authority spreads only along existing references. Miller's thesis lists the
four ways an object can come to hold a reference (initial conditions, parenthood when it creates an
object, endowment when its creator hands it one, and introduction when a message delivers one) and
draws the consequence: "only connectivity begets connectivity — all access must derive from previous
access. Two disjoint subgraphs cannot become connected, as no one can introduce them"
([Miller, *Robust Composition*](https://papers.agoric.com/assets/pdf/papers/robust-composition.pdf)).
Reachability in the object graph therefore bounds what any object can do, which is the reasoning the
*principle of least authority* (POLA) rests on: grant each component only the authority it needs.

Three consequences follow, and they are the ones a design must reproduce to deserve the name.
*Delegation* is passing the reference. *Attenuation* is wrapping it: Redell's caretaker pattern, which
Miller presents as the first "access abstraction", forwards messages to a target only while a gate is
enabled, so the holder of the caretaker has less authority than the holder of the target. *Revocation*
is closing that gate, which refutes the "irrevocability myth" the paper names alongside the
"equivalence myth" (that capabilities and access-control lists are formally equivalent) and the
"confinement myth" (that capability systems cannot confine). All three operations are runtime acts on
runtime values. The languages built on the model are E, Joe-E, Caja and its successor Hardened
JavaScript, Pony, Newspeak, Wyvern, Monte, and Austral, and every one of them removes global mutable
state and global I/O functions, because a global is ambient authority. Pony's tutorial states the rule
plainly: global variables are "ambient authority", so Pony has none, and "a capability is an unforgeable
token that (a) designates an object and (b) gives the program the authority to perform a specific set of
actions on that object" ([Pony tutorial, *Object Capabilities*](https://tutorial.ponylang.io/object-capabilities/object-capabilities.html)).
A Pony program obtains file access only from the `env.root` authority its `Main` actor is handed:

```pony
use "files"

actor Main
  new create(env: Env) =>
    // `env.root` is the only source of authority; it is passed in, never global.
    let auth: FileAuth = FileAuth(env.root)
    let path = FilePath(auth, "/var/app/config.txt")
    match OpenFile(path)
    | let file: File => env.out.print(file.read_string(100))
    else env.out.print("could not open")
    end
```

Austral reaches the same discipline through linear types: a `Terminal` or `RootCapability` value must
be passed to any function that performs the corresponding I/O and returned afterwards, so "code that
wants to write to the terminal needs permission to do so" and there is no ambient authority
([Austral specification](https://austral-lang.org/spec/spec.html)).

### Capability-based security in operating systems and hardware

"Capability-based security" in systems work names the same model applied below the language.
KeyKOS, EROS, and seL4 give a process handles to kernel objects and no other way to name them.
Capsicum adds capability mode to FreeBSD file descriptors. Fuchsia's handles and Genode's capabilities
are the same idea. CHERI moves it into hardware: "architectural capabilities, hardware-supported
descriptions of permissions that can be used, in place of integer virtual addresses, to refer to data,
code, and objects in protected ways", with tagged memory protecting the capabilities themselves
([CHERI project](https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/)). WASI is the design a Rust
reader is likeliest to meet. It "has no ambient authorities, meaning that there are no global namespaces
at runtime, and no global functions at link time", and its handles "are unforgeable, meaning there's no
way for an instance to acquire access to a handle other than to have another instance explicitly pass
one to it" ([WASI design principles](https://github.com/WebAssembly/WASI/blob/main/docs/DesignPrinciples.md)).

Rust's `cap-std` crate brings that discipline to the standard library's surface. Its APIs "don't access
files, directories, network addresses, clocks, or other external resources implicitly, but instead
operate on handles that are explicitly passed in", so a file is opened through a `Dir` handle rather than
by an absolute path, and a path that would escape the directory fails. The one place ambient authority
is exercised is marked by an explicit `ambient_authority()` argument, and the crate is candid that it is
"just a library", so "it can't prevent arbitrary Rust code from using `std::fs`'s path-oriented APIs"
([Gohman, *Introducing cap-std*](https://blog.sunfishcode.online/introducing-cap-std/);
[cap-std README](https://github.com/bytecodealliance/cap-std)). Compiled with `cap-std` 3:

```rust
use cap_std::ambient_authority;
use cap_std::fs::Dir;

fn read_config(dir: &Dir) -> std::io::Result<String> {
    // `dir` is the only authority this function holds; it cannot reach outside it.
    let mut text = String::new();
    std::io::Read::read_to_string(&mut dir.open("config.txt")?, &mut text)?;
    Ok(text)
}

// Ambient authority is exercised once, and the call marks it.
let dir = Dir::open_ambient_dir("/var/app", ambient_authority())?;
read_config(&dir)?;
dir.open("../secret.txt")   // Err(PermissionDenied: a path led outside of the filesystem)
```

### Two senses that share only the word

Two well-known uses of "capability" are unrelated to authority in the model's sense, and a reader who
brings either will be confused by a comparison built on the first. Linux "capabilities" divide "the
privileges traditionally associated with superuser into distinct units, known as capabilities, which can
be independently enabled and disabled", such as `CAP_NET_BIND_SERVICE` and `CAP_CHOWN`, held as a
per-thread attribute ([capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)).
They are privilege bits, not references to resources. Miller, Yee, and Shapiro note that the mechanism
"bears a weak resemblance to capability models" but lacks dynamic resource creation, and Wikipedia lists
it among uses "inconsistent with the model".

Pony's *reference capabilities* are the other case. The six qualifiers `iso`, `trn`, `ref`, `val`, `box`,
and `tag` describe what a reference permits its holder to do with the memory it points at (isolated,
transitional, mutable, immutable, read-only, identity-only), and their purpose is that "the type system
ensures at compile time that your concurrent program can never have data races"
([Pony tutorial, *Reference Capabilities*](https://tutorial.ponylang.io/reference-capabilities/)). The
tutorial itself separates the two senses: object capabilities grant "the ability to do things with
objects" such as files and sockets, while reference capabilities *deny* aliasing and mutation. A Rust
reader already has this second thing under the names ownership, `&`, and `&mut`. It is not what CGP is
about, and it is not what a Rust reader asking for capabilities is asking for.

### Effects as capabilities

The third live sense comes from effect systems, and it is the one CGP most resembles. Effekt's
designers describe their language as "effects as capabilities": "effect types express which
capabilities a computation requires from its context", and the semantics is given "as a translation to
System Ξ, a calculus in explicit capability-passing style" ([Brachthäuser, Schuster & Ostermann,
*Effects as Capabilities* (OOPSLA 2020)](https://dl.acm.org/doi/10.1145/3428194)). Here a capability
is a value that a handler introduces and that must be in scope for an operation to be performed. The
type of a function records which capabilities it needs from its caller, so an effect type is a list of
requirements on the context rather than a list of side effects that might happen. To keep this sound
Effekt treats capabilities, and functions that close over them, as *second-class*: they can be passed
down but not returned or stored, so a capability cannot outlive the handler that introduced it.

Scala's research line reaches the same place from the other direction. *Scoped Capabilities for
Polymorphic Effects* shows that tracking the free variables a value captures is enough "to safely
implement effects and effect polymorphism via scoped capabilities"
([Odersky, Boruch-Gruszecki, Lee, Brachthäuser & Lhoták](https://arxiv.org/abs/2207.03402)), and
Scala 3's experimental *capture checking* implements it: "a capability is syntactically a method- or
class-parameter, a local variable, or the `this` of an enclosing class", whose type carries a capture
set marked `^`, and the checker prevents such a value from escaping the scope that introduced it
([Scala 3 Reference, *Capture Checking*](https://docs.scala-lang.org/scala3/reference/experimental/cc.html)).
The concrete application is `CanThrow`, an *erased* class: a `throw` requires a `CanThrow[E]`
capability, a `try` creates one as an erased given in its body, and `U throws E` abbreviates
`CanThrow[E] ?=> U`, a context parameter ([Scala 3 Reference, *CanThrow Capabilities*](https://docs.scala-lang.org/scala3/reference/experimental/canthrow.html)).
Compiled with Scala 3.8.4:

```scala
import language.experimental.saferExceptions

class LimitExceeded extends Exception
val limit = 10e9

def f(x: Double): Double throws LimitExceeded =
  if x < limit then x * x else throw LimitExceeded()

try println(List(1.0, 2.0, 3.0).map(f).sum)   // the try supplies the CanThrow capability
catch case ex: LimitExceeded => println("too large")
```

This sense keeps one thing from the object-capability model: authority to perform an operation is a
value the context supplies rather than something available everywhere. It drops the runtime half. A
`CanThrow` is erased, a Scala capability is checked by a static capture set, and delegation is lexical
scoping rather than message passing. It is a *static* discipline, and that is why it is the sense
CGP can be compared with honestly.

### The Rust community's word

Rust programmers use the word in a mixture of these senses, usually without saying which, and three
threads are worth separating because they ask for different things. The first is *implicit values*.
Tyler Mandry's contexts-and-capabilities proposal declares a `capability` such as an arena and lets a
function or impl require it in a `with` clause, supplied by a `with` block at the call site, so an
allocator, executor, or logger need not be threaded through every signature
([Mandry, *Contexts and capabilities in Rust*](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/)).
Yoshua Wuyts describes the motivating pain: "the global allocator acts, in a capability-sense, as an
ambient authority", because "every function in Rust has access to the global allocator without functions
needing to take allocators explicitly as arguments", and passing one down by hand "doesn't exactly seem
ideal" ([Wuyts, *Nesting Allocators*](https://blog.yoshuawuyts.com/nesting-allocators)). Emulations of
the proposal in today's Rust thread a generic context parameter through every call and read each
"capability" off it through a trait ([haibane_tenshi, *Futuristic Rust: context emulation*](https://haibane-tenshi.github.io/rust-contexts/)).
This thread is about ergonomics and explicitness, not confinement, and its "capability" is an implicit
parameter in the sense the [implicit parameters](implicit-parameters.md) comparison covers.

The second thread is *sandboxing*, which is the object-capability sense proper: `cap-std`, WASI, and the
Wasmtime runtime built on them, where the point is that code holding a `Dir` cannot reach outside it.
The third is *ownership tokens*. The embedded Rust book makes each peripheral a value obtained once
through `take()`, so that "to call the `read_speed()` method, we must have ownership or a reference to a
`SerialPort` structure", and the borrow checker guarantees "at no point do we have multiple mutable
references to the same hardware" ([Embedded Rust Book, *Peripherals as singletons*](https://docs.rust-embedded.org/book/peripherals/singletons.html)).
PermRust generalizes the idea into "a token-based permission system for Rust", "a zero cost abstraction
on top of the type system" that manages access to system resources per library
([Gehring, Rehms & Tschorsch, *PermRust*](https://arxiv.org/abs/2506.11701)). A token is a static capability: a
value whose type proves authority and whose ownership prevents forgery, checked at compile time. A reader
who says "I want capabilities in Rust" may mean any of the three, and the properties they get from each
differ.

### The properties that tell the senses apart

Six properties separate the senses, and a design can be placed by asking which it has:

| Property | Object capabilities (E, Pony, seL4, WASI, cap-std) | Effects as capabilities (Effekt, Scala) | Rust contexts proposal | Ownership tokens |
|---|---|---|---|---|
| Designation and authority are one reference | yes | partly: the value is the permission, the resource may be elsewhere | no: a named implicit value | yes for the resource the token stands for |
| No ambient authority, enforced | yes, by removing globals | no, unless the language also removes them | no: ambient values are named, not removed | no |
| Unforgeable | yes, by memory safety and no pointer arithmetic | yes, by private constructors or erasure | not addressed | yes, by a private constructor |
| Provisioned at runtime | yes: introduction, parenthood, endowment | value at runtime, scope lexical; `CanThrow` erased | value at runtime, binding lexical | value at runtime |
| Delegation, attenuation, revocation | all three, at runtime (caretaker) | delegation by passing; attenuation by wrapping; no revocation | delegation by scope; nested `with` blocks shadow | delegation by move or borrow |
| Confinement reasoning | reachability in the object graph | capture sets bound escape | not addressed | ownership bounds aliasing |

## How CGP expresses it

CGP shares the effects-as-capabilities reading almost exactly and the object-capability reading only in
part, and the two need separating with the same care as the senses above. A provider's
[impl-side dependencies](../cgp/concepts/impl-side-dependencies.md) are the requirements a computation
places on its context; the context supplies them; and
[`check_components!`](../cgp/reference/macros/check_components.md) verifies that every requirement is
met. That is Effekt's "which capabilities a computation requires from its context", made into trait
bounds. CGP does not remove ambient authority, does not make its requirements unforgeable, and does not
provision them at runtime. The subsections take the resemblance first and then the three properties CGP
lacks.

### A requirement on the context is a capability in the effect-system sense

A CGP provider declares what it needs with [`#[uses]`](../cgp/reference/attributes/uses.md) for traits
and [`#[implicit]`](../cgp/reference/attributes/implicit.md) for values, and the consumer trait a caller
invokes hides both. The greeter from the [Hello World tutorial](../website/tutorials/hello-world.md)
is the smallest case:

```rust
#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self, #[implicit] name: &str) -> String {
        format!("Hello, {name}!")
    }
}

#[derive(HasField)]
pub struct App {
    pub name: String,
}

delegate_components! {
    App {
        GreeterComponent: GreetHello,
    }
}

check_components! { App { GreeterComponent } }
```

Read as an effect type, `GreetHello` requires one thing of its context, a `name` field, and `App`
supplies it. Constructing `App { name }` is the `try` that supplies a `CanThrow`, or the `with` block
that supplies Mandry's arena. The parallel holds at the type level: an
[abstract type](../cgp/concepts/abstract-types.md) such as a context's `Error` is a requirement the
context discharges by wiring, which no capability system expresses, and the
[algebraic effects](algebraic-effects.md) comparison develops that extension. The `App` here is an
**environmental context**, a type standing for the application, and `GreetHello` is self-targeted.

### An object capability can live in the context

Where the value a provider requires is itself an object capability, CGP carries it without ceremony and
adds a static check that it reaches the code that needs it. A `cap-std` `Dir` handle stored as a context
field is an object capability in the model's sense, and a provider that reads configuration through it
holds no other filesystem authority in its body. This compiles against `cgp` `0.8.0-alpha` and
`cap-std` 3:

```rust
use cap_std::fs::Dir;

#[cgp_component(ConfigReader)]
pub trait CanReadConfig {
    fn read_config(&self) -> std::io::Result<String>;
}

#[cgp_impl(new ReadConfigFromDir)]
impl ConfigReader {
    fn read_config(&self, #[implicit] config_dir: &Dir) -> std::io::Result<String> {
        let mut text = String::new();
        std::io::Read::read_to_string(&mut config_dir.open("config.txt")?, &mut text)?;
        Ok(text)
    }
}

#[derive(HasField)]
pub struct App {
    pub config_dir: Dir,
}

delegate_components! {
    App {
        ConfigReaderComponent: ReadConfigFromDir,
    }
}

check_components! { App { ConfigReaderComponent } }
```

The division of labor is the point. `cap-std` supplies the unforgeable handle and the runtime
confinement; CGP supplies the declaration that `ReadConfigFromDir` needs a `Dir` and the compile-time
check that `App` has one. This is the arrangement CGP's author uses for an arena-allocating
deserializer, where the arena is a context field and the provider reads it as an implicit argument,
which the [Rust proposals](rust-language-proposals.md) comparison relates to Mandry's example.

### CGP does not remove ambient authority

The property that makes a language capability-safe is that code can reach only what it is handed, and
Rust does not have it. `ReadConfigFromDir` could call `std::fs::File::open("/etc/passwd")` in its body
and CGP would neither notice nor object. The provider's declared requirements bound what it reaches
*through the context*, which is useful for reading and for testing, but they do not bound what it
reaches through `std`, through statics, or through the global allocator that Wuyts identifies as the
ambient authority every Rust function holds. A capability-safe language forbids the global; CGP is a
library in a language that permits it. The reachability argument that lets an E programmer bound a
component's authority by the references it holds does not transfer, and a piece that suggests a CGP
provider is confined to its declared dependencies is claiming something Rust cannot deliver.

### A requirement is not an unforgeable token

An object capability is unforgeable because the only way to obtain the reference is to be given it. A
CGP requirement is a trait bound on the context, and any context that carries a field of the right name
and type satisfies a `HasField<Symbol!("config_dir")>` bound. The bound says what the provider needs; it
does not certify who may construct the context. Authority, where there is any, lives in the *value*
stored in the field. A `Dir` is unforgeable because `cap-std` made it so; a `String` named `name` is
not a capability at all. The same holds for trait dependencies: `#[uses(CanSendEmail)]` states that the
context must be able to send email, and a context satisfies it by wiring any provider, which is
selection, not permission. Rust can express unforgeable tokens as types with private constructors, and
CGP can carry such a token as a field or fix one as an [abstract type](../cgp/concepts/abstract-types.md),
but the token pattern is Rust's, not CGP's.

### Provisioning is fixed per context type

In the object-capability model authority is provisioned at runtime: an object is introduced to another by
a message, a caretaker attenuates a reference, a gate revokes it, and the graph changes while the program
runs. In CGP the set of requirements a context satisfies, and the providers it satisfies them with, are
part of the context *type*, fixed when `delegate_components!` is written and resolved by the compiler.
Only the field *values* are dynamic: two `App` values may carry two different `Dir` handles, and a
test may carry a `Dir` opened on a temporary directory. That is provisioning of values, not of
authority structure. Delegation in CGP means constructing another context value, or defining another
context type. Attenuation means a [higher-order provider](../cgp/concepts/higher-order-providers.md)
that wraps an inner one, decided statically. Revocation has no counterpart. And bindings are flat: there
is no nested scope in which a provider could be shadowed, which the
[Rust proposals](rust-language-proposals.md) comparison records as the single-context model's chief
limit against Mandry's nested `with` blocks. Where a Scala capability is checked against a lexical
scope by capture sets, a CGP requirement is checked against a context type by trait resolution, and
nothing prevents a context field from being cloned out and used elsewhere.

### The two senses CGP has nothing to do with

Pony's reference capabilities and Linux's capability bits do not enter the comparison at all. Aliasing
and mutation control in CGP is Rust's ownership, unchanged: a provider receives `&self`, and the
[Rust proposals](rust-language-proposals.md) comparison records that a context cannot supply `&mut` or
owned values without interior mutability. Privilege bits are an operating-system concern that CGP does
not touch. A reader who arrives with either sense should be told so in one sentence and pointed at the
other three.

## What users like and dislike

Object capabilities are admired for what their reasoning buys. Least authority is a property of the
object graph rather than a policy someone must maintain, so a compromised component does only the damage
its references allow. Confused-deputy attacks, where a program is tricked into using its own authority
on an attacker's behalf, are structurally impossible when designation and authority travel together,
which the *Capability Myths Demolished* paper spends a section on. Delegation and attenuation are
ordinary programming (pass a reference, wrap it), and the model's authors point out that it is the only
protection model whose semantics can be stated in programming-language terms, roughly lambda calculus
with local side effects ([Miller, *Robust Composition*](https://papers.agoric.com/assets/pdf/papers/robust-composition.pdf)).
The effects-as-capabilities line is praised for making effect polymorphism lightweight: a higher-order
function need not mention the effects of the block it receives, because the block carries its own
capabilities ([Brachthäuser, Schuster & Ostermann 2020](https://dl.acm.org/doi/10.1145/3428194)).

The dislikes are the costs of removing what everyone is used to. Ambient authority is convenient, and a
capability-safe design asks every function to receive what it uses; Wuyts's complaint that passing an
allocator by hand "doesn't exactly seem ideal" is the whole Rust contexts discussion in one sentence,
and Mandry's proposal exists to restore the convenience without the ambient global. Retrofitting is the
second cost. `cap-std` cannot sandbox code that still has `std::fs`, WASI needed a new system interface
rather than a POSIX layer, and Pony and Austral removed globals from the language, which no established
ecosystem can do after the fact. The effect-system designs pay in restrictions and maturity: Effekt's
second-class capabilities cannot be returned or stored, and Scala's capture checking is, by its own
documentation, "still highly experimental and unstable". And the word itself is a cost. The three myths
Miller, Yee, and Shapiro set out to demolish persist because capabilities are conflated with
access-matrix rows, with POSIX privilege bits, and with keys anyone may copy, and a Rust reader who has
met the word in the contexts proposal, in `cap-std`, and in the embedded book has met three different
properties under one name.

## How CGP compares

CGP offers capability-like features, and the honest way to say so is to name the sense. In the
effects-as-capabilities sense CGP is close: a provider's impl-side dependencies are the requirements a
computation places on its context, the context supplies them, `check_components!` verifies that every
one is met, and the consumer trait hides them from callers, which is the contextual effect
polymorphism Effekt advertises. In the implicit-value sense of the Rust contexts proposal, CGP delivers
the ergonomics today: an implicit argument reads an allocator, a runtime, or a logger from the context
without a parameter at every call, at the cost of declaring one flat context type per configuration. In
the object-capability sense CGP is a host, not a system: it can carry an unforgeable handle as a context
field and check statically that the handle reaches the provider that needs it, but it does not remove
ambient authority, its bounds are requirements rather than tokens, and its authority structure is fixed
per context type at compile time with no runtime delegation, attenuation, or revocation.

The costs on CGP's side follow. A reader who wants confinement gets none from CGP alone and must bring
`cap-std`, WASI, or a token type of their own. A reader who wants nested scopes that shadow a binding,
as Mandry's `with` blocks and effect handlers do, gets a single flat context. A reader who wants a
capability that can be returned, stored, and revoked gets a field value with none of those semantics
attached. And a reader who wants Pony's aliasing control or Linux's privilege bits is in the wrong
document. Where a program needs a capability-safe language, Pony, Austral, or Hardened JavaScript is the
tool, and where it needs sandboxed I/O in Rust, `cap-std` and WASI are. Where a program wants its
implementations to state what they require and a compiler to check that each context supplies it, on
stable Rust and with the choice of implementation made per application, CGP delivers that, and it
combines with the object-capability libraries rather than competing with them.

## Presenting CGP to someone who knows this

Start by asking which sense the reader means, and answer that sense. The one-line framing that survives
every reader is: **CGP is capability-like in that a provider declares what it requires and the context
supplies it, checked at compile time; it is not a capability system, because it does not remove ambient
authority, its requirements are not unforgeable tokens, and its provisioning is fixed per context type.**
Follow it with the property table above rather than with a longer argument, because a reader who knows
one sense will locate CGP on the table faster than in prose.

For the reader who knows the object-capability model, concede first. Say that Rust has ambient authority
and CGP cannot take it away, that a CGP bound is a requirement rather than a token, and that the object
graph does not change at runtime. Then offer the true claim: CGP is a good host for object capabilities,
because a `Dir` or an arena stored in a context is carried to exactly the providers that declare they
need it, with the delivery checked by the compiler, and the `cgp-serde` arena example and the `cap-std`
snippet above show it. This reader will respect the concession more than any claim, and will recognize
the discipline of naming requirements even where enforcement is absent.

For the reader who knows Effekt or Scala's capture checking, lead with the resemblance: an impl-side
dependency is a capability requirement, a context is the handler that supplies it, and a consumer trait
is effect-polymorphic in the contextual sense. Then name the two things missing: there is no escape
check (a context field can be cloned out), and there is no scoping (bindings are flat). This reader
will also see at once that CGP's [abstract types](../cgp/concepts/abstract-types.md) are a requirement
kind their systems lack.

For the Rust reader who "wants capabilities", the work is to find out which of three things they want.
If it is implicit passing of an allocator or a runtime, CGP's implicit arguments do that now, and the
[Rust proposals](rust-language-proposals.md) comparison states what the contexts proposal would add. If
it is sandboxing, point at `cap-std` and WASI and show that CGP carries their handles. If it is ownership
tokens, they already have them, and CGP can fix one as an abstract type. Never say that CGP "gives Rust
capabilities" without the qualifier, because the reader will hear the sense they came with, and for two
of the three it is false.

Finally, hold the vocabulary line in CGP's own prose. A component defines a *trait*, a provider
*requires* traits and *reads* fields, `#[uses]` imports a *trait dependency*, and a context *supplies*
what providers need. Calling any of these a capability invites the object-capability reading, which CGP
cannot honor, and the [vocabulary](../communication-strategy/vocabulary.md#words-and-framings-to-avoid)
rule against it stands.

## Sources

The account of the related work draws on the primary literature of the object-capability model, the
documentation of the systems and languages that implement it, the effects-as-capabilities papers and
the Scala reference, and the Rust community's own writing. The `cap-std` snippets were compiled with
`cap-std` 3.x and the CGP snippet against the local `cgp` source at `0.8.0-alpha`; the Scala snippet was
compiled with Scala 3.8.4. The Pony snippet is not compiled, because the Nix `ponyc` package builds
its own LLVM; its calls were checked against the standard library's signatures for `FileAuth`,
`FilePath`, and `OpenFile`.

- [Dennis & Van Horn, *Programming Semantics for Multiprogrammed Computations* (CACM 1966)](https://dl.acm.org/doi/10.1145/365230.365252) — the origin of the capability and the capability list.
- [Miller, *Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control* (PhD thesis, 2006)](https://papers.agoric.com/assets/pdf/papers/robust-composition.pdf) — the object-capability model, the four ways a reference is obtained, "only connectivity begets connectivity", the principle of least authority, and Redell's caretaker pattern for revocation.
- [Miller, Yee & Shapiro, *Capability Myths Demolished* (2003)](https://papers.agoric.com/assets/pdf/papers/capability-myths-demolished.pdf) — the seven properties, among them *no designation without authority* and *no ambient authority*, the equivalence, confinement, and irrevocability myths, and the remark that POSIX capabilities lack dynamic resource creation.
- [Wikipedia, *Object-capability model*](https://en.wikipedia.org/wiki/Object-capability_model) and [*Capability-based security*](https://en.wikipedia.org/wiki/Capability-based_security) — the definitions, the languages and systems that implement the model, and the note that some uses of the word are inconsistent with it.
- [Pony tutorial, *Object Capabilities*](https://tutorial.ponylang.io/object-capabilities/object-capabilities.html) and [*Reference Capabilities*](https://tutorial.ponylang.io/reference-capabilities/) — the unforgeable-token definition, `env.root` and the absence of globals, and the six aliasing qualifiers that share the word.
- [Austral specification](https://austral-lang.org/spec/spec.html) — linear capability values and the removal of ambient authority.
- [CHERI](https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/) and [WASI design principles](https://github.com/WebAssembly/WASI/blob/main/docs/DesignPrinciples.md) — architectural capabilities, and WASI's unforgeable handles and absence of ambient authority.
- [Gohman, *Introducing cap-std*](https://blog.sunfishcode.online/introducing-cap-std/) and the [cap-std README](https://github.com/bytecodealliance/cap-std) — capability-oriented APIs, the `ambient_authority()` marker, `Dir` handles, and the limit that a library cannot sandbox arbitrary Rust code.
- [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html) — Linux capabilities as per-thread privilege units.
- [Brachthäuser, Schuster & Ostermann, *Effects as Capabilities: Effect Handlers and Lightweight Effect Polymorphism* (OOPSLA 2020)](https://dl.acm.org/doi/10.1145/3428194) — effect types as the capabilities a computation requires from its context, capability-passing style, and second-class capabilities.
- [Odersky, Boruch-Gruszecki, Lee, Brachthäuser & Lhoták, *Scoped Capabilities for Polymorphic Effects* (2022)](https://arxiv.org/abs/2207.03402), [Scala 3 Reference, *Capture Checking*](https://docs.scala-lang.org/scala3/reference/experimental/cc.html), and [*CanThrow Capabilities*](https://docs.scala-lang.org/scala3/reference/experimental/canthrow.html) — capabilities as tracked values with capture sets, the erased `CanThrow` capability, and the experimental status.
- [Mandry, *Contexts and capabilities in Rust*](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/), [Wuyts, *Nesting Allocators*](https://blog.yoshuawuyts.com/nesting-allocators), and [haibane_tenshi, *Futuristic Rust: context emulation*](https://haibane-tenshi.github.io/rust-contexts/) — the Rust community's implicit-value sense, the global allocator as ambient authority, and today's emulations.
- [Embedded Rust Book, *Peripherals as singletons*](https://docs.rust-embedded.org/book/peripherals/singletons.html) and [Gehring, Rehms & Tschorsch, *PermRust: A Token-based Permission System for Rust*](https://arxiv.org/abs/2506.11701) — ownership tokens as static capabilities.
