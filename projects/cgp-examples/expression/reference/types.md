# Types

The types are the standalone operator structs in `types/`, the two structs the Lisp target uses, and
the language enums each context defines from them. The operator structs are generic over the
expression type they nest, so the same struct appears in every language; only the enums fix the
recursion.

## `Plus` and `Times`

`Plus<Expr>` and `Times<Expr>` are the binary operators of the base language.

### Definition

```rust
#[derive(Debug, Eq, PartialEq, HasField)]
pub struct Plus<Expr> {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

#[derive(Debug, Eq, PartialEq, HasField)]
pub struct Times<Expr> {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}
```

### Behavior

The operands are boxed so a language enum can contain them recursively. Both derive `HasField`,
which is what implements the [`BinarySubExpression`](abstract-types-and-getters.md#binarysubexpression)
getter for them and lets `BinaryOpToLisp` read `left` and `right` without naming the struct.

### Context dependencies

None; they are plain data.

## `Minus` and `Negate`

`Minus<Expr>` and `Negate<Expr>` are the operators the extended language adds.

### Definition

```rust
#[derive(Debug, Eq, PartialEq)]
pub struct Minus<Expr> {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

#[derive(Debug, Eq, PartialEq)]
pub struct Negate<Expr>(pub Box<Expr>);
```

### Behavior

Neither derives `HasField`, so `BinaryOpToLisp` cannot convert a `Minus`; no context converts the
extended language, so nothing needs it to.

### Context dependencies

None.

## `Literal`

`Literal<T>` is a constant of any value type.

### Definition

```rust
#[derive(Debug, Eq, PartialEq)]
pub struct Literal<T>(pub T);
```

### Behavior

It is generic over the value, not over the expression, so the same struct holds a `u64` in the base
language, an `i64` in the extended one, and appears unchanged as a variant of `LispExpr`.

### Context dependencies

None.

## `List` and `Ident`

`List<Expr>` and `Ident` are the two structs of the Lisp target besides `Literal`.

### Definition

```rust
#[derive(Debug, Eq, PartialEq)]
pub struct List<Expr>(pub Vec<Box<Expr>>);

#[derive(Debug, Eq, PartialEq)]
pub struct Ident(pub String);
```

### Behavior

A `List` is an S-expression, a sequence of boxed sub-expressions, and an `Ident` is an operator symbol
such as `+`. `(+ 2 3)` is a `List` of an `Ident` and two `Literal`s.

### Context dependencies

None.

## The language enums

The language enums are defined in each context module rather than in `types/`, so each context has
its own copy. They wrap the structs above, instantiating each operator at the enum itself.

### Definition

```rust
pub type Value = u64;

#[derive(Debug, HasFields, FromVariant, ExtractField)]
pub enum MathExpr {
    Plus(Plus<MathExpr>),
    Times(Times<MathExpr>),
    Literal(Literal<Value>),
}

#[derive(Eq, PartialEq, Debug, HasFields, FromVariant, ExtractField)]
pub enum LispExpr {
    List(List<LispExpr>),
    Literal(Literal<Value>),
    Ident(Ident),
}
```

`add_mult`, `add_mult_binary_op`, and `add_mult_code` each define these two identically. `add_mult_neg`
defines the extended language instead, with `Value` as `i64`:

```rust
pub type Value = i64;

#[derive(Debug, HasFields, FromVariant, ExtractField)]
pub enum MathPlusExpr {
    Plus(Plus<MathPlusExpr>),
    Times(Times<MathPlusExpr>),
    Literal(Literal<Value>),
    Negate(Negate<MathPlusExpr>),
    Minus(Minus<MathPlusExpr>),
}
```

The `classic` module holds a separate, closed `Expr` enum with its own `eval` and `expr_to_string`
functions, the form the rest of the crate improves on:

```rust
pub enum Expr {
    Plus(Box<Expr>, Box<Expr>),
    Times(Box<Expr>, Box<Expr>),
    Literal(u64),
}
```

### Behavior

Each variant of `MathExpr`, `LispExpr`, and `MathPlusExpr` wraps exactly one payload type, which is
what the `FromVariant` and `ExtractField` derives require. The three derives let
`MatchWithValueHandlers` take the enum apart variant by variant and let a provider build a `LispExpr`
by upcasting a smaller enum. They are listed individually rather than as `#[derive(CgpData)]`; see
[issues.md](../issues.md#modernization). `LispExpr` also derives `Eq` and `PartialEq`, which the
conversion test uses to compare trees.

### Context dependencies

None.

## Source

- [`types/`](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/expression/src/types) — the
  operator structs, `List`, and `Ident`.
- [`contexts/`](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/expression/src/contexts) —
  the language enums.
- [`classic/add_mult.rs`](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/classic/add_mult.rs)
  — the closed `Expr`.

## Public material derived from this

The "Evaluator Computer" and "Extending `MathExpr`" sections of page 3 of the planned
[extensible data types deep dive](../../../../website/deep-dives/extensible-datatypes.md).
