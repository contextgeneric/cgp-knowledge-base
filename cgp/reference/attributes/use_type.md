# `#[use_type]`

`#[use_type]` imports an abstract associated type into a CGP definition and rewrites every bare
mention of it into the fully qualified `<Self as Trait>::AssocType` form, adding the trait as a
supertrait or bound at the same time.

## Purpose

`#[use_type]` removes the boilerplate of referring to an abstract type defined on another trait. A
CGP trait often needs a type that lives elsewhere, such as a `Scalar` from `HasScalarType` or an
`Error` from `HasErrorType`, and Rust requires each reference to be written as
`<Self as HasScalarType>::Scalar`, because a bare `Scalar` names nothing. Writing that prefix in the
return type, in each implicit argument, and in the body is verbose and easy to get wrong.

The attribute lets the author write the bare `Scalar` everywhere. The type is declared once, as
`#[use_type(HasScalarType.Scalar)]`, and the macro replaces each standalone `Scalar` with
`<Self as HasScalarType>::Scalar` and adds `HasScalarType` where the definition needs it. The bare
name reads like a generic parameter but resolves to the qualified associated type.

The qualified rewrite also expresses things the bare form cannot. Because the macro always emits the
full `<Context as Trait>::Type` path, nested abstract types compose without the author spelling a
path, an abstract type can be taken from a type parameter instead of `Self`, and equalities between
two imported types can be stated declaratively. That is why the `/cgp` skill recommends
`#[use_type]` as the default way to import an abstract type.

## Syntax

`#[use_type]` is an outer attribute beside the host macro. It is accepted by
[`#[cgp_fn]`](../macros/cgp_fn.md), [`#[cgp_impl]`](../macros/cgp_impl.md), and
[`#[cgp_component]`](../macros/cgp_component.md), and by [`#[cgp_type]`](../macros/cgp_type.md),
[`#[cgp_getter]`](../macros/cgp_getter.md), and
[`#[cgp_auto_getter]`](../macros/cgp_auto_getter.md), which share `#[cgp_component]`'s attribute
collector. Its argument names a trait, then a `.`, then one or more of the trait's associated types:

```rust
#[use_type(HasScalarType.Scalar)]
```

The rewrite target defaults to `Self`, so this rewrites `Scalar` to
`<Self as HasScalarType>::Scalar`. The separator is `.` rather than `::`, so the trait itself can be
a full path or carry generic arguments with ordinary `::`.

A spec combines up to four features, which may be used together:

- **A trait path or generic trait.** `#[use_type(errors::HasErrorType.Error)]` imports from a trait
  named by path without bringing it into scope, and `#[use_type(HasFooType<X>.Foo)]` imports from
  one instantiation, rewriting `Foo` to `<Self as HasFooType<X>>::Foo`. A trait argument may itself
  be another import's alias, as Expansion describes. This lets one associated type be imported from
  two instantiations under different names, as in
  `#[use_type(HasFooType<X>.{Foo as FooX}, HasFooType<Y>.{Foo as FooY})]`.
- **A braced list with renames.** `#[use_type(HasFooType.{Foo, Bar as Baz})]` imports `Foo` under
  its own name and `Bar` under the alias `Baz`.
- **An equality pin.** `#[use_type(HasScalarType.{Scalar = f64})]` imports `Scalar` and also
  constrains it, emitting `Self: HasScalarType<Scalar = f64>`.
- **A foreign context.** A trailing `in Context` clause changes the rewrite target from `Self` to a
  named type: `#[use_type(HasScalarType.Scalar in Types)]` rewrites `Scalar` to
  `<Types as HasScalarType>::Scalar`. `Types` is usually a generic parameter, so a trait can take an
  abstract type from a parameter instead of the implementing context. The clause scopes over the
  whole spec, so `#[use_type(HasFooType.{Foo, Bar} in Ctx)]` projects both types against `Ctx`.
  Because `in` is a reserved keyword, it cannot be confused with a name, and it matches the `in` of
  `#[prefix(@path in Namespace)]`.

When a definition imports types from several traits, list the specs in one attribute, separated by
commas, as in `#[use_type(HasUserIdType.UserId, HasCurrencyType.Currency, HasErrorType.Error)]`, so
they read as one import list. Stacked `#[use_type]` attributes behave identically, because the host
collects every attribute's specs before resolving any of them, so an alias imported by one attribute
is available to another. Use a second attribute only when there is a reason to.

