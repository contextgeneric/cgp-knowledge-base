# Usability issues

This document lists the ways `cargo-cgp` presents errors that carry the root cause but bury it: the
problems a reader hits even when the diagnostic contains everything needed to find the cause. What
separates these from a [hidden root cause](hidden-root-cause.md) is that the information is present:
the cause could be recovered from the output by a careful reader or a post-processor, so the work
here is re-presentation, not recovery. Every issue is backed by a fixture under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/) whose header declares `//@quality: usability`, in the directory of its error
class. When a fixture's presentation reaches the bar, its header changes to
`//@quality: acceptable` and its issue is deleted from this document.

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
- **A check that carries a generic parameter:** `check_components! { <T> App<T> { … } }` keeps
  rustc's headline over the renamed notes, whose `help` still names the missing field. The resolver
  solves under an empty parameter environment, where the solver does not prove a wiring lookup that
  names the check's own `T`, so a walk would report a wired component as missing. It declines any
  seed holding a type parameter
  ([`generic_check_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_check_context.rs),
  and the same seed from a generic wrapper impl,
  [`generic_wrapper_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_wrapper_impl.rs),
  and from an overflow,
  [`generic_check_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/generic_check_cycle.rs)).
  Checking or calling one instantiation resolves as usual.
- **A method's own `where` bound:** a generic method bounded by `where Self: CanLoad<T, Output = T>`
  keeps rustc's report, since the bound-call anchor reads a path call's function and not a method's
  bound
  ([`method_own_bound_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/method_own_bound_call.rs),
  [`method_own_bound_output_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/method_own_bound_output_mismatch.rs)).
- **A generic consumer called on a field access:** only typeck could type the receiver, and the
  component's parameter rides in the call
  ([`generic_consumer_field_access_receiver`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_consumer_field_access_receiver.rs)).
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
- **A blanket-trait bound on a struct named only in a type:** `pub holder: Holder<App>` for a
  `Holder<T: GetName>` has no expression to read `App` from and no span on `App`'s definition, so the
  error keeps rustc's `E0277`, which states the missing field in a `help` under the bound
  ([`cgp_fn_struct_bound_in_type`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_struct_bound_in_type.rs)).

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
