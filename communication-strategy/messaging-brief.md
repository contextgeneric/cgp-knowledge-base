# Messaging brief: the strategy on one page

Use this brief while drafting, and consult the linked documents for reasoning, examples, and limits.

The fuller documents govern when a summary disagrees with them. Start with the author's
[preferences](author-personality.md) and [voice guidance](voice-and-register.md), then choose the
reader and problem before writing the opening.

## The line, and the two lines after it

Use the settled descriptor and follow it with reassurance and relevant breadth. The wording and
positioning belong to [identity.md](identity.md#the-pitch-that-follows-the-line):

- **Tag line:** A language extension for Rust, with pluggable trait implementations at compile-time.
- **Reassurance:** Still ordinary Rust: a library on the stable toolchain, with provider selection
  resolved at compile time, adopted one trait at a time.
- **Breadth:** Beyond interchangeable implementations, CGP adds abstract types chosen by each
  context, so error and runtime types need not be separate parameters through every layer. It also
  supports extensible records and variants, and composable handlers.

Show how CGP extends Rust's trait system. Consumer traits support direct impls, and a project can
adopt a component without converting the rest of its code. Introduce the paradigm name beside a
plain description after the concrete benefit is clear.

## The five headline features

Use this panel for a full feature summary, in the order fixed by
[identity.md](identity.md#the-headline-feature-set). Put code early in a README rather than requiring
readers to pass the full panel first.

| Feature | Public wording |
| --- | --- |
| One Interface, Many Implementations | Write interchangeable implementations of one interface and choose between them per application. Separate provider types let implementations coexist while each application makes its choice explicit. |
| Zero-Cost Abstraction | CGP resolves provider selection at compile time and uses direct calls, without a runtime container or vtable lookup. Unused providers do not require runtime instances. |
| Type-Safe Wiring | Check wiring at compile time so missing dependencies fail the build. CGP connects providers through ordinary Rust traits, without requiring runtime reflection or dynamic dispatch. |
| Abstract Over Every Dependency | Write core logic against abstract error, runtime, and I/O dependencies, then let each context supply them. This supports a `no_std`-friendly core when the chosen implementations support it. |
| Still Ordinary Rust | Adopt CGP one component at a time. Providers use familiar impl syntax, implicit arguments resemble parameters, and consumer traits can still be implemented directly. |

## The pain to lead with, by reader

Choose the problem the intended reader recognizes. The examples and their limits are in
[message.md](message.md#the-problems-cgp-removes):

| Reader | Lead with |
| --- | --- |
| Broad audience or type-system reader | Overlapping implementations rejected by Rust |
| Trait-heavy developer or library author | Behavior for a foreign target without a newtype |
| Working developer | Test and production implementations |
| Reader unsure why contexts differ | Existing build-time variation or a test harness |
| Systems or ML-module reader | A context-selected error or runtime type |
| Deep call-graph maintainer | Repeated dependency parameters |
| Evaluator or framework author | Decomposing a trait with unrelated responsibilities |
| Structural-framework author | Generic operations on opted-in fields and variants |
| Reader concerned about errors | A real failure explained by the toolchain |

## The objections, and the one-line answers

Grant the valid concern, then explain the mechanism and limit. See
[message.md](message.md#the-objections-readers-bring) for the full answers:

| Concern | Answer |
| --- | --- |
| DI is heavy or fails at runtime | CGP selects providers through Rust traits; it does not require a runtime container. Compare other DI tools individually. |
| Values appear from nowhere | Show the context's data, provider requirements, and wiring or defaults that select implementations. |
| Coherence exists for a reason | Separate provider types allow alternatives while Rust still checks the generated impls for overlap. |
| This is over-engineered | Start with a plain trait; add providers when interchangeable implementations or reuse justify them. |
| I have only one application | Assess current needs such as foreign targets and hidden implementation dependencies. Do not assume a future context justifies wiring. |
| Components can have only one method | They support methods, associated types, and consts. Group items according to provider choice and reuse. |
| Every configuration needs a context | Separate useful type-level distinctions and retain enums, generics, or trait objects for other choices. |
| Macros hide the code | Show the expansion, using `cargo cgp expand` where available. Debugging generated code remains a cost. |
| Which code runs? | Trace the wiring and any forwarding or wrappers to the selected provider. |
| What about compile times? | CGP adds compile-time work. Give a magnitude only with supporting measurements. |
| The errors are verbose | Add explicit checks and demonstrate the toolchain, with its limitation below. |
| Is it mature enough? | State current limits and offer a small evaluation; stable compilation does not establish production readiness. |
| There is a learning curve | Start with a useful operation and teach the machinery as needed. |

Use the canonical checker qualification without paraphrasing:
`cargo cgp check` leads with the root cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every class.

## The boundary, and the costs to concede every time

Use the lowest level of abstraction that solves the problem. Plain traits and generics suit simple
choices; direct consumer impls suit context-specific behavior; enums suit small closed sets; and
`dyn Trait` supports runtime-selected implementations. Providers help when interchangeable behavior,
reuse, or composition warrants wiring. See [the decision guide](message.md#when-not-to-reach-for-cgp).

State the relevant costs beside the benefit: additional declarations and wiring, compile-time work,
verbose raw diagnostics, and learning. A delegation entry alone does not verify dependencies;
check or use the component to force verification.

Mention the [CGP agent skill](https://github.com/contextgeneric/cgp-skills) only beside the costs it
can help address, following [message.md](message.md#the-one-mitigation-that-spans-three-of-these).
It teaches an assistant to read and write CGP; it does not remove the reader's review responsibility.
Keep AI support out of the pitch and distinguish it from [AI authorship](ai-disclosure.md).
The website's AI navigation label is the documented exception to placement, not a feature claim.

## The ask, by stage

Match the next step to the reader, following [formats.md](formats.md#the-conversion-ladder):

- **First contact:** A quickstart or runnable example.
- **Working developer:** A tutorial addressing their problem.
- **Evaluator:** Maturity, trade-offs, incremental adoption, and a real system using CGP.
- **Enthusiast:** The book and contribution guidance, with version context where needed.

## Words

Use concrete terms and preserve their scope. [vocabulary.md](vocabulary.md) owns the full list:

| Avoid | Prefer |
| --- | --- |
| "modular" or "paradigm" as the lead | language extension; pluggable trait implementations |
| magic; finds the right implementation | a provider selected through explicit wiring or defaults |
| blazingly fast | provider selection resolved at compile time, without a runtime lookup |
| no boilerplate | wiring recorded in a readable table |
| replaces traits; a new language | ordinary Rust traits; a library on stable Rust |
| capability for a CGP construct | trait, method, operation, or trait dependency |
| errors solved | leads with the root cause for the classes it recognizes |
| AI-native or AI-first | an agent skill, described beside a cost |
| context without explanation | value or environmental context, with its role stated |

## The rules that apply to every piece

Apply these rules across formats:

- **Match voice to the page.** Project voice on documentation; the author's voice on the blog.
  Avoid a corporate "we" for one person. Preserve the exceptions in
  [voice-and-register.md](voice-and-register.md).
- **Keep claims accurate.** Verify code, qualify benefits, and represent alternatives fairly.
- **Protect readers' identities.** Summarize reactions to CGP without linking threads or quoting
  identifiable commenters.
- **Explain example shapes.** Identify the context and target, especially when they change.
- **Reuse established examples.** Prefer the encoder pair, greeter, email swap, or area calculation
  before introducing another domain.

## The four checks before publishing

Read the draft in this order, following [voice-and-register.md](voice-and-register.md#checking-a-draft):

1. Does it sound like the author or project, with specific claims instead of generic praise?
2. Are the relevant costs stated where readers need them?
3. Can intensifiers be removed without changing the meaning?
4. Does the voice match the page, without an accidental corporate "we"?

## Where the rest is

Consult the fuller guidance for the decision at hand:

- [Identity](identity.md): Positioning, descriptor, pitch, and headline features.
- [Readers](readers.md): Audience knowledge and comprehension barriers.
- [The message](message.md): Problems, benefits, objections, and boundaries.
- [Formats](formats.md): Structure and worked drafts for each format.
- [Reader simulation](reader-simulation.md): Predicting and testing comprehension while revising.
- [Writing styles](writing-styles.md): Direct sentences and plain wording.
- [Evidence](evidence.md): Audience findings, reception, and communication sources.
- [AI disclosure](ai-disclosure.md): Authorship, assistance, and review limits.
