# The `path` AST stack

The `path` stack is the family of AST types that parse and emit CGP's type-level paths. `Path!`
drives only two of them: `UniPath`, which parses an `@`-path and emits its `PathCons` chain, and
`PathElement`, which classifies each segment as a symbol or a named type. The rest serve the richer
path forms of `delegate_components!` keys, the `=>` redirect, `#[prefix]`, and `#[default_impl]`.
This document covers the types in the order the data flows; the
[entrypoint document](../entrypoints/path.md) covers what `Path!` produces.

## `PathElement`

`PathElement` is one segment of a path, either a named `Type` or a `Symbol`. Its `Parse` impl reads
the segment as a full Rust `Type` and then reclassifies it: a type that is a single identifier,
begins with a lowercase ASCII letter, and is not a primitive name becomes a `Symbol`, built with
`Symbol::from_ident` (see the [`Symbol` AST](symbol.md)); anything else stays the named `Type`.

```rust
app                  // Symbol: lowercase, not a primitive
ErrorRaiserComponent // Type: capitalized
u32                  // Type: lowercase but a primitive
```

`is_primitive_type` recognizes `char`, `bool`, `usize`, `isize`, and `str` by name, and the numeric
primitives by shape: `i`, `u`, or `f` followed only by digits. The shape rule over-matches, as Known
issues records. `PathElement` emits itself through `ToTokens`, delegating to the symbol or the type,
and implements the internal `ToType` trait. Its `span()` returns the segment's source span (the
type's own span, or the symbol's parse-time span), which `delegate_components!` joins across a path
to aim an [error span](../entrypoints/delegate_components.md#error-spans) at an `@`-path key.

## `UniPath`

`UniPath` is a single, non-branching `@`-path: the type `Path!` parses into, and the value side of a
`=>` redirect. Its `Parse` impl consumes a leading `@` and then a dot-separated, non-empty run of
`PathElement`s through `parse_separated_nonempty`, so a body without the `@` or without segments is
rejected. Its `ToTokens` right-folds the segments onto `Nil`:

```rust
// @app.error.ErrorRaiserComponent folds to
PathCons<Symbol!("app"), PathCons<Symbol!("error"), PathCons<ErrorRaiserComponent, Nil>>>
```

Two helpers build paths the macros need. `append_type` pushes a trailing named segment, which is how
a [`#[prefix(@bar.baz in Ns)]`](attributes/prefix.md) attribute appends the component name to its
path before the fold. `to_prefix` converts the path into a `PrefixPath` with a chosen suffix. The
component's `RedirectLookup` impl also builds a `UniPath` directly, from the trait's type
parameters, to form the `PathCons<Shape, Nil>` it concatenates onto a lookup path. `PathCons` and
`Nil` come from the
[export markers](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/exports.rs).

## `PrefixPath`

`PrefixPath` is a `UniPath` whose chain ends in a chosen type instead of `Nil`. It holds the segment
list and a `suffix: Type`, and its `ToTokens` folds the segments onto the suffix. Both of its uses
pass the reserved wildcard `__Wildcard__`, a generic parameter of the generated impl, as the suffix,
which leaves the tail of the path open for a lookup to fill:

- an `@`-path key in `delegate_components!` or `cgp_namespace!`, so `@app.Foo: P` is keyed on
  `PathCons<Symbol!("app"), PathCons<Foo, __Wildcard__>>` and matches every longer path beneath it;
- a `=>` redirect whose key is itself an `@`-path, such as `@cgp.core.error => @app`, which
  redirects a whole branch: the value becomes
  `RedirectLookup<Table, PathCons<Symbol!("app"), __Wildcard__>>`, so the rest of the looked-up path
  carries over. A redirect from a plain key, such as `C => @C`, uses the `Nil`-terminated `UniPath`
  instead.

## `PathHead` and `PathElementWithGenerics`

`PathHead` parses the branching path grammar of an `@`-path key, which `Path!` does not accept. It
is a recursive enum with four variants: `Type` (one segment followed by the rest of the path),
`Group` (a bracketed list of alternative segments sharing the rest of the path), `Nested` (a braced
list of alternative whole tails, which ends the path), and `End`. Its `into_paths` walks the tree
into the cartesian product of every alternative, returning one `(ImplGenerics, UniPath)` pair per
concrete path. Each segment is a `PathElementWithGenerics`, a `PathElement` with an optional leading
generic list, so a segment such as `<T> Wrapper<T>` can introduce a parameter; `into_paths` merges
each segment's generics into the pair it contributes to. The grammar and its combination rules are
described in
[entrypoints/delegate_components.md](../entrypoints/delegate_components.md#behavior-and-corner-cases).

## `UniPathOrType` and `PathHeadOrType`

`UniPathOrType` decides by peeking for a leading `@` whether an input is a `UniPath` or a plain
`Type`; [`#[default_impl]`](attributes/default_impl.md) parses its key with it, so a default
registers under either a component name or a namespace path. `PathHeadOrType` is the same
disambiguation for a `PathHead`, but no macro uses it.

## Known issues

`is_primitive_type` accepts any identifier of `i`, `u`, or `f` followed by zero or more digits, so
the bare `i`, `u`, and `f`, and names such as `u2` or `i7` that are not Rust primitives, stay named
types instead of becoming symbols. `@app.f` therefore lowers its second segment to a type `f`, which
fails to compile unless such a type is in scope. Every `@`-path shares the defect, since they all
parse through `PathElement`. The fix is to match only Rust's primitive names; the user-visible side
is in [reference/macros/path.md](../../reference/macros/path.md#known-issues).

`PathHeadOrType` is dead code: nothing constructs or parses it.

## Tests

`Path!` is rarely written directly, so the stack is exercised mainly through the constructs that
reuse it.

- [namespaces/path_macro.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/path_macro.rs)
  asserts by type equality that `Path!` classifies lowercase, capitalized, and primitive segments
  and ends the chain in `Nil`.
- [namespaces/redirect_lookup.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/redirect_lookup.rs)
  pins, through a `snapshot_cgp_component!` golden, the chain a
  `#[prefix(@bar.baz in DefaultNamespace)]` attribute builds with `append_type`.
- [namespaces/namespace_symbol_path.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/namespace_symbol_path.rs)
  and
  [namespaces/namespace_type_path.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/namespace_type_path.rs)
  exercise the symbol and type classification of a leading segment.
- [namespaces/namespace_group.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/namespace_group.rs)
  and
  [namespaces/combined_forms.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/namespaces/combined_forms.rs)
  pin `PathHead`'s bracketed and braced groups and a per-segment generic, expanded into `PrefixPath`
  keys.

## Source

- The stack lives in
  [cgp-macro-core/src/types/path/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/path/):
  - `PathElement` and `is_primitive_type` in `path_element.rs`;
  - `UniPath` in `unipath.rs` and `PrefixPath` in `prefix.rs`;
  - `PathHead` in `path_head.rs` and `PathElementWithGenerics` in `path_element_with_generics.rs`;
  - `UniPathOrType` in `unipath_or_type.rs` and `PathHeadOrType` in `path_head_or_type.rs`.
- The runtime list `PathCons` is defined in
  [cgp-base-types](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/path.rs).
