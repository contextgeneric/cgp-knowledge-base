# `Symbol!`

`Symbol!("...")` turns a string literal into a type-level string: a distinct type, with no runtime
value, that CGP uses to name a field so the name can be matched at compile time.

## Purpose

`Symbol!` exists because CGP needs field names to be types. The core field-access trait,
[`HasField`](../traits/has_field.md), is parameterized by a `Tag` type that identifies the field
being read, so reading a field called `name` needs a type that stands for the string `"name"`.
`Symbol!("name")` is that type. Its identity is the character sequence it encodes, so two `Symbol!`s
with the same string are the same type and two with different strings are different types.

Encoding names as types lets field access take part in trait resolution. A context can carry a
`HasField<Symbol!("width")>` impl beside a `HasField<Symbol!("height")>` impl, and the compiler
picks the right one from the tag alone. The same device drives
[`#[implicit]`](../attributes/implicit.md) arguments, [`#[cgp_auto_getter]`](cgp_auto_getter.md),
`UseField<Symbol!("...")>`, and the `Field<Symbol!("..."), Value>` entries of a struct's
[`HasFields`](../traits/has_fields.md) representation. Wherever a name must be matched at compile
time, it appears as a `Symbol!`.

A type-level string is distinct from the type-level number used for tuple fields. An unnamed
tuple-struct field has no name, so [`#[derive(HasField)]`](../derives/derive_has_field.md) tags it
with [`Index`](../types/index.md) instead: `Index<0>`, `Index<1>`, and so on. A field is keyed by
`Symbol!` when it has a name and by `Index` when it has only a position.

## Syntax

The macro takes a single string literal and is used wherever a type is expected, such as a trait
bound, an associated type, or a `PhantomData` tag:

```rust
Symbol!("name")
Symbol!("first_name")
Symbol!("")
```

Any string literal is accepted, including the empty string and multi-byte Unicode such as
`Symbol!("世界")`. The parser reads a `LitStr` and keeps its value, so a raw string or an escape
spells the characters it denotes: `Symbol!(r"raw")` is `Symbol!("raw")`, and `Symbol!("a\nb")`
holds a newline. A byte string, a C string, or an identifier fails with `expected string literal`,
and a second token after the literal fails with `unexpected token`. The most common place to see
one is a `HasField` bound, as in `HasField<Symbol!("name"), Value = String>`.

The macro takes the literal verbatim. A field declared as the raw identifier `r#type` is tagged
`Symbol!("type")` by the derives, which strip the `r#`, so `Symbol!("type")` is the tag that
addresses it.

## Syntax Grammar

The input is a single string literal:

```ebnf
SymbolInput -> STRING_LITERAL
```

`STRING_LITERAL` is the Rust string-literal token, raw strings included, so any string literal is
accepted and nothing may follow it.

## Expansion

`Symbol!("...")` expands to the `Symbol` type wrapping a `Chars` chain that spells the string one
character at a time:

```rust
// before
Symbol!("abc")
```

```rust
// after
Symbol<3, Chars<'a', Chars<'b', Chars<'c', Nil>>>>
```

Two type constructors from `cgp-base-types` build this.
[`Chars<const CHAR: char, Tail>`](../types/chars.md) pairs one character with the rest of the
string; chained through `Tail` and ending in `Nil`, it forms a type-level character list, the
analogue of [`Cons`](../types/cons.md)/`Nil` with a `const char` head instead of a type.
`Symbol<const LEN: usize, Chars>` wraps that list together with the string's length. The macro folds
the characters from right to left onto `Nil` and wraps the result, so the empty string becomes
`Symbol<0, Nil>`.

The `LEN` parameter works around a limit of stable Rust, which cannot compute the length of a
`Chars` chain in a const-generic context. The macro precomputes the length and stores it as its own
parameter, so length-dependent code reads it from the type instead of recursing through the list.
`LEN` is the byte length, `str::len()`, not the character count: `Symbol!("abc")` records `3`, and
`Symbol!("世界")` records `6` while its list has two `Chars` nodes, one per Unicode scalar value.

## Examples

`Symbol!` most often appears as the tag in a `HasField` bound. This function reads a `name` field
from any context that has one:

