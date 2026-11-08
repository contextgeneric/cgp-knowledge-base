# Unsatisfied dependency (hidden)

A provider is wired onto a context that cannot satisfy the provider's impl-side dependency, and the
failure is triggered by calling the consumer-trait method directly, so the compiler reports only
that the method's trait bounds are unsatisfied (`E0599`) and hides the dependency that failed.

## What triggers it

This class arises because [wiring](../../reference/macros/delegate_components.md) is lazy and the mistake is
exercised through a method call rather than a check. A provider carries an impl-side dependency, a context
wired to it does not meet the dependency, and `delegate_components!` accepts the entry without verifying it.
The failure appears when the consumer method is called. The leaf can be any bound the provider names (a
missing `HasField`, a CGP trait like `HasName`, or an [ordinary trait bound](../checks/ordinary-trait-bound.md)
such as `Scalar: Eq`), since the method probe drops the nested bound without inspecting it.

```rust
#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}

#[cgp_auto_getter]
pub trait HasName {
    fn name(&self) -> &str;
}

#[cgp_impl(new GreetHello)]
impl Greeter
where
    Self: HasName, // impl-side dependency
{
    fn greet(&self) {
        let _ = self.name();
    }
}

#[derive(HasField)]
pub struct Person {
    pub age: u8, // no `name` field, so Person does not implement HasName
}

// Accepted even though Person cannot satisfy GreetHello's `Self: HasName`.
delegate_components! {
    Person {
        GreeterComponent: GreetHello,
    }
}

fn main() {
    Person { age: 0 }.greet(); // fails here, at the call site
}
```

