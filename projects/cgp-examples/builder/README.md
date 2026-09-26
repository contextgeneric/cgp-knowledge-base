# `builder`

`builder` assembles application contexts, structs holding a database pool, an HTTP client, and one or
two AI clients, from independent per-subsystem builder providers that know nothing of the final struct
or of each other, and wires five builder contexts that combine those providers into four application
types.

- **Source** — [builder/](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/builder), on the
  `v0.8.0` branch; see [which revision](../README.md#which-revision-these-documents-describe)
- **Run** — nothing: the crate has no binary and no test, and its two `main` functions are ordinary
  library functions nothing calls
- **Needs** — a database file or server, and an `OPENAI_API_KEY` for the default builder
- **Result** — as shipped, every builder that opens a database panics, because the crate's `sqlx`
  dependency enables no async runtime. With the runtime enabled in a probe, every SQLite-based builder
  assembled its application offline; see [testing.md](testing.md#what-a-probe-ran)
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

The crate's providers are `#[cgp_impl]` blocks, but the rest is older than current CGP. The providers
read their configuration through six `#[cgp_auto_getter]` traits although every field they read is on
their own context, which is the case an `#[implicit]` argument covers; they state dependencies as
hand-written `where Self: …` bounds and return `Self::Error`; the multi-target builder dispatches with
a legacy `UseDelegate` table; and the structs list their derives rather than deriving `CgpData`. Copy
the patterns from the [application builder](../../../examples/application-builder.md) worked example,
which writes the providers with `#[uses]` and `#[use_type]`. The changes are listed in
[issues.md](issues.md#modernization), and a probe confirmed the `open` form of the multi-target table.

## Status and gaps

The crate demonstrates the pattern but cannot run as shipped. Its gaps are each confirmed against the
`v0.8.0` branch and recorded in full in [issues.md](issues.md):

- **No async runtime for `sqlx`** — opening any SQLite or Postgres pool panics.
- **A panicking default provider** — `BuildDefaultOpenAiClient` panics when `OPENAI_API_KEY` is unset
  instead of raising an error.
- **The `main` functions fail on a fresh checkout** — their SQLite options do not create the database
  file.
- **Nothing runs it** — no binary, no test.
- **Older idioms and a misspelled marker** — see Idioms above, and the `BuildAnthroicAndChatGptApp`
  marker.

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
  - [subsystem-providers.md](reference/subsystem-providers.md) — the nine builder providers, their
    output structs, and their configuration getters.
  - [application-contexts.md](reference/application-contexts.md) — the four application structs and
    the hand-written constructors.
  - [builder-contexts.md](reference/builder-contexts.md) — the five builder contexts and their target
    markers.
- [testing.md](testing.md) — the compile-time checks, what a probe ran, and what nothing tests.
- [issues.md](issues.md) — the confirmed defects, missing features, modernization items, and
  housekeeping.

## Public material derived from these documents

These documents are the verified record behind pages 1 and 2 of the planned
[extensible data types deep dive](../../../website/deep-dives/extensible-datatypes.md), which uses this
crate as its running code, and the source changes those pages need first are the
[modernization items](issues.md#modernization).

## How it relates to the rest of the base

The [application builder](../../../examples/application-builder.md) worked example teaches the
crate's pattern and stands alone. The pattern itself is
[extensible records](../../../cgp/concepts/extensible-records.md), the merge dispatcher and its
internals are in the [dispatch combinators](../../../cgp/reference/providers/dispatch_combinators.md),
the builder trait family is [`HasBuilder`](../../../cgp/reference/traits/has_builder.md), and the
merging is `CanBuildFrom` from the [casts](../../../cgp/reference/traits/cast.md).
