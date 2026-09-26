# Application contexts

The application contexts are the four structs the builders produce: plain structs of subsystem
handles, each deriving `CgpData` so a builder can assemble it field by field, with no wiring of their
own. The SQLite `App` also keeps the two hand-written constructors the builder pattern replaces.

## `App` in `contexts/app.rs`

`App` is the SQLite application: a SQLite pool, an HTTP client, and an OpenAI client and agent.

### Definition

```rust
#[derive(CgpData)]
pub struct App {
    pub sqlite_pool: SqlitePool,
    pub http_client: Client,
    pub open_ai_client: openai::Client,
    pub open_ai_agent: Agent<openai::CompletionModel>,
}

impl App {
    pub async fn new(
        db_options: &str,
        db_journal_mode: &str,
        http_user_agent: &str,
        open_ai_key: &str,
        open_ai_model: &str,
        llm_preamble: &str,
    ) -> Result<Self, Error> { ... }

    pub async fn new_with_default(db_path: &str) -> Result<Self, Error> { ... }
}
```

### Behavior

`FullAppBuilder`, `DefaultAppBuilder`, and the `BuildChatGptApp` target of
`AnthropicAndChatGptAppBuilder` all build this struct. Its fields match the output structs of
`BuildSqliteClient` or `BuildDefaultSqliteClient`, the HTTP builders, and the OpenAI builders by name,
which is what lets [`BuildAndMergeOutputs`](../../../../cgp/reference/providers/dispatch_combinators.md#buildwithhandlers-and-buildandmergeoutputs)
merge them into it.

The two constructors are the starting point the builders replace, each doing in one function what a
builder context splits across providers. `new` takes every configuration value as an argument and
does what `BuildSqliteClient`, `BuildHttpClient`, and `BuildOpenAiClient` do together; a probe called
it with a `mode=rwc` SQLite connection string and it returned the built `App`. `new_with_default`
does what the three default builders do, reading the OpenAI key from `OPENAI_API_KEY`; a probe called
it with `sqlite::memory:` and got the built `App` with the variable set and
`Err(environment variable not found)` without it. Both return the `cgp-error-anyhow` `Error`, which is
`anyhow::Error`, and nothing in the crate calls either.

### Context dependencies

None; it is plain data.

### Known issues

The Postgres application in `contexts/postgres.rs` is also named `App`; see
[issues.md](../issues.md#housekeeping).

## `App` in `contexts/postgres.rs`

The Postgres `App` swaps the SQLite pool for a Postgres pool and keeps the other three fields.

### Definition

```rust
#[derive(CgpData)]
pub struct App {
    pub postgres_pool: PgPool,
    pub http_client: Client,
    pub open_ai_client: openai::Client,
    pub open_ai_agent: Agent<openai::CompletionModel>,
}
```

### Behavior

Only `postgres::AppBuilder` builds it. Its `postgres_pool` field is what `BuildPostgresClient`'s output
supplies, and the other three fields come from the same HTTP and OpenAI builders the SQLite `App`
uses, which is the point of the variant: one subsystem swapped, the rest reused unchanged.

### Context dependencies

None.

### Known issues

It shares the name `App` with the SQLite application; see [issues.md](../issues.md#housekeeping).

## `AnthropicApp`

`AnthropicApp` replaces the OpenAI client and agent with an Anthropic client and agent.

### Definition

```rust
#[derive(CgpData)]
pub struct AnthropicApp {
    pub sqlite_pool: SqlitePool,
    pub http_client: Client,
    pub anthropic_client: anthropic::Client,
    pub anthropic_agent: Agent<anthropic::completion::CompletionModel>,
}
```

### Behavior

`anthropic::AppBuilder` builds it, and so does the `BuildAnthropicApp` target of
`AnthropicAndChatGptAppBuilder`. Its Anthropic fields come from `BuildDefaultAnthropicClient`.

### Context dependencies

None.

## `AnthropicAndChatGptApp`

`AnthropicAndChatGptApp` carries both AI subsystems at once.

### Definition

```rust
#[derive(CgpData)]
pub struct AnthropicAndChatGptApp {
    pub sqlite_pool: SqlitePool,
    pub http_client: Client,
    pub anthropic_client: anthropic::Client,
    pub anthropic_agent: Agent<anthropic::completion::CompletionModel>,
    pub open_ai_client: openai::Client,
    pub open_ai_agent: Agent<openai::CompletionModel>,
}
```

### Behavior

Only the `BuildAnthropicAndChatGptApp` target of `AnthropicAndChatGptAppBuilder` builds it, by merging
four builders' outputs: SQLite, HTTP, Anthropic, and OpenAI.

### Context dependencies

None.

## Source

- [`contexts/app.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/contexts/app.rs)
  — the SQLite `App` and its two constructors.
- [`contexts/postgres.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/contexts/postgres.rs)
  — the Postgres `App`.
- [`contexts/anthropic.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/contexts/anthropic.rs)
  — `AnthropicApp`.
- [`contexts/anthropic_and_chatgpt.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/contexts/anthropic_and_chatgpt.rs)
  — `AnthropicAndChatGptApp`.

## Public material derived from this

The "Motivation for Extensible Builders" section of page 1 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
