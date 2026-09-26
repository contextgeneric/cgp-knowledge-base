# `compare_and_branch`

A comparison of two checksum sub-pipelines used as the condition of `If`, which runs one of two
`echo` commands.

- **Source** — [crates/hypershell-examples/examples/compare_and_branch.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/compare_and_branch.rs)
- **Run** — `cargo run --example compare_and_branch`
- **Needs** — network, `echo`
- **Result** — compiles; no run is confirmed. It fetches the same two URLs as
  [`parallel_compare`](parallel-compare.md), whose run succeeds. On a slow network, one run was
  stopped after two minutes without output, and a copy with both URLs non-redirecting failed with a
  connection timeout, so whether it prints its message is unconfirmed

## The program

```rust
pub type GetChecksumOf<Url> = hypershell! {
    StreamingHttpRequest<
        GetMethod,
        Url,
        WithHeaders[ ],
    >
    | Checksum<Sha256>
    | BytesToHex
};

pub type Program = hypershell! {
    If<
        Compare<
            GetChecksumOf<FieldArg<"url_a">>,
            GetChecksumOf<FieldArg<"url_b">>,
        >,
        SimpleExec<
            StaticArg<"echo">,
            WithStaticArgs[
                "the checksums are equals",
            ],
        >,
        SimpleExec<
            StaticArg<"echo">,
            WithStaticArgs[
                "the checksums are not equal",
            ],
        >,
    >
    | StreamToStdout
};
```

The context is the same `MyApp` as in `parallel_compare`, joined to `HypershellCompareNamespace`.
`main` passes `((Vec::new(), Vec::new()), Vec::new())`.

## Context and wiring

`If`'s input is a pair of the condition's input and the branch's input, and the condition here is a
`Compare`, whose input is itself a pair. Hence the nested tuple in `main`. Both branches are
`SimpleExec`, so they share the `Vec<u8>` output type `If` requires, and `StreamToStdout` prints it.

## What it demonstrates

- Nesting control syntax: see [the examples library](README.md#the-examples-library) and
  [extending the language](../guides/extending-the-language.md#add-control-syntax).
- Inputs shaped by the program: see [interpretation](../architecture/interpretation.md#handler-is-the-interpreter-interface).

## Known issues

The success message reads "the checksums are equals". The file sets `#![recursion_limit = "512"]`,
which the pinned toolchain does not need. See [issues.md](../issues.md#housekeeping).

## Public material derived from this

None yet.
