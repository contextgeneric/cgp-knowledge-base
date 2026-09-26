# `expression`

`expression` is a modular interpreter for a small arithmetic language: each operator is its own
generic type, each operation over the language is a set of per-operator providers, and four
contexts wire those pieces into interpreters of increasing reach, from evaluation alone to an extended
language with subtraction and negation.

- **Source** — [expression/](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/expression), on
  the `v0.8.0` branch; see [which revision](../README.md#which-revision-these-documents-describe)
- **Run** — `cargo test -p cgp-example-expression` from the repository root
- **Needs** — nothing beyond the workspace build
- **Result** — three unit tests pass: `test_add_mult`, `test_add_mult_to_lisp`, and
  `test_add_mult_neg`
- **Worked example** — [expression interpreter](../../../examples/expression-interpreter.md)
- **Cited by** — [extensible data types, part 2](../../../website/blog/extensible-datatypes-part-2.md),
  which links the crate

## What it is

The language is the arithmetic of `Plus`, `Times`, and `Literal`, with `Minus` and `Negate` added in
the extended language. Each is a standalone struct generic over the expression type it nests, so one
`Plus<Expr>` serves every language that has addition. A language is an enum whose variants wrap those
structs, such as `MathExpr` with its three variants, and the enum derives the extensible-variant
traits so a dispatcher can take it apart without a hand-written `match`.

Two operations run over the language. **Evaluation** turns an expression into a number, and
**conversion to Lisp** turns it into a `LispExpr` S-expression tree such as `(+ 2 3)`. Each operation
is one provider per operator, and a context chooses which providers serve which operator and
operation. The crate is `no_std` with `alloc`, and has no binary; its three tests are the way to run
it.

The crate holds four contexts, each a separate module under `contexts/` with its own copy of the enums
it needs, because each shows a different wiring of the same providers. They are documented one per
page in [examples/](examples/README.md), in teaching order:

| Context | Module | Wires | Tests |
|---|---|---|---|
| `Interpreter` | `add_mult` | evaluation by value and conversion by reference, one component each | two |
| `Interpreter` | `add_mult_binary_op` | the same, with one generic provider for both binary operators | none |
| `Interpreter` | `add_mult_code` | both operations by reference in one component, keyed by operation and input together | none |
| `InterpreterPlus` | `add_mult_neg` | evaluation only, over the extended `MathPlusExpr` with `i64` literals | one |

A fifth module, `classic`, holds the closed `enum` and `match` form of the same interpreter, which the
crate keeps as the starting point it improves on and which no context uses.

## Idioms

The crate uses current CGP idioms throughout. Every context dispatches with the `open` statement and
path keys, per [dispatching per type](../../../cgp/guides/dispatching-per-type.md), keying on the
input alone or on the operation code and the input together. The providers import their
dependencies with `#[uses]` and the two abstract types with `#[use_type]`, and the enums derive
`CgpData`. The one getter trait, `BinarySubExpression`, stays a getter because it reads the
provider's input rather than its context.

## Status and gaps

The interpreter is a demonstration, and its gaps are each confirmed against the `v0.8.0` branch and
recorded in full in [issues.md](issues.md):

- **Two contexts have no test** — `add_mult_binary_op` and `add_mult_code` compile and pass their
  checks, and only a probe has run them.
- **An unwired provider** — `EvalSubtractWithNegate` is defined and never wired.

## Where the blog post's code lives

The [part 2 post](../../../website/blog/extensible-datatypes-part-2.md) develops this interpreter
section by section, and its code survives in the crate in current syntax. How the post's code
diverges from current CGP is recorded in the post's own document; the table below says only where
each section's code now lives:

| Post section | Current code |
|---|---|
| The Expression Problem | `classic/add_mult.rs`, as `Expr` |
| Evaluator Computer | `types/` and `providers/eval/` |
| Evaluating Concrete Expressions, Dispatching Eval | `contexts/add_mult.rs` |
| Converting to a Lisp Expression, `PlusToLisp`, `LiteralToLisp` | `providers/to_lisp/` and `components/expression.rs` |
| Wiring To-Lisp Handlers | `contexts/add_mult.rs` |
| Binary Operator Provider | `providers/to_lisp/binary.rs` and `contexts/add_mult_binary_op.rs` |
| Code-Based Dispatching | `contexts/add_mult_code.rs` and `dsl.rs` |
| Extending `MathExpr`, Omitting To-Lisp Implementations | `contexts/add_mult_neg.rs`, with the providers in `providers/eval/` |

The post's `ComputerRef` component and its variant dispatchers are CGP library items, documented under
[cgp/](../../../cgp/reference/components/computer.md) rather than here.

## The documents

Read the architecture first for the design, the examples for each context, and the reference to look
up an item.

- [architecture/](architecture/README.md) — the design on one page, and:
  - [dispatch-layers.md](architecture/dispatch-layers.md) — how the four contexts key their
    dispatch differently, and why each needs a context-specific dispatch wrapper.
- [reference/](reference/README.md) — every public item, grouped by family:
  - [types.md](reference/types.md) — the operator structs, `List`, and `Ident`.
  - [abstract-types-and-getters.md](reference/abstract-types-and-getters.md) — `HasMathExprType`,
    `HasLispExprType`, and `BinarySubExpression`.
  - [eval-providers.md](reference/eval-providers.md) — the five evaluation providers and
    `EvalSubtractWithNegate`.
  - [to-lisp-providers.md](reference/to-lisp-providers.md) — the four conversion providers and the
    local sub-enums they upcast from.
  - [dispatchers.md](reference/dispatchers.md) — the dispatch wrappers and the wiring keys that
    reach them.
- [examples/](examples/README.md) — one document per context:
  - [add-mult.md](examples/add-mult.md) — evaluation and conversion in two components.
  - [add-mult-binary-op.md](examples/add-mult-binary-op.md) — one conversion provider for both binary
    operators.
  - [add-mult-code.md](examples/add-mult-code.md) — both operations in one component, dispatched on
    operation and input together.
  - [add-mult-neg.md](examples/add-mult-neg.md) — the extended language, with evaluation alone.
- [testing.md](testing.md) — what the three tests and four check blocks pin, and what nothing tests.
- [issues.md](issues.md) — the confirmed defects, missing features, and housekeeping.

## Public material derived from these documents

These documents are the verified record behind page 3 of the planned
[extensible data types deep dive](../../../website/deep-dives/extensible-datatypes.md), which uses this
crate as its running code.

## How it relates to the rest of the base

The [expression interpreter](../../../examples/expression-interpreter.md) worked example teaches this
crate's patterns step by step and stands alone. The CGP ideas it applies are documented where they
belong: [extensible variants](../../../cgp/concepts/extensible-variants.md) and
[dispatching](../../../cgp/concepts/dispatching.md) for the per-variant providers, the
[dispatch combinators](../../../cgp/reference/providers/dispatch_combinators.md) for
`MatchWithValueHandlers`, [`Computer`](../../../cgp/reference/components/computer.md) for the two
computation components, and the [casts](../../../cgp/reference/traits/cast.md) for building target values
through a local enum.
