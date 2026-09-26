# Issues

This document records what is wrong with or missing from `transfer` on the `v0.8.0` branch, grouped
as defects, missing features, and housekeeping. Every entry was confirmed against the source, by a
probe crate or a run of the server where it says so. Remove an entry in the same change that fixes it
in the crate, per [../../AGENTS.md](../../AGENTS.md#the-shape-of-a-project-section).

## Defects

A defect is behavior that is wrong for the input it is given.

### `UseMockedApp` credits a self-transfer

The mock backend's transfer reads both balances before writing either, so when sender and recipient
are the same user the recipient's write lands last and the balance grows by the amount:

```rust
let old_sender_balance = balances.get(&sender_key)...;
let old_recipient_balance = balances.get(&recipient_key)...;

let new_sender_balance = old_sender_balance.checked_sub(quantity)...;
let new_recipient_balance = old_recipient_balance.checked_add(quantity)...;

balances.insert(sender_key, new_sender_balance);
balances.insert(recipient_key, new_recipient_balance); // same key: overwrites the debit
```

A probe context that joined `MockNamespace` and wired
`@app.finance.MoneyTransferrerComponent: UseMockedApp` directly turned a balance of 100 into 110 with
a self-transfer of 10. The service itself is unaffected, because `MockApp` wraps the backend in
`NoTransferToSelf`, which rejects the request with `400` first. The defect surfaces in any
context that wires the backend's transfer without the guard, and nothing in the provider or its
component says the guard is required. The fix is to
reject `sender == recipient` in the provider itself, or to write the sender's balance before reading
the recipient's. See [mock backend](reference/mock-backend.md#moneytransferrer).

## Missing features

A missing feature is behavior the crate does not attempt.

- **No automated tests** — the crate has no `#[test]`, and `example.sh` prints without checking. See
  [testing.md](testing.md).
- **No request bodies** — `CanAddRoute` requires the request to implement `FromRequestParts`, so an
  endpoint reads only the URI and headers, and the transfer endpoint takes its arguments from the
  query string. See [the HTTP layer](reference/http-layer.md#canaddroute).
- **The type choices cannot be shared between backends** — the error type, the five abstract types, and
  the HTTP error provider are bound in `MockNamespace` together with the mock providers. A namespace
  binding cannot be overridden by an inheriting namespace, so a second backend cannot inherit
  `MockNamespace` and replace only its providers; it must repeat every type choice in a namespace of
  its own, as [swapping the backend](guides/swapping-the-backend.md) shows. Moving the type and error
  bindings into a base namespace that each backend namespace inherits fixes it: a probe with an
  `AppTypesNamespace: DefaultNamespace` holding only those bindings, a
  `MockBackendNamespace: AppTypesNamespace` binding only the three backend paths, and a context
  joining the latter compiled and passed the same check as `MockApp`. See
  [namespace organization](architecture/namespace-organization.md).
- **Routes serve only `AppError`** — the routing traits require `HasErrorType<Error = AppError>`, so a
  context with a different error type cannot be served without new routing impls.

## Housekeeping

Housekeeping items are neither defects nor features: code that is unused, inconsistent with the rest,
or misdescribed.

- **Unused items** — `HandleHttpErrorWithAnyhow` and `HandleFromResponse` are defined and never
  wired, `ErrInternal` is never raised, and the `CanAddApiRoutes` alias in `contexts/app.rs` is never
  named; the binary imports `CanAddMainApiRoutes` instead. Each is either worth a use in the service or
  worth removing.
- **A comment gives the wrong reason** — the comment on `MockNamespace` in `namespaces/mock.rs` says
  its body holds "the pieces that have no `#[cgp_impl]` block of their own to attach a
  `#[default_impl]` to". `DisplayHttpError` has one; it is in the body because it is generic over
  `Code` and `Detail`, which `#[default_impl]` cannot register.
- **"Capability" in comments** — the code comments in `interfaces/`, `contexts/app.rs`, and
  `bin/server.rs` call components "capabilities", a word the base avoids for CGP's own constructs, per
  the `/cgp` skill's vocabulary.
- **A stray lockfile** — `transfer/Cargo.lock` is tracked, but `transfer` is a workspace member, so
  Cargo uses the root `Cargo.lock` and ignores this one.

### The crate's README

The crate's [README](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/README.md)
is the repository's public walkthrough of this program, and four of its statements disagree with the
code:

- It says the error wiring "picks between the two per detail type", naming `DisplayHttpError` and
  `HandleHttpErrorWithAnyhow`. Only `DisplayHttpError` is wired, for `String` details.
- It says failures return "`404` when a user is unknown". An unknown user fails authentication and gets
  `401`; `404` is returned for an unknown transfer recipient.
- It says `MockNamespace` spells out "the entries that have no `#[cgp_impl]` block to attach to",
  repeating the wrong reason in the code comment above.
- Its closing summaries understate both extension paths: adding an endpoint takes the six pieces in
  [adding an endpoint](guides/adding-an-endpoint.md), not "a handler provider and one line", and a
  new backend needs its own namespace, per [swapping the backend](guides/swapping-the-backend.md).

It also uses "capability" for components throughout, as the code comments do.

## Public material derived from this

The fixes the crate's README needs, listed above.
