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

Each context's check block asserts its components for a list of `(Code, Input)` pairs. Every block
asserts evaluation of the enum, `Literal`, and `Plus`, and the three converting contexts assert
conversion of all four input types, but no block asserts evaluation of `Times`:

| Context | Evaluation checked for | Conversion checked for |
|---|---|---|
| `add_mult` | `MathExpr`, `Literal`, `Plus` | `MathExpr`, `Literal`, `Plus`, `Times` |
| `add_mult_binary_op` | `MathExpr`, `Literal`, `Plus` | `MathExpr`, `Literal`, `Plus`, `Times` |
| `add_mult_code` | `MathExpr`, `Literal`, `Plus` | `MathExpr`, `Literal`, `Plus`, `Times` |
| `add_mult_neg` | `MathPlusExpr`, `Literal`, `Plus`, `Negate`, `Minus` | none wired |

The variants are still covered, by the compiler rather than by the checks. Each context's dispatch
wrapper calls `MatchWithValueHandlers` over every variant of its enum, so a missing or broken variant
entry fails the build inside the wrapper's body even when no check names it. A probe confirmed this
on a copy of `add_mult`'s evaluation wiring with the `Times` entry removed, keeping the same check
entries:

```rust
ComputerComponent:
    UseInputDelegate<new EvalTable {
        MathExpr: DispatchEval,
        Plus<MathExpr>: EvalAdd,
        Literal<u64>: EvalLiteral,
    }>,
```

The build failed at the wrapper's `<MatchWithValueHandlers>::compute(context, code, expr)` call.
A plain `cargo build` reports eight `E0277` errors there, walking the dispatcher's chain from the
matcher down to the table, and the one that names the root cause is the missing entry:

```text
error[E0277]: the trait bound `EvalTable: DelegateComponent<Times<MathExpr>>` is not satisfied
```

`cargo cgp check` folds the chain into one `[CGP-E002]` error at the same call. It names the matcher
step that fails, the `ExtractFieldAndHandle<Symbol!("Times"), HandleFieldValue>` handler, rather
than the table.

The check on `(Eval, MathExpr)` reported nothing, because the wrapper it resolves to has no `where`
clause for the check to evaluate. So an explicit per-operator check entry is what moves such an error
to the wiring site, and that is all the missing `Times` entries lose.

## What is untested

These have no test, and the first two were exercised by a probe for these documents instead:

- **Two whole contexts** — `add_mult_binary_op` and `add_mult_code` have no test. A probe evaluated
  and converted `2 * (3 + 4)` through each and got `14` and `(* 2 (+ 3 4))`, so `BinaryOpToLisp` and
  the code-keyed bundles work, but nothing in the repository pins it.
- **The dispatch wrappers' necessity** — nothing records that wiring `MatchWithValueHandlers`
  directly overflows; a probe did, as [dispatch layers](architecture/dispatch-layers.md) records.
- **`EvalSubtractWithNegate`** — never wired, so never run.
- **The `classic` module** — its `eval` and `expr_to_string` have no test.
- **Compile failures** — there are no compile-fail tests.

## Public material derived from this

None yet.
