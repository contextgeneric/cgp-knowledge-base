# cgp-error-std

`cgp-error-std` makes a boxed standard error, `Box<dyn core::error::Error + Send + Sync>`, a CGP
context's abstract error type, and supplies the providers that raise errors into it and add context
to it, together with the two error types those providers build. It needs nothing beyond `alloc`, so
it suits a library or a `no_std` context that wants an open-ended error type.

- **Source** — [`crates/standalone/error/cgp-error-std/`](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error/cgp-error-std)
  in the `cgp` repository, on `main`; see [which revision](../README.md#which-revision-these-documents-describe)
- **Crate** — `cgp-error-std` 0.8.0-alpha, depending only on `cgp-core`
- **`no_std`** — yes, with `alloc`
- **Tests** — the `std_*` files, `readme_std.rs`, and the shared `swapping_backends.rs` of the
  `error_backends` target; see [testing.md](testing.md)

## What it provides

The crate exports one provider per role of the [shared design](../architecture.md#the-four-roles),
plus three types:

| Item | Implements | Accepts | Produces |
|---|---|---|---|
| `UseBoxedStdError` | `ErrorTypeProvider` | — | `Error = cgp_error_std::Error` |
| `RaiseBoxedStdError` | `ErrorRaiser<E>`, `ErrorWrapper<Detail>` | `E: StdError + Send + Sync + 'static`; `Detail: Display` | the source boxed; a `WrapError` around the error |
| `DebugBoxedStdError` | `ErrorRaiser<E>`, `ErrorWrapper<Detail>` | `E: Debug`; `Detail: Debug` | a boxed `StringError` formatted with `{:?}`; a `WrapError` with the detail formatted the same way |
| `DisplayBoxedStdError` | `ErrorRaiser<E>`, `ErrorWrapper<Detail>` | `E: Display`; `Detail: Display` | a boxed `StringError` formatted with `{}`; a `WrapError` with the detail formatted the same way |
| `Error` | — | — | the alias `Box<dyn StdError + Send + Sync + 'static>` |
| `StringError` | `core::error::Error` | — | an error holding only a message |
| `WrapError` | `core::error::Error` | — | an error holding a detail and the error it wraps, returned as its `source` |

Each entry is documented in [reference.md](reference.md). The wiring is the same as for
[cgp-error-anyhow](../cgp-error-anyhow/README.md#what-it-provides) with these names, and the routing
rules are in [choosing-a-backend.md](../guides/choosing-a-backend.md#routing-each-source-type).

The std wrapper differs from the other two backends in one bound: `RaiseBoxedStdError` converts the
detail to a `String` before storing it, so it needs only `Detail: Display` and accepts a borrowed
detail that anyhow's and eyre's raise-role wrappers reject.

## Printing a chain

The errors this crate builds follow the standard convention for error chains: an error's `Display`
prints its own message, and the error it wraps is reachable only through `source()`. So a
`WrapError` prints its detail alone with `{}`, and a reporter that walks `source()`, such as anyhow's
or eyre's when a boxed error is later converted into one of theirs, prints every message exactly once.
To print the whole chain from the error itself, use `{:#}` or `{:?}` on a `WrapError`, which join the
messages with `": "`. The published 0.8.0-alpha printed the source inside `Display` as well, so a
chain walk repeated it; see [which revision](../README.md#which-revision-these-documents-describe).

One consequence is worth knowing when printing the boxed `Error` directly: `{:#}` reaches
`WrapError`'s chain form only when the outermost error is a `WrapError`. A raised error that was never
wrapped prints as its own type prints.

## Who uses it

No project in the ecosystem, and none of the worked examples, wires `cgp-error-std`. Its only users
are the tests.

## The catalog

- [reference.md](reference.md) — the four providers and the three types.
- [testing.md](testing.md) — what the tests pin and what nothing tests.
- [issues.md](issues.md) — open items.

**Public material derived from this:** the crate's README, which is its docs.rs front page.
