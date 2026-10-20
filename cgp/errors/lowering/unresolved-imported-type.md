# Unresolved imported abstract type

A `#[use_type]` import names an associated type the owning trait does not declare, so the macro
rewrites the bare alias into a `<Self as Trait>::WrongName` path that resolves to nothing and the
compiler rejects it with `E0576`.

## What triggers it

This class is a *lowering* failure, not a wiring one: the mistake is a misnamed associated type in
the `#[use_type]` attribute itself, which the macro cannot validate at expansion time. `#[use_type]`
works by textual substitution: it rewrites every bare use of an imported alias into
`<Context as Trait>::Assoc`, and it has no knowledge of which associated types the trait actually
declares. So an alias that names a nonexistent associated type is lowered faithfully into a
qualified path, and only the compiler, resolving that path, discovers the name is not there.

The canonical case is a typo in the imported type name:

```rust
#[cgp_type]
pub trait HasScalarType {
    type Scalar;
}

#[cgp_fn]
#[use_type(HasScalarType.Scalr)] // typo: the trait declares `Scalar`, not `Scalr`
pub fn get_scalar(&self) -> Scalr {
    todo!()
}
```

The import declares the alias `Scalr`, so the bare `Scalr` in the return type is rewritten to
`<Self as HasScalarType>::Scalr`, which names an associated type `HasScalarType` never declares. The
same failure arises from a stale name after a trait rename, or from importing an item that lives on
a different trait than the one named. CGP is working as designed here: it cannot see the trait's
item list during expansion, so it lowers the name literally and defers to the compiler: an
[acceptable failure](../../implementation/AGENTS.md), not a defect.

## The raw diagnostic

This section describes what plain `cargo check` prints, the fallback when `cargo-cgp` is not on
hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers the readable form. This
is a **surfaced** class with the simplest diagnostic in the catalog: a single
[`E0576`](../error_codes/e0576.md), "cannot find associated type `Scalr` in trait `HasScalarType`",
with the caret on the offending name. Because the substitution copies the *span* of the identifier
the user wrote onto the rewritten path, the caret lands on the `Scalr` in the user's signature (the
token they actually typed) rather than on the `#[use_type]` attribute or the whole macro block. When
a similarly named item exists, `rustc` adds a "similarly named associated type `Scalar` defined
here" note pointing at the trait's real declaration and a `help:` that suggests the correct spelling
inline. There is no note chain, no CGP scaffolding, and no `IsProviderFor`/`DelegateComponent`
frame, because the failure is caught during name resolution, before any bound is evaluated.

## Where the root cause is

The root cause is **present and is the entire diagnostic**: the primary `E0576` names both the
missing associated type and the trait it was sought in, and the caret points at a token that carries
the misspelled name. This is the opposite of the hidden and cascading classes: nothing is
suppressed, nothing is buried, and there is no verbosity to wade through. The CGP-specific fact the
message does not state is that the name came from a `#[use_type]` import, and that fact decides the
fix: the misspelling is in the attribute, while the caret sits on the alias in the signature.

The `help:` misleads for the same reason. It suggests the correct spelling at the caret, so applying
it changes the signature to `Scalar` while the attribute still imports `Scalr`. Nothing then declares
the bare `Scalar`, and the compiler reports an `E0425`, "cannot find type `Scalar` in this scope". A
reader must follow the alias back to the attribute and correct it there.

## How cargo-cgp presents it

