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
are not unforgeable tokens, and dependency checking does not establish confinement. Wiring is
fixed per context type; authority-bearing field values can vary at runtime.

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
    // File access through `dir` stays within the directory it represents.
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
Wasmtime runtime built on them, where operations through a `Dir` are restricted to the directory it represents.
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

CGP declares what a provider needs from its context and checks that the context supplies it.
Those requirements may include authority-bearing values, but CGP does not make every dependency
an authority token. It also does not restrict access to globals or check the escape of capability
references beyond Rust's ordinary type and lifetime rules.

### Providers declare requirements on a context

A provider uses `#[uses]` for trait dependencies and `#[implicit]` for field dependencies.
This fragment assumes a `CanGreet` component whose method returns a `String`:

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

`GreetHello` needs a `name` field, and `App` supplies it. `check_components!` verifies the field
requirement for the selected provider; constructing `App { name }` supplies its runtime value.
`App` is an environmental context representing an application, and the component is self-targeted.
This is a dependency relationship: the `String` does not confer protected authority.

Contexts can also determine [abstract types](../cgp/concepts/abstract-types.md), such as the error type
shared by their providers. Selecting such a type is separate from supplying an authority-bearing
value of that type. A type choice alone does not grant access to a resource.

### An object capability can live in the context

A context can carry a `cap-std` directory handle to a provider that declares it as a dependency.
This example reads configuration using that handle:

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

`cap-std` constrains file access performed through `config_dir`, while CGP verifies that `App`
supplies the required field. `App` is again an environmental context with a self-targeted component.
The mechanisms compose: the value type supplies resource-access behavior, and CGP supplies the
dependency declaration and static wiring check. An allocator or arena can be passed through a context
field in the same way, as discussed in [Rust's own proposals](rust-language-proposals.md).

### CGP does not remove ambient authority

A provider can access ordinary Rust APIs beyond its context dependencies. `ReadConfigFromDir`
could call `std::fs::File::open(...)` directly if the execution environment allows it, and CGP
would not reject the call. Its declared bounds describe requirements on the context, not a complete
list of effects or authority exercised by the body.

### A trait bound does not create an authority token

A `HasField` bound establishes access to a field of a particular name and type. It does not
establish who may create the field's value. When the field contains a capability, the relevant
construction and access restrictions come from that value's type and execution environment.
Rust types with private constructors can implement controlled tokens; CGP can carry those tokens
without changing their guarantees.

### Wiring is static; capability values can vary at runtime

A concrete context type fixes its provider selections and field types. Its values can still hold
different handles: two `App` instances can refer to different directories, including a temporary
directory used by a test. Their filesystem authority therefore differs even though their wiring
is identical.

Delegation, attenuation, and revocation must come from the capability implementation. A context
can hold a wrapper that limits access or checks whether access has been revoked. A
[higher-order provider](../cgp/concepts/higher-order-providers.md) can also wrap behavior, but wrapping
alone is not proof of attenuation if other access paths remain available. CGP does not add these
security properties or prevent runtime capability values from implementing them.

## What users like and dislike

Object capabilities are admired for what their reasoning buys. Least authority is a property of the
object graph rather than a policy someone must maintain, so a compromised component does only the damage
its references allow. Linking designation to authority helps avoid confused-deputy mistakes, in which code exercises
its own authority on another party's behalf. The guarantee depends on the actual delegation and
resource-access design; *Capability Myths Demolished* explains the distinction. Delegation and attenuation are
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

Object capabilities support reasoning about authority through references, but that reasoning needs
an enforcement boundary. Retrofitting a handle-based API into an unrestricted language does not
remove other APIs that exercise ambient authority. Applications must account for those bypasses
or use an environment that excludes them. The
[cap-std documentation](https://github.com/bytecodealliance/cap-std) makes this library-level limit
explicit.

Effect-capability systems add scope and escape rules that programmers must understand.
Effekt's second-class treatment restricts where capabilities can be stored or returned, while
Scala's capture checking tracks their use through types. These rules support guarantees that a
plain dependency declaration does not provide. The
[Effekt paper](https://dl.acm.org/doi/10.1145/3428194) and
[Scala reference](https://docs.scala-lang.org/scala3/reference/experimental/cc.html) explain the
respective designs.

CGP adds declarations, wiring, and compile-time work without supplying confinement or capture
checking. Programs that need those properties must obtain them elsewhere. Its generated trait
machinery also affects diagnostics: [`cargo cgp check`](../cargo-cgp/reference/usage.md) leads with the root
cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every
class. The [Modularity Hierarchy](../cgp/concepts/modularity-hierarchy.md) compares this machinery
with simpler Rust abstractions.

### Where the other approach fits

Use an enforcing capability system when the requirement is to limit what code may access.
A capability-safe language or sandbox can exclude ambient access paths. Within Rust, `cap-std`
helps express handle-based access, while an appropriate sandbox is needed to constrain code that
could otherwise bypass those handles. Ownership tokens address controlled access to resources
through Rust's construction and borrowing rules.

CGP fits the separate requirement of reusable implementations with declared dependencies and
choices per context. It can carry capability values from those systems, but a wiring check is not
a security audit or proof of confinement.

## Presenting CGP to someone who knows this

Identify which capability property the reader needs before comparing mechanisms. CGP declares
requirements on a context and can carry authority-bearing values; it does not exclude ambient
access or add capture checking. Keep the term capability for those external mechanisms and values,
not for CGP traits, components, or dependency bounds.

Explain the distinction between static wiring and runtime authority. A context's type fixes its
providers, while field values can refer to different resources and implement dynamic delegation,
attenuation, or revocation. These guarantees belong to the value type and enforcement environment.
A dependency check does not establish confinement or prove that a wrapper attenuates authority.

State escape restrictions accurately. Rust ownership, borrowing, lifetimes, and the value's type
still govern whether it can be moved or cloned. CGP adds neither Effekt's second-class restriction
nor Scala's capture tracking. Selecting an abstract type does not itself supply a token value.

## Sources

The public version of this document is the website's
[capabilities comparison page](https://contextgeneric.dev/docs/comparisons/capabilities), ported per the
[comparison page guide](../website/writing-guides/related-work.md); a change here updates that page
in the same change.

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
