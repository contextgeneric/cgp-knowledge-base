# `#[cgp_component]`

`#[cgp_component]` is the foundational CGP macro: applied to a trait, it turns that ordinary Rust trait into a full CGP component — a consumer trait, a matching provider trait, and the blanket implementations that let a context delegate the trait's behavior to a freely chosen provider.

## Purpose

`#[cgp_component]` exists to lift a single trait into a pair of traits that separate *using* a capability from *implementing* it. A normal Rust trait conflates the two: the type that implements `Area` is the same type that callers invoke `.area()` on, and Rust's coherence rules then allow only one implementation per type. CGP breaks this conflation by generating two traits from one definition. The **consumer trait** is what callers use (`context.area()`); the **provider trait** is what implementers write, with the original `Self` moved into an explicit `Context` type parameter so that any number of provider types can implement it without colliding.

The payoff is that providers become first-class, named, swappable units. Because a provider implements the provider trait for a generic `Context` rather than for itself, the usual orphan and overlap restrictions do not bite, and a crate can define many alternative providers for the same component. A concrete context then picks one provider per component through wiring (see [`delegate_components!`](delegate_components.md)), and the generated blanket impls route the consumer-trait call through that choice. `#[cgp_component]` is what makes a trait participate in this mechanism; without it, a trait is just a vanilla Rust trait.

One design decision belongs to the trait rather than to this macro, and it determines how much the wiring can vary. A component is **self-targeted** when the capability is about the `Self` type — `CanCalculateArea` computing the area of the context itself — and **parameter-targeted** when it is about a type parameter while `Self` only supplies the decisions, as `CanSerializeValue<Value>` is. A parameter alone does not decide this: in `CanCompute<Code, Input>` the target is `Input` while `Code` is a selector the wiring dispatches on, and a component may carry both. The choice matters because a self-targeted component's wiring is keyed on the type the capability is about, so that type gets one provider for the whole program, whereas a parameter-targeted component's wiring is keyed on a context that can be defined as many times as needed. The [modularity hierarchy](../../concepts/modularity-hierarchy.md) works through which to reach for.

## Syntax

The macro is applied as an attribute on a trait definition and takes the provider trait's name as its argument. The simplest form passes a bare identifier:

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}
```

Here `CanCalculateArea` is the consumer trait (named in verb form, `CanDoSomething`) and `AreaCalculator` is the provider trait (named in noun form). When more control is needed, the macro accepts a key/value form instead of a bare identifier:

```rust
#[cgp_component {
    name: AreaCalculatorComponent,
    provider: AreaCalculator,
    context: Context,
}]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}
```

The three keys correspond to the three names the macro needs, and each has a default. The `provider` key sets the provider trait name and is the only required value; passing a bare identifier is shorthand for setting `provider` alone. The `name` key sets the component name type and defaults to the provider name with a `Component` suffix, so `AreaCalculator` yields `AreaCalculatorComponent`. The `context` key sets the identifier used for the generic context type parameter in the generated provider trait and defaults to `__Context__` — a deliberately unusual name chosen to avoid clashing with the user's own type parameters.

The trait body itself is unrestricted in the number of items it declares. A component trait may carry any number of methods, associated types, and associated consts, and every one of them is reproduced on the generated provider trait, so a provider implements the whole set — CGP's own [`CanCompute`](../components/computer.md) declares an associated `Output` beside its `compute` method, and a [getter trait](cgp_getter.md) commonly declares one method per field. The only rejected declaration is a **const generic parameter** on the trait, for the reason given under Known issues. Which items are worth grouping into one component is a design question rather than a limit of the macro, and it is answered in [sizing a component](../../guides/sizing-a-component.md): everything in one component is decided by one provider, so items that a single provider choice settles belong together while items that separate choices settle are better off in separate components.

Four companion attributes extend the macro for special cases, and each is documented separately. [`#[extend(...)]`](../attributes/extend.md) adds supertrait bounds to the generated consumer trait; [`#[use_type(...)]`](../attributes/use_type.md) imports an abstract associated type, adding the owning trait as a supertrait and rewriting the bare alias throughout the signatures; [`#[derive_delegate(...)]`](../attributes/derive_delegate.md) generates `UseDelegate` providers that dispatch on a generic parameter; and [`#[prefix(@path in Namespace)]`](../attributes/prefix.md) registers the component into a namespace under a type-level path, emitting one namespace impl per attribute. Any of the four may be repeated, and `#[extend]`, `#[use_type]`, and `#[derive_delegate]` each accept a comma-separated list in one attribute.

