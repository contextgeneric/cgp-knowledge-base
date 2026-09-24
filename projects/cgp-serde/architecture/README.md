# cgp-serde architecture

cgp-serde is built from a handful of design decisions that every provider in it follows, and this page
states them together so a reader can hold the whole design at once before opening the reference. Each
decision has its own document below, which carries the mechanism and the code; this page carries only
the claim and why it matters. CGP's own constructs are documented under [cgp/](../../../cgp/README.md)
and are linked rather than re-explained, per [../../AGENTS.md](../../AGENTS.md#leave-cgp-itself-to-cgp).

## The design on one page

**cgp-serde replaces Serde's `Serialize` and `Deserialize` traits and nothing else.** Serde splits
serialization into a data model, the `Serializer` and `Deserializer` traits that formats implement, and
the `Serialize` and `Deserialize` traits that data types implement. cgp-serde swaps out only that last
layer. Its providers call the same `Serializer` and `Deserializer` methods a hand-written impl would,
so a format needs no changes to work with it. Two of those calls differ from what Serde's derive emits,
and they limit which formats accept the output: the record and sequence providers start a map or
sequence without declaring its length, which length-prefixed binary formats such as postcard reject,
and records are written as maps rather than structs, so a format with distinct struct syntax, such as
RON, shows a map. The two layers meet in both directions: `UseSerde` lets a context use a type's
existing `Serialize` or `Deserialize` impl, and two adapter types let a context-aware value enter any
API that expects an ordinary `Serialize` or `DeserializeSeed`. See [serde-bridge.md](serde-bridge.md).

**The type being encoded moves out of `Self` and into a parameter.** `CanSerializeValue<Value>` and
`CanDeserializeValue<'de, Value>` keep Serde's method signatures but add `&self`, and `Self` becomes an
environmental context that carries the wiring. Both components are parameter-targeted, the fully
modular shape that the [modularity hierarchy](../../../cgp/concepts/modularity-hierarchy.md) places on
tier 4: each context chooses a provider per value type, including value types it does not own. A
self-targeted component would give a foreign type such as `Vec<u8>` one encoding for the whole
program, which is exactly the limitation cgp-serde exists to remove. See
[component-design.md](component-design.md).

**Composite values are encoded by calling back into the context.** A provider for a struct, a
sequence, a reference, or a converted value does not encode the inner values itself. It hands each one
back to the context, through `SerializeWithContext` when a Serde API needs a `Serialize` value and
`DeserializeWithContext` when it needs a `DeserializeSeed`. Because every nested value takes that route,
a context's per-type choices reach any depth of nesting, and no provider has to know the shape of the
data it sits inside. This is the mechanism the rest of the design depends on; see
[reentrant-providers.md](reentrant-providers.md).

**One provider struct can serve both directions.** A provider is a type-level name, so a single struct
may implement both `ValueSerializer` and `ValueDeserializer`, and a context names it once in each
table. The library uses this for every encoding whose two directions are one decision: `UseSerde`, the
string and byte providers, the conversion providers, and all four encodings in `cgp-serde-extra`.
Structs named `Serialize…` may implement both directions, while structs named `Deserialize…` implement
only deserialization. Where the two directions need different mechanisms, they are separate structs:
`SerializeFields` pairs with `DeserializeRecordFields`, and `SerializeIterator` with
`DeserializeExtend`. The full pairing is in [component-design.md](component-design.md#one-struct-both-directions).

**A struct needs no serialization-specific derive.** `SerializeFields` walks a struct's field list
through [`HasFields`](../../../cgp/reference/traits/has_fields.md), and `DeserializeRecordFields` fills
the struct through CGP's optional builder. Both depend only on derives from `cgp`: serializing needs
`HasFields` and `HasField`, deserializing needs `HasFields` and `BuildField`, and `CgpData` derives all
three. A library can therefore make its types serializable without depending on `serde` or
`cgp-serde`, and an application can encode them however it likes. See
[derive-free-records.md](derive-free-records.md).

**A deserializer can take services from its context.** Because every provider method receives the
context, a provider can require a trait on it as an impl-side dependency and call it mid-deserialization.
The allocation crates use this to deserialize a borrowed `&'a T` by allocating the owned value into an
arena that the context supplies. They split the work into layers: `DeserializeAndAllocate` requires an
allocation component, `CanAlloc`, and `AllocateWithArena` implements that component from an arena
getter. So the arena is a wiring choice rather than part of the deserializer. See
[context-services.md](context-services.md).

**Crates split along external dependencies.** The core crate depends only on `cgp` and `serde`, and
each other crate adds only the external dependencies of its own providers: `hex`, `base64`, and
`chrono` for the encodings, `serde_json` for the JSON providers, `typed-arena` for the arena, and
nothing for the allocation component. Every library crate is `no_std`. An application depends on
exactly the crates whose providers its wiring names; see [crate-layout.md](crate-layout.md).

## The catalog

Register each architecture document here, in [../README.md](../README.md), and in
[../../../summary.md](../../../summary.md) in the same change.

- [serde-bridge.md](serde-bridge.md) — the layer of Serde cgp-serde replaces and the layers it keeps,
  the two directions values cross between them, the two levels at which errors are reported, and the
  Serde behaviors that change.
- [component-design.md](component-design.md) — why the value moves out of `Self` and what that costs,
  one provider struct for both directions with the full pairing table, and the `'de` lifetime as a
  component parameter.
- [reentrant-providers.md](reentrant-providers.md) — how composite providers hand each nested value
  back to the context through `SerializeWithContext` and `DeserializeWithContext`, which providers do
  it and which are leaves, and what a context must therefore wire.
- [derive-free-records.md](derive-free-records.md) — serializing structs through CGP's general field
  traits instead of a serialization-specific derive, the derives each direction still needs, and what
  the approach gives up.
- [context-services.md](context-services.md) — providers drawing services from the context, the three
  layers of the arena deserializer, and the lifetimes that let allocated values outlive the context.
- [crate-layout.md](crate-layout.md) — the five crates and their dependency graph, why allocation is
  two crates, the shared module names, and the build facts.

## Public material derived from this

The first page of the planned [cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and
the opening of the repository README.
