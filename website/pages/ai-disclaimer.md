# AI disclaimer

The disclaimer states how the project uses AI, part by part, from the most agent-written to the
least, and who is responsible.

- **URL:** <https://contextgeneric.dev/docs/ai/disclaimer>
- **Source:** [docs/ai/disclaimer.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/ai/disclaimer.md)
- **Status:** Current
- **How it was made:** written by an agent from
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md), which specifies it; level one of
  the four it describes. The revision awaits the author's required pre-publication read, and its
  footer records agent authorship without claiming that review.

## What it covers

The page opens with the settled descriptor, a summary of AI's roles and the author's design
ownership, and a sentence saying the sections run from most agent-written to least. It explains why
the division varies: agents get more writing responsibility where output can be checked against
existing code and does not become part of a user's application, and checking an implementation is
distinct from deciding what the library should do.

The sections then run from most AI to least:

- **Documentation and reference pages,** the longest, because it is the only level whose
  trustworthiness rests on a process rather than a person: the knowledge base, the rule that source
  outranks every document, claims read from code, tests, and expansion snapshots rather than recalled,
  documentation changing with the behavior it describes, the author directing the work while agents
  ask rather than guess, the per-commit model trailers that make it checkable, the review arrangement
  (every page outside the read-in-full list ships on its guide and a spot check), and which checks are
  mechanical and which depend on agents and review.
- **Blog posts and tutorials,** where the author drafts and an agent revises.
- **Tooling and tests,** covering `cargo-cgp` and the test suite under one rule, that neither becomes
  part of a user's program, and closing on the canonical `cargo cgp check` qualification from
  [vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each).
- **The CGP library,** whose design is entirely the author's, separated from the macro implementation
  work he directs and shares, with the limits of source verification, human review, and tests,
  including wrong test expectations and missing cases.
- **Contributions from others:** the light contribution policy, its prompt requirement, the value of
  reporting problems in the base, and a link to the [contributing page](knowledge-base.md).
- **Responsibility:** the page's one sentence in the author's own voice, and where to report an error
  (the issue tracker for the base, Discussions or the repository otherwise).
- **How pages are marked:** the provenance notes, and why older pages lack them.

## How it relates to the knowledge base

[ai-disclosure.md](../../communication-strategy/ai-disclosure.md) owns the policy, the wording
rules, the two claims easiest to get wrong, and the page's specification. Its review claim is taken
from the [authorship rule](../../communication-strategy/ai-disclosure.md#the-two-claims-that-are-easiest-to-get-wrong) rather
than paraphrased, because a wrong version is a false public claim about the project. The disposition
behind it is in [author-personality.md](../../communication-strategy/author-personality.md), and the
linking mechanics in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md#linking-to-it-from-a-page).

The page is one of the two surfaces allowed to link into the knowledge base, with the
[knowledge-base pages](knowledge-base.md), per [AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links): the
base is the subject it discloses. It links the repository's front door, never a path inside it, and
links the [process page](knowledge-base.md) for the full account.

## Maintaining it

- Revisit it when the review policy changes, when a part of the project starts or stops being
  agent-written, and when a level's stated limit stops being true. It describes a working
  arrangement, so it can become false while still reading well.
- **Keep the review claim non-uniform.** Flattening it into "everything is reviewed" is the most
  damaging edit available here.
- **Keep the library section's split between design and implementation,** because the `cgp`
  repository's commit trailers would disprove a blunter claim in a minute.
- **Do not reword its section headings.** Every page with a provenance note links them
  (`#documentation-and-reference-pages`, `#blog-posts-and-tutorials`, `#tooling-and-tests`,
  `#the-cgp-library`, and the rest), the anchors come from the heading text, and a broken one fails
  the build.
