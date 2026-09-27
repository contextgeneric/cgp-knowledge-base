# `Runner` (`CanRun` / `CanSendRun`)

The `Runner` family is CGP's pair of task-running components: `CanRun<Code>` runs a task named by a type-level `Code` asynchronously, and `CanSendRun<Code>` runs it with a `Send` future, for work that must cross a thread boundary.

## Purpose

`CanRun` gives a context a uniform way to run a unit of work chosen at the type level. The task is named by a phantom `Code` type, so one context can host many tasks, one per `Code`, each with its own provider. Running a task awaits a `Result<(), Error>`: the task completes or fails with the context's abstract error. There is no input and no output, which separates a runner, a fire-and-complete action, from the [handler](handler.md) family, which maps an `Input` to an `Output`.

`CanSendRun` works around a Rust limitation with `Send` futures. A spawner such as `tokio::spawn` needs a `Send` future, but a generic `async fn` over abstract context types cannot promise `Send` without `Send` bounds on every abstract type in scope, and those bounds would spread through every interface. `CanSendRun::send_run` instead returns `impl Future<Output = ...> + Send`, so the requirement lives on this one trait. The context implements it as a thin proxy over its own `CanRun`, written for the concrete context, where the compiler can see that the concrete future is `Send`. The workaround stays necessary until Rust stabilizes Return Type Notation. The [`Send` bounds](../../concepts/send-bounds.md) concept covers the problem in full.

## Definition

Both components are declared in `cgp-run` with [`#[cgp_component]`](../macros/cgp_component.md), [`#[async_trait]`](../macros/async_trait.md), [`#[derive_delegate(UseDelegate<Code>)]`](../attributes/derive_delegate.md), and [`#[use_type(HasErrorType.Error)]`](../attributes/use_type.md):

```rust
#[cgp_component(Runner)]
#[async_trait]
#[derive_delegate(UseDelegate<Code>)]
#[use_type(HasErrorType.Error)]
pub trait CanRun<Code> {
    async fn run(&self, _code: PhantomData<Code>) -> Result<(), Error>;
}

#[cgp_component(SendRunner)]
#[async_trait]
#[derive_delegate(UseDelegate<Code>)]
#[use_type(HasErrorType.Error)]
pub trait CanSendRun<Code> {
    fn send_run(&self, _code: PhantomData<Code>) -> impl Future<Output = Result<(), Error>> + Send;
}
```

The parts are these:

- **`Code`** names the task. It is passed only as `PhantomData<Code>`, so it carries no data and only selects an implementation.
- **`run`** is an `async fn` with no `Send` promise on its future, and **`send_run`** returns an explicit `Send` future. Both yield `()` on success, since a task's effect is observed elsewhere.
- **The provider traits** are `Runner` and `SendRunner`, wired with `RunnerComponent` and `SendRunnerComponent`.
- **`#[use_type(HasErrorType.Error)]`** adds `HasErrorType` as a supertrait and rewrites the bare `Error` to `<Self as HasErrorType>::Error`.
- **`#[derive_delegate(UseDelegate<Code>)]`** generates the `UseDelegate` impl for the legacy per-task delegation table.

Unlike the handler family, the runner components carry no `#[prefix]` and are not in the prelude. All four names are imported from `cgp::extra::run`.

## Behavior

A context runs a task by calling `context.run(PhantomData::<MyTask>)`, which routes to the provider it wired for `RunnerComponent`. To host several tasks, a context dispatches on `Code`:

```rust
delegate_components! {
    App {
        open RunnerComponent;

        @RunnerComponent.ActionA: RunWithFooBar,
        @RunnerComponent.ActionB: SpawnAndRun<ActionA>,
    }
}
```

`app.run(PhantomData::<ActionA>)` then runs `RunWithFooBar`, and `app.run(PhantomData::<ActionB>)` runs `SpawnAndRun<ActionA>`. The legacy form wires `RunnerComponent` to a `UseDelegate<new AppRunnerComponents { ... }>` table with the same entries. A runner provider is an ordinary provider for the `Runner` trait: it receives the context and the `PhantomData<Code>` tag, and may call any other component on the context.

`CanSendRun` is supplied by a direct impl on the concrete context rather than by wiring. The context implements the provider trait `SendRunner` for itself, forwarding to its own `run`, and the consumer blanket impl then gives it `CanSendRun`:

```rust
use cgp::extra::run::{CanRun, SendRunner, SendRunnerComponent};

#[cgp_provider]
impl SendRunner<App, ActionA> for App {
    async fn send_run(context: &App, code: PhantomData<ActionA>) -> Result<(), Infallible> {
        context.run(code).await
    }
}
```

The impl names the concrete `App` and `ActionA`, so the future of `context.run(code)` has a known type, and the compiler checks that it is `Send`. `#[cgp_provider]` derives the component key `SendRunnerComponent` from the trait name, so that key must be in scope even though the context never wires it.

## Examples

A spawning provider requires `CanSendRun` and hands the `Send` future to a spawner. Here `spawn` stands for any function with the signature of `tokio::spawn`, which requires a `Send + 'static` future:

```rust
#[cgp_impl(new SpawnAndRun<InCode>: RunnerComponent)]
#[use_type(HasErrorType.Error)]
impl<Code, InCode> Runner<Code>
where
    Self: 'static + Send + Clone + CanSendRun<InCode>,
{
    async fn run(&self, _code: PhantomData<Code>) -> Result<(), Error> {
        let context = self.clone();

        spawn(async move {
            let _ = context.send_run(PhantomData).await;
        });

        Ok(())
    }
}
```

`SpawnAndRun<InCode>` runs the task `Code` by cloning the context and spawning the inner task `InCode`. The bound `Self: CanSendRun<InCode>` is what makes the spawn type-check, because `send_run` returns the `Send` future the spawner needs. With the wiring and the `SendRunner` proxy shown above, `app.run(PhantomData::<ActionB>)` spawns `ActionA`. No abstract task or error type carries a `Send` bound; the bound is checked only at the concrete proxy.

## Related constructs

These constructs are the ones the runner components work with:

- [`HasErrorType`](has_error_type.md) — the supertrait whose error a task returns.
- [`HasRuntime`](has_runtime.md) — the runtime abstraction a runner provider can use to spawn or await work.
- [The handler family](handler.md) — the input-to-output counterpart with the same `Code`-tag shape.
- [`Send` bounds](../../concepts/send-bounds.md) — why `CanSendRun` exists.
- [`delegate_components!`](../macros/delegate_components.md) — its `open` statement dispatches on `Code`.

## Source

- `CanRun` / `Runner` and `CanSendRun` / `SendRunner` are defined together in [crates/extra/cgp-run/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-run/src/lib.rs), reached from the facade as `cgp::extra::run`.
- The `#[cgp_component]` and `#[derive_delegate]` expansions they rely on live under [crates/macros/cgp-macro-core/src/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **2 pages**: [`runner`](https://contextgeneric.dev/docs/reference/components/runner) for `CanRun`/`Runner` and [`send_runner`](https://contextgeneric.dev/docs/reference/components/send_runner) for the `Send`-future variant `CanSendRun`/`SendRunner`. A change here is propagated to both, per the [synchronization rule](../../../AGENTS.md#the-synchronization-rule); the granularity rule behind the split is recorded in [website/site-structure.md](../../../website/site-structure.md).
