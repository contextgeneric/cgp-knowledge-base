# `#[cgp_getter]`

`#[cgp_getter]` defines a getter as a full CGP component: the same getter trait [`#[cgp_auto_getter]`](cgp_auto_getter.md) accepts, built with [`#[cgp_component]`](cgp_component.md) and backed by a [`UseField`](../providers/use_field.md) provider, so the field name can differ from the method name and each context can choose how the getter is supplied.

## Purpose

`#[cgp_getter]` is for the advanced case where a getter must take part in wiring rather than resolve to one blanket impl. Most getters read a field of the same name, which an [`#[implicit]`](../attributes/implicit.md) argument or [`#[cgp_auto_getter]`](cgp_auto_getter.md) handles with no wiring. Reserve `#[cgp_getter]` for a context that needs control over the getter: storing the value under another field name, or supplying it differently from other contexts. The macro provides that control by making the getter a component, with a provider trait, a component name, and an entry in the context's wiring.

The trade-off against `#[cgp_auto_getter]` is one line of wiring for that decoupling. `#[cgp_auto_getter]` emits a blanket impl that applies to any context with a field of the method's name, so there is nothing to wire and nothing to choose. `#[cgp_getter]` emits a component that each context wires to a provider, usually `UseField<Symbol!("...")>` naming the field the context actually stores. The field name then lives in the wiring rather than in the trait. Like any getter trait, a `#[cgp_getter]` trait can also be implemented directly on a concrete context.

## Syntax

