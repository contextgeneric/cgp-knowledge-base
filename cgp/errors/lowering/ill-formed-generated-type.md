# Ill-formed generated type

A macro lowers a field- or argument-type shorthand over a type it cannot tell is unsized, and the
generated bound names a type that is not well-formed, so the compiler rejects it with `E0277` (the
`Sized` form).

## What triggers it

This class is distinct from every other in the catalog: it is neither a wiring mistake nor a lazy
dependency, but a macro *lowering* that produces a type the compiler cannot accept. CGP's getter and
implicit-argument macros recognize a small set of field-type shorthands (`Option<&T>` for an
optional field, `&[T]` for a slice field, `&str` for a `String` field) and lower each to a
`HasField` bound and an accessor. The `Option<&T>` form reads an `Option<T>` field, and an `Option`
holds only a sized value, so it is well-formed only when `T` is sized.

The macros reject the optional references whose shape shows the referent is unsized:
`Option<&[T]>` and `Option<&dyn Trait>`, with their `&mut` forms, fail at expansion with a message
naming the sized container to read instead (see the
[`#[cgp_auto_getter]` implementation document](../../implementation/entrypoints/cgp_auto_getter.md#behavior-and-corner-cases)).
A type named by a path carries no such mark. Whether `Path`, `OsStr`, `CStr`, or a program's own
dynamically sized struct is sized is known only to the compiler, so the macro lowers an optional
reference to one by the `Option<&T>` rule, and the resulting bound names an ill-formed type that
only the compiler catches:

```rust
#[cgp_auto_getter]
pub trait HasConfigPath {
    fn config_path(&self) -> Option<&Path>;
}
```

The shared `parse_field_type` reads an `Option<Path>` field, so the generated `HasField` bound names
`Option<Path>`. `Path` wraps the unsized `OsStr`, and through it a `[u8]`, so `Option<Path>` is
ill-formed, and the compiler rejects it. The boundary is shared by
[`#[cgp_auto_getter]`](../../reference/macros/cgp_auto_getter.md),
[`#[cgp_getter]`](../../reference/macros/cgp_getter.md), and a
[`#[cgp_fn]`](../../reference/macros/cgp_fn.md)
[`#[implicit]`](../../guides/reading-context-fields.md) argument, since all three lower field types
through `parse_field_type`. Deferring to the compiler is correct here, because the macro lacks the
type information the check needs: an [acceptable failure](../../implementation/writing-guide.md), not a
defect.

## The raw diagnostic

This section describes what plain `cargo check` prints, the fallback when `cargo-cgp` is not on
hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers the readable form. This
is a **surfaced** class, and the root cause is the *primary* error. The compiler reports **`E0277`**
in its dedicated `Sized` form, naming the innermost unsized type rather than the one the user wrote:
"the size for values of type `[u8]` cannot be known at compilation time," with the label "doesn't
have a size known at compile-time." The notes then lead back to the user's type: a `help:` "within
`Path`, the trait `Sized` is not implemented for `[u8]`," a note "required because it appears within
the type `Path`," and a note "required by an implicit `Sized` bound in `Option`," which names
*where* the size is required (the `T` of `Option<T>` carries an implicit `Sized` bound). The caret
lands on the macro attribute (`#[cgp_auto_getter]`), because the offending type is synthesized in
the expansion, and a closing note attributes the error to that attribute macro.

Search for that exact form: rustc special-cases a missing `Sized`, so the headline is not "the trait
bound `[u8]: Sized` is not satisfied", and `Sized` appears only in the `help:`. It is the standard
diagnostic for a
[dynamically sized type](https://doc.rust-lang.org/reference/dynamically-sized-types.html) in a
position that needs a known size.

A second error follows as a consequence. The getter body calls `.as_ref()` on the ill-formed value, so
the compiler adds an **`E0599`**, "the method `as_ref` exists for reference `&Option<Path>`, but its
trait bounds were not satisfied".

## Where the root cause is

The root cause is **present at the top of the output**. The headline names the innermost unsized type
(`[u8]`), so the type the user wrote first appears in the `help:` ("within `Path`") and the note after
it. The raw message does not say that the unsized type came from the `Option<&T>` shorthand reading an
`Option<Path>` field, since the compiler sees only the synthesized type.

## How cargo-cgp presents it

`cargo-cgp` passes this class through unchanged, which gives the fixture `usability` quality: the
cause is present, but the headline names `[u8]` rather than `Path`, the caret points at the attribute
rather than the return type, and the derived `E0599` adds noise. The improvement left is translation:
drop the `E0599`, and read the synthesized `Option<Path>` back to the rule that the `Option<&T>`
shorthand needs a sized `T`.

## Resolving it

Read the sized type that owns the unsized one, so the macro lowers the shorthand to a well-formed
bound: `Option<&PathBuf>` from an `Option<PathBuf>` field rather than `Option<&Path>`, as the
macros' own message names `Option<&Vec<T>>` for `Option<&[T]>`. When the accessor must return the
borrowed form, write the getter by hand: the macros only save boilerplate over a plain `HasField`
impl, so a hand-written impl can return `self.config_path.as_deref()` as an `Option<&Path>`. The
rule to carry away is that the `Option<&T>` shorthand composes only with a sized `T`; the macros
catch the shapes they can see, and the compiler catches the rest.

## Backing fixtures

- [`lowering/ill-formed-generated-type/option_unsized_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/ill-formed-generated-type/option_unsized_path.rs):
  a `#[cgp_auto_getter]` returning `Option<&Path>`, lowered to a `HasField` bound over the unsized
  `Option<Path>`, and passed through.

## Related

- [`#[cgp_auto_getter]`](../../reference/macros/cgp_auto_getter.md),
  [`#[cgp_getter]`](../../reference/macros/cgp_getter.md),
  [`#[cgp_fn]`](../../reference/macros/cgp_fn.md), and
  [reading context fields](../../guides/reading-context-fields.md): the macros whose shared
  `parse_field_type` lowers the shorthands, and the field-type forms they support.
- [`cgp_auto_getter` implementation document](../../implementation/entrypoints/cgp_auto_getter.md):
  the shapes the parser rejects at expansion, and why a path type reaches the compiler instead.
- [`HasField`](../../reference/traits/has_field.md): the trait the generated bound targets, whose
  value type must be `Sized` here.
- [`E0277`](../error_codes/e0277.md) and
  [dynamically sized types](https://doc.rust-lang.org/reference/dynamically-sized-types.html): the
  error-code reference (including the `Sized` special case) and the Rust reference for the size
  requirement the generated type violates.
