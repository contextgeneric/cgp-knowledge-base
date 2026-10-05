# Writing a tooling page

A tooling page documents a **program the reader runs**, not a construct they write. The site has one
such subject, [`cargo-cgp`](https://contextgeneric.dev/docs/cargo-cgp/), and its section is the model
this guide describes.

- **Where they live**: `docs/cargo-cgp/`, a top-level category beside the reference
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from**: [cargo-cgp/reference/](../../cargo-cgp/reference/README.md) and
  [cargo-cgp/error-code.md](../../cargo-cgp/error-code.md), which stay the source of truth
- **Scale**: eight pages, namely an overview, installation, one page per reading command, a page on
  reading the output, troubleshooting, and two lookup pages for the error codes and the command line

## Why this is its own kind of page

A tooling page fails differently from every other page on the site, which is why it needs its own
rules rather than borrowing the reference guide's.

A [reference page](reference.md) documents a construct whose behavior is fixed by the source: get the
expansion right and the page is right. A tooling page documents a program whose behavior depends on
**the reader's machine** (which toolchain is active, which package manager installed it, which version
they have), so the same command produces different results for different readers, and most of the page
exists to handle that. Installation is a decision tree rather than a command. Troubleshooting is a
substantial page rather than a *Gotchas* section, because the interesting failures happen before the
tool does anything.

The second difference is that a tooling page's claims **decay on their own**. A construct's expansion
changes only when someone changes the macro; a tool's version numbers, published commands, and error
text change when the tool ships. Assume every version-specific sentence on these pages is stale until
re-checked.

## The section shape

Eight pages, ordered by what the reader is doing: the five a reader works through first, then the
troubleshooting page they reach when the tool will not run, then the two pages they look things up in.
The order is the reader's rather than the tool's.

**An overview** at `index.md`, which is the category's `link` target rather than a generated index. It
answers *why this exists* before *how to run it*, and it earns that with a concrete before/after: the
same mistake as the tool presents it and as the reader would otherwise meet it. Choose the mistake
whose raw form hides the cause rather than buries it, since that contrast is the strongest honest
argument the tool has. It states what the tool costs and what it does not do, and closes by routing to
the rest.

**Installation**, which is a decision before it is a command: lead with a table matching what the reader
*has* to the path they should take, including the reader for whom no path fits, then one section per
path. It is also where the tool's version, its supported platforms, and the CGP version it is built for
are stated.

**One page per reading command** (`check` and `expand`). Each shows the command, a worked example on
real code the reader can paste, and where the command stops being the right tool. Commands get their own
pages rather than sections of one page because a reader arrives wanting one of them. The provisioning
commands (`setup`, `update`) belong to the installation page, since they are steps in installing rather
than tools a reader reaches for.

**Reading the output**, an explanation of every shape the tool's output takes: the headline, the
root-cause note and its dependency tree, several causes in one block, the two-caret conflict, the fix
given in a `help` line, and which error classes still arrive as the compiler wrote them. It exists
because a reader holding an error is a different reader from one learning to run the command, and they
arrive here from a search or from the check page.

**Troubleshooting**, which opens with a **symptom index** (a table from the distinctive fragment of an
error to the section that explains it), because a reader arrives holding an error message and nothing
else. Then one section per failure, each quoting the exact text, ordered by how often a reader meets it.

**Two lookup pages close the section.** *Error codes* gives every code the tool stamps its own heading,
so a link can land on it, with the message, what it means, the fix, and the section of the reference's
compile-errors page that explains the class. That page is organized by the mistake and starts from raw
output; *Error codes* is organized by what the tool printed, and the two link to each other rather than
repeating each other. *Command reference* lists every command, option, and environment variable in one
place, so a reader looking for a flag does not have to find it inside a worked example.

## What every tooling page owes its reader

**Quote real output, never remembered output.** Run the command and paste what it printed. This is the
rule most easily broken and the one that most damages the page, because a reader compares your quoted
output against their screen character by character, and a paraphrase reads as a version mismatch. It
applies to error text especially: the tool's messages are the thing being documented. The quoted output
must come from exactly the program the page shows, so keep that program in the website repository's
`example-code/` crate and re-run the tool on it rather than on a variant.

**Write against the release the site ships with.** The site publishes alongside a tool release, so the
pages describe that release as already out, including commands and fixes that land on the tool's
default branch before the tag. Output captured from a pre-release build that names the build's version
is quoted with the release's version, and the page's record says so; re-running every quoted command
against the tagged release is a publication step, not an optional check. Where a passage describes
behavior that does not exist yet on any build, it carries no quoted output until that behavior lands.

**Say what the command does *not* do.** Every page here carries a boundary, because the honest scope of
this tool is narrow: it is optional, it is not a build tool, and CGP compiles on stable Rust without it.
A page that omits that leaves the reader assuming a dependency they do not have.

**Distinguish the tool's errors from the ones it forwards.** `cargo-cgp` forwards most of its arguments
to cargo, so a large share of what a reader sees comes from cargo and is not the tool's to explain. Say
which is which; a reader debugging the wrong program wastes real time.

**Concede the limits without a version number.** Per
[vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each),
copy the canonical sentence unchanged: `cargo cgp check` leads with the root cause for the classes it
recognizes, and the tool does not yet reshape every class. Name the classes that still pass through
where a reader needs them. Never call the problem *solved* or *fixed*. A reader who hits an unreshaped
error having been told the problem was solved trusts nothing else on the page.

**State the version once.** The tool's version appears on the installation and command-reference pages
and nowhere else, so a release changes two sentences rather than a section.

**Say which platforms are tested.** The tool is tested on Linux only. A page says so wherever it gives a
platform-specific instruction, and an instruction for an untested platform is either marked untested or
left out.

**Pin a claim to the thing that can be checked.** Where a fact depends on the release (which commands
exist, which nightly is pinned), say how the reader can check it themselves rather than asserting a
value that will age. A pinned nightly's date is the clearest case: show where to read it, not the date.

## What must not be on one

**No knowledge-base links**, per the [one-way rule](../AGENTS.md#the-one-way-link-rule). The internal
[cargo-cgp section](../../cargo-cgp/README.md) is the source, and it links out to implementation
documents that must not follow the material onto the site.

**No implementation detail as explanation.** How the two executables find each other and how the driver
reaches the compiler belong in the internal documents. They appear here only where a reader needs them
to *fix* something: the sibling-path lookup earns its place on the troubleshooting page because it is
why a driver goes missing, and nowhere else.

**No instructions the page cannot stand behind.** If a path has not been run, do not present it as
though it has; say which paths are verified.

## Checking a draft

**Run every command in it**, on the program the page shows, and paste what came back.

**Read the installation page as someone with only Nix, then again as someone with only rustup, then as
someone with neither.** Each should find their path, or learn that none fits, without reading the
others'.

**Grep for `solved`, `fixed`, and `no longer`** in anything said about the error experience.

**Check the boundary is present on every page**: what the command does not do, and what to use instead.

**Check the symptom index covers every error the troubleshooting page quotes**, since the index is how
readers enter that page and an unindexed section is an unread one.

**Check every code the site quotes has an entry on the error-codes page**, and that every entry links
to the compile-errors section for its class.
