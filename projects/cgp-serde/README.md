# cgp-serde

`cgp-serde` rebuilds [Serde](https://serde.rs/)'s `Serialize` and `Deserialize` as CGP components, so
that how each value type is encoded stops being a fixed property of the type and becomes a per-context
wiring choice — which makes overlapping and orphan serialization implementations legal, and lets a
deserializer draw capabilities such as an arena allocator from the context it runs in.

- **Repository** — <https://github.com/contextgeneric/cgp-serde>
- **Local checkout** — `../cgp-serde`, per [sibling-projects.md](../../sibling-projects.md)
- **Crates** — `cgp-serde` and companions at 0.2.0
- **Tracks** — `cgp` 0.8.0-alpha
- **Status** — Proof of concept; usable, with named gaps

## What it is

The library defines two components that mirror Serde's traits with one structural change:
`CanSerializeValue<Value>` and `CanDeserializeValue<'de, Value>` move the original `Self` into an
explicit `Value` parameter, leaving `Self` free to be a **context**. That single move buys two things
at once. Because the implementing `Self` type is now a provider struct the library owns, overlapping
implementations become legal — `UseSerde` for anything already implementing `Serialize`,
`SerializeBytes` for anything `AsRef<[u8]>`, `SerializeWithDisplay` for anything `Display`, and
`SerializeIterator` for anything iterable can all coexist, where any two of them as blanket `Serialize`
impls would conflict. And because the methods now take `&self`, an implementation can reach into the
context for runtime dependencies, which is what makes context-dependent deserialization possible.

The practical result is that two applications can wire different providers for `Vec<u8>` and
`DateTime<Utc>` and produce structurally different JSON from the same value, differing only in a few
lines of wiring. The library stays compatible with the existing Serde ecosystem in both directions: a
`SerializeWithContext` wrapper pairs a value with its context to satisfy an ordinary `Serialize`
bound, so `serde_json::to_string` works unchanged.

Its most consequential property is that a data type needs **no serialization-specific derive at all**.
A struct deriving [`CgpData`](../../cgp/reference/derives/derive_cgp_data.md) can be serialized by a
generic `SerializeFields` provider, so a library can expose serializable types without depending on
`serde` or `cgp-serde` — which is a direct structural answer to the orphan-rule pressure that pushes
library authors into deriving every popular trait.

## How it is organized

`cgp-serde` holds the two components, the `SerializeWithContext` and `DeserializeWithContext` adapter
types, and the core providers: `serde` for delegating to the original traits, `bytes`, `display`,
`string`, `iterator`, `deref`, `from` and `try_from` for conversions, `fields` and `record` for
datatype-generic struct handling, `default`, and `extend`. `cgp-serde-extra` adds the encoding
providers the demos turn on — `hex`, `base64`, `date`, and `timestamp`. `cgp-serde-json` carries the
JSON-specific helpers, `cgp-serde-alloc` the allocation traits and providers, and
`cgp-serde-typed-arena` the [`typed-arena`](https://docs.rs/typed-arena/) binding behind the arena
demonstration. `cgp-serde-tests` holds the worked examples, including the encrypted-messages and
arena scenarios.

## What CGP it exercises

The library is the clearest available demonstration of
[bypassing coherence](../../cgp/concepts/coherence.md) — so much so that the concept document uses
`cgp-serde`'s own providers as its worked illustration. The trait split is
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md) via
[`#[cgp_component]`](../../cgp/reference/macros/cgp_component.md), with implementations written as
[`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) providers.

Beyond that it exercises three things that few other codebases do. Derive-free struct handling rests
on [extensible records](../../cgp/concepts/extensible-records.md) and
[`HasFields`](../../cgp/reference/traits/has_fields.md), with deserialization using the optional
builder from [optional fields](../../cgp/reference/traits/optional_fields.md) because a partial record
being filled from dynamic input cannot change type on each field. Per-value-type routing is
[dispatching](../../cgp/concepts/dispatching.md). And the arena deserializer requires **lifetimes in
component parameters** — `CanDeserializeValue<'de, Value>` — which are lifted into
[`Life`](../../cgp/reference/types/life.md) inside
[`IsProviderFor`](../../cgp/reference/traits/is_provider_for.md) and must be named that way in a
[`check_components!`](../../cgp/reference/macros/check_components.md) assertion; that is the least
common corner of CGP any project currently uses. Errors go through
[modular error handling](../../cgp/concepts/modular-error-handling.md), and the type-level string
support that lets a generic provider hand a field name to Serde as a `&'static str` is
[`StaticFormat` / `StaticString`](../../cgp/reference/traits/static_format.md).

## How it relates to the rest of the base

The [modular serialization example](../../examples/modular-serialization.md) re-derives the project's
scenario in verified current syntax and is what other documents quote. The
[announcement post](../../website/blog/cgp-serde-release.md) is the fullest published account, written
against CGP v0.6.x with wiring that has since changed — that document records the specifics. The
project was also the live demonstration in the
[RustLab 2025 talk](../../website/blog/rustlab-2025-coherence.md).

For the communication strategy this is the project's strongest argument, because Serde is universally
known and the orphan-rule pain around it is universally felt; the framing belongs in
[message.md](../../communication-strategy/message.md#the-problems-cgp-removes) and the derive-free result in
[message.md](../../communication-strategy/message.md#the-capabilities-worth-advertising).

## Status and gaps

The project tracks the current library at `cgp` 0.8.0-alpha and crate version 0.2.0, so its source is
a reliable reference for current CGP. Four gaps are named by the project itself and remain open.
Serialization providers for **enums and extensible variants** are not implemented, so only structs can
be handled datatype-generically. JSON helpers are limited to deserializing from a string, with no
`from_slice` or `from_value` equivalents. Other Serde formats are untested, though serialization
through the `SerializeWithContext` wrapper should work with any of them. And no **benchmark** has been
run — the open question being whether a generic field-matching implementation can match the
`match`-on-string-literals code Serde's derive generates, which the project flags as the most likely
place a gap would appear.

Its documentation is thin: the README summarizes the components and points at the announcement post
for everything else. Expanding it is an open task, and this document is deliberately brief pending
that work.
