# Namespace override conflict

Wiring claims a key or path that a namespace already claims — a context re-wiring a path its joined namespace registers, a child namespace redefining an entry it inherits, or either of them binding a prefixed component by its bare marker rather than its path — and the specific entry collides with the namespace's blanket impl, so the compiler rejects the overlap with `E0119`.

## What triggers it

This class is the failure of a natural-seeming intent: "the namespace sets this, but I want something different here." A namespace's entries cannot be replaced from below: a context, or a child namespace, may add an entry only for a key the namespace *routes* to without *terminating*. A key the namespace itself binds (through a `:` body entry, a [`#[default_impl]`](../../reference/attributes/default_impl.md), or an inherited entry) is already covered by the namespace's blanket impl, so a second, more specific impl for that same key overlaps it. The overlap takes two shapes, by whether the specific entry sits on a context or inside a namespace, and the namespace one has a further face where the collision is an accident of notation rather than an override.

The **context-level** shape is a context that joins a namespace and then directly wires a path the namespace registers:

```rust
#[cgp_impl(new GreetHello)]
#[default_impl(@app.GreeterComponent in AppNamespace)] // AppNamespace binds this path
impl Greeter { /* … */ }

delegate_components! {
    App {
        namespace AppNamespace;

        @app.GreeterComponent: GreetBye, // tries to override a path the namespace binds
    }
}
```

The **namespace-level** shape is a child namespace that inherits a parent and redefines one of the parent's keys:

```rust
cgp_namespace! {
    new BaseNs {
        GreeterComponent: GreetHello,
    }
}

cgp_namespace! {
    new ChildNs: BaseNs {
        GreeterComponent: GreetBye, // tries to override an inherited entry
    }
}
```

The namespace-level shape has a second face, and it is the one a prefixed component provokes. A component registered with [`#[prefix(...)]`](../../reference/attributes/prefix.md) is answered by the namespace through a *redirect*, so a child namespace that binds the component's bare marker — in its body, or through a [`#[default_impl]`](../../reference/attributes/default_impl.md) on a provider — collides with the inherited redirect:

```rust
#[cgp_component(Greeter)]
#[prefix(@app in DefaultNamespace)] // answered as a redirect to `@app.GreeterComponent`
pub trait CanGreet {
    fn greet(&self) -> String;
}

cgp_namespace! {
    new AppNamespace: DefaultNamespace
}

#[cgp_impl(new GreetHello)]
#[default_impl(GreeterComponent in AppNamespace)] // should be `@app.GreeterComponent`
impl Greeter { /* … */ }
```

Here nothing is being overridden on purpose: the key is simply written in the wrong form. A prefixed component is addressed by its path, so the registration must read `@app.GreeterComponent`, and writing the bare marker claims a key the inherited namespace already answers.

All three reduce to "a specific entry for a key the namespace's blanket impl already covers." In the context case the blanket impl is the `namespace N;` forwarding `impl<Key> DelegateComponent<Key> for App where Key: N<App>`; in the namespace case it is the inheritance forwarding `impl<Table, Key, Value> ChildNs<Table> for Key where Key: BaseNs<…>`. Either way, CGP lowers both the blanket impl and the specific entry faithfully and cannot see from one macro invocation that they claim the same key, so it defers the overlap to the compiler.

## The raw diagnostic

This section describes what plain `cargo check` prints — the fallback when `cargo-cgp` is not on hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers the readable form. This is a **structural** class reported as **[`E0119`](../error_codes/e0119.md) conflicting implementations**, with the two-caret shape — "first implementation here" on the namespace's blanket source, and "conflicting implementation" on the specific entry — landing on the entries the user wrote. What the specific side of the overlap *names* is the signature that tells this class from the generic-versus-generic [overlapping namespace forwarding](namespace-forwarding-conflict.md): here one impl is keyed on a *concrete* key. The two shapes differ in the details, and recognizing each on sight tells a reader which override they attempted.

