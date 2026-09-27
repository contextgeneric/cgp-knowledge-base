# `#[implicit]`

`#[implicit]` marks a function argument as an implicit dependency: instead of being passed by the
caller, the value is read from a same-named field of the context, and the argument disappears from
the public signature.

## Purpose

`#[implicit]` makes field-based dependency injection look like an ordinary function parameter.
Without it, a provider that needs a `width` from its context declares a
`HasField<Symbol!("width"), Value = f64>` bound and calls `self.get_field(PhantomData)` in its body.
That works, but it makes the author learn `HasField`, type-level symbols, and `PhantomData` tags
before writing the simplest provider. `#[implicit]` hides all of it behind a normal-looking
parameter.

An argument `#[implicit] width: f64` reads as "this function needs a `width` of type `f64`", the
intuition a Rust programmer already has. The macro does the mechanical work: it removes the argument
from the signature, adds the matching `HasField` bound, and binds a local variable to the field's
value at the top of the body. The result looks like a function taking arguments and behaves like a
provider injecting dependencies from its context.

This makes `#[implicit]` the recommended starting point for basic CGP, and the default way to read
any field of a provider's own context. A newcomer writes providers in
[`#[cgp_fn]`](../macros/cgp_fn.md) and [`#[cgp_impl]`](../macros/cgp_impl.md) with only familiar
function syntax, and meets the `HasField` machinery later, when it is actually needed.

## Syntax

`#[implicit]` is a bare marker attribute on a typed function argument whose pattern is a plain
identifier. It takes no arguments, and a list or name-value spelling such as `#[implicit(foo)]` or
`#[implicit = "foo"]` is rejected with
`` `#[implicit]` does not take any arguments; write it as a bare `#[implicit]` ``:

```rust
fn area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
    width * height
}
```

The argument's name is also the field's name: `width` and `height` are both the locals the body uses
and the context fields the values come from, as `Symbol!("width")` and `Symbol!("height")`. A raw
identifier is read by its logical name, so `#[implicit] r#type: String` reads the field `type`. The
argument's type is the type the body sees, and it decides how the field is read, as the next section
describes.

`#[implicit]` is meaningful only where CGP rewrites a function body: in
[`#[cgp_fn]`](../macros/cgp_fn.md) and in the methods of a [`#[cgp_impl]`](../macros/cgp_impl.md)
block. It is not a standalone macro, so anywhere else, such as a method of a
[`#[cgp_component]`](../macros/cgp_component.md) trait, it is left in place and fails with
``cannot find attribute `implicit` in this scope``.

### Rules

Three rules constrain an implicit argument, each rejected with a spanned error:

- **The function must take `self` first**, because the field is read from `self`. Otherwise it fails
  with ``The first argument of a function with implicit arguments must be `self` ``.
- **The pattern must be a bare identifier**, not a destructuring pattern (`Expected an identifier`)
  or a `mut` binding. For a mutable local, clone the injected value in the body.
- **A mutable implicit argument must be alone.** An argument whose type contains a `&mut`, whether
  the outer reference of `&mut T` or the inner one of `Option<&mut T>`, is read through
  `get_field_mut`, which borrows the whole context exclusively. It therefore requires a `&mut self`
  receiver and must be the function's only implicit argument; otherwise the error says
  ``a `&mut` implicit argument must be the only implicit argument, …``.

Immutable implicit arguments have no such limit: they are shared borrows and combine freely, in any
number, on a `&self` or a `&mut self` receiver.

### Access forms

The argument's type decides the field type the bound requires and the conversion applied to the
read. The forms are shared with [`#[cgp_auto_getter]`](../macros/cgp_auto_getter.md):

| Argument type | Field type | Conversion |
|---|---|---|
| an owned type (a path, tuple, or array) | the same type | `.clone()` |
| `&T` | `T` | none |
| `&str` | `String` | `.as_str()` |
| `Option<&T>` | `Option<T>` | `.as_ref()` |
| `Option<&str>` | `Option<String>` | `.as_deref()` |
| `&[T]` | any `'static` value implementing `AsRef<[T]>` | `.as_ref()` |
| [`MRef<'_, T>`](../types/mref.md) | `T` | wrapped as `MRef::Ref(…)` |

Each reference form has a mutable mirror, read through [`HasFieldMut`](../traits/has_field.md) and
`get_field_mut`: `&mut T`, `&mut str` (a `String` field, via `.as_mut_str()`), `&mut [T]` (a field
implementing `AsMut<[T]>`, via `.as_mut()`), `Option<&mut T>` (via `.as_mut()`), and
`Option<&mut str>` (via `.as_deref_mut()`). Every mutable form needs a `&mut self` receiver and must
be alone, per the rules above.

The mutability of the read follows the argument's own type, not the receiver. An immutable argument,
including a `&[T]` slice, reads through `HasField` even on a `&mut self` receiver. This is the one
rule that differs from a getter trait, which takes its mode from the receiver instead.

