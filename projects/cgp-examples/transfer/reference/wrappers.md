# Wrappers

The wrappers are the five [higher-order providers](../../../../cgp/concepts/higher-order-providers.md)
in `transfer`: four for `ApiHandler`, which each take an inner handler and add one concern around it,
and one for `MoneyTransferrer`, which guards the business operation. Each declares its inner provider
with [`#[use_provider]`](../../../../cgp/reference/attributes/use_provider.md) and calls it as an
associated function, so the inner call goes to the named provider rather than back through the
context's wiring. How the endpoints nest them is traced in
[the request lifecycle](../architecture/request-lifecycle.md).

## `HandleFromRequest`

`HandleFromRequest<Request, InHandler>` accepts an outer request type and converts it into the inner
handler's request before delegating.

### Definition

```rust
#[cgp_impl(new HandleFromRequest<Request, InHandler>)]
#[use_type(HasErrorType.Error)]
#[use_provider(InHandler: ApiHandler<Api>)]
impl<Api, Request, InHandler> ApiHandler<Api>
where
    Request: Into<InHandler::Request>,
{
    type Request = Request;

    type Response = InHandler::Response;

    async fn handle_api(
        &self,
        api: PhantomData<Api>,
        request: Self::Request,
    ) -> Result<Self::Response, Error> { ... }
}
```

### Behavior

It calls `request.into()` and passes the result to the inner handler, returning the inner response
unchanged. Both endpoints use it outermost, with the raw Axum extractor tuple as `Request`, so the
endpoints below it see only the domain request types. The conversion is the `From` impl the request
type provides, and it cannot fail.

### Context dependencies

The inner handler's own, since it adds none beyond `HasErrorType` for the return type.

## `HandleFromResponse`

`HandleFromResponse<Response, InHandler>` runs the inner handler and converts its response into an
outer response type.

### Definition

```rust
#[cgp_impl(new HandleFromResponse<Response, InHandler>)]
#[use_type(HasErrorType.Error)]
#[use_provider(InHandler: ApiHandler<Api>)]
impl<Api, Response, InHandler> ApiHandler<Api>
where
    InHandler::Response: Into<Response>,
{
    type Request = InHandler::Request;

    type Response = Response;

    async fn handle_api(
        &self,
        api: PhantomData<Api>,
        request: Self::Request,
    ) -> Result<Self::Response, Error> { ... }
}
```

### Behavior

It awaits the inner handler, propagates its error, and converts a success with `Into`. It is the
mirror of `HandleFromRequest`, and no pipeline in the crate uses it.

### Context dependencies

The inner handler's own.

### Known issues

Unused; see [issues.md](../issues.md#housekeeping).

## `ResponseToJson`

`ResponseToJson<InHandler>` wraps the inner handler's response in `axum::Json`.

### Definition

```rust
#[cgp_impl(new ResponseToJson<InHandler>)]
#[use_type(HasErrorType.Error)]
#[use_provider(InHandler: ApiHandler<Api>)]
impl<Api, InHandler> ApiHandler<Api> {
    type Request = InHandler::Request;

    type Response = Json<InHandler::Response>;

    async fn handle_api(
        &self,
        api: PhantomData<Api>,
        request: Self::Request,
    ) -> Result<Self::Response, Error> { ... }
}
```

### Behavior

The response becomes a JSON body when Axum turns it into an HTTP response, which requires the inner
response to implement `Serialize`; the provider itself places no bound on it, so the requirement
surfaces at the route. Only the balance endpoint uses it, because the transfer returns `()`. It lives
in `providers/axum` because it names an Axum type.

### Context dependencies

The inner handler's own.

## `UseBasicAuth`

`UseBasicAuth<InHandler>` logs a user in from the request's Basic-auth credentials, then delegates.

### Definition

```rust
#[cgp_impl(new UseBasicAuth<InHandler>)]
#[uses(CanQueryUserHashedPassword, CanCheckPassword)]
#[use_type(HasUserIdType.UserId, HasErrorType.Error)]
#[use_provider(InHandler: ApiHandler<Api>)]
impl<Api, InHandler> ApiHandler<Api>
where
    InHandler::Request: HasLoggedInUserMut<Self> + HasBasicAuthHeader<Self>,
    Self::UserId: Clone,
{
    type Request = InHandler::Request;

    type Response = InHandler::Response;

    async fn handle_api(
        &self,
        api: PhantomData<Api>,
        mut request: Self::Request,
    ) -> Result<Self::Response, Error> { ... }
}
```

### Behavior

When the request has no logged-in user and carries a `(user, password)` header, it looks up the
stored password and, if one exists and `check_password` accepts it, writes the user into the request's
`logged_in_user`. It then calls the inner handler with the request whatever the outcome. It never
raises an authentication error itself: a missing header, an unknown user, and a wrong password all
leave the user unset, and the endpoint below reports `401`. An error from the password lookup is
propagated. A request that already has a logged-in user skips the lookup.

### Context dependencies

`CanQueryUserHashedPassword` and `CanCheckPassword`, plus `HasUserIdType` with `UserId: Clone`, and
the inner handler's own. The request must implement `HasLoggedInUserMut` and `HasBasicAuthHeader`.

## `NoTransferToSelf`

`NoTransferToSelf<InHandler>` is a `MoneyTransferrer` provider that rejects a transfer whose sender
and recipient are the same user, and otherwise delegates.

### Definition

```rust
#[cgp_impl(new NoTransferToSelf<InHandler>)]
#[use_type(
    HasUserIdType.UserId,
    HasCurrencyType.Currency,
    HasQuantityType.Quantity,
    HasErrorType.Error,
)]
#[uses(CanRaiseHttpError<ErrBadRequest, String>)]
#[use_provider(InHandler: MoneyTransferrer)]
impl<InHandler> MoneyTransferrer
where
    UserId: Eq,
{
    async fn transfer_money(
        &self,
        sender: &UserId,
        recipient: &UserId,
        currency: &Currency,
        quantity: &Quantity,
    ) -> Result<(), Error> { ... }
}
```

### Behavior

When `sender == recipient` it raises `ErrBadRequest` with the detail
`cannot transfer with the same sender and recipient: {sender}`, and the inner provider is never called.
Otherwise it forwards all four arguments to the inner provider. `MockApp` wires it around
`UseMockedApp`, whose own transfer accepts a self-transfer as a no-op, so this wrapper is what turns
that request into a `400` for the service.

### Context dependencies

`CanRaiseHttpError<ErrBadRequest, String>` and the four abstract types, with `UserId: Eq`, and the
inner provider's own.

## Source

- [`providers/api_handlers/from_request.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/api_handlers/from_request.rs)
  — `HandleFromRequest` and `HandleFromResponse`.
- [`providers/axum/json.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/axum/json.rs)
  — `ResponseToJson`.
- [`providers/api_handlers/basic_auth.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/api_handlers/basic_auth.rs)
  — `UseBasicAuth`.
- [`providers/finance.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/finance.rs)
  — `NoTransferToSelf`.

## Public material derived from this

Section 5, "Reusable wrappers as higher-order providers", and the end of section 6 of the crate's own
README.
