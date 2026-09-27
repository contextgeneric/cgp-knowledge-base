# `ChainGetters`

`ChainGetters<Getters>` is a zero-sized foundational field getter that composes a list of field
getters, reading from the context through a sequence of intermediate values to reach a nested field.

## Purpose

`ChainGetters` reaches a field several hops inside the context. A single [`UseField`](use_field.md)
reads one field of one value, but contexts nest: a context holds a config, and the config holds a
port. `ChainGetters` takes a list of getters, applies them in order, and passes the reference from
each step to the next, so the wiring reads like the path it follows.

The list is a type-level [`Cons`](../types/cons.md) list, usually written with
[`Product!`](../macros/product.md), whose elements are field getters for the value the previous step
produced.

## Definition

`ChainGetters` is defined in `cgp-field`:

```rust
pub struct ChainGetters<Getters>(pub PhantomData<Getters>);
```

It implements only the foundational [`FieldGetter`](../traits/has_field.md), not a getter
component's provider trait, so it is wired to a getter through [`WithProvider`](with_provider.md).
It has no `With…` alias and is not in the prelude; it is imported from `cgp::core::field::impls`.

## Implementations

Two `FieldGetter` impls recurse over the list. The `Cons` impl applies the head getter and runs the
rest of the chain on its result:

```rust
impl<Context, Tag, Getter, RestGetters, ValueA, ValueB> FieldGetter<Context, Tag>
    for ChainGetters<Cons<Getter, RestGetters>>
where
    Getter: FieldMapper<Context, Tag, Value = ValueA>,
    ChainGetters<RestGetters>: FieldGetter<ValueA, Tag, Value = ValueB>,
{
    type Value = ValueB;

    fn get_field(context: &Context, tag: PhantomData<Tag>) -> &ValueB {
        Getter::map_field(context, tag, |value| {
            <ChainGetters<RestGetters>>::get_field(value, tag)
        })
    }
}
```

The `Nil` impl ends the recursion as the identity getter, returning the value it was given:

```rust
impl<Context, Tag> FieldGetter<Context, Tag> for ChainGetters<Nil> {
    type Value = Context;

    fn get_field(context: &Context, _tag: PhantomData<Tag>) -> &Context {
        context
    }
}
```

Three details of the `Cons` impl matter to a user:

- **The head is applied through `FieldMapper`**, whose `map_field` passes the intermediate reference
  to a closure. This keeps the borrow's lifetime inferable across hops. `FieldMapper` has a blanket
  impl for every `FieldGetter`, which requires the getter and the tag to be `'static`.
- **Every step is asked under the same `Tag`**, the getter component's marker. Each getter in the
  list decides which field of its input it reads, so a `UseField<Symbol!("port")>` step reads `port`
  whatever the tag.
- **A one-getter chain** is that getter, and an empty chain returns the context itself.

## Examples

This getter reads a port stored inside the context's config:

```rust
use cgp::prelude::*;
use cgp::core::field::impls::ChainGetters;

#[cgp_getter]
pub trait HasPort {
    fn port(&self) -> &u16;
}

#[derive(HasField)]
pub struct Config {
    pub port: u16,
}

#[derive(HasField)]
pub struct App {
    pub config: Config,
}

delegate_components! {
    App {
        PortGetterComponent: WithProvider<
            ChainGetters<Product![
                UseField<Symbol!("config")>,
                UseField<Symbol!("port")>,
            ]>,
        >,
    }
}
```

The first step reads `App`'s `config` field as a `&Config`, and the second reads that config's
`port` as a `&u16`. `WithProvider` turns the chain's `FieldGetter` into the `PortGetter` provider,
so `app.port()` returns the nested port.

## Related constructs

These constructs are the ones `ChainGetters` works with:

- [`FieldGetter`](../traits/has_field.md): the trait it implements and composes, with `FieldMapper`
  from the same crate.
- [`UseField`](use_field.md) and [`UseFieldRef`](use_field_ref.md): getters used as steps.
- [`WithProvider`](with_provider.md): the adapter that wires it to a getter component.
- [`Cons`](../types/cons.md) and [`Product!`](../macros/product.md): the list of steps.
- [`#[cgp_getter]`](../macros/cgp_getter.md): defines the getter components it serves.

## Source

- The `ChainGetters` struct and its two `FieldGetter` impls (the `Cons` recursion step and the `Nil`
  base case) are in
  [crates/core/cgp-field/src/impls/chain.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/impls/chain.rs).
- The `FieldGetter` and `FieldMapper` traits it builds on are in
  [crates/core/cgp-field/src/traits/has_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/has_field.rs)
  and
  [crates/core/cgp-field/src/traits/map_field.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/map_field.rs).
- The `Cons`/`Nil` list it recurses over is defined in
  [crates/core/cgp-base-types/src/types/](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-base-types/src/types/)
  (`cons.rs` and `nil.rs`).
