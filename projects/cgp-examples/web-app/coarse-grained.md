# The coarse-grained stage

`coarse_grained.rs` is the first stage: one manager trait per domain, with the content filters as
two small components of their own, wired on `ProductionApp` in four entries.

- **Source** — [coarse_grained.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/web-app/src/coarse_grained.rs)
- **Run** — no test; the context is exercised only by the check its wiring macro derives
- **Needs** — nothing
- **Result** — compiles and passes its checks. A probe called `get_user` and `create_user` on
  `ProductionApp`, and both panicked with `not yet implemented`

## The components

The module defines four components. `UserManager` and `PostManager` each gather a domain's whole
lifecycle into one trait, and the two filters return a `Probability` for a manager to threshold:

```rust
#[cgp_component(UserManager)]
pub trait CanManageUser {
    fn create_user(&self, username: &str, email: &Email) -> Result<User, Error>;

    fn get_user(&self, user_id: &UserId) -> Result<User, Error>;

    fn update_user_data(&self, user_id: &UserId, user_data: &UserData) -> Result<(), Error>;
}

#[cgp_component(UsernameCensor)]
pub trait CanCensorUsername {
    fn username_is_censored(&self, username: &str) -> Probability;
}
```

`CanManagePost` has `create_post`, `get_post`, `update_post`, and `delete_post`, and
`CanDetectSpamMessage` has `message_is_spam`. None of the four carries a namespace prefix.

## The providers

`PostgresUserManager` implements the whole user manager. It reads the context's `database` field as
an implicit argument and imports `CanCensorUsername`, which only `create_user` calls:

```rust
#[cgp_impl(new PostgresUserManager)]
#[uses(CanCensorUsername)]
impl UserManager {
    fn create_user(
        &self,
        #[implicit] database: &PostgresDb,
        username: &str,
        email: &Email,
    ) -> Result<User, Error> {
        if self.username_is_censored(username) > Probability::new(0.8) {
            return Err(Error::InvalidUsername);
        }

        todo!()
    }

    fn get_user(&self, #[implicit] database: &PostgresDb, user_id: &UserId) -> Result<User, Error> {
        todo!()
    }

    // update_user_data, likewise
}
```

`PostgresPostManager` has the same shape: it imports `CanDetectSpamMessage`, and `create_post` returns
`Error::InvalidMessage` when `message_is_spam` scores above 0.8. The filters have one provider each,
`DummyUserCensor` and `DummySpamMessageDetector`, whose bodies are `todo!()`. The AI-backed filters
first appear in the next stage.

## The context and its wiring

`ProductionApp` holds the database handle and wires all four components in one
[`delegate_and_check_components!`](../../../cgp/reference/macros/delegate_and_check_components.md)
table:

```rust
#[derive(HasField)]
pub struct ProductionApp {
    pub database: PostgresDb,
}

delegate_and_check_components! {
    ProductionApp {
        UserManagerComponent: PostgresUserManager,
        PostManagerComponent: PostgresPostManager,
        UsernameCensorComponent: DummyUserCensor,
        SpamMessageDetectorComponent: DummySpamMessageDetector,
    }
}
```

Despite its name, this stage's `ProductionApp` wires the dummy filters. The macro checks each of the
four entries as it wires it, so the manager's dependency on the filter is verified at this site.

## What it demonstrates

- A dependency one method needs that the whole provider carries: a context can use `get_user` or
  `update_user_data` through `PostgresUserManager` only if it implements `CanCensorUsername`, though
  neither method calls it. The
  [social media app](../../../examples/social-media-app.md#one-manager-per-domain) example develops
  this strain, and [sizing a component](../../../cgp/guides/sizing-a-component.md) is the guide to the
  decision it motivates.
- A basic context wired and checked in one macro, which suits a table of plain entries.

## Public material derived from this

The "An example social media web app" and "Filtering usernames and post messages" sections of the
[v0.8.0 release post](../../../website/blog/v0-8-0-release.md).
