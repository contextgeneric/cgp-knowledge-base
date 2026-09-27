# `add_mult_neg`

The extended language: an `InterpreterPlus` context that evaluates `MathPlusExpr`, which adds `Minus`
and `Negate` to the base operators and uses `i64` literals, and wires no conversion to Lisp at all.

- **Source**: [contexts/add_mult_neg.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult_neg.rs)
- **Run**: `cargo test -p cgp-example-expression add_mult_neg::`
- **Needs**: nothing
- **Result**: `test_add_mult_neg` passes

## The context and its wiring

`InterpreterPlus` opens only `ComputerRefComponent`, and every key fixes the one code it wires,
`Eval`, along with the input:

```rust
delegate_components! {
    InterpreterPlus {
        open ComputerRefComponent;

        @ComputerRefComponent.Eval.MathPlusExpr: DispatchEval,
        @ComputerRefComponent.Eval.Plus<MathPlusExpr>: EvalAdd,
        @ComputerRefComponent.Eval.Times<MathPlusExpr>: EvalMultiply,
        @ComputerRefComponent.Eval.Literal<Value>: EvalLiteral,
        @ComputerRefComponent.Eval.Minus<MathPlusExpr>: EvalSubtract,
        @ComputerRefComponent.Eval.Negate<MathPlusExpr>: EvalNegate,
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
all six input types.

## What it demonstrates

- Extending a language with new variants while reusing every existing provider unchanged: see
  [evaluation providers](../reference/eval-providers.md).
- Leaving an operation unimplemented for a new language, relying on lazy wiring: see
  [check traits](../../../../cgp/concepts/check-traits.md).
- Dispatch keyed on the code and the input together: see
  [dispatch layers](../architecture/dispatch-layers.md#two-arrangements).

## Known issues

- **`EvalSubtractWithNegate` is not wired here**: the alternative subtraction provider implements
  `Computer`, which this context does not wire; see
  [evaluation providers](../reference/eval-providers.md#evalsubtractwithnegate).

## Try a change

Asking for conversion is the change the public page shows. A probe copied the module, added `ToLisp`
to its `dsl` import, and added `(ToLisp, MathPlusExpr)` to its check block. `cargo cgp check` built
from the `cargo-cgp` source at commit `b6a6323` reported:

```text
error[E0277]: [CGP-E001] the consumer trait `CanComputeRef<ToLisp, MathPlusExpr>` is not implemented for context `InterpreterPlus`
   = note: root cause: [CGP-E107] context `InterpreterPlus` does not contain any delegate entry for `@ComputerRefComponent.ToLisp.MathPlusExpr`
```

A call to `compute_ref` with `ToLisp`, without the check, reports the same root cause as a missing
`@ComputerRefComponent.ToLisp`, with the input type shown as `_`, which is why the page uses the
check.

## Public material derived from this

The `expression/examples/add-mult-neg` page of the [cgp-examples project
section](../../../../website/projects/cgp-examples.md), including its change to try.
