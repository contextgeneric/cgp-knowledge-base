# `#[cgp_auto_getter]`

`#[cgp_auto_getter]` turns a getter trait into a single blanket implementation that satisfies each getter method by reading a context field through [`HasField`](../traits/has_field.md), keyed by the method's own name as a [`Symbol!`](symbol.md).

## Purpose

`#[cgp_auto_getter]` publishes a context field as a named getter trait that other code can depend on. Reading a field is the most basic form of dependency injection in CGP, and the underlying bound, `HasField<Symbol!("name"), Value = String>`, is precise but verbose. The macro lets the author declare the accessor as an ordinary trait method, `fn name(&self) -> &str;`, and generates the `HasField` plumbing behind it.

Prefer an [`#[implicit]`](../attributes/implicit.md) argument, and declare a getter trait only when an implicit argument cannot do the job. An implicit argument reads a field of the provider's own context with the same `HasField` bound and the same access rules a getter uses, but needs no separate trait. It covers the common case directly, including a field that several providers read. A getter trait is worth declaring in three cases an implicit argument cannot reach:

- **A field on another type.** A getter such as `HasBasicAuthHeader` reads from a request or payload type and is required as a bound on that type (`Request: HasBasicAuthHeader<Self>`), so there is no field of `self` for an implicit argument to read.
- **A named accessor.** Other code depends on the trait by name, through [`#[uses]`](../attributes/uses.md) or a supertrait.
- **An abstract field type.** The getter declares an associated type inferred from the field, so callers can name the type without knowing it.

`#[cgp_auto_getter]` produces exactly one implementation and no CGP wiring. It emits no provider trait, component name, or delegation table, only a blanket impl over a generic context, so any context that derives `HasField` with a field of the method's name satisfies the trait. The price is that the field must have exactly that name. When the field name must differ from the method name, or the getter must be chosen per context through wiring, [`#[cgp_getter]`](cgp_getter.md) builds the same getter as a full component. That is the advanced tool; among getter traits, `#[cgp_auto_getter]` is the default.

## Syntax

The macro is a bare attribute on a trait definition. It takes no argument, and any argument fails with `#[cgp_auto_getter] does not accept any attribute argument`. The trait body consists of getter methods, each taking `&self` or `&mut self` and returning the field in one of the forms listed below:

```rust
#[cgp_auto_getter]
pub trait HasName {
    fn name(&self) -> &str;
}
```

A getter trait may declare several methods, and each method name is the tag of its own field. The following trait reads two fields:

```rust
#[cgp_auto_getter]
pub trait HasDimensions {
    fn width(&self) -> &f64;
    fn height(&self) -> &f64;
}
```

### Return-type forms

The return type decides which field type the getter requires and how the value is converted. The recognized forms are these:

| Return type | Field type | Conversion |
|---|---|---|
| `&T` | `T` | none |
| `&str` | `String` | `.as_str()` |
| `Option<&T>` | `Option<T>` | `.as_ref()` |
| `Option<&str>` | `Option<String>` | `.as_deref()` |
| `&[T]` | any `'static` value implementing `AsRef<[T]>` | `.as_ref()` |
| [`MRef<'_, T>`](../types/mref.md) | `T` | wrapped as `MRef::Ref(…)` |
| an owned type (a path, tuple, or array) | the same type | `.clone()` |

A `&mut self` getter reads the field through `get_field_mut`, so its bound is on [`HasFieldMut`](../traits/has_field.md) rather than `HasField`, and each reference form has a mutable mirror: `&mut T`, `&mut str` (a `String` field, via `.as_mut_str()`), `&mut [T]` (a field implementing `AsMut<[T]>`, via `.as_mut()`), `Option<&mut T>` (via `.as_mut()`), and `Option<&mut str>` (via `.as_deref_mut()`).

### Mutability follows the receiver

A getter takes its access mode from the receiver, not from its return type. A `&mut self` getter reads through `get_field_mut` and applies the mutable conversion, and a `&self` getter reads through `get_field`. An [`#[implicit]`](../attributes/implicit.md) argument differs here, taking its mode from the argument's own type, although it shares every other access rule. The difference is easy to miss for that reason.

