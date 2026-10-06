# Wiring a context

A cgp-serde context is an ordinary environmental context whose table chooses a provider for every
type it encodes. This guide gives the steps for building that table, the key syntax the value types
need, and the checks that prove it complete. The general wiring grammar is in
[`delegate_components!`](../../../cgp/reference/macros/delegate_components.md); the provider
behavior is in the [reference](../reference/README.md).

## Open the components and dispatch per type

**Open each serialization component with the `open` statement and key its entries on the value
type.** Statements come first in the block, then the entries:

```rust
pub struct AppA;

delegate_components! {
    AppA {
        open ValueSerializerComponent;

        @ValueSerializerComponent.<'a, T> &'a T: SerializeDeref,
        @ValueSerializerComponent.[u64, String]: UseSerde,
        @ValueSerializerComponent.Vec<u8>: SerializeHex,
        @ValueSerializerComponent.DateTime<Utc>: SerializeRfc3339Date,
        @ValueSerializerComponent.[Vec<EncryptedMessage>, Vec<MessagesByTopic>]: SerializeIterator,
        @ValueSerializerComponent.[MessagesArchive, MessagesByTopic, EncryptedMessage]: SerializeRecordFields,
    }
}
```

This is the table of `AppA` in the repository's [two-application example](../examples/messages.md),
condensed to one line per entry. Open several components at once with braces, as in
`open { ValueSerializerComponent, ValueDeserializerComponent };`. Prefer `open` to the
`UseDelegate<new … { … }>` tables of the published release and the announcement post, per
[dispatching per type](../../../cgp/guides/dispatching-per-type.md). A context that also runs the
JSON providers through `try_compute` opens `TryComputerComponent` too and keys it on the
[JSON codes](../reference/json.md#serializejson-and-deserializejson).

## Wire every type the traversal reaches

**List the value types a traversal touches, not only the types an application names.** Start from
each top-level type and follow what each provider asks the context for, using the "Re-enters for"
column of the [reference table](../reference/README.md#serialization-and-deserialization-providers):

- **Structs** wired to `SerializeRecordFields` or `DeserializeRecordFields` need an entry for each
  field's type.
- **Enums** wired to `SerializeVariantFields` or `DeserializeVariantFields` need an entry for each
  variant's payload type, including `()` for a unit-like variant such as `Empty(())`. The `()`
  entry decides how that variant is written: `UseSerde` writes `{"Empty":null}`; see
  [variants](../reference/variants.md#wiring-the-pair).
- **Collections** need their own entry, not only their item type's, and `SerializeIterator` needs an
  entry for the item *reference* it yields; the generic `<'a, T> &'a T: SerializeDeref` entry covers
  every reference at once.
- **Encodings** re-enter for their intermediate type: hex, base64, and RFC 3339 for `String`, the
  timestamp encoding for `i64`. A context wires that intermediate type even when no field has it.
- **Leaves**, the types an application does not want to customize, go to `UseSerde`.

A missing entry is a compile error rather than a runtime surprise, and
[debugging wiring](debugging-wiring.md) shows what each kind of omission reports.

## Write keys for references, lifetimes, and arrays

Three kinds of value type need care in a key:

- **References and borrowed types** carry their lifetime as a per-entry generic:
  `@ValueSerializerComponent.<'a, T> &'a T`, `@ValueDeserializerComponent.<'a> &'a str`, and
  `@ValueDeserializerComponent.<'a> Cluster<'a>`. Inside a list key, each type carries its own:
  `[Coord, <'a> Cluster<'a>]`. A key with a concrete lifetime, such as `&'static str`, also works
  but matches only that lifetime.
- **A context with a lifetime** declares it on the table, `<'s> App<'s> { … }`, with the entries
  using their own lifetime names.
- **Fixed-size arrays** cannot be written directly, because square brackets are the path-grouping
  syntax: `@ValueDeserializerComponent.[u8; 32]` fails with `expected ','`. Define a type alias,
  such as `type Digest = [u8; 32];`, and key on the alias.

## Wire the error components when the JSON providers are used

The JSON providers and `deserialize_json_string` raise `serde_json` errors through the context, so a
context using them wires an error type and a raiser, such as the `anyhow` backend:

```rust
ErrorTypeProviderComponent: UseAnyhowError,
ErrorRaiserComponent: RaiseAnyhowError,
```

These are plain entries, without `open`, imported from `cgp::core::error` and `cgp_error_anyhow`;
see [modular error handling](../../../cgp/concepts/modular-error-handling.md), and the
[`cgp-error-anyhow` reference](../../error/cgp-error-anyhow/reference.md) for the two providers. A
context that only serializes through the adapters directly does not need them.

## Check every value type

**Assert the wiring with a standalone `check_components!` listing every value type the context
encodes**, because wiring is [lazy](../../../cgp/concepts/check-traits.md) and an omission otherwise
surfaces only at the first use. List the deserializing side with the component's lifetime lifted
into [`Life`](../../../cgp/reference/types/life.md):

```rust
check_components! {
    #[check_trait(CanSerializeApp)]
    App {
        ValueSerializerComponent: [u64, String, Vec<u8>, Payload],
    }
}

check_components! {
    #[check_trait(CanDeserializeApp)]
    <'de> App {
        ValueDeserializerComponent: [
            (Life<'de>, u64),
            (Life<'de>, String),
            (Life<'de>, Vec<u8>),
            (Life<'de>, Payload),
        ],
    }
}
```

The repository's [`basic` example](../examples/basic.md) checks its context the same way. Give each
table its own `#[check_trait]` name when a module holds more than one check for the same context,
since both would otherwise derive the same trait name. Use standalone checks rather than
`delegate_and_check_components!`, which derives checks only for plain entries and leaves every
`open` dispatch unchecked.

## Share wiring between contexts

**cgp-serde publishes no namespace of defaults**, so the library gives two applications nothing to
share, and the demo's `AppA` and `AppB` repeat every entry but the three that differ. An application
can define a namespace of its own with
[`cgp_namespace!`](../../../cgp/reference/macros/cgp_namespace.md), put the shared `@` entries in
it, and have each context join it and add only its differences. A probe confirmed this form against
the `v0.8.0` branch, with the demo reduced to `EncryptedMessage` and `MessagesByTopic`:

```rust
cgp_namespace! {
    new MessagesNamespace {
        @ValueSerializerComponent.<'a, T> &'a T:
            SerializeDeref,
        @ValueSerializerComponent.[i64, u64, String]:
            UseSerde,
        @ValueSerializerComponent.Vec<EncryptedMessage>:
            SerializeIterator,
        @ValueSerializerComponent.[MessagesByTopic, EncryptedMessage]:
            SerializeRecordFields,
    }
}

pub struct AppA;

delegate_components! {
    AppA {
        namespace MessagesNamespace;
        open ValueSerializerComponent;

        @ValueSerializerComponent.Vec<u8>: SerializeHex,
        @ValueSerializerComponent.DateTime<Utc>: SerializeRfc3339Date,
    }
}
```

`AppB` is the same with `SerializeBase64` and `SerializeTimestamp`, and the two produced hex and RFC
3339 dates from one and base64 and timestamps from the other, as the full demo does. Two facts
constrain the form. **Each context still opens the component**: without its `open` statement, plain
`cargo check` fails every check with the unsatisfied bound
`ValueSerializerComponent: MessagesNamespace<AppA>`, and `cargo cgp check` names the root cause as
`[CGP-E107]`, `AppA` having no delegate entry for `ValueSerializerComponent`. And **a context cannot
rebind an entry the namespace makes**: adding `@ValueSerializerComponent.u64: UseSerde` to `AppA`
fails with `[CGP-E005]`, saying that `AppA` cannot wire `@ValueSerializerComponent.u64.*` because it
is already set through `MessagesNamespace`. So the namespace holds only what every joining context
shares, and each point of difference stays in the contexts. The mechanism is in
[namespaces and prefixes](../../../cgp/guides/namespaces-and-prefixes.md). The website's wiring
guide shows this form as its last step.

## Public material derived from this

The `guides/wiring-a-context` page of the
[cgp-serde project section](../../../website/projects/cgp-serde.md).
