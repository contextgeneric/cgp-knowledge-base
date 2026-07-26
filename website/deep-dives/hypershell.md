# Hypershell deep dive

The type-level shell-scripting DSL, developed end to end: what a Hypershell program is, how a program
that is a *type* gets interpreted at compile time, how the language is assembled from namespaces, and
how anyone can extend it. The largest of the three planned deep dives, and the one that gains most from
being split.

- **Planned URL** — `https://contextgeneric.dev/docs/deep-dives/hypershell/`
- **Source post** — [Hypershell: a type-level DSL for shell-scripting](../blog/hypershell-release.md),
  2025-06-14, ~16,500 words, written against CGP v0.4.1
- **Code base** — [`hypershell`](https://github.com/contextgeneric/hypershell), tracking `cgp`
  0.8.0-alpha locally at `../hypershell`
- **Status** — planned; no page written

## What it covers, and why it needs this format

Hypershell is a DSL whose programs are Rust *types*, interpreted at compile time through CGP wiring, so
a pipeline like `SimpleExec<StaticArg<"echo">, WithStaticArgs["hello"]> | StreamToStdout` compiles to
direct calls with no interpreter and no runtime overhead. It is the project's best demonstration that
CGP's wiring is a general mechanism rather than a dependency-injection trick, and the source post is
still the fullest account anywhere of building one.

The material justifies the format on both counts the [deep-dive guide](../writing-guides/deep-dive.md)
names. Its **code is uniformly stale** — every context in the post uses the removed
`#[cgp_context(MyAppComponents: HypershellPreset)]`, and its four-level preset delegation trace
describes a mechanism that no longer exists — while the repository has since been rebuilt on
namespaces. And it is **one page of 16,500 words**, which serves the reader who commits two hours and
nobody else.

## The page split

Six pages, one running example — the checksum pipeline the repository's own examples use — carried
throughout.

**`index.md` — what Hypershell is** (~800 words). The hello-world program, two or three example
programs of increasing interest, what makes them unusual (the program is a type), and the declared
shape of the whole deep dive. Ends by saying plainly that Hypershell is an experimental proof of
concept for CGP rather than a shell replacement, which the source post says in a disclaimer and which
belongs on the first page.

**1 — Programs as types** (~1,200 words). The abstract syntax: each fragment is a zero-data struct
whose parameters carry structure, a pipeline is a `Product!` list, a literal is a `Symbol!`. The
`hypershell!` macro as strictly optional surface sugar, shown desugared. This page is where a reader
either accepts the central idea or leaves.

**2 — Interpreting a program** (~1,500 words). The `Handler` component as the interpreter interface,
the `Code` tag as the program fragment, and a provider as the interpreter for one fragment. One worked
provider read line by line.

**3 — Assembling the language with namespaces** (~1,500 words). The page that has changed most: how
`HypershellNamespace` collects the whole language, how a component registers into it under a path
prefix, and how a context joins it in one line. This replaces the post's preset chapter entirely.

**4 — Extending the language** (~1,500 words). Adding a fragment, adding a provider for an existing
fragment, and building a custom context — the checksum and compare namespaces in the repository's
examples are the worked cases.

**5 — Trade-offs and related work** (~1,500 words). The honest costs, and the comparison to tagless
final and Servant. This page must not shrink; it is the most credible thing in the source post.

## What changes from the source post

**The embedded CGP primer comes out.** The post carries a self-contained tour of CGP because nothing
else on the site could carry one in 2025. The [explanation tier](../writing-guides/explanation.md) now
can, so the deep dive links to *Why CGP exists* and *How CGP works* and keeps only the orientation its
own subject needs. This is the single largest reduction available and is most of the difference between
16,500 words and roughly 8,000.

**Presets become namespaces throughout.** `cgp_preset!`, `#[cgp::re_export_imports]`, `override`,
`#[wrap_provider(UseDelegate)]`, `Preset::Provider`, and `#[cgp_context]` are all gone. The repository
already shows the replacement: a namespace declared with `cgp_namespace!` and `@`-path entries,
components registered into it with `#[prefix(@hypershell.core in DefaultNamespace)]`, and a context
that reads in full as

```rust
delegate_components! {
    HypershellCli {
        namespace HypershellNamespace;
    }
}
```

That one-line context is a better demonstration than anything in the post, and should be shown early.

**Providers become `#[cgp_impl]`.** Every provider in the post is inside-out with `#[cgp_new_provider]`
and an explicit `context: &Context` parameter; the repository is already fully converted.

**Dependencies become `#[uses]` and `#[implicit]`.** The post declares every provider dependency as a
hand-written `where` bound on the context — a long `Context: CanExtractCommandArg<...> + ...` list —
which is the current guides' explicit anti-pattern. The repository has *not* made this change, which is
the largest code item below.

**`HasAsyncErrorType` and `Async` are gone**, removed in v0.5.0; `Send` recovery is now the
[proxy-trait pattern](../../cgp/concepts/send-bounds.md).

**Two claims are overtaken.** The post offers AI editors as the practical answer to CGP's error
messages; that is now second best, behind [`cargo-cgp`](../../cgp/reference/cargo-cgp.md). And its
"no simple tutorials, because CGP's benefits only show past 5,000 lines" argument is obsolete now that
two tutorial series exist — the deep dive should link them rather than argue against them.

**Voice converts to the project's.** The naming backstory — Hypershell as a homage to a 2012 project —
is the author talking and stays on the blog, linked. The Disadvantages section converts by grounding
rather than deleting: "the cause is not fully understood, and the available measurements are rough" is
project voice and keeps the honesty.

## Source-code changes needed

The repository is the most modernized of the four and its remaining gaps are localized. Nothing here
blocks starting the deep dive, but items in the first group will otherwise force the deep dive to show
code the guides tell readers not to write.

### Required before the deep dive quotes the code

**Adopt `#[uses(...)]` for capability dependencies.** The repository has **zero** `#[uses]` attributes
and eight hand-written `Self:` `where` bounds. Every one is the form
[declaring-dependencies](../../cgp/guides/declaring-dependencies.md) tells readers to replace, and page
2 of the deep dive quotes a provider in full.

**Adopt `#[implicit]` arguments for context fields.** The repository has zero, and one
getter-trait declaration. Reading a provider's own context field through a getter is the pattern
[reading-context-fields](../../cgp/guides/reading-context-fields.md) reserves for the cases an implicit
argument cannot reach — a field on another type, or a named shared capability — and it should be
checked case by case rather than converted wholesale.

**Replace the one live `UseDelegate` table.** `crates/hypershell-components/src/providers/pipe.rs`
still wires the pipe handler through a nested dispatch table:

```rust
delegate_components! {
    new HandlePipe {
        HandlerComponent: UseDelegate<new RunPipeHandler {
            <Handlers: WrapCall> Pipe<Handlers>:
                PipeHandlers<Handlers::Wrapped>,
        }>,
    }
}
```

The `open` statement with an `@`-path key is the current idiom per
[dispatching-per-type](../../cgp/guides/dispatching-per-type.md). **Verify this one before changing
it** — the key carries a bound on its generic parameter, and whether the `open` form accepts a bounded
generic key should be confirmed against the
[`delegate_components!` reference](../../cgp/reference/macros/delegate_components.md) rather than
assumed.

**Fix two stale comments.** `crates/hypershell-examples/examples/hello_name.rs:21` and
`github_issues.rs:21` both describe `#[cgp_inherit]`, a construct removed in v0.7.0, while the code
beneath them correctly uses `namespace HypershellNamespace;`. These are the only preset-era references
left in the repository and they will be read as current by anyone quoting the examples.

### Worth doing, not blocking

**Consider dropping the six `#[derive_delegate(UseDelegate<Arg>)]` attributes** on
`command_arg.rs`, `method_arg.rs`, `url_arg.rs`, `string_arg.rs`, `update_builder.rs`, and
`update_command.rs`. Since `open` resolves through the `RedirectLookup` impl that every
`#[cgp_component]` generates, these are needed only by a context that still wires the component through
a `UseDelegate<new ...>` table. Removing them is a **breaking change for downstream users** who do, so
it is a deliberate decision rather than a cleanup — and the deep dive can simply not show them either
way.

**Widen `#[use_type]` adoption.** Two uses exist against several places where an abstract type is
named. Low priority, but it is what the deep dive's code should look like.

## How it relates to the knowledge base

The verified counterpart is the [shell-scripting DSL example](../../examples/shell-scripting-dsl.md),
which carries the same progression in current form and is the source to quote from. The pattern behind
the whole deep dive is [type-level DSLs](../../cgp/concepts/type-level-dsls.md); the interpreter
interface is the [handler family](../../cgp/concepts/handlers.md) over
[`Handler`](../../cgp/reference/components/handler.md); the assembly mechanism is
[namespaces](../../cgp/concepts/namespaces.md) via
[`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md) and the `#[prefix(...)]` attribute;
composition uses the [handler combinators](../../cgp/reference/providers/handler_combinators.md); and
the `Send` question is [send-bounds](../../cgp/concepts/send-bounds.md). The project entry is
[projects/hypershell](../../projects/hypershell/README.md).

For framing, the trade-offs page is bound by
[message.md](../../communication-strategy/message.md#the-objections-readers-bring), and the
"DSL users need not learn CGP" argument the post makes is the author's own positioning thesis, recorded
in [author-personality.md](../../communication-strategy/author-personality.md).

## Maintaining it

Once written, this is a docs page and is corrected in place as CGP changes — that is the whole point of
the format. Two things a revision must preserve: the **trade-offs page**, which is what makes the rest
credible and which a well-meaning trim will target first; and the **one-line context**, which is the
deep dive's strongest single demonstration and should stay early rather than being buried in the
namespaces page.

Do not let the CGP primer creep back in. Each time a reader is thought to need more background, the
answer is a link to the explanation tier and, if the explanation is genuinely missing, a change there.
