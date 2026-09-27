# `define_keyword!`

`define_keyword!` declares a custom-keyword marker for the CGP parsers: a zero-sized struct paired, through the `IsKeyword` trait, with the identifier it matches. The CGP macros accept a few bare words that are not Rust keywords (`new` in `#[cgp_impl]`, `#[cgp_provider]`, `delegate_components!`, `cgp_namespace!`, and nested tables; `open` and `namespace` as `delegate_components!` statements), and each is represented at the type level by one of these markers.

## Expansion

`define_keyword!(Name, "spelling")` emits two items: `pub struct Name;` and an `impl crate::traits::IsKeyword for Name` whose associated const `IDENT` is `"spelling"`. The CGP set is declared in `types/keywords.rs`:

```rust
define_keyword!(New, "new");
define_keyword!(Namespace, "namespace");
define_keyword!(Open, "open");
```

`cgp-macro-test-util-lib` uses the same macro for the snapshot wrappers' own keywords (`derive`, `cgp_component`, and one per pinned macro), which is why the macro is `#[macro_export]`ed rather than private to `cgp-macro-core`.

## How the parsers use a keyword

The marker carries only a spelling; the parsing lives in two generic pieces that every keyword shares. `Keyword<K>` in `types/keyword.rs` is the parsed form: its `Parse` impl reads one `Ident`, fails with ``expect keyword: `new` `` (naming `K::IDENT`) when the identifier differs, and records the identifier's span. The `PeekKeyword` and `ParseOptionalKeyword` traits in `traits/keyword.rs` extend `syn`'s `ParseBuffer`: `peek_keyword::<K>()` forks the input and compares the next identifier with `K::IDENT` without consuming it, and `parse_optional_keyword::<K>()` parses a `Keyword<K>` only when the peek succeeds. An AST type therefore stores `Option<Keyword<New>>` for an optional `new` and `Keyword<Open>` for a required `open`.

## Behavior and corner cases

A keyword is an ordinary identifier to the Rust lexer, so the match is a string comparison on `Ident`, and a raw identifier such as `r#new` does not match, because `Ident`'s comparison includes the `r#`. The struct name and the spelling are independent, although every CGP keyword names its marker after its spelling.

## Tests

- `define_keyword!` has no dedicated test. The keywords it defines are exercised by the snapshots of the macros that parse them: the `new` forms in the `basic_delegation` and `namespaces` targets, and the `open` and `namespace` statements in the `namespaces` target. The ``expect keyword`` error is not pinned by a rejection case, since every caller peeks, or parses speculatively on a fork, before it commits to a required keyword.

## Source

- The macro is defined in [cgp-macro-core/src/macros/keyword.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/macros/keyword.rs).
- `IsKeyword`, `PeekKeyword`, and `ParseOptionalKeyword` are in [cgp-macro-core/src/traits/keyword.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/traits/keyword.rs).
- The `Keyword<K>` parsed form is in [cgp-macro-core/src/types/keyword.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/keyword.rs), and the CGP markers in [cgp-macro-core/src/types/keywords.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/keywords.rs).
- The convention that custom keywords go through this macro is recorded in [cgp-macro-core/AGENTS.md](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/AGENTS.md).
