# Architecture of the error backends

Each backend fixes a context's abstract error to one concrete type through four providers that play
the same four roles in every crate. This document states that shared design once, so the per-crate
references only record what differs. The error components themselves, `HasErrorType`,
`CanRaiseError`, and `CanWrapError`, are documented in [cgp/](../../cgp/README.md): see
[`HasErrorType`](../../cgp/reference/components/has_error_type.md),
[`CanRaiseError` and `CanWrapError`](../../cgp/reference/components/can_raise_error.md), and the
[modular error handling](../../cgp/concepts/modular-error-handling.md) concept.

## The four roles

Every crate exports one provider per role, and a context wires each role to the component it
implements. The roles are the same across the crates; only the concrete type and the method that
builds or extends it change.

| Role | Implements | anyhow | eyre | std |
|---|---|---|---|---|
| Set the error type | `ErrorTypeProvider` | `UseAnyhowError` | `UseEyreError` | `UseBoxedStdError` |
| Raise a standard error intact, wrap a detail as context | `ErrorRaiser`, `ErrorWrapper` | `RaiseAnyhowError` | `RaiseEyreError` | `RaiseBoxedStdError` |
| Format with `{:?}` | `ErrorRaiser`, `ErrorWrapper` | `DebugAnyhowError` | `DebugEyreError` | `DebugBoxedStdError` |
| Format with `{}` | `ErrorRaiser`, `ErrorWrapper` | `DisplayAnyhowError` | `DisplayEyreError` | `DisplayBoxedStdError` |