### Restrictions

Three restrictions guard against imports the macro cannot lower unambiguously:

- **No two imports may share a bare name or alias**, whether in different specs or in one braced
  list, on any host. The substitution could pick only one and would silently drop the other, so a
  collision fails with `Multiple abstract types cannot share the same identifier or alias`.
- **The equality form is rejected on `#[cgp_component]`** with
  `Type equality constraints cannot be used in component trait definition`, because a pin is a
  decision a provider makes, not a requirement on every provider. It belongs on `#[cgp_fn]` and
  `#[cgp_impl]`, where it becomes a `where` bound.
- **Imports may not resolve through one another in a cycle**, since a cycle leaves no order to
  resolve them in, as Expansion describes.

## Syntax Grammar

The grammar covers the tokens inside `#[use_type(...)]`, a comma-separated list of specs:

```ebnf
UseTypeArgs  -> UseTypeSpec ( `,` UseTypeSpec )* `,`?

UseTypeSpec  -> TraitPath `.` TypeItems ( `in` ContextPath )?

ContextPath  -> TypePath
TraitPath    -> TypePath

TypeItems    -> UseTypeIdent
              | `{` ( UseTypeIdent ( `,` UseTypeIdent )* `,`? )? `}`

UseTypeIdent -> IDENTIFIER ( `as` IDENTIFIER )? ( `=` Type )?
```

`ContextPath` and `TraitPath` are Rust `TypePath`s, whose last segment may carry angle-bracketed
generic arguments. Their `::` segments belong to the path, and the `.` after the trait starts the
associated-type list. An omitted `in ContextPath` makes `Self` the target. In each `UseTypeIdent`,
the first identifier is the associated type's own name, `as` gives it a local alias, and `= Type`
pins it, which is accepted on `#[cgp_fn]` and `#[cgp_impl]` and rejected on `#[cgp_component]`. An
empty braced list parses: it imports no names but still adds the trait's bound.

## Expansion

`#[use_type]` runs before the rest of its host in three steps. It first grounds each spec, resolving
any `in Context` or trait argument that names another import into a fully qualified path. It then
substitutes every matching bare type name in one pass. Finally it adds the bounds: on a generated
trait, a supertrait for a `Self` import or a `where` predicate for a foreign one; on an impl, a
`where` predicate for every import. Consider this `#[cgp_fn]`:

```rust
pub trait HasScalarType {
    type Scalar: Clone + Mul<Output = Self::Scalar>;
}

#[cgp_fn]
#[use_type(HasScalarType.Scalar)]
fn rectangle_area(
    &self,
    #[implicit] width: Scalar,
    #[implicit] height: Scalar,
) -> Scalar {
    width * height
}
```

The macro rewrites every standalone `Scalar` to `<Self as HasScalarType>::Scalar`, adds
`HasScalarType` as a supertrait of the generated trait and as a bound on its impl, and then expands
the `#[cgp_fn]` as usual:

```rust
pub trait RectangleArea: HasScalarType {
    fn rectangle_area(&self) -> <Self as HasScalarType>::Scalar;
}

impl<__Context__> RectangleArea for __Context__
where
    Self: HasField<Symbol!("width"), Value = <Self as HasScalarType>::Scalar>
        + HasField<Symbol!("height"), Value = <Self as HasScalarType>::Scalar>,
    Self: HasScalarType,
{
    fn rectangle_area(&self) -> <Self as HasScalarType>::Scalar {
        let width: <Self as HasScalarType>::Scalar =
            self.get_field(PhantomData::<Symbol!("width")>).clone();
        let height: <Self as HasScalarType>::Scalar =
            self.get_field(PhantomData::<Symbol!("height")>).clone();
        width * height
    }
}
```

### What is rewritten

The substitution matches single-segment type paths without arguments whose name is an imported name
or alias. A bare `Scalar` in a return type, an implicit argument, a `where` predicate, or a `let` in
the body is rewritten the same way, which is what lets nested uses work without the author writing a
path. On `#[cgp_impl]` it also reaches the provider trait's arguments in the impl header, so
`impl FooProvider<Error>` under `#[use_type(HasErrorType.Error)]` implements the provider trait at
the context's error type rather than at a type named `Error`.

