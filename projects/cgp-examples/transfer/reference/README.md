# `transfer` reference

This directory documents every public item in the `transfer` crate, grouped by family, with one
document per family following the entry template in
[../../../AGENTS.md](../../../AGENTS.md#reference-entries). The tables below list every item so a
reader can find one by what it is, see where it is wired, and know which module to import it from.
Read the [architecture](../architecture/README.md) first for how the families fit together.

## Components and abstract types

Every component is defined with `#[cgp_component]` or `#[cgp_type]`, so each also has a provider
trait and a `…Component` wiring key, and each registers a path in `DefaultNamespace`.

| Item | Provider trait | Path | Bound in | Module |
|---|---|---|---|---|
| [`HasUserIdType`](domain-types.md#hasuseridtype) | `UserIdTypeProvider` | `@app.auth.types` | `MockNamespace`, to `String` | `interfaces` |
| [`HasPasswordType`](domain-types.md#haspasswordtype) | `PasswordTypeProvider` | `@app.auth.types` | `MockNamespace`, to `String` | `interfaces` |
| [`HasHashedPasswordType`](domain-types.md#hashashedpasswordtype) | `HashedPasswordTypeProvider` | `@app.auth.types` | `MockNamespace`, to `String` | `interfaces` |
| [`HasQuantityType`](domain-types.md#hasquantitytype) | `QuantityTypeProvider` | `@app.finance.types` | `MockNamespace`, to `u64` | `interfaces` |
| [`HasCurrencyType`](domain-types.md#hascurrencytype) | `CurrencyTypeProvider` | `@app.finance.types` | `MockNamespace`, to `DemoCurrency` | `interfaces` |
| [`CanHandleApi<Api>`](components.md#canhandleapi) | `ApiHandler` | `@app.api` | `MockApp`, per endpoint | `interfaces` |
| [`CanRaiseHttpError<Code, Detail>`](components.md#canraisehttperror) | `HttpErrorRaiser` | `@app.error` | `MockNamespace`, `String` details only | `interfaces` |
| [`CanCheckPassword`](components.md#cancheckpassword) | `PasswordChecker` | `@app.auth` | `MockNamespace`, by `#[default_impl]` | `interfaces` |
| [`CanQueryUserHashedPassword`](components.md#canqueryuserhashedpassword) | `UserHashedPasswordQuerier` | `@app.auth` | `MockNamespace`, by `#[default_impl]` | `interfaces` |
| [`CanQueryUserBalance`](components.md#canqueryuserbalance) | `UserBalanceQuerier` | `@app.finance` | `MockNamespace`, by `#[default_impl]` | `interfaces` |
| [`CanTransferMoney`](components.md#cantransfermoney) | `MoneyTransferrer` | `@app.finance` | `MockApp` | `interfaces` |

The two endpoint markers, `QueryBalanceApi` and `TransferApi`, and the four status markers,
`ErrUnauthorized`, `ErrBadRequest`, `ErrNotFound`, and `ErrInternal`, are documented with the
component that takes them.

## Providers

Each provider implements one component, except `UseMockedApp`, which implements four. The last column
is what the provider requires of the context, and so what a context must also wire for it.

| Provider | Implements | Wired for | Requires of the context |
|---|---|---|---|
| [`HandleQueryBalance<Request>`](api-handlers.md#handlequerybalance) | `ApiHandler` | `QueryBalanceApi` | `CanQueryUserBalance`, `CanRaiseHttpError<ErrUnauthorized, String>` |
| [`HandleTransfer<Request>`](api-handlers.md#handletransfer) | `ApiHandler` | `TransferApi` | `CanTransferMoney`, `CanRaiseHttpError<ErrUnauthorized, String>` |
| [`HandleFromRequest<Request, InHandler>`](wrappers.md#handlefromrequest) | `ApiHandler` | both endpoints, outermost | the inner handler's |
| [`HandleFromResponse<Response, InHandler>`](wrappers.md#handlefromresponse) | `ApiHandler` | nothing | the inner handler's |
| [`ResponseToJson<InHandler>`](wrappers.md#responsetojson) | `ApiHandler` | `QueryBalanceApi` | the inner handler's |
| [`UseBasicAuth<InHandler>`](wrappers.md#usebasicauth) | `ApiHandler` | both endpoints | `CanQueryUserHashedPassword`, `CanCheckPassword` |
| [`NoTransferToSelf<InHandler>`](wrappers.md#notransfertoself) | `MoneyTransferrer` | `MockApp`, around `UseMockedApp` | `CanRaiseHttpError<ErrBadRequest, String>` |
| [`DisplayHttpError`](error-providers.md#displayhttperror) | `HttpErrorRaiser` | `String` details | `HasErrorType<Error = AppError>` |
| [`HandleHttpErrorWithAnyhow`](error-providers.md#handlehttperrorwithanyhow) | `HttpErrorRaiser` | nothing | `HasErrorType<Error = AppError>` |
| [`UseMockedApp`](mock-backend.md#usemockedapp) | the four backend components | all four | the `user_passwords` and `user_balances` fields, and error raising |

## Other items

The rest are ordinary Rust items: the types the configuration plugs in, the traits of the HTTP layer,
the request getters, and the wiring itself.

| Item | Kind | Module |
|---|---|---|
| [`HasLoggedInUser`, `HasLoggedInUserMut`](api-handlers.md#the-request-getters) | `#[cgp_auto_getter]` traits | `interfaces` |
| [`HasBasicAuthHeader`, `HasQueryBalanceFields`, `HasTransferMoneyFields`](api-handlers.md#the-request-getters) | `#[cgp_auto_getter]` traits | `providers` |
| [`QueryBalanceResponse<App>`](api-handlers.md#querybalanceresponse) | response struct | `providers` |
| [`IsStatusCode`](error-providers.md#isstatuscode) | trait | `providers` |
| [`AppError`](error-providers.md#apperror) | struct | `types` |
| [`DemoCurrency`](http-layer.md#democurrency) | enum | `types` |
| [the request types](http-layer.md#the-request-types) | structs and type aliases | `types` |
| [`CanHandleApiSend<Api>`](http-layer.md#canhandleapisend) | trait | `interfaces` |
| [`CanAddRoute`, `GetMethod`, `PostMethod`](http-layer.md#canaddroute) | trait and markers | `providers` |
| [`CanAddMainApiRoutes`](http-layer.md#canaddmainapiroutes) | trait | `providers` |
| [`handle_api_error`](http-layer.md#handle_api_error) | function | `providers` |
| [`CanAddApiRoutes`](http-layer.md#canaddapiroutes) | trait | `contexts` |
| [`MockNamespace`](wiring.md#mocknamespace), [`DefaultApiHandlers`](wiring.md#defaultapihandlers) | namespaces | `namespaces` |
| [`MockApp`](wiring.md#mockapp) | context | `contexts` |

Every module re-exports its files with glob imports, so an item is imported from its module's root,
such as `cgp_example_transfer::providers::UseBasicAuth`.

## The catalog

- [domain-types.md](domain-types.md) — the five abstract types and their bounds.
- [components.md](components.md) — the six components and the marker types they take.
- [api-handlers.md](api-handlers.md) — the two endpoint handlers, the balance response, and the
  request getters.
- [wrappers.md](wrappers.md) — the five higher-order providers.
- [error-providers.md](error-providers.md) — `IsStatusCode`, the two error providers, and `AppError`.
- [mock-backend.md](mock-backend.md) — `UseMockedApp` and its four impls.
- [wiring.md](wiring.md) — `MockNamespace`, `DefaultApiHandlers`, and `MockApp`.
- [http-layer.md](http-layer.md) — `CanHandleApiSend`, the routing traits, the request types, and
  `DemoCurrency`.

## Public material derived from this

The crate's rustdoc, which the source does not yet carry beyond a few doc comments, and the item
descriptions in the crate's own README.
