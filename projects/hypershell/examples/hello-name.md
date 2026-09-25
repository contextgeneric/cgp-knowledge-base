# `hello_name`

`echo` with one argument read from a field of a custom context, showing how a program that is a type
reads a runtime value it cannot hold itself.

- **Source** — [crates/hypershell-examples/examples/hello_name.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/hello_name.rs)
- **Run** — `cargo run --example hello_name`
- **Needs** — `echo`
- **Result** — prints `Hello, Alice`

## The program

```rust
use hypershell::namespaces::HypershellNamespace;
use hypershell::prelude::*;

pub type Program = hypershell! {
        SimpleExec<
            StaticArg<"echo">,
            WithArgs[
                StaticArg<"Hello,">,
                FieldArg<"name">,
            ],
        >
    |   StreamToStdout
};

#[derive(HasField)]
pub struct MyApp {
    pub name: String,
}

delegate_components! {
    MyApp {
        namespace HypershellNamespace;
    }
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    let app = MyApp {
        name: "Alice".to_owned(),
    };

    app.handle(PhantomData::<Program>, Vec::new()).await?;

    Ok(())
}
```

## Context and wiring

`WithArgs` takes a list of argument expressions, unlike `WithStaticArgs`, which takes literals.
`FieldArg<"name">` is resolved through `HasField`, so the context must derive it and have a `name`
field. `MyApp` joins the same namespace as `HypershellCli` and adds only the field. Run on
`HypershellCli` instead, the program fails to compile; through a check, `cargo cgp check` reports
"missing field `name` on `HypershellCli`" as the root cause, as shown in
[debugging](../guides/debugging.md#a-context-lacks-a-field).

## What it demonstrates

- The argument sub-language and `FieldArg`: see [arguments](../reference/arguments.md#fieldarg-and-extractfieldarg).
- A custom context that joins the namespace: see [assembly](../architecture/assembly.md#layer-three-contexts).
- Why a field read here is `HasField` rather than an `#[implicit]` argument: the program chooses
  the field name; see [arguments](../reference/arguments.md#fieldarg-and-extractfieldarg).

## Known issues

The header comment (lines 20–23) says the context is wired with `#[cgp_inherit]` and
`HypershellPreset`, both removed. The code below it uses `namespace HypershellNamespace;`. See
[issues.md](../issues.md#housekeeping).

## Public material derived from this

The variable-parameter program in the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
