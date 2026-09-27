# `merge_generics`

`merge_generics` combines two `syn::Generics` into one by concatenating their parameters and joining their `where` clauses. The wiring macros need it wherever an impl's generics come from two places: `delegate_components!` merges a table's generics with a key's or path segment's own, and `check_components!` merges a table's generics with a `#[check_params]` value's.

## Behavior

The merge concatenates without inspecting anything. The first argument's parameters come before the second's, the two `where` clauses' predicates are collected into one clause in the same order (and the clause is dropped when both are empty), and the angle-bracket tokens are taken from the first argument. Nothing is de-duplicated, so a parameter named on both sides appears twice. Writing `<T> Table<T> { <T> Key<T>: P }` therefore fails with `E0403` (the name `T` is already used for a generic parameter), with the caret on the key's `T`; a key reuses the table's parameter by naming it without redeclaring it.

Parameter kinds need no care from the caller. A merge can place a type parameter before a lifetime, as when a table's `<T>` is followed by a key's `<'a>`, but `Generics::to_tokens` always emits lifetimes first, so the rendered impl is valid. The [implementation README](../../README.md#generic-parameter-insertion-and-lifetime-ordering) explains the rule.

## Tests

- The helper has no dedicated test. It is covered by the snapshots that merge generics: [basic_delegation/delegate_generic_table.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/basic_delegation/delegate_generic_table.rs) for a table and a key, and [checking/check_generic.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/checking/check_generic.rs) for a check table and a generic check value.

## Source

- The function lives in [cgp-macro-core/src/functions/generics/merge_generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/generics/merge_generics.rs).
- Its callers are `types/delegate_component/mapping/eval.rs`, `types/delegate_component/key/path.rs`, and `types/check_components/table.rs`.
