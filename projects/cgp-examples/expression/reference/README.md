# `expression` reference

This directory documents every public item in the `expression` crate, grouped by family, with one
document per family following the entry template in
[../../../AGENTS.md](../../../AGENTS.md#reference-entries). The tables below list every item so a
reader can find one by what it handles and see which contexts wire it. Read the
[architecture](../architecture/README.md) first for how the families fit together.

## Providers

Every provider is written with `#[cgp_impl]` and implements `Computer`, `ComputerRef`, or both for one
input type. The last column is what the provider requires of the context.

| Provider | Input | Implements | Wired in | Requires of the context |
|---|---|---|---|---|
| [`EvalAdd`](eval-providers.md#evaladd) | `Plus<E>` | both | all four contexts | evaluation of `E` to an `Add` output |
| [`EvalMultiply`](eval-providers.md#evalmultiply) | `Times<E>` | both | all four contexts | evaluation of `E` to a `Mul` output |
| [`EvalLiteral`](eval-providers.md#evalliteral) | `Literal<T>` | both | all four contexts | nothing; `T: Clone` by reference |
| [`EvalSubtract`](eval-providers.md#evalsubtract) | `Minus<E>` | `ComputerRef` | `add_mult_neg` | evaluation of `E` to a `Sub` output |
| [`EvalNegate`](eval-providers.md#evalnegate) | `Negate<E>` | `ComputerRef` | `add_mult_neg` | evaluation of `E` to a `Neg` output |
| [`EvalSubtractWithNegate`](eval-providers.md#evalsubtractwithnegate) | `Minus<E>` | `Computer` | nothing | evaluation of `Plus<E>`, and a `Negate` variant in `E` |
| [`PlusToLisp`](to-lisp-providers.md#plustolisp-and-timestolisp) | `Plus<E>` | `ComputerRef` | `add_mult` | `HasLispExprType`, and conversion of `E` |
| [`TimesToLisp`](to-lisp-providers.md#plustolisp-and-timestolisp) | `Times<E>` | `ComputerRef` | `add_mult` | `HasLispExprType`, and conversion of `E` |
| [`LiteralToLisp`](to-lisp-providers.md#literaltolisp) | `Literal<T>` | `ComputerRef` | the three converting contexts | `HasLispExprType` |
| [`BinaryOpToLisp<Operator>`](to-lisp-providers.md#binaryoptolisp) | any `BinarySubExpression` | `ComputerRef` | `add_mult_binary_op`, `add_mult_code` | `HasMathExprType`, `HasLispExprType`, and conversion of the operands |
| [`DispatchEval`](dispatchers.md#dispatcheval-and-dispatchtolisp) | the language enum | varies by context | each context, its own | the context's evaluation wiring for every variant |
| [`DispatchToLisp`](dispatchers.md#dispatcheval-and-dispatchtolisp) | the language enum | `ComputerRef` | the three converting contexts, each its own | the context's conversion wiring for every variant |

## Other items

The remaining items are the types, the abstract-type components, the getter, and the contexts.

| Item | Kind | Module |
|---|---|---|
| [`Plus`, `Times`, `Minus`, `Negate`, `Literal`](types.md) | operator structs | `types` |
| [`List`, `Ident`](types.md#list-and-ident) | Lisp target structs | `types` |
| [`MathExpr`, `LispExpr`, `MathPlusExpr`, `Value`](types.md#the-language-enums) | language enums and value alias | each `contexts` module |
| [`Expr`, `eval`, `expr_to_string`](types.md#the-language-enums) | the closed interpreter | `classic::add_mult` |
| [`HasMathExprType`, `HasLispExprType`](abstract-types-and-getters.md) | `#[cgp_type]` components | `components` |
| [`BinarySubExpression`](abstract-types-and-getters.md#binarysubexpression) | `#[cgp_auto_getter]` trait | `providers` |
| `Eval`, `ToLisp` | operation codes | `dsl` |
| [`Interpreter`, `InterpreterPlus`](../examples/README.md) | contexts | each `contexts` module |

The `providers`, `types`, and `components` modules re-export their files with glob imports, while
each context is reached through its module path, such as
`cgp_example_expression::contexts::add_mult::Interpreter`.

## The catalog

- [types.md](types.md) — the operator structs, the Lisp target structs, and the language enums.
- [abstract-types-and-getters.md](abstract-types-and-getters.md) — `HasMathExprType`,
  `HasLispExprType`, and `BinarySubExpression`.
- [eval-providers.md](eval-providers.md) — the six evaluation providers.
- [to-lisp-providers.md](to-lisp-providers.md) — the four conversion providers.
- [dispatchers.md](dispatchers.md) — the dispatch wrappers and the wiring keys that reach them.

## Public material derived from this

The crate's rustdoc, which the source does not carry.
