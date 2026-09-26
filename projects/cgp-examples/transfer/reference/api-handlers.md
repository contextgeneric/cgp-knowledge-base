# API handlers

The API handlers are the two endpoint providers at the center of each pipeline, the balance response
they produce, and the five getter traits through which they and the auth wrapper read the request.
The handlers depend only on business components and the error component, never on the backend or on
HTTP types, and they are generic over their request type.

## `HandleQueryBalance`

`HandleQueryBalance<Request>` is the balance endpoint: it requires a logged-in user and returns that
user's balance in the requested currency.

### Definition

```rust
#[cgp_impl(new HandleQueryBalance<Request>)]
#[uses(CanQueryUserBalance, CanRaiseHttpError<ErrUnauthorized, String>)]
#[use_type(HasErrorType.Error)]
impl<Api, Request> ApiHandler<Api>
where
    Request: HasLoggedInUser<Self> + HasQueryBalanceFields<Self>,
{
    type Request = Request;

    type Response = QueryBalanceResponse<Self>;

    async fn handle_api(
        &self,
        _api: PhantomData<Api>,
        request: Request,
    ) -> Result<QueryBalanceResponse<Self>, Error> { ... }
}
```

### Behavior

If the request's `logged_in_user` is `None`, it raises `ErrUnauthorized` with the detail
`you must first login`. Otherwise it calls `query_user_balance` with the user and the request's
currency, propagates any error unchanged, and returns `QueryBalanceResponse { balance }`. It is
generic over `Api`, so it would serve any endpoint marker it is wired to, and over `Request`, so any
request type with the two getters works.

### Context dependencies

`CanQueryUserBalance` and `CanRaiseHttpError<ErrUnauthorized, String>`, and `HasErrorType` for the
return type. The getter bounds are on the request, not the context.

## `HandleTransfer`

`HandleTransfer<Request>` is the transfer endpoint: it requires a logged-in sender and moves the
requested amount to the named recipient.

### Definition

```rust
#[cgp_impl(new HandleTransfer<Request>)]
#[uses(CanTransferMoney, CanRaiseHttpError<ErrUnauthorized, String>)]
#[use_type(HasErrorType.Error)]
impl<Api, Request> ApiHandler<Api>
where
    Request: HasLoggedInUser<Self> + HasTransferMoneyFields<Self>,
{
    type Request = Request;

    type Response = ();

    async fn handle_api(&self, _api: PhantomData<Api>, request: Request) -> Result<(), Error> { ... }
}
```

### Behavior

If no user is logged in, it raises `ErrUnauthorized` with the detail
`you must first login to perform transfer`. Otherwise it calls `transfer_money` with the logged-in
user as sender and the request's recipient, currency, and quantity, and returns `()`, which Axum
answers with an empty `200`. Whether a self-transfer is allowed is decided by the `MoneyTransferrer`
provider the context wires, not here.

### Context dependencies

`CanTransferMoney` and `CanRaiseHttpError<ErrUnauthorized, String>`, and `HasErrorType` for the
return type.

## `QueryBalanceResponse`

`QueryBalanceResponse<App>` is the balance endpoint's output, generic over the context so its field is
the context's abstract quantity.

### Definition

```rust
#[derive(Serialize)]
pub struct QueryBalanceResponse<App>
where
    App: HasQuantityType,
{
    pub balance: App::Quantity,
}
```

### Behavior

Serialized as JSON by `ResponseToJson`, it becomes `{"balance":100}` for a `u64` quantity.

### Context dependencies

`HasQuantityType` on the context it is instantiated with.

## The request getters

The five getter traits read fields off a request value rather than off the context, which is why they
are [`#[cgp_auto_getter]`](../../../../cgp/reference/macros/cgp_auto_getter.md) traits and not
`#[implicit]` arguments: an implicit argument reads only from `self`. Each is generic over the
context, `App`, so its return types can name the context's abstract types, and each is implemented
automatically for any request type with a field of the method's name. The request types in
[the HTTP layer](http-layer.md#the-request-types) derive `HasField` to satisfy them.

### Definition

```rust
#[cgp_auto_getter]
#[use_type(HasUserIdType.UserId in App)]
pub trait HasLoggedInUser<App> {
    fn logged_in_user(&self) -> &Option<UserId>;
}

#[cgp_auto_getter]
#[use_type(HasUserIdType.UserId in App)]
pub trait HasLoggedInUserMut<App> {
    fn logged_in_user(&mut self) -> &mut Option<UserId>;
}

#[cgp_auto_getter]
#[use_type(HasUserIdType.UserId in App, HasPasswordType.Password in App)]
pub trait HasBasicAuthHeader<App> {
    fn basic_auth_header(&self) -> &Option<(UserId, Password)>;
}

#[cgp_auto_getter]
#[use_type(HasCurrencyType.Currency in App)]
pub trait HasQueryBalanceFields<App> {
    fn currency(&self) -> &Currency;
}

#[cgp_auto_getter]
#[use_type(
    HasUserIdType.UserId in App,
    HasCurrencyType.Currency in App,
    HasQuantityType.Quantity in App,
)]
pub trait HasTransferMoneyFields<App> {
    fn currency(&self) -> &Currency;

    fn recipient(&self) -> &UserId;

    fn quantity(&self) -> &Quantity;
}
```

### Behavior

`HasLoggedInUser` and `HasLoggedInUserMut` read the same `logged_in_user` field, the first by shared
reference for the endpoints and the second by mutable reference for
[`UseBasicAuth`](wrappers.md#usebasicauth), which writes the authenticated user into it. The two
declare a method of the same name, which works because each provider bounds its request by only one of
them. `HasQueryBalanceFields` and `HasTransferMoneyFields` likewise both declare `currency`, and again
no bound names both. Each imports the app's abstract types with `#[use_type(… in App)]`, which also
supplies the `App` bounds, so the plain `<App>` parameter is enough.

### Context dependencies

The abstract types each return type names, on `App`.

## Source

- [`providers/api_handlers/query_balance.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/api_handlers/query_balance.rs)
  — `HandleQueryBalance`, `QueryBalanceResponse`, and `HasQueryBalanceFields`.
- [`providers/api_handlers/transfer.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/api_handlers/transfer.rs)
  — `HandleTransfer` and `HasTransferMoneyFields`.
- [`providers/api_handlers/basic_auth.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/api_handlers/basic_auth.rs)
  — `HasBasicAuthHeader`.
- [`interfaces/auth.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/interfaces/auth.rs)
  — `HasLoggedInUser` and `HasLoggedInUserMut`.

## Public material derived from this

Section 4, "The endpoint handlers", of the crate's own README.
