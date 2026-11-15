# Installing the CGP Skill

*Installing the CGP Skill* tells a reader how to install the `/cgp` agent skill in the agent they
use, starting with asking that agent to do it, then each harness's own route, all at the skill's
release tag.

- **URL:** <https://contextgeneric.dev/docs/ai/skills/installation>
- **Source:** [docs/ai/skills/installation.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/ai/skills/installation.md)
- **Status:** Current on the `v0.8.0` branch; the live site has no installation page

## How the page was made

An agent wrote the page in natural style, following the how-to rules of
[the knowledge-base pages' guide](../writing-guides/knowledge-base.md#what-a-how-to-page-owes-its-reader),
since no guide covers the skill section; its foot carries the provenance line for documentation
pages: level one of the four in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md).
The author asked for the page and for it to open with the general route: give the agent the
repository's URL and ask it to install the skill.

## What it covers

The opening names Context-Generic Programming beside what the skill does, says the skill is
Markdown with no scripts, and says every route takes the `v0.8.0` tag, the version that describes
`cgp` v0.8.0. Then, in order:

- **Ask your agent to install it:** a request naming the repository's URL and the tag, which sends
  the agent to the `cgp-skills` README's steps for agents and asks it to confirm the scope first.
- **Installing it yourself:** one section per harness, each with its own installer and its user and
  project skills directories: Claude Code's plugin, invoked as `/cgp:cgp`; Codex's plugin, listed as
  `cgp:cgp`, and `$skill-installer`; Cursor's folders, `~/.cursor/skills/` being the one that syncs
  to Cloud Agents; `gh skill` for GitHub Copilot and VS Code; `gemini skills install`, which cannot
  pin a tag; OpenCode's folders; Pi's `pi install`; and `npx skills` or `gh skill` for any other
  agent, with the former's telemetry and how to turn it off.
- **Copying the skill by hand:** the clone and copy commands, keeping `SKILL.md` with `references/`,
  and copying rather than linking, since Codex names a linked skill `cgp:cgp`.
- **Installing it for a team:** committing the skill into the project's skills folders.
- **Checking that it loaded**, with the review warning, **updating to a newer version**, and
  **agents without skill support**, which attach `SKILL.md` at the tag.

## How it relates to the knowledge base

The page and the `cgp-skills` README give the same routes and directories, and a rule in
`cgp-skills`' `AGENTS.md` keeps them in agreement. The commands come from each tool's help,
documentation, or source. Before the tag existed, each route that runs on the maintainer's machine
was installed from a local clone into a scratch project: the copy for Claude Code, Codex, OpenCode,
and Pi, `npx skills`, `gh skill`, both plugins, and Pi's package each loaded one skill, and the
ask-your-agent request led Claude Code and Codex to the README's folder for a project, where each
harness refused the copy in a non-interactive run, as it would ask the user to approve it in an
interactive one. The Cursor, GitHub Copilot, and Gemini CLI sections and the `$skill-installer`
route rest on those tools' documentation alone, since none of them was available to test. The
release post and *Using the Knowledge Base with Your Agent* link it.

## Where it diverges

- none

## Maintaining it

- Change a route here and in the `cgp-skills` README together, and move every tag with the skill's
  release.
- Follow [message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these):
  the page says what the skill helps with and keeps the review warning, without promising that it
  removes a cost.
