# The fine-grained stage

`fine_grained.rs` splits each manager into one component per operation, moves the two content checks
into higher-order providers that wrap a creator, and groups the providers into three bundles that
`ProductionApp` forwards to with array keys.

- **Source** — [fine_grained.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/web-app/src/fine_grained.rs)
- **Run** — no test; the context is exercised only by its check block
- **Needs** — nothing
- **Result** — compiles and passes its check. A probe compiled the commented-out flat table on a
  context of its own, and it passed the same nine checks

## The components

The module defines nine components, none with a namespace prefix: `UserCreator`, `UserGetter`, and
`UserUpdater` for users, `PostCreator`, `PostGetter`, `PostUpdater`, and `PostDeleter` for posts, and
the same `UsernameCensor` and `SpamMessageDetector` as the coarse stage. Each operation component has
the one method its coarse manager had, with the same signature:

```rust
#[cgp_component(UserCreator)]
pub trait CanCreateUser {
    fn create_user(&self, username: &str, email: &Email) -> Result<User, Error>;
}
```

## The providers

The providers fall into three groups, and only the two filter wrappers import another trait:

| Provider | Implements | Reads or requires |
|---|---|---|
| `FilterCensoredUsername<InnerCreator>` | `UserCreator` | `CanCensorUsername`, and `InnerCreator: UserCreator` |
| `FilterSpamMessage<InnerCreator>` | `PostCreator` | `CanDetectSpamMessage`, and `InnerCreator: PostCreator` |
| `CreateUserWithPostgres`, `GetUserWithPostgres`, `UpdateUserWithPostgres` | the three user components | the `database` field |
| `CreatePostWithPostgres`, `GetPostWithPostgres`, `UpdatePostWithPostgres`, `DeletePostWithPostgres` | the four post components | the `database` field |
| `DummyUserCensor`, `AiUserCensor` | `UsernameCensor` | nothing |
| `DummySpamMessageDetector`, `AiSpamMessageDetector` | `SpamMessageDetector` | nothing |

The wrappers are where the content checks now live. `FilterCensoredUsername` rejects a censored name
and otherwise forwards to its inner creator:

```rust
#[cgp_impl(new FilterCensoredUsername<InnerCreator>)]
#[uses(CanCensorUsername)]
#[use_provider(InnerCreator: UserCreator)]
impl<InnerCreator> UserCreator {
    fn create_user(&self, username: &str, email: &Email) -> Result<User, Error> {
        if self.username_is_censored(username) > Probability::new(0.8) {
            return Err(Error::InvalidUsername);
        }

        InnerCreator::create_user(self, username, email)
    }
}
```

`FilterSpamMessage` does the same for `create_post`, returning `Error::InvalidMessage`. The Postgres
creators check nothing themselves, since the wiring always wraps them. Every provider body other than
the two wrappers' is `todo!()`.

## The bundles and the context

Three bundles, defined with `new` in
[`delegate_components!`](../../../cgp/reference/macros/delegate_components.md), each group one
domain's providers:

```rust
delegate_components! {
    new PostgresUserComponents {
        UserCreatorComponent:
            FilterCensoredUsername<CreateUserWithPostgres>,
        UserGetterComponent:
            GetUserWithPostgres,
        UserUpdaterComponent:
            UpdateUserWithPostgres,
    }
}
```

`PostgresPostComponents` wires the four post components, with
`FilterSpamMessage<CreatePostWithPostgres>` as the creator, and `AiContentFilterComponents` wires
`AiUserCensor` and `AiSpamMessageDetector`. `ProductionApp` forwards each component to its bundle, listing the keys in three arrays:

```rust
delegate_components! {
    ProductionApp {
        [
            UserCreatorComponent,
            UserGetterComponent,
            UserUpdaterComponent,
        ]:
            PostgresUserComponents,
        [
            PostCreatorComponent,
            PostGetterComponent,
            PostUpdaterComponent,
            PostDeleterComponent,
        ]:
            PostgresPostComponents,
        [
            UsernameCensorComponent,
            SpamMessageDetectorComponent,
        ]:
            AiContentFilterComponents,
    }
}
```

A separate `check_components!` block asserts all nine components on `ProductionApp`. Above the
bundles, the module keeps the same wiring written as a flat nine-entry table on `ProductionApp`, as a
comment. The dummy filter providers are defined here but not wired.

## What it demonstrates

- Fine-grained components, which let each provider carry only the dependencies its one method uses;
  see [sizing a component](../../../cgp/guides/sizing-a-component.md).
- A check moved out of a provider into a [higher-order provider](../../../cgp/concepts/higher-order-providers.md)
  that wraps any inner creator.
- [Aggregate providers](../../../cgp/concepts/aggregate-providers.md) that group related wiring, and
  the cost that remains: the context still names every component key.

## Known issues

- **The flat table is a comment** — nothing compiles it; see [issues.md](issues.md#housekeeping).
- **Unwired providers** — `DummyUserCensor` and `DummySpamMessageDetector`; see
  [issues.md](issues.md#housekeeping).

## Public material derived from this

The "Fine grained traits", "Higher-order providers", "Too much wiring with fine grained traits", and
"The challenges of grouping delegate component keys" sections of the
[v0.8.0 release post](../../../website/blog/v0-8-0-release.md).
