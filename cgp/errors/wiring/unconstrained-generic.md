# Unconstrained generic

A per-entry generic parameter appears only in the provider value and never reaches the key, so the
generated impl leaves the parameter unconstrained and the compiler rejects it with `E0207`.

## What triggers it

An entry in a wiring table may introduce its own generic parameters, but a per-entry generic is
well-formed only when it reaches the *key*, where `DelegateComponent<Key<…>>` binds it. Writing one
that appears only in the provider value never binds it, and CGP lowers the entry faithfully rather
than second-guessing it, so the compiler rejects the free parameter exactly as it would a
hand-written impl with an unused parameter. The same holds for an entry in
`delegate_and_check_components!`, and for one in a `cgp_namespace!` body, which lowers to an impl of
the namespace's lookup trait for its key.

```rust
delegate_components! {
    Person {
        <T> GreeterComponent: GreetWith<T>, // T is in the value, never the key
    }
}
// lowers to an impl with an unconstrained parameter:
impl<T> DelegateComponent<GreeterComponent> for Person {
    type Delegate = GreetWith<T>; // T constrains nothing
}
```

The same shape arises in two more places. A *generic* provider registered as a per-type default
with `#[default_impl]` leaves its parameter unbound, since the registration copies the provider
impl's parameters and nothing in it uses them. A `for <T, Provider> in Table` loop in
`delegate_components!` whose key does not mention `T` leaves both variables unbound, since only the
key binds `T` and only `T` binds `Provider`. A
[`#[cgp_computer]`](../../reference/macros/cgp_computer.md) function whose type parameter appears
only in its return type would leave it unbound too, but the macro sees the whole signature and
rejects it at expansion, so it never reaches the compiler.

## The raw diagnostic

This section describes what plain `cargo check` prints, the fallback when `cargo-cgp` is not on
hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers the readable form. The
compiler reports **`E0207`**, "the type parameter `T` is not constrained by the impl trait, self
type, or predicates", with the caret on the `<T>` the user wrote in the entry. The class is
well-localized rather than cascading, but it is not quite a single line: the entry lowers into more
than one generated position carrying `T`, so the same `E0207` prints twice, each with a different
`help:`: one offering to move `T` onto the `Person` type, one to remove the unused parameter. Both
carets land on the same `<T>` and name the same cause, so there is no note chain and nothing to
trace. Neither suggestion compiles: `Person<T>` leaves the struct's parameter unused, and removing
`<T>` leaves `GreetWith<T>` naming an undeclared type. The count depends on the impls the entry
lowers to: `delegate_and_check_components!` adds a check impl, so it prints three, and a
`cgp_namespace!` entry lowers to one impl, so it prints once, with a suggestion to make the
component generic. An entry whose parameter appears nowhere prints once, with only the help to
remove it, which is the right fix there.

