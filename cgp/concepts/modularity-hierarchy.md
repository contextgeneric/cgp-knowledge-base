# Modularity hierarchy

CGP and vanilla Rust together form a ladder of modularity: each rung allows strictly more independent implementations of one interface than the rung below, by loosening a coherence constraint at a matching cost in syntax or coupling, so the right rung is the lowest one that still expresses what a use case needs.

## A ladder, not a switch

Adopting CGP is not an all-or-nothing jump from ordinary Rust traits to fully context-generic code. The same capability — say, serializing a value — can be expressed at several levels of modularity, and the levels form a gradient from "exactly one implementation, no wiring" to "any number of implementations, wired per type per provider." Each step up admits more overlapping or orphan implementations that vanilla Rust's [coherence](coherence.md) rules would reject, and each step costs something: more boilerplate, a changed interface, or tighter coupling between providers. Reading the rungs in order shows what each technique buys and what it asks for, so a use case can settle at the lowest rung that still works rather than reaching for the most powerful tool by default.

The ladder is illustrated throughout with one running capability — serializing a value, mirroring the [modular serialization](../../examples/modular-serialization.md) example — so the only thing that changes between rungs is the modularity technique, not the problem. All snippets assume `use cgp::prelude::*;`.

## What actually varies: the context and the target

Two independent questions decide which rung a capability sits on, and naming them before the rungs makes the whole ladder legible — because the rung numbers describe *consequences*, while these two questions describe the *causes*.

**What is the `Self` type?** It is either a **value context** — the data the capability operates on, such as the `Vec<u8>` being serialized — or an **environmental context**, a type that exists to supply choices and capabilities rather than to be operated on, such as an application. Both are contexts in the ordinary CGP sense: both sit in the `Self` position and both carry a wiring table. They differ in what they *are*, and the difference decides how much freedom the wiring has.

**What does the capability target?** It is either **self-targeted**, meaning the capability is about the `Self` type — `CanEncode`, `CanGreet`, `HasErrorType` — or **parameter-targeted**, meaning it is about a type parameter while `Self` only decides — `CanEncodeValue<Value>`, `CanSerializeValue<Value>`, `CanCalculateArea<Shape>`. A parameter is not automatically a target: in `CanCompute<Code, Input>` the target is `Input` and `Code` is a *selector* the wiring dispatches on, and a component may carry both. The test is which type the capability acts on, not whether a parameter is present.

Crossed, the two questions describe three shapes that occur in practice, and one that does not earn its keep.

| Shape | `Self` is | Targets | Independent choices available | Rung |
|---|---|---|---|---|
| **Retrofit** | a value context | `Self` | one per value type, program-wide | 3 |
| **Application** | an environmental context | `Self` | one per context you define | 3 |
| **Fully modular** | an environmental context | a parameter | one per context, per target type | 4–5 |

A value context with a target parameter is legal and uninteresting, since the capability would be about one type while being wired on another for no gain.

### Why the qualifications are needed at all

**Vanilla Rust idiomatically supports exactly one of these three shapes, which is why it never needed the vocabulary — and why CGP does.** The distinctions are not terminology CGP invented for its own sake; they are the names of choices that only become choices once alternatives are viable.

The **retrofit** shape is what every ordinary Rust trait is: `impl Display for String`, `impl Iterator for Chars`. The data is `Self`, the capability is about it, and coherence gives it exactly one implementation. This shape is so dominant that a Rust programmer has no reason to notice it *is* a shape.

The **application** shape is legal and does occur — `impl Handler for MyApp` — but vanilla Rust gives it no leverage. Each application type must write its own method bodies, because the moment two implementations are factored into blanket impls they overlap:

```rust
impl<T: HasSmtpConfig>      CanSendEmail for T { /* ... */ }
impl<T: HasRecordedEmails>  CanSendEmail for T { /* ... */ }   // error[E0119]
```

So the shape survives but nothing can be shared, and it never becomes a *modularity* technique.

The **fully modular** shape is legal too, and this surprises people: a parameter-targeted trait implemented on an application type compiles perfectly well in vanilla Rust.

```rust
pub trait CanEncodeValue<Value> {
    fn encode(&self, value: &Value) -> Vec<u8>;
}

impl CanEncodeValue<Vec<u8>> for ApiServer { /* hex */ }
impl CanEncodeValue<Vec<u8>> for Firmware  { /* raw bytes */ }
```

