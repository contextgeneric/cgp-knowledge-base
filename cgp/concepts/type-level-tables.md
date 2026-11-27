# Type-level tables

A CGP wiring table is a trait with an associated type, implemented once per key, so the compiler can
look an entry up during type checking. This document explains that lookup in general, then the forms
CGP builds on it: the wiring table that routes a call to its provider, tables keyed by other types,
path keys, tables that point to other tables, and namespaces written from the key's side. It is the
one concept document that explains the lookup; the others link here.

## A trait as a map

A trait whose only item is an associated type works as a compile-time map. Each impl is one entry:
the implementing type is the table, the trait's parameter is the key, and the associated type is the
value. This plain Rust table maps two shape types to the provider types that measure them:

```rust
use core::marker::PhantomData;

pub trait HasEntry<Key> {
    type Value;
}

pub struct AreaTable;

pub struct Rectangle;
pub struct Circle;
pub struct RectangleArea;
pub struct CircleArea;

impl HasEntry<Rectangle> for AreaTable {
    type Value = RectangleArea;
}

impl HasEntry<Circle> for AreaTable {
    type Value = CircleArea;
}

pub fn entry<Key>() -> PhantomData<<AreaTable as HasEntry<Key>>::Value>
where
    AreaTable: HasEntry<Key>,
{
    PhantomData
}
```

The bound `AreaTable: HasEntry<Key>` reads an entry, and the projection
`<AreaTable as HasEntry<Key>>::Value` names its value: `RectangleArea` for `Rectangle` and
`CircleArea` for `Circle`. A key without an impl fails the bound at compile time.

Coherence is what makes the trait a map rather than a relation. A second impl of `HasEntry<Rectangle>`
for `AreaTable` overlaps the first and is rejected with `E0119`, so each key has one value. The lookup
runs during type checking, so the compiled program holds no table and pays nothing to consult it.

## The wiring table

CGP's table trait has exactly this shape under another name:
[`DelegateComponent<Key>`](../reference/traits/delegate_component.md), whose associated type
`Delegate` is the entry's value:

```rust
pub trait DelegateComponent<Key: ?Sized> {
    type Delegate;
}
```

[`delegate_components!`](../reference/macros/delegate_components.md) writes one impl per entry. The
same `AreaTable` written with it is:

```rust
delegate_components! {
    new AreaTable {
        Rectangle: RectangleArea,
        Circle: CircleArea,
    }
}
```

The table a context carries for its wiring is the same trait, keyed by component markers. Take a
`StorageObjectFetcher` component, whose consumer trait `CanFetchStorageObject` fetches a stored
object by its ID, and an environmental context `App` that wires it to `FetchS3Object`. The entry
`StorageObjectFetcherComponent: FetchS3Object` is:

```rust
impl DelegateComponent<StorageObjectFetcherComponent> for App {
    type Delegate = FetchS3Object;
}
```

A call reaches its provider through two blanket impls that
[`#[cgp_component]`](../reference/macros/cgp_component.md) generates. The consumer blanket impl gives a
context the consumer trait when it implements the provider trait for itself:

```rust
impl<Context> CanFetchStorageObject for Context
where
    Context: StorageObjectFetcher<Context>,
{
    fn fetch_storage_object(&self, object_id: &str) -> anyhow::Result<Vec<u8>> {
        Context::fetch_storage_object(self, object_id)
    }
}
```

The provider blanket impl gives any type with a table entry the provider trait of the entry's value.
Shown with only its table bound, and with readable parameter names:

```rust
impl<Context, Table> StorageObjectFetcher<Context> for Table
where
    Table: DelegateComponent<StorageObjectFetcherComponent>,
    Table::Delegate: StorageObjectFetcher<Context>,
{
    fn fetch_storage_object(context: &Context, object_id: &str) -> anyhow::Result<Vec<u8>> {
        Table::Delegate::fetch_storage_object(context, object_id)
    }
}
```

For `app.fetch_storage_object("alice.png")`, the consumer blanket impl asks for
`App: StorageObjectFetcher<App>`. The provider blanket impl answers it with `Table` and `Context` both
`App`: it reads `App`'s entry, finds `FetchS3Object`, and needs
`FetchS3Object: StorageObjectFetcher<App>`, which the provider's own impl supplies. The context stays `App`
throughout, so the provider receives the value the caller invoked the method on. In a real expansion
the parameters are `__Context__` and `__Provider__`, and `cargo cgp expand` prints them.

## The hidden requirement

The real provider blanket impl also bounds the table on
[`IsProviderFor`](../reference/traits/is_provider_for.md):
`Provider: DelegateComponent<StorageObjectFetcherComponent> + IsProviderFor<StorageObjectFetcherComponent, Context, ()>`.
`DelegateComponent` itself has no such bound; `delegate_components!` writes an `IsProviderFor` impl
beside each entry, forwarding the chosen provider's own `IsProviderFor`, which carries the provider's
dependencies. So when a dependency of the chosen provider is missing, the compiler reports it against
that provider instead of a bare unimplemented trait. A `DelegateComponent` impl written by hand without
the `IsProviderFor` impl beside it does not wire the component.
[Check traits](check-traits.md) explains `IsProviderFor` and how a check reaches through it.

