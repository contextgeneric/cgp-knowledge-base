# Typed resolution: leaves and labels

This document covers what ends a branch of the [walk](walk.md): which terminal
bound counts as which cause, when it is dropped, and how a cause reads in the tree
[the emitter emits](output.md). Two rules run throughout. A program's names are
never trusted: CGP's traits are recognized by their shape, or by `DefId` when anchored to the crate
that defines them, so a lookalike is never misread. And a `help` naming a specific adapter or
component is confirmed against the program, never guessed, so an obligation holding an unknown gets
none.

## The leaf shapes

`classify_leaf` turns a terminal obligation into the rustc-free `Leaf` the emitter words, or drops
it. Most shapes are the plain cause they look like: an unmet `HasField` is the field leaf, and an
ordinary bound on a foreign type is itself the cause. An unmet `DelegateComponent` needs real
judgment, since it depends on who owns the lookup:

| Owner | Leaf |
| --- | --- |
| The context | Missing wiring (`[CGP-E113]`), by marker or whole path |
| A table a provider holds as a parameter, or an aggregate provider | Missing dispatch entry (`[CGP-E114]`) |
| A type with no impl of the provider trait | Not a provider (`[CGP-E115]`) |
| A provider with its own impl, one argument explaining the mismatch | Provider for other arguments (`[CGP-E127]`) |
| A provider with its own impl, otherwise | Dropped as a routing dead-end |

The choice among these rows runs without the compiler. The driver answers the yes-or-no facts the
table turns on, such as whether the owner is the context or the key is a path, through the
`DelegateLeafFacts` trait, and `delegate_leaf_shape` in `cargo-cgp-error-processing` picks the
shape, which the driver then names from the compiler's types. Unit tests check the precedence over
every combination of the facts. The facts are methods, not fields, because the finder of the other
arguments runs the trait solver, and the decision asks for it only on a blanket dead-end.

The corner cases behind that table are the ones a change is likely to break:

