# Subsystem providers

The subsystem providers are the nine builder providers, each a `Handler` that builds one subsystem's
fields from the builder context's configuration, together with the struct each returns. Every provider
is generic over `Code` and `Input` and ignores both, and every one returns `Error`, the builder
context's abstract error, imported with `#[use_type(HasErrorType.Error)]`.

## The output structs

Each provider returns a small struct holding only the fields it built, and each struct derives the
record traits that let `BuildAndMergeOutputs` merge it into a target by field name.

### Definition

```rust
#[derive(CgpData)]
pub struct SqliteClient {
    pub sqlite_pool: SqlitePool,
}

#[derive(CgpData)]
pub struct PostgresClient {
    pub postgres_pool: PgPool,
}

#[derive(CgpData)]
pub struct HttpClient {
    pub http_client: Client,
}

#[derive(CgpData)]
pub struct OpenAiClient {
    pub open_ai_client: openai::Client,
    pub open_ai_agent: Agent<openai::CompletionModel>,
}

#[derive(CgpData)]
pub struct AnthropicClient {
    pub anthropic_client: anthropic::Client,
    pub anthropic_agent: Agent<CompletionModel>,
}

#[derive(CgpData)]
pub struct SqliteAndHttpClient {
    pub sqlite_pool: SqlitePool,
    pub http_client: Client,
}
```

### Behavior

The field names are the contract: a struct merges into any target with fields of the same names and
types. A merge needs the field list from its source and the builder from its target, per
[`HasBuilder`](../../../../cgp/reference/traits/has_builder.md), and
[`#[derive(CgpData)]`](../../../../cgp/reference/derives/derive_cgp_data.md) supplies both, so each
struct could serve as either. The `Client` types are `reqwest::Client` and the `rig-core` 0.13
OpenAI and Anthropic clients.

### Context dependencies

None; they are plain data.

## `BuildSqliteClient`

`BuildSqliteClient` opens a SQLite pool from a connection string and a journal mode.

### Definition

```rust
#[cgp_impl(new BuildSqliteClient)]
#[uses(CanRaiseError<sqlx::Error>)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input> {
    type Output = SqliteClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
        #[implicit] db_options: &str,
        #[implicit] db_journal_mode: &str,
    ) -> Result<Self::Output, Error> { ... }
}
```

### Behavior

It parses `db_journal_mode` with `SqliteJournalMode::from_str` and `db_options` with
`SqliteConnectOptions::from_str`, sets the journal mode, and connects. Each step raises an
`sqlx::Error` on failure: an unknown journal mode such as `NOPE` fails with
``unknown value "NOPE" for `journal_mode` ``, and a connection string that points at a missing file
without `mode=rwc` fails with `unable to open database file`. Connecting runs on the tokio runtime,
which the crate enables through `sqlx`'s `runtime-tokio` feature.

### Context dependencies

The `db_options` and `db_journal_mode` fields, and `CanRaiseError<sqlx::Error>`.

## `BuildDefaultSqliteClient`

`BuildDefaultSqliteClient` opens a SQLite pool from a single path.

### Definition

```rust
#[cgp_impl(new BuildDefaultSqliteClient)]
#[uses(CanRaiseError<sqlx::Error>)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input> {
    type Output = SqliteClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
        #[implicit] db_path: &str,
    ) -> Result<Self::Output, Error> { ... }
}
```

### Behavior

It calls `SqlitePool::connect(db_path)` and raises the `sqlx::Error` on failure. `sqlite::memory:` is a
valid path for an in-memory database.

### Context dependencies

The `db_path` field, and `CanRaiseError<sqlx::Error>`.

## `BuildPostgresClient`

`BuildPostgresClient` opens a Postgres pool from a URL.

### Definition

```rust
#[cgp_impl(new BuildPostgresClient)]
#[uses(CanRaiseError<sqlx::Error>)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input> {
    type Output = PostgresClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
        #[implicit] postgres_url: &str,
    ) -> Result<Self::Output, Error> { ... }
}
```

### Behavior

It calls `PgPool::connect(postgres_url)` and raises the `sqlx::Error` on failure. With no server
listening, a probe's connection failed with `pool timed out while waiting for an open connection`
after `sqlx`'s default pool timeout.

### Context dependencies

The `postgres_url` field, and `CanRaiseError<sqlx::Error>`.

## `BuildHttpClient`

`BuildHttpClient` builds a `reqwest` client with a configured user agent.

### Definition

```rust
#[cgp_impl(new BuildHttpClient)]
#[uses(CanRaiseError<reqwest::Error>)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input> {
    type Output = HttpClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
        #[implicit] http_user_agent: &str,
    ) -> Result<Self::Output, Error> { ... }
}
```

### Behavior

It builds the client with the `http_user_agent` and a five-second connect timeout, raising a
`reqwest::Error` if the builder fails. It makes no network request.

### Context dependencies

The `http_user_agent` field, and `CanRaiseError<reqwest::Error>`.

## `BuildDefaultHttpClient`

`BuildDefaultHttpClient` builds a default `reqwest` client.

### Definition

