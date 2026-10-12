# Hidden root cause

This document catalogs the cases where `cargo-cgp` does not emit enough information to identify the
root cause of an error: the cases where the cause cannot be recovered from the output alone, no
matter how that output is later processed. It is the tool's most important measure of correctness,
because everything else the tool might do to a diagnostic assumes the cause is present to work with.

The test this document applies is *sufficiency*, not readability. `cargo-cgp`'s role is to produce
output from which a downstream consumer (a formatter, an IDE, or an AI agent) can recover the root
cause; how that output is spelled or laid out is a separate concern, handled in
[usability](usability.md). An issue belongs here only when the root cause is genuinely absent from,
or unrecoverable from, `cargo-cgp`'s output, so that no downstream processing of the text could
reconstruct it, and only when a fixture under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui) reproduces it. These
are the cases that justify the tool's compiler-internal foothold: where the ordinary text output has
lost information, only a tool reading the compiler's own state can put it back.

## Two defeated archetypes

The two archetypes this category was first built around are both defeated, each by a flag the
driver injects, so neither hides a cause the output cannot recover. They are recorded so a future
agent recognizes them. Apart from the
[extensible-data failures below](#extensible-data-failures-that-never-name-their-cause), every
post-codegen compile-fail class CGP produces has a fixture under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui) that carries its root
cause in the tool's output. The one class that produces no usable diagnostic under cargo-cgp,
`inheritance_cycle`, does so because the next-gen solver *accepts* it (a missing error, tracked as
a solver caveat in [The driver](../implementation/driver.md#choosing-the-trait-solver)), not
because a cause is suppressed.

The two archetypes are defeated by *different* levers, and the distinction is the useful one to
carry forward. A cause can be hidden because the compiler **never computed it** or because the
compiler computed it and then **elided it while printing**: the first is a trait-solver problem, the
second a diagnostic-printing problem, and they need different flags. Both levers are argument
injections documented in [The error pipeline](../implementation/error-pipeline.md); the printing
side is mapped function-by-function in
[rustc diagnostic internals](../implementation/rustc-diagnostic-internals.md).

### Defeated: a cause the default trait solver never computed

The archetypal hidden failure is a wiring mistake exercised by a direct consumer-method call, where
the compiler reports only that a method's bounds are unsatisfied (`E0599`) without ever naming the
failed dependency. On that path the *default* solver's method-resolution heuristic bottoms out at
the provider trait and does not compute the real missing leaf bound at all, so no amount of text
processing could recover it, since the leaf was never in the diagnostic. `cargo-cgp` defeats this by
injecting `-Znext-solver=globally`, which descends to the leaf and even renders CGP's own "add
`#[derive(HasField)]`" hint. The fixture for that path,
[`unsatisfied_dependency`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unsatisfied_dependency.rs),
demonstrates the recovered cause, and since the typed resolver also presents it as a `[CGP-E001]`
headline over a `root cause:` note, it has `acceptable` quality rather
than `usability`.

### Defeated: a field name the printer elided a character from

The second archetype is a field name the compiler prints with a character missing, so the name
cannot be read back from the diagnostic at all. When a provider needs a field the context lacks and
the context has a *near-miss* field, rustc reports the unmet bound through its two-line "similar
impl exists" hint and, in that hint, diffs the two `HasField` symbols and replaces every generic
argument they share with `_`. In
[`base_area_1`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_1.rs)
a `Rectangle` that has `width` but not `height` makes the two symbols share the character `'h'`, and
that shared `'h'` is collapsed to `_` in *both* names (`h,e,i,g,_,t` for `height`), so without the
flag below the field name is absent from the text, not merely encoded. `cargo-cgp` defeats this by
injecting `--verbose`, which turns off the compiler's matching-argument elision (along with two
related compressions) so the full `Symbol` always prints. That fixture, too, has `acceptable`
quality, because the typed resolver reads the field name straight from the `Symbol!` and states it
plainly.

## Extensible-data failures that never name their cause

Five failures of the [extensible-data](../../cgp/concepts/extensible-records.md) family reach the
reader as rustc wrote them, and no line of the output contains the cause: the derive or the
`Default` impl the program lacks. Each names a bound on a macro-generated type or a missing method,
and the field or type at fault appears nowhere, so the cause cannot be read back from the output
without the program's source. Their fixtures carry `//@quality: hidden`:

- [`auto_dispatch_missing_derive`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/auto_dispatch_missing_derive.rs):
  a `#[cgp_auto_dispatch]` call on an enum without `#[derive(CgpData)]`, reported as the generated
  matcher's unmet `Computer` bound.
- [`build_from_source_without_has_fields`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/build_from_source_without_has_fields.rs):
  `build_from` on a source struct without `#[derive(HasFields)]`, reported as `CanBuildFrom<…>` not
  implemented for the target's partial record.
- [`build_with_default_without_default`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/build_with_default_without_default.rs)
  and
  [`finalize_with_default_without_default`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/finalize_with_default_without_default.rs):
  building or finalizing with defaults when an unset field's type has no `Default`, reported as
  `CanFinalizeWithDefault` on the partial record, or as a missing method, without naming the field.
- [`upcast_source_without_has_fields`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/upcast_source_without_has_fields.rs):
  `upcast` on an enum that derives only `ExtractField`, reported as "no method named `upcast`" with
  a note suggesting an impl of `CanUpcast`.

Unlike the defeated archetypes, each cause is in the compiler's state: the presence markers of the
partial record (`IsPresent`, `IsNothing`, and the rest) say which field is unset, and the unmet
bound names the trait the missing derive would implement. So a typed leaf over them can name the
field, its type without `Default`, or the derive, the same leaf the readable-but-buried failures of
the family need ([usability](usability.md#extensible-data-failures-are-not-reshaped-at-all)).

## What a new case would look like

Should another wiring mistake be found whose cause survives *both* levers (the next-gen solver still
does not compute it, and `--verbose` still does not print it), it belongs here, with a fixture of `hidden` quality in its error class's directory
that proves the cause is unrecoverable from the text. The upstream catalog's
[hidden-versus-surfaced axis](../../cgp/errors/README.md#the-central-axis-hidden-versus-surfaced) is
the same distinction from the CGP side and is the reference for judging which classes carry their
cause and which suppress it.

The second thing that stays out is by scope: plain Rust or Cargo diagnostics that have nothing to do
with CGP are not `cargo-cgp`'s to recover and are not tracked here.