Three modifiers that host macros elsewhere accept are **not** accepted here, and the failure they produce is worth recognizing because the macro does not report it. `#[uses(...)]`, `#[extend_where(...)]`, and `#[use_provider(...)]` are meaningful only where there is a provider impl or a generated trait definition to attach them to, so the component collector does not match them; an unrecognized attribute is passed straight through onto the items the macro emits, where the compiler rejects it as `cannot find attribute … in this scope`. None of these modifiers is a standalone proc macro, so there is nothing else for the name to resolve to. The equivalent of `#[uses]` on a component is a supertrait, written with `#[extend]`.

The related macros [`#[cgp_type]`](cgp_type.md) and [`#[cgp_getter]`](cgp_getter.md) build on `#[cgp_component]` to derive additional constructs for abstract-type and getter components respectively.

When a component's supertrait exists only to supply an abstract type the trait's own signatures name — most commonly [`HasErrorType`](../components/has_error_type.md), whose `Error` a fallible method returns — prefer importing that type with [`#[use_type]`](../attributes/use_type.md) over writing the supertrait and the qualified `Self::` path by hand. Annotating the trait with `#[use_type(HasErrorType.Error)]` adds `HasErrorType` as a supertrait *and* rewrites a bare `Error` in the signatures to `<Self as HasErrorType>::Error`, so the definition reads `pub trait CanLoad { fn load(&self, path: &str) -> Result<String, Error>; }` rather than spelling `: HasErrorType` and `Self::Error`. For a supertrait `#[use_type]` cannot express — a capability supertrait with no associated type to import, or a bound the trait does not name in its signatures — declare it with `#[extend(...)]` in preference to native `: Supertrait` syntax, which reads as OOP-style inheritance rather than the capability import a CGP supertrait actually is. A local associated type the trait declares itself, such as a handler's `type Output`, always stays written as `Self::Output`; it is not imported, so `#[use_type]` neither lists nor rewrites it.

One form of `#[use_type]` is refused on a component trait: the **equality form** `#[use_type(HasScalarType.{Scalar = f64})]`, which pins an imported type to a concrete one. Pinning belongs to a provider that has decided the type, not to the definition every provider must satisfy, so the macro rejects the `=` with `Type equality constraints cannot be used in component trait definition`. Every other form — the `in Context` clause, the `as Alias` rename, the braced list, and generic arguments on the owning trait — is accepted here exactly as it is on `#[cgp_impl]` and `#[cgp_fn]`.

## Syntax Grammar

The attribute argument of `#[cgp_component]` is either a bare provider name or a comma-separated set of keyed values:

```ebnf
CgpComponentArgs -> ProviderName
                  | KeyValueArg ( `,` KeyValueArg )* `,`?

ProviderName     -> IDENTIFIER

KeyValueArg      -> `name` `:` ComponentName
                  | `provider` `:` IDENTIFIER
                  | `context` `:` IDENTIFIER

ComponentName    -> IDENTIFIER GenericArgs?
```

`ProviderName` is the bare-identifier form and is shorthand for setting `provider` alone. In the key/value form each of the three keys may appear at most once and in any order, and `provider` is required — the other two have defaults (`context` is `__Context__`, `name` is the provider name with a `Component` suffix). `IDENTIFIER` is a Rust identifier token, and `GenericArgs` is the Rust grammar's `< … >` argument list (so the component name may carry generic parameters while the provider name may not). The attribute delimiter shown in Syntax — `(...)` for the bare form and `{...}` for the key/value form — is ordinary Rust attribute syntax; the argument tokens inside follow this grammar regardless of which delimiter is used.

