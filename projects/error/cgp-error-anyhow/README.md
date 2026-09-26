# cgp-error-anyhow

`cgp-error-anyhow` makes `anyhow::Error` a CGP context's abstract error type, and supplies the
providers that raise errors into it and add context to it. It is the backend the ecosystem's projects
wire, and the one to reach for first.

- **Source** — [`crates/standalone/error/cgp-error-anyhow/`](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error/cgp-error-anyhow)
  in the `cgp` repository, on `main`; see [which revision](../README.md#which-revision-these-documents-describe)
- **Crate** — `cgp-error-anyhow` 0.8.0-alpha, depending on `cgp-core` and `anyhow` 1.0.104 without
  default features
- **`no_std`** — yes, using anyhow's `no_std` mode
- **Tests** — the `anyhow_*` files, `readme_anyhow.rs`, and three shared files of the `error_backends`
  target; see [testing.md](testing.md)

## What it provides

The crate exports one provider per role of the [shared design](../architecture.md#the-four-roles)
and re-exports `anyhow::Error` as `cgp_error_anyhow::Error`:

| Provider | Implements | Accepts | Produces |
|---|---|---|---|
| `UseAnyhowError` | `ErrorTypeProvider` | — | `Error = anyhow::Error` |
| `RaiseAnyhowError` | `ErrorRaiser<E>`, `ErrorWrapper<Detail>` | `E: StdError + Send + Sync + 'static`; `Detail: Display + Send + Sync + 'static` | the source converted with `From`; the detail added with `context` |
| `DebugAnyhowError` | `ErrorRaiser<E>`, `ErrorWrapper<Detail>` | `E: Debug`; `Detail: Debug` | a new message formatted with `{:?}`; the formatted detail added with `context` |
| `DisplayAnyhowError` | `ErrorRaiser<E>`, `ErrorWrapper<Detail>` | `E: Display`; `Detail: Display` | a new message formatted with `{}`; the formatted detail added with `context` |

Each entry is documented in [reference.md](reference.md). A context wires `UseAnyhowError` and then
routes each source type to one of the others, per
[choosing-a-backend.md](../guides/choosing-a-backend.md#routing-each-source-type):

```rust
use cgp::core::error::{ErrorRaiserComponent, ErrorTypeProviderComponent, ErrorWrapperComponent};
use cgp::prelude::*;
use cgp_error_anyhow::{DisplayAnyhowError, RaiseAnyhowError, UseAnyhowError};

pub struct App;

delegate_components! {
    App {
        open ErrorRaiserComponent;

        ErrorTypeProviderComponent: UseAnyhowError,
        @ErrorRaiserComponent.std::io::Error: RaiseAnyhowError,
        @ErrorRaiserComponent.String: DisplayAnyhowError,
        ErrorWrapperComponent: RaiseAnyhowError,
    }
}
```

With that wiring, raising `std::io::Error::other("disk full")` and wrapping it with
`"while saving"` gives an error whose `{}` is `while saving` and whose `{:#}` is
`while saving: disk full`, and `downcast_ref::<std::io::Error>()` still finds the original. This is
the example in the crate's own README, which `readme_anyhow.rs` compiles and runs.

## Who uses it

Three projects wire it, each documented in its own section:

- **hypershell** — its namespace sets `UseAnyhowError`, raises standard errors with
  `RaiseAnyhowError` and two non-standard ones with `DebugAnyhowError`, and wraps every detail with
  `DebugAnyhowError`; see [error handling](../../hypershell/architecture/error-handling.md). Its
  prelude re-exports `cgp_error_anyhow::Error`.
- **cgp-serde** — three of its tests wire `UseAnyhowError` and `RaiseAnyhowError`; see
  [wiring a context](../../cgp-serde/guides/wiring-a-context.md).
- **cgp-examples** — every `builder` context wires the same two; see
  [builder contexts](../../cgp-examples/builder/reference/builder-contexts.md).

The worked examples [modular serialization](../../../examples/modular-serialization.md),
[application builder](../../../examples/application-builder.md), and
[shell-scripting DSL](../../../examples/shell-scripting-dsl.md) wire it too.

## The catalog

- [reference.md](reference.md) — the four providers and the `Error` re-export.
- [testing.md](testing.md) — what the tests pin and what nothing tests.
- [issues.md](issues.md) — open items.

**Public material derived from this:** the crate's README, which is its docs.rs front page.
