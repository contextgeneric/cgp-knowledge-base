# Dispatch layers

Every `expression` context routes a computation by the type of its input, and two of them also route
by the operation, but the four contexts nest those two layers in three different ways. This document
records each arrangement and the one piece every arrangement needs: a context-specific wrapper that
dispatches the whole language enum. The general technique of dispatching a component per type is in
[dispatching per type](../../../../cgp/guides/dispatching-per-type.md), which shows the `open` form
this crate does not yet use.

## Three arrangements

The contexts differ in which components they use and how they key them:

| Context | Components | Layers |
|---|---|---|
| `add_mult`, `add_mult_binary_op` | `Computer` for evaluation, `ComputerRef` for conversion | input only, one table per component; the component itself picks the operation |
| `add_mult_code` | `ComputerRef` for both | input first, then operation, through a bundle per operator |
| `add_mult_neg` | `ComputerRef` for evaluation | operation first, then input |

In the first arrangement the operation is decided by which component is called. `Interpreter` wires
`ComputerComponent` and `ComputerRefComponent` to separate `UseInputDelegate` tables, so
`compute` evaluates and `compute_ref` converts, and the `Code` passed in is ignored:

```rust
ComputerComponent:
    UseInputDelegate<
        new EvalComponents {
            MathExpr: DispatchEval,
            Plus<MathExpr>: EvalAdd,
            Times<MathExpr>: EvalMultiply,
            Literal<Value>: EvalLiteral,
        }
    >,
```

In the second, one component serves both operations, so the code must pick. `add_mult_code` keys its
`ComputerRefComponent` table by input type, and each entry is a bundle, such as `HandlePlus`, that keys
a second table by the `Eval` or `ToLisp` code:

```rust
delegate_components! {
    new HandlePlus {
        ComputerRefComponent: UseDelegate<
            new PlusHandlers {
                Eval: EvalAdd,
                ToLisp: BinaryOpToLisp<Symbol!("+")>,
            }>
    }
}
```

The bundles are [aggregate providers](../../../../cgp/concepts/aggregate-providers.md): `HandlePlus`,
`HandleTimes`, `HandleLiteral`, and `HandleMathExpr` are delegated to and never used as contexts, so
each operator's two operations are grouped where the operator is wired.

In the third, `add_mult_neg` reverses the order. `InterpreterPlus` keys an outer `UseDelegate` table by
code, with one entry, `Eval`, whose value is a `UseInputDelegate` table by input. Adding conversion to
the extended language would be a second entry in the outer table, grouping the wiring by operation
rather than by operator.

All three resolve at compile time, so the choice affects only how the wiring reads and where a new
operator or a new operation is added.

## The dispatch wrapper for the whole enum

Each context maps its language enum, such as `MathExpr`, to a small provider written for that
context alone, rather than to the dispatcher that does the work:

```rust
#[cgp_impl(new DispatchEval)]
impl<Code> Computer<Code, MathExpr> for Interpreter {
    type Output = Value;

    fn compute(context: &Interpreter, code: PhantomData<Code>, expr: MathExpr) -> Self::Output {
        <MatchWithValueHandlers>::compute(context, code, expr)
    }
}
```

The wrapper is required. `MatchWithValueHandlers` finds the variant and hands its payload back to the
context, which dispatches it to `EvalAdd` or another operator provider, and those providers recurse
into the context for `MathExpr` again. Wiring the dispatcher directly as the `MathExpr` entry makes
that recursion part of the trait resolution itself. A probe wired `add_mult`'s evaluation table that
way on its own context, `Interp`, and evaluated a `Plus`:

```rust
ComputerComponent:
    UseInputDelegate<new EvalTable {
        MathExpr: MatchWithValueHandlers,
        Plus<MathExpr>: EvalAdd,
        Times<MathExpr>: EvalMultiply,
        Literal<u64>: EvalLiteral,
    }>,
```

The build failed on the recursion limit, because proving `Interp` can evaluate a `MathExpr` requires
proving it can evaluate each operand, which is again a `MathExpr`. `cargo cgp check` reports the
cycle at the `compute` call:

```text
error[E0275]: overflow evaluating the requirement `<Interp as CanCompute<Eval, MathExpr>>::Output == _`
error[E0275]: overflow evaluating the requirement `Interp: CanCompute<Eval, MathExpr>`
```

A plain `cargo build` reports a single `E0275` from inside the cycle instead, on the requirement
`EvalAdd: Computer<Interp, Eval, Plus<MathExpr>>`.

What breaks the loop is that the wrapper's impl has no `where` clause. It names the concrete context
and a concrete `Output` and bounds nothing, so the compiler can accept
`Interpreter: CanCompute<Code, MathExpr>` from the impl header alone, and resolves the dispatcher only
when it type-checks the body. Two probes point at the `where` clause as the difference. Each kept the
wrapper and moved the dispatcher's requirement into a `where` clause, once on a wrapper generic over
the context and once on the concrete context:

```rust
#[cgp_impl(new ConcreteWhereDispatch)]
impl<Code> Computer<Code, MathExpr> for Interp
where
    MatchWithValueHandlers: Computer<Interp, Code, MathExpr, Output = u64>,
{
    type Output = u64;

    fn compute(context: &Interp, code: PhantomData<Code>, expr: MathExpr) -> u64 { ... }
}
```

In both, `rustc` was still compiling the probe after ten minutes and had reported nothing, while the
same wrapper without the `where` clause builds normally. That is evidence for the explanation rather
than proof of it, since a probe that never finishes does not say why.

The price of the wrapper is one per context and per operation, fixed to that context's types: each
context module defines its own `DispatchEval` and, where it converts, `DispatchToLisp`. In
`add_mult_code` and `add_mult_neg` the wrappers also fix `Code` to `Eval` or `ToLisp`, because there
the code selects the operation.

## Source

- [`contexts/add_mult.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult.rs),
  [`add_mult_binary_op.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult_binary_op.rs),
  [`add_mult_code.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult_code.rs),
  and [`add_mult_neg.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult_neg.rs)
  — the four arrangements and their wrappers.
- [`dsl.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/dsl.rs) — the
  `Eval` and `ToLisp` codes.

## Public material derived from this

The "Dispatching Eval" and "Code-Based Dispatching" sections of page 3 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
