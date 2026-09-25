# Assembly

Hypershell's language is assembled from three layers of wiring: backend bundles that map syntax to
providers, a namespace that routes syntax to bundles, and contexts that join the namespace. This
document describes each layer, why it is split this way, and one lookup traced through all three.
The CGP mechanisms are [namespaces](../../../cgp/concepts/namespaces.md),
[aggregate providers](../../../cgp/concepts/aggregate-providers.md), and the `open` statement of
[`delegate_components!`](../../../cgp/reference/macros/delegate_components.md).

## Components register their own paths

**Every component a Hypershell program can reach is registered into `DefaultNamespace` under a path
prefix, with [`#[prefix]`](../../../cgp/reference/attributes/prefix.md) on its trait.** The prefix
records a route; it binds no provider. The prefixes group the components by the crate that defines
them:

| Prefix | Components | Defined in |
|---|---|---|
| `@cgp.extra.handler` | `HandlerComponent` | `cgp` |
| `@cgp.core.error` | `ErrorTypeProviderComponent`, `ErrorRaiserComponent`, `ErrorWrapperComponent` | `cgp` |
| `@hypershell.core` | `StringArgExtractorComponent`, `CommandArgExtractorComponent`, `UrlArgExtractorComponent`, `MethodArgExtractorComponent`, and the type components `CommandArgTypeProviderComponent`, `UrlTypeProviderComponent`, `HttpMethodTypeProviderComponent` | `hypershell-components` |
| `@hypershell.tokio` | `CommandUpdaterComponent` | `hypershell-tokio-components` |
| `@hypershell.reqwest` | `RequestBuilderUpdaterComponent`, `ReqwestClientGetterComponent` | `hypershell-reqwest-components` |

Because the extractor, updater, and handler components are generic over their syntax, the
[`RedirectLookup`](../../../cgp/reference/providers/redirect_lookup.md) impl behind each route
appends every type parameter to the path before looking it up. A handler lookup therefore ends in the
syntax and then the input, as in `@cgp.extra.handler.HandlerComponent.SimpleExec<…>.Vec<u8>`. That
second segment is what lets a bundle dispatch on the input; see
[streams-and-input-dispatch.md](streams-and-input-dispatch.md).

## Layer one: backend bundles

**Each backend crate publishes one aggregate provider that maps its syntax to its providers.** A
bundle is declared with `delegate_components! { new … }`, `open`s each component it serves, and
lists one `@Component.Syntax` entry per piece of syntax. This is an abridged view of the Tokio
bundle:

```rust
delegate_components! {
    new HypershellTokioProvider {
        open {
            HandlerComponent,
            StringArgExtractorComponent,
            CommandArgExtractorComponent,
            UrlArgExtractorComponent,
            CommandUpdaterComponent,
        };

        CommandArgTypeProviderComponent:
            UseType<PathBuf>,

        @HandlerComponent.<Path, Args> SimpleExec<Path, Args>:
            HandleSimpleExec,

        @HandlerComponent.<Path, Args> StreamingExec<Path, Args>:
            PipeHandlers<Product![
                HandleToTokioAsyncRead,
                HandleStreamingExec,
                WrapTokioAsyncRead,
            ]>,

        @CommandUpdaterComponent.<Args> WithArgs<Args>:
            ExtractArgs,
        // …
    }
}
```

The bundles are:

- **`HypershellBaseProvider`** (`hypershell-components`) — the control syntax (`Pipe`, `Use`,
  `ConvertTo`, `Box`), `BytesToString`, and the string, command, and URL extractors for
  `StaticArg`, `FieldArg`, and `JoinArgs`.
- **`HypershellTokioProvider`** (`hypershell-tokio-components`) — process execution, files, the stream
  conversions, `JoinArgs` for command paths, the command updaters, and `CommandArg = PathBuf`.
- **`HypershellReqwestProvider`** (`hypershell-reqwest-components`) — the HTTP syntax, the method
  extractor, `UrlEncodeArg`, the header updaters, and `Url = url::Url`, `HttpMethod = reqwest::Method`.
