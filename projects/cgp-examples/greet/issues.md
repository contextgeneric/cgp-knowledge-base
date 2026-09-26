# Issues

This document records what is wrong with or missing from `greet` on the `v0.8.0` branch, grouped as
defects, missing features, and housekeeping. Every entry was confirmed against the source, by a probe
crate where it says so. Remove an entry in the same change that fixes it in the crate, per
[../../AGENTS.md](../../AGENTS.md#the-shape-of-a-project-section).

## Defects

No defect has been confirmed. Each binary prints what its code says; see
[testing.md](testing.md#what-running-the-binaries-shows).

## Missing features

- **No check blocks** — neither component binary asserts its wiring with
  [`check_components!`](../../../cgp/reference/macros/check_components.md), so a wiring mistake is
  reported at the `greet` call in `main` rather than at the wiring. A check block listing
  `GreeterComponent` for `Person` in each of `greet-component` and `greet-abstract-type` would move it
  there. For wiring this small, `delegate_and_check_components!` would do the same in one macro.

## Housekeeping

- **An outdated hand-written expansion** — `src/greet_expanded.rs` gives a consumer blanket impl that
  routes through `DelegateComponent`, where the macro's requires `Context: Greeter<Context>`, and it
  omits the `UseContext` and `RedirectLookup` impls. A probe showed the difference is observable: a
  context that provides the component for itself, with no wiring entry, has `greet` under the macro
  and not under the module. Regenerating the module from `cargo cgp expand`, or marking it as a
  simplified sketch, would stop it teaching the older shape; see [expansion.md](expansion.md).
- **An unused abstract type** — `bin/greet_component.rs` declares `HasNameType` and never uses it; the
  trait belongs to `greet-abstract-type`.
- **An unwired provider** — `GreetHi` in `bin/greet_component.rs` is never wired. It shows that a
  second provider exists, but the program never demonstrates swapping to it.

## Public material derived from this

None yet.
