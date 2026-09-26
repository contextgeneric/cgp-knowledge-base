# Issues

This document records what is wrong with or missing from `builder` on the `v0.8.0` branch, grouped as
defects, missing features, and housekeeping. Every entry was confirmed against the source, by a probe
crate where it says so. Remove an entry in the same change that fixes it in the crate, per
[../../AGENTS.md](../../AGENTS.md#the-shape-of-a-project-section).

## Defects

No defect has been confirmed. A probe called every builder, both constructors, and both `main`
functions, and each behaved as its code says; see [testing.md](testing.md#what-a-probe-ran).

## Missing features

- **Nothing runs the crate** — it has no binary and no test, and its two `main` functions are
  `pub async fn` in the library that nothing calls. A binary per builder, or a test that builds each
  SQLite target with `sqlite::memory:`, would give the crate a way to run and would pin its behavior.
  See [testing.md](testing.md#what-is-untested).

## Housekeeping

- **An unused provider** — `BuildDefaultSqliteAndHttpClient` and its output `SqliteAndHttpClient`, in
  `providers/sqlite_and_http.rs`, are defined and never wired. They show that one provider may build
  several subsystems at once, which is worth either a builder context that uses them or removal. See
  [subsystem providers](reference/subsystem-providers.md#builddefaultsqliteandhttpclient).
- **Reused names** — `App` names both the SQLite application in `contexts/app.rs` and the Postgres one
  in `contexts/postgres.rs`, and `AppBuilder` names both the Postgres and the Anthropic builder. Each
  module compiles on its own, but a reader or an import must qualify them by module, and a distinct
  name such as `PostgresApp` would remove the ambiguity.

## Public material derived from this

None yet.
