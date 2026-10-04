# `#[cgp_fn]`

`#[cgp_fn]` turns a plain Rust function into a CGP trait with a single blanket implementation: from
one function body it generates a trait and a blanket impl for every context, so a context gains the
method with no separate wiring step.

## Purpose

`#[cgp_fn]` makes the simplest, most common form of CGP reachable with nothing more than a function.
Writing such a trait by hand means defining it, writing a blanket impl over a generic context, and
threading the dependencies the body needs through that impl's `where` clause. `#[cgp_fn]` collapses
all of that into a single function: you write the body as if `self` were a concrete value, mark the
values you want pulled from the context with `#[implicit]`, and the macro produces the trait and the
blanket impl that wires it up.

The result is a trait that any context implements automatically, as long as the context can satisfy
the impl-side dependencies. Because the generated impl is a blanket impl over a generic context,
there is no `delegate_components!` call, no provider type, and no component name: the method simply
becomes available on every type that has the fields the body reads. This is what makes `#[cgp_fn]`
the recommended entry point for basic CGP. A reader only needs to understand plain Rust functions to
use it, and the trait machinery stays hidden.

**The trade-off against [`#[cgp_component]`](cgp_component.md) is one implementation versus many.**
A `#[cgp_component]` trait can have many alternative providers, one chosen per context through
wiring, and that flexibility is exactly what costs the extra ceremony. `#[cgp_fn]` permits only one
implementation, the function body, and in exchange removes the wiring entirely. Reach for `#[cgp_fn]`
when an operation has a single natural definition, and graduate to `#[cgp_component]` only when a
context genuinely needs to swap in a different implementation. Starting with `#[cgp_fn]` costs
nothing if that happens: the trait keeps its name and method, so promoting it to a component leaves
every call site unchanged. The two interoperate: a `#[cgp_fn]` trait can depend on a
`#[cgp_component]` one, and vice versa, through [`#[uses]`](../attributes/uses.md).

Two neighbours cover what `#[cgp_fn]` does not. When the body's dependencies are other traits
rather than fields, [`#[blanket_trait]`](blanket_trait.md) builds the same single-implementation,
wiring-free trait from a trait with supertraits and default bodies. And a type the body needs lives
best in [`#[impl_generics]`](../attributes/impl_generics.md) while it flows only through implicit
arguments, climbing to an abstract type once it must appear in the trait's signature or two traits
must agree on it; a plain generic on the function is the form to avoid, since it lands on the trait
and every caller repeats it. [Naming a type dependency](../../guides/naming-a-type-dependency.md)
carries that decision.

## Syntax

`#[cgp_fn]` is applied as an attribute on a free function whose first parameter is normally `&self`
(or `&mut self`). The function name, in snake case, becomes the generated method name, and the trait
name defaults to that function name converted to PascalCase. A receiver is required once any
parameter is `#[implicit]`, and omitting it then fails with
`` The first argument of a function with implicit arguments must be `self` ``. A function with no
receiver and no implicit argument is accepted and yields a trait whose item is an associated
function, called as `<Context as Trait>::name()`; it reads nothing from the context, so it computes
the same result for every context. A `&mut self` function can take a mutable implicit argument and
write through it, provided that argument is the only implicit one, as Known issues records.

```rust
#[cgp_fn]
pub fn rectangle_area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
    width * height
}
```

Any parameter marked `#[implicit]` is removed from the method signature and instead fetched from a
field of the context whose name matches the parameter. The function above therefore generates a
`RectangleArea` trait with a `rectangle_area(&self) -> f64` method, and the body reads `width` and
`height` from the context rather than from arguments.

The trait name can be set explicitly by passing an identifier as the attribute argument, which
overrides the PascalCase default. This is useful when a verb-style trait name reads better than the
function name:

```rust
#[cgp_fn(CanCalculateRectangleArea)]
pub fn rectangle_area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
    width * height
}
```

