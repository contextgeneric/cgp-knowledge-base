# `Path!`

`Path!(@a.B.c)` builds a type-level path, a `PathCons` list of segments naming a route through
nested delegation tables, from a dotted, `@`-prefixed sequence of names.

## Purpose

`Path!` gives a readable syntax for the `PathCons` list CGP uses to address an entry behind layers
of delegation. A path names a route read left to right, where each segment narrows the lookup one
step: through a namespace, through a prefix, down to a component key. Writing that route as nested
`PathCons<…, PathCons<…, Nil>>` by hand is unwieldy, so `Path!` lets it be written as it reads, as a
dotted name like `@app.error.ErrorRaiserComponent`, and folds it into the list.

`Path!` is the routing sibling of the other type-level construction macros. [`Symbol!`](symbol.md)
makes a single type-level string, and [`Product!`](product.md) and [`Sum!`](sum.md) build record and
variant lists; `Path!` builds the routing list, with the same right-nested, `Nil`-terminated shape.
It constructs the [`PathCons`](../types/path_cons.md) type, and the same `@`-path syntax is embedded
directly in [`delegate_components!`](delegate_components.md) and
[`cgp_namespace!`](cgp_namespace.md) entries and in [`#[prefix(...)]`](../attributes/prefix.md)
attributes, which is where paths are most often written.

## Syntax

`Path!` takes one `@`-prefixed path of one or more dot-separated segments. The leading `@` is
required, as the sigil that marks the body as a path, and at least one segment must follow:

```rust
Path!(@app)
Path!(@app.error)
Path!(@app.error.ErrorRaiserComponent)
```

Each segment is parsed as a type, and the segment's spelling decides how it is encoded:

- **A symbol segment** is a single identifier that starts with a lowercase ASCII letter and is not a
  primitive type name. It becomes a [`Symbol!`](symbol.md) string of that identifier, so `app` and
  `error` are symbols.
- **Any other segment** stays the type it spells: a capitalized name such as `ErrorRaiserComponent`,
  usually a component key or a namespace marker, a primitive such as `u32`, `bool`, `usize`, or
  `str`, or any type with generic arguments or a path.

The primitive check is broader than the real primitives. It treats `char`, `bool`, `usize`, `isize`,
`str`, and any identifier made of `i`, `u`, or `f` followed only by digits as a primitive, which
includes the bare names `i`, `u`, and `f` and names such as `u2`. So `@app.f` names a type `f`
rather than the symbol `"f"`, as Known issues explains.

Mixing the two kinds is normal: `@my_app.ShowImplComponent` pairs a symbol segment with a component
segment.

## Syntax Grammar

The input is a leading `@` followed by one or more dot-separated segments:

```ebnf
PathInput   -> `@` PathSegment ( `.` PathSegment )*

PathSegment -> Type
```

Each `PathSegment` is parsed as a Rust `Type`, and its encoding is decided afterwards by the rule in
Syntax. This is the `Path` production that [`delegate_components!`](delegate_components.md),
[`cgp_namespace!`](cgp_namespace.md), and [`#[prefix(...)]`](../attributes/prefix.md) embed. A
`delegate_components!` key extends it with groups and per-segment generics; a redirect value and a
prefix use it unchanged.

## Expansion

`Path!` expands to a right-nested chain of [`PathCons`](../types/path_cons.md) ending in `Nil`, with
each segment encoded by the rule above:

```rust
// before
Path!(@app.error.ErrorRaiserComponent)
```

```rust
// after
PathCons<
    Symbol!("app"),
    PathCons<
        Symbol!("error"),
        PathCons<ErrorRaiserComponent, Nil>,
    >,
>
```

The macro folds the segments from right to left onto `Nil`, wrapping each in a `PathCons` whose tail
is the rest. A single-segment path is therefore `PathCons<Segment, Nil>`, and because a symbol
segment is itself a `Symbol`/`Chars` chain, `Path!(@app)` fully expands to
`PathCons<Symbol<3, Chars<'a', Chars<'p', Chars<'p', Nil>>>>, Nil>`.

