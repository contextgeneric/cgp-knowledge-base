# Announcing cgp-serde: A modular serialization library for Serde powered by CGP

The announcement for [cgp-serde](../../projects/cgp-serde/README.md), and the companion piece to the
RustLab talk. It rebuilds Serde's `Serialize` and `Deserialize` as CGP components, shows two
applications encoding the same nested data into different JSON, and demonstrates an
arena-allocating deserializer that realizes the context-and-capabilities proposal on stable Rust.

- **URL** — <https://contextgeneric.dev/blog/cgp-serde-release>
- **Source** — [blog/2025-11-03-cgp-serde-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-11-03-cgp-serde-release.md)
- **Published** — 3 November 2025, tagged `release`
- **Status** — Historical

## What it covers

The post is structured as demonstration first, mechanism second.

It begins by redefining the two Serde traits as CGP components: `CanSerializeValue<Value>` and
`CanDeserializeValue<'de, Value>` move the original `Self` into an explicit `Value` parameter, leaving
`Self` free to be a *context* that the method can read dependencies from. It then writes four
deliberately overlapping providers — `UseSerde` for anything already implementing `Serialize`,
`SerializeWithDisplay`, `SerializeBytes` for anything `AsRef<[u8]>`, and `SerializeIterator` for
anything iterable — and points out that any two of them would be rejected as conflicting blanket impls
of `Serialize`, while all four coexist as providers.

The **serialization demo** is the strongest concrete argument in the post. An encrypted-messaging
library defines three nested data types deriving only `CgpData`. Two applications then wire different
providers for `Vec<u8>` and `DateTime<Utc>` — hex and RFC 3339 versus base64 and Unix timestamps —
and produce structurally different JSON from the same value, with the two wiring tables differing by
three lines. The post shows both JSON outputs in full. Its sharpest observation is that the library
needs neither `serde` nor `cgp-serde` as a dependency: deriving `CgpData` is enough, because
`SerializeFields` is generic over any struct that does, which the post frames as the real answer to
the orphan rule — library authors stop being asked to derive third-party traits at all.

The **deserialization demo** implements the [context and capabilities](https://tmandry.gitlab.io/blog/posts/2021-12-21-context-capabilities/)
proposal's own motivating example. A `DeserializeAndAllocate` provider deserializes an owned value and
moves it into an arena reached from the context, producing `&'a Coord` values stored in a
`Cluster<'a>`. This requires lifetimes in component parameters and generic keys with lifetimes in the
wiring table, both of which the post exercises.

The **implementation** section explains provider traits, the `#[cgp_impl]` desugaring, and type-level
lookup tables, tracing a full recursive resolution of `CanSerializeValue<Vec<EncryptedMessage>>`
through `UseDelegate` down to `SerializeFields`. The **future work** section is candid: enum variants
are not yet supported for serialization, only `deserialize_json_string` exists as a JSON helper, other
formats are untested, documentation is thin, and no benchmark has been run — with a specific
hypothesis that `serde`'s macro-generated `match` on string literals may beat `cgp-serde`'s sequential
field-tag comparison during deserialization.

## How it relates to the knowledge base

The scenario is re-derived in current syntax as the
[modular serialization example](../../examples/modular-serialization.md), which is the source to
quote. The project is documented at [projects/cgp-serde/](../../projects/cgp-serde/README.md).

The central argument is [coherence](../../cgp/concepts/coherence.md) — indeed
`UseSerde`/`SerializeBytes`/`SerializeWithDisplay` are the exact providers that concept document uses
to illustrate incoherent implementations. The trait split is
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md); the derive-free
struct serialization is [extensible records](../../cgp/concepts/extensible-records.md) via
[`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md); the per-value-type routing is
[dispatching](../../cgp/concepts/dispatching.md); the error wiring is
[modular error handling](../../cgp/concepts/modular-error-handling.md); and the lifetimes in component
parameters are [`Life`](../../cgp/reference/types/life.md).

Two things make this post disproportionately useful to the communication strategy. It is the project's
best worked answer to "what problem does this solve" for a reader who does not care about paradigms,
because Serde is universally known and the orphan-rule pain around it is universally felt — which is
what [message.md](../../communication-strategy/message.md#the-problems-cgp-removes) asks a lead to be. And the
"you don't even need `#[derive(Serialize)]`" result is a genuine
[selling point](../../communication-strategy/message.md#the-capabilities-worth-advertising) that no competing approach in Rust can
match. The candid future-work section is the honesty that
[message.md](../../communication-strategy/message.md#the-objections-readers-bring) requires be paired with those claims.

## Where it diverges from CGP v0.8.0

- **`#[cgp_impl]` is used with an explicit generic context** — `impl<Context, Value> ValueSerializer<Value> for Context` —
  which v0.6.1 made unnecessary. The current form omits the generic and writes `impl ValueSerializer<Value>`
  with `Self` bounds.
- **`derive_delegate: UseDelegate<Value>` with nested tables is the legacy dispatch form.** The
  current idiom is the `open` statement of
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md) with `@`-path keys, per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md); the
  [modular serialization example](../../examples/modular-serialization.md) shows the same wiring in
  that form.
- **`#[cgp_new_provider]` appears in the arena deserializer**, an inside-out provider impl.
- **Dependencies are hand-written `where` bounds** rather than
  [`#[uses(...)]`](../../cgp/reference/attributes/uses.md).
- **The blanket-impl walkthrough is one revision stale.** It shows the consumer trait performing its
  own `DelegateComponent` lookup; v0.7.0 simplified that to `Context: ValueSerializer<Context, Value>`.
- **One inconsistency to not copy:** the section on lookup-table implementation shows a
  `#[cgp_impl(Provider)]` block whose body still uses the inside-out `Provider::Delegate::serialize`
  form, mixing the two styles in one snippet.
- **`cgp-serde` itself has moved on.** The repository now tracks `cgp` 0.8.0-alpha at crate version
  0.2.0, so the post describes the 0.1 release rather than the current library.

## Maintaining it

Leave it alone. Of all the posts on the site this is the one whose *argument* is most worth reusing —
a widely-known library, a pain every Rust developer has met, and a result no alternative delivers — so
when a new piece needs that argument, rebuild it from the
[modular serialization example](../../examples/modular-serialization.md) and
[coherence](../../cgp/concepts/coherence.md) rather than quoting this post's code. If `cgp-serde` cuts
a documented release, a fresh post rather than a revision is the right form, and its future-work
section should be re-checked against what has since been implemented rather than carried over.
