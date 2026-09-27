# `check_components!`

`check_components!` asserts at compile time that a context's wiring is complete, generating
`CanUseComponent`-based checks that force the compiler to report exactly which dependency is
missing.

## Purpose

`check_components!` exists because CGP wiring is lazy. When
[`delegate_components!`](delegate_components.md) records that a context delegates a component to a
provider, the compiler does not verify that the provider's transitive dependencies hold for that
context. The [`DelegateComponent`](../traits/delegate_component.md) impl is accepted on its own, and
the provider's `where` bounds are tested only when something uses the component. A context can
therefore look fully wired and still fail the first time a consumer trait is called.

A failure far from the wiring is hard to read. Asking only whether the context implements the
consumer trait makes the compiler report the outermost unmet bound, usually that the provider does
not implement the provider trait, without saying why. The root cause, often one missing field or
type, stays hidden.

`check_components!` turns the question into a [`CanUseComponent`](../traits/can_use_component.md)
check instead. `CanUseComponent` holds only when the context delegates the component and the
delegated provider satisfies [`IsProviderFor`](../traits/is_provider_for.md) for that context.
`IsProviderFor` carries the provider's real `where` bounds, so routing the check through it makes
the compiler evaluate and report them: an unmet transitive requirement appears as an error naming
the missing dependency. The checks are compile-time only, so a successful build is the passing
assertion.

## Syntax

The macro takes check tables, each a context type followed by a braced list of the components to
check on it. The simplest table lists bare component names:

```rust
check_components! {
    Person {
        GreeterComponent,
    }
}
```

Each entry names a component the macro confirms `Person` can use. Several tables may appear in one
invocation, one after another with no separator, each with its own context type and attributes.

A component with generic parameters takes the parameters to check after a colon. A single parameter
is written bare, and several are grouped into a tuple, mirroring the `Params` position of the
component's `IsProviderFor`:

```rust
check_components! {
    MyApp {
        AreaOfShapeCalculatorComponent: Rectangle,                 // one parameter
        TransformCalculatorComponent: (Rectangle, f64),            // two parameters, as a tuple
    }
}
```

A bracketed key or value expands to the cartesian product of its elements. A bracketed value checks
one component against several parameters, a bracketed key checks several components against one, and
bracketing both checks every combination:

```rust
check_components! {
    MyApp {
        [AreaCalculatorComponent, RotatorComponent]: [Rectangle, Circle],
    }
}
```

A table may also carry a leading `<...>` generic list and a `where` clause after the context type,
to introduce and constrain generics the checked parameters use. A parameter may carry its own
generic list as well, which is merged with the table's.

### Attributes

Two attributes may head a table, in either order, each at most once:

- **`#[check_trait(Name)]`** names the generated check trait. By default the macro derives
  `__Check{Context}` from the last segment of the context's path, so `Person` and `some_mod::Person`
  both give `__CheckPerson`. The override is needed when two tables in one module would derive the
  same name, and when the context is not a path at all, such as `&'a Person`, from which no name can
  be derived.
- **`#[check_providers(...)]`** checks that each listed provider is a provider for the context,
  instead of checking the context. Each provider is asserted separately, which is how the layers of
  a higher-order provider are checked one by one. It must list at least one provider.

Any other attribute is rejected by name with `Invalid attribute …`. An empty `#[check_providers()]`
or a repeated attribute is also a compile error.

## Syntax Grammar

The input is any number of check tables, each an optional attribute set and generic list, a context
type, an optional `where` clause, and a braced list of check entries:

```ebnf
CheckComponents -> CheckTable*

CheckTable      -> TableAttr* Generics? ContextType WhereClause? `{` CheckEntries `}`

TableAttr       -> `#` `[` `check_trait` `(` IDENTIFIER `)` `]`
                 | `#` `[` `check_providers` `(` Type ( `,` Type )* `,`? `)` `]`

ContextType     -> Type

CheckEntries    -> ( CheckEntry ( `,` CheckEntry )* `,`? )?

CheckEntry      -> CheckKey ( `:` CheckValue )?

CheckKey        -> Type
                 | `[` ( Type ( `,` Type )* `,`? )? `]`

