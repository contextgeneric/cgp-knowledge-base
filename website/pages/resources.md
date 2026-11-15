# Resources

Resources is the site's section for material about CGP beyond the documentation and the places where
people discuss it, one subpage per kind; its index introduces the section, *Videos* holds the
recorded talks, and *Community* holds the discussion channels and the social account.

- **URL:** <https://contextgeneric.dev/docs/resources>,
  <https://contextgeneric.dev/docs/resources/videos>, and
  <https://contextgeneric.dev/docs/resources/community>
- **Source:** [docs/resources/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/resources)
- **Status:** Current on the `v0.8.0` branch; the live page is the older list described under
  *Where it diverges*

## How the page was made

An agent wrote the pages to [the orientation guide](../writing-guides/orientation.md#resources),
when the author kept Resources for material beyond the documentation and asked for a subpage per
kind, starting with videos, and approved a Community page for the discussion channels and the
social account. Each page's foot carries the provenance line for documentation pages: level one of
the four in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md).

## What it covers

The index names Context-Generic Programming, links the Introduction, and relates the short form
"CGP enables pluggable trait implementations in Rust" to the rest of the documentation, then gives
each kind of resource its own section:

- **Videos:** what the *Videos* page holds, naming the RustLab 2025 talk and its transcript.
- **Community:** what the *Community* page is for, naming its four channels.
- **API documentation:** `cgp`'s [docs.rs](https://docs.rs/cgp) entry, the only link to it on the
  site, beside the Reference for what each construct does and generates, following
  [the reference guide](../writing-guides/reference.md).
- **More to come:** more kinds, such as events, will be added, each with a page of its own.

*Videos* opens by saying its talks introduce CGP, with the short form beside the name, and says what
each entry gives. Its one entry, *RustLab
2025: How to stop fighting with coherence*, embeds the talk in a player that scales to the column's
width and links its [transcript post](../blog/rustlab-2025-coherence.md).

*Community* opens with the name and the short form beside a reader's unanswered question, then gives
two sections and a closing route. *Ask a question or start a discussion* lists the Discord server
for quick and beginner questions, GitHub Discussions for threads others find later, and the r/cgp
subreddit for public discussion, then sends a reader with a wrong page to Contribute's *Report a
problem*. *Follow CGP's news* links the Bluesky account `@contextgeneric.dev`, the blog, and its RSS
feed. *Help with CGP* routes to Contribute. It is the one page that lists every channel; Contribute
and the Introduction link it.

The section lists no crates, tools, or projects, which the Tooling, AI, and Projects sections cover,
and leaves out the CGP Patterns book and the Hermes SDK, which are
[legacy resources](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#legacy-resources).
The Introduction's routing list sends a reader who wants a talk to *Videos*, and one with a question
or who wants CGP's news to *Community*.

## How it relates to the knowledge base

The talk's transcript and its record, [rustlab-2025-coherence.md](../blog/rustlab-2025-coherence.md),
are the source for the line that describes it.

## Where it diverges

The live page on `main` is a single list that omits `cargo-cgp` and the agent skill, names
`cgp-error-anyhow` but not `cgp-error-eyre` or `cgp-error-std`, lists `cgp-serde` by GitHub URL,
carries a books group with the CGP Patterns book and the Hermes SDK among its projects, and lacks a
`description`. The `v0.8.0` section replaces it when the branch merges, at the same
`/docs/resources` URL.

## Maintaining it

- Give each new kind of resource its own subpage, so its URL stays stable, and a section on the
  index in the same change; revise *More to come* when the kinds it names arrive.
- Add a new channel or social account to *Community* and to the footer's Community column, and
  nowhere else, so the list keeps one home.
- Add each new talk to *Videos* in the change that publishes it, with its transcript post where one
  exists, and check every link when a page is touched.
- The pages are `.md` files, which Docusaurus reads as CommonMark, so the video's `style` is a plain
  HTML attribute; a JSX style object is dropped from the output.
