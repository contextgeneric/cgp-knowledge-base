# Usability issues

This document lists the ways `cargo-cgp` presents errors that carry the root cause but bury it: the
problems a reader hits even when the diagnostic contains everything needed to find the cause. What
separates these from a [hidden root cause](hidden-root-cause.md) is that the information is present:
the cause could be recovered from the output by a careful reader or a post-processor, so the work
here is re-presentation, not recovery. Every issue is backed by a fixture under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/) whose header declares `//@quality: usability`, in the directory of its error
class. When a fixture's presentation reaches the bar, its header changes to
`//@quality: acceptable` and its issue is deleted from this document.

## What the tool already presents well

The classes below carry their root cause in a form that clears the usability bar, so their fixtures
have `acceptable` quality and are listed here only so a reader can tell them from the open issues.
Their codes are catalogued in [error-code.md](../error-code.md) and their mechanics in the
[implementation documents](../implementation/README.md); each entry names the behavior and the
fixture that pins it.

- **Check-trait failures**, the dominant class of CGP error. The
  [typed root-cause resolver](../implementation/typed-root-cause-resolution.md) leads with a single
  coded headline that states the cause as one plain sentence
  (`` [CGP-E001] missing field `height` on `Rectangle` ``, the code classing an unimplemented
  consumer trait, or `[CGP-E004]` for a field-type mismatch), repeats it on the `root cause:` line
  above the tree, decodes the field name from its `Symbol!`, and renders the dependency path as a
  compact `cargo tree`, with the `IsProviderFor` / `CanUseComponent` / `__Check…` scaffolding
  suppressed throughout.
- **A missing derive across several fields** is one root cause: several present-but-underived fields
  on one struct merge into a single `[CGP-E111]` lead listing every field, over one merged tree,
  with the derive `help` naming the one fix
  ([`base_area_2`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_2.rs);
  the boundaries, a lone underived field and genuinely absent fields, are pinned by
  [`underived_and_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/underived_and_missing_field.rs)
  and
  [`parallel_branches`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/parallel_branches.rs)).
  The *same* field reached by several coalesced consumers is one cause too: the block's union of its
  members' causes is folded by leaf before the wording runs, so the lead keeps the single-field form
  ([`coalesced_underived_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/coalesced_underived_field.rs)).
  And a use-site failure spanning several wired components that share a cause renders every
  component's route, converging on the shared hop
  ([`use_site_shared_cause`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/use_site_shared_cause.rs)).
- **A pipeline stage routing back to the context for an unwired `Code`** ends at the absent entry. A
  type-level DSL interprets each stage by routing through the context's own handler, and a context
  that joins a namespace carries a blanket forwarding that matches *every* key, but an unmet
  delegation on the context is terminal whatever nominally matches it. So the block leads with
  `[CGP-E113] … does not contain any delegate entry for @….Missing` rather than one `[CGP-E002]` per
  combinator layer naming `PipeHandlers`/`ComposeHandlers`
  ([`pipeline_unhandled_code`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/pipeline_unhandled_code.rs)).