The same fold produces the paths embedded in wiring. A [`cgp_namespace!`](cgp_namespace.md) redirect
entry `FooProviderComponent => @MyFooComponent` has the `Delegate`
`RedirectLookup<__Table__, PathCons<MyFooComponent, Nil>>`, and
`#[prefix(@MyBarComponent in MyNamespace)]` on a `Bar` component produces
`PathCons<MyBarComponent, PathCons<BarProviderComponent, Nil>>`, with the component's own name
appended. A `delegate_components!` path key differs in one respect: it ends in a wildcard parameter
rather than `Nil`, as that macro's Expansion explains.

## Examples

A path is usually written as a redirect target. Used directly as a type, `Path!` names a route that
a [`RedirectLookup`](../providers/redirect_lookup.md) resolves against a table:

```rust
use cgp::prelude::*;

type ErrorRoute = Path!(@app.error.ErrorRaiserComponent);
// ErrorRoute = PathCons<Symbol!("app"),
//                  PathCons<Symbol!("error"),
//                      PathCons<ErrorRaiserComponent, Nil>>>
```

The same syntax is more often embedded in a table than written through the bare macro:

```rust
use cgp::prelude::*;

cgp_namespace! {
    new MyNamespace {
        FooProviderComponent =>
            @MyFooComponent,
    }
}
// the entry's Delegate is RedirectLookup<__Table__, PathCons<MyFooComponent, Nil>>
```

Either way the path is the same `PathCons` list.

## Related constructs

These constructs are the ones `Path!` relates to:

- [`PathCons`](../types/path_cons.md): the list type the macro expands to.
- [`Symbol!`](symbol.md): the encoding of each symbol segment.
- [`Product!`](product.md) and [`Sum!`](sum.md): the other type-level list macros, with the same
  right-fold shape.
- [`RedirectLookup`](../providers/redirect_lookup.md): resolves a lookup along a path.
- [`delegate_components!`](delegate_components.md), [`cgp_namespace!`](cgp_namespace.md), and
  [`#[prefix(...)]`](../attributes/prefix.md): embed the `@`-path syntax in wiring.
- [`ConcatPath`](../traits/static_format.md): appends one path to another, as a component's
  `RedirectLookup` impl does with its type parameters.

## Known issues

A lowercase segment spelled like a numeric primitive becomes a type rather than a symbol. The
primitive check accepts any identifier of `i`, `u`, or `f` followed only by digits, so it matches
the bare `i`, `u`, and `f` and names such as `u2` or `f16` alongside the real `u32` and `f64`.
`@app.f` therefore expands with a type segment `f` instead of `Symbol!("f")`, and fails to compile
unless a type `f` is in scope. The correct behavior would be to recognize only Rust's actual
primitive names. Until then, avoid such one-letter or letter-digit segments in paths.

## Source

- Entry point: `Path` in
  [crates/macros/cgp-macro-lib/src/path.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/path.rs),
  which parses the body into a `UniPath` and emits its tokens.
- Parsing and codegen:
  [crates/macros/cgp-macro-core/src/types/path/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/path/):
  `unipath.rs` requires the leading `@`, parses the dot-separated segments, and right-folds them
  with `PathCons` onto `Nil`; `path_element.rs` decides per segment whether it becomes a `Symbol` or
  stays a type, including the `is_primitive_type` check.
- Runtime list `PathCons`:
  [crates/core/cgp-base-types/src/types/path.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/path.rs);
  the `RedirectLookup` provider that resolves a path is in
  [crates/core/cgp-component/src/providers/redirect_lookup.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/providers/redirect_lookup.rs).
- Internal walkthrough (the parse-and-emit pipeline, the per-segment classification, the `PathCons`
  fold, and the index of tests):
  [implementation/entrypoints/path.md](../../implementation/entrypoints/path.md).
