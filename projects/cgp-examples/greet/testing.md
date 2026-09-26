# Testing

`greet` has no tests and no check blocks, so the only verification the repository carries is that the
crate builds and its binaries run. On the `v0.8.0` branch all three build, and each prints
`Hello, Alice!` for a `Person` named Alice. This document records what that shows and what nothing
exercises.

## What running the binaries shows

Each binary's `main` constructs one `Person` and calls `greet`, so a run confirms three things per
program: the wiring resolves, the implicit `name` argument reads the field, and the provider's message
is the one printed.

| Binary | Printed | So the run confirms |
|---|---|---|
| `greet-function` | `Hello, Alice!` | the `#[cgp_fn]` blanket impl applies to `Person` |
| `greet-component` | `Hello, Alice!` | `Person`'s wiring entry selects `GreetHello` |
| `greet-abstract-type` | `Hello, Alice!` | `GreetHello` accepts `Person`'s `Name = String` through `#[use_type]` |

Because the wiring is lazy, the call in `main` is also what checks it. A wiring mistake in these
programs fails at that call rather than at the wiring, which is the gap recorded in
[issues.md](issues.md#missing-features).

## What a probe ran

A probe crate compiled and called the library's hand-written expansion, which no binary uses. A
context wired through it greeted as expected, and a context that implements the provider trait for
itself without a wiring entry did not compile against it, while the same context compiles against the
macro's component; see [expansion.md](expansion.md#how-it-differs-from-the-macro).

## What is untested

These have no test, and the runs and probe above are the only evidence:

- **`GreetHi`** — no context wires it, so its message is never printed.
- **`greet_expanded.rs`** — nothing in the repository uses it; only the probe did.
- **Compile failures** — there are no compile-fail tests.

## Public material derived from this

None yet.