- **`HypershellJsonProvider`** (`hypershell-json-components`) — `EncodeJson` and `DecodeJson`.
- **`HypershellTungsteniteProvider`** (`hypershell-tungstenite-components`) — `WebSocket`, per input
  type.
- **`HypershellErrorHandler`** (`hypershell`) — the raising strategy per source error type; see
  [error-handling.md](error-handling.md).
- **`HypershellChecksumProvider`** (`hypershell-examples`) — `Checksum` and `BytesToHex`, wired from
  `hypershell-hash-components`, which ships providers but no bundle of its own.

Three smaller aggregates sit inside the bundles and are named as providers by their entries:
`HandlePipe` for `Pipe`, and the input dispatchers `HandleToTokioAsyncRead` and
`HandleToFuturesStream`.

**The bundles use `open` because `open` redirects into the bundle's own table, keyed by the bare
component name.** A bundle joins no namespace and knows nothing of the prefix its components are
registered under, so it can be reached from any namespace route and any context entry alike. The
`open` statement is documented as not combining with a joined namespace when the component carries
a `#[prefix]`. The bundle pattern avoids that restriction by keeping the `open` in a table that joins
no namespace, and leaving the prefixed routes to the layer above.

The bundles are providers, not contexts, so none is checked with `delegate_and_check_components!`.
Nothing in the repository checks them at all; see [testing.md](../testing.md).

## Layer two: the namespace

**`HypershellNamespace` routes each prefixed path to the bundle that serves it, and binds the few
components that need no bundle directly.** It inherits CGP's `DefaultNamespace`, which carries the
`#[prefix]` routes, and its body is a list of `:` entries whose keys use `[…]` groups for sets of
syntax and `{…}` groups for sets of whole path tails. This is abridged from
[`hypershell/src/namespaces/handlers.rs`](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell/src/namespaces/handlers.rs):

```rust
cgp_namespace! {
    new HypershellNamespace: DefaultNamespace {
        @cgp.core.error.ErrorTypeProviderComponent:
            UseAnyhowError,

        @cgp.core.error.ErrorRaiserComponent.[
            Error, Infallible, std::io::Error, /* … */ ErrorResponse,
        ]:
            HypershellErrorHandler,

        @hypershell.reqwest.ReqwestClientGetterComponent:
            UseField<Symbol!("http_client")>,

        @cgp.extra.handler.HandlerComponent.[
            <Path, Args> SimpleExec<Path, Args>,
            <Path, Args> StreamingExec<Path, Args>,
            // … every Tokio handler syntax
        ]:
            HypershellTokioProvider,

        @hypershell.{
            core.CommandArgExtractorComponent.[
                <Args> JoinArgs<Args>,
            ],
            tokio.CommandUpdaterComponent.[
                <Args> WithArgs<Args>,
                <Tag> FieldArgs<Tag>,
            ],
        }:
            HypershellTokioProvider,
        // … routes to the base, reqwest, and JSON bundles
    }
}
```

