# Re-entrant providers

A cgp-serde provider for a composite value never encodes the values inside it. It hands each inner
value back to the context, and the context's wiring chooses the provider for that value's type. This
document explains the two ways a provider re-enters the context, the adapter types that make the second
way possible, and what the design requires of a context's wiring.

## Why the providers re-enter

**Re-entry is what makes a context's choices reach every level of nesting.** In plain Serde, the
`Serialize` impl of a struct calls each field's own `Serialize` impl, so the encoding of a `Vec<u8>`
field is fixed by whoever implemented `Serialize` for `Vec<u8>`. cgp-serde replaces that call with a
call on the context. `SerializeFields` serializes a field by asking the context to serialize the field's
type, `SerializeIterator` does the same for each item, and so on down. A context that wires `Vec<u8>` to
`SerializeHex` therefore gets hex for every `Vec<u8>` wherever it occurs (a top-level value, a field,
an item of a list inside a field), and no provider on the path has to know about the choice.

The same property keeps providers small and reusable. `SerializeFields` knows how to walk a struct and
nothing about its fields' types; `SerializeIterator` knows how to walk a collection and nothing about
its items. Each is written once, generically, and composed by the context. The dependency on the
context appears in each provider as an [impl-side dependency](../../../cgp/concepts/impl-side-dependencies.md)
on the consumer trait, such as `Self: CanSerializeValue<String>`, so the context resolves it from its
own wiring.

## The two forms of re-entry

A provider re-enters in one of two ways, depending on who performs the nested call. When the provider
itself encodes the whole value by first converting it, it calls the consumer trait on `self` directly.
When it must hand the nested value to a Serde API that performs the call, it wraps the value and the
context in an adapter.

### Direct calls

**A converting provider transforms the value and calls `self.serialize` or `self.deserialize` on the
result.** `SerializeWithDisplay` formats a value to a `String` and then asks the context to serialize
that `String`, which its header declares as a dependency on the consumer trait:

```rust
#[cgp_impl(new SerializeWithDisplay)]
#[uses(CanSerializeValue<String>)]
impl<Value> ValueSerializer<Value>
where
    Value: Display,
{ ... }
```

The provider passes its `serializer` straight through to the nested call, so no adapter is needed. The
encoding of the resulting string is still a wiring choice: `UseSerde` and `SerializeString` both
serialize a `String` as a string, but a context could choose otherwise. The deserializing direction
mirrors it: `DeserializeWithFromStr` asks the context to deserialize a `&'de str` and parses the
result.

### Adapter calls

**A structural provider hands each nested value to a Serde compound API, which needs an ordinary Serde
value, so the provider wraps the value with the context.** Serde's compound serializers, such as
`SerializeSeq::serialize_element` and `SerializeMap::serialize_entry`, take `&impl Serialize`. Its
access traits, such as `SeqAccess::next_element_seed` and `MapAccess::next_value_seed`, take an
`impl DeserializeSeed`. None of them accept a context. cgp-serde bridges the gap with two adapter types
in `cgp_serde::types`, documented in [context adapters](../reference/context-adapters.md).
`SerializeWithContext` borrows a context and a value and implements `Serialize` by calling the
context's `CanSerializeValue`; `DeserializeWithContext` borrows a context, names a target type, and
implements `DeserializeSeed`, Serde's mechanism for deserialization that needs state, by calling the
context's `CanDeserializeValue`. In both, the context is the state Serde's own traits have no room for.

`SerializeIterator` shows the adapter in use. Its header asks the context to serialize each item type,
and its body opens a sequence and passes each item to `serialize_element` wrapped in
`SerializeWithContext`:

```rust
#[cgp_impl(new SerializeIterator)]
impl<Value> ValueSerializer<Value>
where
    for<'a> &'a Value: IntoIterator,
    Self: for<'a> CanSerializeValue<<&'a Value as IntoIterator>::Item>,
{ ... }
```

The item bound is written as a higher-ranked `Self: for<'a> CanSerializeValue<…>` in the `where` clause
rather than with [`#[uses]`](../../../cgp/reference/attributes/uses.md), because the item type depends
on the borrow's lifetime. The same adapters are the entry point from outside: an application passes
`SerializeWithContext::new(&context, &value)` to `serde_json::to_string`, or calls
`DeserializeWithContext::new(&context).deserialize(&mut deserializer)`, and the whole traversal runs
through the context from there.

`DeserializeExtend` does not use `DeserializeWithContext`; it defines a private seed of the same shape
for its items. The behavior is identical, and the duplication is an internal detail.

## Which providers re-enter

Every provider either re-enters for some type or is a leaf that encodes its value itself. The table
lists what each provider in the library asks of the context, which is exactly what a context must wire
for that provider to work. `Value` is the type the provider is handling; `Item` and `Target` are the
associated types named in its bounds.