Two application types, the same value type, different encodings — with no CGP at all. What fails is reuse: every `(context, target type)` pair needs its own hand-written body, and factoring one into `impl<V: Display> CanEncodeValue<V> for ApiServer` collides with any sibling. The shape is therefore available and unrewarding, which is why almost nobody writes it and why "application context" tends to land on a reader as an unfamiliar noun rather than a familiar arrangement.

**CGP's contribution is not that it legalizes these shapes — two of the three are already legal — but that it makes the implementations reusable, which is what turns each shape into a technique.** Named providers replace hand-written bodies, so a per-pair decision becomes a wiring line. Once all three shapes are worth using, a reader has to be able to say which one they are in, and that is what the qualifiers are for.

### Which restriction each shape escapes

The most consequential thing the two axes reveal is that **the escape from coherence happens when `Self` becomes a type you own, not when a parameter appears**. This is easy to miss, because the parameter is the visible change.

At the retrofit shape the wired type is data you often do not own, so coherence still binds: `Vec<u8>` gets one wiring for the whole program, and no amount of provider machinery changes that. At the application shape `Self` is a type you define, so when one wiring per type is not enough you simply define another type — which is why `App` and `TestApp` can each choose their own `CanSendEmail` provider with no parameter anywhere. The fully modular shape then extends that same freedom to target types you do *not* own, which is the only thing the parameter adds.

That ordering matters when explaining the ladder, because it means the application shape is the common case rather than a way-station, and the parameter is a response to a specific need rather than the point.

## Rung 1 — one implementation per interface

The least modular rung is a generic function or a blanket trait impl, which allows exactly one implementation of the interface it defines. A blanket impl over a generic type captures a single piece of logic that applies everywhere the bound holds, and there can be only one such impl:

```rust
pub trait CanSerializeBytes {
    fn serialize_bytes<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error>;
}

impl<Value: AsRef<[u8]>> CanSerializeBytes for Value {
    fn serialize_bytes<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_bytes(self.as_ref())
    }
}
```

A blanket trait is preferred over a bare generic function because it hides the `AsRef<[u8]>` bound behind a clean interface rather than leaking it to every transitive caller — the [impl-side dependency](impl-side-dependencies.md) idea in its simplest form. The limitation is absolute, though: this is the *only* way `CanSerializeBytes` is ever implemented. There is no room for a second strategy, so this rung fits a capability that genuinely has one implementation for all types, and nothing more.

## Rung 2 — one implementation per type

Vanilla Rust traits climb one rung by allowing a different implementation for each type, while coherence still permits at most one implementation per type. This is the everyday Rust trait, where `Vec<u8>` and `&[u8]` can each implement `Serialize` their own way:

```rust
impl Serialize for Vec<u8> {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_bytes(self.as_ref())
    }
}

impl<'a> Serialize for &'a [u8] {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_bytes(self)
    }
}
```

The gain over rung 1 is per-type variation; the cost is that each type needs its own explicit impl even when several share logic, and the [overlap rule](coherence.md) forbids any blanket impl that would collide. Reusable building blocks can still be factored out — both bodies above could call the rung-1 `serialize_bytes` — but the trait itself admits no alternatives: once `Serialize for Vec<u8>` is chosen, that choice is global and final. This is where Rust's coherence guarantee delivers its value and also where it starts to bind: a type gets exactly one implementation of a trait, no matter what a particular application would prefer.

## Rung 3 — many implementations, one wiring per type

The first CGP rung keeps the type in the `Self` position but splits the trait into a consumer/provider pair, so many overlapping implementations can coexist as named providers while each type still commits to one of them globally. The component is therefore **self-targeted**, which the names below say out loud — `CanSerializeSelf` here against the `CanSerializeValue<Value>` of rung 4, which is a *different* component rather than a revision of this one. Applying [`#[cgp_component]`](../reference/macros/cgp_component.md) to the trait and writing providers with [`#[cgp_impl]`](../reference/macros/cgp_impl.md) lets `SerializeSelfAsBytes` and a `Serialize`-deferring `UseSerdeForSelf` both exist, overlapping freely on any type that is both `AsRef<[u8]>` and `Serialize`:

```rust
#[cgp_component(SelfSerializer)]
pub trait CanSerializeSelf {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error>;
}

#[cgp_impl(new SerializeSelfAsBytes)]
#[uses(AsRef<[u8]>)]
impl SelfSerializer {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        serializer.serialize_bytes(self.as_ref())
    }
}
```

