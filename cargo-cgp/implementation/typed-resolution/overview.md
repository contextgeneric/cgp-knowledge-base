# Typed root-cause resolution

The resolver turns a CGP wiring failure into a compact, root-cause-first error by asking the
compiler what failed rather than parsing rustc's text. A wiring mistake is reported against
generated types the programmer never wrote, and the fact that matters (a missing field, an unwired
component) sits under `IsProviderFor` and `CanUseComponent` scaffolding, or is dropped. The resolver
recovers the failing obligation, walks the wiring down to each root cause through the trait solver,
and replaces the diagnostic with one coded headline over a `cargo tree`-style dependency chain.

The walk follows the **real consumer and provider obligations**, never the scaffolding, and a change
must keep it that way. `IsProviderFor` exists only so that plain rustc can surface a wiring failure
(see [check traits](../../../cgp/concepts/check-traits.md)): it carries a copy of a provider's `where`
bounds so the compiler names the missing one. The walk re-solves the real provider impl, whose
`where` clause holds the same bounds, and the aim is to make `IsProviderFor` removable. Three places
still touch the scaffolding, each for a stated reason. The check anchor reads a check impl's
`CanUseComponent` assertion to learn which component the entry names, the
[`[CGP-E128]` leaf](leaves.md#the-wiring-without-isproviderfor-leaf) reports a
context that lacks its own `IsProviderFor`, and the
[text-rewrite fallback](../driver/diagnostic-reshapes.md#naming-the-traits-behind-a-component-marker) for a
declined diagnostic reads both names in rustc's rendered output.

Everything downstream of the rustc-free
[`Resolved`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/resolved.rs)
model (the wording, the tree) is tested without a compiler; [Architecture](../architecture.md) places
that line.

## A worked example

One failure end to end shows what the resolver produces. This program is distilled from the
[`base_area_1`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_1.rs)
fixture, itself the failure of the [area-calculation example](../../../examples/area-calculation.md):

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_auto_getter]
pub trait HasRectangleFields {
    fn width(&self) -> f64;
    fn height(&self) -> f64;
}

#[cgp_impl(new RectangleArea)]
impl AreaCalculator
where
    Self: HasRectangleFields,
{
    fn area(&self) -> f64 {
        self.width() * self.height()
    }
}

#[derive(HasField)]
pub struct Rectangle {
    pub width: f64,
    // the `height` field is missing
}

delegate_components! {
    Rectangle {
        AreaCalculatorComponent: RectangleArea,
    }
}

check_components! {
    Rectangle {
        AreaCalculatorComponent,
    }
}
```

The **root cause is the absent `height` field**. Plain rustc reports an unmet
`HasField<Symbol<6, Chars<'h', …>>>` routed through `IsProviderFor` and `CanUseComponent`. The fixture's
snapshot replaces that with:

```text
error[E0277]: [CGP-E001] missing field `height` on `Rectangle`
  --> src/main.rs:64:9
   |
64 |         AreaCalculatorComponent,
   |         ^^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: root cause: [CGP-E110] missing field `height` on `Rectangle`
           this is required through the dependency chain:
             [CGP-E101] consumer trait impl `CanCalculateArea` for context `Rectangle`
             └─ [CGP-E102] provider trait impl `AreaCalculator` with context `Rectangle` for provider `RectangleArea`
               └─ [CGP-E104] trait impl `HasRectangleFields` for `Rectangle`
                 └─ [CGP-E110] missing field `height` on `Rectangle`
   = help: add the field `height: f64` to `Rectangle`
```

The headline states the mistake, and `[CGP-E001]` classes it as a context that cannot implement a
consumer trait. The tree is the obligation chain the walk descended, and it holds no `IsProviderFor`
node because the walk never went through one. The `help` names the field with the type the getter
requires. [error-code.md](../../error-code.md) catalogs the codes.

## When the resolver engages, and when it declines

A diagnostic is a candidate when it reports an **unmet obligation**: `E0271`, `E0277`, or a
method-bounds `E0599` ("the method `…` exists … but its trait bounds were not satisfied"). The gate
goes by code rather than by whether the text names a CGP construct, because a failure that names none
can still come from a component: a hand-written `Send`-recovery wrapper fails with an `E0271` on an
opaque future. The resolver then traces the chain, and a candidate whose chain reaches no CGP cause
**declines** to the text fallback.

The gate excludes these shapes deliberately, and each exclusion prevents a false or fatal result:

- **A resolution-class `E0599`** (`no variant named …`, `no associated item …`) is emitted while
  type lowering is mid-flight. Running the solver there re-enters the diagnostic context and aborts
  the compiler, the
  [re-entrant-emission hazard](../rustc-diagnostic-internals.md#re-entering-the-diagnostic-context-lock-was-already-held).
- **A coherence conflict (`E0119`)** can name `HasField`, but two overlapping impls leave no bound
  unmet, so a walk would invent a missing-impl cause
  ([`deref_has_field_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/deref_has_field_conflict.rs)).