```rust
#[cgp_impl(new BuildDefaultHttpClient)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input> {
    type Output = HttpClient;

    async fn handle(&self, _code: PhantomData<Code>, _input: Input) -> Result<Self::Output, Error> { ... }
}
```

### Behavior

It returns `reqwest::Client::new()` and cannot fail. It imports `HasErrorType` only so its signature
has an error type to name.

### Context dependencies

`HasErrorType`.

## `BuildOpenAiClient`

`BuildOpenAiClient` builds an OpenAI client and an agent from a key, a model, and a preamble.

### Definition

```rust
#[cgp_impl(new BuildOpenAiClient)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input> {
    type Output = OpenAiClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
        #[implicit] open_ai_key: &str,
        #[implicit] open_ai_model: &str,
        #[implicit] llm_preamble: &str,
    ) -> Result<Self::Output, Error> { ... }
}
```

### Behavior

It constructs `openai::Client::new(open_ai_key)` and an agent for `open_ai_model` with
`llm_preamble`. Nothing is validated or sent, so any key builds a client offline, and the provider
never fails.

### Context dependencies

The `open_ai_key`, `open_ai_model`, and `llm_preamble` fields, and `HasErrorType`.

## `BuildDefaultOpenAiClient`

`BuildDefaultOpenAiClient` builds an OpenAI client from the environment and a `gpt-4o` agent.

### Definition

```rust
#[cgp_impl(new BuildDefaultOpenAiClient)]
#[uses(CanRaiseError<VarError>)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input> {
    type Output = OpenAiClient;

    async fn handle(&self, _code: PhantomData<Code>, _input: Input) -> Result<Self::Output, Error> { ... }
}
```

### Behavior

It reads `OPENAI_API_KEY` from the environment, raises the `VarError` if it is unset or not Unicode,
and builds `openai::Client::new` with it and a `gpt-4o` agent with no preamble. With the variable
unset, a probe's `DefaultAppBuilder` returned `Err(environment variable not found)`. The client is
the one `rig-core`'s own `Client::from_env` would build, which reads the same variable but panics
when it is missing.

### Context dependencies

`CanRaiseError<VarError>`, and the `OPENAI_API_KEY` environment variable.

## `BuildDefaultAnthropicClient`

`BuildDefaultAnthropicClient` builds an Anthropic client and a Claude 3.7 Sonnet agent.

### Definition

```rust
#[cgp_impl(new BuildDefaultAnthropicClient)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input> {
    type Output = AnthropicClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
        #[implicit] anthropic_key: &str,
        #[implicit] llm_preamble: &str,
    ) -> Result<Self::Output, Error> { ... }
}
```

### Behavior

It builds the client from `anthropic_key` with the latest API version, and an agent for
`CLAUDE_3_7_SONNET` with `llm_preamble`. The model is fixed in the provider, which is what makes it the
default one. Nothing is sent, so it builds offline and never fails. It is the only Anthropic builder.

### Context dependencies

The `anthropic_key` and `llm_preamble` fields, and `HasErrorType`.

## `BuildDefaultSqliteAndHttpClient`

`BuildDefaultSqliteAndHttpClient` builds both the SQLite pool and a default HTTP client in one
provider.

### Definition

```rust
#[cgp_impl(new BuildDefaultSqliteAndHttpClient)]
#[uses(CanRaiseError<sqlx::Error>)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input> {
    type Output = SqliteAndHttpClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
        #[implicit] db_path: &str,
    ) -> Result<Self::Output, Error> { ... }
}
```

### Behavior

It connects to `db_path` and creates `reqwest::Client::new()`, returning both in one struct, which
shows that a provider may build several subsystems at once. No builder context wires it.

### Context dependencies

The `db_path` field, and `CanRaiseError<sqlx::Error>`.

### Known issues

Unused; see [issues.md](../issues.md#housekeeping).

## How the providers read configuration

Every configurable provider reads the builder context's fields as
[`#[implicit]`](../../../../cgp/reference/attributes/implicit.md) arguments on `handle`, so a builder
context satisfies a provider by having `String` fields of the argument names. Each argument is a
`&str` read from a `String` field. `BuildOpenAiClient` and `BuildDefaultAnthropicClient` both read
`llm_preamble`, and a context with one `llm_preamble` field serves both. `BuildDefaultHttpClient` and
`BuildDefaultOpenAiClient` read no field: the first needs only the error type, and the second reads
its key from the environment instead.

## Source

- [`providers/sqlite.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/sqlite.rs)
  — `SqliteClient` and the two SQLite providers.
- [`providers/postgres.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/postgres.rs)
  — `PostgresClient` and `BuildPostgresClient`.
- [`providers/http_client.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/http_client.rs)
  — `HttpClient` and the two HTTP providers.
- [`providers/chatgpt.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/chatgpt.rs)
  — `OpenAiClient` and the two OpenAI providers.
- [`providers/anthropic.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/anthropic.rs)
  — `AnthropicClient` and `BuildDefaultAnthropicClient`.
- [`providers/sqlite_and_http.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/sqlite_and_http.rs)
  — `SqliteAndHttpClient` and `BuildDefaultSqliteAndHttpClient`.

## Public material derived from this

Page 1 of the planned [extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
