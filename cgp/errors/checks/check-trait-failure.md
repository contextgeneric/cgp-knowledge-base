# Check-trait failure (surfaced)

A check forces an unsatisfied impl-side dependency through `IsProviderFor`, so the compiler names
the real missing bound (`E0277`) at the wiring site, the surfaced counterpart of the
[hidden unsatisfied dependency](../hidden/unsatisfied-dependency.md), produced from the very same
mistake.

## What triggers it

This class arises from the mistake behind the [hidden class](../hidden/unsatisfied-dependency.md): a
provider wired onto a context that cannot meet its impl-side dependency. Here the wiring is exercised
through a [`check_components!`](../../reference/macros/check_components.md) assertion, or the fused
`delegate_and_check_components!`, instead of a method call. The check asserts `CanUseComponent` for
each listed component, which requires `IsProviderFor` as a *direct* bound, so the compiler must
evaluate the provider's `where` clause.

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

Any other direct obligation produces the same shape. A
[`#[use_type]`](../../reference/attributes/use_type.md) foreign import
(`HasScalarType.Scalar in Types`) puts `Types: HasScalarType` onto the generated trait itself, grounded
to `<Self as HasTypes>::Types: HasScalarType` for a nested import. Asserting that trait for a context
whose type lacks the bound surfaces the same `E0277`, with the `required for …` chain running through
the trait's own `where` bound rather than through `CanUseComponent`.

## The raw diagnostic

This section describes plain `cargo check`, the fallback when `cargo-cgp` is not on hand. This is a
**surfaced** class: the compiler prints an `E0277` whose notes name the concrete missing bound.

The primary error reports that `Person: CanUseComponent<GreeterComponent>` is not satisfied, with its
caret on the `GreeterComponent` entry inside the `check_components!` block, since the check re-spans
the context token onto each entry. A `help:` below it gives the leaf, with the field name encoded as a
type-level list:

```text
help: the trait `HasField<Symbol<4, Chars<'n', Chars<'a', Chars<'m', …>>>>>` is not implemented for `Person`
      but trait `HasField<Symbol<3, Chars<'a', Chars<'g', …>>>>` is implemented for it
```

The second line is rustc's "a similar impl exists" hint: the context has a field, but not the one the
provider expects. A `required for …` chain follows, outward from the leaf: `Person` to implement
`HasName`, `GreetHello` to implement `IsProviderFor<GreeterComponent, Person>`, `Person` to implement
`CanUseComponent<GreeterComponent>`, and the bound in the generated `__CheckPerson` trait.

The direct obligation explains why the leaf appears. The solver must prove the bound outright, so it
discharges the whole `where`-clause chain, and [`IsProviderFor`](../../reference/traits/is_provider_for.md)
carries the provider's clause into that chain. A method call instead lets the solver abandon an
inapplicable blanket impl at the top, which is the [hidden class](../hidden/unsatisfied-dependency.md).

## Where the root cause is

The root cause is **present** near the top, in the `help:` note, and the `required for …` notes build
outward from it toward the check. The caret sits on the wiring entry, so the error points at the fix
site. When many providers depend on one leaf, the output multiplies into a
[verbose cascade](verbose-cascade.md).

## When the derive is missing entirely

A context with the field but no `#[derive(HasField)]` fails with the same
`CanUseComponent` / `IsProviderFor` / `HasField` shape, and its tell is an absence. The `help:` names
the missing `HasField<…>` and points at the `struct`, without the "but trait `HasField<…>` is
implemented for it" line, because the context implements the trait for no field. The fix is the
derive, not fields one at a time.

## When the dependency is an equality-pinned abstract type

An impl-side dependency can pin an [abstract type](../../concepts/abstract-types.md) to a concrete one
(`#[use_type(HasErrorType.{Error = AppError})]`, which emits `Self: HasErrorType<Error = AppError>`)
while the context binds it elsewhere, by wiring `UseType<T>` or implementing the trait. When the two
disagree, the trait half of the bound holds and only the projection fails, so the code is `E0271`.

The tell is the headline: `` type mismatch resolving `<Rectangle as HasScalarType>::Scalar == f64` ``,
over an `expected this to be …` note whose caret lands on the `#[cgp_type]` attribute that defined the
abstract type. The type the context supplies appears nowhere in the message, so the reader must find
the wiring. One abstract type is shared by everything that touches it, so one wrong binding surfaces
at every consumer that raises through it. The fix is to bind the component to the required type, or
to relax the provider.

## When the field's required type comes from the wiring