**Generic parameters and a `where` clause on the function are split deliberately.** Every generic
parameter declared in the function's `<...>` list goes onto both the generated trait and the impl.
The `where` clause, by contrast, is treated as an impl-side dependency: it lands only on the impl,
hidden from the trait interface, exactly as the constraints in a hand-written blanket impl would be.

```rust
#[cgp_fn]
pub fn rectangle_area<Scalar>(
    &self,
    #[implicit] width: Scalar,
    #[implicit] height: Scalar,
) -> Scalar
where
    Scalar: Mul<Output = Scalar> + Copy,
{
    width * height
}
```

Here `Scalar` appears on both `RectangleArea<Scalar>` (the trait) and its impl, while
`Scalar: Mul<Output = Scalar> + Copy` appears only on the impl. A parameter that should exist on the
impl but not be a trait parameter can instead be written with the
[`#[impl_generics(...)]`](../attributes/impl_generics.md) attribute, which adds generic parameters to
the impl block alone:

```rust
#[cgp_fn]
#[impl_generics(Name: Display)]
pub fn greet(&self, #[implicit] name: &Name) -> String {
    format!("Hello, {}!", name)
}
```

**`#[cgp_fn]` intentionally does not support generics on the desugared *method* itself.** Generics
belong to the trait and impl, not to the generated method signature. Method-level generics are
uncommon in CGP and, where genuinely needed, are an advanced case better written as an explicit
blanket impl or a [`#[cgp_component]`](cgp_component.md) provider.

Several companion attributes refine the generated code, and each is documented separately:

- [`#[uses(...)]`](../attributes/uses.md) adds trait bounds on `Self` as impl-side dependencies.
- [`#[use_type(...)]`](../attributes/use_type.md) imports an abstract type and rewrites its
  occurrences to fully qualified form.
- [`#[use_provider(...)]`](../attributes/use_provider.md) supports higher-order providers.
- [`#[extend(...)]`](../attributes/extend.md) adds supertrait bounds to the generated trait.
- [`#[extend_where(...)]`](../attributes/extend_where.md) adds `where` predicates to the generated
  trait definition.
- [`#[impl_generics(...)]`](../attributes/impl_generics.md) declares generic parameters on the
  generated impl alone.

Each may be repeated, and each parses a comma-separated list inside one attribute. `#[use_provider]`
is the exception: its argument ends in a `+`-joined bound list, so a comma after it fails with
``expected `+` `` and a second binding needs a second attribute. `#[uses]` takes ordinary Rust
traits as readily as CGP ones. An [`#[async_trait]`](async_trait.md) written beneath `#[cgp_fn]` on
an `async fn` is not a companion attribute but is copied onto both generated items like any
unrecognized attribute, so the trait declares `-> impl Future` and the impl keeps its `async fn`.

## Syntax Grammar

The attribute argument of `#[cgp_fn]` is a single optional trait name:

```ebnf
CgpFnArgs -> TraitName?

TraitName -> IDENTIFIER
```

When the argument is omitted, the trait name defaults to the function name converted to PascalCase.
The `#[implicit]` markers on parameters and the companion attributes (`#[uses]`, `#[use_type]`,
`#[extend]`, and the rest) are separate attributes with their own grammars, documented on their own
pages.

## Expansion

`#[cgp_fn]` emits exactly two items: the trait carrying the method, and a blanket impl of that trait
for a generic context. Starting from the basic form:

```rust
#[cgp_fn]
pub fn rectangle_area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
    width * height
}
```

the macro produces the trait, with the `#[implicit]` parameters stripped from the signature, followed
by the blanket impl over the reserved context type `__Context__`. The implicit parameters become
`HasField` bounds on the impl and `get_field` bindings at the top of the body:

```rust
pub trait RectangleArea {
    fn rectangle_area(&self) -> f64;
}

impl<__Context__> RectangleArea for __Context__
where
    Self: HasField<Symbol!("width"), Value = f64>
        + HasField<Symbol!("height"), Value = f64>,
{
    fn rectangle_area(&self) -> f64 {
        let width: f64 = self.get_field(PhantomData::<Symbol!("width")>).clone();
        let height: f64 = self.get_field(PhantomData::<Symbol!("height")>).clone();

        width * height
    }
}
```

