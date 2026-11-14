# Supercharge Rust functions with implicit arguments using CGP v0.7.0

The largest ergonomics release, and the published post closest to current CGP: it introduces the
attribute suite CGP is written in today, removes `#[cgp_context]`, and ships the area-calculation
tutorials and the AI skills page.

- **URL**: <https://contextgeneric.dev/blog/v0.7.0-release>
- **Source**: [blog/2026-02-28-v0.7.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2026-02-28-v0.7.0-release.md)
- **Published**: 28 February 2026, tagged `release`
- **Release**: [v0.7.0](../../releases/v0-7-0.md)
- **Status**: Historical

## What it covers

The post opens on two problems, threading parameters through call chains and the coupling that comes
from grouping values into one struct with methods, and introduces the features as answers:

- **`#[cgp_fn]` with `#[implicit]` arguments:** a function becomes a context-generic trait whose marked
  arguments come from the context's fields; a struct opts in with `#[derive(HasField)]` alone.
- **`#[uses]` and `#[extend]`:** import another CGP trait so a function calls it on `self` without
  knowing its requirements, `#[extend]` also re-exporting it, framed as `pub use` to `#[uses]`'s `use`.
- **`#[implicit]` in `#[cgp_impl]`:** a `#[cgp_auto_getter]` trait, a `where` clause, and two method
  calls collapse into two annotated parameters, shown before and after.
- **`#[use_provider]`:** fills in the `Self` argument on an inner provider's bound.
- **`#[use_type]`:** imports an abstract associated type as a bare alias.

**"Isn't this just Scala implicits?"** concedes the reputation, then distinguishes: Scala resolves from
a layered implicit scope, CGP only from a field on `self`; Scala matches on type alone and admits
ambiguity, CGP on name and type, which Rust's field rules make unambiguous; and every `#[implicit]`
expands to a readable `HasField` bound and `get_field` call.

The breaking changes:

- `#[cgp_context]` is removed.
- The consumer-trait blanket impl applies when a context implements the provider trait for itself,
  dropping a redundant lookup; static method calls can become ambiguous with both traits in scope.
- `check_components!` and `delegate_and_check_components!` replace `Name for Context` with an optional
  `#[check_trait(...)]` attribute, and gain `#[check_params]` and `#[skip_check]`.
- Owned getter and implicit values are said to require `Copy` rather than `Clone`; the divergence
  below corrects this.
- `#[cgp_type]` drops the `{Type}Of` alias, and `ProvideType`/`TypeComponent` become
  `TypeProvider`/`TypeProviderComponent`.

The post announces the [area-calculation tutorials](../tutorials/area-calculation.md) and the
[AI skills page](../pages/ai-skills.md), and links its discussion threads.

## How it relates to the knowledge base

- **Constructs:** [`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md),
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md),
  [`#[uses]`](../../cgp/reference/attributes/uses.md),
  [`#[extend]`](../../cgp/reference/attributes/extend.md),
  [`#[use_provider]`](../../cgp/reference/attributes/use_provider.md), and
  [`#[use_type]`](../../cgp/reference/attributes/use_type.md), over
  [implicit arguments](../../cgp/concepts/implicit-arguments.md) and
  [abstract types](../../cgp/concepts/abstract-types.md).
- **Guides:** [reading-context-fields](../../cgp/guides/reading-context-fields.md),
  [declaring-dependencies](../../cgp/guides/declaring-dependencies.md),
  [method-supertraits](../../cgp/guides/method-supertraits.md), and
  [importing-abstract-types](../../cgp/guides/importing-abstract-types.md).
- **Breaking changes:** [`HasType` / `TypeProvider`](../../cgp/reference/components/has_type.md),
  [`check_components!`](../../cgp/reference/macros/check_components.md), and
  [`delegate_and_check_components!`](../../cgp/reference/macros/delegate_and_check_components.md).
- **The Scala section:** a model of the concede-then-distinguish move
  [message.md](../../communication-strategy/message.md#the-objections-readers-bring) prescribes,
  grounded in [implicit-parameters](../../related-work/implicit-parameters.md); public writing about
  `#[implicit]` should reuse its structure. The post's reception is in
  [evidence.md](../../communication-strategy/evidence.md).

## Where it diverges from CGP v0.8.0

Less than any other release note, but one gap is easy to miss:

- **`#[use_type(HasScalarType::Scalar)]` uses `::`; current syntax uses `.`**:
  `#[use_type(HasScalarType.Scalar)]`. This is the line most likely to be copied wrong, because
  everything around it still compiles. See [`#[use_type]`](../../cgp/reference/attributes/use_type.md)
  for the grammar, including the equality form `#[use_type(HasErrorType.{Error = AppError})]`, which
  this release shipped with the `::` separator but the post does not show.
- **Namespaces did not exist yet.** Its wiring examples show flat `delegate_components!` tables, where
  a real application would now group them per [namespaces](../../cgp/concepts/namespaces.md) and the
  [namespaces-and-prefixes guide](../../cgp/guides/namespaces-and-prefixes.md).
- **Per-type dispatch is not covered.** The `open` statement of
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md) postdates the post; see
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **`cargo-cgp` did not exist.** The post's debugging guidance is silent where the current answer
  leads with [`cargo cgp check`](../../cargo-cgp/reference/usage.md).
- **The `HasScalarType` example declares `type Scalar: Mul<Output = Scalar> + Copy;`**, naming `Scalar`
  bare inside its own definition rather than as `Self::Scalar`. It is a slip, not a syntax that ever
  worked.
- **The note that owned getter and implicit values "now require `Copy` rather than `Clone`" never
  described the published crate.** The release renamed the macro's internal field mode but kept the
  generated `.clone()` call with no `Copy` bound, so at this tag and in v0.8.0 `Clone` is the
  requirement and a `String` field satisfies an owned `String` argument; a probe against `cgp` 0.7.0
  compiles one. Do not carry the `Copy` claim into any current page.

## Maintaining it

Leave it alone, but expect it to be mined for current code, since it is the newest finished release
note and most of it still compiles; anyone quoting it checks the `#[use_type]` separator. The
[area calculation example](../../examples/area-calculation.md) covers the same features in verified
form.
