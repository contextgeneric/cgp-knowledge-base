# Naming a type dependency

When an implementation needs a type it does not fix — a database handle, a transaction, a scalar, an error — that type has to live somewhere, and this guide is about choosing between the two places CGP offers instead of the one vanilla Rust offers.

The decision matters because the obvious answer is the expensive one. A generic parameter on the trait works, and it makes every caller and every intermediate capability that never touches the type declare it anyway and repeat its bounds. The two CGP forms both avoid that, and they differ in what they let you *do* with the type afterwards, so picking between them is worth doing deliberately rather than by reaching for whichever construct is already in the file.

All snippets below wire an **environmental context** — `App` stands for the application and carries the database handle — and every capability is **self-targeted**. Nothing crosses into another shape, so the difference between the tiers is only where the type lives. The shapes themselves are the subject of [choosing a component's shape](choosing-a-component-shape.md).

## Start by inferring the type from a field

**When the type appears only in [`#[implicit]`](../reference/attributes/implicit.md) arguments, declare it with [`#[impl_generics]`](../reference/macros/cgp_fn.md) and let the field's type supply it.** The parameter lands on the generated impl alone, so the trait is unparameterized and no caller mentions it:

```rust
#[cgp_fn]
#[impl_generics(Db: Database)]
pub fn row_count(&self, #[implicit] database: &Pool<Db>) -> u64 { /* ... */ }
```

`RowCount` has no type parameter, and a context becomes eligible purely by carrying a `database` field: an `App` holding a `Pool<Postgres>` resolves `Db = Postgres`, an embedded context holding a `Pool<Sqlite>` resolves `Db = Sqlite`, and neither is wired for it. This is the form to reach for first, and not only because it is shorter. It is the one a reader understands on sight — *this works with any `database` field of a compatible type* — with no trait to declare, no wiring line, and no associated-type syntax, which makes it the honest entry point to abstracting a type at all. [Profile picture lookup](../../examples/profile-picture.md) works the same form against real `sqlx` bounds.

The cost is that the type is **concealed rather than named**. It exists only where a value of it flows through an implicit argument, so nothing else can refer to it: not a second provider, not another component, and not the signature of this one.

## The two conditions that force a climb

**Climb to an abstract type when either of two things is true, and stay on `#[impl_generics]` when neither is.** Both conditions are about needing to *name* the type somewhere the inferred form cannot reach.

The first is that **the type appears in the capability's public signature**. An impl-only parameter is not in scope in the generated trait, so a method that returns one does not compile — `fetch_row` returning `Db::Row` fails with `E0433: cannot find type 'Db' in this scope`, pointed at the return type. The same holds for an explicit (non-implicit) parameter. This is the condition that arrives the moment a capability hands a value of the type back to its caller: opening a transaction, producing a connection, returning a decoded row.

The second is that **two types have to agree**. A transaction type only means anything relative to a database, so the capability that opens one and the capability that commits it must be talking about the same transaction. An inferred parameter cannot express that, because each impl infers its own.

## Do not answer either condition with a trait generic

**Declaring the type as a generic parameter on the capability is the form to avoid, and it is what vanilla Rust leaves you with.** A generic on a [`#[cgp_fn]`](../reference/macros/cgp_fn.md) goes onto the trait *and* the impl, so the type is nameable in the signature — and every capability built on top of it inherits the parameter and its bounds:

```rust
#[cgp_fn]
pub fn begin_transaction<Db>(&self, #[implicit] database: &Pool<Db>) -> Tx<Db>
where
    Db: Database,
{ /* ... */ }

#[cgp_fn]
#[uses(BeginTransaction<Db>)]
pub fn run_unit_of_work<Db>(&self) -> u64
where
    Db: Database,
{ /* ... */ }
```

`run_unit_of_work` never mentions a database, yet it declares `Db`, repeats `Db: Database`, and passes the parameter on to anything that calls it. That propagation is the whole cost, and it compounds: a second such type doubles it, and a bound relating the two has to be restated at every layer in between.

There is a subtler defect than the verbosity. `<Db>` on the trait says the *caller* chooses the database type, when the application is what determines it. The signature misplaces the decision, which is why no amount of tidying makes this form right.

## Climb to an abstract type

**Declare the type as an [abstract type](../concepts/abstract-types.md) with [`#[cgp_type]`](../reference/macros/cgp_type.md), import it with [`#[use_type]`](../reference/attributes/use_type.md), and let the context supply it by wiring.** The type is then nameable everywhere *and* threaded nowhere, because it is determined by the context rather than passed by a caller:

```rust
#[cgp_type]
pub trait HasDbType {
    type Db: Database;
}

#[cgp_type]
pub trait HasTransactionType {
    type Transaction;
}

#[cgp_component(TransactionStarter)]
#[use_type(HasTransactionType.Transaction, HasErrorType.Error)]
pub trait CanBeginTransaction {
    fn begin_transaction(&self) -> Result<Transaction, Error>;
}

#[cgp_component(TransactionCommitter)]
#[use_type(HasTransactionType.Transaction, HasErrorType.Error)]
pub trait CanCommitTransaction {
    fn commit_transaction(&self, transaction: Transaction) -> Result<(), Error>;
}
```

A bound intrinsic to the type moves onto its declaration once — `type Db: Database` — instead of being restated in every provider's `where` clause, and it is checked against the concrete type at the wiring site. A bound *relating* two abstract types stays where it belongs, on the provider that depends on the relationship, written over both bare aliases:

```rust
#[cgp_impl(new BeginPooledTransaction)]
#[use_type(HasDbType.Db, HasTransactionType.Transaction, HasErrorType.Error)]
impl TransactionStarter
where
    Transaction: CanBeginFrom<Db>,
{
    fn begin_transaction(&self, #[implicit] database: &Pool<Db>) -> Result<Transaction, Error> {
        Ok(Transaction::begin_from(database))
    }
}
```

The provider names both abstract types, reads the pool from a field whose type is expressed in terms of one of them, and stays generic over every context. Two payoffs follow from the same wiring. Every capability that mentions `Transaction` means the context's `Transaction`, so the starter and the committer agree with nothing to coordinate — the type-level counterpart of the way a shared [`HasErrorType`](../reference/components/has_error_type.md) makes every fallible provider agree on one error. And the intermediate capability that composes them names neither type:

```rust
#[cgp_fn]
#[uses(CanBeginTransaction, CanCommitTransaction)]
#[use_type(HasErrorType.Error)]
pub fn run_unit_of_work(&self) -> Result<(), Error> {
    let transaction = self.begin_transaction()?;
    self.commit_transaction(transaction)?;
    Ok(())
}
```

Compare that with the `run_unit_of_work<Db>` above. The body is the same, the signature carries nothing, and adding a third abstract type to the providers beneath it would leave this function untouched — where adding a third generic parameter would change its signature and every caller's.

The context supplies both types and the handle, in one table:

```rust
#[derive(HasField)]
pub struct App {
    pub database: Pool<Postgres>,
}

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<String>,
        DbTypeProviderComponent: UseType<Postgres>,
        TransactionTypeProviderComponent: UseType<Tx<Postgres>>,
        TransactionStarterComponent: BeginPooledTransaction,
        TransactionCommitterComponent: CommitPooledTransaction,
    }
}
```

The wiring is also where the inferred form's last piece of slack disappears. Because the provider's implicit argument is typed `&Pool<Db>`, the field it requires is one holding a pool for the context's *wired* `Db` — so a context that wires `Db` to one engine while carrying a pool for another fails its [check](../reference/macros/check_components.md) with `E0271`, reported on the check entry and naming both types. Under `#[impl_generics]` the two could never disagree, because there was only ever one of them; here the agreement is stated and verified rather than assumed.

## Four things that bite

Four details are easy to get wrong, and three of them are about naming rather than design.

**Do not give the abstract type the same name as the trait bounding it.** Declaring `type Database: Database` fails outright with `E0404: expected trait, found type parameter 'Database'`, because the bound resolves to the associated type being declared rather than to the trait of that name in scope. Name the type so the two differ — `type Db: Database` — which is also why an abstract database type reads better as `Db` than as `Database`.

**The wiring key comes from the associated type, not the trait.** `#[cgp_type]` keys the generated names off the associated type, so `type Db` yields `DbTypeProviderComponent` and `type Transaction` yields `TransactionTypeProviderComponent` — not `HasDbTypeComponent`.

**`ErrorTypeProviderComponent` is not in the prelude.** Import it from `cgp::core::error`, along with any [error provider](../reference/providers/error_providers.md) the context wires.

**An alias standing alone as an expression is not the abstract type.** `#[use_type]` substitutes the alias in every type position — signatures, `where` predicates, `let` annotations — and as the qualifier of an expression path, so `Transaction::begin_from(pool)` resolves. What it deliberately leaves alone is a bare, single-segment alias in expression position, because that names a *value* and an abstract type can never be one. So an alias that shares its name with a unit struct the body constructs will mean the abstract type in the signature and the struct in the body, which compiles and is almost never what you want — name them apart.

## Related guides

- [Choosing a component's shape](choosing-a-component-shape.md) — the decision that comes first: what goes in `Self`, and whether the capability targets `Self` or a parameter.
- [Importing abstract types](importing-abstract-types.md) — the `#[use_type]` forms to use once you have decided a type should be abstract, including the `in Context` and equality forms.
- [Reading context fields](reading-context-fields.md) — the value-level counterpart, where the same reasoning picks `#[implicit]` over a getter trait.
- [Declaring a provider's dependencies](declaring-dependencies.md) — where a bound belongs once the type it constrains has a home.
- [Impl-side dependencies](../concepts/impl-side-dependencies.md) — the mechanism behind all three levels: a requirement carried on the impl rather than the interface, so it never reaches a caller.
- [Guides summary](README.md#summary) — the cheat-sheet across all the guides.
