# `add_mult`

The base interpreter: an `Interpreter` context that evaluates the `Plus`/`Times`/`Literal` language
by value and converts it to Lisp by reference, keying each operation's providers by input.

- **Source**:
  [contexts/add_mult.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult.rs)
- **Run**: `cargo test -p cgp-example-expression add_mult::`
- **Needs**: nothing
- **Result**: `test_add_mult` and `test_add_mult_to_lisp` pass

## The context and its wiring

`Interpreter` is an empty struct. Its wiring binds the two abstract types and gives each operation
its own component, opened for per-input dispatch, so the operation is chosen by calling `compute` or
`compute_ref`:

```rust
delegate_components! {
    Interpreter {
        open { ComputerComponent, ComputerRefComponent };

        MathExprTypeProviderComponent:
            UseType<MathExpr>,
        LispExprTypeProviderComponent:
            UseType<LispExpr>,

        @ComputerComponent.<Code> Code.MathExpr: DispatchEval,
        @ComputerComponent.<Code> Code.Plus<MathExpr>: EvalAdd,
        @ComputerComponent.<Code> Code.Times<MathExpr>: EvalMultiply,
        @ComputerComponent.<Code> Code.Literal<Value>: EvalLiteral,

        @ComputerRefComponent.<Code> Code.MathExpr: DispatchToLisp,
        @ComputerRefComponent.<Code> Code.Literal<Value>: LiteralToLisp,
        @ComputerRefComponent.<Code> Code.Plus<MathExpr>: PlusToLisp,
        @ComputerRefComponent.<Code> Code.Times<MathExpr>: TimesToLisp,
    }
}
```

Each key's first segment is a per-entry generic `Code`, so the entry matches whatever code the
caller passes and dispatches on the input alone.

The `MathExpr` entries go to the module's own
[`DispatchEval` and `DispatchToLisp`](../reference/dispatchers.md#dispatcheval-and-dispatchtolisp),
which are also generic over `Code`. `MathExprTypeProviderComponent` is wired although no provider in
this context reads it; the next two contexts need it for `BinaryOpToLisp`.

## What the tests check

`test_add_mult` evaluates `2 + 3` to `5`, `2 * 3` to `6`, and `2 * (3 + 4)` to `14`, all by value
with the `Eval` code. `test_add_mult_to_lisp` converts the same three expressions with the `ToLisp`
code and compares the trees, so `2 * (3 + 4)` must become `(* 2 (+ 3 4))`. The module's
`check_components!` block asserts both evaluation and conversion of all four input types.

## What it demonstrates

- One provider per operator, composed by input-keyed wiring: see
  [evaluation providers](../reference/eval-providers.md).
- Building a target enum from a local sub-enum: see
  [conversion providers](../reference/to-lisp-providers.md).
- The dispatch wrapper for the whole enum: see
  [dispatch layers](../architecture/dispatch-layers.md#the-dispatch-wrapper-for-the-whole-enum).

## Try a change

Removing the evaluation entry for `Times` is the change the public page shows. A probe copied the
module into a crate with a path dependency on this one, dropped the line
`@ComputerComponent.<Code> Code.Times<MathExpr>: EvalMultiply`, and kept the full check block, then
ran `cargo cgp check` built from the `cargo-cgp` source at commit `b6a6323`:

```text
error[E0277]: [CGP-E001] the consumer trait `CanCompute<Eval, Times<MathExpr>>` is not implemented for context `Interpreter`
   = note: root cause: [CGP-E107] context `Interpreter` does not contain any delegate entry for `@ComputerComponent.Eval.Times<MathExpr>`
```

A second error, `[CGP-E002]`, lands at the wrapper's `<MatchWithValueHandlers>::compute` call,
naming the dispatcher's step for `Times`; this is the check-and-wrapper pair
[testing.md](../testing.md#what-the-checks-pin) records on a reduced context.

## Public material derived from this

The `expression/examples/add-mult` page of the
[cgp-examples project section](../../../../website/projects/cgp-examples.md), including its change
to try.
