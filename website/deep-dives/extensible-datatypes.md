# Extensible data types deep dive

Building and reading Rust structs and enums by their *names* rather than their types: the extensible
builder pattern that assembles a context from independent providers, the extensible visitor pattern
that solves the expression problem, the casts between shapes, and the type-level machinery underneath.
The only deep dive drawn from a series rather than a single post.

- **Planned URL** — `https://contextgeneric.dev/docs/deep-dives/extensible-datatypes/`
- **Source posts** — [part 1: builders](../blog/extensible-datatypes-part-1.md) (2025-07-07),
  [part 2: interpreters](../blog/extensible-datatypes-part-2.md) (2025-07-09),
  [part 3: implementing records](../blog/extensible-datatypes-part-3.md) (2025-07-12),
  [part 4: implementing variants](../blog/extensible-datatypes-part-4.md) (2025-07-30); ~35,000 words
  in total, written against CGP v0.4.2
- **Code bases** — [`cgp-examples`](https://github.com/contextgeneric/cgp-examples), the `builder` and
  `expression` crates, tracking `cgp` 0.8.0-alpha locally at `../cgp-examples`
- **Status** — planned; no page written

## What it covers, and why it needs this format

Extensible data types are CGP's answer to a problem Rust has no other answer for: writing code that
works over a type's *shape* — its fields and variants — with full static checking and no runtime
reflection. A record becomes a product of named fields, an enum a sum of named variants, and generic
code recurses over that shape. The payoffs are the two patterns the source series develops: an
application context assembled from independent per-subsystem builders that never name the final type,
and an interpreter whose per-variant handlers can each be added without editing the others.

This is the deep dive with the strongest structural case, for a reason the other two do not share.
**The material is already four documents**, published across three weeks, split as
concepts-then-internals — parts 1 and 2 teach the patterns, parts 3 and 4 explain the machinery. That
split is sound and mostly survives. What does not survive is that each part is itself several thousand
words, and that a reader who wants the builder pattern must currently work out that part 1 is the one
they want and part 3 is optional.

## The page split

Seven pages. The two patterns get two pages each — the pattern, then its internals — so a reader can
stop after either, and the casts get a page of their own because they are genuinely separable and are
the part most often wanted on its own.

**`index.md` — why shape-generic code** (~800 words). The problem: a struct literal names every field
in one place, a `match` names every variant, and both bake the shape into every function that touches
them. What extensible data changes, what the two patterns are, and which pages to read for which. States
plainly that this needs an opt-in derive and does no runtime introspection, which is the honest limit
and belongs on page one.

**1 — Building a record from independent providers** (~1,500 words). The extensible builder pattern
from part 1: each subsystem produces a small struct, a dispatcher merges them, and no provider names the
final application type. The `builder` example crate is the running code.

**2 — Under the hood: records** (~1,500 words). Partial records, the `MapType` presence markers, the
builder trait family, and why `finalize_build` cannot be called early. From part 3.

**3 — Handling every variant, extensibly** (~1,500 words). The extensible visitor pattern from part 2:
per-variant providers, the dispatcher, and the expression problem stated and solved. The `expression`
example crate is the running code.

**4 — Under the hood: variants** (~1,500 words). Partial variants, `IsVoid` and the uninhabited
remainder, the extractor family, and how exhaustiveness is proved without a wildcard arm. From part 4.

**5 — Casting between shapes** (~1,000 words). `CanUpcast`, `CanDowncast`, and `CanBuildFrom`, and the
trick of constructing a small local enum and upcasting it. Currently spread across parts 1 and 4, and
better on its own.

**6 — When to reach for this** (~800 words). The honest boundary: the derive requirement, the diagnostic
cost when a structural operation is mis-wired, and the cases where a plain struct or a `match` is
simply right. The source series is the weakest of the three on this, so this page is written rather than
adapted.

## What changes from the source posts

**`#[cgp_context]` disappears from every context**, along with the `{Context}Components` provider struct
that all the series' `delegate_components!` blocks target. Both were removed in v0.7.0.

**`#[derive(CgpData)]` replaces the individually-listed derives.** The series writes
`#[derive(HasFields, BuildField)]` and `#[derive(HasFields, FromVariant, ExtractField)]`; both still
work, but the umbrella derive added in v0.5.0 is what current code writes.

**Providers become `#[cgp_impl]`.** Every provider in the series is inside-out. Both example crates are
already converted.

**Getter traits become `#[implicit]` arguments** where the field is on the provider's own context —
`HasSqlitePath`, `HasHttpClientConfig`, and `HasOpenAiConfig` in part 1 are the current guides' explicit
anti-pattern. This is also the largest code item below.

**`CanRaiseAsyncError` and `HasAsyncErrorType` are gone**, removed in v0.5.0.

**`PartialPerson` became `__PartialPerson`** in v0.5.0, which matters for parts 3 and 4, where partial
types are shown directly.

**The "future extensions" have shipped.** Filling uninitialized fields with defaults and the
optional-field builder both arrived in v0.5.0, so what the series presents as future work is now
[optional fields](../../cgp/reference/traits/optional_fields.md) and should be presented as a feature.

**One prose error must not be carried over.** Part 1's exhaustive-downcast example calls
`downcast_fields`, a method that does not exist; the remainder is narrowed with `extract_field`, as part
4 shows correctly.

## Source-code changes needed

The two example crates are the least modernized of the four repositories, and unlike Hypershell and
cgp-serde their gaps are pervasive rather than localized. Both are small, so the work is modest.

### `cgp-examples/builder`

**Convert the getter traits to `#[implicit]` arguments.** The crate declares six
`#[cgp_auto_getter]` traits — `HasSqlitePath`, `HasSqliteOptions`, and their HTTP, OpenAI, and Anthropic
counterparts — and reads every configuration value through them. Each is read only from the provider's
own context, which is exactly the case
[reading-context-fields](../../cgp/guides/reading-context-fields.md) says an implicit argument should
cover. `providers/sqlite.rs` is the clearest instance: `BuildSqliteClient` bounds
`Self: HasSqliteOptions` and calls `self.db_journal_mode()`, where the current form is
`#[implicit] db_journal_mode: &str`. **This is the single most visible modernization in the deep dive**,
because page 1 quotes a builder provider in full.

**Adopt `#[uses(...)]`.** The crate has zero `#[uses]` attributes and nine hand-written `Self:` bounds.
`Self: HasSqliteOptions + CanRaiseError<sqlx::Error>` becomes `#[uses(CanRaiseError<sqlx::Error>)]`
once the getter half is gone.

**Replace the `UseDelegate` table.** `contexts/anthropic_and_chatgpt.rs` wires
`HandlerComponent: UseDelegate<new BuilderHandlers { BuildChatGptApp: ..., BuildAnthropicApp: ... }>`.
This dispatches on the handler's `Code` parameter, which is what `open` handles, so it becomes
`open HandlerComponent;` with `@HandlerComponent.BuildChatGptApp: ...` entries — the form the
[application builder example](../../examples/application-builder.md) already uses.

**Consider `#[derive(CgpData)]`** on `App` and the per-subsystem output structs, which currently derive
`HasField, HasFields, BuildField` individually. Cosmetic, but the deep dive teaches the umbrella derive.

### `cgp-examples/expression`

**Adopt `#[uses(...)]`.** Zero `#[uses]`, eleven hand-written `Self:` bounds.

**Replace the `UseDelegate` tables where they key on `Code`.** `contexts/add_mult_neg.rs` has one and
`contexts/add_mult_code.rs` has four; these are `open` candidates.

**Do *not* try to replace the `UseInputDelegate` tables.** `contexts/add_mult.rs` wires
`ComputerComponent: UseInputDelegate<new EvalComponents { MathExpr: DispatchEval, ... }>` and a matching
`ToLispComponents`, and these look like the same pattern but are not. `open` resolves through the
`RedirectLookup` impl every `#[cgp_component]` generates, which for the handler family keys on `Code`;
`UseInputDelegate` is a *separate* dispatcher generated by a second `#[derive_delegate]` attribute and
keyed on `Input`, per the [`#[derive_delegate]` reference](../../cgp/reference/attributes/derive_delegate.md).
**There is currently no `open` equivalent for input-keyed dispatch**, so these tables stay, and the deep
dive should show them as the correct current form rather than apologizing for them. If that changes, this
entry changes with it. This is also the one exception to the decision to remove `#[derive_delegate]` from
the ecosystem code: the `Arg`-keyed attributes in [hypershell](hypershell.md) and
[cgp-serde](cgp-serde.md) go, but the `Input`-keyed attribute these tables resolve through must remain,
because removing it would break them.

**Consider `#[derive(CgpData)]`** on `MathExpr` and `LispExpr`, which derive
`HasFields, FromVariant, ExtractField` individually.

**One getter trait** exists and should be checked against the same implicit-argument rule as the builder
crate's.

## How it relates to the knowledge base

The verified counterparts are the [application builder](../../examples/application-builder.md) example
for pages 1 and 2 and the [expression interpreter](../../examples/expression-interpreter.md) for pages 3
and 4; the [extensible shapes](../../examples/extensible-shapes.md) example is the non-recursive
companion and a good source for page 5. The concepts are
[extensible records](../../cgp/concepts/extensible-records.md),
[extensible variants](../../cgp/concepts/extensible-variants.md), and
[dispatching](../../cgp/concepts/dispatching.md), with
[monadic handlers](../../cgp/concepts/monadic-handlers.md) behind the visitor pipeline.

The reference material for the internals pages is the
[builder family](../../cgp/reference/traits/has_builder.md),
the [extractor family](../../cgp/reference/traits/extract_field.md), the
[`MapType` markers](../../cgp/reference/traits/map_type.md), the
[casts](../../cgp/reference/traits/cast.md), the
[dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md), and the
[`CgpData` derive](../../cgp/reference/derives/derive_cgp_data.md).

For page 6, the boundary is drawn in
[message.md](../../communication-strategy/message.md#when-not-to-reach-for-cgp), and the
row-polymorphism reader's specific objection — that extensible records mean gigantic error messages — is
answered in [message.md](../../communication-strategy/message.md#the-objections-readers-bring) and
compared honestly in [row polymorphism](../../related-work/row-polymorphism.md).

## Maintaining it

Two structural properties are worth defending. The **pattern-then-internals split** across pages 1–4 is
what lets a reader stop halfway with something useful; collapsing it into four sequential chapters would
lose that. And **page 6 must not be dropped** — it is the page the source series never wrote, and it is
what stops the deep dive reading as an advertisement for the most advanced thing CGP does.

When the code changes land in `cgp-examples`, update the lists above rather than leaving them as a
record of a state that has passed.
