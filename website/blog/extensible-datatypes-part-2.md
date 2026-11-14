# Extensible Data Types, Part 2: Modular Interpreters and Extensible Visitors

The second part of the extensible-data-types series: extensible variants applied to the expression
problem, building an interpreter for a toy arithmetic language in which every operator and every
operation is an independent, separately compilable piece.

- **URL**: <https://contextgeneric.dev/blog/extensible-datatypes-part-2>
- **Source**: [blog/2025-07-09-extensible-datatypes-part-2.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-07-09-extensible-datatypes-part-2.md)
- **Published**: 9 July 2025, tagged `deepdive`
- **Release**: [v0.4.2](../../releases/v0-4-2.md)
- **Status**: Historical
- **Notice**: a note at the top of the post, written on the website's `v0.8.0` branch, links the [`expression` pages](https://contextgeneric.dev/docs/projects/cgp-examples/expression/) and the *Extensible variants* Concepts page, per [projects/cgp-examples.md](../projects/cgp-examples.md); it is the sanctioned edit in [../AGENTS.md](../AGENTS.md#do-not-rewrite-history) and changes no claim

## What it covers

**The opening argues the visitor pattern is closed for extension**, with `serde`'s `Visitor` as the
case: the trait fixes its visit methods, so a format cannot add a `U256`, and a format such as
`postcard` that supports fewer types than JSON must reject cases at *runtime* while formally
implementing `Deserialize`. The pattern is too restrictive or too permissive, where both sides should
state their requirements at compile time, the problem CGP's dispatchers solve.

The rest, in order:

- **The [expression problem](https://en.wikipedia.org/wiki/Expression_problem):** a `MathExpr` enum
  with `Literal`, `Plus`, and `Times` forces `eval` and `expr_to_string` to change with every variant,
  and recursion defeats extracting helpers. CGP makes each operator a generic struct (`Plus<Expr>`,
  `Times<Expr>`, `Literal<T>`) and each evaluation step a `Computer` provider recursing through the
  context; wiring maps each input type to its provider, and the enum to a dispatcher.
- **A second operation**, to a Lisp S-expression, a "double expression problem" decoupled from both
  source and target types: `ComputerRef` for borrowed input, an abstract `LispExpr` type supplied by
  wiring, and providers that build a local `LispSubExpr` enum with only the variants they need and
  upcast it into the full target.
- **Two advanced sections:** a generic `BinaryOpToLisp<Operator>` collapsing `PlusToLisp` and
  `TimesToLisp`, parameterized by a `Symbol!` operator; and **code-based dispatching**, where the
  `Code` parameter selects `Eval` or `ToLisp` for one input type, a two-layer dispatch nestable in
  either order at no runtime cost.
- **The closing extension:** `Minus` and `Negate` in a second enum reuse the evaluators unchanged, and
  because wiring is lazy, the extended language can skip the to-Lisp implementations and still compile.

## How it relates to the knowledge base

- **The source to quote:** the [expression interpreter
  example](../../examples/expression-interpreter.md). The code lives on as cgp-examples'
  `expression` crate; where each section now sits is in the
[`expression`
subproject](../../projects/cgp-examples/expression/README.md#where-the-blog-posts-code-lives).
- **Concepts and constructs:** [extensible variants](../../cgp/concepts/extensible-variants.md),
  [dispatching](../../cgp/concepts/dispatching.md), [`Computer` /
  `CanCompute`](../../cgp/reference/components/computer.md) and its by-reference variant, the
  [dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md),
  [`CanUpcast`](../../cgp/reference/traits/cast.md),
  [`#[cgp_type]`](../../cgp/reference/macros/cgp_type.md) over [abstract
  types](../../cgp/concepts/abstract-types.md), and lazy wiring in [check
  traits](../../cgp/concepts/check-traits.md).
- **Strategy assets:** the `serde::Visitor` analysis is the project's most concrete "a real library
  hits this wall" argument, for
  [message.md](../../communication-strategy/message.md#the-problems-cgp-removes); the closing point,
  that minimal traits and lazy wiring defer an implementation without `unimplemented!()` stubs, is a
  [strength](../../communication-strategy/message.md#the-strengths-worth-advertising) against
  heavyweight-trait designs. The `serde::Visitor` motivation needs no CGP syntax and is reusable
  verbatim.

## Where it diverges from CGP v0.8.0

- **`#[cgp_context] pub struct Interpreter;` and `InterpreterComponents` no longer exist**; a context
  carries its own wiring table.
- **Every provider is inside-out**, with `#[cgp_new_provider]` and an explicit `context: &Context`;
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) is the current form.
- **`#[derive(HasFields, FromVariant, ExtractField)]` is now
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md).**
- **`UseInputDelegate` and `UseDelegate` tables are the legacy dispatch form.** Per-type dispatch on a
  context is now the `open` statement of
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md), per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **`#[cgp_auto_getter] pub trait BinarySubExpression`** reads `left` and `right`, fields of the
  *input* rather than the provider's context, so a getter trait is still right here (see
  [reading-context-fields](../../cgp/guides/reading-context-fields.md)), but it would be written with
  the modern attribute forms.
- **Several code blocks are internally inconsistent**, mixing an earlier `Expr` name with `MathExpr`:
  the first wiring block maps `Expr: DispatchEval` beside `Plus<MathExpr>: EvalAdd`, and the manual
  `match` in "Dispatching Eval" matches on `Expr::Plus` in a function typed over `MathExpr`. Do not
  copy these blocks.

## Maintaining it

Leave it alone; write anything downstream of the `serde::Visitor` motivation from the
[expression interpreter example](../../examples/expression-interpreter.md).
