# Check-trait failure (surfaced)

A check forces an unsatisfied impl-side dependency through `IsProviderFor`, so the compiler names
the real missing bound (`E0277`) at the wiring site, the surfaced counterpart of the
[hidden unsatisfied dependency](../hidden/unsatisfied-dependency.md), produced from the very same
mistake.

## What triggers it

This class arises from exactly the mistake behind the
[hidden class](../hidden/unsatisfied-dependency.md): a provider wired onto a context that cannot
meet the provider's impl-side dependency, but exercised through a
[`check_components!`](../../reference/macros/check_components.md) assertion (or the fused
`delegate_and_check_components!`) instead of a direct method call. The check is what changes the
outcome: it asserts `CanUseComponent` for each listed component, and that assertion requires
`IsProviderFor` as a *direct* bound, which forces the compiler to evaluate the provider's `where`
clause rather than suppressing it.

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
    pub age: u8, // no `name` field
}

delegate_components! {
    Person {
        GreeterComponent: GreetHello,
    }
}

// Forces the failure here, at the wiring, instead of at a later call site.
check_components! {
    Person {
        GreeterComponent,
    }
}
```

A `check_components!` is the canonical way to force this diagnostic, but it is not the only one: any
*direct* obligation on a trait bound produces the same shape. A
[`#[use_type]`](../../reference/attributes/use_type.md) foreign import
(`HasScalarType.Scalar in Types`) puts the trait bound `Types: HasScalarType` (grounded to
`<Self as HasTypes>::Types: HasScalarType` for a nested import) onto the *generated trait itself*,
so asserting or using that trait for a context whose supplied type does not implement the trait
surfaces the identical `E0277` with a trait leaf, without any `check_components!`. Here the
`required for …` chain runs through the trait's own `where` bound
(`required by a bound in CanCalculateArea` / `GetScalar`) rather than through `CanUseComponent`, but
the leaf, the `DelegateComponent`/`IsProviderFor` `help:`, and the position of the cause are the
same.

## The raw diagnostic

This section describes what plain `cargo check` prints, the fallback when `cargo-cgp` is not on
hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers the readable form. This
is a **surfaced** class: the compiler prints an `E0277` that names the concrete missing bound,
unlike the hidden class that omits it. The primary error reports that
`Person: CanUseComponent<GreeterComponent>` is not satisfied, and its caret lands on the
`GreeterComponent` entry *inside the `check_components!` block*, not on the `Person` context type,
because the check re-spans the shared context token onto each listed component in turn. Immediately
below, a `help:` note gives the actual unmet leaf bound: that `HasField<Symbol!("name")>` is not
implemented for `Person`, "but trait `HasField<Symbol!("age")>` is implemented for it." That second
half is a useful landmark: the compiler is pointing at the *nearest existing* field impl, which
tells you the context has a field, just not the one the provider expects.

Below the `help:` note, a `required for …` chain traces the dependency path outward from the leaf:
`Person` to implement `HasName`, then `GreetHello` to implement
`IsProviderFor<GreeterComponent, Person>`, then `Person` to implement
`CanUseComponent<GreeterComponent>`, and finally the bound in the generated `__CheckPerson` trait
that the `check_components!` block emitted. The chain is the scaffolding; the leaf in the `help:`
note is the cause.

What makes the cause visible is that the check produces a *direct* trait obligation, and this is
where the class differs mechanically from its hidden twin. A `check_components!` asserts
`Person: CanUseComponent<GreeterComponent>` as a bound on the generated `__CheckPerson` trait, so
the solver must prove that bound outright; and proving it means discharging the whole `where`-clause
chain down to the leaf and reporting the first bound that cannot be met. The `required for …` notes
are simply `rustc`'s ordinary `E0277` obligation-tracing output for that proof. It is exactly the
path the [hidden class](../hidden/unsatisfied-dependency.md) never takes: a method call lets the
solver abandon an inapplicable blanket impl at the top instead of proving a direct bound, so it
never descends to the leaf. [`IsProviderFor`](../../reference/traits/is_provider_for.md) is the
supertrait that carries the provider's own `where` clause into this chain, which is why the leaf is
named here and suppressed there. The `help:` note's "but trait `HasField<Symbol!("age")>` is
implemented for it" is a second piece of standard machinery: `rustc`'s "a similar impl exists" hint,
pointing at the nearest impl of the same trait to show the context has *a* field, just not the
expected one.

## Where the root cause is

The root cause is **present**, and it is near the top, in the compiler's `help:` note, not at the
end of the output. This is the opposite of what a reader might expect from a long note chain: the
concrete unmet bound (`HasField<Symbol!("name")>`) is stated early, and the `required for …` notes
that follow build *outward* from it toward the check trait, rather than drilling down to it. The
caret's position is the other half of the value: it sits on the wiring entry the user controls, so
the error points at the fix site rather than at a distant call. When many providers depend
transitively on one leaf, the output multiplies into a [verbose cascade](verbose-cascade.md), and
the position guidance shifts to *which block* carries the actionable cause; for a single checked
component it is simply the `help:` note.

## When the derive is missing entirely