```rust
use cgp::prelude::*;

fn print_name<Context>(context: &Context)
where
    Context: HasField<Symbol!("name"), Value = String>,
{
    println!("{}", context.get_field(PhantomData::<Symbol!("name")>));
}
```

An [`#[implicit]`](../attributes/implicit.md) argument named `name` generates exactly this bound and
read, which is why idiomatic providers rarely spell the tag out.

The one place a reader routinely writes the macro is a wiring entry that points a
[`#[cgp_getter]`](cgp_getter.md) at a field whose name differs from the method's:

```rust
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
```

So write `Symbol!` by hand when the field name is a wiring decision, with
[`UseField`](../providers/use_field.md), and let `#[implicit]`, `#[cgp_auto_getter]`, and the derives
generate it everywhere else. Use `Index` for a tuple field rather than a `Symbol!("0")`, which is a
different type.

A type-level string can also be constructed and printed, because `Symbol` implements `Default` and
`Display`, reconstructing the string from the `Chars` chain:

```rust
let s = <Symbol!("hello")>::default();
assert_eq!(s.to_string(), "hello");
```

The same text is a constant through [`StaticString`](../traits/static_format.md), imported from
`cgp::core::field::traits`: `<Symbol!("hello") as StaticString>::VALUE` is `"hello"`. That trait is
what `LEN` exists for, since it decodes the characters into a `[u8; LEN]` buffer at compile time.

## Related constructs

These constructs are the ones `Symbol!` works with:

- [`Index`](../types/index.md): the position tag for tuple-struct fields, the other half of CGP's
  field-tagging scheme.
- [`HasField`](../traits/has_field.md) and [`HasFields`](../traits/has_fields.md): consume the tags,
  for single-field access and in the `Field<Tag, Value>` entries of a whole shape.
- [`Chars`](../types/chars.md): the character list inside a `Symbol`, a specialized form of the
  [`Product!`](product.md) list.
- [`#[cgp_auto_getter]`](cgp_auto_getter.md), [`UseField`](../providers/use_field.md), and
  [`#[implicit]`](../attributes/implicit.md): the getters that key on a `Symbol!` tag.
- [`Sum!`](sum.md): where an enum's variant names appear as `Symbol!` tags.
- [`StaticFormat`](../traits/static_format.md): the trait behind `Symbol`'s `Display`, which turns
  the type back into a string.

## Known issues

These corner cases report themselves in ways that do not name the cause:

- **Two spellings of one field are unrelated tags.** `Symbol!("first_name")` and
  `Symbol!("firstName")` are different types, so a mismatch reports as a missing `HasField` bound
  rather than as a typo.
- **The tag is a type, not a value.** `let tag = Symbol!("name");` parses the expanded
  `Symbol<4, Chars<…>>` as a comparison chain and fails with
  ``macro expansion ignores `,` and any tokens following``, then an `E0369` about `<` and an `E0308`
  about a struct constructor. The tag is passed as `PhantomData::<Symbol!("name")>`.
- **An error prints the expanded tag.** A missing field is reported against
  `HasField<Symbol<5, Chars<'w', Chars<'i', …>>>>`, which spells `width` one character at a time;
  [`cargo cgp check`](../cargo-cgp.md) names the field directly.

## Source

- Entry point: `Symbol` in
  [crates/macros/cgp-macro-lib/src/symbol.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/symbol.rs),
  which forwards to the `Symbol` construct in
  [crates/macros/cgp-macro-core/src/types/field/symbol.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/field/symbol.rs);
  its `ToTokens` impl right-folds the characters, computes `LEN` from `str::len()`, and wraps the
  result in `Symbol`.
- Runtime types:
  [crates/core/cgp-base-types/src/types/symbol.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/symbol.rs)
  (`Symbol<const LEN: usize, Chars>`) and
  [crates/core/cgp-base-types/src/types/chars.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/chars.rs)
  (`Chars<const CHAR: char, Tail>`), with `Nil` in
  [crates/core/cgp-base-types/src/types/nil.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-base-types/src/types/nil.rs).
- Internal walkthrough (the parse-and-emit pipeline, the character fold and the `LEN` workaround,
  and the index of tests):
  [implementation/entrypoints/symbol.md](../../implementation/entrypoints/symbol.md).
