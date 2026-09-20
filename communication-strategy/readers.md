# Readers: knowledge, expectations, and comprehension barriers

Choose an intended reader, identify what they already understand, and teach the missing concepts
before relying on them.

This document supplies audience profiles and teaching guidance. Most profiles are working
hypotheses, not measured descriptions of CGP's audience. [Evidence.md](evidence.md) records the
observations behind the model; [keeping the model observed](#keeping-the-model-observed) explains
how to test it. Use [reader-simulation.md](reader-simulation.md) to apply a chosen profile to a draft.

## Naming the reader is the first decision in a piece

Choose the reader before the outline and examples. Their knowledge and purpose determine which
problem to introduce, which terms need explanation, and how much mechanism the piece should show.
An explanation of overlapping implementations may suit a type-system reader, while a test and
production example gives an application developer a more immediate reason to continue.

Describe the reader along independent dimensions:

- **Rust experience:** Which trait, generic, and associated-type concepts can the piece assume?
- **Disposition:** Are they exploring an idea or evaluating whether its complexity is justified?
- **Prior model:** Which other languages or frameworks shape their expectations?
- **Task:** Are they scanning, learning, debugging, or making an adoption decision?

Treat profiles as combinations, not exclusive categories. An advanced Rust developer can also be
a cautious evaluator familiar with Haskell. Technical fluency does not imply approval of CGP or
remove the need to explain its vocabulary.

## Readers by Rust experience

Match the explanation to the reader's prerequisites. These profiles guide teaching choices without
claiming that every developer at a given experience level knows the same things.

### The Rust newcomer

Start a newcomer with a useful operation that resembles ordinary Rust. A `#[cgp_fn]` function
with an implicit argument and a matching context can show a result before introducing providers
or wiring. Explain any required field-access derive and import rather than assuming they are obvious.

Defer the consumer/provider split and coherence until they answer a question the example raises.
Keep `DelegateComponent` and `IsProviderFor` out of the initial explanation. When wiring becomes
necessary, describe it as a table selecting an implementation and state that selection happens at
compile time.

Give this reader a short path through the material. They may still be learning ownership and trait
bounds, so a complete feature tour can obscure the next useful step. Make prerequisites and links
to later explanations explicit.

### The working Rust developer

Use the working developer as the default reader for general CGP writing. Assume familiarity with
traits and generics, but explain CGP-specific roles. Lead with a concrete problem such as reusable
alternative implementations, foreign target types, or test and production dependencies.

Show enough ordinary Rust and CGP code to assess the tradeoff. Address compile-time work,
diagnostics, teammate learning, and the cost of adoption. Explain when plain traits or direct impls
remain sufficient. [Message.md](message.md#the-objections-readers-bring) owns the detailed responses,
including the case of a single application context.

Introduce higher-order providers after the reader understands a provider and its wiring.
Composition adds another relationship to follow, so establish a reason for a wrapper before showing
its type parameters. For debugging, show checks and the tool's limits using the
[canonical cargo-cgp wording](vocabulary.md#terms-to-use-and-how-to-introduce-each).

### The advanced Rust developer

Give advanced readers access to the actual mechanism. They may already understand associated
types, blanket impls, `PhantomData`, and coherence, so a generated impl can explain more than an
extended analogy. Still define the CGP names used in the expansion.

Engage technical objections directly. Show how distinct provider types satisfy coherence, how
wiring selects one implementation, and where bounds are checked. Discuss compilation and diagnostic
costs without inventing measurements. Use the [coherence account](../cgp/concepts/coherence.md)
and [type-class comparison](../related-work/type-classes.md) for the detailed reasoning.

Do not treat interest in the type system as a preference for complexity. An expert may understand
the construction and still reasonably prefer a simpler design for the use case.

## Readers by prior mental model

Use familiar concepts to introduce CGP, but qualify each analogy where behavior differs.
The linked [related-work documents](../related-work/README.md) own the technical comparisons and
their evidence. Public comparison pages follow the
[comparison guide](../website/writing-guides/related-work.md).

**Functional-programming and type-system readers** may know type classes, implicit parameters,
row types, effects, or ML modules. Connect only the concepts relevant to their background:
provider selection can be compared with instance selection, and provider requirements with type
constraints. Explain that CGP uses Rust types and compile-time wiring rather than claiming full
equivalence to first-class modules, row polymorphism, or effect handlers. Use
[type classes](../related-work/type-classes.md),
[implicit parameters](../related-work/implicit-parameters.md),
[row polymorphism](../related-work/row-polymorphism.md),
[algebraic effects](../related-work/algebraic-effects.md), or [ML modules](../related-work/ml-modules.md).
State why the Rust setting matters instead of claiming better ergonomics than those languages.

**Dependency-injection developers** may think in interfaces, bindings, construction, and object
lifecycles. Explain wiring as selecting implementations and provider bounds as dependency
requirements. Then distinguish those choices from constructing runtime objects: CGP does not supply
a runtime container or lifecycle manager. Do not imply that all DI systems rely on reflection or
startup checks; compare the specific system, following
[dependency injection](../related-work/dependency-injection.md).

**Dynamic-language developers** may recognize code written against operations a value supports
without naming its concrete type. Explain that Rust checks the declared bounds and resolves CGP
wiring at compile time. This does not guarantee freedom from runtime failures or provide
monkey-patching and runtime-open plugins. Trait objects or other runtime representations can still
live inside a CGP context. See [dynamic dispatch](../related-work/dynamic-dispatch.md).

**Framework, library, and tooling authors** may need generic operations over fields and variants.
Lead with a verified structural operation and state that participating types must expose their
shape, usually through derives. Explain the compile-time representation and the runtime work the
operation still performs. Address diagnostic quality, compile time, and generated code size.
Use [reflection](../related-work/reflection.md) for the limits of that comparison rather than
presenting CGP as arbitrary runtime introspection.

Library authors also need to understand what consumers must learn. Show how a reusable provider
can hide implementation dependencies while its public interface remains ordinary Rust. Do not
promise that consumers never need to understand wiring or diagnostics.

## Readers by role and point of contact

Adapt the entry and supporting detail to what the reader is trying to decide. A quick introduction
and an adoption review can use the same facts in different orders.

**First-contact skimmers** need a concrete description before specialized vocabulary. Give a
short benefit, a small example, and a clear next step. Address the most likely misunderstanding
raised by that example, such as runtime provider lookup, without making the opening a list of
rebuttals. Do not assume a short visit means hostility or predict how the reader will react publicly.

**Evaluators and decision-makers** need evidence about fit and cost. Explain incremental adoption,
learning requirements, debugging, project maturity, and where simpler tools suffice. A component
can be adopted independently, but removing an abstraction still takes work. Use the
[message guidance](message.md) and [evidence](evidence.md) rather than promises about effortless
migration or production readiness.

### The language-design and compiler-team reader

Present CGP to language-design readers as a concrete implementation relevant to a specific design
question. Show the generated Rust, the fragment of the proposed behavior it expresses, and the
limitations it leaves unresolved. They may care more about that boundary than about application-level
benefits.

Use precise terminology and preserve uncertainty where evidence is incomplete. Technical depth
permits concise explanations of familiar mechanisms; it does not justify unsupported certainty.
Distinguish working code from a formal result, and distinguish an implementation pattern from a
solution for migrating Rust's existing trait ecosystem.

Connect the piece to a relevant design discussion when one exists. The
[evidence catalog](evidence.md#the-conversations-that-draw-attention) records topics worth checking.
A broad announcement can introduce the project, but a focused example is more useful for evaluating
a language-design claim. Avoid positioning CGP as a competitor to language improvements.

## What nearly every reader shares

Help readers judge whether the abstraction solves a problem they have. Show the implementation
choice, where the compiler checks it, and what extra code or knowledge it requires.

Explain recurring sources of confusion when the passage raises them: provider selection is static,
CGP builds on ordinary Rust traits, and using a construct does not require learning every generated
impl first. These are explanatory needs, not a reason to label readers as dismissive.

For a mixed audience, default to a working Rust developer evaluating a concrete use case. Keep the
opening understandable to a skimmer and provide links or later sections for deeper inspection.
This is an editorial default, not a claim about the audience's demographics.

## The comprehension barriers

Distinguish difficulty understanding CGP from doubt about its value. A reader who cannot follow a
bound needs an explanation; a reader who understands it but questions the cost needs a comparison.
Additional persuasion does not supply a missing prerequisite.

Introduce concepts in an order that builds on what the reader knows. Traits and generic bounds
support understanding blanket implementations and associated types; those in turn help explain
provider selection and type-level composition. Check the chosen reader's knowledge rather than
assuming every working Rust developer follows the same progression.

Use CGP's [recommended idioms](../cgp/guides/README.md) to control how much machinery appears at
once. The concise forms are normal CGP code, not a temporary dialect the reader must later replace.

### Generic parameters are intimidating

Introduce each generic parameter when the example needs the variation it represents.
`#[cgp_fn]` can introduce an operation without written generic parameters, `#[cgp_impl]` can omit
an explicit context parameter, and `#[implicit]` can name needed context values as arguments.

Show what the code does before explaining every generated bound. When a parameter becomes
necessary, identify its role: context, target, selector, or inner provider. Avoid reassuring readers
that a long signature is simple without explaining those relationships.

### The provider trait reads inside-out

Distinguish the meaning of `Self` in ergonomic syntax from its meaning in a raw provider impl.
Inside `#[cgp_impl]`, `self` and `Self` refer to the context. In a raw provider-trait impl, Rust's
`Self` is the provider marker and `Context` is an explicit parameter.

Teach `#[cgp_impl]` as the usual writing form. When showing its expansion, label the roles before
tracing the method body. Use the
[consumer/provider account](../cgp/concepts/consumer-and-provider-traits.md) for the generated traits;
do not describe raw provider-side `Self` as the context.

### A type can stand for your whole application

Explain an application context by showing what it selects and stores. `struct App;` can carry
wiring without fields, while another context can hold a client, configuration, or mutable state.
An empty context is possible, not a requirement or evidence that all dependencies lack runtime data.

Use ordinary Rust to establish the arrangement before attributing its benefits to CGP. A trait
implemented on `ApiServer` can encode a separate `Vec<u8>` argument, and `Firmware` can implement
the same interface differently. Ordinary Rust already permits these contexts. CGP adds a reusable
provider layer and wiring when independently selectable implementations are useful.

Show an actual overlap if it motivates the example. Do not claim that application contexts are
pointless in ordinary Rust or that sharing logic always requires overlapping blanket impls.
The [modularity hierarchy](../cgp/concepts/modularity-hierarchy.md) explains the available choices,
and [vocabulary.md](vocabulary.md#qualifying-a-context-and-a-target) names their roles.

### The trait a reader would design hides the payoff

Explain component grouping as a decision about provider reuse. A `Shape` component containing
`area`, `perimeter`, `scale`, and `rotate` is valid, but every provider must supply that interface.
An area-only wrapper may need unrelated forwarding methods, and an area-only context may not have
the dependencies needed for rotation.

Show a multi-item component before recommending a split. `CanCompute` and `CanHandle` each contain
an associated `Output` and a method; components also support multiple methods and consts. This
prevents the observed misunderstanding that CGP limits a trait to one item, recorded in
[evidence.md](evidence.md#cgps-own-reception-and-the-lessons-in-it).

Compare the reuse of a grouped component with that of focused components. Group items when one
provider choice should determine them together. A noun-based consumer trait name can prompt a
review, but it does not prove the grouping is wrong. The author decides whether the reuse benefit
justifies a split; [sizing a component](../cgp/guides/sizing-a-component.md) supplies the procedure.

### Bounds on the context are a barrier of their own

Explain `#[uses]` as declaring a trait dependency on the context. It generates a bound such as
`Self: HasName`; it does not act as a Rust `use` statement or import a trait into module scope.
A resemblance to an import can help, provided that distinction remains clear.

Start less experienced readers with `#[cgp_fn]` when a single implementation is sufficient.
The author writes a function, and the macro generates a trait and blanket impl. Defer the expansion
until useful, but do not claim the generated operation works without traits.

### Traits that are "magically" implemented

Explain where generated implementations come from when a method appears without a handwritten impl.
An automatic getter uses a blanket impl over matching `HasField` bounds. The relevant trait must
also be in scope for trait-method syntax.

Prefer implicit arguments for routine reads from the provider's own context. They avoid requiring
a separately named getter, while still using generated field bounds and reads. Introduce getter
traits when code needs a named accessor, access on another type, or an inferred associated type.
Use a wireable getter when contexts must choose different source fields.

### Associated types and qualified paths

Introduce `#[use_type]` as a concise way to name an abstract type and declare its trait requirement.
It lets an implementation use `Error` while generating the corresponding qualified associated-type
path and bound.

Show the expansion when the reader needs to understand where that type comes from. Keep a
construct's own associated type qualified, as in `Self::Output`; the imported-type shorthand does
not apply to every associated type in a trait.

### The wiring table and its machinery

Describe wiring as a table from a component key to a provider. Trace one call through one entry
before introducing forwarding, namespaces, or wrappers. State that Rust resolves the selection at
compile time without a runtime lookup table.

Reserve `DelegateComponent` and `IsProviderFor` for explanations of expansions or diagnostics.
A beginner can understand the selection model first, then inspect the generated traits when the
mechanism answers a concrete question.

### Reading the error messages

Prepare readers for verbose errors involving generated types and transitive dependencies.
`check_components!` checks selected components near their wiring, which helps locate failures.
It does not guarantee that every diagnostic becomes short or identifies the cause equally well.

Introduce cargo-cgp when demonstrating a wiring failure. Use the canonical qualification:
`cargo cgp check` leads with the root cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every class.
Teach readers to inspect the reported cause and use the
[error catalog](../cgp/errors/README.md) or [tool reference](../cgp/reference/cargo-cgp.md) for
unfamiliar cases. Check actual output rather than promising a particular rewrite.

Mention the agent skill beside these costs when relevant. It teaches an assistant the CGP
vocabulary and can help it trace wiring and interpret diagnostics. The reader still needs to review
the result. [Message.md](message.md#the-one-mitigation-that-spans-three-of-these) owns the limits
and placement of that claim.

### Knowing where to start, and why it is worth it

Give the reader a minimal useful path and a reason to follow it. An operation with one shared
implementation may need only a plain trait or `#[cgp_fn]`. Introduce provider selection when the
example needs interchangeable or reusable implementations.

Use the [modularity hierarchy](../cgp/concepts/modularity-hierarchy.md) to explain how far to go.
A reader who can parse every macro may still need an example showing why the split is useful;
a reader who sees the benefit may still need prerequisites before reading the expansion.

### The teaching discipline this points to

Check instructional writing for these requirements:

- **Name example roles:** Identify the context and target, especially when they change.
- **Build on prerequisites:** Explain a dependency before using it to explain another construct.
- **Use recommended syntax:** Teach `#[cgp_fn]`, `#[cgp_impl]`, and companion attributes as idioms.
- **Motivate the construct:** Show the problem and the change the construct makes.
- **Explain grouping:** Demonstrate multi-item support and the reuse consequences of component size.
- **Expose the mechanism when needed:** Use expansions to answer questions about behavior or trust.
- **Show costs and checks:** Include relevant limitations and a way to inspect failures.

Progressive explanation controls order, not completeness. A first-principles tutorial may show
explicit Rust before macro syntax; an applied tutorial may defer that explanation. Follow the
[tutorial guide](../website/writing-guides/tutorial.md) and the reader's task.

## Keeping the model observed

Treat the profiles as hypotheses until evidence supports a more specific claim. CGP's recorded
reception includes requests for a clearer motivating problem, confusion about the project name,
and the mistaken inference that components are limited to one method. The
[reception summary](evidence.md#cgps-own-reception-and-the-lessons-in-it) records these patterns;
it does not establish their frequency across the whole Rust community.

Use reading and usage feedback to test the model. A **friction log** records where someone following
a page stops or needs outside information. For a runnable tutorial, use the documented starting
environment, follow the page without other guidance, and record each stall, search, command, and
compiler result. Measure time to the working program. For an explanation or navigation page,
record comprehension and routing problems instead of imposing a compilation task.

Distinguish a cold reader's experience from an author's or agent's review. An author already knows
the missing steps, and an agent may supply knowledge the page never taught. Both reviews can find
problems, but neither establishes how an unfamiliar human reader performs. Keep raw logs outside
this repository; summarize useful patterns in [evidence.md](evidence.md) and revise the affected page.

Ask people who have used CGP about concrete attempts. Useful questions include what they tried
first, where they stopped, what they did next, how they would describe CGP to a colleague, and what
it failed to do that they expected. Summarize answers without attributed quotations or links to
individual reactions, following the [public-repository rule](../AGENTS.md#this-repository-is-public).

Mark supported findings as observed and link to their evidence. When a finding contradicts an
inference, rewrite the inference rather than appending a history of the correction. Keep the scope
of the finding visible so a few reports do not become claims about every reader.
