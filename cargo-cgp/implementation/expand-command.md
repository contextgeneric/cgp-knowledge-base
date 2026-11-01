# The expand command

`cargo cgp expand` shows a CGP programmer the ordinary Rust their CGP macros generate: a full macro
expansion in the style of `cargo-expand`, with CGP's type-level sugar resugared by the driver, so a field
name reads as `Symbol!("height")` rather than as a six-deep `Chars` list. It reuses the split in
[Executable structure](executable-structure.md) and adds a second hook to the callbacks in
[The driver](driver/program.md). Its reference implementation is `cargo-expand`, checked out read-only at
[`../external/cargo-expand`](../../../external/cargo-expand), rather than Clippy.

## What the command shows

The command answers one question: what did that macro generate? CGP is macro-heavy, so most of what the
compiler type-checks is code nobody wrote, and reading it confirms a wiring table means what was intended
or shows why a provider needs a bound. Take a rectangle whose fields an auto-getter reads:

```rust
#[cgp_auto_getter]
pub trait HasRectangleFields {
    fn width(&self) -> f64;
    fn height(&self) -> f64;
}
```

Expanded and resugared, its blanket impl reads the way the programmer thinks about it:

```rust
impl<__Context__> HasRectangleFields for __Context__
where
    __Context__: HasField<Symbol!("width"), Value = f64>,
    __Context__: HasField<Symbol!("height"), Value = f64>,
{
    fn width(&self) -> f64 {
        self.get_field(::core::marker::PhantomData::<Symbol!("width")>).clone()
    }
    …
}
```

Without the resugaring, each bound is a list of characters that the compiler's printer line-breaks
mid-list. This is the same difference the [diagnostic resugaring](error-processing.md) makes to an error
message.

