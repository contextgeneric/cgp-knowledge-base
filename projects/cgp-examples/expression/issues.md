# Issues

This document records what is wrong with or missing from `expression` on the `v0.8.0` branch,
grouped as defects, missing features, modernization, and housekeeping. Every entry was confirmed
against the source, by a probe crate where it says so. Remove an entry in the same change that fixes
it in the crate, per [../../AGENTS.md](../../AGENTS.md#the-shape-of-a-project-section).

## Defects

No defect has been confirmed. Every context that has a test passes it, and a probe ran the two that do
not and got the expected results.

## Missing features

- **The checks skip `Times` evaluation** — no context's `check_components!` block lists evaluation of
  its `Times` variant, although every context wires it. A broken entry still fails the build, inside
  the dispatch wrapper's body, as a probe confirmed; what the gap loses is an error at the wiring
  site. The probe's wiring and error are in [testing.md](testing.md#what-the-checks-pin). Adding
  `(Eval, Times<MathExpr>)` to each block, or `(Eval, Times<MathPlusExpr>)` in `add_mult_neg`, closes
  it.
- **Two contexts have no test** — `add_mult_binary_op` and `add_mult_code` are exercised only by their
  checks. See [testing.md](testing.md#what-is-untested).
- **`BinaryOpToLisp` cannot convert the new operators** — `Minus` does not derive `HasField`, so it does
  not implement `BinarySubExpression`, and a context that converts the extended language could not use
  `BinaryOpToLisp` for it without that derive. See [types](reference/types.md#minus-and-negate).

## Modernization

The crate's providers are current `#[cgp_impl]` blocks, but its wiring, bounds, and derives use older
forms. These are the source changes page 3 of the planned
[extensible data types deep dive](../../../website/deep-dives/extensible-datatypes.md) needs before it
quotes the crate, and the [expression interpreter](../../../examples/expression-interpreter.md) worked
example changes with them, since it matches the crate.

- **Replace the nested tables with `open`.** `add_mult` and `add_mult_binary_op` key their
  `ComputerComponent` and `ComputerRefComponent` tables by input alone, which becomes
  `open { ComputerComponent, ComputerRefComponent };` with keys such as
  `@ComputerComponent.<Code> Code.Plus<MathExpr>: EvalAdd`. `add_mult_code` and `add_mult_neg` key by
  both code and input, which becomes one key per pair, such as
  `@ComputerRefComponent.Eval.Plus<MathExpr>: EvalAdd` beside
  `@ComputerRefComponent.ToLisp.Plus<MathExpr>: BinaryOpToLisp<Symbol!("+")>`; the four per-operator
  bundles and their inner tables then disappear. A probe converted `add_mult_code` this way: the
  context compiled, passed a check that includes `Times` for both codes, and evaluated and converted
  `2 * (3 + 4)` to the same results. The one rule to respect is that a table cannot key a code both
  on its own and per input, per
  [dispatching per type](../../../cgp/guides/dispatching-per-type.md#dispatch-on-a-later-parameter-with-a-longer-path-key-not-useinputdelegate).
- **Adopt `#[uses]`.** The providers state eleven dependencies as hand-written `where Self: …` bounds,
  such as `Self: CanCompute<Code, MathExpr, Output = Output>` on `EvalAdd`; `#[uses]` takes the same
  bounds as imports, per [declaring dependencies](../../../cgp/guides/declaring-dependencies.md). The
  `HasLispExprType` and `HasMathExprType` bounds are abstract-type imports, which `#[use_type]` is for,
  per [importing abstract types](../../../cgp/guides/importing-abstract-types.md).
- **Derive `CgpData`.** `MathExpr`, `LispExpr`, `MathPlusExpr`, and the four local `LispSubExpr`
  enums list `HasFields`, `FromVariant`, and `ExtractField`; `#[derive(CgpData)]` is the umbrella form.

`BinarySubExpression` is the crate's one getter trait, and it stays one: it reads fields of the
provider's input, not of its context, which an `#[implicit]` argument cannot do.

## Housekeeping

- **`EvalSubtractWithNegate` is unwired** — it is defined in `providers/eval/subtract.rs` and no
  context uses it. As a `Computer` provider for `Minus`, it could serve a context that evaluates the
  extended language by value; otherwise it is worth removing. See
  [evaluation providers](reference/eval-providers.md#evalsubtractwithnegate).
- **An unread type binding** — `add_mult` wires `MathExprTypeProviderComponent`, which none of its
  providers reads.

## Public material derived from this

The source changes the planned deep dive's page 3 depends on, listed under Modernization.
