# cgp-serde and Serde

cgp-serde is built on Serde and depends on it, so the comparison is between two ways of implementing
Serde's data-type layer: Serde's own `Serialize` and `Deserialize` traits with their derive, and
cgp-serde's components with their providers. This document records what cgp-serde keeps from Serde,
what it adds, how Serde's common idioms map onto it, what it lacks, and when plain Serde is the better
choice. It is written to be fair to Serde, which is the mature, widely adopted library of the two and
the foundation cgp-serde stands on.

## What is kept

Everything below Serde's data-type layer is shared rather than compared. cgp-serde uses Serde's data
model, its `Serializer` and `Deserializer` traits, and every format built on them, and it reuses any
existing `Serialize` or `Deserialize` impl through [`UseSerde`](reference/use-serde.md). A project can
therefore adopt cgp-serde for some types and keep Serde's derive for the rest, in the same value; the
[bridge](architecture/serde-bridge.md) explains how the two meet.

## What cgp-serde adds

cgp-serde adds four things Serde's trait design cannot express, each following from moving the encoded
type out of `Self`:

- **Per-application encodings.** Two contexts can encode the same type differently, such as `Vec<u8>`
  as hex in one application and base64 in another, with the choice reaching every nested occurrence.
  In Serde, a type has one `Serialize` impl for the whole program.
- **Overlapping and orphan implementations.** Providers such as "any `Display` type as a string" and
  "any `AsRef<[u8]>` type as bytes" coexist, and a crate can provide an encoding for a type it does not
  own. Serde's coherence rules allow at most one blanket impl and forbid implementing `Serialize` for a
  foreign type.
- **No serialization derive on data types.** A struct deriving CGP's general field traits serializes
  through generic providers, so a data crate needs no dependency on `serde`; see
  [derive-free records](architecture/derive-free-records.md).
- **Services during deserialization.** A provider can draw values from the context, such as an arena
  to allocate into; see [context services](architecture/context-services.md). Serde supports stateful
  deserialization only through hand-written `DeserializeSeed` impls, which its derive does not produce.

## How Serde's idioms map

Many Serde features exist to work around the one-impl-per-type rule, and in cgp-serde the same need is
met by wiring instead. The mapping is not one to one, because Serde's attributes are per field while
cgp-serde's choices are per type:

| Serde idiom | cgp-serde equivalent |
|---|---|
| `#[serde(with = "hex")]` on a field | wire the field's type to `SerializeHex` in the context; every field of that type follows |
| `serialize_with` / `deserialize_with` | write a provider and wire the type to it |
| a newtype wrapper to change a type's encoding | wire a different provider in a different context |
| `#[serde(remote = "…")]` for a foreign type | not needed for encoding choice; a foreign type is wired to a provider directly |
| `#[derive(Serialize, Deserialize)]` on a struct | derive `CgpData`, wire the struct to `SerializeFields` and `DeserializeRecordFields` |
| a hand-written `DeserializeSeed` for state | a provider that takes the state from the context |
| zero-copy `&'de str` fields | wire `&'a str` to `UseSerde` and deserialize from a borrowing reader |

## What cgp-serde lacks

Serde's derive carries a large set of behaviors cgp-serde has no equivalent for, and a project that
relies on them cannot move those types to cgp-serde yet:

- **Field and container attributes** — `rename`, `rename_all`, `skip`, `flatten`, `default`,
  `deny_unknown_fields`, and the rest. Every field is written under its Rust name and must be present.
- **Enums** — Serde derives all four enum representations; cgp-serde has no generic enum provider.
- **Tuple structs and tuples** — Serde derives them; cgp-serde's record providers reject tuple structs,
  and no provider handles tuples.
- **Recursive types** — Serde derives them without difficulty; cgp-serde's generic providers fail to
  compile for them.
- **Binary formats** — Serde's derived impls declare lengths and struct names, which formats such as
  postcard rely on; cgp-serde's record and sequence providers do neither.
- **Maturity** — Serde is extensively tested, documented, and benchmarked; cgp-serde is a proof of
  concept with thin tests, no rustdoc, and no benchmark. See [issues.md](issues.md) and
  [testing.md](testing.md).

The performance question is open rather than answered. Provider selection is resolved at compile time,
so wiring adds no runtime lookup, but the generic record deserializer allocates and compares keys where
Serde's derive matches them against literals, and no measurement exists either way.

## When plain Serde is the better choice

Plain Serde is the right tool whenever the one-impl-per-type rule does not bind: a program that encodes
each type one way needs no per-context choice, and Serde's derive gives it attributes, enums, binary
formats, and a mature implementation that cgp-serde does not match. It is also the right choice for any
type that needs the attributes or representations listed above, for binary formats, and for a team that
has no other use for CGP, since cgp-serde's wiring and diagnostics carry CGP's learning cost.

cgp-serde earns its place where the rule does bind: the same types encoded differently by different
applications, encodings for types a crate does not own, data crates that should not depend on
`serde`, and deserialization that needs services Serde's traits have no room for. Because the two
interoperate through `UseSerde` and the adapters, a project can use each for the types it suits.

## Public material derived from this

The page on what the library does not do in the planned
[cgp-serde deep dive](../../website/deep-dives/cgp-serde.md), and any comparison with Serde in public
writing, which [message.md](../../communication-strategy/message.md) requires to state where the
simpler tool wins.
