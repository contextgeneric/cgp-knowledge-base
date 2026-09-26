# Writing a program

This guide is for someone using Hypershell rather than extending it: how to write a program, choose a
context, feed it input, and check it before running it. The syntax is listed in the
[reference](../reference/README.md), and the running programs in [examples](../examples/README.md)
show each step in context.

## Start from the prelude and a context

**Import `hypershell::prelude::*`, and run the program on `HypershellCli` if it reads no runtime
values.** The prelude brings the syntax, the `hypershell!` macro, the names the macro's expansion
needs, `CanHandle`, `PhantomData`, and the error type. Run the program with `handle`, inside a Tokio
runtime:

```rust
use hypershell::prelude::*;

pub type Program = hypershell! {
        SimpleExec<StaticArg<"echo">, WithStaticArgs["hello", "world!"]>
    |   StreamToStdout
};

#[tokio::main]
async fn main() -> Result<(), Error> {
    HypershellCli.handle(PhantomData::<Program>, Vec::new()).await?;
    Ok(())
}
```

Import the prelude rather than the macro alone. The macro emits `Pipe`, `Product!`, and `Symbol!`
unqualified, so a file without them in scope fails with "cannot find macro `Product`"; see
[the macro reference](../reference/macro.md#known-issues). Use `HypershellHttp` instead when the
program makes HTTP requests and reads no other value; it carries the `http_client` field.

## Read runtime values from a custom context

**A value a program needs at run time lives in a field of the context, named by the program.** A
program is a type, so it cannot hold a URL or a name. Define a struct with the fields, derive
`HasField`, and join `HypershellNamespace`:

```rust
use hypershell::namespaces::HypershellNamespace;
use hypershell::prelude::*;

#[derive(HasField)]
pub struct MyApp {
    pub http_client: reqwest::Client,
    pub url: String,
}

delegate_components! {
    MyApp {
        namespace HypershellNamespace;
    }
}
```

Name the client field `http_client`; the namespace reads the client from a field of exactly that name.
Then reach the fields from the program with the argument syntax:

- **`FieldArg<"name">`** — one value, formatted with `Display`, wherever an argument is expected.
- **`FieldArgs<"args">`** — every item of an iterable field, as a command's whole argument list.
- **`JoinArgs[…]`** — several arguments joined into one. For a URL or header this concatenates,
  and for a command path or file path it joins path segments with `PathBuf::join`.
- **`UrlEncodeArg<…>`** — a value encoded for a URL; use it inside the `JoinArgs` that builds the
  URL, since it is routed only as a string argument.

The details of each are in [arguments](../reference/arguments.md).

## Choose simple or streaming stages

**Use a simple stage when the data is small or a command must finish before the next starts, and a
streaming stage for large data or concurrent processes.** `SimpleExec` and `SimpleHttpRequest` buffer
the whole output and produce bytes. `StreamingExec` and `StreamingHttpRequest` produce a stream at
once, and consecutive streaming stages run in parallel, as in a shell.

The choice affects error reporting. `SimpleExec` fails when the command exits with a non-zero status,
and reports its standard error. `StreamingExec` ignores both, so a failing command in a streaming
stage yields whatever it wrote to standard output; see
[issues.md](../issues.md#streamingexec-ignores-the-exit-status-and-standard-error). A streaming HTTP
request whose body is a stream does not follow redirects, so give such a request the final URL; one
whose input is a `Vec<u8>` or `String` follows them.

## Make adjacent stages agree

**Each stage's output is the next stage's input, and a stage accepts only the input types its wiring
lists.** Most stages accept bytes or any stream, so they chain freely. Three boundaries need an
adapter:

- **A streaming stage before a simple stage** — insert `StreamToBytes`, as in
  `StreamingExec<…> | StreamToBytes | SimpleExec<…>`.
- **An HTTP or WebSocket stream before `StreamToBytes` or `StreamToString`** — insert
  `ToTokioAsyncRead`, imported from `hypershell_tokio_components::dsl`.
- **Raw bytes to print as text** — `BytesToString` decodes UTF-8, and `BytesToHex` encodes bytes such
  as a digest.

The full table of what each stage accepts and produces is in
[streams and input dispatch](../architecture/streams-and-input-dispatch.md#which-stages-accept-which-inputs).

## Pass the right input

**The input argument is the first stage's input, and its type must be one the first stage accepts.**
The common cases are:

- `Vec::<u8>::new()` for a program whose first stage runs a command or sends a request with an empty
  body.
- `()` for a program starting with `ReadFile`, which accepts nothing else.
- A Rust value for a program starting with `EncodeJson`.
- A pair for the examples library's `Compare` and `If`, one input per operand.

Prefer `Vec::<u8>::new()` to `Vec::new()`. When the program fails to type-check, the element type of
a bare `Vec::new()` cannot be inferred, which adds unresolved `_` types to every message.

The program's output type is computed from its last stage, so `handle` on a program ending in
`DecodeJson<Vec<Issue>>` returns a `Vec<Issue>` with no conversion.

## Check the program before running it

**Assert that a context can run a program with `check_components!`, keyed on the program and its
input.** The check forces the whole resolution at the definition, and a failure then carries a root
cause:

```rust
check_components! {
    #[check_trait(CheckMyApp)]
    MyApp {
        HandlerComponent: (Program, Vec<u8>),
    }
}
```

A check lists several programs or inputs as an array, `HandlerComponent: [(A, Vec<u8>), (B, ())]`.
Read failures with `cargo cgp check`; [debugging](debugging.md) shows the common ones. A failure at
the `handle` call itself is often reported without a root cause, which is the practical reason to
check.

## Toolchain

The Hypershell workspace pins nightly Rust with the new trait solver (`-Z next-solver=globally`). A
crate whose programs nest sub-programs should do the same. On stable Rust the simpler examples check,
but the two largest exhausted memory while type-checking; see
[crate layout](../architecture/crate-layout.md#build-facts). The `recursion_limit` attributes some
examples carry are not needed with the pinned toolchain.

## Public material derived from this

The user-facing part of the planned [Hypershell deep dive](../../../website/deep-dives/hypershell.md),
and the getting-started section of the repository README.
