# Undeclared dependency

A `#[cgp_fn]`, `#[cgp_impl]`, or `#[cgp_component]` definition uses a trait, an inner provider, or
an abstract type it does not declare, so the generated code relies on a bound that the generated
context or the inner provider lacks, and the compiler reports an error about that parameter
(`E0599`, `E0220`, `E0425`, or `E0277`).

## What triggers it

This class is a *lowering* failure: every dependency a CGP definition relies on must be declared in
an attribute, because the macros lower the definition into an impl over a generated context
parameter and only the declared dependencies become bounds on it. `#[cgp_fn]` lowers a function
into a blanket impl, `impl<__Context__> Describe for __Context__ where __Context__: GetName`, and
`#[cgp_impl]` lowers a provider into `impl<__Context__> Greeter<__Context__> for GreetHello`, with
`self` renamed to a `&__Context__` parameter and `Self` to `__Context__`. Three attributes write the
bounds: [`#[uses]`](../../reference/attributes/uses.md) a trait on the context,
[`#[use_provider]`](../../reference/attributes/use_provider.md) an inner provider's provider trait,
and [`#[use_type]`](../../reference/attributes/use_type.md) an abstract type together with the trait
that declares it. A dependency left out of them is used on a context that carries no bound for it.

The macros cannot catch the omission, because they do not type-check what they lower: which trait a
method belongs to, or which trait declares an associated type, is known only to the compiler. So
the omission is an [acceptable failure](../../implementation/AGENTS.md) that CGP defers to the
compiler. It takes one shape for each kind of declaration.

### A trait the body calls without `#[uses]`

A body may call any trait on the context, but each trait it calls must be declared with `#[uses]`:

```rust
#[cgp_fn]
pub fn get_count(&self, #[implicit] count: &u64) -> u64 {
    *count
}

#[cgp_fn]
#[uses(GetName)]
pub fn describe(&self) -> String {
    format!("{} ({})", self.get_name(), self.get_count()) // `GetCount` is not declared
}
```

`describe` calls `get_count`, a method of the `#[cgp_fn]` trait `GetCount`, but `#[uses]` lists only
`GetName`. The same mistake arises for a consumer trait called in a `#[cgp_impl]` body, for an
associated function called on `Self` (`Self::raise_error(…)` needs `CanRaiseError`), and for a
generic trait, whose declaration must also give the arguments the call uses
(`#[uses(CanFormatPair<(u32, u64)>)]`).

### An inner provider without `#[use_provider]`

A [higher-order provider](../../concepts/higher-order-providers.md) calls its inner provider through
the provider trait, which needs the inner parameter bounded by that trait:

```rust
#[cgp_impl(new ScaledArea<InnerCalculator>)]
impl<InnerCalculator> AreaCalculator {
    fn area(&self, #[implicit] scale_factor: f64) -> f64 {
        InnerCalculator::area(self) * scale_factor * scale_factor // not imported
    }
}
```

Without `#[use_provider(InnerCalculator: AreaCalculator)]`, the parameter `InnerCalculator` carries
no `AreaCalculator<Self>` bound, so the associated-function call cannot resolve.

### An abstract type without `#[use_type]`

An [abstract type](../../concepts/abstract-types.md) such as the context's `Error` is an associated
type of a trait the context implements, so using it needs that trait as a bound:

```rust
#[cgp_impl(new ValidateNothing)]
impl Validator {
    fn validate(&self) -> bool {
        let _e: Option<Self::Error> = None; // `HasErrorType.Error` is not imported
        true
    }
}
```

`Self::Error` names an associated type of the context, which carries no `HasErrorType` bound. A bare
`Error` is the same mistake in the form `#[use_type]` teaches: without the import, nothing rewrites
`Error` into `<Self as HasErrorType>::Error`, so the name refers to no type at all.

### A component requirement the provider does not declare

A component can require a trait of every context, and each provider must then declare it too:

```rust
#[cgp_component(Greeter)]
#[extend(HasName)]
pub trait CanGreet {
    fn greet(&self);
}

#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self) {} // `HasName` is not declared, though the component requires it
}
```