## Tables keyed by other types

A table can be keyed by any type, and a provider can read it with a second lookup. The legacy
[`UseDelegate<Components>`](../reference/providers/use_delegate.md) does this for a component with a
type parameter: a component marked `#[derive_delegate(UseDelegate<Shape>)]` gets an impl that looks
`Shape` up in `Components` and forwards to the entry's provider, so one wiring entry fans out per
type. The handler family's `UseInputDelegate` is the same lookup keyed by a handler's input.

The `open` statement replaces both, keeping the per-type entries in the context's own table:

```rust
delegate_components! {
    MyApp {
        open AreaCalculatorComponent;

        @AreaCalculatorComponent.Rectangle: RectangleArea,
        @AreaCalculatorComponent.Circle: CircleArea,
    }
}
```

Here the component is `CanCalculateArea<Shape>`, a parameter-targeted component on an environmental
context, `MyApp`.

## Paths as keys

`open` works by routing the component to a lookup on a type-level path. Its entry wires the component
to [`RedirectLookup`](../reference/providers/redirect_lookup.md), whose generated impl appends each of
the component's type parameters to the path, as a [`PathCons`](../reference/types/path_cons.md) list,
and makes one `DelegateComponent` query on the whole path. `@AreaCalculatorComponent.Rectangle` is the
key `PathCons<AreaCalculatorComponent, PathCons<Rectangle, _>>`.

A path entry is emitted with a generic tail, so a key matches every longer path beneath it. A shorter
key and a longer key under it therefore overlap and fail with `E0119`; the table has no rule that the
most specific entry wins. A generic segment, as in `@ComputerComponent.<Code> Code.Plus<MathExpr>`,
matches every value in its position.

## Nested tables and namespaces

An entry's value can be another table. An [aggregate provider](aggregate-providers.md) is a table
declared with `new` and used as a provider: a context delegates a group of components to it, and each
lookup reads the context's entry, then the aggregate's entry for the same key, while the context
stays the same. The `->` operator forwards one key to the same key's entry in another table.

A [namespace](namespaces.md) is a table written from the key's side. A
[`cgp_namespace!`](../reference/macros/cgp_namespace.md) entry emits `impl Namespace<Table> for Key`,
the reverse of `impl DelegateComponent<Key> for Table`, and leaves the table generic, so one entry
serves every context that joins. Because the impl is for the key:

- **Routes:** [`#[prefix]`](../reference/attributes/prefix.md) lets a component's crate register its
  route into any namespace, since the impl is for the component marker, which that crate owns.
- **Defaults:** [`#[default_impl]`](../reference/attributes/default_impl.md) registers a per-type
  default under the orphan rule: the crate must own the namespace trait, or a local type must stand
  ahead of the table parameter, such as the key or a component in the namespace path. A path key is
  never local.

A context joins with `namespace N;`, which emits one blanket `DelegateComponent` impl that forwards
every key `N` answers. A direct entry for a key the namespace binds overlaps that blanket and fails
with `E0119`, so a shared namespace leaves open the paths its contexts vary. A `for … in` loop copies
registered defaults into the context's table by projecting each default's `Delegate`.

## Other tables

The same shape recurs beyond wiring:

- **Fields:** [`HasField<Tag>`](../reference/traits/has_field.md) is a table on a struct keyed by a
  field's type-level name, whose value is the field's type, with a method that reads it.
- **Abstract types:** [`UseDelegatedType<Components>`](../reference/providers/use_delegated_type.md)
  answers an abstract type from a `DelegateComponent` table keyed by its tag.
- **Checks:** [`CanUseComponent`](../reference/traits/can_use_component.md) requires both an entry and
  a delegate that can serve the context.

## What a table cannot do

The lookup's limits follow from its being trait resolution:

- **No overriding or priority:** every overlap is an error, so a shared table cannot be specialized
  by a context; it must leave open the entries contexts vary.
- **Cycles:** each lookup is a trait obligation, so a provider that needs the instance it is defining
  overflows the solver with `E0275`. A recursive type needs a provider written for the concrete
  context; the language-proposals comparison,
  [rust-language-proposals.md](../../related-work/rust-language-proposals.md), works this out.
- **Laziness:** a table entry alone checks nothing about its provider; a missing dependency surfaces
  at a use or a [check](check-traits.md).
- **Diagnostics:** errors name `PathCons` and `Symbol` types; `cargo cgp expand` prints them as
  `Path!` and `Symbol!`.
- **Fixed at compile time:** a table cannot be listed or changed at runtime, and each lookup adds
  compile-time work.

## Related constructs

[`DelegateComponent`](../reference/traits/delegate_component.md) is the table trait and
[`delegate_components!`](../reference/macros/delegate_components.md) writes it.
[`RedirectLookup`](../reference/providers/redirect_lookup.md),
[`UseDelegate`](../reference/providers/use_delegate.md), and
[`DefaultNamespace`](../reference/traits/default_namespace.md) read tables keyed by paths, parameters,
and namespace keys. [Consumer and provider traits](consumer-and-provider-traits.md) explains the
trait split the wiring table connects, and [check traits](check-traits.md) explains `IsProviderFor`.
