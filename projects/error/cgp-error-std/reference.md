# cgp-error-std reference

The crate's four providers each implement one role of the
[shared design](../architecture.md#the-four-roles) for a boxed standard error, and every one but the
type provider pins the context's error to `cgp_error_std::Error` through `#[use_type]`. The providers
build two error types of the crate's own, `StringError` for a formatted message and `WrapError` for a
detail around another error, which are documented after the providers.

## `UseBoxedStdError`

`UseBoxedStdError` sets the context's abstract error type to `Error`, a boxed standard error.

### Definition

```rust
pub struct UseBoxedStdError;

#[cgp_impl(UseBoxedStdError)]
impl ErrorTypeProvider {
    type Error = crate::Error;
}
```

### Behavior

Wired to `ErrorTypeProviderComponent`, it makes the context implement `HasErrorType` with
`Error = Box<dyn core::error::Error + Send + Sync + 'static>`. It is equivalent to
`UseType<cgp_error_std::Error>`.

### Context dependencies

None.

## `RaiseBoxedStdError`

`RaiseBoxedStdError` boxes a standard error without formatting it, and wraps a `Display` detail in a
`WrapError`.

### Definition

```rust
pub struct RaiseBoxedStdError;

#[cgp_impl(RaiseBoxedStdError)]
#[use_type(HasErrorType.{Error = crate::Error})]
impl<E> ErrorRaiser<E>
where
    E: StdError + Send + Sync + 'static,
{
    fn raise_error(e: E) -> Error { ... }
}

#[cgp_impl(RaiseBoxedStdError)]
#[use_type(HasErrorType.{Error = crate::Error})]
impl<Detail> ErrorWrapper<Detail>
where
    Detail: Display,
{
    fn wrap_error(error: Error, detail: Detail) -> Error { ... }
}
```

### Behavior

Raising boxes the source, so `downcast_ref::<E>()` on the boxed error finds it and the error prints as
the source prints.

Wrapping converts the detail with `to_string` and boxes a `WrapError` holding it and the wrapped
error. The result downcasts to `WrapError`, prints the detail with `{}`, and prints the chain with
`{:#}` or `{:?}`: wrapping `"while loading"` and then `String::from("while starting")` around an
`io::Error` reading `no file` prints `while starting` and `while starting: while loading: no file`.
Because the detail is copied, any `Display` detail works, borrowed or not.

### Context dependencies

`HasErrorType<Error = cgp_error_std::Error>`, which `UseBoxedStdError` supplies.

## `DebugBoxedStdError`

`DebugBoxedStdError` raises any `Debug` value as a `StringError` formatted with `{:?}`, and wraps a
`Debug` detail in a `WrapError` the same way.

### Definition

```rust
pub struct DebugBoxedStdError;

#[cgp_impl(DebugBoxedStdError)]
#[use_type(HasErrorType.{Error = crate::Error})]
impl<E> ErrorRaiser<E>
where
    E: Debug,
{
    fn raise_error(e: E) -> Error { ... }
}

#[cgp_impl(DebugBoxedStdError)]
#[use_type(HasErrorType.{Error = crate::Error})]
impl<Detail> ErrorWrapper<Detail>
where
    Detail: Debug,
{
    fn wrap_error(error: Error, detail: Detail) -> Error { ... }
}
```

### Behavior

Raising formats the value with `{:?}` and boxes a `StringError` holding the message, so the boxed
error downcasts to `StringError` and never to the original type. Raising `Rejected { code: 7 }` gives
a `StringError` whose `message` is `Rejected { code: 7 }`; a string keeps its quotation marks.
Wrapping formats the detail with `{:?}` into a `WrapError`.

### Context dependencies

`HasErrorType<Error = cgp_error_std::Error>`.

## `DisplayBoxedStdError`

`DisplayBoxedStdError` raises any `Display` value as a `StringError` formatted with `{}`, and wraps a
`Display` detail in a `WrapError` the same way.

### Definition

```rust
pub struct DisplayBoxedStdError;

#[cgp_impl(DisplayBoxedStdError)]
#[use_type(HasErrorType.{Error = crate::Error})]
impl<E> ErrorRaiser<E>
where
    E: Display,
{
    fn raise_error(e: E) -> Error { ... }
}

#[cgp_impl(DisplayBoxedStdError)]
#[use_type(HasErrorType.{Error = crate::Error})]
impl<Detail> ErrorWrapper<Detail>
where
    Detail: Display,
{
    fn wrap_error(error: Error, detail: Detail) -> Error { ... }
}
```

### Behavior

Raising converts the value with `to_string` into a boxed `StringError`, the provider to use for a
`String` or another message. Wrapping does the same with the detail into a `WrapError`. As a
wrapper it behaves exactly like `RaiseBoxedStdError`'s, which has the same bound.

### Context dependencies

`HasErrorType<Error = cgp_error_std::Error>`.

## `Error`

`Error` is the boxed standard error that `UseBoxedStdError` makes the context's error type.

### Definition

```rust
pub type Error = Box<dyn StdError + Send + Sync + 'static>;
```

### Behavior

It is a plain alias, so every standard-library facility for boxed errors applies: `?` converts a
standard error into it, `downcast_ref` recovers a concrete type, and `source()` walks the chain. It
satisfies `HasErrorType`'s `Debug` bound through the boxed error's own `Debug`.

## `StringError`

`StringError` is a standard error that holds only a message, which the formatting providers build
from a value that is not itself a standard error.

### Definition

```rust
pub struct StringError {
    pub message: String,
}

impl From<String> for StringError { ... }
impl Debug for StringError { ... }
impl Display for StringError { ... }
impl Error for StringError {}
```

### Behavior

Both `{}` and `{:?}` print the message unquoted, and `source()` returns `None`. It is constructed from
a `String` with `From`.

## `WrapError`

`WrapError` is a standard error that holds a detail message and the error it wraps, which every
wrapper in the crate builds.

### Definition

```rust
pub struct WrapError {
    pub detail: String,
    pub source: Error,
}

impl Display for WrapError { ... }
impl Debug for WrapError { ... }
impl StdError for WrapError {
    fn source(&self) -> Option<&(dyn StdError + 'static)> { ... }
}
```

### Behavior

`source()` returns the wrapped error. `{}` prints the detail alone, so a reporter that walks
`source()` prints each message once. `{:#}` and `{:?}` print the detail followed by the `Display` of
every error down the chain, each joined by `": "`; a three-level chain reading `outer`, `middle`,
`inner` prints `outer` and `outer: middle: inner`. The chain form prints each link with plain `{}`, so
a nested `WrapError` contributes its detail alone and the walk continues past it.

## Source

- [`src/lib.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-std/src/lib.rs)
  — the re-exports
- [`src/types/error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-std/src/types/error.rs)
- [`src/types/string.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-std/src/types/string.rs)
- [`src/types/wrap.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-std/src/types/wrap.rs)
- [`src/impls/use_boxed.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-std/src/impls/use_boxed.rs)
- [`src/impls/raise_boxed.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-std/src/impls/raise_boxed.rs)
- [`src/impls/debug_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-std/src/impls/debug_error.rs)
- [`src/impls/display_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/standalone/error/cgp-error-std/src/impls/display_error.rs)

**Public material derived from this:** the crate's README, and the item docs in its source.