## Expansion

`#[cgp_component]` replaces the annotated trait with five top-level items plus a set of standard provider impls. The five are emitted in a fixed order — consumer trait, consumer blanket impl, provider trait, provider blanket impl, component marker — and are described below in the order that makes them easiest to read, which pairs each trait with the impl that routes to it. Starting from this input:

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}
```

the macro emits, first, the **consumer trait** unchanged from its definition:

```rust
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}
```

Second, it emits the **provider trait**, which is the consumer trait with `Self` replaced by an explicit leading `Context` type parameter and every `self`/`Self` reference rewritten to `context`/`Context`. The provider trait carries an [`IsProviderFor`](../traits/is_provider_for.md) supertrait that captures the component name and context so that unsatisfied dependencies surface as readable compiler errors. The supertrait's third argument is the `Params` tuple of the component's extra type parameters; for a component with no parameters beyond the context it is the empty `()`:

```rust
pub trait AreaCalculator<Context>:
    IsProviderFor<AreaCalculatorComponent, Context, ()>
{
    fn area(context: &Context) -> f64;
}
```

The provider trait's supertrait list is *replaced* by `IsProviderFor` rather than extended with it, and the consumer trait's own supertraits — whether written natively, added by [`#[extend]`](../attributes/extend.md), or added by [`#[use_type]`](../attributes/use_type.md) — are lowered into a `where` predicate on the context instead. This is a consequence of the `Self`-to-`Context` move: a supertrait of the consumer trait constrains the type the capability is about, which on the provider side is the context parameter and not `Self`. So `#[cgp_component(Greeter)] #[extend(HasName)] pub trait CanGreet { … }` yields:

```rust
pub trait Greeter<Context>: IsProviderFor<GreeterComponent, Context, ()>
where
    Context: HasName,
{
    fn greet(context: &Context);
}
```

The same predicate is added to *every* item the macro emits that mentions the context — the consumer blanket impl, the provider blanket impl, and the `UseContext` and `RedirectLookup` provider impls each gain their own `Context: HasName` — since none of them can apply where the supertrait does not hold.

**A component trait's methods may carry default bodies, and the body travels to the provider trait rather than staying behind on the consumer trait.** This is the second thing the `Self`-to-`Context` move reaches, and it is what makes a provider able to inherit a default at all: the body is rewritten along with the signature, so `fn greet(&self) -> String { format!("Hello, {}!", self.name()) }` on the consumer trait becomes `fn greet(context: &Context) -> String { format!("Hello, {}!", context.name()) }` on the provider trait, keeping its default. The consumer trait keeps its own copy of the body as well, so the same duplication [`#[blanket_trait]`](blanket_trait.md) produces appears here.

The payoff is that an **empty provider impl inherits the default**, which is how [`UseDefault`](../providers/use_default.md) works and the reason a provider can be declared with nothing in its block:

```rust
#[cgp_impl(UseDefault)]
impl<Context: HasName> Greeter for Context {}
```

Third, it emits the **consumer blanket impl**, which says that any context implementing the provider trait *for itself* automatically gets the consumer trait. This is the bridge that lets callers write `context.area()`:

```rust
impl<Context> CanCalculateArea for Context
where
    Context: AreaCalculator<Context>,
{
    fn area(&self) -> f64 {
        Context::area(self)
    }
}
```

Fourth, it emits the **provider blanket impl**, which lets any provider that delegates this component (via [`DelegateComponent`](../traits/delegate_component.md)) inherit the provider trait from the provider it delegates to. This is the mechanism `delegate_components!` drives — it turns a context into a type-level table whose entry for `AreaCalculatorComponent` names the chosen provider:

