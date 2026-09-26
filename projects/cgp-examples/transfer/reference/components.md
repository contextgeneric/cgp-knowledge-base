# Components

The components are the six operations of the service, each defined with
[`#[cgp_component]`](../../../../cgp/reference/macros/cgp_component.md) and registered under a path in
`DefaultNamespace`, together with the zero-sized marker types two of them take. Every component
imports the abstract types it names with [`#[use_type]`](../../../../cgp/reference/attributes/use_type.md),
and the three async ones declare their methods under
[`#[async_trait]`](../../../../cgp/reference/macros/async_trait.md).

## `CanHandleApi`

`CanHandleApi<Api>` is the component every endpoint implements, dispatched on an endpoint marker.

### Definition

```rust
#[cgp_component(ApiHandler)]
#[prefix(@app.api in DefaultNamespace)]
#[async_trait]
#[use_type(HasErrorType.Error)]
pub trait CanHandleApi<Api> {
    type Request;

    type Response;

    async fn handle_api(
        &self,
        _api: PhantomData<Api>,
        request: Self::Request,
    ) -> Result<Self::Response, Error>;
}

pub struct TransferApi;

pub struct QueryBalanceApi;
```

### Behavior

`Api` selects the provider and carries no data; the call passes `PhantomData`. Because `Request` and
`Response` are associated types, each endpoint's provider fixes its own input and output, and a
wrapper can change one of them: `HandleFromRequest` sets `Request` to the raw Axum tuple and
`ResponseToJson` sets `Response` to `Json<…>`. The provider trait is `ApiHandler`, and the wiring key
is `ApiHandlerComponent`, dispatched per marker at `@app.api.ApiHandlerComponent.<Api>`. The returned
future carries no `Send` bound, which is why the HTTP layer restates the method in
[`CanHandleApiSend`](http-layer.md#canhandleapisend).

### Context dependencies

`HasErrorType`, as a supertrait from the `#[use_type]` import.

## `CanRaiseHttpError`

`CanRaiseHttpError<Code, Detail>` builds the context's error from a status marker and a detail value.

### Definition

```rust
#[cgp_component(HttpErrorRaiser)]
#[prefix(@app.error in DefaultNamespace)]
#[use_type(HasErrorType.Error)]
pub trait CanRaiseHttpError<Code, Detail> {
    fn raise_http_error(_code: Code, detail: Detail) -> Error;
}

pub struct ErrUnauthorized;

pub struct ErrBadRequest;

pub struct ErrNotFound;

pub struct ErrInternal;
```

### Behavior

The method is an associated function, called as `Self::raise_http_error(ErrNotFound, detail)`. The
four markers name the status classes the crate uses; each implements
[`IsStatusCode`](error-providers.md#isstatuscode). No provider raises `ErrInternal`. The wiring key is
`HttpErrorRaiserComponent`, dispatched on both parameters at
`@app.error.HttpErrorRaiserComponent.<Code>.<Detail>`; see [error design](../architecture/error-design.md).

### Context dependencies

`HasErrorType`, as a supertrait.

## `CanCheckPassword`

`CanCheckPassword` compares a cleartext password with a stored one.

### Definition

```rust
#[cgp_component(PasswordChecker)]
#[prefix(@app.auth in DefaultNamespace)]
#[use_type(HasPasswordType.Password, HasHashedPasswordType.HashedPassword)]
pub trait CanCheckPassword {
    fn check_password(password: &Password, hashed_password: &HashedPassword) -> bool;
}
```

### Behavior

It is an associated function returning a plain `bool`, so a check cannot fail with an error. Its
wiring key is `PasswordCheckerComponent`, bound in `MockNamespace` to
[`UseMockedApp`](mock-backend.md#passwordchecker).

### Context dependencies

`HasPasswordType` and `HasHashedPasswordType`, as supertraits.

## `CanQueryUserHashedPassword`

`CanQueryUserHashedPassword` looks up a user's stored password.

### Definition

```rust
#[cgp_component(UserHashedPasswordQuerier)]
#[prefix(@app.auth in DefaultNamespace)]
#[async_trait]
#[use_type(HasUserIdType.UserId, HasHashedPasswordType.HashedPassword, HasErrorType.Error)]
pub trait CanQueryUserHashedPassword {
    async fn query_user_hashed_password(
        &self,
        user_id: &UserId,
    ) -> Result<Option<HashedPassword>, Error>;
}
```

### Behavior

An unknown user is `Ok(None)` rather than an error, so authentication can treat it like a wrong
password. Its wiring key is `UserHashedPasswordQuerierComponent`, bound in `MockNamespace` to
[`UseMockedApp`](mock-backend.md#userhashedpasswordquerier).

### Context dependencies

`HasUserIdType`, `HasHashedPasswordType`, and `HasErrorType`, as supertraits.

## `CanQueryUserBalance`

`CanQueryUserBalance` reads a user's balance in one currency.

### Definition

```rust
#[cgp_component(UserBalanceQuerier)]
#[prefix(@app.finance in DefaultNamespace)]
#[async_trait]
#[use_type(HasUserIdType.UserId, HasCurrencyType.Currency, HasQuantityType.Quantity, HasErrorType.Error)]
pub trait CanQueryUserBalance {
    async fn query_user_balance(
        &self,
        user: &UserId,
        currency: &Currency,
    ) -> Result<Quantity, Error>;
}
```

### Behavior

Its wiring key is `UserBalanceQuerierComponent`, bound in `MockNamespace` to
[`UseMockedApp`](mock-backend.md#userbalancequerier).

### Context dependencies

`HasUserIdType`, `HasCurrencyType`, `HasQuantityType`, and `HasErrorType`, as supertraits.

## `CanTransferMoney`

`CanTransferMoney` moves an amount of one currency from one user to another.

### Definition

```rust
#[cgp_component(MoneyTransferrer)]
#[prefix(@app.finance in DefaultNamespace)]
#[async_trait]
#[use_type(HasUserIdType.UserId, HasCurrencyType.Currency, HasQuantityType.Quantity, HasErrorType.Error)]
pub trait CanTransferMoney {
    async fn transfer_money(
        &self,
        sender: &UserId,
        recipient: &UserId,
        currency: &Currency,
        quantity: &Quantity,
    ) -> Result<(), Error>;
}
```

### Behavior

The component says nothing about a transfer to oneself; that rule is supplied by the
[`NoTransferToSelf`](wrappers.md#notransfertoself) wrapper `MockApp` wires. Its wiring key is
`MoneyTransferrerComponent`, which `MockNamespace` leaves unbound so that `MockApp` can bind it; see
[namespace organization](../architecture/namespace-organization.md#the-one-path-mockapp-wires-itself).

### Context dependencies

`HasUserIdType`, `HasCurrencyType`, `HasQuantityType`, and `HasErrorType`, as supertraits.

## Source

- [`interfaces/api.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/interfaces/api.rs)
  — `CanHandleApi` and the endpoint markers.
- [`interfaces/error.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/interfaces/error.rs)
  — `CanRaiseHttpError` and the status markers.
- [`interfaces/auth.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/interfaces/auth.rs)
  — `CanCheckPassword`, `CanQueryUserHashedPassword`, and the two logged-in-user getters, which are
  documented with the [API handlers](api-handlers.md#the-request-getters).
- [`interfaces/finance.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/interfaces/finance.rs)
  — `CanQueryUserBalance` and `CanTransferMoney`.

## Public material derived from this

Sections 2 and 3 of the crate's own README.
