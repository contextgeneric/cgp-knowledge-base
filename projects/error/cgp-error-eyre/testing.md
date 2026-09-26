# Testing cgp-error-eyre

The crate has no tests of its own; it is tested by the `error_backends` target of the `cgp-tests`
crate, which runs with the rest of the `cgp` workspace suite. No test in that target calls
`eyre::set_hook`, so every eyre test also checks that the crate's `auto-install` feature supplies a
handler: with the feature removed, both eyre tests fail with the handler panic.

## What the tests pin

Four files cover this crate:

- [`eyre_raise_and_wrap.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/eyre_raise_and_wrap.rs)
  — `RaiseEyreError` as raiser and wrapper: an `io::Error` survives `downcast_ref` before and after
  wrapping, `{}` and `{:#}` print the outermost detail and the chain, and `{:?}` begins with the
  default handler's numbered `Caused by:` form and has no `Location:` section. The `{:?}` check
  matches a prefix because the handler appends a backtrace when `RUST_BACKTRACE` or
  `RUST_LIB_BACKTRACE` is set.
- [`eyre_formatting.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/eyre_formatting.rs)
  — `DebugEyreError` and `DisplayEyreError` dispatched per type with `open`: a `Debug`-only struct
  and a `String` raise, a formatted report has a one-link chain, and both wrappers stack.
- [`swapping_backends.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/swapping_backends.rs)
  — the same generic provider on an eyre context as on the anyhow and std ones.
- [`readme_eyre.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/readme_eyre.rs)
  — the crate README's example, copied verbatim, since the README marks it `ignore`.

## What nothing tests

- **A custom handler.** Nothing installs one, so the interaction with `set_hook` rests on eyre's
  source and on a probe in which `set_hook` returned an error after the first report.
- **`track-caller` enabled elsewhere.** The workspace never enables it, so the `Location:` section it
  would add, and that section naming a line inside the crate, is shown only by a probe.
- **Downstream use.** No project wires the crate.

**Public material derived from this:** None yet.
