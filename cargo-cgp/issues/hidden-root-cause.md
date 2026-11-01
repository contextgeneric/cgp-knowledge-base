# Hidden root cause

This document catalogs the cases where `cargo-cgp`'s output lacks the root cause of an error, so that no
downstream processing could recover it. The test is *sufficiency*, not readability, which
[usability](usability.md) handles. An issue belongs here only when a fixture under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui) reproduces it.

## No open case

No fixture has `hidden` quality: every post-codegen error class CGP produces has a fixture whose
cause appears in the tool's output. A namespace inheritance cycle produces no diagnostic at all, but
because the compiler accepts it, not because a cause is suppressed
([usability](usability.md#errors-the-tool-cannot-settle)).

A cause can be hidden in two ways, and each needs a different flag: the compiler **never computed
it**, a trait-solver problem, or it computed the cause and **elided it while printing**, a
diagnostic-printing problem. Both flags are in
[Architecture](../implementation/architecture.md#the-flow-of-a-diagnostic), and
[rustc diagnostic internals](../implementation/rustc-diagnostic-internals.md) maps the printing
side.

### Defeated: a cause the default trait solver never computed

This kind is a wiring mistake exercised by a direct consumer-method call, where
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

This kind is a field name the compiler prints with a character missing, so the name cannot be read
back from the diagnostic. When a provider needs a field the context lacks and
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

## What a new case would look like

A wiring mistake whose cause survives *both* flags belongs here, with a fixture of `hidden` quality
in its error class's directory that proves the cause is unrecoverable from the text. The catalog's
[hidden-versus-surfaced axis](../../cgp/errors/README.md#the-central-axis-hidden-versus-surfaced) is
the same distinction from the CGP side.