The rewrite also reaches an alias that qualifies an expression path, so the alias means one thing
throughout the definition. `Transaction::begin_from(pool)` becomes
`<<Self as HasTransactionType>::Transaction>::begin_from(pool)`, the qualified-type form, since
`<Self as Trait>::Assoc::method` is not valid syntax; an associated const reads the same way. The
one position left alone is a bare, single-segment alias in expression position, which names a value,
something an abstract type can never be. So an alias that shares its name with a unit struct the
body constructs still resolves to the struct: an alias as a type or as a path qualifier is the
abstract type, and an alias standing alone as an expression is whatever value that name denotes.

A construct's own local associated types are not imported, so they always stay qualified as
`Self::Assoc`. A `#[cgp_component]` trait or a `#[cgp_impl]` provider that declares its own
`type Output` refers to it as `Self::Output`, and it is never listed in `#[use_type]`. This is why a
signature like `Result<Self::Output, Error>` is idiomatic: the local `Self::Output` stays qualified
while the imported `Error`, from `#[use_type(HasErrorType.Error)]`, is written bare. A bare `Output`
would name nothing, since the substitution has no entry for it.

### On a component

On `#[cgp_component]`, the trait is added as a supertrait, and the rewrite touches the trait's own
signatures. Given:

```rust
#[cgp_component(AreaCalculator)]
#[use_type(HasScalarType.Scalar)]
pub trait CanCalculateArea {
    fn area(&self) -> Scalar;
}
```

the `#[use_type]` phase rewrites the trait into the following before the component macro continues:

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea: HasScalarType {
    fn area(&self) -> <Self as HasScalarType>::Scalar;
}
```

### A foreign context

A supertrait is added only when the target is `Self`. With an `in Context` import the target is a
named type, so the macro adds a `Context: Trait` predicate instead. On `#[cgp_fn]` and `#[cgp_impl]`
the predicate lands in the impl's `where` clause, and on `#[cgp_component]` and `#[cgp_fn]` it is
also added to the generated trait's own `where` clause, because the trait's signatures now name
`<Context as Trait>::Assoc` and would not be well formed without it. So a component using the `in`
form need not bound its parameter by hand: `pub trait CanCalculateArea<Types>` is enough, and
`Types: HasScalarType` is supplied. An equality pin, by contrast, stays on the impl and is never
added to the trait.

This `#[cgp_fn]` imports `Scalar` from a generic parameter `Types`:

```rust
#[cgp_fn]
#[use_type(HasScalarType.Scalar in Types)]
pub fn rectangle_area<Types>(
    &self,
    #[implicit] width: Scalar,
    #[implicit] height: Scalar,
) -> Scalar
where
    Scalar: Mul<Output = Scalar> + Copy,
{
    let res: Scalar = width * height;
    res
}
```

Every `Scalar`, including those in the written `where` clause, becomes
`<Types as HasScalarType>::Scalar`, and `Types: HasScalarType` is added to both the trait's `where`
clause and the impl's, so the unbounded `<Types>` the author wrote is enough:

```rust
pub trait RectangleArea<Types>
where
    Types: HasScalarType,
{
    fn rectangle_area(&self) -> <Types as HasScalarType>::Scalar;
}

impl<__Context__, Types> RectangleArea<Types> for __Context__
where
    <Types as HasScalarType>::Scalar:
        Mul<Output = <Types as HasScalarType>::Scalar> + Copy,
    Self: HasField<Symbol!("width"), Value = <Types as HasScalarType>::Scalar>
        + HasField<Symbol!("height"), Value = <Types as HasScalarType>::Scalar>,
    Types: HasScalarType,
{
    fn rectangle_area(&self) -> <Types as HasScalarType>::Scalar {
        let width: <Types as HasScalarType>::Scalar =
            self.get_field(PhantomData::<Symbol!("width")>).clone();
        let height: <Types as HasScalarType>::Scalar =
            self.get_field(PhantomData::<Symbol!("height")>).clone();
        let res: <Types as HasScalarType>::Scalar = width * height;
        res
    }
}
```

### Equality pins

The equality form adds a constrained bound on top of the substitution.
`#[use_type(HasScalarType.{Scalar = f64})]` substitutes `Scalar` exactly as before, but emits
`Self: HasScalarType<Scalar = f64>` instead of the plain `Self: HasScalarType`, pinning the abstract
type to `f64`. When the imported trait is generic, the pin joins the trait's existing arguments, so
`#[use_type(HasFooType<u8>.{Foo = u32})]` emits `Self: HasFooType<u8, Foo = u32>`, the only spelling
Rust accepts for a bound that both instantiates a trait and pins its associated type. The binding
always names the associated type's real name, even when the import is aliased.

