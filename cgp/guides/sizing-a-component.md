# Sizing a component

What belongs in one component is the set of items a single provider choice should decide *together* — often one method, sometimes a method and the type it returns, and rarely a whole entity's surface — and this guide is about making that grouping deliberately, then splitting a trait that has already grouped too much.

**Nothing in CGP limits how many items a trait may declare.** A component's trait is an ordinary Rust trait: it can carry as many methods, associated types, and consts as you like, `#[cgp_component]` generates the provider trait from all of them, and a provider implements all of them. CGP's own library does this — [`CanCompute`](../reference/components/computer.md), [`CanHandle`](../reference/components/handler.md), and [`CanProduce`](../reference/components/producer.md) each declare an associated `Output` type alongside their method. So this guide is a cost curve rather than a rule, and the curve is what matters: items that share a provider choice cost nothing to group, while items that answer to different choices cost reuse in three specific ways worth knowing before you pay them.

The snippets below draw on two kinds of context, and the difference matters when reading them. The shape components are about the data, so their contexts are **value contexts** — a `Rectangle` *is* the thing whose area is computed — while the service components are about the application, so the contexts actually wired here are **environmental** ones: `CloudApp`, `ProductionApp`, and `TestApp` stand for a deployment or a test harness. Every component is self-targeted; nothing crosses into a target parameter. The shapes themselves are the subject of [choosing a component's shape](choosing-a-component-shape.md).

## Group the items one provider choice decides together

**A component is the unit of wiring, so the question to ask is not "how many methods?" but "how many independent choices?"** Everything inside one component is answered by one provider, so two items in one component can never come from two different providers. Group the items that a single decision settles, and separate the ones that different decisions settle.

That principle is what makes the count vary rather than being fixed at one. Sending an email is one decision, so `CanSendEmail` holds one method:

```rust
#[cgp_component(EmailSender)]
pub trait CanSendEmail {
    fn send_email(&self, to: &str, body: &str) -> Result<(), Error>;
}
```

Most application capabilities are like this — create a user, calculate an area, load the config — which is why most components you write and read hold a single method. The count is a consequence of the principle, not the principle itself.

## When several items belong in one component

**Two groupings recur, and in both the extra items are decided by the same choice as the method, so keeping them together is right rather than merely permitted.**

The first is **a method together with the associated type it produces.** A provider that answers *how* also answers *what comes back*, so the type cannot be chosen separately. This is exactly what CGP's handler family does — `CanCompute` declares `type Output` beside `compute` — and it is equally right in your own code. Two providers here choose a database engine and, inescapably, the row type that engine returns:

```rust
#[cgp_component(DatabaseQuerier)]
pub trait CanQueryDatabase {
    type Row;

    fn query(&self, sql: &Sql) -> Vec<Self::Row>;
}

#[cgp_impl(new QueryWithPostgres)]
impl DatabaseQuerier {
    type Row = PgRow;

    fn query(&self, #[implicit] database: &PostgresDb, sql: &Sql) -> Vec<PgRow> { /* ... */ }
}

#[cgp_impl(new QueryWithSqlite)]
impl DatabaseQuerier {
    type Row = SqliteRow;

    fn query(&self, #[implicit] database: &SqliteDb, sql: &Sql) -> Vec<SqliteRow> { /* ... */ }
}

delegate_components! { CloudApp    { DatabaseQuerierComponent: QueryWithPostgres } }
delegate_components! { EmbeddedApp { DatabaseQuerierComponent: QueryWithSqlite } }
```

Splitting `Row` into its own [`#[cgp_type]`](../reference/macros/cgp_type.md) component would be the wrong move *here*, because it would let a context wire the Postgres querier with the SQLite row type and only find out later. Reach for a separate abstract type when several components must agree on it — which is the case [naming a type dependency](naming-a-type-dependency.md) covers — and keep it local when one provider decides it alone.

The second is **a getter component grouping several field reads.** A getter is answered by the *method's own name* rather than by a strategy, so one [`UseFields`](../reference/providers/use_fields.md) provider satisfies every method of the trait at once by reading the same-named field for each, and there is no choice to split apart:

```rust
#[cgp_getter(DimensionsGetter)]
pub trait HasDimensions {
    fn width(&self) -> &f64;
    fn height(&self) -> &f64;
}
```

Splitting that trait multiplies declarations and wiring entries and buys nothing. The one thing the grouping costs is the single-field providers: [`UseField`](../reference/providers/use_field.md) and [`WithProvider`](../reference/providers/with_provider.md) are emitted only for a getter trait with exactly one method, since both presuppose one field to read, so a getter that must be wired to a *differently named* field needs a component of its own. Note also that the default way to read a field is an [`#[implicit]`](../reference/attributes/implicit.md) argument rather than a getter trait at all, per [reading context fields](reading-context-fields.md); this case is about the narrow situations that genuinely need the trait.

## What grouping unrelated decisions costs

**When items in one component answer to different choices, the component pays in three ways, and the cost rises with how unrelated they are rather than with the count.** Two closely related methods cost almost nothing; five methods spanning storage, presentation, and geometry cost a great deal. The three costs arrive at different times, and only the first is obvious.

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

The reverse holds too, which is the same cost read from the other side: there is no way to grant one method a capability without granting it to the whole component, so capability isolation becomes impossible. The [social media app](../../examples/social-media-app.md) example shows what the split buys — once deleting a post is its own component, code that should only read and write posts can be handed the getter and the updater and never receive the destructive delete.

**A [higher-order provider](../concepts/higher-order-providers.md) must implement every item, including the ones it does not care about.** This is the cost that arrives second and bites hardest, because wrapping is where CGP's composition pays. A component holding one decision wraps in four lines, and the wrapper composes over any inner provider:

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

The passthrough grows with the trait, and every method added to `Shape` later must be added to this wrapper and to every other wrapper written over it. The `describe` body is ceremony that exists only because unrelated decisions share a component. Note the contrast with the `Row` case above: there the associated type is carried *by* the decision the wrapper is making, so it costs nothing; here `describe` is a second decision the wrapper has no view on.

**A context that needs part of the surface must still supply all of it.** Every method and every associated type has to be answered, so grouping unrelated concerns forces stubs on the contexts and providers that use only some of them. Fold rotation into the same `Shape` trait and it brings an associated type with it:

```rust
#[cgp_component(ShapeProvider)]
pub trait Shape {
    type Angle;

    fn rotate(&mut self, angle: Self::Angle);

    // area, perimeter, and describe as above
}
```

A provider that only computes areas must now pick some `Angle` it never uses and write a `rotate` body it has no meaning for — in practice a placeholder type and an `unimplemented!()`. That pattern is common in real codebases, most often in the mock contexts written for tests, and it is a reliable sign that one component is carrying two decisions. Splitting `Angle` out with [`#[cgp_type]`](../reference/macros/cgp_type.md) and `rotate` into its own component lets an area-only context ignore both entirely.

## The entity trait is the shape you will reach for anyway

**A trait grouping every operation of an entity is the natural design for anyone with an object-oriented background, and it is worth being honest that the recommendation here cuts against a habit most developers hold for good reasons.** `Shape` with `area`, `perimeter`, `scale`, and `rotate` describes a coherent thing, gives a team one word to talk about, and matches how most people were taught to model a domain. A behavior-named component like `AreaCalculator` feels thinner and less principled by comparison, so the entity trait is what an author writes unless something stops them — and CGP will compile it.

The trait's own name is the cheapest signal that the grouping has gone past one decision. CGP's consumer traits read as verbs — `CanCreateUser`, `CanCalculateArea` — precisely because a capability is something a context *does*; a consumer trait named after a noun is usually several decisions sharing one component. The diagnostic behind the naming is more direct: **would any provider for this trait ever be reused, whole, by a second context?** If the honest answer is no, the trait's providers are not reusable units and the CGP machinery around them is not paying for itself — at which point implementing the trait directly on each concrete type, with no component at all, is the better design. That is a real outcome and not a failure: it is rung 2 of the [modularity hierarchy](../concepts/modularity-hierarchy.md), one implementation per type, chosen deliberately rather than settled for.

## Split an existing trait along the axis its contexts differ on

**When a component has grown past one decision and it matters, do not redesign it in the abstract — split it along the axis on which the contexts you actually want differ.** A split only pays where it creates a choice, so the contexts decide where the seams go. The procedure is four steps.

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
impl CanSendEmail for ProductionApp {
    fn send_email(&self, to: &str, body: &str) -> Result<(), Error> { /* over SMTP */ }
}

impl CanSendEmail for TestApp {
    fn send_email(&self, to: &str, body: &str) -> Result<(), Error> { /* record for assertions */ }
}
```

Reach for named providers and wiring on that half only when a second context wants the same implementation, or when the implementation should be composable — at which point `#[cgp_impl(new SendViaSmtp)]` and a wiring line replace the direct impl with no change to the trait or its callers. The direct impl is a starting point rather than a dead end.

## What the split costs

**Splitting a trait reaches every caller of it, and that cost is why the grouping is worth getting right before the trait is written rather than after.** The methods move to new traits, so every call site imports a different trait and every existing implementation is rewritten. On a trait most of a codebase depends on, that is a real refactoring with no partial credit, and a team may reasonably judge it too expensive to schedule — which is an argument for grouping by decision the first time, not an argument that the monolith was fine.

The second cost is arithmetic: one component per decision means more components to wire and to check, and a flat `delegate_components!` table stops being readable as they accumulate. Both halves of that growth have answers, which is why neither should decide the question. [Namespaces and prefixes](namespaces-and-prefixes.md) group components under paths and lift a backend's choices into a reusable table so the top-level wiring stays short, and a [`check_components!`](../reference/macros/check_components.md) block lists components in array form, so verifying twelve costs no more attention than verifying four. Weigh the split against the refactoring, not against the wiring, because the wiring is the part that has a remedy.

One observation makes the trade-off easier to hold: **a component holding exactly one decision never needs splitting again.** A trait's definition is stable when it has nothing left to divide, so the discipline is to notice the moment a second decision arrives — a method whose dependencies diverge from its neighbours', or an associated type more than one provider would want to fix independently — and to split then, while the trait has few enough callers that splitting is cheap.

## Related guides

- [Choosing a component's shape](choosing-a-component-shape.md) — the decision that comes first: what goes in `Self`, and whether the capability targets `Self` or a type parameter.
- [Naming a type dependency](naming-a-type-dependency.md) — when an associated type belongs in its own abstract-type component rather than inside the component that produces it.
- [Writing providers](writing-providers.md) — the `#[cgp_impl]` form each provider above is written in, including the `#[cgp_impl(Self)]` direct impl.
- [Organizing wiring with namespaces and prefixes](namespaces-and-prefixes.md) — the answer to the component count a split produces.
- [Modularity hierarchy](../concepts/modularity-hierarchy.md) — the ladder, and rung 2 as the honest destination for a trait whose providers nothing would reuse.
- [Higher-order providers](../concepts/higher-order-providers.md) — the composition a single-decision component buys and a many-decision one taxes.
- [Guides summary](README.md#summary) — the cheat-sheet across all the guides.
