# `add_mult_neg`

The extended language: an `InterpreterPlus` context that evaluates `MathPlusExpr`, which adds `Minus`
and `Negate` to the base operators and uses `i64` literals, and wires no conversion to Lisp at all.

- **Source** — [contexts/add_mult_neg.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult_neg.rs)
- **Run** — `cargo test -p cgp-example-expression add_mult_neg::`
- **Needs** — nothing
- **Result** — `test_add_mult_neg` passes

## The context and its wiring

`InterpreterPlus` wires only `ComputerRefComponent`, keyed by code first and by input second, with one
code, `Eval`:

```rust
delegate_components! {
    InterpreterPlus {
        ComputerRefComponent:
            UseDelegate<new CodeComponents {
                Eval: UseInputDelegate<new EvalComponents {
                    MathPlusExpr: DispatchEval,
                    Plus<MathPlusExpr>: EvalAdd,
                    Times<MathPlusExpr>: EvalMultiply,
                    Literal<Value>: EvalLiteral,
                    Minus<MathPlusExpr>: EvalSubtract,
                    Negate<MathPlusExpr>: EvalNegate,
                }>,
            }>
    }
}
```

`EvalAdd`, `EvalMultiply`, and `EvalLiteral` are the same providers the base contexts use, now at
`MathPlusExpr` and `i64`. The two new operators get `EvalSubtract` and `EvalNegate`, which implement
`ComputerRef` only, so the whole context evaluates by reference. Its `DispatchEval` implements
`ComputerRef<Eval, MathPlusExpr>` with `Output = i64`.

The context binds neither abstract type and wires no `ToLisp` entry. It needs neither: wiring is
checked only where it is used, so the evaluator compiles and runs with conversion left out.

## What the tests check

`test_add_mult_neg` evaluates `2 + 3` to `5`, `2 * 3` to `6`, `2 - 3` to `-1`, and `-2 * (3 + 4)` to
`-14`, all by reference with the `Eval` code. The `check_components!` block asserts evaluation of
`MathPlusExpr`, `Literal`, `Plus`, `Negate`, and `Minus`.

## What it demonstrates

- Extending a language with new variants while reusing every existing provider unchanged: see
  [evaluation providers](../reference/eval-providers.md).
- Leaving an operation unimplemented for a new language, relying on lazy wiring: see
  [check traits](../../../../cgp/concepts/check-traits.md).
- Dispatch on code first and input second: see
  [dispatch layers](../architecture/dispatch-layers.md#three-arrangements).

## Known issues

- **Legacy wiring** — both layers are nested tables; see [issues.md](../issues.md#modernization).
- **`EvalSubtractWithNegate` is not wired here** — the alternative subtraction provider implements
  `Computer`, which this context does not wire; see
  [evaluation providers](../reference/eval-providers.md#evalsubtractwithnegate).

## Public material derived from this

The "Extending `MathExpr`" and "Omitting To-Lisp Implementations" sections of page 3 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