The **context-level** shape produces a **pair** of `E0119`s, because a context is wired through both the `DelegateComponent` table and the `IsProviderFor` forwarding: one conflict on `DelegateComponent<PathCons<…>>` for `App` and one on `IsProviderFor<PathCons<…>, _, _>` for `App`, the conflicting key expanded into the long `PathCons<Symbol<…>>` path type (read the caret, not the type). This shape additionally carries a `note: downstream crates may implement trait IsProviderFor<PathCons<…>, _, _> for type GreetHello` (and for the overriding provider), which is `rustc` making its coherence reasoning explicit: whether the namespace's blanket forwarding and the direct path entry overlap hinges on whether the redirect's delegate provider implements `IsProviderFor` for that path, a bound a downstream crate could add, so the compiler cannot rule the overlap out and cites the hypothetical impl. That future-compatibility (negative-reasoning) rule is the same one [RFC 2451](https://rust-lang.github.io/rfcs/2451-re-rebalancing-coherence.html) formalizes and that the [conflicting wiring](conflicting-wiring.md) class explains in full.

The **namespace-level** shape produces a **single** `E0119` — `conflicting implementations of trait ChildNs<_> for type GreeterComponent` — and **no** downstream note. There is only one conflict because a `cgp_namespace!` block emits only its own lookup-trait impls (`ChildNs<Table> for Key`), never the context-side `DelegateComponent`/`IsProviderFor` pair, so nothing doubles it. There is no downstream note because the overlap is provable locally: the inheritance blanket impl covers `GreeterComponent` exactly when `GreeterComponent: BaseNs<…>`, an impl the same crate already emitted for the parent, so the compiler constructs the conflict without reasoning about any future impl. The self type of the conflict is the *component marker* (`GreeterComponent`), not the context, which is the tell that the collision is inside the namespace's own table rather than on a context.

## Where the root cause is

The root cause is **present and precise** in both shapes: the two carets name the namespace source and the overriding entry, and the error code names the collision. This is a structural class with no note chain to walk and nothing suppressed. The one reading skill it asks for is to look past the expanded `PathCons<Symbol<…>>` key type on the context-level shape and trust the caret, and to read the `downstream crates may implement …` note as coherence's *reason*, not a second, separate problem. What neither shape states is the CGP-specific remedy, since the message frames a namespace override decision as a bare coherence conflict.

## How cargo-cgp presents it

`cargo-cgp` rewrites every shape, and the code it stamps says which mistake was made. The **context-level** shape is rewritten as follows: keeping `E0119`, it collapses the `DelegateComponent` + `IsProviderFor` pair into one message, suppresses the `downstream crates may implement …` note, resugars the `PathCons<Symbol<…>>` key to its bare `@app.…` path, and stamps **`[CGP-E005]` overlapping wiring** — `` [CGP-E005] `App` cannot wire `@app.GreeterComponent.*` that is already set through `AppNamespace` ``. That headline names the overriding entry, the path it claims, and the namespace that already binds it, so the reader sees the override decision the raw coherence conflict only implied; the two `rustc` carets are kept, this being a structural class with no `root cause:` tree.

The **namespace-level** shape is rewritten the same way, with the namespace standing where the context does. Which code it takes depends on how the parent answers the colliding key, because that is what decides the fix. A key the parent *binds* is a genuine override attempt and reads as **`[CGP-E005]`** — `` [CGP-E005] `ChildNs` cannot wire component `GreeterComponent` that is already set through `BaseNs` `` — naming the parent the reader has to change instead. A key the parent *redirects*, the prefixed-component face above, is a key written in the wrong form rather than an override, so `cargo-cgp` normalizes the parent's `Delegate` for that key to recover the path and reads it as **`[CGP-E007]`** — `` [CGP-E007] component `GreeterComponent` on `AppNamespace` is redirected to `@app.GreeterComponent` `` — putting the entry to write in a `help`: `` wire the provider `GreetHello` with the key `@app.GreeterComponent` ``. Both keep rustc's two carets, this being a structural class with no `root cause:` tree. The codes are defined in the [cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md).

## Resolving it

The fix depends on which mistake was made. The two genuine overrides follow one rule: **a namespace entry, once bound, cannot be overridden — only a path the namespace leaves unbound is overridable.** The third, a prefixed component bound by its bare marker, is not an override at all and is fixed by writing the key as a path.

For the **context-level** shape, override by targeting a path the namespace *routes to* but does not itself *terminate*: register the component's [`#[prefix]`](../../reference/attributes/prefix.md) redirect in a base namespace the context inherits, and leave the leaf path unclaimed so the context can supply it directly. If the namespace genuinely binds the path (a `:` body entry or a `#[default_impl]`), it is not overridable on the context — change it in the namespace instead, or move the binding out of the namespace so the leaf stays open. The [namespaces guide](../../guides/namespaces-and-prefixes.md) works this through: `MockApp` overrides `@app.finance.MoneyTransferrerComponent` precisely because `MockNamespace` deliberately does not register that path.

For the **namespace-level** shape, first tell the two faces apart. When the message names a redirected path, the fix is only to write the key in that form — `@app.GreeterComponent` rather than the bare `GreeterComponent` — since a prefixed component is addressed by its path and nothing is being overridden at all.

For a genuine override, do not bind the key in the base and redefine it in the child. To vary a key per configuration, leave it *unbound* in the shared base namespace and bind it in each inheriting namespace, so each child supplies the key without overriding an inherited one — the separation the guide recommends between a base namespace that describes an application's *structure* and inheriting namespaces that each describe one *configuration*.

## Notes for tooling

Every shape is reshaped today, so the class has no outstanding tooling gap. What is worth preserving is the discrimination the messages rest on: the subject of a namespace-level collision is the namespace's own lookup trait rather than a context, and the code turns on whether the parent *binds* the colliding key (`[CGP-E005]`, an override to undo) or *redirects* it (`[CGP-E007]`, a key to rewrite as a path) — a distinction only the normalized `Delegate` answers, never the error text.

## Backing fixtures

The `.rust.stderr` snapshot pins the raw `E0119` shape and the `.cgp.stderr` the reshaped form.

- [`wiring/namespace-paths/override_registered_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/wiring/namespace-paths/override_registered_path.rs) — the context-level shape: a context joining `AppNamespace` overrides a path bound with `#[default_impl]`; the `.rust.stderr` pins the `E0119` pair on `DelegateComponent<PathCons<…>>` and `IsProviderFor<PathCons<…>, _, _>` for `App` with the expanded path type and the `downstream crates may implement` note, the `.cgp.stderr` the single `[CGP-E005]` headline with the resugared `@app.GreeterComponent.*` path.
- [`wiring/namespace-paths/inherited_override_conflict.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/wiring/namespace-paths/inherited_override_conflict.rs) — the namespace-level shape against a key the parent *binds*: a child namespace redefining an inherited entry; the `.rust.stderr` pins the single `E0119` on `ChildNs<_>` for `GreeterComponent`, with "first implementation here" on the inherited parent and no downstream note, and the `.cgp.stderr` the `[CGP-E005]` headline naming the parent that already sets the key.
- [`wiring/namespace-paths/namespace_inherited_unprefixed_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/wiring/namespace-paths/namespace_inherited_unprefixed_key.rs) — the namespace-level shape against a key the parent *redirects*: a `#[default_impl]` binding a prefixed component's bare marker in a namespace inheriting `DefaultNamespace`; the `.cgp.stderr` pins the `[CGP-E007]` headline and the `help` naming `@app.GreeterComponent`. Its context-level counterpart is [`namespace_unprefixed_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/wiring/namespace-paths/namespace_unprefixed_key.rs), where a context joining a namespace makes the same mistake.

## Related

- [Overlapping namespace forwarding](namespace-forwarding-conflict.md) — the sibling namespace `E0119`, a *blanket*-versus-blanket overlap over every key (fully-generic `DelegateComponent<_>`); contrast it by the concrete key one side names here.
- [Conflicting wiring](conflicting-wiring.md) — the general `E0119`/`E0428` class for a key or name declared twice, and the full account of the RFC 2451 coherence reasoning behind the `downstream crates may implement` note.
- [Orphan-rule violation](orphan-rule.md), [Wiring cycle](wiring-cycle.md), [Namespace inheritance cycle](namespace-inheritance-cycle.md), [Unconstrained generic](unconstrained-generic.md) — the sibling structural classes.
- [`#[cgp_namespace]`](../../reference/macros/cgp_namespace.md) (and its Known issues), [`DefaultNamespace`](../../reference/traits/default_namespace.md), and the [namespaces guide](../../guides/namespaces-and-prefixes.md) — the inherit-and-override mechanics and the rule that a bound entry is not overridable.
- [Debugging CGP compile errors](../../guides/debugging.md) — the `E0119` entry in the decoder.
