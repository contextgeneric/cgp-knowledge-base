# Domain types

The domain types are the five abstract types every handler, wrapper, and backend in `transfer` names
instead of a concrete type. Each is a one-associated-type [`#[cgp_type]`](../../../../cgp/reference/macros/cgp_type.md)
component with a path in `DefaultNamespace`, and `MockNamespace` binds all five with `UseType`.
Together with CGP's own [`HasErrorType`](../../../../cgp/reference/components/has_error_type.md), they
are the only domain types the handlers and the backend refer to; the concrete types they resolve to
are named only in the wiring and the HTTP layer.

## `HasUserIdType`

`HasUserIdType` is the abstract type of a user identifier.

### Definition

```rust
#[cgp_type]
#[prefix(@app.auth.types in DefaultNamespace)]
pub trait HasUserIdType {
    type UserId: Display;
}
```

### Behavior

The `Display` bound lets a provider interpolate a user id into an error message, which is the only
use the code makes of it. Providers that key a map by user id add `Ord` and `Clone` in their own
`where` clauses rather than on the type. `MockNamespace` binds it to `String`. Its wiring key is
`UserIdTypeProviderComponent`.

### Context dependencies

None; it is bound directly with `UseType<String>`.

## `HasPasswordType`

`HasPasswordType` is the abstract type of the cleartext password a request carries.

### Definition

```rust
#[cgp_type]
#[prefix(@app.auth.types in DefaultNamespace)]
pub trait HasPasswordType {
    type Password;
}
```

### Behavior

It has no bound, because only the password checker compares it, and the checker adds the bound it
needs. `MockNamespace` binds it to `String`, and the request types store it in their
`basic_auth_header` field. Its wiring key is `PasswordTypeProviderComponent`.

### Context dependencies

None; it is bound directly with `UseType<String>`.

## `HasHashedPasswordType`

`HasHashedPasswordType` is the abstract type of a stored password, which the backend looks up and the
checker compares against the cleartext one.

### Definition

```rust
#[cgp_type]
#[prefix(@app.auth.types in DefaultNamespace)]
pub trait HasHashedPasswordType {
    type HashedPassword;
}
```

### Behavior

The name anticipates a real hashed store, but `MockNamespace` binds it to `String` and the mock
backend stores passwords in the clear. The mock checker unifies it with `Password` through a
`#[use_type]` equality, as recorded in [mock backend](mock-backend.md#passwordchecker). Its wiring key
is `HashedPasswordTypeProviderComponent`.

### Context dependencies

None; it is bound directly with `UseType<String>`.

## `HasQuantityType`

`HasQuantityType` is the abstract type of a money amount.

### Definition

```rust
#[cgp_type]
#[prefix(@app.finance.types in DefaultNamespace)]
pub trait HasQuantityType {
    type Quantity: Display;
}
```

### Behavior

`MockNamespace` binds it to `u64`. The mock transfer adds `CheckedAdd + CheckedSub` from `num-traits`
in its own bounds, so an overflow or an overdraft is detected rather than wrapping. The balance
response serializes the quantity directly. Its wiring key is `QuantityTypeProviderComponent`.

### Context dependencies

None; it is bound directly with `UseType<u64>`.

## `HasCurrencyType`

`HasCurrencyType` is the abstract type of a currency.

### Definition

```rust
#[cgp_type]
#[prefix(@app.finance.types in DefaultNamespace)]
pub trait HasCurrencyType {
    type Currency: Display;
}
```

### Behavior

`MockNamespace` binds it to [`DemoCurrency`](http-layer.md#democurrency), an enum of `EUR` and `USD`
that deserializes from the query string. Its wiring key is `CurrencyTypeProviderComponent`.

### Context dependencies

None; it is bound directly with `UseType<DemoCurrency>`.

## Source

- [`interfaces/types.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/interfaces/types.rs)
  — the five types.
- [`namespaces/mock.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/namespaces/mock.rs)
  — their bindings.

## Public material derived from this

Section 1, "Abstract domain types", of the crate's own README.
