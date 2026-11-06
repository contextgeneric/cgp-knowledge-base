# Resugaring

CGP's type-level macros compile to deeply nested types, so a programmer writes `Symbol!("height")`
and the compiler talks back about `Symbol<6, Chars<'h', Chars<'e', …>>>`. Resugaring reverses each
expansion, so every construct cargo-cgp shows is spelled as the programmer wrote it. Three
implementations exist because there are three different inputs, and this document is their one
specification: a change to what a construct resugars to, or to what counts as an exact match,
belongs in all three at once.

The expanded form does more than look bad: it hides the fact the reader needs. A missing-field error
exists to name the field, and a `Chars` chain buries that name, worse when rustc elides part of it,
which is why the driver also
[injects `--verbose`](rustc-diagnostic-internals.md#the-suppression-points).

**A resugaring must never lie, and that shapes every rule below.** Showing `Symbol!("height")` is a
claim about what the program wrote, and a reader shown a construct that was never in the source will
go looking for it. So every transform matches **exactly or declines**, leaving the raw type in
place.

## The three approaches

Each works over a different representation of the same construct, and no two share an input, so no
two can share a matcher:

| | Typed | Text | Syntax tree |
|---|---|---|---|
| **Input** | interned `Ty<'tcx>` | rendered diagnostic string | re-parsed printed source |
| **Identity available** | `DefId` (the defining crate) | name only | name only |
| **Structure available** | the type itself | none; parsed by hand | the `syn` tree |
| **Output form** | a string | a string | a syntax node |
| **May live outside `rustc_private`** | no | yes | yes |

### Typed: `Ty<'tcx>` inside the resolver

[`render_ty`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/label/render_ty.rs)
and
[`decode_symbol`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/query/cgp_item/spine.rs)
serve every label and leaf the [typed resolver](typed-resolution/overview.md) produces. **Identity
is its asset:** every cell is checked by `DefId` against the crate that defines it, so a type merely
spelled `Cons` elsewhere is never resugared, and the rules need only describe the shape. It alone
reads a `Symbol!` character exactly, from the const argument's valtree, and sees a placeholder as
such. It must link the compiler, so its coverage comes from UI fixtures.

### Text: `&str` in the rustc-free crate

The
[`postprocess`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/postprocess)
chain runs over each diagnostic in a crate that uses CGP
([what it may change](error-processing.md#where-post-processing-sits-in-the-pipeline)). It exists
because **by then the types are gone**: rustc records no mapping from a substring of a message back
to the `Ty` it was printed from, though the compiler is still in the process.

So it needs two kinds of machinery the typed pass does not:

- **Structural parsing by hand:** balancing nesting to find a cell's head and tail, skipping string
  literals, and tolerating rustc's line breaks.
- **Name-collision defence:** with no `DefId`, the list pass must check a cell name stands alone, or
  the `Cons<` at the end of `PathCons<` would read as a list cell.

rustc also
[shreds a message into styled fragments](error-processing.md#how-the-driver-applies-the-transforms),
a hazard this approach alone has. In return, each transform is a pure function, so the whole catalog
of cases runs as library tests.

### Syntax tree: `syn::Type` in the expand command

[`cargo-cgp-expand`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-expand)
resugars a whole printed crate for
[`cargo cgp expand`](expand-command.md#the-rustc-free-resugaring). It cannot reuse the typed pass,
since the expanded AST is pre-resolution, with no `DefId`s or `Ty`s.

**It cannot reuse the text pass either, a measured result rather than a preference.** On printed
source the text matchers are formatting-sensitive: `prettyplease` breaks a long generic list and
ends it with a trailing comma before the `>`, which the `Symbol!` matcher's final check rejects. On
a rectangle example they resugar `width` and leave `height` raw, purely because the longer name
wraps.

These demands are specific to it:

- **Its output is a syntax node,** a macro-call type the printer formats.
- **Each pass folds a list outermost-first,** then recurses into the elements it collected. A
  visitor recurses innermost-first, and folding an inner cell first leaves `Cons<A, Product![B]>`.
- **It ends with a narrow text pass over printing.** The printer lays a macro body out token by
  token, so it prints `Product![Multiply < Symbol!("foo") >]`, and breaks each brace body onto
  lines. That pass only removes whitespace inside the bodies of the macros the crate emits, keeping
  the space after a `Struct!` field's `:`, so it cannot alter meaning.

## The rules every resugaring follows

**Match exactly or decline.** An inference placeholder mid-list, a wrong terminator, or a same-named
foreign type all leave the raw type. Declining is a normal outcome.

**The order is fixed, because the transforms read each other's output:** the module strip, then
`Symbol!`, whose output `Path!` reads as a segment and the list pass reads as a `Field`'s tag, then
`Path!`, then the lists.

**`Nil` terminates three different lists, so the passes stay separate.** It ends a `Symbol`'s
characters, a `PathCons` path, and a `Cons` list. A pass that rewrites a bare `Nil` before the
enclosing construct is examined destroys the match: one combined visitor turns a `Symbol`'s
terminator into `Product![]`, and every field name silently stays raw. So no implementation may fold
them into one traversal.

**Every form shown is one the programmer could have written,** in a diagnostic and in source alike.
The test case is an **open-ended path**, ending in a generic "rest of path" parameter rather than
`Nil`, as every `@`-path key does through the reserved `__Wildcard__`. No `Path!` spelling names
that type, since `Path!(@foo.bar)` is the closed path. So the `Path!(…)` form declines on an open
tail, and the list stays raw with its segments resugared. A message the tool rewrites names a key
rather than a type, so there the tail is left out, as the entry wrote it.

**An empty list is written `Product![]` only where its type is known.** The typed pass writes a
standalone CGP `Nil` as `Product![]` and `Void` as `Sum![]`, leaving the `Nil` that ends a spine or
a variant's unit payload, so a `Struct!` field of an empty list reads `Product![]` there. The others
see only the name, which a program may give its own type, so a bare `Nil` stays, and their folds need
a first cell.

## The resugarings

Each construct below is one transform in each implementation that owns it.

### `Symbol!`: the type-level string

`Symbol!` encodes a string as a type so it can key a trait, which is how every CGP field name
travels ([`Symbol!` reference](../../cgp/reference/macros/symbol.md)). A getter declares the fields
it reads:

```rust
#[cgp_auto_getter]
pub trait HasRectangleFields {
    fn width(&self) -> f64;
    fn height(&self) -> f64;
}
```

and its generated blanket impl requires `HasField<Symbol!("height")>` on the context. What the
compiler holds, and prints, is the expansion, a byte length and a right-folded character list closed
by `Nil`:

```text
Symbol<6, Chars<'h', Chars<'e', Chars<'i', Chars<'g', Chars<'h', Chars<'t', Nil>>>>>>>
```

Resugaring reverses it to `Symbol!("height")`, and in a message the tool constructs itself the name
is usually unwrapped further into prose (`` missing field `height` on `Rectangle` ``), since a
root-cause lead reads better naming the field than the tag type.

The match is exact in three ways, and any of them failing leaves the type as it stands. The
**declared length must equal the decoded string's byte length**, because `Symbol!` bakes in
`str::len()` rather than a character count, so a length that disagrees means this is not a `Symbol!`
expansion. The **list must be `Chars` all the way down to `Nil`**, with nothing else in the chain.
And each `Chars` head must be a **single character**. The text pass alone reads a literal rustc
rendered, so an escaped one (`'\''`) declines there rather than being decoded by guesswork, while the
other two read the character itself. The empty string is a legitimate match: `Symbol<0, Nil>` resugars
to `Symbol!("")`.

The typed implementation is `decode_symbol`, which additionally checks `Symbol`, `Chars`, and `Nil`
by `DefId` against `cgp-base-types` and reads each character out of the const argument's valtree;
the text implementation is
[`resugar_symbol`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/resugar_symbol.rs).

### `Path!`: the type-level path

`Path!` encodes a routing path as a type-level list, which is what a namespace or an `open`
statement dispatches on ([`Path!` reference](../../cgp/reference/macros/path.md)). A context that
dispatches one component per encoded type writes:

```rust
delegate_components! {
    App {
        open ItemEncoderComponent;

        @ItemEncoderComponent.Vec<u8>: EncodeHex,
    }
}
```

The wiring key that entry generates is a `PathCons` chain, which shows up in a coherence
conflict or a missing-wiring leaf:

```text
PathCons<ItemEncoderComponent, PathCons<Vec<u8>, Nil>>
```

Resugaring reverses it to the path the programmer wrote, `@ItemEncoderComponent.Vec<u8>`. **Which of
two forms it renders is chosen by the caller**, through `resugar_path`'s `wrap` parameter: a message
the tool *constructs* (a coded header, a root-cause note) wants the bare `@…`, because there it
reads as a path the sentence names; a message the tool merely *cleaned up* wants the macro form
`Path!(@ItemEncoderComponent.Vec<u8>)`, because there a raw type is being shown back in source form.
The emitter passes `wrap` accordingly, bare on a rewrite and wrapped on a fallback.

Segments are rendered back the way `Path!` classifies them going forward, which makes the
round trip faithful. `Path!` turns a lowercase, non-primitive identifier into a `Symbol` and keeps
every other segment verbatim as a named type, so resugaring unwraps a `Symbol!("app")` head to the
bare segment `app` only when `app` is such an identifier, and renders every other head verbatim: a
capitalized component marker, a primitive like `u32`, or a compound value type an `open` statement
dispatches on (`Vec<u8>`, `&Coord`, `DateTime<Utc>`). A namespace path therefore reads as written:

```text
PathCons<Symbol!("app"), PathCons<GreeterComponent, Nil>>   →   @app.GreeterComponent
```

A segment qualified only inside its arguments (`Wrap<a::Item>`) is an ordinary compound type, whose
head decides. A **module-qualified** segment is rendered as written, since `Path!` parses each
segment as a type: `PathCons<ErrorRaiserComponent, PathCons<std::io::Error, Nil>>` reads
`@ErrorRaiserComponent.std::io::Error`. The [path strip](#the-path-strips-that-run-first) runs first
and keeps a qualifier only where it tells two types apart, so the one that reaches this pass is
meaningful, and dropping it would make `std::io::Error` read as any other `Error`. The exception is a
key in a code an `E0207` or `E0210` carries, `CGP-E017`, `CGP-E018`, `CGP-E019`, or `CGP-E022`, whose
types [print by their own names](driver/diagnostic-reshapes.md), so it reads `@ErrorRaiserComponent.Error`
([`entry_generic_qualified_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/entry_generic_qualified_key.rs)). Two segment
shapes decline, leaving the whole list raw rather than risking a mangled path: a qualified segment
that is not a plain type path (a lowercase tail, generics), and a **bare lowercase identifier**,
which `Path!` would have encoded as a `Symbol`, so meeting one as a plain type is ambiguous. A
`Symbol!` head that is not a lowercase, non-primitive identifier declines too, in all three passes,
since no bare segment spells it. The typed pass holds the type itself, so it prints a qualified
segment with generics or a lowercase tail rather than declining on its name.

One non-`Nil` tail is treated apart. An **open-ended path** ends in the macros' generic "rest of
path" parameter instead of `Nil`, which rustc prints as the inference placeholder `_`, the shape
that appears in the conflicting-wiring `E0119` blocks over a duplicated `@`-path key. The bare form
a rewritten message uses names the key, so it leaves the tail out, while the `Path!(…)` form
declines, since `Path!(@foo.bar)` would be the closed path:

```text
PathCons<Symbol!("foo"), PathCons<Symbol!("bar"), _>>   →   @foo.bar           (a rewritten message)
PathCons<Symbol!("foo"), PathCons<Symbol!("bar"), _>>   →   unchanged          (the `Path!(…)` form)
```

Only a bare `_` is an open tail, since `_` is never a concrete segment; any other non-`Nil` tail
declines in both forms.

The text implementation is
[`resugar_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/resugar_path.rs),
which follows the macro's own `is_primitive_type` rule (the real primitive names only) through the
error-processing crate's
[`syntax`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/syntax)
module, as the expand crate does, so a segment classifies alike in a diagnostic and an expansion.

### `Product!` and `Sum!`: the lists

`Product!` and `Sum!` encode a type list and a type sum, the lists behind every field list, variant
list, and handler pipeline ([`Product!`](../../cgp/reference/macros/product.md),
[`Sum!`](../../cgp/reference/macros/sum.md)). A wiring table names one directly:

```rust
delegate_components! {
    App {
        ComputerComponent: PipeHandlers<Product![Multiply<Symbol!("foo")>, Add<Symbol!("bar")>]>,
    }
}
```

Both expand to right-nested lists, a product through `Cons` to `Nil` and a sum through `Either` to
`Void`, and resugaring folds each back to the flat list:

```text
Cons<u64, Cons<String, Nil>>        →   Product![u64, String]
Either<u64, Either<f64, Void>>      →   Sum![u64, f64]
```

The value is highest in a dependency chain, where a recursive provider walks a list one cell at a
time: without resugaring, each hop of the chain restates a slightly shorter list and the reader has
to diff them to see progress; with it, each hop names the list it is working on.

Three details make the match exact. The list must **close on its own terminator** (`Nil` for a
product, `Void` for a sum), so an open-ended or wrongly-terminated list is left alone, and a tail
cell must be the *whole* remaining tail rather than something a trailing token follows. Elements are
**resugared recursively**, so a `Sum!` nested inside a `Product!`, or a `Symbol!` inside an element,
folds in turn. And the text pass takes one precaution the typed pass gets for free from its `DefId`
check: it requires the cell name to stand alone rather than end a longer identifier, so the `Cons<`
at the end of `PathCons<` is never mistaken for a list cell.

The typed implementation is `render_ty`'s `cgp_spine`; the text implementation is
[`resugar_lists`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/resugar_list.rs).

### `Struct!` and `Enum!`: a list of fields

When every element of a list is a `Field` cell, the list is not really a list to the reader: it is
a record or a variant set, and resugaring folds it one step further, to CGP's
[`Struct!`](../../cgp/reference/macros/struct.md) or [`Enum!`](../../cgp/reference/macros/enum.md)
shape. This is the shape `#[derive(HasFields)]` produces:

```rust
#[derive(HasFields)]
pub struct Rectangle {
    pub width: f64,
    pub height: f64,
}
```

whose `Fields` associated type is a product of `Field` cells, each pairing a `Symbol!` name tag
(or, for a tuple struct, an `Index<N>` position tag) with the field's type. Each macro expands to
exactly the `Fields` the derive gives the same body, so the fold is the macro's expansion reversed:

```text
Cons<Field<Symbol!("width"), f64>, Cons<Field<Symbol!("height"), f64>, Nil>>
    →   Struct! { width: f64, height: f64 }

Cons<Field<Index<0>, u64>, Cons<Field<Index<1>, String>, Nil>>
    →   Struct!(u64, String)

Either<Field<Symbol!("Rect"), u64>, Either<Field<Symbol!("Circle"), f64>, Void>>
    →   Enum! { Rect(u64), Circle(f64) }
```

The shapes are worth folding to because the list form is unreadable: a real record provider's
chain hop otherwise names a chain of `Field` cells several fields long, where
`Struct! { message_id: u64, date: DateTime<Utc>, … }` says the same thing at a glance. And because
they are real macros, a shape read in a diagnostic or an expansion can be copied back into code.

**A shape is printed only when it has an exact spelling, since the output must parse back to the
same type.** A product folds to `Struct! { a: A, … }` when every tag is a name a struct body can
write, and to `Struct!(A, B, …)` when the tags are `Index<0>`, `Index<1>`, … in order with at least
two cells. Several lists have no such spelling and keep their `Product!` form:

- **A single `Index` cell:** `Struct!(T)` is the bare `T` by the derive's newtype rule, so
  `Cons<Field<Index<0>, T>, Nil>` stays `Product![Field<Index<0>, T>]`.
- **Positions out of order or with a gap,** and a list that **mixes** name and position tags.
- **A name that is not an identifier,** such as a hand-written `Symbol!("foo bar")`. A keyword is
  writable raw, so a `Symbol!("type")` tag prints as `r#type`, which `Struct!` tags by its logical
  name; `self`, `Self`, `super`, `crate`, and `_` cannot be written even raw.
- **Any element that is not a `Field` cell,** since a half-record form would misrepresent the list.

A sum folds to `Enum!` when every tag is a writable name; a variant cannot be named by a position.

**Each variant takes the shortest of its equivalent spellings.** An `Enum!` variant's fields are
encoded by the `Struct!` rules, so several spellings name the same payload, and the fold picks the
one a programmer would write. The payload is resugared first, and then:

- **A `Nil` payload** is a unit variant, `Empty`, rather than `Empty(Nil)`.
- **A payload that folded to `Struct! { … }`** lends the variant its braces: `Rect { w: f64 }`.
- **A payload that folded to `Struct!(…)`** lends the variant its parentheses: `Pair(u8, u16)`.
- **Any other payload** is the single positional field: `Circle(f64)`, or
  `One(Product![Field<Index<0>, u8>])` for a one-element positional list.

Field values are resugared recursively, so a nested record folds in turn.

The rules are written once, in the rustc-free crate's
[`shape`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/shape)
module, which the text and typed passes both call: `render_struct_shape`, `render_enum_shape`, and
`render_variant` take names and already-rendered values, so the two diagnostic passes cannot
disagree on a spelling. The syntax-tree pass applies the same rules to `syn` nodes, and calls the
same writable-name check, `shape_name`.

### The path strips that run first

A path strip is not a resugaring but must run before them, since every rule above matches bare type
names. It also does real work of its own. rustc shortens a path only when the name is unique across
the build and was not brought in by a glob import, so the CGP types a crate imports through
`use cgp::prelude::*` print qualified, and in a message the tool built, or around a construct it
resugared, those qualifiers are noise the reader did not write. A diagnostic the tool otherwise left
alone keeps them, as plain `cargo check` prints them.

The chain's strip,
[`strip_unambiguous_paths`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/strip_modules.rs),
drops the module segments of an `a::b::C` identifier run unless the qualifier tells two types apart.
A module is named in lowercase and a type or trait in uppercase, so the run keeps everything from
its first uppercase segment: a trait's method keeps its trait
(`cgp::prelude::TryComputer::try_compute` reads `TryComputer::try_compute`), and a run with no
uppercase segment keeps its last one. rustc's own rule decides which ones do: a name it prints
qualified is either non-unique or glob-imported, so a qualified name the crate does not glob-import
is ambiguous, and its qualifier stays. A glob-imported name is qualified whether or not it collides,
so the driver also reads which item each glob brings in under the name, and a printed path that is
not one of those items keeps its qualifier: in a crate that glob-imports its own `Error`,
`std::io::Error` stays qualified
([`glob_imported_error_route`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/errors/glob_imported_error_route.rs)).
Each item counts under every path rustc prints for it. rustc prints a parent module by its name
alone when that name is unique, so an item a glob re-exports out of a private module prints from
its nearest uniquely named enclosing module, `add::EvalAdd` for `providers::eval::add::EvalAdd`, and
reads bare
([`glob_reexported_provider_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/glob_reexported_provider_cycle.rs)).
A shorter path that starts at the name of a crate-root item or of a crate is left out, since rustc
prints a path from there for that other item
([`glob_reexported_provider_name_shared`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/glob_reexported_provider_name_shared.rs),
[`glob_imported_error_under_crate_named_module`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/errors/glob_imported_error_under_crate_named_module.rs)).
The driver supplies the glob-imported names from the resolver's `glob_map`, and the items from each
glob `use`'s target module. Reading that module needs the HIR, so only a message the tool rewrote
gets it; an untransformed message, which can arrive during name resolution, treats a glob-imported
name as unambiguous. Two kinds of run always collapse: one rooted at the `cgp` crate, since the
prelude glob is why rustc qualifies it, and one ending in a name of CGP's encoding (`Symbol`,
`Chars`, `Nil`, `Cons`, `Either`, `Void`, `PathCons`, `Field`, `Index`, `HasField`), whichever crate
re-exports it, because the stages after the strip match those names bare. Some of them are ambiguous
(`std::str::Chars`), but in a CGP diagnostic they are the encoding the resugaring folds away:

```text
cgp::prelude::HasErrorType                        →   HasErrorType
app::prelude::Chars                               →   Chars                           (encoding)
finance::QuantityTypeProviderComponent            →   QuantityTypeProviderComponent   (glob-imported)
std::io::Error                                    →   std::io::Error                  (ambiguous)
```

Stripping every qualifier would turn `std::io::Error` beside a crate's `backend::Error` into two
bare `Error`s, which also read as CGP's abstract `Error` type
([`stripped_error_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/errors/stripped_error_path.rs),
[`open_route_stripped_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/errors/open_route_stripped_path.rs)).
[`strip_module_paths`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/strip_modules.rs),
which collapses every run, supplies the form the missing-field check reads a landmark through.

Both scan the ASCII identifier run by byte but copy every other character whole by its UTF-8 width,
so multi-byte text (a rendered dependency tree's `└─`) is never split into invalid bytes. They skip
string literals, so a name inside a `Symbol!("a::b")` is never mangled, and they leave a turbofish,
an associated-type `>::Assoc` tail, and a lone identifier alone. A run right after the word `use`
keeps every segment too, since a `use` statement is code the reader types as written: the
extensible-data `help` that names a method's import
(`` with `use cgp::core::field::impls::CanDowncastFields;` in scope ``) keeps its path
([`downcast_on_remainder`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/downcast_on_remainder.rs)).

The expand command treats these differently from a diagnostic, and deliberately so: it strips the
`cgp::macro_prelude::` qualifier the macros emit, because that is pure noise, but **keeps** general
module qualifiers, because in printed source a qualifier carries information a reader may want (see
[The expand command](expand-command.md#the-rustc-free-resugaring)).

## What is left unresugared

These are deliberate, so nobody adds them as a "missing" transform:

- **An open-ended path** stays raw in source output and an untransformed diagnostic, as above. An
  `open` statement's per-key entry keys on `PathCons<Component, PathCons<Key, __Wildcard__>>`.
- **An empty list** stays as its terminator in those same places, as above.
- **`Index<N>`** needs nothing, since it is the surface form.
- **A `Life<'a>` lift** is decoded rather than resugared: the resolver
  [reads the region back](typed-resolution/anchors.md#the-check-anchors), and the label shows the
  lifetime in its ordinary position.
- **A call-site placeholder** renders as `_`, a rendering decision rather than a resugaring, with a
  tuple rendered element by element so a nested one does too.

## Further reading

The CGP references define each expansion this document reverses, and are the ground truth for
checking a rule: [`Symbol!`](../../cgp/reference/macros/symbol.md),
[`Path!`](../../cgp/reference/macros/path.md), [`Product!`](../../cgp/reference/macros/product.md),
[`Sum!`](../../cgp/reference/macros/sum.md), [`Struct!`](../../cgp/reference/macros/struct.md),
[`Enum!`](../../cgp/reference/macros/enum.md), [`Field`](../../cgp/reference/types/field.md), and
[`HasFields`](../../cgp/reference/traits/has_fields.md).

## Tests

**What is not guarded:** the typed implementation needs the compiler, so no test compares it with
the other two directly, and its agreement rests on the fixtures below and this document. A rule only
it can break is its reading of a path segment, in
[`render_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/query/keys.rs),
which [`qualified_path_segment`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/qualified_path_segment.rs)
pins for a qualifier.

- [`tests/error_processing/postprocess/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/postprocess):
  the text implementations, with every decline above.
- [`tests/error_processing/shape.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/shape.rs):
  the shared spelling rules.
- [`tests/expand/resugar.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-expand/tests/expand/resugar.rs):
  the syntax-tree implementation through the driver's whole pipeline, including both `Nil` overlap
  hazards.
- [`tests/expand/agreement.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-expand/tests/expand/agreement.rs):
  the text and syntax-tree implementations compared on the same constructs.
- Each fixture's `.expand.rs` in the [UI suite](testing.md#three-passes-per-fixture): the
  syntax-tree pass over real macro output, the widest coverage of the three.
- [`base_area_1`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_1.rs),
  [`record_field_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/record_field_chain.rs),
  [`sum_variant_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/sum_variant_chain.rs),
  [`enum_variant_shapes_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/enum_variant_shapes_chain.rs),
  and
  [`unregistered-namespace-path/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/unregistered-namespace-path):
  the typed pass, construct by construct.
- [`fallback_shape_resugar`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/fallback_shape_resugar.rs):
  the text fold on rustc's own rendering.
- [`ok/shape_macros`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/shape_macros.rs):
  `Struct!` and `Enum!` by hand, against the forms the syntax-tree pass prints.

## Source

- [`resolve/label/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/label)
  and
  [`resolve/query/cgp_item/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/query/cgp_item):
  the typed pass, its symbol decode, and its `DefId` anchor.
- [`cargo-cgp-error-processing/src/shape/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/shape):
  the shared `Struct!` and `Enum!` rules.
- [`cargo-cgp-error-processing/src/postprocess/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/postprocess):
  the text passes, one module each.
- [`cargo-cgp-expand/src/resugar/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-expand/src/resugar):
  the syntax-tree passes, one module per construct, with `spacing/` for the post-print pass and
  `file.rs` for the order.