`MRef` has no mutable mirror. It borrows the field as a shared value, so it reads through `HasField`
whatever the receiver. It suits a body that wants a value that may be owned or borrowed, without
committing the field to either. The form is recognized by shape, not by name resolution: a
single-segment path named `MRef` with exactly a lifetime and a type argument. A differently shaped
`MRef`, or one reached through a qualified path, falls through to the owned-and-cloned case.

## Expansion

`#[implicit]` rewrites each marked argument into a `HasField` bound plus a `let` binding and leaves
the rest of the function alone. Given a `#[cgp_fn]` definition:

```rust
#[cgp_fn]
fn rectangle_area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
    width * height
}
```

the macro produces a trait whose method takes no extra arguments, and an impl whose `where` clause
requires one `HasField` bound per implicit argument:

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

The `let` bindings are inserted at the top of the body in argument order, before the original
statements, so the names are in scope throughout. Each binding's type is the argument's declared
type, and its value is the read with the conversion from the table. For `#[implicit] name: &str`,
for example, the bound is `HasField<Symbol!("name"), Value = String>` and the binding is
`let name: &str = self.get_field(PhantomData::<Symbol!("name")>).as_str();`, so the field holds a
`String` while the body works with a `&str`.

Inside a [`#[cgp_impl]`](../macros/cgp_impl.md) block the rewrite is the same: the bounds are added
to the impl's `where` clause and the bindings are prepended to the method's body. Given:

```rust
#[cgp_impl(new RectangleAreaCalculator)]
impl AreaCalculator {
    fn area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
        width * height
    }
}
```

the impl gains
`__Context__: HasField<Symbol!("width"), Value = f64> + HasField<Symbol!("height"), Value = f64>`,
and `area` binds `width` and `height` at its top.

A `#[cgp_impl]` block with several methods gathers the bounds of every method and removes duplicates
before adding them, since all methods share one impl. Two methods that each take
`#[implicit] name: &str` contribute one `HasField<Symbol!("name"), Value = String>` bound. The
comparison covers the whole specification (name, argument type, field type, access form, and
mutability), so two methods reading the same field at different types each contribute a bound. A
`&str` in one method and a `String` in another therefore require two conflicting `Value` types
rather than merging silently. The `let` bindings are still emitted once per method.

## Examples

A `#[cgp_fn]` with implicit arguments needs only a context that derives
[`HasField`](../derives/derive_has_field.md) and has the named fields:

```rust
use cgp::prelude::*;

#[cgp_fn]
pub fn rectangle_area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
    width * height
}

#[derive(HasField)]
pub struct Rectangle {
    pub width: f64,
    pub height: f64,
}

fn print_area(rect: &Rectangle) {
    println!("area = {}", rect.rectangle_area());
}
```

`Rectangle` derives `HasField` for `width` and `height`, which satisfies both bounds, so the blanket
impl gives it `RectangleArea`. The call `rect.rectangle_area()` passes no arguments, because both
are read from `rect`.

A mutable implicit argument modifies a field in place, alone and under `&mut self`:

```rust
#[cgp_fn]
pub fn shout(&mut self, #[implicit] name: &mut str) {
    name.make_ascii_uppercase();
}
```

## Related constructs

These constructs are the ones `#[implicit]` works with:

- [`#[cgp_fn]`](../macros/cgp_fn.md) and [`#[cgp_impl]`](../macros/cgp_impl.md): the two hosts that
  consume the attribute.
- [`#[derive(HasField)]`](../derives/derive_has_field.md): supplies the field access the generated
  bounds require.
- [`#[cgp_auto_getter]`](../macros/cgp_auto_getter.md): shares the access forms, and is the choice
  only where an implicit argument cannot reach: a field on another type, an accessor other code
  depends on by name, or a getter with an associated type inferred from the field.
- [`#[uses]`](uses.md): brings in other traits alongside implicit arguments.

## Source

- Parsing:
  [crates/macros/cgp-macro-core/src/functions/implicits/parse.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/implicits/parse.rs)
  extracts `#[implicit]` arguments, enforces the `self`, identifier, `mut`, and mutable-exclusivity
  rules, and rejects a non-bare attribute.
- Per-argument model:
  [crates/macros/cgp-macro-core/src/types/implicits/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/implicits/):
  `arg_field.rs` builds the `HasField` bound and the `let` binding, and `arg_fields.rs` adds the
  bounds, prepends the bindings, and removes duplicate bounds across a `#[cgp_impl]` block's
  methods.
- Argument-type-to-access mapping:
  [crates/macros/cgp-macro-core/src/functions/field/parse.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/field/parse.rs),
  with the conversions in
  [crates/macros/cgp-macro-core/src/types/getter/field_mode.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/getter/field_mode.rs).
- Implementation document (how implicit arguments are parsed and lowered, and the index of tests):
  [implementation/entrypoints/cgp_fn.md](../../implementation/entrypoints/cgp_fn.md).