The component's [`#[extend(HasName)]`](../../reference/attributes/extend.md), like a component's
`#[use_type(HasErrorType.Error)]`, lowers to a `where` clause on the provider trait,
`trait Greeter<__Context__> where __Context__: HasName`. A provider impl must satisfy that clause
from its own declarations, so `GreetHello` fails even though its body never calls `HasName`. A
[`UseDefault`](../../reference/providers/use_default.md) provider written with
`#[cgp_impl(UseDefault)]` fails the same way.

## The raw diagnostic

This section describes what plain `cargo check` prints on stable `rustc`, the fallback when
`cargo-cgp` is not on hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers
the readable form. This is a **surfaced** class: each shape names what is missing somewhere in its
output, but frames it as a property of the generated `__Context__` and steers toward a wrong fix.
Each shape has its own diagnostic:

- **An undeclared trait:** an [`E0599`](../error_codes/e0599.md). A method call reads "the method
  `get_count` exists for reference `&__Context__`, but its trait bounds were not satisfied", with a
  note listing the `HasField<Symbol<…>>` bounds of the called trait's blanket impl, which suggest a
  missing field. Its `help:` offers to "restrict type parameter `__Context__`" by splicing
  `: GetCount` after the `#[cgp_fn]` attribute. An associated-function call reads "no associated
  function or constant named `raise_error` found for type parameter `__Context__`", with the same
  spliced suggestion, written with `/* SourceError */` placeholders. For a generic trait, stable
  `rustc` also labels the call an associated function and suggests rewriting it as
  `__Context__::format_pair(…)`.
- **An unimported inner provider:** an `E0599` "no associated function or constant named `area`
  found for type parameter `InnerCalculator`", whose `help:` offers to restrict the parameter by
  `AreaCalculator</* __Context__ */>`, naming the generated context, or by the consumer trait
  `CanCalculateArea`, the wrong half of the component.
- **An unimported abstract type:** `Self::Error` gives one [`E0220`](../error_codes/e0220.md),
  "associated type `Error` not found for `__Context__`" in a `#[cgp_impl]` (or "for `Self`" in a
  `#[cgp_fn]`), with no help. A bare `Error` gives an [`E0425`](../error_codes/e0425.md), "cannot
  find type `Error` in this scope", whose `help:` offers to import `std::error::Error`,
  `std::fmt::Error`, `std::io::Error`, and other types named `Error`. When the component itself
  imports the type, its `#[use_type(HasErrorType.Error)]` requires `HasErrorType` of every context,
  so the provider also fails that requirement and stable adds four
  [`E0277`](../error_codes/e0277.md) blocks on `__Context__`: two on `HasErrorType`, "required by a
  bound in `Loader`", and two on the `DelegateComponent<ErrorTypeProviderComponent>` and
  `IsProviderFor<ErrorTypeProviderComponent, __Context__>` bounds behind it.
- **An undeclared requirement:** an `E0277` "the trait bound `__Context__: HasName` is not
  satisfied", with the caret on the `#[cgp_impl]` attribute and a note "required by a bound in
  `Greeter`" pointing at the component's `#[extend(HasName)]`. A `help:` or the caret's label names
  the bound behind the trait: a `HasField<Symbol<4, Chars<'n', …>>>` for a `#[cgp_auto_getter]`
  trait, which suggests a missing field, or `DelegateComponent<NameGetterComponent>` for a
  `#[cgp_getter]` component. The error can repeat, once for each place the compiler checks the
  bound.

## Where the root cause is

The root cause is **present in every shape but misframed**: the output names the trait or the type
the definition uses, never the declaration it lacks. The undeclared trait appears in the `E0599`'s
"restrict type parameter `__Context__`" help, the abstract type in the `E0220` headline, and the
required trait in the `E0277` headline, each as a property of `__Context__`, a name the author never
wrote. The helps around them point at wrong fixes: a missing field (the `HasField` notes), an edit
spliced into the macro attribute (`#[cgp_fn]: GetCount`, which is not valid syntax), a bound written
with `/* … */` placeholders, or an import of `std::error::Error`. A bare `Error` without a
requirement of the component names only the type, not the trait that declares it.

The reliable landmark is the generated name. A headline or a help that mentions `__Context__`
(including the help that restricts an inner provider's parameter by
`AreaCalculator</* __Context__ */>`) places the error in a CGP definition whose declarations are
incomplete. For the undeclared requirement, the "required by a bound in" note also names the
component and points at the attribute that requires the trait, which is the dependency to copy into
the provider.

