# `transfer`

`transfer` is a small money-transfer web service: it answers a balance query and moves funds between
two users, served over HTTP by Axum, with every domain type, every business operation, and every
cross-cutting concern expressed as a swappable CGP component.

- **Source** — [transfer/](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/transfer), on
  the `v0.8.0` branch; see [which revision](../README.md#which-revision-these-documents-describe)
- **Run** — `cargo run --bin server` from the repository root, then `transfer/example.sh` in a second
  terminal
- **Needs** — port 8080 free; `curl` and `base64` for the script
- **Result** — serves on `0.0.0.0:8080`. `example.sh` returned `{"balance":100}` for Alice,
  `{"balance":200}` for Bob, and an empty `200` for the transfer; every error path returned its
  status and message, as recorded in [request-lifecycle.md](architecture/request-lifecycle.md)
- **Worked example** — [money-transfer API](../../../examples/money-transfer-api.md)
- **Cited by** — the [v0.5.0 release post](../../../website/blog/v0-5-0-release.md)

## What it is

The service has two endpoints, both authenticated with HTTP Basic auth. `GET /balance?currency=EUR`
returns the caller's balance in one currency as `{"balance":…}`, and
`POST /transfer?currency=EUR&recipient=bob&quantity=10` moves an amount to another user and returns
an empty `200`. Both endpoints read their arguments from the query string, not from a request body.
Failures return an HTTP status and a plain-text message: `401` when the caller is not logged in, `400`
for a bad request such as a transfer to oneself, and `404` for an unknown recipient.

The data lives in memory, in two maps on the one context, `MockApp`. The server seeds them with two
users, `alice` with password `wonderland` (100 EUR, 50 USD) and `bob` with password `sponge`
(200 EUR, 150 USD). Every other part of the program is written against abstract types and
components: the handlers never name `String`, `u64`, or the currency enum, and never name the
in-memory store. The concrete choices are made once, in the wiring, which is what
[architecture/](architecture/README.md) explains.

The crate has its own [README](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/README.md),
a public walkthrough of the same program written for a reader new to CGP. These documents are the
verified record the walkthrough should agree with, and [issues.md](issues.md) lists where it does
not.

## Idioms

The crate is written in current CGP idioms, so its code is safe to copy for the patterns it shows:
providers are `#[cgp_impl]` blocks, dependencies are `#[uses]` and `#[use_provider]` imports,
abstract types are imported with `#[use_type]` (including the equality form), fields are read as
`#[implicit]` arguments, and the wiring is organized with prefixes, namespaces, `#[default_impl]`,
and a `for` loop. The request getters import the app's abstract types with
`#[use_type(… in App)]`.

## Status and gaps

The service works as a demonstration and has no automated tests. Its gaps are each confirmed against
the `v0.8.0` branch and recorded in full in [issues.md](issues.md):

- **Unused items** — `HandleHttpErrorWithAnyhow`, `HandleFromResponse`, `ErrInternal`, and
  `CanAddApiRoutes` are defined and never wired or called.
- **No request bodies** — the routing layer extracts requests with `FromRequestParts`, so an endpoint
  cannot read a body.
- **The walkthrough has drifted** — the crate's README describes a per-detail error wiring the code no
  longer has, and calls components "capabilities" throughout.

## The documents

Read the architecture first for how the pieces fit, then use the reference to look up an item.

- [architecture/](architecture/README.md) — the design on one page, and one document per idea:
  - [module-layout.md](architecture/module-layout.md) — the five modules, which kind of item each
    holds, and which way their dependencies point.
  - [error-design.md](architecture/error-design.md) — status-code markers, the one error type, and
    how the error provider is chosen per detail type.
  - [namespace-organization.md](architecture/namespace-organization.md) — the prefix tree, the two
    tables `MockApp` draws on, and the one path it overrides.
  - [request-lifecycle.md](architecture/request-lifecycle.md) — one balance query traced through
    every layer, with the responses recorded for each error path.
- [reference/](reference/README.md) — every public item, grouped by family, with a table of all of
  them:
  - [domain-types.md](reference/domain-types.md) — the five abstract types.
  - [components.md](reference/components.md) — the API handler, auth, finance, and HTTP-error
    components, and the marker types they take.
  - [api-handlers.md](reference/api-handlers.md) — `HandleQueryBalance` and `HandleTransfer`, and
    the getter traits they read requests through.
  - [wrappers.md](reference/wrappers.md) — `UseBasicAuth`, `HandleFromRequest`,
    `HandleFromResponse`, `ResponseToJson`, and `NoTransferToSelf`.
  - [error-providers.md](reference/error-providers.md) — `DisplayHttpError`,
    `HandleHttpErrorWithAnyhow`, `IsStatusCode`, and `AppError`.
  - [mock-backend.md](reference/mock-backend.md) — the four `UseMockedApp` implementations.
  - [wiring.md](reference/wiring.md) — `MockNamespace`, `DefaultApiHandlers`, and `MockApp`.
  - [http-layer.md](reference/http-layer.md) — the request types, `DemoCurrency`, the `Send`
    recovery trait, and the Axum routing traits.
- [guides/](guides/README.md) — how to change the service:
  - [adding-an-endpoint.md](guides/adding-an-endpoint.md) — every piece a new endpoint needs, in
    the crate or from a downstream crate.
  - [swapping-the-backend.md](guides/swapping-the-backend.md) — replacing the in-memory backend,
    and why a new backend needs its own namespace.
- [testing.md](testing.md) — what the compile-time checks pin, and what no test exercises.
- [issues.md](issues.md) — the confirmed defects, missing features, and housekeeping items.

## Public material derived from these documents

These documents are the source the crate's own README should be checked against, and the fixes it
needs are listed in [issues.md](issues.md#the-crates-readme). They are also the verified record behind
the `Send`-recovery snippets that the [v0.5.0 release post](../../../website/blog/v0-5-0-release.md)
links to in an older commit of `contexts/app.rs`; the two `CanHandleApiSend` impls it points at are
unchanged in the current code.

## How it relates to the rest of the base

The [money-transfer API](../../../examples/money-transfer-api.md) worked example teaches this
scenario's patterns and stands alone, so an agent learning them reads that example rather than these
documents. The general techniques the crate applies are documented where they belong:
[organizing wiring with namespaces and prefixes](../../../cgp/guides/namespaces-and-prefixes.md) for
its wiring, [recovering `Send` bounds](../../../cgp/concepts/send-bounds.md) for its HTTP layer,
[modular error handling](../../../cgp/concepts/modular-error-handling.md) for its errors, and
[higher-order providers](../../../cgp/concepts/higher-order-providers.md) for its wrappers. These
documents say only what this crate does with each.
