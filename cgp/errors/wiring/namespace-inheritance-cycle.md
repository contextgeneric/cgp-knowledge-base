# Namespace inheritance cycle

Two namespaces that inherit from each other make resolving any key chase the inheritance chain
forever, so the trait solver overflows with `E0275`, reported *at the `cgp_namespace!` definitions
themselves*. A namespace that names itself as its parent, by its bare name or a `self::` path, never
reaches the compiler: `cgp_namespace!` rejects it.

## What triggers it

The mistake is a circular parent chain among namespaces: `A` names `B` as its parent while `B` names
`A`. A [namespace](../../reference/macros/cgp_namespace.md) inherits
its parent through a blanket impl whose `where` clause requires the parent's lookup trait, so a
parent chain that loops back on itself produces a `where` clause that can never be discharged.

```rust
cgp_namespace! {
    new NamespaceA: NamespaceB {} // A inherits B
}

cgp_namespace! {
    new NamespaceB: NamespaceA {} // B inherits A — the chain loops
}
```

`new NamespaceA: NamespaceB` emits the inheritance blanket impl
`impl<Table, Key, Value> NamespaceA<Table> for Key where Key: NamespaceB<…>, Key: NamespaceB<Table, Delegate = Value>`,
and `new NamespaceB: NamespaceA` emits the mirror. CGP cannot see the parent chain is circular from
one macro invocation (each `cgp_namespace!` knows only its own parent) so it lowers each namespace
faithfully and defers the contradiction to the compiler. A self-inheriting `new A: A {}` is the one
cycle a single invocation shows, so the macro rejects it with
``the namespace `A` cannot inherit from itself``, the caret on the parent's name, as it rejects a
parent that is another instance of the namespace, such as `<T> new A<T>: A<u32>`, or the namespace
through a `self::` path. A parent through any other path, such as `crate::A`, names an item the
macro cannot resolve, so that cycle reaches the compiler as an `E0207` on the generated `__Value__`.

## The raw diagnostic

