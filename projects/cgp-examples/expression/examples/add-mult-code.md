# `add_mult_code`

The base interpreter with both operations served by one component, `ComputerRef`, and chosen by the
operation code: each wiring key names the `Eval` or `ToLisp` code and the input type together.

- **Source** — [contexts/add_mult_code.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult_code.rs)
- **Run** — no test; the context is exercised only by its check block
- **Needs** — nothing
- **Result** — compiles and passes its check. A probe evaluated `2 * (3 + 4)` to `14` and converted it
  to `(* 2 (+ 3 4))`, both by reference

## The context and its wiring

`Interpreter` opens only `ComputerRefComponent`, and each key fixes both the code and the input, so
every operator has one entry per operation:

```rust
delegate_components! {
    Interpreter {
        open ComputerRefComponent;

        MathExprTypeProviderComponent:
            UseType<MathExpr>,
        LispExprTypeProviderComponent:
            UseType<LispExpr>,

        @ComputerRefComponent.Eval.MathExpr: DispatchEval,
        @ComputerRefComponent.Eval.Literal<Value>: EvalLiteral,
        @ComputerRefComponent.Eval.Plus<MathExpr>: EvalAdd,
        @ComputerRefComponent.Eval.Times<MathExpr>: EvalMultiply,

        @ComputerRefComponent.ToLisp.MathExpr: DispatchToLisp,
        @ComputerRefComponent.ToLisp.Literal<Value>: LiteralToLisp,
        @ComputerRefComponent.ToLisp.Plus<MathExpr>: BinaryOpToLisp<Symbol!("+")>,
        @ComputerRefComponent.ToLisp.Times<MathExpr>: BinaryOpToLisp<Symbol!("*")>,
    }
}
```

Because evaluation runs through `ComputerRef`, it uses the by-reference impls of the evaluation
providers. The dispatch wrappers fix their code to match their keys: `DispatchEval` implements
`ComputerRef<Eval, MathExpr>` and `DispatchToLisp` implements `ComputerRef<ToLisp, MathExpr>`.

## What the checks pin

The `check_components!` block asserts `ComputerRefComponent` for evaluation and conversion of all four
input types. Nothing runs the context at test time.

## What it demonstrates

- Dispatch on two parameters at once, with a concrete segment for each: see
  [dispatch layers](../architecture/dispatch-layers.md#two-arrangements).
- Operations selected by a type-level code rather than by which component is called: see the
  [`Eval` and `ToLisp` codes](../reference/README.md#other-items).

## Known issues

- **No test** — the probe result above is the only runtime evidence; see
  [testing.md](../testing.md).

## The test the public page gives

The public page runs this context with an integration test the reader saves as
`expression/tests/code.rs`, which builds `2 * (3 + 4)`, converts it with `ToLisp`, and evaluates it
with `Eval`, printing each result. A probe ran the same test from a crate with a path dependency on
this one, and it printed `14` and then the Lisp tree:

```text
List(List([Ident(Ident("*")), Literal(Literal(2)), List(List([Ident(Ident("+")), Literal(Literal(3)), Literal(Literal(4))]))]))
```

With the line `@ComputerRefComponent.ToLisp.Plus<MathExpr>: BinaryOpToLisp<Symbol!("+")>` removed
from a copy of the module, `cargo cgp check` built from the `cargo-cgp` source at commit `b6a6323`
reported the change the public page shows:

```text
error[E0277]: [CGP-E001] the consumer trait `CanComputeRef<ToLisp, Plus<MathExpr>>` is not implemented for context `Interpreter`
   = note: root cause: [CGP-E107] context `Interpreter` does not contain any delegate entry for `@ComputerRefComponent.ToLisp.Plus<MathExpr>`
```

Two `E0271` errors followed at the `ToLisp` wrapper's call to `MatchWithValueHandlersRef`.

## Public material derived from this

The `expression/examples/add-mult-code` page of the [cgp-examples project
section](../../../../website/projects/cgp-examples.md), including its test and its change to try.
