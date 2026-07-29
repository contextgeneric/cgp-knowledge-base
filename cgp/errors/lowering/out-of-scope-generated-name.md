# Out-of-scope generated name

An `#[impl_generics]` parameter is named in the capability's own signature, where the generated trait cannot see it, so the compiler rejects the generated code with `E0433` "cannot find type".

## What triggers it

This class is a *lowering* failure: the name the author wrote is real and the construct they used is real, but the two do not meet, because the macro placed the name where it cannot resolve. It is not a wiring mistake — the failure precedes any trait solving, so no `IsProviderFor` or `DelegateComponent` frame appears anywhere in the output.

[`#[impl_generics]`](../../reference/macros/cgp_fn.md) adds a generic parameter to the generated *impl* alone, which is what lets a context supply the type implicitly through the type of a field, with no parameter on the trait for a caller to thread. The generated trait therefore does not carry it, so a signature that names it refers to nothing:

```rust
#[cgp_fn]
#[impl_generics(Db: Database)]
pub fn fetch_row(&self, #[implicit] database: &Pool<Db>) -> Db::Row {
    todo!() // `Db` is in scope in the impl, but the trait declares no `Db`
}
```

The `&Pool<Db>` annotation is fine — that parameter is stripped from the signature and becomes a `HasField` bound on the impl, where `Db` *is* in scope — while the `Db::Row` return type is not, because the return type stays on the trait. The same holds for an explicit (non-implicit) parameter, and for any other position that survives into the trait.

This is an acceptable failure CGP defers to the compiler, because the macro cannot second-guess which of two things the author meant: promoting the type to an abstract type so it can be named, or keeping it out of the signature so it need not be. The choice between those is the subject of [naming a type dependency](../../guides/naming-a-type-dependency.md), and this diagnostic is the condition that forces it.

## The raw diagnostic

This section describes what plain `cargo check` prints — which for this class is also what the tool prints, per [How cargo-cgp presents it](#how-cargo-cgp-presents-it). This is a **surfaced** class with a short diagnostic: one [`E0433`](../error_codes/e0433.md) "cannot find type `Db` in this scope" carrying the trailing label `use of undeclared type`, with no note chain and no CGP scaffolding, because the failure is caught during name resolution before any bound is evaluated.

The caret lands on the offending segment of the return type in the author's own signature — the code to change — rather than on the `#[impl_generics]` attribute that scoped the parameter.

One adjacent code is worth knowing, because a grep for `E0433` will not find it. A bare name the compiler looked up with no path context is reported as [`E0425`](../error_codes/e0425.md) instead, with the same "cannot find type" headline but the bare label `not found in this scope`. In CGP that is most often a generated `…Component` marker an ill-formed `#[cgp_impl]` header derived from a trait that is not a provider trait, where the caret sits on the attribute rather than in the code it rewrote.

## Where the root cause is

The root cause is **present and is the entire diagnostic** — the message names the unresolved type and the caret points at where it could not be resolved. Nothing is suppressed and there is no cascade to wade through.

What the raw output does not carry is the CGP-level reading, and for this class that costs little: a reader who knows that `#[impl_generics]` scopes its parameter to the impl has the answer from the caret alone. The message never says which construct introduced the name, but the caret is inside the definition that carries the attribute, so the attribute is one line away.

## How cargo-cgp presents it

`cargo-cgp` passes this class through unchanged — the fixture's `.cgp.stderr` is byte-for-byte its `.rust.stderr` — because this is a name-resolution error emitted before trait solving, and the [typed resolver](../../../cargo-cgp/implementation/typed-root-cause-resolution.md) neither engages on it nor could recover anything useful if it did: there is no obligation to re-run and no wiring to descend.

The pass-through is the right outcome rather than a gap, which is why the fixture sits in the tool's `acceptable/` tier: the caret is on the author's own token and the message names exactly what is missing. The codes the tool stamps on the classes it does rewrite are in the [cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md).

## Resolving it

The parameter is the wrong construct for a type the signature names. Promote the type to an [abstract type](../../concepts/abstract-types.md) with [`#[cgp_type]`](../../reference/macros/cgp_type.md) and import it with [`#[use_type]`](../../reference/attributes/use_type.md), so it is determined by the context and nameable everywhere — or, when the type genuinely need not be named, keep `#[impl_generics]` and take the value through an implicit argument instead of returning it.

## A sibling: the shadowed abstract type

A related failure has the opposite cause — the name resolves, but to the wrong thing. Giving an abstract type the same name as the trait that bounds it makes the bound resolve to the associated type being declared rather than to the trait in scope:

```rust
#[cgp_type]
pub trait HasDatabaseType {
    type Database: Database; // the bound resolves to this very associated type
}
```

The compiler reports [`E0404`](../error_codes/e0404.md) "expected trait, found type parameter `Database`" — a type *parameter*, because `#[cgp_type]`'s expansion carries the associated type into that position — with a "you might have meant to refer to this trait" note pointing at the real trait and a "found this type parameter" label under the declaration. Both halves of the collision are named, so the diagnostic is self-explanatory once read; the trap is only that the declaration reads naturally to an author thinking "the abstract type `Database`, which implements `Database`". The fix is to name them apart, which is why an abstract database type reads better as `Db`. This is not a CGP defect — the collision is ordinary Rust name resolution — but it is easy to walk into when naming an abstract type after the concrete trait it abstracts over.

## Backing fixtures

- [`acceptable/lowering/impl_generics_in_signature.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/lowering/impl_generics_in_signature.rs) — an `#[impl_generics(Db: Database)]` parameter named as the return type `Db::Row`; its snapshots pin the `E0433` with the caret on the return type and the pass-through, and the fixture doubles as the recorded forcing condition for promoting an inferred type to an abstract one.
- [`acceptable/lowering/cgp_type_name_shadows_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/lowering/cgp_type_name_shadows_bound.rs) — the [shadowed abstract type](#a-sibling-the-shadowed-abstract-type), pinning the `E0404` and both of its landmark notes.
- [`ok/abstract_db_transaction.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/abstract_db_transaction.rs) — the clean-compile counterpart: the same two abstract types named in both components' signatures, where promoting them is what makes naming them legal. Two further `ok/` fixtures pin the positions a `#[use_type]` alias reaches, so neither is a case of this class — [`use_type_alias_in_expr_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/use_type_alias_in_expr_path.rs) for an alias qualifying an expression path, and [`use_type_pin_nested_alias.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/use_type_pin_nested_alias.rs) for one nested inside an equality pin's right-hand side.

## Related

- [`#[cgp_fn]`](../../reference/macros/cgp_fn.md) — the host of `#[impl_generics]`, whose Failure modes section records this case from the macro's side.
- [Naming a type dependency](../../guides/naming-a-type-dependency.md) — the prescriptive guide this class is the failure mode of: which of the two homes a type dependency belongs in, and the conditions that force the climb.
- [Unresolved imported abstract type](unresolved-imported-type.md) — the sibling lowering class, where a `#[use_type]` import names an associated type the trait does not declare (`E0576`).
- [Ill-formed generated type](ill-formed-generated-type.md) — the third lowering class, where the generated type resolves but is not well-formed.
- [`E0433`](../error_codes/e0433.md), [`E0425`](../error_codes/e0425.md), and [`E0404`](../error_codes/e0404.md) — the Rust codes this class and its adjacent shapes are reported under.
- [Debugging CGP compile errors](../../guides/debugging.md) — the prescriptive playbook this catalog supports.
