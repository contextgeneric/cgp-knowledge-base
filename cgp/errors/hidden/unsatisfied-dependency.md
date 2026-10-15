# Unsatisfied dependency (hidden)

A provider is wired onto a context that cannot satisfy the provider's impl-side dependency, and the
failure is triggered by calling the consumer-trait method directly, so the compiler reports only
that the method's trait bounds are unsatisfied (`E0599`, or `E0277` when the consumer trait is used
as a bound) and hides the dependency that actually failed.

## What triggers it

This class arises whenever [wiring](../../reference/macros/delegate_components.md) is lazy and the
mistake is exercised through the consumer trait rather than a check. A provider carries an impl-side
dependency in its `where` clause; a context is wired to that provider but does not meet the
dependency; and because `delegate_components!` records the entry without verifying the provider's
transitive requirements, the wiring is accepted. The failure appears only when the context's
consumer-trait method is finally called. The dependency's leaf can be any bound the provider names
(a missing `HasField`, an unmet CGP trait like `HasName`, or an
[ordinary Rust trait bound](../checks/ordinary-trait-bound.md) such as `Scalar: Eq` on an abstract
type), and the hidden form suppresses it identically in every case, because the compiler's
method-probe heuristic drops the nested bound without inspecting what it is.

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

The same hiding occurs, in a slightly different shape, when the consumer trait is used as a bound
(`fn use_it<C: CanGreet>(c: &C)` called on a `Person`) rather than as a direct method call. Both
exercise the broken wiring through the consumer trait, and both hide the cause; the difference is
only the error code.

## The raw diagnostic

This section describes what plain `cargo check` prints, the fallback when `cargo-cgp` is not on
hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers the recovered form, which
for this class is not a reformat but a genuinely different output. This is a **hidden** class: the
compiler prints a short diagnostic that names the traits it could not satisfy but never descends to
the dependency that failed. Calling the method directly produces an `E0599`, "the method `greet`
exists for struct `Person`, but its trait bounds were not satisfied", whose notes state that
`Person` does not satisfy `Person: CanGreet` or `Person: Greeter<Person>` and that the trait
`Greeter` must be implemented, and then stop. Using the consumer trait as a `where` bound instead
produces an `E0277` reporting that `Person: CanGreet` is not satisfied, again without expanding why.
In neither shape does the output mention `HasName` or the missing `HasField<Symbol!("name")>`; the
real cause is absent, not merely buried.

The `E0599` form carries one more piece of misdirection worth naming so a reader discounts it.
Alongside the unsatisfied-bound notes, the compiler adds "this is an associated function, not a
method," reports `greet` under "found the following associated functions," and suggests rewriting
the call as `Person::greet()`. This is an artifact of how `#[cgp_component]` lowers the method: the
provider trait's `greet(context: &Context)` has no `self` receiver, so the method probe classifies
it as an associated function. The suggestion is wrong (`Person::greet()` drops the required context
argument), and it says nothing about the missing dependency; it is noise the class produces, not a
clue.

