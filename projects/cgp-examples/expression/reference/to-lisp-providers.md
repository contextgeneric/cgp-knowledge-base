# Conversion providers

The conversion providers turn an expression into a Lisp S-expression tree, one provider per operator,
all by reference through `ComputerRef`. Each builds its output without naming the target enum: the
context supplies the type through [`HasLispExprType`](abstract-types-and-getters.md#haslispexprtype),
and the provider constructs only the variants it needs in a small local enum, then upcasts it into the
full type with [`CanUpcast`](../../../../cgp/reference/traits/cast.md).

## `PlusToLisp` and `TimesToLisp`

`PlusToLisp` and `TimesToLisp` convert a `Plus` or `Times` to a list headed by the operator symbol.

### Definition

```rust
#[derive(CgpData)]
enum LispSubExpr<Expr> {
    List(List<Expr>),
    Ident(Ident),
}

#[cgp_impl(new PlusToLisp)]
#[use_type(HasLispExprType.LispExpr)]
#[uses(CanComputeRef<Code, MathExpr, Output = LispExpr>)]
impl<Code, MathExpr> ComputerRef<Code, Plus<MathExpr>>
where
    LispSubExpr<LispExpr>: CanUpcast<LispExpr>,
{
    type Output = LispExpr;

    fn compute_ref(
        &self,
        code: PhantomData<Code>,
        Plus { left, right }: &Plus<MathExpr>,
    ) -> Self::Output { ... }
}
```

`TimesToLisp` is the same, over `Times<MathExpr>`, in its own file with its own copy of `LispSubExpr`.

### Behavior

It converts both operands through the context, builds an `Ident("+")` (or `"*"`) and a `List` of the
identifier and the two operands, and upcasts each through the local enum. For `Plus(2, 3)` the result is
`(+ 2 3)`: `List([Ident("+"), Literal(2), Literal(3)])`. The upcast succeeds for any target enum that
has `List` and `Ident` variants of those types. Only `add_mult` wires these two; the later contexts use
`BinaryOpToLisp`.

### Context dependencies

`HasLispExprType`, and `CanComputeRef<Code, MathExpr>` producing that type for the operands.

## `LiteralToLisp`

`LiteralToLisp` converts a `Literal` to the target's `Literal` variant.

### Definition

```rust
#[derive(CgpData)]
enum LispSubExpr<T> {
    Literal(Literal<T>),
}

#[cgp_impl(new LiteralToLisp)]
#[use_type(HasLispExprType.LispExpr)]
impl<Code, T> ComputerRef<Code, Literal<T>>
where
    LispSubExpr<T>: CanUpcast<LispExpr>,
    T: Clone,
{
    type Output = LispExpr;

    fn compute_ref(&self, _code: PhantomData<Code>, Literal(value): &Literal<T>) -> Self::Output { ... }
}
```

### Behavior

It clones the value into a new `Literal` and upcasts it. The same `Literal` struct is both the source
operator and the target variant, which is what lets the upcast match by variant name.

### Context dependencies

`HasLispExprType`, with a target enum whose `Literal` variant holds `Literal<T>`.

## `BinaryOpToLisp`

`BinaryOpToLisp<Operator>` converts any binary operator, taking the symbol as a type-level string.

### Definition

```rust
#[cgp_impl(new BinaryOpToLisp<Operator>)]
#[use_type(HasMathExprType.MathExpr, HasLispExprType.LispExpr)]
#[uses(CanComputeRef<Code, MathExpr, Output = LispExpr>)]
impl<Code, MathSubExpr, Operator> ComputerRef<Code, MathSubExpr>
where
    MathSubExpr: BinarySubExpression<MathExpr>,
    Operator: Default + Display,
    LispSubExpr<LispExpr>: CanUpcast<LispExpr>,
{
    type Output = LispExpr;

    fn compute_ref(&self, code: PhantomData<Code>, expr: &MathSubExpr) -> Self::Output { ... }
}
```

### Behavior

It reads the operands through [`BinarySubExpression`](abstract-types-and-getters.md#binarysubexpression),
so its input is any struct with `left` and `right` fields, and it renders the symbol with
`Operator::default().to_string()`, which for a `Symbol!("+")` is `+`. It needs `HasMathExprType` to
name the operand type, since its input type no longer shows it. `add_mult_binary_op` and
`add_mult_code` wire it as `BinaryOpToLisp<Symbol!("+")>` for `Plus` and `BinaryOpToLisp<Symbol!("*")>`
for `Times`, replacing the two hand-written providers above.

### Context dependencies

`HasMathExprType`, `HasLispExprType`, and `CanComputeRef<Code, MathExpr>` producing the target type.

## Source

- [`providers/to_lisp/add.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/providers/to_lisp/add.rs)
  and [`multiply.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/providers/to_lisp/multiply.rs)
  — `PlusToLisp` and `TimesToLisp`.
- [`providers/to_lisp/literal.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/providers/to_lisp/literal.rs)
  — `LiteralToLisp`.
- [`providers/to_lisp/binary.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/providers/to_lisp/binary.rs)
  — `BinaryOpToLisp`.

## Public material derived from this

The "Converting to a Lisp Expression" and "Binary Operator Provider" sections of page 3 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
