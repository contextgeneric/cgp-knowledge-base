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
  `#[default_impl]` on a generic provider impl `[CGP-E018]`, a wiring or namespace entry whose key
  skips its generic parameters `[CGP-E019]` (one block for rustc's `E0207` per parameter and impl,
  whose two suggestions do not compile), a check entry that names no parameters for a component that
  takes some `[CGP-E060]` (in place of an `E0277` that reads like a broken provider), and two
  `#[cgp_auto_dispatch]` traits in one module sharing a method name `[CGP-E061]` (one block for the
  two `E0428`s on the items the macro generates), each with its fix in a `help`
  ([`check_duplicate_entry`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/check_duplicate_entry.rs),
  [`check_twice_same_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/check_twice_same_context.rs),
  [`for_loop_key_without_var`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/for_loop_key_without_var.rs),
  [`default_impl_generic_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_generic_provider.rs),
  [`unconstrained_generic`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/unconstrained_generic.rs),
  [`generic_component_unit_params`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/generic_component_unit_params.rs),
  [`auto_dispatch_shared_method_name`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/auto_dispatch_shared_method_name.rs)).
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
  `[CGP-E031]` error naming the inner provider and the fix (with a generic component's parameters
  written from the call), in place of rustc's `E0599`, which leaks the generated `__Context__` and
  suggests the wrong consumer-trait bound
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
- **A wiring key or value that does not resolve** is named with its fix, in place of rustc's `dyn`,
  type-parameter, and similar-name suggestions: a consumer trait as a key names its component
  (`[CGP-E040]`), a component not in scope its import (`[CGP-E041]`), a key guessed from a trait's
  name the real component (`[CGP-E042]`), an undeclared provider its component (`[CGP-E043]`), an undeclared type in an `@`-path its
  coded header (`[CGP-E044]`), and a
  `#[cgp_impl]` without `new` the `new` that declares the provider, with the wiring and call errors
  it causes dropped (`[CGP-E038]`)
  ([`wiring/unresolved-wiring-name/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring/unresolved-wiring-name)).
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
  `Symbol!("Foo")` beside a header naming `Symbol!("Bar")`
  ([`from_variant_bound_missing_variant`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/from_variant_bound_missing_variant.rs)
  shows it on a declined diagnostic).
- **An extensible-data failure** names the field or variant at fault, behind a check, a cast, or a
  call on a builder or an extractor that other data operations produced. The walk descends CGP's
  data traits to the bound on the generated partial type and reads its presence markers, so a
  builder list without a step for one field reads
  `` [CGP-E001] field `port` of `Config` is not set ``
  ([`builder_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/builder_missing_field.rs)),
  an upcast into an enum without one of the source's variants reads
  `` [CGP-E050] missing variant `Bar` on `Big` ``
  ([`upcast_missing_variant`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/upcast_missing_variant.rs)),
  and a type without the data derive an operation needs gets a `help` naming it
  ([`auto_dispatch_missing_derive`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/auto_dispatch_missing_derive.rs)).
  The data-call anchor types a builder chain, a remainder a pattern binds, and a type-relative call
  through the operations' signatures, so a `build_field` setting a field twice reads
  `` [CGP-E050] field `first_name` of `Person` is already set ``
  ([`build_field_twice`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_field_twice.rs)),
  and the shapes rustc reports before the bounds are checked are resolved too: a premature
  `finalize_build`'s "no method named" `E0599`
  ([`finalize_build_premature`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_build_premature.rs))
  and a variant extracted twice, an `E0308`
  ([`extract_field_twice`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/extract_field_twice.rs)).
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

What remains below are the shapes the tool does not yet reshape, grouped by what stands in the
way. Each names the fixture that pins it.

## Errors the tool cannot settle

Some failures carry a cause the tool has no way to confirm, or produce no error at all, so their
output stays as the compiler wrote it:

