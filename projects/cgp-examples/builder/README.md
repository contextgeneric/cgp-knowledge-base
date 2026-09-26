# `builder`

`builder` assembles application contexts, structs holding a database pool, an HTTP client, and one or
two AI clients, from independent per-subsystem builder providers that know nothing of the final struct
or of each other, and wires five builder contexts that combine those providers into four application
types.

- **Source** — [builder/](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/builder), on the
  `v0.8.0` branch; see [which revision](../README.md#which-revision-these-documents-describe)
- **Run** — nothing: the crate has no binary and no test, and its two `main` functions are ordinary
  library functions nothing calls
- **Needs** — for the SQLite builders, a connection string that names an existing file or carries
  `mode=rwc` to create one, as both `main` functions do; a Postgres server for the Postgres builder;
  and `OPENAI_API_KEY` for the default builder
- **Result** — a probe called every builder: each SQLite-based builder assembled its application
  offline, and both `main` functions returned `Ok` in a directory with no database file; see
  [testing.md](testing.md#what-a-probe-ran)
- **Worked example** — [application builder](../../../examples/application-builder.md)
- **Cited by** — [extensible data types, part 1](../../../website/blog/extensible-datatypes-part-1.md),
  which links the crate

## What it is

An application context is an ordinary struct, such as `App` with a `sqlite_pool`, an `http_client`,
an `open_ai_client`, and an `open_ai_agent`. Instead of one constructor that sets every field, each
subsystem has its own builder provider, a [`Handler`](../../../cgp/reference/components/handler.md)
that reads its configuration from a **builder context** and returns a small struct holding just its
own fields, such as `SqliteClient { sqlite_pool }`. A builder context wires a list of those providers
into `BuildAndMergeOutputs<App, …>`, which runs each one and merges its fields into the target by name.

The crate has four application structs and five builder contexts, one per combination it
demonstrates:

| Builder context | Module | Builds | Providers |
|---|---|---|---|
| `FullAppBuilder` | `full_builder` | `App` | configurable SQLite, HTTP, and OpenAI |
| `DefaultAppBuilder` | `default_builder` | `App` | the three default providers |
| `AppBuilder` | `postgres` | that module's `App`, with a `PgPool` | Postgres, HTTP, and OpenAI |
| `AppBuilder` | `anthropic` | `AnthropicApp` | SQLite, HTTP, and Anthropic |
| `AnthropicAndChatGptAppBuilder` | `anthropic_and_chatgpt` | `App`, `AnthropicApp`, or `AnthropicAndChatGptApp`, by code | SQLite, HTTP, and either or both AI providers |

Two names repeat across modules: `App` is both the SQLite application in `contexts/app.rs` and the
Postgres one in `contexts/postgres.rs`, and `AppBuilder` is both the Postgres and the Anthropic builder.
The reference qualifies them by module.

## Idioms

The crate uses current CGP idioms throughout. The providers read their configuration as
[`#[implicit]`](../../../cgp/reference/attributes/implicit.md) arguments, import the traits they call
with `#[uses]`, and name the builder context's error as a bare `Error` imported with
`#[use_type(HasErrorType.Error)]`. The output and application structs derive `CgpData`, and the
multi-target builder dispatches on its code with the `open` statement.

## Status and gaps

The crate demonstrates the pattern, and every builder runs when called. Its gaps are each confirmed
against the `v0.8.0` branch and recorded in full in [issues.md](issues.md):

- **Nothing runs it** — no binary and no test; the `main` functions are library functions nothing
  calls.

## Where the blog post's code lives

The [part 1 post](../../../website/blog/extensible-datatypes-part-1.md) builds this crate section by
section. How its code diverges from current CGP is recorded in the post's own document; the table
below says only where each section's code now lives:

| Post section | Current code |
|---|---|
| Feature Highlights: enum upcasting and downcasting, struct building | not in this repository |
| Motivation for Extensible Builders | `contexts/app.rs`: `App::new` and `App::new_with_default` |
| Modular SQLite Builder | `providers/sqlite.rs` |
| HTTP Client Builder | `providers/http_client.rs` |
| Combined SQLite and HTTP Client Builder | `providers/sqlite_and_http.rs`, never wired |
| ChatGPT Client Builder | `providers/chatgpt.rs` |
| Builder Context, Building the App | `contexts/full_builder.rs` |
| Builder Dispatcher | `BuildAndMergeOutputs` in CGP itself; the post's hand-written `BuildApp` is not in the crate |
| Default Builder | `contexts/default_builder.rs` |
| Postgres App | `contexts/postgres.rs` and `providers/postgres.rs` |
| Anthropic App | `contexts/anthropic.rs` and `providers/anthropic.rs` |
| Anthropic and ChatGPT Builder, Multi-Context Builder | `contexts/anthropic_and_chatgpt.rs`, which holds only the multi-target form |

## The documents

- [architecture/](architecture/README.md) — the design on one page: builders as handlers, name-driven
  merging, target selection by code, and where the pattern's internals are documented.
- [reference/](reference/README.md) — every public item, grouped by family:
  - [subsystem-providers.md](reference/subsystem-providers.md) — the nine builder providers and their
    output structs.
  - [application-contexts.md](reference/application-contexts.md) — the four application structs and
    the hand-written constructors.
  - [builder-contexts.md](reference/builder-contexts.md) — the five builder contexts, their target
    markers, and the two `main` functions.
- [testing.md](testing.md) — what the compile-time checks catch, what a probe ran, and what nothing
  tests.
- [issues.md](issues.md) — the missing features and housekeeping.

## Public material derived from these documents

These documents are the verified record behind pages 1 and 2 of the planned
[extensible data types deep dive](../../../website/deep-dives/extensible-datatypes.md), which uses this
crate as its running code.

## How it relates to the rest of the base

The [application builder](../../../examples/application-builder.md) worked example teaches the
crate's pattern and stands alone. The pattern itself is
[extensible records](../../../cgp/concepts/extensible-records.md), the merge dispatcher and its
internals are in the [dispatch combinators](../../../cgp/reference/providers/dispatch_combinators.md),
the builder trait family is [`HasBuilder`](../../../cgp/reference/traits/has_builder.md), and the
merging is `CanBuildFrom` from the [casts](../../../cgp/reference/traits/cast.md).
