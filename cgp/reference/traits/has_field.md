# `HasField`

`HasField<Tag>` is the trait for reading one named field out of a context by a type-level tag. `HasFieldMut<Tag>` adds mutable access, `FieldGetter` and `MutFieldGetter` are the provider-side mirrors used in wiring, and `MapField` and `FieldMapper` let chained accesses borrow correctly.

## Purpose

`HasField` lets a provider demand a value from its context without naming the context's type. A provider is generic over the context but still needs a `name`, a `port`, or another field, and it cannot reach into a struct it does not know. `HasField<Tag>` keys each field with a tag type standing for the field's name, so a provider writes `Context: HasField<Symbol!("name"), Value = String>` in its `where` clause and receives the field through the trait system. Field access becomes an impl-side dependency rather than part of a public interface: any context with a matching field satisfies the bound. See [impl-side dependencies](../../concepts/impl-side-dependencies.md) for why this constraint-based style is the heart of CGP.

The trait is small because the value-injection macros stand on it. [`#[derive(HasField)]`](../derives/derive_has_field.md) generates the impls from a struct's fields, and `#[cgp_auto_getter]`, `#[cgp_getter]` through [`UseField`](../providers/use_field.md), and `#[implicit]` arguments all desugar into `HasField` bounds and `get_field` calls.

## Definition

`HasField<Tag>` carries the field's type as an associated `Value` and returns a reference to it, taking a `PhantomData<Tag>` argument that exists only to disambiguate which field is meant when several `HasField` impls are in scope:

```rust
pub trait HasField<Tag> {
    type Value;

    fn get_field(&self, _tag: PhantomData<Tag>) -> &Self::Value;
}
```

The `Tag` parameter is a type-level name. A named struct field is keyed by [`Symbol!("field_name")`](../macros/symbol.md), the type-level string of its identifier; a tuple field is keyed by [`Index<N>`](../types/index.md), the type-level natural number of its position. Because the tag is a type and not a value, `get_field` receives `PhantomData<Tag>` purely to tell the compiler which impl to select.

`HasFieldMut<Tag>` is the mutable extension. It supertraits `HasField<Tag>` and adds a method returning `&mut Self::Value`:

```rust
pub trait HasFieldMut<Tag>: HasField<Tag> {
    fn get_field_mut(&mut self, tag: PhantomData<Tag>) -> &mut Self::Value;
}
```

Neither trait carries a `#[diagnostic::on_unimplemented]` note; a missing field is reported as an unsatisfied `HasField<Symbol<…>>` bound, whose tag spells the field name, and [cargo-cgp](../cargo-cgp.md) turns it into a "missing field" message. `HasField`, `HasFieldMut`, `FieldGetter`, and `MutFieldGetter` are in the prelude; `MapField` and `FieldMapper` are imported from `cgp::core::field::traits`.

Field access has a provider-side mirror, so it can be wired like a component rather than only implemented on the context. `FieldGetter<Context, Tag>` corresponds to `HasField`, taking the context as an explicit argument instead of `&self`:

```rust
pub trait FieldGetter<Context, Tag> {
    type Value;

    fn get_field(context: &Context, _tag: PhantomData<Tag>) -> &Self::Value;
}

pub trait MutFieldGetter<Context, Tag>: FieldGetter<Context, Tag> {
    fn get_field_mut(context: &mut Context, tag: PhantomData<Tag>) -> &mut Self::Value;
}
```

`MapField` and `FieldMapper` add a variant that borrows through a closure. They organize lifetime inference: chaining `context.get_field().get_field()` would otherwise force `Self::Value` to be `'static`, so `map_field` applies a `for<'a> FnOnce(&'a Self::Value) -> &'a T` closure to the borrowed field:

```rust
pub trait MapField<Tag>: HasField<Tag> {
    fn map_field<T>(
        &self,
        _tag: PhantomData<Tag>,
        mapper: impl for<'a> FnOnce(&'a Self::Value) -> &'a T,
    ) -> &T;
}

pub trait FieldMapper<Context, Tag>: FieldGetter<Context, Tag> {
    fn map_field<T>(
        context: &Context,
        _tag: PhantomData<Tag>,
        mapper: impl for<'a> FnOnce(&'a Self::Value) -> &'a T,
    ) -> &T;
}
```

## Behavior

The consumer impls of `HasField` come almost entirely from `#[derive(HasField)]`. The trait files add blanket impls that make access compose:

- **A `Deref` forwarding impl.** A type that dereferences to a target with the field inherits it, so a `HasField` bound passes through smart pointers and newtypes. A private `DerefMap` helper keeps the target free of a `'static` bound.
- **A `DerefMut` forwarding impl** for `HasFieldMut`, which does require the target to be `'static`.

