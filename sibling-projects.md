# Sibling projects

The Context-Generic Programming ecosystem is split across several repositories that are developed
together, and this file records where each one lives and which revision of it to read. An agent
working here routinely needs one of them — to verify a claim against another project's source, to
revise a document a change here affects, or to keep a fixture and the prose that describes it in
step — so treat this table as the authoritative list of what exists alongside this repository.

The knowledge base documents these projects rather than duplicating them: `cgp/` and `cargo-cgp/`
each document one member's own subject, so every claim in them is verified against that member's
source; the skills built from this base live in `cgp-skills`; the public website is documented from
this side in `website/`, because a published page may not link back here; and the libraries built
*with* CGP are documented briefly in `projects/`.

| Project | Repository | Branch/tag to read | What it is |
|---|---|---|---|
| `cgp` | <https://github.com/contextgeneric/cgp> | `main` | The CGP library: the proc-macro suite and the runtime crates its expansions target. |
| `cargo-cgp` | <https://github.com/contextgeneric/cargo-cgp> | `main` | CGP's first-class toolchain: the cargo subcommand that makes CGP compile errors readable and expands CGP macros. |
| `cgp-skills` | <https://github.com/contextgeneric/cgp-skills> | `main` | The agent skills for CGP, deployed on their own — the `/cgp` skill among them. |
| `cgp-website` | <https://github.com/contextgeneric/contextgeneric.dev> | `main` | The public website at <https://contextgeneric.dev>: a Docusaurus site holding the docs, tutorials, and blog. Documented in [website/](website/README.md). |
| `hypershell` | <https://github.com/contextgeneric/hypershell> | `main` | A modular type-level DSL for shell-script-like programs, built with CGP. Documented in [projects/hypershell/](projects/hypershell/README.md). |
| `cgp-serde` | <https://github.com/contextgeneric/cgp-serde> | `main` | Serde's `Serialize` and `Deserialize` rebuilt as CGP components. Documented in [projects/cgp-serde/](projects/cgp-serde/README.md). |
| `cgp-examples` | <https://github.com/contextgeneric/cgp-examples> | `main` | Runnable example crates — `builder`, `expression`, `greet`, `transfer`, `web-app` — several of which are the origin of the scenarios in [examples/](examples/README.md). |
| `cgp-example-profile-picture` | <https://github.com/contextgeneric/cgp-example-profile-picture> | `main` | A single worked tutorial evolving one real application from a monolithic function to a modular CGP design; the origin of [examples/profile-picture.md](examples/profile-picture.md). |
| `cgp-anatomy` | <https://github.com/contextgeneric/cgp-anatomy> | `main` | *The Anatomy of Context-Generic Programming*, a book-length report on CGP and fission-driven development, together with the preserved record of how it was co-authored by the project's author and an LLM — the human draft, the instructions, each AI revision, and the methodology. |

The two example repositories have no directory of their own here, and the reason is a rule rather than
an oversight. [examples/AGENTS.md](examples/AGENTS.md) requires a worked example to be **self-contained
and to cite no source**, re-derived in current vocabulary rather than copied — so an example document
must not point back at the repository its scenario came from. Recording the relationship here instead
keeps the provenance findable for an agent without putting a citation in the document. Both repositories
track the same `cgp` version as the library, so they are reliable references for current syntax.

Two entries need a note on their names. The website's local checkout is `../cgp-website` while its
repository is named `contextgeneric.dev`, so the directory and the remote do not match — use the
directory name when locating the checkout and the repository name when writing a link. And
[Hermes SDK](https://github.com/informalsystems/hermes-sdk/), the first real-world adopter of CGP, is
developed outside the contextgeneric organization and is not a sibling: read it as an external
reference, never expect a local checkout of it, and do not edit it.

## Finding a sibling

Look for a sibling in the parent directory first, at `../<project>`. Every project in this list,
including this one, is expected to sit side by side under one parent directory in a local
environment, so `../cgp` is the fastest and most current reference — it reflects uncommitted work
that GitHub does not. When the checkout is absent, fetch the file you need from the repository above
instead, at the revision the table records.

## Reading a sibling versus linking to one

Reading and linking follow different rules, and conflating them is the mistake to avoid. When you
**read** a document or a source file from a sibling, use the branch or tag this table names, so every
project sees the same revision of the others. When you **link** to one from a committed file here, always
write a GitHub URL on the `main` branch (`https://github.com/contextgeneric/<project>/blob/main/<path>`)
rather than a relative `../<project>/...` path, so the link resolves for a reader who has only this
repository checked out. A bare mention of a checkout's location, like the path `../cgp`, is a
filesystem reference rather than a link and stays relative.

## Updating a revision

The branch or tag recorded above changes **only on explicit instruction**, such as when a project
cuts an official release and the ecosystem should pin it. During ordinary development every entry
stays `main`, and it deliberately does *not* track a feature branch in progress: work in flight is
read from the local sibling checkout, not from a revision recorded here. The same rule governs the
`main` in a cross-project link — update it only when told to, as part of a release.