| Provider | Direction | Re-enters for | Form |
|---|---|---|---|
| `UseSerde` | both | nothing; defers to Serde's own impl | leaf |
| `SerializeString` | both | nothing | leaf |
| `SerializeBytes` | both | nothing | leaf |
| `TryDeserializeBytes` | deserialize | nothing | leaf |
| `SerializeWithDisplay` | serialize | `String` | direct |
| `DeserializeWithFromStr` | deserialize | `&'de str` | direct |
| `SerializeFrom<Target>` | serialize | `Target` | direct |
| `SerializeFrom<Source>` | deserialize | `Source` | direct |
| `TrySerializeFrom<…>` | both | `Target` / `Source` | direct |
| `SerializeDeref` | serialize | `Value::Target` | direct |
| `SerializeIterator` | serialize | each item yielded by iterating `&Value` | adapter |
| `DeserializeExtend` | deserialize | each `Item` | adapter (private seed) |
| `SerializeFields` | serialize | each field's type | adapter |
| `DeserializeRecordFields` | deserialize | each field's type | adapter |
| `SerializeHex`, `SerializeBase64`, `SerializeRfc3339Date` | both | `String` | direct |
| `SerializeTimestamp` | both | `i64` | direct |
| `DeserializeAndAllocate` | deserialize | the owned `Value` behind `&'a Value`, then allocates through `CanAlloc` | direct |
| `DeserializeDefault<Provider>` | deserialize | nothing; calls `Provider` explicitly | higher-order |

`DeserializeDefault` is the one serialization provider that delegates without re-entering. It is a
[higher-order provider](../../../cgp/concepts/higher-order-providers.md): for a non-null input it calls
its `Provider` parameter directly for the same `Value`, which it must, since re-entering the context
for `Value` would resolve back to `DeserializeDefault` itself.

A higher-order provider is also the only way to bypass re-entry for one value while leaving the
context's wiring alone. The [modularity hierarchy](../../../cgp/concepts/modularity-hierarchy.md)
illustrates its top tier with a `SerializeIteratorWith<Provider>` that serializes a collection's items
through an explicit provider instead of the context. cgp-serde does not provide that provider:
`SerializeIterator` always re-enters, and `DeserializeDefault` is the only higher-order provider
among the serialization providers.

## What re-entry requires of a context

**A context must wire every type the traversal reaches, including the intermediate ones.** Serializing
a `MessagesByTopic` whose `messages` field is a `Vec<EncryptedMessage>` needs an entry for the vector
as well as for `EncryptedMessage`, and serializing an `encrypted_data: Vec<u8>` field through
`SerializeHex` needs an entry for `String`, because `SerializeHex` re-enters for the string it
produces. The same
reasoning explains an entry that is easy to miss: `SerializeTimestamp` re-enters for `i64`, so a context
that encodes dates as timestamps must wire `i64` even if no field has that type.

**`SerializeIterator` re-enters for references, so a context that uses it needs a reference entry.**
The provider iterates `&Value`, and iterating a borrowed collection yields borrowed items, so
serializing a `Vec<EncryptedMessage>` asks the context to serialize `&EncryptedMessage`. The test
contexts answer with one generic entry that forwards every reference to the value behind it:

```rust
delegate_components! {
    AppA {
        open ValueSerializerComponent;

        @ValueSerializerComponent.<'a, T> &'a T:
            SerializeDeref,
        // ...
    }
}
```

`SerializeDeref` then re-enters for `EncryptedMessage`, so the item reaches its real provider. Without
the entry, the context cannot serialize a `Vec` or a slice through `SerializeIterator`, since both
yield references when iterated by reference.

**A missing entry is a compile error, and a cycle is too.** Wiring resolves at compile time, so a type
the traversal reaches without an entry fails to compile at the point the context is used, which is why
the library's tests assert each context's wiring with
[`check_components!`](../../../cgp/reference/macros/check_components.md). A cycle in the wiring does
not recurse at runtime either. A provider that re-enters for a type whose entry leads back to itself,
such as `String` wired to `SerializeWithDisplay`, which re-enters for `String`, fails to compile. The
trait solver reports it as `E0275`, overflow evaluating the requirement.

That same compile-time resolution is why a **recursive data type** cannot be serialized through the
re-entrant providers. A `Node` with a `children: Vec<Node>` field makes `CanSerializeValue<Node>`
require `CanSerializeValue<Vec<Node>>`, which requires `CanSerializeValue<&Node>`, which requires
`CanSerializeValue<Node>` again. Rust's trait solver treats that cycle as an overflow rather than as a
proof, so the context fails with `E0275` even though every entry is present. The library offers no
provider for a recursive type, so such a type needs one written for it, and that provider must walk the
recursion itself rather than re-entering the context for the recursive type. A provider for `Node` that
serializes its children with its own recursive helper, and asks the context only for the `u64` inside
each node, compiles and produces the expected nested JSON.

## Public material derived from this

The "Writing serializers" page of the planned [cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md),
and the rustdoc for `SerializeWithContext` and `DeserializeWithContext`.
