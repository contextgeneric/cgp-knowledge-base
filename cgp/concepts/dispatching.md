# Dispatching

Dispatching is the CGP pattern for handling an extensible-data value generically by routing it to per-variant or per-field handlers: an enum's current variant goes to the handler for that variant, and each field of a record is produced by its own handler.

This page is about dispatching on the *value* of extensible data. Choosing a provider per *type* through wiring, with the `open` statement of [`delegate_components!`](../reference/macros/delegate_components.md#statements-open-namespace-and-for) or the legacy [`UseDelegate`](../reference/providers/use_delegate.md) tables, is a different mechanism, covered by the [dispatching per type](../guides/dispatching-per-type.md) guide. The two often meet: a context can wire an enum type to one of the matchers below through `open`.

## Purpose

Dispatching writes one piece of logic over a record or enum whose exact shape is not known where the logic is written. A concrete `match` names every variant in one place, and a struct literal supplies every field at once; both bake the shape into the code. Dispatching keeps the per-variant and per-field structure but lets the shape and the handlers be chosen by type, so one matcher serves many enums and one builder serves many records, with each variant's or field's behavior wired separately.

The extensible-data machinery already represents records and enums as type-level lists, and dispatching turns those lists into work. The extractor family in [`extract_field`](../reference/traits/extract_field.md) takes an enum apart one variant at a time, and the builder family in [`has_builder`](../reference/traits/has_builder.md) assembles a record one field at a time, but neither decides what to do with each variant or field. Dispatching pairs each one with a handler and runs the list as a handler provider, so it composes with the rest of the [handler family](handlers.md). The concrete providers are documented in [dispatch combinators](../reference/providers/dispatch_combinators.md); this page explains the idea they share.

## Matching a variant to a handler

A matcher tries each variant in turn and stops at the one that is present. It converts the input into its *extractor*, the partial enum from [`HasExtractor`](../reference/traits/extract_field.md) in which every variant is still possible, and runs a list of per-variant handlers over it. Each handler tries one variant. If the value is that variant, the handler runs the variant's own handler on the payload and reports success. Otherwise it reports failure and hands back a *remainder*: the extractor with that variant ruled out in its type. The next handler receives the remainder, so each miss narrows the variants still in play.

The narrowing makes the match provably exhaustive without a wildcard arm. After the last handler, every variant has been ruled out, so the remainder is an uninhabited type, and the matcher discharges it with `finalize_extract`, which is sound because no such value can exist. Adding a variant without adding its handler leaves the final remainder inhabited, so the code fails to compile until the variant is handled: the guarantee of a concrete `match`, recovered for a generic one.

The loop is a monadic pipeline. Each handler returns `Result<Output, Remainder>`, `Ok` for a match and `Err` for a miss, and the matcher runs the list under the ok monad, which continues on `Err` and stops at the first `Ok`. The list is built from small adapters: one that tries a single variant and forwards its payload, and one that strips the variant name so the payload's own computer sees the bare value. A convenience matcher builds this list from the enum's variants, so wiring an enum to a matcher needs only the matcher's name.

## Routing fields of a record to handlers

Building a record mirrors matching a variant: instead of taking a value apart and stopping at one branch, it starts from nothing and runs a handler for every field. The builder begins with an empty *partial record* from [`HasBuilder`](../reference/traits/has_builder.md), in which every field is absent, and pipes it through a list of per-field handlers. Each handler sees the partial record by reference, so it can read fields already set, computes one field, and sets it. After the list has run, every field is present and the builder finalizes the concrete struct.

The per-field tracking makes a missing handler a compile error. The operation that turns a partial record into the struct exists only when every field is present, so a builder that omits a field cannot finalize. Just as a matcher proves it covered every variant, a builder proves it filled every field. The field adapters are one that computes and sets a single named field, and one that computes a whole record and merges every shared field at once, which suits extending a record with a few extra fields.

## How the pieces fit together

Dispatching is the top of a stack, each layer supplying what the layer above needs:

1. **The extensible-data derives** give an enum the extractor traits and a record the builder traits, and expose the variant or field list through [`has_fields`](../reference/traits/has_fields.md).
2. **The [`extract_field`](../reference/traits/extract_field.md) and [`has_builder`](../reference/traits/has_builder.md) families** turn those into per-variant extraction with a remainder and per-field set-and-finalize.
3. **The [handler components](handlers.md)** provide the uniform `(context, Code, Input) -> Output` interface every per-element handler and dispatcher speaks.
4. **The dispatchers** are handler providers: a matcher is a [`PipeMonadic`](../reference/providers/monad_providers.md) pipeline under the ok monad, and a builder is a `PipeHandlers` pipeline.

The two directions implement different members of the family. The matchers and their adapters implement `Computer` and `AsyncComputer`, so they serve anywhere an infallible computer is expected. The builders also implement `TryComputer` and `Handler`, propagating a field handler's error.

The concrete providers are these:

- **Matching:** the `MatchWithHandlers` family (owned, by reference, and by mutable reference), the `MatchFirstWithHandlers` family for handlers that take extra arguments, and the `MatchWithValueHandlers` and `MatchWithFieldHandlers` conveniences that build the list from the enum. The per-variant adapters are `ExtractFieldAndHandle`, `HandleFieldValue`, and `DowncastAndHandle`, which matches a group of variants at once.
- **Building:** `BuildWithHandlers`, which drives the assembly, the per-field adapters `BuildAndSetField` and `BuildAndMerge`, and `BuildAndMergeOutputs` for a list of record-producing providers.

To turn a Rust trait with one impl per type into a variant-dispatching impl over an enum, [`#[cgp_auto_dispatch]`](../reference/macros/cgp_auto_dispatch.md) generates the matcher wiring, so none of these providers has to be named.

## Related constructs

These constructs are the ones dispatching works with:

- [Dispatch combinators](../reference/providers/dispatch_combinators.md) — the providers that implement the pattern.
- [`extract_field`](../reference/traits/extract_field.md), [`has_builder`](../reference/traits/has_builder.md), and [`has_fields`](../reference/traits/has_fields.md) — the traits underneath.
- [Handlers](handlers.md) and [monad providers](../reference/providers/monad_providers.md) — the handler interface and the matcher's pipeline.
- [`#[cgp_auto_dispatch]`](../reference/macros/cgp_auto_dispatch.md) — automates the pattern for a per-type trait.
- [Extensible records](extensible-records.md) and [extensible variants](extensible-variants.md) — the data-type view behind the two directions.
- The [application builder](../../examples/application-builder.md), [extensible shapes](../../examples/extensible-shapes.md), and [expression interpreter](../../examples/expression-interpreter.md) examples.

## Source

The dispatching pattern is implemented entirely by the providers in [crates/extra/cgp-dispatch/src/providers/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-dispatch/src/providers/), which build on the extractor and builder traits in [crates/core/cgp-field/src/traits/](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-field/src/traits/) and the handler components in [crates/extra/cgp-handler/src/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-handler/src/). The matcher loop reuses the monadic pipeline from [crates/extra/cgp-monad/src/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-monad/src/). Tests covering both directions are in [crates/tests/cgp-tests/tests/extensible_records/](https://github.com/contextgeneric/cgp/tree/main/crates/tests/cgp-tests/tests/extensible_records/) and [crates/tests/cgp-tests/tests/extensible_variants/](https://github.com/contextgeneric/cgp/tree/main/crates/tests/cgp-tests/tests/extensible_variants/), and the macro that generates dispatch wiring is exercised in [crates/tests/cgp-tests/tests/dispatching/](https://github.com/contextgeneric/cgp/tree/main/crates/tests/cgp-tests/tests/dispatching/).
