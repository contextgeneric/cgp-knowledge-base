# `HasRuntime`

`HasRuntime` is CGP's runtime abstraction: a pair of components in which `HasRuntimeType` declares an abstract runtime type and `HasRuntime` borrows the runtime value from the context. `RuntimeOf<Context>` is the alias for the resolved runtime type.

## Purpose

`HasRuntime` lets context-generic code use a runtime without naming a concrete one. A runtime here is whatever object provides execution-time services, such as spawning tasks, sleeping, opening sockets, or reading the clock. Different deployments want different runtimes: Tokio in production, a mock in tests, a single-threaded executor in a benchmark. The context names an abstract `Runtime` type and stores one runtime value, and providers reach it through these two traits.

The abstraction is split because the two questions are independent. `HasRuntimeType` says what the runtime type is, and `HasRuntime` says how to get the runtime value from the context. Code that only names types the runtime exposes needs `HasRuntimeType` alone. Code that performs effects needs `HasRuntime`, which has `HasRuntimeType` as a supertrait. A bound then asks for exactly the trait it uses, and a context can set the type and the value in separate wiring entries.

## Definition

The two components are declared in `cgp-runtime`. `HasRuntimeType` is an abstract-type component defined with [`#[cgp_type]`](../macros/cgp_type.md):

```rust
#[cgp_type]
pub trait HasRuntimeType {
    type Runtime;
}

pub type RuntimeOf<Context> = <Context as HasRuntimeType>::Runtime;
```

`#[cgp_type]` derives the provider name from the associated type, so `Runtime` yields the provider trait `RuntimeTypeProvider` and the key `RuntimeTypeProviderComponent`. `Runtime` has no bound, so any type may be plugged in.

`HasRuntime` is a getter component defined with [`#[cgp_getter]`](../macros/cgp_getter.md), importing the runtime type with [`#[use_type(HasRuntimeType.Runtime)]`](../attributes/use_type.md):

```rust
#[cgp_getter]
#[use_type(HasRuntimeType.Runtime)]
pub trait HasRuntime {
    fn runtime(&self) -> &Runtime;
}
```

`#[cgp_getter]` derives the provider name from the trait name by dropping `Has` and adding `Getter`, so `HasRuntime` yields the provider trait `RuntimeGetter` and the key `RuntimeGetterComponent`. `#[use_type]` adds `HasRuntimeType` as a supertrait and rewrites the bare `Runtime` to `<Self as HasRuntimeType>::Runtime`.

Neither component carries a `#[prefix]` or is in the prelude. All the names above are imported from `cgp::extra::runtime`.

## Behavior

A context sets its runtime type as it would any `#[cgp_type]` abstract type: by implementing `HasRuntimeType` directly, or by wiring `RuntimeTypeProviderComponent: UseType<TokioRuntime>`, after which `RuntimeOf<Context>` is `TokioRuntime`. The generated constructs are the usual [`#[cgp_type]`](../macros/cgp_type.md) expansion.

A context supplies its runtime value as it would any `#[cgp_getter]` getter: by implementing `HasRuntime` directly, or by wiring `RuntimeGetterComponent` to [`UseField`](../providers/use_field.md), which `#[cgp_getter]` supports. A context that keeps its runtime in a `runtime` field wires `RuntimeGetterComponent: UseField<Symbol!("runtime")>`. Because `HasRuntimeType` is a supertrait, a context cannot satisfy `HasRuntime` without also declaring its runtime type.

Providers then write `where Self: HasRuntime` and call `self.runtime()` to get a `&RuntimeOf<Self>`, never naming the concrete runtime. The same effectful code runs on a Tokio context, a mock context, and a test context, with only the wiring changed.

## Examples

A context declares its runtime type and the field that holds the runtime:

```rust
use cgp::prelude::*;
use cgp::extra::runtime::{
    HasRuntime, RuntimeGetterComponent, RuntimeOf, RuntimeTypeProviderComponent,
};

pub struct TokioRuntime { /* handle, clock, etc. */ }

#[derive(HasField)]
pub struct App {
    pub runtime: TokioRuntime,
}

delegate_components! {
    App {
        RuntimeTypeProviderComponent: UseType<TokioRuntime>,
        RuntimeGetterComponent: UseField<Symbol!("runtime")>,
    }
}

fn runtime_of<Context>(context: &Context) -> &RuntimeOf<Context>
where
    Context: HasRuntime,
{
    context.runtime()
}
```

`App` resolves `HasRuntimeType` to `TokioRuntime` through `UseType` and `HasRuntime` through its `runtime` field. `runtime_of` names neither `TokioRuntime` nor the field, so a test context that wires `UseType<MockRuntime>` and its own field reuses it unchanged.

## Related constructs

These constructs are the ones `HasRuntime` works with:

- [`#[cgp_type]`](../macros/cgp_type.md) and [`UseType`](../providers/use_type.md) — define and set `HasRuntimeType`.
- [`#[cgp_getter]`](../macros/cgp_getter.md) and [`UseField`](../providers/use_field.md) — define and supply `HasRuntime`.
- [`HasType`](has_type.md) — the tag-indexed abstract-type component, the general form of `HasRuntimeType`.
- [The `Runner` family](runner.md) — task-running components whose providers can reach the runtime through `HasRuntime`.

## Source

- `HasRuntimeType`, the `RuntimeTypeProvider` provider trait, and the `RuntimeOf` alias are defined in [crates/extra/cgp-runtime/src/traits/has_runtime_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-runtime/src/traits/has_runtime_type.rs).
- `HasRuntime` and its `RuntimeGetter` provider trait are in [crates/extra/cgp-runtime/src/traits/has_runtime.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-runtime/src/traits/has_runtime.rs), re-exported through [crates/extra/cgp-runtime/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-runtime/src/lib.rs) and reached from the facade as `cgp::extra::runtime`.
- The `#[cgp_type]` and `#[cgp_getter]` expansions these rely on live under [crates/macros/cgp-macro-core/src/types/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **2 pages**: [`has_runtime`](https://contextgeneric.dev/docs/reference/components/has_runtime) for the `HasRuntime` getter component and [`has_runtime_type`](https://contextgeneric.dev/docs/reference/components/has_runtime_type) for the `HasRuntimeType` abstract-type component. A change here is propagated to both, per the [synchronization rule](../../../AGENTS.md#the-synchronization-rule); the granularity rule behind the split is recorded in [website/site-structure.md](../../../website/site-structure.md).
