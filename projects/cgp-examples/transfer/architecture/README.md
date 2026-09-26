# `transfer` architecture

`transfer` is built from a handful of decisions that every part of it follows, and this page states
them together so a reader can hold the whole design at once before opening the reference. Each
decision that needs more than a paragraph has its own document below. The CGP patterns behind them
are taught in the [money-transfer API](../../../../examples/money-transfer-api.md) worked example and
the documents it links to, so this page says only what the crate does with them.

## The design on one page

**The handlers name only abstract types.** The user id, the password, the stored password, the
amount, and the currency are five abstract types, each a one-line `#[cgp_type]` component carrying
only the bound the code needs, and the error is CGP's own abstract `HasErrorType`. Every handler,
wrapper, and backend imports them with `#[use_type]` and writes them as bare names, so none of that
code mentions `String`, `u64`, or `DemoCurrency`. `MockApp` fixes all six in its wiring. See
[domain types](../reference/domain-types.md).

**Every endpoint is one component, dispatched on a marker type.** `CanHandleApi<Api>` is the single
async component all endpoints implement, and `Api` is a zero-sized marker, `QueryBalanceApi` or
`TransferApi`, that selects the provider. The component's `Request` and `Response` associated types
let each endpoint fix its own input and output. The `Api` parameter is a selector rather than a
target: the handler's work is on the request, and `Self` is always the application context. See
[components](../reference/components.md).

**Cross-cutting concerns are wrappers, nested per endpoint.** Converting the raw Axum request,
encoding the response as JSON, and authenticating are each a higher-order provider for `ApiHandler`
that takes an inner handler and implements `ApiHandler` itself. An endpoint is a nesting of those
wrappers around a handler that knows only the business logic, and the two endpoints nest them
differently. The business operation `MoneyTransferrer` is wrapped the same way, by `NoTransferToSelf`.
See [the request lifecycle](request-lifecycle.md) and [wrappers](../reference/wrappers.md).

**Errors carry their HTTP status as a type.** A provider raises an error by naming a zero-sized
status marker, such as `ErrNotFound`, together with a detail, through the crate's own
`CanRaiseHttpError<Code, Detail>` component. The mapping from marker to status code, and from detail
to the concrete `AppError`, lives in one provider that the wiring selects by the detail's type. See
[error design](error-design.md).

**One provider struct is the whole backend.** `UseMockedApp` implements the password lookup, the
password check, the balance query, and the transfer, each reading the two in-memory maps off the
context as `#[implicit]` arguments. Replacing the backend means replacing that provider in the wiring
and nothing else. See [mock backend](../reference/mock-backend.md) and
[swapping the backend](../guides/swapping-the-backend.md).

**The wiring is three tables and one override.** Every component registers a path under `@app` in
CGP's `DefaultNamespace` with `#[prefix]`, which fixes the application's structure. `MockNamespace`
inherits it and binds one configuration: the concrete types, the error provider, and the mock
backend. `DefaultApiHandlers` is a separate table of the two endpoint pipelines. `MockApp` joins the
namespace, loops over the handler table, and wires one path itself, wrapping the transfer in
`NoTransferToSelf`. See [namespace organization](namespace-organization.md) and
[wiring](../reference/wiring.md).

**HTTP lives outside the components.** The routing layer is ordinary Rust traits over Axum's
`Router`, and it reaches the components through `CanHandleApiSend`, a plain trait that restates the
handler with a `Send` future. The crate implements that trait once per endpoint on the concrete
`MockApp`, because only there can the compiler prove the future is `Send`. See the
[HTTP layer](../reference/http-layer.md).

**The modules follow the same split.** Interfaces, providers, concrete types, namespaces, and the
context each have their own module, and the dependencies point from the context inward to the
interfaces. See [module layout](module-layout.md).

## The documents

Each document below carries the mechanism and the code for one of the decisions above.

- [module-layout.md](module-layout.md) — the five modules, which kind of item each holds, and the
  one dependency that points backward.
- [error-design.md](error-design.md) — the status-code markers, `AppError`, the per-detail
  dispatch, and the provider that is defined but never wired.
- [namespace-organization.md](namespace-organization.md) — the prefix tree, how `MockNamespace` and
  `DefaultApiHandlers` divide the wiring, and why `MockApp` can override only the transfer path.
- [request-lifecycle.md](request-lifecycle.md) — a balance query and a transfer traced from the
  socket to the backend and back, with every recorded response.

## Public material derived from this

The crate's own README, whose walkthrough follows the same decisions in the same order.
