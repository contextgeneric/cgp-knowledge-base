# Extensible Data Types, Part 1: Modular App Construction and Extensible Builders

The first of a four-part series announcing CGP v0.4.2 and extensible records and variants. It
demonstrates safe enum upcasting and downcasting, incremental struct building, and then works a
realistic use case: assembling an application context from independent per-subsystem builder
providers.

- **URL** — <https://contextgeneric.dev/blog/extensible-datatypes-part-1>
- **Source** — [blog/2025-07-07-extensible-datatypes-part-1.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-07-07-extensible-datatypes-part-1.md)
- **Published** — 7 July 2025, tagged `release` and `deepdive`
- **Release** — [v0.4.2](../../releases/v0-4-2.md), announced across all four parts
- **Status** — Historical

## What it covers

The post opens by positioning the release: CGP could already *read* a field from any struct through
`HasField`, and v0.4.2 adds the ability to *construct* fields and to operate over enum variants
generically. It names the two patterns this unlocks — the extensible builder and the extensible
visitor — and tells readers from other language backgrounds that this brings
[datatype-generic programming](https://wiki.haskell.org/index.php?title=Generics), structural typing,
row polymorphism, and polymorphic variants to Rust.

A **feature highlights** section demonstrates three capabilities in isolation. Safe *upcasting* lifts
a `Shape` value into a `ShapePlus` enum that is a superset of its variants, with the two enums needing
no knowledge of each other. Safe *downcasting* goes the other way and returns a `Result` whose `Err`
carries the unhandled remainder, which can be downcast again — so a chain of downcasts can exhaust an
enum, and the compiler knows when no variant is left and lets the final `Err` arm be omitted. Safe
*struct building* merges smaller structs into a larger one: `Employee::builder().build_from(person).build_from(employee_id).finalize_build()`.

The bulk of the post is the **motivation and worked example**. It starts from an ordinary `App::new`
constructor holding a SQLite pool and an HTTP client, grows it with two OpenAI fields, then grows it
again into a six-parameter monster, and argues that the conventional builder pattern does not fix this
because a builder is tightly coupled to one target struct and cannot be extended without editing it.
The CGP answer is one `Handler` provider per subsystem — `BuildSqliteClient`, `BuildHttpClient`,
`BuildOpenAiClient` — each generic over a *builder context* that supplies its configuration through
`#[cgp_auto_getter]` traits, each returning a small wrapper struct, and all of them merged by the
`BuildAndMergeOutputs` dispatcher. The post then shows the payoff by varying the result: a minimal
default builder, a Postgres variant, an Anthropic variant, a dual-agent variant carrying both AI
clients, and finally a single builder that produces all three application types by dispatching on a
`Code` parameter.

## How it relates to the knowledge base

The worked example is re-derived in current syntax as the
[application builder example](../../examples/application-builder.md), which is the source to quote.
The concepts are [extensible records](../../cgp/concepts/extensible-records.md) for the builder side
and [extensible variants](../../cgp/concepts/extensible-variants.md) for the casts, with
[dispatching](../../cgp/concepts/dispatching.md) covering the visitor and builder dispatchers.

Per construct: the derives are [`#[derive(HasFields)]`](../../cgp/reference/derives/derive_has_fields.md),
[`#[derive(BuildField)]`](../../cgp/reference/derives/derive_build_field.md),
[`#[derive(ExtractField)]`](../../cgp/reference/derives/derive_extract_field.md), and
[`#[derive(FromVariant)]`](../../cgp/reference/derives/derive_from_variant.md), now normally reached
through the umbrella [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md). The casts
are [`CanUpcast` / `CanDowncast` / `CanBuildFrom`](../../cgp/reference/traits/cast.md); the builder
family is [`HasBuilder`](../../cgp/reference/traits/has_builder.md); the extractor family is
[`ExtractField`](../../cgp/reference/traits/extract_field.md). The subsystem builders are
[`Handler`](../../cgp/reference/components/handler.md) providers, and the merge dispatcher is in the
[dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md).

The post also carries a communication-strategy asset: its opening is a textbook execution of the
before/after narrative [problems-solved.md](../../communication-strategy/problems-solved.md)
prescribes, growing an ordinary constructor until the reader feels the pain before naming any CGP
construct. The "swap SQLite for Postgres, ChatGPT for Claude, or run both" progression is the
concrete answer to the feature-flag alternative that
[positioning.md](../../communication-strategy/positioning.md) weighs.

## Where it diverges from CGP v0.8.0

- **`#[cgp_context]` appears on every context and no longer exists**, removed in v0.7.0 along with
  the `{Context}Components` provider struct that all the `delegate_components!` blocks target.
- **The derives are listed individually.** `#[derive(HasFields, BuildField)]` and
  `#[derive(HasFields, FromVariant, ExtractField)]` still work, but
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md), added in v0.5.0, is the
  current umbrella and is what current code writes.
- **Every provider is inside-out.** `#[cgp_new_provider] impl<Build, Code, Input> Handler<Build, Code, Input> for BuildSqliteClient`
  would today be [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md).
- **`CanRaiseAsyncError` and `HasAsyncErrorType` were removed** in v0.5.0; see
  [send-bounds](../../cgp/concepts/send-bounds.md).
- **Configuration is read through `#[cgp_auto_getter]` traits** — `HasSqlitePath`,
  `HasHttpClientConfig`, `HasOpenAiConfig`. The current default for reading a builder context's own
  fields is [`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments, per
  [reading-context-fields](../../cgp/guides/reading-context-fields.md).
- **`UseDelegate<new BuilderHandlers { ... }>`** in the multi-context builder is the legacy dispatch
  form; the current idiom is the `open` statement, per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **`PartialPerson` became `__PartialPerson`** in v0.5.0. The post does not show partial types
  directly, but [part 3](extensible-datatypes-part-3.md) does.
- **The post's "future extensions" have shipped.** Filling uninitialized fields with defaults
  (`finalize_with_default`) and the optional-field builder arrived in v0.5.0; see
  [optional fields](../../cgp/reference/traits/optional_fields.md).
- **One error in the prose.** The exhaustive-downcast example calls `downcast_fields`, a method name
  that does not exist — the remainder is narrowed with `extract_field`, as
  [part 4](extensible-datatypes-part-4.md) shows correctly.

## Maintaining it

Leave it alone. The series is a coherent, cross-referenced whole and cannot be partially updated
without breaking the links between its four parts. Its enduring value is the *motivation* — the
argument that the conventional builder pattern cannot be extended without editing it, and that this
follows from Rust requiring every field of a struct at construction time — which is exactly the
framing to reuse when writing about extensible records, from
[extensible records](../../cgp/concepts/extensible-records.md) and the
[application builder example](../../examples/application-builder.md).
