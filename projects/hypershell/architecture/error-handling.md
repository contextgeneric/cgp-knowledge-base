# Error handling

Every Hypershell provider reports failure through the context's abstract error type, and only the
namespace decides what that type is. This document describes how providers raise and annotate
errors, how `HypershellNamespace` makes them concrete with `anyhow`, and what an extension that
raises a new kind of error must add. The CGP side is
[modular error handling](../../../cgp/concepts/modular-error-handling.md).

## Providers name the error sources, never the error type

**A provider requires `CanRaiseError<E>` for each source error it can produce and
`CanWrapError<D>` for each detail it attaches.** `Handler` returns `Result<Output, Error>` against
the context's [`HasErrorType`](../../../cgp/reference/components/has_error_type.md), so no provider
names `anyhow::Error` or any other concrete type. `HandleCoreExec` shows the full pattern: it raises
the `std::io::Error` from spawning a process, then wraps it with a `CommandNotFound` detail when the
kind is `NotFound`, and with a `SpawnCommandFailure` detail in every case.

```rust
Context: CanRaiseError<std::io::Error>
    + for<'a> CanWrapError<CommandNotFound<'a>>
    + for<'a> CanWrapError<SpawnCommandFailure<'a>>,
```

The detail structs borrow the `Command` rather than copying it, so the bounds are higher-ranked over
the borrow's lifetime. Each detail carries a `Debug` impl that writes a short message, and that
message is what the default wrapper records. A probe running a missing command produced this chain:

```text
error executing command: no-such-cmd-xyz a

Caused by:
    0: command not found: no-such-cmd-xyz
    1: No such file or directory (os error 2)
```

The error types a provider raises from its own logic are defined next to it: `ExecOutputError`
(a non-zero exit from `SimpleExec`, carrying the whole `Output`), `ErrorResponse` (a non-success HTTP
status, carrying the whole `Response`), and the detail structs `StdinPipeError`,
`WaitWithOutputError`, and `DecodeUtf8InputError`. The [reference](../reference/README.md) lists
each with its provider.

## The namespace makes the error concrete

**`HypershellNamespace` binds all three error components, routing every source error type to one
aggregate that picks a raising strategy per type.** The bindings are:

- **`ErrorTypeProviderComponent`** — `UseAnyhowError`, so the error type is `anyhow::Error`, which
  the prelude re-exports as `Error`.
- **`ErrorRaiserComponent`** — for each listed source type, `HypershellErrorHandler`.
- **`ErrorWrapperComponent`** — `DebugAnyhowError` for every detail, which formats the detail with
  `Debug` and attaches it as `anyhow` context.

`HypershellErrorHandler` is an aggregate provider that `open`s `ErrorRaiserComponent` and chooses a
strategy from the [error providers](../../../cgp/reference/providers/error_providers.md) and
`cgp-error-anyhow`:

| Source error | Strategy |
|---|---|
| `anyhow::Error` | `ReturnError` — already the context's error |
| `Infallible` | `RaiseInfallible` |
| `std::io::Error`, `Utf8Error`, `reqwest::Error`, `url::ParseError`, `InvalidHeaderName`, `InvalidHeaderValue`, `serde_json::Error` | `RaiseAnyhowError` — convert through `std::error::Error` |
| `ExecOutputError`, `ErrorResponse` | `DebugAnyhowError` — neither implements `std::error::Error`, so format with `Debug` |

`ErrorResponse` derives `Debug`, so the error for a non-success response is the `Debug` of the entire
`reqwest::Response`, headers included. A probe of a redirected request printed a single line
carrying the URL, status, and every response header. `ExecOutputError` writes its own `Debug`,
giving the exit code and the captured stderr.

## Every source error type is listed twice

**Each source type appears in the namespace's route list and again in `HypershellErrorHandler`'s
table, and a type in neither is a compile error at the first provider that raises it.** The route
list routes the path `@cgp.core.error.ErrorRaiserComponent.<Type>` to the aggregate, and the
aggregate maps the type to its strategy. An extension that raises a type the namespace has never
seen must add a route for it, which is why the `bluesky_websocket` example wires
`@cgp.core.error.ErrorRaiserComponent.TungsteniteError: RaiseAnyhowError` on its context. A probe
that raised an unregistered `TooLong` error from a custom handler failed with a
`[CGP-E107]` root cause naming the missing path; see [debugging](../guides/debugging.md).

The duplication has a reason. The namespace entries are routes and the aggregate entries are
choices, and keeping the choices in an aggregate lets a different namespace reuse them. But nothing
checks that the two lists agree, and they agree today only because both were written by hand.

## Where errors escape

Two failure paths bypass the error type entirely, both recorded as defects in
[issues.md](../issues.md#defects):

- `HandleWebsocket` calls `unwrap()` on the connection result, so a refused connection panics
  instead of raising `tungstenite::Error`.
- `HandleStreamingExec` ignores the child's exit status and discards its stderr, so a failing command
  in a streaming stage produces no error at all.

## Source

- The error wiring: [crates/hypershell/src/namespaces/handlers.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell/src/namespaces/handlers.rs) and [crates/hypershell/src/providers/error.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell/src/providers/error.rs)
- The error types and details: [crates/hypershell-tokio-components/src/providers/core_exec.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/core_exec.rs), [simple_exec.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/simple_exec.rs), [crates/hypershell-reqwest-components/src/providers/simple_request.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-reqwest-components/src/providers/simple_request.rs), and [crates/hypershell-components/src/providers/convert.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/providers/convert.rs)

## Public material derived from this

The error-handling part of page 2 of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
