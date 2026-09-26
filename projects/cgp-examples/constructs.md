# Constructs by subproject

This document maps each CGP construct the five crates use to the subproject documents that show it in
running code, so an agent looking for a real use of a construct can find one without reading every
section. Each row links the construct's reference document for its semantics; the subproject links
say only where the crate uses it. A construct that no crate uses is absent from the tables, and the
survey behind it is a search of the crates' `src/` and `bin/` trees on the `v0.8.0` branch.

## Defining components and providers

These define the components, the providers, and the traits around them:

| Construct | Where the crates show it |
|---|---|
| [`#[cgp_component]`](../../cgp/reference/macros/cgp_component.md) | [`transfer` components](transfer/reference/components.md), [`web-app` fine-grained](web-app/fine-grained.md#the-components), [`greet-component`](greet/README.md#greet-component) |
| [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) | every subproject; for instance [`builder` providers](builder/reference/subsystem-providers.md) and [`expression` evaluators](expression/reference/eval-providers.md) |
| [`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md) | [`greet-function`](greet/README.md#greet-function) |
| [`#[cgp_type]`](../../cgp/reference/macros/cgp_type.md) | [`transfer` domain types](transfer/reference/domain-types.md), [`expression` abstract types](expression/reference/abstract-types-and-getters.md), [`greet-abstract-type`](greet/README.md#greet-abstract-type) |
| [`#[cgp_auto_getter]`](../../cgp/reference/macros/cgp_auto_getter.md) | [`transfer` request getters](transfer/reference/api-handlers.md#the-request-getters), [`expression`'s `BinarySubExpression`](expression/reference/abstract-types-and-getters.md#binarysubexpression) |
| [`#[async_trait]`](../../cgp/reference/macros/async_trait.md) | [`transfer` components](transfer/reference/components.md) |
| hand-written component expansion | [`greet`'s `greet_expanded.rs`](greet/expansion.md), which is not the macro's current output |

## Provider attributes

The attributes that declare a provider's dependencies and inputs appear in every crate:

| Construct | Where the crates show it |
|---|---|
| [`#[implicit]`](../../cgp/reference/attributes/implicit.md) | [`builder` configuration](builder/reference/subsystem-providers.md#how-the-providers-read-configuration), [`transfer` mock backend](transfer/reference/mock-backend.md), [`web-app` providers](web-app/coarse-grained.md#the-providers), [`greet`](greet/README.md#the-binaries) |
| [`#[uses]`](../../cgp/reference/attributes/uses.md) | [`expression` evaluators](expression/reference/eval-providers.md), [`builder` providers](builder/reference/subsystem-providers.md), [`web-app` filters](web-app/fine-grained.md#the-providers), [`transfer` API handlers](transfer/reference/api-handlers.md) and [wrappers](transfer/reference/wrappers.md) |
| [`#[use_type]`](../../cgp/reference/attributes/use_type.md) | [`transfer` components](transfer/reference/components.md), with the `in App` form on its [request getters](transfer/reference/api-handlers.md#the-request-getters); [`expression` to-Lisp providers](expression/reference/to-lisp-providers.md); [`builder`'s error type](builder/reference/subsystem-providers.md); [`greet-abstract-type`](greet/README.md#greet-abstract-type) |
| [`#[use_provider]`](../../cgp/reference/attributes/use_provider.md) | [`transfer` wrappers](transfer/reference/wrappers.md), [`web-app` filter wrappers](web-app/fine-grained.md#the-providers) |

## Wiring and checking

Every crate wires with `delegate_components!`, and all but `greet` check their wiring:

| Construct | Where the crates show it |
|---|---|
| [`delegate_components!`](../../cgp/reference/macros/delegate_components.md) | every subproject; array keys in [`web-app` fine-grained](web-app/fine-grained.md#the-bundles-and-the-context) |
| the `open` statement | [`expression`'s two arrangements](expression/architecture/dispatch-layers.md#two-arrangements), [`builder`'s multi-target builder](builder/reference/builder-contexts.md#anthropicandchatgptappbuilder-and-its-markers) |
| [aggregate providers](../../cgp/concepts/aggregate-providers.md) | [`web-app` bundles](web-app/fine-grained.md#the-bundles-and-the-context), and behind namespace paths in [`web-app` namespaces](web-app/namespaces.md#the-bundles) |
| [`check_components!`](../../cgp/reference/macros/check_components.md) | [`expression` checks](expression/testing.md#what-the-checks-pin), [`builder` checks](builder/testing.md#what-the-checks-pin), [`web-app` checks](web-app/testing.md#what-the-checks-pin), [`transfer` checks](transfer/testing.md) |
| [`delegate_and_check_components!`](../../cgp/reference/macros/delegate_and_check_components.md) | [`web-app` coarse-grained](web-app/coarse-grained.md#the-context-and-its-wiring) |

## Namespaces

Two crates organize their wiring with namespaces, `transfer` for one context and `web-app` across
three stages:

| Construct | Where the crates show it |
|---|---|
| [`#[prefix]`](../../cgp/reference/attributes/prefix.md) | [`transfer`'s prefix tree](transfer/architecture/namespace-organization.md#the-prefix-tree), [`web-app`'s prefix tree](web-app/namespaces.md#the-prefix-tree) |
| joining a namespace with `namespace …;` | [`transfer`'s `MockApp`](transfer/reference/wiring.md#mockapp), [`web-app` contexts](web-app/namespaces.md#the-contexts) |
| [`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md) | [`transfer`'s `MockNamespace`](transfer/reference/wiring.md#mocknamespace), [`web-app`'s `DefaultAppComponents`](web-app/default-impls.md#the-namespace) |
| [`#[default_impl]`](../../cgp/reference/attributes/default_impl.md) | [`transfer` mock backend](transfer/reference/mock-backend.md), [`web-app` default implementations](web-app/default-impls.md#the-namespace) |
| the `for` statement | [`transfer`'s `DefaultApiHandlers`](transfer/architecture/namespace-organization.md#defaultapihandlers-is-a-table-not-a-namespace-to-join) |

## Handlers, errors, and extensible data

The remaining constructs are specific to one or two crates:

| Construct | Where the crates show it |
|---|---|
| [`Handler`](../../cgp/reference/components/handler.md) | [`transfer` API handlers](transfer/reference/api-handlers.md), [`builder` providers](builder/reference/subsystem-providers.md) |
| [`Computer` and `ComputerRef`](../../cgp/reference/components/computer.md) | [`expression` evaluators](expression/reference/eval-providers.md) and [to-Lisp providers](expression/reference/to-lisp-providers.md) |
| [`HasErrorType`](../../cgp/reference/components/has_error_type.md) | [`transfer`'s error design](transfer/architecture/error-design.md), which raises through a component of its own, [`CanRaiseHttpError`](transfer/reference/components.md#canraisehttperror); [`builder`'s anyhow wiring](builder/reference/builder-contexts.md#fullappbuilder) |
| [`CanRaiseError`](../../cgp/reference/components/can_raise_error.md) | [`builder` providers](builder/reference/subsystem-providers.md), raising `sqlx`, `reqwest`, and `VarError` errors |
| recovering a `Send` bound | [`transfer`'s `CanHandleApiSend`](transfer/reference/http-layer.md#canhandleapisend) |
| [`UseType`](../../cgp/reference/providers/use_type.md) | [`transfer`'s `MockNamespace`](transfer/reference/wiring.md#mocknamespace), [`expression` contexts](expression/examples/README.md) |
| [`#[derive(HasField)]`](../../cgp/reference/derives/derive_has_field.md) | every context that reads a field: [`builder`](builder/reference/builder-contexts.md), [`transfer`](transfer/reference/wiring.md#mockapp), [`web-app`](web-app/coarse-grained.md#the-context-and-its-wiring), [`greet`](greet/README.md#the-binaries) |
| [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md) | [`expression`'s language enums](expression/reference/types.md#the-language-enums), [`builder`'s output structs](builder/reference/subsystem-providers.md#the-output-structs) |
| [`MatchWithValueHandlers`](../../cgp/reference/providers/dispatch_combinators.md) and its `Ref` form | [`expression` dispatchers](expression/reference/dispatchers.md) |
| [`BuildAndMergeOutputs`](../../cgp/reference/providers/dispatch_combinators.md) | [`builder` contexts](builder/reference/builder-contexts.md) |
| [upcasting](../../cgp/reference/traits/cast.md) | [`expression` to-Lisp providers](expression/reference/to-lisp-providers.md) |
| [`Symbol!`](../../cgp/reference/macros/symbol.md) | [`expression`'s `BinaryOpToLisp`](expression/reference/to-lisp-providers.md#binaryoptolisp) |
| [`Product!`](../../cgp/reference/macros/product.md) | [`builder` provider lists](builder/reference/builder-contexts.md) |

## Public material derived from this

None yet.
