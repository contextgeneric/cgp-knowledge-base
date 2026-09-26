# HTTP

The HTTP family sends requests with `reqwest`. As with processes, a simple and a streaming syntax
differ in whether the response is buffered or streamed, and both delegate the request itself to an
internal `CoreHttpRequest` step. Methods, headers, and the client come from their own components. The
providers are in `hypershell-reqwest-components`; the syntax types and the method extractor are in
`hypershell-components`.

## `SimpleHttpRequest` and `HandleSimpleHttpRequest`

`SimpleHttpRequest<Method, Url, Params>` sends one request with the input as its body and produces
the whole response body as bytes.

### Definition

```rust
pub struct SimpleHttpRequest<Method, Url, Params>(pub PhantomData<(Method, Url, Params)>);

#[cgp_impl(new HandleSimpleHttpRequest)]
impl<Context, MethodArg, UrlArg, Headers, Input>
    Handler<SimpleHttpRequest<MethodArg, UrlArg, Headers>, Input> for Context
where
    Context: CanHandle<CoreHttpRequest<MethodArg, UrlArg, Headers>, Input, Output = Response>
        + CanRaiseError<reqwest::Error>
        + CanRaiseError<ErrorResponse>,
{
    type Output = Vec<u8>;

    async fn handle(
        context: &Context,
        _tag: PhantomData<SimpleHttpRequest<MethodArg, UrlArg, Headers>>,
        body: Input,
    ) -> Result<Vec<u8>, Context::Error> { ... }
}
```

### Behavior

The provider sends the request through `CoreHttpRequest`, raises `ErrorResponse` for a status
outside 2xx, and otherwise reads the body into a `Vec<u8>`. The input is the request body and must
be `Into<reqwest::Body>`, so the usual `Vec::new()` input sends an empty body even with `GetMethod`,
and `EncodeJson`'s output can feed a POST directly. Redirects are followed, per the client's policy.
The third parameter is `WithHeaders<…>` in every program in the repository.

### Context dependencies

`CanHandle<CoreHttpRequest<…>, Input>` with `Output = Response`, and raising `reqwest::Error` and
`ErrorResponse`.

## `StreamingHttpRequest` and `HandleStreamingHttpRequest`

`StreamingHttpRequest<Method, Url, Params>` sends one request with a streamed body and produces the
response body as a stream.

### Definition

```rust
pub struct StreamingHttpRequest<Method, Url, Params>(pub PhantomData<(Method, Url, Params)>);

#[cgp_impl(new HandleStreamingHttpRequest)]
impl<Context, MethodArg, UrlArg, Headers, Input>
    Handler<StreamingHttpRequest<MethodArg, UrlArg, Headers>, Input> for Context
where
    Context: CanHandle<CoreHttpRequest<MethodArg, UrlArg, Headers>, Input, Output = Response>
        + CanRaiseError<reqwest::Error>
        + CanRaiseError<ErrorResponse>,
{
    type Output = Pin<Box<dyn FutAsyncRead + Send>>;

    async fn handle(
        context: &Context,
        _tag: PhantomData<StreamingHttpRequest<MethodArg, UrlArg, Headers>>,
        body: Input,
    ) -> Result<Pin<Box<dyn FutAsyncRead + Send>>, Context::Error> { ... }
}

#[cgp_impl(new StreamToBody)]
impl<Context, Code, Input> Handler<Code, Input> for Context
where
    Context: HasErrorType,
    Input: Send + AsyncRead + 'static,
{
    type Output = Body;
    // ...
}
```

### Behavior

The reqwest bundle dispatches the syntax on its input, with one entry for byte buffers and one for
readers. A `Vec<u8>` or `String` is sent as a buffered body:

```rust
PipeHandlers<Product![
    HandleStreamingHttpRequest,   // send, check status, return the body as a futures reader
    WrapFuturesAsyncRead,         // → FuturesAsyncReadStream
]>
```

A `TokioAsyncReadStream` or `FuturesAsyncReadStream` is streamed as the body, through two more
stages in front:

