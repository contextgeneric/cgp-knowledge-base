# Module layout

`transfer` is one library crate with one binary, and its library is split into five modules by the
kind of item each holds, so the interfaces of the service sit apart from every implementation of
them. This document records what each module holds and which way the dependencies between them point.

## The five modules

The library root, [`src/lib.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/lib.rs),
declares five public modules, and each holds one kind of item:

| Module | Holds | Depends on |
|---|---|---|
| `interfaces` | the abstract types, the components, and the marker types they take | `cgp` only |
| `providers` | every provider: endpoint handlers, wrappers, error providers, the mock backend, and the Axum routing traits | `interfaces`, `types`, `namespaces` |
| `types` | the concrete types a deployment plugs in: `DemoCurrency`, `AppError`, and the request types | `axum`, `axum-extra`, `headers`, `serde` |
| `namespaces` | `MockNamespace` and `DefaultApiHandlers` | `interfaces`, `providers`, `types` |
| `contexts` | `MockApp`, its wiring and checks, and the `CanHandleApiSend` impls | all four |

The binary, [`bin/server.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/bin/server.rs),
depends only on `contexts` and on the routing trait in `providers`. It builds a `MockApp`, mounts the
routes on an Axum `Router`, and serves.

The split puts every choice in one place. `interfaces` names no concrete type and no backend, so it
compiles with `cgp` alone. `types` names no CGP item, so it is ordinary Rust. The context module is
the only one that sees all of them, and its wiring is where they meet. One file per item family
keeps each module small: `providers` has `api_handlers/`, `axum/`, `error.rs`, `finance.rs`, and
`mocked.rs`, and `interfaces` has one file per domain (`api`, `auth`, `error`, `finance`, `types`).

## The dependencies that cross the split

Three dependencies do not follow the inward direction, and each has a reason in the code.

- **`providers` depends on `namespaces`.** The mock backend in
  [`providers/mocked.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/mocked.rs)
  registers itself into `MockNamespace` with `#[default_impl(... in MockNamespace)]`, so it must name
  the namespace. The attribute places a provider's wiring next to the provider, and the price is this
  backward edge: the backend module cannot be compiled without the namespace that uses it. See
  [namespace organization](namespace-organization.md).
- **`providers` depends on `types`.** The error providers build an `AppError` directly, and the
  routing traits in `providers/axum/routes.rs` bound the context's error to `AppError`, so both are
  written for this deployment's concrete error rather than for any context.
- **`interfaces` holds one ordinary trait.** `CanHandleApiSend` in
  [`interfaces/api.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/interfaces/api.rs)
  is not a CGP component. It sits beside `CanHandleApi` because it restates that component with a
  `Send` future, and it is implemented in `contexts`. See the [HTTP layer](../reference/http-layer.md).

The five modules are `pub`, and each keeps its files as private submodules whose `pub` items its
`mod.rs` re-exports with glob imports, so every item is reachable from its module's root and a
downstream crate can reuse any piece, as the probes behind the [guides](../guides/README.md) did.

## Source

- [`transfer/src/`](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/transfer/src) — the five
  modules.
- [`transfer/bin/server.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/bin/server.rs)
  — the binary.
- [`transfer/Cargo.toml`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/Cargo.toml)
  — the dependencies: `cgp`, `anyhow`, `futures`, `num-traits`, `serde`, `axum`, `axum-extra`,
  `headers`, and `tokio`.

## Public material derived from this

The "Map of the code" section of the crate's own README.
