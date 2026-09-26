# Evaluation providers

The evaluation providers compute a number from an expression, one provider per operator. Each is
generic over the context, the `Code`, and the expression type, and recurses into its operands through
the context's own evaluation, so none of them names a language enum or a numeric type. The three
base-language providers implement both [`Computer`](../../../../cgp/reference/components/computer.md) and
`ComputerRef` on one struct; the two extended-language providers implement `ComputerRef` only.

## `EvalAdd`

`EvalAdd` evaluates a `Plus` by evaluating both operands and adding the results.

### Definition

```rust
#[cgp_impl(new EvalAdd)]
#[uses(CanCompute<Code, MathExpr, Output = Output>)]
impl<Code, MathExpr, Output> Computer<Code, Plus<MathExpr>>
where
    Output: Add<Output = Output>,
{
    type Output = Output;

    fn compute(
        &self,
        code: PhantomData<Code>,
        Plus { left, right }: Plus<MathExpr>,
    ) -> Self::Output { ... }
}

#[cgp_impl(EvalAdd)]
#[uses(CanComputeRef<Code, MathExpr, Output = Output>)]
impl<Code, MathExpr, Output> ComputerRef<Code, Plus<MathExpr>>
where
    Output: Add<Output = Output>,
{
    type Output = Output;

    fn compute_ref(
        &self,
        code: PhantomData<Code>,
        Plus { left, right }: &Plus<MathExpr>,
    ) -> Self::Output { ... }
}
```

### Behavior

The by-value impl consumes the `Plus`, unboxes each operand, and calls `self.compute` on it with the
same `Code`; the by-reference impl borrows through the boxes and calls `self.compute_ref`. Both return
the sum. The output type is whatever the context evaluates the operand to, so the same provider adds
`u64` in the base language and `i64` in the extended one. The second block names the existing struct
without `new`, since the first declared it.

### Context dependencies

`CanCompute<Code, MathExpr>` or `CanComputeRef<Code, MathExpr>` for the operand type, with an `Output`
that implements `Add`.

## `EvalMultiply`

`EvalMultiply` evaluates a `Times` the same way, with multiplication.

### Definition

```rust
#[cgp_impl(new EvalMultiply)]
#[uses(CanCompute<Code, MathExpr, Output = Output>)]
impl<Code, MathExpr, Output> Computer<Code, Times<MathExpr>>
where
    Output: Mul<Output = Output>,
{
    type Output = Output;

    fn compute(&self, code: PhantomData<Code>, Times { left, right }: Times<MathExpr>) -> Output { ... }
}

#[cgp_impl(EvalMultiply)]
#[uses(CanComputeRef<Code, MathExpr, Output = Output>)]
impl<Code, MathExpr, Output> ComputerRef<Code, Times<MathExpr>>
where
    Output: Mul<Output = Output>,
{
    type Output = Output;

    fn compute_ref(
        &self,
        code: PhantomData<Code>,
        Times { left, right }: &Times<MathExpr>,
    ) -> Self::Output { ... }
}
```

### Behavior

As for `EvalAdd`, with `*` in place of `+`.

### Context dependencies

`CanCompute` or `CanComputeRef` for the operand type, with an `Output` that implements `Mul`.

## `EvalLiteral`

`EvalLiteral` evaluates a `Literal` to its value, the base case of the recursion.

### Definition

```rust
#[cgp_impl(new EvalLiteral)]
impl<Code, T> Computer<Code, Literal<T>> {
    type Output = T;

    fn compute(&self, _code: PhantomData<Code>, Literal(value): Literal<T>) -> T { ... }
}

#[cgp_impl(EvalLiteral)]
impl<Code, T> ComputerRef<Code, Literal<T>>
where
    T: Clone,
{
    type Output = T;

    fn compute_ref(&self, _code: PhantomData<Code>, Literal(value): &Literal<T>) -> T { ... }
}
```

### Behavior

The by-value impl returns the value; the by-reference impl returns a clone of it. It needs nothing
from the context, so its output type, and through the recursion every operator's output type, is the
literal's value type.

### Context dependencies

None; the by-reference impl requires `T: Clone`.

## `EvalSubtract`

`EvalSubtract` evaluates a `Minus` by subtracting the right operand from the left.

### Definition

```rust
#[cgp_impl(new EvalSubtract)]
#[uses(CanComputeRef<Code, MathExpr, Output = Output>)]
impl<Code, MathExpr, Output> ComputerRef<Code, Minus<MathExpr>>
where
    Output: Sub<Output = Output>,
{
    type Output = Output;

    fn compute_ref(
        &self,
        code: PhantomData<Code>,
        Minus { left, right }: &Minus<MathExpr>,
    ) -> Self::Output { ... }
}
```

### Behavior

It evaluates both operands by reference and returns `left - right`. It has no by-value impl, which is
why the extended language is wired only through `ComputerRef`.

### Context dependencies

`CanComputeRef<Code, MathExpr>` for the operand type, with an `Output` that implements `Sub`.

## `EvalNegate`

`EvalNegate` evaluates a `Negate` by negating its operand.

### Definition

```rust
#[cgp_impl(new EvalNegate)]
#[uses(CanComputeRef<Code, MathExpr, Output = Output>)]
impl<Code, MathExpr, Output> ComputerRef<Code, Negate<MathExpr>>
where
    Output: Neg<Output = Output>,
{
    type Output = Output;

    fn compute_ref(
        &self,
        code: PhantomData<Code>,
        Negate(expr): &Negate<MathExpr>,
    ) -> Self::Output { ... }
}
```

### Behavior

It evaluates the operand by reference and returns its negation. `u64` does not implement `Neg`, so a
language that negates cannot evaluate to `u64`, and the extended language uses `i64` literals.

### Context dependencies

`CanComputeRef<Code, MathExpr>` for the operand type, with an `Output` that implements `Neg`.

## `EvalSubtractWithNegate`

`EvalSubtractWithNegate` evaluates a `Minus` by rewriting `a - b` as `a + (-b)` and evaluating the
result.

### Definition

```rust
#[cgp_impl(new EvalSubtractWithNegate)]
#[uses(CanCompute<Code, Plus<Expr>, Output = Output>)]
impl<Code, Expr, Output> Computer<Code, Minus<Expr>>
where
    Expr: FromVariant<Symbol!("Negate"), Value = Negate<Expr>>,
{
    type Output = Output;

    fn compute(&self, code: PhantomData<Code>, Minus { left, right }: Minus<Expr>) -> Self::Output { ... }
}
```

### Behavior

It wraps the right operand in a `Negate`, builds the enum's `Negate` variant through
[`FromVariant`](../../../../cgp/reference/traits/from_variant.md) without naming the enum, and evaluates
`Plus { left, right: negated }` through the context. So it delegates to whatever provider the context
wires for `Plus<Expr>`, and requires the language to have a `Negate` variant. It implements `Computer`
only, and no context wires it: `InterpreterPlus` evaluates through `ComputerRef`, so it could not use
this provider without also wiring by-value evaluation.

### Context dependencies

`CanCompute<Code, Plus<Expr>>`, and a language enum `Expr` with a `Negate` variant holding
`Negate<Expr>`.

### Known issues

Never wired or exercised; see [issues.md](../issues.md#housekeeping).

## Source

- [`providers/eval/`](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/expression/src/providers/eval)
  — one file per operator: `add.rs`, `multiply.rs`, `literal.rs`, `subtract.rs` (with
  `EvalSubtractWithNegate`), and `negate.rs`.

## Public material derived from this

The "Evaluator Computer" and "Implementing Eval Providers" sections of page 3 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