The reason the cause is absent is a deliberate compiler heuristic, and it is the whole point of
isolating this class. `#[cgp_component]` emits a blanket impl of the consumer trait for any context
that is its own provider, so when the compiler checks `Person: CanGreet` it finds that blanket impl
(alongside every other candidate impl in scope), determines it does not apply because
`Person: Greeter<Person>` is unmet, and declines to expand the nested `where` bound that made it
inapplicable. `rustc` does not, in general, report *which* `where`-clause bound of an inapplicable
blanket impl failed. It reports only that the top-level trait is unimplemented and stops, because
with a blanket impl and multiple candidates present, expanding every candidate's unmet sub-bound
would usually be noise. This is a long-standing, acknowledged limitation of the `E0599` diagnostic,
tracked upstream in [rust-lang/rust#61661](https://github.com/rust-lang/rust/issues/61661) and
[#75222](https://github.com/rust-lang/rust/issues/75222), not a quirk of CGP. The suppression is
exactly what CGP's [`IsProviderFor`](../../reference/traits/is_provider_for.md) supertrait exists to
defeat, but only a check that requires `IsProviderFor` *directly* forces the compiler past the
heuristic; the lazy consumer-trait path never does.

The same `E0599`/`E0277` shape, and the same absence of a cause, also arises when the wiring is not
merely *unmet* but *missing*: a component never wired on the context, or an
[unregistered namespace path](../checks/unregistered-namespace-path.md) whose redirect lands on an
empty table slot. Whether a provider was found but its dependency failed, or no provider was found
at all, the consumer-trait path hides it identically; the two are told apart only by promoting the
error into a surfaced one.

## Where the root cause is

On stable `rustc` (checked with 1.98.1), the root cause is **not present in the output.** A reader
or tool must not scan this diagnostic for the failing dependency, because the compiler discarded it
before printing. The most specific thing the output names is the unsatisfied provider trait
(`Person: Greeter<Person>`) or consumer trait (`Person: CanGreet`); everything below that (the
missing field, the unmet `HasName`, any deeper transitive bound) is gone. This absence is the
defining property of the class and the reason it lives apart from the
[surfaced classes](../checks/), whose diagnostics *do* carry the cause.

**Newer nightly compilers descend further, so the class is hidden only on stable.** The
nightly toolchain that `cargo-cgp` pins prints the same `E0599` but adds a
`note: trait bound … was not satisfied` naming the leaf itself:
`Person: HasField<Symbol<4, Chars<..>>>` for the missing field, or `f64: Eq` for an ordinary bound.
The `method … not found … because it doesn't satisfy` line names the leaf as well. The fixtures'
`.rust.stderr` snapshots are produced with that nightly, so they show the leaf; on stable, the note
stops at `Person: Greeter<Person>`. A reader on a recent nightly can therefore read the leaf from
the raw output, although the chain between the consumer trait and the leaf is still missing.

## How cargo-cgp presents it

`cargo-cgp` is the reason this class need not stay hidden, and it is the one class where the tool
does more than reshape existing text: its next-generation trait solver **recovers the cause the raw
`E0599` discarded.** Where plain `cargo check` on stable prints a diagnostic that bottoms out at
`Person: Greeter<Person>` and names no dependency, `cargo-cgp` keeps the Rust code (`E0599` at a
call site, `E0277` at a `where` bound) but rewrites the headline to the recovered cause,
`` [CGP-E001] missing field `name` on `Person` ``, and attaches a `root cause:` note: a
`` [CGP-E110] missing field `name` on `Person` `` leaf over a compact dependency tree that the raw
output never contained at all: `[CGP-E101]` consumer-trait hop → `[CGP-E102]` provider-trait hop →
`[CGP-E104]` the `HasName` trait → the `[CGP-E110]` field leaf. The method-probe misdirection ("this
is an associated function, not a method" and the wrong `Person::greet()` suggestion) is dropped, so
the recovered cause leads instead of the noise.

The leaf the tree bottoms out on names the actual mistake, and it varies with the suppressed
dependency's kind. A genuinely absent field is `[CGP-E110]`; a struct that never derived `HasField`
coalesces to `[CGP-E111]`; a component the context never wired, or an
[unregistered namespace path](../checks/unregistered-namespace-path.md), is
``[CGP-E113] missing wiring for `GreeterComponent` on `Person` ``. When the buried leaf is an
[ordinary Rust trait bound](../checks/ordinary-trait-bound.md) such as `Scalar: Eq`, the tree's
terminal passes the bound through in rustc's own words and the `root cause:` lead takes `[CGP-E117]`
instead. A provider written for another context, wired on this one, ends at
``[CGP-E127] `GreetPerson` implements `Greeter` only for `Person`, not `Robot` ``. In every case the
recovered result matches, byte for byte, what a
[check-trait failure](../checks/check-trait-failure.md) produces for the same mistake, which is
exactly how `cargo-cgp` recovers it, by promoting the hidden bound to the direct one the solver will
trace. A call to a [`#[cgp_auto_dispatch]`](../../reference/macros/cgp_auto_dispatch.md) trait whose
enum has a payload without the trait is recovered as well, though the trait is no component and has
no check form: the tree runs through the generated matcher to the per-variant computer and ends at
the payload's missing impl, ``[CGP-E003] the trait bound `Square: HasArea` is not satisfied``. A
provider's own method called through its path (`Add::try_compute(&App, …)`), which asserts the
provider trait itself, is recovered the way a `#[check_providers]` entry is, as the provider class
``[CGP-E002] missing wiring for `ErrorTypeProviderComponent` on `App` ``. A context wired by a
hand-written `DelegateComponent` impl, with no `IsProviderFor` impl beside it, passes a check but
fails every call, since only the call's route needs the context's own `IsProviderFor`; it ends at
``[CGP-E128] the wiring of `GreeterComponent` on `App` has no `IsProviderFor` impl ``, with a `help`
naming the `delegate_components!` entry to write. The codes are defined in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md).

## Resolving it

The underlying fix is ordinary: give the context what the provider needs (add the `name` field to
`Person`, or wire the getter component to an existing field), so `Person` satisfies `HasName` and
`GreetHello` becomes a valid provider. The difficulty is not the fix but *finding* it, since the
error points nowhere useful.

To make the cause visible, **promote the hidden error into a surfaced one** by forcing the check at
the wiring site with [`check_components!`](../../reference/macros/check_components.md):

```rust
check_components! {
    Person {
        GreeterComponent,
    }
}
```

The check asserts `CanUseComponent<GreeterComponent>` for `Person`, which requires
`GreetHello: IsProviderFor<GreeterComponent, Person>` as a *direct* bound. That defeats the
suppression heuristic, and the compiler now reports the full `E0277` note chain ending at the
missing `HasField<Symbol!("name")>`. That surfaced form is the
[check-trait failure](../checks/check-trait-failure.md) class, and moving between the two is the
standard technique the [debugging guide](../../guides/debugging.md) prescribes for a hidden
dependency.

## Notes for tooling

The move this class needs, inspecting the fulfillment errors the trait solver produced but the
diagnostic heuristic suppressed rather than reformatting text that never held the cause, is exactly
what `cargo-cgp`'s typed resolver already performs (above), which is why this class is *replaced*
rather than reshaped. What remains useful to a plainer tool, or to a reader on the raw fallback, is
recognizing the class without the cause: an `E0599` "method exists but its trait bounds were not
satisfied" whose unmet bound is a provider trait of the form `Context: SomeProvider<Context>`, or an
`E0277` on a consumer trait backed by a `…Component` blanket impl, with no note descending past that
bound. A text-only post-processor cannot recover the cause here; only re-driving the solver (or
promoting to a check) can.

## Backing fixtures

- [`hidden/unsatisfied-dependency/missing_dependency_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/missing_dependency_call.rs):
  `GreetHello` requires `Self: HasName`, `Person` lacks the `name` field, and the method is called
  directly; its `.rust.stderr` pins the raw `E0599` as the pinned nightly prints it, whose notes
  already name the `HasField<Symbol<4, …>>` leaf (plus the method-probe advice) but not the chain to
  it, and its `.cgp.stderr` the recovered `[CGP-E001]` headline over a
  `` root cause: [CGP-E110] missing field `name` `` tree. Its checked counterpart,
  [`checks/check-trait-failure/fields/missing_dependency.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/missing_dependency.rs),
  reaches the same mistake through a check and belongs to the
  [check-trait failure](../checks/check-trait-failure.md) class.
- [`hidden/unsatisfied-dependency/ordinary_bound_unsatisfied_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/ordinary_bound_unsatisfied_call.rs):
  the same hidden `E0599` where the suppressed leaf is an *ordinary* trait bound (`Scalar: Eq`, with
  `f64` wired) rather than a `HasField`, which stable hides the same way whatever the leaf's kind,
  and whose nightly `.rust.stderr` names `f64: Eq` in a note; its `.cgp.stderr` recovers the cause
  as a ``[CGP-E001] the trait bound `f64: Eq` is not satisfied`` headline over a
  ``root cause: [CGP-E117] the trait bound `f64: Eq` is not satisfied`` tree. Its surfaced
  counterpart is the [unsatisfied ordinary trait bound](../checks/ordinary-trait-bound.md) class.
- [`hidden/unsatisfied-dependency/provider_for_other_context_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/provider_for_other_context_call.rs):
  the hidden `E0599` where the provider `GreetPerson` implements `Greeter` for `Person` and `Robot`
  wires it; the `.rust.stderr` names the unmet `GreetPerson: IsProviderFor<GreeterComponent, Robot>`
  but never the context the provider takes, and the `.cgp.stderr` leads with the
  `[CGP-E127]` cause. Its checked counterpart is
  [`checks/check-trait-failure/providers/provider_for_other_context.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/provider_for_other_context.rs).
- [`hidden/unsatisfied-dependency/provider_called_directly_without_error_type.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/provider_called_directly_without_error_type.rs):
  a `#[cgp_computer]` provider's fallible `try_compute` called through its path on a context with no
  error type; the `.rust.stderr` stops at `App: ErrorTypeProvider<App>` with rustc's implementor
  list, and the `.cgp.stderr` leads with the `[CGP-E002]` missing wiring and its `help`. Its sibling
  [`provider_called_directly.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/provider_called_directly.rs)
  calls a `PipeHandlers` pipeline whose second stage takes the first stage's input type, not its
  `Result` output, and ends at `[CGP-E127]`.
- [`hidden/unsatisfied-dependency/consumer_bound_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/consumer_bound_call.rs):
  the consumer trait used as a bound, `fn greet_twice<Context: CanGreet>(…)` called with a `Person`
  that lacks the `name` field; the `.rust.stderr` is the `E0277` on the call, and the `.cgp.stderr`
  the `[CGP-E001]` block whose tree starts at `CanGreet`. Its sibling
  [`raise_error_unwired_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/raise_error_unwired_call.rs)
  bounds a function on `CanRaiseError<String>` and calls it as `fail::<App>()` on a context with no
  error raiser wired, which ends at the missing `ErrorRaiserComponent` wiring and its `help`.
- [`hidden/unsatisfied-dependency/hand_delegate_without_is_provider.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/hand_delegate_without_is_provider.rs):
  `App` wired by a hand-written `impl DelegateComponent<GreeterComponent> for App` and called; the
  `.rust.stderr` names the unmet `App: IsProviderFor<GreeterComponent, App>` and points into `cgp`,
  and the `.cgp.stderr` leads with the `[CGP-E128]` cause and its `help`.
- [`hidden/unsatisfied-dependency/auto_dispatch_missing_variant_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/auto_dispatch_missing_variant_impl.rs):
  the same hidden `E0599` reached through
  [`#[cgp_auto_dispatch]`](../../reference/macros/cgp_auto_dispatch.md): one of an enum's two
  payloads lacks the dispatch trait, so the generated matcher's `Computer` bound fails where the
  enum's method is called. The `.rust.stderr` names that matcher bound but never the payload,
  `Square`, that lacks the impl; the `.cgp.stderr` reads the enum off the variant constructor at the
  call and leads with ``[CGP-E003] the trait bound `Square: HasArea` is not satisfied`` over the
  matcher chain.

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
