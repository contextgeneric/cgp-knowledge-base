# The hand-written expansion

`src/greet_expanded.rs` writes out by hand the items `#[cgp_component(Greeter)]` generates for
`CanGreet`, but it is a simplified, older form: its consumer blanket impl routes through the wiring
table instead of through the provider trait, and it leaves out two of the macro's provider impls.

- **Source** — [src/greet_expanded.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/greet/src/greet_expanded.rs)
- **Run** — nothing uses it; it is the library's only module, and no binary imports it
- **Needs** — nothing
- **Result** — compiles. A probe wired a context through it and printed `Hello, Alice!`, and a second
  probe showed where it and the macro part ways

## What it defines

The module declares the items a reader meets first in any component: the marker, the consumer trait,
the provider trait with its `IsProviderFor` supertrait, and the two blanket impls that connect them.
The provider blanket impl matches the macro's. The consumer blanket impl does not:

```rust
impl<Context> CanGreet for Context
where
    Context: DelegateComponent<GreeterComponent>,
    Context::Delegate: Greeter<Context>,
{
    fn greet(&self) {
        Context::Delegate::greet(self)
    }
}
```

## How it differs from the macro

`cargo cgp expand -p cgp-example-greet --bin greet-component` shows what the macro emits for the same
trait. Three differences matter:

| Item | `greet_expanded.rs` | The macro |
|---|---|---|
| Consumer blanket impl | requires `Context: DelegateComponent<GreeterComponent>` and calls the delegate | requires `Context: Greeter<Context>` and calls the context's own provider impl |
| `UseContext` impl of `Greeter` | absent | present, for any context that implements `CanGreet` |
| `RedirectLookup` impl of `Greeter` | absent | present, which `open` and namespaces rely on |

The macro also emits the marker last rather than first, which changes nothing. The full list of
generated items is in [`#[cgp_component]`](../../../cgp/reference/macros/cgp_component.md#expansion).

The consumer impl is the difference a reader can observe. For a context that delegates the component
the two forms agree: the probe wired a `Person` to a hand-written `GreetHello` through the module's
traits, and `greet` ran. They disagree for a context that implements the provider trait for itself
with no wiring entry:

```rust
pub struct Robot;

impl Greeter<Robot> for Robot {
    fn greet(_context: &Robot) {
        println!("Beep.");
    }
}

impl IsProviderFor<GreeterComponent, Robot, ()> for Robot {}
```

Against the macro's component, `Robot.greet()` prints `Beep.`, because the consumer impl needs only
`Robot: Greeter<Robot>`. Against the module's traits the call does not compile, because the consumer
impl needs a wiring entry `Robot` does not have:

```text
error[E0599]: the method `greet` exists for struct `Robot`, but its trait bounds were not satisfied
  |
5 | pub struct Robot;
  | ---------------- method `greet` not found for this struct because it doesn't satisfy `Robot: cgp_example_greet::greet_expanded::CanGreet` or `_: DelegateComponent<GreeterComponent>`
```

So the module teaches that a consumer trait is implemented only through the wiring table, while the
macro implements it for any context that provides the component, wired or not.

## Known issues

- **It does not match the macro** — see [issues.md](issues.md#housekeeping).

## Public material derived from this

None yet.