A type then picks one provider with a [`delegate_components!`](../reference/macros/delegate_components.md) entry — `Vec<u8>` becomes its own context, wiring its serializer component to `SerializeSelfAsBytes`:

```rust
delegate_components! {
    Vec<u8> {
        SelfSerializerComponent: SerializeSelfAsBytes,
    }
}
```

This rung's advantage is backward compatibility: the original trait is extended without changing its interface, a type can still implement it directly, and many reusable providers replace the hand-copied logic of rung 2. Its limitation is that coherence is only partly lifted. The wiring still keys on the type in the `Self` position, so `Vec<u8>` commits to one provider globally — there can be no separate wiring for a generic `Vec<T>` that would overlap it, and the [orphan rule](coherence.md) still applies, since `delegate_components!` for `Vec<u8>` must live in a crate that owns either the trait or `Vec`.

### The rung holds two shapes, and only one of them is limited

**How binding that limitation is depends entirely on whether the `Self` type is a value context or an environmental one**, and this rung contains both — which is why it is the rung most often misread.

Wired on a **value context**, the limitation bites exactly as described. `Vec<u8>` is data, it is not yours, and one wiring is all you get; this is the **retrofit** shape, and it is the right choice when a capability genuinely belongs to the data or when an existing trait's signature cannot be changed.

Wired on an **environmental context**, the same rung behaves very differently, because the constraint "one wiring per type" stops being a constraint when you control how many types there are. The capability there is about the application rather than about data — `CanSendEmail` rather than `CanSerializeSelf` — so the component is still self-targeted and still on this rung. `App` and `TestApp` are both yours, so each wires its own provider and the same capability resolves differently in production and in tests:

```rust
delegate_components! { App     { EmailSenderComponent: SendViaSmtp } }
delegate_components! { TestApp { EmailSenderComponent: RecordEmails } }
```

No parameter is involved, and nothing has been worked around. This is the **application** shape, and it is where most CGP code lives: a capability about the application itself — send an email, query a user, run the server — wired per application. Reading rung 3 as merely "the retrofit rung" therefore undersells it substantially, and reading rung 4 as the first rung with per-application choice is simply wrong.

## Rung 4 — many implementations, one wiring per type per context

This rung moves the type being implemented out of `Self` and into an explicit parameter, so the `Self` position is always an environmental context — which lifts the orphan rule and lets each context choose providers **per target type** independently. What it adds over the application shape of rung 3 is precise and worth stating narrowly: rung 3 already lets each context you define make its own choice, so what rung 4 buys is the ability to make that choice **about types you do not own**. The trait gains a `Value` parameter, leaving `Self` free to be any application context:

```rust
#[cgp_component(ValueSerializer)]
pub trait CanSerializeValue<Value: ?Sized> {
    fn serialize<S>(&self, value: &Value, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer;
}
```

Now two application contexts can serialize the *same* type differently, each coherent within itself, by opening the component and keying on the value type — `AppA` encoding `Vec<u8>` as hexadecimal where `AppB` uses base64:

```rust
delegate_components! {
    AppA {
        open ValueSerializerComponent;
        @ValueSerializerComponent.Vec<u8>: SerializeHex,
    }
}

delegate_components! {
    AppB {
        open ValueSerializerComponent;
        @ValueSerializerComponent.Vec<u8>: SerializeBase64,
    }
}
```

This rung nearly eliminates the coherence restrictions. Because the wiring keys on the context rather than on `Vec<u8>`, a crate that owns neither the trait nor `Vec` can still wire a serializer for `Vec<u8>` as long as it owns the context, so the orphan rule no longer bites and overlapping providers coexist without any global commitment. The cost is that the trait must be designed with the extra context parameter from the start — it cannot be retrofitted onto an existing trait like `serde::Serialize` without a breaking change — and wiring must be spelled out for every value type a context uses. This is the rung most idiomatic CGP code lives on, and the one the [modular serialization](../../examples/modular-serialization.md) and [money-transfer API](../../examples/money-transfer-api.md) examples build on; the per-type dispatch it relies on is the subject of [dispatching](dispatching.md), wired through the [`open` statement](../reference/macros/delegate_components.md) over [namespaces](namespaces.md).

## Rung 5 — many implementations, wiring per type per provider

