# `builder` architecture

`builder` rests on a few decisions that every provider and context in it follows, stated together
here. The pattern behind them, the extensible builder, is taught in the
[application builder](../../../../examples/application-builder.md) worked example, and its internals
(partial records, `BuildWithHandlers`, `BuildAndMerge`) are documented under
[cgp/](../../../../cgp/reference/providers/dispatch_combinators.md#buildwithhandlers-and-buildandmergeoutputs),
so this page says only what the crate does with it.

## The design on one page

**Each subsystem is built by its own handler.** A builder provider implements CGP's
[`Handler`](../../../../cgp/reference/components/handler.md) component, so it is async and fallible, and
it is generic over the `Code` and `Input` it ignores. It reads its configuration from the builder
context through a getter trait, raises any failure into the context's abstract error, and returns a
struct holding only the fields it built. `BuildSqliteClient` reads `db_options` and `db_journal_mode`
and returns `SqliteClient { sqlite_pool }`. See [subsystem providers](../reference/subsystem-providers.md).

**Most subsystems have two builders.** A configurable one reads the full configuration, and a default
one reads less or nothing: `BuildSqliteClient` against `BuildDefaultSqliteClient`, `BuildHttpClient`
against `BuildDefaultHttpClient`, and `BuildOpenAiClient` against `BuildDefaultOpenAiClient`. A builder
context picks one per subsystem, so two contexts with different configuration fields can build the
same application type.

**Outputs merge into the target by field name.** Every output struct and every application struct
derives `HasField`, `HasFields`, and `BuildField`. `BuildAndMergeOutputs<Target, Product![…]>` starts
an empty builder for the target, runs each provider in order, merges each output's fields into the
builder, and finalizes it. The merge matches fields by name and type, so `SqliteClient`'s
`sqlite_pool` lands in `App`'s `sqlite_pool` with no code written, and the target is complete only if
the providers together supply every field.

**A builder context is configuration plus wiring.** Each builder context is a struct of `String`
configuration fields that derives `HasField`, which satisfies the providers' getters, and
`Deserialize`, so it can be loaded from a file. Its wiring picks `anyhow::Error` as the abstract error
through `cgp-error-anyhow`, and wires `HandlerComponent` to the merge dispatcher. Building is one call,
`builder.handle(PhantomData::<()>, ())`. See [builder contexts](../reference/builder-contexts.md).

**One builder can target several applications, selected by code.** `AnthropicAndChatGptAppBuilder`
carries the configuration for every provider it might use, and dispatches `HandlerComponent` on the
`Code` parameter: each of three marker types selects a different target and provider list. The
configuration field `llm_preamble` is read by both AI providers from the same field.

**The application structs stay plain.** The targets are ordinary structs with public fields and no
wiring of their own; the builders produce them, and nothing else in the crate uses them. `App` also
keeps two hand-written constructors, the starting point the pattern replaces. See
[application contexts](../reference/application-contexts.md).

## Public material derived from this

Pages 1 and 2 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