`cargo-cgp` keeps the compiler's header and notes, which already name the missing associated type,
its trait, and the similar one the trait declares, and replaces the misleading `help:` with one
naming the edit that compiles:
``rename `Scalr` to `Scalar` in the `#[use_type]` import from `HasScalarType` and in each use of `Scalr` ``,
without the last clause when the import gives an `as` alias of its own
(`#[use_type(HasScalarType.{Scalr as Value})]`). No `[CGP-Exxx]` code is stamped, since the header
is the compiler's; the change is one of the tool's
[uncoded rewrites](../../../cargo-cgp/error-code.md#uncoded-rewrites).

The tool confirms the import before it changes anything. The `E0576` comes from name resolution, so
the tool holds it until resolution is over, then requires the caret to sit in an item a CGP macro
generated, with the name written bare there, and the trait to declare an associated type the name is
a slip of. A qualified path the program wrote itself, `<Self as HasScalarType>::Scalr`, is respelled
where it stands, so the compiler's help is right for it and stays.

The codes cargo-cgp stamps on the classes it does rewrite are defined in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md).

## Resolving it

Correct the imported name so it matches an associated type the trait declares: change
`#[use_type(HasScalarType.Scalr)]` and every use of the alias to `Scalar`, or use an `as` clause
(`#[use_type(HasScalarType.{Scalar as Scalr})]`) if the short local name was intended. The `help:`
names the correct spelling but applies it only to the signature, so make the same change in the
attribute (`cargo-cgp`'s help names both edits). If the type genuinely lives on a different trait, point the import at that trait
instead.

## What this class does *not* cover

An unresolvable *context* is not a member of this class, because it never reaches the compiler. Two
imports whose `in Context` clauses reference each other (`#[use_type(HasA.A in B, HasB.B in A)]`)
leave grounding no order in which to resolve them, and `#[use_type]` rejects that arrangement at
macro time with a spanned error naming the cycle. The distinction is the catalog's dividing line: a
misnamed associated type is a name only the compiler can check, since the macro cannot see a trait's
item list during expansion, whereas a cyclic context is decidable from the import list alone. So the
two look alike in the source and are caught in different phases. The macro-time rejection is a
[`#[use_type]`](../../reference/attributes/use_type.md#expansion) behavior rather than a
post-codegen error class, and its mechanics are in the
[implementation document](../../implementation/asts/attributes/use_type.md#ground_specs).

## Backing fixtures

- [`lowering/unresolved-imported-type/use_type_unknown_assoc.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/unresolved-imported-type/use_type_unknown_assoc.rs):
  a `#[cgp_fn]` importing `HasScalarType.Scalr` where the trait declares `Scalar`; its
  `.rust.stderr` pins the `E0576` with the caret on the `Scalr` in the signature and the "similarly
  named associated type" `help:`, doubling as a guard that the substitution preserves the user's
  identifier span, and its `.cgp.stderr` replaces that `help:` with the rename in the import and in
  each use of the alias.
- [`lowering/unresolved-imported-type/use_type_unknown_assoc_alias.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/unresolved-imported-type/use_type_unknown_assoc_alias.rs):
  the same misspelling under an `as` alias, `#[use_type(HasScalarType.{Scalr as Value})]`, whose
  help renames the import alone.
- [`lowering/unresolved-imported-type/qualified_path_unknown_assoc.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/unresolved-imported-type/qualified_path_unknown_assoc.rs):
  a qualified path the program wrote itself in a `#[cgp_fn]`, `<Self as HasScalarType>::Scalr`,
  whose compiler `help:` respells it in place and is kept.

## Related

- [`#[use_type]`](../../reference/attributes/use_type.md) and
  [`#[cgp_type]`](../../reference/macros/cgp_type.md): the import attribute whose textual
  substitution produces the unresolved path, and the macro defining the abstract-type trait it
  imports from.
- [Ill-formed generated type](ill-formed-generated-type.md): the sibling lowering class, where the
  generated type is *resolvable* but not well-formed (an unsized type) rather than unresolvable by
  name.
- [Undeclared dependency](undeclared-dependency.md): the sibling class where the import is missing
  rather than misspelled, so `Self::Error` or a bare `Error` names a type no bound declares.
- [`E0576`](../error_codes/e0576.md): the Rust error code this class is reported under.
- [Debugging CGP compile errors](../../guides/debugging.md): the prescriptive playbook this catalog
  supports.
