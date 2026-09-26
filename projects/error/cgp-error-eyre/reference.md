# cgp-error-eyre reference

The crate's four providers each implement one role of the
[shared design](../architecture.md#the-four-roles) for `eyre::Report`, and every one but the type
provider pins the context's error to `eyre::Report` through `#[use_type]`. The crate also re-exports
`eyre::Error`, eyre's alias for `Report`, as `cgp_error_eyre::Error`. Every report is built by eyre's
installed handler, which the crate's `auto-install` feature supplies; see
[the report handler](README.md#the-report-handler).

## `UseEyreError`

`UseEyreError` sets the context's abstract error type to `eyre::Report`.

### Definition

```rust
pub struct UseEyreError;

#[cgp_impl(UseEyreError)]
impl ErrorTypeProvider {
    type Error = eyre::Report;
}
```

### Behavior

Wired to `ErrorTypeProviderComponent`, it makes the context implement `HasErrorType` with
`Error = eyre::Report`, which the other three providers require. It is equivalent to
`UseType<eyre::Report>`.

### Context dependencies

None.

## `RaiseEyreError`

`RaiseEyreError` raises a standard error into `eyre::Report` without formatting it, and wraps a
`'static` detail with `wrap_err`.

### Definition

```rust
pub struct RaiseEyreError;

#[cgp_impl(RaiseEyreError)]
#[use_type(HasErrorType.{Error = eyre::Report})]
impl<E> ErrorRaiser<E>
where
    E: StdError + Send + Sync + 'static,
{
    fn raise_error(e: E) -> Error { ... }
}

#[cgp_impl(RaiseEyreError)]
#[use_type(HasErrorType.{Error = eyre::Report})]
impl<Detail> ErrorWrapper<Detail>
where
    Detail: Display + Send + Sync + 'static,
{
    fn wrap_error(error: Error, detail: Detail) -> Error { ... }
}
```

### Behavior

Raising converts the source with `From`, so the report keeps the source value: `downcast_ref::<E>()`
finds it, before and after wrapping, and it is the first link of `chain()`.

Wrapping calls `eyre::Report::wrap_err`. The result prints the outermost detail with `{}` and the
whole chain joined by `": "` with `{:#}`. With the default handler, `{:?}` prints the outermost detail
followed by a numbered `Caused by:` list; wrapping `"while loading"` and then
`String::from("while starting")` around an `io::Error` reading `no file` prints

```text
while starting

Caused by:
   0: while loading
   1: no file
```

After the chain the handler prints a `Location:` section with the file, line, and column that called
`raise_error`, since the crate enables eyre's `track-caller` feature and `raise_error` is
`#[track_caller]` through every impl; wrapping keeps that location. When `RUST_BACKTRACE` or
`RUST_LIB_BACKTRACE` is set, the handler also captures a backtrace and appends it at the end.

The raiser rejects any source that is not a standard error, and the wrapper rejects a borrowed
detail, exactly as anyhow's do; see [debugging](../guides/debugging.md).

### Context dependencies

`HasErrorType<Error = eyre::Report>`, which `UseEyreError` supplies.

## `DebugEyreError`

`DebugEyreError` raises any `Debug` value as a new eyre report formatted with `{:?}`, and wraps a
`Debug` detail the same way.

### Definition

```rust
pub struct DebugEyreError;

#[cgp_impl(DebugEyreError)]
#[use_type(HasErrorType.{Error = eyre::Report})]
impl<E> ErrorRaiser<E>
where
    E: Debug,
{
    fn raise_error(e: E) -> Error { ... }
}

#[cgp_impl(DebugEyreError)]
#[use_type(HasErrorType.{Error = eyre::Report})]
impl<Detail> ErrorWrapper<Detail>
where
    Detail: Debug,
{
    fn wrap_error(error: Error, detail: Detail) -> Error { ... }
}
```

### Behavior

Raising builds `eyre!("{e:?}")`, so the report holds only the formatted message, its chain has one
link, and the source value cannot be recovered. A string raised through it keeps its quotation marks.
Wrapping formats the detail with `{:?}` and adds the `String` with `wrap_err`, so it accepts a
borrowed detail.

### Context dependencies

`HasErrorType<Error = eyre::Report>`.

## `DisplayEyreError`

`DisplayEyreError` raises any `Display` value as a new eyre report formatted with `{}`, and wraps a
`Display` detail the same way.

### Definition

```rust
pub struct DisplayEyreError;

#[cgp_impl(DisplayEyreError)]
#[use_type(HasErrorType.{Error = eyre::Report})]
impl<E> ErrorRaiser<E>
where
    E: Display,
{
    fn raise_error(e: E) -> Error { ... }
}

#[cgp_impl(DisplayEyreError)]
#[use_type(HasErrorType.{Error = eyre::Report})]
impl<Detail> ErrorWrapper<Detail>
where
    Detail: Display,
{
    fn wrap_error(error: Error, detail: Detail) -> Error { ... }
}
```

### Behavior

Raising builds `eyre!("{e}")`, the provider to use for a `String` or another message. It keeps only
the message. Wrapping converts the detail with `to_string` and adds it with `wrap_err`, so it accepts
a borrowed detail.

### Context dependencies

`HasErrorType<Error = eyre::Report>`.

## Source

- [`Cargo.toml`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-eyre/Cargo.toml)
  — the eyre features and why
- [`src/lib.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-eyre/src/lib.rs)
  — the re-exports
- [`src/impls/use_eyre_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-eyre/src/impls/use_eyre_error.rs)
- [`src/impls/raise_eyre_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-eyre/src/impls/raise_eyre_error.rs)
- [`src/impls/debug_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-eyre/src/impls/debug_error.rs)
- [`src/impls/display_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-eyre/src/impls/display_error.rs)

**Public material derived from this:** the crate's README, and the item docs in its source.
