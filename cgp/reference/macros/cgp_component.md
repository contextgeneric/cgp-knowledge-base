# `#[cgp_component]`

`#[cgp_component]` is the foundational CGP macro: applied to a trait, it turns that ordinary Rust
trait into a full CGP component, made of a consumer trait, a matching provider trait, and the blanket
implementations that let a context delegate the trait's behavior to a freely chosen provider.

## Purpose

`#[cgp_component]` lifts a single trait into a pair of traits that separate *calling* a trait's
methods from *implementing* them. A normal Rust trait conflates the two: the type that implements
`Area` is the same type that callers invoke `.area()` on, and Rust's coherence rules then allow only
one implementation per type. CGP breaks this conflation by generating two traits from one
definition. The **consumer trait** is what callers use (`context.area()`). The **provider trait** is
what implementers write, with the original `Self` moved into an explicit `Context` type parameter so
that any number of provider types can implement it without colliding.

The payoff is that providers become first-class, named, swappable units. Because a provider
implements the provider trait for a generic `Context` rather than for itself, the usual orphan and
overlap restrictions do not bite, and a crate can define many alternative providers for the same
component. A concrete context then picks one provider per component through wiring (see
[`delegate_components!`](delegate_components.md)), and the generated blanket impls route the
consumer-trait call through that choice. Without `#[cgp_component]`, a trait is just a vanilla Rust
trait and takes no part in this mechanism. The choice costs nothing at run time: the compiler
resolves the provider while it type-checks the call and monomorphizes it into a direct, statically
dispatched call, with no runtime table or vtable.

**A component is worth its cost only when a trait needs more than one implementation and the
choice belongs to the type using it.** A component is a consumer trait, a provider trait, a marker,
and a wiring line per context. A trait with one implementation ever is better written with
[`#[cgp_fn]`](cgp_fn.md), which can later be promoted to a component without touching its call
sites. One implementation per type chosen program-wide is what a plain Rust trait already does, a
trait whose implementations each serve one concrete type can be implemented directly on that type,
and a small closed set of variants reads better as an `enum` and a `match`. Named providers pay once
a second context wants the same implementation, or once an implementation should compose with a
wrapper. The [modularity hierarchy](../../concepts/modularity-hierarchy.md) and
[sizing a component](../../guides/sizing-a-component.md) carry the full argument.

**Whether a component is self-targeted or parameter-targeted belongs to the trait, and it decides
how much the wiring can vary.** A component is *self-targeted* when its operation acts on the `Self`
type, as `CanCalculateArea` computes the area of the context itself. It is *parameter-targeted* when
the operation is about a type parameter while `Self` only supplies the decisions, as
`CanSerializeValue<Value>` is. A parameter alone does not decide this: in `CanCompute<Code, Input>`
the target is `Input`, while `Code` is a selector the wiring dispatches on, and a component may carry
both. The choice matters because a self-targeted component's wiring is keyed on the type the
operation acts on, so that type gets one provider for the whole program. A parameter-targeted
component's wiring is keyed on a context, which can be defined as many times as needed. The
[modularity hierarchy](../../concepts/modularity-hierarchy.md) works through which to reach for.

## Syntax

The macro is applied as an attribute on a trait definition and takes the provider trait's name as
its argument. The simplest form passes a bare identifier:

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}
```

Here `CanCalculateArea` is the consumer trait, named in verb form (`CanDoSomething`), and
`AreaCalculator` is the provider trait, named in noun form (`SomethingDoer`, or with a `Provider`
suffix when a noun does not fit). When more control is needed, the macro accepts a key/value form
instead of a bare identifier:

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

The three keys correspond to the three names the macro needs, and only `provider` lacks a default.
A bare identifier is shorthand for setting `provider` alone.

- **`provider`** sets the provider trait name, and is required.
- **`name`** sets the component name type. It defaults to the provider name with a `Component`
  suffix, so `AreaCalculator` yields `AreaCalculatorComponent`.
- **`context`** sets the identifier of the generic context type parameter in the generated provider
  trait. It defaults to `__Context__`, a deliberately unusual name chosen to avoid clashing with the
  user's own type parameters.

**The trait body may declare any number of items.** A component trait may carry any number of
methods, associated types, and associated consts, and every one of them is reproduced on the
generated provider trait, so a provider implements the whole set. CGP's own
[`CanCompute`](../components/computer.md) declares an associated `Output` beside its `compute`
method, and a [getter trait](cgp_getter.md) commonly declares one method per field. The only
rejected declaration is a **const generic parameter** on the trait, for the reason given under Known
issues. Which items are worth grouping into one component is a design question rather than a limit
of the macro, and [sizing a component](../../guides/sizing-a-component.md) answers it: everything in
one component is decided by one provider, so items that a single provider choice settles belong
together, while items that separate choices settle are better off in separate components.

Four companion attributes extend the macro for special cases, and each is documented separately:

- [`#[extend(...)]`](../attributes/extend.md) adds supertrait bounds to the generated consumer trait.
- [`#[use_type(...)]`](../attributes/use_type.md) imports an abstract associated type, adding the
  owning trait as a supertrait and rewriting the bare alias throughout the signatures.
