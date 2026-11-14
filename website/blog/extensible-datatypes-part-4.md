# Extensible Data Types, Part 4: Implementing Extensible Variants

The series' final part and part 3's dual: partial variants and the uninhabited `Void` type, the cast
implementations, the monadic visitor dispatchers, and the reference-based variants built on the owned
ones.

- **URL**: <https://contextgeneric.dev/blog/extensible-datatypes-part-4>
- **Source**: [blog/2025-07-30-extensible-datatypes-part-4.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-07-30-extensible-datatypes-part-4.md)
- **Published**: 30 July 2025, tagged `deepdive`
- **Release**: [v0.4.2](../../releases/v0-4-2.md)
- **Status**: Historical
- **Notice**: a note at the top of the post, written on the website's `v0.8.0` branch, links the *Extensible variants* Concepts page, the reference, and the [`expression` pages](https://contextgeneric.dev/docs/projects/cgp-examples/expression/); it is the sanctioned edit in [../AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#blog-posts) and changes no claim

## What it covers

The post frames variants as the categorical dual of records (coproducts to products) and carries part
3's machinery over inverted:

- **Construction:** `FromVariant` builds an enum from a tagged value. CGP supports only "sums of
  products": every variant carries exactly one unnamed field, so richer payloads are wrapped in a
  struct.
- **Partial variants:** absence is `IsVoid`, mapping to the empty enum `Void`, so an extracted variant
  cannot be constructed and the compiler proves it unreachable. `HasExtractor` gives the all-present
  form, and `ExtractField` removes one variant, returning `Result<Value, Remainder>`.
- **Exhaustiveness, the post's most striking result:** extractions narrow the remainder until its type
  is `PartialShape<IsVoid, IsVoid>`, which is uninhabited, so the final `Err` arm is omitted and the
  match is exhaustive, with no `unreachable!()` or runtime assertion. `FinalizeExtract` generalizes
  this with an empty `match self {}`, and `FinalizeExtractResult` wraps it.
- **A fictional `⸮` operator:** the mirror of `?`, short-circuiting on `Ok` and threading the changing
  `Err` remainder, the clearest published explanation of what the visitor dispatchers do.
- **Casts:** `HasFields` for an enum is a `Sum!` over `Either`/`Void`, recursed by a shared
  `FieldsExtractor`. `CanUpcast` iterates the *source's* fields and requires an empty remainder;
  `CanDowncast` iterates the *target's* and returns the remainder.
- **Visitor dispatchers:** `MatchWithHandlers` converts an input to its extractor form, pipes it
  through `DispatchMatchers` (`PipeMonadic<OkMonadic, Providers>`, the `⸮` operator realized), and
  finalizes, with a plain-language account of monads framing `?` and `.await` as bind.
  `ExtractFieldAndHandle` and `HandleFieldValue` adapt providers to tagged fields; `ToFieldHandlers`
  and `HasFieldHandlers` generate the handler list from the enum's fields, so
  `MatchWithValueHandlers<Provider>` needs no per-enum boilerplate. `UseContext` as the default
  provider parameter lets the context decide how each variant is handled, which makes per-variant
  overriding possible.
- **References:** `PartialRefShape`, `HasExtractorRef`, and the bidirectional `PromoteRef` adapter
  bridging `Computer` and `ComputerRef`.

## How it relates to the knowledge base

- **Concepts:** [extensible variants](../../cgp/concepts/extensible-variants.md),
  [dispatching](../../cgp/concepts/dispatching.md), and
  [monadic handlers](../../cgp/concepts/monadic-handlers.md); the scenario in current syntax is the
  [extensible shapes example](../../examples/extensible-shapes.md).
- **Traits and types:** [`FromVariant`](../../cgp/reference/traits/from_variant.md),
  [`ExtractField`](../../cgp/reference/traits/extract_field.md),
  [`HasFields`](../../cgp/reference/traits/has_fields.md),
  [`MapType`](../../cgp/reference/traits/map_type.md),
  [`CanUpcast` / `CanDowncast`](../../cgp/reference/traits/cast.md), the
  [monad traits](../../cgp/reference/traits/monad.md),
  [`Either` / `Void`](../../cgp/reference/types/either.md), and
  [`Field`](../../cgp/reference/types/field.md).
- **Providers:** the [dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md),
  the promotion adapters among the [handler
  combinators](../../cgp/reference/providers/handler_combinators.md), `PipeMonadic` in the [monad
  providers](../../cgp/reference/providers/monad_providers.md), and
  [`UseContext`](../../cgp/reference/providers/use_context.md).
- **Teaching devices:** the `⸮` operator makes an unfamiliar control flow legible by analogy to one
  every Rust programmer knows, for the toolkit
  [readers.md](../../communication-strategy/readers.md#the-comprehension-barriers) assembles; the monad
  explanation introduces a functional concept without the jargon
  [vocabulary.md](../../communication-strategy/vocabulary.md) warns against.

## Where it diverges from CGP v0.8.0

- **Partial variant types are prefixed.** `PartialShape` and `PartialRefShape` became `__PartialShape`
  and `__PartialRefShape` in v0.5.0.
- **The dispatcher family grew.** v0.5.0 added the mutable and tuple-input matchers
  (`MatchWithValueHandlersMut`, `MatchFirstWithValueHandlers` and its ref and mut forms), so the post's
  list is incomplete; see the
  [dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md).
- **`AsyncComputer` did not exist yet.** Added in v0.5.0 as the async counterpart of `Computer`, it is
  what the visitor and monadic machinery build on, with `Handler` reserved for the async fallible case.
- **`#[cgp_dispatch]` shipped under another name.** The post proposes it to remove the boilerplate of
  implementing a plain trait through a dispatcher; it became
  [`#[cgp_auto_dispatch]`](../../cgp/reference/macros/cgp_auto_dispatch.md) in v0.5.0.
- **The custom-updater future work shipped too**, as `UpdateField` and the `IsOptional` marker in
  v0.5.0; see [optional fields](../../cgp/reference/traits/optional_fields.md).
- **`#[derive(HasFields, ExtractField, FromVariant)]` is now
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md)**, and the `#[cgp_context]` on
  the `App` context in the `UseContext` section no longer exists.
- **Every provider is inside-out**, with `#[cgp_provider]`/`#[cgp_new_provider]` rather than
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md).
- **The promised fifth part was never written.** The post says the computation hierarchy (`Computer`,
  `ComputerRef`, `TryComputer`, `Handler`, the `Promote` adapters, `PipeHandlers` versus `PipeMonadic`)
  would get its own post or series. It has not been published, so
  [handlers](../../cgp/concepts/handlers.md) and
  [monadic handlers](../../cgp/concepts/monadic-handlers.md) are the only accounts of it.
- **One typo:** an `ExtractField` impl for `PartialRefShape` gives its `Remainder` as
  `PartialShape<'a, IsVoid, F1>`, mixing the owned name into the reference-based type.

## Maintaining it

Leave it alone. The unwritten fifth part is a gap in the site's coverage, not an oversight to correct
here; [handlers](../../cgp/concepts/handlers.md) is the material it would be written from. The `⸮`
device and the monad explanation are the passages to carry forward.