The rule behind it is that an impl parameter must be *determined* by the impl, and knowing why makes
the fix obvious. Rust requires every generic parameter on an impl to appear in the implemented
trait, in the self type, or in a `where`-clause predicate that pins it as an associated type (one of
the three "constrained" positions the message names), because otherwise, given a trait reference,
the compiler could not decide which `T` the impl is for. Here `T` reaches only the `Delegate`
*value* (`GreetWith<T>`), an associated-type position on the right of the `=`, which does not
constrain the impl: `DelegateComponent<GreeterComponent>` names no `T`, so any `T` would satisfy the
header equally. Permitting that would also break coherence, since a downstream crate adding another
`GreetWith<U>` would make the choice ambiguous. This is the rule introduced by
[RFC 447](https://github.com/rust-lang/rfcs/pull/447) ("prohibit unused type parameters in impls");
the [`E0207`](../error_codes/e0207.md) reference summarizes it. It is the same negative-reasoning
concern that underlies the [orphan rule](orphan-rule.md) and coherence conflicts: an impl must be
resolvable no matter what impls other crates add later.

## Where the root cause is

The root cause is **present and precise**: the caret sits on the offending generic parameter, and
the message states exactly why it is rejected. This is the most localized class in the catalog: the
diagnostic needs no tracing and hides nothing. What the raw message lacks is the CGP-specific
remedy: it describes the constraint in impl terms rather than in terms of the wiring entry, and its
suggestions do not compile.

## How cargo-cgp presents it

`cargo-cgp` rewrites the per-entry generic into one **`[CGP-E019]`** in place of rustc's errors,
whichever table holds the entry:
``[CGP-E019] the entry for `GreeterComponent` in the wiring of `Person` binds `T`, but its key does not use it``,
with the caret on `T` and a `help:` to write a concrete type in place of `T` in `GreetWith<T>` and
remove `T` from the entry's generic parameters. rustc's two suggestions are dropped, since neither
compiles. The headline names every parameter the key leaves out (``binds `T` and `U` ``), and a
`cgp_namespace!` entry by its namespace (``in the namespace `AppNamespace` ``). The help adapts to
what uses the parameter: it is only to remove the parameter when nothing in the entry uses it, and
it points at where the entry uses it when that is not a plain provider, such as the table a `->`
entry forwards to.

The `for` loop and the `#[default_impl]` shapes are rewritten too. A loop whose key does not use its
key variable becomes one **`[CGP-E017]`** in place of rustc's three `E0207`s:
``[CGP-E017] the `for` loop in the wiring of `App` binds `T`, but its key `@test.ShowImplComponent.String` does not use it``,
with the caret on `T` and a `help:` to write `T` in the key. A `#[default_impl]` on a generic
provider impl becomes **`[CGP-E018]`**:
``[CGP-E018] `#[default_impl]` cannot register `ShowWithDisplay` for `String`, because the provider's impl is generic over `T` ``,
with a `help:` to write the impl for `String` alone in the concise `#[cgp_impl]` form. The same code
covers the explicit-context form, `impl<Context> ShowImpl<String> for Context`, whose copied
parameter is `Context`, and a provider struct that is itself generic over the parameter,
`#[cgp_impl(ShowWith<T>)]` over `impl<T: Display> ShowImpl<T>`, when the key is a type. Its `help:`
registers the provider at the key instead:
``write the impl for `String` alone, as `#[cgp_impl(ShowWith<String>)]` with `String` in place of `T` ``.
All of them drop rustc's suggestion to remove the parameter, which is not the fix. The codes are
defined in the [cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md).

Four shapes keep rustc's errors, and with them suggestions that do not compile. A per-entry lifetime
that only the provider uses (`<'a> GreeterComponent: GreetRef<'a>`) is unconstrained because the
entry's `Delegate` names it, but `[CGP-E019]` lists only type and const parameters. A blanket entry
keyed by its own parameter (`<T, U> T: Wrap<U>`) has no key `[CGP-E019]` can name. And a
`#[default_impl]` of a provider struct generic over the parameter is beyond `[CGP-E018]`'s fix when
its key is a path, which gives no type to put in the parameter's place, or when the struct names a
second parameter the key does not fix. An ordinary impl with an unconstrained parameter in a crate
that uses CGP is not a CGP error, and keeps rustc's diagnostic as written.

## Resolving it

Make the generic reach the key so it is bound: introduce it on a key that carries it
(`<T> SomeKey<T>: …`) rather than only on the value, or, when the intent was a single concrete
wiring, register a concrete provider with no per-entry generic at all. For a generic provider
registered as a per-type default, write the provider's impl for the registered type alone, in the
concise `#[cgp_impl]` form, since the default position cannot bind the provider's parameter. For a
`for` loop, write the loop's key variable in the key, where the type the loop covers goes.

## Backing fixtures

- [`wiring/unconstrained-generic/unconstrained_generic.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/unconstrained_generic.rs):
  a per-entry generic (`<T> GreeterComponent: GreetWith<T>`) that appears only in the value,
  lowering to an impl with an unconstrained `T`; its `.rust.stderr` pins the `E0207` carets on the
  `<T>` (the error printed twice, with its two suggestions), and its `.cgp.stderr` the single
  `[CGP-E019]` with the help to write a concrete type in place of `T`.
- [`wiring/unconstrained-generic/entry_generic_shapes.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/entry_generic_shapes.rs):
  an entry binding two such parameters, an entry binding one it never uses, and a `->` entry
  forwarding to a table named with its parameter; the `.cgp.stderr` pins one `[CGP-E019]` per entry,
  naming both parameters together, a help that only removes the unused one, and a help pointing at
  where the `->` entry uses its parameter.
- [`wiring/unconstrained-generic/entry_generic_checked.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/entry_generic_checked.rs):
  the plain entry in `delegate_and_check_components!`, whose `.rust.stderr` pins the `E0207` three
  times and whose `.cgp.stderr` pins one `[CGP-E019]`.
- [`wiring/unconstrained-generic/namespace_entry_generic.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/namespace_entry_generic.rs):
  the plain entry in a `cgp_namespace!` body; the `.rust.stderr` pins one `E0207` suggesting a
  generic component, and the `.cgp.stderr` the `[CGP-E019]` naming the namespace.
- [`wiring/unconstrained-generic/for_loop_key_without_var.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/for_loop_key_without_var.rs):
  a `for <T, Provider>` loop whose key `@test.ShowImplComponent.String` does not use `T`; the
  `.rust.stderr` pins rustc's three `E0207`s with contradictory helps, and the `.cgp.stderr` the
  single `[CGP-E017]`.
- [`wiring/unconstrained-generic/default_impl_generic_provider.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_generic_provider.rs)
  and
  [`wiring/unconstrained-generic/default_impl_explicit_context.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_explicit_context.rs):
  `#[default_impl]` on a provider impl generic over `T`, and on one written in the explicit-context
  form; the `.rust.stderr` pins the `E0207` with its "remove the unused type parameter" help, and
  the `.cgp.stderr` the `[CGP-E018]` naming the parameter.
- [`wiring/unconstrained-generic/default_impl_generic_provider_struct.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_generic_provider_struct.rs):
  `#[default_impl]` on the impl of a provider struct generic over `T` (`#[cgp_impl(ShowWith<T>)]`);
  the `.rust.stderr` pins the single `E0207`, and the `.cgp.stderr` the `[CGP-E018]` whose help
  registers `ShowWith<String>`.
- [`wiring/unconstrained-generic/entry_generic_redirect.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/entry_generic_redirect.rs):
  a per-entry generic only a `=>` redirect uses; the `.cgp.stderr` pins the `[CGP-E019]` whose help
  points at where the entry uses it, without naming the generated `RedirectLookup`.
- [`wiring/unconstrained-generic/entry_lifetime_not_in_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/entry_lifetime_not_in_key.rs),
  [`wiring/unconstrained-generic/entry_generic_blanket_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/entry_generic_blanket_key.rs),
  and
  [`wiring/unconstrained-generic/default_impl_unregistrable_provider_struct.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_unregistrable_provider_struct.rs):
  the shapes that keep rustc's errors, a per-entry lifetime, a blanket key, and the two
  registrations `[CGP-E018]` cannot write the fix for.

## Related

- [Conflicting wiring](conflicting-wiring.md), [Orphan-rule violation](orphan-rule.md),
  [Wiring cycle](wiring-cycle.md): the sibling structural classes.
- [`delegate_components!`](../../reference/macros/delegate_components.md),
  [`cgp_namespace!`](../../reference/macros/cgp_namespace.md), and
  [`DelegateComponent`](../../reference/traits/delegate_component.md).
- [Debugging CGP compile errors](../../guides/debugging.md): the `E0207` entry in the decoder.
