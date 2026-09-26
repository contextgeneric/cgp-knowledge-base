# The request lifecycle

This document traces one balance query and one transfer from the socket to the in-memory store and
back, naming the item that handles each step, and records what the running server returned for each
path. It ties together the reference entries, which describe each item on its own.

## A balance query, step by step

A request to `GET /balance?currency=EUR` with Alice's Basic-auth header passes through nine steps,
each handled by one item or, at step 3, by the wiring. The pipeline in the middle is the `QueryBalanceApi` entry of
[`DefaultApiHandlers`](../reference/wiring.md#defaultapihandlers):

```rust
HandleFromRequest<
    AxumQueryBalanceRequest,
    ResponseToJson<UseBasicAuth<HandleQueryBalance<QueryBalanceRequest>>>,
>
```

1. **Routing.** The `GetMethod` impl of [`CanAddRoute`](../reference/http-layer.md#canaddroute)
   mounted a closure on `/balance`. Axum runs its extractors, `State<Arc<MockApp>>` and the context's
   `Request` type, which for this endpoint is the tuple
   [`AxumQueryBalanceRequest`](../reference/http-layer.md#the-request-types): a `Query<QueryBalanceQuery>`
   and an optional `TypedHeader<Authorization<Basic>>`. A query string that does not deserialize is
   rejected here, before any handler runs.
2. **The `Send` boundary.** The closure calls `handle_api_send`, which the
   [`CanHandleApiSend`](../reference/http-layer.md#canhandleapisend) impl for `QueryBalanceApi`
   forwards to `handle_api`.
3. **Dispatch.** `MockApp` resolves `ApiHandler` for `QueryBalanceApi` through the path
   `@app.api.ApiHandlerComponent.QueryBalanceApi`, which the `for` loop in its wiring filled from
   `DefaultApiHandlers`.
4. **Decoding.** [`HandleFromRequest`](../reference/wrappers.md#handlefromrequest) converts the Axum
   tuple into a [`QueryBalanceRequest`](../reference/http-layer.md#the-request-types) with `Into`: the
   currency, the header as a `(user, password)` pair, and `logged_in_user` set to `None`.
5. **Encoding, on the way out.** [`ResponseToJson`](../reference/wrappers.md#responsetojson) calls its
   inner handler and wraps whatever it returns in `axum::Json`.
6. **Authentication.** [`UseBasicAuth`](../reference/wrappers.md#usebasicauth) sees no logged-in user
   and a header, asks the context for the stored password with `query_user_hashed_password`, compares
   it with `check_password`, and on a match writes the user into the request's `logged_in_user`. On any
   failure it leaves the field `None` and continues.
7. **The endpoint.** [`HandleQueryBalance`](../reference/api-handlers.md#handlequerybalance) raises
   `401` if no user is logged in, and otherwise calls `query_user_balance`.
8. **The backend.** [`UseMockedApp`](../reference/mock-backend.md#userbalancequerier) locks the
   `user_balances` map on the context, looks up `(user, currency)`, and raises `404` if it is absent.
9. **The response.** The `QueryBalanceResponse` travels back out, `ResponseToJson` wraps it, and Axum
   serializes it as `{"balance":100}` with status `200`. An error instead travels out as an `AppError`,
   and the route turns it into its status and message.

Authentication failures surface at step 7, not step 6. `UseBasicAuth` never raises an error of its
own, so a wrong password, an unknown user, and a missing header all reach the endpoint as "not logged
in" and produce the same `401`.

## A transfer

`POST /transfer?currency=EUR&recipient=bob&quantity=10` follows the same steps with two differences.
Its pipeline has no `ResponseToJson`, because the endpoint returns `()`, which Axum answers with an
empty `200`:

```rust
HandleFromRequest<
    AxumTransferRequest,
    UseBasicAuth<HandleTransfer<TransferRequest>>,
>
```

And the business operation it calls is itself wrapped. [`HandleTransfer`](../reference/api-handlers.md#handletransfer)
calls `transfer_money`, which `MockApp` resolves to
[`NoTransferToSelf<UseMockedApp>`](../reference/wrappers.md#notransfertoself). The guard raises `400`
when sender and recipient are the same user, and otherwise delegates to the backend, which checks that
both accounts exist and that the sender can afford the amount before updating both balances.

## What the server returned

The responses below were recorded against the running server on the `v0.8.0` branch, starting from
the seeded data and running `example.sh` first. The balances in the first rows reflect that
script's transfer of 10 EUR from Alice to Bob:

| Request | Status | Body |
|---|---|---|
| Alice, `GET /balance?currency=EUR`, before the script's transfer | 200 | `{"balance":100}` |
| Alice, `GET /balance?currency=EUR`, after it | 200 | `{"balance":90}` |
| Bob, `GET /balance?currency=EUR`, after it | 200 | `{"balance":210}` |
| No auth header | 401 | `you must first login` |
| Alice with a wrong password | 401 | `you must first login` |
| An unknown user | 401 | `you must first login` |
| `currency=GBP` | 400 | ``Failed to deserialize query string: currency: unknown variant `GBP`, expected `EUR` or `USD` `` |
| No `currency` parameter | 400 | ``Failed to deserialize query string: missing field `currency` `` |
| Alice transfers to herself | 400 | `cannot transfer with the same sender and recipient: alice` |
| Alice transfers to an unknown recipient | 404 | `recipient not found in mocked database: carol` |
| Alice transfers 1000 USD, holding 50 | 400 | `sender alice has insufficient balance 50 to transfer 1000` |
| A transfer with no auth header | 401 | `you must first login to perform transfer` |
| `GET /transfer` | 405 | empty |

The two `400` responses for a bad query string come from Axum's extractor at step 1, so their text is
Axum's. Every other error body is a message a provider formatted and raised through
[`CanRaiseHttpError`](../reference/components.md#canraisehttperror).

## Source

- [`bin/server.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/bin/server.rs)
  and [`example.sh`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/example.sh)
  — the server and the script the responses were recorded with.
- [`providers/axum/routes.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/axum/routes.rs)
  — steps 1, 2, and 9.
- [`providers/api_handlers/`](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/transfer/src/providers/api_handlers)
  and [`providers/axum/json.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/axum/json.rs)
  — steps 4 to 7.
- [`providers/mocked.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/mocked.rs)
  and [`providers/finance.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/finance.rs)
  — step 8 and the transfer guard.

## Public material derived from this

Sections 5 and 8 of the crate's own README, and its "How to run it" section.