This section describes what plain `cargo check` prints, and for this one class it is the *only*
place the error appears, because
[`cargo-cgp` does not report it at all](#how-cargo-cgp-presents-it). Stable reports **`E0275`
"overflow evaluating the requirement"**, and the defining property of this class is *where* it
lands: on the `cgp_namespace!` blocks that define the namespaces, with no context or use site
required. Evaluating the well-formedness of `NamespaceA`'s inheritance impl means evaluating its
`where` bound `__Key__: NamespaceB<…>`, which pulls in `NamespaceB`'s impl and its bound
`__Key__: NamespaceA<…>`, which pulls in the first again: an infinite chain. The overflow message
names the requirement that recurses (`__Key__: NamespaceA<__NamespaceBComponents>`), a `note:` chain
that walks `NamespaceB<…>` → `NamespaceA<…>` and names the loop, a
`= note: N redundant requirements hidden` marking the collapsed repetition, and the standard
`help: consider increasing the recursion limit`. Each of the two definitions carries its own
`E0275`.

This eager, definition-site failure is the sharp contrast with the sibling
[wiring cycle](wiring-cycle.md). A [`UseContext`](../../reference/providers/use_context.md)
delegation cycle is *lazy*: the wiring is accepted, and the overflow appears only when the wiring is
forced through a check (and hides as an [`E0599`](../hidden/unsatisfied-dependency.md) when reached
by a plain call). A namespace inheritance cycle is *eager*: the cycle lives in the `where` clause of
a generated blanket impl, and the compiler evaluates that clause when it checks the impl, so the
overflow fires at the definition before anything uses the namespace. A context that *does* join the
cycle and is then checked simply adds more `E0275` blocks (an
`App: DelegateComponent<GreeterComponent>` overflow at the check) on top of the definition-site
ones; it does not change the cause.

The overflow itself is ordinary `rustc` behavior. The trait solver walks a requirement's supporting
bounds to a bounded depth (the
[default `recursion_limit` is 128](https://doc.rust-lang.org/reference/attributes/limits.html)) and
reports [`E0275`](../error_codes/e0275.md) when it exceeds that depth without terminating. A genuine
cycle never terminates, so the limit is only ever reached, never cleared; the `help:` suggestion to
raise it is generic advice the compiler prints for every overflow and does not apply here.

## Where the root cause is

The cause is **present and the diagnostic points straight at it**: the two `E0275` carets land on
the two `cgp_namespace!` definitions, and the `note:` chain names both namespaces and the loop
between them. Unlike a hidden failure there is nothing to promote and nothing suppressed: the
participants are all named. What the diagnostic does not state is the remedy, and it actively
misleads on it: the `help: increase the recursion limit` line suggests a fix that cannot work,
because the requirement does not terminate at any depth. Read the overflow as "these namespaces'
parent chain is circular," not as "the chain is merely deep."

## How cargo-cgp presents it

`cargo-cgp` does not report this error at all: its pinned nightly accepts the mutually-inheriting
namespaces, under the default solver and the next-generation one alike, so there is no `E0275` to reshape.
This is the one class in the catalog where the tool's output is *empty*.

So this class surfaces only for a reader on stable `rustc`. A mutually-inheriting namespace is still a
mistake, only invisible under the tool, so the fix in [Resolving it](#resolving-it) still applies.

## Resolving it

Break the cycle so the parent chain is acyclic: a namespace's inheritance must form a tree, not a
loop. Remove one direction of the mutual inheritance so one namespace is unambiguously the parent,
or, when both namespaces genuinely need a shared set of entries, factor those entries into a third
base namespace that both inherit from, rather than having them inherit each other. Raising
`#![recursion_limit]` is the wrong move: the chain has no terminating step, so no limit is high
enough.

## Backing fixtures

The fixture pins the class's divergence rather than an error, since under the pinned nightly there
is none to snapshot:

- [`wiring/namespace-inheritance-cycle/namespace_inheritance_cycle.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-inheritance-cycle/namespace_inheritance_cycle.rs):
  two namespaces that inherit from each other, which both the default and the next-generation solver
  on the pinned nightly accept, so its `.cgp.stderr` and `.rust.stderr` are empty; its exit-status
  check fails if a later nightly makes the two disagree.

The raw `E0275` described above therefore has no blessed `.rust.stderr`; stable `rustc` prints it,
verified against the compiler rather than against a committed snapshot. The self-inheriting
form's macro rejection is pinned by the `cargo-cgp` fixture
[`pass-through/namespace_self_inherit.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/namespace_self_inherit.rs),
which checks that the tool prints the macro's message as rustc does, the instance form's by
[`pass-through/namespace_inherits_own_instance.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/namespace_inherits_own_instance.rs),
and the `self::` form's by
[`pass-through/namespace_self_inherit_self_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/namespace_self_inherit_self_path.rs).
The unchecked `crate::` form's `E0207`, which the tool passes through, is pinned by
[`pass-through/namespace_self_inherit_crate_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/namespace_self_inherit_crate_path.rs).

## Related

- [Wiring cycle](wiring-cycle.md): the sibling cycle class through
  [`UseContext`](../../reference/providers/use_context.md); both overflow with `E0275`, but that one
  is lazy (surfaces only when checked, hides as `E0599` when called) while this one is eager (caught
  at the namespace definitions).
- [Conflicting wiring](conflicting-wiring.md), [Orphan-rule violation](orphan-rule.md),
  [Unconstrained generic](unconstrained-generic.md): the sibling structural classes.
- [`cgp_namespace!`](../../reference/macros/cgp_namespace.md) and
  [`DefaultNamespace`](../../reference/traits/default_namespace.md): the inheritance blanket impl
  whose `where` clause the cycle poisons.
- [Debugging CGP compile errors](../../guides/debugging.md): the `E0275`/overflow entry in the
  decoder.
