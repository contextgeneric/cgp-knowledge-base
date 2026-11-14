# Area calculation tutorial series

The site's only sustained teaching material: a four-page series that carries a reader from ordinary
Rust functions, through the coherence wall, to configurable compile-time dispatch with composable
higher-order providers, and finally to catching a wiring mistake at the line that made it, with one
running example the whole way.

- **URL**: <https://contextgeneric.dev/docs/tutorials/area-calculation/>
- **Source**: [docs/tutorials/area-calculation/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/tutorials/area-calculation)
- **Pages**: an unnumbered `index.md` framing the problem, then `context-generic-functions.md`
  (position 1), `static-dispatch.md` (position 2), and `checking.md` (position 3, on the `v0.8.0`
  branch only)
- **Status**: Current

## What it teaches

**The index teaches no CGP, deliberately.** It writes `rectangle_area(width, height)` as a plain
function and `scaled_rectangle_area` forwarding parameters it does not use (the first problem:
parameter threading grows with the call chain), then groups the fields into a `Rectangle` struct with
methods (the second: the methods are coupled to one type, so a third party wanting another field must
ask upstream or fork). It closes by stating what would fix both, without naming a construct.

**Context-Generic Functions** delivers the fix: `#[cgp_fn]` with `#[implicit]` arguments on any context
with `width` and `height` fields, `#[derive(HasField)]` to opt a struct in, `#[uses(RectangleArea)]` so
`scaled_rectangle_area` calls it without knowing its requirements, and a `print_rectangle_area` showing
`#[cgp_fn]`'s value with no implicit arguments. Two contexts, `PlainRectangle` and `ScaledRectangle`,
coexist without knowing about each other. An optional **"How it works"** section shows the desugaring
(a `RectangleArea` trait, a simplified `RectangleFields` getter trait, and a blanket impl, with
`#[uses]` as `Self: RectangleArea`), borrowed against owned implicit arguments, the zero-cost claim,
the generalization to `HasField`, and a comparison with **Scala implicit parameters** that separates
CGP's name-and-type field resolution from Scala's scope-based type resolution.

**Static Dispatch is where the series earns its length.** A second shape duplicates the scaled
function, a unified `CanCalculateArea` trait is proposed, and two blanket impls fail: the tutorial
**shows the compiler error** and explains it with a struct that has `width`, `height`, and `radius`.
`#[cgp_component]` then introduces the provider trait and `#[cgp_impl]` names implementations, which
are **called explicitly**, as `RectangleAreaCalculator::area(&rectangle)`, before any wiring exists,
including both on the ambiguous struct. A hand-written consumer impl binds a provider to a context
before `delegate_components!` replaces it, presented as a lookup table with a table in the prose.
`#[use_provider]` and `ScaledAreaCalculator<Inner>` close the page, with a note that composed providers
are generic types that can be aliased.

**Checking and Debugging** asks what happens when the wiring is wrong. It mis-wires `PlainCircle` to
`RectangleAreaCalculator`, shows the program still compiles because wiring is lazy, and carries that
one mistake through three diagnostics: the raw `E0599` at the call site, naming neither the missing
field nor the provider; the `E0277` that `check_components!` moves to the wiring site, spelling the
field as a `Chars` list; and `cargo cgp check`, which leads with the missing fields in English. It fixes
the wiring, shows the check passing, and ends with an optional *How it works* giving the hand-written
equivalent of a check.

The series makes its zero-cost argument in its own section: no vtables, no unsafe, no runtime
resolution, and no external compile-time processing.

## The teaching contract

**Objective.** A reader can define a component, write two named implementations that would otherwise
conflict, wire each context to the one it needs, compose implementations with a higher-order provider,
and say why each step was necessary.

**Prerequisites.** Basic Rust, with "a basic familiarity with Rust traits will be helpful" per the
index. It does *not* assume blanket implementations, coherence, or the orphan rule, and teaches
coherence when it hits it. It does not assume [Hello World](hello-world.md), though the two overlap.

**Register and shape.** First-principles, on a **value context** whose component targets `Self`:
`Rectangle` is the thing whose area is computed.

**Concept sequence.** Plain functions → concrete-context methods → `#[cgp_fn]` + `#[implicit]` →
`#[uses]` → *(optional desugaring)* → a second shape → the need for a unified trait → the coherence
error → `#[cgp_component]` → `#[cgp_impl]` → explicit provider calls → hand-written consumer impls →
`delegate_components!` → `#[use_provider]` → higher-order providers → lazy wiring → the call-site
failure → `check_components!` → `cargo cgp check` → *(optional desugaring)*.