The right-hand side of a pin is itself substituted, so an imported alias is grounded wherever it
occurs inside it:

- **A pin whose target is another alias** ties two abstract types together:
  `#[use_type(HasBarType.{Bar as Baz = Foo}, HasFooType.Foo)]` emits
  `Self: HasBarType<Bar = <Self as HasFooType>::Foo>`.
- **A pin whose target mentions an alias** grounds it in place:
  `#[use_type(HasDbType.Db, HasTransactionType.{Transaction = Tx<Db>})]` emits
  `Self: HasTransactionType<Transaction = Tx<<Self as HasDbType>::Db>>`, and an alias inside a
  qualified path is grounded the same way, so `{Transaction = <Db as Database>::Transaction}`
  becomes `<<Self as HasDbType>::Db as Database>::Transaction`.

This resolution relies on aliases being unique, which the duplicate check guarantees. The one name
not substituted in a pin's right-hand side is the pinned alias itself, so a self-pin such as
`{Foo = Foo}` fails as an unresolved name rather than becoming a bound that says nothing.

### Grounding and order

Grounding reaches a trait's own generic arguments as well as an `in Context` clause, since both end
up inside the emitted `<Context as Trait<Args…>>::Assoc` path. So an alias may parameterize the
trait it is imported from: `#[use_type(HasDbType.Db, HasPoolType<Db>.Pool)]` projects against
`HasPoolType<<Self as HasDbType>::Db>`, in the rewritten signature and the added supertrait alike.
This composes with a pin, so `#[use_type(HasDbType.Db, HasPoolType<Db>.{Pool = u32})]` emits
`Self: HasPoolType<<Self as HasDbType>::Db, Pool = u32>`.

The result does not depend on the order the imports are written in. Each spec is resolved against
the specs it depends on, not the ones that precede it, so every arrangement of the same imports
yields the same substitutions and bounds; source order decides only the order the bounds are listed
in. That holds across a chain, for a pin whose right-hand side names an alias declared after it, and
across stacked attributes. So `#[use_type(HasC.C in B, HasB.B in A, HasA.A)]` grounds exactly as
`#[use_type(HasA.A, HasB.B in A, HasC.C in B)]` does, and two imports may share one context, as in
`#[use_type(HasA.A, HasB.B in A, HasC.C in A)]`, as readily as they chain.

The one arrangement with no valid order is a cycle, where positions resolve through each other, as
in `#[use_type(HasA.A in B, HasB.B in A)]` or the degenerate `#[use_type(HasAType.A in A)]`. A cycle
is rejected at macro time with the caret on the alias that closes the loop and a message naming it:
``cannot ground `#[use_type]` imports: they resolve through one another in a cycle `B` -> `A` -> `B`. …``.
Correct the imports so the positions form an acyclic chain; any acyclic order will do.

## Examples

This example threads one abstract `Scalar` through a component and its provider, with neither
writing `Self::` by hand. The type trait and the component come first:

```rust
use cgp::prelude::*;
use core::ops::Mul;

#[cgp_type]
pub trait HasScalarType {
    type Scalar: Clone + Mul<Output = Self::Scalar>;
}

#[cgp_component(AreaCalculator)]
#[use_type(HasScalarType.Scalar)]
pub trait CanCalculateArea {
    fn area(&self) -> Scalar;
}
```

`CanCalculateArea` gains `HasScalarType` as a supertrait, and `area` returns
`<Self as HasScalarType>::Scalar`. A provider imports the same type and writes its body with the
bare name:

```rust
#[cgp_impl(new RectangleAreaCalculator)]
#[use_type(HasScalarType.Scalar)]
impl AreaCalculator {
    fn area(&self, #[implicit] width: Scalar, #[implicit] height: Scalar) -> Scalar {
        width * height
    }
}
```

The provider's `#[use_type]` adds `__Context__: HasScalarType` to its `where` clause and rewrites
each `Scalar`, so the implicit fields and the return value agree on the context's scalar type. A
context then binds the type by wiring `ScalarTypeProviderComponent` to `UseType<f64>` and supplies
the fields, and its own code never mentions associated-type syntax.

## Related constructs

These constructs are the ones `#[use_type]` works with:

