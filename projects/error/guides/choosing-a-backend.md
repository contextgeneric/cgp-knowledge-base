# Choosing a backend and routing errors

Pick the backend whose error type the application already uses, and route each source type to the
raise provider when it is a standard error and to a formatting provider when it is not. This guide
covers that choice, the per-type routing, the wiring forms, and how to check a downstream project
against a local change to the crates. The design behind it is in
[../architecture.md](../architecture.md).

## Which backend

The three crates offer the same roles and differ in the error type, and the error type is the
decision that matters, because every fallible operation on the context returns it.

- **`cgp-error-anyhow`** suits an application that already reports errors with anyhow or wants
  context chaining with no setup. It is `no_std`, and it is what the ecosystem's projects use.
- **`cgp-error-eyre`** suits an application that wants eyre's customizable reports, such as
  `color-eyre`. It needs `std`, and a custom handler must be installed with `eyre::set_hook` before
  the first error is raised.
- **`cgp-error-std`** suits a library or a `no_std` context that wants an open-ended error type
  without an extra dependency. Its errors are plain `Box<dyn core::error::Error + Send + Sync>`
  values that any caller can inspect with `source()` and `downcast_ref`.

A backend is not always needed. A context that only raises standard errors and never wraps them gets
the same result from the generic `UseType<anyhow::Error>` and `RaiseFrom`, as
[../architecture.md](../architecture.md#what-a-backend-adds-over-the-generic-providers) explains. A
context whose errors form a closed set is often better served by its own error enum with
`UseType<AppError>` and `RaiseFrom`, which keeps every variant matchable; the backends trade that
for accepting any error at all.

## Routing each source type

A context usually raises several unrelated source types, and each belongs with the provider that
keeps the most information about it. The table applies to every backend, with the crate's own
provider names:

| Source or detail | Raise with | Wrap with | Why |
|---|---|---|---|
| A standard error: `std::io::Error`, `ParseIntError`, `serde_json::Error` | `Raise…` | — | kept intact, so `downcast_ref` and the chain still reach it |
| `String`, `&'static str`, or another message | `Display…` | `Display…` or `Raise…` | not a standard error; `{}` prints it without quotes |
| A type with only `Debug`, such as a `#[derive(Debug)]` struct | `Debug…` | `Debug…` | the only trait it has |
| A borrowed detail such as a `&'a str` | — | `Display…` or `Debug…` | the `Raise…` wrapper needs `'static` in anyhow and eyre |
| The context's own error, raised again | the generic `RaiseFrom` or `ReturnError` | — | the backend's own type is not a standard error, so `Raise…` rejects it |

`Debug…` applied to a string quotes it: raising `"bad input"` produces the message `"bad input"`,
quotation marks included. Prefer `Display…` for anything that is already a message.

## The wiring forms

A context can wire a backend in any of the forms `delegate_components!` accepts, and the providers
are the same structs in each. The simplest form wires one provider for every source type, which works
when every source is a standard error:

```rust
delegate_components! {
    App {
        ErrorTypeProviderComponent: UseAnyhowError,
        [ErrorRaiserComponent, ErrorWrapperComponent]: RaiseAnyhowError,
    }
}
```

The `open` statement dispatches per source or detail type, which is the usual form once a context
raises both standard errors and messages:

```rust
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

A context that joins `DefaultNamespace` wires the same entries by the path the error components
register under:

```rust
delegate_components! {
    App {
        namespace DefaultNamespace;

        @cgp.core.error.ErrorTypeProviderComponent: UseAnyhowError,
        @cgp.core.error.ErrorRaiserComponent.std::io::Error: RaiseAnyhowError,
        @cgp.core.error.ErrorRaiserComponent.String: DisplayAnyhowError,
    }
}
```

Hypershell's namespace uses this form, adding a whole list of source types to one path with a
bracket group. Older code builds a `UseDelegate` table under `ErrorRaiserComponent` instead; it
still works, and [dispatching per type](../../../cgp/guides/dispatching-per-type.md) explains why
`open` replaces it.

The wiring keys come from `cgp::core::error` and the providers from the backend crate. A check block
lists the source types the context must accept, which catches a type routed to the wrong provider at
the wiring site:

```rust
check_components! {
    App {
        ErrorRaiserComponent: [std::io::Error, String],
        ErrorWrapperComponent: &'static str,
    }
}
```

## Testing a downstream project against a local change

A project that uses a backend from crates.io is tested against a local change to the crates through
its workspace's `[patch.crates-io]` section, never by rewriting its dependency lines. Override `cgp`
together with the backend, because the backend's `cgp-core` must be the same copy the project's
`cgp` uses. Patching the backend alone leaves two copies of the CGP crates in the graph, and a probe
that did so failed with `E0599` on `raise_error`, with rustc noting "there are multiple different
versions of crate `cgp_error` in the dependency graph":

```toml
[patch.crates-io]
cgp              = { path = "../cgp/crates/main/cgp" }
cgp-error-anyhow = { path = "../cgp/crates/standalone/error/cgp-error-anyhow" }
```

Use local paths while the change is being tested and switch the same entries to the `cgp` git
repository when the change is committed. When the change raises a minimum dependency version, the
project's lockfile may pin an older one and fail to resolve until `cargo update -p <crate>` moves it.

**Public material derived from this:**
the `/cgp` skill's [error backends](https://github.com/contextgeneric/cgp-skills/blob/main/cgp/references/error-backends.md) reference.
