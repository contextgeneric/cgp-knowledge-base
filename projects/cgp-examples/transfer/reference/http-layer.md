# HTTP layer

The HTTP layer is everything that connects the components to Axum: the request types the extractors
produce, the currency type they deserialize, the trait that recovers a `Send` future, and the routing
traits that mount the endpoints. None of it is a CGP component; it is ordinary Rust that reaches the
components through their consumer traits. The pattern behind `CanHandleApiSend` is
[recovering `Send` bounds](../../../../cgp/concepts/send-bounds.md).

## `CanHandleApiSend`

`CanHandleApiSend<Api>` restates `CanHandleApi<Api>` with a future that is `Send`, so the routing
layer can hand it to Axum's multi-threaded runtime.

### Definition

```rust
pub trait CanHandleApiSend<Api>:
    CanHandleApi<Api, Request: Send, Response: Send> + Send + Sync
{
    fn handle_api_send(
        &self,
        _api: PhantomData<Api>,
        request: Self::Request,
    ) -> impl Future<Output = Result<Self::Response, Self::Error>> + Send;
}

impl CanHandleApiSend<QueryBalanceApi> for MockApp { ... }

impl CanHandleApiSend<TransferApi> for MockApp { ... }
```

### Behavior

Each impl forwards to `self.handle_api(api, request).await`. The impls are written per endpoint on the
concrete `MockApp` because only there is the awaited future a concrete type the compiler can check for
`Send`; a single blanket impl over every context fails to prove it. The trait is declared in
`interfaces/api.rs` and implemented in `contexts/app.rs`, and a new endpoint needs a new impl; see
[adding an endpoint](../guides/adding-an-endpoint.md).

### Context dependencies

`CanHandleApi<Api>` with `Send` request and response types, and a `Send + Sync` context.

## `CanAddRoute`

`CanAddRoute<App, Api, Method>` adds one endpoint to an Axum router, for one HTTP method.

### Definition

```rust
pub struct GetMethod;

pub struct PostMethod;

pub trait CanAddRoute<App, Api, Method> {
    fn add_route(self, _tag: PhantomData<(Api, Method)>, path: &str) -> Self;
}

impl<App, Api> CanAddRoute<App, Api, GetMethod> for Router<Arc<App>>
where
    App: 'static + HasErrorType<Error = AppError> + CanHandleApiSend<Api>,
    App::Request: 'static + FromRequestParts<Arc<App>>,
    App::Response: 'static + IntoResponse,
{ ... }

impl<App, Api> CanAddRoute<App, Api, PostMethod> for Router<Arc<App>>
where
    App: 'static + HasErrorType<Error = AppError> + CanHandleApiSend<Api>,
    App::Request: 'static + FromRequestParts<Arc<App>>,
    App::Response: 'static + IntoResponse,
{ ... }
```

### Behavior

Each impl mounts a closure on `path` with `get` or `post`. The closure extracts the shared context and
the endpoint's request, calls `handle_api_send`, and maps an error through `handle_api_error`. The two
impls differ only in the Axum method router they call.

The request must implement `FromRequestParts`, not `FromRequest`, so an endpoint's request can be built
only from the URI and headers, never from a body; the transfer endpoint takes its arguments from the
query string for that reason. The context's error must be `AppError`, so the routes serve only a
deployment that wires that error type.

### Context dependencies

`CanHandleApiSend<Api>` and `HasErrorType<Error = AppError>` on `App`.

### Known issues

