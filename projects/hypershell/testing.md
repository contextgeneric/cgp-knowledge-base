# Testing

Hypershell's tests live in one place, the `hypershell-examples` crate, and consist of four runtime
tests, while the examples themselves give compile-only coverage to most of the rest. This document
records what each test pins, what the examples add, and what nothing exercises. On the `v0.8.0`
branch, `cargo test --workspace` passes all four tests. The library crates carry no tests of their
own, and there are no doc tests, since the source has no doc comments. The repository has no CI
configuration, so nothing runs the tests automatically.

## What each test pins

The tests are in [`crates/hypershell-examples/tests/`](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-examples/tests),
gathered by a `main.rs` that sets `#![recursion_limit = "256"]`. Each defines its program, and where
it needs one, its context:

| Test | Program | Assertion |
|---|---|---|
| `basic_exec::test_basic_exec` | `SimpleExec` running `echo hello world!` on `HypershellCli` | output equals `hello world!\n` |
| `field::test_join_fields` | `SimpleExec` running `ls -la` on a path joined from a `base_dir` field and two literals | none; the output is printed |
| `field::test_field_args` | `SimpleExec` running `echo` with `FieldArgs<"args">` over a `Vec<&'a str>`, on a context generic over `'a` | output equals `hello world!\n` |
| `pipe::test_simple_pipe` | `ReadFile` of a joined path, `StreamToBytes`, `SimpleExec` running `wc -l`, `BytesToString`, written without the macro | none; the output is printed |

The tests need `echo`, `ls`, and `wc` on the machine, and two resolve paths relative to the crate
directory (`../..`), so they assume `cargo test` runs from the workspace. `test_field_args` is the
only place a context with a lifetime parameter is wired, with
`delegate_components! { <'a> TestApp<'a> { namespace HypershellNamespace; } }`.

## What the examples add

Every example builds as part of `cargo check --workspace --all-targets`, so the examples pin that
their programs type-check against their contexts: HTTP, JSON, files, the checksum and WebSocket
extensions, and the examples library's `Compare` and `If`. They assert nothing at run time, and most
need the network. Running them by hand shows that every example with a confirmed run works.
`rust_playground` was not run, because it publishes a gist, and `compare_and_branch` has no
confirmed run; see [the examples catalog](examples/README.md#running-an-example).

## What is exercised

Taken together, the tests and examples reach the following, in the ways listed:

- **Asserted at run time** — `SimpleExec` with `StaticArg`, `WithStaticArgs`, and `FieldArgs`.
- **Run but not asserted** — `JoinArgs` as a path, `ReadFile`, `StreamToBytes`, `BytesToString`, and
  `Pipe` written by hand.
- **Type-checked only, and run by hand while documenting** — `StreamingExec`, `StreamToStdout`,
  `SimpleHttpRequest`, `StreamingHttpRequest`, `WriteFile`, `EncodeJson`, `DecodeJson`, headers,
  `UrlEncodeArg`, `Checksum`, `BytesToHex`, `WebSocket`, `Compare`, and `If`.

## What is not exercised

Several things no test and no example reaches:

- **Every failure path.** No test runs a failing command, a missing command, a non-success HTTP
  status, a bad URL, or invalid UTF-8, so none of the error messages is pinned, including a streamed
  command's failure.
- **Wiring checks.** No `check_components!` appears anywhere, not for `HypershellCli`,
  `HypershellHttp`, or any bundle. A check over the two contexts and a representative program per
  syntax would catch an unroutable syntax such as `StreamToLines`.
- **Syntax nothing uses.** `ConvertTo`, `Use`, `Box`, `CoreExec` and `CoreHttpRequest` written
  directly, `PutMethod`, `DeleteMethod`, `StreamToLines`, and `ToTokioAsyncRead` appear in no test or
  example.
- **The macro's edges.** Nothing pins the expansion of `hypershell!`, including the nested-pipe
  behavior the compare examples depend on.
- **Redirects.** No test requests a URL that redirects. Only the compare examples do, and they need
  the network.

## Public material derived from this

None yet.
