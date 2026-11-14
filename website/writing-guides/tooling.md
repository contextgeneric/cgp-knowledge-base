# Writing a tooling page

A tooling page documents a **program the reader runs**, not a construct they write. The site has one
such subject, [`cargo-cgp`](https://contextgeneric.dev/docs/cargo-cgp/), and its section is the model
this guide describes.

- **Where they live**: `docs/cargo-cgp/`, a top-level category beside the reference, recorded in
  [pages/cargo-cgp.md](../pages/cargo-cgp.md)
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from**: [cargo-cgp/reference/](../../cargo-cgp/reference/README.md) and
  [cargo-cgp/error-code.md](../../cargo-cgp/error-code.md), which stay the source of truth
- **Reading**: the shared set and [the `cargo-cgp` pages' row](README.md#cargo-cgp-pages) of the
  reading map

## Writing style

Write every page under `docs/cargo-cgp/` in **natural-writing**'s natural style: each sentence builds
on the last, paragraphs connect the reasoning, and sentence lengths vary. A reader arrives to run a
command or understand an error, so the opening names that task and why it matters, names
Context-Generic Programming once beside a plain description of what the tool checks, and links the
Introduction. The overview may relate a short form of the tag line, since the tool checks wiring that
selects implementations; a lookup page leaves it out, per the
[naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page).

**The form still follows the content.** The symptom index, the decision table, the command tables, and
each code's entry stay tables or short structured entries for lookup, and commands and quoted output
stay code blocks; natural style governs the prose that introduces and connects them. An error-code
entry may explain its cause and remedy in connected paragraphs, keeping the code's heading, anchor, and
message form separate from the explanation. Convert a list to prose when its items develop one
argument, and preserve technical conditions, exceptions, and uncertainty.

## Why this is its own kind of page

**A tooling page's behavior depends on the reader's machine**: which toolchain is active, which
package manager installed the tool, which version they have. A [reference page](reference.md) is right
once its expansion is right; a tooling page must handle the same command producing different results,
so installation is a decision tree and troubleshooting is a substantial page, because the interesting
failures happen before the tool does anything.

**Its claims decay on their own.** A tool's version numbers, commands, and error text change when it
ships, so treat every version-specific sentence as stale until re-checked.

## The section shape

Nine pages, in the reader's order: the five a reader works through first, the editor page, the
troubleshooting page, then the two lookup pages.

- **Overview** (`index.md`, the category's `link` target): *why this exists* before *how to run it*,
  earned with a before/after of the same mistake as the tool presents it and as the reader would
  otherwise meet it; choose a mistake whose raw form hides the cause rather than buries it. It states
  what the tool costs and does not do, and routes to the rest.
- **Installation**: a table matching what the reader *has* to the path they should take, including
  the reader no path fits, then one section per path. It states the tool's version, its supported
  platforms, and the CGP version it is built for, and holds the provisioning commands (`setup`,
  `update`), which are installation steps.
- **One page per reading command** (`check` and `expand`), because a reader arrives wanting one: the
  command, a worked example on real code the reader can paste, and where the command stops being the
  right tool.
- **Reading the output**: every shape the output takes (the headline, the root-cause note and its
  tree, several causes in one block, the two-caret conflict, the fix in a `help` line) and which
  classes still arrive as the compiler wrote them, for a reader holding an error.
- **Editor integration**: the check wired into an editor's on-save diagnostics, its own page because a
  reader searches for it and because the switch changes what a reader would blame on the tool (a slow
  first save, the editor's check options dropped, as-you-type errors not rewritten). It covers one
  editor and language server at a time, says how the setting was verified, and names an untried editor
  as untried rather than giving it a recipe.
- **Troubleshooting**: a **symptom index** first, from the distinctive fragment of an error to its
  section, because a reader arrives holding only the message; then one section per failure, quoting
  the exact text, ordered by how often a reader meets it.
- **Error codes**: every code the tool stamps under its own heading, so a link lands on it, with the
  message, the meaning, the fix, and the section of the reference's compile-errors page for its class.
  The compile-errors page starts from the mistake and raw output, this page from what the tool
  printed, and they link each other rather than repeating.
- **Command reference**: every command, option, and environment variable in one place.

## What every tooling page owes its reader

- **Quote real output, never remembered output.** Run the command and paste what it printed, from
  exactly the program the page shows, kept in the website's `example-code/` crate; a reader compares
  quoted output with their screen character by character, and a paraphrase reads as a version mismatch.
- **Write against the official release the site ships with**, as already out, including commands and
  fixes that land on the tool's default branch before the tag. No page names a pre-release, per the
  base's [rule on versions](../../AGENTS.md#document-official-versions-never-pre-releases): output
  naming one is quoted with the official version. Re-running every quoted command against the tagged
  release is a publication step, and a passage about behavior no build has yet carries no quoted
  output.
- **Say what the command does *not* do.** The tool is optional, is not a build tool, and CGP compiles
  on stable Rust without it; every page carries that boundary.
- **Distinguish the tool's errors from the ones it forwards** from cargo, so a reader debugs the right
  program.
- **Concede the limits without a version number**, copying the canonical sentence from
  [vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each)
  unchanged: `cargo cgp check` leads with the root cause for the classes it recognizes, and the tool
  does not yet reshape every class. Name the classes that pass through where a reader needs them, and
  never call the problem *solved* or *fixed*.
- **State the tool's version once**, on the installation and command-reference pages only.
- **Say which platforms are tested**: Linux only, stated wherever a page gives a platform-specific
  instruction; an instruction for an untested platform is marked untested or left out.
- **Pin a claim to the thing that can be checked**: where a fact depends on the release, such as a
  pinned nightly's date, show where the reader reads it rather than the value.

## What must not be on one

- **No knowledge-base links**, per the
  [one-way rule](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links).
- **No implementation detail as explanation.** How the two executables find each other and how the
  driver reaches the compiler appear only where a reader needs them to fix something, such as the
  sibling-path lookup on the troubleshooting page, because it is why a driver goes missing.
- **No instructions the page cannot stand behind**; say which paths are verified.

## Checking a draft

- **Run every command in it**, on the program the page shows, and paste what came back.
- **Read it through in natural style.**
- **Read the installation page as someone with only Nix, then only rustup, then neither**; each finds
  their path, or learns that none fits, without reading the others'.
- **Grep for `solved`, `fixed`, and `no longer`** in anything said about the error experience.
- **Check the boundary on every page**: what the command does not do, and what to use instead.
- **Check the symptom index covers every error the troubleshooting page quotes.**
- **Check every code the site quotes has an entry on the error-codes page**, each linking the
  compile-errors section for its class.
