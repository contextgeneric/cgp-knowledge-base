# Supercharge Rust functions with implicit arguments using CGP v0.7.0

The largest ergonomics release, and the post closest to current CGP. It introduces the attribute suite
that defines how CGP is written today — `#[cgp_fn]`, `#[implicit]`, `#[uses]`, `#[extend]`,
`#[use_provider]`, `#[use_type]` — removes `#[cgp_context]`, and ships the area-calculation tutorials
and the AI skills page alongside.

- **URL** — <https://contextgeneric.dev/blog/v0.7.0-release>
- **Source** — [blog/2026-02-28-v0.7.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2026-02-28-v0.7.0-release.md)
- **Published** — 28 February 2026, tagged `release`
- **Release** — [v0.7.0](../../releases/v0-7-0.md)
- **Status** — Historical, but the most current release note on the site

## What it covers

The post opens on the two problems the release targets — explicit parameter threading through call
chains, and the tight coupling that follows from grouping values into one struct and writing methods
on it — and then introduces the features as answers to them.

**`#[cgp_fn]` with `#[implicit]` arguments** turns a plain function into a context-generic capability
whose marked arguments are fetched from the calling context's fields rather than passed. A struct
opts in with `#[derive(HasField)]` and nothing else. **`#[uses]`** imports another CGP capability so a
function can call it on `self` without knowing its requirements, and **`#[extend]`** does the same
while re-exporting it, which the post frames neatly as the `pub use` to `#[uses]`'s `use`.
**`#[implicit]` in `#[cgp_impl]`** removes the getter-trait layer from provider implementations, and
the post shows the before-and-after directly: a `#[cgp_auto_getter]` trait, a `where` clause, and two
method calls collapse into two annotated parameters. **`#[use_provider]`** fills in the stray `Self`
argument on an inner provider's bound, so a higher-order provider's dependency reads like an ordinary
one. **`#[use_type]`** imports an abstract associated type as a bare alias, removing `Self::` from
every use site.

A section titled **"Isn't this just Scala implicits?"** answers the objection the word invites, and
answers it well: Scala resolves from a broad layered implicit scope while CGP resolves only from a
field on `self`; Scala matches on type alone and so admits ambiguity while CGP matches on name *and*
type, which Rust's field rules make unambiguous by construction; and every `#[implicit]` expands
mechanically to a `HasField` bound and a `get_field` call that any developer can read.

The **breaking changes** are substantial. `#[cgp_context]` is removed. The consumer-trait blanket impl
is simplified so that a context implements the consumer trait if it implements the provider trait for
itself, dropping a redundant table lookup — with a noted consequence that static method calls can
become ambiguous when both traits are in scope. `check_components!` and
`delegate_and_check_components!` drop the `Name for Context` syntax in favour of an optional
`#[check_trait(...)]` attribute, and gain `#[check_params]` and `#[skip_check]`. Owned getter and
implicit values now require `Copy` rather than `Clone`, so that expensive values are not silently
cloned. The `{Type}Of` alias is dropped from `#[cgp_type]`, and `ProvideType`/`TypeComponent` are
renamed `TypeProvider`/`TypeProviderComponent`.

The post also announces the [area-calculation tutorials](../tutorials/area-calculation.md) and the
[AI skills page](../site-structure.md), and links its discussions on
[GitHub](https://github.com/orgs/contextgeneric/discussions/21),
[Reddit](https://www.reddit.com/r/rust/comments/1rhwxnd/supercharge_rust_functions_with_implicit/),
[Lobsters](https://lobste.rs/s/6gcdzl/supercharge_rust_functions_with), and
[Hacker News](https://news.ycombinator.com/item?id=47206419).

## How it relates to the knowledge base

Every feature here is current and documented:
[`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md),
[`#[implicit]`](../../cgp/reference/attributes/implicit.md),
[`#[uses]`](../../cgp/reference/attributes/uses.md),
[`#[extend]`](../../cgp/reference/attributes/extend.md),
[`#[use_provider]`](../../cgp/reference/attributes/use_provider.md), and
[`#[use_type]`](../../cgp/reference/attributes/use_type.md), over the
[implicit arguments](../../cgp/concepts/implicit-arguments.md) and
[abstract types](../../cgp/concepts/abstract-types.md) concepts. The guides that prescribe them are
[reading-context-fields](../../cgp/guides/reading-context-fields.md),
[declaring-dependencies](../../cgp/guides/declaring-dependencies.md),
[capability-supertraits](../../cgp/guides/capability-supertraits.md), and
[importing-abstract-types](../../cgp/guides/importing-abstract-types.md). The renamed type component
is [`HasType` / `TypeProvider`](../../cgp/reference/components/has_type.md), and the checking changes
are in [`check_components!`](../../cgp/reference/macros/check_components.md) and
[`delegate_and_check_components!`](../../cgp/reference/macros/delegate_and_check_components.md).

The Scala-implicits section is a communication-strategy asset in its own right. It is a model of the
concede-then-distinguish move [message.md](../../communication-strategy/message.md#the-objections-readers-bring) prescribes —
it grants that the reputation is deserved before explaining why the mechanisms differ — and the
comparison itself is grounded in [implicit-parameters](../../related-work/implicit-parameters.md).
Anyone writing publicly about `#[implicit]` should reuse that structure rather than reinventing it.
The Reddit and Lobsters threads it links are part of the reception evidence analyzed in
[evidence.md](../../communication-strategy/evidence.md).

## Where it diverges from CGP v0.8.0

Less than any other release note, but the gaps are real and one of them is easy to miss.

- **`#[use_type(HasScalarType::Scalar)]` uses `::`; current syntax uses `.`** —
  `#[use_type(HasScalarType.Scalar)]`. This is the single most likely thing to be copied wrong from
  this post, because everything around it still compiles. See
  [`#[use_type]`](../../cgp/reference/attributes/use_type.md) for the current grammar, including the
  equality form `#[use_type(HasErrorType.{Error = AppError})]` that did not exist here.
- **Namespaces did not exist yet.** Nothing in the post is wrong for it, but its wiring examples show
  flat `delegate_components!` tables, and a real application would now group them per
  [namespaces](../../cgp/concepts/namespaces.md) and the
  [namespaces-and-prefixes guide](../../cgp/guides/namespaces-and-prefixes.md).
- **Per-type dispatch is not covered.** The `open` statement of
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md) postdates the post, so
  its examples predate the current answer to
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **`cargo-cgp` did not exist.** The post's guidance on debugging is silent where the current answer
  would lead with [`cargo cgp check`](../../cargo-cgp/reference/usage.md).
- **The `HasScalarType` example declares `type Scalar: Mul<Output = Scalar> + Copy;`**, which names
  `Scalar` bare inside its own definition rather than as `Self::Scalar` — a slip in the post, not a
  syntax that ever worked.

## Maintaining it

Leave it alone, but treat it as the post most likely to be mined for current code, since it is the
newest finished release note and most of it still compiles. The `::` versus `.` change in
`#[use_type]` is the trap; anyone quoting from here must check that one line against
[`#[use_type]`](../../cgp/reference/attributes/use_type.md). For material on the same features in
verified current form, the [area calculation example](../../examples/area-calculation.md) covers the
same ground.
