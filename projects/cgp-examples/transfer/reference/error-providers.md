# Error providers

The error providers are the two implementations of `HttpErrorRaiser`, the trait that maps a status
marker to an HTTP status, and the concrete error they build. All three are written for this
deployment's `AppError`, not for any error type, which is the design choice
[error design](../architecture/error-design.md) explains.

## `IsStatusCode`

`IsStatusCode` is an ordinary trait, not a component, that maps a status marker to an Axum
`StatusCode`.

### Definition

```rust
pub trait IsStatusCode {
    fn status_code() -> StatusCode;
}

impl IsStatusCode for ErrUnauthorized { ... }
impl IsStatusCode for ErrBadRequest { ... }
impl IsStatusCode for ErrNotFound { ... }
impl IsStatusCode for ErrInternal { ... }
```

### Behavior

The four impls return `UNAUTHORIZED` (401), `BAD_REQUEST` (400), `NOT_FOUND` (404), and
`INTERNAL_SERVER_ERROR` (500). A provider reads the status from the marker's type, so the mapping
involves no runtime match.

### Context dependencies

None; it is implemented on the markers.

## `DisplayHttpError`

`DisplayHttpError` raises an `AppError` from any status marker and any `Display` detail.

### Definition

```rust
#[cgp_impl(new DisplayHttpError)]
#[use_type(HasErrorType.{Error = AppError})]
impl<Code, Detail> HttpErrorRaiser<Code, Detail>
where
    Code: IsStatusCode,
    Detail: Display,
{
    fn raise_http_error(_code: Code, detail: Detail) -> AppError { ... }
}
```

### Behavior

It sets the status from `Code::status_code()` and formats the detail into the error with
`anyhow!("{detail}")`, so the response body is the detail's `Display` text. The
[`#[use_type]` equality form](../../../../cgp/reference/attributes/use_type.md) requires the context's
error to be `AppError`, which is what lets the body construct one. `MockNamespace` wires it for every
`Code` with a `String` detail, which covers every call site in the crate. Because the impl is generic,
it cannot register itself with `#[default_impl]` and is wired in the namespace body instead.

### Context dependencies

`HasErrorType<Error = AppError>`.

## `HandleHttpErrorWithAnyhow`

`HandleHttpErrorWithAnyhow` raises an `AppError` from any status marker and any detail that converts
into `anyhow::Error`, keeping the detail's error chain.

### Definition

```rust
#[cgp_impl(new HandleHttpErrorWithAnyhow)]
#[use_type(HasErrorType.{Error = AppError})]
impl<Code, Detail> HttpErrorRaiser<Code, Detail>
where
    Code: IsStatusCode,
    anyhow::Error: From<Detail>,
{
    fn raise_http_error(_code: Code, detail: Detail) -> AppError { ... }
}
```

### Behavior

It sets the status the same way and stores `detail.into()` instead of formatting it. No wiring entry
selects it and no call site raises with an `anyhow::Error` detail, so it never runs.

### Context dependencies

`HasErrorType<Error = AppError>`.

### Known issues

Unused; see [issues.md](../issues.md#housekeeping).

## `AppError`

`AppError` is the concrete error the context wires as its abstract error type.

### Definition

```rust
#[derive(Debug)]
pub struct AppError {
    pub status_code: StatusCode,
    pub detail: anyhow::Error,
}
```

### Behavior

It satisfies `HasErrorType`'s `Debug` bound through the derive. The routing layer's `handle_api_error`
turns it into the `(StatusCode, String)` pair Axum sends, using the detail's `Display` text as the
body; see the [HTTP layer](http-layer.md#the-axum-routing-traits).

### Context dependencies

None; it is plain data.

## Source

- [`providers/error.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/error.rs)
  — `IsStatusCode`, `DisplayHttpError`, and `HandleHttpErrorWithAnyhow`.
- [`types/error.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/types/error.rs)
  — `AppError`.

## Public material derived from this

Section 2, "Status-coded errors", of the crate's own README.
