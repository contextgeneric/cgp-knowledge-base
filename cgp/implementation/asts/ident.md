# The restricted argument and parameter types

The `ident` types are CGP's own parsers for a name followed by an angle-bracketed list, used wherever a macro reads a type-level name from user input. They exist because `syn` parses these lists far more leniently than Rust accepts in the positions CGP cares about: `syn::GenericArgument` takes associated bindings and bounds, and `syn::GenericParam` takes bounds and defaults. Each restricted type models only the valid forms, so a wrong input is rejected at parse time with a message naming the problem, instead of lowering into code the compiler rejects later. The [Parsing note](../README.md#parsing-build-with-parse_internal-and-distrust-syns-leniency) states the rule; this document covers the types.

## Type arguments: `TypeArg` and `TypeArgs`

`TypeArg` is one argument in a type-expression position, such as each of `'a`, `A`, `(A, B)`, and `Bar<A>` in `Foo<'a, A, (A, B), Bar<A>>`. It has three variants: a lifetime, a type, and a const written as a literal or a braced block (`3`, `{ N }`); a bare `N` is parsed as a type, as in `syn`. After a type, an `=` fails with ``associated bindings (`Name = ...`) are not allowed in type arguments`` and a `:` with ``associated type bounds (`Name: ...`) are not allowed in type arguments``.

`TypeArgs` is the list: an optional `<…>` of `TypeArg`s, parsed and emitted by the shared `parse_angle_bracketed` and `to_tokens_angle_bracketed` helpers. The absence of brackets and an empty `<>` both parse as the empty list, which renders as nothing. The list is emitted in the order it holds, so a caller that inserts an argument at position 0 ahead of a lifetime relies on a `syn` re-parse to put the lifetime first, as `#[use_provider]` does.

## `IdentWithTypeArgs` and `PathWithTypeArgs`

`IdentWithTypeArgs` is an identifier followed by `TypeArgs`, such as `Foo<A, B>`; the `cgp_namespace!` header parses its namespace name with it.

`PathWithTypeArgs` generalizes it to a full path, such as `path::to::Foo<A, B>` or `::path::Foo`, and is the type most macros use for a trait or type they read from user input: the `#[use_type]` trait path and `in Context`, the `#[use_provider]` bounds, the `#[prefix]` and `#[default_impl]` namespaces, the `check_components!` context, the `cgp_namespace!` parent, the `delegate_components!` `namespace` and `for` statements, and the provider trait of `#[cgp_provider]` and `#[cgp_impl]`. It parses a `syn::Path` and lifts the final segment's arguments into a separate `type_args` field, which makes them easy to read and rewrite. It rejects three forms:

- generic arguments on a segment other than the last (``generic arguments are only allowed on the final path segment``);
- a turbofish (``turbofish arguments (`Foo::<A>`) are not allowed; use `Foo<A>` ``);
- parenthesized arguments such as `Fn(A) -> B`.

The final segment's arguments are re-parsed through `TypeArgs`, so they carry the same restrictions as `TypeArg`. Two methods serve the callers: `ident()` returns the final segment's identifier, which `check_components!` uses to derive `__Check{Context}`, and `to_bound_tokens` renders the path with associated-type bindings merged into its own argument list (`Trait<Arg, Item = u8>`), the form a pinned `#[use_type]` bound needs.

## Definition-site parameters: `TypeGenericParam` and `IdentWithTypeGenerics`

`TypeGenericParam` is one parameter at a definition site, such as each of `'a` and `C` in `Bar<'a, C>`. It accepts a bare lifetime, a bare type identifier, or a `const N: T` parameter, and rejects each richer form with its own message:

- a lifetime bound (``lifetime bounds (`'a: 'b`) are not allowed in type generics``);
- a trait bound (``trait bounds (`A: Clone`) are not allowed in type generics``);
- a type default (``default type parameters (`A = B`) are not allowed in type generics``);
- a const default (``default const parameters (`const N: T = ...`) are not allowed in type generics``).

`TypeGenericParams` is the list, parsed with the same `parse_angle_bracketed` helper, and `to_generics` lowers it to a `syn::Generics` for a struct definition. It is distinct from `TypeGenerics` in `types/generics/`, which adapts an already-parsed `syn::Generics` and normalizes it through `split_for_impl`; the inline docs explain when to use each.

`IdentWithTypeGenerics` is an identifier followed by `TypeGenericParams`. The `#[cgp_component]` `name:` key parses the component name with it, and so do the `delegate_components!` `new` table name and the provider type `#[cgp_new_provider]` declares, all of which name a struct with those parameters.

## Known issues

`TypeGenericParam` accepts a const parameter, but the component name that carries one is also rendered in type positions, where `const N: usize` is not valid. `#[cgp_component { provider: Foo, name: FooComponent<const N: usize> }]` therefore fails inside the macro with ``failed to parse internal tokens to type `syn::generics::TypeParamBound` ``. The fix is either to reject a const parameter where the name is used as a type or to render it as the bare `N` there; the user-visible side is in [reference/macros/cgp_component.md](../../reference/macros/cgp_component.md#known-issues).

## Tests

The parse rules are pinned directly in `cgp-macro-tests`, by parsing token streams into each type with `assert_parses` and `assert_rejects`:

- [ident_with_type_params/new_ident_with_type_args.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/ident_with_type_params/new_ident_with_type_args.rs) covers `IdentWithTypeArgs`: the accepted lifetime, type, composite, and const forms, the rejected associated bindings and bounds, a path head, a turbofish, and an unterminated list, and a parse-print round trip.
- [ident_with_type_params/new_ident_with_type_generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/ident_with_type_params/new_ident_with_type_generics.rs) covers `IdentWithTypeGenerics`: the accepted bare, lifetime, and const parameters, the rejected bounds, defaults, composite forms, and path head, the lowering to `syn::Generics`, and a round trip.
- [ident_with_type_params/path_with_type_args.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/ident_with_type_params/path_with_type_args.rs) covers `PathWithTypeArgs`: single- and multi-segment paths, a leading `::`, the shared argument forms, the rejected intermediate generics, turbofish, bindings, and parenthesized arguments, the `ident()` accessor, and `to_bound_tokens` merging bindings into one argument list.

## Source

- The types live in [cgp-macro-core/src/types/ident/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/ident/):
  - `TypeArg` and `TypeArgs` in `type_arg.rs`;
  - `TypeGenericParam`, `ConstGenericParam`, and `TypeGenericParams` in `type_generic_param.rs`;
  - `IdentWithTypeArgs`, `IdentWithTypeGenerics`, and `PathWithTypeArgs` in the files of the same names;
  - the shared list helpers in `angle_bracketed.rs`.
- `TypeGenerics`, the adapter for an already-parsed `syn::Generics`, is in [cgp-macro-core/src/types/generics/type_generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/generics/type_generics.rs).
