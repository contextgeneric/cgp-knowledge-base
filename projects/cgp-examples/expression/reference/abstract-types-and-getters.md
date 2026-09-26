# Abstract types and getters

The two abstract types let the conversion providers name the context's source and target languages
without naming either enum, and the one getter lets a provider read any binary operator's operands.
Each context that converts binds both types with `UseType`.

## `HasLispExprType`

`HasLispExprType` is the abstract type of the conversion target.

### Definition

```rust
#[cgp_type]
pub trait HasLispExprType {
    type LispExpr;
}
```

### Behavior

The conversion providers import it with `#[use_type(HasLispExprType.LispExpr)]` and build values of
that type by upcasting, so they work for any target enum with the variants they construct. The
contexts that convert wire `LispExprTypeProviderComponent: UseType<LispExpr>`. It registers no
namespace prefix.

### Context dependencies

None; it is bound directly with `UseType`.

## `HasMathExprType`

`HasMathExprType` is the abstract type of the source language.

### Definition

```rust
#[cgp_type]
pub trait HasMathExprType {
    type MathExpr;
}
```

### Behavior

Only `BinaryOpToLisp` imports it, with `#[use_type]`, to name the expression type its operands hold,
since its input is any binary operator rather than a `Plus<MathExpr>` with the type in view. The
contexts that convert wire `MathExprTypeProviderComponent: UseType<MathExpr>`; `add_mult` wires it
too, although none of its providers reads it.

### Context dependencies

None; it is bound directly with `UseType`.

## `BinarySubExpression`

`BinarySubExpression<Expr>` reads the two operands of any binary operator struct.

### Definition

```rust
#[cgp_auto_getter]
pub trait BinarySubExpression<Expr> {
    fn left(&self) -> &Box<Expr>;
    fn right(&self) -> &Box<Expr>;
}
```

### Behavior

The blanket impl covers any type with `left` and `right` fields of type `Box<Expr>`, which `Plus` and
`Times` satisfy through their `HasField` derive. It is a getter trait rather than an `#[implicit]`
argument because it reads fields of the provider's *input*, not of its context, which is the case
[`#[cgp_auto_getter]`](../../../../cgp/reference/macros/cgp_auto_getter.md) is kept for. Its `&Box<Expr>`
return type is the only `&Box` in any signature in the crate, which is the pattern the crate-level
`#![allow(clippy::borrowed_box)]` in `lib.rs` silences.

### Context dependencies

None; it is implemented on the operator types.

## Source

- [`components/expression.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/components/expression.rs)
  — the two abstract types.
- [`providers/to_lisp/binary.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/providers/to_lisp/binary.rs)
  — `BinarySubExpression`.

## Public material derived from this

The "Binary Operator Provider" section of page 3 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
