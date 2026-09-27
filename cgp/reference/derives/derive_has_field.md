# `#[derive(HasField)]`

`#[derive(HasField)]` gives a struct field-level getters: for every field it generates a
`HasField<Tag>` and a `HasFieldMut<Tag>` implementation keyed by a type-level name, so providers can
read fields out of a context by name without the field appearing in any trait interface.

## Purpose

`#[derive(HasField)]` turns a struct's fields into type-level entries that CGP's dependency
injection can look up. A provider often needs a value from its context, such as a `name`, a `width`,
or a configuration handle, but it is generic over the context and cannot name the concrete struct.
`HasField` solves this by keying each field with a tag type that stands for its name, so a provider
can require `Context: HasField<Symbol!("name"), Value = String>` and receive the field without
knowing what the context is.

This makes field access an impl-side dependency rather than part of a public interface. A provider
states "I need a `String` field called `name`" in its `where` clause alone, and any context that
derives `HasField` and has such a field satisfies it. The derive is the bridge between an ordinary
struct and that bound; without it, the struct's fields are invisible to the trait system.

The trait being implemented is small. It carries the field's type as `Value` and returns a reference
to the field, with a `PhantomData<Tag>` argument that tells the compiler which field is meant when
several `HasField` impls apply:

```rust
pub trait HasField<Tag> {
    type Value;

    fn get_field(&self, _tag: PhantomData<Tag>) -> &Self::Value;
}
```

Higher-level constructs are built on these impls. [`#[implicit]`](../attributes/implicit.md)
arguments turn function parameters into `get_field` calls, and
[`#[cgp_auto_getter]`](../macros/cgp_auto_getter.md) and [`#[cgp_getter]`](../macros/cgp_getter.md),
through [`UseField`](../providers/use_field.md), generate impls whose `where` clauses are `HasField`
bounds. All of them assume the context derives `HasField`.

## Syntax

The derive is applied to a struct and takes no arguments:

```rust
#[derive(HasField)]
pub struct Person {
    pub name: String,
    pub age: u8,
}
```

It accepts structs with named fields and tuple structs, which differ only in how each field's tag is
computed. A named field is keyed by [`Symbol!("field_name")`](../macros/symbol.md), the type-level
string of its identifier, and a tuple field by [`Index<N>`](../types/index.md), its position. A unit
struct produces no impls, since it has no fields, and an enum is rejected with
``expected `struct` ``.

A raw-identifier field is keyed by its logical name: a field written `r#type` is keyed by
`Symbol!("type")`, while the generated accessor still borrows `&self.r#type`.

The derive gives only the field-level view. The whole-struct view as a single type-level list comes
from [`#[derive(HasFields)]`](derive_has_fields.md), and the two are often derived together.

## Expansion

`#[derive(HasField)]` emits one `HasField` impl and one `HasFieldMut` impl per field and leaves the
struct untouched. Given the named-field struct above, it generates a pair of impls per field, with
the identifier as a `Symbol!` tag and the field's type as `Value`:

```rust
impl HasField<Symbol!("name")> for Person {
    type Value = String;

    fn get_field(&self, key: PhantomData<Symbol!("name")>) -> &Self::Value {
        &self.name
    }
}

impl HasFieldMut<Symbol!("name")> for Person {
    fn get_field_mut(&mut self, key: PhantomData<Symbol!("name")>) -> &mut Self::Value {
        &mut self.name
    }
}

impl HasField<Symbol!("age")> for Person {
    type Value = u8;

    fn get_field(&self, key: PhantomData<Symbol!("age")>) -> &Self::Value {
        &self.age
    }
}

impl HasFieldMut<Symbol!("age")> for Person {
    fn get_field_mut(&mut self, key: PhantomData<Symbol!("age")>) -> &mut Self::Value {
        &mut self.age
    }
}
```

[`HasFieldMut<Tag>`](../traits/has_field.md) has `HasField<Tag>` as its supertrait and adds
`get_field_mut`, returning `&mut Self::Value`. Most CGP code reads through `HasField`, but the
mutable impl is always generated beside it, which is what mutable
[`#[implicit]`](../attributes/implicit.md) arguments and `&mut self` getters rely on.

A tuple struct expands the same way, with each tag its position. Given:

```rust
#[derive(HasField)]
pub struct Rectangle(pub f64, pub f64);
```

the derive generates:

