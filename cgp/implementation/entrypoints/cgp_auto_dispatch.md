# `#[cgp_auto_dispatch]`: implementation

`#[cgp_auto_dispatch]` takes a trait with one impl per payload type and appends the code that makes
the trait work on an enum of those payloads: a blanket impl of the trait for a fresh enum parameter
that runs a value-handler matcher, plus one per-variant
[`Computer`](../../reference/components/computer.md) per method, built through the
[`#[cgp_computer]`](cgp_computer.md) pipeline. This document covers how the macro is built; for the
accepted syntax and the full expansion, read the reference document
[reference/macros/cgp_auto_dispatch.md](../../reference/macros/cgp_auto_dispatch.md).

## Entry point

The macro is the `cgp_auto_dispatch` function in
[cgp-macro-extra-lib/src/cgp_auto_dispatch.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/cgp_auto_dispatch.rs),
forwarded from the proc-macro shim in `cgp-macro-extra`. It rejects any attribute argument
("`#[cgp_auto_dispatch]` takes no arguments"), parses the body as a `syn::ItemTrait`, builds an
`ItemCgpAutoDispatch`, and runs `preprocess()?.eval()?` to get an `EvaluatedCgpAutoDispatch`. That
IR holds the trait, the blanket impl, and one `ItemCgpComputer` per method. The entrypoint emits the
trait unchanged and the blanket impl, then runs each `ItemCgpComputer` through the `#[cgp_computer]`
stages and lowers the result with the helper the computer macro uses. The stages live in
`cgp-macro-extra-core` and are documented in the
[`cgp_auto_dispatch` AST stack](../asts/cgp_auto_dispatch.md).

The macro is additive: the trait itself is unchanged, so the per-payload impls the user writes still
satisfy it directly. Everything the macro produces is emitted *after* the trait: the enum-level
blanket impl first, then one per-variant computer per method.

## Pipeline

The pipeline is two stages, then the computer pipeline for each method:

