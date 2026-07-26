# Extensible Data Types, Part 4: Implementing Extensible Variants

The final part of the series and its dual: how extensible variants work, mirroring part 3 step for
step. It covers partial variants and the uninhabited `Void` type, the cast implementations, the
monadic visitor dispatchers, and the reference-based variants layered on top of the owned ones.

- **URL** — <https://contextgeneric.dev/blog/extensible-datatypes-part-4>
- **Source** — [blog/2025-07-30-extensible-datatypes-part-4.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-07-30-extensible-datatypes-part-4.md)
- **Published** — 30 July 2025, tagged `deepdive`
- **Release** — [v0.4.2](../../releases/v0-4-2.md)
- **Status** — Historical

## What it covers

The post frames variants as the categorical dual of records — products and coproducts — and predicts
that most of part 3's machinery will carry over inverted. It then does exactly that.

`FromVariant` constructs an enum from a tagged value, the mirror of `HasField` reading one. The post
states the shape restriction plainly: CGP supports only "sums of products," meaning every variant must
carry exactly one unnamed field, because anything else would make the `Value` type unwieldy; wrap
richer payloads in a struct. **Partial variants** mirror partial records, but where absence in a
record is `IsNothing` mapping to `()`, absence in a variant is `IsVoid` mapping to the empty enum
`Void` — a variant that has been extracted becomes impossible to construct, so the compiler can prove
it unreachable. `HasExtractor` converts an enum into its all-present partial form and `ExtractField`
removes one variant, returning `Result<Value, Remainder>` where the `Err` carries what is left.

The consequence is the post's most striking result: a chain of extractions narrows the remainder until
its type is `PartialShape<IsVoid, IsVoid>`, which is uninhabited, so the final `Err` arm can simply be
omitted and the compiler accepts the match as exhaustive — no `unreachable!()`, no runtime assertion.
`FinalizeExtract` generalizes this with an empty `match self {}` over an uninhabited type, and
`FinalizeExtractResult` wraps it for ergonomics.

A short digression introduces a fictional `⸮` operator — the mirror of `?`, short-circuiting on `Ok`
and threading the changing `Err` remainder — as a way to make the control flow legible. This
pseudo-operator is the clearest explanation the project has published of what the visitor dispatchers
actually do, and it recurs later.

The casts are then built from the same parts. `HasFields` for an enum is a type-level `Sum!` over
`Either`/`Void` rather than a `Product!` over `Cons`/`Nil`, and a shared `FieldsExtractor` helper
recurses over it. `CanUpcast` iterates the *source's* fields and requires an empty remainder;
`CanDowncast` iterates the *target's* and returns the remainder — the same machinery, differing only
in which side supplies the field list.

The visitor dispatchers follow. `MatchWithHandlers` converts an input to its extractor form, pipes it
through `DispatchMatchers` — which is `PipeMonadic<OkMonadic, Providers>`, the `⸮` operator realized —
and finalizes. The post includes a genuinely useful plain-language explanation of monads for a Rust
audience, framing `?` and `.await` as bind operations. `ExtractFieldAndHandle` and `HandleFieldValue`
adapt providers to tagged fields; `ToFieldHandlers` and `HasFieldHandlers` generate the handler list
from an enum's own field list, so `MatchWithValueHandlers<Provider>` needs no per-enum boilerplate.
The section on `UseContext` as the default provider parameter is important: it lets the concrete
context, rather than the dispatcher, decide how each variant is handled, which is what makes
per-variant overriding possible.

The last section builds the reference-based dispatchers on top of the owned ones, introducing
`PartialRefShape`, `HasExtractorRef`, and the bidirectional `PromoteRef` adapter that bridges
`Computer` and `ComputerRef`.

## How it relates to the knowledge base