- **An `E0275` overflow** is explained only by a cut (a cycle, or a lookup that grows), which
  [the text path](../driver/diagnostic-reshapes.md#naming-the-traits-behind-a-component-marker) words from the
  overflow walk. A bound the walk stops at is one whose own evaluation overflowed, which no root
  cause states truly.
- **A `?`-operator error** is about `Try` on the call's result, not about the call's bounds.

Two more shapes reach
[the data-call anchor](call-site.md#calls-to-extensible-data-operations) alone: the
probe's "no method named `…`" `E0599`, and an `E0308` on a call's argument. A call to an
extensible-data operation can fail with either before its bounds are checked, as when a builder
finalized too early has no `finalize_build`. An `E0308` is taken only when the walk finds the field
or variant state the operation rejects, since it is otherwise a plain type error.

## Why it runs in the emitter

The resolver runs inside the diagnostic emitter because no later hook sees a failing crate. The
natural home would be an `after_analysis` callback, but the `analysis` query raises a fatal error
once type checking reports any non-lint error, before `after_analysis` runs. A crate with a CGP
failure has an error by definition, the same reason Clippy's late passes run only on code that
type-checks.

The emitter executes while the error exists and before that fatal unwind, with a `TyCtxt` in
thread-local scope. So the resolver re-enters the trait solver from within a diagnostic being
emitted. A fresh `InferCtxt` per query makes this work, and the whole approach assumes it. Every
fixture the resolver reshapes exercises that assumption.

This position is also the source of every panic risk the tool faces.
[rustc diagnostic internals](../rustc-diagnostic-internals.md#panic-hazards-running-compiler-code-inside-the-emitter)
catalogs the constraints: never force a query that emits (so `tcx.typeck` is off limits),
instantiate a binder before relating it, and keep each `InferCtxt`'s variables to itself.

## How the root cause is recovered

The stages run in order: anchor the starting obligation, walk it to the leaves, classify each leaf,
label each hop, and emit. They fill rustc-free types with owned `String`s, so the wording needs no
compiler. The obligation and its causes come from typed lookups. Message text plays a smaller part:
it tells the `E0599` forms and the `?` cascade apart, and the headline decision reads the bound
rustc stated.

Two facts hold across every stage:

- **The walk's obligation is always a real one:** a consumer obligation
  `Ctx: ConsumerTrait<Params…>`, or a provider obligation `Provider: ProviderTrait<Ctx, Params…>`
  for a `#[check_providers]` entry or a provider's own method called directly.
- **CGP's traits are recognized by what `#[cgp_component]` generates, without `IsProviderFor`.** A
  provider trait has the delegation blanket
  `impl<Ctx, P> ProviderTrait<Ctx> for P where P: DelegateComponent<Marker>, …`, which also yields
  the component marker. A consumer trait has the blanket
  `impl<C> Consumer for C where C: Provider<C>` routing to such a provider. `DelegateComponent` and
  the other traits CGP defines are matched by name and defining crate, so a same-named trait
  elsewhere does not count.

A `#[cgp_fn]` or `#[blanket_trait]` **blanket trait** is the third shape, walked as a consumer is. A
blanket impl alone proves nothing, since `ToString` and `Into` carry one, so the trait qualifies only
when its blanket depends on a CGP construct
([`upstream_blanket_trait_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/upstream_blanket_trait_use_site.rs),
[`local_blanket_trait_reached`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/local_blanket_trait_reached.rs)).

**[Anchoring the starting obligation](anchors.md)** recovers what the compiler
failed to prove. The anchors are tried in this order and the first success wins, so the order is
behavior. A blank gate takes any candidate:

| Anchor | The failure it reads | Gate |
| --- | --- | --- |
| Check entry | A `check_components!` entry at the caret | |
| Provider check | A `#[check_providers]` entry at the caret | |
| Impl site | A hand-written `impl Trait for Context`, or a bound of an impl's own `where` clause | |
| Wrapper chain | An `impl … for Foreign` whose `where` clauses reach a consumer | |
| Use site, by component | A consumer call: every component the context in the spans wires | |
| Use site, by consumer | A local non-generic consumer the spans name, reaching a namespace-joined context | |
| [Call site](call-site.md) | The call's HIR: a `Code`-dispatched pipeline, or a `#[cgp_fn]` method | |
| Data call | A call to an extensible-data operation | Also the data-call shapes |
| Provider call | A provider trait's method called through the provider's own path | |
| Bound call | A generic function's own bound the context fails | `E0277` only |
| By blanket trait | A blanket trait required as a bound elsewhere | `E0277` only |
| Forwarding entry | A `Key -> Table` entry whose forwarding bound fails | `E0277` only |

The span-matching anchors come first because each recovers a more exact obligation than re-reading
the call. The by-blanket-trait gate keeps a method call leading with the trait the programmer
invoked, and keeps a declined generic consumer from latching onto a transitive trait.

**[Walking to the root cause](walk.md)** descends the obligation's dependency graph
to every terminal unmet bound. **[Leaves and labels](leaves.md)** decides what each
terminal means and how each hop reads. **[The transformed diagnostic](output.md)**
is the output side: the headline classes, the merged notes, and the plan applied to rustc's
`DiagInner`. A rewritten main message carries its `[CGP-Exxx]` code inline, and everything else
stays in rustc's own form, as the [error-code scheme](../../error-code.md) settles.

## Boundaries

The resolver reports only what it can trust and declines the rest, so a change should not widen it by
guessing. It gives up in these cases, each keeping rustc's headline:

- **A check that carries a generic parameter.** The walk solves under an empty parameter environment,
  where the solver does not prove a wiring lookup that names the check's own `T`, so a walk would
  blame wiring that exists. So any seed holding a type parameter declines, from a check
  ([`generic_check_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_check_context.rs)),
  a generic wrapper impl
  ([`generic_wrapper_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_wrapper_impl.rs)),
  or an overflow
  ([`generic_check_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/generic_check_cycle.rs)).
  Checking or calling one instantiation resolves as usual
  ([`generic_context_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_context_call.rs)).
- **A call whose receiver only typeck could type,** such as a method's result or a field access. The
  call-site anchor reads types syntactically, because the emitter cannot force `tcx.typeck`. A plain
  consumer still resolves, since rustc's note lands on the context's definition and the use-site
  anchor reads it
  ([`field_access_receiver_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/field_access_receiver_call.rs)).
  A generic consumer does not, since its parameter rides in the call
  ([`generic_consumer_field_access_receiver`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_consumer_field_access_receiver.rs)).
  A chain of extensible-data operations is the exception, typed from their signatures.
- **A parameter only an untyped argument carries,** such as a plain variable or an unsuffixed
  literal. The by-component anchor skips a generic component's bare marker, the by-consumer anchor
  needs a consumer whose only generic is `Self`, and the call-site seed's unknown makes every root
  cause depend on it. The emitter strips the method-probe advice so the unmet bound leads
  ([`generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs)).
- **A method's own `where` bound.** The bound-call anchor reads a path call's function, not a
  method's bound, so a failure there keeps rustc's report, whether it is an unmet bound
  ([`method_own_bound_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/method_own_bound_call.rs))
  or an `E0271` on its associated type
  ([`method_own_bound_output_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/method_own_bound_output_mismatch.rs)).
- **A written type beyond the call-site anchor's small hand lowering,** and a generic component's
  trait definition, which no anchor reads.
- **A provider struct's own impl.** The anchors skip its supertrait, the only one being
  `IsProviderFor`, because routing through it would leak `__Context__` into the tree. A failing
  bound of its own `where` clause is still read, walked as the consumer obligation it names, so it
  de-duplicates into that context's own check
  ([`cross_context_node_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/cross_context_node_key.rs)).

Neither the wrapper-chain descent nor a call-site seed can invent a chain from an unrelated bound.
The descent follows real `where` clauses, reports only a CGP consumer on a context, and stops at a
depth bound, and each seed is used only when the obligation actually fails.

The walk also drops what it cannot state truly: a wiring-plumbing dead-end, a leaf that depends on a
call-site unknown, and an associated-type mismatch on anything but a trait's projection, since an
opaque, inherent, or const alias has no `Trait::Assoc` to name. Where a projection does not reduce
to a concrete type, the leaf renders that side as `_`.

The cost grows with the square of the chain depth past about 120 chained hops, a known limit that
[Dependency-graph rendering](../dependency-graph-rendering.md#known-limits) explains.

## Further reading

- [The driver](../driver/program.md): the emitter this resolver runs in.
- [Error processing](../error-processing.md): the rustc-free crate that holds the `Resolved` model and
  the wording.
- [Check traits](../../../cgp/concepts/check-traits.md): why `IsProviderFor` and `CanUseComponent`
  exist.
- [rustc diagnostic internals](../rustc-diagnostic-internals.md): where rustc drops what the resolver
  must recover, and the panic hazards.
- [Architecture](../architecture.md#the-flow-of-a-diagnostic): where this transformation sits.
- [CGP check-trait failure](../../../cgp/errors/checks/check-trait-failure.md): the error class it
  reshapes.

## Tests

The UI suite pins the resolver end to end, and each fixture's `//!` header states what it
demonstrates. The [`cgp/errors/`](../../../cgp/errors/README.md) class documents list every fixture,
and [Testing](../testing.md) describes the suite. These groups pin the resolver:

- [`checks/check-trait-failure/fields/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/fields):
  an absent field, an underived one, one behind `Deref`, several in written order, and a `Symbol!`
  tag on a tuple struct.
- [`checks/check-trait-failure/field-types/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/field-types):
  a field of the wrong type, including a required type that projects through the context's own wiring
  and two same-named structs told apart by `DefId`.
- [`checks/check-trait-failure/types/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/types):
  an abstract-type mismatch, and `plain_assoc_type_mismatch`, which has no wiring entry and so no
  `UseType` help.
- [`checks/check-trait-failure/missing-wiring/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/missing-wiring):
  an unwired component, an aggregate lacking a key, a forwarding entry into a table lacking it, and
  list recursion through `Cons` and `Either`.
- [`checks/check-trait-failure/providers/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/providers):
  a type that is no provider, a provider written for another context, and `#[check_providers]`
  entries.
- [`checks/check-trait-failure/resolution/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/resolution):
  the harder mechanics: a diamond, higher-ranked descent, `projected_impl_argument` (an impl's trait
  ref reduced before it is related), two same-named components, a CGP tree beside an untouched
  `E0308`, and the text fallback's resugaring.
- [`checks/check-trait-failure/generic/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/generic):
  component parameters, a lifetime restored from `Life<'a>`, a single tuple parameter kept whole, and
  the declined generic check.
- [`checks/check-trait-failure/constrained-key/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/constrained-key):
  a delegation whose key's own bound fails, ending on an ordinary-bound leaf.
- [`checks/check-trait-failure/duplication/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/duplication):
  coalesced and repeated causes, and the wrapper-chain shapes `foreign_wrapper_chain` and
  `traced_send_wrapper`.
- [`checks/check-trait-failure/errors/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/errors)
  and
  [`handlers/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/handlers):
  error routes and handler pipelines reached from a check or a call.
- [`checks/check-trait-failure/checks/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/checks),
  [`use-site/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/use-site),
  [`use-type/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/use-type),
  and
  [`verbosity/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/verbosity):
  check-table shapes, the decline boundary, an unsatisfiable `#[use_type]` import, and a deep chain
  with every hop spelled in full.
- [`checks/higher-order-provider-layer/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/higher-order-provider-layer):
  the provider-check anchor, whose tree starts at the failing layer.
- [`hidden/unsatisfied-dependency/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/hidden/unsatisfied-dependency):
  the use-site paths: consumer calls, namespace-joined and `open`-dispatched contexts, `cascade_*`
  later pipeline stages, `unrelated_error_*` errors that keep their own diagnostic beside a failing
  call or wrapper impl, foreign contexts through `//@aux-build`, and direct provider and bound
  calls.
- [`data/extensible-data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/data/extensible-data):
  the data-call anchor and the partial-value leaves, cataloged by the
  [extensible data](../../../cgp/errors/data/extensible-data.md) class.
- [`lowering/wrong-component-half/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/lowering/wrong-component-half):
  the descent into a provider whose header names the consumer trait.
- [`pass-through/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/pass-through):
  lookalikes left as rustc wrote them, among them a local blanket trait with no CGP evidence, and
  calls named like data operations.
- [`enum_hasfields_lock`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/enum_hasfields_lock.rs):
  the resolution-class `E0599` the gate must decline.
- [`cargo-cgp-error-processing/tests/error_processing/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/diagnosis),
  [`graph.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/graph.rs),
  [`tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/tree.rs),
  and
  [`coalesce.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/coalesce.rs):
  the wording and the tree over hand-built `Resolved` values, with no compiler.

## Source

Each stage's modules import only the layers below them, in the order `resolve/mod.rs` states:

- [`resolve/anchors.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/anchors.rs):
  the ordered anchor list, with each anchor's gate and what its resolution means.
- [`resolve/anchor/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/anchor):
  the eight span-matching anchors, and the seed they share.
- [`resolve/call_site/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/call_site):
  the four anchors that re-read a call from HIR.
- [`resolve/walk/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/walk):
  the recursion, its guards, and what it descends into.
- [`resolve/classify/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/classify):
  a terminal bound turned into a `Leaf`, and in `fix/` the finders of what a `help` names.
- [`resolve/data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/data):
  the extensible-data traits, and a partial value read back into its target.
- [`resolve/label/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/label):
  each hop as a rustc-free `DepNode`, and list types resugared.
- [`resolve/query/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/query):
  the compiler readers and solver helpers more than one stage uses. It decides no resolution, so the
  stages and the class detectors in
  [`detect/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect)
  import it and it imports none of them. `query/cgp_item/` holds the structural trait recognition,
  and `impl_match.rs` the one impl match.
- [`resolve/cache.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/cache.rs):
  the walk's memo ([Cached dependency resolution](../cached-dependency-resolution.md)).
- [`resolve/overflow.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/overflow.rs):
  the overflow walk the `E0275` wording reads.
- [`emitter/stage/resolver.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/stage/resolver.rs):
  the candidate gate, and the plan applied to the diagnostic.
- [`cargo-cgp-error-processing/src/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis):
  the rustc-free model, the wording, the plan, and the graph
  ([Dependency-graph rendering](../dependency-graph-rendering.md)).
- [`cargo-cgp-error-processing/src/tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/tree.rs):
  the `cargo tree`-style renderer.
- [`crates/cargo-cgp-driver/src/config/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/config):
  the crate and trait names the recognition anchors to.
