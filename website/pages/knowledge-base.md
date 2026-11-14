# The knowledge-base pages

The knowledge-base subsection explains this base to a person in four pages: an index, one page on
how the documentation is written, and two how-to pages.

- **URL:** <https://contextgeneric.dev/docs/ai/knowledge-base/>
- **Source:** [docs/ai/knowledge-base/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/ai/knowledge-base)
- **Status:** Current, on the `v0.8.0` branch; awaiting the author's read of the process page
- **How it was made:** all four written by an agent (level one) from
  [writing-guides/knowledge-base.md](../writing-guides/knowledge-base.md); none read by the author
  yet, and each footer records agent authorship without claiming review

## What it covers

The four pages explain the public [knowledge base](../../README.md) and keep the AI section's two
directions apart:

- **The index** (`index.md`): what the base is, who writes it and for whom, the order of authority
  from source code to base to skill and site, a one-line map of each top-level section named in
  prose, a section on its current state (the errors the checks can miss, and problems filed on the
  issue tracker), the four entry files as links, and routing by question.
- **How CGP's Documentation Is Written** (`how-cgp-is-documented.md`), the fact about the project:
  the problem of one-shot prompting from stale training material and of reading macro source, the
  write-once-and-keep-true rules, `#[cgp_component]` traced through its five views, the `AGENTS.md`
  rules with the section writing guides and the code repositories' own files, and the communication
  strategy, who directs the work and its separate passes, how the site's
  pages derive from the base, and where the checks stop, including the errors they miss and where to
  file one.
- **Using the Knowledge Base with Your Agent** (`using-it-with-your-agent.md`), the site's first
  how-to page: when the skill suffices, access, the instructions to give an agent with the section
  that owns each kind of question, the context cost of `summary.md`, and reviewing the answer, with
  problems filed on the issue tracker along with the prompt that surfaced them.
- **Contributing to CGP with an Agent** (`contributing-with-an-agent.md`), the second how-to page:
  the light contribution policy (use the knowledge base, and include the prompts behind an
  AI-assisted pull request or issue), reporting problems in the base as a contribution, the
  side-by-side checkout layout, the `AGENTS.md` files and their shared documentation obligation, the
  `point-first-writing` skill, the two rules that shape how the agent works with the contributor (ask
  rather than guess, commit only when asked), and the macro review and error-message workflows.

**The pages carry no prompt templates,** by the author's decision, until each has been tested enough
to recommend. Adding one follows the testing step in the
[guide](../writing-guides/knowledge-base.md#checking-a-draft), with each run recorded here.

## How it relates to the knowledge base

Every process claim comes from
[ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-knowledge-base-behind-the-first-level),
which also owns the
[contribution policy](../../communication-strategy/ai-disclosure.md#contributions-from-outside-the-project);
the page shape, how-to rules, and draft checks come from
[writing-guides/knowledge-base.md](../writing-guides/knowledge-base.md). The term follows
[vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each), and
the readers are the two hypothesis profiles in
[readers.md](../../communication-strategy/readers.md#the-reader-who-doubts-agent-written-documentation).

The pages are the second exception to the [one-way link rule](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links):
they link the base's front door, its issue tracker, and its four top-level entry files, and name every
deeper path in prose. The base's [README](../../README.md#reading-it-from-outside-the-project) carries
the matching section for an outside agent, which the using page relies on.

Pages outside the subsection link in with one line beside the reader's task: the skill index to the
using page, the Contribute page's *Contribute Code or Documentation* section to the contributing
page, and the disclaimer's documentation section to the process page. The v0.8.0 release draft's
placeholder knowledge-base link is recorded in
[its post record](../blog/v0-8-0-release.md#maintaining-it), since setting it is the author's call.

## Maintaining it

These pages describe the base's own structure, so they go stale when the base changes. Revisit them
in the same change as any of these:

- a top-level section of the base is added, renamed, or removed, or an entry file is renamed;
- a section or path the using page names moves;
- the documentation process or its review arrangement changes, together with the disclaimer;
- the contribution policy is replaced by the fuller one it promises.

The process page is on the author's read-in-full list; the other three ship on the guide and a spot
check.