- [`#[derive_delegate(...)]`](../attributes/derive_delegate.md) generates `UseDelegate` providers
  that dispatch on a generic parameter.
- [`#[prefix(@path in Namespace)]`](../attributes/prefix.md) registers the component into a
  namespace under a type-level path, emitting one namespace impl per attribute.

Any of the four may be repeated. `#[extend]` and `#[use_type]` also accept a comma-separated list in
one attribute. `#[derive_delegate]` takes a single dispatch spec per attribute (whose parameter may
itself be a parenthesized tuple), so a second dispatcher needs a second attribute.

**Three modifiers that other host macros accept are not accepted here, and the macro does not report
the mistake itself.** `#[uses(...)]`, `#[extend_where(...)]`, and `#[use_provider(...)]` are
meaningful only where there is a provider impl or a generated trait definition to attach them to, so
the component collector does not match them. An unrecognized attribute is passed straight through
onto the items the macro emits, where the compiler rejects it as
`cannot find attribute … in this scope`. None of these modifiers is a standalone proc macro, so there is nothing else for the name to
resolve to. The equivalent of `#[uses]` on a component is a supertrait, written with `#[extend]`.

The related macros [`#[cgp_type]`](cgp_type.md) and [`#[cgp_getter]`](cgp_getter.md) build on
`#[cgp_component]` to derive additional constructs for abstract-type and getter components
respectively.

**Import an abstract type with `#[use_type]` rather than writing its supertrait by hand.** This
applies when a component's supertrait exists only to supply an abstract type the trait's own
signatures name, most commonly [`HasErrorType`](../components/has_error_type.md), whose `Error` a
fallible method returns. Annotating the trait with `#[use_type(HasErrorType.Error)]` adds
`HasErrorType` as a supertrait *and* rewrites a bare `Error` in the signatures to
`<Self as HasErrorType>::Error`. The definition then reads
`pub trait CanLoad { fn load(&self, path: &str) -> Result<String, Error>; }` rather than spelling out
`: HasErrorType` and `Self::Error`. For a supertrait `#[use_type]` cannot express (a method
supertrait with no associated type to import, or a bound the trait does not name in its signatures),
declare it with `#[extend(...)]` in preference to native `: Supertrait` syntax, which reads as
OOP-style inheritance rather than the trait import a CGP supertrait actually is. A local associated
type the trait declares itself, such as a handler's `type Output`, always stays written as
`Self::Output`; it is not imported, so `#[use_type]` neither lists nor rewrites it.

**The equality form of `#[use_type]` is refused on a component trait.** The form
`#[use_type(HasScalarType.{Scalar = f64})]` pins an imported type to a concrete one. Pinning belongs
to a provider that has decided the type, not to the definition every provider must satisfy, so the
macro rejects the `=` with `Type equality constraints cannot be used in component trait definition`.
Every other form (the `in Context` clause, the `as Alias` rename, the braced list, and generic
arguments on the owning trait) is accepted here exactly as it is on `#[cgp_impl]` and `#[cgp_fn]`.

## Syntax Grammar

The attribute argument of `#[cgp_component]` is either a bare provider name or a comma-separated set
of keyed values:

```ebnf
CgpComponentArgs -> ProviderName
                  | KeyValueArg ( `,` KeyValueArg )* `,`?

ProviderName     -> IDENTIFIER

KeyValueArg      -> `name` `:` ComponentName
                  | `provider` `:` IDENTIFIER
                  | `context` `:` IDENTIFIER

ComponentName    -> IDENTIFIER ( `<` NameParam ( `,` NameParam )* `,`? `>` )?

NameParam        -> LIFETIME_OR_LABEL
                  | IDENTIFIER
                  | `const` IDENTIFIER `:` Type
```

