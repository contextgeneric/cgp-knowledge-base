# `builder` reference

This directory documents every public item in the `builder` crate, grouped by family, with one
document per family following the entry template in
[../../../AGENTS.md](../../../AGENTS.md#reference-entries). The tables below list every item so a
reader can find one by what it builds and see which builder contexts use it. Read the
[architecture](../architecture/README.md) first for how the families fit together.

## Providers

Every provider is a `#[cgp_impl]` block implementing `Handler<Code, Input>` for any `Code` and
`Input`, and returns a small output struct that `BuildAndMergeOutputs` merges into the target. The last
column is what the provider requires of the builder context.

| Provider | Output | Used by | Requires of the context |
|---|---|---|---|
| [`BuildSqliteClient`](subsystem-providers.md#buildsqliteclient) | `SqliteClient` | `FullAppBuilder`, the Anthropic `AppBuilder`, `AnthropicAndChatGptAppBuilder` | `db_options` and `db_journal_mode` fields, `CanRaiseError<sqlx::Error>` |
| [`BuildDefaultSqliteClient`](subsystem-providers.md#builddefaultsqliteclient) | `SqliteClient` | `DefaultAppBuilder` | a `db_path` field, `CanRaiseError<sqlx::Error>` |
| [`BuildPostgresClient`](subsystem-providers.md#buildpostgresclient) | `PostgresClient` | the Postgres `AppBuilder` | a `postgres_url` field, `CanRaiseError<sqlx::Error>` |
| [`BuildHttpClient`](subsystem-providers.md#buildhttpclient) | `HttpClient` | every builder context but `DefaultAppBuilder` | an `http_user_agent` field, `CanRaiseError<reqwest::Error>` |
| [`BuildDefaultHttpClient`](subsystem-providers.md#builddefaulthttpclient) | `HttpClient` | `DefaultAppBuilder` | `HasErrorType` |
| [`BuildOpenAiClient`](subsystem-providers.md#buildopenaiclient) | `OpenAiClient` | `FullAppBuilder`, the Postgres `AppBuilder`, `AnthropicAndChatGptAppBuilder` | `open_ai_key`, `open_ai_model`, and `llm_preamble` fields |
| [`BuildDefaultOpenAiClient`](subsystem-providers.md#builddefaultopenaiclient) | `OpenAiClient` | `DefaultAppBuilder` | `CanRaiseError<VarError>`, and `OPENAI_API_KEY` in the environment |
| [`BuildDefaultAnthropicClient`](subsystem-providers.md#builddefaultanthropicclient) | `AnthropicClient` | the Anthropic `AppBuilder`, `AnthropicAndChatGptAppBuilder` | `anthropic_key` and `llm_preamble` fields |
| [`BuildDefaultSqliteAndHttpClient`](subsystem-providers.md#builddefaultsqliteandhttpclient) | `SqliteAndHttpClient` | nothing | a `db_path` field, `CanRaiseError<sqlx::Error>` |

## Other items

The remaining items are the output structs, the application structs, the builder contexts, the
markers, and the `main` functions.

| Item | Kind | Module |
|---|---|---|
| [`SqliteClient`, `PostgresClient`, `HttpClient`, `OpenAiClient`, `AnthropicClient`, `SqliteAndHttpClient`](subsystem-providers.md#the-output-structs) | output structs | `providers` |
| [`App`](application-contexts.md#app-in-contextsapprs), with `new` and `new_with_default` | SQLite application | `contexts::app` |
| [`App`](application-contexts.md#app-in-contextspostgresrs) | Postgres application | `contexts::postgres` |
| [`AnthropicApp`](application-contexts.md#anthropicapp) | Anthropic application | `contexts::anthropic` |
| [`AnthropicAndChatGptApp`](application-contexts.md#anthropicandchatgptapp) | combined application | `contexts::anthropic_and_chatgpt` |
| [`FullAppBuilder`](builder-contexts.md#fullappbuilder) | builder context | `contexts::full_builder` |
| [`DefaultAppBuilder`](builder-contexts.md#defaultappbuilder) | builder context | `contexts::default_builder` |
| [`AppBuilder`](builder-contexts.md#appbuilder-in-contextspostgresrs) | builder context | `contexts::postgres` |
| [`AppBuilder`](builder-contexts.md#appbuilder-in-contextsanthropicrs) | builder context | `contexts::anthropic` |
| [`AnthropicAndChatGptAppBuilder`](builder-contexts.md#anthropicandchatgptappbuilder-and-its-markers) | builder context | `contexts::anthropic_and_chatgpt` |
| [`BuildAnthropicAndChatGptApp`, `BuildChatGptApp`, `BuildAnthropicApp`](builder-contexts.md#anthropicandchatgptappbuilder-and-its-markers) | target markers | `contexts::anthropic_and_chatgpt` |
| [`main`](builder-contexts.md#the-main-functions) | example entry functions | `contexts::full_builder`, `contexts::anthropic_and_chatgpt` |

The `providers` module re-exports its files with glob imports, while each context is reached through
its module path, such as `cgp_example_builder::contexts::full_builder::FullAppBuilder`.

## The catalog

- [subsystem-providers.md](subsystem-providers.md) — the nine builder providers and their output
  structs.
- [application-contexts.md](application-contexts.md) — the four application structs and the
  hand-written constructors.
- [builder-contexts.md](builder-contexts.md) — the five builder contexts, their target markers, and
  the `main` functions.

## Public material derived from this

The crate's rustdoc, which the source does not carry.