A distinct sub-case of this class is worth recognizing because its fix differs and its diagnostic
drops the usual landmark: the mistake is not a missing *field* but a missing `#[derive(HasField)]`
on the context altogether. When the struct has the field the getter names but no derive, it has *no*
`HasField` impls at all, so the getter trait is still unsatisfiable and the check still fails with
the same `CanUseComponent` / `IsProviderFor` / `HasField` shape. The tell is what is *absent*: the
`help:` note names the missing `HasField<Symbol!("name")>` and points at the `struct` definition,
but there is **no** "but trait `HasField<…>` is implemented for it" line, because the context
implements the trait for no field at all. The near-impl hint that a single missing field always
produces cannot appear when every field is missing.

Read the absence as its own signal: a checked context that implements `HasField` for nothing behind
a `#[derive(HasField)]`-shaped requirement has most likely forgotten the derive, and the fix is to
add `#[derive(HasField)]` to the struct, not to add fields one at a time. A tool handling this class
should special-case it: zero `HasField` impls plus an unmet `HasField` leaf means the derive, and
the headline should say so rather than sending the user after a single field.

## When the dependency is an equality-pinned abstract type

A second sub-case is worth recognizing because its diagnostic is an `E0271` rather than an `E0277`,
and because the wiring it points at is a *type* choice rather than a field or a provider. An
impl-side dependency can pin an [abstract type](../../concepts/abstract-types.md) to a concrete one
(`#[use_type(HasErrorType.{Error = AppError})]` on a provider, which emits
`Self: HasErrorType<Error = AppError>`) while the context binds that same abstract type elsewhere,
by wiring its component to `UseType<T>` or by implementing the trait directly. When the two
disagree, the *trait* half of the bound still holds (the context genuinely implements
`HasErrorType`) and only the associated-type projection fails, so the compiler reports a type
mismatch rather than an unimplemented trait.

The tell is the headline shape, which the backing fixture (a `Rectangle` wiring `HasScalarType` to
`UseType<u32>` under a provider that pins it to `f64`) prints as
`` type mismatch resolving `<Rectangle as HasScalarType>::Scalar == f64` ``, followed by an
`expected this to be …` note whose caret lands on the `#[cgp_type]` attribute that *defined* the
abstract type, nowhere near either side of the disagreement. Two things make this harder to read
than the field cases above. The type the context actually supplies is nowhere in the message: rustc
names only what was required, so a reader must find the wiring themselves to learn what it was
required *against*. And because one abstract type is shared by everything in the context that
touches it, a single wrong binding surfaces at every consumer that raises through it, multiplying
into a [verbose cascade](verbose-cascade.md). The fix is to reconcile the two: bind the component to
the type the provider requires, or relax the provider to accept the one the context supplies.

## When the field's required type comes from the wiring

A third sub-case sits between the two above and is worth separating because the two things that
disagree are both the context's own decisions. A provider can read a field whose type is expressed
through an [abstract type](../../concepts/abstract-types.md) it imports
(`#[implicit] database: &Pool<Db>` under `#[use_type(HasDbType.Db)]`) so the field bound the macro
emits is not `HasField<…, Value = Pool<Postgres>>` but `HasField<…, Value = Pool<Self::Db>>`, a
requirement that projects through whatever the context wires for `Db`. A context that wires `Db` to
one type while declaring a field of another therefore contradicts *itself*, and the failure is an
`E0271` on the `HasField` projection exactly as the concrete-type case is.

The tell that distinguishes it from an ordinary mistyped field is what the raw diagnostic omits.
Because rustc *normalizes* the required type before printing it, the headline reads
`` type mismatch resolving `<App as HasField<Symbol<8, Chars<..>>>>::Value == Pool<Postgres>` ``,
naming the wired type as though the provider had asked for it literally, with nothing to indicate
the requirement came from an abstract type at all. A reader who checks the provider will find no
mention of `Postgres` in it, and the field name is mangled to a `Symbol<8, Chars<..>>` list in the
same line, so neither half of the disagreement is stated in terms the author would recognize. The
`expected this to be …` note's caret does land on the field declaration, which is one of the two
places to change.

This is also the sub-case that shows what naming a type buys over inferring it. Had the provider
taken the engine as an `#[impl_generics]` parameter inferred from the field's own type, the two
could not have disagreed (there would have been one type, not two) so this diagnostic exists only
because the pairing became a stated claim, and a stated claim is one a check can verify. The fix is
to reconcile them: wire `Db` to the engine the field holds, or change the field to the engine the
wiring names.

## When a check names no parameters

A fourth sub-case fails although nothing is missing: the check asks the wrong question. A component
whose consumer trait takes type parameters (`CanCalculateArea<Shape>`) is checked at the parameters
its entry names, and an entry that names none, in
[`check_components!`](../../reference/macros/check_components.md) or
[`delegate_and_check_components!`](../../reference/macros/delegate_and_check_components.md), is
checked at the **unit parameters** `()`. A provider written for particular parameters does not serve
`()`, so the check fails even though the context uses the component correctly at the parameters it
actually needs:

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea<Shape> {
    fn area(&self, shape: &Shape) -> f64;
}

pub struct Rectangle {
    pub width: f64,
    pub height: f64,
}

#[cgp_impl(new RectangleArea)]
impl AreaCalculator<Rectangle> {
    fn area(&self, shape: &Rectangle) -> f64 {
        shape.width * shape.height
    }
}

pub struct App;

