# Issues

This document records what is wrong with or missing from `expression` on the `v0.8.0` branch,
grouped as defects, missing features, and housekeeping. Every entry was confirmed
against the source, by a probe crate where it says so. Remove an entry in the same change that fixes
it in the crate, per [../../AGENTS.md](../../AGENTS.md#the-shape-of-a-project-section).

## Defects

No defect has been confirmed. Every context that has a test passes it, and a probe ran the two that do
not and got the expected results.

## Missing features

- **Two contexts have no test** — `add_mult_binary_op` and `add_mult_code` are exercised only by their
  checks. See [testing.md](testing.md#what-is-untested).
- **`BinaryOpToLisp` cannot convert the new operators** — `Minus` does not derive `HasField`, so it does
  not implement `BinarySubExpression`, and a context that converts the extended language could not use
  `BinaryOpToLisp` for it without that derive. See [types](reference/types.md#minus-and-negate).

## Housekeeping

- **`EvalSubtractWithNegate` is unwired** — it is defined in `providers/eval/subtract.rs` and no
  context uses it. As a `Computer` provider for `Minus`, it could serve a context that evaluates the
  extended language by value; otherwise it is worth removing. See
  [evaluation providers](reference/eval-providers.md#evalsubtractwithnegate).
- **An unread type binding** — `add_mult` wires `MathExprTypeProviderComponent`, which none of its
  providers reads.

## Public material derived from this

None yet.
