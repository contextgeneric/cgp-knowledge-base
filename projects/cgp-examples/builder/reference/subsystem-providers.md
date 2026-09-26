# Subsystem providers

The subsystem providers are the nine builder providers, each a `Handler` that builds one subsystem's
fields from the builder context's configuration, together with the struct each returns and the getter
trait each reads its configuration through. Every provider is generic over `Code` and `Input` and
ignores both, and every one returns `Self::Error`, the builder context's abstract error.

## The output structs

Each provider returns a small struct holding only the fields it built, and each struct derives the
three record traits that let `BuildAndMergeOutputs` merge it into a target by field name.

### Definition

```rust
#[derive(HasField, HasFields, BuildField)]
pub struct SqliteClient {
    pub sqlite_pool: SqlitePool,
}

#[derive(HasField, HasFields, BuildField)]
pub struct PostgresClient {
    pub postgres_pool: PgPool,
}

#[derive(HasField, HasFields, BuildField)]
pub struct HttpClient {
    pub http_client: Client,
}

#[derive(HasField, HasFields, BuildField)]
pub struct OpenAiClient {
    pub open_ai_client: openai::Client,
    pub open_ai_agent: Agent<openai::CompletionModel>,
}

#[derive(HasField, HasFields, BuildField)]
pub struct AnthropicClient {
    pub anthropic_client: anthropic::Client,
    pub anthropic_agent: Agent<CompletionModel>,
}

#[derive(HasField, HasFields, BuildField)]
pub struct SqliteAndHttpClient {
    pub sqlite_pool: SqlitePool,
    pub http_client: Client,
}
```

### Behavior

The field names are the contract: a struct merges into any target with fields of the same names and
types. `HasFields` is the derive the merge needs from a source, and `BuildField` the one it needs from
a target, per [`HasBuilder`](../../../../cgp/reference/traits/has_builder.md); each struct derives
both, so it could serve as either. The `Client` types are `reqwest::Client` and the `rig-core` 0.13
OpenAI and Anthropic clients.

### Context dependencies

None; they are plain data.

## The configuration getters

The six getter traits read the builder context's configuration fields, one trait per subsystem
configuration.

### Definition

```rust
#[cgp_auto_getter]
pub trait HasSqlitePath {
    fn db_path(&self) -> &str;
}

#[cgp_auto_getter]
pub trait HasSqliteOptions {
    fn db_options(&self) -> &str;

    fn db_journal_mode(&self) -> &str;
}

#[cgp_auto_getter]
pub trait HasPostgresUrl {
    fn postgres_url(&self) -> &str;
}

#[cgp_auto_getter]
pub trait HasHttpClientConfig {
    fn http_user_agent(&self) -> &str;
}

#[cgp_auto_getter]
pub trait HasOpenAiConfig {
    fn open_ai_key(&self) -> &str;

    fn open_ai_model(&self) -> &str;

    fn llm_preamble(&self) -> &str;
}

#[cgp_auto_getter]
pub trait HasAnthropicConfig {
    fn anthropic_key(&self) -> &str;

    fn llm_preamble(&self) -> &str;
}
```

### Behavior