**Expanding is not checking.** The driver stops once expansion is done, so type analysis never runs:
a type error or a wiring mistake goes unreported, and the command exits 0. `cargo cgp check` remains
the diagnostic command. An error reported during expansion or name resolution behaves as
[the failure cases](#how-a-run-fails) describe.

## Why the whole crate is expanded

The command expands everything because `rustc` offers no way to expand selectively. Expansion is a
whole-crate fixed point, driven to completion before anything can look at the result, and
`-Zunpretty=expanded` only prints the finished AST: its `PpSourceMode`
([`rustc_session/src/config.rs`](../../../external/rust/compiler/rustc_session/src/config.rs)) has
no mode that filters by macro. No driver callback sits inside expansion, and
`after_crate_root_parsing` runs before submodules are parsed. The only route to selectivity is
*un*-expansion, which the tool does not do
([the limitation](#known-limitation-every-macro-is-expanded)).

## The front-end: the `expand` subcommand

**It runs `cargo rustc`, not `cargo check`,** because the driver must be told which crate to expand, and
`cargo rustc` is the one subcommand that appends rustc arguments to a *single* target's invocation:

```text
cargo rustc <forwarded args> --profile check --target-dir <dir> -- --cgp-expand=<output path>
```

The marker flag after `--` reaches only the selected target, so its dependencies, including workspace
siblings that also go through the driver, compile normally and produce their metadata. An environment
variable would reach every workspace crate at once, and the driver would have to reconstruct the user's
choice from `--crate-name`. `--profile check` skips codegen, and is left out when the caller chose a
profile.

A `--` of the user's own stays the one separator: the flags the tool adds for cargo go in front of
it, and the marker flags follow the user's rustc flags after it. The arguments after it are rustc's,
so the front-end reads none of them. `--item` there is rustc's unknown option, and `--help` there
prints rustc's help. Everything else about the launch is the
[wrapped command](executable-structure.md) `check` runs, shared rather than copied.

**Target selection is cargo's.** `cargo rustc` requires exactly one target, so the front-end forwards
`--lib`, `--bin`, `-p`, `--features`, and the rest, and cargo's own error tells the user to disambiguate.

**`expand` answers `--help` itself,** unlike `check`, because `cargo rustc --help` never mentions
`--item`, and the run would then report a help request as a failed expansion.

**`--item <path>` is the one argument the front-end does not forward.** It travels to the driver as
a second marker flag, `--cgp-expand-item=<path>`. It is a flag rather than the bare positional
`cargo-expand` accepts, because a bare word cannot be told from the value of a cargo flag
(`--bin my_module`) without re-declaring cargo's whole grammar, which forwarding exists to avoid.
The front-end checks the path's shape before anything compiles, so a typo costs nothing, and the
driver parses it again for real. A leading `crate::`, `self::`, or `::` is dropped, since `crate::…`
is how a reader spells a module.

Three rules decide what a path selects, and the third is the CGP-shaped one:

- an item **declared** at that path, where a module selects its *contents*;
- an `impl` whose **self type** is that path, so `--item Rectangle` shows the struct with its `HasField`
  impls and its wiring;
- an `impl` whose **trait** is that path, so `--item AreaCalculator` shows a component's provider
  trait with the blanket impls and each provider's impl.

A CGP component's generated items are almost all impls, which have no names of their own, so a filter on
declarations alone would answer "what does this component generate?" with just the trait. The impl rules
also reach an impl inside an unnamed constant's block, `const _: () = { … };`, the shape many third-party
derives emit. Selecting one selects its whole block, because the impl's paths resolve through the block's
imports.

**The driver writes the text to a file, and the front-end prints it.** The file sits in a directory
created exclusively for the one run under the system temp directory (mode 0700 on Unix) and removed
afterward. A fixed name in the shared temp directory would let another user place a symlink for the
driver's write to follow, and a fresh directory means no earlier run's output can be printed by
mistake. Using a file rather than stdout keeps the content from interleaving with cargo's progress,
and leaves the front-end relaying output without parsing it.

## How a run fails

Each layer reports what it knows, and the front-end only says that nothing came back, because it
sees only an absent expansion. Guessing at a cause would contradict cargo's correct explanation
when, say, a package with several targets needs `--lib`. The exit code keeps any failure in cargo's,
and a run with nothing to print is never 0. [`expansion_exit_code`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/src/expand/command.rs)
decides it, and running each case gave:

| Run | Expansion printed | Exit code |
| --- | --- | --- |
| A clean crate, or one with a type error or a wiring mistake | yes | 0 |
| A CGP macro rejecting its input, `compile_error!`, a wiring entry or import naming nothing, a missing module file, or a syntax error the parser recovers from | what expanded | cargo's 101 |
| A type defined twice, a `macro_rules!` call matching no rule, or an unclosed delimiter | no | cargo's 101 |
| Several targets and none selected | no | cargo's 101 |
| An `--item` path that matches nothing | no | 1 |

The second row surprises readers: the compilation reaches `after_expansion` after those errors, and
the listing omits what the failed macro would have generated. The third row's `macro_rules!` case
differs because a call matching no rule counts in `nb_macro_errors`, on which rustc aborts after
expansion ([`rustc_interface/src/passes.rs`](../../../external/rust/compiler/rustc_interface/src/passes.rs)),
while the CGP macros' rejections, in the runs above, do not stop it. The driver's reshaping of
name-resolution errors runs only in a check, so those errors print as rustc wrote them.

The driver prints the `--item` miss straight to stderr rather than as a diagnostic, for two reasons.
It is not about the code, so it should not fail the compilation in cargo's eyes. And the
[post-processing](error-processing.md) would rewrite it: the module-path strip would turn the quoted
`contexts::nope` into `nope`.

An expansion that `syn` cannot parse comes back whole even when `--item` asked for less, because the
filter works on the parsed tree.

A reader that closes the pipe early, as `head` does, is not a failure, so the command then exits with
cargo's code; any other write error reports. A forwarded `--message-format=json` puts cargo's JSON on
stdout ahead of the expansion, since stdout is inherited.

Cargo re-runs the expanded unit on each invocation, and a `cargo cgp check` in the same target
directory afterward re-checks the crate normally.

## The driver: expand mode

The driver strips its two flags first, since neither is rustc's, and records them as its expand
request. The pair is the second half of the contract between the executables, alongside
`CARGO_CGP_SYSROOT`, and each crate's `config` declares the spelling independently. The item flag is
taken even without the mode flag, so a stray one never reaches the compiler.

**The driver must not set `-Zunpretty=expanded`, and this is the most important fact in this
document.** When `sess.opts.pretty` is set, `compiler_entrypoint`
([`rustc_driver_impl/src/lib.rs`](../../../external/rust/compiler/rustc_driver_impl/src/lib.rs))
prints the crate and exits *before* any callback runs, so the driver would never get a turn to
resugar. Capturing the output through `Config.output_file` would also trip the `IgnoringOutDir`
warning alongside cargo's `--out-dir`.

So the driver hooks `after_expansion` and prints the crate itself. The compiler forces
`resolver_for_lowering` just before that callback, which drives expansion and name resolution, and
the expanded AST is reachable from that query, where rustc's own
[`pretty.rs`](../../../external/rust/compiler/rustc_driver_impl/src/pretty.rs) reads it. The driver
clones it and calls `pprust::print_crate` with `is_expanded` set, the call `-Zunpretty=expanded`
makes, so the text matches what `cargo-expand` consumes, including the `#![feature(prelude_import)]`
preamble. It then resugars, writes the file, and returns `Compilation::Stop`, because analyzing a
crate it is only reading would cost a full type-check for no output. A failed write is a compiler
warning, so a bad path does not look like a crate that would not expand.

The diagnostic flags are left off, since `-Znext-solver=globally` and `--verbose` shape analysis,
which never runs. The CGP emitter stays installed, so an expansion-time error still passes through
it.

## The rustc-free resugaring

The resugaring lives in the library crate `cargo-cgp-expand`, which links no compiler internals, so
it builds and its tests run on any toolchain. It is separate from the error-processing crate because
expansion output is not diagnostics, though it takes that crate's spelling rules (`shape_name`,
`is_ident`, `is_primitive_type`), so the two cannot spell a name differently.

It parses the compiler's text with `syn::parse_file`, narrows to the `--item`, rewrites the tree,
prints with `prettyplease::unparse`, and tightens the printed spacing. When `syn` cannot parse the
text, it returns the input unchanged, so the command degrades to the compiler's own output rather
than failing.

[Resugaring](resugaring.md) specifies what each construct folds back to. These facts are particular to resugaring
*source* rather than a diagnostic:

- **It matches on `syn::Type`, not on rendered text,** because the text matchers are
  formatting-sensitive: `prettyplease` breaks a long generic list and ends it with a trailing comma,
  which the `Symbol!` matcher's final `>` check rejects. Which name stays raw would then depend on
  its length.
- **Its passes are separate whole-tree visits, and each list folds outermost-first.** The separation
  is the [`Nil` overlap hazard](resugaring.md#the-rules-every-resugaring-follows): a visitor
  recurses innermost-first, so one combined visitor would rewrite a `Symbol`'s terminating `Nil` to
  `Product![]` before examining the `Symbol`, and every field name would stay raw. A list's tail is
  itself a list, so folding the innermost cell first leaves `Cons<A, Product![B]>`.
- **Only real syntax is emitted.** No `Path!` spelling names a path ending in a generic tail, so an
  `open` statement's per-key entry keeps its raw
  `PathCons<ItemEncoderComponent, PathCons<u64, __Wildcard__>>`, and a list with a generic tail, such
  as a written `impl … for Cons<Head, Tail>`, stays raw for the same reason. A field list folds to
  its real `Struct!` or `Enum!` shape.
- **The printer's spacing is corrected afterward.** The printer lays a macro body out token by
  token, so it prints `Product![Multiply < Symbol!("foo") >]` and breaks a brace-delimited body onto
  its own lines. One narrow text pass removes the spaces inside the bodies of the macros the crate
  emits and joins `Struct!` and `Enum!` bodies back onto the macro's line. Its search steps over
  literals and comments.
- **Sugar the user wrote needs no attention,** because the CGP macro that copied it never expanded it.
- **Stripping the prelude must move a qualified path's index.** A qualified path
  (`<__Provider__ as DelegateComponent<C>>::Delegate`) records where its qualifier ends. Dropping
  segments without moving that index makes the printer assert, which panics the driver, so the strip
  corrects it for both node kinds that carry one.

The `cgp::macro_prelude::` qualifier is always stripped, as the first pass, so the printed expansion
does not compile as it stands, and no option keeps it. Other module qualifiers stay, unlike in a
diagnostic, because in source they carry information a reader may want.

## Known limitation: every macro is expanded

The command expands the whole crate, so `println!` and `#[derive(Debug)]` appear expanded beside the
CGP code. Printing only the CGP expansions would mean un-expanding the rest. Every `ExpnData`
carries `macro_def_id`
([`rustc_span/src/hygiene.rs`](../../../external/rust/compiler/rustc_span/src/hygiene.rs)), so each
node can be traced to its macro by defining crate. Three things make it hard: one invocation
commonly expands to several sibling items, a derive strips its attribute and appends impls, and code
a `cfg` eliminated cannot come back.

## Comparison with cargo-expand

`cargo-expand` owns no expansion logic, and that explains most of its design
([`main.rs`](../../../external/cargo-expand/src/main.rs)). It runs `cargo rustc` with
`-o <tmpfile> -Zunpretty=expanded`, reads the file, discards the comments the compiler misplaced,
prints with `prettyplease` or `rustfmt`, and pipes the result through `bat`. `cargo cgp expand` has
one thing to add, the resugaring, and each divergence follows from where that must happen.

The command agrees on these points: the same `cargo rustc` for per-target rustc arguments; a file
rather than stdout; the expansion printed whenever one exists, with cargo's code returned; and `syn`
plus `prettyplease` behind a fallback to the compiler's text.

It diverges deliberately on these:

- **The post-processing lives in the driver.** `cargo-expand` has no driver, so it post-processes
  after cargo exits. `cargo-cgp`'s driver owns every transform while the front-end relays output.
- **No `-Zunpretty=expanded`.** The driver must run after expansion, and the flag exits before any
  callback.
- **No `RUSTC_BOOTSTRAP` machinery.** `cargo-expand` needs `needs_rustc_bootstrap` and
  `do_rustc_wrapper` to enable a `-Z` flag on a stable toolchain. `cargo cgp expand` forces the
  pinned nightly.
- **No `rustfmt` and no `$crate` placeholder.** `cargo-expand` rewrites `$crate` to `Ξcrate` so
  `rustfmt` can parse its input.
- **`--item` rather than a positional,** matched by the crate's own
  [`select`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-expand/src/select.rs)
  rather than `syn-select`, which adds the rule selecting the impls *of* a named trait.

`cargo-expand` does more in these ways, which this command lacks: syntax highlighting and paging,
the `--ugly` raw mode, theme selection, re-declared cargo flags, and the manifest's `default-run`
lookup, where this command leaves the ambiguity for cargo to report.

## Further reading

Two references explain mechanisms the design relies on:

- [`cargo rustc`, in The Cargo Book](https://doc.rust-lang.org/cargo/commands/cargo-rustc.html):
  arguments after `--` go to the compiler invocation for the *selected target only*, which scopes
  expand mode to one crate.
- [Macro expansion, in the Rust Compiler Development Guide](https://rustc-dev-guide.rust-lang.org/macro-expansion.html):
  the fixed-point process and its interleaving with name resolution, the reason there is no
  per-macro switch.

## Tests

The resugaring is pure text-to-text, so unit tests pin it without a compiler, and the UI suite
covers the launching and printing halves.

- [`crates/cargo-cgp-expand/tests/expand/resugar.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-expand/tests/expand/resugar.rs):
  each construct and its decline cases, the overlap hazards, the outermost-first fold, the spacing,
  the prelude strip with both qualified-path shapes, unparsable input, and sugar named inside a
  literal or a comment.
- [`crates/cargo-cgp-expand/tests/expand/agreement.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-expand/tests/expand/agreement.rs): this
  crate and the diagnostic text resugaring agreeing on every construct.
- [`crates/cargo-cgp-expand/tests/expand/select.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-expand/tests/expand/select.rs): the
  selection rules, a path matching nothing, the path parser, and an unnamed constant's block.
- [`crates/cargo-cgp-driver/tests/driver/expand.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/expand.rs): the
  marker flags recovered and stripped, and a stray item flag never reaching the compiler.
- [`crates/cargo-cgp/tests/front_end/expand.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/expand.rs): the exit code, the
  closed pipe, the profile detection, the output directory, and the `--item` extraction.
- [`crates/cargo-cgp/tests/front_end/invocation.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/invocation.rs): the
  marker flags after one `--`.
- [`crates/cargo-cgp/tests/front_end/help.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp/tests/front_end/help.rs): what the expand help
  documents.
- The [UI suite](testing.md#three-passes-per-fixture) expands **every fixture**, comparing with its
  `<name>.expand.rs` and requiring the command to fail exactly when it reported an error. The
  `pass-through/` fixtures `macro_rules_no_matching_rule`, `unclosed_delimiter`,
  `recovered_syntax_error`, and `compile_error_macro` pin the kinds of failure.

## Source

- [`crates/cargo-cgp/src/expand/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src/expand): the subcommand, the `--item` extraction, the
  private directory, and the profile decision.
- [`crates/cargo-cgp/src/launch/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp/src/launch): the launch both reading subcommands share.
- [`crates/cargo-cgp-driver/src/expand/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/expand): the marker flags, and printing
  the expanded crate.
- [`crates/cargo-cgp-driver/src/callbacks.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/callbacks.rs): the
  `after_expansion` hook.
- [`crates/cargo-cgp-expand/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-expand): the resugaring passes, the spacing pass, and `select.rs`
  ([Resugaring](resugaring.md)).
