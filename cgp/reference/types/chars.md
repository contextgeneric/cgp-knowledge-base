# `Chars` and `Symbol`

`Chars<const CHAR: char, Tail>` is a type-level character list, and
`Symbol<const LEN: usize, Chars>` wraps such a list with the string's byte length; together they are
CGP's encoding of a string as a type.

## Purpose

`Chars` and `Symbol` let a string be a type rather than a value, which is what lets a field name
take part in trait resolution. CGP keys field access by a `Tag` type, so reading a field called
`name` needs a type standing for the string `"name"`, from which the compiler can pick one
`HasField` impl over another. A `Symbol` is that type. Its identity is the character sequence it
encodes, so two symbols built from the same string are the same type and two built from different
strings are different.

The encoding is a list of characters because of a limit of stable Rust: a `String` or `&str` cannot
be a const-generic parameter, but a single `char` can. CGP therefore spells the string out one
character at a time through a recursive `Chars` list, the way a heterogeneous list spells out its
elements through [`Cons`/`Nil`](cons.md). `Chars` is the analogue of `Cons` whose head is a
`const char` rather than a type.

These types are almost never written by hand. The [`Symbol!`](../macros/symbol.md) macro takes a
string literal and folds it into the `Symbol`/`Chars`/`Nil` chain; that document covers the
construction syntax and expansion, and this one covers the runtime types and their traits.

## Definition

`Chars` is a zero-sized struct carrying one character as a const parameter and the rest of the
string as its `Tail`:

```rust
#[derive(Eq, PartialEq, Clone, Copy, Default)]
pub struct Chars<const CHAR: char, Tail>(pub PhantomData<Tail>);
```

The `Tail` is the next `Chars` node, or `Nil` at the end of the string, so a `Chars` chain ending in
`Nil` is a type-level list of characters. The character lives in the const parameter and the tail in
a `PhantomData`, so the whole list is a zero-sized value at runtime.

`Symbol` wraps a `Chars` chain and records the string's byte length as a separate const parameter:

```rust
pub struct Symbol<const LEN: usize, Chars>(pub PhantomData<Chars>);
```

Despite its name, the `Chars` parameter is the whole chain, not a single node. `LEN` is the string's
byte length, `str::len()`. It is stored explicitly because stable Rust cannot compute the length of
a `Chars` chain in a const-generic context, so length-dependent code reads it from the type instead
of recursing. Because it counts bytes, `Symbol!("世界")` records `6`, while its list has two `Chars`
nodes, one per Unicode scalar value.

## Behavior

Both types turn back into their string through the [`StaticFormat`](../traits/static_format.md)
trait, which writes a type-level string into a `Formatter` without needing a value.
`Chars<CHAR, Tail>` writes `CHAR` and recurses into `Tail`, `Nil` ends the recursion by writing
nothing, and `Symbol<LEN, Chars>` forwards to its chain. Each of `Chars` and `Symbol` also
implements `Display` through `StaticFormat`, so `<Symbol!("hello")>::default().to_string()` yields
`"hello"`.

The `LEN` parameter exists for [`StaticString`](../traits/static_format.md), which exposes the
string as a `const VALUE: &'static str` rather than a formatting routine. Its implementation decodes
the `Symbol`'s characters into a `[u8; LEN]` at compile time, and that byte buffer must be sized by
a const. So a reader who needs the string at runtime uses `Display`, and one who needs it as a
constant uses `StaticString::VALUE`.

`Symbol` implements `Default` unconditionally, since it is a zero-sized marker, and nothing else
beyond `StaticFormat` and `Display`. `Default` is what lets a `Symbol!("…")` type be materialized as
a value where one is needed. `Chars` additionally derives `Eq`, `PartialEq`, `Clone`, and `Copy`.

## Examples

A type-level string most often appears as the `Tag` of a [`HasField`](../traits/has_field.md) bound,
naming the field a function or provider reads:

```rust
use cgp::prelude::*;

fn print_name<Context>(context: &Context)
where
    Context: HasField<Symbol!("name"), Value = String>,
{
    println!("{}", context.get_field(PhantomData::<Symbol!("name")>));
}
```

The same type can be constructed and printed, walking the `Chars` chain to rebuild the string:

```rust
use cgp::prelude::*;

let s = <Symbol!("hello")>::default();
assert_eq!(s.to_string(), "hello");
```

An empty string is `Symbol<0, Nil>`: a character list that is only the terminator, and a recorded
length of zero.

## Related constructs

These constructs are the ones `Chars` and `Symbol` relate to:

- [`Cons`/`Nil`](cons.md): the product list `Chars` specializes, with a `const char` head in place
  of a type.
- [`Symbol!`](../macros/symbol.md): the macro that builds a `Symbol`.
- [`StaticFormat`/`StaticString`](../traits/static_format.md): turn a symbol back into a string, for
  display and as a constant.
- [`Index`](index.md): the position tag for tuple fields, the counterpart of a `Symbol` name.
- [`HasField`](../traits/has_field.md) and [`Field`](field.md): match and carry the tags a `Symbol`
  provides, including inside a struct's [`HasFields`](../traits/has_fields.md) representation.
- [`PathCons`](path_cons.md): whose lowercase segments are symbols, built by
  [`Path!`](../macros/path.md).

## Source

- The runtime types are defined in
  [crates/core/cgp-base-types/src/types/chars.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/chars.rs)
  (`Chars<const CHAR: char, Tail>`) and
  [crates/core/cgp-base-types/src/types/symbol.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/symbol.rs)
  (`Symbol<const LEN: usize, Chars>`), with `Nil` in
  [crates/core/cgp-base-types/src/types/nil.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/nil.rs).
- The `StaticFormat` impls behind `Display` are in
  [crates/core/cgp-base-types/src/traits/static_format.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/traits/static_format.rs),
  and the const-decoding `StaticString` impl that uses `LEN` is in
  [crates/core/cgp-field/src/traits/static_string.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/static_string.rs).
- The constructing macro is [`Symbol!`](../macros/symbol.md); its implementation document,
  [implementation/entrypoints/symbol.md](../../implementation/entrypoints/symbol.md), indexes the
  tests.

## Public pages derived from this document

This document feeds the public [`Chars`](https://contextgeneric.dev/docs/reference/types/chars) page
under `types/`. The `Symbol` type it also documents is covered on the
[`Symbol!`](https://contextgeneric.dev/docs/reference/macros/symbol) macro page rather than a page
of its own, so a change to `Symbol` here is propagated there. Both are bound by the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping is recorded in
[website/site-structure.md](../../../website/site-structure.md).
