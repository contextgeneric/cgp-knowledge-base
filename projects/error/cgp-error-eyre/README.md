# cgp-error-eyre

`cgp-error-eyre` makes `eyre::Report` a CGP context's abstract error type, and supplies the providers
that raise errors into it and add context to it. It suits an application that wants eyre's
customizable reports; no project in the ecosystem wires it yet.

- **Source** — [`crates/standalone/error/cgp-error-eyre/`](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error/cgp-error-eyre)
  in the `cgp` repository, on `main`; see [which revision](../README.md#which-revision-these-documents-describe)
- **Crate** — `cgp-error-eyre` 0.8.0-alpha, depending on `cgp-core` and `eyre` 0.6.14 with the
  `auto-install` and `track-caller` features
- **`no_std`** — no, because eyre requires `std`
- **Tests** — the `eyre_*` files, `readme_eyre.rs`, and the shared `swapping_backends.rs` of the
  `error_backends` target; see [testing.md](testing.md)

## What it provides

The crate exports one provider per role of the [shared design](../architecture.md#the-four-roles)
and re-exports `eyre::Error`, eyre's own alias for `Report`, as `cgp_error_eyre::Error`:

| Provider | Implements | Accepts | Produces |
|---|---|---|---|
| `UseEyreError` | `ErrorTypeProvider` | — | `Error = eyre::Report` |
| `RaiseEyreError` | `ErrorRaiser<E>`, `ErrorWrapper<Detail>` | `E: StdError + Send + Sync + 'static`; `Detail: Display + Send + Sync + 'static` | the source converted with `From`; the detail added with `wrap_err` |
| `DebugEyreError` | `ErrorRaiser<E>`, `ErrorWrapper<Detail>` | `E: Debug`; `Detail: Debug` | a new report formatted with `{:?}`; the formatted detail added with `wrap_err` |
| `DisplayEyreError` | `ErrorRaiser<E>`, `ErrorWrapper<Detail>` | `E: Display`; `Detail: Display` | a new report formatted with `{}`; the formatted detail added with `wrap_err` |

Each entry is documented in [reference.md](reference.md). The wiring is the same as for
[cgp-error-anyhow](../cgp-error-anyhow/README.md#what-it-provides) with the eyre names, and the
routing rules are in [choosing-a-backend.md](../guides/choosing-a-backend.md#routing-each-source-type).

## The report handler

Every eyre report is built by a handler, and the crate relies on eyre's `auto-install` feature to have
one. The first report the crate builds installs eyre's default handler, so the providers work with no
setup. An application that wants a different handler, such as `color-eyre`, installs it with
`eyre::set_hook` at the start of `main`: once any report exists, `set_hook` returns an error and the
default handler stays. Without `auto-install`, building a report with no hook installed panics with
"a handler must always be installed if the `auto-install` feature is disabled", which is how the
published 0.8.0-alpha behaves; see [which revision](../README.md#which-revision-these-documents-describe).

The crate also enables eyre's `track-caller` feature, so the default handler prints a `Location:`
section naming where the report was built. That is the line that called `raise_error`, because
`raise_error` is `#[track_caller]` through every impl CGP generates; see
[architecture](../architecture.md#features-no_std-and-dependencies).

## Who uses it

No project in the ecosystem, and none of the worked examples, wires `cgp-error-eyre`. Its only users
are the tests.

## The catalog

- [reference.md](reference.md) — the four providers and the `Error` re-export.
- [testing.md](testing.md) — what the tests pin, including the handler, and what nothing tests.
- [issues.md](issues.md) — open items.

**Public material derived from this:** the crate's README, which is its docs.rs front page.