```rust
impl<Context, Provider> AreaCalculator<Context> for Provider
where
    Provider: DelegateComponent<AreaCalculatorComponent>
        + IsProviderFor<AreaCalculatorComponent, Context, ()>,
    Provider::Delegate: AreaCalculator<Context>,
{
    fn area(context: &Context) -> f64 {
        Provider::Delegate::area(context)
    }
}
```

Note that the `IsProviderFor` bound sits on `Provider` itself, beside the `DelegateComponent` bound — not on `Provider::Delegate`. The blanket impl of `IsProviderFor` (generated by `delegate_components!`) forwards a component's dependencies through `Provider`, so requiring `Provider: IsProviderFor<…>` is what threads those dependencies down the delegation chain and surfaces them in error messages.

Fifth, it emits the **component name struct**, a zero-sized marker that serves as the key into delegation tables:

```rust
pub struct AreaCalculatorComponent;
```

Beyond these five items, the macro also generates standard provider impls that make the component usable in the patterns CGP relies on. Two are unconditional and two are one-per-attribute:

- A [`UseContext`](../providers/use_context.md) impl, so that the provider trait can be satisfied by routing back through a context's own consumer-trait implementation. Its `where` clause is the single predicate `__Context__: CanCalculateArea`, and each method body forwards to the consumer method.
- A [`RedirectLookup`](../providers/redirect_lookup.md) impl, which is what the `open` statement of [`delegate_components!`](delegate_components.md) and the [namespace](cgp_namespace.md) machinery resolve through. It is written for `RedirectLookup<__Components__, __Path__>` and looks the component up as `__Components__: DelegateComponent<__Path__>`.
- One [`UseDelegate`](../providers/use_delegate.md) impl per [`#[derive_delegate(...)]`](../attributes/derive_delegate.md) attribute, dispatching on the named generic parameter.
- One namespace impl per [`#[prefix(@path in Namespace)]`](../attributes/prefix.md) attribute, binding the component's key inside that namespace to a `RedirectLookup` down the given path.

The `RedirectLookup` impl is where a component's own type parameters earn their place in a path, and it is the mechanism behind `@AreaCalculatorComponent.Rectangle`. When the component has type parameters, the impl does not look up `__Path__` directly: it requires `__Path__: ConcatPath<Shape>` and looks up the *extended* path `<__Path__ as ConcatPath<Shape>>::Output`, so the component's parameters are appended to whatever path the lookup arrived on. Only **type** parameters take part — lifetimes and const parameters are filtered out, since neither can key a path — and a component with no type parameters gets the simpler form that looks `__Path__` up unchanged.

Two details of the expansion are worth holding onto because they are easy to get wrong. The generated type parameters carry reserved names, not the readable ones used above: the context parameter is literally `__Context__` unless overridden, and the provider parameter in the provider blanket impl is `__Provider__`. The examples here use `Context` and `Provider` for legibility, but the emitted code uses the reserved names. And the generic parameters of a component with parameters of its own are appended *after* the context parameter in the provider trait — except lifetimes, which Rust requires to lead, so `HasReference<'a, T>` yields `ReferenceGetter<'a, __Context__, T>` — and are grouped into a parenthesized list in the `IsProviderFor` `Params` position. The tuple holds *types*, so each parameter is recorded by name and a **lifetime is lifted into [`Life<'a>`](../types/life.md)**: `CanCalculateArea<Shape>` gives `IsProviderFor<AreaCalculatorComponent, __Context__, (Shape)>`, a two-parameter component gives `(Shape, Scalar)`, and `HasReference<'a, T>` gives `(Life<'a>, T)`. Bounds and defaults are dropped, since the tuple only names the parameters positionally, and a const parameter has no representation at all — which is why it is rejected outright, per Known issues.

## Examples

A complete component, from definition through wiring to use, ties the pieces together. First the component and a provider for it:

```rust
use cgp::prelude::*;

#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_auto_getter]
pub trait HasDimensions {
    fn width(&self) -> &f64;
    fn height(&self) -> &f64;
}

#[cgp_impl(new RectangleArea)]
impl AreaCalculator
where
    Self: HasDimensions,
{
    fn area(&self) -> f64 {
        self.width() * self.height()
    }
}
```

