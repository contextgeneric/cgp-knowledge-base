# AGENTS.md — the ecosystem projects

This directory documents the libraries built *with* CGP, one section per project. Read
[README.md](README.md) for what qualifies as a project here, and the base-wide
[../AGENTS.md](../AGENTS.md) for the rules every section shares: the synchronization rule, verifying
against the source, the prose style, document-the-present, the public-repository rules, and how a
document registers itself. The rules below add what is specific to documenting a project.

## A project section documents its project in depth

**A project section is verified against its project's source, exactly as `cgp/` is verified against
`cgp`'s.** The project's code is the single source of truth, above any document here, and a change to
the project that alters a provider's bounds, its wire format, its context dependencies, or the crate
it lives in is a change to the matching document. When the project's checkout is present, make both
changes; when it is absent, say plainly what needs updating here.

Read the project at the branch [../sibling-projects.md](../sibling-projects.md) records for it, and
link to it at that same branch (`https://github.com/contextgeneric/<project>/blob/<branch>/<path>`).
This departs from the base-wide rule that source links always name `main`. A project whose current
development lives on a branch other than `main` is documented against that branch, so a link to
`main` would show a reader different code from the code the document describes. When the recorded
branch changes, update the links in the same change.

**Do not modify the project's source while documenting it**, unless the user asks. Documenting often
turns up a defect, a missing test, or stale metadata. Record each one in the section's `issues.md`
rather than fixing it in passing, so the fix is a separate, reviewable change in the project's own
repository.

## Verify behavior with a probe, not by reading alone

A claim about what a provider *does* at runtime (the JSON it writes, the input it rejects, the error
message it produces) is checked by running it. Build a scratch crate in the session's scratchpad with
path dependencies on the local checkout, copy the project's `Cargo.lock` and `rust-toolchain.toml` so
the probe resolves the same versions, and exercise the behavior. A compile-time claim, such as which
derives a provider needs or which wiring mistake produces which error, is checked by building the
probe, and with `cargo cgp check` where a diagnostic is quoted. State the result in your own words.
The probe is evidence and is never linked from a document. A claim you could not confirm is written
as unconfirmed.

## Leave CGP itself to `cgp/`

A project section explains the project's design, not CGP's. When a document relies on a CGP
construct or idea (the consumer and provider trait split, the `open` statement, extensible records),
link to its document under [../cgp/](../cgp/README.md) and say only what the project does with it.
The test is whether the paragraph would still be true of a different project: if it would, it belongs
in `cgp/`, and the project document links there.

## The shape of a project section

A project starts as a single `README.md` and grows into the shape below as it is documented. The
directories and files are fixed names, so an agent moving between projects finds the same kind of
material in the same place. Omit what a project does not need, and add nothing outside this shape
without raising it.

- **`README.md`** — the front door: the header block (repository, local checkout, the branch
  documented, crates, the `cgp` version tracked, status), what the project is, a present-tense
  paragraph stating which revision the documents describe and how the published crate differs from
  it, a short list of the project's confirmed gaps that links to `issues.md` for the detail, the
  catalog of every document in the section, and the map from those documents to the public material
  they will feed.
- **`architecture/`** — the project's own design, one idea per document: how the crates divide, the
  decisions that shape every provider, and the mechanisms a reader must understand before the
  reference makes sense. Its `README.md` states the whole design on one page and catalogs the rest.
- **`reference/`** — what each public item does, grouped by family rather than one document per
  item, since a project's providers usually come in closely related sets. Its `README.md` carries a
  table of every public item and the catalog.
- **`guides/`** — prescriptive documents for using the project: how to write a new provider for it,
  how to wire a context, how to recognize and fix the common mistakes.
- **A comparison document**, named for what it compares against (`serde-comparison.md`), when the
  project replaces or extends a well-known library: what it matches, what it lacks, and when the
  original is the better choice.
- **`testing.md`** — what the project's tests pin, which checks they assert, and what is untested.
- **`issues.md`** — the open defects, missing features, and housekeeping items, grouped in that order.
  Each defect shows the code that triggers it and what happens, per
  [../AGENTS.md](../AGENTS.md#show-the-example-behind-an-error-message). Remove an entry in the same
  change that fixes it.

## Reference entries

Each public item in a reference document gets its own level-two section in a fixed order, so a
reader can find the same fact in the same place for every provider. Open with one sentence saying
what the item is, then:

- **Definition** — the impl header and bounds as the source writes them, in a code block.
- **Behavior** — what it does, in prose: what it produces on the wire or accepts from it, and how it
  fails.
- **Context dependencies** — what it looks up through the context, since that is what a context must
  wire for it to work.
- **Pairing** — for a project with both directions of an operation, which item handles the other
  direction, or that none does.
- **Known issues** — present only when there is something to record, linking to `issues.md`.

A reference document opens with a short introduction to the family and ends with a **Source** section
listing, one per bullet, the files the items live in.

## Say what public material a document feeds

These documents are the source for public writing about the project: its repository README, its
rustdoc, a deep dive on the website. End each document with a **Public material derived from this**
line naming what it feeds, or `None yet` when nothing does. The README carries the full map, and the
website's own planning documents under [../website/](../website/README.md) record the pages themselves.

## Registering a document

Register a new document in its directory's `README.md` catalog, in the project `README.md` catalog,
and in [../summary.md](../summary.md), all in the same change. A new project section is registered in
[README.md](README.md) and in [../sibling-projects.md](../sibling-projects.md), per
[../AGENTS.md](../AGENTS.md#registering-a-document-and-adding-a-section).
