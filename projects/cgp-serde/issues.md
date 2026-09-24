# Issues

This document records what is wrong with or missing from cgp-serde on the `v0.8.0` branch, grouped as
defects, missing features, and housekeeping. Every entry was confirmed against the source with a probe
build unless it says otherwise. Remove an entry in the same change that fixes it in the project, per
[../AGENTS.md](../AGENTS.md#the-shape-of-a-project-section). The reference documents carry the same
issues in their per-provider Known issues sections, with the behavior in full.

## Defects

A defect is behavior that is wrong for the input it is given.

### `SerializeBytes` output cannot be read back from JSON

`SerializeBytes` serializes bytes with `serialize_bytes`, which `serde_json` writes as an array of
numbers, but deserializes them only from an unescaped JSON string. With `Vec<u8>` wired to
`SerializeBytes` in both directions, `vec![1, 2, 3]` serializes to `[1,2,3]`, and reading `[1,2,3]` back
fails with `invalid type: sequence, expected bytes`. The two directions of one provider disagree about
the format. See [strings and bytes](reference/strings-and-bytes.md#serializebytes).

### The byte providers reject owned bytes

The visitor behind `SerializeBytes` and `TryDeserializeBytes` implements only `visit_borrowed_bytes`, so
any bytes the deserializer must copy are rejected. A JSON string with an escape sequence, such as
`"a\nb"`, fails with `invalid type: byte array, expected bytes`, and so does every input read through a
`serde_json::de::IoRead`. Accepting them needs both the owned visitor methods, `visit_bytes` and
`visit_byte_buf`, and a bound on the value that does not tie it to the input's lifetime, since the
providers require `From<&'de [u8]>` or `TryFrom<&'de [u8]>`. See
[strings and bytes](reference/strings-and-bytes.md#known-issues).

### `DeserializeWithFromStr` rejects escaped strings and reader input

`DeserializeWithFromStr` asks the context for a `&'de str` borrowed from the input, so any string the
input cannot lend fails before parsing. With `u64` wired to `DeserializeWithFromStr` and `&'a str` to
`UseSerde`, the JSON string `"42"` parses, but the same number written with an escape sequence fails
with `invalid type: string "42", expected a borrowed string`, and every string read through an
`IoRead` fails the same way. Re-entering for an owned `String` would accept them. See
[conversions](reference/conversions.md#deserializewithfromstr).

### Records and sequences do not declare their length

`SerializeFields` calls `serialize_map(None)` and `SerializeIterator` calls `serialize_seq(None)`, even
when the length is known, so a format that must write a length before the elements rejects them.
`postcard::to_allocvec` fails with `SerializeSeqLengthUnknown` on any struct or collection. See
[records](reference/records.md#known-issues) and [collections](reference/collections.md#known-issues).

## Missing features

A missing feature is behavior the library does not attempt. Each is documented where it applies.

- **Enums** — no provider serializes or deserializes an enum generically; an enum works only through
  `UseSerde`. See [the project README](README.md#status-and-gaps).
- **Recursive data types** — a type that contains itself fails to compile with `E0275` through the
  generic providers and needs a hand-written provider. See
  [re-entrant providers](architecture/reentrant-providers.md#what-re-entry-requires-of-a-context).
- **Tuple structs** — the record providers reject them, because `Index<N>` tags do not implement
  `StaticString`. See [records](reference/records.md).
- **Serde's field attributes** — there is no equivalent of renaming, skipping, flattening,
  `#[serde(default)]`, or `deny_unknown_fields`, and CGP's defaulting finalize is not offered for
  missing fields. See [`DeserializeRecordFields`](reference/records.md#deserializerecordfields) and
  [derive-free records](architecture/derive-free-records.md#what-it-gives-up).
- **Struct and map forms** — records are written with `serialize_map` rather than `serialize_struct`,
  maps are written and read as sequences of pairs, and tuples have no provider. See
  [collections](reference/collections.md).
- **Unsized values** — `CanSerializeValue` admits `?Sized` values, but no provider accepts one, so
  `str` and slices cannot be wired. See [components](reference/components.md#canserializevalue).
- **Encoding variants** — base64 has no URL-safe or unpadded variant, and timestamps have no sub-second
  variant. See [encodings](reference/encodings.md).
- **JSON conveniences** — there is no serializing convenience method, no pretty-printing or
  `io::Write` provider, and the string helper cannot produce values that borrow from its input. See
  [JSON providers](reference/json.md).
- **Other formats** — no format other than JSON has providers or helpers. See
  [formats](guides/formats.md).
- **A namespace of defaults** — the library publishes no namespace, so every context spells out its
  full wiring. The website's plan tracks this as task DC3 in
  [tasks.md](../../website/tasks.md).
- **Performance evidence** — no benchmark has been run. The likeliest cost is in
  `DeserializeRecordFields`, which allocates each key as a `String` and compares it against each field
  name in turn.
- **Documentation in the code** — no public item has a doc comment, so the docs.rs pages list items
  without explanation.

## Housekeeping

Housekeeping items affect neither behavior nor features but mislead a reader or a tool.

- **Legacy dispatch attributes.** `CanSerializeValue`, `CanDeserializeValue`, and `HasArena` carry
  `#[derive_delegate(UseDelegate<…>)]`, which only `UseDelegate` tables need; every context on the
  branch uses `open`. Removing them is breaking for downstream `UseDelegate` users, and the website's
  task DC3 accepts that.
- **Repository metadata.** The workspace `Cargo.toml` sets `repository` to
  `https://github.com/contextgeneric/cgp`, so all five published crates point at the CGP repository
  rather than cgp-serde's.
- **Crate descriptions.** `cgp-serde-alloc` and `cgp-serde-typed-arena` share the description
  "Arena-based deserialization using cgp-serde", although only the second involves an arena, and the
  test crate repeats the core crate's description.
- **Version numbers.** The `v0.8.0` branch still carries version 0.2.0 in every manifest, the same
  number as the published crates built on `cgp` 0.7.0.
- **The repository README.** It shows the component definitions in the pre-0.8 attribute syntax and
  defers everything else to the announcement post.
- **Tests that assert nothing.** `messages.rs` prints both applications' JSON without checking it, and
  seven providers are never run; see [testing.md](testing.md).
- **A duplicated seed.** `DeserializeExtend` defines a private seed identical in behavior to the public
  `DeserializeWithContext`.

## Public material derived from this

The page on what the library does not do in the planned
[cgp-serde deep dive](../../website/deep-dives/cgp-serde.md), which the deep-dive plan requires to be
kept rather than trimmed as the library matures.
