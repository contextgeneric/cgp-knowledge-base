# Testing

`transfer` has no tests: `cargo test --workspace` compiles its library and its server binary and runs
no test in either. What the crate verifies, it verifies at compile time, through one
`check_components!` block, the two `CanHandleApiSend` impls, and the binary's route setup. This
document records what those pin and what nothing exercises.

## What compiles only if the wiring is right

Three parts of the code are compile-time assertions, and each covers a different property.

- **The check block** in `contexts/app.rs` asserts that `MockApp` can use `QuantityTypeProviderComponent`,
  `UserBalanceQuerierComponent`, `MoneyTransferrerComponent`, and `ApiHandlerComponent` for both
  `QueryBalanceApi` and `TransferApi`. Because a
  [`check_components!`](../../../cgp/reference/macros/check_components.md) entry follows each
  provider's own dependencies, the two handler entries also cover every component the pipelines call:
  the password lookup and check, the balance query, the transfer through `NoTransferToSelf`, the error
  raiser for each status the providers raise, and all five abstract types and the error type.
- **The `CanHandleApiSend` impls** compile only if each endpoint's future is `Send`, which is the
  property Axum's multi-threaded runtime needs and the check block cannot express.
- **The binary** compiles only if `Router<Arc<MockApp>>` satisfies `CanAddMainApiRoutes`, which
  requires each endpoint's request to be extractable and its response to be an Axum response.

## What runs

Nothing runs automatically. `example.sh` is a manual script: it queries Alice's and Bob's balances and
transfers 10 EUR, printing the responses without checking them. The responses recorded in
[the request lifecycle](architecture/request-lifecycle.md), including every error path, were
produced by hand against the running server for these documents; the repository pins none of them.

## What is untested

These behaviors have no test of any kind, and each is recorded from a probe or a manual run instead:

- **Every error path** — no test sends a wrong password, an unknown recipient, an overdraft, or a bad
  query string, so none of the status codes or messages is pinned.
- **The backend on its own** — `UseMockedApp`'s transfer is only ever run behind `NoTransferToSelf`,
  so no test would catch its self-transfer defect; see
  [issues.md](issues.md#usemockedapp-credits-a-self-transfer).
- **Unused providers** — `HandleFromResponse` and `HandleHttpErrorWithAnyhow` are never wired, so the
  compiler checks their definitions but never checks them against a context.
- **Concurrency** — no test runs overlapping transfers against the shared balance map.
- **Compile failures** — there are no compile-fail tests, so the diagnostic in
  [swapping the backend](guides/swapping-the-backend.md) is not pinned either.

## Public material derived from this

None yet.
