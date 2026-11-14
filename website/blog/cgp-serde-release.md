# Announcing cgp-serde: A modular serialization library for Serde powered by CGP

The announcement for [cgp-serde](../../projects/cgp-serde/README.md), companion to the RustLab talk:
Serde's `Serialize` and `Deserialize` rebuilt as CGP components, two applications encoding the same
nested data into different JSON, and an arena-allocating deserializer that realizes the
context-and-capabilities proposal on stable Rust.

- **URL**: <https://contextgeneric.dev/blog/cgp-serde-release>
- **Source**: [blog/2025-11-03-cgp-serde-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-11-03-cgp-serde-release.md)
- **Published**: 3 November 2025, tagged `release`
- **Status**: Historical
- **Notice**: a note at the top of the post, written on the website's `v0.8.0` branch, links the [cgp-serde pages](https://contextgeneric.dev/docs/projects/cgp-serde/), per [projects/cgp-serde.md](../projects/cgp-serde.md); it is the sanctioned edit in [../AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#blog-posts) and changes no claim

## What it covers

Demonstration first, mechanism second:

- **The components:** `CanSerializeValue<Value>` and `CanDeserializeValue<'de, Value>` move Serde's
  `Self` into a `Value` parameter, leaving `Self` free to be a context the method reads dependencies
  from. Four overlapping providers (`UseSerde` for anything `Serialize`, `SerializeWithDisplay`,
  `SerializeBytes` for anything `AsRef<[u8]>`, `SerializeIterator` for anything iterable) would
  conflict as blanket impls of `Serialize` but coexist as providers.
- **The serialization demo, the post's strongest argument:** an encrypted-messaging library defines
  three nested types deriving only `CgpData`. Two applications wire different providers for `Vec<u8>`
  and `DateTime<Utc>` (hex and RFC 3339 against base64 and Unix timestamps) and produce structurally
  different JSON, shown in full, from wiring tables three lines apart. The library needs neither
  `serde` nor `cgp-serde`, because `SerializeFields` is generic over any `CgpData` struct, which the
  post frames as the answer to the orphan rule: library authors stop deriving third-party traits.
- **The deserialization demo:** the
  [context and capabilities](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/)
  proposal's own example. `DeserializeAndAllocate` moves an owned value into an arena reached from the
  context, producing `&'a Coord` values in a `Cluster<'a>`, which exercises lifetimes in component
  parameters and generic keys with lifetimes in the wiring table.
- **Implementation:** provider traits, the `#[cgp_impl]` desugaring, and type-level lookup tables,
  tracing `CanSerializeValue<Vec<EncryptedMessage>>` through `UseDelegate` down to `SerializeFields`.
- **Future work, candidly:** no enum serialization yet, only `deserialize_json_string` as a JSON
  helper, other formats untested, thin documentation, and no benchmark, with the hypothesis that
  `serde`'s generated `match` on string literals may beat `cgp-serde`'s sequential field-tag comparison
  when deserializing.

## How it relates to the knowledge base

- **The source to quote:** the [modular serialization example](../../examples/modular-serialization.md).
  The project is [projects/cgp-serde/](../../projects/cgp-serde/README.md), whose
  [issues](../../projects/cgp-serde/issues.md) record that all five future-work items remain open on
  the `v0.8.0` branch, the JSON-helper item narrower, since the reader provider accepts slices and
  `io::Read` and only the convenience method is limited to strings.
- **Concepts:** [coherence](../../cgp/concepts/coherence.md), which uses
  `UseSerde`/`SerializeBytes`/`SerializeWithDisplay` to illustrate incoherent implementations;
  [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md);
  [extensible records](../../cgp/concepts/extensible-records.md) via
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md);
  [dispatching](../../cgp/concepts/dispatching.md);
  [modular error handling](../../cgp/concepts/modular-error-handling.md); and
  [`Life`](../../cgp/reference/types/life.md).
- **Strategy assets:** the project's best answer to "what problem does this solve" for a reader
  indifferent to paradigms, because Serde and its orphan-rule pain are universally known, as
  [message.md](../../communication-strategy/message.md#the-problems-cgp-removes) asks of a lead. The
  "no `#[derive(Serialize)]` needed" result is a
  [selling point](../../communication-strategy/message.md#the-strengths-worth-advertising) no
  competing Rust approach matches, and the future-work section is the honesty
  [message.md](../../communication-strategy/message.md#the-objections-readers-bring) pairs with it.

## Where it diverges from CGP v0.8.0

- **`#[cgp_impl]` is used with an explicit generic context** (`impl<Context, Value> ValueSerializer<Value> for Context`),
  which v0.6.1 made unnecessary; the current form is `impl ValueSerializer<Value>` with `Self` bounds.
- **`derive_delegate: UseDelegate<Value>` with nested tables is the legacy dispatch form.** The idiom
  is the `open` statement of [`delegate_components!`](../../cgp/reference/macros/delegate_components.md)
  with `@`-path keys, per [dispatching-per-type](../../cgp/guides/dispatching-per-type.md); the
  [modular serialization example](../../examples/modular-serialization.md) shows that form.
- **`#[cgp_new_provider]` appears in the arena deserializer**, an inside-out provider impl.
- **Dependencies are hand-written `where` bounds** rather than
  [`#[uses(...)]`](../../cgp/reference/attributes/uses.md).
- **The blanket-impl walkthrough is one revision stale.** It shows the consumer trait doing its own
  `DelegateComponent` lookup; v0.7.0 simplified that to `Context: ValueSerializer<Context, Value>`.
- **One inconsistency to not copy:** the lookup-table section shows a `#[cgp_impl(Provider)]` block
  whose body uses the inside-out `Provider::Delegate::serialize` form, mixing the two styles.
- **The two "Full Example" links point at the `main` branch**, whose `messages.rs` and
  `arena_simplified.rs` are the 0.2.0 tests wired with `UseDelegate` tables. The `v0.8.0` versions,
  wired with `open`, are in [projects/cgp-serde/examples/](../../projects/cgp-serde/examples/README.md).
- **The record serializer is named `SerializeFields` in the post.** On the `v0.8.0` branch it is
  `SerializeRecordFields`, matching `DeserializeRecordFields`.
- **`cgp-serde` has moved on.** The repository tracks `cgp` 0.8.0 at crate version 0.2.0, so the post
  describes the 0.1 release.

## Maintaining it

Leave it alone. Its argument is the most reusable on the blog: rebuild it from the
[modular serialization example](../../examples/modular-serialization.md) and
[coherence](../../cgp/concepts/coherence.md) rather than quoting the post's code. A documented
`cgp-serde` release would get a fresh post, with its future-work section re-checked rather than
carried over.
