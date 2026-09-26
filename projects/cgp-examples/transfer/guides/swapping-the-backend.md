# Swapping the backend

Replacing the in-memory backend means writing providers for the four backend components and a new
namespace that binds them, because `MockNamespace` cannot be inherited and partly overridden. This
guide shows both, using a `ConstBalance` provider that answers every balance query from a context
field as the running example. The snippets compiled and ran in a downstream probe crate against the
`v0.8.0` branch, where the new context returned the field's value for Alice's balance.

## Write the new provider

A backend provider implements a backend component against the abstract types, reads what it needs
from the context, and registers itself into the new namespace with `#[default_impl]`:

```rust
#[cgp_impl(new ConstBalance)]
#[default_impl(@app.finance.UserBalanceQuerierComponent in ConstNamespace)]
#[use_type(HasUserIdType.UserId, HasCurrencyType.Currency, HasQuantityType.{Quantity = u64}, HasErrorType.Error)]
impl UserBalanceQuerier {
    async fn query_user_balance(
        &self,
        _user: &UserId,
        _currency: &Currency,
        #[implicit] fixed_balance: &u64,
    ) -> Result<u64, Error> {
        Ok(*fixed_balance)
    }
}
```

A real backend would take a database handle as its `#[implicit]` argument instead. The components it
must cover are the four `UseMockedApp` implements: `UserHashedPasswordQuerier`, `PasswordChecker`,
`UserBalanceQuerier`, and `MoneyTransferrer`. It may replace only some of them and keep `UseMockedApp`
for the rest, as the probe did for authentication.

## Give it a namespace of its own

The new configuration needs a namespace that inherits `DefaultNamespace`, not `MockNamespace`, and
that repeats the type and error choices `MockNamespace` makes:

```rust
cgp_namespace! {
    new ConstNamespace: DefaultNamespace {
        @cgp.core.error.ErrorTypeProviderComponent: UseType<AppError>,
        @app.error.HttpErrorRaiserComponent.<Code> Code.String: DisplayHttpError,
        @app.auth.types.{
            UserIdTypeProviderComponent,
            PasswordTypeProviderComponent,
            HashedPasswordTypeProviderComponent,
        }: UseType<String>,
        @app.finance.types.QuantityTypeProviderComponent: UseType<u64>,
        @app.finance.types.CurrencyTypeProviderComponent: UseType<DemoCurrency>,
        @app.auth.{UserHashedPasswordQuerierComponent, PasswordCheckerComponent}: UseMockedApp,
    }
}
```

Inheriting `MockNamespace` and rebinding one path is the natural attempt, and it fails.
`MockNamespace` already binds `@app.finance.UserBalanceQuerierComponent` through `UseMockedApp`'s
`#[default_impl]`, and a child namespace that binds the same path conflicts with the parent's
forwarding impl:

```rust
cgp_namespace! {
    new ProdNamespace: MockNamespace {
        @app.finance.UserBalanceQuerierComponent: ConstBalance,
    }
}
```

`cargo cgp check` reports it as [`[CGP-E005]`](../../../../cargo-cgp/error-code.md), overlapping
wiring:

```text
error[E0119]: [CGP-E005] `ProdNamespace` cannot wire `@app.finance.UserBalanceQuerierComponent.*` that is already set through `MockNamespace`
 --> src/bin/override.rs:9:10
  |
8 |     new ProdNamespace: MockNamespace {
  |                        ------------- first implementation here
9 |         @app.finance.UserBalanceQuerierComponent: ConstBalance,
  |          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ conflicting implementation for `@app.finance.UserBalanceQuerierComponent`
```

The mistake is treating a namespace binding as a default a child can override; a binding is final
for every namespace below it. This is the
[namespace override conflict](../../../../cgp/errors/wiring/namespace-override-conflict.md). The
crate's layout makes the repetition unavoidable, because the type choices a second backend would
keep live in the same namespace as the mock providers it replaces; see
[issues.md](../issues.md#missing-features).

## Wire a context

The new context carries the fields its providers read, joins the new namespace, pulls in the same API
surface, and wires the transfer path itself, exactly as `MockApp` does:

```rust
#[derive(HasField)]
pub struct ConstApp {
    pub fixed_balance: u64,
    pub user_passwords: BTreeMap<String, String>,
    pub user_balances: Arc<Mutex<BTreeMap<(String, DemoCurrency), u64>>>,
}

delegate_components! {
    ConstApp {
        namespace ConstNamespace;

        for <Key, Value> in DefaultApiHandlers {
            @app.api.ApiHandlerComponent.Key: Value,
        }

        @app.finance.MoneyTransferrerComponent: NoTransferToSelf<UseMockedApp>,
    }
}

check_components! {
    ConstApp {
        UserBalanceQuerierComponent,
        MoneyTransferrerComponent,
        ApiHandlerComponent: [QueryBalanceApi, TransferApi],
    }
}
```

The probe's context keeps `user_balances` because it still uses `UseMockedApp` for transfers. A
context that serves the endpoints over HTTP also needs one `CanHandleApiSend` impl per endpoint, as in
[adding an endpoint](adding-an-endpoint.md).

Keep `NoTransferToSelf` around the transfer provider if the service should reject a self-transfer:
the mock provider accepts one as a no-op, and a replacement backend decides for itself unless the
guard decides first.

## Public material derived from this

"The payoff" section of the crate's own README, whose summary of this change ("writing one backend
provider and changing one wiring entry") holds only for a backend whose namespace is written afresh.