`ProviderName` is the bare-identifier form and is shorthand for setting `provider` alone. In the
key/value form each of the three keys may appear at most once and in any order, and `provider` is
required; the other two have defaults (`context` is `__Context__`, and `name` is the provider name
with a `Component` suffix). The parser rejects a repeated key with `duplicate key is not allowed`,
an unrecognized one with `unknown key <key>`, and a missing `provider` with
``the `provider` key must be given``. `IDENTIFIER` is a Rust identifier token.

**The component name may carry a list of bare generic parameter names**, such as
`name: ShapeComponent<Shape>`, which the marker struct then declares. Each must be one of the
trait's own parameters, because the macro writes the name, parameters included, wherever the
component appears; Known issues records what an undeclared one does. Anything more is rejected:

- a bound fails with ``trait bounds (`A: Clone`) are not allowed in type generics``, and a lifetime
  bound with ``lifetime bounds (`'a: 'b`) are not allowed in type generics``;
- a default fails with ``default type parameters (`A = B`) are not allowed in type generics``;
- a type that is not a single identifier, such as `Vec<u8>`, fails to parse (``expected `,` ``),
  while a single identifier such as `u32` is read as a parameter *name*, not as the type;
- a const parameter (`const N: usize`) parses, which is why `NameParam` lists it, but then fails
  inside the macro, as Known issues records.

A provider for such a component written with [`#[cgp_impl]`](cgp_impl.md) must name the component
explicitly, as in `#[cgp_impl(new SquareArea: AreaCalculatorComponent<Square>)]`, because the
default component name `{Provider}Component` carries no arguments and fails with `E0107` (missing
generics). The provider name and the context name take no generics. The attribute delimiter shown in
Syntax (`(...)` for the bare form and `{...}` for the key/value form) is ordinary Rust attribute
syntax; the argument tokens inside follow this grammar whichever delimiter is used.

## Expansion

`#[cgp_component]` replaces the annotated trait with five top-level items plus a set of standard
provider impls. The five are emitted in a fixed order (consumer trait, consumer blanket impl,
provider trait, provider blanket impl, component marker), and are described below in the order that
makes them easiest to read, which pairs each trait with the impl that routes to it. Starting from
this input:

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

Second, it emits the **provider trait**: the consumer trait with `Self` replaced by an explicit
leading `Context` type parameter, and every `self`/`Self` reference rewritten to the context value
and type (literally `__context__` and `__Context__` in the emitted code). The provider trait carries
an [`IsProviderFor`](../traits/is_provider_for.md) supertrait that captures the component name and
context, so that unsatisfied dependencies surface as readable compiler errors. The supertrait's third
argument is the `Params` tuple of the component's extra type parameters; for a component with no
parameters beyond the context it is the empty `()`:

```rust
pub trait AreaCalculator<Context>:
    IsProviderFor<AreaCalculatorComponent, Context, ()>
{
    fn area(context: &Context) -> f64;
}
```

**An associated type the trait declares for itself is the one `Self` the rewrite leaves alone.** The
provider trait keeps the declaration, so a `Self::Output` in the consumer trait stays `Self::Output`
in the provider trait, where it names the provider's own `Output`, and each provider chooses the
type it returns. The consumer blanket impl then sets
`type Output = <Context as OutputProducer<Context>>::Output`, and the provider blanket impl reads the
same projection through its delegate.

**The provider trait's supertrait list is replaced by `IsProviderFor` rather than extended with it,
and the consumer trait's own supertraits become a `where` predicate on the context.** That holds for
supertraits written natively, added by [`#[extend]`](../attributes/extend.md), or added by
[`#[use_type]`](../attributes/use_type.md). It follows from the `Self`-to-`Context` move: a supertrait
of the consumer trait constrains the type the operation acts on, which on the provider side is the
context parameter and not `Self`. So
`#[cgp_component(Greeter)] #[extend(HasName)] pub trait CanGreet { … }` yields:

```rust
pub trait Greeter<Context>: IsProviderFor<GreeterComponent, Context, ()>
where
    Context: HasName,
{
    fn greet(context: &Context);
}
```

The same predicate is added to *every* item the macro emits that mentions the context: the consumer
blanket impl, the provider blanket impl, and the `UseContext` and `RedirectLookup` provider impls each
gain their own `Context: HasName`, since none of them can apply where the supertrait does not hold.
A user-written provider must satisfy it too, because a trait's `where` bound is not implied for its
implementations: a `#[cgp_impl]` provider for `Greeter` declares `#[uses(HasName)]` (or the matching
`#[use_type]` for a type supertrait) even when its body never calls `name()`, and without it fails at
its own definition with ``E0277 the trait bound `__Context__: HasName` is not satisfied``.

