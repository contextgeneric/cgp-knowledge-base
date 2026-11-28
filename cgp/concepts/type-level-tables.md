# Type-level tables

A trait whose only item is an associated type works as a compile-time map: each impl is one entry,
the implementing type is the table, the trait's parameter is the key, and the associated type is the
value. This document explains that lookup in plain Rust, beside the value-level `HashMap` code each
step mirrors, then maps the pieces onto the traits CGP's wiring uses. The CGP side of each piece is
explained where it is used: the call trace in [consumer and provider traits](consumer-and-provider-traits.md),
`IsProviderFor` in [check traits](check-traits.md), and path keys and key-side registration in
[namespaces](namespaces.md).

## A table and its entries

A trait with one associated type, implemented once per key, is a table. Each lookup in the examples
returns a `&'static str` through `core::any::type_name`, so it can be compared with a value-level map:

```rust
use core::any::type_name;

pub trait HasEntry<Key> {
    type Value;
}

pub struct MyTable;

pub struct FooKey;
pub struct BarKey;

pub struct Bar;
pub struct Baz;

impl HasEntry<FooKey> for MyTable {
    type Value = Bar;
}

impl HasEntry<BarKey> for MyTable {
    type Value = Baz;
}

pub fn get_foo_value<Table: HasEntry<FooKey>>() -> &'static str {
    type_name::<Table::Value>()
}

// get_foo_value::<MyTable>() == type_name::<Bar>()
```

The bound `Table: HasEntry<FooKey>` reads an entry, and `Table::Value` names its value; the short form
stands for `<Table as HasEntry<FooKey>>::Value` and is accepted because one bound in scope supplies a
`Value`. `type_name` returns a full path, so a test compares with `type_name::<Bar>()`, not the
literal `"Bar"`. The value-level counterpart reads `table["FooKey"]` from a global
`static MY_TABLE: LazyLock<HashMap<&'static str, &'static str>>`, since a type-level table is one per
program; its functions take the table as an argument, mirroring the `Table` parameter.

## Duplicate and missing keys

Coherence makes the trait a map rather than a relation, and the type checker reports every mistake
the `HashMap` would report at runtime:

- **Duplicate key:** a second `impl HasEntry<FooKey> for MyTable` fails with `E0119`.
- **Missing key:** `get_foo_value::<OtherTable>()` for a table without the entry fails with `E0277`,
  ``the trait bound `OtherTable: HasEntry<FooKey>` is not satisfied``, where the map panics or `get`
  returns `None`.
- **Generic key:** `impl<T> HasEntry<Vec<T>>` beside `impl HasEntry<Vec<u8>>` fails with `E0119`; the
  table has no rule that the most specific entry wins.
- **No runtime table:** every lookup is resolved during type checking.

## A lookup as a type

A type can answer a question by reading a table it is given:

```rust
use core::marker::PhantomData;

pub trait HasStaticString<Key> {
    fn static_string() -> &'static str;
}

pub struct Lookup<Table>(pub PhantomData<Table>);

impl<Table, Key> HasStaticString<Key> for Lookup<Table>
where
    Table: HasEntry<Key>,
{
    fn static_string() -> &'static str {
        type_name::<Table::Value>()
    }
}
```

The `where` clause is a precondition checked at each use. The value-level counterpart takes both the
table and the key as arguments, with `'static` values to match the return type.

## Nested tables

An entry's value can answer the next question, which gives a two-step lookup:

```rust
pub struct Forward<Table, KeyB>(pub PhantomData<(Table, KeyB)>);

impl<Table, KeyA, KeyB> HasStaticString<KeyA> for Forward<Table, KeyB>
where
    Table: HasEntry<KeyB>,
    Table::Value: HasStaticString<KeyA>,
{
    fn static_string() -> &'static str {
        <Table::Value as HasStaticString<KeyA>>::static_string()
    }
}
```

With an `OuterTable` whose entry for `InnerKey` is `Lookup<MyTable>`, `Forward<OuterTable, InnerKey>`
answers `FooKey` with `type_name::<Bar>()`. The value-level counterpart is a global map whose values
are references to other global maps, read as `outer[key_b][key_a]`.

