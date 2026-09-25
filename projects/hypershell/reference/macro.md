# The `hypershell!` macro

`hypershell!` is the function-like procedural macro that gives Hypershell programs their shell-like
surface syntax. It rewrites tokens into the plain type a programmer could write by hand, and has no
knowledge of what any syntax means. It lives in `hypershell-macro`, which depends only on
`proc-macro2` and `quote`, and is re-exported by `hypershell::prelude`. Why the layer is kept this
thin is in [abstract syntax](../architecture/abstract-syntax.md#the-surface-syntax).

## Definition

```rust
#[proc_macro]
pub fn hypershell(body: TokenStream) -> TokenStream
```

The body is any sequence of Rust tokens forming a type once rewritten. The macro is used in type
position, as `pub type Program = hypershell! { … };` or as a type argument.

## Behavior

The macro first regroups the input so that `<` and `>` delimit groups, since Rust's token trees treat
angle brackets as punctuation, and then applies four rules, recursively inside every group:

- **A `|` splits the enclosing group into pipeline stages.** Two or more stages become
  `Pipe<Product![stage, stage, …]>`, and a single stage is emitted as itself, so
  `hypershell! { StreamToStdout }` is `StreamToStdout`.
- **A bracketed group right after an identifier becomes a `Product!` type argument.**
  `WithStaticArgs["a", "b"]` becomes `WithStaticArgs<Product![Symbol!("a"), Symbol!("b")]>`, and
  `WithHeaders[]` becomes `WithHeaders<Product![]>`, which is `WithHeaders<Nil>`.
- **A string literal becomes `Symbol!("…")`.** Any other literal passes through unchanged, so a
  number in type position is a parse error.
- **Every other token passes through**, and every other group is emitted with its own delimiters.

Because the rules recurse, a `|` inside angle brackets builds a nested pipeline. The compare examples
rely on this to pass a sub-pipeline as a type argument:

```rust
pub type GetChecksumOf<Url> = hypershell! {
    StreamingHttpRequest<GetMethod, Url, WithHeaders[ ]>
    | Checksum<Sha256>
    | BytesToHex
};
```

A probe confirmed each rule by type equality against the hand-written form, including
`Box< A | B >` becoming `Box<Pipe<Product![A, B]>>`.

## Known issues

Four edges were confirmed by probes, and each is recorded in [issues.md](../issues.md#the-hypershell-macro):

- **The expansion is unhygienic.** `Pipe`, `Product!`, and `Symbol!` are emitted as bare names, so
  they must be in scope at the use site. Importing the macro and the syntax types without the prelude
  fails with "cannot find macro `Product` in this scope" and "cannot find type `Pipe` in this scope".
- **An unbalanced `<` panics the macro**, reported as "proc macro panicked" with the message
  `mismatch > at the end of token stream`, rather than as a spanned error.
- **`|` splits at the token level, not per list element.** Inside a bracket list, a `|` makes the
  whole list one pipeline: `WithArgs[a, b | c]` becomes `WithArgs<Product![Pipe<Product![a, b, c]>]>`,
  not a two-element list.
- **Any `>` closes the innermost angle group**, so a type written with `->`, such as a function
  pointer, is misparsed. `hypershell! { ConvertTo<fn() -> u8> }` fails with "expected one of `!`,
  `(`, `,`, `::`, `<`, or `>`, found `<eof>`". No program in the repository uses one.

## Source

- [crates/hypershell-macro/src/lib.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-macro/src/lib.rs)
- [crates/hypershell-macro/src/expand.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-macro/src/expand.rs)

## Public material derived from this

The desugaring section of page 1 of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md), and the macro's rustdoc.
