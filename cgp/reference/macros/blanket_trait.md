# `#[blanket_trait]`

`#[blanket_trait]` generates a blanket implementation for a trait whose methods and constants have
default definitions, turning it into an extension trait that hides its supertrait dependencies
behind a small interface.

## Purpose

`#[blanket_trait]` removes the boilerplate of the blanket impl that makes an extension trait work.
The blanket-trait pattern, which CGP itself is built on, uses the `where` clause of a blanket impl
to keep the constraints generic code needs out of the interface its callers see. Written by hand,
the pattern repeats itself: the supertrait bounds appear on the trait and again on the impl, and
each default method body is copied into the impl. With `#[blanket_trait]` the trait is written once,
with its default bodies, and the macro generates the matching impl.

The pattern is the impl-side dependency in its simplest form. A trait declared
`pub trait FooBar: Foo + Bar` with a default `foo_bar` method shows callers only `foo_bar`, while
the generated impl requires `Foo + Bar`. Any context satisfying both gains `FooBar`, and a generic
caller that needs `foo_bar` bounds on `FooBar` alone rather than repeating `Foo + Bar`, which is the
advantage over a free generic function.

`#[blanket_trait]` is not a CGP component. It produces an ordinary trait and an ordinary blanket
impl, with no consumer and provider split, no component name, and no wiring. It fits an operation
with exactly one definition that should still read as a method. When the operation later needs
alternative implementations, promote the trait to a [`#[cgp_component]`](cgp_component.md).

**The discriminator against [`#[cgp_fn]`](cgp_fn.md) is what the body depends on.** Both produce a
single-implementation trait with no wiring; `#[cgp_fn]` suits dependencies on context *fields*,
read through `#[implicit]` arguments, while `#[blanket_trait]` suits dependencies on other traits,
stated as supertraits. The empty-body form stands in for trait aliases, which stable Rust lacks,
and is worth it only where writing the bounds out at the use site reads badly. A plain generic
function is simpler still when no caller is generic over the type, since then the propagation of
its `where` clause never arises.

## Syntax

`#[blanket_trait]` is not in the prelude, unlike the other macros in this section, so it must be
imported as `use cgp::core::macros::blanket_trait;`. Without the import, the error is
``cannot find attribute `blanket_trait` in this scope``, which names the attribute rather than the
missing import.

The attribute is applied to a trait definition. Every method and constant in the trait must have a
default, since the defaults are what the generated impl supplies, and associated types may declare
bounds. The trait's supertraits become the dependencies the blanket impl requires:

```rust
#[blanket_trait]
pub trait FooBar: Foo + Bar {
    fn foo_bar(&self) {
        self.foo();
        self.bar();
    }
}
```

An optional argument names the context type parameter of the generated impl. It defaults to
`__Context__`, the reserved identifier the CGP macros share to avoid colliding with the user's own
parameters:

```rust
#[blanket_trait(Ctx)]
pub trait FooBar: Foo + Bar { /* ... */ }
```

The trait may carry generic parameters and associated types. Its generic parameters are copied onto
the impl, with the context parameter after them, so `pub trait Scaled<T: Copy>: Foo` gets
`impl<T: Copy, __Context__> Scaled<T> for __Context__`. Each associated type becomes a further
generic parameter on the impl, bound through the supertraits, as Expansion shows. A trait with no
supertraits still gets the `__Context__:` predicate, with an empty bound list, so its impl covers
every type.

## Syntax Grammar

The attribute argument is a single optional context name:

```ebnf
BlanketTraitArgs -> ContextName?

ContextName      -> IDENTIFIER
```

An omitted name defaults to `__Context__`.

## Expansion

`#[blanket_trait]` emits two items: the trait unchanged, and a blanket impl for a generic context
that supplies each default and requires the trait's supertraits in its `where` clause. Given:

```rust
#[blanket_trait]
pub trait FooBar: Foo + Bar {
    fn foo_bar(&self) {
        self.foo();
        self.bar();
    }
}
```

the macro emits:

```rust
pub trait FooBar: Foo + Bar {
    fn foo_bar(&self) {
        self.foo();
        self.bar();
    }
}

impl<__Context__> FooBar for __Context__
where
    __Context__: Foo + Bar,
{
    fn foo_bar(&self) {
        self.foo();
        self.bar();
    }
}
```

The trait keeps its default bodies, so each body appears on both the trait and the impl. The impl
supplies the method for every qualifying context, and the retained default is harmless. Expect the
duplication when reading an expansion.

A trait with no methods generates an empty impl, which makes it a trait alias in everything but
name:

```rust
#[blanket_trait]
pub trait FooBar: Foo + Bar {}
```

expands to:

```rust
pub trait FooBar: Foo + Bar {}

impl<__Context__> FooBar for __Context__
where
    __Context__: Foo + Bar,
{}
```

### Associated types