A provider can read a field whose type goes through an
[abstract type](../../concepts/abstract-types.md) it imports (`#[implicit] database: &Pool<Db>` under
`#[use_type(HasDbType.Db)]`), so the bound is `HasField<…, Value = Pool<Self::Db>>`. A context that
wires `Db` to one type and declares a field of another contradicts itself, and the failure is an
`E0271` on the `HasField` projection.

The raw diagnostic hides where the requirement came from, because rustc normalizes the required type:
`` type mismatch resolving `<App as HasField<Symbol<8, Chars<'d', _>>>>::Value == Pool<Postgres>` ``.
The provider never mentions `Postgres`, and the field name is an encoded list. The
`expected this to be …` note's caret lands on the field declaration, one of the two places to change.

An `#[impl_generics]` parameter inferred from the field could not disagree, since there would be one
type, so this diagnostic exists because the pairing became a stated claim a check can verify. The fix
is to wire `Db` to the engine the field holds, or to change the field.

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

`cargo-cgp` keeps the `E0277` code and leads with the cause, `` [CGP-E001] missing field `name` on `Person` ``,
replacing the `required for …` scaffolding with one `root cause:` note over a dependency tree:
`[CGP-E101]` consumer-trait hop, `[CGP-E102]` provider-trait hop, then the leaf. The leaf is
`[CGP-E110]` for an absent field, `[CGP-E111]` for the
[missing derive](#when-the-derive-is-missing-entirely), which merges every underived field of the
struct into one cause, and `[CGP-E113]` for the `#[use_type]` foreign import whose type has no wiring.
A `help` names the fix: `` add the field `name: String` to `Person` `` when the struct derives
`HasField` for its other fields, or `` add `#[derive(HasField)]` to `Person` ``. The
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) defines each code.

