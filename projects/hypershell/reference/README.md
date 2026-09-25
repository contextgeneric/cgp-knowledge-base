# Hypershell reference

This directory documents every public item in the Hypershell crates, grouped by family, with one
document per family following the entry template in
[../../AGENTS.md](../../AGENTS.md#reference-entries). Two adaptations of the template apply
throughout. A syntax type and the provider that interprets it share one entry, since neither means
anything without the other. And no entry has a Pairing field, because nothing in Hypershell has two
directions the way serialization does. Each family document instead ends with a **Wiring** section
saying which bundle and namespace route serve its items. Read the
[architecture](../architecture/README.md) first for the ideas the items share.

## Syntax

Every syntax type is an empty marker. The table lists each with the crate that defines it, the
provider that interprets it under `HypershellNamespace`, and whether the namespace routes it.

| Syntax | Defined in | Interpreted by | Routed | Reference |
|---|---|---|---|---|
| `SimpleExec<Path, Args>` | `hypershell-components` | `HandleSimpleExec` | yes | [execution](execution.md) |
| `StreamingExec<Path, Args>` | `hypershell-components` | `HandleToTokioAsyncRead` → `HandleStreamingExec` → `WrapTokioAsyncRead` | yes | [execution](execution.md) |
| `CoreExec<Path, Args>` | `hypershell-tokio-components` | `HandleCoreExec` | yes | [execution](execution.md) |
| `WithArgs<Args>`, `WithStaticArgs<Args>` | `hypershell-components` | `ExtractArgs` | yes | [execution](execution.md) |
| `FieldArgs<Tag>` | `hypershell-components` | `ExtractFieldArgs` | yes | [execution](execution.md) |
| `StaticArg<Arg>` | `hypershell-components` | `ExtractStaticArg`, via the layered extractors | yes | [arguments](arguments.md) |
| `FieldArg<Tag>` | `hypershell-components` | `ExtractFieldArg`, via the layered extractors | yes | [arguments](arguments.md) |
| `JoinArgs<Args>` | `hypershell-components` | `JoinStringArgs` (strings, URLs), `JoinExtractArgs` (paths) | yes | [arguments](arguments.md) |
| `UrlEncodeArg<Arg>` | `hypershell-components` | `UrlEncodeStringArg` | strings only | [arguments](arguments.md) |
| `SimpleHttpRequest<Method, Url, Params>` | `hypershell-components` | `HandleSimpleHttpRequest` | yes | [HTTP](http.md) |
| `StreamingHttpRequest<Method, Url, Params>` | `hypershell-components` | four-stage pipeline ending in `HandleStreamingHttpRequest` | yes | [HTTP](http.md) |
| `CoreHttpRequest<Method, Url, Params>` | `hypershell-reqwest-components` | `HandleCoreHttpRequest` | yes | [HTTP](http.md) |
| `GetMethod`, `PostMethod` | `hypershell-components` | `ExtractReqwestMethod` | yes | [HTTP](http.md) |
| `PutMethod`, `DeleteMethod` | `hypershell-components` | `ExtractReqwestMethod` | **no** | [HTTP](http.md) |
| `WithHeaders<Headers>`, `Header<Key, Value>` | `hypershell-components` | `UpdateRequestHeaders`, `UpdateRequestHeader` | yes | [HTTP](http.md) |
| `StreamToBytes`, `StreamToString`, `StreamToStdout`, `BytesToStream`, `BytesToString` | `hypershell-components` | the adapter providers | yes | [streams and I/O](streams-and-io.md) |
| `StreamToLines` | `hypershell-components` | `HandleStreamToLines` | **no** | [streams and I/O](streams-and-io.md) |
| `ToTokioAsyncRead` | `hypershell-tokio-components` | `HandleToTokioAsyncRead` | yes | [streams and I/O](streams-and-io.md) |
| `ReadFile<Path>`, `WriteFile<Path>` | `hypershell-components` | `HandleReadFile`, `HandleWriteFile` | yes | [streams and I/O](streams-and-io.md) |
| `EncodeJson`, `DecodeJson<T>` | `hypershell-components` | `HandleEncodeJson`, `HandleDecodeJson` | yes | [JSON](json.md) |
| `Pipe<Handlers>` | `hypershell-components` | `HandlePipe` | yes | [control](control.md) |
| `Use<Provider, Code>` | `hypershell-components` | `HandleUseProvider` | yes | [control](control.md) |
| `ConvertTo<T>` | `hypershell-components` | `Promote<HandleConvert>`, which does not resolve | yes | [control](control.md) |
| `Box<Code>` | `std` | `BoxHandler<Call<Code>>` | yes | [control](control.md) |
| `Checksum<Hasher>`, `BytesToHex` | `hypershell-hash-components` | `HandleStreamChecksum`, `HandleBytesToHex` | extension | [extensions](extensions.md) |
| `WebSocket<Url, Params>` | `hypershell-components` | `HandleWebsocket`, per input | extension | [extensions](extensions.md) |

All the `hypershell-components` syntax is re-exported by `hypershell::prelude`. The core syntax and
`ToTokioAsyncRead` are imported from their own crates' `dsl` modules.

## Components

Each component is defined with `#[cgp_component]`, `#[cgp_type]`, or `#[cgp_getter]`, so it also has
a provider trait and a `…Component` wiring key, and each carries a `#[prefix]` into `DefaultNamespace`.

| Consumer trait | Provider trait | Prefix | Import from | Reference |
|---|---|---|---|---|
| `CanExtractStringArg<Arg>` | `StringArgExtractor` | `@hypershell.core` | `hypershell_components::components` | [arguments](arguments.md) |
| `CanExtractCommandArg<Arg>` | `CommandArgExtractor` | `@hypershell.core` | `hypershell_components::components` | [arguments](arguments.md) |
| `HasCommandArgType` | `CommandArgTypeProvider` | `@hypershell.core` | `hypershell_components::components` | [arguments](arguments.md) |
| `CanExtractUrlArg<Arg>` | `UrlArgExtractor` | `@hypershell.core` | `hypershell_components::components` | [arguments](arguments.md) |
| `HasUrlType` | `UrlTypeProvider` | `@hypershell.core` | `hypershell_components::components` | [arguments](arguments.md) |
| `CanExtractMethodArg<Arg>` | `MethodArgExtractor` | `@hypershell.core` | `hypershell_components::components` | [HTTP](http.md) |
| `HasHttpMethodType` | `HttpMethodTypeProvider` | `@hypershell.core` | `hypershell_components::components` | [HTTP](http.md) |
| `CanUpdateCommand<Args>` | `CommandUpdater` | `@hypershell.tokio` | `hypershell_tokio_components::components` | [execution](execution.md) |
| `CanUpdateRequestBuilder<Args>` | `RequestBuilderUpdater` | `@hypershell.reqwest` | `hypershell_reqwest_components::components` | [HTTP](http.md) |
| `HasReqwestClient` | `ReqwestClientGetter` | `@hypershell.reqwest` | `hypershell_reqwest_components::components` | [HTTP](http.md) |

The interpreter itself is CGP's [`Handler`](../../../cgp/reference/components/handler.md), imported
from `cgp::extra::handler`, with `CanHandle` re-exported by the prelude. The extractor and updater
components also carry a legacy `#[derive_delegate(UseDelegate<…>)]` that nothing uses.

## Providers without their own syntax

Most providers appear in the syntax table. These are the ones a wiring names directly:

| Provider | Crate | What it does | Reference |
|---|---|---|---|
| `Call<InCode>` | `hypershell-components` | handles any syntax by handling `InCode` on the context | [control](control.md#call) |
| `BoxHandler<InHandler>` | `hypershell-components` | boxes an inner handler's future | [control](control.md#box-and-boxhandler) |
| `ReturnInput` | `hypershell-components` | identity handler, duplicating CGP's | [control](control.md#returninput) |
| `ExtractStringCommandArg`, `ExtractStringUrlArg` | `hypershell-components` | build the command and URL extractors from the string extractor | [arguments](arguments.md) |
| `ExtractUrlFieldArg`, `ExtractMethodFieldArg` | `hypershell-components` | read a typed URL or method field; **routed nowhere** | [arguments](arguments.md), [HTTP](http.md) |
| `StreamToBody` | `hypershell-reqwest-components` | a Tokio reader as a streamed request body | [HTTP](http.md) |
| `HandleToTokioAsyncRead`, `HandleToFuturesStream` | `hypershell-tokio-components` | input dispatchers | [streams and I/O](streams-and-io.md) |
| the byte, reader, and stream adapters | `hypershell-tokio-components` | convert between bytes and the stream kinds | [streams and I/O](streams-and-io.md) |
| `TokioToFuturesAsyncRead` | `hypershell-tokio-components` | Tokio reader to futures reader; **routed nowhere** | [streams and I/O](streams-and-io.md) |

## Bundles, contexts, and other items

| Item | Kind | Import from | Reference |
|---|---|---|---|
| `HypershellNamespace` | namespace | `hypershell::namespaces` | [contexts and namespace](contexts-and-namespace.md) |
| `HypershellErrorHandler` | error aggregate | `hypershell::providers` | [contexts and namespace](contexts-and-namespace.md) |
| `HypershellCli`, `HypershellHttp` | contexts | `hypershell::prelude` | [contexts and namespace](contexts-and-namespace.md) |
| `HypershellBaseProvider`, `HypershellTokioProvider`, `HypershellReqwestProvider`, `HypershellJsonProvider`, `HypershellTungsteniteProvider` | bundles | each crate's `providers` | [contexts and namespace](contexts-and-namespace.md#the-backend-bundles) |
| `TokioAsyncReadStream`, `FuturesAsyncReadStream`, `FuturesStream` | stream wrappers | `hypershell_tokio_components::types` | [streams and I/O](streams-and-io.md) |
| `WrapCall`, `WrapStaticArg` | type-level list maps | `hypershell_components::traits` | [control](control.md), [execution](execution.md) |
| `ExecOutputError`, `StdinPipeError`, `WaitWithOutputError`, `CommandNotFound`, `SpawnCommandFailure` | errors and details | `hypershell_tokio_components::providers` | [execution](execution.md#error-types) |
| `ErrorResponse` | error | `hypershell_reqwest_components::providers` | [HTTP](http.md#errorresponse) |
| `DecodeUtf8InputError` | detail | `hypershell_components::providers` | [streams and I/O](streams-and-io.md) |
| `hypershell!` | macro | `hypershell::prelude` | [macro](macro.md) |

## The catalog

Register each reference document here, in [../README.md](../README.md), and in
[../../../summary.md](../../../summary.md) in the same change.

- [execution.md](execution.md) — `SimpleExec`, `StreamingExec`, `CoreExec`, the command updater and
  its list syntax, and the execution error types.
- [arguments.md](arguments.md) — the string, command, and URL extractors and their abstract types,
  `StaticArg`, `FieldArg`, `JoinArgs`, `UrlEncodeArg`, and the layered providers.
- [http.md](http.md) — the three request syntaxes, the method markers and extractor, headers, the
  client getter, and `ErrorResponse`.
- [streams-and-io.md](streams-and-io.md) — the conversion syntax, files and standard output, the
  stream wrappers, the adapters, and the input dispatchers.
- [json.md](json.md) — `EncodeJson` and `DecodeJson`.
- [control.md](control.md) — `Pipe`, `Call`, `Use`, `ConvertTo`, `Box`, and `ReturnInput`.
- [extensions.md](extensions.md) — the checksum and WebSocket extension crates.
- [contexts-and-namespace.md](contexts-and-namespace.md) — the full route table of
  `HypershellNamespace`, the error aggregate, the bundles, the two contexts, and the prelude.
- [macro.md](macro.md) — the rewriting rules of `hypershell!` and its edges.

## Public material derived from this

Rustdoc for every public item. The source carries no doc comments, so the crates' docs.rs pages list
items without explanation; the entries here are written to be condensed into them.
