# Contexts and namespace

The assembly crate `hypershell` defines the namespace that routes the whole language, the error
aggregate, two ready-made contexts, and the prelude a program file imports. The bundles it routes to
are defined in the backend crates and listed here for completeness. How the layers fit is in
[assembly](../architecture/assembly.md).

## `HypershellNamespace`

`HypershellNamespace` is the namespace a context joins to run the full base language.

### Definition

The namespace is defined with [`cgp_namespace!`](../../../cgp/reference/macros/cgp_namespace.md),
inheriting `DefaultNamespace`, in
[`namespaces/handlers.rs`](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell/src/namespaces/handlers.rs).
Its entries, grouped by the provider they route to, are:

| Route | Keys | Provider |
|---|---|---|
| `@cgp.core.error.ErrorTypeProviderComponent` | — | `UseAnyhowError` |
| `@cgp.core.error.ErrorRaiserComponent` | `anyhow::Error`, `Infallible`, `std::io::Error`, `Utf8Error`, `reqwest::Error`, `url::ParseError`, `InvalidHeaderName`, `InvalidHeaderValue`, `serde_json::Error`, `ExecOutputError`, `ErrorResponse` | `HypershellErrorHandler` |
| `@cgp.core.error.ErrorWrapperComponent` | every detail | `DebugAnyhowError` |
| `@hypershell.core.CommandArgTypeProviderComponent` | — | `HypershellTokioProvider` |
| `@hypershell.reqwest.ReqwestClientGetterComponent` | — | `UseField<Symbol!("http_client")>` |
| `@cgp.extra.handler.HandlerComponent` | `BytesToString`, `ConvertTo<T>`, `Pipe<Handlers>`, `Use<Provider, Code>`, `Box<Code>` | `HypershellBaseProvider` |
| `@cgp.extra.handler.HandlerComponent` | `SimpleExec`, `StreamingExec`, `CoreExec`, `ReadFile`, `WriteFile`, `StreamToBytes`, `StreamToString`, `BytesToStream`, `StreamToStdout`, `ToTokioAsyncRead` | `HypershellTokioProvider` |
| `@cgp.extra.handler.HandlerComponent` | `SimpleHttpRequest`, `StreamingHttpRequest`, `CoreHttpRequest` | `HypershellReqwestProvider` |
| `@cgp.extra.handler.HandlerComponent` | `EncodeJson`, `DecodeJson<Value>` | `HypershellJsonProvider` |
| `@hypershell.core.StringArgExtractorComponent` | `StaticArg`, `FieldArg`, `JoinArgs` | `HypershellBaseProvider` |
| `@hypershell.core.CommandArgExtractorComponent` | `StaticArg`, `FieldArg` | `HypershellBaseProvider` |
| `@hypershell.core.UrlArgExtractorComponent` | `StaticArg`, `JoinArgs`, `FieldArg` | `HypershellBaseProvider` |
| `@hypershell.core.CommandArgExtractorComponent` | `JoinArgs` | `HypershellTokioProvider` |
| `@hypershell.tokio.CommandUpdaterComponent` | `WithArgs`, `FieldArgs` | `HypershellTokioProvider` |
| `@hypershell.core.HttpMethodTypeProviderComponent`, `@hypershell.core.UrlTypeProviderComponent` | — | `HypershellReqwestProvider` |
| `@hypershell.core.StringArgExtractorComponent` | `UrlEncodeArg` | `HypershellReqwestProvider` |
| `@hypershell.core.MethodArgExtractorComponent` | `GetMethod`, `PostMethod` | `HypershellReqwestProvider` |
| `@hypershell.reqwest.RequestBuilderUpdaterComponent` | `WithHeaders`, `Header` | `HypershellReqwestProvider` |

### Behavior

