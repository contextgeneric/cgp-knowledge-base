# Debugging wiring

Most cgp-serde compile errors come from a handful of wiring mistakes, and each has a recognizable
diagnostic. This guide shows each mistake with the code that makes it and what the compiler reports.
The general method for reading CGP errors is in [debugging](../../../cgp/guides/debugging.md), and the
diagnostics below come from `cargo cgp check`, CGP's error toolchain. `cargo cgp check` leads with the
root cause for the classes it recognizes, and the tool is a v0.1.0-alpha that does not yet reshape every
class. Two of the mistakes below are classes it leaves as rustc reports them.

## A type the traversal reaches has no entry

**The most common mistake is a missing entry for a nested type.** Here `Payload` is wired to
`SerializeFields`, but its `data: Vec<u8>` field's type has no entry:

```rust
#[derive(CgpData)]
pub struct Payload {
    pub quantity: u64,
    pub data: Vec<u8>,
}

delegate_components! {
    App {
        open ValueSerializerComponent;
        @ValueSerializerComponent.u64: UseSerde,
        @ValueSerializerComponent.Payload: SerializeFields,
    }
}

check_components! {
    App {
        ValueSerializerComponent: [u64, Payload],
    }
}
```

The check fails on `Payload`, and `cargo cgp check` names the missing entry as the root cause:

```text
error[E0277]: [CGP-E001] the consumer trait `CanSerializeValue<Payload>` is not implemented for context `App`
  = note: root cause: [CGP-E107] context `App` does not contain any delegate entry for `@ValueSerializerComponent.Vec<u8>`
```

The dependency chain the tool prints beneath the root cause walks from `SerializeFields` through the
field list to the `data` field, so the missing type is named even when it is several levels deep. The
fix is an entry for `Vec<u8>`.

The same diagnostic, naming a different key, covers the two missing entries that are easiest to
overlook because no field in the data has the type:

- **The reference entry for `SerializeIterator`.** Wiring `Vec<u64>` to `SerializeIterator` without a
  reference entry reports a missing `@ValueSerializerComponent.&u64`, because iterating the vector by
  reference yields `&u64`. The fix is `@ValueSerializerComponent.<'a, T> &'a T: SerializeDeref`.
- **The intermediate type of an encoding.** Wiring `DateTime<Utc>` to `SerializeTimestamp` without an
  `i64` entry reports a missing `@ValueSerializerComponent.i64`, because the timestamp encoding
  serializes the number through the context. Hex, base64, and RFC 3339 need `String` the same way.

## A deserialization check omits the lifetime

**Writing a deserializing check entry without `Life<'de>` reports a provider that does not implement
the component, rather than a missing entry.**

```rust
check_components! {
    App {
        ValueDeserializerComponent: u64,
    }
}
```

The check fails even though `u64` is wired:

```text
error[E0277]: [CGP-E002] the provider trait `ValueDeserializer<u64>` with context `App` is not implemented for provider `RedirectLookup<App, @ValueDeserializerComponent>`
```

The clue is in the list of implementations the error prints, which includes
`IsProviderFor<ValueDeserializerComponent, __Context__, (Life<'_>, Value)>`: the component's parameters
are a lifetime and a type, and the check supplied only the type. The fix is to write the entry as
`(Life<'de>, u64)` with `<'de>` declared on the table, as
[wiring a context](wiring-a-context.md#check-every-value-type) shows.

## The JSON helper is missing its error wiring

**`deserialize_json_string` needs the context's error components, and plain rustc does not say so.**

```rust
delegate_components! {
    Ctx {
        open ValueDeserializerComponent;
        @ValueDeserializerComponent.u64: UseSerde,
    }
}

let r: Result<u64, _> = Ctx.deserialize_json_string("1");
```

Plain `cargo check` reports only that the method `deserialize_json_string` exists for `Ctx` but its
trait bounds were not satisfied, as `E0599`, the hidden-cause shape the error catalog records as an
[unsatisfied dependency](../../../cgp/errors/hidden/unsatisfied-dependency.md). `cargo cgp check`
reshapes it as a `[CGP-E009]` error saying the trait `CanDeserializeJsonString<_>` is not
implemented for `Ctx`, with root causes naming the missing `ErrorTypeProviderComponent` and
`ErrorRaiserComponent` entries.
It also lists a missing `@ValueDeserializerComponent` entry, because the method call failed before the
target type was inferred, so the tree shows `CanDeserializeValue<_>`; that cause disappears once the
error components are wired. The fix is the two error entries.

## A provider depends on itself

**Wiring a type to a provider that re-enters the context for the same type overflows the trait
solver.**

```rust
delegate_components! {
    Ctx {
        open ValueSerializerComponent;
        @ValueSerializerComponent.String: SerializeWithDisplay,
    }
}
```

`SerializeWithDisplay` serializes a value by formatting it to a `String` and asking the context to
serialize that `String`, which leads straight back to `SerializeWithDisplay`. Using the context reports
`E0275`, overflow evaluating the requirement, at the call site; `cargo cgp check` leaves this class
unchanged. The fix is a leaf provider for the intermediate type, such as `UseSerde` or
`SerializeString` for `String`.

## The data type is recursive

**A type that contains itself fails the same way even when every entry is present.** A
`Node { id: u64, children: Vec<Node> }` wired to `SerializeFields`, with `Vec<Node>` wired to
`SerializeIterator` and the reference entry in place, reports `E0275` when used, because serializing
`Node` requires serializing `Vec<Node>`, which requires `&Node`, which requires `Node` again. No wiring
fixes it: the type needs a provider that walks the recursion itself and asks the context only for the
non-recursive parts, as
[re-entrant providers](../architecture/reentrant-providers.md#what-re-entry-requires-of-a-context)
describes.

## A key does not parse

**A key the wiring grammar cannot read fails inside the macro, before any trait is checked.** The case
serialization runs into is a fixed-size array: `@ValueDeserializerComponent.[u8; 32]` fails with
`expected ','` at the semicolon, because square brackets are the path-grouping syntax. Key the array on
a type alias instead, as
[wiring a context](wiring-a-context.md#write-keys-for-references-lifetimes-and-arrays) describes.

## Public material derived from this

A troubleshooting section of the repository README, and the wiring page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md).
