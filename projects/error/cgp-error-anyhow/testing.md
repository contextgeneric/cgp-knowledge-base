# Testing cgp-error-anyhow

The crate has no tests of its own; it is tested by the `error_backends` target of the `cgp-tests`
crate, which runs with the rest of the `cgp` workspace suite. Each file that wires a context also
asserts the wiring with `check_components!`, and checks at runtime what the raised and wrapped errors
print and whether the source survives.

## What the tests pin

Six files cover this crate:

- [`anyhow_raise_and_wrap.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/anyhow_raise_and_wrap.rs)
  — `RaiseAnyhowError` as raiser and wrapper: an `io::Error` survives `downcast_ref` before and after
  wrapping, a `&'static str` and a `String` detail both wrap, and `{}` and `{:#}` print the outermost
  detail and the chain.
- [`anyhow_formatting.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/anyhow_formatting.rs)
  — `DebugAnyhowError` and `DisplayAnyhowError` dispatched per source and detail type with `open`: a
  `Debug`-only struct, a `String`, and a `&'static str` raise, the string's `Debug` form keeps its
  quotes, a formatted error has a one-link chain, and both wrappers stack.
- [`namespace_wiring.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/namespace_wiring.rs)
  — the same providers wired by `@cgp.core.error.*` paths on a context that joins `DefaultNamespace`.
- [`generic_equivalents.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/generic_equivalents.rs)
  — `UseType<anyhow::Error>` with the generic `RaiseFrom` raises an `io::Error` exactly as the
  backend does, and re-raises an `anyhow::Error` through the reflexive `From`, which are the claims
  in [architecture.md](../architecture.md#what-a-backend-adds-over-the-generic-providers).
- [`readme_anyhow.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/readme_anyhow.rs)
  — the crate README's example, which the `cgp-tests` build script turns into a test, since the
  README marks it `ignore`.
- [`swapping_backends.rs`](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/error_backends/swapping_backends.rs)
  — one provider generic over `CanRaiseError` and `CanWrapError` runs unchanged on an anyhow, an
  eyre, and a std context and produces the same messages from each.

## Downstream coverage

Hypershell, cgp-serde, and cgp-examples depend on the crate, and each overrides it through its
`[patch.crates-io]` section with the `cgp` repository's `main` branch. Against commit `adc616c`, the
four Hypershell tests, the four cgp-serde tests, and the three cgp-examples tests passed, and every
Hypershell target compiled. Which of their tests reach an error
path is recorded in their own testing documents.

## What nothing tests

- **Without `std`.** Nothing builds the crate for a target without `std`. The workspace never
  enables anyhow's `std` feature, so the tests do run anyhow in its `no_std` mode, but on a host that
  has `std`.
- **With anyhow's `std` feature.** Because the workspace never enables it, backtrace capture and
  anything else that feature changes are unexercised.
- **`{:?}` output.** The tests assert `{}` and `{:#}` but not the multi-line `Debug` form, which is
  anyhow's own.

**Public material derived from this:** None yet.
