# Writing a tooling page

A tooling page documents a **program the reader runs**, not a construct they write. The site has one
such subject — [`cargo-cgp`](https://contextgeneric.dev/docs/cargo-cgp/) — and its section is the model
this guide describes.

- **Where they live** — `docs/cargo-cgp/`, a top-level category beside the reference
- **Voice** — project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from** — [cargo-cgp/reference/](../../cargo-cgp/reference/README.md), which stays the source
  of truth
- **Scale** — five pages: an overview, then one per command, plus installation and troubleshooting

## Why this is its own kind of page

A tooling page fails differently from every other page on the site, which is why it needs its own
rules rather than borrowing the reference guide's.

A [reference page](reference.md) documents a construct whose behavior is fixed by the source: get the
expansion right and the page is right. A tooling page documents a program whose behavior depends on
**the reader's machine** — which toolchain is active, which package manager installed it, which version
they have — so the same command produces different results for different readers, and most of the page
exists to handle that. Installation is a decision tree rather than a command. Troubleshooting is a
substantial page rather than a *Gotchas* section, because the interesting failures happen before the
tool does anything.

The second difference is that a tooling page's claims **decay on their own**. A construct's expansion
changes only when someone changes the macro; a tool's version numbers, published commands, and error
text change when the tool ships. Assume every version-specific sentence on these pages is stale until
re-checked.

## The section shape

Five pages, in this order, and the order is the reader's rather than the tool's.

**An overview** at `index.md`, which is the category's `link` target rather than a generated index. It
answers *why this exists* before *how to run it*, and it earns that with a concrete before/after: the
same mistake as the tool presents it and as the reader would otherwise meet it. It closes by routing to
the other four.

**One page per command.** Each shows the command, a worked example on real code, how to read what comes
back, and where the command stops being the right tool. Commands get their own pages rather than
sections of one page because a reader arrives wanting one of them.

**Installation**, which is a decision before it is a command: lead with a table matching what the reader
*has* to the path they should take, then one section per path.

**Troubleshooting**, which opens with a **symptom index** — a table from the distinctive fragment of an
error to the section that explains it — because a reader arrives holding an error message and nothing
else. Then one section per failure, each quoting the exact text.

## What every tooling page owes its reader

**Quote real output, never remembered output.** Run the command and paste what it printed. This is the
rule most easily broken and the one that most damages the page, because a reader compares your quoted
output against their screen character by character, and a paraphrase reads as a version mismatch. It
applies to error text especially: the tool's messages are the thing being documented.

**Say what the command does *not* do.** Every page here carries a boundary, because the honest scope of
this tool is narrow: it is optional, it is not a build tool, and CGP compiles on stable Rust without it.
A page that omits that leaves the reader assuming a dependency they do not have.

**Distinguish the tool's errors from the ones it forwards.** `cargo-cgp` forwards most of its arguments
to cargo, so a large share of what a reader sees comes from cargo and is not the tool's to explain. Say
which is which; a reader debugging the wrong program wastes real time.

**Concede the version.** The tool is a `v0.1.0-alpha` that reshapes the classes it recognizes and passes
the rest through. Per
[vocabulary.md](../../communication-strategy/vocabulary.md), the framing is *dramatically better and
actively improving*, never *solved* — and never *fixed*. A reader who hits an unreshaped error having
been told the problem was solved trusts nothing else on the page.

**Pin a claim to the thing that can be checked.** Where a fact depends on the release — which commands
exist, which version is published — say how the reader can check it themselves rather than asserting a
number that will age.

## What must not be on one

**No knowledge-base links**, per the [one-way rule](../AGENTS.md#the-one-way-link-rule). The internal
[cargo-cgp section](../../cargo-cgp/README.md) is the source, and it links out to implementation
documents that must not follow the material onto the site.

**No implementation detail as explanation.** How the two executables find each other and how the driver
reaches the compiler belong in the internal documents. They appear here only where a reader needs them
to *fix* something — the sibling-path lookup earns its place on the troubleshooting page because it is
why a driver goes missing, and nowhere else.

**No instructions the page cannot stand behind.** If a path has not been run, do not present it as
though it has; say which paths are verified.

## Checking a draft

**Run every command in it**, on a real project, and paste what came back.

**Read the installation page as someone with only Nix, then again as someone with only rustup.** Each
should find their path without reading the other's.

**Grep for `solved`, `fixed`, and `no longer`** in anything said about the error experience.

**Check the boundary is present on every page** — what the command does not do, and what to use instead.

**Check the symptom index covers every error the troubleshooting page quotes**, since the index is how
readers enter that page and an unindexed section is an unread one.