Both carry `#[diagnostic::do_not_recommend]`, so the compiler does not suggest the blanket path in errors.

The provider side connects field access to wiring. `UseContext` implements `FieldGetter<Context, Tag>` for any context that has the field under the same tag:

```rust
impl<Context, Tag, Field> FieldGetter<Context, Tag> for UseContext
where
    Context: HasField<Tag, Value = Field>,
{
    type Value = Field;
    fn get_field(context: &Context, _tag: PhantomData<Tag>) -> &Self::Value {
        context.get_field(PhantomData)
    }
}
```

The tag `UseContext` reads is the tag it is asked under. Through [`WithContext`](../providers/with_provider.md), a getter component asks under its own marker, so the context must implement `HasField<NameGetterComponent>` for `WithContext` to apply.

`FieldMapper` has a blanket impl for every `FieldGetter` whose getter and tag are `'static`, and `MapField` one for every `HasField` whose tag is `'static`. The two sides follow CGP's consumer and provider split: generic code bounds on `HasField` and `HasFieldMut`, while `FieldGetter` and `MutFieldGetter` are what gets wired, with [`UseField`](../providers/use_field.md) as the usual implementation.

## Examples

A provider that needs a value from its context expresses the need as a `HasField` bound and reads the field with `get_field`:

```rust
use cgp::prelude::*;

#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}

#[cgp_impl(new GreetHello)]
impl Greeter
where
    Self: HasField<Symbol!("name"), Value = String>,
{
    fn greet(&self) {
        println!("Hello, {}!", self.get_field(PhantomData));
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
```

`Person` derives `HasField`, so it implements `HasField<Symbol!("name"), Value = String>`, the bound `GreetHello` requires, and `person.greet()` prints the name. The explicit bound is rarely hand-written; `#[cgp_auto_getter]`, `#[cgp_getter]`, and `#[implicit]` arguments generate it.

## Related constructs

`HasField` is generated by [`#[derive(HasField)]`](../derives/derive_has_field.md), which emits one `HasField` and one `HasFieldMut` impl per struct field. Its tags come from [`Symbol!`](../macros/symbol.md) for named fields and [`Index<N>`](../types/index.md) for tuple fields. The provider-side [`UseField`](../providers/use_field.md) provider is the wiring-side implementation of `FieldGetter` that `#[cgp_getter]` targets, and field access in general is the canonical example of [impl-side dependencies](../../concepts/impl-side-dependencies.md). For the whole-struct structural view rather than single-field access, see [`HasFields`](has_fields.md).

## Known issues

A type that implements `Deref` cannot also have a derived or hand-written `HasField` impl for a tag its `Deref` target implements. The `Deref` forwarding impl already covers that tag, so the two impls overlap and fail with `E0119`. Tags the target lacks are unaffected. See [`#[derive(HasField)]`](../derives/derive_has_field.md#known-issues).

## Source

- The consumer traits and their blanket impls are in [crates/core/cgp-field/src/traits/has_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field.rs) (`HasField`, `FieldGetter`, the `Deref` forwarding impl, and the `UseContext` provider impl) and [crates/core/cgp-field/src/traits/has_field_mut.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field_mut.rs) (`HasFieldMut`, `MutFieldGetter`, the `DerefMut` forwarding impl).
- The `MapField`/`FieldMapper` lifetime helpers are in [crates/core/cgp-field/src/traits/map_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/map_field.rs).
- The `UseField` provider lives in [crates/core/cgp-field/src/impls/use_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/use_field.rs).
- For how it is generated and the index of tests, see the implementation document [implementation/entrypoints/derive_has_field.md](../../implementation/entrypoints/derive_has_field.md).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **6 pages** rather than one: [`has_field`](https://contextgeneric.dev/docs/reference/traits/field-access/has_field), [`has_field_mut`](https://contextgeneric.dev/docs/reference/traits/field-access/has_field_mut), [`field_getter`](https://contextgeneric.dev/docs/reference/traits/field-access/field_getter), [`mut_field_getter`](https://contextgeneric.dev/docs/reference/traits/field-access/mut_field_getter), [`map_field`](https://contextgeneric.dev/docs/reference/traits/field-access/map_field), [`field_mapper`](https://contextgeneric.dev/docs/reference/traits/field-access/field_mapper). A change here is propagated to each of them, per the [synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping and the granularity rule behind it are recorded in [website/site-structure.md](../../../website/site-structure.md).
