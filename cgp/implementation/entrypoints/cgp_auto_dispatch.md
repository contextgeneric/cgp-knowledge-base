# `#[cgp_auto_dispatch]`: implementation

`#[cgp_auto_dispatch]` takes a trait with one impl per payload type and appends the code that makes
the trait work on an enum of those payloads: a blanket impl of the trait for a fresh enum parameter
that runs a value-handler matcher, plus one per-variant
[`Computer`](../../reference/components/computer.md) per method. This document covers how the macro
is built; for the accepted syntax and the full expansion, read the reference document
[reference/macros/cgp_auto_dispatch.md](../../reference/macros/cgp_auto_dispatch.md).

## Entry point

The macro is the `cgp_auto_dispatch` function in
[cgp-extra-macro-lib/src/entrypoints/cgp_auto_dispatch.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro-lib/src/entrypoints/cgp_auto_dispatch.rs).
It is a self-contained procedural function operating directly on `syn` types rather than a driver
over a `cgp-macro-core` AST stack. It parses the annotated item as a `syn::ItemTrait`, keeps the
original trait tokens verbatim, and appends generated code to them. The attribute takes no
arguments.

The macro is additive: the trait itself is unchanged, so the per-payload impls the user writes still
satisfy it directly. Everything the macro produces is emitted *after* the trait: the enum-level
blanket impl first, then one per-variant computer per method.

## Pipeline

There is no staged AST pipeline; the entry function walks the trait's methods twice. The generated
code is built by two internal helpers, each of which is worth naming because it emits one of the two
kinds of output:

- **`derive_blanket_impl`** builds the single `impl <Trait> for __Variants__` that, per method,
  invokes a value-handler matcher over the enum. It threads a `where` clause that bounds each
  matcher and requires `__Variants__: HasExtractor`.
- **`derive_method_computer`** builds, per method, a private free function annotated with
  [`#[cgp_computer]`](cgp_computer.md) whose body calls the trait method on the payload, named
  `__compute_{method}__` so it does not collide with the module's own items. Both this name and
  the computer's `Compute{Method}` are built from the unrawed method identifier, so a method named
  `r#type` yields `__compute_type__` and `ComputeType` rather than an invalid identifier. The macro
  emits these by delegating to `#[cgp_computer]` rather than synthesizing the `Computer` impl
  itself.

The helpers share their rejections. A trait item that is not a method fails with "Only function
items are allowed in a dispatch trait", a method without a `self` receiver with "Dispatcher method
must have a self argument", and an argument written as a bare pattern with "Dispatcher method
arguments must be typed". `derive_blanket_impl` also rejects a method with a non-lifetime generic
parameter.

## Generated items

For each method the macro emits a per-variant computer named `Compute` followed by the method name
in PascalCase (`area` yields `ComputeArea`). Its body is just the trait-method call on the payload,
and it is bound so it applies to every payload type implementing the trait; a `&self` method borrows
the payload through a fresh lifetime `'__a__`:

```rust
// from `fn area(&self) -> f64;`
#[cgp_computer(ComputeArea)]
fn __compute_area__<'__a__, __Variants__: HasArea>(__Variants__: &'__a__ __Variants__) -> f64 {
    __Variants__.area()
}
```

The enum-level blanket impl implements the trait for a fresh parameter `__Variants__` and, in each
method body, dispatches through the matcher struct selected for that method's shape, invoking it
with a unit context `&()` and unit code `PhantomData::<()>`:

