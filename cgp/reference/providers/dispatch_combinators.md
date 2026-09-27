# Dispatch combinators

The dispatch combinators are the `cgp-dispatch` providers that route an extensible-data value to
per-variant or per-field handlers: the matchers take an enum apart and hand each variant's payload
to a handler, and the builders assemble a record with one handler per field.

## Purpose

The dispatch combinators handle an arbitrary enum or record generically, when the variants or fields
are known only at the type level and the logic for each lives in its own provider. A hand-written
`match` names every variant in one place. The matchers instead drive the extractor traits of
[`extract_field`](../traits/extract_field.md), trying one variant at a time and proving the match
exhaustive without a wildcard arm. The builders drive the builder traits of
[`has_builder`](../traits/has_builder.md), starting from an empty partial record and filling one
field per handler.

Both halves are handler providers, so they wire into a context with
[`delegate_components!`](../macros/delegate_components.md) and compose with the
[handler combinators](handler_combinators.md). They differ in which handler traits they implement:

- **The matchers and their adapters** implement `Computer` and `AsyncComputer` only.
- **The builders** implement `Computer`, `TryComputer`, and `Handler`, propagating an inner
  provider's error in the fallible forms.

The prelude exports the value matchers `MatchWithValueHandlers`, `MatchWithValueHandlersRef`,
`MatchWithValueHandlersMut`, and their `MatchFirstWith…` counterparts. Every other name here is
imported from `cgp::extra::dispatch`.

## The matcher loop: `DispatchMatchers`

Every matcher runs its handler list through one loop, a monadic pipeline that stops at the first
handler that matches:

```rust
pub type DispatchMatchers<Providers> = PipeMonadic<OkMonadic, Providers>;
```

Each handler in the `Product!` list takes the extractor, a partial view of the enum, and returns
`Result<Output, Remainder>`. `Ok(output)` means the handler matched. `Err(remainder)` hands back the
extractor with one more variant ruled out. Under [`OkMonadic`](monad_providers.md) the pipeline
continues on `Err` and stops on `Ok`, carrying the shrinking remainder from handler to handler. If
the last handler still returns `Err`, every variant has been ruled out, so the remainder type is
uninhabited and the matcher discharges it without a fallback arm. Users rarely name
`DispatchMatchers` directly.

## Matchers

`MatchWithHandlers<Handlers>` is the owned-input matcher. It requires the input to implement
[`HasExtractor`](../traits/extract_field.md), runs `DispatchMatchers<Handlers>` over
`Input::Extractor`, and calls `finalize_extract_result` to discharge the uninhabited remainder and
return the bare `Output`:

```rust
pub struct MatchWithHandlers<Handlers>(pub PhantomData<Handlers>);

impl<Context, Code, Input, Output, Remainder, Handlers> Computer<Context, Code, Input>
    for MatchWithHandlers<Handlers>
where
    Input: HasExtractor,
    DispatchMatchers<Handlers>:
        Computer<Context, Code, Input::Extractor, Output = Result<Output, Remainder>>,
    Remainder: FinalizeExtract,
{
    type Output = Output;
    // compute: DispatchMatchers::compute(context, code, input.to_extractor())
    //              .finalize_extract_result()
}
```

The matchers come in six forms, along two axes:

| | owned input | `&'a Input` | `&'a mut Input` |
| --- | --- | --- | --- |
| **value alone** | `MatchWithHandlers` | `MatchWithHandlersRef` | `MatchWithHandlersMut` |
| **value with extra arguments** | `MatchFirstWithHandlers` | `MatchFirstWithHandlersRef` | `MatchFirstWithHandlersMut` |

The borrowed forms require `HasExtractorRef` or `HasExtractorMut` and match without moving the
value. The `MatchFirstWith…` forms take a tuple `(Input, Args)` whose first element is matched while
`Args` rides along to every handler: the list runs over `(Input::Extractor, Args)` and returns
`Result<Output, (Remainder, Args)>`, so a miss carries both the remainder and the arguments forward.

## Adapters

A matcher's handler list is normally a list of adapters, each of which tries one variant and
forwards the payload to an inner provider. Every adapter defaults its provider to
[`UseContext`](use_context.md) and returns the `Result<Output, Remainder>` shape the loop expects:

- **`ExtractFieldAndHandle<Tag, Provider>`** calls `ExtractField<Tag>` on the input. On a match it
  passes the payload to `Provider` as a `Field<Tag, Value>` and returns `Ok` of the output;
  otherwise it returns `Err` of the remainder.
