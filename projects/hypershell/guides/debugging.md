# Debugging

A mistake in a Hypershell program or its wiring is a compile error, and the raw `rustc` output for
one spans every layer of wiring between the context and the provider that failed. This guide shows
the common mistakes, each with the code that triggers it, the root cause `cargo cgp check` reports,
and the fix. Every output below was produced by a probe against the `v0.8.0` branch and trimmed to
its headline, its root cause, and the part of the tree that locates it. The general technique is in
the CGP [debugging guide](../../../cgp/guides/debugging.md).

## Check first, then read the root cause

**Put the program in a `check_components!` before reading any error, and read it with
`cargo cgp check`.** A failure reported at the `handle` call often carries no root cause at all. The
missing-field mistake below, reported at its call site, produced only `[CGP-E002]` headlines about
`PipeHandlers` and `ComposeHandlers`. Through a check, the same mistake names the missing field. The
check is keyed on the program and its input:

```rust
check_components! {
    #[check_trait(CheckHypershellCli)]
    HypershellCli {
        HandlerComponent: (Program, Vec<u8>),
    }
}
```

The tree `cargo cgp check` prints follows the lookup described in
[assembly](../architecture/assembly.md#one-lookup-end-to-end). Each namespace hop and each bundle's
`open` redirect is a `[CGP-E104]` line, each provider a `[CGP-E102]`, and each consumer trait
reached through a dependency a `[CGP-E101]`. Read from the bottom: the last lines name the leaf that
failed. Two labels mislead. Every `[CGP-E104]` names the context as the table (`in HypershellCli`),
even for a redirect that runs inside a bundle such as `HypershellTokioProvider`. And a missing entry
in an aggregate reached through `open`, such as an input dispatcher, is reported as a `[CGP-E107]`
leaf that calls the aggregate a "context", rather than as the `[CGP-E110]` provider-table leaf the
[error-code catalog](../../../cargo-cgp/error-code.md) defines for a provider's table.

## A context lacks a field

A `FieldArg` names a field the context does not have. Here `HypershellCli`, which has no fields,
runs a program that reads `name`:

```rust
pub type Program = hypershell! {
        SimpleExec<StaticArg<"echo">, WithArgs[StaticArg<"Hello,">, FieldArg<"name">]>
    |   StreamToStdout
};
```

```text
error[E0277]: [CGP-E002] the provider trait `Handler<Pipe<…>, Vec<u8>>` with context `HypershellCli` is not implemented …
  = note: root cause: [CGP-E106] missing field `name` on `HypershellCli`
```

The tree runs through the pipeline, `HandleSimpleExec`, `CoreExec`, the command updater, and
`ExtractArgs` recursing over the argument list, down to the string extractor for `FieldArg<"name">`.
**Fix:** run the program on a context with the field, deriving `HasField`. The same error names
`http_client` when an HTTP program runs on a context without a client.

## A stage cannot accept the previous stage's output

The input type of a stage is the previous stage's output, and the error takes one of two forms
depending on whether the stage has an input dispatcher.

**A stage with a plain bound reports the unmet bound.** `SimpleExec` requires `AsRef<[u8]>`, and a
streaming stage's output is a stream:

```rust
pub type Program = hypershell! {
        StreamingExec<StaticArg<"echo">, WithStaticArgs["hello"]>
    |   SimpleExec<StaticArg<"wc">, WithStaticArgs["-c"]>
    |   StreamToStdout
};
```

```text
  = note: root cause: [CGP-E201] the trait bound `TokioAsyncReadStream<Either<ChildStdout, Empty>>: AsRef<[u8]>` is not satisfied
```

**Fix:** insert `StreamToBytes` between the two stages.

**A stage with an input dispatcher reports the missing dispatch entry.** Removing `BytesToHex` from
`http_checksum_native` leaves a raw digest flowing into `StreamToStdout`:

```rust
pub type Program = hypershell! {
    StreamingHttpRequest<GetMethod, FieldArg<"url">, WithHeaders[ ]>
    | Checksum<Sha256>
    | StreamToStdout
};
```

```text
  = note: root cause: [CGP-E107] context `HandleToTokioAsyncRead` does not contain any delegate entry for `@HandlerComponent.StreamToStdout.GenericArray<u8, …>`
```

The path names the syntax and then the input type, which is exactly what the dispatcher could not
match; see [streams and input dispatch](../architecture/streams-and-input-dispatch.md#dispatching-on-the-input-type).
**Fix:** convert the value into one of the dispatcher's input types, here with `BytesToHex`. The same
form appears for an input the program's caller passes: `StreamingExec` given a `&'static str`
reports a missing `@HandlerComponent.StreamingExec<…>.&str` entry, and the fix is to pass a
`String` or `Vec<u8>`.

## A syntax has no route

A syntax that no route reaches fails at the missing route, even when a provider for it exists.
`PutMethod` is implemented by `ExtractReqwestMethod`, but neither the reqwest bundle nor the namespace
lists it:

```rust
pub type Program = hypershell! {
    SimpleHttpRequest<PutMethod, StaticArg<"http://127.0.0.1:1/">, WithHeaders[]>
};
```

```text
error[E0277]: [CGP-E001] the consumer trait `CanHandle<SimpleHttpRequest<PutMethod, …>, Vec<u8>>` is not implemented for context `HypershellHttp`
  = note: root cause: [CGP-E107] context `HypershellHttp` does not contain any delegate entry for `@hypershell.core.MethodArgExtractorComponent.PutMethod`
```

`StreamToLines` fails the same way at `@cgp.extra.handler.HandlerComponent.StreamToLines.…`, and so
does `Checksum` or `WebSocket` on a context that joined only `HypershellNamespace`. **Fix:** add the
route on the context or on an extension namespace; see
[extending the language](extending-the-language.md). For `PutMethod`, `DeleteMethod`, and
`StreamToLines` the route is missing from the library itself; see [issues.md](../issues.md#defects).

## A raised error type has no route

A provider raises an error type the namespace does not know. This custom handler raises `TooLong`:

```rust
#[derive(Debug)]
pub struct TooLong;

#[cgp_impl(new HandleCheckLength)]
#[uses(CanRaiseError<TooLong>)]
#[use_type(HasErrorType.Error)]
impl<Input> Handler<CheckLength, Input>
where
    Input: AsRef<[u8]>,
{ /* … */ }
```

```text
error[E0277]: [CGP-E001] the consumer trait `CanHandle<CheckLength, _>` is not implemented for context `App`
  = note: root cause: [CGP-E107] context `App` does not contain any delegate entry for `@cgp.core.error.ErrorRaiserComponent.TooLong`
          this is required through the dependency chain:
            [CGP-E101] consumer trait impl `CanHandle<CheckLength, _>` for context `App`
            └─ [CGP-E104] redirect lookup to `@cgp.extra.handler.HandlerComponent` in `App`
              └─ [CGP-E102] provider trait impl `Handler<CheckLength, _>` with context `App` for provider `HandleCheckLength`
                └─ [CGP-E101] consumer trait impl `CanRaiseError<TooLong>` for context `App`
                  └─ [CGP-E104] redirect lookup to `@cgp.core.error.ErrorRaiserComponent` in `App`
                    └─ [CGP-E107] context `App` does not contain any delegate entry for `@cgp.core.error.ErrorRaiserComponent.TooLong`
```

**Fix:** route the type to a raiser, as
`@cgp.core.error.ErrorRaiserComponent.TooLong: DebugAnyhowError`, with `ErrorRaiserComponent`
imported from `cgp::core::error`; see [error handling](../architecture/error-handling.md).

## A routed provider cannot resolve

A route that exists can still lead to a provider whose own requirements fail. `ConvertTo` is routed
to `Promote<HandleConvert>`, which does not implement `Handler`:

```text
error[E0277]: [CGP-E001] the consumer trait `CanHandle<ConvertTo<String>, &str>` is not implemented for context `HypershellCli`
  = note: root cause: [CGP-E111] the provider trait `AsyncComputer` is not implemented for `HandleConvert`
```

There is no fix in a program; `ConvertTo` is broken in the library. See
[issues.md](../issues.md#convertto-never-resolves).

## Rebinding a syntax conflicts

An entry for a syntax the namespace already routes conflicts with the namespace:

```rust
delegate_components! {
    App {
        namespace HypershellNamespace;
        @cgp.extra.handler.HandlerComponent.<Path, Args> SimpleExec<Path, Args>: FakeSimpleExec,
    }
}
```

```text
error[E0119]: [CGP-E005] `App` cannot wire `@cgp.extra.handler.HandlerComponent.SimpleExec.*` that is already set through `HypershellNamespace`
```

The same entry in a namespace that inherits `HypershellNamespace` fails with a plain `E0119` on the
namespace trait. **Fix:** see [replacing an interpretation](extending-the-language.md#replace-the-interpretation-of-existing-syntax).

## The macro fails

Three `hypershell!` failures come from the macro rather than the wiring, and none mentions CGP:

- **"cannot find macro `Product` in this scope"** or **"cannot find type `Pipe` in this scope"** —
  the prelude is not imported. Import `hypershell::prelude::*`.
- **"proc macro panicked … mismatch > at the end of token stream"** — an unbalanced `<`.
- **"expected one of `!`, `(`, `,`, `::`, `<`, or `>`, found `<eof>`"** — a `->` inside the program,
  whose `>` the macro reads as closing a group. Write that type outside the macro and refer to it by
  an alias.

See [the macro reference](../reference/macro.md#known-issues).

## Public material derived from this

The diagnostics section of the planned trade-offs page of the
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
