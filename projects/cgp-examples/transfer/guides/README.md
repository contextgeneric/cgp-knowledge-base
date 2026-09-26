# `transfer` guides

These guides say how to make the two changes the service is designed for: serving a new endpoint, and
replacing the in-memory backend. Each was checked by building the change in a downstream probe crate
against the `v0.8.0` branch, so the steps are the ones the compiler requires rather than the ones the
crate's README summarizes.

- [adding-an-endpoint.md](adding-an-endpoint.md) — the six pieces a new endpoint needs, where each
  goes, and which of them a downstream crate can add without editing `transfer`.
- [swapping-the-backend.md](swapping-the-backend.md) — writing a second backend, why it needs a
  namespace of its own rather than an override of `MockNamespace`, and the error the override
  produces.

## Public material derived from this

The closing "The payoff" section of the crate's own README, whose one-line summaries of both changes
these guides expand.