- **`ExtractFirstFieldAndHandle<Tag, Provider>`** does the same for the `(Input, Args)` form,
  calling `Provider` with `(Field<Tag, Value>, Args)`.
- **`HandleFieldValue<Provider>`** sits between an extract adapter and the real work: it strips the
  `Field` wrapper and passes the bare value to `Provider`. **`HandleFirstFieldValue<Provider>`**
  does the same for `(Field<Tag, Input>, Args)`, forwarding `(Input, Args)`.
- **`DowncastAndHandle<Inner, Provider>`** matches a group of variants at once. It uses
  `CanDowncastFields<Inner>` from [`cast`](../traits/cast.md) to narrow the input to a smaller enum
  `Inner`, and on success hands the whole `Inner` value to `Provider`.

```rust
pub struct ExtractFieldAndHandle<Tag, Provider = UseContext>(pub PhantomData<(Tag, Provider)>);
pub struct ExtractFirstFieldAndHandle<Tag, Provider = UseContext>(pub PhantomData<(Tag, Provider)>);
pub struct HandleFieldValue<Provider = UseContext>(pub PhantomData<Provider>);
pub struct HandleFirstFieldValue<Provider = UseContext>(pub PhantomData<Provider>);
pub struct DowncastAndHandle<Input, Provider = UseContext>(pub PhantomData<(Input, Provider)>);
```

## Convenience matchers

