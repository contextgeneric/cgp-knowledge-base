# Namespace organization

`MockApp`'s whole wiring is three lines because the crate spreads its wiring across three tables with
different jobs: a tree of paths that describes the application's structure, a namespace that binds
one configuration, and a table of endpoint pipelines. This document records that division and the
one override it leaves room for. The techniques themselves (prefixes, namespaces, `#[default_impl]`,
and the `for` loop) are taught in
[organizing wiring with namespaces and prefixes](../../../../cgp/guides/namespaces-and-prefixes.md).

## The prefix tree

Every component in `interfaces` registers a path into CGP's built-in `DefaultNamespace` with
`#[prefix]`, so the application's structure is written once, on the components themselves. The
resulting tree has six branches under `@app`, plus CGP's own error path:

| Path | Components registered there |
|---|---|
| `@app.auth.types` | `UserIdTypeProviderComponent`, `PasswordTypeProviderComponent`, `HashedPasswordTypeProviderComponent` |
| `@app.finance.types` | `QuantityTypeProviderComponent`, `CurrencyTypeProviderComponent` |
| `@app.auth` | `PasswordCheckerComponent`, `UserHashedPasswordQuerierComponent` |
| `@app.finance` | `UserBalanceQuerierComponent`, `MoneyTransferrerComponent` |
| `@app.error` | `HttpErrorRaiserComponent` |
| `@app.api` | `ApiHandlerComponent` |
| `@cgp.core.error` | `ErrorTypeProviderComponent`, registered by CGP |

The abstract types sit on `types` sub-paths apart from the operations of the same layer. That keeps
the choice of `String` or `u64` separate from the choice of backend, so a second configuration can
bind one without the other. Because the prefixes live in `DefaultNamespace`, not in a namespace the
crate defines, any namespace that inherits `DefaultNamespace` addresses the components by these
paths.

## `MockNamespace` binds one configuration

[`MockNamespace`](../reference/wiring.md#mocknamespace) inherits `DefaultNamespace` and binds a
provider at every path in the tree except two, the transfer and the API handler, from two sides. Its body binds the entries no provider
can register for itself: the concrete error type, the three auth types and two finance types, all
through `UseType`, and the HTTP error provider, which is generic and so cannot use `#[default_impl]`.
The mock backend's three auth and balance implementations register themselves with
`#[default_impl(@app.… in MockNamespace)]` on their own `#[cgp_impl]` blocks, as recorded in
[mock backend](../reference/mock-backend.md).

Keeping the prefixes in `DefaultNamespace` and the bindings in `MockNamespace` is what makes the
bindings a replaceable layer. A second configuration inherits `DefaultNamespace` and binds its own
providers at the same paths. It cannot inherit `MockNamespace` and override one binding: a child
namespace that rebinds a path its parent binds conflicts with the parent's forwarding impl, as
[swapping the backend](../guides/swapping-the-backend.md) shows with the compiler's message. The
consequence for this crate is that the type choices, which a second backend would usually keep, live
in `MockNamespace` alongside the mock providers, so a new configuration repeats them.

## `DefaultApiHandlers` is a table, not a namespace to join

The endpoint pipelines live in a separate table,
[`DefaultApiHandlers`](../reference/wiring.md#defaultapihandlers), keyed by the endpoint marker:
`QueryBalanceApi` and `TransferApi`. It is declared with `cgp_namespace!` but has no parent and is
never joined. `MockApp` reads it with a `for <Key, Value> in DefaultApiHandlers` loop and writes each
entry onto the `ApiHandler` component's dispatch path, `@app.api.ApiHandlerComponent.Key`. Keeping the
API surface out of `MockNamespace` means another configuration can serve the same endpoints without
inheriting the mock backend.

## The one path `MockApp` wires itself

`MockApp` binds exactly one path directly: `@app.finance.MoneyTransferrerComponent`, to
`NoTransferToSelf<UseMockedApp>`. It can do so only because `MockNamespace` leaves that path unbound;
the backend's transfer implementation carries no `#[default_impl]`, and a comment on it in
`providers/mocked.rs` says why. Had the namespace bound the path, the context's entry would overlap
the blanket impl that `namespace MockNamespace;` generates, and the compiler would reject it with
`E0119`, the [namespace override conflict](../../../../cgp/errors/wiring/namespace-override-conflict.md).

A probe confirmed the other half of the rule: a context that joins `MockNamespace` and wires the same
path to the bare `UseMockedApp` compiles and runs. So the choice to guard transfers belongs to the
context and not to the namespace, which is why it can be removed by editing one line. Without it, a
self-transfer succeeds and leaves the balance unchanged, as the
[mock backend](../reference/mock-backend.md#moneytransferrer) records, instead of being rejected with
`400`.

## Source

- [`interfaces/`](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/transfer/src/interfaces)
  — the `#[prefix]` attributes.
- [`namespaces/mock.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/namespaces/mock.rs)
  and [`namespaces/api_handlers.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/namespaces/api_handlers.rs)
  — the two tables.
- [`providers/mocked.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/mocked.rs)
  — the `#[default_impl]` registrations.
- [`contexts/app.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/contexts/app.rs)
  — `MockApp`'s wiring.

## Public material derived from this

Section 7, "Assembling the app with namespaces", of the crate's own README.
