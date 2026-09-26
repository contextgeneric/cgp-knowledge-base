# Debugging backend wiring

Most mistakes with a backend are a source or detail type routed to a provider whose bounds it does
not meet, and a `check_components!` block that lists the types the context must accept turns each
into a compile error at the wiring site. Check the context first, then read the error with
[`cargo cgp check`](../../../cgp/reference/cargo-cgp.md), which leads with the unmet bound. Each
section below shows a small program that triggers one mistake, what `cargo cgp check` reports, the
root cause, and the fix. The outputs were produced by the local cargo-cgp build against the `cgp`
source on `main`; the anyhow crate stands in for all three, since the providers share their bounds.

## A message routed to the raise provider

The raise provider accepts only standard errors, so a `String` or any other plain message cannot go
through it. This context sends every source type to `RaiseAnyhowError` and then checks `String`:

```rust
delegate_components! {
    App {
        ErrorTypeProviderComponent: UseAnyhowError,
        ErrorRaiserComponent: RaiseAnyhowError,
    }
}

check_components! {
    App {
        ErrorRaiserComponent: String,
    }
}
```

`cargo cgp check` reports `E0277`, "the trait bound `String: Error` is not satisfied", on the check
entry, with the chain running from `CanRaiseError<String>` for `App` through
`ErrorRaiser<String>` for `RaiseAnyhowError`. The root cause is the provider's
`E: StdError + Send + Sync + 'static` bound, which `String` does not meet. Route `String` to the
formatting provider instead, with `open ErrorRaiserComponent;` and
`@ErrorRaiserComponent.String: DisplayAnyhowError`.

## A raiser without its error type

A raiser or wrapper works only on a context whose error is the crate's type, so wiring one without
the type provider leaves nothing to pin. This context wires `RaiseAnyhowError` and no
`ErrorTypeProviderComponent`:

```rust
delegate_components! {
    App {
        ErrorRaiserComponent: RaiseAnyhowError,
    }
}

check_components! {
    App {
        ErrorRaiserComponent: io::Error,
    }
}
```

`cargo cgp check` reports `[CGP-E001]`, that `CanRaiseError<Error>` is not implemented for `App`,
with the root cause `[CGP-E107]`: `App` contains no delegate entry for `ErrorTypeProviderComponent`.
The tree shows the missing `HasErrorType` twice, once as the consumer trait's supertrait and once as
the provider's pin. Add `ErrorTypeProviderComponent: UseAnyhowError`.

## Two backends on one context

The providers of different backends cannot be mixed, because each pins the context's error to its
own type. This context sets a boxed standard error and raises with anyhow's provider:

```rust
delegate_components! {
    App {
        ErrorTypeProviderComponent: UseBoxedStdError,
        ErrorRaiserComponent: RaiseAnyhowError,
    }
}

check_components! {
    App {
        ErrorRaiserComponent: io::Error,
    }
}
```

`cargo cgp check` reports `E0271` tagged `[CGP-E017]`: the abstract type `Error` of `HasErrorType` on
`App` was expected to be `Error` but is `Box<dyn Error + Send + Sync>`. The first `Error` is
`anyhow::Error` with its path stripped by the tool's resugaring, which makes the message read
oddly; its help line suggests wiring `UseType<Error>` for the same reason. The root cause is the
`#[use_type(HasErrorType.{Error = anyhow::Error})]` pin on `RaiseAnyhowError`. Use the raiser from the
same crate as the type provider, here `RaiseBoxedStdError`.

## A `String` routed back to itself

The generic `DebugError` and `DisplayError` from `cgp-error-extra` format a value and raise the
resulting `String` through the context again, so they cannot be the provider for `String` itself.
This context formats `ParseIntError` with `DebugError` and also routes `String` to `DebugError`:

```rust
delegate_components! {
    App {
        open ErrorRaiserComponent;

        ErrorTypeProviderComponent: UseAnyhowError,
        @ErrorRaiserComponent.ParseIntError: DebugError,
        @ErrorRaiserComponent.String: DebugError,
    }
}

check_components! {
    App {
        ErrorRaiserComponent: ParseIntError,
    }
}
```

`cargo cgp check` reports `E0275` tagged `[CGP-E010]`: the wiring for `CanRaiseError<ParseIntError>`
never resolves, because the lookup recurses. `DebugError` for `String` needs `CanRaiseError<String>`,
which is `DebugError` for `String` again. The tool's help text names the most common cause of a
recursing lookup, a component delegated back to the context, which is the same shape here in a less
obvious place. Route `String` to a provider that builds the error itself:
`@ErrorRaiserComponent.String: DisplayAnyhowError`. The generic `DebugError` for `ParseIntError`
then works, or the backend's `DebugAnyhowError` can replace it and skip the round trip.

## A borrowed detail

The anyhow and eyre wrappers in the raise role store the detail inside the error, so they need it to
be `'static`. This provider wraps each error with the path it was given, a borrowed `&str`, and the
context wires `RaiseAnyhowError` as its wrapper:

```rust
#[cgp_impl(new LoadFile)]
#[uses(CanRaiseError<io::Error>, for<'a> CanWrapError<&'a str>)]
#[use_type(HasErrorType.Error)]
impl Loader {
    fn load(&self, path: &str) -> Result<String, Error> {
        std::fs::read_to_string(path)
            .map_err(Self::raise_error)
            .map_err(|e| Self::wrap_error(e, path))
    }
}

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseAnyhowError,
        [ErrorRaiserComponent, ErrorWrapperComponent]: RaiseAnyhowError,
        LoaderComponent: LoadFile,
    }
}

check_components! {
    App {
        LoaderComponent,
    }
}
```

`cargo cgp check` passes this through as a plain `E0477`, "the type `&'a str` does not fulfill the
required lifetime", noting that the type must satisfy the static lifetime, on the `LoaderComponent`
check entry. It carries no dependency chain, so the link to the wrapper has to be inferred: the only
`'static` bound in reach is `RaiseAnyhowError`'s `Detail: Display + Send + Sync + 'static`. Wire the
wrapper to `DisplayAnyhowError` or `DebugAnyhowError`, which copy the detail into a string and
accept a borrow; with `ErrorWrapperComponent: DisplayAnyhowError` the program compiles. The std
backend has no such bound, since `RaiseBoxedStdError` converts the detail to a string too.

## A custom eyre handler installed too late

`cgp-error-eyre` installs eyre's default report handler the first time a report is built, so a
custom handler must be installed before any error is raised. `eyre::set_hook` returns
`Err(InstallError)` once a handler exists, and a probe that raised one report and then called
`set_hook` got that error. Install `color-eyre` or another handler at the start of `main`, and check
the result of `set_hook` rather than discarding it, since a discarded error leaves the default
handler in place without any sign.

**Public material derived from this:**
the `/cgp` skill's [error backends](https://github.com/contextgeneric/cgp-skills/blob/main/cgp/references/error-backends.md) reference.
