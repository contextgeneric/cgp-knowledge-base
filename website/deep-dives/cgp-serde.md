# cgp-serde deep dive

Serde's `Serialize` and `Deserialize` rebuilt as CGP components, so that how a value is encoded becomes
a per-application wiring choice instead of one fixed implementation baked into the type. The clearest
demonstration of the coherence bypass on a trait every Rust developer already knows.

- **Planned URL** — `https://contextgeneric.dev/docs/deep-dives/cgp-serde/`
- **Source post** — [cgp-serde: Serde as CGP components](../blog/cgp-serde-release.md), 2025-11-03,
  ~6,900 words, written against `cgp-serde` 0.1
- **Code base** — [`cgp-serde`](https://github.com/contextgeneric/cgp-serde), tracking `cgp`
  0.8.0-alpha at crate version 0.2.0, locally at `../cgp-serde`
- **Status** — planned; no page written

## What it covers, and why it needs this format

cgp-serde is the argument that CGP's coherence bypass is worth having, made on ground the reader
already occupies. Serde is universally used and its limitations are universally felt: one `Serialize`
impl per type, chosen by whoever owns the type, so an application that wants bytes as hex where another
wants base64 must newtype or fork. cgp-serde makes the choice a wiring line, and gets a second result
almost for free — a type needs no serialization derive at all, because deriving the general-purpose
`CgpData` is enough.

The format helps this deep dive differently from the other two. It is the **shortest** source post of
the three and does not urgently need splitting for length. What it needs is to stop being a *release
announcement*: the post is framed around what version 0.1 shipped, spends its opening on the release,
and trails into future work. As a living document under `docs/`, the same material becomes the standing
answer to "can CGP do something real", which is the question the evaluator profile actually asks.

## The page split

Five pages, one running example — the `Payload` struct with a `Vec<u8>` field that two applications
encode differently — carried throughout.

**`index.md` — one type, two encodings** (~700 words). Open on the constraint: Serde gives a type one
`Serialize` impl, chosen by whoever owns the type. Show the two-application payoff immediately, then
the derive-free result, then the shape of the rest. This page is the deep dive's whole pitch and should
work standing alone.

**1 — Serialization as a component** (~1,200 words). `CanSerializeValue<Value>` and
`CanDeserializeValue<'de, Value>`: why the value moves out of `Self` into a parameter, what that buys,
and how it differs from `serde::Serialize`. The page where the coherence argument is made concretely —
and the one that should link to *Why CGP exists* rather than re-arguing it.

**2 — Writing serializers** (~1,200 words). The provider family: `UseSerde` deferring to an existing
Serde impl, `SerializeString`, `SerializeHex`, `SerializeFields` for a whole record. Several of these
overlap freely on the same type, which is the point.

**3 — Wiring an application** (~1,200 words). The `open` statement and `@`-path per-type dispatch, then
the payoff: two contexts, the same `Payload`, different JSON. The page most changed from the post, and
the one whose code the repository's tests already carry in current form.

**4 — Arena-allocating deserialization** (~1,200 words). The lifetime-carrying component and the
context-supplied arena — the most advanced thing cgp-serde does and the best evidence that the approach
scales past toy cases.

**5 — What it does not do** (~800 words). The honest gaps: what Serde does that cgp-serde does not, the
maturity of the crate, and when plain Serde is simply the right tool. The post's future-work section
converted from a roadmap into a boundary.

## What changes from the source post

**The `#[cgp_impl]` form loses its explicit context.** The post writes
`impl<Context, Value> ValueSerializer<Value> for Context`, which v0.6.1 made unnecessary; the current
form is `impl ValueSerializer<Value>` with `Self` bounds. The repository is already converted.

**`UseDelegate` tables become `open` and `@`-paths.** This is the change the post most needs and the one
the repository has already made — its tests wire with `open { ValueSerializerComponent, ... };` followed
by `@ValueSerializerComponent.Vec<u8>: SerializeHex,`. Take page 3's code from
`crates/cgp-serde-tests/src/tests/basic.rs` rather than from the post.

**`#[cgp_new_provider]` disappears from the arena deserializer**, the post's one remaining inside-out
provider.

**Dependencies become `#[uses(...)]`.** Already done in the repository, which is the heaviest user of
`#[uses]` of the four code bases.

**The blanket-impl walkthrough is one revision stale.** The post shows the consumer trait performing its
own `DelegateComponent` lookup; v0.7.0 simplified that to `Context: ValueSerializer<Context, Value>`.
This material is a candidate to cut entirely rather than update — it is *How CGP works*, and page 1
should link there.

**One inconsistency must not be copied.** The post's lookup-table section shows a `#[cgp_impl(Provider)]`
block whose body still uses the inside-out `Provider::Delegate::serialize` form, mixing two styles in one
snippet.

**The version framing goes.** The post describes the 0.1 release; the crate is at 0.2.0. A living
document should not lead with a version at all.

## Source-code changes needed

cgp-serde is the most idiomatic of the four repositories at the provider level and needs the least work.
Its one structural gap is at the wiring level and is an opportunity rather than a defect.

### The opportunity: publish a namespace

**cgp-serde defines no namespace.** There is not a single `cgp_namespace!` in the repository, so every
context spells out its complete wiring — `crates/cgp-serde-tests/src/tests/basic.rs` lists the error
type, the error raiser, four serializer entries, three deserializer entries, and two JSON codec entries
before it can serialize anything.

This is exactly the problem namespaces exist to solve, and Hypershell already shows the answer: a
library publishes a namespace, registers its components into it with `#[prefix(...)]`, and an
application joins it with one line and overrides only what it cares about. A `CgpSerdeNamespace`
carrying the sensible defaults — `UseSerde` for the primitives, `SerializeFields` for records, the JSON
codec — would turn those test contexts into a `namespace CgpSerdeNamespace;` line plus the two or three
entries that are actually application-specific.

**This is the deep dive's strongest available demonstration and it does not exist yet.** Page 3's
payoff — two applications differing by a handful of lines — is far more striking when the shared part is
one line than when both contexts list a dozen entries. It is also a genuine library improvement rather
than a documentation convenience, so it belongs in the crate regardless. Treat it as the one substantial
code change this deep dive asks for, and note that it is a design decision about what the defaults
should be, not a mechanical conversion.

### Smaller items

**Consider dropping the three `#[derive_delegate(UseDelegate<...>)]` attributes** on
`crates/cgp-serde/src/components/serialize.rs`, `deserialize.rs`, and
`crates/cgp-serde-typed-arena/src/traits/has_arena.rs`. Now that every context wires through `open`,
these are needed only by a downstream user still building `UseDelegate<new ...>` tables, so removing
them is a **breaking change** and a deliberate call. The deep dive need not show them either way.

**Check the two getter traits** against the implicit-argument rule in
[reading-context-fields](../../cgp/guides/reading-context-fields.md). The arena getter is likely a
legitimate exception — it carries an associated type and is required as a named capability — but the
second should be confirmed.

**Ignore `target/package/`.** It holds packaged copies of 0.2.0 containing the old
`UseDelegate<new SerializerComponents { ... }>` tables, and a grep for legacy constructs will find them.
They are build artifacts, not source.

## How it relates to the knowledge base

The verified counterpart is the [modular serialization example](../../examples/modular-serialization.md),
which works the whole progression through in current form and is the source to quote. The argument on
page 1 is [bypassing coherence](../../cgp/concepts/coherence.md) and
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), with the
[modularity hierarchy](../../cgp/concepts/modularity-hierarchy.md) explaining why the value moves out of
`Self`. Page 3's mechanism is [namespaces](../../cgp/concepts/namespaces.md) and the `open` statement of
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md); page 2's derive-free result
rests on [extensible records](../../cgp/concepts/extensible-records.md). The project entry is
[projects/cgp-serde](../../projects/cgp-serde/README.md), which also records the crate's open gaps and is
the source for page 5.

For framing, this deep dive is the worked instance of the
[strongest lead pain](../../communication-strategy/message.md#the-problems-cgp-removes) — the
implementations Rust rejects outright — which is why the [homepage guide](../writing-guides/homepage.md)
uses a serialization contrast for its hero code. The two should stay consistent.

## Maintaining it

This deep dive is the one most likely to be read by an evaluator deciding whether CGP is real, so its
**page 5 is load-bearing** and must not be quietly trimmed as the crate matures — what changes is its
contents, not its existence.

If the namespace above is built, revisit page 3 rather than patching it: the whole page is better when
the shared wiring is one line, and the deep dive should be written against that shape rather than
retrofitted to it.
