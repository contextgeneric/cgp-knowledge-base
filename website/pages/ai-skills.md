# AI skills

The AI skills pages publish CGP's agent skills for readers who want to hand them to an agent: one
index page for the section, an installation page, then one directory per skill, today the `/cgp`
skill, whose own files are served unedited.

- **URL:** <https://contextgeneric.dev/docs/ai/skills/>
- **Source:** [docs/ai/skills/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/ai/skills)
- **Status:** Current: the index is written and the skill is served from a pinned submodule
- **How it was made:** the index written by an agent; the skill pages are
  [`cgp-skills`](https://github.com/contextgeneric/cgp-skills) published unedited

## What it covers

The index, *Agent Skills*, names Context-Generic Programming, says why an agent needs a skill (the
macros generate code the agent cannot see, and its training may show syntax the library no longer
accepts), and introduces the `/cgp` skill: what its main page covers, a few of its references, that
it supports `cgp` v0.8.0 and later, and that it has the agent check for a newer skill when the
project's `cgp` is newer. It says the skill does not make the agent's code correct and asks the
reader to review what the agent writes, links [the installation page](skill-installation.md), routes
learners to the tutorials and Concepts, sends a reader whose question outgrows the skill to the
[knowledge-base using page](knowledge-base.md), and says the pages are a pinned snapshot. It carries
no skill content of its own, and its foot carries the provenance line for documentation pages: level
one of the four in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md).

**Each skill has its own directory, and its pages are symlinks, not copies.** `cgp-skills` is a git
submodule at the repository root's `cgp-skills/`. Under `docs/ai/skills/cgp/`, `SKILL.md` and one
page per file in `cgp/references/` are symlinks into it, so the site serves the skill's own bytes at
a pinned revision; the directory's `_category_.json` labels it `/cgp` and opens its `SKILL` page.
[site.md](../site.md#how-the-site-is-built) records the three build settings this needs. The live
site's one older skill URL, `/docs/ai/skills/references/modularity-hierarchy`, redirects through a
static page under `static/docs/ai/skills/references/`.

## How it relates to the knowledge base

The skill is built from this base and is one of the five views of CGP's truth that the
[synchronization rule](../../AGENTS.md#the-synchronization-rule) keeps in agreement. The site renders
the skill repository rather than transcribing it, so the page cannot drift from the skill, and
correcting the skill is the only way to correct the page. Three consequences follow:

- **The skill's links are published, and that is accepted.** The skill cites the knowledge base by
  GitHub URL roughly ninety times. These pages are the bounded exception to the
  [one-way link rule](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links):
  they are prose for agents, the index says so first, and nobody hand-writes them.
- **Heading depth matters here.** Docusaurus anchors `h2` and `h3` only, so a skill file must have one
  `#` title with its sections beneath it, or its sections lose their anchors and table-of-contents
  entries. Check with a count of `#` headings outside code fences; a plain grep overcounts shell
  comments inside fenced blocks.
- **The skill's front matter is not Docusaurus front matter.** Docusaurus tolerates `SKILL.md`'s
  `name`/`description` block and takes the title from the first heading, so the sidebar reads
  "Context-Generic Programming (CGP) in Rust"; only a `sidebar_label` in the upstream file could
  change it.

## Maintaining it

- The index is the only page here an agent writes. Correct the skill in
  [`cgp-skills`](https://github.com/contextgeneric/cgp-skills), read that checkout to know what the
  skill says, and leave the submodule pointer to the author, per
  [AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#the-agent-skill).
  A lagging snapshot is not a defect.
- Advancing the snapshot is one submodule pointer commit, but a **new file** in `cgp/references/`
  also needs a symlink beside its siblings in `docs/ai/skills/cgp/references/`, because the site
  publishes named files rather than a directory glob.
- A **new skill** gets its own directory beside `cgp/`, with its symlinks and a `_category_.json`,
  and a section on the index.