The convenience matchers build the adapter list from the input enum's own variants, so no list is
written by hand. `MatchWithFieldHandlers` and `MatchWithValueHandlers` are aliases over
[`UseInputDelegate`](handler_combinators.md#the-legacy-form-useinputdelegate) that key on the input
type and, for each input, derive the list from its [`HasFields`](../traits/has_fields.md):

```rust
pub type MatchWithFieldHandlers<Provider = UseContext> =
    UseInputDelegate<MatchWithFieldHandlersInputs<Provider>>;

pub type MatchWithValueHandlers<Provider = UseContext> =
    UseInputDelegate<MatchWithFieldHandlersInputs<HandleFieldValue<Provider>>>;
```

They differ by one `HandleFieldValue` wrapper. `MatchWithFieldHandlers` runs
`ExtractFieldAndHandle<Tag, Provider>` per variant, so `Provider` receives a `Field<Tag, Value>`.
`MatchWithValueHandlers` runs `ExtractFieldAndHandle<Tag, HandleFieldValue<Provider>>`, so
`Provider` receives the bare payload. That makes it the form for payload handlers that are ordinary
computers, such as ones from [`#[cgp_computer]`](../macros/cgp_computer.md). With the default
`UseContext`, each payload goes back through the context's own `ComputerComponent`.

The borrowed forms `MatchWithFieldHandlersRef`, `MatchWithValueHandlersRef`, and
`MatchWithValueHandlersMut` are delegation tables. Their `Computer` and `AsyncComputer` entries
dispatch `&Input` or `&mut Input` to the borrowed matchers, and their `ComputerRef` and
`AsyncComputerRef` entries do the same through [`PromoteRef`](handler_combinators.md). The
`MatchFirstWith…` convenience matchers are the same aliases built on the first-argument adapters and
matchers.

The list is built by three traits:

```rust
pub trait MapFieldHandler {
    type FieldHandler<Tag>;
}

pub trait ToFieldHandlers<M> {
    type Handlers;
}

pub trait HasFieldHandlers<M> {
    type Handlers;
}
```

`MapFieldHandler` maps a variant's `Tag` to its adapter; the crate provides
`MapExtractFieldAndHandle<Provider>` and `MapExtractFirstFieldAndHandle<Provider>`.
`ToFieldHandlers` walks a sum-type field list: `Either<Field<Tag, Value>, Rest>` becomes
`Cons<M::FieldHandler<Tag>, Rest::Handlers>`, and [`Void`](../types/either.md) becomes `Nil`.
`HasFieldHandlers` applies `ToFieldHandlers` to a type's `HasFields::Fields`. Because only the
`Either`/`Void` list is handled, the convenience matchers apply to enums, not to structs.

## Builders

The builders assemble a record from an empty partial record, one handler per field. Two adapters do
the per-field work, each running its provider over a reference to the current builder, so a handler
can read fields already set:

- **`BuildAndSetField<Tag, Provider>`** computes one field's value with `Provider` and sets it with
  `BuildField<Tag>`.
- **`BuildAndMerge<Provider>`** computes a whole record with `Provider` and copies every shared
  field into the builder with `CanBuildFrom` from [`has_builder`](../traits/has_builder.md).

```rust
pub struct BuildAndSetField<Tag, Provider = UseContext>(pub PhantomData<(Tag, Provider)>);

impl<Context, Code, Tag, Value, Provider, Output, Builder> Computer<Context, Code, Builder>
    for BuildAndSetField<Tag, Provider>
where
    Provider: for<'a> Computer<Context, Code, &'a Builder, Output = Value>,
    Builder: BuildField<Tag, Value = Value, Output = Output>,
{
    type Output = Output;
    // compute: let value = Provider::compute(context, code, &builder);
    //          builder.build_field(PhantomData::<Tag>, value)
}
```

`BuildWithHandlers<Output, Handlers>` runs the adapters. It starts from `Output::builder()`, pipes
the builder through `Handlers` with [`PipeHandlers`](handler_combinators.md), and calls
`finalize_build` to recover the concrete `Output`. It ignores its own input. `finalize_build` exists
only for a builder with every field set, so a missing handler is a compile error:

```rust
pub struct BuildWithHandlers<Output, Handlers>(pub PhantomData<(Output, Handlers)>);

impl<Context, Code, Input, Output, Builder, Handlers, Res> Computer<Context, Code, Input>
    for BuildWithHandlers<Output, Handlers>
where
    Output: HasBuilder<Builder = Builder>,
    PipeHandlers<Handlers>: Computer<Context, Code, Builder, Output = Res>,
    Res: FinalizeBuild<Target = Output>,
{
    type Output = Output;
    // compute: PipeHandlers::compute(context, code, Output::builder()).finalize_build()
}
```

`BuildAndMergeOutputs<Output, Handlers>` takes a list of plain record-producing providers instead of
adapters. It is a delegation table that maps the handler components to
`BuildWithHandlers<Output, Handlers::Mapped>`, after wrapping each provider in `BuildAndMerge`
through the `ToBuildAndMergeHandler` [`MapType`](../traits/map_type.md) marker.

All the builders implement `Computer`, `TryComputer`, and `Handler`; the fallible forms require
`Context: HasErrorType`.

## Examples

This matcher dispatches a `Shape` to a per-variant area provider with an explicit adapter list:

```rust
use core::marker::PhantomData;
use cgp::prelude::*;
use cgp::extra::dispatch::{ExtractFieldAndHandle, HandleFieldValue, MatchWithHandlers};

pub struct Circle {
    pub radius: f64,
}

pub struct Rectangle {
    pub width: f64,
    pub height: f64,
}

#[derive(CgpData)]
pub enum Shape {
    Circle(Circle),
    Rectangle(Rectangle),
}

pub struct ComputeArea;

#[cgp_provider]
impl<Context, Code> Computer<Context, Code, Circle> for ComputeArea {
    type Output = f64;

    fn compute(_context: &Context, _code: PhantomData<Code>, shape: Circle) -> f64 {
        core::f64::consts::PI * shape.radius * shape.radius
    }
}

#[cgp_provider]
impl<Context, Code> Computer<Context, Code, Rectangle> for ComputeArea {
    type Output = f64;

    fn compute(_context: &Context, _code: PhantomData<Code>, shape: Rectangle) -> f64 {
        shape.width * shape.height
    }
}

fn area(shape: Shape) -> f64 {
    MatchWithHandlers::<
        Product![
            ExtractFieldAndHandle<Symbol!("Circle"), HandleFieldValue<ComputeArea>>,
            ExtractFieldAndHandle<Symbol!("Rectangle"), HandleFieldValue<ComputeArea>>,
        ],
    >::compute(&(), PhantomData::<()>, shape)
}
```

The list tries `Circle` first. A rectangle misses it, and the remainder, with `Circle` ruled out,
reaches the `Rectangle` adapter, the last arm.

`MatchWithValueHandlers` builds the same list from the enum. Wired with `open`, keyed on the input
as the second path segment, it handles a `Shape` by sending each payload back through the context:

```rust
pub struct App;

delegate_components! {
    App {
        open ComputerComponent;

        @ComputerComponent.<Code> Code.[Circle, Rectangle]: ComputeArea,
        @ComputerComponent.<Code> Code.Shape: MatchWithValueHandlers,
    }
}
```

`App` computes a `Circle` or `Rectangle` directly with `ComputeArea`. For a `Shape` it runs
`MatchWithValueHandlers`, whose `UseContext` provider asks `App` again for the payload's type, which
reaches `ComputeArea`. Existing code writes the same table as
`ComputerComponent: UseInputDelegate<new AreaComputers { … }>`.

The builder side, given a provider `BuildFooBar` that produces a `FooBar` record and a provider
`BuildBaz` that computes a `baz` value, assembles a `FooBarBaz`:

```rust
use cgp::extra::dispatch::{BuildAndMerge, BuildAndSetField, BuildWithHandlers};

type Handlers = Product![
    BuildAndMerge<BuildFooBar>,
    BuildAndSetField<Symbol!("baz"), BuildBaz>,
];

let foo_bar_baz = BuildWithHandlers::<FooBarBaz, Handlers>::compute(&context, code, ());
```

`BuildAndMerge<BuildFooBar>` copies `foo` and `bar` from a built `FooBar`, and `BuildAndSetField`
sets `baz`. Dropping either handler leaves a field unset and fails to compile at `finalize_build`.
The [application builder](../../../examples/application-builder.md) example develops this pattern
with `BuildAndMergeOutputs`.

## Related constructs

These constructs are the ones the dispatch combinators work with:

- [`extract_field`](../traits/extract_field.md), [`has_fields`](../traits/has_fields.md), and
  [`cast`](../traits/cast.md): the enum-deconstruction traits behind the matchers.
- [`has_builder`](../traits/has_builder.md): the record-assembly traits behind the builders.
- [Monad providers](monad_providers.md) and [handler combinators](handler_combinators.md):
  `PipeMonadic`, `PipeHandlers`, `UseInputDelegate`, and `PromoteRef`.
- [`UseContext`](use_context.md): the default per-element provider.
- [Dispatching](../../concepts/dispatching.md),
  [extensible variants](../../concepts/extensible-variants.md), and
  [extensible records](../../concepts/extensible-records.md): the concepts these combinators serve.
- [`#[cgp_auto_dispatch]`](../macros/cgp_auto_dispatch.md): generates a matcher-backed trait impl.
- The [extensible shapes](../../../examples/extensible-shapes.md),
  [expression interpreter](../../../examples/expression-interpreter.md), and
  [application builder](../../../examples/application-builder.md) examples.

## Known issues

Some delegation entries in the crate can never resolve, because they point at providers that lack
the needed impl:

- **The borrowed value matchers.** `MatchWithFieldHandlersRef`, `MatchWithValueHandlersRef`, and
  `MatchWithValueHandlersMut` also route `TryComputerComponent`, `HandlerComponent`,
  `TryComputerRefComponent`, and `HandlerRefComponent`. Those entries lead to `MatchWithHandlersRef`
  or `MatchWithHandlersMut`, which implement only `Computer` and `AsyncComputer`, so wiring a
  fallible component to one of these matchers fails with an unsatisfied bound. The owned
  `MatchWithValueHandlers` has the same limit without the misleading entries.
- **`BuildAndMergeOutputs`.** It routes `ComputerRefComponent`, `TryComputerRefComponent`, and
  `HandlerRefComponent` to `BuildWithHandlers`, which implements only `Computer`, `TryComputer`, and
  `Handler`.

Either the entries should be removed, or the matchers should gain fallible impls and the builder a
`PromoteRef` route. Until then, use these providers only for the components they implement.

## Source

- The provider structs live under
  [crates/extra/cgp-dispatch/src/providers/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-dispatch/src/providers/):
  the matchers in `with_handlers/` (`match_with_handlers.rs`, `match_with_handlers_ref.rs`,
  `match_with_handlers_mut.rs`, `match_first_with_handlers*.rs`, `build_with_handlers.rs`), the
  matcher loop alias in `dispatchers/dispatch_matchers.rs`, the field/variant adapters in
  `field_matchers/` (`extract_field.rs`, `extract_first_field.rs`, `extract_handle.rs`,
  `field_value.rs`, `first_field_value.rs`), the convenience matchers and the
  `ToFieldHandlers`/`HasFieldHandlers`/`MapFieldHandler` machinery in `matchers/`
  (`match_with_field_handlers.rs`, `match_first_with_field_handlers.rs`, `to_field_handlers.rs`),
  and the builders in `field_builders/` (`build_and_set_field.rs`, `build_and_merge.rs`) and
  `builders/build_and_merge_outputs.rs`.
- The prelude re-exports the value matchers from
  [crates/main/cgp-extra/src/prelude.rs](https://github.com/contextgeneric/cgp/blob/main/crates/main/cgp-extra/src/prelude.rs);
  the remaining structs are reached through `cgp::extra::dispatch`.
