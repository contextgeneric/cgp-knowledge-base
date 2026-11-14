# AI section overview

The overview is the AI section's landing page: it orients a reader with the settled descriptor and
routes by question under two headings that keep the section's two directions apart.

- **URL:** <https://contextgeneric.dev/docs/ai/>
- **Source:** [docs/ai/index.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/ai/index.md)
- **Status:** Current, on the `v0.8.0` branch
- **How it was made:** written by an agent (level one), following
  [writing-guides/orientation.md](../writing-guides/orientation.md); not yet read by the author

## What it covers

The category's `link` targets the page in place of a generated index. *Working with CGP through an
agent* is the feature: what the agent skill and knowledge base can reduce, that the reader still
reviews the result, routes to the skill, the using page, and the contributing page, and a route to
the tutorials and Concepts for a reader learning CGP themselves. *How the CGP project uses AI* is the
fact about the project: two sentences summarizing the disclaimer's arrangement, then routes to the
disclaimer, the process page, and the knowledge-base index.

**The section holds pages pointing in opposite directions, and keeping them apart is its design
problem.** The [skill pages](ai-skills.md) are a feature; the [disclaimer](ai-disclaimer.md) is a
fact about the project; the [knowledge-base subsection](knowledge-base.md) has one page of each kind.
The category is labelled "AI-Assisted Development" and the directory stays `docs/ai/`. The unmerged
`rustlab-presentation` branch renames the directory to `docs/ai-assisted-development/`, which would
move every URL in the section for a label that already reads correctly, so it is not worth doing.

## How it relates to the knowledge base

It is an orientation page, so [writing-guides/orientation.md](../writing-guides/orientation.md)
governs its shape: one line of orientation, routes named by the question each answers, and nothing
that teaches or persuades. Its summary of how the project uses AI comes from the
[disclaimer](ai-disclaimer.md) and [ai-disclosure.md](../../communication-strategy/ai-disclosure.md);
its sentence on what agent support can do follows
[message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these). It
links no knowledge-base file.

## Maintaining it

- Revisit it when a page joins or leaves the AI section, and whenever the disclaimer's arrangement
  changes, since its two-sentence summary is a public claim that must match the disclaimer.
- Keep it a routing page; an explanation that grows here belongs on the page it routes to.