```rust
impl<__Variants__> HasArea for __Variants__
where
    MatchWithValueHandlersRef<ComputeArea>:
        for<'__a__> Computer<(), (), &'__a__ __Variants__, Output = f64>,
    __Variants__: HasExtractor,
{
    fn area(&self) -> f64 {
        <MatchWithValueHandlersRef<ComputeArea> as Computer<_, _, _>>::compute(&(), PhantomData::<()>, self)
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
clause spells out, since that type can name the `'__a__` lifetime, which is bound only inside the
clause's `for<'__a__>` and is not in scope in the body.

## Behavior and corner cases

The **matcher input reflects the receiver and argument list**. A no-argument method passes the bare
payload as the input; a method with arguments passes a nested tuple `(self, (arg_0, arg_1, …))`, and
the arguments are rebound positionally as `arg_i` (the source patterns are discarded).

**Reference lifetimes are elaborated** so the matcher bound can be quantified. A reference receiver,
reference argument, or reference return type with an elided lifetime is rewritten to carry the fresh
`'__a__`. `derive_blanket_impl` collects the lifetimes the bound must quantify into a set: `'__a__`
whenever it was introduced, plus any named lifetime on a reference argument or return type. A
`'static` lifetime is excluded from the quantifier. The emit loop keeps only the last lifetime of
the set, which is the two-lifetime defect under Known issues.

The **enum must be extensible**: the blanket impl always carries `__Variants__: HasExtractor`, so
the enum needs a `CgpData`/`CgpVariant`-style derive that supplies the extractor and field
machinery. Forgetting a per-variant impl surfaces as an unsatisfied matcher bound at the point the
enum's method is used, not at the trait definition.

## Known issues

