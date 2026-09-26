# Wiring

The wiring is the two tables in `namespaces` and the one context in `contexts`, which together choose
a provider for every component. How the three divide the work is explained in
[namespace organization](../architecture/namespace-organization.md); this document records each
table's entries.

## `MockNamespace`

`MockNamespace` is the namespace that binds the mock configuration: the concrete types, the error
provider, and, through `#[default_impl]`, three of the backend's four impls.

### Definition

```rust
cgp_namespace! {
    new MockNamespace: DefaultNamespace {
        @cgp.core.error.ErrorTypeProviderComponent:
            UseType<AppError>,

        @app.error.HttpErrorRaiserComponent.<Code> Code.String:
            DisplayHttpError,

        @app.auth.types.{
            UserIdTypeProviderComponent,
            PasswordTypeProviderComponent,
            HashedPasswordTypeProviderComponent,
        }:
            UseType<String>,
        @app.finance.types.QuantityTypeProviderComponent:
            UseType<u64>,
        @app.finance.types.CurrencyTypeProviderComponent:
            UseType<DemoCurrency>,
    }
}
```

### Behavior

It inherits every path `DefaultNamespace` routes, including the `#[prefix]` paths of the crate's
components and CGP's own error paths. Beyond the body above, the `#[default_impl]` attributes in
[the mock backend](mock-backend.md) bind three more paths to `UseMockedApp`:

| Path | Provider |
|---|---|
| `@app.auth.UserHashedPasswordQuerierComponent` | `UseMockedApp` |
| `@app.auth.PasswordCheckerComponent` | `UseMockedApp` |
| `@app.finance.UserBalanceQuerierComponent` | `UseMockedApp` |

It leaves `@app.finance.MoneyTransferrerComponent` and `@app.api.ApiHandlerComponent` unbound, so a
context that joins it must supply both. A comment in `namespaces/mock.rs` says the body holds "the
pieces that have no `#[cgp_impl]` block of their own"; `DisplayHttpError` does have one, and is in the
body because it is generic; see [issues.md](../issues.md#housekeeping).

### Context dependencies

A context joining it must supply the transfer and API paths, and the two fields the backend reads.

## `DefaultApiHandlers`

`DefaultApiHandlers` is the table of endpoint pipelines, keyed by endpoint marker.

### Definition

```rust
cgp_namespace! {
    new DefaultApiHandlers {
        QueryBalanceApi:
            HandleFromRequest<
                AxumQueryBalanceRequest,
                ResponseToJson<UseBasicAuth<HandleQueryBalance<QueryBalanceRequest>>>,
            >,
        TransferApi:
            HandleFromRequest<
                AxumTransferRequest,
                UseBasicAuth<HandleTransfer<TransferRequest>>,
            >,
    }
}
```

### Behavior

It has no parent and is never joined with `namespace`; a context reads it with a `for` loop. Each
pipeline reads outside in as the stages a request passes through, traced in
[the request lifecycle](../architecture/request-lifecycle.md). Because the pipelines name the Axum
request types, the table is tied to the HTTP layer, while the handlers inside them are not.

### Context dependencies

Every dependency of the providers in the two pipelines.

## `MockApp`

`MockApp` is the application context: two in-memory maps, and the wiring that selects every provider.

### Definition

```rust
#[derive(HasField, Default)]
pub struct MockApp {
    pub user_balances: Arc<Mutex<BTreeMap<(String, DemoCurrency), u64>>>,
    pub user_passwords: BTreeMap<String, String>,
}

impl MockApp {
    pub fn new_with_dummy_data() -> Self { ... }
}

delegate_components! {
    MockApp {
        namespace MockNamespace;

        for <Key, Value> in DefaultApiHandlers {
            @app.api.ApiHandlerComponent.Key: Value,
        }

        @app.finance.MoneyTransferrerComponent:
            NoTransferToSelf<UseMockedApp>,
    }
}

check_components! {
    MockApp
    {
        QuantityTypeProviderComponent,
        UserBalanceQuerierComponent,
        MoneyTransferrerComponent,
        ApiHandlerComponent: [
            QueryBalanceApi,
            TransferApi,
        ],
    }
}
```

### Behavior

The field types are the concrete forms of the abstract types the backend's `#[implicit]` arguments
name, which is what lets `MockApp` satisfy them: `(String, DemoCurrency)` to `u64` for balances, and
`String` to `String` for passwords. `new_with_dummy_data` seeds Alice (`wonderland`; 100 EUR, 50 USD)
and Bob (`sponge`; 200 EUR, 150 USD); `Default` gives two empty maps.

The wiring joins `MockNamespace`, copies both `DefaultApiHandlers` entries onto the `ApiHandler`
dispatch path, and binds the transfer to `NoTransferToSelf<UseMockedApp>`. The check asserts the four
listed components, the handler once per endpoint; [testing.md](../testing.md) records what that
covers transitively.

The same file implements `CanHandleApiSend` for each endpoint and declares `CanAddApiRoutes`; both are
documented with the [HTTP layer](http-layer.md).

### Context dependencies

None; it is the context.

## Source

- [`namespaces/mock.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/namespaces/mock.rs)
  — `MockNamespace`.
- [`namespaces/api_handlers.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/namespaces/api_handlers.rs)
  — `DefaultApiHandlers`.
- [`contexts/app.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/contexts/app.rs)
  — `MockApp`, its wiring, and its check.

## Public material derived from this

Section 7, "Assembling the app with namespaces", of the crate's own README.
