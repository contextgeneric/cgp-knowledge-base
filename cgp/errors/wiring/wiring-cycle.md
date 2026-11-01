# Wiring cycle

A delegation chases its own tail (a component wired to a provider whose resolution routes back to
that same component) so when the wiring is forced through a check the trait solver overflows with
`E0275`.

## What triggers it

The classic cycle is delegating a component to
[`UseContext`](../../reference/providers/use_context.md) when the context's only implementation of
that component *is* that delegation. `UseContext` implements the provider trait by routing back
through the context's own consumer-trait impl, but that consumer impl exists only via this
delegation to `UseContext`, so resolving the provider trait requires resolving the consumer trait,
which requires the provider trait again.

```rust
#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}

#[derive(HasField)]
pub struct Person { pub name: String }

// Person's only source of CanGreet is this delegation to UseContext, which
// resolves back to CanGreet: a cycle with no terminating provider.
delegate_components! {
    Person {
        GreeterComponent: UseContext,
    }
}
```

CGP lowers the wiring faithfully and cannot see that the delegation is self-referential without a
whole-program view, so it accepts the entry and defers the failure to the compiler. A mutual cycle
between two components that each delegate through the other fails the same way, unless another
branch of the resolution also has a real missing dependency. Then plain `rustc` reports that
dependency's `E0277` instead of an overflow.

A lookup that grows without ever repeating overflows the same way, though no obligation recurs. A
provider of `CanShow<T>` that requires `CanShow<Vec<T>>` of its context asks for `CanShow<Vec<T>>`,
then `CanShow<Vec<Vec<T>>>`, and so on without end.

## The raw diagnostic

This section describes what plain `cargo check` prints, the fallback when `cargo-cgp` is not on
hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers the readable form. How
the cycle surfaces depends on how it is exercised, and the two shapes are very different. Forcing
the wiring through a [`check_components!`](../../reference/macros/check_components.md) drives the
solver directly into the loop, and it overflows with **`E0275`**, "overflow evaluating the
requirement `Person: IsProviderFor<GreeterComponent, Person>`", followed by a note chain that *names
the cycle*: `Person` to implement `Greeter<Person>`, then `CanGreet`, then `UseContext` to implement
`IsProviderFor<GreeterComponent, Person>`, then back into `CanUseComponent<GreeterComponent>`. The
loop is visible in the chain. That is stable's output: the nightly `cargo-cgp` pins overflows one
step earlier, on the check's `Person: CanUseComponent<GreeterComponent>`, and prints no chain.

Exercised instead by a plain method call on the context, the same cycle does *not* overflow: the
method probe treats the unresolvable requirement as simply unsatisfied and reports a
[hidden `E0599`](../hidden/unsatisfied-dependency.md) (`no method named` on stable, when the context
is what fails to resolve) with no hint that a cycle is the reason. So a wiring cycle is `E0275` when checked and a
hidden `E0599` when called, and only the checked form actually reveals the cause.

