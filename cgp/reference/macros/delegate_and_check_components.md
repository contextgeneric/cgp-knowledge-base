# `delegate_and_check_components!`

`delegate_and_check_components!` wires a context's components and asserts the wiring is complete in one step, combining [`delegate_components!`](delegate_components.md) with [`check_components!`](check_components.md).

## Purpose

`delegate_and_check_components!` exists so that a context's wiring is checked the moment it is written, with no separate test block to remember. Because CGP wiring is lazy — a [`delegate_components!`](delegate_components.md) entry is accepted without verifying that the chosen provider can actually satisfy the component — it is easy to leave a context that compiles but fails at the first call to a consumer trait. A standalone [`check_components!`](check_components.md) block closes that gap, but keeping it in sync with the wiring is manual: add a delegation and you must remember to add its check. This macro removes that bookkeeping by deriving the checks directly from the delegations.

This macro is aimed at basic wiring and at getting started with CGP, rather than at advanced code. Its value is that a newcomer following a tutorial cannot forget to write a separate check and then be tripped by the confusing errors lazy wiring produces at the first use of a component. The derivation it performs only understands a mapping keyed on a component *name* — the plain `Component: Provider` form and its `->` sibling — so while the block accepts the whole [`delegate_components!`](delegate_components.md) grammar and wires all of it, it cannot generate check traits for the advanced forms: generic-parameter dispatch through the `open` statement and `@`-path keys, `=>` redirects, and [namespace](cgp_namespace.md) joins are wired and left unchecked, and per-layer higher-order checks are not expressible at all, because each needs concrete parameters or providers the fused derivation cannot infer from a delegation alone. Larger and more advanced codebases therefore keep [`delegate_components!`](delegate_components.md) and [`check_components!`](check_components.md) separate, using the standalone check block for the control the per-entry derivation cannot give: `#[check_providers(...)]`, concrete parameters for generic keys, and checks over opened or namespaced wiring. One case makes this macro not merely unnecessary but *incorrect*: an [aggregate provider](../../concepts/aggregate-providers.md) — a `new SomeComponents { … }` table (see [`delegate_components!`](delegate_components.md)) that defines a zero-sized provider dispatching each component to a sub-provider, which other contexts then delegate to as a reusable bundle. An aggregate provider is delegated *to* by contexts and is never its own context; it has no fields and is not meant to stand in the context position, so the derived `CanUseComponent<Component, Params>` assertion — which asks whether the *target* can use the component as a context — is asking the wrong question. **Which way it goes wrong depends on the bundled provider, and neither outcome is useful.** When the leaf provider has no impl-side dependencies its provider impl is generic over every context, so the assertion happens to hold and the check passes while proving nothing. When the leaf provider needs anything from its context — a field, an abstract type — the assertion fails and blames the bundle: `the trait bound 'GeometryComponents: CanUseComponent<AreaCalculatorComponent>' is not satisfied`, with a note that `RectangleArea` must implement `IsProviderFor<AreaCalculatorComponent, GeometryComponents>`. Nothing in either result says the target was never meant to be a context, which is why the rule is worth stating as a rule rather than left to the diagnostic. Wire an aggregate provider with plain `delegate_components!`; it is verified indirectly when a real context that delegates to it is checked, or directly with a [`check_components!`](check_components.md) `#[check_providers(...)]` block that asserts [`IsProviderFor`](../traits/is_provider_for.md) on it for a real context. The invariant across both approaches is that a context's wiring is checked somehow; this macro is the beginner-level way to guarantee that for simple contexts, and the two separate macros are the way that scales.

Functionally, the macro emits exactly what writing both macros by hand would, with the check entries inferred from the delegation keys. Every delegated component is checked unless explicitly opted out, so the default behavior is "wire it and prove it works."

## Syntax

The macro takes the same table shape as [`delegate_components!`](delegate_components.md) — an optional `new` keyword and generics, a target type, and brace-delimited `Key: Value` delegation entries — and additionally accepts a few attributes that control the checking half. The basic form simply wires and checks each entry:

```rust
delegate_and_check_components! {
    ScaledRectangle {
        AreaCalculatorComponent:
            ScaledAreaCalculator<RectangleAreaCalculator>,
    }
}
```

The check trait's name defaults to `__CanUse{Context}` (for example `__CanUseScaledRectangle`). This deliberately differs from the `__Check{Context}` name that [`check_components!`](check_components.md) derives, so that both macros can be used once each in the same module without a name clash. A table-level `#[check_trait(Name)]` attribute overrides the derived name:

```rust
delegate_and_check_components! {
    #[check_trait(TestScaledRectangle)]
    ScaledRectangle {
        AreaCalculatorComponent:
            ScaledAreaCalculator<RectangleAreaCalculator>,
    }
}
```

A component with generic parameters needs a `#[check_params(...)]` attribute on its entry, because the derived check would otherwise have no parameters to test. The delegation half does not need the parameters — the `DelegateComponent` impl is generic over them — but the check half does, so `#[check_params(...)]` supplies them, with the same single-versus-tuple convention as [`check_components!`](check_components.md):

```rust
delegate_and_check_components! {
    MyApp {
        #[check_params(
            Rectangle,
            Circle,
        )]
        AreaOfShapeCalculatorComponent:
            UseDelegate<new AreaOfShapeCalculatorComponents {
                Rectangle: RectangleArea,
                Circle: CircleArea,
            }>,
    }
}
```

A `#[skip_check]` attribute on an entry wires it without generating any check, for cases where that component is verified separately. This avoids having to split out a second plain `delegate_components!` block just to wire one component without a check:

```rust
delegate_and_check_components! {
    ScaledRectangle {
        #[skip_check]
        AreaCalculatorComponent:
            ScaledAreaCalculator<RectangleAreaCalculator>,
    }
}
```

The `#[check_params(...)]` and `#[skip_check]` attributes are mutually exclusive on a given key, and at most one may appear; a second is rejected with `Expected at most one #[check_params] or #[skip_check] attribute`, and an attribute that is neither with a message naming both. `#[skip_check]` takes no arguments and says so if given any.

Both attributes may appear on a **list key** as well as on the individual keys inside it, and the two are merged per element rather than one overriding the other. An absent attribute defers to the present one; two `#[check_params]` lists concatenate, so a list-level `#[check_params(Rectangle)]` above `[<T> AreaCalculatorComponent, RotatorComponent]` with an inner `#[check_params(Circle)]` on the first key checks that key against `Rectangle` *and* `Circle` while the second is checked against `Rectangle` alone. Two `#[skip_check]`s stay a skip. The one combination that is refused is a `#[skip_check]` merged with a `#[check_params]`, since the two ask for opposite things: `cannot combine #[skip_check] with #[check_params]`.

Two forms silently produce no check, and both are worth recognizing because neither reports anything. An **empty** `#[check_params()]` supplies no parameters to iterate, so it skips the entry exactly as `#[skip_check]` would — write the latter when that is the intent, since it says so. And a key that carries **only generics** and no attribute is still checked, with those generics bound on the check impl and unit parameters: `<I> FooKey<I>: FooProvider` derives `impl<I> __CanUseContext<FooKey<I>, ()> for Context {}`, which is what keeps the key's own parameter from appearing unbound.

### What the shared grammar covers, and what the derivation reads

