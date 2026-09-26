# Error design

`transfer` reports every failure as an HTTP status with a plain-text message, and the status is
chosen by the type a provider raises with, not by a runtime value. This document records how that
works in the crate. The general technique of an abstract error type plus raising components is
[modular error handling](../../../../cgp/concepts/modular-error-handling.md).

## One error type, raised with a status marker

The crate has one concrete error, [`AppError`](../reference/error-providers.md#apperror), a status code
paired with an `anyhow::Error` detail, and it reaches the rest of the code only as the context's
abstract `HasErrorType::Error`. `MockNamespace` fixes that abstract type to `AppError`, and every
handler and backend imports it as a bare `Error` with `#[use_type(HasErrorType.Error)]`, so none of
them names `AppError`.

Providers raise errors through the crate's own component, not through CGP's `CanRaiseError`:

```rust
#[cgp_component(HttpErrorRaiser)]
#[prefix(@app.error in DefaultNamespace)]
#[use_type(HasErrorType.Error)]
pub trait CanRaiseHttpError<Code, Detail> {
    fn raise_http_error(_code: Code, detail: Detail) -> Error;
}
```

`Code` is one of four zero-sized markers, `ErrUnauthorized`, `ErrBadRequest`, `ErrNotFound`, and
`ErrInternal`, so the status class is part of the call's type. A provider that needs to report a
missing user writes `Self::raise_http_error(ErrNotFound, format!(...))` and declares the dependency
as `#[uses(CanRaiseHttpError<ErrNotFound, String>)]`. That makes each provider's possible statuses
visible in its imports: `UseMockedApp`'s transfer raises `404` and `400`, and nothing else can.

## The provider is chosen per detail type

The component is generic over `Detail` as well as `Code`, so the wiring can choose a different
provider for each detail type. `MockNamespace` uses that freedom only once:

```rust
@app.error.HttpErrorRaiserComponent.<Code> Code.String:
    DisplayHttpError,
```

The key dispatches on both parameters in order: any `Code`, with a `String` detail, goes to
`DisplayHttpError`. That provider maps the marker to a status through the ordinary `IsStatusCode`
trait and formats the detail into an `anyhow::Error`. Every call site in the crate passes a `String`
detail, so this one entry covers every error the service raises.

The crate also defines `HandleHttpErrorWithAnyhow`, a provider for details that are already
`anyhow::Error` values, which would forward the detail instead of formatting it. No wiring entry
selects it and no call site raises an `anyhow::Error` detail, so it is unused; see
[issues.md](../issues.md#housekeeping).

## Where the status reaches the client

The status travels inside the error value until the routing layer turns it into a response. The
route closures in `providers/axum/routes.rs` map a failed handler result through `handle_api_error`,
which returns the `(StatusCode, String)` pair Axum sends: the stored status, and the detail's
`Display` text. So the body of an error response is exactly the message the provider formatted, such
as `404` with `recipient not found in mocked database: carol`.

Two kinds of failure never pass through `CanRaiseHttpError`. A request whose query string does not
deserialize, such as `currency=GBP`, is rejected by Axum's `Query` extractor before any handler runs,
with Axum's own `400` message. And an HTTP method with no route, such as `GET /transfer`, gets Axum's
`405`. [The request lifecycle](request-lifecycle.md) records the response for each path.

## Source

- [`interfaces/error.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/interfaces/error.rs)
  — the component and the four markers.
- [`providers/error.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/error.rs)
  — `IsStatusCode` and the two providers.
- [`types/error.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/types/error.rs)
  — `AppError`.
- [`namespaces/mock.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/namespaces/mock.rs)
  — the error wiring.

## Public material derived from this

Section 2, "Status-coded errors", of the crate's own README.
