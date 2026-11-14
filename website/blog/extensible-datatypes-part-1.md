# Extensible Data Types, Part 1: Modular App Construction and Extensible Builders

The first of a four-part series announcing CGP v0.4.2's extensible records and variants: safe enum
upcasting and downcasting, incremental struct building, and an application context assembled from
independent per-subsystem builder providers.

- **URL**: <https://contextgeneric.dev/blog/extensible-datatypes-part-1>
- **Source**: [blog/2025-07-07-extensible-datatypes-part-1.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-07-07-extensible-datatypes-part-1.md)
- **Published**: 7 July 2025, tagged `release` and `deepdive`
- **Release**: [v0.4.2](../../releases/v0-4-2.md), announced across all four parts
- **Status**: Historical
- **Notice**: a note at the top of the post, written on the website's `v0.8.0` branch, links the *Extensible records* Concepts page and the [cgp-examples section](https://contextgeneric.dev/docs/projects/cgp-examples/), whose `builder` pages this post's code grew into are not yet written; per [projects/cgp-examples.md](../projects/cgp-examples.md); it is the sanctioned edit in [../AGENTS.md](../AGENTS.md#do-not-rewrite-history) and changes no claim

## What it covers

The opening positions the release: CGP could already *read* a field through `HasField`, and v0.4.2
adds *constructing* fields and operating over enum variants generically, through the extensible
builder and the extensible visitor. For readers from other languages it names
[datatype-generic programming](https://wiki.haskell.org/index.php?title=Generics), structural typing,
row polymorphism, and polymorphic variants.

**Feature highlights** show three features alone:

- **Upcasting:** a `Shape` value lifted into `ShapePlus`, a superset enum, with neither enum knowing
  the other.
- **Downcasting:** returns a `Result` whose `Err` carries the unhandled remainder, which can be
  downcast again; the compiler knows when no variant is left and lets the final `Err` arm be omitted.
- **Struct building:** smaller structs merged into a larger one:
  `Employee::builder().build_from(person).build_from(employee_id).finalize_build()`.

**The worked example is the bulk of the post.** An `App::new` constructor with a SQLite pool and an
HTTP client grows two OpenAI fields, then six parameters, and the post argues the conventional builder
cannot fix this because a builder is coupled to one target struct and cannot be extended without
editing it. The CGP answer is one `Handler` provider per subsystem (`BuildSqliteClient`,
`BuildHttpClient`, `BuildOpenAiClient`), each generic over a *builder context* supplying its
configuration through `#[cgp_auto_getter]` traits and returning a small wrapper struct, merged by the
`BuildAndMergeOutputs` dispatcher. The payoff varies the result: a minimal default builder, Postgres
and Anthropic variants, a dual-agent variant with both AI clients, and one builder producing all three
application types by dispatching on a `Code` parameter.

## How it relates to the knowledge base

- **The source to quote:** the [application builder example](../../examples/application-builder.md).
  The post's code lives on as cgp-examples' `builder` crate; where each section now sits is in the
  [`builder` subproject](../../projects/cgp-examples/builder/README.md#where-the-blog-posts-code-lives).
- **Concepts:** [extensible records](../../cgp/concepts/extensible-records.md),
  [extensible variants](../../cgp/concepts/extensible-variants.md) for the casts, and
  [dispatching](../../cgp/concepts/dispatching.md) for the dispatchers.
- **Constructs:** [`#[derive(HasFields)]`](../../cgp/reference/derives/derive_has_fields.md),
  [`#[derive(BuildField)]`](../../cgp/reference/derives/derive_build_field.md),
  [`#[derive(ExtractField)]`](../../cgp/reference/derives/derive_extract_field.md), and
  [`#[derive(FromVariant)]`](../../cgp/reference/derives/derive_from_variant.md), now reached through
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md);
  [`CanUpcast` / `CanDowncast` / `CanBuildFrom`](../../cgp/reference/traits/cast.md);
  [`HasBuilder`](../../cgp/reference/traits/has_builder.md);
  [`ExtractField`](../../cgp/reference/traits/extract_field.md);
  [`Handler`](../../cgp/reference/components/handler.md); and the
  [dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md).
- **Strategy assets:** the opening grows an ordinary constructor until the reader feels the pain
  before naming a construct, the before/after narrative
  [message.md](../../communication-strategy/message.md#the-problems-cgp-removes) prescribes; the
  "swap SQLite for Postgres, ChatGPT for Claude, or run both" progression answers the feature-flag
  alternative [message.md](../../communication-strategy/message.md#when-not-to-reach-for-cgp) weighs.

## Where it diverges from CGP v0.8.0

- **`#[cgp_context]` appears on every context and no longer exists**, removed in v0.7.0 with the
  `{Context}Components` provider struct that every `delegate_components!` block targets.
- **The derives are listed individually.** `#[derive(HasFields, BuildField)]` and
  `#[derive(HasFields, FromVariant, ExtractField)]` still work, but current code writes
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md), added in v0.5.0.
- **Every provider is inside-out.** `#[cgp_new_provider] impl<Build, Code, Input> Handler<Build, Code, Input> for BuildSqliteClient`
  would be [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md).
- **`CanRaiseAsyncError` and `HasAsyncErrorType` were removed** in v0.5.0; see
  [send-bounds](../../cgp/concepts/send-bounds.md).
- **Configuration is read through `#[cgp_auto_getter]` traits** (`HasSqlitePath`,
  `HasHttpClientConfig`, `HasOpenAiConfig`). A builder context's own fields are now read with
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments, per
  [reading-context-fields](../../cgp/guides/reading-context-fields.md).
- **`UseDelegate<new BuilderHandlers { ... }>`** in the multi-context builder is the legacy dispatch
  form; the idiom is the `open` statement, per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **`PartialPerson` became `__PartialPerson`** in v0.5.0. This post does not show partial types;
  [part 3](extensible-datatypes-part-3.md) does.
- **The "future extensions" have shipped.** `finalize_with_default` and the optional-field builder
  arrived in v0.5.0; see [optional fields](../../cgp/reference/traits/optional_fields.md).

## Maintaining it

Leave it alone; the four parts cross-reference one another and cannot be partly updated. Its lasting
value is the motivation: the conventional builder cannot be extended without editing it, because Rust
requires every field at construction. Reuse that framing from
[extensible records](../../cgp/concepts/extensible-records.md) and the
[application builder example](../../examples/application-builder.md).

When the `builder` pages are written, the notice gains a link to the `builder` index.
