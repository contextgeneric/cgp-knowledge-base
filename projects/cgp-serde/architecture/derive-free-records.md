# Derive-free records

cgp-serde serializes a struct without the struct deriving anything serialization-specific. The struct
derives CGP's general-purpose field traits, and two generic providers walk its fields. This document
explains why that matters, what the struct must still opt into, and what the approach gives up. The
providers themselves are documented in [records](../reference/records.md).

## The problem it removes

**With Serde, a type is serializable only if its owner derives or implements Serde's traits for it.**
The orphan rule forbids anyone else from implementing `Serialize` for a type they did not define, so a
library that wants its types to be serializable must depend on `serde` and derive the traits itself,
and must keep doing so for every other trait its users might want. An application that needs a
different encoding for a library's type has to wrap it in a newtype or copy it.

**cgp-serde replaces the per-trait derive with one general-purpose one.** A struct deriving
[`CgpData`](../../../cgp/reference/derives/derive_cgp_data.md), or the narrower field derives, exposes
its fields as type-level data: a list of named fields through
[`HasFields`](../../../cgp/reference/traits/has_fields.md), per-field access through `HasField`, and an
incremental builder through `BuildField`. `SerializeFields` and `DeserializeRecordFields` are written
once against that data and work for every struct that exposes it, so a library defines its types with
a dependency on `cgp` alone, and each application wires its own serialization for them. This is CGP's
[extensible records](../../../cgp/concepts/extensible-records.md) applied to serialization.

## What a struct still opts into

The approach removes the serialization-specific derive, not the derive altogether. Each direction
needs specific field traits:

- **Serializing** — `HasFields` to list the fields and `HasField` to read each one.
- **Deserializing** — `HasFields` to list the fields and `BuildField` to fill them through the optional
  builder.

`#[derive(CgpData)]` provides all three. The same derive also serves every other generic CGP provider
that works over fields, such as builders and structural casts, so one opt-in covers more than
serialization. A type that has not derived the field traits, including any foreign type whose owner did
not, cannot use the record providers; the [reflection comparison](../../../related-work/reflection.md)
sets this against Rust's proposed compile-time reflection, which is designed to need no opt-in.

## What it gives up

**The generic providers know only what the field list tells them: names, types, and order.** They have
no equivalent of the per-field attributes Serde's derive reads, so every field is written under its
Rust name, and nothing can be renamed, skipped, flattened, or defaulted when missing. Customizing
encoding happens per type instead, through the context: a field of type `Vec<u8>` is encoded however
the context encodes `Vec<u8>`. Two fields of the same type in one struct therefore cannot be encoded
differently, short of giving one of them a distinct type.

Three further limits come from the providers rather than the approach, and are recorded with them in
[records](../reference/records.md#known-issues): records are written as maps rather than structs,
without a declared length; tuple structs are rejected; and enums have no generic provider at all. The
field-list recursion is also monomorphized per struct, as Serde's derive output is, so the approach
saves writing the code rather than compiling it.

## Public material derived from this

The "Writing serializers" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the derive-free argument in the
repository README.
