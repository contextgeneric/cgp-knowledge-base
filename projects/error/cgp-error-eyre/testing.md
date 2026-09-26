# Testing cgp-error-eyre

The crate has no tests of its own; it is tested by the `error_backends` target of the `cgp-tests`
crate, which runs with the rest of the `cgp` workspace suite. No test in that target calls
`eyre::set_hook`, so every eyre test also checks that the crate's `auto-install` feature supplies a
handler: with the feature removed, both eyre tests fail with the handler panic.

## What the tests pin

Five files cover this crate:

- [`eyre_raise_and_wrap.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/eyre_raise_and_wrap.rs)
  — `RaiseEyreError` as raiser and wrapper: an `io::Error` survives `downcast_ref` before and after
  wrapping, `{}` and `{:#}` print the outermost detail and the chain, and `{:?}` begins with the
  default handler's numbered `Caused by:` form. The `{:?}` check matches a prefix because the
  handler appends a `Location:` section, and a backtrace when `RUST_BACKTRACE` or
  `RUST_LIB_BACKTRACE` is set.
- [`eyre_location.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/eyre_location.rs)
  — the `Location:` a report records is the line that called `raise_error`, through plain, `open`,
  and namespace-path wiring, for each of the three raisers and for the generic `RaiseFrom` over
  `UseType<eyre::Report>`, and wrapping keeps it. With the
  `#[track_caller]` removed from `raise_error`, the test fails with a location inside
  `raise_eyre_error.rs`.
- [`eyre_formatting.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/eyre_formatting.rs)
  — `DebugEyreError` and `DisplayEyreError` dispatched per type with `open`: a `Debug`-only struct
  and a `String` raise, a formatted report has a one-link chain, and both wrappers stack.
- [`swapping_backends.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/swapping_backends.rs)
  — the same generic provider on an eyre context as on the anyhow and std ones.
- [`readme_eyre.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/readme_eyre.rs)
  — the crate README's example, which the `cgp-tests` build script turns into a test, since the
  README marks it `ignore`.

## What nothing tests

- **A custom handler.** Nothing installs one, so the interaction with `set_hook` rests on eyre's
  source and on a probe in which `set_hook` returned an error after the first report.
- **Downstream use.** No project wires the crate.

**Public material derived from this:** None yet.