- **`preprocess`** walks the trait's items in order. A non-method item fails with "Only function
  items are allowed in a dispatch trait", and each method becomes a `DispatchMethod`, whose
  constructor rejects the shapes the macro cannot dispatch and names every elided lifetime in the
  signature (see [Behavior and corner cases](#behavior-and-corner-cases)).
- **`eval`** builds the blanket impl, with one method and one matcher bound per `DispatchMethod`,
  and one `ItemCgpComputer` per method: the IR for a private helper function that calls the method
  on the payload, named `__compute_{method}__` so it does not collide with the module's own items,
  with `Compute{Method}` as the provider name.
- **The computer pipeline** turns each `ItemCgpComputer` into the helper function, its `Computer`
  provider, and the promotion wiring, exactly as a written `#[cgp_computer(Compute{Method})]` would.

`DispatchMethod`'s rejections each report through `Error::new_spanned`: a method with a type or
const generic parameter ("Dispatch trait methods cannot contain non-lifetime generic parameters due
to the lack of quantified constraints in Rust"), a method without a `self` receiver ("Dispatcher
method must have a self argument"), and a typed receiver such as `self: Box<Self>`, which no
matcher can take ("Dispatcher method receiver must be `self`, `&self`, or `&mut self`").

## Generated items

For each method the computer pipeline emits the helper, its provider `Compute` followed by the
method name in PascalCase (`area` yields `ComputeArea`), and the provider's wiring. The helper's
body is the trait-method call on the payload, and it is bound so it applies to every payload type
implementing the trait; a `&self` method borrows the payload through the receiver's lifetime,
`'__a__` when elided:

```rust
// the IR's helper function for `fn area(&self) -> f64;`, lowered as a #[cgp_computer(ComputeArea)]
fn __compute_area__<'__a__, __Variants__: HasArea>(__Variants__: &'__a__ __Variants__) -> f64 {
    __Variants__.area()
}
```

The enum-level blanket impl implements the trait for a fresh parameter `__Variants__` and, in each
method body, dispatches through the matcher selected for that method's shape, invoking it with a
unit context `&()` and unit code `PhantomData::<()>`:

```rust
impl<__Variants__> HasArea for __Variants__
where
    MatchWithValueHandlersRef<ComputeArea>:
        for<'__a__> Computer<(), (), &'__a__ __Variants__, Output = f64>,
    __Variants__: HasExtractor,
{
    fn area(&self) -> f64 {
        <MatchWithValueHandlersRef<ComputeArea> as Computer<_, _, _>>::compute(&(), ::core::marker::PhantomData::<()>, self)
    }
}
```

The matcher is chosen from the value-handler family by two properties of the method: the receiver
form and whether the method takes extra arguments. With no extra arguments the plain family is used:
`MatchWithValueHandlersRef` for `&self`, `MatchWithValueHandlersMut` for `&mut self`,
`MatchWithValueHandlers` for by-value `self`. With extra arguments the first-argument family is used
instead (`MatchFirstWithValueHandlersRef`, `Mut`, or plain), and the receiver and arguments are
bundled into the matcher input as `(context, (args…))`. An `async` method selects the
`AsyncComputer` form of both the `where` bound and the matcher call, and `.await`s the result. The
call names the provider trait, because a type-relative `Matcher::compute` would also match the
consumer traits `CanCompute` and `CanComputeAsync` whenever a module imports them, and fail with
`E0034`. Its trait arguments are the inferred `_, _, _` rather than the input type the `where`
clause spells out, since that type can name lifetimes that only the clause's `for<…>` declares.

When the trait has supertraits, the blanket impl also requires them of the enum
(`__Variants__: Supertrait`), since implementing the trait for every `__Variants__` would otherwise
need each supertrait to hold for every type. Every CGP name in the expansion (the matchers, the
computer traits, `HasExtractor`) is emitted through an `exports` marker, so the expansion resolves
with only `cgp` in scope. The blanket impl's boundary tokens are re-spanned onto the trait
identifier with `override_item_span`, and the helper and computer names are spanned on the method
identifier they derive from.

## Behavior and corner cases

The **matcher input reflects the receiver and argument list**. A no-argument method passes the bare
payload as the input; a method with arguments passes a nested tuple `(self, (arg_0, arg_1, …))`, and
the arguments are rebound positionally as `arg_i` (the source patterns are discarded).

**Elided lifetimes are named by the compiler's elision rules.** The method's argument and return
types are copied into the matcher bound and the helper's signature, where an elided lifetime is
either rejected or means something else, so `DispatchMethod` names each one once and both the bound
and the helper read the result:

- A borrowed receiver keeps the lifetime it names, or gets `'__a__` when elided.
- Each elided lifetime in an argument type, at any depth (`&str`, `Option<&str>`, `Foo<'_>`), gets
  its own fresh `'__a1__`, `'__a2__`, …, through the `ElaborateElidedLifetimes` visitor, matching
  the distinct lifetimes the compiler gives elided inputs.
- An elided lifetime in the return type takes the receiver's lifetime, or, for a by-value `self`,
  the one lifetime the arguments use.
- A function-pointer type (`fn(&T)`) and the `Fn(&T)` sugar bind their own elided lifetimes, so the
  visitor leaves them untouched.

```rust
// fn label(&self, suffix: &str) -> &str;  quantifies a distinct lifetime per elided input:
MatchFirstWithValueHandlersRef<ComputeLabel>:
    for<'__a__, '__a1__> Computer<(), (), (&'__a__ __Variants__, (&'__a1__ str)), Output = &'__a__ str>
```

The matcher bound is quantified, in a single `for<…>`, over the method's own lifetime parameters and
the lifetimes the elaboration introduced. The trait's lifetime parameters are never quantified,
because the blanket impl already declares them, and `'static` is never introduced. The helper
function declares the introduced lifetimes ahead of the trait's and the method's generics.

The **enum must be extensible**: the blanket impl always carries `__Variants__: HasExtractor`, so
the enum needs a `CgpData`/`CgpVariant`-style derive that supplies the extractor and field
machinery.

**A method with a type or const generic parameter is rejected by design.** The generated blanket
impl would need a bound quantified over the method's type parameter to guarantee every payload
satisfies it for all instantiations, and Rust has no such quantified bound. The user-visible
consequence is documented in [reference/macros/cgp_auto_dispatch.md](../../reference/macros/cgp_auto_dispatch.md);
a method that must be generic has to be wired with the dispatch combinators directly.

## Failure modes

**A payload without the trait fails at the call, not at its cause.** The blanket impl's matcher bound
holds only when every variant's payload implements the trait, and the macro cannot see the enum's
variants, so a missing payload impl surfaces as `E0599` where the enum's method is called. The
compiler's notes name the matcher's unsatisfied `Computer` bound but not the payload that lacks the
impl:

```rust
impl HasArea for Circle { /* … */ }   // but no impl for Square
let _ = Shape::Circle(Circle).area();  // E0599 at the call
```

This is the [hidden unsatisfied dependency](../../errors/hidden/unsatisfied-dependency.md) class,
pinned by the `cargo-cgp` fixture
[`usability/extensible-data/auto_dispatch_missing_variant_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/usability/extensible-data/auto_dispatch_missing_variant_impl.rs).

**A hand-written impl of the trait for an extensible enum conflicts with the blanket impl** with
`E0119`, because the blanket impl covers every type implementing `HasExtractor`. The macro cannot see
the other impls in the crate, so the compiler's coherence check reports it.

## Known issues

**Two dispatch traits in one module cannot share a method name.** Both the helper
(`__compute_{method}__`) and the computer (`Compute{Method}`) are derived from the method identifier
alone, so two `#[cgp_auto_dispatch]` traits declaring `fn area` in one module emit each twice and
fail with `E0428` on both names and `E0119` on the computers' impls and wiring. The fix is to fold
the trait identifier into both names, which renames the public `Compute{Method}` provider that code
outside the macro wires by name, so it is deferred. The `cargo-cgp` fixture
[`acceptable/wiring/duplicate-keys/auto_dispatch_shared_method_name.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/acceptable/wiring/duplicate-keys/auto_dispatch_shared_method_name.rs)
pins it; the [conflicting wiring](../../errors/wiring/conflicting-wiring.md) class describes the
errors.

**A lifetime hidden in a path is not named.** A type that carries a lifetime parameter without
writing it, such as `Cow<str>` for `Cow<'_, str>`, has no token for the elaboration to rewrite, so
the elided lifetime stays implicit in the matcher bound and the expansion fails: `E0726` ("implicit
elided lifetime not allowed here") for such an argument, and `E0106` ("missing lifetime specifier")
for such a return type. Whether a path hides a lifetime is recoverable only from the type's
definition, which the macro cannot see, so the fix is to write the lifetime out as `Cow<'_, str>`,
which the elaboration then names.

## Snapshots

The expansion is pinned in the `auto_dispatch` target, which owns this macro's snapshots:

- [auto_dispatch/self_ref_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/self_ref_only.rs):
  the canonical `&self` method with no arguments.
- [auto_dispatch/self_mut_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/self_mut_only.rs),
  [auto_dispatch/self_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/self_only.rs):
  the `&mut self` and by-value `self` matchers, the latter with no `for<…>` quantifier.
- [auto_dispatch/multi_args_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/multi_args_ref.rs):
  the first-argument matcher family, with a named lifetime shared by receiver, argument, and return.
- [auto_dispatch/async_self_ref_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/async_self_ref_only.rs):
  the `AsyncComputer` form, stacked with `#[async_trait]`.
- [auto_dispatch/self_ref_return_explicit_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/self_ref_return_explicit_ref.rs):
  a named return lifetime.
- [auto_dispatch/elided_lifetimes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/elided_lifetimes.rs):
  distinct lifetimes for an elided receiver and an elided argument.
- [auto_dispatch/generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/generics.rs):
  a generic trait, with a by-value method whose elided return takes its argument's lifetime.
- [auto_dispatch/supertrait.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/supertrait.rs):
  the supertrait bound on the enum.
- [auto_dispatch/raw_method_name.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/raw_method_name.rs):
  the unrawed `ComputeType` and `__compute_type__` names for a method named `r#type`.

## Tests

The behavioral tests cover every receiver-and-argument shape the matcher selection distinguishes,
the lifetime elaboration, and the generated names:

- [auto_dispatch/shape.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/shape.rs):
  a realistic `Shape` enum with a `&self` reader (`area`) and a `&mut self` mutator (`scale`).
- [auto_dispatch/self_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/self_only.rs),
  [auto_dispatch/self_ref_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/self_ref_only.rs),
  [auto_dispatch/self_mut_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/self_mut_only.rs):
  the by-value, `&self`, and `&mut self` no-argument forms, selecting the three plain matchers.
- [auto_dispatch/multi_args.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/multi_args.rs),
  [auto_dispatch/multi_args_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/multi_args_ref.rs),
  [auto_dispatch/multi_args_owned_self.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/multi_args_owned_self.rs):
  the argument-taking forms, selecting the first-argument matcher family.
- [auto_dispatch/self_ref_return_implicit_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/self_ref_return_implicit_ref.rs),
  [auto_dispatch/self_ref_return_explicit_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/self_ref_return_explicit_ref.rs):
  a reference return type with an elided versus an explicit lifetime.
- [auto_dispatch/named_lifetimes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/named_lifetimes.rs):
  a named receiver lifetime the return does not mention, a named receiver beside an elided argument,
  a trait lifetime parameter, and a named receiver whose lifetime an elided return takes.
- [auto_dispatch/elided_lifetimes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/elided_lifetimes.rs):
  a borrow returned from `&self` outliving a shorter-lived argument, references nested in
  `Option`, a by-value `self` whose elided return takes its argument's lifetime, and a `Fn(&str)`
  argument left alone.
- [auto_dispatch/multi_methods.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/multi_methods.rs):
  a trait mixing `&self`, `&mut self`, and `self` methods over one enum.
- [auto_dispatch/generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/generics.rs):
  a generic *trait* (`CanCall<T>`) whose per-variant impls add their own bounds; distinct from a
  generic *method*, which is rejected.
- [auto_dispatch/supertrait.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/supertrait.rs):
  a dispatch trait whose supertrait is another dispatch trait.
- [auto_dispatch/default_method.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/default_method.rs):
  a method with a default body, used by one payload and overridden by the other.
- [auto_dispatch/async_self_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/async_self_only.rs),
  [auto_dispatch/async_self_ref_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/async_self_ref_only.rs),
  [auto_dispatch/async_self_mut_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/async_self_mut_only.rs),
  [auto_dispatch/async_multi_args.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/async_multi_args.rs),
  [auto_dispatch/async_multi_args_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/async_multi_args_ref.rs),
  [auto_dispatch/async_multi_args_owned_self.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/async_multi_args_owned_self.rs),
  [auto_dispatch/async_generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/async_generics.rs):
  the same shapes stacked with [`#[async_trait]`](async_trait.md), selecting the `AsyncComputer`
  matcher form.
- [auto_dispatch/consumer_traits_in_scope.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/consumer_traits_in_scope.rs):
  a synchronous and an async dispatch trait in a module that imports `CanCompute` and
  `CanComputeAsync`, pinning that the generated matcher call names its provider trait.
- [auto_dispatch/method_name_in_scope.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/method_name_in_scope.rs):
  a free function named `area` beside a dispatch trait with an `area` method, pinning that the
  per-variant helper takes a reserved name.
- [auto_dispatch/raw_method_name.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/raw_method_name.rs):
  a method named `r#type`.
- [auto_dispatch/computer_by_name.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/computer_by_name.rs):
  the generated `ComputeCall` wired by name, called on a payload directly and through a matcher.
- [auto_dispatch/cross_module.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/cross_module.rs):
  a trait declared in one module, its payloads and enum in another, and the call in a third.
- [auto_dispatch/without_prelude.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/without_prelude.rs):
  the macro invoked by path in a module without `cgp::prelude::*` that declares its own `Computer`
  and `HasExtractor`.
- [auto_dispatch/types.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/auto_dispatch/types.rs)
  is the shared fixture the shape tests import: the `FooBar` enum, derived with `CgpVariant`, over
  the unit structs `Foo` and `Bar`.

The failure cases pin each rejection and its message with `assert_macro_rejects_with`:

- [parser_rejections/cgp_auto_dispatch.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/cgp_auto_dispatch.rs)
  covers an associated type and an associated const in the trait, a method without a `self`
  receiver, a method with a type or a const generic parameter, a typed receiver, and an attribute
  argument.

The cross-crate cases are `cargo-cgp` fixtures backed by two auxiliary crates:
[`ok/cross_crate_dispatch_enum.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/cross_crate_dispatch_enum.rs)
implements and dispatches traits declared in another crate over its own payloads and enum, and
[`ok/cross_crate_dispatch_payloads.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/cross_crate_dispatch_payloads.rs)
spreads the traits, the payloads, and two enums over three crates.
[`ok/auto_dispatch.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/ok/auto_dispatch.rs)
pins the fully expanded code in its `.expand.rs`. The compile-failure fixtures are linked under
Failure modes and Known issues.

## Source

- Entry point: `cgp_auto_dispatch` in
  [cgp-macro-extra-lib/src/cgp_auto_dispatch.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-lib/src/cgp_auto_dispatch.rs),
  forwarded from the proc-macro shim in
  [cgp-macro-extra/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra/src/lib.rs).
- The stages and `DispatchMethod`: [the `cgp_auto_dispatch` AST stack](../asts/cgp_auto_dispatch.md),
  in
  [cgp-macro-extra-core/src/types/cgp_auto_dispatch/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-extra-core/src/types/cgp_auto_dispatch/),
  with the lifetime elaboration in
  [cgp-macro-extra-core/src/visitors/elaborate_lifetimes.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-extra-core/src/visitors/elaborate_lifetimes.rs).
- The per-variant handlers go through [`#[cgp_computer]`](cgp_computer.md)'s stages.
- The value-handler matchers it wires:
  [crates/extra/cgp-dispatch/src/providers/matchers/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-dispatch/src/providers/matchers/).
