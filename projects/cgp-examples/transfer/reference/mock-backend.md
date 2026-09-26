# Mock backend

The mock backend is one provider struct, `UseMockedApp`, that implements all four backend components
by reading two in-memory maps off the context as
[`#[implicit]`](../../../../cgp/reference/attributes/implicit.md) arguments. Three of its four impls
register themselves into `MockNamespace` with
[`#[default_impl]`](../../../../cgp/reference/attributes/default_impl.md); the transfer does not, so
that `MockApp` can wrap it.

## `UseMockedApp`

`UseMockedApp` is the provider struct the four impls below share.

### Definition

```rust
pub struct UseMockedApp;
```

### Behavior

Four blocks implement it, so the struct is declared once by hand, with a doc comment, and each block
names it as `#[cgp_impl(UseMockedApp)]` without the `new` keyword.

### Context dependencies

Those of the impl in use, listed below.

## `UserHashedPasswordQuerier`

`UseMockedApp`'s password lookup reads the stored password from a map on the context.

### Definition

```rust
#[cgp_impl(UseMockedApp)]
#[default_impl(@app.auth.UserHashedPasswordQuerierComponent in MockNamespace)]
#[use_type(HasUserIdType.UserId, HasHashedPasswordType.HashedPassword, HasErrorType.Error)]
impl UserHashedPasswordQuerier
where
    UserId: Ord,
    HashedPassword: Clone,
{
    async fn query_user_hashed_password(
        &self,
        user_id: &UserId,
        #[implicit] user_passwords: &BTreeMap<UserId, HashedPassword>,
    ) -> Result<Option<HashedPassword>, Error> { ... }
}
```

### Behavior

It returns a clone of the map entry, or `None` for an unknown user, and never fails.

### Context dependencies

A `user_passwords: BTreeMap<UserId, HashedPassword>` field, and the three abstract types.

## `PasswordChecker`

`UseMockedApp`'s password check compares the two passwords for equality.

### Definition

```rust
#[cgp_impl(UseMockedApp)]
#[default_impl(@app.auth.PasswordCheckerComponent in MockNamespace)]
#[use_type(HasPasswordType.Password, HasHashedPasswordType.{HashedPassword = Password})]
impl PasswordChecker
where
    Password: Eq,
{
    fn check_password(password: &Password, hashed_password: &HashedPassword) -> bool { ... }
}
```

### Behavior

It returns `password == hashed_password`. The `#[use_type]` equality form requires the stored-password
type to be the cleartext type, which is what makes the comparison type-check; the mock stores
passwords in the clear.

### Context dependencies

`HasPasswordType` with `Password: Eq`, and `HasHashedPasswordType` with `HashedPassword = Password`.

## `UserBalanceQuerier`

`UseMockedApp`'s balance query reads one entry of the shared balance map.

### Definition

```rust
#[cgp_impl(UseMockedApp)]
#[default_impl(@app.finance.UserBalanceQuerierComponent in MockNamespace)]
#[uses(CanRaiseHttpError<ErrNotFound, String>)]
#[use_type(HasUserIdType.UserId, HasCurrencyType.Currency, HasQuantityType.Quantity, HasErrorType.Error)]
impl UserBalanceQuerier
where
    UserId: Ord + Clone,
    Currency: Ord + Clone,
    Quantity: Clone,
{
    async fn query_user_balance(
        &self,
        user: &UserId,
        currency: &Currency,
        #[implicit] user_balances: &Arc<Mutex<BTreeMap<(UserId, Currency), Quantity>>>,
    ) -> Result<Quantity, Error> { ... }
}
```

### Behavior

It locks the map, looks up `(user, currency)`, and returns a clone of the balance. A missing entry
raises `ErrNotFound` with `user not found in mocked database: {user}`. Through the HTTP service that
path is unreachable with the seeded data, because every user with a password has a balance in both
currencies and an unknown user fails authentication first. The mutex is `futures::lock::Mutex`, an
async lock, so holding it does not block the executor.

### Context dependencies

A `user_balances: Arc<Mutex<BTreeMap<(UserId, Currency), Quantity>>>` field,
`CanRaiseHttpError<ErrNotFound, String>`, and the four abstract types.

## `MoneyTransferrer`

`UseMockedApp`'s transfer moves an amount between two entries of the balance map.

### Definition

```rust
#[cgp_impl(UseMockedApp)]
#[uses(CanRaiseHttpError<ErrNotFound, String>, CanRaiseHttpError<ErrBadRequest, String>)]
#[use_type(HasUserIdType.UserId, HasCurrencyType.Currency, HasQuantityType.Quantity, HasErrorType.Error)]
impl MoneyTransferrer
where
    Quantity: CheckedAdd + CheckedSub,
    UserId: Ord + Clone,
    Currency: Ord + Clone,
{
    async fn transfer_money(
        &self,
        sender: &UserId,
        recipient: &UserId,
        currency: &Currency,
        quantity: &Quantity,
        #[implicit] user_balances: &Arc<Mutex<BTreeMap<(UserId, Currency), Quantity>>>,
    ) -> Result<(), Error> { ... }
}
```

### Behavior

It holds the lock for the whole operation. It raises `ErrNotFound` if the sender's or the recipient's
entry is missing, checked in that order, and `ErrBadRequest` if subtracting from the sender underflows
(`sender {sender} has insufficient balance {balance} to transfer {quantity}`). A transfer from a user
to themselves then returns `Ok` without writing, so it leaves the balance unchanged. For two distinct
users it raises `ErrBadRequest` if adding to the recipient overflows
(`recipient already has too much money!`), and otherwise writes the sender's new balance, then the
recipient's.

A probe wired this impl without `NoTransferToSelf`. A self-transfer of 10 left a balance of 100 at 100,
a self-transfer of 1000 was rejected for insufficient balance, and a transfer of 10 to another user
moved the money.

It carries no `#[default_impl]`, so `MockNamespace` leaves the transfer path open for `MockApp` to
wire; a comment on the impl records why.

### Context dependencies

A `user_balances` field as above, `CanRaiseHttpError<ErrNotFound, String>` and
`CanRaiseHttpError<ErrBadRequest, String>`, and the four abstract types with the checked-arithmetic
bounds.

## Source

- [`providers/mocked.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/transfer/src/providers/mocked.rs)
  — the struct and all four impls.

## Public material derived from this

Section 6, "The in-memory backend", of the crate's own README.