Using the consumer trait as a bound (`fn use_it<C: CanGreet>(c: &C)` called on a `Person`) is a different
proof: the solver must prove the bound directly, so stable's `E0277` does carry the leaf, as
[the raw diagnostic](#the-raw-diagnostic) describes.

## The raw diagnostic

This section describes plain `cargo check`, the fallback when `cargo-cgp` is not on hand. This is a **hidden**
class: stable prints an `E0599`, "the method `greet` exists for struct `Person`, but its trait bounds were not
satisfied", whose notes name `Person: CanGreet` and `Person: Greeter<Person>`, say the trait `Greeter` must be
implemented, and stop. The output does not mention `HasName` or the missing `HasField`, so the cause is absent
rather than buried.

The form also misdirects. It adds "this is an associated function, not a method" and suggests the call
`Person::greet()`, because the provider trait's `greet(context: &Context)` has no `self` receiver. The
suggestion drops the required context argument and says nothing about the dependency.

The absence comes from a compiler heuristic. `#[cgp_component]` emits a blanket impl of the consumer trait, so
checking `Person: CanGreet` finds it, sees that `Person: Greeter<Person>` is unmet, and declines to expand the
nested bound. rustc does not in general report which `where` bound of an inapplicable blanket impl failed, a
limitation of `E0599` tracked upstream in [rust-lang/rust#61661](https://github.com/rust-lang/rust/issues/61661)
and [#75222](https://github.com/rust-lang/rust/issues/75222). CGP's
[`IsProviderFor`](../../reference/traits/is_provider_for.md) supertrait defeats it only where a bound requires it
directly.

**A consumer-trait bound on a called function is not hidden.** Its stable `E0277` opens with an intermediate
block, `GreetHello: Greeter<Person>` with the "conditionally implemented" hint, then `Person: CanGreet`, whose
`help:` names the missing `HasField<Symbol<4, Chars<'n', …>>>` and whose chain runs through `HasName` and
`IsProviderFor`. Read it as a [check-trait failure](../checks/check-trait-failure.md).

The same `E0599` also arises when the wiring is missing rather than unmet: a component never wired, or an
[unregistered namespace path](../checks/unregistered-namespace-path.md). Only a check tells the two apart.

## Where the root cause is

On stable, the root cause is **not present in the `E0599` output**, so a reader or tool must not scan it for the
failing dependency. The most specific thing it names is the provider trait (`Person: Greeter<Person>`) or the
consumer trait (`Person: CanGreet`).

**The nightly `cargo-cgp` pins descends further.** It prints the same `E0599` with a
`note: trait bound … was not satisfied` naming the leaf: `Person: HasField<Symbol<4, Chars<..>>>` for the missing
field, or `f64: Eq` for an ordinary bound. The fixtures' `.rust.stderr` snapshots come from that nightly, so they
show the leaf, though the chain between the consumer trait and the leaf is still missing.

## How cargo-cgp presents it

This is the one class where the tool does more than reshape text: its next-generation solver **recovers the cause
the raw `E0599` discarded.** It keeps the Rust code and rewrites the headline to the cause,
`` [CGP-E001] missing field `name` on `Person` ``, over a `root cause:` note and a tree the raw output never held:
`[CGP-E101]` consumer hop, `[CGP-E102]` provider hop, `[CGP-E104]` for `HasName`, then the `[CGP-E110]` leaf. The
method-probe advice is dropped. The [cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) defines the codes.

The leaf names the mistake, and the result reads as a [check-trait failure](../checks/check-trait-failure.md) for the
same mistake does. Beyond the leaves that class lists, these shapes are specific to a call:

- **A `#[cgp_auto_dispatch]` call** whose enum has a payload without the trait, recovered through the generated
  matcher: ``[CGP-E003] the trait bound `Square: HasArea` is not satisfied``.
- **A provider's own method called through its path** (`Add::try_compute(&App, …)`), classed as a
  `#[check_providers]` entry is: ``[CGP-E002] missing wiring for `ErrorTypeProviderComponent` on `App` ``.
- **A hand-written `DelegateComponent` impl** without `IsProviderFor` beside it, which passes a check but fails every
  call: ``[CGP-E128] the wiring of `GreeterComponent` on `App` has no `IsProviderFor` impl ``.
- **A consumer method on an unbounded type parameter,** which is a missing bound rather than missing wiring:
  ``[CGP-E129] the type parameter `Context` of `run` is not bounded by `CanGreet` ``.

One call shape stays as rustc wrote it, because no anchor reads it: a generic consumer called on a
field access
([`generic_consumer_field_access_receiver`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_consumer_field_access_receiver.rs)).
A method's own `where` bound classifies from the provider's trait instead, leading with
`` [CGP-E002] the provider trait `Loader<u32>` with context `App` is not implemented for provider `LoadName` ``
([`method_own_bound_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/method_own_bound_call.rs)).

## Resolving it

Give the context what the provider needs: add the `name` field, or wire the getter component to an existing field.
The difficulty is finding it, so **promote the hidden error** with a
[`check_components!`](../../reference/macros/check_components.md) at the wiring site:

```rust
check_components! {
    Person {
        GreeterComponent,
    }
}
```

The check requires `GreetHello: IsProviderFor<GreeterComponent, Person>` as a direct bound, so the compiler reports the
chain down to the missing field: the [check-trait failure](../checks/check-trait-failure.md) class. The
[debugging guide](../../guides/debugging.md) prescribes this move.

## Notes for tooling

A text-only post-processor cannot recover the cause, since the text never held it. It can recognize the class: an
`E0599` "method exists but its trait bounds were not satisfied" whose unmet bound is `Context: SomeProvider<Context>`.
Only re-driving the solver, or promoting to a check, finds the cause.

## Backing fixtures

- [`hidden/unsatisfied-dependency/missing_dependency_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/missing_dependency_call.rs):
  `GreetHello` requires `Self: HasName`, `Person` lacks `name`, and the method is called directly. Its checked
  counterpart is
  [`checks/check-trait-failure/fields/missing_dependency.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/missing_dependency.rs).
- [`hidden/unsatisfied-dependency/ordinary_bound_unsatisfied_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/ordinary_bound_unsatisfied_call.rs):
  the same `E0599` where the leaf is an ordinary bound (`Scalar: Eq`, with `f64` wired), recovered under
  `[CGP-E001]` over `[CGP-E117]`.
- [`hidden/unsatisfied-dependency/provider_for_other_context_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/provider_for_other_context_call.rs):
  `GreetPerson` implements `Greeter` for `Person` and `Robot` wires it, ending at `[CGP-E127]`. Its checked
  counterpart is
  [`checks/check-trait-failure/providers/provider_for_other_context.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/provider_for_other_context.rs).
- [`hidden/unsatisfied-dependency/provider_called_directly_without_error_type.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/provider_called_directly_without_error_type.rs):
  a `#[cgp_computer]` provider's `try_compute` called through its path on a context without an error type:
  `[CGP-E002]`. Its sibling
  [`provider_called_directly.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/provider_called_directly.rs)
  calls a `PipeHandlers` pipeline whose second stage takes the first stage's input type, ending at `[CGP-E127]`.
- [`hidden/unsatisfied-dependency/cgp_fn_output_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_output_bound.rs):
  a `#[cgp_fn]` whose generic output a provider bound pins, reached by the call-site anchor.
- [`hidden/unsatisfied-dependency/field_access_receiver_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/field_access_receiver_call.rs):
  a consumer called on a field access, recovered by the use-site anchor.
- [`hidden/unsatisfied-dependency/generic_consumer_field_access_receiver.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_consumer_field_access_receiver.rs):
  a generic consumer called on a field access, which declines.
- [`hidden/unsatisfied-dependency/method_own_bound_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/method_own_bound_call.rs):
  a method's own `where` bound, which no anchor reads.
- [`hidden/unsatisfied-dependency/method_own_bound_output_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/method_own_bound_output_mismatch.rs):
  the same bound failing on its associated type, left as rustc's `E0271`.
- [`hidden/unsatisfied-dependency/consumer_bound_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/consumer_bound_call.rs):
  the consumer trait as a bound, `fn greet_twice<Context: CanGreet>(…)` called with a `Person` lacking `name`,
  whose stable `E0277` carries the leaf. Its sibling
  [`raise_error_unwired_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/raise_error_unwired_call.rs)
  bounds a function on `CanRaiseError<String>` on a context with no error raiser wired.
- [`hidden/unsatisfied-dependency/generic_fn_missing_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_missing_bound.rs):
  `context.greet()` in `fn run<Context>(context: &Context)` without the bound: `[CGP-E129]`.
- [`hidden/unsatisfied-dependency/hand_delegate_without_is_provider.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/hand_delegate_without_is_provider.rs):
  `App` wired by a hand-written `impl DelegateComponent<GreeterComponent> for App` and called: `[CGP-E128]`.
- [`hidden/unsatisfied-dependency/auto_dispatch_missing_variant_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/auto_dispatch_missing_variant_impl.rs):
  a [`#[cgp_auto_dispatch]`](../../reference/macros/cgp_auto_dispatch.md) call where one of an enum's payloads
  lacks the trait, leading with `[CGP-E003]` over the matcher chain.
- [`hidden/unsatisfied-dependency/call_site_annotated_receiver.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/call_site_annotated_receiver.rs):
  a failing call whose receiver is a `let` with a type annotation.
- [`hidden/unsatisfied-dependency/call_site_tuple_input.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/call_site_tuple_input.rs):
  a call-site `E0277` whose failing provider destructures a tuple input, so the cause is reachable only once that shape is recovered.
- [`hidden/unsatisfied-dependency/call_site_written_shapes.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/call_site_written_shapes.rs):
  a call-site `E0277` whose input writes its type in every shape the call-site anchor reads.
- [`hidden/unsatisfied-dependency/cascade_after_use_site.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_after_use_site.rs):
  a use-site `E0277` on a `Code`-dispatched handler pipeline, resolved from the call expression itself.
- [`hidden/unsatisfied-dependency/cascade_later_stage.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_later_stage.rs):
  a use-site `E0277` on a `Code`-dispatched handler pipeline whose root cause lives in a *later* stage, the shape `cascade_after_use_site` does not cover.
- [`hidden/unsatisfied-dependency/cascade_later_stage_input.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_later_stage_input.rs):
  a use-site `E0277` on a `Code`-dispatched handler pipeline whose root cause is a *later* stage's requirement on its **input type**, where that input is an earlier stage's fixed output, threaded through a forwarding `Call` handler.
- [`hidden/unsatisfied-dependency/cascade_nested_projection.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_nested_projection.rs):
  a use-site `E0277` on a `Code`-dispatched handler pipeline whose root cause is a missing **input-dispatch entry**: the third stage dispatches its provider on the *input type* through [`UseInputDelegate`](https://github.com/contextgeneric/cgp-knowledge-base/blob/main/cgp/reference/providers/use_delegate.md), and no entry matches the type the second stage produces.
- [`hidden/unsatisfied-dependency/cgp_fn_call_mixed_causes.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_call_mixed_causes.rs):
  a direct call to a `#[cgp_fn]` trait method on a type without wiring, whose blanket impl fails for two kinds of cause.
- [`hidden/unsatisfied-dependency/cgp_fn_struct_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_struct_bound.rs):
  a `#[cgp_fn]` trait required by a **struct's** bound, built with a context missing the field the trait reads.
- [`hidden/unsatisfied-dependency/cgp_fn_struct_bound_in_type.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_struct_bound_in_type.rs):
  a `#[cgp_fn]` trait required by a struct's bound, where the struct is only named in a type, so no expression carries the context.
- [`hidden/unsatisfied-dependency/cgp_fn_struct_where_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_struct_where_bound.rs):
  a `#[cgp_fn]` trait required by a struct's `where` clause, built with a context missing the field the trait reads.
- [`hidden/unsatisfied-dependency/cgp_fn_use_site.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_use_site.rs):
  a `#[cgp_fn]` trait called at a **use site**, on a context that cannot satisfy it.
- [`hidden/unsatisfied-dependency/cgp_fn_where_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_where_bound.rs):
  a `#[cgp_fn]` trait required through a `where` **bound**, not called as a method.
- [`hidden/unsatisfied-dependency/consumer_struct_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/consumer_struct_bound.rs):
  a consumer trait required by a struct's bound, built with a context whose wiring misses the field the provider reads.
- [`hidden/unsatisfied-dependency/empty_dispatch_table.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/empty_dispatch_table.rs):
  a use-site `E0277` on a handler pipeline whose root cause is an *empty* input-dispatch table: the second stage dispatches its provider on the input type through `UseInputDelegate<EmptySink>`, and that table wires no entries at all.
- [`hidden/unsatisfied-dependency/enum_hasfields_lock.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/enum_hasfields_lock.rs):
  a resolution-class `E0599` near CGP wiring, which must not crash the resolver.
- [`hidden/unsatisfied-dependency/foreign_context_error_route.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/foreign_context_error_route.rs):
  a handler pipeline run on a context defined in another crate, with one error type unrouted.
- [`hidden/unsatisfied-dependency/foreign_context_where_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/foreign_context_where_bound.rs):
  a hand-written impl whose own `where` clause names a context defined in another crate, with one error type unrouted.
- [`hidden/unsatisfied-dependency/foreign_context_wrapper_chain.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/foreign_context_wrapper_chain.rs):
  a local wrapper trait implemented on a foreign type that holds a context defined in another crate, with one error type unrouted.
- [`hidden/unsatisfied-dependency/foreign_context_wrapper_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/foreign_context_wrapper_impl.rs):
  a local wrapper trait implemented on a context defined in another crate, with one error type unrouted.
- [`hidden/unsatisfied-dependency/generic_consumer_bound_reference_binding.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_consumer_bound_reference_binding.rs):
  a generic function's bound on a generic consumer trait, its context from a binding of reference type.
- [`hidden/unsatisfied-dependency/generic_consumer_use_site.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_consumer_use_site.rs):
  a *generic* consumer failing at its call site, its parameter recovered from a plain value argument.
- [`hidden/unsatisfied-dependency/generic_fn_consumer_not_in_scope.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_consumer_not_in_scope.rs):
  a consumer method called on an unbounded type parameter, where the consumer trait is not in scope.
- [`hidden/unsatisfied-dependency/generic_fn_missing_bound_on_generic_consumer.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_missing_bound_on_generic_consumer.rs):
  a method of a consumer trait with a parameter, called on an unbounded type parameter.
- [`hidden/unsatisfied-dependency/generic_fn_two_consumers_one_method.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_two_consumers_one_method.rs):
  a method two consumer traits declare, called on an unbounded type parameter.
- [`hidden/unsatisfied-dependency/getter_unwired_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/getter_unwired_call.rs):
  calling a `#[cgp_getter]` method on a context that does not wire the getter.
- [`hidden/unsatisfied-dependency/manual_supertrait_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/manual_supertrait_impl.rs):
  a wiring gap surfaced inside a *hand-written* `impl Trait for Context` block, where the caret sits on the impl, never on the context's own type definition.
- [`hidden/unsatisfied-dependency/missing_wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/missing_wiring.rs):
  a missing wiring surfaced at the *use site* rather than at a check.
- [`hidden/unsatisfied-dependency/namespace_join_use_site.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/namespace_join_use_site.rs):
  a use-site failure on a namespace-joined context, resolved to its root cause *through* the namespace.
- [`hidden/unsatisfied-dependency/open_dispatch_use_site.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/open_dispatch_use_site.rs):
  a use-site failure on an `open`-dispatched context, resolved to the real missing wiring.
- [`hidden/unsatisfied-dependency/placeholder_error_route_leaf.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/placeholder_error_route_leaf.rs):
  a pipeline call whose first stage raises its input's error type, with the input left to inference.
- [`hidden/unsatisfied-dependency/provider_called_directly_name_shared.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/provider_called_directly_name_shared.rs):
  a provider's own method called through its path, where a provider trait of another module declares a function of the same name.
- [`hidden/unsatisfied-dependency/unrelated_error_before_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_before_call.rs):
  a plain Rust error in a function that also calls a consumer method whose wiring fails.
- [`hidden/unsatisfied-dependency/unrelated_error_in_awaited_argument.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_in_awaited_argument.rs):
  a plain Rust error inside an argument of an awaited consumer method call whose wiring fails.
- [`hidden/unsatisfied-dependency/unrelated_error_in_call_argument.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_in_call_argument.rs):
  a plain Rust error inside an argument of a consumer method call whose wiring fails.
- [`hidden/unsatisfied-dependency/unrelated_error_in_forwarding_argument.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_in_forwarding_argument.rs):
  a plain Rust error inside an argument of a hand-written impl's forwarding call, whose CGP supertrait also fails.
- [`hidden/unsatisfied-dependency/unrelated_error_in_wrapper_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_in_wrapper_impl.rs):
  a plain Rust error inside a hand-written impl whose CGP supertrait also fails.
- [`hidden/unsatisfied-dependency/unrelated_error_noted_on_foreign_wrapper_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_noted_on_foreign_wrapper_impl.rs):
  a plain Rust error whose note points at a wrapper impl on a foreign type whose chain reaches a failing CGP consumer.
- [`hidden/unsatisfied-dependency/unrelated_error_noted_on_wrapper_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_noted_on_wrapper_impl.rs):
  a plain Rust error whose note points at a hand-written impl whose CGP supertrait also fails.
- [`hidden/unsatisfied-dependency/unsatisfied_dependency.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unsatisfied_dependency.rs):
  a hidden-class error whose cause the tool surfaces.
- [`hidden/unsatisfied-dependency/upstream_blanket_trait_use_site.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/upstream_blanket_trait_use_site.rs):
  a `#[cgp_fn]` trait defined **upstream**, called on a context that cannot satisfy it.
- [`hidden/unsatisfied-dependency/use_site_shared_cause.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/use_site_shared_cause.rs):
  every consumer a use-site failure names gets its chain, sharing one root cause.
- [`hidden/unsatisfied-dependency/wrapper_impl_with_failing_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/wrapper_impl_with_failing_bound.rs):
  a wrapper impl on a context whose supertrait and own `where` bound fail for different causes.

## Related

- [Check-trait failure (surfaced)](../checks/check-trait-failure.md): the same unmet dependency
  forced through a check, where the cause *is* reported; the two are the two halves of one
  phenomenon.
- [Unsatisfied ordinary trait bound (surfaced)](../checks/ordinary-trait-bound.md): the surfaced
  class for the ordinary-trait-bound flavor of this hidden failure.
- [Debugging CGP compile errors](../../guides/debugging.md): the playbook: read the error's shape,
  then move the error to the wiring site with a check to surface a hidden cause.
- [`IsProviderFor`](../../reference/traits/is_provider_for.md) and
  [`DelegateComponent`](../../reference/traits/delegate_component.md): the traits every wiring error
  is ultimately about; `IsProviderFor` is the supertrait a check uses to defeat the suppression
  heuristic.
- [`check_components!`](../../reference/macros/check_components.md) and the
  [check-traits concept](../../concepts/check-traits.md): why wiring is lazy and how a check forces
  a readable error at the wiring site.