**The wiring half accepts every syntax [`delegate_components!`](delegate_components.md) accepts** — the three mapping operators (`:`, `->`, `=>`), all three key forms (a single key, a bracketed [list key](delegate_components.md#keys-a-single-name-a-list-or-a-path), an `@`-path key with its `[…]` and `{…}` groups), per-key generics, the nested-table value form, and the three leading statements (`open`, `namespace`, `for`). Read that macro's Syntax section for the grammar; nothing about the delegation is different here, because it is literally the same table evaluation.

**The checking half reads only some of those forms, and the gap is silent.** Check entries are derived from the delegation *keys*, and only a single or list key can become one, so the coverage divides as follows:

- A `:` or `->` mapping keyed on a single or list key **is checked**, one check impl per name, with `#[check_params(...)]` supplying the parameters for a generic component and `#[skip_check]` opting one out. A list key attaches its check params per bracketed element, merging a list-level attribute with any on an individual key.
- A mapping keyed on an `@`-**path** is **wired but not checked**, because the derivation has no way to turn a route into a `CanUseComponent` assertion about a component and its parameters.
- A `=>` **redirect** mapping is **wired but not checked**, for the same reason on the value side.
- An `open`, `namespace`, or `for` **statement** is **wired but not checked**. Each still emits its delegation impls; none contributes a check entry.

Nothing warns about the second, third, or fourth case — the block compiles, the wiring is correct, and the components those forms wire simply go unverified. That silence is the practical reason larger codebases keep [`delegate_components!`](delegate_components.md) and [`check_components!`](check_components.md) apart: a standalone check block can name the concrete parameters an opened component needs, assert `IsProviderFor` per provider layer, and cover what a namespace brought in, none of which the fused derivation can infer from a delegation alone. Where a table mixes forms, the honest reading is that this macro checks the plain entries and a standalone block is still owed for the rest.

Attributes are only accepted where they mean something. The checking attributes attach to the table and to single or list keys; an attribute on an `@`-path key, or on a key inside a `for` loop, is rejected with the same spanned "unsupported attribute" error [`delegate_components!`](delegate_components.md) raises, rather than being read as a check attribute the derivation would then ignore.

## Syntax Grammar

The body of `delegate_and_check_components!` is the same table shape as [`delegate_components!`](delegate_components.md), with an optional table-level check-trait attribute and a per-entry check attribute added:

```ebnf
DelegateAndCheck -> TableAttr* Generics? `new`? TargetType `{` TableBody `}`

TableAttr        -> `#` `[` `check_trait` `(` IDENTIFIER `)` `]`

TableBody        -> Statement* ( CheckedMapping ( `,` CheckedMapping )* `,`? )?

CheckedMapping   -> EntryAttr? Mapping       // Mapping, Key, ProviderValue — see delegate_components!

EntryAttr        -> `#` `[` `check_params` `(` Type ( `,` Type )* `,`? `)` `]`
                  | `#` `[` `skip_check` `]`
```

The `Mapping`, `NormalMapping`, `Key`, `ProviderValue`, and `Statement` productions are exactly those of [`delegate_components!`](delegate_components.md); only the attributes differ, and the grammar is therefore permissive in a way the *derivation* is not — see [what the derivation reads](#what-the-shared-grammar-covers-and-what-the-derivation-reads). The table-level `#[check_trait(...)]` overrides the derived `__CanUse{Context}` trait name. Each mapping may carry at most one `EntryAttr`, and `#[check_params(...)]` and `#[skip_check]` are mutually exclusive: `#[check_params(...)]` supplies the generic parameters the derived check needs for a component with type parameters, and `#[skip_check]` wires the entry without generating a check at all. An `EntryAttr` is accepted only on a `SingleKey` or a `MultiKey` — the key forms a check entry can be derived from — and is rejected on a `PathKey` and inside a `ForStmt` body rather than being silently dropped.

## Expansion

The macro emits the delegation impls exactly as [`delegate_components!`](delegate_components.md) would, then appends a check trait and one impl per non-skipped entry, exactly as [`check_components!`](check_components.md) would. Starting from:

```rust
delegate_and_check_components! {
    #[check_trait(CheckMyContext)]
    MyContext {
        NameTypeProviderComponent: UseType<String>,
        NameGetterComponent: UseField<Symbol!("name")>,
    }
}
```

the macro first produces the wiring half — a [`DelegateComponent`](../traits/delegate_component.md) impl and an [`IsProviderFor`](../traits/is_provider_for.md) forwarding impl for each entry:

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

then the checking half — a check trait aliasing [`CanUseComponent`](../traits/can_use_component.md), with one impl per delegated component:

```rust
trait CheckMyContext<__Component__, __Params__: ?Sized>:
    CanUseComponent<__Component__, __Params__>
{}

impl CheckMyContext<NameTypeProviderComponent, ()> for MyContext {}
impl CheckMyContext<NameGetterComponent, ()> for MyContext {}
```

Without the `#[check_trait(...)]` override, the trait would instead be named `__CanUseMyContext`. The whole output is identical to writing a `delegate_components!` block followed by a `check_components!` block whose check trait carries the `__CanUse{Context}` name.

A `#[check_params(...)]` entry expands its parameters into the `__Params__` slot of the generated check impls, one impl per listed parameter, while the delegation impl stays generic over the parameter. The earlier `MyApp` table therefore checks `MyApp` at `Rectangle` and at `Circle` (`impl __CanUseMyApp<AreaOfShapeCalculatorComponent, Rectangle> for MyApp {}` and likewise for `Circle`), even though its single `DelegateComponent` impl is parameter-generic. A `#[skip_check]` entry contributes its delegation impls but no check impl, so it appears in the wiring half and is absent from the checking half.

A generic table threads its generics through both halves. `<T> MyContext<T> { ... }` yields `impl<T> DelegateComponent<...> for MyContext<T>` delegations alongside `impl<T> __CanUseMyContext<..., ()> for MyContext<T> {}` checks.

A delegation key may also carry its own generic parameters, and they are bound on the derived check impl. An entry such as `<I> BarGetterAtComponent<I>: UseField<Symbol!("dummy")>` — the array-key generic form [`delegate_components!`](delegate_components.md) accepts — checks as `impl<I> __CanUse…<BarGetterAtComponent<I>, ()> for MyContext {}`, and a `#[check_params((I, Index<0>))]` value that mentions the key generic is bound the same way. This lets a component whose marker is generic be wired and checked in one step without splitting the check into a separate block.

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

If `MyContext` were missing the `name` field, the derived check on `NameGetterComponent` would fail to compile and report the missing `HasField` bound, rather than letting the gap slip through to a later use of `name()`.

Mixing checked and skipped entries lets a higher-order delegation be verified elsewhere while the rest is checked inline:

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

`delegate_and_check_components!` is the fusion of [`delegate_components!`](delegate_components.md) and [`check_components!`](check_components.md): the wiring half behaves exactly like the former and the checking half like the latter, so the semantics of [`DelegateComponent`](../traits/delegate_component.md), [`IsProviderFor`](../traits/is_provider_for.md), and [`CanUseComponent`](../traits/can_use_component.md) all carry over unchanged. It wires components defined with [`#[cgp_component]`](cgp_component.md) to providers written with [`#[cgp_impl]`](cgp_impl.md), [`#[cgp_provider]`](cgp_provider.md), or [`#[cgp_fn]`](cgp_fn.md), and supports nested-table values via [`use_delegate.md`](../providers/use_delegate.md) and field getters via [`use_field.md`](../providers/use_field.md). Reach for plain [`delegate_components!`](delegate_components.md) instead when building an [aggregate provider](../../concepts/aggregate-providers.md), and for a standalone [`check_components!`](check_components.md) block when a check needs `#[check_providers(...)]` or other control beyond per-entry `#[check_params]`/`#[skip_check]`.

## Source

- Entry point: `delegate_and_check_components` in [crates/macros/cgp-macro-lib/src/delegate_and_check_components.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/delegate_and_check_components.rs), which parses the table, evaluates the delegation half via the shared `DelegateTable`, derives a `CheckComponentsTable` from the keys, and emits both.
- Logic: [crates/macros/cgp-macro-core/src/types/delegate_and_check_components/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/delegate_and_check_components/) — the `__CanUse{Context}` default name and `#[check_trait]` handling in `item.rs`, the `#[check_params]`/`#[skip_check]` parsing and their mutual exclusion in `check_params.rs`, the per-key conversion to check entries in `key_with_check_params.rs`, and the walk over delegation entries in `to_keys_with_check_params.rs`.
- Reused tables: the `DelegateTable` from [delegate_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/delegate_component/) and the `CheckComponentsTable` from [check_components/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/check_components/).
- Internal walkthrough (the two reused pipelines, the key-to-check derivation, the corner-case handling, and the index of expansion snapshots): [implementation/entrypoints/delegate_and_check_components.md](../../implementation/entrypoints/delegate_and_check_components.md).