An associated type lets the trait lift a type out of a supertrait, which is one of the pattern's
main uses. Each associated type becomes a generic parameter on the impl, every `Self::` path naming
it is rewritten to that parameter, and the impl assigns the parameter back to the associated type.
Given:

```rust
#[blanket_trait]
pub trait HasFooTypeAtBar: HasFooTypeAt<Bar, Foo = Self::FooBar> {
    type FooBar;
}
```

the macro emits:

```rust
pub trait HasFooTypeAtBar: HasFooTypeAt<Bar, Foo = Self::FooBar> {
    type FooBar;
}

impl<__Context__, FooBar> HasFooTypeAtBar for __Context__
where
    __Context__: HasFooTypeAt<Bar, Foo = FooBar>,
{
    type FooBar = FooBar;
}
```

Bounds on an associated type move into the impl's `where` clause as predicates on its parameter, so
`type FooBar: Clone` adds `FooBar: Clone` after the supertrait requirement. An associated type needs
no default, because the macro writes the assignment itself. The rewrite of `Self::FooBar` to the
parameter covers the whole trait, method signatures and bodies included, so a default method such as
`fn clone_foo(value: &Self::FooBar) -> Self::FooBar` reads the impl's `FooBar` parameter in the
impl's copy.

### Associated constants

Associated constants are supplied like methods. Each constant's default expression becomes the
impl's definition, and the trait keeps its default as well.

## Examples

This extension trait hides two dependencies behind one method. `FooBar` is defined once, with its
body, and applies to any context implementing both `Foo` and `Bar`:

```rust
use cgp::prelude::*;
use cgp::core::macros::blanket_trait;

pub trait Foo {
    fn foo(&self);
}

pub trait Bar {
    fn bar(&self);
}

#[blanket_trait]
pub trait FooBar: Foo + Bar {
    fn foo_bar(&self) {
        self.foo();
        self.bar();
    }
}

pub struct Context;

impl Foo for Context {
    fn foo(&self) {}
}

impl Bar for Context {
    fn bar(&self) {}
}

fn run(ctx: &Context) {
    ctx.foo_bar(); // available because Context: Foo + Bar
}
```

`Context` implements only `Foo` and `Bar`, and the generated blanket impl supplies `foo_bar`. A
caller of `foo_bar` sees one method and never names the `Foo + Bar` requirement.

## Related constructs

These constructs are the ones `#[blanket_trait]` is most often compared with:

- [`#[cgp_fn]`](cgp_fn.md): also a single-implementation blanket impl with no wiring, but built from
  a function with `#[implicit]` field arguments; `#[blanket_trait]` fits better when the
  dependencies are traits rather than fields.
- [`#[cgp_component]`](cgp_component.md): the multiple-implementation alternative, selected per
  context through [`delegate_components!`](delegate_components.md), and the natural promotion when
  one implementation is no longer enough.
- [`#[cgp_auto_getter]`](cgp_auto_getter.md) and [`HasField`](../traits/has_field.md): use the same
  impl-side dependency mechanism for value injection.

## Known issues

Three trait-item shapes are rejected rather than lowered, each with a message naming what is
missing. A method with no default body fails with `function item require implementation block`, and
a constant with no default expression fails with `const item require implementation expression`,
because the default is what the macro copies into the impl. This inverts an ordinary trait, where a
declaration without a body is the normal case. Any other kind of item, such as a macro invocation in
the trait body, fails with `unsupported trait item`, because the macro handles only methods,
constants, and associated types.

The generated impl covers every type satisfying its bounds, which limits the pattern in the usual
way for blanket impls. A hand-written impl of the same trait for any type that could satisfy the
bounds conflicts with it (`E0119`), so the trait cannot be specialized for one type. This is the
restriction the pattern works within rather than a defect. Needing to escape it is the signal to
promote the trait to a [`#[cgp_component]`](cgp_component.md).

## Source

- Entry point: `blanket_trait` in
  [crates/macros/cgp-macro-lib/src/blanket_trait.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/blanket_trait.rs),
  which parses the optional context identifier (defaulting to `__Context__` when the attribute
  argument is empty) and the trait, then runs `item.to_items()?`.
- Logic:
  [crates/macros/cgp-macro-core/src/types/blanket_trait.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/blanket_trait.rs):
  `to_item_impl` walks the trait items, copies each default method or constant and each
  associated-type assignment into the impl, lifts associated types into impl generics, moves
  associated-type bounds into the `where` clause, and appends the trait's supertraits as the
  `__Context__: ...` predicate.
- `Self`-to-parameter rewriting for associated types: `RemoveSelfPathVisitor` in
  [crates/macros/cgp-macro-core/src/visitors/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/visitors/).
- Internal walkthrough (the codegen walk, the corner-case handling, and the index of tests and
  expansion snapshots):
  [implementation/entrypoints/blanket_trait.md](../../implementation/entrypoints/blanket_trait.md).