The return type still constrains the receiver in one direction. A `&mut` anywhere in it, whether `&mut T` or the inner reference of `Option<&mut T>`, is rejected under a `&self` receiver with `&mut self is required for mutable field reference`. The reverse pairing, a shared return under `&mut self`, is accepted and reads mutably. It compiles where the mutable result coerces to the shared return type, which fails for the `Option` forms, as Known issues records.

### Other method shapes

The first argument may be a typed reference to another type instead of `self`. That lets a getter read a field of a type the context names rather than of the context itself:

```rust
#[cgp_auto_getter]
pub trait HasFooBar: HasFooType + HasBarType {
    fn foo_bar(foo: &Self::Foo) -> &Self::Bar;
}
```

The blanket impl then bounds `Self::Foo` rather than the context, as `__Context__::Foo: HasField<Symbol!("foo_bar"), Value = __Context__::Bar>`, and the method is called as an associated function, `App::foo_bar(&foo)`. `Self` inside the argument and return types is rewritten to the context parameter, and whether the argument is `&` or `&mut` decides the access mode as a receiver would. An implicit argument cannot express this shape, since there is no field of `self` to read.

A getter may also take a second argument, which must be a `PhantomData<T>`:

```rust
#[cgp_auto_getter]
pub trait HasFoo {
    fn foo(&self, _tag: PhantomData<Foo>) -> &Foo;
}
```

The argument is forwarded to the generated method unchanged and plays no part in the field lookup; it lets a getter carry a type-level argument in its signature. Any other type in that position fails with `only PhantomData is allowed as second argument`, and a third argument fails with ``getter method must contain exactly one `&self` argument``.

A getter trait may declare one associated type and use it as the return type, which lets the field's type be inferred, as Expansion shows. Such a trait must contain exactly one getter method, and that method must read the associated type itself, most often as `&Self::Name`. A second associated type, a generic associated type, a second method, or a return type that reads some other field type is rejected.

### Rejected methods

A getter method is a plain signature, and the macro rejects anything more with a message naming the problem. A `const`, `async`, or `unsafe` method, a method with generic parameters or a `where` clause, a method without a return type, and a by-value `self` receiver are all rejected, as is any trait item other than a method or the one associated type.

## Expansion

`#[cgp_auto_getter]` re-emits the trait unchanged and adds one blanket impl over the reserved context parameter `__Context__`. Given:

```rust
#[cgp_auto_getter]
pub trait HasName {
    fn name(&self) -> &str;
}
```

the macro emits the trait followed by this impl. The field tag is the method name as a `Symbol!`, and because the return type is `&str`, the `Value` is `String` and the body appends `.as_str()`:

```rust
impl<__Context__> HasName for __Context__
where
    __Context__: HasField<Symbol!("name"), Value = String>,
{
    fn name(&self) -> &str {
        self.get_field(PhantomData::<Symbol!("name")>).as_str()
    }
}
```

A trait with several methods gets one `where` predicate and one method body per field, all in the same impl. The `&f64` returns below are plain references, so each `Value` matches the return type and nothing is appended:

```rust
impl<__Context__> HasDimensions for __Context__
where
    __Context__: HasField<Symbol!("width"), Value = f64>,
    __Context__: HasField<Symbol!("height"), Value = f64>,
{
    fn width(&self) -> &f64 {
        self.get_field(PhantomData::<Symbol!("width")>)
    }

    fn height(&self) -> &f64 {
        self.get_field(PhantomData::<Symbol!("height")>)
    }
}
```

The trait's supertraits, including those added by [`#[extend]`](../attributes/extend.md) or [`#[use_type]`](../attributes/use_type.md), become a `__Context__: …` predicate placed before the field bounds.

An associated type used as the return type becomes an extra generic parameter on the impl, bound through the `HasField` `Value`, which is what lets the field's type be inferred. Given:

```rust
#[cgp_auto_getter]
pub trait HasName {
    type Name: Display;

    fn name(&self) -> &Self::Name;
}
```

the impl declares `Name` as a parameter, moves the associated type's bounds into the `where` clause, and sets the associated type to that parameter:

```rust
impl<__Context__, Name> HasName for __Context__
where
    Name: Display,
    __Context__: HasField<Symbol!("name"), Value = Name>,
{
    type Name = Name;

    fn name(&self) -> &Self::Name {
        self.get_field(PhantomData::<Symbol!("name")>)
    }
}
```