**The generated context type parameter is literally `__Context__`**, the same reserved name
`#[cgp_component]` uses, and references to it inside the impl appear as `Self`. The `Symbol!("...")`
shorthand stands for the type-level string the macro actually emits (for `width`,
`Symbol<5, Chars<'w', Chars<'i', Chars<'d', Chars<'t', Chars<'h', Nil>>>>>>`). Each implicit binding
follows the same conversion rules as [`#[cgp_auto_getter]`](cgp_auto_getter.md): an owned value gets
a trailing `.clone()`, an argument typed `&str` reads a `String` field through `.as_str()`, and a
borrowed `&Name` is taken by reference with no conversion. The full set of forms, including options,
slices, and mutable borrows, is in [`#[implicit]`](../attributes/implicit.md).

Generics and the `where` clause expand according to the split described above. Given the `Scalar`
example, the generic goes on both trait and impl, while the function's `where` bound stays on the
impl, ahead of the implicit `HasField` bounds:

```rust
pub trait RectangleArea<Scalar> {
    fn rectangle_area(&self) -> Scalar;
}

impl<__Context__, Scalar> RectangleArea<Scalar> for __Context__
where
    Scalar: Mul<Output = Scalar> + Copy,
    Self: HasField<Symbol!("width"), Value = Scalar>
        + HasField<Symbol!("height"), Value = Scalar>,
{
    fn rectangle_area(&self) -> Scalar { /* ... */ }
}
```

The bounds contributed by the companion attributes are layered into this same impl.
`#[extend(Trait)]` adds `Trait` as a supertrait of the generated trait, and `#[extend_where(...)]`
adds its predicates to the trait's own `where` clause; both are repeated on the impl, which must
satisfy whatever the trait requires. [`#[impl_generics(...)]`](../attributes/impl_generics.md)
inserts its parameters into the impl generics only, after the function's own generics. Its argument
is a comma-separated list of Rust `GenericParam` productions, so a lifetime and a const parameter are
accepted there alongside a bounded type parameter.

**The impl's `where` clause is assembled in a fixed order**, which helps when reading an expansion:

1. the function's own `where` clause;
2. a single `Self: …` predicate joining every `#[extend]` bound followed by every `#[uses]` bound;
3. the `#[extend_where]` predicates;
4. the implicit-argument `HasField` bounds;
5. the predicates `#[use_type]` and `#[use_provider]` contribute, in that order.

Two further placements are decided by the macro rather than written by the author:

- **The function's visibility moves to the generated trait**, and the method inside the impl is
  emitted with inherited visibility. So `pub fn rectangle_area` yields `pub trait RectangleArea`,
  while a private `fn` yields a trait visible only in its own module.
- **An attribute the macro does not recognize is copied onto both generated items**, which is what
  lets `#[allow(...)]`, `#[doc]`, and a doc comment on the function apply to the trait and its impl
  alike.

## Examples

A two-layer operation shows `#[cgp_fn]` composing with itself through `#[uses]`. The first function
defines the base area calculation; the second builds a scaled version on top of it, declaring its
dependency on the first with `#[uses(RectangleArea)]`:

```rust
use cgp::prelude::*;

#[cgp_fn]
pub fn rectangle_area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
    width * height
}

#[cgp_fn]
#[uses(RectangleArea)]
pub fn scaled_rectangle_area(&self, #[implicit] scale_factor: f64) -> f64 {
    self.rectangle_area() * scale_factor * scale_factor
}
```

A concrete context only needs the right fields; no wiring is required. Deriving `HasField` is enough
for both traits to apply automatically:

```rust
#[derive(HasField)]
pub struct Rectangle {
    pub width: f64,
    pub height: f64,
    pub scale_factor: f64,
}

fn report(rect: &Rectangle) {
    println!("base area  = {}", rect.rectangle_area());
    println!("scaled area = {}", rect.scaled_rectangle_area());
}
```