Then a concrete context that wires the component to that provider and uses it:

```rust
#[derive(HasField)]
pub struct Rectangle {
    pub width: f64,
    pub height: f64,
}

delegate_components! {
    Rectangle {
        AreaCalculatorComponent: RectangleArea,
    }
}

fn print_area(rect: &Rectangle) {
    println!("area = {}", rect.area()); // CanCalculateArea, via RectangleArea
}
```

The call `rect.area()` resolves through the consumer blanket impl to `Rectangle::area(rect)`, which resolves through the provider blanket impl to `RectangleArea::area(rect)` because `Rectangle`'s table maps `AreaCalculatorComponent` to `RectangleArea`.

## Related constructs

`#[cgp_component]` is the root that most other constructs attach to. [`#[cgp_impl]`](cgp_impl.md) and [`#[cgp_provider]`](cgp_provider.md) are the idiomatic ways to write providers for a component; [`#[cgp_fn]`](cgp_fn.md) is the lighter-weight alternative when only one implementation is ever needed. [`delegate_components!`](delegate_components.md) wires a component to a provider on a concrete context, and [`check_components!`](check_components.md) verifies at compile time that the wiring is complete. The specialized forms [`#[cgp_type]`](cgp_type.md) and [`#[cgp_getter]`](cgp_getter.md) extend `#[cgp_component]` for abstract types and getters. The attributes [`#[derive_delegate]`](../attributes/derive_delegate.md), [`#[extend]`](../attributes/extend.md), and [`#[use_type]`](../attributes/use_type.md) modify what the macro generates.

## Known issues

A const generic parameter on the trait is not supported and is rejected with `const generic parameters are not supported on CGP component traits`. Because the provider trait records a component's extra parameters as a tuple of *types* in its `IsProviderFor` supertrait, and CGP's wiring dispatches on types rather than values, a const value has nowhere to live in that machinery. A const *item* on the trait is unaffected — writing `const CONSTANT: u64;` as a trait member is an associated const, not a generic parameter, and is supplied by a const-generic provider struct (for example `UseConstant<const CONSTANT: u64>`) in the usual way.

The macro must be applied to a trait, and anything else is rejected at parse time rather than lowered into non-compiling code: applying it to a struct, an enum, or a free function fails with a parse error naming the trait item it expected. Two rejections come from `#[use_type]` and are worth knowing here because a component definition is where a reader most often meets them: the equality form described under Syntax, and two imports that resolve to the same bare alias, which would make the substitution silently pick one and drop the other.

Finally, a modifier the component collector does not recognize is not rejected but forwarded, and it is forwarded onto *every* generated item rather than one. The unmatched attribute is re-attached to the consumer trait, and from there it is cloned onto the provider trait and onto the impls built from each — the two blanket impls and the `UseContext` and `RedirectLookup` provider impls. That is what lets `#[allow(...)]` or a doc comment apply where it should. It also means a misplaced `#[uses(...)]` surfaces as a *cannot find attribute* resolution error repeated once per generated item, none of which mentions `#[cgp_component]` — the same shape of error a genuine typo in an attribute name produces, several times over.

## Source

- Entry point: `cgp_component` in [crates/macros/cgp-macro-lib/src/cgp_component.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_component.rs), which drives the `preprocess → eval → to_items` pipeline.
- Logic: [crates/macros/cgp-macro-core/src/types/cgp_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_component/) — argument parsing in `args/`, the provider trait and blanket impls in `preprocessed/`, the standard provider impls (`UseContext`, `RedirectLookup`, `UseDelegate`) in `evaluated/`.
- Default identifiers `__Context__` and `{Provider}Component`: set in `args/component_args.rs`.
- Internal walkthrough (pipeline stages, synthesizing functions, corner cases, and the index of tests and snapshots): [implementation/entrypoints/cgp_component.md](../../implementation/entrypoints/cgp_component.md).
