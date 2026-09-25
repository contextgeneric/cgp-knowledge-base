# `hello`

The smallest Hypershell program: `echo hello world!` with the output streamed to standard output, run
on the predefined empty context.

- **Source** — [crates/hypershell-examples/examples/hello.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/hello.rs)
- **Run** — `cargo run --example hello`
- **Needs** — `echo`
- **Result** — prints `hello world!`

## The program

```rust
use hypershell::prelude::*;

pub type Program = hypershell! {
        SimpleExec<
            StaticArg<"echo">,
            WithStaticArgs["hello", "world!"],
        >
    |   StreamToStdout
};

#[tokio::main]
async fn main() -> Result<(), Error> {
    HypershellCli
        .handle(PhantomData::<Program>, Vec::new())
        .await?;

    Ok(())
}
```

## Context and wiring

The program uses only static arguments, so it runs on `HypershellCli`, an empty struct whose whole
wiring is `namespace HypershellNamespace;`. The input `Vec::new()` is the command's standard input,
which `echo` ignores. `SimpleExec` produces the output as a `Vec<u8>`, and `StreamToStdout` accepts
bytes as well as streams, so no conversion stage is needed.

## What it demonstrates

- A program is a type, and `hypershell!` is sugar over `Pipe<Product![…]>` and `Symbol!`: see
  [abstract syntax](../architecture/abstract-syntax.md#the-surface-syntax) and
  [the macro reference](../reference/macro.md).
- Running a program is one `handle` call: see [interpretation](../architecture/interpretation.md).
- The one-line context: see [assembly](../architecture/assembly.md#layer-three-contexts).
- `SimpleExec` and `WithStaticArgs`: see [execution](../reference/execution.md).

## Public material derived from this

The opening program on the first page of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
