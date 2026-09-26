# Dispatchers

The dispatchers are the context-specific wrappers that route a whole language enum to the provider
for its current variant. Why the wrappers must exist, and how the contexts key their dispatch, is
explained in [dispatch layers](../architecture/dispatch-layers.md).

## `DispatchEval` and `DispatchToLisp`

`DispatchEval` and `DispatchToLisp` dispatch a language enum to the provider for its current variant,
one pair per context module.

### Definition

In `add_mult` and `add_mult_binary_op`, where the component picks the operation and `Code` is free:

```rust
#[cgp_impl(new DispatchEval)]
impl<Code> Computer<Code, MathExpr> for Interpreter {
    type Output = Value;

    fn compute(context: &Interpreter, code: PhantomData<Code>, expr: MathExpr) -> Self::Output { ... }
}

#[cgp_impl(new DispatchToLisp)]
impl<Code> ComputerRef<Code, MathExpr> for Interpreter {
    type Output = LispExpr;

    fn compute_ref(
        context: &Interpreter,
        code: PhantomData<Code>,
        expr: &MathExpr,
    ) -> Self::Output { ... }
}
```

In `add_mult_code`, where the code picks the operation, both are `ComputerRef` impls with `Code` fixed
to `Eval` and `ToLisp`, and in `add_mult_neg` there is one, `ComputerRef<Eval, MathPlusExpr>` for
`InterpreterPlus`, with `Output = i64`.

### Behavior

Each body calls `MatchWithValueHandlers` (by value) or `MatchWithValueHandlersRef` (by reference) from
the [dispatch combinators](../../../../cgp/reference/providers/dispatch_combinators.md), which extracts
the enum's current variant and hands its payload back to the context's own `Computer` or `ComputerRef`
wiring, so a `Plus` payload reaches `EvalAdd`. The impls name the concrete context, which is written
in the explicit `impl … for Interpreter` form of `#[cgp_impl]`, and fix `Output` to the context's
value or target type. Each context module declares its own pair, so the name `DispatchEval` denotes a
different struct in each module.

### Context dependencies

The context's wiring for every variant's payload type, under the same component and code.

## How the contexts reach them

Each context wires its language enum to its own wrappers with the same path keys it uses for the
operators, so the wrappers need no wiring of their own:

| Context | Key for the enum |
|---|---|
| `add_mult`, `add_mult_binary_op` | `@ComputerComponent.<Code> Code.MathExpr: DispatchEval` and `@ComputerRefComponent.<Code> Code.MathExpr: DispatchToLisp` |
| `add_mult_code` | `@ComputerRefComponent.Eval.MathExpr: DispatchEval` and `@ComputerRefComponent.ToLisp.MathExpr: DispatchToLisp` |
| `add_mult_neg` | `@ComputerRefComponent.Eval.MathPlusExpr: DispatchEval` |

The `open` statement declares no separate table types, so a compiler message about a missing entry
names the context itself and the full lookup path, such as
`ComputerComponent`, then `Code`, then `Times<MathExpr>`.

## Source

- [`contexts/`](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/expression/src/contexts) —
  the wrappers and their keys, one context per file.

## Public material derived from this

The "Dispatching Eval" and "Code-Based Dispatching" sections of page 3 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