delegate_and_check_components! {
    App {
        AreaCalculatorComponent: RectangleArea, // checked at `()`, not at `Rectangle`
    }
}
```

The raw output reads like a broken provider: an `E0277`
`` the trait bound `RectangleArea: IsProviderFor<AreaCalculatorComponent, App>` is not satisfied ``,
its caret on the entry. The only clue is the near-impl hint, which says the trait is implemented for
`IsProviderFor<AreaCalculatorComponent, App, Rectangle>` but not for `()` ("expected `Rectangle`,
found `()`"). A key whose marker carries the trait's own parameter
(`<I> FooKeyComponent<I>: AnyFoo`) fails the same way, with no near-impl hint at all and a `help:`
that splices a `where` clause into the entry, which does not compile. The fix is to name the
parameters: `#[check_params(Rectangle)]` on a `delegate_and_check_components!` entry,
`AreaCalculatorComponent: Rectangle` in `check_components!`, and `#[check_params(I)]` for the
generic key.

## When the provider takes other arguments

A provider can fail a check although it is a provider of the component: it implements the provider
trait, but not for the arguments the wiring gives it. A provider written for one context and wired
on another is the plain case, since `#[cgp_impl(new GreetPerson)] impl Greeter for Person`
implements `Greeter` for the context `Person` alone:

```rust
#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}

pub struct Person;
pub struct Robot;

#[cgp_impl(new GreetPerson)]
impl Greeter for Person {
    fn greet(&self) {}
}

delegate_components! {
    Robot {
        GreeterComponent: GreetPerson, // a provider for `Person`, not `Robot`
    }
}

check_components! {
    Robot {
        GreeterComponent,
    }
}
```

A component argument can differ the same way. A
[handler pipeline](../../reference/providers/handler_combinators.md) feeds each stage the output of
the stage before it, so a stage that takes `u64` after one that returns `String` is asked for
`Computer` with the input `String`, which its impl does not provide.

The raw output is an `E0277` on the provider's `IsProviderFor` bound,
`` the trait bound `GreetPerson: IsProviderFor<GreeterComponent, Robot>` is not satisfied ``, its
caret on the entry. The cause sits in the near-impl hint below it, which names the
`IsProviderFor<GreeterComponent, Person, ()>` the provider does implement and adds
"for that trait implementation, expected `Person`, found `Robot`"; for a pipeline stage the hint
reads "expected `u64`, found `String`". The fix is a provider for these arguments, or other
arguments for this provider: wire a provider written for `Robot`, or make the stage before it
return what the stage takes.

## How cargo-cgp presents it

`cargo-cgp` recognizes this class and leads with the cause. It keeps the `E0277` code but rewrites
the headline to state the cause, `` [CGP-E001] missing field `name` on `Person` ``, and replaces the
`required for …` scaffolding with a single `root cause:` note over a compact dependency tree:
`[CGP-E101]` consumer-trait-impl hop → `[CGP-E102]` provider-trait-impl hop → the leaf. The leaf is
`` [CGP-E110] missing field `name` on `Person` `` for a genuinely absent field, or `[CGP-E111]` for
the [derive-missing variant](#when-the-derive-is-missing-entirely), which coalesces every underived
field on the struct into one "add `#[derive(HasField)]`" cause rather than listing them singly. The
`#[use_type]` foreign-import form bottoms out on `[CGP-E113]` (the context supplies no wiring for
the trait). The `Symbol!("name")` list is resugared and the
`CanUseComponent`/`IsProviderFor`/`__Check…` frames are dropped, so what remains is the field to fix
and the wiring entry it hangs from. A `help` after the note names the fix,
`` add the field `name: String` to `Person` `` (with the type the provider requires), when the struct
derives `HasField` for its other fields, or `` add `#[derive(HasField)]` to `Person` `` for the
derive-missing variant. The codes are defined in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md).

