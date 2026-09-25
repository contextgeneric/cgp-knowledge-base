# Issues

This document records the open problems in Hypershell's `v0.8.0` branch, found while documenting it
and each confirmed by a probe unless it says otherwise. They are grouped as defects, missing
features, and housekeeping. Per [../AGENTS.md](../AGENTS.md#a-project-section-documents-its-project-in-depth),
none has been fixed in the project's source; each is a separate change for the Hypershell repository,
and an entry is removed in the same change that fixes it.

## Defects

### `ConvertTo` never resolves

`ConvertTo<T>` is routed to `Promote<HandleConvert>`, but `HandleConvert` implements only `Computer`,
and `Promote`'s `Handler` impl requires an `AsyncComputer`. Every use fails to compile:

```rust
check_components! {
    #[check_trait(CheckHypershellCli)]
    HypershellCli {
        HandlerComponent: (ConvertTo<String>, &'static str),
    }
}
```

`cargo cgp check` reports a `[CGP-E111]` root cause, "the provider trait `AsyncComputer` is not
implemented for `HandleConvert`". The fix is to wire the syntax to
`Promote<PromoteAsync<HandleConvert>>`, where `PromoteAsync` lifts the `Computer` to an
`AsyncComputer` and `Promote` lifts that to a `Handler`. A probe ran that provider through
`Use<Promote<PromoteAsync<HandleConvert>>, ConvertTo<String>>` and converted a `&str` to a `String`.
See [control](reference/control.md#convertto-and-handleconvert).

### `StreamingExec` ignores the exit status and standard error

`HandleStreamingExec` returns the child's standard output and drops the child, so the exit status is
never read, and standard error is piped but never read. A failing command yields success:

```rust
type Program = hypershell! {
    StreamingExec<StaticArg<"sh">, WithStaticArgs["-c", "echo out; echo err >&2; exit 3"]>
    | StreamToString
};
```

This program returns `Ok("out\n")`. The stderr pipe closes when the handler returns, so a command
writing a megabyte to stderr completed without blocking, and the output was lost. `SimpleExec` does
check the status and reports stderr. See [execution](reference/execution.md#streamingexec-and-handlestreamingexec).

### `StreamingHttpRequest` does not follow redirects

A streaming request to a URL that answers with a redirect returns the redirect as an
`ErrorResponse`, while a simple request to the same URL follows it:

```rust
type Simple = hypershell! {
    SimpleHttpRequest<GetMethod, StaticArg<"https://nixos.org/manual/nixpkgs/unstable">, WithHeaders[]>
};
type Streaming = hypershell! {
    StreamingHttpRequest<GetMethod, StaticArg<"https://nixos.org/manual/nixpkgs/unstable">, WithHeaders[]>
    | StreamToStdout
};
```

On `HypershellHttp`, `Simple` returned the 2.8 MB page and `Streaming` failed with the 301 response.
The cause is the body. The streaming pipeline always sends its input through `StreamToBody`, which
builds a `reqwest::Body::wrap_stream`, even when the input is an empty `Vec<u8>`. The locked
`reqwest` 0.12.28 follows redirects with `tower-http`'s `FollowRedirect`, which resends the request
only with a clone of its body. A streamed body cannot be cloned, so the redirect response is returned
unless the redirect itself discards the body, as a 303 does, or a 301 or 302 answering a POST. The
simple request's `Vec<u8>` body is reusable, which is why it follows. The mechanism was read from the
two crates' source, and the probe below confirms the consequence.

The defect makes the `parallel_compare` and `compare_and_branch` examples fail, since their second URL
lacks the trailing slash. The fix is to send a byte-buffer input as a buffered body instead of a
stream. A probe ran the streaming request's inner providers directly on an empty `Vec<u8>`, skipping
the input dispatcher and `StreamToBody`, and the request followed the redirect and returned the page:

```rust
type Buffered = Pipe<Product![
    Use<
        PipeHandlers<Product![HandleStreamingHttpRequest, WrapFuturesAsyncRead]>,
        StreamingHttpRequest<GetMethod, Url, WithHeaders<Nil>>,
    >,
    ToTokioAsyncRead,
    StreamToBytes,
]>;
```

In the library, that means replacing the reqwest bundle's single `StreamingHttpRequest` entry with
entries keyed per input, since a table cannot key one syntax both on its own and per input. The
`Vec<u8>` and `String` entries would omit `HandleToTokioAsyncRead` and `StreamToBody`, and the reader
entries would keep them. A streamed input still could not follow a redirect. See
[HTTP](reference/http.md#streaminghttprequest-and-handlestreaminghttprequest).

### The WebSocket handler panics on a failed connection

`HandleWebsocket` calls `unwrap()` on `connect_async`, so a refused connection panics instead of
raising `tungstenite::Error`:

```rust
type Program = hypershell! { WebSocket<StaticArg<"ws://127.0.0.1:1/">, ()> | StreamToStdout };
```

Run on a context that routes `WebSocket` and its error, as `bluesky_websocket` does, this panicked
at `websocket.rs:37` with `called Result::unwrap() on an Err value: Io(… ConnectionRefused …)`. See
[extensions](reference/extensions.md#websocket-and-handlewebsocket).

### PUT and DELETE are implemented but unrouted

`ExtractReqwestMethod` implements the method extractor for `PutMethod` and `DeleteMethod`, but
neither `HypershellReqwestProvider` nor `HypershellNamespace` routes them:

```rust
type Program = hypershell! {
    SimpleHttpRequest<PutMethod, StaticArg<"http://127.0.0.1:1/">, WithHeaders[]>
};
```

A check on `HypershellHttp` fails with a `[CGP-E107]` root cause naming the missing
`@hypershell.core.MethodArgExtractorComponent.PutMethod` entry. Adding both markers to the bundle's
and the namespace's method lists fixes it. See [HTTP](reference/http.md).

### `StreamToLines` is unusable

`StreamToLines` has a provider, `HandleStreamToLines`, but no bundle entry and no route, so
`StreamingExec<…> | StreamToLines` fails with a `[CGP-E107]` root cause naming
`@cgp.extra.handler.HandlerComponent.StreamToLines.…`. Routing it would not be enough: the provider
returns a `Box<dyn Stream<…>>` without `Unpin`, which does not implement `Stream` itself and carries
no wrapper type, so no later stage could consume it. See
[streams and I/O](reference/streams-and-io.md#the-conversion-syntax).

## Missing features

### Existing syntax cannot be reinterpreted by inheriting the namespace

`HypershellNamespace` binds every syntax path to a bundle, so neither a context that joins it nor a
namespace that inherits it can route one syntax to a different provider. An entry for `SimpleExec`
beside `namespace HypershellNamespace;` fails with `[CGP-E005]`, "`App` cannot wire
`@cgp.extra.handler.HandlerComponent.SimpleExec.*` that is already set through
`HypershellNamespace`". This undercuts the design's claim that a context can change how a syntax
behaves. It matters most for `CoreExec` and `CoreHttpRequest`, which exist so one entry can change how
every command runs or every request is sent. The workarounds, `Use` in the program or a namespace
that restates the routes, are in [extending the language](guides/extending-the-language.md#replace-the-interpretation-of-existing-syntax).

The restriction is CGP's rule rather than Hypershell's: a namespace entry, once bound, cannot be
overridden, so a default and an override cannot share a path; see the
[namespace override conflict](../../cgp/errors/wiring/namespace-override-conflict.md). The pattern the
[namespaces guide](../../cgp/guides/namespaces-and-prefixes.md) recommends is a base namespace that
describes the structure and leaves the varying paths unbound, with each inheriting namespace binding
them as one configuration. Applied here, `HypershellNamespace` would split into a base that binds
every syntax meant to stay fixed, and a default configuration that binds the rest. A custom
configuration would inherit the base and bind every varying syntax itself, including those it does
not change. Which syntax should vary is not decided.

### `StreamToBytes` and `StreamToString` accept only Tokio readers

The two conversions have no input dispatcher, so they cannot follow `StreamingHttpRequest` or
`WebSocket`, whose output is a futures reader. `StreamingHttpRequest<…> | StreamToString` fails to
compile, and the workaround, `ToTokioAsyncRead`, is not in the prelude. Wiring both behind
`HandleToTokioAsyncRead`, as `StreamToStdout` is, would remove the need for it. See
[streams and I/O](reference/streams-and-io.md#the-conversion-syntax).

### The WebSocket handler ignores its parameters and `String` input

`WebSocket<Url, Params>` ignores `Params`, so a program cannot set headers or subprotocols, and every
example passes `()`. The bundle wires `Vec<u8>` and the two reader wrappers as inputs but not
`String`, which every other streaming stage accepts.

### Defined but unrouted providers

Three providers are public but routed nowhere, and no example uses them:

- **`ExtractUrlFieldArg`** — reads a pre-parsed `Url` from a field, as an alternative to parsing a
  string.
- **`ExtractMethodFieldArg`** — reads a `reqwest::Method` from a field.
- **`TokioToFuturesAsyncRead`** — converts a Tokio reader to a futures reader.

Each is either a missing route or dead code; the source does not say which.

### The `hypershell!` macro

The macro works for every program in the repository, but four edges were confirmed by probes; see
[the macro reference](reference/macro.md#known-issues):

- **The expansion is unhygienic.** It emits `Pipe`, `Product!`, and `Symbol!` unqualified, so it fails
  without the prelude in scope. Emitting paths through the Hypershell crates would fix it.
- **An unbalanced `<` panics the macro** instead of producing a spanned compile error.
- **`|` splits at the token level**, so `WithArgs[a, b | c]` becomes one pipeline rather than two
  elements.
- **A `->` inside the program is misparsed**, since any `>` closes an angle group.

### No wiring checks and no rustdoc

Nothing in the repository uses `check_components!`, so a syntax that has a provider but no route goes
unnoticed; see [testing.md](testing.md#what-is-not-exercised). The
source has no doc comments, so the crates' docs.rs pages list items with no explanation.

## Housekeeping

- **Stale comments in five examples.** `hello_name.rs`, `github_issues.rs`, `bluesky.rs`,
  `bluesky_websocket.rs`, and `http_checksum_native.rs` open with comments describing
  `HypershellPreset`, `MyAppPreset`, `TungsteniteHandlerPreset`, or `#[cgp_inherit]`, all removed.
  The code beneath each uses namespaces. The comments will be read as current by anyone quoting the
  examples.
- **The repository README is stale.** Its install snippet pins `cgp = "0.4.1"` and
  `reqwest = "0.11"`, it describes the assembly crate as defining "presets", and it defers to the
  announcement post, whose wiring code is several breaking releases old.
- **The branches diverge from the published crate.** The crates.io release, 0.1.0 (tag `v0.1.0`),
  was built against `cgp` 0.4.1, `main` tracks `cgp` 0.7.0, and `v0.8.0` tracks `cgp` 0.8.0-alpha.
  All three carry version 0.1.0.
- **The workspace builds only beside `../cgp`.** The root manifest patches `cgp` and
  `cgp-error-anyhow` to local paths, and its `repository` field points at the `cgp` repository
  rather than Hypershell's.
- **Providers use the explicit form.** Almost every provider names the context and lists `Context:`
  bounds, and none uses [`#[uses]`](../../cgp/reference/attributes/uses.md). This is the form the
  [declaring-dependencies](../../cgp/guides/declaring-dependencies.md) guide replaces.
- **The HTTP client is read through `#[cgp_getter]`.** Every field read except one names its field in
  the program (`FieldArg<Tag>`, `FieldArgs<Tag>`), so an
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md) argument cannot express it. The
  exception is `HasReqwestClient`, a `#[cgp_getter]` component that `HypershellNamespace` wires to
  `UseField<Symbol!("http_client")>` for every context. The
  [reading-context-fields](../../cgp/guides/reading-context-fields.md) guide reserves `#[cgp_getter]`
  for choosing the field per context, which nothing in the repository does, so an
  `#[implicit] http_client: &Client` argument on `HandleCoreHttpRequest` would be the default form. It
  would also remove the option of supplying the client some other way. Which to keep is a design
  decision.
- **`HandlePipe` uses a legacy `UseDelegate` table.** A probe confirmed that `open` accepts its
  bounded key, `<Handlers: WrapCall> Pipe<Handlers>`, so it can move to the form the
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md) guide prescribes.
- **Six components carry an unused `#[derive_delegate(UseDelegate<…>)]`.** The four extractors and
  the two updaters generate a legacy dispatcher that nothing uses, since every bundle dispatches with
  `open`. Removing them is breaking for a downstream user who wires a `UseDelegate` table.
- **`ExtractArgs` recurses through the wiring.** Its tail bound is written as
  `Self: CommandUpdater<…>`, which `#[cgp_impl]` expands to a bound on the context, so `cargo cgp expand`
  shows each tail of a `WithArgs` list resolved through the context's routes rather than by
  `ExtractArgs` itself. `JoinStringArgs`, `JoinExtractArgs`, and `UpdateRequestHeaders` name
  themselves instead. The recursion works only because the namespace routes every `WithArgs<Args>`
  to the same provider; naming `ExtractArgs` in the bound, as the other three do, would make it direct.
- **Two bundles open components they never wire.** `HypershellTokioProvider` opens the string and
  URL extractors, and `HypershellReqwestProvider` the command and URL extractors, with no entries for
  them. The namespace routes none of those paths to either bundle, so the extra `open`s are inert.
- **`ReturnInput` duplicates CGP's.** `hypershell_components::providers::ReturnInput` has the same
  name and `Handler` bound as `cgp::extra::handler::ReturnInput`.
- **A vestigial higher-ranked bound.** `HandleSimpleExec` requires `for<'a> CanRaiseError<ExecOutputError>`,
  and nothing uses `'a`.
- **Unneeded recursion limits.** Four examples and the test crate set `#![recursion_limit]`, which the
  pinned toolchain does not need.
- **Two unclear or mistyped strings.** The compare namespace's comment says `Compare` is "much slower"
  unboxed without saying whether it means compile time or run time, and `compare_and_branch` prints
  "the checksums are equals".
- **The HTTP error message is the whole response.** `ErrorResponse` derives `Debug` and is raised
  through `DebugAnyhowError`, so its message is the `Debug` of the `reqwest::Response`, every header
  included.

## Public material derived from this

The limitations section of the planned trade-offs page of the
[Hypershell deep dive](../../website/deep-dives/hypershell.md), and the "Source-code changes needed"
list in that plan.