- [`#[cgp_type]`](../macros/cgp_type.md): defines the abstract-type traits it imports.
- [`UseType`](../providers/use_type.md): the provider a context uses to bind an abstract type to a
  concrete one.
- [`#[cgp_fn]`](../macros/cgp_fn.md), [`#[cgp_impl]`](../macros/cgp_impl.md), and
  [`#[cgp_component]`](../macros/cgp_component.md): the main hosts, each receiving the bound where
  it fits.
- [`#[extend]`](extend.md): adds a supertrait without rewriting names; prefer `#[use_type]` when the
  imported type appears in signatures.
- [`#[impl_generics]`](impl_generics.md): the lighter alternative on `#[cgp_fn]` when the type only
  flows through values the body reads from fields, so it is inferred rather than wired; move to an
  abstract type once a signature names the type or two traits must agree on it, per
  [naming a type dependency](../../guides/naming-a-type-dependency.md).
- [`HasType`](../components/has_type.md): CGP's tag-indexed abstract-type component.
- [Importing abstract types](../../guides/importing-abstract-types.md): the guide recommending this
  attribute over a supertrait plus `Self::Type`.

## Known issues

Three corner cases are lowered faithfully and left to the compiler, and each is worth recognizing:

- **A misspelled associated type** lowers into a path that names nothing, and because the
  substitution keeps the user's span, the error lands on each use of the alias:
  `#[use_type(HasErrorType.Eror)]` fails with
  ``E0576 cannot find associated type `Eror` in trait `HasErrorType` ``.
- **An alias in a trait path's head is not grounded**, since that position must name a trait and an
  alias names a type, so `#[use_type(HasFooType.Foo, Foo.Bar)]` fails on the second `Foo` with
  ``E0405 cannot find trait `Foo` in this scope``.
- **Two pins naming each other**, `#[use_type(HasFooType.{Foo = Bar}, HasBarType.{Bar = Foo})]`,
  ground in one pass and emit both bounds, which the solver cannot discharge:
  ``E0275 overflow evaluating the requirement `<__Context__ as HasFooType>::Foo == _` ``. The
  [implementation document](../../implementation/asts/attributes/use_type.md#behavior-and-corner-cases)
  records why this is emitted rather than rejected.

One further case is a defect rather than a deliberate deferral:

- **An alias inside a type-level macro is not rewritten.** The rewrite reaches every `syn::Type`
  in the item, but a macro invocation's body is opaque tokens, so a bare alias written inside
  `Product![…]`, `Sum![…]`, [`Struct! { … }`](../macros/struct.md), or
  [`Enum! { … }`](../macros/enum.md) is left bare and fails with
  ``E0425 cannot find type `Error` in this scope``. Write the qualified
  `<Self as HasErrorType>::Error` inside the macro until the
  [fix](../../implementation/asts/attributes/use_type.md#known-issues) lands.

## Source

- Parsing: `UseTypeAttribute` in
  [crates/macros/cgp-macro-core/src/types/attributes/use_type/attribute.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/use_type/attribute.rs)
  reads the trait as a `PathWithTypeArgs`, the associated-type list after the `.`, and an optional
  `in Context` (also a `PathWithTypeArgs`); the per-type entries (`as` alias and `=` pin) are in
  `ident.rs`.
- The three-step transform, with entry points in `attributes.rs`: `ground_specs` in `grounding.rs`
  resolves each `in Context` or trait argument that names another import, grounding each spec
  against its dependencies and rejecting a cycle in the same walk; `transform_item_trait`
  substitutes and adds the trait's bounds (used by `#[cgp_component]` and `#[cgp_fn]`), and
  `transform_item_impl` does the same for an impl. Both first reject a shared name through
  `forbid_duplicate_aliases`, and the impl-side predicates, including pins, are derived in
  `type_predicates.rs`.
- Name substitution: the `SubstituteAbstractTypes` pass in
  [crates/macros/cgp-macro-core/src/visitors/substitute_abstract_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/visitors/substitute_abstract_type.rs),
  which rewrites single-segment, argument-free type paths in one traversal.
- Rejection of the equality form on component traits:
  [crates/macros/cgp-macro-core/src/types/attributes/cgp_component_attributes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/cgp_component_attributes.rs).
- Implementation document (the internal AST types, the transform, and the index of tests and
  snapshots):
  [implementation/asts/attributes/use_type.md](../../implementation/asts/attributes/use_type.md).
