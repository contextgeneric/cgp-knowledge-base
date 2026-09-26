# Dispatching a component per type

A component that is generic over a type parameter often wants a different provider per value of that parameter, and this guide is about doing that with the `open` statement or a namespace rather than the legacy `UseDelegate` nested table.

This guide connects directly to [organizing wiring with namespaces and prefixes](namespaces-and-prefixes.md), which develops the namespace side of the choice in depth.

## Dispatch per type with `open` and namespaces, not `UseDelegate`

Route a generic-parameter component to a different provider per type with the [`open` statement](../reference/macros/delegate_components.md) or a [namespace](namespaces-and-prefixes.md), rather than the legacy [`UseDelegate`](../reference/providers/use_delegate.md) nested-table pattern. Both the `open` statement and namespaces dispatch through the `RedirectLookup` impl that every [`#[cgp_component]`](../reference/macros/cgp_component.md) already generates, so they store the per-type entries directly on the context and need no wrapper type. The legacy form nests a `UseDelegate` table:

```rust
delegate_components! {
    MyApp {
        AreaCalculatorComponent:
            UseDelegate<new AreaCalculatorComponents {
                Rectangle: RectangleArea,
                Circle: CircleArea,
            }>,
    }
}
```

while dispatching inline with `open`:

```rust
delegate_components! {
    MyApp {
        open AreaCalculatorComponent;

        @AreaCalculatorComponent.Rectangle: RectangleArea,
        @AreaCalculatorComponent.Circle: CircleArea,
    }
}
```

Because `open` and namespaces ride `RedirectLookup`, **a new component you intend to dispatch this way does not need the [`#[derive_delegate(UseDelegate<Param>)]`](../reference/attributes/derive_delegate.md) attribute at all** — that attribute exists only to generate the `UseDelegate` provider the legacy nested-table form relies on. You will still see `#[derive_delegate]` on some CGP-shipped components, such as the error and handler families, which carry it so existing `UseDelegate`-based wiring keeps working; but code that dispatches only through `open` or a namespace can omit it.

Choose between `open` and a namespace by scope. Prefer `open` for a self-contained context wiring its own components directly — it folds the per-type entries into the context's own table with no separate type. Reach for a [namespace](namespaces-and-prefixes.md) when a reusable, inheritable dispatch table is worth sharing across contexts, or when a single generic component is served by several providers whose per-type entries you want to merge into one flat table.

## Dispatch on a later parameter with a longer path key, not `UseInputDelegate`

Dispatch on a component's second or later type parameter with the same `open` statement, writing a path key with one segment per parameter, rather than the legacy [`UseInputDelegate`](../reference/providers/handler_combinators.md#the-legacy-form-useinputdelegate) table. The redirect appends every type parameter of the consumer trait to the path, so for `CanCompute<Code, Input>` the lookup follows `@ComputerComponent.Code.Input`, and a key whose first segment is a per-entry generic ignores the `Code` and dispatches on the input. Written the legacy way, the [expression interpreter](../../examples/expression-interpreter.md)'s evaluator is:

```rust
delegate_components! {
    Interpreter {
        ComputerComponent:
            UseInputDelegate<new EvalComponents {
                MathExpr: DispatchEval,
                Plus<MathExpr>: EvalAdd,
                Times<MathExpr>: EvalMultiply,
                Literal<Value>: EvalLiteral,
            }>,
    }
}
```

and the same dispatch with `open` stores the entries on the context:

```rust
delegate_components! {
    Interpreter {
        open ComputerComponent;

        @ComputerComponent.<Code> Code.MathExpr: DispatchEval,
        @ComputerComponent.<Code> Code.Plus<MathExpr>: EvalAdd,
        @ComputerComponent.<Code> Code.Times<MathExpr>: EvalMultiply,
        @ComputerComponent.<Code> Code.Literal<Value>: EvalLiteral,
    }
}
```

Dispatch on two parameters at once needs no second layer of tables either. Where the legacy form nests a `UseInputDelegate` inside a `UseDelegate` keyed on the operation, a key with a concrete segment for each parameter says the same thing, as in `@ComputerRefComponent.Eval.Plus<MathExpr>: EvalAdd` beside `@ComputerRefComponent.ToLisp.Plus<MathExpr>: BinaryOpToLisp<Symbol!("+")>`.

One rule constrains the conversion. Every path key ends in a wildcard, so a key covers every longer key that shares its segments: within one table, key a first-parameter value either on its own or per later parameter, never both, or the two entries conflict with `E0119`. Keep the shorter key when every value of the later parameter goes to the same provider, and write only the longer keys when they differ. The [Hypershell](../../projects/hypershell/README.md) crates dispatch every handler this way, including input dispatchers packaged as aggregate providers; see its [streams and input dispatch](../../projects/hypershell/architecture/streams-and-input-dispatch.md).

## Related guides

- [Organizing wiring with namespaces and prefixes](namespaces-and-prefixes.md) — the full namespace treatment, including flattening multi-provider dispatch that `open` alone cannot.
- [Guides summary](README.md#summary) — the cheat-sheet across all the guides.
