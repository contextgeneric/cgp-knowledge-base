# cargo-cgp `[CGP-Exxx]` codes

This entry catalogs the `[CGP-Exxx]` codes
[`cargo-cgp`](https://github.com/contextgeneric/cargo-cgp) stamps on a diagnostic it rewrites into a
recognized CGP class, so a class document's *How cargo-cgp presents it* section can cite a code by
number. Unlike the sibling `rustc`-code entries, these codes are **owned by `cargo-cgp`, not by
CGP**; this file is a pointer, and the authoritative definitions (what triggers each code and how to
fix it) live in `cargo-cgp`'s [error-code catalog](../../../cargo-cgp/error-code.md). When the two
disagree, that catalog wins; keep this list in sync with it under the
[cross-project rule](../../../AGENTS.md#the-synchronization-rule).

## What a code is

A code is `CGP-E` plus three digits, shown in square brackets at the start of a rewritten message,
before the cause it states, for example
`` error[E0277]: [CGP-E001] missing field `height` on `Rectangle` ``. The diagnostic keeps its own
`rustc` code (`E0277`, `E0599`, `E0271`, `E0275`), so `rustc --explain` still works and the entries
in this directory still apply; the `[CGP-Exxx]` tag rides *inside* the message text. A code is
assigned only when `cargo-cgp` both rewrote the message and identified it as a CGP class; everything
else is left uncoded by design.

The hundreds digit says where a code appears: a `CGP-E0xx` code heads a rewritten message, and a
`CGP-E1xx` code labels one entry of the dependency tree beneath it.

## Main-message headlines: `CGP-E0xx`

These lead a rewritten main message, in family blocks of ten. `E001` to `E005` come from the typed
resolver and carry a dependency chain in their notes, led by a `root cause:` line except for the two
mismatch codes `E004` and `E005`, whose message states the cause; `E010` to `E014` classify a
duplicate-key `E0119` conflict (no root-cause note, both `rustc` carets kept); `E015` to `E018` name
a structural mistake in a check table or a wiring entry; `E020` and `E021` reshape the `E0275`
overflow of a wiring lookup that never ends, and `E022` an orphan-rule coherence error; and `E030`
to `E034` reword a macro-lowering error, each with its fix in a `help`.

- **CGP-E001**: the consumer trait is not implemented for the context (missing wiring, or an unmet
  transitive dependency).
- **CGP-E002**: a provider a `#[check_providers]` entry lists does not implement its provider trait
  for the context (its impl-side `where` bounds do not hold).
- **CGP-E003**: a hand-written wrapper trait or a `#[cgp_fn]` blanket trait (not a CGP consumer)
  fails because a CGP component it depends on fails.
- **CGP-E004**: a context field has the wrong type (the `HasField` bound holds but its `::Value`
  projection fails).
- **CGP-E005**: an abstract type has the wrong type (the owner supplies one type where a provider
  requires another).
- **CGP-E010**: duplicate wiring: the same key mapped twice.
- **CGP-E011**: overlapping wiring: a key already set through another (generic over specific,
  `@`-path over a namespace forwarding, or a prefix path).
- **CGP-E012**: multiple namespaces used for one target in `delegate_components!`.
- **CGP-E013**: redirect collision: a direct wiring collides with a redirect of the same key.
- **CGP-E014**: duplicate redirect: the same key redirected more than once.
- **CGP-E015**: a `check_components!` table lists one entry twice.
- **CGP-E016**: two `check_components!` tables in one module share a check-trait name.
- **CGP-E017**: a `for` loop in a wiring table whose key does not use its key variable.
- **CGP-E018**: a `#[default_impl]` on a provider impl generic over a parameter the registration
  cannot carry.
- **CGP-E020**: the wiring never resolves because the lookup leads back to itself (an `E0275`
  overflow whose requirement is a `CanUseComponent` bound; a `UseContext` cycle is the usual case).
- **CGP-E021**: the wiring never resolves because each step requires the consumer trait for a larger
  type (the same `E0275` overflow, for a lookup that grows without repeating).
- **CGP-E022**: an orphan-rule namespace registration: a foreign component or path registered into a
  foreign namespace (`E0210`/`E0117`).
- **CGP-E030**: a trait used in a `#[cgp_fn]`/`#[cgp_impl]` body but not declared with `#[uses]`.
- **CGP-E031**: an inner provider a higher-order provider calls but never imports with
  `#[use_provider]`.
- **CGP-E032**: a `#[cgp_impl]` header names the component's consumer trait where its provider trait
  belongs.
- **CGP-E033**: `#[cgp_impl]` applied to a trait that is not a CGP component.
- **CGP-E034**: an inner-provider bound names the consumer trait rather than the provider trait.

## Dependency-tree entries: `CGP-E1xx`

One per rendering template, riding at the start of each entry in a `root cause:` dependency tree.
`E101` to `E104` are the steps of the chain; `E110` onward are the root causes it ends at, and the
`root cause:` line above the tree carries its cause's code too.

- **CGP-E101**: consumer trait impl step.
- **CGP-E102**: provider trait impl step.
- **CGP-E103**: redirect-lookup step (a namespace or `open` `RedirectLookup`), naming the table it
  looks the path up in.
- **CGP-E104**: a step through any other trait impl (a user's blanket trait, or an ordinary bound
  restated).
- **CGP-E110**: cause: a genuinely missing context field.
- **CGP-E111**: cause: the struct has the field but did not derive `HasField`.
- **CGP-E112**: cause: a field has the wrong type (the tree's face of `CGP-E004`).
- **CGP-E113**: cause: the context wires no provider for a component (or terminates no namespace
  path).
- **CGP-E114**: cause: a non-context delegation table (aggregate provider,
  `UseDelegate`/`UseInputDelegate`) is missing a key, including an `@`-path its own `open`
  redirected along.
- **CGP-E115**: cause: a non-provider was wired into a provider slot.
- **CGP-E116**: cause: an associated type the owner supplies differs from the one a provider requires
  (the tree's face of `CGP-E005`).
- **CGP-E117**: cause: an ordinary (non-CGP) trait bound that does not hold, in the compiler's own
  wording.

## Where CGP classes cite these

A class document's *How cargo-cgp presents it* section names the specific code(s) the tool produces
for that class and links to the [authoritative catalog](../../../cargo-cgp/error-code.md). For
example, [check-trait-failure](../checks/check-trait-failure.md) is stamped `[CGP-E001]` with a
`root cause:` tree whose leaf is `[CGP-E110]` (missing field) or `[CGP-E111]` (underived); the
[conflicting-wiring](../wiring/conflicting-wiring.md) family maps to `[CGP-E010]`–`[CGP-E014]`; and
[wiring-cycle](../wiring/wiring-cycle.md) maps to `[CGP-E020]` for a cycle and `[CGP-E021]` for a
lookup that grows.