CheckValue      -> CheckParam
                 | `[` ( CheckParam ( `,` CheckParam )* `,`? )? `]`

CheckParam      -> Generics? Type
```

The grammar needs a few notes beyond what the rules show:

- **Tables are unseparated.** Several `CheckTable`s follow one another directly, and an empty
  invocation parses and emits nothing.
- **Attributes are collected at the head of a table.** Both `TableAttr` forms may be stacked in
  either order, each at most once, and any other attribute is rejected by name.
- **Omitting the value checks a component without parameters.** A bracketed `CheckKey` or
  `CheckValue` expands to the cartesian product.
- **The two empty lists behave differently.** An empty `CheckValue`, `FooComponent: []`, falls back
  to the no-parameter check, exactly as omitting the colon does. An empty `CheckKey`,
  `[]: Rectangle`, expands to no entries at all, so the line asserts nothing and reports nothing. A
  table that seems to pass while asserting nothing is the failure to watch for.

`WhereClause`, `Generics`, and `Type` are Rust grammar productions.

## Expansion

A check table expands to one marker trait and one impl per checked entry. The trait's supertrait is
the assertion, and each impl has an empty body that compiles only if the supertrait holds for its
entry. Given:

```rust
check_components! {
    Person {
        GreeterComponent,
    }
}
```

the macro emits a check trait with `CanUseComponent` as its supertrait, and an impl of it for
`Person` at the listed component with a unit params type:

```rust
trait __CheckPerson<__Component__, __Params__: ?Sized>:
    CanUseComponent<__Component__, __Params__>
{}

