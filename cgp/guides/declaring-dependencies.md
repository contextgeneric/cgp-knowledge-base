# Declaring a provider's dependencies

A provider states what it needs from its context in its `where` clause, and this guide is about writing those needs as attributes that read like imports rather than as hand-written trait bounds.

This guide follows on from [writing the provider header](writing-providers.md), which leaves the bounds off the header for these attributes to supply.

## Declare dependencies with `#[uses]` and `#[use_provider]`

State a provider's impl-side dependencies with [`#[uses(...)]`](../reference/attributes/uses.md) and [`#[use_provider(...)]`](../reference/attributes/use_provider.md) rather than hand-written `where` clauses, so a dependency reads like a `use` import instead of a trait bound. A trait the body calls on the context is imported with `#[uses]`: writing `#[uses(CanCalculateArea)]` adds `Self: CanCalculateArea` to the generated impl. An inner provider a [higher-order provider](../concepts/higher-order-providers.md) delegates to is declared with `#[use_provider]`: writing `#[use_provider(InnerCalculator: AreaCalculator)]` adds the bound `InnerCalculator: AreaCalculator<Self>`, filling in the `<Self>` argument that a provider trait inserts. The hand-written `where` forms:

```rust
#[cgp_impl(new ScaledArea<InnerCalculator>)]
impl<Context, InnerCalculator> AreaCalculator for Context
where
    Self: HasField<Symbol!("scale_factor"), Value = f64>,
    InnerCalculator: AreaCalculator<Self>,
{
    fn area(&self) -> f64 { /* ... */ }
}
```

become:

```rust
#[cgp_impl(new ScaledArea<InnerCalculator>)]
#[use_provider(InnerCalculator: AreaCalculator)]
impl<InnerCalculator> AreaCalculator {
    fn area(&self, #[implicit] scale_factor: f64) -> f64 { /* ... */ }
}
```

Both attributes desugar to the same `where` predicates they replace. When a provider imports several traits, list them in one `#[uses]` separated by commas, as in `#[uses(CanTransferMoney, CanRaiseHttpError<ErrUnauthorized, String>)]`, rather than stacking the attribute; one combined attribute reads as a single dependency list. `#[use_provider]` is the exception: one attribute binds one provider, with several bounds on it joined by `+` (`#[use_provider(Inner: TraitA + TraitB)]`), and several providers take one attribute each. A comma fails with ``expected `+` ``.

**The imported bound need not be a CGP trait.** An ordinary Rust trait the provider requires of its context is imported exactly the same way: `#[uses(Display)]` and `#[uses(AsRef<[u8]>)]` are preferred over `where Self: Display` and `where Self: AsRef<[u8]>`, because the attribute declares a dependency on `Self` regardless of where the trait came from, and using it for a familiar trait shows that it is not CGP-specific machinery. Reserve the hand-written `where` clause for the bounds `#[uses]` genuinely cannot carry, listed below and in the [guides summary](README.md#summary).

`#[uses(...)]` accepts any bound a `where` clause allows, including one with associated-type equality, though the simple `Trait<Params>` form is the idiomatic one. One case moves elsewhere: when a bound pins an *abstract type*, such as `Self: HasErrorType<Error = AppError>`, express it with the [`#[use_type]` equality form](importing-abstract-types.md) rather than spelling the equality in `#[uses]` or a hand-written `where`. Only equality on a trait that is not a `#[use_type]` import (`Iterator<Item = u8>`) stays an explicit `where` clause, where it reads more clearly than crammed into an import-shaped attribute.

When a `#[uses]`-imported trait carries an abstract-type component as a *supertrait*, its associated type reaches the impl body, but not a signature: `#[uses]` bounds only the impl, so a `#[cgp_fn]` signature naming `Self::Foo` fails with `E0220`. Import the type explicitly with [`#[use_type]`](importing-abstract-types.md). If `CanCreateFoo` has `HasFooType` as a supertrait, write `#[uses(CanCreateFoo)]` *and* `#[use_type(HasFooType.Foo)]`, with `#[uses]` declaring the trait dependency and `#[use_type]` declaring the type dependency. See [importing abstract types](importing-abstract-types.md#re-import-a-type-that-arrives-through-a-supertrait).

## Related guides

- [Writing providers](writing-providers.md) — the `#[cgp_impl]` header these attributes attach to.
- [Importing abstract types](importing-abstract-types.md) — where an abstract-type pin belongs instead of `#[uses]`.
- [Guides summary](README.md#summary) — the cheat-sheet across all the guides, and the list of cases where an explicit `where` clause is still right.
