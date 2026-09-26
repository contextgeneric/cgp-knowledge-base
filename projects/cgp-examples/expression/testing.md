# Testing

`expression` has three unit tests, in two of its four context modules, and one `check_components!`
block per context. On the `v0.8.0` branch `cargo test -p cgp-example-expression` passes all three.
This document records what the tests and checks pin and what nothing exercises.

## What the tests pin

The tests evaluate or convert a few fixed expressions and assert the exact result:

| Test | Context | Asserts |
|---|---|---|
| `test_add_mult` | `add_mult` | `2 + 3`, `2 * 3`, and `2 * (3 + 4)` evaluate by value to `5`, `6`, and `14` |
| `test_add_mult_to_lisp` | `add_mult` | the same three convert to the expected `LispExpr` trees, compared with `==` |
| `test_add_mult_neg` | `add_mult_neg` | `2 + 3`, `2 * 3`, `2 - 3`, and `-2 * (3 + 4)` evaluate by reference to `5`, `6`, `-1`, and `-14` |

So the tests run evaluation by value through `Computer`, conversion through `PlusToLisp`,
`TimesToLisp`, and `LiteralToLisp`, and evaluation by reference through `ComputerRef` for all five
operators.

## What the checks pin

Each context's check block asserts its components for a list of `(Code, Input)` pairs, and every
block lists every input type for each operation the context wires:

| Context | Evaluation checked for | Conversion checked for |
|---|---|---|
| `add_mult` | `MathExpr`, `Literal`, `Plus`, `Times` | `MathExpr`, `Literal`, `Plus`, `Times` |
| `add_mult_binary_op` | `MathExpr`, `Literal`, `Plus`, `Times` | `MathExpr`, `Literal`, `Plus`, `Times` |
| `add_mult_code` | `MathExpr`, `Literal`, `Plus`, `Times` | `MathExpr`, `Literal`, `Plus`, `Times` |
| `add_mult_neg` | `MathPlusExpr`, `Literal`, `Plus`, `Times`, `Negate`, `Minus` | none wired |

The per-operator entries are what report a broken operator entry at the wiring site. The entry for
the enum alone would not: it resolves to the dispatch wrapper, which has no `where` clause for the
check to evaluate. A broken operator entry fails the build whether or not it is checked, because the
wrapper's body calls `MatchWithValueHandlers` over every variant, but without its check entry the
only error lands in the wrapper. A probe showed this on a copy of `add_mult`'s evaluation wiring with
the `Times` key removed and only the enum, `Literal`, and `Plus` checked:

```rust
@ComputerComponent.<Code> Code.MathExpr: DispatchEval,
@ComputerComponent.<Code> Code.Plus<MathExpr>: EvalAdd,
@ComputerComponent.<Code> Code.Literal<u64>: EvalLiteral,
```

The checks passed, and the build failed at the wrapper's
`<MatchWithValueHandlers>::compute(context, code, expr)` call. A plain `cargo build` reports eight
`E0277` errors there, walking the dispatcher's chain from the matcher down to the context, and the
one that names the root cause is the missing entry:

```text
error[E0277]: the trait bound `Interp: DelegateComponent<PathCons<ComputerComponent, ...>>` is not satisfied
```

Its `help` note spells out the elided path as `ComputerComponent`, then `Code`, then
`Times<MathExpr>`. `cargo cgp check` folds the chain into one `[CGP-E002]` error at the same call,
naming the matcher step for `Times` that fails.

Adding `(Eval, Times<MathExpr>)` to the probe's check block kept the wrapper's error and added one at
the check line, which `cargo cgp check` reports in terms of the component rather than the matcher:

```text
error[E0277]: [CGP-E001] the consumer trait `CanCompute<Eval, Times<MathExpr>>` is not implemented for context `Interp`
```

## What is untested

These have no test, and the first two were exercised by a probe for these documents instead:

- **Two whole contexts** — `add_mult_binary_op` and `add_mult_code` have no test. A probe evaluated
  and converted `2 * (3 + 4)` through each and got `14` and `(* 2 (+ 3 4))`, so `BinaryOpToLisp` and
  the code-keyed wiring work, but nothing in the repository pins it.
- **The dispatch wrappers' necessity** — nothing records that wiring `MatchWithValueHandlers`
  directly overflows; a probe did, as [dispatch layers](architecture/dispatch-layers.md) records.
- **`EvalSubtractWithNegate`** — never wired, so never run.
- **The `classic` module** — its `eval` and `expr_to_string` have no test.
- **Compile failures** — there are no compile-fail tests.

## Public material derived from this

None yet.
