# Builder contexts

The builder contexts are the five structs that hold configuration and wire the subsystem providers
into `BuildAndMergeOutputs`, together with the three target markers the multi-target builder
dispatches on and the two `main` functions that call a builder. Every builder context derives
`HasField`, so the providers' `#[implicit]` arguments read its fields, and `Deserialize`, so it can be
loaded from a configuration file.

## `FullAppBuilder`

`FullAppBuilder` builds the SQLite `App` from the full configuration of every subsystem.

### Definition

```rust
#[derive(HasField, Deserialize)]
pub struct FullAppBuilder {
    pub db_options: String,
    pub db_journal_mode: String,
    pub http_user_agent: String,
    pub open_ai_key: String,
    pub open_ai_model: String,
    pub llm_preamble: String,
}

delegate_components! {
    FullAppBuilder {
        ErrorTypeProviderComponent:
            UseAnyhowError,
        ErrorRaiserComponent:
            RaiseAnyhowError,
        HandlerComponent:
            BuildAndMergeOutputs<
                App,
                Product![
                    BuildSqliteClient,
                    BuildHttpClient,
                    BuildOpenAiClient,
                ]>,
    }
}

check_components! {
    FullAppBuilder {
        HandlerComponent: ((), ()),
    }
}
```

### Behavior

