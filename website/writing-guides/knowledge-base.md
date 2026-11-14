# Writing the knowledge-base pages

The knowledge-base pages explain the public CGP knowledge base to a person: what it is, how CGP's
documentation is written from it, and how to direct an agent to use it for learning, auditing, or
contributing. They are the only hand-written pages besides the disclaimer that may link into the base,
and two of them are the site's first how-to guides.

- **Where they live**: `docs/ai/knowledge-base/`, a subsection of the AI section between the agent
  skill and the disclaimer, recorded in one entry, [pages/knowledge-base.md](../pages/knowledge-base.md)
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md), with no first-person
  passage
- **Derived from**: [the base's README](../../README.md) and [AGENTS.md](../../AGENTS.md) for what
  the base is;
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-knowledge-base-behind-the-first-level)
  for every claim about the process and for the contribution policy; the member repositories'
  `AGENTS.md` files for the contributor workflows
- **Reading**: the shared set and
  [the knowledge-base pages' row](README.md#the-knowledge-base-pages-and-the-ai-disclosure-page) of
  the reading map

## Why this is its own kind of page

**These pages explain the knowledge base itself**, so they cannot do their job without naming its
files, and the [one-way link rule](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links) grants them a bounded exception.

**They carry both directions of the AI section, one per page.** The process page is a **fact about the
project**, read by someone deciding whether to trust agent-written pages; the two how-to pages are
**features**, read by someone directing an agent. A page that blends them reads as a sales pitch for
the process or a disclosure dressed as a feature.

## The section shape

Four pages, ordered by what the reader is doing: orienting, deciding whether to trust the process,
then acting on it. Every page opens by naming Context-Generic Programming beside a plain description
and linking the Introduction, per the
[naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page), and
leaves out the tag line, since the pages are about how CGP is documented rather than about choosing an
implementation.

- **The index** (`index.md`, the subsection's `link` target) orients: what the base is, who writes it,
  and who it is written for; a one-line map of each top-level section, named in prose rather than
  linked; the order of authority (the source code outranks the base, and the base outranks the agent
  skill and the website pages derived from it); that the base is written for agents and records
  unfinished work and known defects; a section of its own stating that the checks can miss errors,
  so some documents still contain them, that reports move the base toward full accuracy to the
  author's intent, and where to file one; and routes by the question each page answers. Avoid
  exact document counts; "several hundred documents" stays true.
- **How CGP's Documentation Is Written** (`how-cgp-is-documented.md`) explains the process. It opens
  with the problem as a mechanism rather than a judgement: an agent reading CGP's macro source sees
  token manipulation rather than meaning, and one prompted without a written record falls back on
  training that shows syntax the library no longer accepts. It traces `#[cgp_component]` through the
  views that must agree, so "kept in sync" is checkable; says who directs the work (the author designs
  CGP, writes the rules, and chooses what is documented, and the rules tell agents to ask rather than
  guess and to check claims before polishing prose); links the disclaimer for who reviews what rather
  than restating it; and ends on the limits, including the errors the checks miss, sending a reader who
  finds an error to the issue tracker. Every claim comes from
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-knowledge-base-behind-the-first-level),
  and the page is on the author's
  [read-in-full list](../../communication-strategy/ai-disclosure.md#the-two-claims-that-are-easiest-to-get-wrong).
- **Using the Knowledge Base with Your Agent** (`using-it-with-your-agent.md`), a how-to: when the
  agent skill is enough and when the base is needed, covering both meanings of auditing CGP (reviewing
  the library's source, and reviewing what the macros add to a project through `cargo cgp expand`);
  access; the instructions to include in a prompt (load the skill, read the README, read the section
  that owns the question, with the section for each kind of question named); the context cost of
  reading; and what the reader still has to do.
- **Contributing to CGP with an Agent** (`contributing-with-an-agent.md`), a how-to: the contribution
  policy, including that an AI-assisted pull request or issue carries the prompts that produced it;
  reporting problems in the base as a contribution in its own right, before any setup; the local
  layout of the repositories; the `AGENTS.md` files that bind the agent and their shared documentation
  obligation; the skills the rules name; how the agent works with the contributor; and the established
  workflows. It is the site's only guide to contributing code, so the Contribute page links to it.

**Neither how-to page carries prompt templates yet.** A copyable prompt promises that it works, and
none has been tested enough to make that promise, so a page gives in prose the instructions a prompt
should contain. A template may be added once it has been run as [Checking a draft](#checking-a-draft)
describes; until then, adding one is a defect.

## What a how-to page owes its reader

The two how-to pages follow Diátaxis's how-to guide, for a reader who knows what they want to do and
needs the steps:

- **Title it by the goal**, and say in the first paragraph who the page is for and what it assumes.
- **Give steps in the order they are taken, harness-neutral**: name files by path and say "load the
  CGP skill" rather than one harness's `@` mentions or slash commands, noting where a harness-specific
  mechanism would help without depending on it. A future prompt template is plain text in a fenced
  block that works in any harness.
- **Explain only what a step needs**, linking the process page or the Concepts pages for the reasoning.
- **State the cost where the reader pays it**: reading the base consumes an agent's context, and
  `summary.md` alone is roughly a hundred kilobytes, so say so beside the step that reads it and give
  the narrower alternative.
- **Never promise an outcome.** A page may say what the base gives an agent, never that the agent will
  be correct or more correct than without it; the reader reviews what the agent produces, and every
  how-to page says so.

## What must not be on one

- **Never link into a document inside a section of the base.** The pages may link the repository's
  front door, its issue tracker, and its four top-level entry files (`README.md`, `summary.md`,
  `AGENTS.md`, `sibling-projects.md`), per [AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links), and every
  page that asks a reader to report a problem links the issue tracker. A section is named by its
  directory in prose, as an instruction to pass to an agent.
- **Never characterize other projects' AI use, or public attitudes to it.** The process page contrasts
  CGP's practice with one-shot prompting as a mechanism; it calls nobody's output slop and does not
  describe what the Rust community thinks, which
  [evidence.md](../../communication-strategy/evidence.md) does not record.
- **Never claim the process makes output correct, or better than a human's**; the honest claim is that
  it makes errors checkable and correctable against a public record.
- **Never add a contribution requirement the policy does not contain**, such as trailers,
  attestations, or review steps; the policy is light and says a fuller one will follow.
- **Keep AI-led framing off the pages that link here.** Contribute and the skill index link in one
  line beside the reader's task, per
  [message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these).

## Checking a draft

- **Check every claim about the process** against
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md#the-knowledge-base-behind-the-first-level),
  and every claim about a file, directory, or rule against the repository that holds it.
- **Check every link to the knowledge base** against the bound above.
- **Before adding a prompt template, run it** in fresh agent sessions without prior context, against
  the current base, on more than one agent if the page claims it is harness-neutral, and record each
  run in the pages' record; it goes on a page only once the runs show it does what the page says. An
  agent's run checks that the instructions are followable, not how a person new to CGP fares, per
  [readers.md](../../communication-strategy/readers.md#keeping-the-model-observed).
- **Read the process page and a how-to page side by side**, and confirm neither has taken on the
  other's direction.
- **Grep for "slop", "hallucinat", "guarantee", "ensures", and "AI-native"**, and justify or remove
  each hit.