## How cargo-cgp presents it

`cargo-cgp` reshapes each shape into one error that names what was used and not declared, carries
the declaration to write in a `help`, and keeps `rustc`'s own code. The codes are defined in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) (summarized in
[cargo-cgp-codes.md](../error_codes/cargo-cgp-codes.md)):

- **`[CGP-E030]`** for an undeclared trait, with the trait written with the arguments the call uses:
  ``the trait `CanFormatPair` is used but not declared as a dependency``, and
  ``help: declare it as a dependency with `#[uses(CanFormatPair<(u32, u64)>)]` ``. The arguments
  are read from the written argument types or the declared types of the parameters passed. An
  argument it cannot read stays as the trait's own parameter, and the help says to replace it:
  "with the type the call uses in place of `SourceError`".
- **`[CGP-E031]`** for an unimported inner provider, with a generic component's parameters written
  from the call (`AreaCalculator<Shape>`):
  ``the inner provider `InnerCalculator` is used but not imported``, and
  ``help: import it with `#[use_provider(InnerCalculator: AreaCalculator)]` ``. When two provider
  traits declare the called function and the impl implements neither, the import is ambiguous and
  rustc's error stays.
- **`[CGP-E035]`** for an unimported abstract type, reported once per definition:
  ``the abstract type `Error` is used but not imported``, and
  ``help: import it with `#[use_type(HasErrorType.Error)]` ``. The tool rewords the `E0220` of
  `Self::Error`, and the `E0425` of a bare `Error` when a requirement of the component names the
  trait that declares it; the `E0277` blocks of that requirement are dropped, since the import
  satisfies them too.
- **`[CGP-E036]`** for an undeclared requirement, reported once per provider, with the caret where
  rustc first reported it, usually the `#[cgp_impl]` attribute, and the context written as `Self`
  in any requirement that names it:
  ``the provider trait `Greeter` requires `HasName` of the context, but the provider `GreetHello` does not declare it``,
  and ``help: declare it as a dependency with `#[uses(HasName)]` ``, or
  `#[use_type(HasErrorType.Error)]` for an abstract-type component.