The concept is [extensible variants](../../cgp/concepts/extensible-variants.md), with
[dispatching](../../cgp/concepts/dispatching.md) for the visitor side and
[monadic handlers](../../cgp/concepts/monadic-handlers.md) for the pipeline. The traits are
[`FromVariant`](../../cgp/reference/traits/from_variant.md),
[`ExtractField`](../../cgp/reference/traits/extract_field.md),
[`HasFields`](../../cgp/reference/traits/has_fields.md),
[`MapType`](../../cgp/reference/traits/map_type.md) for the presence markers including the void one,
[`CanUpcast` / `CanDowncast`](../../cgp/reference/traits/cast.md), and the
[monad traits](../../cgp/reference/traits/monad.md). The spine types are
[`Either` / `Void`](../../cgp/reference/types/either.md) and
[`Field`](../../cgp/reference/types/field.md). The dispatchers are the
[dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md), the promotion adapters
are among the [handler combinators](../../cgp/reference/providers/handler_combinators.md), and
`PipeMonadic` with its monad markers is in the
[monad providers](../../cgp/reference/providers/monad_providers.md).
[`UseContext`](../../cgp/reference/providers/use_context.md) is the default-provider pattern the post
explains. The worked scenario in current syntax is the
[extensible shapes example](../../examples/extensible-shapes.md).

Two passages are reusable as explanations rather than as code. The `⸮` operator is a teaching device
worth keeping in the toolkit [readers.md](../../communication-strategy/readers.md#the-comprehension-barriers)
assembles, because it makes an unfamiliar control flow legible by analogy to one every Rust programmer
knows. And the monad explanation — monads as containers, `?` and `.await` as bind — is a rare instance
of introducing a functional-programming concept without the jargon that
[vocabulary.md](../../communication-strategy/vocabulary.md) warns against.

## Where it diverges from CGP v0.8.0

- **Partial variant types are now prefixed.** `PartialShape` and `PartialRefShape` became
  `__PartialShape` and `__PartialRefShape` in v0.5.0.
- **The dispatcher family grew.** v0.5.0 added the mutable and tuple-input matchers —
  `MatchWithValueHandlersMut`, `MatchFirstWithValueHandlers` and its ref and mut forms — so the
  post's list is incomplete; see the
  [dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md).
- **`AsyncComputer` did not exist yet.** Added in v0.5.0, it is the async counterpart of `Computer`
  and is what the visitor and monadic machinery now build on, with `Handler` reserved for the async
  fallible case.
- **`#[cgp_dispatch]` shipped under a different name.** The post proposes it as future work to remove
  the boilerplate of implementing a plain trait through a dispatcher; that became
  [`#[cgp_auto_dispatch]`](../../cgp/reference/macros/cgp_auto_dispatch.md) in v0.5.0.
- **The custom-updater future work shipped too**, as `UpdateField` and the `IsOptional` marker in
  v0.5.0; see [optional fields](../../cgp/reference/traits/optional_fields.md).
- **`#[derive(HasFields, ExtractField, FromVariant)]` is now normally
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md)**, and `#[cgp_context]`
  appears on the `App` context in the `UseContext` section and no longer exists.
- **Every provider is inside-out**, written with `#[cgp_provider]`/`#[cgp_new_provider]` rather than
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md).
- **The promised fifth part was never written.** The post says the computation hierarchy —
  `Computer`, `ComputerRef`, `TryComputer`, `Handler`, the `Promote` adapters, `PipeHandlers` versus
  `PipeMonadic` — would get its own post or series. It has not been published, which leaves
  [handlers](../../cgp/concepts/handlers.md) and
  [monadic handlers](../../cgp/concepts/monadic-handlers.md) as the only accounts of it, and makes
  that post an obvious gap in the site's coverage.
- **One typo:** an `ExtractField` impl for `PartialRefShape` gives its `Remainder` as
  `PartialShape<'a, IsVoid, F1>`, mixing the owned name into the reference-based type.

## Maintaining it

Leave it alone. Note the unwritten fifth part as a real gap rather than an oversight to correct in
this post — the computation hierarchy deserves its own piece, and
[handlers](../../cgp/concepts/handlers.md) is the material it would be written from. The `⸮` device
and the monad explanation are the passages to carry forward.
