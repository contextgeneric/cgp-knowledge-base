# `PathCons`

`PathCons<Head, Tail>` is the type-level path list, a recursive list of segments whose head and tail may both be unsized, that CGP uses to address an entry behind layers of delegation.

## Purpose

`PathCons` expresses a route through nested delegation tables as a single type. A bare component name picks one entry out of a context's table, but CGP sometimes needs an entry that sits behind indirection: inside a namespace, behind a namespace it inherits from, or under a prefix. A path names such a route as a list of segments read left to right. `PathCons` is the cell of that list and [`Nil`](cons.md) ends it, so `PathCons<A, PathCons<B, Nil>>` is the two-step path "first `A`, then `B`".

A path differs from the [`Cons`](cons.md) product list, although both are right-nested and end in `Nil`, in its unsized bounds. `PathCons` declares `Head: ?Sized` and `Tail: ?Sized`, so a segment can be an unsized type such as `str`, and a whole path can be handled without requiring its parts to have a known size. A product list holds a struct's field values, which are always sized; a path's segments are markers that never need to be.

The segments are the markers CGP uses elsewhere. A lowercase identifier becomes a [`Symbol`](chars.md) type-level string, and a capitalized name, usually a component key such as `FooProviderComponent` or a namespace marker, stays that type. Paths are written with the [`Path!`](../macros/path.md) macro or embedded in wiring as `@a.B.c`, rather than spelled by hand; that macro's document covers the syntax and the segment rule, and this one covers the runtime list.

## Definition

`PathCons` is a zero-sized struct holding two `PhantomData` markers, one for the head segment and one for the rest of the path:

```rust
pub struct PathCons<Head: ?Sized, Tail: ?Sized>(pub PhantomData<Head>, pub PhantomData<Tail>);
```

`Head` is the path's first segment and `Tail` the remainder, another `PathCons` or `Nil` at the end. The struct carries no runtime data and exists so a route can be named and matched in trait resolution.

## Behavior

`PathCons` supports concatenation through the [`ConcatPath`](../traits/static_format.md) trait, which appends one path to another at the type level. The trait recurses down the list: `PathCons<Head, Tail>` concatenated with `Other` keeps `Head` and concatenates `Tail` with `Other`, and `Nil` concatenated with `Other` becomes `Other`. The result is list append, computed as an associated-type projection:

```rust
pub trait ConcatPath<Other: ?Sized> {
    type Output: ?Sized;
}

impl<Head: ?Sized, Tail: ?Sized, Other: ?Sized> ConcatPath<Other> for PathCons<Head, Tail>
where
    Tail: ConcatPath<Other>,
{
    type Output = PathCons<Head, <Tail as ConcatPath<Other>>::Output>;
}

impl<Other: ?Sized> ConcatPath<Other> for Nil {
    type Output = Other;
}
```

A path is consumed by [`RedirectLookup`](../providers/redirect_lookup.md), the provider a redirect or a namespace entry names as `RedirectLookup<Components, Path>`. Its impl, which [`#[cgp_component]`](../macros/cgp_component.md) generates for each component, extends `Path` with the component's type parameters through `ConcatPath` and looks the whole extended path up as one key in `Components`, as `Components: DelegateComponent<Path>`. The path therefore never names a provider itself; it says which key to look up, so the same path can resolve to different providers in different tables, and the entry it reaches may redirect again.

## Examples

Paths most often appear inside the entries emitted by [`cgp_namespace!`](../macros/cgp_namespace.md). A namespace entry that redirects a component key to a path becomes a `RedirectLookup` over a `PathCons` list:

```rust
use cgp::prelude::*;

cgp_namespace! {
    new MyNamespace {
        FooProviderComponent =>
            @MyFooComponent,
    }
}

// the emitted entry, in readable form:
// impl<__Table__> MyNamespace<__Table__> for FooProviderComponent {
//     type Delegate = RedirectLookup<__Table__, PathCons<MyFooComponent, Nil>>;
// }
```

A path can interleave symbol and type segments. Registering a `Bar` component into a namespace with `#[prefix(@app in MyNamespace)]` produces a path of a symbol followed by the component's own marker:

```rust
// @app.BarProviderComponent  expands to
// PathCons<Symbol!("app"), PathCons<BarProviderComponent, Nil>>
```

A single-segment path is `PathCons<Segment, Nil>`, and the empty path is `Nil` alone.

## Related constructs

These constructs are the ones `PathCons` relates to:

- [`Cons`/`Nil`](cons.md) — the product list, with the same right-nested shape but sized field values as elements.
- [`Symbol`](chars.md) — the encoding of a lowercase segment.
- [`Path!`](../macros/path.md) — the macro that builds a path.
- [`ConcatPath`](../traits/static_format.md) — appends one path to another.
- [`RedirectLookup`](../providers/redirect_lookup.md) — looks a path up in a table.
- [`delegate_components!`](../macros/delegate_components.md) and [`cgp_namespace!`](../macros/cgp_namespace.md) — produce paths for redirects, `open` dispatch, and prefixed components; a `delegate_components!` path key ends in a wildcard parameter instead of `Nil`.

## Source

- The runtime type is defined in [crates/core/cgp-base-types/src/types/path.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/path.rs) (`PathCons<Head: ?Sized, Tail: ?Sized>`), with `Nil` in [crates/core/cgp-base-types/src/types/nil.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/nil.rs).
- The `ConcatPath` trait and its impls are in [crates/core/cgp-base-types/src/traits/concat_path.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/traits/concat_path.rs).
- The constructing macro is [`Path!`](../macros/path.md) ([crates/macros/cgp-macro-lib/src/path.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/path.rs)), whose fold over the segments is in [crates/macros/cgp-macro-core/src/types/path/unipath.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/path/unipath.rs).
- `RedirectLookup`, which consumes a path at resolution time, is in [crates/core/cgp-component/src/providers/redirect_lookup.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/providers/redirect_lookup.rs).

## Public pages derived from this document

This document feeds the public [`PathCons`](https://contextgeneric.dev/docs/reference/types/path_cons) page under `types/`, per the [synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping is recorded in [website/site-structure.md](../../../website/site-structure.md).
