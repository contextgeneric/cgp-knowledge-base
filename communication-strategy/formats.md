# Formats: guidance and worked drafts

Choose each piece's opening, depth, voice, and next step for its channel and intended reader.

This document covers launch posts, blog deep dives, READMEs, talks, threads, and comparisons. The
[homepage](../website/writing-guides/homepage.md),
[tutorial](../website/writing-guides/tutorial.md), and
[comparison page](../website/writing-guides/related-work.md) guides own those website formats and
govern where the guidance overlaps.

## Deciding in order

Decide the channel, reader, voice, format, and opening in that order. Use [evidence.md](evidence.md)
for observed reception, [readers.md](readers.md) for audience profiles, and
[voice-and-register.md](voice-and-register.md) for the project and author voices.

For each piece, settle these choices before drafting:

- **Opening:** Show a concrete problem or useful example before teaching the paradigm.
- **Depth:** Match the format and the reader's prerequisites; describe the scope of a long piece.
- **Likely objection:** Address the concern the opening could reasonably provoke, without turning
  the introduction into a list of rebuttals.
- **Next step:** Offer an action the reader is ready to take. Usually one is enough; a README may
  serve both a reader trying the code and an evaluator checking maturity.

## The link-aggregator launch post

Write a short author-voiced introduction that gives unfamiliar readers a reason to inspect the
code. Use "pluggable trait implementations for Rust, at compile-time" in the title rather than
relying on the paradigm name.

Open with a runnable example or a clearly labeled before-and-after. Show the problem that warrants
providers, then say when a plain trait suffices. Link to deeper material instead of reproducing it
in the submission. The next step is a quickstart or runnable example.

Plan to answer substantive questions in the discussion. The replies below provide starting points,
but each answer should address the actual question. Publication and replies are separate actions
from preparing a draft.

## The blog deep-dive

Use the author's first-person voice and give a complex explanation the space it needs. State the
reading time or scope up front and preview the sections so readers can navigate a long piece.

Develop one running example from a concrete problem. Begin with familiar Rust where possible and
introduce each CGP construct when it solves a problem the reader has seen. Show relevant generated
code before expecting readers to debug it.

Discuss costs with the same care as benefits. Name compile-time work, diagnostic difficulties,
missing behavior, and uncertainty where they matter. The
[Hypershell post](../website/blog/hypershell-release.md) provides a long-form example; length is
useful when it carries explanation rather than repetition.

## The README and project front matter

Use the project voice and make the first screen explain what CGP does. Put the settled descriptor
beneath the name, follow it with a short reassurance line, and show code early. Keep any feature
summary compact; do not make readers pass a full feature panel before reaching the example.

