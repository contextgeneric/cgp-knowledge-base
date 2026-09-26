# Expression interpreter

This example builds a modular interpreter for a small arithmetic language, where each operator is its own type and each operation over the language — evaluation, conversion to Lisp — is a separate provider, so variants and operations can both be added without editing existing code. It progresses from the closed enum-and-`match` form, through per-variant evaluation providers wired by input dispatch, to a second operation, a generalized operator provider, code-based dispatch between operations, and finally an extended language with new variants. It is a template for any recursive data type — expression trees, JSON values, syntax trees — that must stay open to new cases and new traversals at once, the classic [expression problem](https://en.wikipedia.org/wiki/Expression_problem).

The contexts here are **environmental contexts** — `Interpreter` and its extensions exist only to carry the wiring, with no expression data of their own — and the components are **parameter-targeted**, since the expression being evaluated arrives as the handler's input rather than as `Self`. That separation is what lets one language have several independent operations; see the [modularity hierarchy](../cgp/concepts/modularity-hierarchy.md).

The concepts each step demonstrates are documented in full in the reference; this example only notes which one is in play and links to it:

- handling each variant of an enum independently — [extensible variants](../cgp/concepts/extensible-variants.md) and the [extensible visitor pattern](../cgp/concepts/dispatching.md)
- exposing an enum as a sum of named variants — [`#[derive(CgpData)]`](../cgp/reference/derives/derive_cgp_data.md)
- the computation components — [`Computer` / `CanCompute`](../cgp/reference/components/computer.md) and its by-reference variant `ComputerRef`
- writing a per-variant provider — [`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md), with its dependencies imported by [`#[uses]`](../cgp/reference/attributes/uses.md) and [`#[use_type]`](../cgp/reference/attributes/use_type.md)
- routing on the input variant and on the operation — the `open` statement of [`delegate_components!`](../cgp/reference/macros/delegate_components.md), per [dispatching per type](../cgp/guides/dispatching-per-type.md)
- the variant dispatcher — [`MatchWithValueHandlers`](../cgp/reference/providers/dispatch_combinators.md)
- constructing part of a target enum — [`CanUpcast`](../cgp/reference/traits/cast.md)
- abstract output types per context — [`#[cgp_type]`](../cgp/reference/macros/cgp_type.md) and [`UseType`](../cgp/reference/providers/use_type.md)

All snippets assume `use cgp::prelude::*;`, with the computation items from `cgp::extra::handler`, the dispatchers from `cgp::extra::dispatch`, and `CanUpcast` from `cgp::core::field::impls`.

## The closed interpreter

The conventional way to model the language is one enum with a `match`-based function per operation:

```rust
pub enum Expr {
    Plus(Box<Expr>, Box<Expr>),
    Times(Box<Expr>, Box<Expr>),
    Literal(u64),
}

pub fn eval(expr: Expr) -> u64 {
    match expr {
        Expr::Plus(a, b) => eval(*a) + eval(*b),
        Expr::Times(a, b) => eval(*a) * eval(*b),
        Expr::Literal(value) => value,
    }
}
```

This is concise but closed in two directions. Adding a variant forces every function that matches on `Expr` to change, and the recursive structure means even a helper like `eval_plus` must still mention `Expr`. A real expression type such as `syn::Expr` has dozens of variants and many operations, so this coupling becomes the central obstacle the rest of the example removes.

## Variants as standalone types

The first move is to give each operator its own type, generic over the expression it nests, rather than burying its shape in the enum:

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

#[derive(Debug, Eq, PartialEq)]
pub struct Literal<T>(pub T);
```

Each operator is now a reusable building block parameterized by the broader expression type, which is what lets the same `Plus` appear in several languages. `Plus` and `Times` derive [`#[derive(HasField)]`](../cgp/reference/derives/derive_has_field.md) so their `left` and `right` fields can be read generically later.

## Evaluating one variant

Evaluation is a [`Computer`](../cgp/reference/components/computer.md) — CGP's component for a synchronous, pure computation whose consumer trait is `CanCompute`. One provider handles addition, recursing into the operands through the context's own evaluation:

```rust
#[cgp_impl(new EvalAdd)]
#[uses(CanCompute<Code, MathExpr, Output = Output>)]
impl<Code, MathExpr, Output> Computer<Code, Plus<MathExpr>>
where
    Output: Add<Output = Output>,
{
    type Output = Output;

    fn compute(&self, code: PhantomData<Code>, Plus { left, right }: Plus<MathExpr>) -> Self::Output {
        let output_a = self.compute(code, *left);
        let output_b = self.compute(code, *right);
        output_a + output_b
    }
}
```

`EvalAdd` is written with [`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md) and is completely decoupled: it knows nothing of the concrete expression enum, only that the context can evaluate a nested `MathExpr` to some `Output` that supports `Add`, a dependency it imports with [`#[uses]`](../cgp/reference/attributes/uses.md). Multiplication is identical with `Mul`, and the literal case is the base of the recursion: it just returns its inner value, needing nothing from the context:

```rust
#[cgp_impl(new EvalLiteral)]
impl<Code, T> Computer<Code, Literal<T>> {
    type Output = T;

    fn compute(&self, _code: PhantomData<Code>, Literal(value): Literal<T>) -> T {
        value
    }
}
```

Each provider lives on its own and could be defined in a separate crate; nothing ties `EvalAdd`, `EvalMultiply`, and `EvalLiteral` together until a context composes them.

## Assembling the evaluator

The concrete enum wraps the standalone operator types and derives the [extensible-variant](../cgp/concepts/extensible-variants.md) machinery so it can be taken apart generically:

```rust
pub type Value = u64;

#[derive(Debug, CgpData)]
pub enum MathExpr {
    Plus(Plus<MathExpr>),
    Times(Times<MathExpr>),
    Literal(Literal<Value>),
}
```

The context is an empty struct whose only job is to wire each input type to its provider. It opens `ComputerComponent` for per-type dispatch with the [`open` statement](../cgp/reference/macros/delegate_components.md), and each path key names the component and then one segment per type parameter: the `Code`, then the *input* type. A per-entry generic `<Code>` as the first segment matches any code, so `Plus<MathExpr>` routes to `EvalAdd`, `Literal<Value>` to `EvalLiteral`, and the whole enum to a dispatcher, whatever operation code the caller passes:

```rust
pub struct Interpreter;

delegate_components! {
    Interpreter {
        open ComputerComponent;

        @ComputerComponent.<Code> Code.MathExpr: DispatchEval,
        @ComputerComponent.<Code> Code.Plus<MathExpr>: EvalAdd,
        @ComputerComponent.<Code> Code.Times<MathExpr>: EvalMultiply,
        @ComputerComponent.<Code> Code.Literal<Value>: EvalLiteral,
    }
}

#[cgp_impl(new DispatchEval)]
impl<Code> Computer<Code, MathExpr> for Interpreter {
    type Output = Value;

    fn compute(context: &Interpreter, code: PhantomData<Code>, expr: MathExpr) -> Self::Output {
        <MatchWithValueHandlers>::compute(context, code, expr)
    }
}
```

The whole `MathExpr` enum is handled by `DispatchEval`, a context-specific provider that defers to [`MatchWithValueHandlers`](../cgp/reference/providers/dispatch_combinators.md) — the variant dispatcher that derives one handler per variant from the enum's own variant list and runs them as a match, described in [dispatching](../cgp/concepts/dispatching.md). The thin `DispatchEval` wrapper is needed to break a trait-resolution cycle: wiring `MatchWithValueHandlers` directly for `MathExpr` would require the compiler to resolve the per-variant providers, which themselves route back through the dispatcher. Marking the trait implemented in the wrapper's body breaks the cycle.

## A second operation over the same language

Converting an expression to a Lisp [S-expression](https://en.wikipedia.org/wiki/S-expression) is a second operation, and adding it must not touch the evaluator. It uses `ComputerRef`, the by-reference variant of `Computer`, so the expression can still be used afterward, and it targets a separate `LispExpr` enum — making this a "double" expression problem, decoupled from both the source and the target type. The target type stays abstract through a [`#[cgp_type]`](../cgp/reference/macros/cgp_type.md) component:

```rust
#[cgp_type]
pub trait HasLispExprType {
    type LispExpr;
}

#[cgp_impl(new PlusToLisp)]
#[use_type(HasLispExprType.LispExpr)]
#[uses(CanComputeRef<Code, MathExpr, Output = LispExpr>)]
impl<Code, MathExpr> ComputerRef<Code, Plus<MathExpr>>
where
    LispSubExpr<LispExpr>: CanUpcast<LispExpr>,
{
    type Output = LispExpr;

    fn compute_ref(&self, code: PhantomData<Code>, Plus { left, right }: &Plus<MathExpr>) -> Self::Output {
        let expr_a = self.compute_ref(code, left);
        let expr_b = self.compute_ref(code, right);
        let ident = LispSubExpr::Ident(Ident("+".to_owned())).upcast(PhantomData);

        LispSubExpr::List(List(vec![ident.into(), expr_a.into(), expr_b.into()])).upcast(PhantomData)
    }
}
```

[`#[use_type]`](../cgp/reference/attributes/use_type.md) imports the abstract `LispExpr` from the context, so the provider writes it as a bare type. `PlusToLisp` only needs to build two kinds of `LispExpr`, a list and an identifier, so rather than depend on the full target enum it defines a small local enum with just those variants and [upcasts](../cgp/reference/traits/cast.md) into the full `LispExpr`:

```rust
#[derive(CgpData)]
enum LispSubExpr<Expr> {
    List(List<Expr>),
    Ident(Ident),
}
```

This is the variant-side analog of reading only the fields you need from a struct: `CanUpcast` constructs the parts of an enum a provider cares about without binding it to the entire definition. Wiring the new operation opens `ComputerRefComponent` beside `ComputerComponent`, adds its keys and a `DispatchToLisp` wrapper alongside the existing evaluator, and binds the abstract `LispExpr` type to the concrete enum with [`UseType`](../cgp/reference/providers/use_type.md):

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

The evaluator's keys are untouched; the conversion is added by extension, and the only shared line that changes is the `open` statement, which now lists both components.

## One provider for every binary operator

`PlusToLisp` and `TimesToLisp` differ only in the operator symbol, so they collapse into a single provider parameterized by the operator. The operator is a type-level string, and the operand fields are read through a getter that any binary struct satisfies:

```rust
#[cgp_auto_getter]
pub trait BinarySubExpression<Expr> {
    fn left(&self) -> &Box<Expr>;
    fn right(&self) -> &Box<Expr>;
}

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

    fn compute_ref(&self, code: PhantomData<Code>, expr: &MathSubExpr) -> Self::Output {
        let expr_a = self.compute_ref(code, expr.left());
        let expr_b = self.compute_ref(code, expr.right());
        let ident = LispSubExpr::Ident(Ident(Operator::default().to_string())).upcast(PhantomData);

        LispSubExpr::List(List(vec![ident.into(), expr_a.into(), expr_b.into()])).upcast(PhantomData)
    }
}
```

`BinaryOpToLisp<Operator>` works for any `MathSubExpr` whose `left` and `right` fields the [`#[cgp_auto_getter]`](../cgp/reference/macros/cgp_auto_getter.md) trait `BinarySubExpression` can read, which is why `Plus` and `Times` derived `HasField` earlier. The getter is a trait rather than an [`#[implicit]`](../cgp/reference/attributes/implicit.md) argument because it reads fields of the provider's input, not of its context. Since its input type no longer shows the expression type, the provider imports `MathExpr` from the context as well. Both operators now wire to the same provider with a different [`Symbol!`](../cgp/reference/macros/symbol.md) operator string:

```rust
@ComputerRefComponent.<Code> Code.Plus<MathExpr>: BinaryOpToLisp<Symbol!("+")>,
@ComputerRefComponent.<Code> Code.Times<MathExpr>: BinaryOpToLisp<Symbol!("*")>,
```

## Dispatching on the operation as well as the input

Evaluation and conversion can share one component by keying the dispatch on the *operation* as well as the input. Marker types name the operations, and each path key fixes a concrete code as its first segment instead of a generic one, so one component routes a `Plus` to evaluation or conversion depending on the `Code`:

```rust
pub struct Eval;
pub struct ToLisp;

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

Evaluation now runs through `ComputerRef`, so it uses the by-reference impls the evaluation providers also carry, and the dispatch wrappers fix their code: `DispatchEval` implements `ComputerRef<Eval, MathExpr>` and `DispatchToLisp` implements `ComputerRef<ToLisp, MathExpr>`. The keys can be grouped by operation, as here, or by operator; the grouping is a free choice that costs nothing at runtime, since all of it resolves through trait selection at compile time. Within one component a code is keyed per input throughout, never also on its own, because a shorter key would cover every longer key beneath it. Defining the operation routing through `delegate_components!` rather than separate `impl` blocks is what keeps the `Eval` and `ToLisp` logic free to live in different crates.

## Extending the language

A new language lives alongside the old one rather than replacing it, which is the whole point of keeping variants standalone. Subtraction and negation get their own types and evaluation providers, written exactly like the originals:

```rust
#[derive(Debug, Eq, PartialEq)]
pub struct Minus<Expr> {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

#[derive(Debug, Eq, PartialEq)]
pub struct Negate<Expr>(pub Box<Expr>);

#[cgp_impl(new EvalSubtract)]
#[uses(CanComputeRef<Code, MathExpr, Output = Output>)]
impl<Code, MathExpr, Output> ComputerRef<Code, Minus<MathExpr>>
where
    Output: Sub<Output = Output>,
{
    type Output = Output;

    fn compute_ref(&self, code: PhantomData<Code>, Minus { left, right }: &Minus<MathExpr>) -> Self::Output {
        let output_a = self.compute_ref(code, left);
        let output_b = self.compute_ref(code, right);
        output_a - output_b
    }
}
```

The extended enum reuses the original operator providers, now instantiated at a signed `Value` so negation has something to return:

```rust
pub type Value = i64;

#[derive(Debug, CgpData)]
pub enum MathPlusExpr {
    Plus(Plus<MathPlusExpr>),
    Times(Times<MathPlusExpr>),
    Literal(Literal<Value>),
    Negate(Negate<MathPlusExpr>),
    Minus(Minus<MathPlusExpr>),
}

delegate_components! {
    InterpreterPlus {
        open ComputerRefComponent;

        @ComputerRefComponent.Eval.MathPlusExpr: DispatchEval,
        @ComputerRefComponent.Eval.Plus<MathPlusExpr>: EvalAdd,
        @ComputerRefComponent.Eval.Times<MathPlusExpr>: EvalMultiply,
        @ComputerRefComponent.Eval.Literal<Value>: EvalLiteral,
        @ComputerRefComponent.Eval.Minus<MathPlusExpr>: EvalSubtract,
        @ComputerRefComponent.Eval.Negate<MathPlusExpr>: EvalNegate,
    }
}
```

`EvalAdd` and `EvalMultiply` work unchanged because `i64` implements `Add` and `Mul` just as `u64` did — the providers never named a concrete numeric type. Equally telling is what is *absent*: `InterpreterPlus` wires only evaluation and simply omits a to-Lisp handler for `Minus` and `Negate`. Because CGP wiring is lazy and checked only where it is used, the evaluator compiles and runs without those handlers, so a new variant can be prototyped against one operation before the others catch up — the kind of partial extension a closed `enum` with exhaustive `match`es cannot express.

For an agent working on the interpreter itself rather than learning its patterns, the runnable crate is documented as the [`expression`](../projects/cgp-examples/expression/README.md) subproject of cgp-examples.