**A component trait's methods may carry default bodies, and the body travels to the provider trait
rather than staying behind on the consumer trait.** This is the second thing the `Self`-to-`Context`
move reaches, and it is what makes a provider able to inherit a default at all. The body is rewritten
along with the signature, so `fn greet(&self) -> String { format!("Hello, {}!", self.name()) }` on
the consumer trait becomes
`fn greet(context: &Context) -> String { format!("Hello, {}!", context.name()) }` on the provider trait, keeping its default. The consumer trait keeps its own copy
of the body as well, the same duplication [`#[blanket_trait]`](blanket_trait.md) produces.

The payoff is that an **empty provider impl inherits the default**, which is how
[`UseDefault`](../providers/use_default.md) works and the reason a provider can be declared with
nothing in its block. `UseDefault` is not in the prelude and comes from `cgp::core::component`:

```rust
#[cgp_impl(UseDefault)]
impl<Context: HasName> Greeter for Context {}
```

Third, it emits the **consumer blanket impl**, which says that any context implementing the provider
trait *for itself* automatically gets the consumer trait. This is the bridge that lets callers write
`context.area()`:

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

Fourth, it emits the **provider blanket impl**, which lets any provider that delegates this
component (via [`DelegateComponent`](../traits/delegate_component.md)) inherit the provider trait
from the provider it delegates to. This is the mechanism `delegate_components!` drives: it turns a
context into a type-level table whose entry for `AreaCalculatorComponent` names the chosen provider.

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

**The `IsProviderFor` bound sits on `Provider` itself, beside the `DelegateComponent` bound, not on
`Provider::Delegate`.** The blanket impl of `IsProviderFor` (generated by `delegate_components!`)
forwards a component's dependencies through `Provider`, so requiring `Provider: IsProviderFor<…>` is
what threads those dependencies down the delegation chain and surfaces them in error messages.

Fifth, it emits the **component name struct**, a zero-sized marker that serves as the key into
delegation tables:

```rust
pub struct AreaCalculatorComponent;
```

**Beyond these five items, the macro generates standard provider impls that make the component
usable in the patterns CGP relies on.** Two are unconditional and two are one per attribute:

- A [`UseContext`](../providers/use_context.md) impl, so that the provider trait can be satisfied by
  routing back through a context's own consumer-trait implementation. Its `where` clause adds
  `__Context__: CanCalculateArea` to any supertrait predicates the provider trait carries, and each
  method body forwards to the consumer method.
- A [`RedirectLookup`](../providers/redirect_lookup.md) impl, which is what the `open` statement of
  [`delegate_components!`](delegate_components.md) and the [namespace](cgp_namespace.md) machinery
  resolve through. It is written for `RedirectLookup<__Components__, __Path__>` and looks the
  component up as `__Components__: DelegateComponent<__Path__>`.
- One [`UseDelegate`](../providers/use_delegate.md) impl per
  [`#[derive_delegate(...)]`](../attributes/derive_delegate.md) attribute, dispatching on the named
  generic parameter.
- One namespace impl per [`#[prefix(@path in Namespace)]`](../attributes/prefix.md) attribute,
  binding the component's key inside that namespace to a `RedirectLookup` down the given path with the
  component's own name appended.

Each of the provider impls in the first three bullets is emitted together with a matching
[`IsProviderFor`](../traits/is_provider_for.md) impl under the same `where` clause, so wiring a
component to `UseContext`, `open`-ing it, or dispatching it through `UseDelegate` keeps the
dependency-surfacing error messages. The `RedirectLookup` impl additionally requires the redirected
provider to be `IsProviderFor` the component, which is how a missing dependency is reported through
an `open` entry or a namespace path. The namespace impls carry no `IsProviderFor` impl, since they
are table entries rather than providers.

**The `RedirectLookup` impl is where a component's own type parameters join a path, and it is the
mechanism behind `@AreaCalculatorComponent.Rectangle`.** When the component has type parameters, the
impl does not look up `__Path__` directly. It requires `__Path__: ConcatPath<PathCons<Shape, Nil>>`
and looks up the *extended* path `<__Path__ as ConcatPath<PathCons<Shape, Nil>>>::Output`, so the
component's parameters, gathered into a [`Path!`](path.md) in declaration order
(`PathCons<Shape, PathCons<Scalar, Nil>>` for two), are appended to whatever path the lookup arrived
on. Only **type** parameters take part; lifetimes and const parameters are filtered out, since
neither can key a path. A component with no type parameters gets the simpler form, which looks
`__Path__` up unchanged.

