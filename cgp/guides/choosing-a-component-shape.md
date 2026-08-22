# Choosing a component's shape

When you define a component you decide two things about it before you write a line of its body — what goes in the `Self` position, and whether the capability is about `Self` or about a type parameter — and this guide is about making that choice deliberately rather than by copying whichever example you read last.

The decision matters because it fixes how many independent choices the wiring can ever express, and because it cannot be revised later without a breaking change to the trait. It is also the decision most likely to be made by accident: the two arrangements look almost identical in a snippet, so an author who patterns a new component after a tutorial usually inherits the tutorial's shape without noticing there was an alternative.

## Default to a capability about the application

**Start by asking what the capability is *about*, and default to the answer "the application".** Most capabilities in a real program — send an email, query a user, run the server, load the config — are things the application does, so the natural `Self` is a type standing for the application and the capability targets that `Self`. This is the shape most CGP code is in, it needs no type parameter, and it already gives per-application choice:

```rust
#[cgp_component(EmailSender)]
pub trait CanSendEmail {
    fn send_email(&self, to: &str, body: &str);
}

#[cgp_impl(new SendViaSmtp)]
impl EmailSender { /* connect and send over SMTP */ }

#[cgp_impl(new RecordEmails)]
impl EmailSender { /* push to a Vec so a test can assert on it */ }

delegate_components! { App     { EmailSenderComponent: SendViaSmtp } }
delegate_components! { TestApp { EmailSenderComponent: RecordEmails } }
```

`App` and `TestApp` are **environmental contexts** — types whose job is to carry choices and whatever data the providers need, frequently no data at all, so `pub struct App;` is a complete context. Because both are types you define, "one wiring per type" is not a limit: when one choice is not enough you define a second context. Reach for a parameter only when this shape genuinely cannot express the case, which the two sections below identify.

## Reach for a value context when the capability belongs to the data

Put the data in `Self` when the capability really is a property of the data rather than of the application — computing a shape's area, formatting a value — or when you are adding alternatives to an existing trait whose signature you cannot change. The wired type is then a **value context**, and the component is still self-targeted:

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

delegate_components! { Rectangle { AreaCalculatorComponent: RectangleArea } }
```

The cost is the one thing this shape cannot do: **the wired type gets one provider for the whole program.** That is fine for `Rectangle`, which you own and which has one sensible area. It is a real constraint for a foreign type — `Vec<u8>` wired to one encoder cannot be encoded differently by two applications, and the [orphan rule](../concepts/coherence.md) additionally requires the `delegate_components!` entry to live in a crate owning either the trait or the type. Choose this shape knowing that limit, not by inheriting it.

## Move the target into a parameter when the type is not yours

**Add a `Value` parameter when the capability is about a type you do not own *and* different applications must treat it differently.** That combination is the only thing the parameter buys; if either half is missing, the shapes above are simpler and sufficient.

Serialization is the canonical case: the encoded types are foreign, and two services genuinely need the same `Vec<u8>` sent as hexadecimal by one and base64 by the other. Making the component **parameter-targeted** leaves `Self` free to be an application:

```rust
#[cgp_component(Encoder)]
pub trait CanEncodeValue<Value> {
    fn encode(&self, value: &Value) -> Vec<u8>;
}
```

The cost is threefold and worth weighing rather than accepting silently. The trait must be designed this way from the start, since adding the parameter later breaks every caller. Every value type a context touches needs a wiring entry, which grows tedious and is what [namespaces](namespaces-and-prefixes.md) exist to shorten. And providers become slightly harder to read, because the value arrives as an argument rather than as `self`.

## The refactoring, worked

Promoting a self-targeted component to a parameter-targeted one is mechanical once the decision is made, and seeing it done shows exactly what changes. Start from the self-targeted form, wired on the values themselves:

```rust
#[cgp_component(Encoder)]
pub trait CanEncode {
    fn encode(&self) -> Vec<u8>;
}

#[cgp_impl(new EncodeAsText)]
#[uses(Display)]
impl Encoder {
    fn encode(&self) -> Vec<u8> { self.to_string().into_bytes() }
}

delegate_components! { String { EncoderComponent: EncodeAsText } }
```

Four things change together, and none of them can be done alone. The **trait gains the parameter** and its method takes the value as an argument. The **provider's bound moves off `Self`** and onto that parameter — which means it stops being an [`#[uses]`](../reference/attributes/uses.md) import, since `#[uses]` adds `Self:` predicates and the constraint is now on `Value`, so it returns to an explicit `where` clause. The **body reads `value` instead of `self`**. And the **wiring moves to a context you define**, keyed per value type with the [`open` statement](../reference/macros/delegate_components.md):

```rust
#[cgp_component(Encoder)]
pub trait CanEncodeValue<Value> {
    fn encode(&self, value: &Value) -> Vec<u8>;
}

#[cgp_impl(new EncodeAsText)]
impl<Value> Encoder<Value>
where
    Value: Display,
{
    fn encode(&self, value: &Value) -> Vec<u8> { value.to_string().into_bytes() }
}

#[cgp_impl(new EncodeAsBytes)]
impl<Value> Encoder<Value>
where
    Value: AsRef<[u8]>,
{
    fn encode(&self, value: &Value) -> Vec<u8> { value.as_ref().to_vec() }
}

pub struct ApiServer;
pub struct Firmware;

delegate_components! {
    ApiServer {
        open EncoderComponent;
        @EncoderComponent.String: EncodeAsText,
    }
}

delegate_components! {
    Firmware {
        open EncoderComponent;
        @EncoderComponent.String: EncodeAsBytes,
    }
}
```

The payoff is the last two blocks: `ApiServer` and `Firmware` encode the same `String` differently, which the self-targeted version could not express at any price. What did *not* change is worth noting too — the providers are the same two implementations with the same bounds, so the refactoring moves the choice rather than rewriting the logic.

## Two traps

**A type parameter does not make a component parameter-targeted.** The target is the type the capability *acts on*; a parameter may instead be a **selector** the wiring dispatches on. In [`CanCompute<Code, Input>`](../reference/components/computer.md) the target is `Input` while `Code` selects which computation runs, and [`CanRaiseError<SourceError>`](../reference/components/can_raise_error.md) dispatches on the source error. A component may carry both kinds at once, so count the roles rather than the parameters.

**Do not climb to a parameter to get per-application choice**, which is the most common over-application of this decision. Per-application choice comes from the wired type being a type you define, so the self-targeted shape on an environmental context already has it. The parameter is for foreign *target* types, and reaching for it earlier buys wiring entries and a harder-to-read provider for nothing.

## Related guides

- [Sizing a component](sizing-a-component.md) — the companion decision: how many methods the component carries, once you know what it is about.
- [Writing providers](writing-providers.md) — the `#[cgp_impl]` header each shape uses, once the shape is chosen.
- [Declaring a provider's dependencies](declaring-dependencies.md) — why a `Self` bound is an `#[uses]` import while a bound on the target parameter stays an explicit `where` clause.
- [Organizing wiring with namespaces and prefixes](namespaces-and-prefixes.md) — how to keep a parameter-targeted component's per-type entries from overwhelming a context's table.
- [Modularity hierarchy](../concepts/modularity-hierarchy.md) — the concept behind this decision: the five tiers, the two axes, and why vanilla Rust idiomatically supports only one of the three shapes.
- [Guides summary](README.md#summary) — the cheat-sheet across all the guides.
