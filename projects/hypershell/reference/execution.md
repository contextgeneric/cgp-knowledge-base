# Process execution

The execution family runs external commands on Tokio. Two user-facing syntaxes, `SimpleExec` and
`StreamingExec`, differ in whether the process's input and output are buffered or streamed, and both
delegate spawning to an internal `CoreExec` step. The command's arguments are applied by the
`CommandUpdater` component. Everything here lives in `hypershell-tokio-components`, except the syntax
types, which are in `hypershell-components`. The design is in
[interpretation](../architecture/interpretation.md) and
[streams and input dispatch](../architecture/streams-and-input-dispatch.md).

## `SimpleExec` and `HandleSimpleExec`

`SimpleExec<Path, Args>` runs a command to completion, writing its input to the command's standard
input and producing the command's standard output as bytes.

### Definition

```rust
pub struct SimpleExec<Path, Args>(pub PhantomData<(Path, Args)>);

#[cgp_impl(new HandleSimpleExec)]
impl<Context, CommandPath, Args, Input> Handler<SimpleExec<CommandPath, Args>, Input> for Context
where
    Context: CanHandle<CoreExec<CommandPath, Args>, (), Output = Child>
        + for<'a> CanRaiseError<ExecOutputError>
        + CanWrapError<StdinPipeError>
        + CanWrapError<WaitWithOutputError>
        + CanRaiseError<std::io::Error>,
    Input: Send + AsRef<[u8]>,
{
    type Output = Vec<u8>;

    async fn handle(
        context: &Context,
        _tag: PhantomData<SimpleExec<CommandPath, Args>>,
        input: Input,
    ) -> Result<Vec<u8>, Context::Error> { ... }
}
```

### Behavior

The provider spawns the process through `CoreExec`, writes the input to standard input if the input
is non-empty, and waits for the process to exit. On a zero exit status it returns the captured
standard output. On any other status it raises `ExecOutputError`, which carries the whole
`std::process::Output`; its message gives the exit code and the captured standard error, as in
`child process exited with non-success code Some(1), stderr: `. A failure to write standard input or
to wait is raised as the `std::io::Error` and wrapped with `StdinPipeError` or
`WaitWithOutputError`.

Any byte-like input works, since the bound is `AsRef<[u8]>`: `Vec<u8>`, `String`, `&str`, or the
output of `EncodeJson` or `BytesToHex`. A stream does not; place `StreamToBytes` before a
`SimpleExec` that follows a streaming stage.

### Context dependencies

`CanHandle<CoreExec<CommandPath, Args>, ()>` with `Output = Child`, which brings in everything
`HandleCoreExec` needs, plus the four error bounds above.

### Known issues