The [`E0275`](../error_codes/e0275.md) itself is ordinary `rustc` behavior. The trait solver follows
a requirement's supporting bounds only to a bounded depth (the
[default `recursion_limit` is 128](https://doc.rust-lang.org/reference/attributes/limits.html)) and
raises `E0275` when it exceeds that depth without resolving, appending its standard
`help: consider increasing the recursion limit`. That advice suits a merely *deep* obligation, but a
true cycle never terminates at any depth, so the limit here is only ever hit, never cleared; the
suggestion does not apply and should be read past. This is why the cycle must be exercised through a
check to surface at all: the overflow is computed only when the solver is driven into the loop, and
`#[cgp_component]`'s blanket impl otherwise lets the method probe abandon the requirement as
unsatisfied without ever entering it.

## Where the root cause is

The cause (the cycle) is **present in the checked (`E0275`) form** and readable from the note chain:
the requirement that overflows and the intervening `Greeter<Person>` / `CanGreet` / `UseContext`
notes together trace the loop, so the participants (the component, the consumer trait, and
`UseContext`) are all named. What the diagnostic does *not* state is the remedy. In the hidden
(`E0599`) form the cause is absent, exactly as for any
[hidden unsatisfied dependency](../hidden/unsatisfied-dependency.md), which is itself a reason to
reach for a check when a `UseContext` wiring is suspect.

## How cargo-cgp presents it

`cargo-cgp` recognizes the overflow and rewrites it by how the lookup never resolves, which it
learns by walking the consumer obligation of the check entry, or of the method call, at the caret. A walk that meets an obligation among its
own ancestors is a cycle. The headline keeps the `E0275` code but reads
``[CGP-E020] the wiring for the consumer trait `CanGreet` on context `Person` never resolves, because the lookup leads back to itself``.
The tool drops the `__CheckPerson` note and rustc's advice to raise the recursion limit, and keeps
the caret on the `GreeterComponent` entry inside the check block. A `help:` names the provider whose
requirement closes the loop:
``wire a provider in place of `UseContext`, which provides `Greeter` for `Person` by requiring `CanGreet` on `Person` again``.
Where raw `rustc` hands you an overflow depth and a chain to decode, the tool states that the lookup
loops and which provider closes it.

The `help:` names a provider only when a wiring entry chose it, on the context or through a
redirect. An `open` error route that raises its own `String` through `DebugError` reads as a cycle
that `DebugError` closes
([`debug_error_string_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/debug_error_string_cycle.rs)).
A loop that closes inside a higher-order provider has no such entry: a dispatcher wired as the entry
for the type it dispatches routes each variant back to the context through its inner `UseContext`,
so that block's `help:` says only to wire a provider that does not require the consumer trait it
provides
([`dispatcher_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/dispatcher_cycle.rs)).
In a loop through several entries, the `help:` names the provider whose requirement closes the loop
where the walk met it, which is not always the entry to change: the same fixture's other block names
`EvalAdd`, while the fix is a wrapper provider for the dispatched type's entry.

The growing `CanShow<Vec<T>>` lookup has its own code. The walk reaches its depth cap without
meeting a repeat, so the headline is `[CGP-E021]` and reads
``… never resolves, because each step requires it for a larger type (`CanShow<Vec<u32>>`, …)``,
naming the first larger requirement, and the `help:` names `ShowNested` as the provider whose
requirement grows. The tool drops the recursion-limit advice here too, since no limit ends a lookup
that grows. A lookup can also grow in the type the consumer trait is required of: a provider of
`CanShow` that requires `Vec<Self>: CanShow`, wired for `u32` and every `Vec<T>`, asks for
`Vec<u32>`, then `Vec<Vec<u32>>`. The walk follows each `Vec<…>` as a context, since it carries
wiring, so the same `[CGP-E021]` names the first larger type, `` (`Vec<u32>`, …) ``, and the `help:`
names the provider that requires `CanShow` of it
([`divergent_self_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_self_wiring.rs)).

Any overflow the walk does not cut keeps rustc's wording and notes. A walk that stops at a bound
instead of a cut means that bound's own evaluation overflowed, which no root cause states truly, so
the tool names none: in `cross_context_cycle_reuse_distinct` a cycle runs through a plain trait
bound on another context, which the walk does not follow. An overflow that follows from an
unresolved name in the context's wiring, rather than from the wiring itself, is the other case: its
walk ends with neither cut, and the earlier `E0425` stays the error to fix. A real cycle beside such
a name is still a cycle, since the walk does not descend the `{type error}` the name leaves
([`type_error_in_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/type_error_in_wiring.rs)).

The tool does more than restate the overflow when a cycle is tangled with a recoverable cause, and
this is where its cycle guard earns its keep. In `mutual_cycle_with_cause` (`ProviderA` depends on
`CanB`, `ProviderB` depends back on `CanA`, walked alongside a genuinely missing `width` field) the
resolver cuts the `CanA → CanB → CanA` loop and follows the other branch to the leaf, leading with
`` [CGP-E001] missing field `width` on `App` `` over a
`` root cause: [CGP-E110] missing field `width` on `App` `` dependency tree (`[CGP-E101]`
consumer-impl hop → `[CGP-E102]` provider-impl hop → `[CGP-E104]` `HasWidth` hop → the leaf). The
cycle is not the headline; the concrete cause reachable down the non-cyclic branch is.

Reached by a method call instead of a check, the cycle reads the same. On the nightly `cargo-cgp`
pins, the call overflows on the consumer trait itself (`Person: CanGreet`), where stable prints the
hidden `E0599`. The tool walks the call's consumer obligation as it walks a check entry's, so the
block is the same `[CGP-E020]`, with the caret on the method name and the same `help:`. A check
and a call of the same loop print one block, at the check, since the call's states the same cause. A growing lookup reached by a call is `[CGP-E021]` the same way. The codes are defined in
the [cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md).

## Resolving it

Break the cycle by wiring the component to a concrete provider that terminates the lookup rather
than routing back to the context. `UseContext` is only safe as the *inner* provider of a
higher-order provider or where the context supplies the component through some other impl;
delegating a component's sole implementation to `UseContext` is always a cycle. A provider that
re-enters the context for the very type it provides, such as `DebugError` for `String`, needs a
replacement that produces the value itself, and a lookup that grows needs a provider whose
requirement stays at a fixed type. Raising `#![recursion_limit = "…"]` is the wrong fix, because
neither shape terminates at any depth, so no limit is high enough.

## Backing fixtures

- [`wiring/wiring-cycle/use_context_cycle.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle.rs):
  a component wired to `UseContext` with no terminating provider, forced through a
  `check_components!`; its `.rust.stderr` pins the raw `E0275` overflow as the pinned nightly prints
  it, on `Person: CanUseComponent<GreeterComponent>` with no note chain (stable overflows on
  `Person: IsProviderFor<GreeterComponent, Person>` and prints the `Greeter<Person>` → `CanGreet` →
  `UseContext` chain), and its `.cgp.stderr` the `[CGP-E020]` "leads back to itself" rewrite with
  the chain dropped, the caret held on the `GreeterComponent` entry, and a `help:` naming
  `UseContext`.
- [`wiring/wiring-cycle/use_context_cycle_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle_call.rs):
  the same wiring reached by a method call, an `E0275` on `Person: CanGreet` that the tool rewrites
  to the same `[CGP-E020]` with the `help:` naming `UseContext`, the caret on the method name.
- [`wiring/wiring-cycle/use_context_cycle_check_and_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle_check_and_call.rs):
  the same wiring reached by a check and a call; the compiler reports both overflows, and the tool
  prints one `[CGP-E020]` at the check entry, dropping the call's as a repeat of the same mistake.
- [`wiring/wiring-cycle/debug_error_string_cycle.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/debug_error_string_cycle.rs):
  an `open` error raiser routing `String` to `DebugError`, which raises through
  `CanRaiseError<String>` again; a `[CGP-E020]` whose `help:` names `DebugError`.
- [`wiring/wiring-cycle/type_error_in_wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/type_error_in_wiring.rs):
  the same cycle beside a wiring value naming an unresolved type; still a `[CGP-E020]` naming
  `DebugError`, beside the `E0433` for the type.
- [`wiring/wiring-cycle/dispatcher_cycle.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/dispatcher_cycle.rs):
  a dispatcher wired as the entry for the type it dispatches; two `[CGP-E020]` blocks, one whose
  `help:` names `EvalAdd` and one whose loop closes at the dispatcher's inner `UseContext`, so its
  `help:` names no provider.
- [`wiring/wiring-cycle/mutual_cycle_with_cause.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/mutual_cycle_with_cause.rs):
  a two-component cycle (`ProviderA` ↔ `ProviderB`) walked alongside a genuinely missing `width`
  field; its `.rust.stderr` is not an overflow but a raw `E0277` on
  `DoA: IsProviderFor<ProviderAComponent, App>`, and its `.cgp.stderr` shows the resolver's cycle
  guard cutting the loop and leading with `[CGP-E001]` over a
  `` root cause: [CGP-E110] missing field `width` `` tree, the cause down the non-cyclic branch
  rather than the cycle.
- [`wiring/wiring-cycle/cycle_cut_rechecked.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cycle_cut_rechecked.rs):
  the same cycle with both components checked, which merge into one `[CGP-E001]` block over the
  `width` tree; the check of `CanB` resolves only because the resolver does not reuse the subtree
  the first walk cut.
- [`wiring/wiring-cycle/cross_context_cycle_reuse.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cross_context_cycle_reuse.rs):
  a cycle through two contexts (`Inner`'s provider needs `Outer: Linked`, which needs `Outer: CanM`,
  whose provider needs `Inner: CanN`) beside a missing `name` field; `Outer`'s tree keeps only the
  field, because the resolver does not reuse `Inner`'s cached subtree where it would repeat
  `Outer: Linked`.
- [`wiring/wiring-cycle/divergent_wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring.rs):
  the growing `CanShow<Vec<T>>` lookup above; its `.rust.stderr` pins the raw `E0275` and its
  `.cgp.stderr` the `[CGP-E021]` rewrite reached through the depth cap, with a `help:` naming
  `ShowNested`.
- [`wiring/wiring-cycle/divergent_wiring_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring_call.rs):
  the same growing lookup reached by a method call, an `E0275` on `App: CanShow<u32>` that the tool
  rewrites to the same `[CGP-E021]`, dropping rustc's recursion-limit advice.
- [`wiring/wiring-cycle/cross_context_cycle_reuse_distinct.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cross_context_cycle_reuse_distinct.rs):
  the two-context cycle with errors that share no cause, so `Outer`'s tree shows only its missing
  `name` field, pinning that the resolver does not reuse a cached subtree that would repeat an
  ancestor; `Inner`'s overflow, which the walk does not cut, keeps rustc's wording.
- [`wiring/wiring-cycle/cycle_beside_growing_lookup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cycle_beside_growing_lookup.rs):
  a provider whose requirements both grow and loop through `UseContext`, rewritten to the
  `[CGP-E020]` cycle, since a cycle explains the lookup more exactly than its depth cut.
- [`wiring/wiring-cycle/divergent_self_wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_self_wiring.rs):
  a lookup that grows in the type `CanShow` is required of (`Vec<u32>`, then `Vec<Vec<u32>>`),
  rewritten to `[CGP-E021]` naming the first larger type, with a `help:` naming `ShowWrapped`.
- [`wiring/wiring-cycle/glob_reexported_provider_cycle.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/glob_reexported_provider_cycle.rs):
  a provider reached through glob re-exports of private modules, named in a cycle's help.
- [`wiring/wiring-cycle/glob_reexported_provider_name_shared.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/glob_reexported_provider_name_shared.rs):
  two providers named `EvalAdd`, one glob-imported, each named in a cycle's help.

## Related

- [Unsatisfied dependency (hidden)](../hidden/unsatisfied-dependency.md): the `E0599` shape the same
  cycle takes when exercised by a method call instead of a check.
- [Namespace inheritance cycle](namespace-inheritance-cycle.md): the sibling `E0275` cycle through
  circular namespace inheritance rather than `UseContext` delegation; that one is caught *eagerly*
  at the namespace definitions, where this one is lazy.
- [Conflicting wiring](conflicting-wiring.md), [Orphan-rule violation](orphan-rule.md),
  [Unconstrained generic](unconstrained-generic.md): the sibling structural classes.
- [`UseContext`](../../reference/providers/use_context.md): the provider whose misuse most often
  causes the cycle.
- [Debugging CGP compile errors](../../guides/debugging.md): the `E0275` entry in the decoder.