The macro is applied to a getter trait and accepts exactly the method forms [`#[cgp_auto_getter]`](cgp_auto_getter.md#syntax) does, because the two share one parser. Those are the `&self` and `&mut self` receivers, the typed-reference argument that reads a field of another type, the optional `PhantomData<T>` second argument, the return-type forms with their conversions, and the single associated type. That document describes each in full. The simplest form takes no argument:

```rust
#[cgp_getter]
pub trait HasName {
    fn name(&self) -> &str;
}
```

The provider trait's name defaults to the trait name with its leading `Has` replaced by a trailing `Getter`, so `HasName` yields the provider `NameGetter` and the component `NameGetterComponent`. A provider name passed as the argument overrides the default, as with `#[cgp_component]`:

```rust
#[cgp_getter(GetName)]
pub trait HasName {
    fn name(&self) -> &str;
}
```

Here the provider trait is `GetName` and the component `GetNameComponent`. The default suits traits that follow the `Has{Field}` naming convention. A trait whose name does not start with `Has`, or is exactly `Has`, gets no default, and the bare `#[cgp_getter]` then fails with ``the `provider` key must be given``.

Because the getter is a component, its trait also accepts the companion attributes `#[cgp_component]` collects, such as [`#[prefix]`](../attributes/prefix.md) to register it in a namespace.

## Syntax Grammar

The attribute argument has the same grammar as [`#[cgp_component]`](cgp_component.md#syntax-grammar)'s `CgpComponentArgs`, a bare provider name or the keyed `name`/`provider`/`context` form:

```ebnf
CgpGetterArgs -> CgpComponentArgs    // see #[cgp_component]
```

The only difference is the default for an omitted `provider`, derived from a `Has`-prefixed trait name as Syntax describes. Without that prefix `provider` is required. The other keys and their defaults are those of `#[cgp_component]`.

## Expansion

`#[cgp_getter]` emits everything `#[cgp_component]` emits, followed by getter-specific provider impls. The component part is what `#[cgp_component(NameGetter)]` would produce: the consumer trait, the provider trait, both blanket impls, the `NameGetterComponent` marker, and the standard `UseContext` and `RedirectLookup` impls (see [`#[cgp_component]`](cgp_component.md) for that core). The macro then adds three getter providers:

- **`UseFields`** — always emitted; reads each method's field by the method's name.
- **`UseField<Tag>`** — emitted only for a trait with exactly one method; reads the field named by the wiring.
- **`WithProvider<Provider>`** — emitted only for a trait with exactly one method; adapts a field-getter provider.

The two single-method providers presuppose one field to read, which is why a trait with several methods gets only `UseFields`. The macro emits `UseFields` first, then `UseField` and `WithProvider`.

### `UseField`

The `UseField` impl is what lets the field name differ from the method name. For the single-method `HasName` trait, the macro emits this impl for `UseField<__Tag__>`, where `__Tag__` is a free parameter that stands for the field name a context chooses when wiring:

```rust
impl<__Context__, __Tag__> NameGetter<__Context__> for UseField<__Tag__>
where
    __Context__: HasField<__Tag__, Value = String>,
{
    fn name(__context__: &__Context__) -> &str {
        __context__.get_field(PhantomData::<__Tag__>).as_str()
    }
}
```

Wiring the component to `UseField<Symbol!("first_name")>` supplies `first_name` as `__Tag__`, and the getter reads that field. `#[cgp_auto_getter]`'s blanket impl, by contrast, fixes the tag to `Symbol!("name")`. The return-type conversions are the same in both macros, so the `&str` return here requires a `String` field and appends `.as_str()`.

### `WithProvider`

The `WithProvider` impl adapts a [field-getter](../providers/use_field.md) provider into the getter component:

```rust
impl<__Context__, __Provider__> NameGetter<__Context__> for WithProvider<__Provider__>
where
    __Provider__: FieldGetter<__Context__, NameGetterComponent, Value = String>,
{
    fn name(__context__: &__Context__) -> &str {
        __Provider__::get_field(__context__, PhantomData::<NameGetterComponent>).as_str()
    }
}
```

The bound follows the getter's shape. A `&mut self` getter requires `MutFieldGetter` instead of `FieldGetter` and reads through its `get_field_mut`. A slice getter returning `&[T]` or `&mut [T]` bounds the value as `Value: AsRef<[T]> + 'static` (or `AsMut<[T]>`) instead of fixing it with `Value =`.

### `UseFields`

The `UseFields` impl is the provider form of `#[cgp_auto_getter]`'s blanket impl. It reads each method's field keyed by the method name:

```rust
impl<__Context__> NameGetter<__Context__> for UseFields
where
    __Context__: HasField<Symbol!("name"), Value = String>,
{
    fn name(__context__: &__Context__) -> &str {
        __context__.get_field(PhantomData::<Symbol!("name")>).as_str()
    }
}
```

Each of the three provider impls is paired with an `IsProviderFor` impl carrying the same `where` bounds, so a check reports a missing field by name. As elsewhere, `Symbol!("name")` is shown in sugared form rather than as the expanded `Symbol<…>` type.

## Examples

This example wires the getter to `UseField` with a field whose name differs from the method's, the case `#[cgp_auto_getter]` cannot express. The context stores the value in `first_name`, while the method is `name`:

```rust
use cgp::prelude::*;

#[cgp_getter]
pub trait HasName {
    fn name(&self) -> &str;
}

#[derive(HasField)]
pub struct Person {
    pub first_name: String,
}

delegate_components! {
    Person {
        NameGetterComponent: UseField<Symbol!("first_name")>,
    }
}

check_components! {
    Person {
        NameGetterComponent,
    }
}

fn greet(person: &Person) {
    println!("Hello, {}!", person.name()); // reads the first_name field
}
```

`Person` wires `NameGetterComponent` to `UseField<Symbol!("first_name")>`, so the generated `UseField` impl implements `name()` by reading `first_name`.

The consumer trait can instead be implemented directly on a concrete context, skipping the wiring:

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

The direct impl shows that a `#[cgp_getter]` trait is an ordinary component, whose consumer trait can be implemented like any Rust trait.

## Related constructs

These constructs are the ones `#[cgp_getter]` relates to:

- [`#[cgp_auto_getter]`](cgp_auto_getter.md) — the blanket-impl form keyed by the method name, and the owner of the shared method and return-type rules.
- [`#[cgp_component]`](cgp_component.md) — the macro this one extends, inheriting its expansion and provider-name syntax.
- [`UseField`](../providers/use_field.md) — the provider a context usually wires the getter to, reading fields produced by [`#[derive(HasField)]`](../derives/derive_has_field.md) and keyed by [`Symbol!`](symbol.md).
- [`delegate_components!`](delegate_components.md) and [`check_components!`](check_components.md) — wire the getter and verify the wiring.
- [`#[cgp_type]`](cgp_type.md) — overlaps with a getter whose return type is an abstract associated type.

## Known issues

The getter providers share their method synthesis with [`#[cgp_auto_getter]`](cgp_auto_getter.md), so they share its defect. A `&mut self` getter returning a shared `Option<&T>` or `Option<&str>` fails with `E0308`, because the body converts with `.as_mut()` or `.as_deref_mut()`. That document's Known issues gives the workaround.

## Source

- Entry point: `cgp_getter` in [crates/macros/cgp-macro-lib/src/cgp_getter.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_getter.rs), which derives the default provider name (strip `Has`, append `Getter`), runs the `#[cgp_component]` `preprocess → eval` pipeline, then converts the result into `ItemCgpGetter` and emits the extra provider impls.
- Logic: [crates/macros/cgp-macro-core/src/types/cgp_getter/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_getter/) — `item.rs` assembles the items, `use_field.rs` builds the `UseField` impl with the free `__Tag__` parameter, `to_use_fields_impl.rs` builds the `UseFields` impl keyed by method name, and `with_provider.rs` builds the `WithProvider` impl.
- Getter-method parsing and the return-type forms, shared with `#[cgp_auto_getter]`: [crates/macros/cgp-macro-core/src/functions/getter/parse.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/getter/parse.rs) and [crates/macros/cgp-macro-core/src/types/getter/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/getter/).
- Internal walkthrough (the pipeline stages, the function that synthesizes each generated item, the corner-case handling, and the index of tests and expansion snapshots): [implementation/entrypoints/cgp_getter.md](../../implementation/entrypoints/cgp_getter.md).
