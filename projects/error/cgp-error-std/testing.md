# Testing cgp-error-std

The crate has no tests of its own; it is tested by the `error_backends` target of the `cgp-tests`
crate, which runs with the rest of the `cgp` workspace suite.

## What the tests pin

Five files cover this crate:

- [`std_raise_and_wrap.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/std_raise_and_wrap.rs)
  — `RaiseBoxedStdError` as raiser and wrapper, including the wrapper impl: an `io::Error` survives
  `downcast_ref`, a `&'static str`, a `String`, and a `u32` detail all wrap, `{}`, `{:#}`, and `{:?}`
  print the detail and the chain, and the result downcasts to `WrapError`.
- [`std_formatting.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/std_formatting.rs)
  — `DebugBoxedStdError` and `DisplayBoxedStdError` dispatched per type with `open`: a `Debug`-only
  struct raises a `StringError` with the formatted message, and both wrappers stack.
- [`std_wrap_error.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/std_wrap_error.rs)
  — `WrapError` and `StringError` on their own: walking `source()` down a three-level chain yields each
  message exactly once, `{:#}` and `{:?}` print the joined chain, and `StringError` prints unquoted.
- [`swapping_backends.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/swapping_backends.rs)
  — the same generic provider on a std context as on the anyhow and eyre ones.
- [`readme_std.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/readme_std.rs)
  — the crate README's example, copied verbatim, since the README marks it `ignore`.

## What nothing tests

- **Without `std`.** Nothing builds the crate for a target without `std`; the `no_std` claim rests on
  its source, which uses only `core` and `alloc`.
- **Conversion into another backend.** Nothing converts a boxed error into an `anyhow::Error` or
  `eyre::Report` to confirm those reporters print the chain once; the chain walk in
  `std_wrap_error.rs` is the same traversal they perform.
- **Downstream use.** No project wires the crate.

**Public material derived from this:** None yet.