- **The context's lookup is terminal even when an impl unifies.** A wired key would hold and never
  become a node, and the blanket a namespace join writes unifies with every key. The exception is a
  forwarding entry (`Key -> Bundle`), which the context does carry, so the walk descends into that
  table's lookup
  ([`direct_delegation_missing_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/direct_delegation_missing_key.rs)).
- **A table is recognized in two ways.** The structural test, that the owner is a proper part of the
  parent's `Self`, is the only one that reaches an *empty* table
  ([`empty_dispatch_table`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/empty_dispatch_table.rs)).
  The other, that the owner wires some key and has no impl of the trait, covers an aggregate
  provider. Having wired keys is not enough on its own, as a `#[cgp_computer]` provider wires its
  promotions
  ([`cgp_computer_no_error_type_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/cgp_computer_no_error_type_call.rs)).
- **A redirect path off the context is never "not a provider".** The lookup ran in a provider's own
  `open` table, so it is a missing dispatch entry. On a provider with its own impl it reads so only
  when one argument explains the mismatch, and is dropped otherwise.
- **A path recovered from a call with an inferred input ends in a placeholder.** On the context, the
  leaf drops that tail and names the path the programmer can wire. That claims no entry exists for
  *any* value of the unknown, so it is kept only when the solver finds the lookup can hold for none
  ([`placeholder_error_route_leaf`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/placeholder_error_route_leaf.rs)).
- **A dead-end stays dropped because its real cause runs down another branch,** so reporting it
  would blame the wrong type
  ([`cascade_after_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_after_use_site.rs)).

A namespace-lookup bound follows the same split by its table. It is recognized by a lone `Delegate`
associated type plus CGP evidence (CGP's own trait, an impl keyed by a marker or path, or a parent
showing the same), so a user's namespace is caught and a lookalike is not.

An extensible-data bound is read off the partial value's presence markers, and names the field or
variant at fault: `[CGP-E118]` to `[CGP-E122]`, `[CGP-E124]`, and `[CGP-E125]`, with `[CGP-E123]`
for a missing derive and `[CGP-E126]` for a builder or extractor given where its struct or enum
belongs. The fixtures are in
[`data/extensible-data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/data/extensible-data).

## The wiring-without-`IsProviderFor` leaf

The one scaffolding bound that can itself be the cause is the context's own `IsProviderFor`. The
delegation blanket a consumer call routes through requires it, `delegate_components!` writes it, and
a hand-written `DelegateComponent` impl does not. So such a context passes a check of the component,
yet fails at a call. When only scaffolding fails, and the context has no such impl for the
component, the leaf is `[CGP-E128]`
([`hand_delegate_without_is_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/hand_delegate_without_is_provider.rs)).
A context that has the impl is left alone, since the delegate is then at fault.

## Decoding, classifying, and rendering a leaf

**A field name is decoded from the type,** so the replacement never needs the `--verbose` un-eliding
the [text path depends on](../driver/program.md#un-eliding-the-diagnostic).

**A "missing" `HasField` does not always mean an absent field.** The resolver inspects the struct
and its `Deref` chain to separate an absent field, a field present without the derive, a field on a
`Deref` target that has not derived it, and a field of the wrong type
([the projection rule](walk.md#an-impl-whose-trait-clauses-all-hold),
`[CGP-E004]`). Only named fields count: a tuple struct keys fields by `Index<N>`, so `Symbol!("0")`
on one is a missing field
([`symbol_tag_on_tuple_struct_check`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/symbol_tag_on_tuple_struct_check.rs)).

**A fix is recorded only when it would work.** Adding a field is offered only for a struct with
named fields that already derives `HasField`, and not for a field a builder names, since a merge can
still leave another field unset
([`build_and_merge_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_and_merge_missing_field.rs)).

**A partial value's state comes from its definition.** A data derive's generated type stores each
member as `<M as MapType>::Map<…>`, which pairs every marker with its member, so the leaf can name
the target struct or enum rather than the generated type.

**Any other associated type is read by normalizing the projection,** so one query covers a
`UseType<T>` wiring and a hand-written impl alike. The `abstract type` wording needs all three
things [`#[cgp_type]`](../../../cgp/reference/macros/cgp_type.md) generates, because it offers
`UseType<T>` as the fix.

**Labels are read off the obligation,** with no marker or name map. These points need care:

- **Plumbing is dropped:** routing for the context itself, table and namespace lookups, a data
  trait's list recursion, and residual scaffolding.
- **The context is found by type position,** here and in every reader of a provider trait's
  arguments, the fix finders and the detectors included. A component's lifetime parameters sort
  ahead of it, and indexing by raw position lands on a region, which raises a compiler bug inside
  the emitter: the panic is contained, so rustc's error stays, but the reshaping is lost
  ([the lock hazards](../rustc-diagnostic-internals.md#re-entering-the-diagnostic-context-lock-was-already-held)).
- **A redirect hop names its own table,** not the walk's context, so a hop inside an aggregate
  provider names the aggregate.
- **"Context" is used only for a type with wiring of its own.**
- **Every hop spells its types in full,** deliberately, since a pipeline's program-sized `Code` is
  the type a reader is tracing
  ([`deep_dispatch_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/verbosity/deep_dispatch_chain.rs)).
- **A seed that is itself the cause heads its chain with its own step,** so the chain names the
  operation
  ([`finalize_build_premature`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_build_premature.rs)).

Each hop is a [`DepNode`](../error-processing.md) with a code from `CGP-E101` to `CGP-E104`, and a leaf
takes one from `CGP-E110` onward. The walk emits one flat path per way a cause is reached, and the
[dependency graph](../dependency-graph-rendering.md) merges them. List types are resugared as
[Resugaring](../resugaring.md) describes.

## Tests

- [The parent document's catalog](overview.md#tests): the fixture groups that pin
  the leaves.
- [`delegate_leaf_shape.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/delegate_leaf_shape.rs):
  the `DelegateComponent` leaf's shape over every combination of its facts, and the solver-backed
  fact read only on a blanket dead-end.

## Source

- [`resolve/classify/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/classify):
  the leaf classifiers, and in `fix/` the finders of what a `help` names; `leaf.rs` holds the
  compiler reads behind the `DelegateComponent` facts.
- [`diagnosis/leaf/delegate_leaf_shape.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/leaf/delegate_leaf_shape.rs)
  in `cargo-cgp-error-processing`: the facts trait and the shape decision.
- [`resolve/data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/data):
  the extensible-data traits and `read_partial`.
- [`resolve/label/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/label):
  each hop, and the list resugaring.
