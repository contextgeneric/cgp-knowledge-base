# Testing

`builder` has no tests and no binary, so the only checks the repository runs are its five
`check_components!` blocks, at compile time. This document records what those blocks pin, what a
probe crate ran against every builder for these documents, and what nothing exercises.

## What the checks pin

Each builder context has one `check_components!` block, and each asserts `HandlerComponent` at the
`Code` and `Input` its builds use:

| Builder context | Checked for |
|---|---|
| `FullAppBuilder` | `((), ())` |
| `DefaultAppBuilder` | `((), ())` |
| `postgres::AppBuilder` | `((), ())` |
| `anthropic::AppBuilder` | `((), ())` |
| `AnthropicAndChatGptAppBuilder` | `(BuildAnthropicAndChatGptApp, ())`, `(BuildChatGptApp, ())`, and `(BuildAnthropicApp, ())` |

A check covers the whole build, because the providers' bounds reach it through
`BuildAndMergeOutputs`: each provider's fields and error raisers on the builder context, and the
providers' outputs together filling every field of the target. Two probes confirmed the field and
output cases. The first wired `FullAppBuilder`'s table on a copy of the context without the
`llm_preamble` field:

```rust
#[derive(HasField)]
pub struct NoPreambleBuilder {
    pub db_options: String,
    pub db_journal_mode: String,
    pub http_user_agent: String,
    pub open_ai_key: String,
    pub open_ai_model: String,
}
```

With the same `HandlerComponent: ((), ())` check, `cargo cgp check` failed at the check line and named
the field, through the chain from `BuildAndMergeOutputs` down to `BuildOpenAiClient`, whose
`#[implicit] llm_preamble` argument needs it:

```text
error[E0271]: [CGP-E001] the consumer trait `CanHandle<(), ()>` is not implemented for context `NoPreambleBuilder`
   = note: root cause: [CGP-E106] missing field `llm_preamble` on `NoPreambleBuilder`
```

A second probe kept every field and left `BuildHttpClient` out of the list, wiring
`BuildAndMergeOutputs<App, Product![BuildSqliteClient, BuildOpenAiClient]>`. The check failed because
the partial `App` cannot be finalized with its second field, `http_client`, still absent:

```text
error[E0277]: the trait bound `__PartialApp<IsPresent, IsNothing, IsPresent, IsPresent>: FinalizeBuild` is not satisfied
```

The checks say nothing about what a build does at runtime: a builder that compiles can still fail to
connect, as the Postgres one does without a server.

## What a probe ran

A probe crate with a path dependency on the crate called every builder, both constructors, and both
`main` functions, in a fresh working directory with no `db.sqlite` and no network services:

| Call | Result |
|---|---|
| `FullAppBuilder`, with `db_options = "sqlite:probe.db?mode=rwc"` | `App` built |
| `FullAppBuilder`, with `db_journal_mode = "NOPE"` | error: ``unknown value "NOPE" for `journal_mode` `` |
| `DefaultAppBuilder`, with `db_path = "sqlite::memory:"` and `OPENAI_API_KEY` set | `App` built |
| `DefaultAppBuilder`, with `OPENAI_API_KEY` unset | error: `environment variable not found` |
| `anthropic::AppBuilder` | `AnthropicApp` built |
| `AnthropicAndChatGptAppBuilder`, each of the three markers | each target built |
| `postgres::AppBuilder`, with nothing listening at `postgres_url` | error: `pool timed out while waiting for an open connection` |
| `App::new`, with a `mode=rwc` connection string | `App` built |
| `App::new_with_default("sqlite::memory:")`, with `OPENAI_API_KEY` set, then unset | `App` built, then error: `environment variable not found` |
| `full_builder::main` and `anthropic_and_chatgpt::main` | both `Ok`, creating `db.sqlite` |

No builder contacts OpenAI or Anthropic: the AI builders only construct clients and agents, so any key
builds them offline.

## What is untested

These have no test, and the first was exercised only by the probe above:

- **Every build** — nothing in the repository calls a builder, a constructor, or a `main` function.
- **`BuildDefaultSqliteAndHttpClient`** — never wired, so never run; see
  [issues.md](issues.md#housekeeping).
- **A live service** — no run connected to Postgres or sent a request to an AI provider.
- **Compile failures** — there are no compile-fail tests.

## Public material derived from this

None yet.