State that the library uses stable Rust and show installation early. Link readers trying CGP to
the quickstart and evaluators to the candid maturity discussion. Use the
[headline features](identity.md#the-headline-feature-set) for a fuller feature panel and the
[homepage guide](../website/writing-guides/homepage.md) for related layout guidance.

Check every README surface a release exposes. The repository's root README and the file selected
by a crate's `Cargo.toml` `readme` field may differ; inspect the manifest rather than assuming they
are the same. Check the package page and Rustdoc entry separately, since crate-level Rustdoc may
come from source attributes rather than the README.

Give each entry page enough substance to justify following its links. A tag line, useful code, and
a clear documentation link work better than a page that only redirects readers or dismisses its
own documentation.

## The conference talk or video

Use the author's voice to explain one central idea through a familiar problem. Establish why Rust
works as it does, show the limitation at issue, and introduce CGP's approach. Keep the example
consistent and close with the relevant limits.

Build from the [RustLab transcript](../website/blog/rustlab-2025-coherence.md) when its structure
fits. It explains coherence, considers workarounds, and develops the CGP comparison through Serde.
Use enough theory to support the argument without introducing it before the audience needs it.

Publish a transcript with the slides and recording when available. This gives readers a searchable
explanation they can follow without watching the video. Include that artifact in the preparation
plan rather than treating the recording as the only result.

## The social thread

Give a thread one concrete point and one route to the full explanation. Open with a recognizable
constraint or a small before-and-after, using familiar Rust terms. Introduce CGP's own terminology
only when it helps explain the result.

Keep the claim accurate at the shorter length. State a relevant limit and let one link carry the
detail. A thread should earn a closer reading without promising more than the linked material shows.

## The comparison or positioning piece

Describe each alternative as its users would recognize it, including where it is the better choice.
Use [related-work](../related-work/README.md) for the comparison and
[message.md](message.md#when-not-to-reach-for-cgp) for CGP's boundary.

Compare the same attributes across tools. A table works when its rows explain actual differences
and trade-offs; avoid choosing criteria solely to make CGP win. End with guidance for the reader's
case rather than a universal verdict.

Preserve the author's care with related work. Explain both the useful analogy and where it stops,
especially for concepts such as type classes, ML modules, and effects.

The website's comparison pages are the standing form of this piece, and the
[comparison page guide](../website/writing-guides/related-work.md) governs them: it fixes how an
internal related-work document is ported, above all that the document's positioning guidance is applied
as page structure rather than published, and how another community's tool is written about in public.
A comparison written for another channel follows the same rules for the compared tool.

## Titles, first lines, and search

Write each page's title and opening for someone arriving directly from a link or search result.
The reader may not have seen the homepage or an earlier tutorial. This follows the
[Every Page is Page One approach](evidence.md#sources-for-the-craft-this-section-borrows).

Use problem-oriented titles for tutorials, explanations, and posts. These examples connect a
construct to the result the reader wants:

| Construct-led title | Problem-oriented title |
| --- | --- |
| Using `#[cgp_component]` | Give one interface several implementations |
| Namespaces | Keep a growing wiring table short |
| Abstract types | Let each application choose its error type |
| Context-generic programming for library authors | Add behavior for a type you do not own |

Reference pages are the exception: use the construct name readers are looking up, then explain
its purpose in the overview's first sentence.

Orient unfamiliar readers in the first paragraph. Give a short description of CGP linked to an
introduction, then state what this page covers. Use the settled descriptor where it fits, without
repeating a long introduction on every page.

Use established problem names naturally where they apply. Terms such as "orphan rule",
"conflicting implementations", and `E0119` connect the page to the question it answers. Do not
repeat them for search ranking or claim knowledge of search traffic the project does not measure.

Qualify bridge terms such as "structural typing" when using them. CGP remains nominal and wired;
the analogy should explain a resemblance without asserting a different type system. Follow
[vocabulary.md](vocabulary.md#the-name-and-the-communitys-bridge-terms).

Write an explicit page description and blog excerpt. Use Docusaurus `description` front matter for
a concise summary, and check the excerpt above a blog post's truncate marker. Search engines may
choose a different snippet, so do not promise that the description controls every preview.
Aggregator titles follow the [launch-post guidance](#the-link-aggregator-launch-post).

## Answering in threads

Acknowledge the valid concern before explaining the difference. Adapt these responses to the
question, using [message.md](message.md#the-objections-readers-bring) for detail:

| Question | Response |
| --- | --- |
| Is this DI or over-engineering? | Ordinary traits and generics often suffice. Show the specific overlap, foreign-target, or dependency problem that motivates the example. |
| How do I tell which code runs? | Trace the wiring to the provider, including forwarding or wrappers. Concede the added indirection. |
| What about compile times and errors? | State the compile-time work without inventing a number. Show explicit checks and the toolchain on a real diagnostic. |
| Why not plain traits? | Prefer them where they solve the problem. Explain the next step using the modularity hierarchy. |
| I have only one application. | Assess present needs such as foreign targets or reusable providers. Do not invent a future second context to justify wiring. |
| Will every configuration need a context? | Separate only useful type-level distinctions. Keep runtime choices in enums or trait objects inside the context. |

Use the canonical limitation when recommending the checker:
`cargo cgp check` leads with the root cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every class.

## The conversion ladder

Match the next step to what the reader is ready to evaluate. Offer these routes:

| Reader | Next step |
| --- | --- |
| First-contact skimmer | A quickstart, runnable example, or repository |
| Working developer | A tutorial addressing their problem |
| Evaluator | Maturity, costs, incremental adoption, and a real system using CGP |
| Enthusiast | The [CGP Patterns book](https://patterns.contextgeneric.dev/) and contribution guidance |

Check that the destination supports the promise. In particular, dated examples may need version
context; do not send a newcomer to incompatible code without explaining what they will find.

## Worked model drafts

Use these drafts to study the structure, then adapt them to the intended reader. They are examples,
not approved copy. Replace placeholder destinations before publication and verify the snippets
against the source and `/cgp` skill under the
[synchronization rule](../AGENTS.md#the-synchronization-rule).

### A link-aggregator launch post

> **Pluggable trait implementations for Rust, at compile-time**
>
> Rust rejects blanket impls of the same trait for every `T: Display` and every `T: AsRef<[u8]>`:
> `String` satisfies both. Coherence makes the choice unambiguous, but sometimes I want to offer
> both implementations and let each application choose.
>
> CGP separates those implementations into provider types. In this example the value moves from
> `Self` into a `Value` parameter, while `Self` becomes the application context. The providers can
> coexist because each implements the provider trait on its own type.
>
> This fragment shows the component and provider definitions; the wiring follows below.
>
> ```rust
> use cgp::prelude::*;
> use core::fmt::Display;
>
> #[cgp_component(Encoder)]
> pub trait CanEncode<Value> {
>     fn encode(&self, value: &Value) -> Vec<u8>;
> }
>
> #[cgp_impl(new EncodeWithDisplay)]
> impl<Value: Display> Encoder<Value> {
>     fn encode(&self, value: &Value) -> Vec<u8> {
>         value.to_string().into_bytes()
>     }
> }
>
> #[cgp_impl(new EncodeBytes)]
> impl<Value: AsRef<[u8]>> Encoder<Value> {
>     fn encode(&self, value: &Value) -> Vec<u8> {
>         value.as_ref().to_vec()
>     }
> }
> ```
>
> Each application can now select an encoder for `String`. Append this wiring, checks, and entry
> point to the definitions above to run the example:
>
> ```rust
> pub struct ApiServer;
> pub struct Firmware;
>
> delegate_components! {
>     ApiServer {
>         open EncoderComponent;
>         @EncoderComponent.String: EncodeWithDisplay,
>     }
> }
>
> delegate_components! {
>     Firmware {
>         open EncoderComponent;
>         @EncoderComponent.String: EncodeBytes,
>     }
> }
>
> check_components! { ApiServer { EncoderComponent: String } }
> check_components! { Firmware { EncoderComponent: String } }
>
> fn main() {
>     let value = String::from("hello");
>     assert_eq!(ApiServer.encode(&value), b"hello".to_vec());
>     assert_eq!(Firmware.encode(&value), b"hello".to_vec());
> }
> ```
>
> These encoders return the same bytes for this string, but the applications select them
> independently. Provider selection resolves at compile time without a runtime container or
> vtable lookup.
>
> This adds declarations and wiring. For a single implementation, I would use a plain trait.
> Providers become useful when interchangeable implementations or reuse justify them. CGP also
> adds compile-time work and concepts to learn, and raw wiring errors can be verbose.
>
> CGP is a library on stable Rust, so you can try one component before deciding whether it belongs
> in more of your code.
>
> Try the quickstart: [insert quickstart link].

The opening names a Rust restriction and explains why it exists. The code then changes the
implementation arrangement, with the move from value `Self` to environmental context stated
explicitly. Both contexts check their wiring. The close states costs and asks only for a small trial.

Keep the example's scope when adapting it. It demonstrates separate provider choices, not a repeal
of Rust's coherence rules or a claim that both bodies produce different results for every input.
The [message example](message.md#the-problems-cgp-removes) supplies the rejected ordinary-Rust code
when the format has room for a full before-and-after.

### A README above the fold

> **Context-Generic Programming**
>
> A language extension for Rust, with pluggable trait implementations at compile-time.
>
> A library on stable Rust, adopted one component at a time. Install it with `cargo add cgp`.
>
> This example selects a greeting provider for `Person` and checks that the context supplies the
> field the provider needs:

```rust
use cgp::prelude::*;

#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self) -> String;
}

#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self, #[implicit] name: &str) -> String {
        format!("Hello, {name}!")
    }
}

#[derive(HasField)]
pub struct Person {
    pub name: String,
}

delegate_components! { Person { GreeterComponent: GreetHello } }
check_components! { Person { GreeterComponent } }

fn main() {
    let person = Person { name: "World".to_owned() };
    println!("{}", person.greet()); // Hello, World!
}
```

> A plain trait would be enough for this greeting alone. CGP providers are useful when applications
> need interchangeable implementations or want to reuse and compose them. The trade-offs include
> more declarations, compile-time work, and a learning curve; raw diagnostics can also be verbose.
>
> [Insert quickstart link] · [Insert maturity discussion link]

The descriptor, installation, and code give an unfamiliar reader a concrete starting point. This
is a self-targeted component on a value context, `Person`. The limitation prevents the small example
from implying that every greeting needs a component. A fuller README can follow it with the
[canonical feature panel](identity.md#the-headline-feature-set).

### A social thread

> **1/** Rust rejects blanket impls of the same trait for every `T: Display` and every
> `T: AsRef<[u8]>`, because `String` satisfies both. Sometimes an application needs to choose
> between those implementations explicitly.

> **2/** CGP gives each implementation a separate provider type. An application selects a provider
> through wiring, and Rust resolves that selection at compile time. Another application can make
> a different choice for the same target type.

> **3/** It is a library on stable Rust, so you can try one component. Keep a plain trait where one
> implementation is enough: CGP adds declarations, compile-time work, and concepts to learn.
> The example and its diagnostic costs are here: [insert example link].

The thread states one constraint, explains the alternate arrangement, and names the cost. One link
carries the detail. It uses ordinary Rust vocabulary before introducing the provider terminology.

### Adapting these

Change the motivating problem to fit the dominant [reader](readers.md). A foreign target may suit
a library author, an abstract error type a systems programmer, and trait decomposition an evaluator.
Keep the settled descriptor while changing the example that earns the reader's attention.

Preserve the fair explanation of Rust, the relevant cost, and verified code in every adaptation.
Add new worked drafts here when a distinct format needs one, using the same pattern: example copy
followed by a short explanation of its choices.