## Composite keys

A tuple of keys is one key, so a table can answer a pair, and a type can fix one half of it:

```rust
impl HasEntry<(FooKey, BarKey)> for MyTable {
    type Value = Baz;
}

pub struct Redirect<Table, Prefix>(pub PhantomData<(Table, Prefix)>);

impl<Table, Prefix, Key> HasStaticString<Key> for Redirect<Table, Prefix>
where
    Table: HasEntry<(Prefix, Key)>,
{
    fn static_string() -> &'static str {
        type_name::<<Table as HasEntry<(Prefix, Key)>>::Value>()
    }
}
```

`Redirect<MyTable, FooKey>` answers `BarKey` with `type_name::<Baz>()`. A generic position matches every
type there, so `impl<Key> HasEntry<(FooKey, Key)>` overlaps the `(FooKey, BarKey)` entry with
`E0119`. The value-level counterpart is a second global
`HashMap<(&'static str, &'static str), &'static str>`, since a `HashMap` has one key type.

## Entry ownership

The orphan rule decides which crate may write an entry, because an entry is an impl:

- **Table side:** a crate that owns `MyKey` may write `impl HasEntry<MyKey> for TheirTable`, but not
  `impl<Table> HasEntry<MyKey> for Table` outside the crate that defines `HasEntry`, which fails with
  ``E0210: type parameter `Table` must be covered by another type when it appears before the first
  local type (`MyKey`)``.
- **Key side:** turning the trait around, `trait InTable<Table> { type Value; }`, lets the key's crate
  write `impl<Table> InTable<Table> for MyKey`, one entry every table reads.

## The tables in CGP

CGP's wiring is these pieces under other names:

- **`HasEntry<Key>`** is [`DelegateComponent<Key>`](../reference/traits/delegate_component.md), with
  the context as the table, written by [`delegate_components!`](../reference/macros/delegate_components.md).
- **`Forward<Table, Key>`** is the provider blanket impl that
  [`#[cgp_component]`](../reference/macros/cgp_component.md) generates, which reads the context's
  entry for the component and asks the provider found there; see
  [consumer and provider traits](consumer-and-provider-traits.md).
- **`Lookup<Table>`** is the legacy [`UseDelegate`](../reference/providers/use_delegate.md), so an
  outer entry whose value is a `Lookup` is a per-type dispatch table; an
  [aggregate provider](aggregate-providers.md) is the case where the value is another table asked
  for the same key.
- **`Redirect<Table, Prefix>`** is [`RedirectLookup`](../reference/providers/redirect_lookup.md),
  behind `open` and [namespaces](namespaces.md); its keys are [`PathCons`](../reference/types/path_cons.md)
  paths with a generic tail, so a shorter path covers every longer one beneath it.
- **`InTable<Table>`** is the shape of a namespace entry, which `#[prefix]` writes from the
  component's side.

## What a table cannot do

The lookup's limits follow from its being trait resolution:

- **No preference:** every overlap is an error, so a table cannot hold a default beside the cases that
  override it.
- **Cycles:** a lookup that needs its own answer overflows the solver; a table whose entry is a
  `Forward` back to the same table and key fails with ``E0275: overflow evaluating the requirement
  `Forward<Loop, FooKey>: HasStaticString<FooKey>` ``. CGP meets the same limit with recursive types,
  as [rust-language-proposals.md](../../related-work/rust-language-proposals.md) works out.
- **Fixed at compile time:** a table cannot be listed, iterated, or changed at runtime, and each lookup
  adds compile-time work.

## Related constructs

[`DelegateComponent`](../reference/traits/delegate_component.md) is the table trait, and
[`RedirectLookup`](../reference/providers/redirect_lookup.md), [`UseDelegate`](../reference/providers/use_delegate.md),
and [`DefaultNamespace`](../reference/traits/default_namespace.md) read tables keyed by paths,
parameters, and namespace keys. The examples compile in the website's
`example-code/tests/concepts/type_level_tables.rs`.