Requests cannot have bodies; see [issues.md](../issues.md#missing-features).

## `CanAddMainApiRoutes`

`CanAddMainApiRoutes<App>` mounts the whole service in one call.

### Definition

```rust
pub trait CanAddMainApiRoutes<App> {
    fn add_main_api_routes(self) -> Self;
}

impl<App> CanAddMainApiRoutes<App> for Router<Arc<App>>
where
    Self: CanAddRoute<App, QueryBalanceApi, GetMethod> + CanAddRoute<App, TransferApi, PostMethod>,
{ ... }
```

### Behavior

It adds `GET /balance` for `QueryBalanceApi` and `POST /transfer` for `TransferApi`. The paths and
methods are fixed here rather than in the wiring, so adding an endpoint means editing this impl.

### Context dependencies

Those of the two `CanAddRoute` impls.

## `handle_api_error`

`handle_api_error` turns a raised `AppError` into the response Axum sends.

### Definition

```rust
pub fn handle_api_error(err: AppError) -> (StatusCode, String) { ... }
```

### Behavior

It returns the error's status and the detail's `Display` text, so the response body is exactly the
message the raising provider formatted.

### Context dependencies

None.

## `CanAddApiRoutes`

`CanAddApiRoutes` is a trait alias binding `CanAddMainApiRoutes` to `MockApp`.

### Definition

```rust
pub trait CanAddApiRoutes: CanAddMainApiRoutes<MockApp> {}

impl CanAddApiRoutes for Router<Arc<MockApp>> {}
```

### Behavior

Its doc comment says it exists so the binary can mount the service on a `Router<Arc<MockApp>>`, but
the binary imports `CanAddMainApiRoutes` directly, and nothing names `CanAddApiRoutes`.

### Context dependencies

None.

### Known issues

Unused; see [issues.md](../issues.md#housekeeping).

## The request types

The request types come in pairs per endpoint: a raw tuple that Axum extracts, and a domain struct the
endpoint handler reads through its getters.

### Definition

```rust
pub type AxumQueryBalanceRequest = (
    Query<QueryBalanceQuery>,
    Option<TypedHeader<Authorization<Basic>>>,
);

#[derive(Deserialize)]
pub struct QueryBalanceQuery {
    pub currency: DemoCurrency,
}

#[derive(HasField)]
pub struct QueryBalanceRequest {
    pub currency: DemoCurrency,
    pub basic_auth_header: Option<(String, String)>,
    pub logged_in_user: Option<String>,
}

impl From<AxumQueryBalanceRequest> for QueryBalanceRequest { ... }

pub type AxumTransferRequest = (
    Query<TransferQuery>,
    Option<TypedHeader<Authorization<Basic>>>,
);

#[derive(Deserialize)]
pub struct TransferQuery {
    pub currency: DemoCurrency,
    pub recipient: String,
    pub quantity: u64,
}

#[derive(HasField)]
pub struct TransferRequest {
    pub currency: DemoCurrency,
    pub recipient: String,
    pub quantity: u64,
    pub basic_auth_header: Option<(String, String)>,
    pub logged_in_user: Option<String>,
}

impl From<AxumTransferRequest> for TransferRequest { ... }
```

### Behavior

The raw tuples implement `FromRequestParts` through Axum's tuple and `Option` extractors: the query
string must deserialize, and the `Authorization: Basic` header is optional. Each `From` impl copies
the query fields, turns the header into a `(user, password)` pair, and sets `logged_in_user` to
`None` for `UseBasicAuth` to fill. The domain structs derive `HasField`, which is what implements the
[request getters](api-handlers.md#the-request-getters) for them. They name `String`, `u64`, and
`DemoCurrency` directly, so they fit only a context whose abstract types are those.

### Context dependencies

None; they are plain data.

## `DemoCurrency`

`DemoCurrency` is the concrete currency the mock configuration wires.

### Definition

```rust
#[derive(PartialOrd, Ord, PartialEq, Eq, Clone, Deserialize)]
pub enum DemoCurrency {
    EUR,
    USD,
}

impl Display for DemoCurrency { ... }
```

### Behavior

It deserializes from the query-string values `EUR` and `USD`, and any other value is rejected by
Axum's extractor with a `400`. `Ord` and `Clone` let the backend key its balance map by it, and
`Display` satisfies the bound on `HasCurrencyType`.

### Context dependencies

None.

## The Axum routing traits

The binary uses the routing traits in three lines, which is the whole of the service's startup:

```rust
let app = Arc::new(MockApp::new_with_dummy_data());

let router = <Router<Arc<MockApp>>>::new()
    .add_main_api_routes()
    .with_state(app);
```

It then binds `0.0.0.0:8080` and calls `axum::serve`, unwrapping both, so a busy port panics. The
error path runs from a provider's `raise_http_error` to `handle_api_error` inside the route closure;
[error design](../architecture/error-design.md#where-the-status-reaches-the-client) follows it end to
end.

## Source

- [`interfaces/api.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/interfaces/api.rs)
  — `CanHandleApiSend`.
- [`contexts/app.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/contexts/app.rs)
  — the `CanHandleApiSend` impls and `CanAddApiRoutes`.
- [`providers/axum/routes.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/axum/routes.rs)
  — the method markers, `CanAddRoute`, `CanAddMainApiRoutes`, and `handle_api_error`.
- [`types/requests/`](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/transfer/src/types/requests)
  — the request types.
- [`types/currency.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/types/currency.rs)
  — `DemoCurrency`.
- [`bin/server.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/bin/server.rs)
  — the binary.

## Public material derived from this

Section 8, "Serving over HTTP", of the crate's own README.