```rust
impl HasField<Index<0>> for Rectangle {
    type Value = f64;

    fn get_field(&self, key: PhantomData<Index<0>>) -> &Self::Value {
        &self.0
    }
}

impl HasFieldMut<Index<0>> for Rectangle {
    fn get_field_mut(&mut self, key: PhantomData<Index<0>>) -> &mut Self::Value {
        &mut self.0
    }
}

impl HasField<Index<1>> for Rectangle {
    type Value = f64;

    fn get_field(&self, key: PhantomData<Index<1>>) -> &Self::Value {
        &self.1
    }
}

impl HasFieldMut<Index<1>> for Rectangle {
    fn get_field_mut(&mut self, key: PhantomData<Index<1>>) -> &mut Self::Value {
        &mut self.1
    }
}
```

A generic struct's parameters and `where` clause are carried onto every impl, so
`struct Wrapper<T> { pub value: T }` yields `impl<T> HasField<Symbol!("value")> for Wrapper<T>` with
`Value = T`. Each impl is re-spanned onto its field, so a conflict with a hand-written `HasField`
impl for the same tag is reported at that field rather than at the whole derive.

Field access also passes through smart pointers without a derive. `HasField` and `HasFieldMut` have
blanket impls for any type whose `Deref` or `DerefMut` target implements them, so a `Box<Person>`,
or a newtype that dereferences to `Person`, answers `get_field` from the inner struct. These blanket
impls carry `#[diagnostic::do_not_recommend]`, so a missing-field error points at the underlying
struct rather than suggesting them. The mutable one requires the target to be `'static`.

## Examples

A provider that needs a value from its context declares it, and the derive is what lets a concrete
context supply it. Here the need is written as an [`#[implicit]`](../attributes/implicit.md)
argument, which generates the `HasField<Symbol!("name"), Value = String>` bound:

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
    pub name: String,
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

`Person` derives `HasField`, so it implements `HasField<Symbol!("name"), Value = String>`, exactly
the bound `GreetHello` requires. The wiring checks, and `person.greet()` prints the person's name.
The same bound can be written by hand as `where Self: HasField<Symbol!("name"), Value = String>`
with a `self.get_field(PhantomData)` call, which is what the implicit argument expands to.

## Related constructs

These constructs are the ones `#[derive(HasField)]` supports:

- [`HasField` and `HasFieldMut`](../traits/has_field.md): the traits it implements.
- [`#[implicit]`](../attributes/implicit.md): the default way providers read the fields it exposes.
- [`#[cgp_auto_getter]`](../macros/cgp_auto_getter.md) and
  [`#[cgp_getter]`](../macros/cgp_getter.md), with [`UseField`](../providers/use_field.md): getter
  traits built on its impls.
- [`Symbol!`](../macros/symbol.md) and [`Index<N>`](../types/index.md): the tags for named and tuple
  fields.
- [`#[derive(HasFields)]`](derive_has_fields.md): the whole-struct view, commonly derived alongside,
  and part of [`#[derive(CgpData)]`](derive_cgp_data.md).

## Known issues

A struct that implements `Deref` cannot derive a `HasField` impl for a field name its `Deref` target
also exposes. The `Deref` blanket impl already implements `HasField<Tag>` for the struct wherever
the target does, so a derived impl for the same tag overlaps it and fails with `E0119` (conflicting
implementations of `HasField<Symbol<…>>` for the struct). Fields whose names the target lacks derive
without trouble. Rename the colliding field, drop the `Deref` impl, or write the needed accessors by
hand.

## Source

- Entry point: `derive_has_field` in
  [crates/macros/cgp-macro-lib/src/derive_has_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/derive_has_field.rs),
  registered as the `HasField` derive in
  [crates/macros/cgp-macro/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro/src/lib.rs).
  It parses the input as a `syn::ItemStruct`, wraps it in an `ItemCgpRecord`
  ([crates/macros/cgp-macro-core/src/types/cgp_data/record.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/record.rs)),
  and calls `to_has_field_impls`.
- Codegen: `derive_has_field_impls_from_struct` in
  [crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_data/derive_has_field.rs),
  which maps named fields to `Symbol` tags and tuple fields to `Index` tags and emits both impls per
  field.
- Traits and the `Deref` blanket impls:
  [crates/core/cgp-field/src/traits/has_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field.rs)
  and
  [crates/core/cgp-field/src/traits/has_field_mut.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field_mut.rs).
- Internal walkthrough (the codegen helper, the corner cases, and the index of tests and expansion
  snapshots):
  [implementation/entrypoints/derive_has_field.md](../../implementation/entrypoints/derive_has_field.md).
