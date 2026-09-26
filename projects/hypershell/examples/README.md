# Hypershell examples

This directory documents each runnable program in the repository's `hypershell-examples` crate: what
it does, the program and context it defines, what it needs on the machine to run, whether it works,
and which parts of the architecture and reference it demonstrates. It also documents the small
library the crate carries, which two of the examples build on.

## How these differ from the top-level example

**These documents are records of the repository's programs; the top-level
[shell-scripting DSL example](../../../examples/shell-scripting-dsl.md) is the teaching progression
to quote.** That example develops the language step by step for an agent writing a tutorial or a
page, and imports the Hypershell crates to do it. The documents here each describe one program as the
repository ships it, including its defects, so an agent quoting a program knows
what it is quoting. When the two overlap, as for the checksum extension, the top-level example owns
the explanation and a document here links to it.

## Running an example

Examples run from the repository root with `cargo run --example <name>`. The workspace builds only
beside a `cgp` checkout at `../cgp`, and uses the pinned nightly toolchain; see
[crate layout](../architecture/crate-layout.md#build-facts). The table records what each example
needs beyond that, and what happened when it was run against the `v0.8.0` branch:

| Example | Needs | Result |
|---|---|---|
| [`hello`](hello.md) | `echo` | prints `hello world!` |
| [`hello_name`](hello-name.md) | `echo` | prints `Hello, Alice` |
| [`http_checksum_cli`](http-checksum-cli.md) | network, `curl`, `sha256sum`, `cut` | prints the page's SHA-256 digest |
| [`http_checksum_client`](http-checksum-client.md) | network, `sha256sum`, `cut` | prints the same digest |
| [`http_checksum_native`](http-checksum-native.md) | network | prints the same digest |
| [`nix_manual`](nix-manual.md) | network, `tr`, `grep` | prints the matching lines in upper case |
| [`save_webpage`](save-webpage.md) | network | writes `nix_manual.html` in the working directory |
| [`github_issues`](github-issues.md) | network, GitHub API access | prints the open issues of `rust-lang/rust` |
| [`rust_playground`](rust-playground.md) | network | not run: it publishes a public gist |
| [`bluesky`](bluesky.md) | network, `nix-shell` | streams matching firehose events until stopped |
| [`bluesky_websocket`](bluesky-websocket.md) | network, `grep` | streams matching firehose events until stopped |
| [`parallel_compare`](parallel-compare.md) | network | prints `equals: true` |
| [`compare_and_branch`](compare-and-branch.md) | network | compiles; no confirmed run |

## The catalog

The order is the order the examples teach in, from a static command to a language extension.

- [hello.md](hello.md) — `echo hello world!` on the empty `HypershellCli` context.
- [hello-name.md](hello-name.md) — a runtime argument read from a context field with `FieldArg`.
- [http-checksum-cli.md](http-checksum-cli.md) — `curl | sha256sum | cut` as three streaming stages.
- [http-checksum-client.md](http-checksum-client.md) — the same with a native streaming HTTP request.
- [http-checksum-native.md](http-checksum-native.md) — the same with the checksum extension instead
  of the two commands.
- [nix-manual.md](nix-manual.md) — a native request feeding two commands, with a mixed argument list.
- [save-webpage.md](save-webpage.md) — a streaming request written to a file.
- [github-issues.md](github-issues.md) — a URL built from joined and encoded fields, a header, and
  JSON decoding into a Rust type.
- [rust-playground.md](rust-playground.md) — a Rust value encoded to JSON, posted, and decoded, on
  `HypershellHttp`.
- [bluesky.md](bluesky.md) — a long-running stream from a command provisioned by `nix-shell`.
- [bluesky-websocket.md](bluesky-websocket.md) — the same with the WebSocket extension, wired on the
  context.
- [parallel-compare.md](parallel-compare.md) — two sub-pipelines run concurrently and compared, with
  the examples library's `Compare`.
- [compare-and-branch.md](compare-and-branch.md) — a comparison driving `If` to choose between two
  commands.

## The examples library

The `hypershell-examples` crate is a library as well as a set of examples. Its `src/` defines a
two-syntax extension and the namespaces that layer the hash crate and that extension onto the base
language. The `http_checksum_native` example and the two compare examples use it.

**`Compare<CodeA, CodeB>` runs two programs concurrently and produces whether their outputs are
equal.** Its input is a pair, one input per program, and both programs must have the same `Eq`
output type:

```rust
pub struct Compare<CodeA, CodeB>(pub PhantomData<(CodeA, CodeB)>);

#[cgp_impl(new HandleCompare)]
impl<Context, CodeA, CodeB, InputA, InputB, Output> Handler<Compare<CodeA, CodeB>, (InputA, InputB)>
    for Context
where
    Context: CanHandle<CodeA, InputA, Output = Output> + CanHandle<CodeB, InputB, Output = Output>,
    Output: Eq,
{
    type Output = bool;
    // ...
}
```

The provider starts both handlers and awaits them with `futures::try_join!`, so the first error
cancels the comparison.

**`If<CodeCond, CodeThen, CodeElse>` runs a condition program and then one of two branch programs.**
Its input is a pair of the condition's input and the branch's input, the condition must produce a
`bool`, and both branches must produce the same type:

```rust
pub struct If<CodeCond, CodeThen, CodeElse>(pub PhantomData<(CodeCond, CodeThen, CodeElse)>);

#[cgp_impl(new HandleIf)]
impl<Context, CodeCond, CodeThen, CodeElse, InputCond, InputBranch, Output>
    Handler<If<CodeCond, CodeThen, CodeElse>, (InputCond, InputBranch)> for Context
where
    Context: CanHandle<CodeCond, InputCond, Output = bool>
        + CanHandle<CodeThen, InputBranch, Output = Output>
        + CanHandle<CodeElse, InputBranch, Output = Output>,
{ /* ... */ }
```

Both providers interpret their sub-programs by calling back into the context, so any program the
context can run may appear as an operand. They are the repository's worked instance of adding
control syntax, described in [extending the language](../guides/extending-the-language.md).

**Two namespaces layer the extensions.** Each inherits the one before it:

```rust
cgp_namespace! {
    new HypershellChecksumNamespace: HypershellNamespace {
        @cgp.extra.handler.HandlerComponent.[
            <Hasher> Checksum<Hasher>,
            BytesToHex,
        ]:
            HypershellChecksumProvider,
    }
}

cgp_namespace! {
    new HypershellCompareNamespace: HypershellChecksumNamespace {
        // Note: The compare handler is somehow much slower when the future is not boxed
        @cgp.extra.handler.HandlerComponent.<CodeA, CodeB> Compare<CodeA, CodeB>:
            BoxHandler<HandleCompare>,

        @cgp.extra.handler.HandlerComponent.<CodeCond, CodeThen, CodeElse> If<CodeCond, CodeThen, CodeElse>:
            HandleIf,
    }
}
```

`HypershellChecksumProvider` is the bundle the hash crate does not ship: it `open`s
`HandlerComponent` and wires `Checksum` to
`PipeHandlers<Product![HandleToFuturesStream, HandleStreamChecksum]>` and `BytesToHex` to
`HandleBytesToHex`. The comment on `Compare` does not
say whether "slower" means compile time or run time, and nothing measures it.

## Public material derived from this

The worked extension on page 4, "Extending the language", of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md), and the examples section of the
repository README.