The top rung lets one provider override the wiring of a nested type locally, without routing that choice back through the context, by taking the inner provider as a parameter — a [higher-order provider](higher-order-providers.md). A recursive serializer for a collection ordinarily asks the context how to serialize each element; a higher-order variant instead accepts an explicit element serializer, defaulting to the context only when none is given:

```rust
pub struct SerializeIteratorWith<Provider = UseContext>(pub PhantomData<Provider>);

#[cgp_impl(SerializeIteratorWith<Provider>)]
impl<Value, Provider> ValueSerializer<Value>
where
    for<'a> &'a Value: IntoIterator,
    Provider: for<'a> ValueSerializer<Self, <&'a Value as IntoIterator>::Item>,
{
    fn serialize<S>(&self, value: &Value, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    { /* serialize each item through `Provider` */ }
}
```

With this in hand a context can fix the element encoding for one collection while leaving others to the context's general wiring — serializing a `Vec<Vec<u8>>` whose inner byte vectors are hexadecimal even though plain `Vec<u8>` elsewhere is encoded as raw bytes:

```rust
delegate_components! {
    AppA {
        open ValueSerializerComponent;
        @ValueSerializerComponent.Vec<u8>: SerializeBytes,
        @ValueSerializerComponent.Vec<Vec<u8>>: SerializeIteratorWith<SerializeHex>,
        @ValueSerializerComponent.Vec<u64>: SerializeIteratorWith,
    }
}
```

This rung adds fine-grained, per-provider control on top of rung 4's per-context control: the `Vec<u64>` entry omits the parameter and so still routes its elements through the context, while the `Vec<Vec<u8>>` entry pins its inner encoding to `SerializeHex` regardless of how the context serializes `Vec<u8>` on its own. The `UseContext` default is what makes both forms read the same; the [`UseContext` provider](../reference/providers/use_context.md) routes back to the context's wiring when no override is supplied. The cost is the extra coupling and the higher-order machinery, which is why this rung is reserved for the cases where local override genuinely matters rather than used by default.

## Choosing a rung

The guiding rule is to settle at the lowest rung that expresses the use case, because each step up trades simplicity for modularity that may not be needed. A capability with one universal implementation belongs on rung 1; one that varies by type but never by application belongs on rung 2; a trait that should gain alternative providers without changing its interface belongs on rung 3 in its retrofit shape; a capability *about the application itself* belongs on rung 3 in its application shape, which is where most CGP code lives; a capability where different applications must treat the same foreign type differently belongs on rung 4; and only a provider that must override a nested type's wiring locally needs rung 5. Climbing higher than necessary adds context parameters, wiring, and coupling that buy nothing, while stopping too low forces the hand-written impls and global commitments the higher rungs exist to avoid.

Two questions settle it faster than walking the rungs. **Is the capability about the data, or about the application?** About the data means a value context and the retrofit shape; about the application means an environmental context. **Does the capability concern a type you do not own, and must different applications treat it differently?** If yes, the target moves into a parameter and you are on rung 4; if no, self-targeting is enough. Each shape is the right answer to a different question rather than a different amount of sophistication, which is why none of them is a stepping stone to be outgrown.

This document is descriptive; the prescriptive companion is [choosing a component's shape](../guides/choosing-a-component-shape.md), which carries the default to reach for, the cost of each alternative, the refactoring that promotes a self-targeted component to a parameter-targeted one, and the two traps — that a parameter is not always a target, and that per-application choice needs no parameter at all.

## Related constructs

The mechanism that makes rungs 3 through 5 possible — splitting a trait into a [consumer and provider trait](consumer-and-provider-traits.md) so overlapping and orphan implementations become legal — is the subject of [bypassing coherence](coherence.md), and the dependency threading every rung relies on is [impl-side dependencies](impl-side-dependencies.md). The constructs the rungs introduce are [`#[cgp_component]`](../reference/macros/cgp_component.md) and [`#[cgp_impl]`](../reference/macros/cgp_impl.md) for the trait split, [`delegate_components!`](../reference/macros/delegate_components.md) for the wiring, the [`open` statement](../reference/macros/delegate_components.md) over [namespaces](namespaces.md) and the [dispatching](dispatching.md) idea for per-type selection, and [higher-order providers](higher-order-providers.md) with the [`UseContext` provider](../reference/providers/use_context.md) for the top rung. The whole progression is worked through on a real capability in the [modular serialization](../../examples/modular-serialization.md) example.