A few details of the expansion are easy to get wrong:

- **The generated parameters carry reserved names**, not the readable ones used above. The context
  parameter is literally `__Context__` unless overridden, and the provider parameter in the provider
  blanket impl is `__Provider__`. The examples here use `Context`, `context`, and `Provider` for
  legibility.
- **The provider trait's receiver is renamed to `__context__`**, the snake-case form of the context
  identifier. A name that does not already start with an underscore is also wrapped in double
  underscores, so a `context: Ctx` override yields a `__ctx__` receiver.
- **A component's own generic parameters follow the context parameter** in the provider trait,
  except lifetimes, which Rust requires to lead: `HasReference<'a, T>` yields
  `ReferenceGetter<'a, __Context__, T>`.
- **The same parameters are grouped into a parenthesized list in the `IsProviderFor` `Params`
  position.** The tuple holds *types*, so each parameter is recorded by name and a **lifetime is
  lifted into [`Life<'a>`](../types/life.md)**. `CanCalculateArea<Shape>` gives
  `IsProviderFor<AreaCalculatorComponent, __Context__, (Shape)>`, a two-parameter component gives
  `(Shape, Scalar)`, and `HasReference<'a, T>` gives `(Life<'a>, T)`. The single-parameter `(Shape)`
  has no trailing comma, so it is the type `Shape` in parentheses rather than a one-element tuple;
  the same rule applies wherever the tuple is written, so the two sides always agree. Bounds and
  defaults are dropped, since the tuple only names the parameters positionally, and a const parameter
  has no representation at all, which is why it is rejected outright, per Known issues.

## Examples

A complete component, from definition through wiring to use, ties the pieces together. First the
component and a provider for it:

```rust
use cgp::prelude::*;

#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_impl(new RectangleAreaCalculator)]
impl AreaCalculator {
    fn area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
        width * height
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
        AreaCalculatorComponent: RectangleAreaCalculator,
    }
}

check_components! {
    Rectangle {
        AreaCalculatorComponent,
    }
}

fn print_area(rect: &Rectangle) {
    println!("area = {}", rect.area()); // CanCalculateArea, via RectangleAreaCalculator
}
```

The call `rect.area()` resolves through the consumer blanket impl to `Rectangle::area(rect)`, which
resolves through the provider blanket impl to `RectangleAreaCalculator::area(rect)`, because
`Rectangle`'s table maps `AreaCalculatorComponent` to `RectangleAreaCalculator`. The implicit `width`
and `height` arguments are read from `Rectangle`'s fields, which `#[derive(HasField)]` exposes, and
the `check_components!` block makes a missing field fail at the wiring rather than at the call.
`Rectangle` here is a value context: the wired type is the shape whose area is computed. This matches
the [area calculation](../../../examples/area-calculation.md) example, which develops the same
provider.

## Related constructs

`#[cgp_component]` is the root most other constructs attach to:

- [`#[cgp_impl]`](cgp_impl.md) and [`#[cgp_provider]`](cgp_provider.md) are the idiomatic ways to
  write providers for a component.
- [`#[cgp_fn]`](cgp_fn.md) is the lighter-weight alternative when only one implementation is ever
  needed.
- [`delegate_components!`](delegate_components.md) wires a component to a provider on a concrete
  context, and [`check_components!`](check_components.md) verifies at compile time that the wiring is
  complete.
- The specialized forms [`#[cgp_type]`](cgp_type.md) and [`#[cgp_getter]`](cgp_getter.md) extend
  `#[cgp_component]` for abstract types and getters.
- The attributes [`#[derive_delegate]`](../attributes/derive_delegate.md),
  [`#[extend]`](../attributes/extend.md), [`#[use_type]`](../attributes/use_type.md), and
  [`#[prefix]`](../attributes/prefix.md) modify what the macro generates.

## Known issues

**A const generic parameter on the trait is not supported**, and is rejected with
`const generic parameters are not supported on CGP component traits`. The provider trait records a component's extra
parameters as a tuple of *types* in its `IsProviderFor` supertrait, and CGP's wiring dispatches on
types rather than values, so a const value has nowhere to live in that machinery. A const *item* on
the trait is unaffected: `const CONSTANT: u64;` as a trait member is an associated const, not a
generic parameter, and is supplied by a const-generic provider struct (for example
`UseConstant<const CONSTANT: u64>`) in the usual way.

