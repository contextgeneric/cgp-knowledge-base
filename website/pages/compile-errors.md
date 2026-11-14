# The compile-errors page

The compile-errors page consolidates the internal error catalog into one public page, organized by
whether the compiler hides or surfaces a mistake's cause, and closes with the `[CGP-Exxx]` code
tables.

- **URL:** <https://contextgeneric.dev/docs/reference/errors>
- **Source:** [docs/reference/errors.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/reference/errors.md)
- **Status:** Current
- **How it was made:** as for the [Reference](reference.md)

## What it covers

The page documents no construct. It turns the twenty-one class documents under
[cgp/errors/](../../cgp/errors/README.md) into one page, because twenty-one public pages would be a
category no reader scans. It states the catalog's **hidden-versus-surfaced** axis once near the top as
"the one distinction that explains everything", and opens with a lookup table keyed on what a reader
has in front of them: a `rustc` code and a message shape.

**Every quoted diagnostic is real output from a run of the tool** on a small program with the page's
names. The checked and method-call routes to one mistake produce the same headline, chain, and
`help` under different compiler codes, which is the page's central demonstration.

*Using something you did not declare* collects common first-week mistakes: a trait used without
`#[uses]` and an inner provider used without `#[use_provider]` are the
[undeclared dependency](../../cgp/errors/lowering/undeclared-dependency.md) class, and the
consumer-versus-provider-trait confusions are
[wrong component half](../../cgp/errors/lowering/wrong-component-half.md).

The page is the site's home for the `[CGP-Exxx]` codes, since the internal catalog that defines them
cannot be linked from a public page: two tables close it, one for headline codes and one for
dependency-tree codes. The [`cargo-cgp` error-codes page](cargo-cgp.md) holds the per-code entries,
and this page keeps a short section pointing there.

## How it relates to the knowledge base

The page draws on the classes under [cgp/errors/](../../cgp/errors/README.md) and on the tool's code
catalog, [cargo-cgp/error-code.md](../../cargo-cgp/error-code.md).

Its code is backed by
[`tests/reference/errors.rs`](https://github.com/contextgeneric/contextgeneric.dev/blob/main/example-code/tests/reference/errors.rs),
which pins the page's one program in both directions. A live module proves the wiring block
compiles, as the page asserts in bold, and deliberately omits the `check_components!` the crate adds
everywhere else, because the page withholds the check and that omission moves the error. Two
fixtures under `tests/compile_fail/reference/`, `errors_the_fix_1.rs` and `errors_the_fix_2.rs`, pin
the checked failure and the hidden one. The merged failure the page quotes, three checked components
needing one missing field, is the capture-only program
`example-code/diagnostics/reference/shared_missing_name.rs`, described in
[site.md](../site.md#the-example-code-crate).

## Maintaining it

- Rerun the program to change a quote; never edit quoted output.
- A new error class or code reaches this page and the [`cargo-cgp` pages](cargo-cgp.md) in the same
  change as the catalog.