These desugarings match what the macro emits, except that `Symbol!("name")` is shown in its sugared form rather than as the expanded `Symbol<4, Chars<'n', ...>>`.

## Examples

A getter trait paired with a context that derives `HasField` needs no further wiring:

```rust
use cgp::prelude::*;

#[cgp_auto_getter]
pub trait HasName {
    fn name(&self) -> &str;
}

#[derive(HasField)]
pub struct Person {
    pub name: String,
}

fn greet(person: &Person) {
    println!("Hello, {}!", person.name()); // HasName, via the blanket impl
}
```

`Person` derives `HasField<Symbol!("name"), Value = String>`, which is exactly the bound the blanket impl requires, so `Person` implements `HasName` and `person.name()` returns the `name` field as a `&str`.

A getter trait can also be implemented by hand, which suits a context that does not derive `HasField` or stores the value under another name:

```rust
pub struct Person {
    pub full_name: String,
}

impl HasName for Person {
    fn name(&self) -> &str {
        &self.full_name
    }
}
```

The hand-written impl shows that an auto-getter trait is an ordinary Rust trait; the macro only saves writing its body.

## Related constructs

These constructs are the ones `#[cgp_auto_getter]` relates to:

- [`#[cgp_getter]`](cgp_getter.md) — the same getter as a full component, wired to a [`UseField`](../providers/use_field.md) provider so the field name can differ from the method name and the getter can vary per context.
- [`#[implicit]`](../attributes/implicit.md) — the preferred way to read a field of the provider's own context, with the same access rules.
- [`#[derive(HasField)]`](../derives/derive_has_field.md) — generates the per-field `HasField` impls, keyed by [`Symbol!`](symbol.md), that the blanket impl reads.
- [`#[cgp_type]`](cgp_type.md) — the dedicated abstract-type component, which the associated-type form overlaps with when the type exists only as the getter's return type.

## Known issues

A `&mut self` getter that returns a shared `Option<&T>` or `Option<&str>` does not compile. The body picks its conversion from the receiver, so it emits `.as_mut()` or `.as_deref_mut()` and produces an `Option<&mut T>`, which does not coerce to the declared `Option<&T>`. The error is `E0308` ("types differ in mutability") on the `#[cgp_auto_getter]` attribute. The reference, `&str`, slice, and `MRef` forms are unaffected, because a `&mut` result coerces to the shared one. The correct behavior would be to choose the conversion from the return type's mutability while keeping `get_field_mut` for the read. Until then, return `Option<&mut T>` from a `&mut self` getter, or take `&self`.

`#[prefix(...)]` and `#[derive_delegate(...)]` are accepted on a `#[cgp_auto_getter]` trait and dropped without an error. The macro runs the same attribute collector as [`#[cgp_component]`](cgp_component.md) so that [`#[extend]`](../attributes/extend.md) and [`#[use_type]`](../attributes/use_type.md) apply, but it generates no component, so the two attributes that need one register nothing and report nothing. A getter that must live in a namespace or dispatch per type is a [`#[cgp_getter]`](cgp_getter.md) component.

## Source

- Entry point: `cgp_auto_getter` in [crates/macros/cgp-macro-lib/src/cgp_auto_getter.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_auto_getter.rs), which rejects any attribute argument and runs `ItemCgpAutoGetter::preprocess(...).to_items()`.
- Logic: [crates/macros/cgp-macro-core/src/types/cgp_auto_getter/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_auto_getter/) — `item.rs` sets the `__Context__` context identifier and drives field parsing, and `blanket.rs` builds the single blanket impl.
- Getter parsing (including the return-type forms and the associated-type rules), shared with `#[cgp_getter]`: [crates/macros/cgp-macro-core/src/functions/getter/parse.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/getter/parse.rs), [crates/macros/cgp-macro-core/src/functions/field/parse.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/field/parse.rs), and [crates/macros/cgp-macro-core/src/types/getter/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/getter/).
- Internal walkthrough (the pipeline stages, the function that synthesizes each generated item, the corner-case handling, and the index of tests and expansion snapshots): [implementation/entrypoints/cgp_auto_getter.md](../../implementation/entrypoints/cgp_auto_getter.md).
