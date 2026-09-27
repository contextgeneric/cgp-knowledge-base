# `delegate_and_check_components!`

`delegate_and_check_components!` wires a context's components and asserts the wiring is complete in
one step, combining [`delegate_components!`](delegate_components.md) with
[`check_components!`](check_components.md).

## Purpose

`delegate_and_check_components!` checks a context's wiring the moment it is written, with no
separate block to remember. CGP wiring is lazy: a [`delegate_components!`](delegate_components.md)
entry is accepted without verifying that the chosen provider can satisfy the component, so a context
can compile and still fail at the first call to a consumer trait. A standalone
[`check_components!`](check_components.md) block closes that gap, but it must be kept in sync by
hand, since every new delegation needs a new check. This macro derives the checks from the
delegations instead, so every delegated component is checked unless it opts out.

The macro is meant for basic wiring and for getting started with CGP. A newcomer following a
tutorial cannot forget the check and then meet the confusing errors lazy wiring produces at the
first use of a component. Larger codebases keep `delegate_components!` and `check_components!`
separate, because the derivation understands only mappings keyed on a component name. It wires the
whole [`delegate_components!`](delegate_components.md) grammar but leaves the advanced forms
unchecked: `open` dispatch and `@`-path keys, `=>` redirects, and namespace joins. It also cannot
express per-layer checks of a higher-order provider, because those need concrete parameters or
providers the derivation cannot infer from a delegation. A standalone block supplies that control
through `#[check_providers(...)]`, concrete parameters for generic keys, and checks over opened or
namespaced wiring.

For an [aggregate provider](../../concepts/aggregate-providers.md) the macro is not merely
unnecessary but wrong. An aggregate provider, a `new SomeComponents { … }` table that other contexts
delegate to as a bundle, is a provider and never a context. The derived
`CanUseComponent<Component, Params>` assertion asks whether the target can use the component as a
context, which is the wrong question, and it goes wrong in one of two ways depending on the bundled
provider:

- **The provider needs nothing from its context.** Its impl is generic over every context, so the
  assertion holds and the check passes while proving nothing.
- **The provider needs a field or an abstract type.** The assertion fails and blames the bundle:
  `the trait bound 'GeometryComponents: CanUseComponent<AreaCalculatorComponent>' is not satisfied`,
  with a note that `RectangleAreaCalculator` must implement
  `IsProviderFor<AreaCalculatorComponent, GeometryComponents>`.

Neither result says the target was never meant to be a context. Wire an aggregate provider with
plain `delegate_components!`, and verify it through a real context that delegates to it, or directly
with a [`check_components!`](check_components.md) `#[check_providers(...)]` block that asserts
[`IsProviderFor`](../traits/is_provider_for.md) on it for a real context. Either way, every
context's wiring is checked somehow; this macro is the beginner's way to guarantee that for simple
contexts, and the two separate macros are the way that scales.

## Syntax

The macro takes the same table as [`delegate_components!`](delegate_components.md), an optional
generic list and `new` keyword, a target type, and a braced body, plus a few attributes that control
the checking half. The basic form wires and checks each entry:

```rust
delegate_and_check_components! {
    ScaledRectangle {
        AreaCalculatorComponent:
            ScaledAreaCalculator<RectangleAreaCalculator>,
    }
}
```

The check trait's name defaults to `__CanUse{Context}`, such as `__CanUseScaledRectangle`. It
differs from the `__Check{Context}` name [`check_components!`](check_components.md) derives, so both
macros can be used once each in the same module. A single table-level `#[check_trait(Name)]`
overrides it:

```rust
delegate_and_check_components! {
    #[check_trait(TestScaledRectangle)]
    ScaledRectangle {
        AreaCalculatorComponent:
            ScaledAreaCalculator<RectangleAreaCalculator>,
    }
}
```

The table accepts exactly one attribute, and it must be `#[check_trait]`. A second fails with
`Expected exactly one attribute for the check trait name`, and any other attribute fails with a
message asking for `#[check_trait]`.

