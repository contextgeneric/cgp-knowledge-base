# `add_mult_code`

The base interpreter with both operations served by one component, `ComputerRef`, and chosen by the
operation code: the context dispatches on the input type first and on the `Eval` or `ToLisp` code
second.

- **Source** — [contexts/add_mult_code.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult_code.rs)
- **Run** — no test; the context is exercised only by its check block
- **Needs** — nothing
- **Result** — compiles and passes its check. A probe evaluated `2 * (3 + 4)` to `14` and converted it
  to `(* 2 (+ 3 4))`, both by reference

## The context and its wiring

`Interpreter` wires only `ComputerRefComponent`, keyed by input type, and each entry is a
[per-operator bundle](../reference/dispatchers.md#the-per-operator-bundles) that keys a second table by
code:

```rust
delegate_components! {
    Interpreter {
        MathExprTypeProviderComponent:
            UseType<MathExpr>,
        LispExprTypeProviderComponent:
            UseType<LispExpr>,
        ComputerRefComponent:
            UseInputDelegate<
                new ExprComputerComponents {
                    MathExpr: HandleMathExpr,
                    Literal<Value>: HandleLiteral,
                    Plus<MathExpr>: HandlePlus,
                    Times<MathExpr>: HandleTimes,
                }
            >,
    }
}
```

`HandlePlus` routes `Eval` to `EvalAdd` and `ToLisp` to `BinaryOpToLisp<Symbol!("+")>`, and the other
bundles follow the same shape. Because evaluation now runs through `ComputerRef`, it uses the
by-reference impls of the evaluation providers. The dispatch wrappers fix their code:
`DispatchEval` implements `ComputerRef<Eval, MathExpr>` and `DispatchToLisp` implements
`ComputerRef<ToLisp, MathExpr>`, and `HandleMathExpr` routes each code to its wrapper.

## What the checks pin

The `check_components!` block asserts `ComputerRefComponent` for evaluation of `MathExpr`, `Literal`,
and `Plus`, and for conversion of all four input types. Nothing runs the context at test time.

## What it demonstrates

- Dispatch on two parameters, input then code, through aggregate providers: see
  [dispatch layers](../architecture/dispatch-layers.md#three-arrangements).
- Operations selected by a type-level code rather than by which component is called: see the
  [`Eval` and `ToLisp` codes](../reference/README.md#other-items).

## Known issues

- **Legacy wiring** — the two layers of nested tables are the case the `open` statement simplifies
  most, to one key per input and code, such as `@ComputerRefComponent.Eval.Plus<MathExpr>: EvalAdd`.
  A probe of that form compiled, passed a check that includes `Times`, and produced the same results;
  see [issues.md](../issues.md#modernization).
- **No test, and the check skips `Times` evaluation** — see
  [issues.md](../issues.md#missing-features).

## Public material derived from this

The "Code-Based Dispatching" section of page 3 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
