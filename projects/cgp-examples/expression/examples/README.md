# `expression` contexts

This directory documents each of the crate's four contexts as the program it is: what it wires, what
its checks and tests pin, and what it demonstrates. The crate has no binary, so each context runs
only through its tests, and two of the four have none; those two were run in a probe crate for
these documents.

## How these differ from the worked example

**These documents record the contexts as the crate ships them; the
[expression interpreter](../../../../examples/expression-interpreter.md) worked example is the teaching
progression to learn from.** The worked example develops the same interpreter in the same order and
stands alone. The documents here each describe one context module with its checks, its tests, and its
gaps, so an agent changing the crate knows what it is changing.

## Running them

The tests run from the repository root with `cargo test -p cgp-example-expression`. The table records
what each context has and what running its tests produced on the `v0.8.0` branch:

| Context | Test | Result |
|---|---|---|
| [`add_mult`](add-mult.md) | `test_add_mult`, `test_add_mult_to_lisp` | both pass |
| [`add_mult_binary_op`](add-mult-binary-op.md) | none | no test; a probe evaluated `2 * (3 + 4)` to `14` and converted it to `(* 2 (+ 3 4))` |
| [`add_mult_code`](add-mult-code.md) | none | no test; the same probe gave the same two results |
| [`add_mult_neg`](add-mult-neg.md) | `test_add_mult_neg` | passes |

## The catalog

The order is the order the contexts teach in, from two separate operations to an extended language.

- [add-mult.md](add-mult.md) — evaluation by value and conversion by reference, each in its own
  input-keyed table.
- [add-mult-binary-op.md](add-mult-binary-op.md) — the same, with `BinaryOpToLisp` replacing the two
  per-operator conversion providers.
- [add-mult-code.md](add-mult-code.md) — both operations by reference in one component, keyed by input
  and then by operation code.
- [add-mult-neg.md](add-mult-neg.md) — the extended language with subtraction and negation, wired for
  evaluation alone.

## Public material derived from this

None yet.
