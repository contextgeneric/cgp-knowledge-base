# `expression` architecture

`expression` follows a small set of decisions that every provider and context in it shares, stated
together here so the whole design fits on one page. The patterns behind them are taught in the
[expression interpreter](../../../../examples/expression-interpreter.md) worked example, so this page
says only what the crate does with them.

## The design on one page

**Each operator is its own type, generic over the expression it nests.** `Plus<Expr>`,
`Times<Expr>`, `Minus<Expr>`, and `Negate<Expr>` hold boxed sub-expressions of the `Expr` type
parameter, and `Literal<T>` holds a value of any type. The recursion is closed only in the language
enum, which instantiates each operator at itself, such as `Plus(Plus<MathExpr>)`. So one operator
struct, and every provider written for it, serves every language that uses it. See
[types](../reference/types.md).

**Each operation is one provider per operator.** Evaluation is `EvalAdd`, `EvalMultiply`,
`EvalLiteral`, `EvalSubtract`, and `EvalNegate`, and conversion to Lisp is `PlusToLisp`,
`TimesToLisp`, `LiteralToLisp`, or the generic `BinaryOpToLisp<Operator>`. A provider handles one
operator and recurses into its operands through the context, so it never names the language enum or
the other operators. See [evaluation providers](../reference/eval-providers.md) and
[conversion providers](../reference/to-lisp-providers.md).

**The two operations use the two computation components.** Evaluation consumes its input through
`Computer`, conversion borrows it through `ComputerRef`, and the evaluation providers implement both,
so a context that evaluates by reference reuses them. The `Code` parameter both components carry is
free in the providers, and a context either ignores it or fixes it to the `Eval` and `ToLisp`
markers in `dsl.rs` to select the operation. See [dispatch layers](dispatch-layers.md).

**Output types are abstract where a provider must build one.** The conversion providers construct
`LispExpr` values without naming the enum: the context supplies it through `HasLispExprType`, which
each provider imports with `#[use_type]`, and a provider builds only the variants it needs in a small
local enum and upcasts it into the full type. `BinaryOpToLisp` imports the context's `MathExpr`
through `HasMathExprType` the same way. See
[abstract types and getters](../reference/abstract-types-and-getters.md).

**A context dispatches on the input type, and wraps the dispatcher for the whole enum.** Each
context opens its computation components and maps every operator type to its provider with a path
key, and maps the language enum to a context-specific wrapper such as `DispatchEval` that calls
`MatchWithValueHandlers`. The wrapper is required: wiring the
dispatcher directly makes the compiler overflow. See [dispatch layers](dispatch-layers.md) and
[dispatchers](../reference/dispatchers.md).

**Contexts are independent and data-free.** Each context is an empty struct in its own module, with
its own copies of the enums, and none shares wiring with another. Extending the language is a new
context and a new enum next to the old ones, reusing the operator providers unchanged. See the
[examples](../examples/README.md).

## The documents

- [dispatch-layers.md](dispatch-layers.md) — the two ways the contexts key their dispatch on input
  and operation, and the overflow the dispatch wrappers prevent.

## Public material derived from this

Page 3 of the planned [extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