**Every piece of syntax is therefore listed twice: once in its bundle and once in a namespace
route.** The bundle says which provider interprets it, and the route says which bundle to ask.
Nothing connects the two lists, so a syntax a bundle handles but the namespace does not route is
unreachable from any context that joins the namespace. Two such gaps exist today, `PutMethod`/
`DeleteMethod` and `StreamToLines`; see [issues.md](../issues.md#defects).

The one binding outside any bundle worth noting is `ReqwestClientGetterComponent`, which the
namespace wires to [`UseField`](../../../cgp/reference/providers/use_field.md) over the field
`http_client`. That field name is the reason every HTTP-capable context in the repository names its
`reqwest::Client` field `http_client`.

The full route table is in [the contexts and namespace reference](../reference/contexts-and-namespace.md).

## Layer three: contexts

**A context joins the namespace with one statement and gains the whole language.** The two contexts
the `hypershell` crate provides are exactly that:

```rust
pub struct HypershellCli;

delegate_components! {
    HypershellCli {
        namespace HypershellNamespace;
    }
}

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

The two are wired identically; they differ only in their fields. Wiring is lazy, so `HypershellCli`
is wired for HTTP too, and an HTTP program fails to compile on it only because the reqwest client
getter finds no `http_client` field. A user's context follows the same pattern, adding one field per
`FieldArg` its programs read.

A context can also add or override entries next to the `namespace` statement, using the full
prefixed path. The `bluesky_websocket` example adds the WebSocket syntax and its error type this way:

```rust
delegate_components! {
    MyApp {
        namespace HypershellNamespace;

        @cgp.core.error.ErrorRaiserComponent.TungsteniteError:
            RaiseAnyhowError,

        @cgp.extra.handler.HandlerComponent.<Url, Params> WebSocket<Url, Params>:
            HypershellTungsteniteProvider,
    }
}
```

Such an entry works only for a path the namespace does not already bind, or the two impls conflict,
per the [namespace override conflict](../../../cgp/errors/wiring/namespace-override-conflict.md). And
a segment that names a type must be in scope: this entry compiles only with `ErrorRaiserComponent`
imported. An extension that several contexts share is better published as a namespace that inherits
`HypershellNamespace`, as the examples crate does with `HypershellChecksumNamespace` and
`HypershellCompareNamespace`; see [extending the language](../guides/extending-the-language.md).

## One lookup, end to end

Resolving `HypershellCli: CanHandle<SimpleExec<StaticArg<"echo">, Args>, Vec<u8>>` crosses all
three layers, and each step is a CGP rule documented elsewhere:

1. `HypershellCli` has no direct entry for `HandlerComponent`, so its `namespace` blanket forwards the
   key to `HypershellNamespace`, which inherits the `#[prefix]` route from `DefaultNamespace`. The
   delegate is a `RedirectLookup` down `@cgp.extra.handler.HandlerComponent`.
2. The redirect appends the two parameters and looks up
   `@cgp.extra.handler.HandlerComponent.SimpleExec<…>.Vec<u8>` in `HypershellCli`'s table. The
   namespace blanket forwards again, and the namespace entry for `SimpleExec` matches the prefix of
   that path, since path keys end in an open wildcard. Its delegate is `HypershellTokioProvider`.
3. `HypershellTokioProvider` answers `Handler` through its own table, where `open HandlerComponent`
   delegates to a `RedirectLookup` down the bundle's own `@HandlerComponent`.
4. That redirect looks up `@HandlerComponent.SimpleExec<…>.Vec<u8>` in the bundle and finds the
   `SimpleExec` entry: `HandleSimpleExec`.
5. `HandleSimpleExec`'s dependencies are resolved against `HypershellCli` in turn, starting with
   `CanHandle<CoreExec<…>, ()>`, which repeats the walk.

All of it is resolved by the compiler, so the call compiles to a direct call to the provider's body.
`cargo cgp check` shows the same walk as a dependency tree, with each redirect as a `[CGP-E104]` line;
see [debugging](../guides/debugging.md).

## Source

- The bundles: `providers/combined.rs` in [hypershell-components](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/providers/combined.rs), [hypershell-tokio-components](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/combined.rs), [hypershell-reqwest-components](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-reqwest-components/src/providers/combined.rs), [hypershell-json-components](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-json-components/src/providers/combined.rs), and [hypershell-tungstenite-components](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tungstenite-components/src/providers/combined.rs)
- The namespace: [crates/hypershell/src/namespaces/handlers.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell/src/namespaces/handlers.rs)
- The contexts: [crates/hypershell/src/contexts/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell/src/contexts)
- The extension namespaces: [crates/hypershell-examples/src/namespaces/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-examples/src/namespaces)

## Public material derived from this

Page 3, "Assembling the language with namespaces", of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md), which should show the one-line
`HypershellCli` early.
