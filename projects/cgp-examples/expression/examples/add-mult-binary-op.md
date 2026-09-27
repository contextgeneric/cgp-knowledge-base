# `add_mult_binary_op`

The base interpreter again, with the two per-operator conversion providers replaced by one generic
`BinaryOpToLisp` that takes the operator symbol as a type-level string.

- **Source** — [contexts/add_mult_binary_op.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/expression/src/contexts/add_mult_binary_op.rs)
- **Run** — no test; the context is exercised only by its check block
- **Needs** — nothing
- **Result** — compiles and passes its check. A probe evaluated `2 * (3 + 4)` to `14` by value and
  converted it to `(* 2 (+ 3 4))`

## The context and its wiring

The module defines its own `MathExpr`, `LispExpr`, `Interpreter`, and dispatch wrappers, identical to
[`add_mult`](add-mult.md)'s. Only the two conversion keys for the binary operators differ:

```rust
@ComputerRefComponent.<Code> Code.Plus<MathExpr>: BinaryOpToLisp<Symbol!("+")>,
@ComputerRefComponent.<Code> Code.Times<MathExpr>: BinaryOpToLisp<Symbol!("*")>,
```

[`BinaryOpToLisp`](../reference/to-lisp-providers.md#binaryoptolisp) reads the operands through the
`BinarySubExpression` getter, which `Plus` and `Times` satisfy by deriving `HasField`, and renders the
`Symbol!` as the operator. It needs the context's `MathExpr` through `HasMathExprType`, which this
context wires with `UseType<MathExpr>`.

## What the checks pin

The `check_components!` block asserts the same entries as `add_mult`'s: evaluation and conversion of
all four input types. Nothing runs the context at test time.

## What it demonstrates

- A generic provider replacing per-operator duplicates, keyed by a type-level string: see
  [conversion providers](../reference/to-lisp-providers.md#binaryoptolisp).
- A getter trait reading the provider's input rather than its context: see
  [abstract types and getters](../reference/abstract-types-and-getters.md#binarysubexpression).

## Known issues

- **No test** — the probe result above is the only runtime evidence; see
  [testing.md](../testing.md).

## The test the public page gives

The public page runs this context with an integration test the reader saves as
`expression/tests/binary_op.rs`, which builds `2 * (3 + 4)`, converts it with `ToLisp`, and evaluates it
with `Eval`, printing each result. A probe ran the same test from a crate with a path dependency on
this one, and it printed the Lisp tree and then `14`:

```text
List(List([Ident(Ident("*")), Literal(Literal(2)), List(List([Ident(Ident("+")), Literal(Literal(3)), Literal(Literal(4))]))]))
```

With `Symbol!("+")` changed to `Symbol!("add")` in a copy of the module, the same test printed
`List(List([Ident(Ident("*")), Literal(Literal(2)), List(List([Ident(Ident("add")), Literal(Literal(3)), Literal(Literal(4))]))]))`
and `14`, the change the public page shows.

## Public material derived from this

The `expression/examples/add-mult-binary-op` page of the [cgp-examples project
section](../../../../website/projects/cgp-examples.md), including its test and its change to try.