impl __CheckPerson<GreeterComponent, ()> for Person {}
```

The impl compiles only if `Person: CanUseComponent<GreeterComponent, ()>`, which requires that
`Person` delegates `GreeterComponent` and that the delegate satisfies
`IsProviderFor<GreeterComponent, Person, ()>`. If the provider needs a `name` field the context
lacks, the compiler reports the unmet `HasField` bound rather than a bare "provider trait not
implemented", which is the point of routing through `CanUseComponent`. The check trait is private to
its module, and its parameters are literally `__Component__` and `__Params__`.

The `?Sized` bound on `__Params__` is required, not defensive. A component's parameter is an
ordinary type argument and may be unsized, so a component declared over `str`, checked as
`ReferenceGetterComponent: (Life<'a>, str)`, would otherwise be rejected for the implicit `Sized`
bound before the assertion was evaluated.

Generic parameters fill the `__Params__` slot of each impl, a single parameter directly and several
as a tuple:

```rust
// AreaOfShapeCalculatorComponent: Rectangle
impl __CheckMyApp<AreaOfShapeCalculatorComponent, Rectangle> for MyApp {}

// TransformCalculatorComponent: (Rectangle, f64)
impl __CheckMyApp<TransformCalculatorComponent, (Rectangle, f64)> for MyApp {}
```

The cartesian product is expanded before the impls are emitted, so
`[AreaCalculatorComponent, RotatorComponent]: [Rectangle, Circle]` produces four impls. The table's
generics and `where` clause are added to every impl: a
`<'a, I> Context where I: Clone { FooComponent: &'a I }` table expands to
`impl<'a, I> __CheckContext<FooComponent, &'a I> for Context where I: Clone {}`.

### Checking providers

The `#[check_providers(...)]` form changes both the supertrait and the implementing type. The check
trait's supertrait becomes `IsProviderFor` on the context, and the impls are written for each listed
provider rather than for the context:

```rust
check_components! {
    #[check_trait(CheckScaledRectangleProviders)]
    #[check_providers(
        RectangleAreaCalculator,
        ScaledAreaCalculator<RectangleAreaCalculator>,
    )]
    ScaledRectangle {
        AreaCalculatorComponent,
    }
}
```

expands to:

```rust
trait CheckScaledRectangleProviders<__Component__, __Params__: ?Sized>:
    IsProviderFor<__Component__, ScaledRectangle, __Params__>
{}

impl CheckScaledRectangleProviders<AreaCalculatorComponent, ()> for RectangleAreaCalculator {}
impl CheckScaledRectangleProviders<AreaCalculatorComponent, ()>
    for ScaledAreaCalculator<RectangleAreaCalculator> {}
```

Each provider is checked by its own impl, so a dependency missing only from the outer
`ScaledAreaCalculator<RectangleAreaCalculator>` errors on that line alone, while one missing from
the inner `RectangleAreaCalculator` errors on both. The pattern of failures locates the broken
layer.

## Examples

A check that catches a wiring mistake shows the value. Here a greeter reads a `name` field through
an [`#[implicit]`](../attributes/implicit.md) argument, and the context stores the value under
another name:

```rust
use cgp::prelude::*;

#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}

#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self, #[implicit] name: &str) {
        println!("Hello, {name}!");
    }
}

#[derive(HasField)]
pub struct Person {
    pub first_name: String, // mismatch: GreetHello needs `name`
}

delegate_components! {
    Person {
        GreeterComponent: GreetHello,
    }
}

check_components! {
    Person {
        GreeterComponent,
    }
}
```

The `delegate_components!` block compiles on its own, because wiring is lazy. The
`check_components!` block asserts `Person: CanUseComponent<GreeterComponent, ()>`, which fails with
`E0277` at the `GreeterComponent` entry. The compiler's help names the cause:
`HasField<Symbol!("name")>` is not implemented for `Person`, although the `first_name` field is. So
the mismatch is reported at the wiring rather than at some distant call to `person.greet()`.
[`cargo cgp check`](../cargo-cgp.md) condenses the same error into a root-cause tree.

A check for a component with a generic parameter supplies the parameters explicitly:

```rust
#[cgp_component(AreaOfShapeCalculator)]
pub trait CanCalculateAreaOfShape<Shape> {
    fn area(&self, shape: &Shape) -> f64;
}

check_components! {
    MyApp {
        AreaOfShapeCalculatorComponent: [Rectangle, Circle],
    }
}
```

This verifies `MyApp: CanCalculateAreaOfShape<Rectangle>` and
`MyApp: CanCalculateAreaOfShape<Circle>` in one table.

## Related constructs

These constructs are the ones `check_components!` works with:

- [`delegate_components!`](delegate_components.md): produces the wiring this macro checks, for
  components defined with [`#[cgp_component]`](cgp_component.md).
- [`CanUseComponent`](../traits/can_use_component.md): the trait the default check asserts, built on
  [`DelegateComponent`](../traits/delegate_component.md) and
  [`IsProviderFor`](../traits/is_provider_for.md).
- [`delegate_and_check_components!`](delegate_and_check_components.md): fuses wiring and checking in
  one step for basic contexts; its default check trait is `__CanUse{Context}`, so it can share a
  module with this macro's `__Check{Context}`.

A standalone `check_components!` next to `delegate_components!` is the form larger codebases rely
on, because it can check what the fused macro cannot: generic keys, opened or namespaced wiring, and
individual provider layers through `#[check_providers(...)]`, which suits the
[higher-order providers](../../concepts/higher-order-providers.md) such layers come from.

## Known issues

A context that is not a path, such as a reference `&'a Person`, cannot yield a derived check-trait
name. Without `#[check_trait(...)]`, such a table fails to parse with `expected identifier`,
pointing at the context type rather than saying a name is needed. Give the table an explicit
`#[check_trait(Name)]`.

## Source

- Entry point: `check_components` in
  [crates/macros/cgp-macro-lib/src/check_components.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/check_components.rs),
  which parses `CheckComponentsTables` and emits their items.
- Logic:
  [crates/macros/cgp-macro-core/src/types/check_components/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/check_components/):
  table parsing, the `#[check_trait]`/`#[check_providers]` attributes, the `__Check{Context}` name
  derivation, and the choice between `CanUseComponent` and `IsProviderFor` supertraits in
  `table.rs`; key and value parsing (including the bracketed forms) in `key.rs` and `value.rs`; and
  the cartesian-product expansion of entries in `entry.rs`.
- Internal walkthrough (the pipeline, the AST types behind each grammar form, the corner-case
  handling, and the index of expansion snapshots):
  [implementation/entrypoints/check_components.md](../../implementation/entrypoints/check_components.md).
