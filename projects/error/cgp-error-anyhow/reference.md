# cgp-error-anyhow reference

The crate's four providers each implement one role of the
[shared design](../architecture.md#the-four-roles) for `anyhow::Error`, and every one but the type
provider pins the context's error to `anyhow::Error` through `#[use_type]`. The crate also re-exports
`anyhow::Error` as `cgp_error_anyhow::Error`, so a project can name its error type without depending
on anyhow directly.

## `UseAnyhowError`

`UseAnyhowError` sets the context's abstract error type to `anyhow::Error`.

### Definition

```rust
pub struct UseAnyhowError;

#[cgp_impl(UseAnyhowError)]
impl ErrorTypeProvider {
    type Error = anyhow::Error;
}
```

### Behavior

Wired to `ErrorTypeProviderComponent`, it makes the context implement `HasErrorType` with
`Error = anyhow::Error`, which is what the other three providers require. It is equivalent to
`UseType<anyhow::Error>`.

### Context dependencies

None.

## `RaiseAnyhowError`

`RaiseAnyhowError` raises a standard error into `anyhow::Error` without formatting it, and wraps a
`'static` detail as anyhow context.

### Definition

```rust
pub struct RaiseAnyhowError;

#[cgp_impl(RaiseAnyhowError)]
#[use_type(HasErrorType.{Error = anyhow::Error})]
impl<E> ErrorRaiser<E>
where
    E: StdError + Send + Sync + 'static,
{
    fn raise_error(e: E) -> Error { ... }
}

#[cgp_impl(RaiseAnyhowError)]
#[use_type(HasErrorType.{Error = anyhow::Error})]
impl<Detail> ErrorWrapper<Detail>
where
    Detail: Display + Send + Sync + 'static,
{
    fn wrap_error(error: Error, detail: Detail) -> Error { ... }
}
```

### Behavior

Raising converts the source with `From`, so the error keeps the source value: `downcast_ref::<E>()`
finds it, and it is the first link of `chain()`. The error's `{}` is the source's own message.

Wrapping calls `anyhow::Error::context` with the detail. The result prints the outermost detail with
`{}`, the whole chain joined by `": "` with `{:#}`, and the outermost detail followed by a
`Caused by:` list with `{:?}`. A wrapped error still downcasts to the original source. Wrapping
`"while loading"` and then `String::from("while starting")` around an `io::Error` reading
`no file` gives `while starting: while loading: no file` under `{:#}`.

The raiser rejects any source that is not a standard error, `String` included, and the wrapper
rejects a borrowed detail; see [debugging](../guides/debugging.md#a-message-routed-to-the-raise-provider)
and [a borrowed detail](../guides/debugging.md#a-borrowed-detail).

### Context dependencies

`HasErrorType<Error = anyhow::Error>`, which `UseAnyhowError` supplies.

## `DebugAnyhowError`

`DebugAnyhowError` raises any `Debug` value as a new anyhow message formatted with `{:?}`, and wraps a
`Debug` detail the same way.

### Definition

```rust
pub struct DebugAnyhowError;

#[cgp_impl(DebugAnyhowError)]
#[use_type(HasErrorType.{Error = anyhow::Error})]
impl<E> ErrorRaiser<E>
where
    E: Debug,
{
    fn raise_error(e: E) -> Error { ... }
}

#[cgp_impl(DebugAnyhowError)]
#[use_type(HasErrorType.{Error = anyhow::Error})]
impl<Detail> ErrorWrapper<Detail>
where
    Detail: Debug,
{
    fn wrap_error(error: Error, detail: Detail) -> Error { ... }
}
```

### Behavior

Raising builds `anyhow!("{e:?}")`, so the error holds only the formatted message: its chain has one
link and the source value cannot be recovered. Raising `Rejected { code: 7 }` prints
`Rejected { code: 7 }`, and raising the string `"quoted message"` prints `"quoted message"` with its
quotation marks, since that is a string's `Debug` form.

Wrapping formats the detail with `{:?}` and adds the resulting `String` with `context`, which accepts
any `Debug` detail, borrowed or not. Wrapping `42u32` prints `42`.

### Context dependencies

`HasErrorType<Error = anyhow::Error>`.

## `DisplayAnyhowError`

`DisplayAnyhowError` raises any `Display` value as a new anyhow message formatted with `{}`, and wraps
a `Display` detail the same way.

### Definition

```rust
pub struct DisplayAnyhowError;

#[cgp_impl(DisplayAnyhowError)]
#[use_type(HasErrorType.{Error = anyhow::Error})]
impl<E> ErrorRaiser<E>
where
    E: Display,
{
    fn raise_error(e: E) -> Error { ... }
}

#[cgp_impl(DisplayAnyhowError)]
#[use_type(HasErrorType.{Error = anyhow::Error})]
impl<Detail> ErrorWrapper<Detail>
where
    Detail: Display,
{
    fn wrap_error(error: Error, detail: Detail) -> Error { ... }
}
```

### Behavior

Raising builds `anyhow!("{e}")`, which is the provider to use for a `String` or another message:
raising `String::from("plain message")` prints `plain message`. Like `DebugAnyhowError`, it keeps only
the message, so a standard error raised through it loses its type and its own source chain.

Wrapping converts the detail with `to_string` and adds it with `context`, so it accepts a borrowed
detail that `RaiseAnyhowError` would reject.

### Context dependencies

`HasErrorType<Error = anyhow::Error>`.

## Source

- [`src/lib.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-anyhow/src/lib.rs)
  — the re-exports
- [`src/impls/use_anyhow_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-anyhow/src/impls/use_anyhow_error.rs)
- [`src/impls/raise_anyhow_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-anyhow/src/impls/raise_anyhow_error.rs)
- [`src/impls/debug_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-anyhow/src/impls/debug_error.rs)
- [`src/impls/display_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-anyhow/src/impls/display_error.rs)

**Public material derived from this:** the crate's README, and the item docs in its source.
