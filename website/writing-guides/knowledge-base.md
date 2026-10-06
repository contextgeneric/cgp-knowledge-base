# Writing the knowledge-base pages

The knowledge-base pages explain the public CGP knowledge base to a person: what it is, how CGP's
documentation is written from it, and how to direct an agent to use it for learning, auditing, or
contributing. They are the only hand-written pages besides the disclaimer that may link into the
base, and two of them are the site's first how-to guides.

- **Where they live**: `docs/ai/knowledge-base/`, a subsection of the AI section between the agent
  skill and the disclaimer
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md), with no first-person
  passage
- **Derived from**: [the base's README](../../README.md) and [AGENTS.md](../../AGENTS.md) for what
  the base is;
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-knowledge-base-behind-the-first-level)
  for every claim about the process and for the contribution policy; the member repositories'
  `AGENTS.md` files for the contributor workflows
- **Scale**: four pages, namely an index, one explanation of the process, and two how-to guides
- **Recorded in**: one entry in [site-structure.md](../site-structure.md#knowledge-base)

## Why this is its own kind of page

These pages differ from every other page on the site in what they point at. Every other page
explains CGP and may never send the reader into the knowledge base. These pages explain the
knowledge base itself, so they cannot do their job without naming its files, and the [one-way link
rule](../AGENTS.md#the-one-way-link-rule) grants them a bounded exception for that reason.

They also carry both directions of the AI section, which
[information-architecture.md](../information-architecture.md#the-target-page-inventory) requires to
stay apart. The process page is a **fact about the project**, read by someone deciding whether to
trust agent-written pages. The two how-to pages are **features**, read by someone directing an
agent. A page that blends them reads as either a sales pitch for the process or a disclosure dressed
as a feature, so each page holds one direction.

## The section shape

Four pages, ordered by what the reader is doing: orienting, deciding whether to trust the process,
then acting on it.

**The index** (`index.md`, the subsection's `link` target) orients. It opens with the settled
descriptor and a link to the Introduction, then says what the base is, who writes it, and who it is
written for. It gives a one-line map of each top-level section, named in prose rather than linked.
It states the order of authority: the source code outranks the base, and the base outranks the agent
skill and the website pages derived from it. It concedes that the base is written for agents and
records unfinished work and known defects, and it states in a section of its own that the base is in
an early phase and under active development, with many documents still awaiting review, and that it
improves step by step toward full accuracy to the author's intent. It routes onward by the question
each page answers. Avoid exact document counts, which go stale with every change to the base;
"several hundred documents" stays true.

**How CGP's Documentation Is Written** (`how-cgp-is-documented.md`) explains the process. It opens
with the problem the process answers, as a mechanism rather than a judgement: an agent reading CGP's
macro source sees token manipulation rather than meaning, and an agent prompted without a written
record falls back on its training, much of which for CGP shows syntax the library no longer accepts.
It then describes the practice, tracing one construct (`#[cgp_component]`) through the views that
must agree, so "kept in sync" is something a reader can check. It says who directs the work: the
author designs CGP, writes the rules, and chooses what is documented, and the rules tell agents to
ask rather than guess and to check claims before polishing prose. It links the disclaimer for who
reviews what rather than restating the review arrangement. It ends on the limits, including the
base's early phase, and sends a reader who finds an error to the issue tracker. Every claim comes
from
[ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-knowledge-base-behind-the-first-level),
and the page is on the author's [read-in-full
list](../AGENTS.md#who-drafts-a-page-and-who-reads-it-before-it-publishes).

**Using the Knowledge Base with Your Agent** (`using-it-with-your-agent.md`) is a how-to. It says
when the agent skill is enough and when the base is needed, covering both meanings of auditing CGP
(reviewing the library's source, and reviewing what the macros add to a project through
`cargo cgp expand`). It then gives access, the instructions to include in a prompt (load the skill,
read the README, read the section that owns the question, with the section for each kind of question
named), the context cost of reading, and what the reader still has to do.

**Contributing to CGP with an Agent** (`contributing-with-an-agent.md`) is a how-to. It publishes
the contribution policy, including the requirement that an AI-assisted pull request or issue carry
the prompts that produced it. It then presents reporting problems in the knowledge base as a
contribution in its own right, before any setup, and gives the local layout of the repositories. It
names the `AGENTS.md` files that bind the agent and the documentation obligation they share, then
covers the skills the rules name, how the agent works with the contributor, and the established
workflows. It is the site's only guide to contributing code, so the Contribute page links to it.

**Neither how-to page carries prompt templates yet.** A copyable prompt is a promise that it works,
and no template has been tested enough to make that promise. A page gives the instructions a prompt
should contain, in prose, and leaves the wording to the reader. Templates may be added once each has
been run as [Checking a draft](#checking-a-draft) describes; until then, adding one is a defect.

## What a how-to page owes its reader

A how-to page serves a reader who already knows what they want to do and needs the steps. This
follows Diátaxis' how-to guide and is the shape these two pages borrow, since the site has no other
page of the kind.

**Title it by the goal.** The title names what the reader will have done, and the first paragraph
says who the page is for and what it assumes.

**Give steps in the order they are taken, and keep them harness-neutral.** Name files by path and
say "load the CGP skill" rather than using one harness's `@` mentions or slash commands. Say where a
harness-specific mechanism would help without depending on it. The same rule will govern prompt
templates when they are added: plain text in a fenced block that works in any harness.

**Explain only what a step needs.** A how-to page links to the process page or the Concepts pages
for the reasoning rather than repeating it.

**State the cost where the reader pays it.** Reading the base consumes an agent's context, and
`summary.md` alone is roughly a hundred kilobytes. Say so beside the step that reads it, and give
the narrower alternative.

**Never promise an outcome.** A page may say what the base gives an agent. It may not say the agent
will be correct, or more correct than without it, since nothing records such a result. The reader
reviews what the agent produces, and every how-to page says so.

## What must not be on one

**Never link into a document inside a section of the base.** The pages may link the repository's
front door, its issue tracker, and its four top-level entry files (`README.md`, `summary.md`,
`AGENTS.md`, `sibling-projects.md`), per [AGENTS.md](../AGENTS.md#the-one-way-link-rule). Every
page that asks a reader to report a problem in the base links the issue tracker. A page that needs a
section names its directory in prose, where it is an instruction to pass to an agent rather than a
link for a person.

**Never characterize other projects' AI use, or public attitudes to it.** The process page contrasts
CGP's practice with one-shot prompting as a mechanism. It does not call anyone's output slop, and it
does not describe what the Rust community thinks of AI-written documentation, which
[evidence.md](../../communication-strategy/evidence.md) does not record.

**Never claim the process makes output correct, or better than a human's.** The honest claim is that
the process makes errors checkable and correctable against a public record.

**Never add a contribution requirement the policy does not contain.** The policy is light and says a
fuller one will follow. Do not add trailers, attestations, or review steps to it on a page.

**Keep AI-led framing off the pages that link here.** Pages elsewhere that link here, such as
Contribute and the skill index, do so in one line beside the task the reader is doing, per
[message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these).

## Checking a draft

**Check every claim about the process against
[ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-knowledge-base-behind-the-first-level)**,
and every claim about a file, a directory, or a rule against the repository that holds it.

**Check every link to the knowledge base** against the bound above: the front door, the issue
tracker, or a top-level entry file, and nothing deeper.

**Before adding a prompt template, run it** in fresh agent sessions with no prior context, against
the current base, on more than one agent if the page claims it is harness-neutral, and record each
run in the site-structure entry. A template goes on a page only once its runs show it does what the
page says. An agent's run checks that the instructions are followable; it does not show how a person
new to CGP fares, per
[readers.md](../../communication-strategy/readers.md#keeping-the-model-observed).

**Read the process page and a how-to page side by side** and confirm neither has taken on the
other's direction.

**Grep for "slop", "hallucinat", "guarantee", "ensures", and "AI-native"**, and justify or remove
each hit.
