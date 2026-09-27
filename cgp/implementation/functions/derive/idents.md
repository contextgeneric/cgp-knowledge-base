# Identifier case conversion

The case-conversion helpers derive one identifier from another in the naming conventions CGP's generated code uses: PascalCase for type and trait names, snake_case for values. `#[cgp_fn]` derives its trait name from the function name, `#[cgp_computer]` and `#[cgp_producer]` their provider name, `#[cgp_auto_dispatch]` its per-method `Compute…` computer names, and `#[cgp_component]` and `#[cgp_impl]` the name of the context value in a provider method.

## `to_camel_case_str`

`to_camel_case_str` produces PascalCase by splitting on underscores, dropping empty segments, and upper-casing the first character of each segment while leaving the rest unchanged. So `rectangle_area` becomes `RectangleArea`, `__foo__` becomes `Foo`, and `getHTTP` becomes `GetHTTP`.

## `to_snake_case_str` and `to_snake_case_ident`

`to_snake_case_str` produces snake_case by inserting an underscore before every uppercase character that does not follow an underscore or start the string, then lower-casing the result. Each uppercase letter starts a new word, so `Context` becomes `context` but an acronym splits letter by letter: `HTTPServer` becomes `h_t_t_p_server`.

`to_snake_case_ident` adds the reserved form on top. Unless the input already starts with an underscore, it wraps the result as `__…__`, so `Context` becomes `__context__` and `Rectangle` becomes `__rectangle__`, while `__Context__` becomes `__context__` without a second wrapping. This is how the provider trait's receiver gets a name that cannot clash with a user's own parameters, the same convention behind the reserved names in [entrypoints/cgp_component.md](../../entrypoints/cgp_component.md). The returned identifier carries `Span::call_site()`.

## Tests

- These helpers have no dedicated test. The derived names appear throughout the expansion snapshots: the `__context__` receiver in every `snapshot_cgp_component!`, and the PascalCase trait name in [implicit_arguments/cgp_fn_greet.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/implicit_arguments/cgp_fn_greet.rs).

## Source

- The functions live in [cgp-macro-core/src/functions/camel_case.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/camel_case.rs) and [cgp-macro-core/src/functions/snake_case.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/snake_case.rs).
