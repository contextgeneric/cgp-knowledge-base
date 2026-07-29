# Sizing a component

How many methods a component carries decides how much of CGP's reuse you can actually collect, and this guide is about keeping a component to one capability — and splitting a trait that has already grown past that, along the axis its contexts differ on.

The decision is easy to make by accident, because a trait that groups every operation of an entity reads naturally and compiles fine. What it quietly costs is the thing CGP is for: a provider can only be reused when its *whole* surface is worth reusing, so each method added to a component narrows the set of contexts any one provider can serve, until at the limit a plain impl on the concrete type would have been the better tool.

The snippets below draw on two different kinds of context, and the difference matters when reading them. The shape components are about the data, so their contexts are **value contexts** — a `Rectangle` *is* the thing whose area is computed — while the service components are about the application, so the only contexts actually wired here are **environmental** ones: `ProductionApp` and `TestApp` stand for the running service and the test harness. Every component is self-targeted; nothing crosses into a target parameter. The shapes themselves are the subject of [choosing a component's shape](choosing-a-component-shape.md).

## Default to one capability per component

**Give each component one capability, which usually means one method.** A component is the unit of wiring, so its size is the granularity at which a context can make a choice: two methods in one component can never be answered by two different providers, no matter how unrelated they are. Splitting them costs a few extra lines of declaration and buys a choice at each one.

```rust
#[cgp_component(UserCreator)]
pub trait CanCreateUser {
    fn create_user(&self, username: &str, email: &Email) -> Result<User, Error>;
}

#[cgp_component(UserGetter)]
pub trait CanGetUser {
    fn get_user(&self, user_id: &UserId) -> Result<User, Error>;
}
```

Methods belong together only when they always vary together — a paired `encode`/`decode` whose two halves must agree on a format, or a small trait whose methods share state no provider would split. The test is whether you can imagine wanting one method from one provider and another from a second; if you can, they are two components. The [social media app](../../examples/social-media-app.md) example works this decision end to end, starting from one manager trait per domain and arriving at one component per operation.

**Getter components are the deliberate exception, and grouping their methods is idiomatic.** A [`#[cgp_getter]`](../reference/macros/cgp_getter.md) or [`#[cgp_auto_getter]`](../reference/macros/cgp_auto_getter.md) trait declaring `width` and `height` together is not a monolith, because a getter is answered by the *method's own name* rather than by a strategy: one [`UseFields`](../reference/providers/use_fields.md) provider satisfies every method of the trait at once by reading the same-named field for each, so there is no choice to be split apart. Splitting such a trait multiplies declarations and wiring entries and buys nothing. The one thing the grouping costs is the single-field providers — [`UseField`](../reference/providers/use_field.md) and [`WithProvider`](../reference/providers/with_provider.md) are emitted only for a getter trait with exactly one method, since both presuppose one field to read — so a getter that must be wired to a *differently named* field needs its own component. Note also that the default way to read a field is an [`#[implicit]`](../reference/attributes/implicit.md) argument rather than a getter trait at all, per [reading context fields](reading-context-fields.md); this exception applies to the narrow cases that genuinely need the trait.

## The three costs a multi-method component pays

A component with several methods pays in three distinct ways, and it is worth seeing each one, because they arrive at different times and only the first is obvious.

**Every provider carries the union of its methods' dependencies.** A provider must satisfy the dependencies of every method it implements, so a dependency needed by one method is imposed on all of them. In a `CanManageUser` component whose `create_user` screens names but whose `get_user` and `update_user_data` do not, the single provider still depends on `CanCensorUsername`, and every context wiring that provider must supply the censor:

```rust
#[cgp_impl(new PostgresUserManager)]
#[uses(CanCensorUsername)]
impl UserManager {
    fn create_user(&self, #[implicit] database: &PostgresDb, username: &str, email: &Email) -> Result<User, Error> { /* screens the name, then inserts — the only method that calls the censor */ }

    fn get_user(&self, #[implicit] database: &PostgresDb, user_id: &UserId) -> Result<User, Error> { /* ... */ }

    fn update_user_data(&self, #[implicit] database: &PostgresDb, user_id: &UserId, user_data: &UserData) -> Result<(), Error> { /* ... */ }
}
```

The reverse holds too, which is the same cost read from the other side: there is no way to grant one method a capability without granting it to the whole component, so capability isolation becomes impossible. The [social media app](../../examples/social-media-app.md) example shows what the split buys here — once deleting a post is its own component, code that should only read and write posts can be handed the getter and the updater and never receive the destructive delete.

**A [higher-order provider](../concepts/higher-order-providers.md) must implement every method, including the ones it does not care about.** This is the cost that arrives second and hurts most, because wrapping is where CGP's composition pays. A component with one method wraps in four lines, and the wrapper composes over any inner provider:

```rust
#[cgp_impl(new ScaledAreaCalculator<InnerCalculator>)]
#[use_provider(InnerCalculator: AreaCalculator)]
impl<InnerCalculator> AreaCalculator {
    fn area(&self, #[implicit] scale_factor: f64) -> f64 {
        InnerCalculator::area(self) * scale_factor * scale_factor
    }
}
```

Fold `area` into an entity trait alongside its neighbours and the same wrapper has to name all of them, forwarding the ones it has no opinion about:

```rust
#[cgp_component(ShapeProvider)]
pub trait Shape {
    fn area(&self) -> f64;
    fn perimeter(&self) -> f64;
    fn describe(&self) -> String;
}

#[cgp_impl(new ScaledShape<InnerShape>)]
#[use_provider(InnerShape: ShapeProvider)]
impl<InnerShape> ShapeProvider {
    fn area(&self, #[implicit] scale_factor: f64) -> f64 {
        InnerShape::area(self) * scale_factor * scale_factor
    }

    fn perimeter(&self, #[implicit] scale_factor: f64) -> f64 {
        InnerShape::perimeter(self) * scale_factor
    }

    fn describe(&self) -> String {
        InnerShape::describe(self)
    }
}
```

The passthrough grows with the trait, and every method added to `Shape` later must be added to this wrapper and to every other wrapper written over it. The `describe` body is pure ceremony that exists only because the methods share a component.

**A context that needs part of the surface must still supply all of it.** Every method and every associated type of a component has to be answered, so a component grouping unrelated concerns forces stubs on the contexts and providers that use only some of them. Fold rotation into the same `Shape` trait and it brings an associated type with it:

```rust
#[cgp_component(ShapeProvider)]
pub trait Shape {
    type Angle;

    fn rotate(&mut self, angle: Self::Angle);

    // area, perimeter, and describe as above
}
```

A provider that only computes areas must now pick some `Angle` type it never uses and write a `rotate` body it has no meaning for — which in practice means a placeholder type and an `unimplemented!()`. That pattern is common in real codebases, most often in the mock contexts written for tests, and it is a reliable sign that one component is carrying two capabilities. Splitting `Angle` out with [`#[cgp_type]`](../reference/macros/cgp_type.md) and `rotate` into its own component lets an area-only context ignore both entirely.

## The entity trait is the shape you will reach for anyway

**A trait grouping every operation of an entity is the natural design for anyone with an object-oriented background, and recognizing that pull is half of resisting it.** `Shape` with `area`, `perimeter`, `scale`, and `rotate` describes a coherent thing, gives a team one word to talk about, and matches how most developers were taught to model a domain. A behavior-named component like `AreaCalculator` feels thinner and less principled by comparison, so the entity trait is what an author writes unless something stops them.

The trait's own name is the cheapest signal. CGP's consumer traits read as verbs — `CanCreateUser`, `CanCalculateArea` — precisely because a capability is something a context *does*; a consumer trait named after a noun is usually a component carrying several capabilities. The diagnostic question behind the naming is more direct: **would any provider for this trait ever be reused, whole, by a second context?** If the honest answer is no, the trait's providers are not reusable units and the CGP machinery around them is not paying for itself — at which point implementing the trait directly on each concrete type, with no component at all, is the better design. That is a real outcome and not a failure: it is rung 2 of the [modularity hierarchy](../concepts/modularity-hierarchy.md), one implementation per type, chosen deliberately rather than settled for.

## Split an existing trait along the axis its contexts differ on

**When a monolithic trait has to be broken up, do not redesign it in the abstract — split it along the axis on which the contexts you actually want differ.** The reason is that a split only pays where it creates a choice, so the contexts decide where the seams go. The procedure is four steps.

Start by **naming the contexts you want**, which usually means recognizing ones you already have: a production application and a test harness, two deployment targets, a mock and the real thing. Then **list what each method depends on** — which fields it reads, which capabilities it calls, which types it names. **Group the methods whose dependencies are the same across all of those contexts**; those become components with shared, context-generic providers, and they are where the reuse is. Finally, **give the methods that must differ per context their own components**, wired per context — or, where a provider would only ever be used by one context, implement the consumer trait directly on that context and skip the provider entirely.

Worked on a service whose production and test contexts share a database but differ in their outbound integrations, the split falls out of step two. Both contexts hold the same `PostgresDb`, so the user operations are shared, while the email sending genuinely differs:

```rust
#[derive(HasField)]
pub struct ProductionApp {
    pub database: PostgresDb,
    pub smtp: SmtpClient,
}

#[derive(HasField)]
pub struct TestApp {
    pub database: PostgresDb,
    pub sent_emails: RefCell<Vec<String>>,
}
```

The database-backed operations become components with one provider each, generic over any context carrying a `database` field, so both contexts wire the same provider:

```rust
#[cgp_impl(new CreateUserWithPostgres)]
impl UserCreator {
    fn create_user(&self, #[implicit] database: &PostgresDb, username: &str, email: &Email) -> Result<User, Error> {
        // ...
    }
}

delegate_components! { ProductionApp { UserCreatorComponent: CreateUserWithPostgres } }
delegate_components! { TestApp       { UserCreatorComponent: CreateUserWithPostgres } }
```

The email capability differs per context and has exactly one implementation on each side, so it needs no provider at all — a consumer trait is an ordinary trait, and implementing it directly is the lowest rung that expresses the case:

```rust
#[cgp_component(EmailSender)]
pub trait CanSendEmail {
    fn send_email(&self, to: &str, body: &str) -> Result<(), Error>;
}

impl CanSendEmail for ProductionApp {
    fn send_email(&self, to: &str, body: &str) -> Result<(), Error> { /* over SMTP */ }
}

impl CanSendEmail for TestApp {
    fn send_email(&self, to: &str, body: &str) -> Result<(), Error> { /* record for assertions */ }
}
```

Reach for named providers and wiring on that half only when a second context wants the same implementation, or when the implementation should be composable — at which point `#[cgp_impl(new SendViaSmtp)]` and a wiring line replace the direct impl with no change to the trait or its callers. The direct impl is therefore a starting point rather than a dead end.

## What the split costs

**Splitting a trait reaches every caller of it, and that cost is why the decision is worth making before the trait is written rather than after.** The methods move to new traits, so every call site imports a different trait and every existing implementation is rewritten. On a trait that most of a codebase depends on, that is a real refactoring with no partial credit, and a team may reasonably judge it too expensive to schedule — which is an argument for sizing components correctly the first time, not an argument that the monolith was fine.

The second cost is arithmetic: one component per operation means more components to wire and to check, and a flat `delegate_components!` table stops being readable as they accumulate. Both halves of that growth have answers, which is why it should not decide the question. [Namespaces and prefixes](namespaces-and-prefixes.md) group components under paths and lift a backend's choices into a reusable table so the top-level wiring stays short, and a [`check_components!`](../reference/macros/check_components.md) block lists the new components in array form so verifying twelve costs no more attention than verifying four. Weigh the split against the refactoring, not against the wiring, because the wiring is the part that has a remedy.

One observation makes the trade-off easier to hold: **a component with a single capability never needs splitting again.** A trait's definition is stable exactly when it has nothing left to divide, so the discipline is to notice the moment a second method's dependencies diverge from the first's, and to split then, while the trait has few enough callers that splitting is cheap.

## Related guides

- [Choosing a component's shape](choosing-a-component-shape.md) — the decision that comes first: what goes in `Self`, and whether the capability targets `Self` or a type parameter.
- [Writing providers](writing-providers.md) — the `#[cgp_impl]` form each provider above is written in, including the `#[cgp_impl(Self)]` direct impl.
- [Organizing wiring with namespaces and prefixes](namespaces-and-prefixes.md) — the answer to the component count a split produces.
- [Modularity hierarchy](../concepts/modularity-hierarchy.md) — the ladder, and rung 2 as the honest destination for a trait whose providers nothing would reuse.
- [Higher-order providers](../concepts/higher-order-providers.md) — the composition a small component buys and a monolithic one taxes.
- [Guides summary](README.md#summary) — the cheat-sheet across all the guides.
