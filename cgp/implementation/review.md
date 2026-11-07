# Reviewing a CGP macro

This document is the procedure for the macro review workflow that [cgp/AGENTS.md](https://github.com/contextgeneric/cgp/blob/main/AGENTS.md#macro-review-workflow)
summarizes as rules. Review one macro at a time, and continue until no further issue is found.

## Orient first

Invoke the `/cgp` skill. Read the macro's [reference document](../reference/README.md), its
implementation documents (the entrypoint, the AST stack, and the functions it drives), and the
`AGENTS.md` files that keep those views in sync. Then read the implementation in
`crates/macros/`, starting from the `cgp-macro-lib` entry and following it into the
`cgp-macro-core` types and helpers. Finally read the tests: the behavioral tests in `cgp-tests`, and
the rejection cases and expansion snapshots in `cgp-macro-tests`.

## Harden the implementation and its tests

- Fix bugs and unhandled corner cases; when a corner case cannot be fixed now, capture it as a failure
  case and record it under Known issues.
- Add tests for uncovered corner cases, in the concept target that owns the behavior, with a snapshot
  only in the macro's owning target.
- Verify each test exercises the behavior it claims, and make an assertion where one is possible.
- Merge or remove tests that check the same behavior, and factor common boilerplate into a helper.
- Update the reference and implementation documents and the inline docs when they are inconsistent or
  unclear.

## Scrutinize the macro codegen

Check every area below on every macro, not only the ones that already have a fixture.

- **Attributes:** enumerate them, validate each, reject an unknown one with a spanned error, and reject
  a duplicate or a mutually exclusive pair.
- **Parsing:** build `syn` nodes with `parse_internal!`, thread `syn::Result`, and reject malformed or
  unsupported input at the macro's own parse stage.
- **Expansion:** walk the input space and confirm no shape emits invalid Rust: no conflicting impls, no
  unbound or doubly declared generic, no empty expansion, and no generated-name clash.
- **Generics:** keep the kinds (lifetime, type, const) and the roles (impl generic versus type
  generic) distinct, and bind every parameter that appears in a generated header.
- **Hygiene:** emit every CGP item through an `exports` marker, give generated identifiers the
  double-underscore form, and keep the expansion idempotent.
- **Spans:** re-span a generated item onto its originating token for the compiler's carets, and never
  drag a resolvable reference or a derived name onto a user token's range for the IDE.

Capture an accepted input whose expansion fails to compile as a `cargo-cgp` UI fixture, filed under
its error class, and catalog the class in the [error catalog](../errors/README.md). When the failure
is a CGP defect the macro should have rejected, also record it under the macro's Known issues.

## Keep every view in sync and verify

- Update the reference document's Expansion, the implementation document's Pipeline and Generated
  items, the affected snapshots, and the `/cgp` skill in the same change.
- Run the format, clippy, and test checks for the affected crates, and review every snapshot diff.
- Confirm a green suite before considering the review done.

## Ask when in doubt

Surface a question when the intended behavior, a corner case's correct outcome, or a design choice is
unclear. A wrong assumption baked into the source, tests, and four documentation views is expensive to
unwind.
