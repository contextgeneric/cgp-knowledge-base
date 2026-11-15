# Release notes

The Release notes category lists what each official release of `cgp` and `cargo-cgp` changed, in one
dated page per release; it is drafted on the `v0.8.0` branch and publishes with that release.

- **URL:** <https://contextgeneric.dev/docs/release-notes/>
- **Source:** [docs/release-notes/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/release-notes)
- **Status:** Draft

## How the pages are made

An agent writes each page from its release's source diff, read beside the release document, the old
changelog entry, the GitHub Release body, and the release post, as
[writing-guides/release-notes.md](../writing-guides/release-notes.md#sources-and-which-one-decides)
sets out. Each page's foot carries the provenance line for documentation pages: level one of the four
in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md). The author reads the v0.8.0
notes in full before publication.

## What it covers

The index names Context-Generic Programming, says what the notes are, states how CGP numbers its 0.x
releases, and links each artifact's sub-category. Each page restates one source document, which holds
the facts the page gives and the finer detail it leaves out:

| Page | Source document |
|---|---|
| `cgp/` v0.8.0 | [releases/v0-8-0.md](../../releases/v0-8-0.md) |
| `cgp/` v0.7.0 | [releases/v0-7-0.md](../../releases/v0-7-0.md) |
| `cgp/` v0.6.1 | [releases/v0-6-1.md](../../releases/v0-6-1.md) |
| `cgp/` v0.6.0 | [releases/v0-6-0.md](../../releases/v0-6-0.md) |
| `cgp/` v0.5.0 | [releases/v0-5-0.md](../../releases/v0-5-0.md) |
| `cgp/` v0.4.2 | [releases/v0-4-2.md](../../releases/v0-4-2.md) |
| `cgp/` v0.4.1 | [releases/v0-4-1.md](../../releases/v0-4-1.md) |
| `cgp/` v0.4.0 | [releases/v0-4-0.md](../../releases/v0-4-0.md) |
| `cgp/` v0.3.1 | [releases/v0-3-1.md](../../releases/v0-3-1.md) |
| `cgp/` v0.3.0 | [releases/v0-3-0.md](../../releases/v0-3-0.md) |
| `cgp/` v0.2.0 | [releases/v0-2-0.md](../../releases/v0-2-0.md) |
| `cgp/` v0.1.0 | [releases/v0-1-0.md](../../releases/v0-1-0.md) |
| `cargo-cgp/` v0.1.0 | the [cargo-cgp/](../../cargo-cgp/README.md) section, since it is the tool's first release |

## How it relates to the knowledge base

The pages and the release documents are two layers of one history, as
[releases/README.md](../../releases/README.md) describes: a page holds the user-visible changes and
the upgrade steps, and its release document keeps the internal changes, the errors in the old
sources, and what still stands. The category sits after Resources, per
[information-architecture.md](../information-architecture.md#navigation-and-sidebar-order).

## Where it diverges from the guide

- none; no page is written yet.

## Maintaining it

- Add a page for each new release as
  [Adding a release document](../../releases/README.md#adding-a-release-document) describes, and a
  row to the table above.
- Correct a published page only where it misstates its own release, per the website's
  [AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#blog-posts);
  a later change goes on the later release's page.
- Keep the newest-first order with each page's `sidebar_position`, as the guide's
  [section shape](../writing-guides/release-notes.md#the-section-shape) gives it.
- Change the status to Historical once the pages publish: each is correct about its own release and
  does not track the library.