- **A use-site failure the resolver declines** drops rustc's "this is an associated function, not a
  method" framing and its wrong "use associated function syntax instead" suggestion, both artifacts
  of CGP's `self`-less provider methods, leaving the unmet wiring bound as the first note
  ([`generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs);
  recovering the dispatch parameter itself is a documented
  [resolver boundary](../implementation/typed-root-cause-resolution.md#boundaries-and-open-ends)).
- **Wiring coherence conflicts** carry codes. The duplicate delegate-key `E0119` family is
  `[CGP-E010]`–`[CGP-E014]`, including a duplicate `cgp_namespace!` `@`-path as a `[CGP-E014]`
  naming both redirect targets
  ([`namespace_duplicate_path_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/namespace_duplicate_path_key.rs));
  a duplicate provider *name* is the lone `E0428`, since the compiler stops once it finds a type
  defined twice
  ([`duplicate_provider_name`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/duplicate_provider_name.rs));
  and a wiring lookup's `E0275` becomes a `[CGP-E020]` headline when the lookup leads back to
  itself, or a `[CGP-E021]` one when it grows with each step, with a `help` naming the provider
  that closes or grows the loop
  ([`use_context_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle.rs),
  [`divergent_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring.rs)).
  A collision *inside a namespace* reads the same way whatever its key: a child namespace redefining
  a key it inherits is a `[CGP-E011]` naming the parent
  ([`inherited_override_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-override-conflict/inherited_override_conflict.rs)),
  two `#[default_impl]`s on one per-type key a `[CGP-E010]` naming the type and its table
  ([`duplicate_default_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/duplicate_default_impl.rs)),
  and a prefixed component bound by its bare marker (a mis-written key rather than an override) a
  `[CGP-E013]` whose `help` names the path to write instead, whether the entry it collides with is
  an inherited redirect
  ([`namespace_inherited_unprefixed_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-override-conflict/namespace_inherited_unprefixed_key.rs))
  or the component's own `#[prefix]` route
  ([`default_impl_unprefixed_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/default_impl_unprefixed_key.rs)).
- **Structural mistakes** in a check table or a wiring entry carry codes of their own: a check entry
  listed twice is `[CGP-E015]`, two check tables sharing a check-trait name `[CGP-E016]`, a `for`
  loop whose key skips its variable `[CGP-E017]` (one block for rustc's three `E0207`s), a
  `#[default_impl]` on a generic provider impl `[CGP-E018]`, and a wiring or namespace entry whose
  key skips its generic parameters `[CGP-E019]` (one block for rustc's `E0207` per parameter and
  impl, whose two suggestions do not compile), each with its fix in a `help`
  ([`check_duplicate_entry`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/check_duplicate_entry.rs),
  [`check_twice_same_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/check_twice_same_context.rs),
  [`for_loop_key_without_var`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/for_loop_key_without_var.rs),
  [`default_impl_generic_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_generic_provider.rs),
  [`unconstrained_generic`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/unconstrained_generic.rs)).
- **A cross-context dependency** (one context's wiring depending on a *concrete* other context, so
  one obligation appears in two contexts' trees) resolves on both sides. A provider's own
  `where Inner: CanCompute` clause is recovered as that consumer obligation, de-duplicating into
  `Inner`'s own block rather than leaking `__Context__`/`IsProviderFor` or declining to rustc's raw
  bound, and the same node inside the *outer* context's tree is re-rooted at `Inner` so it decodes
  to the missing field
  ([`cross_context_node_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/cross_context_node_key.rs)).
- **An orphan-rule namespace registration** (registering wiring into a namespace the crate does not
  own, keyed on a component it does not own either) becomes a `[CGP-E022]` header naming the foreign
  namespace and key, with the ownership-based fix in a `help`, in place of rustc's `E0210`/`E0117`,
  which names the machinery parameter `__Components__`/`__Table__`. Its three triggers are under
  [`wiring/orphan-rule/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring/orphan-rule):
  a `#[default_impl]` on a bare foreign component marker
  ([`default_impl_foreign_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/orphan-rule/default_impl_foreign_component.rs)),
  on a foreign prefix path
  ([`default_impl_foreign_prefix_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/orphan-rule/default_impl_foreign_prefix_path.rs)),
  and a `cgp_namespace!` re-open whose `__Table__` trigger selects the inherit-a-new-namespace fix
  ([`reopen_foreign_namespace`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/orphan-rule/reopen_foreign_namespace.rs)).
- **One mistake reported as many errors** collapses on both axes. CGP wiring is lazy, so one missing
  dependency surfaces at the `check_components!` entry, at every hand-written `impl` that references
  the broken consumer, and at each call. The *same* consumer re-reported at many sites de-duplicates
  to one block, keyed on a span-independent cause signature
  ([`cross_site_dedup`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/cross_site_dedup.rs),
  [`manual_supertrait_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/manual_supertrait_impl.rs)).
  *Different* failures that share one root cause (consumers, a wrapper trait beside the consumer it
  reduces to, or failures on two contexts that bottom out on one context's field) coalesce into a
  single block whose headline states the shared cause, with its caret on the first failing entry,
  each other entry labelled "also required here" so an editor shows one diagnostic, and the cause
  shown once. The emitter holds each compilation's diagnostics in arrival order and flushes them at
  `Drop`, the only point after every diagnostic has arrived, grouping the consumer failures that
  *share* a root cause, so
  [`density_3`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/density_3.rs)
  (two components, one missing `height`),
  [`dependency_cascade`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/dependency_cascade.rs)
  (three chained providers), and `missing_normal_bound` (two consumers sharing an `App: Clone`
  bound) each collapse to one block, and cargo's re-count keeps the "N errors" summary honest.
  Grouping on a shared cause rather than on one whole-failure key also covers the *partial-overlap*
  form of this class, where one omission is reached at several instantiations and so surfaces as
  several root causes: each `check_components!` entry stops at the first unmet leaf on its own
  branch while a use-site call walks every wired component, so no two cause sets are equal, and the
  union block still keeps its dependency chain
  ([`overlapping_cause_sets`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/overlapping_cause_sets.rs)).
- **A trait used but not declared** (a `#[cgp_fn]`/`#[cgp_impl]` body that calls a CGP trait's
  method, a consumer or `#[cgp_fn]`/`#[blanket_trait]` trait, on `self`, or its associated function
  on `Self`, without declaring it via `#[uses(…)]`) becomes a `[CGP-E030]` header naming the trait,
  with the `#[uses(…)]` fix in a `help`, in place of rustc's vague `E0599`, which names
  `__Context__` and points at a transitive `HasField` bound or splices a bound into the macro
  attribute. A generic trait is written with the arguments the call uses
  ([`undeclared_uses_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_uses_trait.rs),
  [`undeclared_uses_trait_in_cgp_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_uses_trait_in_cgp_impl.rs)
  with its async form for a provider body, where the generated impl's `Self` is the provider struct
  and the receiver's declared type identifies the shape instead,
  [`undeclared_generic_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_generic_trait.rs),
  and
  [`raise_error_in_cgp_fn`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/raise_error_in_cgp_fn.rs)).
  Any `[T]: Sized` cascade the unresolved return type trails is left as rustc wrote it: those errors
  can land off the failing expression, where suppressing them reliably would risk hiding an
  unrelated error.
- **A `#[cgp_impl]` header naming the wrong trait** (the component's *consumer* trait where its
  *provider* trait belongs, `#[cgp_impl(new P)] impl CanCalculateArea` instead of
  `impl AreaCalculator`, or a trait that is not a CGP component at all) becomes a single
  `[CGP-E032]`/`[CGP-E033]` error on the misused trait name, naming the fix, with the whole
  macro-lowering cascade (`E0425` on a `…Component` marker the user never wrote, `E0107`, `E0186`,
  `E0207`, and a downstream check failure) suppressed. A requirement of the impl that fails on its
  own, such as a missing field, is reported beside it as its own block. The recognition uses the
  consumer/provider fingerprints, so it generalizes over a component's generic parameters and tells
  a wrong-half mistake (`[CGP-E032]`, which names the provider trait to use) apart from a
  non-component trait (`[CGP-E033]`, which has no provider to suggest)
  ([`consumer_trait_in_provider_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl.rs),
  [`consumer_trait_in_provider_impl_generic`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl_generic.rs),
  and
  [`cgp_impl_on_non_cgp_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/cgp_impl_on_non_cgp_trait.rs)).
- **A higher-order provider's `#[use_provider]` mistake** is reshaped the same way. Calling
  `InnerCalculator::area(self)` without `#[use_provider(InnerCalculator: AreaCalculator)]` becomes a
  `[CGP-E031]` error naming the inner provider and the fix, in place of rustc's `E0599`, which leaks
  the generated `__Context__` and suggests the wrong consumer-trait bound
  ([`higher_order_missing_use_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/higher_order_missing_use_provider.rs)).
  Naming the *consumer* trait in the `#[use_provider]` bound becomes a `[CGP-E034]` error pointing
  at the provider trait to use, with the `E0308` body cascade suppressed
  ([`higher_order_use_provider_consumer_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/higher_order_use_provider_consumer_trait.rs)).
  Naming a *provider* trait in `#[uses]` becomes a `[CGP-E037]` error naming the consumer trait to
  declare, in place of rustc's suggestion to add the generated `<__Context__>`
  ([`uses_provider_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/uses_provider_trait.rs)).
- **An undeclared import or requirement** is named with its declaration. `Self::Error` without
  `#[use_type(HasErrorType.Error)]` becomes a `[CGP-E035]` error naming the abstract type and the
  import, in place of rustc's `E0220` on `__Context__`
  ([`self_error_without_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_without_bound.rs)).
  A provider that omits a requirement its component places on every context (an `#[extend]` or a
  `#[use_type]`) becomes one `[CGP-E036]` error naming the provider trait, the provider, and the
  `#[uses]` or `#[use_type]` to add, in place of rustc's `E0277` on `__Context__` repeated at the
  attribute and each signature
  ([`supertrait_missing_uses`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/supertrait_missing_uses.rs)).
  A bare `Error` in such a provider is folded into the `[CGP-E035]`
  ([`error_alias_without_use_type`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_without_use_type.rs)).
- **An abstract type the context binds one way while a provider pins it another** is a coded
  mismatch of its own. A context chooses an abstract type's concrete form by wiring its component to
  `UseType<T>`; a provider can pin the same type with the `#[use_type(Trait.{Assoc = Concrete})]`
  equality form, and when the two disagree the trait bound still holds and only the projection
  fails. The resolver's projection recovery covers any associated type, not only `HasField`'s, so
  the failure becomes a `[CGP-E005]` header naming both types over a root-cause tree, with a `help`
  naming the wiring entry to change
  ([`abstract_type_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/types/abstract_type_mismatch.rs)).
- **A dispatch payload that lacks the dispatched trait** is named. When one payload of a
  [`#[cgp_auto_dispatch]`](../../cgp/reference/macros/cgp_auto_dispatch.md) enum lacks the trait,
  the call on the enum resolves through the generated matcher to the per-variant computer's
  requirement, ``[CGP-E003] the trait bound `Square: HasArea` is not satisfied``, in place of
  rustc's `E0599`, which names the matcher's `Computer` bound and the payload that does implement
  the trait
  ([`auto_dispatch_missing_variant_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/auto_dispatch_missing_variant_impl.rs)).
- **A blanket trait published by a library** is reshaped like a local one. A
  `#[cgp_fn]`/`#[blanket_trait]` trait is recognized by its blanket impl over a bare context, a
  signal too broad on its own (`ToString` and `Into` share it), so a foreign trait qualifies only on
  evidence that its blanket depends on a CGP construct, and the `[CGP-E003]` reshaping crosses the
  crate boundary
  ([`upstream_blanket_trait_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/upstream_blanket_trait_use_site.rs)).
- **A CGP construct rustc splits across styled fragments** is resugared. rustc builds its "similar
  impl" hint from fragments split at every difference between the two traits, shredding a
  `Symbol<3, Chars<'B', …>>` so no fragment matches; the tool reads the fragments as the one line
  they render as, and flattens them only when that recovers something, so the hint reads
  `Symbol!("Bar")` like the header beside it
  ([`upcast_missing_variant`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/upcast_missing_variant.rs)
  shows it on a declined diagnostic).
- **A required type that projects through the context's own wiring** is shown in both forms. When a
  provider reads a field whose type is expressed through an
  [abstract type](../../cgp/concepts/abstract-types.md) it imports
  (`#[implicit] database: &Pool<Db>` under `#[use_type(HasDbType.Db)]`), the requirement reads
  `` of type `Pool<<App as HasDbType>::Db>` (`Pool<Postgres>`) ``: the un-normalized form first
  because it names the wiring to change, the reduced form after because it is what the field is
  compared against. A requirement that is already concrete normalizes to itself and gets no
  parenthetical. The `[CGP-E004]` headline and the `[CGP-E112]` leaf render it through one helper,
  so they cannot state a requirement two ways, and the abstract-type pair `[CGP-E005]`/`[CGP-E116]`
  does the same. The one deliberate divergence is the abstract-type `help`, which takes the reduced
  form alone because it prescribes an edit the reader types rather than describing the requirement
  ([`abstract_field_type_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/field-types/abstract_field_type_mismatch.rs)).
- **A slipped name** is named beside the cause it causes. A missing field whose struct carries a
  similar one, or a missing key whose context wires a similar one (a recased or misspelled symbol,
  a doubled or dropped prefix segment), gets a `help` naming it, ahead of the fix the cause itself
  calls for
  ([`getter_use_field_typo`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/getter_use_field_typo.rs),
  [`prefix_case_slip`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/prefix_case_slip.rs),
  [`prefix_doubled_marker_generic`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/prefix_doubled_marker_generic.rs),
  and
  [`namespace_not_inheriting_base`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/namespace_not_inheriting_base.rs)).
- **A missing entry in an aggregate provider's own table** names that provider, whether the
  aggregate `open`s the component or joins a namespace itself. Each `[CGP-E103]` redirect hop reads
  the table off its own `RedirectLookup<Table, Path>`, so a context's redirect says `` in `App` ``
  and the aggregate's says `` in `ByteSink` ``, and a path key missing from the aggregate is the
  `[CGP-E114]` provider-table leaf,
  `` missing entry for `@ComputerComponent.Sink.Digest` in provider `ByteSink` ``,
  rather than a `[CGP-E113]` leaf calling the aggregate a context
  ([`open_aggregate_missing_entry`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/open_aggregate_missing_entry.rs),
  [`namespace_aggregate_missing_entry`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/namespace_aggregate_missing_entry.rs)).

**A dispatch chain shows every CGP construct as written**, at the cost of length. A chain restates a
program-sized `Code` type at every hop, and the tool does not shorten a hop that repeats its
parent's trait: an elision would hide the very type a reader follows the chain to trace, and would
leave a genuine repeat indistinguishable from a hop whose parameters differ. The
[cross-block elision](../implementation/dependency-graph-rendering.md#eliding-across-blocks), which
drops whole subtrees an earlier block already drew, is the mechanism for brevity that does not
sacrifice precision.

What remains below are the classes the tool does not yet reshape.

## Two unconstrained generics still pass through

Two shapes of the [unconstrained generic](../../cgp/errors/wiring/unconstrained-generic.md) class
reach the reader as rustc wrote them, with the cause at the caret but a fix that does not apply.

A `#[default_impl]` on the impl of a provider struct that is itself generic over the impl's
parameter (`#[cgp_impl(ShowWith<T>)]` over `impl<T: Display> ShowImpl<T>`) copies `T` onto the
registration, whose key and table do not use it, so the compiler rejects it with `E0207`
([`default_impl_generic_provider_struct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_generic_provider_struct.rs)).
The `[CGP-E018]` reshaping covers a provider struct that does not use the parameter, and the
`[CGP-E019]` reshaping covers entries a table names, so this one passes through, naming neither the
`#[default_impl]` nor its fix. The fix differs from `[CGP-E018]`'s, since the provider struct needs
the parameter: register a provider instantiated at one type, or wire the generic provider in a
namespace body or on the context.

A [`#[cgp_computer]`](../../cgp/reference/macros/cgp_computer.md) function whose type parameter
appears only in its return type (`fn parse<T: FromStr>(value: String) -> Option<T>`) leaves `T`
unbound on the generated `Computer` impl, whose trait arguments carry only the input types
([`computer_output_only_type_parameter`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/computer_output_only_type_parameter.rs)).
Its two suggestions splice a second generic list after `parse` and remove `T`, which the return type
still uses, so neither compiles. The macro sees the whole signature, so it could reject the function
with the fix, taking `T` from an argument or writing a concrete type, before the compiler runs.

## Macro lowering errors point at the attribute, not the cause

When a macro lowers accepted input into ill-formed Rust, the error lands on the macro attribute and
never states the real cause.
[`option_unsized_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/ill-formed-generated-type/option_unsized_path.rs)
produces an unsized-type failure (an `Option<Path>` generated from an auto-getter returning
`Option<&Path>`) as two cascading errors both anchored on the `#[cgp_auto_getter]` attribute, its
headline naming the `[u8]` inside `Path` and nothing naming the `Option<&T>` shorthand that needs a
sized `T`. The cause is hinted by the notes but never named. Its counterpart
[`use_type_unknown_assoc`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/unresolved-imported-type/use_type_unknown_assoc.rs)
shows a different gap: rustc names the misspelled associated type and the similar one, but its
suggestion edits the function's signature, while the misspelling is in
`#[use_type(HasScalarType.Scalr)]`, so applying it leaves the program failing on an undeclared
`Scalar`. Recognizing the lowering class and naming the offending construct is the work here.

The cheaper way to close a case of this shape is often to fix it in `cgp`. A cyclic `#[use_type]`
routing (`#[use_type(HasA.A in B, HasB.B in A)]`) is decidable from the import list alone, so
`#[use_type]`
[rejects it at macro time](../../cgp/implementation/asts/attributes/use_type.md#ground_specs) with a
message naming the cycle and a caret on the alias that closes it, and nothing reaches the compiler
for the tool to reshape. The getter macros reject an optional reference to a slice or a trait object
the same way, since its shape shows the referent is unsized; only a type named by a path, whose size
the macro cannot see, reaches the compiler. When a lowering error's cause is available to the macro,
fixing it in `cgp` beats teaching the tool to reconstruct it.

Two extensible-data derive defects land here for the same reason. An enum variant named after an
associated type the derives generate (`Value`, `Remainder`, `Fields`, …) makes the generated
`Self::…` path ambiguous; under the extractor both notes land on the derive attribute, so nothing
names the variant
([`reserved_variant_name_extract_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/out-of-scope-generated-name/reserved_variant_name_extract_field.rs),
[`reserved_variant_name_cgp_data`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/out-of-scope-generated-name/reserved_variant_name_cgp_data.rs); the readable
`FromVariant` case is
[`reserved_variant_name_from_variant`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/out-of-scope-generated-name/reserved_variant_name_from_variant.rs)). And a
variant helper attribute of another derive, copied onto the extractor's companion enums, fails with
a help that suggests the derive the enum already has
([`variant_helper_attribute`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/macro-defects/variant_helper_attribute.rs)). Both are fixed in `cgp`:
qualified projections, and filtering the copied attributes.

A `Path!` defect reaches the reader the same way. `Path!` reads a segment such as the `f` of
`@app.f` as a type, so three `E0425`s name `f` as an unresolved type, and rustc's `E0275` overflow
follows, with nothing naming the segment rule as the cause
([`path_segment_read_as_type`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/macro-defects/path_segment_read_as_type.rs)).
The fix belongs in `cgp`'s `Path!` primitive rule.

## Extensible-data failures are not reshaped at all

The casts, builders, and extractors of the
[extensible-data](../../cgp/concepts/extensible-records.md) family have no reshaping and no upstream
error class. A `BuildWithHandlers` list without a step for one field
([`builder_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/builder_missing_field.rs))
reports `__PartialConfig<IsPresent, IsNothing>: FinalizeBuild`, exposing the macro-generated
partial-record state and never naming the unbuilt `port` field. The partial type encodes the mistake
exactly, as type-level list algebra the compiler holds, so the class suits the typed resolver: a
leaf naming the unbuilt field (or the absent variant) is the work here. Where rustc's own headline
already names the tag, the output reads well enough as it stands: an upcast into a target missing a
variant reads `Big: FromVariant<Symbol!("Bar")>`
([`upcast_missing_variant`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/upcast_missing_variant.rs)),
though its notes expose `__PartialSmall<IsVoid, IsPresent>` and its caret lands on the wrong
variant. Four failures of the family never name their cause at all, and are listed under
[hidden root cause](hidden-root-cause.md#extensible-data-failures-that-never-name-their-cause).

Dispatch over an extensible enum names its traits but not the derive. A
[`#[cgp_auto_dispatch]`](../../cgp/reference/macros/cgp_auto_dispatch.md) call on an enum without
`#[derive(CgpData)]`
([`auto_dispatch_missing_derive`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/auto_dispatch_missing_derive.rs))
resolves to the enum's two unmet requirements, `Shape: HasFields` and `Shape: HasExtractor`, the
traits the derive supplies, under the trait's class sentence. Nothing names the derive, and one step
of the tree names the matcher's private `dispatch::providers::matchers::to_field_handlers` path. The
leaf to recover is the missing derive, which those two traits encode.

The rest of the family fails as the builder above does: rustc reports the bound on a generated type,
and the tool passes it through without naming the field or variant at fault. The record builder
reports a field built twice or taken while absent as an `E0271` on its `UpdateField` marker
([`build_field_twice`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/build_field_twice.rs),
[`take_field_absent`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/take_field_absent.rs)),
and a premature finalize as an `E0599` whose only clue is the partial type's marker list
([`finalize_build_premature`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/finalize_build_premature.rs)).
Merging with `build_from` reports a stray or doubled field on the private `FieldsBuilder` recursion
([`build_from_field_not_in_target`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/build_from_field_not_in_target.rs),
[`build_from_overlapping_sources`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/build_from_overlapping_sources.rs)),
and the `BuildAndMergeOutputs` dispatcher reports two different field mistakes with identical output
([`build_and_merge_extra_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/build_and_merge_extra_field.rs),
[`build_and_merge_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/extensible-data/build_and_merge_missing_field.rs)),
and a call to such a builder whose target lacks a field ends at
`__PartialApp<IsPresent>: CanBuildFrom<Http>` without naming the field
([`question_mark_after_failed_handle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/question_mark_after_failed_handle.rs)).
The defaulted and optional builders, extraction, construction by tag, and the casts each have
fixtures under
[`uncataloged/extensible-data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/uncataloged/extensible-data);
the work is the same leaf: name the field or variant the generated types encode.

## Construct failures that carry no fix

Many construct mistakes reach the reader as rustc wrote them, or reshaped without the hint that
names the fix. The cause is in the output, but the reader must know the construct to act on it.
The fixtures group by construct:

- **Wiring keys and values:** a trait written as a key, an undeclared provider or value, an
  unimported or guessed key, each an `E0425` or `E0782` with a wrong suggestion.
- **Wiring checks, conflicts, and cycles:** a bundle checked as a context, a cycle reached by a
  call, and a generic key in `delegate_and_check_components!` checked at unit parameters without
  `#[check_params(...)]` (`check_trait_named_as_wrapper`).
- **Namespaces:** a self-inheriting namespace.
- **Lowering:** `Self::CONST` rewritten to the context (`cgp_impl_self_const`); a bare `Error`
  without `#[use_type]` that no requirement of the component explains, whose `E0425` suggests
  importing `std::error::Error` (`error_alias_in_cgp_fn`, `error_alias_in_provider_body`);
  `Self::Error` where two abstract-type traits declare an `Error` (`self_error_two_traits`); and
  `#[uses]` on a component, where `#[extend]` belongs, with rustc's `#[used]` suggestion
  (`uses_on_component`).
- **Providers, fields, and types:** getters wired to the wrong provider, a generic check without its
  parameter, `UseDelegate` without `#[derive_delegate]`, a provider impl without `#[cgp_provider]`,
  a tuple-struct context, a field read as two types, and a borrowed error detail.
- **Handlers:** promotions of hand-written providers, a matcher wired as a handler or applied to a
  struct, a monadic pipeline over plain values, and matchers or builders missing an arm or a field.
- **Use sites:** calls the resolver declines, leaking `IsProviderFor` or rustc's method-probe
  advice, including a provider's own method called directly.

## What good presentation looks like

Taken together, these issues define the tool's presentation target for the classes it does not yet
reshape: give the extensible-data family a root cause naming the absent variant or field; and
recover the untransformed lowering class into a coded, root-cause-first diagnostic, or at least name
the offending construct instead of the macro attribute. The bar is the one the check-trait-failure
family already meets: lead with the cause as one plain sentence, name the decoded construct, give a
short dependency path, and never let a misleading `rustc` heuristic outrank the real cause. The
[CGP-side tooling notes](../../cgp/errors/checks/check-trait-failure.md#how-cargo-cgp-presents-it)
describe the same extraction from the catalog side and are the reference to build against.