Three defects make valid traits fail to compile, two in `derive_blanket_impl` and one in
`derive_method_computer`; the
[reference Known issues](../../reference/macros/cgp_auto_dispatch.md#known-issues) give the
user-facing workarounds.

- **A supertrait is never required.** The blanket impl implements the trait for every `__Variants__`
  but copies none of the trait's supertraits into its `where` clause, so the expansion fails with
  `E0277` (`__Variants__: Supertrait` is not satisfied) unless the supertrait already holds for
  every type. The fix is to add `__Variants__: Supertrait` to the clause.
- **Only one lifetime is quantified.** The loop over the collected lifetimes reassigns
  `hrtb = quote! { for<#lifetime> }` on each pass instead of accumulating, so a method needing two
  lifetimes, such as `fn lookup<'a>(&'a self, key: &str) -> &'a str`, quantifies only the last one
  in the set's order and fails with `E0261` on the other. The fix is a single `for<…>` over all of
  them.
- **Two dispatch traits in one module cannot share a method name.** Both the helper
  (`__compute_{method}__`) and the computer (`Compute{Method}`) are derived from the method
  identifier alone, so two `#[cgp_auto_dispatch]` traits declaring `fn area` in one module emit each
  twice and fail with `E0428` on both names and `E0119` on the computers' impls. The fix is to fold
  the trait identifier into both names, which changes the `Compute{Method}` provider name the
  reference documents. No `cargo-cgp` UI fixture pins it yet.

The macro also **rejects a trait method with non-lifetime generic parameters** with a spanned
`syn::Error` ("Dispatch trait methods cannot contain non-lifetime generic parameters due to the lack
of quantified constraints in Rust"). This is a deliberate limitation, not a parser gap. The
generated blanket impl would need a bound quantified over the method's type parameter to guarantee
every payload satisfies it for all instantiations, and Rust has no such quantified bound. The
user-visible consequence is documented under Known issues in
[reference/macros/cgp_auto_dispatch.md](../../reference/macros/cgp_auto_dispatch.md); a method that
must be generic has to be wired with the dispatch combinators directly instead.

## Tests

The behavioral tests cover every receiver-and-argument shape the matcher selection distinguishes:

- [dispatching/auto_dispatch_shape.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_shape.rs):
  a realistic `Shape` enum with a `&self` reader (`area`) and a `&mut self` mutator (`scale`).
- [dispatching/auto_dispatch_self_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_self_only.rs),
  [dispatching/auto_dispatch_self_ref_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_self_ref_only.rs),
  [dispatching/auto_dispatch_self_mut_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_self_mut_only.rs):
  the by-value, `&self`, and `&mut self` no-argument forms, selecting the three plain matchers.
- [dispatching/auto_dispatch_multi_args.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_multi_args.rs),
  [dispatching/auto_dispatch_multi_args_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_multi_args_ref.rs),
  [dispatching/auto_dispatch_multi_args_owned_self.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_multi_args_owned_self.rs):
  the argument-taking forms, selecting the first-argument matcher family.
- [dispatching/auto_dispatch_self_ref_return_implicit_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_self_ref_return_implicit_ref.rs),
  [dispatching/auto_dispatch_self_ref_return_explicit_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_self_ref_return_explicit_ref.rs):
  a reference return type with an elided versus an explicit lifetime, pinning the `'__a__`
  elaboration.
- [dispatching/auto_dispatch_multi_methods.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_multi_methods.rs):
  a trait mixing `&self`, `&mut self`, and `self` methods over one enum.
- [dispatching/auto_dispatch_generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_generics.rs):
  a generic *trait* (`CanCall<T>`) whose per-variant impls add their own bounds; distinct from a
  generic *method*, which is rejected.
- [dispatching/auto_dispatch_async_self_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_async_self_only.rs),
  [dispatching/auto_dispatch_async_self_ref_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_async_self_ref_only.rs),
  [dispatching/auto_dispatch_async_self_mut_only.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_async_self_mut_only.rs),
  [dispatching/auto_dispatch_async_multi_args.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_async_multi_args.rs),
  [dispatching/auto_dispatch_async_multi_args_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_async_multi_args_ref.rs),
  [dispatching/auto_dispatch_async_multi_args_owned_self.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_async_multi_args_owned_self.rs),
  [dispatching/auto_dispatch_async_generics.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_async_generics.rs):
  the same shapes stacked with [`#[async_trait]`](async_trait.md), selecting the `AsyncComputer`
  matcher form.
- [dispatching/auto_dispatch_consumer_traits_in_scope.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_consumer_traits_in_scope.rs):
  a synchronous and an async dispatch trait in a module that imports `CanCompute` and
  `CanComputeAsync`, pinning that the generated matcher call names its provider trait.
- [dispatching/auto_dispatch_method_name_in_scope.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_method_name_in_scope.rs):
  a free function named `area` beside a dispatch trait with an `area` method, pinning that the
  per-variant helper takes a reserved name.
- [dispatching/auto_dispatch_raw_method_name.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/auto_dispatch_raw_method_name.rs):
  a method named `r#type`, pinning that the computer and helper names are built from the unrawed
  identifier (`ComputeType`, `__compute_type__`).
- [dispatching/types.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-tests/tests/dispatching/types.rs)
  is the shared fixture the shape tests import: the `FooBar` enum, derived with `CgpVariant`, over
  the unit structs `Foo` and `Bar`.

The failure cases pin the inputs the macro refuses during expansion, each asserting the entrypoint
returns `Err`:

- [parser_rejections/cgp_auto_dispatch.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/cgp_auto_dispatch.rs)
  covers an associated type in the trait, a method without a `self` receiver, and a method with a
  type generic parameter.

There is no `snapshot_cgp_auto_dispatch!` macro in `cgp-macro-test-util`, so the expansion is not
pinned by a snapshot and is exercised only behaviorally.

## Source

- Entry point: `cgp_auto_dispatch` in
  [cgp-extra-macro-lib/src/entrypoints/cgp_auto_dispatch.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro-lib/src/entrypoints/cgp_auto_dispatch.rs),
  forwarded from the proc-macro shim in
  [cgp-extra-macro/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-extra-macro/src/lib.rs).
- The per-variant handlers are emitted through [`#[cgp_computer]`](cgp_computer.md).
- The value-handler matchers it wires:
  [crates/extra/cgp-dispatch/src/providers/matchers/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-dispatch/src/providers/matchers/).