**The macro must be applied to a trait**, and anything else is rejected at parse time rather than
lowered into non-compiling code: applying it to a struct, an enum, or a free function fails with
``expected `trait` ``. Three rejections come from `#[use_type]` and are worth knowing here, because
a component definition is where a reader most often meets them: the equality form described under
Syntax; two imports that resolve to the same bare alias, which would make the substitution silently
pick one and drop the other, rejected with
`Multiple abstract types cannot share the same identifier or alias`; and imports that resolve
through one another in a cycle. [`#[use_type]`](../attributes/use_type.md) documents all three.

**A modifier the component collector does not recognize is forwarded onto the generated items
rather than rejected.** The unmatched attribute is re-attached to the consumer trait, and from there
it is cloned onto the provider trait and onto the impls built from each: the two blanket impls, the
`UseContext` and `RedirectLookup` provider impls, and any `UseDelegate` impl. The marker struct, the
namespace impls, and the `IsProviderFor` impls do not receive it. That is what lets `#[allow(...)]`
or a doc comment apply where it should. It also means a misplaced `#[uses(...)]` surfaces as a
``cannot find attribute `uses` in this scope`` resolution error that does not mention
`#[cgp_component]`. Every copy carries the attribute's own span, so rustc deduplicates them into one
error on the attribute's line, and its help may suggest a similarly named built-in (`#[used]` for
`#[uses]`), which leads away from the fix. A genuine typo in an attribute name produces the same
error.

**A `name:` parameter that the trait does not declare is accepted and fails downstream.**
`#[cgp_component { provider: Shape, name: ShapeComponent<T> }]` on a trait without a `T` parses,
and the compiler then reports ``error[E0425]: cannot find type `T` in this scope`` at the `T`,
followed by an `E0034` about the generated impls, because the name is written into impl positions
where `T` is not in scope. The correct behavior would be a spanned error from the macro naming the
parameter the trait lacks.

**Attributes on a trait *method* follow a different path.** Each is kept on the consumer trait's
method and copied onto the matching method declaration of the provider trait, while the generated
impls' methods carry none. For `#[track_caller]` that is enough, because Rust applies the attribute
on a trait method declaration to every impl of the method. It therefore reaches both blanket impls,
the `UseContext`, `RedirectLookup`, and `UseDelegate` impls, and every provider, so a caller-location
lookup such as `Location::caller()` inside a provider reports the line that called the consumer
method, through direct and `open` wiring alike. [`CanRaiseError`](../components/can_raise_error.md)
relies on this so that error libraries record where an error was raised.

**A method parameter whose pattern is not a plain identifier fails to expand.** The generated
forwarding impls call the delegate with each parameter by name, so the macro reads every parameter
pattern as an identifier. A `_` parameter, which Rust allows in a bodiless trait method, and a
destructuring pattern in a default method, such as `(a, b): (u32, u32)`, both fail with
`expected identifier` followed by ``failed to parse internal tokens to type `proc_macro2::Ident` ``. The
correct behavior would be to bind such a parameter to a fresh name in the forwarding impls. Until
then, give every parameter a name, such as `_value: u32`, and destructure inside a default body.

**A const parameter in the `name:` list is accepted by the parser but not handled by the code that
uses the name as a type.** `#[cgp_component { provider: Foo, name: FooComponent<const N: usize> }]`
fails with ``failed to parse internal tokens to type `syn::generics::TypeParamBound` ``, because the
component name is rendered with `const N: usize` in a type position. The correct behavior would be to
reject the parameter with a spanned error, or to render it as the bare `N` where the name is used as
a type.

## Source

- Entry point: `cgp_component` in
  [crates/macros/cgp-macro-lib/src/cgp_component.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_component.rs),
  which drives the `preprocess → eval → to_items` pipeline.
- Logic:
  [crates/macros/cgp-macro-core/src/types/cgp_component/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_component/):
  argument parsing in `args/`, the provider trait and blanket impls in `preprocessed/`, and the
  standard provider impls (`UseContext`, `RedirectLookup`, `UseDelegate`) in `evaluated/`.
- Default identifiers `__Context__` and `{Provider}Component`: set in `args/component_args.rs`.
- Internal walkthrough (pipeline stages, synthesizing functions, corner cases, and the index of tests
  and snapshots): [implementation/entrypoints/cgp_component.md](../../implementation/entrypoints/cgp_component.md).
