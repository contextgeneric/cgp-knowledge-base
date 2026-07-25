# CGP v0.6.0 Release: Major ergonomic improvements for provider and context implementations

The release that made CGP code start to look like ordinary Rust. It introduces `#[cgp_impl]`, lets a
context own its wiring table directly, and removes `HasCgpProvider` — three changes that together
retired the two constructs most responsible for CGP looking alien.

- **URL** — <https://contextgeneric.dev/blog/v0-6-0-release>
- **Source** — [blog/2025-10-26-v0.6.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-10-26-v0.6.0-release.md)
- **Published** — 26 October 2025, tagged `release`
- **Release** — [v0.6.0](../../releases/v0-6-0.md)
- **Status** — Historical

## What it covers

Three connected changes, each explained with a before-and-after.

**`#[cgp_impl]`** lets a provider be written as if it were a blanket impl of the consumer trait: the
context stays in the `Self` position, methods keep `&self` and their consumer-trait signatures, and
the macro rewrites everything into the provider-trait shape. The post is explicit that this is
presentation rather than mechanism — it expands to the same thing `#[cgp_provider]` produced — but
that the presentation is the point.

**Direct delegation on the context** removes the separate `{Context}Components` provider struct.
`delegate_components!` can now target the context type itself, so `App` is its own lookup table. The
post notes a small compile-time benefit from removing a level of indirection, and a larger consequence:
because the consumer-trait blanket impl no longer goes through a per-context provider, a context can
now implement a consumer trait *directly* for components it has not delegated, mixing hand-written
impls with wired ones. This in turn is what makes it safe to apply `#[cgp_component]` to almost any
existing trait without breaking its existing implementations — the `Hash` example the site's
[Introduction](../site-structure.md) still leads with.

**Removing `HasCgpProvider`** is what enabled the above. Consumer-trait blanket impls now route
through [`DelegateComponent`](../../cgp/reference/traits/delegate_component.md) exactly as provider
traits do. The post gives the history: the original design let several contexts share one provider
table, presets made that unnecessary, and the trait survived only for compatibility. Backward
compatibility was preserved by making `#[cgp_context]` emit a blanket
`impl<Name> DelegateComponent<Name> for App` instead, and `#[cgp_inherit]` was added as the clearer
way for a context to inherit a preset.

The migration guide deprecates both `#[cgp_context]` and `#[cgp_provider]`, recommending removal of
the former and migration to `#[cgp_impl]` for the latter — with a note that mixing the two provider
styles confuses contributors unfamiliar with CGP.

## How it relates to the knowledge base

Both surviving changes are now baseline. [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) is
the form [writing-providers](../../cgp/guides/writing-providers.md) prescribes, with
[`#[cgp_provider]`](../../cgp/reference/macros/cgp_provider.md) and
[`#[cgp_new_provider]`](../../cgp/reference/macros/cgp_new_provider.md) documented as the lower layers
you read rather than write. Direct delegation on the context is how
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md) works throughout the base,
and the distinction between a context and an aggregate provider that the change sharpened is
[aggregate providers](../../cgp/concepts/aggregate-providers.md). The blanket impls that changed are
described in [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md).

The post's `Hash` example is the origin of the framing the
[Introduction page](../site-structure.md) still opens with, and it is a strong one for
[selling-points.md](../../communication-strategy/selling-points.md): CGP can be added to an existing
trait without breaking a single existing implementation, which is the most direct answer available to
the incremental-adoption question in
[positioning.md](../../communication-strategy/positioning.md).

## Where it diverges from CGP v0.8.0

- **`#[cgp_context]` was removed outright in v0.7.0**, so the backward-compatibility mechanism this
  post introduces — the blanket `DelegateComponent` impl it generates — no longer exists either. The
  post's advice to remove `#[cgp_context]` when upgrading is now mandatory rather than recommended.
- **`#[cgp_inherit]` is gone.** It was the preset-inheritance replacement introduced here, and it went
  with the presets; a context now joins a namespace with a `namespace` statement inside
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md), per
  [namespaces](../../cgp/concepts/namespaces.md).
- **The consumer-trait blanket impl changed again in v0.7.0.** The post shows it performing a
  `DelegateComponent` lookup; v0.7.0 simplified it to `Context: Greeter<Context>`, since the provider
  trait's own blanket impl already does the lookup. The generated code shown here is therefore one
  revision stale.
- **`#[cgp_impl]` gained implicit context types in v0.6.1.** Every example here still writes
  `impl<Context> HttpRequestFetcher for Context`; the current form omits the generic entirely and
  writes `impl HttpRequestFetcher` with `Self` bounds.
- **Dependencies are hand-written `where Self: ...` bounds**, where the current idiom is
  [`#[uses(...)]`](../../cgp/reference/attributes/uses.md), and
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments did not yet exist. The
  `HasCount` getter implemented by hand would today usually be an implicit argument.

## Maintaining it

Leave it alone. This is the most consequential release note for understanding *why* current CGP looks
the way it does, and the `HasCgpProvider` history section is the only published account of that
design's origin — worth reading before anyone proposes reintroducing shared context providers. For
current guidance on the choice it settled, use
[writing-providers](../../cgp/guides/writing-providers.md).