Because `Rectangle` derives `HasField` and carries `width`, `height`, and `scale_factor`, it
satisfies the `HasField` bounds on both generated impls, so `rect.rectangle_area()` and
`rect.scaled_rectangle_area()` both resolve directly through the blanket impls. There is no
`delegate_components!` block anywhere in this example.

## Related constructs

`#[cgp_fn]` is the lightweight counterpart to [`#[cgp_component]`](cgp_component.md), and it relates
to these constructs:

- [`#[cgp_component]`](cgp_component.md) also produces a trait usable through a method call, but
  allows many providers selected per context through
  [`delegate_components!`](delegate_components.md), where `#[cgp_fn]` allows a single implementation
  with no wiring.
- [`#[cgp_impl]`](cgp_impl.md) shares its `#[implicit]` argument mechanism, and
  [`#[cgp_auto_getter]`](cgp_auto_getter.md) and the underlying [`HasField`](../traits/has_field.md)
  trait share its field-access semantics.
- The companion attributes [`#[uses]`](../attributes/uses.md), [`#[use_type]`](../attributes/use_type.md),
  [`#[use_provider]`](../attributes/use_provider.md), [`#[extend]`](../attributes/extend.md),
  [`#[extend_where]`](../attributes/extend_where.md), and
  [`#[impl_generics]`](../attributes/impl_generics.md) shape what the macro generates.
- [`#[blanket_trait]`](blanket_trait.md) emits the same style of blanket impl; the difference is that
  `#[cgp_fn]` derives the trait and its body from a function rather than from a trait with default
  methods.

## Known issues

**A mutable implicit argument must be the only implicit argument.** Its `get_field_mut` read borrows
the whole context exclusively for the rest of the body, so it cannot coexist with another field
read, and the macro rejects the combination with
`` a `&mut` implicit argument must be the only implicit argument, since its mutable borrow of the context conflicts with reading any other field ``.
Any number of immutable implicit arguments combine freely.

**An `#[impl_generics]` parameter cannot appear in the trait's own signature.** Only the generated
impl declares it, so a return type or an explicit parameter that names it is unresolved in the
trait: a bare `Db` fails with ``E0425: cannot find type `Db` in this scope`` and a qualified
`Db::Row` with ``E0433: cannot find type `Db` in this scope``. The fix is to keep the type out of the
signature or to make it an abstract type; [`#[impl_generics]`](../attributes/impl_generics.md)
records this and its other deferred failures.

**A function named with a raw identifier needs an explicit trait name.** The default name is the
function name in PascalCase, and for `fn r#type` the macro builds it from the raw spelling, so the
compiler aborts with `custom attribute panicked` (`"R#type"` is not a valid identifier). Naming the
trait explicitly, as `#[cgp_fn(Type)]`, avoids it.

## Source

- Entry point: `cgp_fn` in
  [crates/macros/cgp-macro-lib/src/cgp_fn.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_fn.rs),
  which parses the optional trait-name identifier and the function, then runs
  `item.preprocess()?.to_items()?`.
- Logic:
  [crates/macros/cgp-macro-core/src/types/cgp_fn/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_fn/):
  `item.rs` performs the PascalCase default-name derivation (`to_camel_case_str`), implicit-argument
  extraction, and attribute parsing; `preprocessed.rs` builds the trait in `to_item_trait` and the
  blanket impl in `to_item_impl`, including the generics/`where`-clause split and the insertion of
  the leading `__Context__` parameter.
- Implicit-argument handling:
  [crates/macros/cgp-macro-core/src/types/implicits/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/implicits/);
  the companion-attribute parsing in
  [crates/macros/cgp-macro-core/src/types/attributes/function.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/function.rs).
- Internal walkthrough (the pipeline stages, the function that synthesizes each generated item, the
  corner-case handling, and the index of tests and expansion snapshots):
  [implementation/entrypoints/cgp_fn.md](../../implementation/entrypoints/cgp_fn.md).
