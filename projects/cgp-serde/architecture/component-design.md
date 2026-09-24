# Component design

cgp-serde's two components differ from Serde's traits in one structural decision, moving the encoded
type out of `Self`, and its providers follow one naming and pairing convention. This document explains
both decisions and what they cost. The components themselves are documented in the
[reference](../reference/components.md).

## Moving the value out of `Self`

**The encoded type moves from `Self` into a `Value` parameter so that the application, not the data
type, chooses the encoding.** Serde's `Serialize` is implemented *for* the type being serialized, which
gives each type one encoding for the whole program, chosen by whoever owns the type or the trait.
`CanSerializeValue<Value>` and `CanDeserializeValue<'de, Value>` are implemented for a context instead,
with the value as a parameter, so each context makes its own choice for each value type.

In the vocabulary of the [modularity hierarchy](../../../cgp/concepts/modularity-hierarchy.md), the
components are **parameter-targeted** and the contexts are **environmental**: `AppA` and `AppB` stand
for applications and often have no fields at all. That is the hierarchy's tier 4, the fully modular
shape, and serialization is the case it exists for. The encoded types are usually foreign, so a
self-targeted component wired on `Vec<u8>` itself would give `Vec<u8>` one encoding program-wide, and
the orphan rule would additionally require the wiring to live in a crate owning the trait or the type.
Keying the choice on a context the application owns removes both limits, as
[bypassing coherence](../../../cgp/concepts/coherence.md) explains.

The change costs something at every site that uses the components. The trait could not be retrofitted
onto `serde::Serialize` without breaking it, so cgp-serde defines new traits and bridges to the old ones;
see [the bridge to Serde](serde-bridge.md). And every value type a context encodes needs a wiring entry,
including intermediate types such as a `Vec` of structs and the references iteration yields. The
library does not yet publish a namespace of defaults that would shorten that table, so every context
spells out its full wiring.

## One struct, both directions

**A provider is a type-level name, so one struct can implement both components, and the library uses
this whenever the two directions are one decision.** A context that wires `Vec<u8>` to `SerializeHex`
for serializing wires the same name for deserializing, and the two impls are written together to agree
on one format. The naming convention follows from this: a struct named `Serialize…` may implement both
directions, while a struct named `Deserialize…` implements only deserialization. Where the two
directions need different mechanisms, they are separate structs whose names describe the mechanism.

Sharing a struct makes agreement the intent but does not enforce it. `SerializeBytes` is one struct
whose two directions disagree under JSON, as its
[known issues](../reference/strings-and-bytes.md#known-issues) record, so a context still has to test
that what it writes it can read back.

The table pairs every serializing provider with its deserializing counterpart:

| Serializing | Deserializing | Relationship |
|---|---|---|
| `UseSerde` | `UseSerde` | one struct |
| `SerializeString` | `SerializeString` | one struct; deserializes `String` only |
| `SerializeBytes` | `SerializeBytes`, `TryDeserializeBytes` | one struct, plus a fallible variant |
| `SerializeWithDisplay` | `DeserializeWithFromStr` | separate structs over `Display` and `FromStr` |
| `SerializeFrom<T>` | `SerializeFrom<T>` | one struct; `T` is the target one way, the source the other |
| `TrySerializeFrom<T>` | `TrySerializeFrom<T>` | one struct, fallible |
| `SerializeDeref` | none | a reference is deserialized by `DeserializeAndAllocate` |
| `SerializeIterator` | `DeserializeExtend` | separate structs: iterate by reference, extend by value |
| `SerializeFields` | `DeserializeRecordFields` | separate structs: read fields, fill a builder |
| none | `DeserializeDefault<P>` | deserialize-only, higher-order |
| `SerializeHex`, `SerializeBase64`, `SerializeRfc3339Date`, `SerializeTimestamp` | the same structs | one struct each |
| `SerializeToJsonString` | `DeserializeFromJsonString`, `DeserializeFromJsonReader` | separate structs over `TryComputer` |

The separate pairs differ because their two directions use different machinery rather than different
decisions. `SerializeFields` reads each field through `HasField`, while `DeserializeRecordFields`
builds the struct through CGP's optional builder; `SerializeIterator` borrows the collection and walks
it, while `DeserializeExtend` starts from a default and extends it. Each direction is therefore a
different provider rather than one decision implemented twice, and each gets a name for its mechanism.

## The deserialization lifetime

**`CanDeserializeValue` carries Serde's `'de` lifetime as a component parameter**, so a provider can
produce values that borrow from the input exactly as Serde's `Deserialize<'de>` can. Being a
parameter, the lifetime is part of the component's identity: CGP lifts it into
[`Life<'de>`](../../../cgp/reference/types/life.md) in check traits, so a context's checks list each
value type as `(Life<'de>, T)`. The serializing component has no lifetime, and its `Value` is declared
`?Sized`, although no provider in the library accepts an unsized value.

## Public material derived from this

The "Serialization as a component" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md).