Each method reads a `String` field of the same name as a `&str`, so a builder context satisfies a
getter by having those fields. `llm_preamble` appears in both AI getters, and a context with one
`llm_preamble` field satisfies both. Every getter reads the provider's own context, which is the case
[reading context fields](../../../../cgp/guides/reading-context-fields.md) says an `#[implicit]`
argument should cover; see [issues.md](../issues.md#modernization).

### Context dependencies

The named `String` fields, through `HasField`.

## `BuildSqliteClient`

`BuildSqliteClient` opens a SQLite pool from a connection string and a journal mode.

### Definition

```rust
#[cgp_impl(new BuildSqliteClient)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasSqliteOptions + CanRaiseError<sqlx::Error>,
{
    type Output = SqliteClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
    ) -> Result<Self::Output, Self::Error> { ... }
}
```

### Behavior

It parses `db_journal_mode` with `SqliteJournalMode::from_str` and `db_options` with
`SqliteConnectOptions::from_str`, sets the journal mode, and connects. Each step raises an
`sqlx::Error` on failure: an unknown journal mode such as `NOPE` fails with
``unknown value "NOPE" for `journal_mode` ``, and a connection string that points at a missing file
without `mode=rwc` fails with `unable to open database file`. Connecting needs an async runtime in
`sqlx`, which the crate does not enable; see [issues.md](../issues.md#defects).

### Context dependencies

`HasSqliteOptions`, and `CanRaiseError<sqlx::Error>`.

## `BuildDefaultSqliteClient`

`BuildDefaultSqliteClient` opens a SQLite pool from a single path.

### Definition

```rust
#[cgp_impl(new BuildDefaultSqliteClient)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasSqlitePath + CanRaiseError<sqlx::Error>,
{
    type Output = SqliteClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
    ) -> Result<Self::Output, Self::Error> { ... }
}
```

### Behavior

It calls `SqlitePool::connect(db_path)` and raises the `sqlx::Error` on failure. `sqlite::memory:` is a
valid path for an in-memory database.

### Context dependencies

`HasSqlitePath`, and `CanRaiseError<sqlx::Error>`.

## `BuildPostgresClient`

`BuildPostgresClient` opens a Postgres pool from a URL.

### Definition

```rust
#[cgp_impl(new BuildPostgresClient)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasPostgresUrl + CanRaiseError<sqlx::Error>,
{
    type Output = PostgresClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
    ) -> Result<Self::Output, Self::Error> { ... }
}
```

### Behavior

It calls `PgPool::connect(postgres_url)` and raises the `sqlx::Error` on failure. With no server
listening, a probe's connection failed with `pool timed out while waiting for an open connection`
after `sqlx`'s default pool timeout.

### Context dependencies

`HasPostgresUrl`, and `CanRaiseError<sqlx::Error>`.

## `BuildHttpClient`

`BuildHttpClient` builds a `reqwest` client with a configured user agent.

### Definition

```rust
#[cgp_impl(new BuildHttpClient)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasHttpClientConfig + CanRaiseError<reqwest::Error>,
{
    type Output = HttpClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
    ) -> Result<Self::Output, Self::Error> { ... }
}
```

### Behavior

It builds the client with the `http_user_agent` and a five-second connect timeout, raising a
`reqwest::Error` if the builder fails. It makes no network request.

### Context dependencies

`HasHttpClientConfig`, and `CanRaiseError<reqwest::Error>`.

## `BuildDefaultHttpClient`

`BuildDefaultHttpClient` builds a default `reqwest` client.

### Definition

```rust
#[cgp_impl(new BuildDefaultHttpClient)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasErrorType,
{
    type Output = HttpClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
    ) -> Result<Self::Output, Self::Error> { ... }
}
```

### Behavior

It returns `reqwest::Client::new()` and cannot fail. It requires `HasErrorType` only so its signature
has an error type to name.

### Context dependencies

`HasErrorType`.

## `BuildOpenAiClient`

`BuildOpenAiClient` builds an OpenAI client and an agent from a key, a model, and a preamble.

### Definition

```rust
#[cgp_impl(new BuildOpenAiClient)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasOpenAiConfig + HasErrorType,
{
    type Output = OpenAiClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
    ) -> Result<Self::Output, Self::Error> { ... }
}
```

### Behavior

It constructs `openai::Client::new(open_ai_key)` and an agent for `open_ai_model` with
`llm_preamble`. Nothing is validated or sent, so any key builds a client offline, and the provider
never fails.

### Context dependencies

`HasOpenAiConfig`, and `HasErrorType`.

## `BuildDefaultOpenAiClient`

`BuildDefaultOpenAiClient` builds an OpenAI client from the environment and a `gpt-4o` agent.

### Definition

```rust
#[cgp_impl(new BuildDefaultOpenAiClient)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasErrorType,
{
    type Output = OpenAiClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
    ) -> Result<Self::Output, Self::Error> { ... }
}
```

### Behavior

It calls `openai::Client::from_env()`, which reads `OPENAI_API_KEY`, and builds a `gpt-4o` agent with
no preamble. When the variable is unset, `rig-core` panics with `OPENAI_API_KEY not set` rather than
returning an error, so the provider panics instead of raising into the context's error type.

### Context dependencies

`HasErrorType`, and the `OPENAI_API_KEY` environment variable.

### Known issues

It panics without the environment variable; see [issues.md](../issues.md#defects).

## `BuildDefaultAnthropicClient`

`BuildDefaultAnthropicClient` builds an Anthropic client and a Claude 3.7 Sonnet agent.

### Definition

```rust
#[cgp_impl(new BuildDefaultAnthropicClient)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasAnthropicConfig + HasErrorType,
{
    type Output = AnthropicClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
    ) -> Result<Self::Output, Self::Error> { ... }
}
```

### Behavior

It builds the client from `anthropic_key` with the latest API version, and an agent for
`CLAUDE_3_7_SONNET` with `llm_preamble`. The model is fixed in the provider, which is what makes it the
default one. Nothing is sent, so it builds offline and never fails. It is the only Anthropic builder.

### Context dependencies

`HasAnthropicConfig`, and `HasErrorType`.

## `BuildDefaultSqliteAndHttpClient`

`BuildDefaultSqliteAndHttpClient` builds both the SQLite pool and a default HTTP client in one
provider.

### Definition

```rust
#[cgp_impl(new BuildDefaultSqliteAndHttpClient)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasSqlitePath + CanRaiseError<sqlx::Error>,
{
    type Output = SqliteAndHttpClient;

    async fn handle(
        &self,
        _code: PhantomData<Code>,
        _input: Input,
    ) -> Result<Self::Output, Self::Error> { ... }
}
```

### Behavior

It connects to `db_path` and creates `reqwest::Client::new()`, returning both in one struct, which
shows that a provider may build several subsystems at once. No builder context wires it.

### Context dependencies

`HasSqlitePath`, and `CanRaiseError<sqlx::Error>`.

### Known issues

Unused; see [issues.md](../issues.md#housekeeping).

## Source

- [`providers/sqlite.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/sqlite.rs)
  — `HasSqlitePath`, `HasSqliteOptions`, `SqliteClient`, and the two SQLite providers.
- [`providers/postgres.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/postgres.rs)
  — `HasPostgresUrl`, `PostgresClient`, and `BuildPostgresClient`.
- [`providers/http_client.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/http_client.rs)
  — `HasHttpClientConfig`, `HttpClient`, and the two HTTP providers.
- [`providers/chatgpt.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/chatgpt.rs)
  — `HasOpenAiConfig`, `OpenAiClient`, and the two OpenAI providers.
- [`providers/anthropic.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/anthropic.rs)
  — `HasAnthropicConfig`, `AnthropicClient`, and `BuildDefaultAnthropicClient`.
- [`providers/sqlite_and_http.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/providers/sqlite_and_http.rs)
  — `SqliteAndHttpClient` and `BuildDefaultSqliteAndHttpClient`.

## Public material derived from this

Page 1 of the planned [extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
