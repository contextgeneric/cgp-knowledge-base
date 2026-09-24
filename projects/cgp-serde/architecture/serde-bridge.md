# The bridge to Serde

cgp-serde replaces exactly one layer of Serde and keeps the rest. This document explains which layer
that is, the two directions in which cgp-serde and ordinary Serde code meet, where errors are reported,
and which Serde behaviors change as a result.

## What is replaced and what is kept

**Serde separates what a value is from how a format writes it, and cgp-serde replaces only the first
half.** Serde's `Serializer` and `Deserializer` traits are implemented by formats: `serde_json`, RON,
and the rest. Its data model, the small set of types those traits can express (strings, byte arrays,
sequences, maps, structs, options, and the primitives), is the contract between the two sides. Its
`Serialize` and `Deserialize` traits are implemented by data types, and they decide how a value maps
onto the data model.

cgp-serde replaces the `Serialize` and `Deserialize` layer with its two
[components](../reference/components.md) and keeps the data model and the format traits as they are.
A cgp-serde provider receives an ordinary Serde `Serializer` or `Deserializer` and calls its ordinary
methods (`serialize_str`, `serialize_seq`, `deserialize_map`, and so on), exactly as a hand-written
`Serialize` impl would. So a format needs no changes to work with cgp-serde, and cgp-serde needs no
code per format.

## The two directions of the bridge

**The bridge carries values both ways: into existing Serde impls, and out to existing Serde APIs.**

Going in, [`UseSerde`](../reference/use-serde.md) lets a context use a type's own `Serialize` or
`Deserialize` impl as its provider. Every existing impl, in the standard library or a third-party crate,
is therefore available without a cgp-serde provider being written for it. The cost is that the context's
wiring stops at that value: the type's own impl serializes its fields, and the context's choices do not
reach inside it.

Going out, the [context adapters](../reference/context-adapters.md) wrap a context together with a
value, as a `Serialize`, or with a target type, as a `DeserializeSeed`. Any Serde API that accepts one of
those accepts the pair: `serde_json::to_string` for serializing, and a format's deserializer driving the
seed for deserializing. The same adapters let providers hand nested values back to the context from
inside Serde's compound serializers and access traits, which is how
[re-entry](reentrant-providers.md) works.

**Deserializing needs a little more machinery than serializing.** `DeserializeSeed` is Serde's way to
deserialize with state, but Serde's convenience functions such as `serde_json::from_str` accept only a
stateless `Deserialize` type. An application therefore builds the format's deserializer itself and drives
the seed with it, and checks for trailing input itself. The [JSON providers](../reference/json.md) do
this for `serde_json`; every other format needs the same few lines written by hand.

## Where errors are reported

**Errors are reported at two levels, and only the outer one uses CGP's error handling.** Inside a
traversal, a provider reports a failure through the Serde format's own error type, with
`Error::custom` on the serializer's or deserializer's error. This is how a failed `TryInto`, an invalid
hex digit, or a missing field is reported, and it is the same mechanism a hand-written Serde impl uses,
so the format decorates the message with its position as usual.

At the boundary, the JSON providers convert the format's `serde_json::Error` into the context's own
error type with [`CanRaiseError`](../../../cgp/reference/components/can_raise_error.md), so the caller
sees whatever error type the context wires, such as `anyhow::Error`. A context that serializes through
the adapters directly never touches CGP's error components; the format's error comes straight back.

## Serde behaviors that change

Replacing the data-type layer means the behaviors Serde's derive provides are not automatically
present. Two of them affect which formats accept cgp-serde's output:

- **Records are written as maps.** [`SerializeFields`](../reference/records.md) calls
  `serialize_map` where a derived impl calls `serialize_struct`, so a format with distinct struct
  syntax, such as RON, shows a map.
- **Lengths are not declared.** The record and [collection](../reference/collections.md) providers
  open their map or sequence with an unknown length, so a length-prefixed binary format such as
  postcard rejects them.

The derive's attributes (renaming, skipping, flattening, defaulting a missing field, rejecting unknown
fields) also have no equivalent, and enums have no generic provider. A self-describing format such as
JSON or RON works with the library as it stands; the complete list of gaps is in the project
[README](../README.md#status-and-gaps).

## Public material derived from this

The "Serialization as a component" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the page on what the library does
not do.