**The two orderings of the
[tutorial guide](../writing-guides/tutorial.md#the-two-orderings-that-carry-a-tutorial) carry the
series and must not be disturbed**: every step opens with code that is unsatisfactory for a stated
reason, and providers are called by name and the consumer trait implemented by hand before
`delegate_components!` replaces it.

**Level of explanation.** Deeper than Hello World but gated. Desugaring lives in marked optional
sections in Context-Generic Functions and is largely absent from Static Dispatch; `IsProviderFor`,
`DelegateComponent`, and the generated blanket impls are never named there, though the lookup they
perform is described as a table built and consulted at compile time.

**Vocabulary.** "Consumer trait", "provider trait", "provider", "named implementation", and "component
name", each introduced when it becomes necessary, matching
[vocabulary.md](../../communication-strategy/vocabulary.md).

**Checking and Debugging extends the contract in one way, deliberately.** `CanUseComponent` and
`IsProviderFor` appear there because the diagnostics it quotes name them, and a page about reading
errors cannot hide the errors' words. They arrive last, in the optional desugaring, framed as
machinery that lets a failure explain itself. `DelegateComponent` is still never named.

## How it relates to the knowledge base

The constructs are [`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md),
[`#[implicit]`](../../cgp/reference/attributes/implicit.md),
[`#[uses]`](../../cgp/reference/attributes/uses.md),
[`#[derive(HasField)]`](../../cgp/reference/derives/derive_has_field.md),
[`#[cgp_component]`](../../cgp/reference/macros/cgp_component.md),
[`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md),
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md), and
[`#[use_provider]`](../../cgp/reference/attributes/use_provider.md). The concepts, in the order the
series meets them, are [implicit arguments](../../cgp/concepts/implicit-arguments.md),
[impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md),
[coherence](../../cgp/concepts/coherence.md),
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md), and
[higher-order providers](../../cgp/concepts/higher-order-providers.md).

**The [area calculation example](../../examples/area-calculation.md) is the series' verified
counterpart**, following the same progression; draw code from it when revising, and keep the two in
step. The Scala comparison rests on [implicit-parameters](../../related-work/implicit-parameters.md).
The series follows the tutorial playbook in [formats.md](../../communication-strategy/formats.md) for
the working developer in [readers.md](../../communication-strategy/readers.md).

## Where it diverges from CGP v0.8.0

The code is current: the series was written for v0.7.0, and nothing it uses changed in v0.8.0. Checking
and `cargo-cgp` are covered by `checking.md`, which is on the `v0.8.0` branch only, so the published
series omits both. Two smaller points:

- **Context-Generic Functions says an owned implicit argument needs `Copy`** on the live site; the
  expansion calls `.clone()`, so `Clone` is the requirement, and the `v0.8.0` branch's page says so.
- **`#[cgp_impl]` appears in both forms.** Static Dispatch shows
  `impl<Context> AreaCalculator for Context where Self: RectangleArea` before simplifying to
  `impl AreaCalculator`. That is deliberate, but only the second form is idiomatic per
  [writing-providers](../../cgp/guides/writing-providers.md), and a reader who stops early copies the
  first.

## Maintaining it

**Preserve the two orderings above all**; they make the series work, and they are what an unwary
addition breaks.

**The series is sequential, and Checking and Debugging depends on it.** Its code blocks are fragments
of the program Static Dispatch ends with, and the line numbers in its quoted errors refer to that file,
which the page says in its opening. The [tutorial guide](../writing-guides/tutorial.md) asks tutorials
to stand alone; this series does not. The index describes all three tutorials, and Static Dispatch
routes forward to Checking and Debugging.

**Checking and Debugging's diagnostics are quoted output.** A revision that changes its program re-runs
all three rather than editing the text: `cargo check` at the call site, `cargo check` with the assertion,
and `cargo cgp check`. The program and the mis-wired fixture are in the website's `example-code` crate,
at `tests/tutorials/` and `tests/compile_fail/tutorials/`, so the checked error is pinned by a blessed
`.stderr`; rustc abbreviates the `Chars` list differently by invocation, so the quote matches the pinned
fixture rather than any one local run.

**A further tutorial on namespaces**, drawn from the
[social media app example](../../examples/social-media-app.md), is the natural next step. Namespaces
pay off only once a wiring table is long, and this series' table has one entry, so it needs a bigger
running example rather than a bolt-on section.
