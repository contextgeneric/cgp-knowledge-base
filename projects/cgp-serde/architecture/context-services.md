# Context services

Every cgp-serde provider receives the context, so a provider can require a trait on it and call that
trait while it works. The library uses this to deserialize borrowed values into an arena the context
supplies. This document explains the idea, the layered form the allocation crates take, and the
lifetimes that make it sound. The items are documented in [allocation](../reference/allocation.md).

## A provider can ask the context for more than serialization

**A provider's impl-side dependencies are not limited to the serialization components.** Any trait
the context implements can appear in a provider's `#[uses]` list, and the provider calls it on `self`
like any method. This is ordinary CGP
[impl-side dependency injection](../../../cgp/concepts/impl-side-dependencies.md); what makes it
notable here is that Serde has nowhere to put such a dependency. Serde's `Deserialize` has no receiver,
and `serde_json::from_str` has no argument for extra state, so a deserializer that needs an allocator,
a lookup table, or a configuration value cannot receive one. A cgp-serde provider receives the context,
and the context can carry any of them.

The arena deserializer is the worked instance. Deserializing many values as `&'a T` into one arena,
rather than as a `Box<T>` each, needs the arena during deserialization, and the provider takes it from
the context. The pattern corresponds to the motivating example of the context-and-capabilities
proposal for Rust, which [Rust language proposals](../../../related-work/rust-language-proposals.md)
compares with CGP; the word "capability" belongs to that proposal, not to CGP's own constructs.

## The layers

**The allocation crates separate what the deserializer needs from how it is provided, in three
layers, so the allocator is a wiring choice.**

- **The deserializer.** `DeserializeAndAllocate` deserializes an owned value through the context and
  hands it to the context's `CanAlloc`. It knows nothing about arenas.
- **The allocation component.** `CanAlloc<'a, T>` moves a value into storage living for `'a` and
  returns a reference. A context wires it to a provider like any component.
- **The implementation.** `AllocateWithArena` implements `CanAlloc` by allocating into the
  `typed_arena::Arena` the context's `HasArena` getter returns, and the getter is wired to a field.

A context wires all three, with the getter pointed at the field that holds the arena. Swapping the
allocator means wiring `AllocatorComponent` to a different provider, and giving a second type its own
arena means one more getter entry keyed on that type; neither touches the deserializer.

The repository's tests and the announcement post also use a simplified form that collapses the layers:
a local `DeserializeAndAllocate` calls a local `#[cgp_auto_getter]` `HasArena` directly. It is shorter
to read and fixes the allocator inside the deserializer, which is the dependency the layered form
removes. The [modular serialization example](../../../examples/modular-serialization.md) teaches the
simplified form.

## The lifetimes

**The allocated values outlive the context because the context only borrows the arena.** A context
such as `App<'a>` holds a `&'a Arena<Coord>` field, created by the caller before the context and
passed in. `CanAlloc<'a, T>` returns `&'a mut T`, tied to that outer lifetime rather than to the
context, so a deserialized `Payload<'a>` holding `&'a Coord` values stays valid after the context is
dropped, for as long as the arena lives. The deserialization lifetime `'de` is independent of `'a`: the
input can be discarded once deserialization finishes, because the values borrow from the arena rather
than from the input.

## Public material derived from this

The "Arena-allocating deserialization" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md).
