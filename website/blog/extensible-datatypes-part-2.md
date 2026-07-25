# Extensible Data Types, Part 2: Modular Interpreters and Extensible Visitors

The second part of the extensible-data-types series, applying extensible variants to the expression
problem. It builds a modular interpreter for a toy arithmetic language in which every operator and
every operation over the language is an independent, separately-compilable piece.

- **URL** — <https://contextgeneric.dev/blog/extensible-datatypes-part-2>
- **Source** — [blog/2025-07-09-extensible-datatypes-part-2.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-07-09-extensible-datatypes-part-2.md)
- **Published** — 9 July 2025, tagged `deepdive`
- **Release** — [v0.4.2](../../releases/v0-4-2.md)
- **Status** — Historical

## What it covers

The post opens with the strongest motivating argument in the series: an analysis of why the
traditional visitor pattern is closed for extension, using `serde`'s `Visitor` trait as the case
study. Because the trait fixes its set of visit methods, a format that wants to deserialize a `U256`
cannot extend it, while a format like `postcard` that supports fewer types than JSON must reject
unsupported cases at *runtime* despite the type formally implementing `Deserialize`. The post's
framing — that the pattern is either too restrictive or too permissive, and that what is wanted is for
both sides to state their requirements at compile time — is a clean statement of the problem CGP's
dispatchers solve.

It then narrows to the [expression problem](https://en.wikipedia.org/wiki/Expression_problem) proper.
A `MathExpr` enum with `Literal`, `Plus`, and `Times` variants forces every function over it —
`eval`, `expr_to_string` — to be updated whenever a variant is added, and the recursion makes the
coupling impossible to break by extracting helpers. The CGP answer is to make each operator its own
generic struct (`Plus<Expr>`, `Times<Expr>`, `Literal<T>`) and each per-operator evaluation step its
own `Computer` provider, recursing through the context rather than through a concrete type. Wiring
maps each input type to its provider, with the enum itself routed to a dispatcher.

The post then adds a *second* operation — converting the expression tree to a Lisp S-expression —
which it calls a "double expression problem," since the logic must be decoupled from both the source
and the target type. This introduces `ComputerRef` for borrowed input, an abstract `LispExpr` type
supplied by wiring, and a neat use of upcasting: a provider constructs values through a small local
`LispSubExpr` enum containing only the variants it needs, then upcasts into the full target — the
construction-side counterpart of reading a field you do not own.

Two advanced sections follow. A generic `BinaryOpToLisp<Operator>` provider collapses the near-identical
`PlusToLisp` and `TimesToLisp` into one, parameterized by a `Symbol!` operator string. And
**code-based dispatching** uses the `Code` parameter to select between `Eval` and `ToLisp` for the
same input type, giving a two-layer dispatch — first on input type, then on operation — that the post
notes can be nested in either order at no runtime cost.

The post closes by extending the language with `Minus` and `Negate` in a second enum, reusing the
existing evaluators unchanged, and makes a point worth keeping: because wiring is lazy, the extended
language can skip the to-Lisp implementations entirely and still compile.

## How it relates to the knowledge base

The scenario is re-derived in current syntax as the
[expression interpreter example](../../examples/expression-interpreter.md) — quote that, not this
post. The concepts are [extensible variants](../../cgp/concepts/extensible-variants.md) and
[dispatching](../../cgp/concepts/dispatching.md); the components are
[`Computer` / `CanCompute`](../../cgp/reference/components/computer.md) and its by-reference variant;
the dispatchers are in the [dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md);
the casts are [`CanUpcast`](../../cgp/reference/traits/cast.md); the abstract target type is
[`#[cgp_type]`](../../cgp/reference/macros/cgp_type.md) over
[abstract types](../../cgp/concepts/abstract-types.md); and the lazy-wiring property the closing
section relies on is [check traits](../../cgp/concepts/check-traits.md).

Two pieces of the post are strategy assets. The `serde::Visitor` analysis is the most concrete
"here is a real library that hits this wall" argument the project has published, and belongs in
[problems-solved.md](../../communication-strategy/problems-solved.md) territory. The closing
observation — that CGP lets you defer implementing a capability without `unimplemented!()` stubs,
because minimal traits plus lazy wiring mean only what is used is checked — is a genuine selling point
against heavyweight-trait designs and is the kind of claim
[selling-points.md](../../communication-strategy/selling-points.md) is built from.

## Where it diverges from CGP v0.8.0

- **`#[cgp_context] pub struct Interpreter;` and `InterpreterComponents` no longer exist**; a context
  now carries its own wiring table.
- **Every provider is written inside-out** with `#[cgp_new_provider]` and an explicit
  `context: &Context`; [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) is the current form.
- **`#[derive(HasFields, FromVariant, ExtractField)]` is now normally
  [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md).**
- **`UseInputDelegate` and `UseDelegate` tables are the legacy dispatch form.** The current idiom for
  per-type dispatch on a context is the `open` statement of
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md), per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **`#[cgp_auto_getter] pub trait BinarySubExpression`** reads `left` and `right` through a getter
  trait; because these are fields on the *input* rather than on the provider's own context, this
  remains one of the cases a getter trait is still right for — see
  [reading-context-fields](../../cgp/guides/reading-context-fields.md) — but the trait would now be
  written with the modern attribute forms.
- **Several code blocks are internally inconsistent**, mixing an earlier `Expr` name with the later
  `MathExpr`: the first wiring block maps `Expr: DispatchEval` beside `Plus<MathExpr>: EvalAdd`, and
  the manual `match` in "Dispatching Eval" matches on `Expr::Plus` in a function typed over
  `MathExpr`. Do not copy these blocks.

## Maintaining it

Leave it alone. The part worth carrying forward into any new writing is the `serde::Visitor`
motivation, which does not depend on CGP syntax at all and is reusable verbatim as an argument;
everything downstream of it should be rewritten from the
[expression interpreter example](../../examples/expression-interpreter.md).