### Per-entry attributes

A component with generic parameters needs `#[check_params(...)]` on its entry, because the derived
check otherwise has no parameters to test. The delegation does not need them, since the
`DelegateComponent` impl is generic over the parameters, but the check does. The parameters follow
the single-versus-tuple convention of [`check_components!`](check_components.md), and each one
produces its own check:

```rust
delegate_and_check_components! {
    MyApp {
        #[check_params(Rectangle, Circle)]
        AreaCalculatorComponent: ShapeAreaCalculator,
    }
}
```

A `#[skip_check]` attribute on an entry wires it without a check, for a component verified
elsewhere. It saves splitting a second, unchecked `delegate_components!` block out for one
component:

```rust
delegate_and_check_components! {
    ScaledRectangle {
        #[skip_check]
        AreaCalculatorComponent:
            ScaledAreaCalculator<RectangleAreaCalculator>,
    }
}
```

The two attributes are mutually exclusive, and an entry carries at most one. A second fails with
``Expected at most one `#[check_params]` or `#[skip_check]` attribute``, and an attribute that is neither fails with a message naming both. `#[skip_check]`
takes no arguments and says so if given any.

Both attributes may appear on a list key as well as on the keys inside it, and the two are merged
per element rather than one overriding the other. The merge follows these rules:

- An absent attribute defers to the present one.
- Two `#[check_params]` lists concatenate. A list-level `#[check_params(Rectangle)]` above
  `[AreaCalculatorComponent, RotatorComponent]`, with an inner `#[check_params(Circle)]` on the
  first key, checks that key against `Rectangle` and `Circle`, and the second against `Rectangle`
  alone.
- Two `#[skip_check]`s remain a skip.
- A `#[skip_check]` merged with a `#[check_params]` is refused with
  `cannot combine #[skip_check] with #[check_params]`, since the two ask for opposite things.

Two forms produce no check without saying so. An empty `#[check_params()]` supplies no parameters,
so it skips the entry exactly as `#[skip_check]` does; write `#[skip_check]` when that is the
intent. A key that carries only generics and no attribute is still checked, with its generics bound
on the check impl and unit parameters: `<I> FooKey<I>: FooProvider` derives
`impl<I> __CanUseContext<FooKey<I>, ()> for Context {}`, which keeps the key's parameter from being
unbound.

### Which forms are checked

The wiring half accepts every form [`delegate_components!`](delegate_components.md) accepts: the
three operators, all three key forms, per-key generics, the nested-table value, and the `open`,
`namespace`, and `for` statements. It is literally the same table evaluation, so that macro's Syntax
section is the grammar.

The checking half reads only some of those forms, and the gap is silent. Checks are derived from the
delegation keys, and only a single or list key can become one:

- **A `:` or `->` mapping on a single or list key is checked**, one check impl per name, with
  `#[check_params(...)]` supplying a generic component's parameters and `#[skip_check]` opting out.
- **A mapping on an `@`-path key is wired but not checked**, because a route cannot be turned into a
  `CanUseComponent` assertion about a component and its parameters.
- **A `=>` redirect is wired but not checked**, for the same reason on the value side.
- **An `open`, `namespace`, or `for` statement is wired but not checked.** Each emits its delegation
  impls and contributes no check.

Nothing warns about the last three cases: the block compiles, the wiring is correct, and those
components go unverified. Where a table mixes forms, this macro checks the plain entries, and a
standalone [`check_components!`](check_components.md) block is still owed for the rest.

Check attributes are rejected where the derivation would ignore them. An attribute on an `@`-path
key, on the key of a `=>` mapping, or on a key inside a statement such as a `for` loop fails with
the same spanned `unsupported attribute: …` error [`delegate_components!`](delegate_components.md)
raises. Known issues records the one place an attribute is dropped instead.

## Syntax Grammar

The body is the table of [`delegate_components!`](delegate_components.md), with an optional
table-level check-trait attribute and a per-entry check attribute:

```ebnf
DelegateAndCheck -> TableAttr? Generics? `new`? TargetType `{` TableBody `}`

TableAttr        -> `#` `[` `check_trait` `(` IDENTIFIER `)` `]`

TableBody        -> Statement* ( CheckedMapping ( `,` CheckedMapping )* `,`? )?

CheckedMapping   -> EntryAttr? Mapping       // Mapping, Key, ProviderValue — see delegate_components!

EntryAttr        -> `#` `[` `check_params` `(` ( Type ( `,` Type )* `,`? )? `)` `]`
                  | `#` `[` `skip_check` `]`
```

The `Mapping`, `NormalMapping`, `Key`, `ProviderValue`, and `Statement` productions are exactly
those of [`delegate_components!`](delegate_components.md). The grammar is therefore more permissive
than the derivation, as [which forms are checked](#which-forms-are-checked) explains. An `EntryAttr`
is accepted only on a `SingleKey`, on a `MultiKey`, or on a single key inside a `MultiKey`, and only
for a `:` or `->` mapping; anywhere else it is rejected.

## Expansion

The macro emits the delegation impls exactly as [`delegate_components!`](delegate_components.md)
would, then a check trait and one impl per checked entry exactly as
[`check_components!`](check_components.md) would. Given:

```rust
delegate_and_check_components! {
    #[check_trait(CheckMyContext)]
    MyContext {
        NameTypeProviderComponent: UseType<String>,
        NameGetterComponent: UseField<Symbol!("name")>,
    }
}
```

the macro first produces the wiring half, a [`DelegateComponent`](../traits/delegate_component.md)
impl and a forwarding [`IsProviderFor`](../traits/is_provider_for.md) impl per entry:

```rust
impl DelegateComponent<NameTypeProviderComponent> for MyContext {
    type Delegate = UseType<String>;
}
impl<__Context__, __Params__>
    IsProviderFor<NameTypeProviderComponent, __Context__, __Params__> for MyContext
where
    UseType<String>: IsProviderFor<NameTypeProviderComponent, __Context__, __Params__>,
{}

impl DelegateComponent<NameGetterComponent> for MyContext {
    type Delegate = UseField<Symbol!("name")>;
}
impl<__Context__, __Params__>
    IsProviderFor<NameGetterComponent, __Context__, __Params__> for MyContext
where
    UseField<Symbol!("name")>: IsProviderFor<NameGetterComponent, __Context__, __Params__>,
{}
```

then the checking half, a check trait with [`CanUseComponent`](../traits/can_use_component.md) as
its supertrait and one impl per delegated component:

```rust
trait CheckMyContext<__Component__, __Params__: ?Sized>:
    CanUseComponent<__Component__, __Params__>
{}

impl CheckMyContext<NameTypeProviderComponent, ()> for MyContext {}
impl CheckMyContext<NameGetterComponent, ()> for MyContext {}
```

Without the `#[check_trait(...)]` override the trait would be named `__CanUseMyContext`. The output
is identical to a `delegate_components!` block followed by a `check_components!` block whose check
trait has the `__CanUse{Context}` name.

A `#[check_params(...)]` entry puts each listed parameter in the `__Params__` slot of its own check
impl, while the delegation impl stays generic over the parameter. The earlier `MyApp` table
therefore checks `MyApp` at `Rectangle` and at `Circle`, as
`impl __CanUseMyApp<AreaCalculatorComponent, Rectangle> for MyApp {}` and its `Circle` twin,
although its one `DelegateComponent` impl covers every shape. A `#[skip_check]` entry appears in the
wiring half and not in the checking half.

A generic table threads its generics through both halves: `<T> MyContext<T> { ... }` yields
`impl<T> DelegateComponent<...> for MyContext<T>` alongside
`impl<T> __CanUseMyContext<..., ()> for MyContext<T> {}`.