The type provider decides the context's `Error`. The other three work only on a context whose `Error`
is already the crate's type, so a context wires the type provider alongside whichever raisers and
wrappers it uses; wiring a raiser without it fails, as
[the debugging guide](guides/debugging.md#a-raiser-without-its-error-type) shows.

The raise role keeps the source error. `RaiseAnyhowError` converts through `From`, `RaiseEyreError`
the same, and `RaiseBoxedStdError` boxes the value, so in all three the original error stays
reachable with `downcast_ref` and as the first link of the error chain. The two formatting roles
throw the value away: they render it into a string and build a fresh error from the string, which
is how they accept values that are not standard errors at all, such as `String` or a plain
`#[derive(Debug)]` struct. A context therefore routes each source type by what that type is, and
[choosing-a-backend.md](guides/choosing-a-backend.md#routing-each-source-type) gives the table.

## How the providers are written

Every provider is a unit struct declared on its own with a `///` comment, followed by one
`#[cgp_impl]` block per component it implements. The error type is imported with the equality form
of `#[use_type]`, which both pins the context's error to the crate's type and lets the signature name
it as the bare `Error`:

```rust
pub struct RaiseAnyhowError;

#[cgp_impl(RaiseAnyhowError)]
#[use_type(HasErrorType.{Error = anyhow::Error})]
impl<E> ErrorRaiser<E>
where
    E: StdError + Send + Sync + 'static,
{
    fn raise_error(e: E) -> Error {
        e.into()
    }
}
```

The `#[use_type]` pin becomes the impl-side dependency `Self: HasErrorType<Error = anyhow::Error>`,
which is why a context must set its error type to the crate's own. The bounds on `E` and `Detail` stay
in ordinary `where` clauses, since they constrain the source or detail type rather than the context.
The type providers need no pin and write `type Error = anyhow::Error;` directly. The attribute
forms are documented in [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) and
[`#[use_type]`](../../cgp/reference/attributes/use_type.md).

## What a backend adds over the generic providers

The generic providers in `cgp-error-extra` already cover two of the four roles.
`UseType<anyhow::Error>` sets the error type exactly as `UseAnyhowError` does, since
[`HasErrorType`](../../cgp/reference/components/has_error_type.md) is a `#[cgp_type]` component, and
`RaiseFrom` raises a standard error exactly as `RaiseAnyhowError`'s raiser does, since both convert
through `From`. `RaiseFrom` goes one step further: through the reflexive `From<T> for T` it also
re-raises a value that is already the context's error, which the backend raisers cannot, because
neither `anyhow::Error`, `eyre::Report`, nor a boxed `dyn Error` is itself a standard error. The
`error_backends` tests pin both facts. What a backend adds is the rest:

- **Attaching a detail.** No generic provider stores a detail in the error by itself: `DiscardDetail`
  drops it, and the generic `DebugError` and `DisplayError` format it and forward the `String` to the
  context's own `CanWrapError<String>`, which still needs a provider. Each backend's wrappers attach
  it with the library's own mechanism (`anyhow::Error::context`, `eyre::Report::wrap_err`, or a
  `WrapError`), so they can be that provider.
- **Formatting straight into the concrete type.** The generic
  [`DebugError` and `DisplayError`](../../cgp/reference/providers/error_providers.md) format a value
  and hand the string back to the context's own `CanRaiseError<String>`, so they still need some
  other provider for `String`. A backend's `Debug…`/`Display…` providers build the concrete error
  from the string themselves, so they can be that provider. Wiring the generic `DebugError` for
  `String` instead makes the lookup recurse, as
  [the debugging guide](guides/debugging.md#a-string-routed-back-to-itself) shows.
- **A named type to import.** Each crate re-exports its error type as `Error`, which is what
  hypershell's prelude re-exports to its users.

## The `Send + Sync + 'static` bounds

The raise role requires `E: StdError + Send + Sync + 'static`, and the anyhow and eyre wrappers
require `Detail: Display + Send + Sync + 'static`. The bounds come from the libraries, not from CGP:
`anyhow::Error` and `eyre::Report` are thread-safe, type-erased boxes that can be downcast, so
anything stored inside them must be sendable, shareable, and free of borrows.
`Box<dyn Error + Send + Sync>` imposes the same on what `RaiseBoxedStdError` boxes. The std wrapper
is the exception, since it converts the detail to a `String` before storing it and therefore needs
only `Detail: Display`.

The practical consequence is that a borrowed detail such as a `&'a str` taken from a function
argument cannot go through `RaiseAnyhowError` or `RaiseEyreError` as a wrapper, while a
`&'static str` literal can. The formatting wrappers copy the detail into a string first and accept a
borrowed detail, which is why hypershell wraps every detail with `DebugAnyhowError`; see
[the debugging guide](guides/debugging.md#a-borrowed-detail).

## The namespace paths

`HasErrorType`, `CanRaiseError`, and `CanWrapError` register in `DefaultNamespace` under the prefix
`@cgp.core.error`, so a context that joins `DefaultNamespace` wires a backend by path rather than by
component name, for instance
`@cgp.core.error.ErrorRaiserComponent.std::io::Error: RaiseAnyhowError`. Nothing about the backends
changes under a namespace; the providers are the same structs, reached by a different key.
[choosing-a-backend.md](guides/choosing-a-backend.md#the-wiring-forms) shows each wiring form, and
the mechanism is in [namespaces](../../cgp/concepts/namespaces.md).

## Features, `no_std`, and dependencies

The crates differ in what they need from the platform, and the difference follows the library each
wraps. `cgp-error-anyhow` is `#![no_std]` and builds anyhow with `default-features = false`, which
anyhow supports as its `no_std` mode; if another crate in the graph enables anyhow's `std` feature,
feature unification turns it on here too and adds what anyhow's `std` mode brings, such as backtrace
capture. `cgp-error-std` is `#![no_std]` and needs only `alloc`. `cgp-error-eyre` is not `no_std`,
because eyre itself requires `std`.

`cgp-error-eyre` enables eyre's `auto-install` feature and leaves `track-caller` off. Without
`auto-install`, eyre has no report handler until the application calls `eyre::set_hook`, and every
report the crate builds panics. With it, eyre installs its default handler the first time a report
is built, after which `set_hook` returns an error, so an application that wants `color-eyre` or
another handler installs it before raising anything. `track-caller` stays off because it would
record a location inside the backend; see [cgp-error-eyre/issues.md](cgp-error-eyre/issues.md).

Each crate depends on `cgp-core` under the name `cgp` rather than on the `cgp` facade, which keeps
`cgp-extra` out of its build. The name matters because CGP's macros emit paths through `::cgp`.

## Source

- [`crates/standalone/error/cgp-error-anyhow/`](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error/cgp-error-anyhow)
- [`crates/standalone/error/cgp-error-eyre/`](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error/cgp-error-eyre)
- [`crates/standalone/error/cgp-error-std/`](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error/cgp-error-std)
- [`crates/core/cgp-error/src/traits/`](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-error/src/traits)
  — the components the providers implement

**Public material derived from this:** the crates' READMEs, and
the `/cgp` skill's [error backends](https://github.com/contextgeneric/cgp-skills/blob/main/cgp/references/error-backends.md) reference.
