# CGP v0.6.0 Release: Major ergonomic improvements for provider and context implementations

The release that made CGP code start to look like ordinary Rust: it introduces `#[cgp_impl]`, lets a
context own its wiring table, and removes `HasCgpProvider`.

- **URL**: <https://contextgeneric.dev/blog/v0-6-0-release>
- **Source**: [blog/2025-10-26-v0.6.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-10-26-v0.6.0-release.md)
- **Published**: 26 October 2025, tagged `release`
- **Release**: [v0.6.0](../../releases/v0-6-0.md)
- **Status**: Historical

## What it covers

Three connected changes, each with a before-and-after:

- **`#[cgp_impl]`:** a provider written like a blanket impl of the consumer trait, with the context in
  the `Self` position and the consumer-trait signatures, rewritten by the macro into the provider-trait
  shape. The post says this is presentation rather than mechanism, and that the presentation is the
  point.
- **Direct delegation on the context:** `delegate_components!` targets the context type, so `App` is
  its own lookup table and the `{Context}Components` struct goes. Beyond a small compile-time gain, a
  context can now implement a consumer trait directly for components it has not delegated, mixing
  hand-written and wired impls. That makes it safe to put `#[cgp_component]` on almost any existing
  trait without breaking its impls, which the post's `Hash` example shows.
- **Removing `HasCgpProvider`:** consumer-trait blanket impls now route through
  [`DelegateComponent`](../../cgp/reference/traits/delegate_component.md) as provider traits do. The
  post gives the history: the original design let several contexts share one provider table, presets
  made that unnecessary, and the trait survived only for compatibility. `#[cgp_context]` instead emits
  a blanket `impl<Name> DelegateComponent<Name> for App`, and `#[cgp_inherit]` is added for a context
  to inherit a preset.

The migration guide deprecates `#[cgp_context]` and `#[cgp_provider]`, recommending removing the first
and moving to `#[cgp_impl]` from the second, since mixing the two provider styles confuses contributors
new to CGP.

## How it relates to the knowledge base

- **Providers:** [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) is the form
  [writing-providers](../../cgp/guides/writing-providers.md) prescribes, with
  [`#[cgp_provider]`](../../cgp/reference/macros/cgp_provider.md) and
  [`#[cgp_new_provider]`](../../cgp/reference/macros/cgp_new_provider.md) the layers read rather than
  written.
- **Wiring:** direct delegation is how
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md) works throughout the
  base; the context-versus-aggregate distinction it sharpened is
  [aggregate providers](../../cgp/concepts/aggregate-providers.md), and the blanket impls are in
  [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md).
- **The `Hash` example:** the live site's [Introduction](../pages/introduction.md) opens with it, and
  the `v0.8.0` branch's Introduction has no code example. Adding CGP to an existing trait without
  breaking an impl answers the incremental-adoption question, per
  [message.md](../../communication-strategy/message.md#the-strengths-worth-advertising) and
  [message.md](../../communication-strategy/message.md#when-not-to-reach-for-cgp).

## Where it diverges from CGP v0.8.0

- **`#[cgp_context]` was removed outright in v0.7.0**, so the backward-compatibility mechanism this
  post introduces (the blanket `DelegateComponent` impl it generates) no longer exists either, and
  removing `#[cgp_context]` when upgrading is now mandatory.
- **`#[cgp_inherit]` is gone.** It went with the presets; a context now joins a namespace with a
  `namespace` statement inside
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md), per
  [namespaces](../../cgp/concepts/namespaces.md).
- **The consumer-trait blanket impl changed again in v0.7.0.** The post shows it performing a
  `DelegateComponent` lookup; v0.7.0 simplified it to `Context: Greeter<Context>`, since the provider
  trait's own blanket impl already does the lookup, so the generated code shown is one revision stale.
- **`#[cgp_impl]` gained implicit context types in v0.6.1.** Every example still writes
  `impl<Context> HttpRequestFetcher for Context`; the current form omits the generic and writes
  `impl HttpRequestFetcher` with `Self` bounds.
- **Dependencies are hand-written `where Self: ...` bounds**, where the idiom is
  [`#[uses(...)]`](../../cgp/reference/attributes/uses.md), and
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments did not yet exist. The
  hand-written `HasCount` getter would usually be an implicit argument today.

## Maintaining it

Leave it alone. It is the release note to read for why current CGP looks the way it does, and its
`HasCgpProvider` history is the only published account of that design's origin;
read it before anyone proposes reintroducing shared context providers. For current guidance on the
choice it settled, use [writing-providers](../../cgp/guides/writing-providers.md).