A check on a generic context, `<T> App<T>`, is the exception: the resolver declines it, so rustc's
headline stays over the renamed notes and the `missing field` help
([`generic_check_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_check_context.rs)).
Checking or calling one instantiation resolves as usual.

The headline code follows the trait the failing entry or call names, and the cause and its tree read
the same under each. A `#[check_providers(...)]` entry asserts a provider's trait directly, so its
block is `[CGP-E002]` and its tree starts at that provider
(`` [CGP-E002] missing field `name` on `App` ``,
[`check_providers_unwired_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/check_providers_unwired_provider.rs)),
and one entry over several failing components gives one block per component
([`check_providers_two_components`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/check_providers_two_components.rs)).
A trait that is not a component, a hand-written wrapper over a consumer trait or a `#[cgp_fn]`
blanket trait, fails under `[CGP-E003]`, its tree starting at that trait
([`cgp_fn_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/cgp_fn_missing_field.rs),
[`foreign_wrapper_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/foreign_wrapper_chain.rs)).

The [wiring-derived field type](#when-the-fields-required-type-comes-from-the-wiring) takes the same
`[CGP-E004]`/`[CGP-E112]` shape as a concrete mismatch, with the field name resugared and the
required type given in **both** forms:
`` field `database` on `App` has type `Pool<Sqlite>`, but `Pool<<App as HasDbType>::Db>` (`Pool<Postgres>`) is required ``.
The projection comes first because it names the wiring the requirement flows from, which is where
the fix goes; the reduced type follows in parentheses because it is what the reader compares against
the field. This is the one sub-case where each output would otherwise carry a fact the other lacks:
rustc normalizes and so states `Pool<Postgres>` without saying where it came from, while the
projection alone says where without saying what, so both are printed, and a requirement that is
already concrete normalizes to itself and gets no parenthetical.

The [equality-pinned abstract type](#when-the-dependency-is-an-equality-pinned-abstract-type) is
reshaped the same way into its own class, `[CGP-E005]`, and carries the required type in **both**
forms on the same rule as the field face: a pin whose right-hand side projects through *another*
abstract type (`{Transaction = Tx<Db>}`) requires `Tx<<App as HasDbType>::Db>`, so the message names
that and appends `(Tx<Postgres>)`. The one place the two forms part company is the `help`, which
uses the **reduced** type alone: it prescribes an edit the reader types, and `UseType<Tx<Postgres>>`
is a wiring entry where `UseType<Tx<<App as HasDbType>::Db>>` would restate the requirement and
leave them to reduce it. For the backing fixture the headline reads
`` abstract type `Scalar` of `HasScalarType` on `Rectangle` is `u32`, but `f64` is required ``,
over a `[CGP-E116]` leaf. Both halves of the disagreement are named: the required type read off the
failing projection, the supplied one by normalizing it, so a `UseType<T>` wiring and a direct impl
are read alike, and a `help` names the wiring entry to change
(`` wire `ScalarTypeProviderComponent` to `UseType<f64>` ``), recovered from the trait rather than
guessed. Because one abstract type is shared, the cascade this class produces is also coalesced:
every consumer that fails through it is listed in one block over a single root-cause tree.

A [check that names no parameters](#when-a-check-names-no-parameters) is reported as what it is,
with no tree:
``[CGP-E060] the check of `AreaCalculatorComponent` on `App` names no parameters, so it checks the component at the unit parameters `()` ``,
its caret on the entry and rustc's notes and `where` suggestion dropped, and a `help` naming the
parameters to check, written for the macro the entry is in:
``check it at the parameters its provider implements: `#[check_params(Rectangle)]` `` (or
`` `AreaCalculatorComponent: Rectangle` `` in `check_components!`). The parameters are the ones a
provider of the component implements for the context, kept only where the context passes the check;
when none qualifies, the error keeps its ordinary reshaping.

A [provider that takes other arguments](#when-the-provider-takes-other-arguments) bottoms out on the
`[CGP-E127]` leaf, which names the one argument the provider's impls do not accept and the arguments
they take there: `` [CGP-E001] `GreetPerson` implements `Greeter` only for `Person`, not `Robot` ``
for the context, and
`` [CGP-E001] `Double` implements `Computer` only with `Input = u64`, not `Input = String` `` for a
component parameter, named as the provider trait names it. It carries no `help`, since only the
reader knows whether the wiring or the provider should change.

## Resolving it

The fix is what the diagnostic already points to: satisfy the named leaf bound. Add the `name` field
to `Person`, or wire the getter component to the existing field, so `Person` implements `HasName`
and `GreetHello` becomes a valid provider for the component. Because the check surfaced both the
concrete bound *and* the wiring entry, no further tracing is usually needed, which is exactly why
the standard remedy for a [hidden](../hidden/unsatisfied-dependency.md) failure is to add a check
and read this class instead.

## Notes for tooling

This class is the *target* `cargo-cgp` normalizes toward, and it already handles it fully (above).
It is also where the hidden class lands once promoted: synthesizing a `check_components!` for a
[hidden](../hidden/unsatisfied-dependency.md) failure produces exactly this diagnostic, so both
reduce to the same `[CGP-E001]` headline and `root cause:` tree.

## Backing fixtures

- [`checks/check-trait-failure/fields/missing_dependency.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/missing_dependency.rs):
  the surfaced case for `GreetHello`'s unmet `Self: HasName`; its `.rust.stderr` pins the raw
  `help:` note naming `HasField<Symbol!("name")>` and the caret on `GreeterComponent`, and its
  `.cgp.stderr` the `[CGP-E001]`/`[CGP-E110]` reshaping. Its use-site counterpart,
  [`hidden/unsatisfied-dependency/missing_dependency_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/missing_dependency_call.rs),
  reaches the same mistake by a method call: the [hidden](../hidden/unsatisfied-dependency.md)
  `E0599` in the raw output, which `cargo-cgp`'s next-gen solver recovers to the same headline.
- [`checks/check-trait-failure/use-type/use_type_foreign_unsatisfied.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-type/use_type_foreign_unsatisfied.rs):
  the trait bound reached through a `#[use_type]` foreign import instead of a check: naming a
  component for a `Types` that does not implement the imported `HasScalarType` surfaces `E0277`,
  pinning that the foreign bound is *enforced on the generated trait* rather than silently dropped.
- [`checks/check-trait-failure/use-type/use_type_nested_unsatisfied.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-type/use_type_nested_unsatisfied.rs):
  the same through a *nested* two-hop import, so the grounded bound
  `<Self as HasTypes>::Types: HasScalarType` is the one enforced, confirming the
  transitively-grounded foreign bound is checked at depth.
- [`checks/check-trait-failure/field-types/abstract_field_type_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/field-types/abstract_field_type_mismatch.rs):
  the wiring-derived field type: an `App`
  wiring `Db` to `Postgres` while declaring a `Pool<Sqlite>` field, under a provider reading
  `&Pool<Db>`. Its `.rust.stderr` pins the normalized `Pool<Postgres>` requirement and the mangled
  `Symbol<8, Chars<..>>` field name, and its `.cgp.stderr` the `[CGP-E004]`/`[CGP-E112]` reshaping
  with the required type given as `Pool<<App as HasDbType>::Db>` followed by `(Pool<Postgres>)`, the
  projection that names the wiring plus the type it resolves to. Its concrete-required-type sibling
  is
  [`field_type_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/field-types/field_type_mismatch.rs).
- [`checks/check-trait-failure/types/abstract_type_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/types/abstract_type_mismatch.rs):
  the equality-pinned abstract type: a
  context wiring `HasScalarType` to `UseType<u32>` under a provider that pins it to `f64`. Its
  `.rust.stderr` pins the raw `E0271` with its caret on the `#[cgp_type]` attribute and no mention
  of `u32`, and its `.cgp.stderr` the `[CGP-E005]`/`[CGP-E116]` reshaping with the `UseType<f64>`
  help.
- [`checks/check-trait-failure/fields/missing_has_field_derive.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/missing_has_field_derive.rs):
  the derive-missing variant: a `Person` with the `name`
  field but no `#[derive(HasField)]`, so the raw output drops the "but trait `HasField<…>` is
  implemented" landmark (the signal the whole derive is missing), and `cargo-cgp` coalesces it to
  one `[CGP-E111]` cause. Related field-derive fixtures
  ([`base_area_2`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_2.rs),
  [`empty_field_struct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/empty_field_struct.rs),
  [`underived_and_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/underived_and_missing_field.rs))
  pin the coalescing and the mixed missing-plus-underived case.
- [`checks/check-trait-failure/checks/generic_component_unit_params.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/generic_component_unit_params.rs):
  a check that names no parameters in
  `delegate_and_check_components!`; its `.rust.stderr` pins the provider-shaped `E0277` with the
  "expected `Rectangle`, found `()`" hint, and its `.cgp.stderr` the `[CGP-E060]` block whose help
  names `#[check_params(Rectangle)]`;
  [`qualified_delegate_and_check_unit_params`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/qualified_delegate_and_check_unit_params.rs)
  gives the same help when the table is called as `cgp::prelude::delegate_and_check_components!`,
  and
  [`unit_params_with_unwired_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/unit_params_with_unwired_provider.rs)
  names only `Rectangle` when a provider the context does not wire implements the component for
  `Circle`.
- [`checks/check-trait-failure/providers/generic_check_without_params.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/generic_check_without_params.rs):
  the same in `check_components!`, whose help names `AreaCalculatorComponent: Square`.
- [`checks/check-trait-failure/providers/provider_for_other_context.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/provider_for_other_context.rs):
  a provider that takes other arguments, written for
  `Person` and wired on `Robot`; its `.rust.stderr` pins the near-impl hint "expected `Person`, found
  `Robot`", and its `.cgp.stderr` the `[CGP-E127]` leaf naming the context. The component-argument
  forms are
  [`pipe_handlers_stage_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/pipe_handlers_stage_mismatch.rs)
  (a stage taking `u64` after one returning `String`),
  [`pipe_monadic_non_result`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/pipe_monadic_non_result.rs)
  (a monadic pipeline's `BindErr` given a stage's `u64` where it takes a `Result`), and
  [`promote_ref_owned_input`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/promote_ref_owned_input.rs)
  (`PromoteRef` calling a provider that takes its input by value with a reference, an `E0271`).
- [`checks/check-trait-failure/checks/check_trait_named_as_wrapper.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/check_trait_named_as_wrapper.rs):
  a generic key, `<I> FooKeyComponent<I>: AnyFoo`, checked at unit parameters; its `.rust.stderr`
  pins the spliced `where` suggestion, and its `.cgp.stderr` the `[CGP-E060]` block naming
  `#[check_params(I)]`.
- [`checks/check-trait-failure/checks/aggregate_delegate_and_check.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/aggregate_delegate_and_check.rs):
  `delegate_and_check_components!` on a `new` provider bundle.
- [`checks/check-trait-failure/constrained-key/constrained_delegate_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/constrained-key/constrained_delegate_key.rs):
  a component delegation that fails because the `DelegateComponent` impl carries a **constrained key** whose `where`-clause is unsatisfied, the shape `PipeHandlers<Providers>` produces.
- [`checks/check-trait-failure/constrained-key/constrained_delegate_key_empty_sum.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/constrained-key/constrained_delegate_key_empty_sum.rs):
  a delegation whose constrained key fails on CGP's empty sum, `Sum![]`.
- [`checks/check-trait-failure/constrained-key/pipe_handlers_empty.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/constrained-key/pipe_handlers_empty.rs):
  the constrained-key delegation failure in its canonical core-CGP form: wiring a component to `PipeHandlers<Product![]>`, an *empty* pipeline.
- [`checks/check-trait-failure/duplication/coalesced_underived_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/coalesced_underived_field.rs):
  one underived field named once, however many coalesced consumers reach it.
- [`checks/check-trait-failure/duplication/cross_site_dedup.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/cross_site_dedup.rs):
  one wiring mistake reported once.
- [`checks/check-trait-failure/duplication/overlapping_cause_sets.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/overlapping_cause_sets.rs):
  failures whose root-cause *sets* overlap without being equal, coalesced into one block.
- [`checks/check-trait-failure/duplication/traced_send_wrapper.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/traced_send_wrapper.rs):
  a raw error that never names a CGP construct, traced back to the one CGP cause.
- [`checks/check-trait-failure/errors/glob_imported_error_route.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/errors/glob_imported_error_route.rs):
  an `open` error table missing the route for `std::io::Error`, in a crate that glob-imports its own `Error`.
- [`checks/check-trait-failure/errors/glob_imported_error_under_crate_named_module.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/errors/glob_imported_error_under_crate_named_module.rs):
  an `open` error table missing the route for a dependency's error, in a crate that glob-imports an error of the same name from a module named after that dependency.
- [`checks/check-trait-failure/errors/open_route_stripped_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/errors/open_route_stripped_path.rs):
  an `open` error table missing the route for `std::io::Error`, in a crate with its own `Error`.
- [`checks/check-trait-failure/errors/raiser_without_error_type.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/errors/raiser_without_error_type.rs):
  an error raiser wired on a context with no error type, checked for `io::Error`.
- [`checks/check-trait-failure/errors/stripped_error_path.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/errors/stripped_error_path.rs):
  an error raiser that pins the abstract error to a concrete type named `Error` from another module.
- [`checks/check-trait-failure/field-types/field_type_mismatch_1.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/field-types/field_type_mismatch_1.rs):
  a field whose name matches but whose type does not, read *directly* by a provider, the shorter-chain counterpart of `field_type_mismatch`.
- [`checks/check-trait-failure/field-types/field_type_mismatch_modules.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/field-types/field_type_mismatch_modules.rs):
  two `Rectangle` contexts in different modules, whose `height` fields have different wrong types, each reported against its own struct.
- [`checks/check-trait-failure/fields/abstract_field_type_missing.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/abstract_field_type_missing.rs):
  a provider reads a field whose required type goes through an abstract type, on a context that lacks the field.
- [`checks/check-trait-failure/fields/base_area_1.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_1.rs):
  a missing field whose name rustc encodes as a nested `Symbol`, in the two-line "similar impl" hint.
- [`checks/check-trait-failure/fields/base_area_1_1.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_1_1.rs):
  a missing field read *directly* by a provider, the shorter-chain counterpart of `base_area_1`.
- [`checks/check-trait-failure/fields/field_tag_typo_derive_hint.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/field_tag_typo_derive_hint.rs):
  a `HasField` bound whose tag misspells a field the struct derives.
- [`checks/check-trait-failure/fields/field_via_deref.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/field_via_deref.rs):
  a field the context reaches through `Deref`, whose `Deref` target does not derive `HasField`.
- [`checks/check-trait-failure/fields/getter_use_field_typo.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/getter_use_field_typo.rs):
  `UseField<Symbol!("frist_name")>` for a field named `first_name`.
- [`checks/check-trait-failure/fields/many_missing_fields.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/many_missing_fields.rs):
  a provider reading six fields the context lacks, through `#[implicit]` arguments.
- [`checks/check-trait-failure/fields/parallel_branches.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/parallel_branches.rs):
  a provider with two independent unmet field dependencies, rendered as two parallel branches of the dependency tree.
- [`checks/check-trait-failure/fields/symbol_tag_not_a_tuple_position.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/symbol_tag_not_a_tuple_position.rs):
  `Symbol!` tags on tuple structs that spell no position of the struct.
- [`checks/check-trait-failure/fields/symbol_tag_on_tuple_struct.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/symbol_tag_on_tuple_struct.rs):
  reading a tuple-struct field with `Symbol!("0")` where `Index<0>` belongs.
- [`checks/check-trait-failure/fields/symbol_tag_on_tuple_struct_check.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/symbol_tag_on_tuple_struct_check.rs):
  a provider that requires a tuple field by `Symbol!("0")`, checked on a tuple struct.
- [`checks/check-trait-failure/fields/tuple_struct_named_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/tuple_struct_named_field.rs):
  a tuple-struct context reached through an implicit argument that reads a named field.
- [`checks/check-trait-failure/generic/generic_area.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_area.rs):
  the wiring-note and header rewrites over a component that carries a generic parameter, so `CanUseComponent`/`IsProviderFor` gain an extra type argument.
- [`checks/check-trait-failure/generic/generic_area_multi.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_area_multi.rs):
  the wiring-note and header rewrites over a component with *three* generic parameters, so the parameters reach `CanUseComponent`/`IsProviderFor` grouped in a tuple.
- [`checks/check-trait-failure/generic/generic_check_context.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_check_context.rs):
  a check that carries a generic parameter, which the resolver declines.
- [`checks/check-trait-failure/generic/generic_context_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_context_call.rs):
  a consumer called on one instantiation of a generic context.
- [`checks/check-trait-failure/generic/generic_wrapper_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_wrapper_impl.rs):
  a wrapper impl generic over the context's parameter, which the resolver declines.
- [`checks/check-trait-failure/generic/lifetime_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/lifetime_component.rs):
  a component carrying a *lifetime* parameter, failing its check on a missing field.
- [`checks/check-trait-failure/generic/tuple_param_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/tuple_param_component.rs):
  a component whose single generic parameter is instantiated with a *tuple* type.
- [`checks/check-trait-failure/handlers/cgp_computer_no_error_type_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/cgp_computer_no_error_type_call.rs):
  `try_compute` on a context wiring a `#[cgp_computer]` provider and no error type.
- [`checks/check-trait-failure/handlers/matcher_wired_to_handler.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/matcher_wired_to_handler.rs):
  a value matcher, `MatchWithValueHandlers`, wired as the context's `Handler`.
- [`checks/check-trait-failure/handlers/promote_computer_handwritten_handler.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/promote_computer_handwritten_handler.rs):
  `PromoteComputer<Double>` wired as a handler for a hand-written `Computer` provider.
- [`checks/check-trait-failure/handlers/question_mark_after_failed_handle.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/question_mark_after_failed_handle.rs):
  a `BuildAndMergeOutputs` builder whose second output carries a field the target lacks, called with `?` and no check.
- [`checks/check-trait-failure/handlers/value_matcher_on_struct.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/value_matcher_on_struct.rs):
  `MatchWithValueHandlers` applied to a struct.
- [`checks/check-trait-failure/missing-wiring/basic_missing_wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/basic_missing_wiring.rs):
  a *transitive* missing wiring.
- [`checks/check-trait-failure/missing-wiring/direct_delegation_missing_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/direct_delegation_missing_key.rs):
  a `->` delegation to a table that lacks the key.
- [`checks/check-trait-failure/missing-wiring/direct_delegation_missing_key_unchecked.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/direct_delegation_missing_key_unchecked.rs):
  a `->` delegation to a table that lacks the key, with no check or call that uses it.
- [`checks/check-trait-failure/missing-wiring/direct_missing_wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/direct_missing_wiring.rs):
  the simplest missing wiring: a `check_components!` asserting a component the context does not wire at all.
- [`checks/check-trait-failure/missing-wiring/enum_variant_chain.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/enum_variant_chain.rs):
  a missing wiring reached through a sum spine of *named* variants, whose dependency-tree entries resugar `Either<Field<…>, …, Void>` all the way to the `Enum! { … }` surface form.
- [`checks/check-trait-failure/missing-wiring/enum_variant_shapes_chain.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/enum_variant_shapes_chain.rs):
  a missing wiring reached through a sum of named variants that uses every variant shape, whose dependency-tree entries render each variant in its shortest `Enum!` spelling.
- [`checks/check-trait-failure/missing-wiring/generic_component_forwarding_missing_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/generic_component_forwarding_missing_key.rs):
  a forwarding entry for a component with a type parameter, into a table that lacks the key.
- [`checks/check-trait-failure/missing-wiring/missing_normal_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/missing_normal_bound.rs):
  a checked dependency chain that ends in an ordinary trait bound the context lacks.
- [`checks/check-trait-failure/missing-wiring/open_aggregate_missing_entry.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/open_aggregate_missing_entry.rs):
  a missing entry in an aggregate provider's own `open` table.
- [`checks/check-trait-failure/missing-wiring/parallel_missing_wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/parallel_missing_wiring.rs):
  two independent missing wirings surface as two separate root causes.
- [`checks/check-trait-failure/missing-wiring/record_field_chain.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/record_field_chain.rs):
  a missing wiring reached only *through* the extensible-data record machinery, a record provider that builds each field through the context, over a recursive `Cons`/`Nil` field-list handler.
- [`checks/check-trait-failure/missing-wiring/redirect_distinct_keys.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/redirect_distinct_keys.rs):
  two dependencies dispatched along the same `open` route for distinct, unwired value types, the shape that pins two redirect hops staying distinct nodes across branches.
- [`checks/check-trait-failure/missing-wiring/sum_variant_chain.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/sum_variant_chain.rs):
  a missing wiring reached *through* a type-level sum spine, whose dependency-tree entries resugar `Either<…, Void>` back to `Sum![…]`.
- [`checks/check-trait-failure/missing-wiring/transitive_missing_wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/transitive_missing_wiring.rs):
  a component wired to an aggregate provider that lacks one of the entries it is wired for.
- [`checks/check-trait-failure/missing-wiring/unrelated_error_beside_forwarding_entry.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/unrelated_error_beside_forwarding_entry.rs):
  a plain Rust error beside a forwarding entry whose table lacks the key.
- [`checks/check-trait-failure/providers/field_getter_wired_bare.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/field_getter_wired_bare.rs):
  a hand-written `FieldGetter` wired directly as a component's provider.
- [`checks/check-trait-failure/providers/getter_multi_method_use_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/getter_multi_method_use_field.rs):
  a multi-method `#[cgp_getter]` trait wired to `UseField`.
- [`checks/check-trait-failure/providers/non_provider_wired.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/non_provider_wired.rs):
  a `check_components!` failure whose root cause is a plain type wired where a *provider* was expected: a higher-order provider's inner slot is filled with a struct that does not implement the provider trait at all.
- [`checks/check-trait-failure/providers/provider_for_other_context_and_input.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/provider_for_other_context_and_input.rs):
  a provider written for another context and another input, wired and checked.
- [`checks/check-trait-failure/providers/use_delegate_parameterless_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_delegate_parameterless_component.rs):
  `UseDelegate` wired to a component that takes no parameters.
- [`checks/check-trait-failure/providers/use_delegate_without_derive.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_delegate_without_derive.rs):
  `UseDelegate` wired for a component that lacks `#[derive_delegate]`.
- [`checks/check-trait-failure/providers/use_field_multi_method_missing_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_field_multi_method_missing_field.rs):
  a getter with two methods wired to `UseField` on a context that lacks one of the getter's fields.
- [`checks/check-trait-failure/providers/use_field_on_cgp_type.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_field_on_cgp_type.rs):
  `UseField` wired to a `#[cgp_type]` component.
- [`checks/check-trait-failure/providers/wrong_component_provider_check.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/wrong_component_provider_check.rs):
  a provider of another component wired under the wrong key.
- [`checks/check-trait-failure/resolution/cross_context_node_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/cross_context_node_key.rs):
  a cross-context dependency, one context's wiring depending on a *concrete* other context, the shape that needs the resolution cache's per-context node key.
- [`checks/check-trait-failure/resolution/diamond_shared_trait.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/diamond_shared_trait.rs):
  one shared trait reached from two independent branches of a single dependency tree.
- [`checks/check-trait-failure/resolution/fallback_shape_resugar.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/fallback_shape_resugar.rs):
  a diagnostic the resolver *declines* still gets its field lists resugared to CGP's `Struct!`/`Enum!` shapes by the fallback post-processing chain.
- [`checks/check-trait-failure/resolution/fallback_spine_resugar.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/fallback_spine_resugar.rs):
  a diagnostic the resolver *declines* still gets its type-level spines resugared by the fallback post-processing chain.
- [`checks/check-trait-failure/resolution/foreign_getter_missing_wiring.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/foreign_getter_missing_wiring.rs):
  a getter on a *request* type resolves to the context's missing wiring, not the opaque getter bound.
- [`checks/check-trait-failure/resolution/higher_ranked_descent.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/higher_ranked_descent.rs):
  a wiring failure through a higher-ranked (`for<'a>`) CGP obligation, which the walk descends without a compiler panic.
- [`checks/check-trait-failure/resolution/mixed_rust_error.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/mixed_rust_error.rs):
  a CGP check failure and an ordinary Rust error in the same crate, to confirm the typed resolver replaces only the CGP wiring diagnostic and leaves the plain error untouched.
- [`checks/check-trait-failure/resolution/nested_higher_ranked_descent.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/nested_higher_ranked_descent.rs):
  a wiring failure threading the record field-list machinery through *nested* higher-ranked (`for<'a>`) hops, resolved to its root cause.
- [`checks/check-trait-failure/resolution/projected_impl_argument.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/projected_impl_argument.rs):
  two blanket impls of one trait that differ only in a projected argument, and the walk choosing between them.
- [`checks/check-trait-failure/resolution/same_field_two_contexts.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/same_field_two_contexts.rs):
  two genuinely distinct root causes that happen to *name* the same thing, kept apart.
- [`checks/check-trait-failure/resolution/same_name_components.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/same_name_components.rs):
  two components in different modules that share the marker name `MeasurerComponent` and differ in their consumer and provider traits, told apart by their full paths.
- [`checks/check-trait-failure/resolution/same_name_marker_rename.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/same_name_marker_rename.rs):
  a `#[check_providers]` check whose component shares its marker name with another component.
- [`checks/check-trait-failure/types/abstract_type_mismatch_projected.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/types/abstract_type_mismatch_projected.rs):
  an abstract type a provider pins to a *projection* through another abstract type, which the context binds to something else.
- [`checks/check-trait-failure/types/computer_result_error_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/types/computer_result_error_mismatch.rs):
  a `#[cgp_computer]` function returning `Result<u64, String>`, called through `try_compute` on a context whose abstract error type is `()` rather than `String`.
- [`checks/check-trait-failure/types/has_fields_shape_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/types/has_fields_shape_mismatch.rs):
  a provider bound on the context's whole shape, wired on a context whose field type differs.
- [`checks/check-trait-failure/types/plain_assoc_type_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/types/plain_assoc_type_mismatch.rs):
  the negative counterpart of `abstract_type_mismatch`: the same projection failure on a trait that is **not** a CGP abstract-type component.
- [`checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs):
  a generic consumer failing at a call whose arguments write no types: the resolver declines, and the fallback strips rustc's misleading method advice.
- [`checks/check-trait-failure/use-site/pipeline_unhandled_code.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/pipeline_unhandled_code.rs):
  a pipeline stage that routes back to the context for a `Code` nothing is wired for.
- [`checks/check-trait-failure/verbosity/deep_dispatch_chain.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/verbosity/deep_dispatch_chain.rs):
  a resolved dispatch chain over a DSL-sized program, every construct named in full.
- [`checks/check-trait-failure/missing-wiring/open_key_qualified_argument.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/open_key_qualified_argument.rs):
  an `open` dispatch key whose value type takes a type two modules share a name for.

## Related

- [Unsatisfied dependency (hidden)](../hidden/unsatisfied-dependency.md): the hidden counterpart;
  the two are the two halves of one phenomenon, and promoting the hidden one yields this class.
- [Unsatisfied ordinary trait bound (surfaced)](ordinary-trait-bound.md): the sibling surfaced class
  whose leaf is an ordinary Rust trait (`Eq`, `Clone`) on a concrete type rather than a CGP trait
  like `HasField`; the leaf's kind changes the `help:` note and the position of the cause.
- [Verbose dependency cascade](verbose-cascade.md): this diagnostic multiplied when many providers
  depend transitively on one leaf.
- [`check_components!`](../../reference/macros/check_components.md),
  [`CanUseComponent`](../../reference/traits/can_use_component.md), and
  [`IsProviderFor`](../../reference/traits/is_provider_for.md): the macro and traits this class is
  expressed through.
- [Debugging CGP compile errors](../../guides/debugging.md) and the
  [check-traits concept](../../concepts/check-traits.md): why the check moves the error here and how
  to read it.
