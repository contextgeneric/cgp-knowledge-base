# Allocation providers

The allocation crates deserialize a borrowed `&'a T` by deserializing an owned `T` and moving it into
an allocator that the context supplies. They split the work into layers so the allocator is a wiring
choice: `cgp-serde-alloc` defines an allocation component, `CanAlloc`, and the deserializer that uses
it, `DeserializeAndAllocate`; `cgp-serde-typed-arena` implements the component over
[`typed-arena`](https://docs.rs/typed-arena/) with an arena getter and `AllocateWithArena`. Why a
provider can draw a service from its context at all is the subject of the
[architecture](../architecture/README.md); this document records the items and how they are wired.

## `CanAlloc`

`CanAlloc<'a, T>` is a component that moves a value into storage living for `'a` and returns a
reference to it.

### Definition

```rust
#[cgp_component(Allocator)]
pub trait CanAlloc<'a, T> {
    fn alloc(&self, value: T) -> &'a mut T;
}
```

It lives in `cgp_serde_alloc::traits`, with the provider trait `Allocator` and the wiring key
`AllocatorComponent`.

### Behavior

The trait says nothing about where the value goes, only that it lives for `'a`, which is typically a
lifetime parameter of the context. `AllocateWithArena` is the only provider in the library; another
allocator can implement `Allocator` without touching the deserializer.

### Context dependencies

None of its own; a context wires `AllocatorComponent` to a provider.

### Pairing

Not applicable.

## `DeserializeAndAllocate`

`DeserializeAndAllocate` deserializes a `&'a Value` by deserializing an owned `Value` through the
context and allocating it through the context's `CanAlloc`.

### Definition

```rust
#[cgp_impl(new DeserializeAndAllocate)]
#[uses(CanAlloc<'a, Value>, CanDeserializeValue<'de, Value>)]
impl<'de, 'a, Value> ValueDeserializer<'de, &'a Value>
{ ... }
```

### Behavior

The provider deserializes the owned value through the context, passes it to `alloc`, and returns the
resulting `&'a mut Value` as a `&'a Value`. The lifetime `'a` is independent of the input's `'de`, so
the returned reference outlives the input and borrows from the allocator instead. Wired for `&'a Coord`,
it lets a `Cluster<'a>` whose `coords: Vec<&'a Coord>` field is read through
[`DeserializeExtend`](collections.md#deserializeextend) fill itself with references into an arena.

### Context dependencies

`CanDeserializeValue<'de, Value>` for the owned type, and `CanAlloc<'a, Value>`.

### Pairing

No serializing counterpart; a reference serializes through
[`SerializeDeref`](conversions.md#serializederef).

## `HasArena`

`HasArena<'a, T>` is a getter component that reads a `typed_arena::Arena<T>` from the context.

### Definition

```rust
#[cgp_getter(ArenaGetter)]
#[derive_delegate(UseDelegate<T>)]
pub trait HasArena<'a, T: 'a> {
    fn arena(&self) -> &&'a Arena<T>;
}
```

It lives in `cgp_serde_typed_arena::traits`, with the provider trait `ArenaGetter` and the wiring key
`ArenaGetterComponent`.

### Behavior

Because it is a [`#[cgp_getter]`](../../../cgp/reference/macros/cgp_getter.md) component, a context
chooses which field supplies the arena by wiring, typically with
[`UseField`](../../../cgp/reference/providers/use_field.md). The return type is a reference to a
reference because the getter returns a reference to the field, and the field itself holds a
`&'a Arena<T>` borrowed from outside the context. That outer borrow is what lets allocated values
outlive the context.

A context with arenas for several types wires the getter per type with the `open` statement, keyed on
`T`:

```rust
#[derive(HasField)]
pub struct App<'a> {
    pub coords: &'a Arena<Coord>,
    pub tags: &'a Arena<Tag>,
}

delegate_components! {
    <'s> App<'s> {
        open ArenaGetterComponent;

        @ArenaGetterComponent.Coord: UseField<Symbol!("coords")>,
        @ArenaGetterComponent.Tag: UseField<Symbol!("tags")>,
    }
}
```

The `#[derive_delegate(UseDelegate<T>)]` attribute generates the legacy `UseDelegate` dispatch impl,
which the `open` form does not need.

### Context dependencies

None of its own.

### Pairing

Not applicable.

## `AllocateWithArena`

`AllocateWithArena` implements `CanAlloc` by allocating into the arena the context's `HasArena`
returns.

### Definition

```rust
#[cgp_impl(new AllocateWithArena)]
#[uses(HasArena<'a, Value>)]
impl<'a, Value: 'a> Allocator<'a, Value>
{ ... }
```

### Behavior

The provider calls `self.arena().alloc(value)`, so the value is moved into the arena and lives as long
as the arena's borrow. All values are freed together when the arena is dropped.

### Context dependencies

`HasArena<'a, Value>`.

### Pairing

Not applicable.

## Wiring the layers

A context that deserializes into an arena wires all three layers: the arena getter to a field, the
allocator to `AllocateWithArena`, and the borrowed type to `DeserializeAndAllocate`, alongside the
owned type and the containing types:

```rust
#[derive(HasField)]
pub struct App<'a> {
    pub arena: &'a Arena<Coord>,
}

delegate_components! {
    <'a> App<'a> {
        open ValueDeserializerComponent;

        ErrorTypeProviderComponent: UseAnyhowError,
        ErrorRaiserComponent: RaiseAnyhowError,
        ArenaGetterComponent: UseField<Symbol!("arena")>,
        AllocatorComponent: AllocateWithArena,

        @ValueDeserializerComponent.u64: UseSerde,
        @ValueDeserializerComponent.[Coord, <'b> Payload<'b>]: DeserializeRecordFields,
        @ValueDeserializerComponent.<'b> &'b Coord: DeserializeAndAllocate,
        @ValueDeserializerComponent.<'b> Vec<&'b Coord>: DeserializeExtend,
    }
}

check_components! {
    #[check_trait(CanUseArena)]
    <'a> App<'a> {
        ArenaGetterComponent: (Life<'a>, Coord),
    }
}

check_components! {
    #[check_trait(CanDeserializeWithArena)]
    <'de, 'a> App<'a> {
        ValueDeserializerComponent: [
            (Life<'de>, Coord),
            (Life<'de>, &'a Coord),
            (Life<'de>, Payload<'a>),
        ],
    }
}
```

The context carries the arena as an ordinary field borrowed from outside, so the caller creates the
arena, builds `App { arena: &arena }`, and deserializes; the resulting `Payload<'_>` borrows from the
arena. The error components are there because the JSON helper raises `serde_json` errors through the
context; see [JSON providers](json.md).

The repository's tests also carry a simplified form, which the announcement post uses; the
[modular serialization example](../../../examples/modular-serialization.md) uses the layered form. It defines its own
`#[cgp_auto_getter]` `HasArena` and its own `DeserializeAndAllocate` that calls `self.arena().alloc`
directly, with no `CanAlloc` layer and no allocator wiring. That form is shorter, but it fixes the
allocator inside the deserializer, which the layered crates exist to avoid.

## Source

- [`crates/cgp-serde-alloc/src/traits/alloc.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-alloc/src/traits/alloc.rs) — `CanAlloc`.
- [`crates/cgp-serde-alloc/src/providers/alloc_deserialize.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-alloc/src/providers/alloc_deserialize.rs) — `DeserializeAndAllocate`.
- [`crates/cgp-serde-typed-arena/src/traits/has_arena.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-typed-arena/src/traits/has_arena.rs) — `HasArena`.
- [`crates/cgp-serde-typed-arena/src/providers/alloc.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-typed-arena/src/providers/alloc.rs) — `AllocateWithArena`.

## Public material derived from this

The "Arena-allocating deserialization" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the rustdoc for both crates.
