# The message: pains, strengths, objections, and limits

Choose a problem the reader recognizes, show the relevant CGP benefit, and state the costs and limits.

Keep these parts together when revising a claim. A changed strength may need a matching change to
its motivating problem, objection, and boundary. [readers.md](readers.md) identifies audiences;
[vocabulary.md](vocabulary.md) governs the terms used to address them.

## Lead with the pain, not the paradigm

Open with the reader's problem before explaining CGP's mechanism. Show a recognizable workaround,
then a small, fair before-and-after. State where the extra abstraction is useful and where a plain
trait would be clearer.

Use the modern idioms taught by the `/cgp` skill and [guides](../cgp/guides/README.md). Providers use
`#[cgp_impl]`, context fields use `#[implicit]`, and wiring uses `delegate_components!` with explicit
checks. Label incomplete examples and say what they omit.

Identify the context and target when showing code. A value context holds the data being operated
on; an environmental context supplies an application's choices and dependencies. A self-targeted
component acts on the context, while a parameter-targeted component acts on a separate type.
Narrate any change between these arrangements, following
[vocabulary.md](vocabulary.md#qualifying-a-context-and-a-target).

## The problems CGP removes

### Give one interface many implementations that Rust rejects outright

Use overlapping implementations to show why separate providers can be useful. Rust rejects these
impls because a type such as `String` satisfies both bounds. This complete example intentionally
fails to compile with `E0119`:

```rust
use core::fmt::Display;

pub trait CanEncode {
    fn encode(&self) -> Vec<u8>;
}

impl<T: Display> CanEncode for T {
    fn encode(&self) -> Vec<u8> {
        self.to_string().into_bytes()
    }
}

impl<T: AsRef<[u8]>> CanEncode for T {
    fn encode(&self) -> Vec<u8> {
        self.as_ref().to_vec()
    }
}

fn main() {}
```

Keep the rejected example on a locally defined trait. Using a foreign trait such as
`serde::Serialize` can introduce an orphan-rule error before the intended overlap demonstration.
Explain each restriction separately.

CGP gives each implementation its own provider type, so the impls do not overlap. This fragment
omits context definitions, wiring, checks, and calls:

```rust
use cgp::prelude::*;
use core::fmt::Display;

#[cgp_component(Encoder)]
pub trait CanEncode<Value> {
    fn encode(&self, value: &Value) -> Vec<u8>;
}

#[cgp_impl(new EncodeWithDisplay)]
impl<Value: Display> Encoder<Value> {
    fn encode(&self, value: &Value) -> Vec<u8> {
        value.to_string().into_bytes()
    }
}

#[cgp_impl(new EncodeBytes)]
impl<Value: AsRef<[u8]>> Encoder<Value> {
    fn encode(&self, value: &Value) -> Vec<u8> {
        value.as_ref().to_vec()
    }
}
```

Explain that the encoded value moved from `Self` into `Value`. The consumer's `Self` now represents
an environmental context, and the component is parameter-targeted. Separate application contexts
can choose different encoders for the same value type. The
[modularity hierarchy](../cgp/concepts/modularity-hierarchy.md) explains this arrangement.

Use this opening for type-system readers and broad introductions. A shorter, self-targeted example
can keep the value in `Self`, as the homepage does, but then a given value type has one consumer
implementation program-wide. In either arrangement, providers add machinery that a single
implementation may not need.

### Implement a trait for a type you don't own — no newtype dance

Explain the orphan-rule benefit through a provider that the implementing crate owns. Ordinary Rust
forbids a foreign trait impl for a foreign type. A CGP provider instead implements a provider trait
on its own marker type, with the foreign target supplied as a parameter. A local context can select
it without wrapping the target value.

Keep the scope of the claim explicit. CGP does not make an arbitrary forbidden `impl ForeignTrait for ForeignType` legal. It offers a different arrangement using provider traits and local choices.
Use this comparison for library authors and experienced Rust developers, supported by
[coherence](../cgp/concepts/coherence.md) and the hand-written patterns in [evidence.md](evidence.md).
A program that needs one globally consistent implementation may be better served by a plain trait.

### Mock in tests, run the real thing in production — without `dyn` or a framework

Show production and test contexts choosing different providers for the same operation. A trait
object, a generic parameter, and CGP wiring are all valid ways to separate an interface from its
implementation. CGP is useful when per-context choices or repeated dependency parameters justify
its additional declarations.

This wiring fragment assumes `CanSendEmail`, its component, the providers, and both context types
are defined elsewhere:

```rust
delegate_components! { App { EmailSenderComponent: SendViaSmtp } }
delegate_components! { TestApp { EmailSenderComponent: RecordEmails } }

check_components! { App { EmailSenderComponent } }
check_components! { TestApp { EmailSenderComponent } }
```

Explain what each provider does and where it gets its state. `SendViaSmtp` uses the application's
SMTP dependencies; `RecordEmails` writes to storage supplied by the test context. Provider marker
types do not hold the recorded messages themselves. Callers use the same consumer method while
wiring selects the implementation.

Introduce `App` and `TestApp` as environmental contexts: types that hold each application's choices
and required data. `CanSendEmail` is self-targeted because sending mail is an operation on that
application. Per-application choice does not require a target parameter. The choice is explicit,
and a dependency with one implementation can remain a plain trait.

### Your second application already exists — it is spelled as a feature flag

Look for existing variation before proposing another context type. Feature-gated backends, a
backend enum, a trait object, a generic application type, or a test harness can show that the
program already supports more than one arrangement. Do not assume every reader has this need.

A separate context type can make a build-time distinction explicit. Pair that explanation with the
`App` and `TestApp` wiring above instead of introducing another example. This remains an
environmental, self-targeted arrangement.

Keep runtime choices in a runtime representation. Configuration read at startup may select an enum
variant or a trait object stored inside the context. Static wiring does not replace that decision,
and not every configuration needs a distinct context type.

### Swap your error type or runtime by changing one line

Use abstract types to show how generic logic can avoid committing to a particular error or runtime.
This fragment selects an error type for a context defined elsewhere; it assumes an `anyhow`
dependency and omits error-raising providers and their checks:

```rust
use cgp::prelude::*;
use cgp::core::error::ErrorTypeProviderComponent;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<anyhow::Error>,
    }
}
```

Changing the entry changes the context's associated error type. Generic logic can remain unchanged
when the replacement satisfies its bounds and the error-raising and wrapping providers remain
compatible. Do not promise that changing every error backend requires only this line.

Use this example for systems and ML-module readers. Link to
[modular error handling](../cgp/concepts/modular-error-handling.md), and distinguish configurable
associated types from representation hiding through Rust's module privacy.

### Break up a trait that grew into a monolith

Show how independently chosen implementations can motivate smaller components. CGP grew from work
on the large `ChainHandle` interface described in [author-personality.md](author-personality.md).
The relevant benefit is that reusable providers can satisfy separate operations without each
implementation supplying an unrelated collection of methods.

Split along the choices real contexts need to make. Keep items together when one provider choice
determines them together; separate unrelated choices when doing so improves reuse. Methods specific
to one concrete context can use direct consumer impls. Follow
[sizing a component](../cgp/guides/sizing-a-component.md).

State the refactoring cost. Changing the interface affects its callers, and a small stable trait
with one implementation should usually stay as it is. A large component is legal; size alone does
not establish that splitting it is worthwhile.

### Write a framework over any type's structure — without runtime reflection

Explain structural programming through types that expose their fields or variants to generic code.
CGP derives encode that shape as type-level data, allowing reusable builders, serializers, and
visitors with static checks. See [extensible records](../cgp/concepts/extensible-records.md) and
[extensible variants](../cgp/concepts/extensible-variants.md).

State the opt-in requirement beside the benefit. This is compile-time structural reflection encoded
in types, not runtime introspection of arbitrary values. Static shape information removes the need
for a runtime metadata lookup; the operation still does its actual work, such as reading fields or
serializing values.

### Stop threading a dozen generic parameters through every layer

Lead with intermediate signatures that repeat dependencies they do not use. Separate generic error,
runtime, and storage parameters can spread through a call chain. A context can instead supply
associated types and operations, so callers name the operation they need without repeating every
implementation dependency.

Show the distinction between a type selected by the caller and one determined by the context.
`#[use_type]` imports a context's associated type where the code needs to name it. Implementation
bounds remain explicit at their point of use; they do not disappear from the program.

Use this explanation for maintainers of deep call graphs. It is an environmental-context example,
and its value is simpler dependency signatures. A type inferred from a field may not need a named
abstract type at all, and a function with a few independent inputs may be clearer as a plain
generic. Follow [naming a type dependency](../cgp/guides/naming-a-type-dependency.md).

### Keep a provider's dependencies out of your public API

Explain how impl-side constraints separate an operation's interface from its implementation needs.
A provider can use `#[uses]` and `#[implicit]` without adding those dependencies to the consumer
method signature. This helps library authors keep implementation requirements from spreading to
callers.

Keep Rust's privacy rules in the explanation. A type that appears in a public method signature
still needs appropriate visibility. CGP helps avoid exposing some dependencies in that signature;
it does not make a private type valid in a public interface. See
[impl-side dependencies](../cgp/concepts/impl-side-dependencies.md) and [evidence.md](evidence.md).

### Read a CGP compile error without decoding a wall of generated types

Show a real missing dependency and the diagnostic that identifies it. This example is based on
cargo-cgp's [missing-field fixture](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/fields/base_area_1_1.rs).
The provider needs both dimensions, but `Rectangle` supplies only `width`:

```rust
use cgp::prelude::*;

#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_impl(new RectangleArea)]
impl AreaCalculator {
    fn area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
        width * height
    }
}

#[derive(HasField)]
pub struct Rectangle {
    pub width: f64,
}

delegate_components! { Rectangle { AreaCalculatorComponent: RectangleArea } }
check_components! { Rectangle { AreaCalculatorComponent } }

fn main() {}
```

The fixture's [diagnostic snapshot](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/fields/base_area_1_1.cgp.stderr)
contains this root-cause note:

```text
   = note: root cause: [CGP-E106] missing field `height` on `Rectangle`
           this is required through the dependency chain:
             [CGP-E101] consumer trait impl `CanCalculateArea` for context `Rectangle`
             └─ [CGP-E102] provider trait impl `AreaCalculator` with context `Rectangle` for provider `RectangleArea`
               └─ [CGP-E106] missing field `height` on `Rectangle`
```

Explain the repair rather than only praising the shorter output. The check forces verification of
`RectangleArea` for `Rectangle`; adding a suitable `height` field satisfies the missing dependency.
The [toolchain reference](../cgp/reference/cargo-cgp.md) explains how the driver recovers and presents
the cause. Recheck the fixture before publishing its output.

Keep the canonical limitation beside the tool claim:
`cargo cgp check` leads with the root cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every class.

### Choosing which problem to lead with

Choose the opening by the reader's problem. Use this mapping alongside [readers.md](readers.md):

| Reader | Opening problem |
| --- | --- |
| Broad audience or type-system reader | Overlapping impls rejected by Rust |
| Trait-heavy developer or library author | Behavior for a foreign target without a newtype |
| Working developer evaluating testability | Test and production implementations |
| Reader unsure why contexts differ | Existing build-time variation or a test harness |
| Systems or ML-module reader | A configurable error or runtime type |
| Deep call-graph maintainer | Repeated dependency parameters |
| Evaluator or framework author | A trait whose implementation responsibilities have grown |
| Structural-framework author | Generic operations over opted-in fields and variants |
| Reader concerned about diagnostics | A real wiring failure explained by the toolchain |

For a broad introduction, prefer the overlap or foreign-target example. It shows a specific
restriction and a concrete alternative arrangement before asking the reader to learn CGP's terms.

## The strengths worth advertising

Advertise a strength only when it is accurate, relevant to the intended reader, and tied to a
problem. Use concrete mechanisms instead of general praise, and state the relevant cost nearby.

**Static provider selection** gives a precise runtime claim. Wiring resolves at compile time and
uses statically dispatched calls, without a runtime container or vtable lookup for that selection.
Providers are type-level markers and need not be instantiated. Say "provider selection adds no
runtime lookup"; avoid unsupported claims about comparative speed or the entire binary.

**Separate providers allow interchangeable implementations.** Implementations that would overlap
on one `Self` type can coexist on different provider types. A context selects the provider for a
component and any dispatch parameters. Rust still enforces coherence on the generated impls; CGP
changes the arrangement rather than disabling those checks.

**Explicit selection makes choices inspectable.** Say "the application names its provider in a
wiring table." Use "application" only where that is the context's role. Defaults, namespaces, and
forwarding can add steps to the lookup, so explain those when present rather than promising every
call is explained by one local line.

**Checked dependencies catch incompatible choices at compile time.** A provider declares its
requirements through bounds and attributes. A component use or an explicit `check_components!`
assertion forces those requirements to be checked. Defining the delegation entry alone does not.
Checks are code the writer supplies, and their raw diagnostics can be verbose.

**Declared requirements limit what generic code can access through its context.** A generic
provider can use the operations available through its bounds, instead of assuming access to every
field of a concrete application. This helps even in a single application. It is not a sandbox:
ordinary Rust functions can still access other in-scope APIs, and a broadly bounded dependency may
itself expose many operations.

**Dedicated tooling helps explain wiring failures.** Demonstrate `cargo cgp check` with a real
fixture and retain the canonical qualification: `cargo cgp check` leads with the root cause for the
classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every class.
Do not describe the error problem as solved.

**Gradual adoption preserves ordinary Rust choices.** A consumer trait supports direct impls,
providers use familiar impl syntax, and implicit arguments resemble parameters. Start with one
operation or component. Explain the additional generated code and wiring rather than claiming that
CGP eliminates boilerplate.

Blanket extension traits provide a useful introduction for readers who know them. The pattern
behind `Itertools` or `StreamExt` helps explain how a generic impl can add methods to existing
types. Then explain what CGP adds: separate providers and context-specific selection. The analogy
introduces the foundation without equating the libraries.

**Abstract types keep context-selected types from becoming separate parameters.** Generic code can
name an associated error, scalar, or runtime type and let the context supply it. This can simplify
intermediate signatures, but does not remove every generic parameter, trait bound, or visibility
requirement. Use "the context determines the type" rather than promising that every type dependency
is a one-line change.

**Type-level shapes support reusable structural operations.** An opted-in type exposes field or
variant information to statically checked generic code. State the derive requirement and the work
performed by the operation. Avoid suggesting that compile-time metadata makes serialization or
field traversal itself free.

**Stable Rust lowers the toolchain requirement for the library.** CGP is a library, not a compiler
fork or a language proposal. Distinguish this from the optional compiler-linked `cargo-cgp` tool,
whose setup provisions its own pinned nightly. Stable compilation does not establish production
maturity or adoption at scale.

### Audience-tuned one-liners

Use an analogy only for a reader who knows its source, and give its limit nearby. The
[related-work](../related-work/README.md) documents develop these comparisons:

| Reader | Useful phrasing and qualification |
| --- | --- |
| Scala or implicits | "Keep dependencies out of intermediate calls, with provider choices recorded in wiring." Explain that this is not Scala's implicit search; associated types also carry context-selected type dependencies. |
| Haskell or type classes | "Separate providers let overlapping implementations coexist, with a choice per context." Rust's coherence rules still apply to the generated traits and impls. |
| Spring, Guice, or Dagger | "Select dependencies through Rust traits and check the selected providers at compile time." Compare lifecycle and configuration needs fairly; Dagger also performs compile-time checking. |
| Dynamic languages | "Reuse implementations across types satisfying their bounds, with provider selection resolved statically." This does not supply runtime duck typing or runtime-open plugins. |
| OCaml or ML modules | "Choose implementations in a declarative wiring table." Explain the differences from functor application and representation sealing. |
| Algebraic effects | "An analogy to the exactly-once, resume-in-place fragment, selected through types." CGP does not provide continuation capture or dynamic handler scope. |
| Reflection or framework authors | "Compile-time structural reflection encoded in types." State that types opt in and that runtime work still depends on the operation. |
| PureScript or row types | "Extensible data patterns in nominal Rust, with opt-in shape information." Avoid claiming a built-in row-polymorphic type system. |

Higher-order providers offer another example for readers composing constrained functions. A type
alias can name a composition such as `ScaledAreaCalculator<RectangleAreaCalculator>` without
repeating all its operational bounds at the alias. Those bounds must still hold when the provider
is checked or used. See [higher-order providers](../cgp/concepts/higher-order-providers.md).

## The objections readers bring

Distinguish a mistaken comparison from a real cost before answering. Some concerns come from tools
CGP resembles; others concern Rust macros, learning, or maintenance. Grant the valid part and show
the relevant mechanism. Use [evidence.md](evidence.md) for observed reception rather than assuming
that every reader raises every objection.

### Imported from other paradigms

Answer comparisons by naming the mechanism and its limits:

- **"DI is heavy and fails at runtime."** CGP selects providers through the trait system rather
  than a runtime object container. Do not generalize all DI libraries as reflection-based or
  dynamically checked; compare the specific tool the reader knows.
- **"Values appear from nowhere."** Explain where the context holds values, how a provider
  requests them, and where wiring or defaults select implementations. CGP does not choose a
  preferred provider by guessing the developer's intent.
- **"Coherence exists for a reason."** Agree, then show that separate provider types permit
  alternatives while Rust checks the wiring impls for overlap. Use the
  [RustLab explanation](../website/blog/rustlab-2025-coherence.md) as the model for explaining why
  coherence matters before presenting CGP's arrangement.
- **"Extensible records produce huge errors."** Concede that shape-related failures can expose
  long generated types. Opt-in use and explicit checks help localize them without guaranteeing
  short diagnostics.
- **"Is this an effect or reflection system?"** Explain the fragment the analogy covers. CGP does
  not supply continuations or arbitrary runtime introspection.
- **"Static dispatch loses runtime flexibility."** Agree that static wiring cannot load unknown
  implementations at runtime. Use `dyn Trait` or another runtime representation for that need;
  a CGP context may contain it.

### Native to the Rust audience

Answer Rust-specific concerns with a concrete example and a proportionate recommendation.

**"This is over-engineered."** Show the problem before the component declarations and say where a
plain trait, generic, or enum is enough. More enthusiasm does not justify more machinery.

**"I only have one application."** Concede that selecting different providers across contexts is
not yet a demonstrated benefit. Then examine needs that can exist within one application:
overlapping providers for different targets, foreign target types, and implementation dependencies
kept out of intermediate interfaces. Look for a real test context or build-time variation, without
inventing a future need.

Recommend the simplest useful form when those needs are absent. A plain trait or `#[cgp_fn]` may
suffice without wiring. The presence of only one context does not by itself rule out providers,
and the possibility of a future second context does not justify them by itself.

**"Can a component have only one method?"** Show that a component is an ordinary multi-item trait
before discussing design guidance. `CanCompute` and `CanHandle` include an associated `Output`
alongside a method. Components may contain methods, associated types, and consts; grouping is a
reuse decision, not a macro limit. Follow [sizing a component](../cgp/guides/sizing-a-component.md).

**"Will every configuration require its own context?"** Separate types only where the program
benefits from the distinction. Generics can share a context definition across backend types, while
enums or trait objects can hold runtime choices. A generic context definition still produces
distinct instantiated types; do not claim it erases that distinction.

Context-generic code can also preserve downstream choice. If reusable logic depends on context
traits rather than an upstream backend enum, a downstream crate can define its own context and
backend representation, then reuse compatible providers. State the required bounds instead of
promising universal reuse.

**"I cannot see what the macros generate."** Show the ordinary Rust expansion and point to
`cargo cgp expand`, following the [tool reference](../cgp/reference/cargo-cgp.md). Check the
installed tool's command availability before giving instructions. Debugging generated code remains
a cost.

**"I cannot tell which code runs."** Trace the consumer call through the wiring to the provider.
Concede the indirection and show any namespace, forwarding, or wrapper involved. Static selection
makes the route inspectable; it does not make every route one step long.

**"What happens to compile times?"** State that macros, type checking, and monomorphization add
compile-time work. Do not invent a magnitude or claim that every added compile-time cost replaces
a runtime cost. The [Hypershell account](../website/blog/hypershell-release.md) models how to
separate observations from rough experiments.

**"The errors are a wall of generated types."** Concede the raw diagnostic cost and show checks
and tooling on the actual failure. Use the canonical sentence: `cargo cgp check` leads with the
root cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape
every class.

**"Rust does not need a DI framework."** Agree that ordinary traits and generics often suffice.
Show the particular limitation at issue, such as overlapping impls or repeated dependency
parameters, instead of arguing for frameworks in general.

**"Why not traits, generics, or an enum?"** Compare those alternatives fairly and recommend the
lowest useful level of abstraction. The [modularity hierarchy](../cgp/concepts/modularity-hierarchy.md)
provides the decision guide.

**"Is it mature enough for my codebase?"** State the project's maturity and limits honestly.
Incremental adoption permits a smaller evaluation, but removing an abstraction still takes work.
CGP does not require a framework runtime; that fact is not proof of production readiness. Preserve
the candid maturity guidance recorded in [site-structure.md](../website/site-structure.md).

**"There is a learning curve."** Agree and make the first task small. A function-style operation
can introduce useful context-generic code before components and wiring. Teach the later machinery
when the reader needs it instead of describing the whole learning curve as trivial.

### The one mitigation that spans three of these

Mention CGP's [agent skill](https://github.com/contextgeneric/cgp-skills) where it can help with
learning vocabulary, reading diagnostics, or writing wiring. It teaches an assistant to read and
write CGP. Readers can try it on their own tasks; do not promise that it eliminates their need to
understand or review the result.

Keep this support beside the costs, outside the tag line, feature panel, and opening. Suitable
places include a cost section, a boundary discussion, or a maturity page. State what help is
available without treating readers who work without an assistant as having had their problem solved.

Separate agent support from AI authorship. Help using CGP belongs here; claims about how CGP is
built follow [ai-disclosure.md](ai-disclosure.md).

The website's "AI" navigation entry is a standing exception to the placement rule. It labels the
section containing the skill and disclosure page, under the decision in
[information-architecture.md](../website/information-architecture.md#the-target-page-inventory).
Retain that label while keeping other prominent introductory copy focused on CGP's benefits and
code. The exception permits navigation, not an AI-led pitch.

## When not to reach for CGP

Recommend the simplest abstraction that solves the actual problem. Provider wiring is most useful
when interchangeable or reusable implementations justify explicit selection. Other CGP constructs,
such as `#[cgp_fn]`, can help without a wiring table; distinguish them from the full provider pattern.

Compare the alternatives by the choice the reader needs to make:

| Alternative | Prefer it when | Consider CGP when |
| --- | --- | --- |
| Plain trait or generic | One implementation per type or a few explicit parameters suffice. | Interchangeable providers or repeated implementation dependencies make that arrangement awkward. |
| Direct consumer impl | An implementation belongs to one context and does not need provider composition. | Another context can reuse the provider, or a wrapper needs to compose with it. `#[cgp_impl(Self)]` also supports direct impls. |
| Enum | A small closed set and a match express the choices clearly. | Independent modules need extensible data patterns with statically checked operations. |
| `dyn Trait` | Heterogeneous values or runtime-selected implementations are required. | Static provider selection fits the choice. Runtime values can still live inside a CGP context. |
| DI library | Its object construction, lifecycle, and configuration model fits the application. | Trait-based selection and compile-time dependency checks fit better. Compare the specific library. |
| A library such as `frunk` | A focused structural operation needs a smaller tool. | Structural programming belongs within a broader component design. |
| A bespoke macro | The generation task is narrow. | The macro would otherwise recreate CGP's provider and wiring mechanism. |
| A future language facility | Waiting is acceptable and its eventual design may fit better. | The required pattern is available in CGP now. Do not promise what a proposal will stabilize into. |

Preserve global consistency where the program relies on it. A map key's `Ord` implementation is an
example where one program-wide meaning matters. Per-context alternatives are not automatically an
improvement over that contract.

Use the boundary plainly: "For one implementation, start with a plain trait. Add providers when
interchangeable implementations or reuse justify them." Follow the
[modularity hierarchy](../cgp/concepts/modularity-hierarchy.md) for the more detailed choice.

## Keeping this document honest

Check claims and examples against the source and the `/cgp` skill under the
[synchronization rule](../AGENTS.md#the-synchronization-rule). Keep each problem, strength,
objection, and boundary consistent, and update [messaging-brief.md](messaging-brief.md) when a
summarized claim changes.

Use [vocabulary.md](vocabulary.md) for shared terms, [related-work](../related-work/README.md) for
comparisons, and [evidence.md](evidence.md) for audience findings. A shorter sentence must preserve
the conditions that make the claim true.
