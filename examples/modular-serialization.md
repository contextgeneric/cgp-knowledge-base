# Modular serialization

This example uses [cgp-serde](../projects/cgp-serde/README.md), which rebuilds Serde's `Serialize` and
`Deserialize` as CGP components, so that how each value type is encoded becomes a per-application
wiring choice rather than a single fixed implementation baked into the type. It progresses from the two
serialization components, through the family of overlapping providers the library ships, to two
application contexts that serialize the same nested data into different JSON formats by changing only a
handful of wiring lines, and finally to a deserializer that allocates into an arena the context
supplies. It is the template for any trait where the same type needs several interchangeable
implementations chosen per application, and where the orphan rule would otherwise force a library to
derive the trait on every data type itself.

The concepts each step demonstrates are documented in full elsewhere; this example notes which one is
in play and links to it:

- splitting a trait so overlapping and orphan implementations are legal — [consumer and provider traits](../cgp/concepts/consumer-and-provider-traits.md) and the [coherence](../cgp/concepts/coherence.md) strategy behind it
- the two components and why the value leaves `Self` — [cgp-serde's component design](../projects/cgp-serde/architecture/component-design.md)
- providers that hand nested values back to the context — [re-entrant providers](../projects/cgp-serde/architecture/reentrant-providers.md)
- serializing a struct with no serialization-specific derive — [extensible records](../cgp/concepts/extensible-records.md) via [`#[derive(CgpData)]`](../cgp/reference/derives/derive_cgp_data.md), and cgp-serde's [record providers](../projects/cgp-serde/reference/records.md)
- selecting a provider per value type, inline in the context's own table — the `open` statement of [`delegate_components!`](../cgp/reference/macros/delegate_components.md)
- verifying a context's wiring — [`check_components!`](../cgp/reference/macros/check_components.md)
- pulling a service from the context during deserialization — cgp-serde's [context services](../projects/cgp-serde/architecture/context-services.md), with the [`HasErrorType`](../cgp/reference/components/has_error_type.md) and [`CanRaiseError`](../cgp/reference/components/can_raise_error.md) error components wired through [modular error handling](../cgp/concepts/modular-error-handling.md)

The snippets assume `use cgp::prelude::*;` and compile against the `v0.8.0` branch of
[cgp-serde](https://github.com/contextgeneric/cgp-serde/tree/v0.8.0), using its `cgp-serde`,
`cgp-serde-extra`, `cgp-serde-json`, `cgp-serde-alloc`, and `cgp-serde-typed-arena` crates. The imports
each section needs are shown where it first needs them.

## The two serialization components

The starting point is a context-generic restatement of Serde's two traits, which cgp-serde defines in
`cgp_serde::components`. Each moves the type being serialized out of the `Self` position, where Serde
keeps it, and into an explicit `Value` parameter, leaving `Self` to name a **context** that carries the
wiring:

```rust
#[cgp_component(ValueSerializer)]
pub trait CanSerializeValue<Value: ?Sized> {
    fn serialize<S>(&self, value: &Value, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer;
}

#[cgp_component(ValueDeserializer)]
pub trait CanDeserializeValue<'de, Value> {
    fn deserialize<D>(&self, deserializer: D) -> Result<Value, D::Error>
    where
        D: serde::Deserializer<'de>;
}
```

`CanSerializeValue` and `CanDeserializeValue` are the [consumer traits](../cgp/concepts/consumer-and-provider-traits.md)
callers use as `context.serialize(value, s)`; `ValueSerializer` and `ValueDeserializer` are the provider
traits implementations are written against. The extra `&self` is the whole point: it gives every
implementation access to the context, both to ask how nested values are encoded and, for
deserialization, to pull runtime services out of it. The library's definitions also carry a legacy
`#[derive_delegate]` attribute that this example does not need; see
[the components](../projects/cgp-serde/reference/components.md).

Both components are therefore **parameter-targeted**, and every context in this example is an
**environmental context**, the shape the [modularity hierarchy](../cgp/concepts/modularity-hierarchy.md)
places on tier 4. The example starts there rather than working up to it because serialization is the
case that genuinely needs it: the encoded types are foreign, so a self-targeted component would give
`Vec<u8>` one encoding for the whole program, and the two-applications payoff below would be
impossible.

## Overlapping providers

With the type moved off `Self`, several implementations of the same component can coexist even though
they overlap. Each is written for its own zero-sized provider struct, which the defining crate owns, so
the [coherence](../cgp/concepts/coherence.md) rules never apply. cgp-serde ships such a family in
`cgp_serde::providers`, and their headers show the overlap:

```rust
#[cgp_impl(UseSerde)]
impl<Value> ValueSerializer<Value>
where
    Value: serde::Serialize,
{ ... }

#[cgp_impl(SerializeBytes)]
impl<Value> ValueSerializer<Value>
where
    Value: AsRef<[u8]>,
{ ... }

#[cgp_impl(new SerializeWithDisplay)]
#[uses(CanSerializeValue<String>)]
impl<Value> ValueSerializer<Value>
where
    Value: core::fmt::Display,
{ ... }
```

`UseSerde` defers to a type's existing Serde impl, `SerializeBytes` writes any byte container as bytes,
and `SerializeWithDisplay` formats any `Display` value and serializes the resulting string. A `String`
satisfies all three bounds, so as blanket `Serialize` impls any two would be rejected; as named
providers they are simply entries a context may choose between. `SerializeWithDisplay` also shows the
second property the design depends on: it does not decide how the string is written, but asks the
context through the `CanSerializeValue<String>` dependency its `#[uses]` declares. The full family is
listed in the [provider table](../projects/cgp-serde/reference/README.md#serialization-and-deserialization-providers).

## Encodings that call back into the context

The providers that make the two applications differ live in `cgp_serde_extra::providers`. `SerializeHex`
and `SerializeBase64` encode bytes as text, `SerializeRfc3339Date` and `SerializeTimestamp` encode a
`DateTime<Utc>` as a string or a Unix timestamp, and each converts to an intermediate value that it
serializes through the context, so the final representation of that string or number is itself a
wiring choice:

```rust
#[cgp_impl(SerializeHex)]
#[uses(CanSerializeValue<String>)]
impl<Value> ValueSerializer<Value>
where
    Value: hex::ToHex,
{ ... }

#[cgp_impl(SerializeTimestamp)]
#[uses(CanSerializeValue<i64>)]
impl ValueSerializer<DateTime<Utc>> { ... }
```

Each also implements the deserializing direction on the same struct, so a context that wires `Vec<u8>`
to `SerializeHex` reads hex back with the same entry; see the [encodings](../projects/cgp-serde/reference/encodings.md).
Writing a provider of your own follows the same shape, as
[writing a provider](../projects/cgp-serde/guides/writing-a-provider.md) shows.

## Serializing collections and structs

Two recursive providers handle composite values by serializing each part through the context, so
customization reaches arbitrarily deep without any provider knowing the concrete shape.
`SerializeIterator` serializes any iterable as a sequence, asking the context how to serialize each
item, and `SerializeFields` serializes any struct as a map by walking its fields:

```rust
#[cgp_impl(new SerializeIterator)]
impl<Value> ValueSerializer<Value>
where
    for<'a> &'a Value: IntoIterator,
    Self: for<'a> CanSerializeValue<<&'a Value as IntoIterator>::Item>,
{ ... }

#[cgp_impl(new SerializeFields)]
impl<Value> ValueSerializer<Value>
where
    Value: HasFields,
    Value::Fields: FieldsSerializer<Self, Value>,
{ ... }
```

Each item and each field is handed to Serde wrapped with the context in a `SerializeWithContext`, so it
re-enters the context's wiring; [re-entrant providers](../projects/cgp-serde/architecture/reentrant-providers.md)
explains the mechanism. `SerializeFields` is available because the struct derives
[`CgpData`](../cgp/reference/derives/derive_cgp_data.md) and so exposes its fields through
[`HasFields`](../cgp/reference/traits/has_fields.md). This is the payoff for the orphan rule: a data type
needs no serialization-specific derive and no dependency on `serde` or cgp-serde at all, so a library
never has to implement a serialization trait on types it owns just because a downstream application
wants to encode them; see [derive-free records](../projects/cgp-serde/architecture/derive-free-records.md).

## The data types

The demo serializes a small tree of encrypted-messaging types, each carrying a byte field or a
`DateTime` whose encoding the applications will want to control. Their only derive is `CgpData`:

```rust
use chrono::{DateTime, Utc};

#[derive(CgpData)]
pub struct EncryptedMessage {
    pub message_id: u64,
    pub author_id: u64,
    pub date: DateTime<Utc>,
    pub encrypted_data: Vec<u8>,
}

#[derive(CgpData)]
pub struct MessagesByTopic {
    pub encrypted_topic: Vec<u8>,
    pub messages: Vec<EncryptedMessage>,
}

#[derive(CgpData)]
pub struct MessagesArchive {
    pub decryption_key: Vec<u8>,
    pub messages_by_topics: Vec<MessagesByTopic>,
}
```

## Wiring an application context

A context turns the pile of overlapping providers into one coherent scheme by choosing, per value type,
which provider runs. The `open` statement in [`delegate_components!`](../cgp/reference/macros/delegate_components.md)
opens the serialization component for per-type wiring directly in the context's own table; after it,
an `@ValueSerializerComponent.<Type>: <Provider>` entry assigns a provider to each value type the
archive touches.

`AppA` is a unit struct with no fields, and that is complete rather than a placeholder: an
environmental context's whole job is to be a name the wiring table hangs off, so it carries data only
when a provider needs data from it, as `App<'a>` does for the arena in the deserialization section
below.

```rust
use cgp_serde::components::ValueSerializerComponent;
use cgp_serde::providers::{SerializeDeref, SerializeFields, SerializeIterator, UseSerde};
use cgp_serde_extra::providers::{SerializeHex, SerializeRfc3339Date};

pub struct AppA;

delegate_components! {
    AppA {
        open ValueSerializerComponent;

        @ValueSerializerComponent.<'a, T> &'a T:
            SerializeDeref,
        @ValueSerializerComponent.[
            u64,
            String,
        ]:
            UseSerde,
        @ValueSerializerComponent.Vec<u8>:
            SerializeHex,
        @ValueSerializerComponent.DateTime<Utc>:
            SerializeRfc3339Date,
        @ValueSerializerComponent.[
            Vec<EncryptedMessage>,
            Vec<MessagesByTopic>,
        ]:
            SerializeIterator,
        @ValueSerializerComponent.[
            MessagesArchive,
            MessagesByTopic,
            EncryptedMessage,
        ]:
            SerializeFields,
    }
}
```

Reading the table top to bottom: a borrowed value routes to `SerializeDeref`, which forwards to the
value behind the reference and is needed because `SerializeIterator` yields references; the scalar
types fall back to plain Serde, which also writes the string `SerializeHex` produces; `Vec<u8>` is
encoded as hexadecimal, `DateTime<Utc>` as an RFC 3339 string, the collections as sequences, and the
structs as maps. Because the byte and date entries are the only ones that fix a *format*, a second
application differs in only a few lines: base64 instead of hex, Unix timestamps instead of RFC 3339,
plus an `i64` entry, because `SerializeTimestamp` serializes the timestamp through the context:

```rust
use cgp_serde_extra::providers::{SerializeBase64, SerializeTimestamp};

pub struct AppB;

delegate_components! {
    AppB {
        open ValueSerializerComponent;

        @ValueSerializerComponent.<'a, T> &'a T:
            SerializeDeref,
        @ValueSerializerComponent.[
            i64,
            u64,
            String,
        ]:
            UseSerde,
        @ValueSerializerComponent.Vec<u8>:
            SerializeBase64,
        @ValueSerializerComponent.DateTime<Utc>:
            SerializeTimestamp,
        @ValueSerializerComponent.[
            Vec<EncryptedMessage>,
            Vec<MessagesByTopic>,
        ]:
            SerializeIterator,
        @ValueSerializerComponent.[
            MessagesArchive,
            MessagesByTopic,
            EncryptedMessage,
        ]:
            SerializeFields,
    }
}
```

The two contexts resolve `Vec<u8>` to overlapping providers, `SerializeHex` and `SerializeBase64`, with
no conflict, because each choice is coherent only within its own context. CGP wiring is
[checked lazily](../cgp/concepts/check-traits.md), so a [`check_components!`](../cgp/reference/macros/check_components.md)
block asserts at compile time that each context can serialize every value type, listing them as the
`Value` parameters of `ValueSerializerComponent`; `AppB` gets the same block:

```rust
check_components! {
    AppA {
        ValueSerializerComponent: [
            u64,
            String,
            Vec<u8>,
            DateTime<Utc>,
            EncryptedMessage,
            MessagesByTopic,
            MessagesArchive,
        ],
    }
}
```

## Producing JSON

Because the providers ultimately call a real `serde::Serializer`, the existing JSON ecosystem still does
the writing. The bridge is [`SerializeWithContext`](../projects/cgp-serde/reference/context-adapters.md),
which pairs a context and a value into a type that implements Serde's `Serialize` by calling the
context's `CanSerializeValue`:

```rust
use cgp_serde::types::SerializeWithContext;

let archive = MessagesArchive { /* ... */ };

let json_a = serde_json::to_string_pretty(&SerializeWithContext::new(&AppA, &archive)).unwrap();
let json_b = serde_json::to_string_pretty(&SerializeWithContext::new(&AppB, &archive)).unwrap();
```

For an archive holding one topic with two messages, the first message comes out of `AppA` with hex
bytes and an RFC 3339 date:

```json
{
  "message_id": 1,
  "author_id": 2,
  "date": "2025-11-03T14:15:00+00:00",
  "encrypted_data": "48656c6c6f2066726f6d20527573744c616221"
}
```

and out of `AppB` with base64 bytes and a Unix timestamp:

```json
{
  "message_id": 1,
  "author_id": 2,
  "date": 1762179300,
  "encrypted_data": "SGVsbG8gZnJvbSBSdXN0TGFiIQ=="
}
```

Nothing in the data types or the providers changed between the two, only which context wraps the value.

## Deserializing with a context-supplied service

Deserialization mirrors serialization, and the extra `&self` becomes essential in a way Serde cannot
match: the context can supply runtime *services* that a provider pulls in by dependency injection. The
motivating case is an [arena allocator](https://en.wikipedia.org/wiki/Region-based_memory_management),
deserializing many borrowed `&'a T` values into one arena instead of heap-allocating each. cgp-serde
splits the work into [layers](../projects/cgp-serde/architecture/context-services.md): a
`DeserializeAndAllocate` provider deserializes the owned value through the context and hands it to a
`CanAlloc` allocation component, and `AllocateWithArena` implements that component from an arena
getter:

```rust
#[cgp_impl(new DeserializeAndAllocate)]
#[uses(CanAlloc<'a, Value>, CanDeserializeValue<'de, Value>)]
impl<'de, 'a, Value> ValueDeserializer<'de, &'a Value>
{ ... }

#[cgp_impl(new AllocateWithArena)]
#[uses(HasArena<'a, Value>)]
impl<'a, Value: 'a> Allocator<'a, Value>
{ ... }
```

The data and the context complete the picture. The structs derive `CgpData` for generic field-by-field
deserialization, and the context carries the arena as an ordinary field borrowed from outside, deriving
[`HasField`](../cgp/reference/traits/has_field.md) so the arena getter can be wired to it:

```rust
use typed_arena::Arena;

#[derive(CgpData)]
pub struct Coord {
    pub x: u64,
    pub y: u64,
    pub z: u64,
}

#[derive(CgpData)]
pub struct Cluster<'a> {
    pub id: u64,
    pub coords: Vec<&'a Coord>,
}

#[derive(HasField)]
pub struct App<'a> {
    pub arena: &'a Arena<Coord>,
}
```

The wiring opens the deserialization component and keys on the value type as before, routing the bare
`Coord` and `Cluster` to the record deserializer, the borrowed `&'a Coord` to the arena allocator, and
the `Vec<&'a Coord>` to a sequence deserializer. It wires the allocation layers with two plain entries,
and, because deserialization can fail, the [`HasErrorType`](../cgp/reference/components/has_error_type.md)
and [`CanRaiseError`](../cgp/reference/components/can_raise_error.md) error components to an
`anyhow`-backed backend:

```rust
use cgp::core::error::{ErrorRaiserComponent, ErrorTypeProviderComponent};
use cgp_error_anyhow::{RaiseAnyhowError, UseAnyhowError};
use cgp_serde::components::ValueDeserializerComponent;
use cgp_serde::providers::{DeserializeExtend, DeserializeRecordFields, UseSerde};
use cgp_serde_alloc::providers::DeserializeAndAllocate;
use cgp_serde_alloc::traits::AllocatorComponent;
use cgp_serde_typed_arena::providers::AllocateWithArena;
use cgp_serde_typed_arena::traits::ArenaGetterComponent;

delegate_components! {
    <'s> App<'s> {
        open ValueDeserializerComponent;

        ErrorTypeProviderComponent:
            UseAnyhowError,
        ErrorRaiserComponent:
            RaiseAnyhowError,
        ArenaGetterComponent:
            UseField<Symbol!("arena")>,
        AllocatorComponent:
            AllocateWithArena,

        @ValueDeserializerComponent.u64:
            UseSerde,
        @ValueDeserializerComponent.[
            Coord,
            <'a> Cluster<'a>,
        ]:
            DeserializeRecordFields,
        @ValueDeserializerComponent.<'a> &'a Coord:
            DeserializeAndAllocate,
        @ValueDeserializerComponent.<'a> Vec<&'a Coord>:
            DeserializeExtend,
    }
}

check_components! {
    #[check_trait(CanDeserializeCluster)]
    <'de, 'a> App<'a> {
        ValueDeserializerComponent: [
            (Life<'de>, u64),
            (Life<'de>, Coord),
            (Life<'de>, &'a Coord),
            (Life<'de>, Cluster<'a>),
        ],
    }
}
```

The check lists each value type with a [`Life<'de>`](../cgp/reference/types/life.md), because the
deserialization component's `'de` lifetime is one of its parameters. With the context built around an
arena, deserializing a JSON cluster allocates its coordinates into that arena, and the returned
`Cluster` borrows from it:

```rust
use cgp_serde_json::impls::CanDeserializeJsonString;

let serialized = r#"
    {
        "id": 8,
        "coords": [
            { "x": 1, "y": 2, "z": 3 },
            { "x": 4, "y": 5, "z": 6 }
        ]
    }
"#;

let arena = Arena::new();
let app = App { arena: &arena };

let cluster: Cluster<'_> = app.deserialize_json_string(serialized).unwrap();
```

The arena was never an argument to a deserialize function; Serde's `from_str` has no slot for one. It
reached `DeserializeAndAllocate` through the context, which is how CGP supplies a dependency to code
nested arbitrarily deep without threading it explicitly, the
[dependency-injection](../cgp/concepts/impl-side-dependencies.md) idea applied to deserialization.
Swapping the arena for another allocator means wiring `AllocatorComponent` to a different provider,
without touching the deserializer.