A key's own generics are bound on its check impl as well. An entry such as
`<I> BarGetterAtComponent<I>: UseField<Symbol!("dummy")>` checks as
`impl<I> __CanUse…<BarGetterAtComponent<I>, ()> for MyContext {}`, and a
`#[check_params((I, Index<0>))]` value that mentions the key's generic is bound the same way. So a
component with a generic marker can be wired and checked in one step.

## Examples

A main context wired and checked together is the intended use:

```rust
use cgp::prelude::*;

#[derive(HasField)]
pub struct MyContext {
    pub name: String,
}

delegate_and_check_components! {
    MyContext {
        NameTypeProviderComponent: UseType<String>,
        NameGetterComponent: UseField<Symbol!("name")>,
    }
}
```

If `MyContext` lacked the `name` field, the derived check on `NameGetterComponent` would fail and
report the missing `HasField` bound, instead of letting the gap reach a later call to `name()`.

Mixing checked and skipped entries lets one delegation be verified elsewhere while the rest is
checked inline:

```rust
delegate_and_check_components! {
    ScaledRectangle {
        AreaCalculatorComponent:
            ScaledAreaCalculator<RectangleAreaCalculator>,

        #[skip_check]
        TransformCalculatorComponent:
            ComplexTransform<RectangleAreaCalculator>, // checked in a dedicated check_components! block
    }
}
```

## Related constructs

These constructs are the ones `delegate_and_check_components!` combines or defers to:

- [`delegate_components!`](delegate_components.md): the wiring half and its grammar; use it alone
  for an [aggregate provider](../../concepts/aggregate-providers.md).
- [`check_components!`](check_components.md): the checking half; use a standalone block when a check
  needs `#[check_providers(...)]` or other control beyond `#[check_params]` and `#[skip_check]`.
- [`DelegateComponent`](../traits/delegate_component.md),
  [`IsProviderFor`](../traits/is_provider_for.md), and
  [`CanUseComponent`](../traits/can_use_component.md): the traits the two halves implement and
  assert.
- [`#[cgp_component]`](cgp_component.md), [`#[cgp_impl]`](cgp_impl.md),
  [`#[cgp_provider]`](cgp_provider.md), and [`#[cgp_fn]`](cgp_fn.md): define the components and
  providers the table wires.

## Known issues

An attribute on a key inside a nested inner table, as in
`UseDelegate<new Inner { #[skip_check] Rectangle: RectangleAreaCalculator }>`, is dropped without an
error. The derivation reads attributes only on the outer table's keys, and unlike
[`delegate_components!`](delegate_components.md), this macro does not run the attribute validator
over nested tables. The inner table's entries are never checked either way, since only the outer key
becomes a check entry, so the attribute has no effect. The correct behavior would be to reject it,
as `delegate_components!` does.

## Source

- Entry point: `delegate_and_check_components` in
  [crates/macros/cgp-macro-lib/src/delegate_and_check_components.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/delegate_and_check_components.rs),
  which parses the table, evaluates the delegation half via the shared `DelegateTable`, derives a
  `CheckComponentsTable` from the keys, and emits both.
- Logic:
  [crates/macros/cgp-macro-core/src/types/delegate_and_check_components/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/delegate_and_check_components/):
  the `__CanUse{Context}` default name and `#[check_trait]` handling in `item.rs`, the
  `#[check_params]`/`#[skip_check]` parsing, merging, and mutual exclusion in `check_params.rs`, the
  per-key conversion to check entries in `key_with_check_params.rs`, and the walk over delegation
  entries in `to_keys_with_check_params.rs`.
- Reused tables: the `DelegateTable` from
  [delegate_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/delegate_component/)
  and the `CheckComponentsTable` from
  [check_components/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/check_components/).
- Internal walkthrough (the two reused pipelines, the key-to-check derivation, the corner-case
  handling, and the index of expansion snapshots):
  [implementation/entrypoints/delegate_and_check_components.md](../../implementation/entrypoints/delegate_and_check_components.md).