- **A namespace inheritance cycle:** two namespaces that inherit from each other compile under the
  pinned nightly with both trait solvers, so `cargo cgp check` reports nothing; the tool checks only
  what the next-generation solver rejects
  ([`namespace_inheritance_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-inheritance-cycle/namespace_inheritance_cycle.rs)).
- **A bare `Error` that no requirement explains:** a `#[cgp_fn]` signature or a provider body names
  `Error` without `#[use_type]`, and no requirement of the component names the trait that declares
  it. Name resolution reports an `E0425` suggesting `std::error::Error` and its namesakes, and since
  the author may mean one of them, the tool cannot check that `#[use_type(HasErrorType.Error)]` is
  the fix ([`error_alias_in_cgp_fn`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_in_cgp_fn.rs),
  [`error_alias_in_provider_body`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_in_provider_body.rs)).
- **`Self::Error` with two candidate traits:** when a second abstract-type trait declares an
  `Error`, the import cannot be chosen, so rustc's `E0220` on `__Context__` stays
  ([`self_error_two_traits`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_two_traits.rs)).
- **An optional reference to an unsized type named by a path:** `#[cgp_auto_getter]` over
  `Option<&Path>` generates a bound on the unsized `Option<Path>`, and the compiler's `E0277` lands
  on the attribute naming `[u8]`, with notes naming `Path` and `Option`
  ([`option_unsized_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/ill-formed-generated-type/option_unsized_path.rs)). The getter macros reject an
  optional reference to a slice or a trait object at expansion, since its shape shows the referent
  is unsized, but a type named by a path has a size only the compiler knows.
- **A consumer method on an unbounded type parameter, with no one bound to name:** a method two
  consumer traits declare keeps rustc's `E0599`, since either bound would let the call resolve, and
  a method of a consumer trait with a parameter keeps it too, since a bound written from the call's
  arguments would be a guess
  ([`generic_fn_two_consumers_one_method`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_two_consumers_one_method.rs),
  [`generic_fn_missing_bound_on_generic_consumer`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_missing_bound_on_generic_consumer.rs)).
- **A wrong provider or forwarding entry with no one fix:** a provider whose impls differ from its
  wiring at two arguments keeps the `[CGP-E002]` text rewrite, since no single argument is the one
  to change, and a forwarding entry for a component with a type parameter keeps rustc's two errors
  and their `trivial_bounds` suggestion, which does not fix the program, since the entry names no
  value for the parameter
  ([`provider_for_other_context_and_input`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/provider_for_other_context_and_input.rs),
  [`generic_component_forwarding_missing_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/generic_component_forwarding_missing_key.rs)).

When a lowering error's cause is visible to the macro, fixing it in `cgp` beats teaching the tool to
reconstruct it. The getter rejection above is one case; a cyclic `#[use_type]` routing is another,
which `#[use_type]`
[rejects at macro time](../../cgp/implementation/asts/attributes/use_type.md#ground_specs), so
nothing reaches the compiler for the tool to reshape.

## Errors no anchor or classifier reaches

These errors keep the compiler's output because nothing in the tool starts from them:

- **A lifetime requirement on a check entry:** an error detail borrowed through a wrapper that needs
  `'static` details, or a provider bounded on `FieldsRef<'b>` for every lifetime and checked for an
  enum with a lifetime, fails with a bare `E0477` on the check entry. The resolver walks trait
  obligations, and a lifetime requirement gives it no chain to the bound that demands `'static`
  ([`borrowed_detail`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/ordinary-trait-bound/borrowed_detail.rs),
  [`fields_ref_for_all_lifetimes`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/fields_ref_for_all_lifetimes.rs)).
- **A conflict with a namespace another crate joins or inherits:** a local key wired on an upstream
  context that joins a namespace, or registered into an upstream namespace and the parent it
  inherits, overlaps a blanket impl in the other crate. rustc names that impl only in a note, so the
  conflict classifier finds no local entry to compare with, and each `E0119` keeps rustc's wording
  ([`upstream_namespace_join_overlap`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/upstream_namespace_join_overlap.rs),
  [`upstream_namespace_inheritance_overlap`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-override-conflict/upstream_namespace_inheritance_overlap.rs)).
- **A `Symbol!` digit tag in a direct field read:** `pair.get_field(PhantomData::<Symbol!("0")>)` on
  a tuple struct keeps rustc's `E0277`, whose labels list the `Index<0>` and `Index<1>` tags the
  struct implements; the same tag reached through a check is a missing field with an `Index<0>`
  help ([`symbol_tag_on_tuple_struct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/symbol_tag_on_tuple_struct.rs)).

- **An unconstrained parameter the structural codes do not word:** a per-entry lifetime the
  provider uses, a blanket entry keyed by its own parameter, and a `#[default_impl]` of a generic
  provider struct at a path key or with a second parameter keep rustc's `E0207`s, whose suggestions
  (adding the parameter to the context, or removing it) do not compile
  ([`entry_lifetime_not_in_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/entry_lifetime_not_in_key.rs),
  [`entry_generic_blanket_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/entry_generic_blanket_key.rs),
  [`default_impl_unregistrable_provider_struct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_unregistrable_provider_struct.rs)).
- **A provider called by its own path, or an inner provider two traits could import:** a provider
  body calling another provider directly without its requirement keeps rustc's `E0277` on the
  generated `__Context__`, and an unimported inner provider whose function two provider traits
  declare, neither of them the impl's, keeps rustc's `E0599` with its consumer-trait bounds, where
  the `#[use_provider]` import is the fix (the tool drops its provider-trait bounds, which name
  `__Context__`)
  ([`missing_use_provider_concrete_qualifier`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_concrete_qualifier.rs),
  [`missing_use_provider_shared_method_name`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_shared_method_name.rs)).
  A provider trait bounding an inner provider without its context argument keeps rustc's `E0107`
  with no fix named (the tool drops its help, which adds the generated `__Context__`)
  ([`provider_trait_in_inner_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/provider_trait_in_inner_bound.rs)).
- **A wiring name the tool cannot settle or does not reach:** a key that two components share the
  name of, or that two consumer traits could be guessed from, and a type nested in a value's generic
  arguments (`UseDelegate<Missing>`) keep rustc's `E0425`s, whose suggestions of a similarly named
  item or a type parameter do not fit a wiring entry
  ([`ambiguous_component_names`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/ambiguous_component_names.rs),
  [`value_nested_type_not_declared`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/value_nested_type_not_declared.rs)).
- **A provider impl a macro writes without `#[cgp_provider]`:** the `[CGP-E039]` detector takes
  only an impl whose trait reference the program wrote, so an impl a `macro_rules!` macro writes
  falls to the `[CGP-E002]` text rewrite, which calls the impl's parameter a context, over rustc's
  list of `IsProviderFor` implementors
  ([`provider_impl_from_macro_rules`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_from_macro_rules.rs)).
  A provider whose `IsProviderFor` impl covers fewer contexts than its provider-trait impl falls to
  the same text rewrite
  ([`provider_impl_with_partial_marker`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_with_partial_marker.rs)).
- **A data operation's tag with a computed index:** the data-call anchor reads a const argument
  only when it is a literal, bare or in braces, since evaluating a constant from inside the emitter
  could report into the diagnostic it is rewriting. A `build_field` set twice through
  `Index<{ 0 + 1 }>` therefore keeps rustc's `E0271` on the builder's `Mapper`, where `Index<1>`
  reads ``[CGP-E050] field `1` of `Pair` is already set``
  ([`build_field_twice_computed_tag`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_field_twice_computed_tag.rs)).
- **A consumer method out of scope on an unbounded type parameter:** rustc's "no method named"
  `E0599` goes only to the data-call anchor, so the call-site anchor does not read it, and the error
  keeps its bound on the consumer trait, which the module does not import (the tool drops the bound
  on the provider trait, which names `__Context__`)
  ([`generic_fn_consumer_not_in_scope`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_consumer_not_in_scope.rs)).

## Errors the tool misattributes

These errors are reshaped, but the reshaped message names the wrong owner of the cause:

- **A blanket-trait bound on a struct:** a `#[cgp_fn]` trait required by a struct's bound
  (`pub struct Holder<T: GetName>(pub T)`), built with a context that lacks the field the trait
  reads, is reported as `` missing field `name` on `Holder<T>` ``. The field is missing on the context
  (`App`), and rustc's own message names `App: GetName`; the by-blanket-trait use-site anchor takes
  the struct whose definition holds the bound as the owner
  ([`cgp_fn_struct_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_struct_bound.rs)).

## Errors that need a new class or a deeper walk

These errors are reshaped in part or not at all, and stating their cause needs a class or a walk the
tool does not have:

- **A matcher where a handler or an enum belongs:** a value matcher wired as a `Handler` names its
  expansion, `MatchWithHandlers<Product![ExtractFieldAndHandle<…>, …]>`, as the type that is not a
  provider, and one applied to a struct ends at a bound on the internal `HasFieldHandlers` trait.
  Neither says which construct the program wrote wrong
  ([`matcher_wired_to_handler`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/matcher_wired_to_handler.rs),
  [`value_matcher_on_struct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/value_matcher_on_struct.rs)).
- **One implicit field read as two types:** two methods of one provider read `count` as `u32` and
  as `u64`, and rustc's `E0284` and `E0282` on the provider name `__Context__` without saying that
  the methods disagree ([`implicit_conflicting_types`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/implicit-arguments/implicit_conflicting_types.rs)).
- **A component named with a parameter:** `#[cgp_impl(new SquareArea)]` names the component after
  the provider trait, `AreaCalculatorComponent`, while the component's name carries a parameter, and
  the `E0107` does not say where the name came from
  ([`parameterized_name_default_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/macro-defects/parameterized_name_default_component.rs)).
- **A dispatcher wired as the entry for the type it dispatches:** the `[CGP-E020]` help names the
  provider whose requirement closes the loop (`EvalAdd`), while the fix is a wrapper provider for
  the dispatcher's own entry, which the walk cannot infer
  ([`dispatcher_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/dispatcher_cycle.rs)).
- **A cycle through a plain blanket trait across two contexts:** the walk reads a plain bound on
  another type as a leaf, so the cycle is not named: merged with a missing field, it is reported as
  that bound, `Outer: Linked`, beside the field
  ([`cross_context_cycle_reuse`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cross_context_cycle_reuse.rs)),
  and on its own the overflow keeps rustc's wording
  ([`cross_context_cycle_reuse_distinct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cross_context_cycle_reuse_distinct.rs)).

## What good presentation looks like

The bar is the one the check-trait-failure family meets: lead with the cause as one plain sentence,
name the decoded construct, give a short dependency path, and never let a misleading `rustc`
heuristic outrank the real cause. For the shapes above, that means naming the construct the program
wrote in place of the machinery it expands to, and keeping only suggestions that compile. The
[CGP-side tooling notes](../../cgp/errors/checks/check-trait-failure.md#how-cargo-cgp-presents-it)
describe the same extraction from the catalog side and are the reference to build against.