Four cases keep `rustc`'s output. A call on a generic parameter other than the context
(`value: &Value`) is left alone on purpose, since its fix is a bound on `Value`, which `#[uses]`
cannot write. The other three are gaps, described under [Notes for tooling](#notes-for-tooling): a
bare `Error` that no requirement of the component explains, a `Self::Error` that two abstract-type
traits could declare, and an undeclared trait or inner provider that takes a lifetime or const
parameter, whose `[CGP-E030]` or `[CGP-E031]` header stands without a help.

## Resolving it

Declare the dependency on the definition that uses it, with the attribute for its kind:

- **A trait:** add it to `#[uses(…)]`, with the arguments the call uses for a generic trait, as in
  `#[uses(GetName, GetCount)]` or `#[uses(CanRaiseError<String>)]`.
- **An inner provider:** import it with `#[use_provider(InnerCalculator: AreaCalculator)]`, which
  supplies the context argument the provider trait takes first.
- **An abstract type:** import it with `#[use_type(HasErrorType.Error)]`, then write it bare
  (`Error`).
- **A component requirement:** declare the same trait on the provider, `#[uses(HasName)]` for a
  trait or `#[use_type(HasErrorType.Error)]` for an abstract-type component.

A hand-written `where Self: Trait` bound declares a trait as well, but the attributes are the
idiomatic form, and `#[use_type]` also rewrites the bare type name.

## Notes for tooling

Three shapes still reach the reader as `rustc` wrote them, and each needs more than the emitter has
today:

- **A bare `Error` that no requirement explains:** the `E0425` comes from name resolution, before
  the compiler has built the HIR or can say which traits declare an `Error`, and nothing later
  names the trait. Recognizing it would need the error's span placed inside a CGP definition from
  the source map alone, and the trait to import found once the crate's traits are known.
- **Two abstract-type traits that declare the same name:** the import is ambiguous, and the tool
  does not guess. A rewording could list the candidate imports instead.
- **A trait with a lifetime or const parameter:** the `[CGP-E030]` and `[CGP-E031]` helps write only
  type arguments, so the header stands without one.
- **A provider called by its own path:** a provider body calling another provider directly,
  `WidthArea::area(self)`, without declaring what that provider requires of the context, keeps
  rustc's `E0277` on the generated `__Context__`; the called provider is not an inner provider, so
  `[CGP-E031]` does not claim it, and nothing names the missing `#[uses(…)]`.

The `[T]: Sized` errors that an unresolved call's result type can trail, notably in an `async` body,
are also left in place: they can land off the failing expression, where dropping them reliably
would need type information the emitter cannot obtain.

## Backing fixtures

These fixtures pin the class, one group per shape:

- [`lowering/undeclared-dependency/undeclared_uses_trait.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_uses_trait.rs):
  a `#[cgp_fn]` body calling the `#[cgp_fn]` trait `GetCount` that `#[uses]` omits; `[CGP-E030]`.
- [`lowering/undeclared-dependency/undeclared_uses_trait_in_cgp_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_uses_trait_in_cgp_impl.rs):
  the provider counterpart, a `#[cgp_impl]` body calling an undeclared trait; `[CGP-E030]`.
- [`lowering/undeclared-dependency/undeclared_uses_trait_in_async_cgp_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_uses_trait_in_async_cgp_impl.rs):
  the same in an `async fn` body, whose receiver reaches the call through the `let` the async
  lowering adds; `[CGP-E030]`.
- [`lowering/undeclared-dependency/undeclared_generic_trait.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_generic_trait.rs):
  a generic consumer trait called with a written argument; the help writes
  `CanFormatPair<(u32, u64)>`.
- [`lowering/undeclared-dependency/undeclared_generic_trait_parameter.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_generic_trait_parameter.rs):
  the argument is a parameter of the function, whose declared type gives `CanFormatPair<u32>`.
- [`lowering/undeclared-dependency/raise_error_in_cgp_fn.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/raise_error_in_cgp_fn.rs):
  `Self::raise_error("failed")` in a `#[cgp_fn]` body; the help names `SourceError` to replace.
- [`lowering/undeclared-dependency/raise_error_written_source.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/raise_error_written_source.rs):
  `Self::raise_error(LoadError)` in a provider; the help writes `CanRaiseError<LoadError>`.
- [`lowering/undeclared-dependency/raise_generic_missing_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/raise_generic_missing_bound.rs):
  `Self::raise_error("failed".to_owned())` in a provider, an argument whose type the tool does not
  read, so the help names `SourceError` to replace.
- [`lowering/undeclared-dependency/undeclared_trait_on_non_context_parameter.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_trait_on_non_context_parameter.rs):
  a call on a `value: &Value` parameter, left as `rustc` wrote it because `#[uses]` cannot bound
  `Value`.
- [`lowering/undeclared-dependency/higher_order_missing_use_provider.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/higher_order_missing_use_provider.rs):
  a higher-order provider calling its inner provider without `#[use_provider]`; `[CGP-E031]`.
- [`lowering/undeclared-dependency/missing_use_provider_other_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_other_component.rs):
  the same with an inner provider of another component; `[CGP-E031]`.
- [`lowering/undeclared-dependency/missing_use_provider_generic_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_generic_component.rs):
  the inner provider of a generic component, whose `[CGP-E031]` help writes the component's
  parameter from the call, `AreaCalculator<Shape>`.
- [`lowering/undeclared-dependency/missing_use_provider_unread_argument.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_unread_argument.rs):
  a call whose argument the tool cannot type, so the help names the parameter for the reader to
  replace; and
  [`missing_use_provider_lifetime_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_lifetime_component.rs),
  a component with a lifetime parameter, whose `[CGP-E031]` has no help.
- [`lowering/undeclared-dependency/missing_use_provider_shared_method_name.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_shared_method_name.rs):
  two provider traits declaring `area`; the impl's own trait is named, and with neither the impl's
  own, rustc's `E0599` stays.
- [`lowering/undeclared-dependency/missing_use_provider_concrete_qualifier.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_concrete_qualifier.rs):
  a provider called by its own path without the requirement it has, left as rustc's `E0277`.
- [`lowering/undeclared-dependency/self_error_without_bound.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_without_bound.rs):
  `Self::Error` in a provider body; `[CGP-E035]` from the `E0220`.
- [`lowering/undeclared-dependency/self_error_in_cgp_fn.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_in_cgp_fn.rs):
  `Self::Error` in a `#[cgp_fn]` body, where the `E0220` names `Self`; `[CGP-E035]`.
- [`lowering/undeclared-dependency/self_error_in_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_in_component.rs):
  `Self::Error` in a component's method signature; `[CGP-E035]`.
- [`lowering/undeclared-dependency/self_error_used_twice.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_used_twice.rs):
  two uses in one provider, reported once.
- [`lowering/undeclared-dependency/self_error_two_traits.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_two_traits.rs):
  a crate declaring its own `HasErrorType` beside CGP's, so the `E0220` is left as `rustc` wrote it
  (`usability`).
- [`lowering/undeclared-dependency/error_alias_in_cgp_fn.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_in_cgp_fn.rs)
  and
  [`lowering/undeclared-dependency/error_alias_in_provider_body.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_in_provider_body.rs):
  a bare `Error` that no requirement explains, whose `E0425` and its `std::error::Error` import
  suggestion are left as `rustc` wrote them (`usability`).
- [`lowering/undeclared-dependency/error_alias_without_use_type.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_without_use_type.rs):
  a bare `Error` in a provider of a component that imports the type; the `E0425` becomes
  `[CGP-E035]` and the requirement's `E0277`s are dropped.
- [`lowering/undeclared-dependency/use_type_component_self_error.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/use_type_component_self_error.rs):
  the same with `Self::Error`, where the `E0220` becomes `[CGP-E035]`.
- [`lowering/undeclared-dependency/supertrait_missing_uses.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/supertrait_missing_uses.rs):
  a provider omitting the `HasName` a component's `#[extend]` requires; `[CGP-E036]`.
- [`lowering/undeclared-dependency/supertrait_missing_uses_generic.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/supertrait_missing_uses_generic.rs):
  the requirement is a generic trait, written `TagFor<u32>` in the header and the help.
- [`lowering/undeclared-dependency/supertrait_missing_uses_self_argument.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/supertrait_missing_uses_self_argument.rs):
  the requirement's argument is the context, written `CanCompareWith<Self>` rather than with the
  generated `__Context__`.
- [`lowering/undeclared-dependency/supertrait_missing_uses_beside_body_error.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/supertrait_missing_uses_beside_body_error.rs):
  an unrelated error in the provider's body stays beside the `[CGP-E036]`.
- [`lowering/undeclared-dependency/use_default_getter_context.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/use_default_getter_context.rs):
  a `#[cgp_impl(UseDefault)]` provider omitting a `#[cgp_getter]` requirement; `[CGP-E036]` names
  `UseDefault`.

## Related

- [`#[uses]`](../../reference/attributes/uses.md),
  [`#[use_provider]`](../../reference/attributes/use_provider.md), and
  [`#[use_type]`](../../reference/attributes/use_type.md): the declarations each shape omits.
- [`#[cgp_fn]`](../../reference/macros/cgp_fn.md) and
  [`#[cgp_impl]`](../../reference/macros/cgp_impl.md): the macros whose generated context the
  errors name.
- [Impl-side dependencies](../../concepts/impl-side-dependencies.md): why a dependency is a bound on
  the generated impl rather than on the trait.
- [Wrong component half](wrong-component-half.md): the sibling class, where a dependency is declared
  but names the wrong half of a component (a provider trait in `#[uses]`, say).
- [Unsatisfied dependency (hidden)](../hidden/unsatisfied-dependency.md): the contrasting class,
  where a *declared* dependency is unmet by the context's wiring, and the fix is in the wiring, not
  in the definition.
- [`E0599`](../error_codes/e0599.md), [`E0220`](../error_codes/e0220.md),
  [`E0425`](../error_codes/e0425.md), and [`E0277`](../error_codes/e0277.md): the Rust error codes
  this class is reported under.
- [Debugging CGP compile errors](../../guides/debugging.md#grep-for-the-suspected-line-instead-of-reading-the-whole-log):
  the grep that recognizes the class by its `__Context__` headline.
