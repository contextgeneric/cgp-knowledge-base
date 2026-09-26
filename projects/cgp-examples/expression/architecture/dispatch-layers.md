# Dispatch layers

Every `expression` context routes a computation by the type of its input, and two of them also route
by the operation, which the four contexts express with the `open` statement in two ways. This
document records both arrangements and the one piece every context needs: a context-specific wrapper
that dispatches the whole language enum. The general technique of dispatching a component per type,
including the path-key forms used here, is in
[dispatching per type](../../../../cgp/guides/dispatching-per-type.md).

## Two arrangements

The contexts differ in which components they use and how many segments their keys fix:

| Context | Components | Keys |
|---|---|---|
| `add_mult`, `add_mult_binary_op` | `Computer` for evaluation, `ComputerRef` for conversion | input only; the component itself picks the operation |
| `add_mult_code`, `add_mult_neg` | `ComputerRef` for every operation | operation code and input together |

In the first arrangement the operation is decided by which component is called. `Interpreter` opens
both components and keys each entry by input with a per-entry generic `Code`, so `compute` evaluates
and `compute_ref` converts, and whatever code the caller passes is ignored:

```rust
open { ComputerComponent, ComputerRefComponent };

@ComputerComponent.<Code> Code.MathExpr: DispatchEval,
@ComputerComponent.<Code> Code.Plus<MathExpr>: EvalAdd,
@ComputerComponent.<Code> Code.Times<MathExpr>: EvalMultiply,
@ComputerComponent.<Code> Code.Literal<Value>: EvalLiteral,
```

In the second, one component serves every operation, so the code must pick. `add_mult_code` fixes the
code in each key's first segment, giving each operator one entry per operation:

```rust
@ComputerRefComponent.Eval.Plus<MathExpr>: EvalAdd,
@ComputerRefComponent.ToLisp.Plus<MathExpr>: BinaryOpToLisp<Symbol!("+")>,
```

`add_mult_neg` uses the same form with only the `Eval` code, so adding conversion to the extended
language would be a second group of `ToLisp` keys beside the first. Within one context, a code is
keyed per input throughout and never also on its own, since a shorter key would cover every longer
key beneath it.

All of these resolve at compile time, so the choice affects only how the wiring reads and which
component a caller invokes for which operation.

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
that recursion part of the trait resolution itself. A probe wired `add_mult`'s evaluation keys that
way on its own context, `Interp`, and evaluated a `Plus`:

```rust
@ComputerComponent.<Code> Code.MathExpr: MatchWithValueHandlers,
@ComputerComponent.<Code> Code.Plus<MathExpr>: EvalAdd,
@ComputerComponent.<Code> Code.Times<MathExpr>: EvalMultiply,
@ComputerComponent.<Code> Code.Literal<u64>: EvalLiteral,
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
  — the two arrangements and each context's wrappers.
- [`dsl.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/dsl.rs) — the
  `Eval` and `ToLisp` codes.

## Public material derived from this

The "Dispatching Eval" and "Code-Based Dispatching" sections of page 3 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