A check on a generic context, `<T> App<T>`, is the exception: the resolver declines it, so rustc's
headline stays over the renamed notes and the `missing field` help
([`generic_check_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_check_context.rs)).
Checking or calling one instantiation resolves as usual.

The headline code follows the trait the failing entry or call names. A `#[check_providers(...)]` entry
asserts a provider's trait directly, so its block is `[CGP-E002]` and its tree starts at that provider
([`check_providers_unwired_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/check_providers_unwired_provider.rs)),
and one entry over several failing components gives one block per component
([`check_providers_two_components`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/check_providers_two_components.rs)).
A hand-written wrapper over a consumer trait or a `#[cgp_fn]` blanket trait fails under `[CGP-E003]`
([`cgp_fn_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/cgp_fn_missing_field.rs),
[`foreign_wrapper_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/foreign_wrapper_chain.rs)).

The [wiring-derived field type](#when-the-fields-required-type-comes-from-the-wiring) takes
`[CGP-E004]` over `[CGP-E112]`, with the name resugared and the required type in both forms:
`` field `database` on `App` has type `Pool<Sqlite>`, but `Pool<<App as HasDbType>::Db>` (`Pool<Postgres>`) is required ``.
The projection names the wiring the requirement flows from, and the reader compares the reduced
type with the field.

The [equality-pinned abstract type](#when-the-dependency-is-an-equality-pinned-abstract-type) takes
`[CGP-E005]` over `[CGP-E116]`, naming both sides:
`` abstract type `Scalar` of `HasScalarType` on `Rectangle` is `u32`, but `f64` is required ``. A `help`
names the wiring entry, and writes the reduced type since the reader types it:
`` wire `ScalarTypeProviderComponent` to `UseType<f64>` in the wiring for `Rectangle`, or change the provider to work with `u32` ``.
Every consumer that fails through one abstract type is listed in one block over one tree.

A [check that names no parameters](#when-a-check-names-no-parameters) has no tree:
``[CGP-E060] the check of `AreaCalculatorComponent` on `App` names no parameters, so it checks the component at the unit parameters `()` ``,
its caret on the entry and rustc's notes and `where` suggestion dropped. A `help` names the parameters
for the macro the entry is in:
``check it at the parameters its provider implements: `#[check_params(Rectangle)]` `` (or
`` `AreaCalculatorComponent: Rectangle` `` in `check_components!`). It offers only parameters the
context passes the check at, and with none the error keeps its ordinary reshaping.

A [provider that takes other arguments](#when-the-provider-takes-other-arguments) ends on the
`[CGP-E127]` leaf: `` [CGP-E001] `GreetPerson` implements `Greeter` only for `Person`, not `Robot` ``
for the context, and `` [CGP-E001] `Double` implements `Computer` only with `Input = u64`, not `Input = String` ``
for a component parameter. It carries no `help`, since only the reader knows which side should change.

## Resolving it

Satisfy the named leaf bound: add the `name` field to `Person`, or wire the getter component to an
existing field. The check surfaced both the bound and the wiring entry, so the standard remedy for a
[hidden](../hidden/unsatisfied-dependency.md) failure is to add a check and read this class.

## Backing fixtures

- [`checks/check-trait-failure/fields/missing_dependency.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/missing_dependency.rs):
  the surfaced case for `GreetHello`'s unmet `Self: HasName`. Its use-site counterpart,
  [`hidden/unsatisfied-dependency/missing_dependency_call.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/missing_dependency_call.rs),
  reaches the same headline from the raw `E0599`.
- [`checks/check-trait-failure/use-type/use_type_foreign_unsatisfied.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-type/use_type_foreign_unsatisfied.rs):
  a `#[use_type]` foreign import whose `Types` lacks `HasScalarType`, surfacing `E0277` without a check.
- [`checks/check-trait-failure/use-type/use_type_nested_unsatisfied.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-type/use_type_nested_unsatisfied.rs):
  the same through a nested two-hop import, so the grounded bound is the one enforced.
- [`checks/check-trait-failure/field-types/abstract_field_type_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/field-types/abstract_field_type_mismatch.rs):
  the wiring-derived field type: `Db` wired to `Postgres` over a `Pool<Sqlite>` field. Its concrete
  sibling is
  [`field_type_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/field-types/field_type_mismatch.rs).
- [`checks/check-trait-failure/types/abstract_type_mismatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/types/abstract_type_mismatch.rs):
  the equality-pinned abstract type: `HasScalarType` wired to `UseType<u32>` under a provider pinning `f64`.
- [`checks/check-trait-failure/fields/missing_has_field_derive.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/missing_has_field_derive.rs):
  the missing derive, with no "but trait `HasField<…>` is implemented" line. Related fixtures
  ([`base_area_2`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_2.rs),
  [`empty_field_struct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/empty_field_struct.rs),
  [`underived_and_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/underived_and_missing_field.rs))
  pin the merging and the mixed case.
- [`checks/check-trait-failure/checks/generic_component_unit_params.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/generic_component_unit_params.rs):
  a check naming no parameters in `delegate_and_check_components!`;
  [`qualified_delegate_and_check_unit_params`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/qualified_delegate_and_check_unit_params.rs)
  calls the table by its full path, and
  [`unit_params_with_unwired_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/unit_params_with_unwired_provider.rs)
  names only `Rectangle` when an unwired provider serves `Circle`.
- [`checks/check-trait-failure/providers/generic_check_without_params.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/generic_check_without_params.rs):
  the same in `check_components!`, whose help names `AreaCalculatorComponent: Square`.
- [`checks/check-trait-failure/providers/provider_for_other_context.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/provider_for_other_context.rs):
  a provider written for `Person` and wired on `Robot`. The component-argument forms are
  [`pipe_handlers_stage_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/pipe_handlers_stage_mismatch.rs)
  (a stage taking `u64` after one returning `String`),
  [`pipe_monadic_non_result`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/pipe_monadic_non_result.rs)
  (`BindErr` given a `u64` where it takes a `Result`), and
  [`promote_ref_owned_input`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/handlers/promote_ref_owned_input.rs)
  (`PromoteRef` passing a reference to a provider that takes its input by value, an `E0271`).
- [`checks/check-trait-failure/checks/check_trait_named_as_wrapper.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/check_trait_named_as_wrapper.rs):
  a generic key, `<I> FooKeyComponent<I>: AnyFoo`, checked at unit parameters, whose raw `help:` splices
  a `where` clause into the entry.
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
- [`checks/check-trait-failure/providers/non_provider_wired_lifetime_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/non_provider_wired_lifetime_component.rs):
  a plain type wired as the provider of a component with a lifetime parameter, reached by a call;
  `[CGP-E001]` with a `[CGP-E115]` cause.
- [`checks/check-trait-failure/providers/provider_for_other_context_and_input.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/provider_for_other_context_and_input.rs):
  a provider written for another context and another input, wired and checked.
- [`checks/check-trait-failure/providers/use_delegate_parameterless_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_delegate_parameterless_component.rs):
  `UseDelegate` wired to a component that takes no parameters.
- [`checks/check-trait-failure/providers/use_delegate_without_derive.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_delegate_without_derive.rs):
  `UseDelegate` wired for a component that lacks `#[derive_delegate]`.
- [`checks/check-trait-failure/providers/use_delegate_without_derive_lifetime_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/use_delegate_without_derive_lifetime_component.rs):
  the same for a component with a lifetime parameter, whose `open` help names the type parameter
  alone.
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