A key is the route followed by the syntax or source-error type, and each generic key binds its
parameters, as in `<Path, Args> SimpleExec<Path, Args>`. Every path key ends in an open wildcard, so
a handler entry matches its syntax with any input and leaves input dispatch to the bundle. The table
is complete as listed: `PutMethod`, `DeleteMethod`, `StreamToLines`, `Checksum`, `BytesToHex`, and
`WebSocket` have no route. See [issues.md](../issues.md#defects) for the first three.

## `HypershellErrorHandler`

`HypershellErrorHandler` is an aggregate provider that chooses a raising strategy per source error
type.

### Definition

```rust
delegate_components! {
    new HypershellErrorHandler {
        open {ErrorRaiserComponent};

        @ErrorRaiserComponent.Error: ReturnError,
        @ErrorRaiserComponent.Infallible: RaiseInfallible,
        @ErrorRaiserComponent.[
            std::io::Error, Utf8Error, reqwest::Error, ParseError,
            InvalidHeaderName, InvalidHeaderValue, serde_json::Error,
        ]: RaiseAnyhowError,
        @ErrorRaiserComponent.[ExecOutputError, ErrorResponse]: DebugAnyhowError,
    }
}
```

### Behavior

The strategies and why each type gets its own are in
[error handling](../architecture/error-handling.md#the-namespace-makes-the-error-concrete). Its list
of types must match the namespace's route list; nothing checks that it does.

## The backend bundles

Each backend crate's bundle is an aggregate provider declared with `delegate_components! { new … }`
that `open`s the components it serves. Their entries are documented with the items they route:

- **`HypershellBaseProvider`** (`hypershell_components::providers`) — [control](control.md),
  [arguments](arguments.md), and `BytesToString` in [streams and I/O](streams-and-io.md).
- **`HypershellTokioProvider`** (`hypershell_tokio_components::providers`) —
  [execution](execution.md), [streams and I/O](streams-and-io.md), and `JoinArgs` in
  [arguments](arguments.md).
- **`HypershellReqwestProvider`** (`hypershell_reqwest_components::providers`) — [HTTP](http.md) and
  `UrlEncodeArg` in [arguments](arguments.md).
- **`HypershellJsonProvider`** (`hypershell_json_components::providers`) — [JSON](json.md).
- **`HypershellTungsteniteProvider`** (`hypershell_tungstenite_components::providers`) —
  [extensions](extensions.md#websocket-and-handlewebsocket).

## `HypershellCli`

`HypershellCli` is an empty context for programs that need no runtime values.

### Definition

```rust
pub struct HypershellCli;

delegate_components! {
    HypershellCli {
        namespace HypershellNamespace;
    }
}
```

### Behavior

It runs any program whose arguments are all static. It is wired for the whole language, so an HTTP
program or a `FieldArg` resolves through every route and fails only at the field read, with a
`[CGP-E106]` root cause such as "missing field `http_client` on `HypershellCli`".

## `HypershellHttp`

`HypershellHttp` is `HypershellCli` plus the client field HTTP needs.

### Definition

```rust
#[derive(HasField)]
pub struct HypershellHttp {
    pub http_client: Client,
}

delegate_components! {
    HypershellHttp {
        namespace HypershellNamespace;
    }
}
```

### Behavior

It runs any program whose only runtime value is the `reqwest::Client`. The `rust_playground` example
uses it.

## The prelude

`hypershell::prelude` is the one import a program file needs.

### Definition

```rust
pub use core::marker::PhantomData;

pub use cgp::extra::handler::CanHandle;
pub use cgp::prelude::*;
pub use cgp_error_anyhow::Error;
pub use hypershell_components::dsl::*;
pub use hypershell_macro::hypershell;

pub use crate::contexts::{HypershellCli, HypershellHttp};
```

### Behavior

The prelude brings the `hypershell!` macro together with the `Pipe`, `Product!`, and `Symbol!`
names its expansion uses unqualified, which is why a file that imports the macro alone fails to
compile. It does not re-export `HypershellNamespace`, which a custom context imports from
`hypershell::namespaces`, nor `ToTokioAsyncRead` and the core syntax, which live in
`hypershell_tokio_components::dsl` and `hypershell_reqwest_components::dsl`.

## Source

- [crates/hypershell/src/namespaces/handlers.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell/src/namespaces/handlers.rs)
- [crates/hypershell/src/providers/error.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell/src/providers/error.rs)
- [crates/hypershell/src/contexts/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell/src/contexts)
- [crates/hypershell/src/prelude.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell/src/prelude.rs)

## Public material derived from this

Rustdoc for the `hypershell` crate, and the one-line-context demonstration early in the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
