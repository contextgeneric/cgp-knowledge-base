# Unregistered namespace path

A context joins a namespace that *routes* a component to a path but never *binds* a provider at that
path, so the lookup finds no delegate, and a check surfaces the failure as an `E0277` naming the
path-keyed `DefaultNamespace` (or `DelegateComponent`) bound that has no impl.

## What triggers it

This class is a *lookup* failure rather than a *dependency* failure: no provider is found for the
component at all, as opposed to a provider being found whose `where` clause is unmet. It arises when
a component is registered into a [namespace](../../reference/macros/cgp_namespace.md) under a path,
through [`#[prefix]`](../../reference/attributes/prefix.md), and a context joins that namespace, but
nothing ever terminates the path with a concrete provider. The prefix registers the *routing* (the
namespace resolves the component to a `RedirectLookup` along the path), yet the path itself stays
empty because the author forgot the `#[default_impl]`, the namespace body entry, or the direct
wiring that would place a provider there.

```rust
#[cgp_component(Greeter)]
#[prefix(@app in DefaultNamespace)] // routes GreeterComponent to @app.GreeterComponent
pub trait CanGreet {
    fn greet(&self) -> String;
}

#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self) -> String { "Hello".to_owned() }
}

pub struct App;

// App joins the namespace, so GreeterComponent follows the @app.GreeterComponent
// redirect — but nothing (no #[default_impl], no body entry, no direct line) ever
// binds GreetHello, or anything, at that path.
delegate_components! {
    App {
        namespace DefaultNamespace;
    }
}

check_components! {
    App {
        GreeterComponent,
    }
}
```

The same shape appears whenever a redirect lands on an empty path: a context whose joined namespace
does not inherit the base namespace a component was prefixed into, a `@`-path entry with a mistyped
or too-short segment, or a component prefixed under one path but wired under another. In every case
the redirect resolves to a table slot that holds nothing.

## The raw diagnostic

This section describes plain `cargo check`, the fallback when `cargo-cgp` is not on hand. This is a **surfaced**
class, and the root cause is the primary error. A check produces an `E0277` saying the *path* does not implement
the namespace lookup trait, with the caret on the checked entry:

```text
error[E0277]: the trait bound `PathCons<Symbol<3, Chars<'a', _>>, _>: DefaultNamespace<App>` is not satisfied
```

The failing bound's `Self` is a `PathCons<…>` path rather than a component marker, which is the class's signature.
The nightly `cargo-cgp` pins leads one bound higher, on `RedirectLookup<App, PathCons<…>>: IsProviderFor<_, App>`,
and drops the `DefaultNamespace` help list below, so there a `RedirectLookup` over a `PathCons` path is the
signature.

Two notes confirm the reading. `` required for `App` to implement `DelegateComponent<PathCons<…>>` `` names the
missing table entry, and `` required for `RedirectLookup<App, PathCons<…>>` to implement `IsProviderFor<GreeterComponent, App>` ``
names the [`RedirectLookup`](../../reference/providers/redirect_lookup.md) provider the redirect resolved to. A
`Self` that is one of these, rather than a provider struct, means the failure is in the lookup. The compiler
elides the path and names a `long-type-….txt` file that holds it in full.

The `help:` list reads at first like a contradiction. `the following other types implement trait DefaultNamespace<Components>`
lists markers the namespace resolves, which can include the bare `GreeterComponent`. A marker that implements the
trait beside a path that does not means the `#[prefix]` registration succeeded and only the binding at the path is
missing.

The lookup is the first obligation to fail. Proving `App: CanUseComponent<GreeterComponent>` goes through
`RedirectLookup`, which implements the provider trait only where `App: DelegateComponent<Path>`, and no impl exists at
that path. In a [check-trait failure](check-trait-failure.md), by contrast, a provider is found and the solver
descends into its `where` clause.

## Where the root cause is

The root cause is **present at the top**, in the primary `E0277` and its first `required for … DelegateComponent<PathCons<…>>`
note. The `PathCons<…>` key says which path is unbound; read the `long-type-….txt` file for its full form.

Exercised by a call on the context, the same wiring produces the
[hidden `E0599`](../hidden/unsatisfied-dependency.md), naming only `App: CanGreet`, because the method probe drops the
nested lookup bound. So only a check reveals which path is empty.

## How cargo-cgp presents it

`cargo-cgp` keeps the `E0277` code and replaces the headline with the empty path,
`` [CGP-E001] missing wiring for `@app.GreeterComponent` on `App` ``, stated again in a
`` root cause: [CGP-E113] missing wiring for `@app.GreeterComponent` on `App` `` note. The tree is short: a
`[CGP-E101]` consumer hop, a `[CGP-E103]` redirect hop naming the path, then the leaf. The path reads in its surface
`@` notation throughout.