The `for<'a>` on `CanRaiseError<ExecOutputError>` binds a lifetime nothing uses; see
[issues.md](../issues.md#housekeeping).

## `StreamingExec` and `HandleStreamingExec`

`StreamingExec<Path, Args>` spawns a command and returns its standard output as a stream while its
input is copied into standard input concurrently, so consecutive streaming stages run in parallel.

### Definition

```rust
pub struct StreamingExec<Path, Args>(pub PhantomData<(Path, Args)>);

#[cgp_impl(new HandleStreamingExec)]
impl<Context, CommandPath, Args, Input> Handler<StreamingExec<CommandPath, Args>, Input> for Context
where
    Context:
        CanHandle<CoreExec<CommandPath, Args>, (), Output = Child> + CanRaiseError<std::io::Error>,
    Input: Send + Unpin + AsyncRead + 'static,
{
    type Output = ChildOutputStream;

    async fn handle(
        context: &Context,
        _tag: PhantomData<StreamingExec<CommandPath, Args>>,
        mut input: Input,
    ) -> Result<ChildOutputStream, Context::Error> { ... }
}

pub struct ChildOutputStream { /* the child's stdout, and the tasks feeding stdin and awaiting exit */ }

pub struct ChildExitError {
    pub status: ExitStatus,
    pub stderr: Vec<u8>,
}
```

### Behavior

The provider spawns the process through `CoreExec` and returns its standard output at once as a
`ChildOutputStream`. Building the stream starts two Tokio tasks: one copies the input into the child's
standard input, and one drains standard error and waits for the child to exit, so a child writing a
lot to standard error cannot block. The stream reports a failure when its standard output ends:

- **A failed input** ends the stream with the error from reading the previous stage's output, so an
  upstream failure reaches the stage that reads this one. The copying task records the error before
  it closes the child's standard input, so the error is in place before the child can react to the
  end of its input. A child that exits before reading all of its input breaks the pipe, which is not
  an error, and a copying task still waiting on input once the child has exited is aborted.
- **A non-success exit** ends the stream with an `io::Error` carrying a `ChildExitError`, whose
  message gives the exit code and standard error, as
  `child process exited with non-success code Some(3), stderr: err`.

The stage that reads the stream raises that error through its own `CanRaiseError<std::io::Error>`,
so the program fails. A probe confirmed each case, including a command writing a megabyte to
standard error, which completed, and a child that ignored an input stream which never ends, which
finished once the child exited. Under the namespace's wiring, the provider sits between an input
dispatcher and an output wrapper:

```rust
PipeHandlers<Product![HandleToTokioAsyncRead, HandleStreamingExec, WrapTokioAsyncRead]>
```

So the syntax accepts `Vec<u8>`, `String`, `TokioAsyncReadStream`, or `FuturesAsyncReadStream`, and
produces `TokioAsyncReadStream<ChildOutputStream>`. The stream's tasks are started with
`tokio::spawn`, so the stage must run inside a Tokio runtime.

### Context dependencies

`CanHandle<CoreExec<CommandPath, Args>, ()>` with `Output = Child`, and `CanRaiseError<std::io::Error>`.

## `CoreExec` and `HandleCoreExec`

`CoreExec<Path, Args>` is the internal step both execution syntaxes delegate to: it builds a Tokio
`Command` from the path and arguments and spawns it with all three standard streams piped.

### Definition

```rust
pub struct CoreExec<Path, Args>(pub PhantomData<(Path, Args)>);

#[cgp_impl(new HandleCoreExec)]
impl<Context, CommandPath, Args> Handler<CoreExec<CommandPath, Args>, ()> for Context
where
    Context: HasErrorType
        + CanExtractCommandArg<CommandPath>
        + CanUpdateCommand<Args>
        + CanRaiseError<std::io::Error>
        + for<'a> CanWrapError<CommandNotFound<'a>>
        + for<'a> CanWrapError<SpawnCommandFailure<'a>>,
    Context::CommandArg: AsRef<OsStr>,
{
    type Output = Child;

    async fn handle(
        context: &Context,
        _tag: PhantomData<CoreExec<CommandPath, Args>>,
        _input: (),
    ) -> Result<Child, Context::Error> { ... }
}
```

### Behavior

The command path is extracted with `CanExtractCommandArg`, so it may be any argument syntax the
context routes for that extractor, and the arguments are applied with `CanUpdateCommand<Args>`. A
spawn failure is raised as the `std::io::Error` and wrapped with `SpawnCommandFailure`, which
formats the program and its arguments. When the error kind is `NotFound` it is first wrapped with
`CommandNotFound`, which formats the program name. A missing command therefore reports as
`error executing command: <cmd> <args>`, caused by `command not found: <cmd>`, caused by the OS
error. The syntax takes `()` as input and is not exported from the prelude; it is reached only
through the two execution providers, or from `hypershell_tokio_components::dsl`.

### Context dependencies

The command-argument extractor for `CommandPath`, the command updater for `Args`, a `CommandArg`
type that is `AsRef<OsStr>` (`PathBuf` under the Tokio bundle), and the raise and wrap bounds above.

## `CanUpdateCommand` and `CommandUpdater`

`CanUpdateCommand<Args>` is the component that applies an argument-list syntax to a Tokio `Command`.

### Definition

```rust
#[cgp_component(CommandUpdater)]
#[prefix(@hypershell.tokio in DefaultNamespace)]
#[derive_delegate(UseDelegate<Args>)]
pub trait CanUpdateCommand<Args> {
    fn update_command(&self, _phantom: PhantomData<Args>, command: &mut Command);
}
```

### Behavior

The method mutates the command in place and cannot fail. The interface is tied to
`tokio::process::Command` on purpose; only the Tokio providers depend on it. It is registered at
`@hypershell.tokio.CommandUpdaterComponent`. The `#[derive_delegate]` attribute generates a legacy
`UseDelegate` dispatcher that nothing in the repository uses.

## `WithArgs`, `WithStaticArgs`, and `ExtractArgs`

`WithArgs<Args>` appends each argument in a `Product!` list to the command, and `WithStaticArgs<Args>`
is shorthand for a list of literals.

### Definition

```rust
pub struct WithArgs<Args>(pub PhantomData<Args>);

pub type WithStaticArgs<Args> = WithArgs<<Args as WrapStaticArg>::Wrapped>;

pub struct ExtractArgs;

#[cgp_impl(ExtractArgs)]
impl<Context, Arg, Args> CommandUpdater<WithArgs<Cons<Arg, Args>>> for Context
where
    Context: CanExtractCommandArg<Arg>,
    Context::CommandArg: AsRef<OsStr> + Send,
    Self: CommandUpdater<Context, WithArgs<Args>>,
{
    fn update_command(
        context: &Context,
        _phantom: PhantomData<WithArgs<Cons<Arg, Args>>>,
        command: &mut Command,
    ) { ... }
}

#[cgp_impl(ExtractArgs)]
impl<Context> CommandUpdater<WithArgs<Nil>> for Context {
    fn update_command(
        _context: &Context,
        _phantom: PhantomData<WithArgs<Nil>>,
        _command: &mut Command,
    ) { ... }
}
```

### Behavior

Each element is extracted as a command argument through the context and passed to `Command::arg`, in
order. An element may be any argument syntax the command extractor routes: `StaticArg`, `FieldArg`,
or `JoinArgs`, which joins path segments. `WithStaticArgs` maps `Product![A, B]` to
`Product![StaticArg<A>, StaticArg<B>]` through `WrapStaticArg`, so the two are the same type, and
error messages print the expanded `WithArgs` form.

### Context dependencies

The command-argument extractor for each element.

## `FieldArgs` and `ExtractFieldArgs`

`FieldArgs<Tag>` appends every item of an iterable context field as a command argument.

### Definition

```rust
pub struct FieldArgs<Tag>(pub PhantomData<Tag>);

#[cgp_impl(new ExtractFieldArgs)]
impl<Context, Tag> CommandUpdater<FieldArgs<Tag>> for Context
where
    Context: HasField<Tag>,
    for<'a> &'a Context::Value: IntoIterator<Item: AsRef<OsStr>>,
{ ... }
```

### Behavior

The field is borrowed and passed to `Command::args`, so a `Vec<String>` or `Vec<&str>` field works.
A probe with `args: vec!["x", "y"]` under `echo` printed `x y`. `FieldArgs` is argument-list syntax
and replaces the whole `WithArgs`: `SimpleExec<StaticArg<"echo">, FieldArgs<"args">>`.

### Context dependencies

`HasField<Tag>` for a field whose borrow iterates over `AsRef<OsStr>` items.

## Error types

The execution providers define five error and detail types, each with a `Debug` impl that writes its
message:

- **`ExecOutputError { output: Output }`** — raised by `HandleSimpleExec` for a non-zero exit;
  `child process exited with non-success code {code:?}, stderr: {stderr}`.
- **`StdinPipeError`** — wraps a failed write to standard input;
  `error piping input to stdin of child process`.
- **`WaitWithOutputError`** — wraps a failed wait; `error waiting for output from child process`.
- **`CommandNotFound<'a> { command: &'a Command }`** — wraps a spawn failure of kind `NotFound`;
  `command not found: {program}`.
- **`SpawnCommandFailure<'a> { command: &'a Command }`** — wraps every spawn failure;
  `error executing command: {program} {args}`.

`ExecOutputError` is raised, so it needs an `ErrorRaiser` route, which `HypershellNamespace` gives it
(`DebugAnyhowError`). The other four are details, handled by the namespace's single
`ErrorWrapperComponent` binding. See [error handling](../architecture/error-handling.md).

A sixth type, `ChildExitError { status: ExitStatus, stderr: Vec<u8> }` in
`hypershell_tokio_components::types`, is not raised through the context. `ChildOutputStream` returns
it inside an `io::Error` when a streamed command exits with a non-success status, with the same
message as `ExecOutputError`, and the stage that reads the stream raises the `io::Error`.

## Wiring

`HypershellTokioProvider` maps `SimpleExec` to `HandleSimpleExec`, `CoreExec` to `HandleCoreExec`,
and `StreamingExec` to the three-stage pipeline above; `WithArgs` to `ExtractArgs` and `FieldArgs`
to `ExtractFieldArgs` under `CommandUpdaterComponent`; and `CommandArgTypeProviderComponent` to
`UseType<PathBuf>`. `HypershellNamespace` routes all of them to that bundle, under
`@cgp.extra.handler.HandlerComponent`, `@hypershell.tokio.CommandUpdaterComponent`, and
`@hypershell.core.CommandArgTypeProviderComponent`.

## Source

- [crates/hypershell-components/src/dsl/exec.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/exec.rs)
- [crates/hypershell-components/src/dsl/args.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/args.rs)
- [crates/hypershell-tokio-components/src/dsl/exec.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/dsl/exec.rs)
- [crates/hypershell-tokio-components/src/components/update_command.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/components/update_command.rs)
- [crates/hypershell-tokio-components/src/providers/simple_exec.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/simple_exec.rs)
- [crates/hypershell-tokio-components/src/providers/streaming_exec.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/streaming_exec.rs)
- [crates/hypershell-tokio-components/src/providers/core_exec.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/core_exec.rs)
- [crates/hypershell-tokio-components/src/providers/update_command.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/update_command.rs)

## Public material derived from this

Rustdoc for the execution items, and the worked provider on page 2 of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
