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

## The code families

The [catalog](../../../cargo-cgp/error-code.md) gives each code's message, meaning, and fix. These are the
families, so a class document's code can be placed by its number:

| Codes | Family |
| --- | --- |
| `CGP-E001` to `CGP-E005` | A trait the context cannot use, and the two type mismatches |
| `CGP-E010` to `CGP-E014` | A duplicate-key `E0119` conflict |
| `CGP-E015` to `CGP-E019`, `CGP-E060`, `CGP-E061` | A structural mistake in a check table, a wiring entry, or a dispatch trait |
| `CGP-E020`, `CGP-E021` | An `E0275` overflow of a wiring lookup that never ends |
| `CGP-E022` | An orphan-rule namespace registration |
| `CGP-E030` to `CGP-E039` | A mistake in what a macro was given |
| `CGP-E040` to `CGP-E044` | A wiring key, value, or path type that does not resolve |
| `CGP-E050` | A failed extensible-data operation |
| `CGP-E101` to `CGP-E104` | A step of a dependency chain |
| `CGP-E110` onward | The root cause a dependency chain ends at |

## Where CGP classes cite these

A class document's *How cargo-cgp presents it* section names the specific code(s) the tool produces
for that class and links to the [authoritative catalog](../../../cargo-cgp/error-code.md). For
example, [check-trait-failure](../checks/check-trait-failure.md) is stamped `[CGP-E001]` (or
`[CGP-E002]` for a `#[check_providers]` entry, `[CGP-E003]` for a wrapper or blanket trait) with a
`root cause:` tree whose leaf is `[CGP-E110]` (missing field) or `[CGP-E111]` (underived), or
`[CGP-E060]` for a check that names no parameters; the
[conflicting-wiring](../wiring/conflicting-wiring.md) family maps to `[CGP-E010]`–`[CGP-E016]` and
`[CGP-E061]`; and [wiring-cycle](../wiring/wiring-cycle.md) maps to `[CGP-E020]` for a cycle and
`[CGP-E021]` for a lookup that grows. Three lowering classes take the macro-mistake block:
[undeclared dependency](../lowering/undeclared-dependency.md) maps to `[CGP-E030]`, `[CGP-E031]`,
`[CGP-E035]`, and `[CGP-E036]`, [wrong component half](../lowering/wrong-component-half.md) to
`[CGP-E032]` to `[CGP-E034]` and `[CGP-E037]`, and
[provider impl without the macro](../lowering/provider-impl-without-macro.md) to `[CGP-E039]`;
[unresolved wiring name](../wiring/unresolved-wiring-name.md) takes `[CGP-E038]` and `[CGP-E040]` to
`[CGP-E044]`. The [extensible-data](../data/extensible-data.md) class takes `[CGP-E050]` for a call
to a data operation, and its causes `[CGP-E118]` to `[CGP-E126]` under whichever headline its anchor
gives.
