# `MRef`

`MRef<'a, T>` is a "maybe reference": an enum holding either a borrow of a `T` or an owned `T`, so a
getter can return whichever it has without committing every implementor to one or the other.

## Purpose

`MRef` lets one getter signature serve both a context that stores a value and a context that must
produce one. A getter returning `&'a T` forces every context to keep a `T` it can lend; a getter
returning `T` forces every context to hand over ownership, cloning even when a reference would do.
`MRef<'a, T>` can be either at runtime: a context with the value in a field returns `MRef::Ref` and
lends it, while a context that computes the value returns `MRef::Owned` and gives it away. The
caller treats both the same way, because `MRef` dereferences to `T`.

The type is used in CGP's getter machinery, where a getter's return type decides the body the macro
generates. A getter declared to return `MRef<'a, T>` reads its field and wraps the borrow as
`MRef::Ref(...)`, so reading a stored field costs nothing extra, while the same signature still lets
a hand-written provider return an owned value. So one getter can abstract over whether the value is
stored or made, without splitting into two traits.

## Definition

`MRef` is a two-variant enum over a lifetime and an element type:

```rust
pub enum MRef<'a, T> {
    Ref(&'a T),
    Owned(T),
}
```

`Ref` borrows a `T` for `'a`, and `Owned` carries a `T` by value. The lifetime constrains only the
borrowed case, so an `MRef` built from an owned value is effectively unconstrained in `'a`. Nothing
about the enum is type-level; it is the ordinary value a getter passes back to its caller.

## Behavior

`MRef` behaves like a smart pointer to `T`, which is what makes its two variants interchangeable at
the call site. The surface has three parts:

- **`Deref<Target = T>` and `AsRef<T>`** return a `&T` from either variant, so `&*value`,
  auto-dereferencing method calls, and `as_ref()` all work whichever case is inside.
- **Two `From` impls** make construction easy: `From<T>` builds `Owned` and `From<&'a T>` builds
  `Ref`, so a value or a reference converts with `.into()`.
- **`get_or_clone`**, available when `T: Clone`, resolves the enum to a plain `T`, moving the owned
  value or cloning the borrowed one.

A borrowed `MRef` is therefore read cheaply and promoted to ownership only when asked. Those are the
whole surface: `MRef` is neither `Clone` nor `Debug`. It is in the prelude.

The getter macros and [`#[implicit]`](../attributes/implicit.md) recognize `MRef` by shape, a
single-segment path named `MRef` with a lifetime and a type argument, and read a field of type `T`
into `MRef::Ref(…)`. An implicit argument declared that way therefore always lends. A differently
shaped or qualified `MRef` falls through to the owned form, which expects a field of that very type,
so `fn greeting(&self) -> cgp::prelude::MRef<'_, String>;` under `#[cgp_auto_getter]` places `'_` in
a `HasField` bound and fails with ``error[E0637]: `'_` cannot be used here``.

### Choosing it, and what goes wrong

`MRef` is the getter return type for a value some contexts store and others build: a context wired
to [`UseField`](../providers/use_field.md) lends its field as `MRef::Ref`, and a hand-written
provider returns `MRef::Owned`. A plain `&T` is the better return type when every context stores the
value, and an `#[implicit]` argument remains the default way for a provider to read a stored field.
The type is not related to [`Life`](life.md), whose lifetime is a type-level lift rather than a
borrow. `get_or_clone` clones only the borrowed case, so it is free on an owned value. And because
`Deref` makes the variants transparent, a manual match on `Ref` versus `Owned` usually means the code
wanted `get_or_clone`.

## Examples

A getter returning `MRef` lets one context lend a stored field and another build the value:

```rust
use cgp::prelude::*;

#[cgp_getter]
pub trait HasGreeting {
    fn greeting(&self) -> MRef<'_, String>;
}

#[cgp_impl(new BuildGreeting)]
impl GreetingGetter {
    fn greeting(&self, #[implicit] name: &str) -> MRef<'_, String> {
        MRef::Owned(format!("Hello, {name}!"))
    }
}

#[derive(HasField)]
pub struct Stored {
    pub greeting: String,
}

#[derive(HasField)]
pub struct Computed {
    pub name: String,
}

delegate_components! {
    Stored {
        GreetingGetterComponent: UseField<Symbol!("greeting")>,
    }
}

delegate_components! {
    Computed {
        GreetingGetterComponent: BuildGreeting,
    }
}

// Generic code reads either case through `Deref`.
pub fn shout<Context: HasGreeting>(context: &Context) -> String {
    context.greeting().to_uppercase()
}
```

Both variants share one type and are consumed the same way; only construction differs:

```rust
use cgp::prelude::*;

let stored = String::from("hello");

// a context lending a stored value:
let borrowed: MRef<'_, String> = MRef::from(&stored);
assert_eq!(&*borrowed, "hello");

// a provider returning a freshly built value through the same type:
let made: MRef<'_, String> = MRef::from(String::from("world"));
assert_eq!(made.as_ref(), "world");

// promote either to an owned value when ownership is required:
let owned: String = borrowed.get_or_clone();
assert_eq!(owned, "hello");
```

`get_or_clone` clones in the borrowed case and moves in the owned case.

## Related constructs

These constructs are the ones `MRef` relates to:

- [`#[cgp_auto_getter]`](../macros/cgp_auto_getter.md) and
  [`#[cgp_getter]`](../macros/cgp_getter.md): recognize an `MRef<'_, T>` return type and read a `T`
  field, alongside the `&T`, `Option<&T>`, and `&str` forms.
- [`#[implicit]`](../attributes/implicit.md): accepts the same `MRef` form for an argument.
- [`HasField`](../traits/has_field.md) and [`UseField`](../providers/use_field.md): the field access
  and the provider those getters build on.
- [`Life`](life.md): an unrelated type-level lifetime lift; `MRef`'s lifetime is an ordinary borrow
  lifetime.

## Source

- The type is defined in
  [crates/core/cgp-field/src/types/mref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/types/mref.rs),
  with its `Deref`, `AsRef`, the two `From` impls, and `get_or_clone`.
- The macro logic that recognizes an `MRef<'a, T>` return type is in
  [crates/macros/cgp-macro-core/src/functions/field/parse.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/field/parse.rs)
  (the `MRef` field mode), and the `MRef::Ref(...)` body is emitted by the shared conversion in
  [crates/macros/cgp-macro-core/src/types/getter/field_mode.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/getter/field_mode.rs).