`builder.handle(PhantomData::<()>, ())` runs the three configurable builders and merges their outputs
into an `App`. The two error entries are the same in every builder context: `UseAnyhowError` sets the
abstract error to `anyhow::Error`, and `RaiseAnyhowError` raises any standard error into it, which
satisfies each provider's `CanRaiseError<sqlx::Error>` or `CanRaiseError<reqwest::Error>`. The check
asserts that `HandlerComponent` holds at the unit `Code` and `Input` the call uses, so a missing
configuration field or provider fails the build at the check, as
[testing.md](../testing.md#what-the-checks-pin) shows. A probe built an `App` with a `mode=rwc` SQLite
connection string, and an unknown journal mode such as `NOPE` returned the `sqlx` parse error.

### Context dependencies

None beyond its own fields; it is the context the providers depend on.

## `DefaultAppBuilder`

`DefaultAppBuilder` builds the same SQLite `App` from a single database path, using the three default
providers.

### Definition

```rust
#[derive(HasField, Deserialize)]
pub struct DefaultAppBuilder {
    pub db_path: String,
}

delegate_components! {
    DefaultAppBuilder {
        ErrorTypeProviderComponent:
            UseAnyhowError,
        ErrorRaiserComponent:
            RaiseAnyhowError,
        HandlerComponent:
            BuildAndMergeOutputs<
                App,
                Product![
                    BuildDefaultSqliteClient,
                    BuildDefaultHttpClient,
                    BuildDefaultOpenAiClient,
                ]>,
    }
}
```

Its check block asserts `HandlerComponent: ((), ())`, as `FullAppBuilder`'s does.

### Behavior

It shows the same target built by a different set of providers from different configuration. The
OpenAI key comes from the environment rather than a field. A probe built an `App` with
`db_path = "sqlite::memory:"` and `OPENAI_API_KEY` set, and got `Err(environment variable not found)`
with the variable unset.

### Context dependencies

The `OPENAI_API_KEY` environment variable, through `BuildDefaultOpenAiClient`.

## `AppBuilder` in `contexts/postgres.rs`

The Postgres `AppBuilder` builds the Postgres `App`, swapping `BuildPostgresClient` in for the SQLite
builder.

### Definition

```rust
#[derive(HasField, Deserialize)]
pub struct AppBuilder {
    pub postgres_url: String,
    pub http_user_agent: String,
    pub open_ai_key: String,
    pub open_ai_model: String,
    pub llm_preamble: String,
}

delegate_components! {
    AppBuilder {
        ErrorTypeProviderComponent:
            UseAnyhowError,
        ErrorRaiserComponent:
            RaiseAnyhowError,
        HandlerComponent:
            BuildAndMergeOutputs<
                App,
                Product![
                    BuildPostgresClient,
                    BuildHttpClient,
                    BuildOpenAiClient,
                ]>,
    }
}
```

Its check block asserts `HandlerComponent: ((), ())`.

### Behavior

With no Postgres server listening, a probe's build returned
`pool timed out while waiting for an open connection`, raised from `BuildPostgresClient`.

### Context dependencies

A reachable Postgres server at `postgres_url`.

### Known issues

It shares the name `AppBuilder` with the Anthropic builder; see
[issues.md](../issues.md#housekeeping).

## `AppBuilder` in `contexts/anthropic.rs`

The Anthropic `AppBuilder` builds `AnthropicApp`.

### Definition

```rust
#[derive(HasField, Deserialize)]
pub struct AppBuilder {
    pub db_options: String,
    pub db_journal_mode: String,
    pub http_user_agent: String,
    pub anthropic_key: String,
    pub llm_preamble: String,
}

delegate_components! {
    AppBuilder {
        ErrorTypeProviderComponent:
            UseAnyhowError,
        ErrorRaiserComponent:
            RaiseAnyhowError,
        HandlerComponent:
            BuildAndMergeOutputs<
                AnthropicApp,
                Product![
                    BuildSqliteClient,
                    BuildHttpClient,
                    BuildDefaultAnthropicClient,
                ]>,
    }
}
```

Its check block asserts `HandlerComponent: ((), ())`.

### Behavior

A probe built an `AnthropicApp` offline, since `BuildDefaultAnthropicClient` sends nothing.

### Context dependencies

None beyond its own fields.

### Known issues

It shares the name `AppBuilder` with the Postgres builder; see [issues.md](../issues.md#housekeeping).

## `AnthropicAndChatGptAppBuilder` and its markers

`AnthropicAndChatGptAppBuilder` builds one of three applications, chosen by a marker type passed as the
`Code`.

### Definition

```rust
#[derive(HasField, Deserialize)]
pub struct AnthropicAndChatGptAppBuilder {
    pub db_options: String,
    pub db_journal_mode: String,
    pub http_user_agent: String,
    pub anthropic_key: String,
    pub open_ai_key: String,
    pub open_ai_model: String,
    pub llm_preamble: String,
}

pub struct BuildAnthropicAndChatGptApp;

pub struct BuildChatGptApp;

pub struct BuildAnthropicApp;

delegate_components! {
    AnthropicAndChatGptAppBuilder {
        open HandlerComponent;

        ErrorTypeProviderComponent:
            UseAnyhowError,
        ErrorRaiserComponent:
            RaiseAnyhowError,

        @HandlerComponent.BuildAnthropicAndChatGptApp:
            BuildAndMergeOutputs<AnthropicAndChatGptApp, Product![ ... ]>,
        @HandlerComponent.BuildChatGptApp:
            BuildAndMergeOutputs<App, Product![ ... ]>,
        @HandlerComponent.BuildAnthropicApp:
            BuildAndMergeOutputs<AnthropicApp, Product![ ... ]>,
    }
}

check_components! {
    AnthropicAndChatGptAppBuilder {
        HandlerComponent: [
            (BuildAnthropicAndChatGptApp, ()),
            (BuildChatGptApp, ()),
            (BuildAnthropicApp, ()),
        ],
    }
}
```

The elided provider lists are SQLite, HTTP, Anthropic, and OpenAI for the combined application;
SQLite, HTTP, and OpenAI for `App`; and SQLite, HTTP, and Anthropic for `AnthropicApp`.

### Behavior

The builder opens `HandlerComponent` with the `open` statement and keys each target by its marker, a
one-segment path key that matches the `Code` and any `Input`; see
[dispatching per type](../../../../cgp/guides/dispatching-per-type.md). Calling
`builder.handle(PhantomData::<BuildChatGptApp>, ())` builds an `App`, and the other two markers build
their own targets from the same configuration. The markers are empty structs used only as codes. One
`llm_preamble` field serves both AI providers. A probe built all three targets offline.

### Context dependencies

None beyond its own fields.

## The `main` functions

`full_builder::main` and `anthropic_and_chatgpt::main` each construct a builder with literal
configuration and build from it.

### Definition

```rust
pub async fn main() -> Result<(), Error> {
    let builder = FullAppBuilder {
        db_options: "sqlite:./db.sqlite?mode=rwc".to_owned(),
        db_journal_mode: "WAL".to_owned(),
        http_user_agent: "SUPER_AI_AGENT".to_owned(),
        open_ai_key: "1234567890".to_owned(),
        open_ai_model: "gpt-4o".to_owned(),
        llm_preamble: "You are a helpful assistant".to_owned(),
    };

    let _app = builder.handle(PhantomData::<()>, ()).await?;

    /* Call methods on the app here */

    Ok(())
}
```

`anthropic_and_chatgpt::main` builds an `AnthropicAndChatGptAppBuilder` the same way and calls
`handle` once per marker.

### Behavior

Both use the connection string `sqlite:./db.sqlite?mode=rwc`, whose `mode=rwc` creates the database
file in the working directory when it is missing. A probe called each in a directory with no
`db.sqlite`: both returned `Ok`, and the file appeared. They are `pub async fn` in the library, so nothing runs them
unless another crate calls them.

### Context dependencies

A writable working directory.

## Source

- [`contexts/full_builder.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/contexts/full_builder.rs)
  — `FullAppBuilder` and its `main`.
- [`contexts/default_builder.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/contexts/default_builder.rs)
  — `DefaultAppBuilder`.
- [`contexts/postgres.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/contexts/postgres.rs)
  — the Postgres `AppBuilder`.
- [`contexts/anthropic.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/contexts/anthropic.rs)
  — the Anthropic `AppBuilder`.
- [`contexts/anthropic_and_chatgpt.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/builder/src/contexts/anthropic_and_chatgpt.rs)
  — `AnthropicAndChatGptAppBuilder`, its three markers, and its `main`.

## Public material derived from this

The "Builder Context", "Default Builder", "Postgres App", "Anthropic App", and "Multi-Context Builder"
sections of pages 1 and 2 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