The shape scales with how the redirect fails. A deep prefix renders its whole path
(`@app.finance.types.QuantityTypeProviderComponent`), a chain of redirects prints one `[CGP-E103]` hop per link
(`@start.GreeterComponent`, `@middle`, `@end`), and an `open` dispatch missing a key names the type in the path
(`@ItemEncoderComponent.Vec<u8>`). A path missing from an aggregate provider, which `open`s the component in its own
table or joins the namespace itself, ends on the `[CGP-E114]` leaf instead,
`` missing entry for `@ComputerComponent.Sink.Digest` in provider `ByteSink` ``, and the hop above reads `` in `ByteSink` ``.

A `help` names the entry to write, `` wire `@app.GreeterComponent` to a provider in the wiring of `App` `` or
`` add an entry for `@ComputerComponent.Sink.Digest` to `ByteSink` ``. When the context wires a likely slip of the key,
such as a recased symbol or a doubled prefix segment, a near miss comes first:
`` a similar key exists in the wiring of `App`: `@App.GreeterComponent` ``. The
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) defines the codes.

## Resolving it

Bind a provider at the path the component routes to: register it with
[`#[default_impl(@app.GreeterComponent in Namespace)]`](../../reference/attributes/default_impl.md), add a namespace
body entry (`@app.GreeterComponent: GreetHello`) in the namespace's crate, or wire the path directly on the context,
per the [namespaces guide](../../guides/namespaces-and-prefixes.md). When a prefix and a wiring disagree on the path, or
a joined namespace does not inherit the base the component was prefixed into, reconcile them.

A related variant resolves to a delegate that is not a provider for the component: a path wired to the wrong provider
fails on the provider's own trait rather than the lookup, and the fix is to wire a provider that implements it.

## Notes for tooling

A marker that resolves beside a path that does not shows the binding alone is missing, so a tool could add "you likely
forgot a `#[default_impl]` or body entry". The `[CGP-E113]` `help` names the entry to write, without that reason.

## Backing fixtures

- [`checks/unregistered-namespace-path/unregistered_prefix_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/unregistered_prefix_path.rs):
  a `#[prefix]`ed `Greeter` joined through `DefaultNamespace`, with nothing bound at `@app.GreeterComponent`.
- [`checks/unregistered-namespace-path/qualified_prefix_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/qualified_prefix_path.rs):
  a deep prefix whose leaf renders the full `@app.finance.types.QuantityTypeProviderComponent` path.
- [`checks/unregistered-namespace-path/multi_redirect_missing.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/multi_redirect_missing.rs):
  a chain of redirects that never terminates, one `[CGP-E103]` hop per link.
- [`checks/unregistered-namespace-path/open_missing_type_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/open_missing_type_key.rs):
  an `open` dispatch missing a type key, named in the path (`@ItemEncoderComponent.Vec<u8>`).
- [`checks/check-trait-failure/missing-wiring/open_aggregate_missing_entry.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/open_aggregate_missing_entry.rs):
  an aggregate provider that `open`s `ComputerComponent` and lacks the input the check asks for: the `[CGP-E114]` leaf.
- [`checks/unregistered-namespace-path/namespace_aggregate_missing_entry.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/namespace_aggregate_missing_entry.rs):
  a path-keyed aggregate that joins `DefaultNamespace` itself and lacks `@app.NamerComponent`: the `[CGP-E114]` leaf.
- [`checks/unregistered-namespace-path/namespace_not_inheriting_base.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/namespace_not_inheriting_base.rs):
  a context joining a namespace that does not inherit the namespace its component is prefixed into.
- [`checks/unregistered-namespace-path/near_miss_in_another_context.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/near_miss_in_another_context.rs):
  two contexts miss `@app.GreeterComponent`, and only `Other` wires the near miss `@App.GreeterComponent`.
- [`checks/unregistered-namespace-path/prefix_case_slip.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/prefix_case_slip.rs):
  `@App.GreeterComponent` wired where the component's prefix is `@app`.
- [`checks/unregistered-namespace-path/prefix_doubled_marker_generic.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/prefix_doubled_marker_generic.rs):
  a prefix that repeats the component marker the path already appends.

## Related

- [Check-trait failure (surfaced)](check-trait-failure.md): the sibling surfaced class, where a
  provider *is* found but its dependency is unmet; contrast the position of the cause (a `help:`
  note there, the primary error here) and the failing bound (a concrete `HasField` there, a
  `PathCons` lookup here).
- [Unsatisfied dependency (hidden)](../hidden/unsatisfied-dependency.md): the `E0599` shape this
  class takes when exercised by a method call instead of a check; a missing wiring and an unmet
  dependency are indistinguishable in that hidden form.
- [Verbose dependency cascade](verbose-cascade.md): when several components route through the same
  empty path, this diagnostic multiplies the same way.
- [`cgp_namespace!`](../../reference/macros/cgp_namespace.md),
  [`RedirectLookup`](../../reference/providers/redirect_lookup.md),
  [`DefaultNamespace`](../../reference/traits/default_namespace.md), and the
  [namespaces guide](../../guides/namespaces-and-prefixes.md): the routing mechanics and the wiring
  that fills a path.
- [Debugging CGP compile errors](../../guides/debugging.md): the `DelegateComponent`/`Namespace`
  "lookup failed" entry in the decoder.