```rust
PipeHandlers<Product![
    HandleToTokioAsyncRead,       // either reader → Tokio reader
    StreamToBody,                 // Tokio reader → reqwest::Body::wrap_stream
    HandleStreamingHttpRequest,
    WrapFuturesAsyncRead,
]>
```

Either way the output is a `FuturesAsyncReadStream`, the response body read as it arrives.
A non-success status raises `ErrorResponse`, and stream errors surface as `std::io::Error` from the
reader. The output is a futures reader, so `StreamToBytes` and `StreamToString` cannot follow it
directly; insert `ToTokioAsyncRead`, per [streams and I/O](streams-and-io.md).

### Known issues

A streamed body does not follow a redirect. `reqwest` follows one only when it can resend the body
or the redirect discards it, and a streamed body cannot be resent, so a reader input does not follow
a 301, 302, 307, or 308. A buffered body does: a probe sent an empty `Vec<u8>` to a URL that answers
301 and got the redirected page back. See
[issues.md](../issues.md#a-streamed-request-body-does-not-follow-redirects).

## `CoreHttpRequest` and `HandleCoreHttpRequest`

`CoreHttpRequest<Method, Url, Params>` is the internal step both HTTP syntaxes delegate to: it builds
the request from the method, URL, and header syntax, attaches the body, and sends it.

### Definition

```rust
pub struct CoreHttpRequest<Method, Url, Args>(pub PhantomData<(Method, Url, Args)>);

#[cgp_impl(new HandleCoreHttpRequest)]
impl<Context, MethodArg, UrlArg, Headers, Input>
    Handler<CoreHttpRequest<MethodArg, UrlArg, Headers>, Input> for Context
where
    Context: HasReqwestClient
        + CanExtractUrlArg<UrlArg, Url = Url>
        + CanExtractMethodArg<MethodArg, HttpMethod = Method>
        + CanUpdateRequestBuilder<Headers>
        + CanRaiseError<reqwest::Error>,
    Input: Into<Body>,
{
    type Output = Response;
    // ...
}
```

### Behavior

The provider takes the client from `HasReqwestClient`, extracts the URL and method, applies the
header syntax with `CanUpdateRequestBuilder`, sets the body, and sends. It returns the `Response`
whatever its status; the two callers check the status. It pins the URL type to `reqwest::Url` and
the method type to `reqwest::Method`, which the reqwest bundle's `UseType` entries supply.

### Context dependencies

The client getter, the URL and method extractors, the request-builder updater for the header
syntax, and raising `reqwest::Error`.

## Method markers, `CanExtractMethodArg`, and `ExtractReqwestMethod`

The method is chosen by a marker type and turned into the context's abstract method type by an
extractor.

### Definition

```rust
pub struct GetMethod;
pub struct PostMethod;
pub struct PutMethod;
pub struct DeleteMethod;

#[cgp_type]
#[prefix(@hypershell.core in DefaultNamespace)]
pub trait HasHttpMethodType {
    type HttpMethod;
}

#[cgp_component(MethodArgExtractor)]
#[prefix(@hypershell.core in DefaultNamespace)]
#[derive_delegate(UseDelegate<Arg>)]
pub trait CanExtractMethodArg<Arg>: HasHttpMethodType {
    fn extract_method_arg(&self, _phantom: PhantomData<Arg>) -> Self::HttpMethod;
}

pub struct ExtractReqwestMethod;

#[cgp_impl(ExtractReqwestMethod)]
impl<Context> MethodArgExtractor<GetMethod> for Context
where
    Context: HasHttpMethodType<HttpMethod = Method>,
{ ... }
// … one impl each for PostMethod, PutMethod, and DeleteMethod

#[cgp_impl(new ExtractMethodFieldArg)]
impl<Context, Tag> MethodArgExtractor<FieldArg<Tag>> for Context
where
    Context: HasHttpMethodType + HasField<Tag, Value = Context::HttpMethod>,
    Context::HttpMethod: Clone,
{ ... }
```

### Behavior

`ExtractReqwestMethod` maps each marker to the matching `reqwest::Method` constant, and the reqwest
bundle and the namespace route all four markers to it. `ExtractMethodFieldArg` would read a method
from a context field instead.

### Known issues

`ExtractMethodFieldArg` is routed nowhere. See [issues.md](../issues.md#defined-but-unrouted-providers).

## `WithHeaders`, `Header`, and the request-builder updater

`WithHeaders<Headers>` sets a `Product!` list of `Header<Key, Value>` entries on the request.

### Definition

```rust
pub struct WithHeaders<Headers>(pub PhantomData<Headers>);

pub struct Header<Key, Value>(pub PhantomData<(Key, Value)>);

#[cgp_component(RequestBuilderUpdater)]
#[derive_delegate(UseDelegate<Args>)]
#[prefix(@hypershell.reqwest in DefaultNamespace)]
pub trait CanUpdateRequestBuilder<Args>: HasErrorType {
    fn update_request_builder(
        &self,
        _phantom: PhantomData<Args>,
        builder: RequestBuilder,
    ) -> Result<RequestBuilder, Self::Error>;
}

#[cgp_impl(new UpdateRequestHeader)]
impl<Context, Key, Value> RequestBuilderUpdater<Header<Key, Value>> for Context
where
    Context: CanExtractStringArg<Key>
        + CanExtractStringArg<Value>
        + CanRaiseError<InvalidHeaderName>
        + CanRaiseError<InvalidHeaderValue>,
{ ... }

pub struct UpdateRequestHeaders;
// one impl for WithHeaders<Cons<Arg, Args>> recursing on the tail, one for WithHeaders<Nil>
```

### Behavior

`UpdateRequestHeaders` applies each element of the list through the context, and
`UpdateRequestHeader` extracts the key and value as strings and parses them as a header name and
value, raising either parse error. Both the key and the value are argument syntax, so a header value
may come from a `FieldArg`. `WithHeaders[]` expands to `WithHeaders<Nil>` and sets nothing.

## `HasReqwestClient`

`HasReqwestClient` is the getter the HTTP core step uses for its client.

### Definition

```rust
#[cgp_getter]
#[prefix(@hypershell.reqwest in DefaultNamespace)]
pub trait HasReqwestClient {
    fn request_client(&self) -> &Client;
}
```

### Behavior

It is a [`#[cgp_getter]`](../../../cgp/reference/macros/cgp_getter.md) component, so the field it
reads is chosen by wiring. `HypershellNamespace` wires it to `UseField<Symbol!("http_client")>`, so
a context that runs HTTP must have a `reqwest::Client` field named `http_client`. A context without
one fails with a `[CGP-E106]` "missing field `http_client`" root cause.

## `ErrorResponse`

`ErrorResponse` is the error both HTTP handlers raise for a non-success status.

### Definition

```rust
#[derive(Debug)]
pub struct ErrorResponse {
    pub response: Response,
}
```

### Behavior

It carries the whole response, so a handler of the error can read the body. The namespace raises it
with `DebugAnyhowError`, so its message is the `Debug` of the `Response`, headers included.

## Wiring

`HypershellReqwestProvider` maps the three request syntaxes, `GetMethod` and `PostMethod` under the
method extractor, `UrlEncodeArg` under the string extractor, and `WithHeaders` and `Header` under the
request-builder updater, and fixes `HttpMethod = reqwest::Method` and `Url = url::Url`.
`HypershellNamespace` routes each to the bundle, and wires `ReqwestClientGetterComponent` to
`UseField<Symbol!("http_client")>` itself. `HypershellHttp` is the ready-made context with that
field.

## Source

- [crates/hypershell-components/src/dsl/http.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/http.rs)
- [crates/hypershell-components/src/components/method_arg.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/components/method_arg.rs) and [providers/method_arg.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/providers/method_arg.rs)
- [crates/hypershell-reqwest-components/src/components/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-reqwest-components/src/components)
- [crates/hypershell-reqwest-components/src/providers/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-reqwest-components/src/providers)

## Public material derived from this

Rustdoc for the HTTP items.
