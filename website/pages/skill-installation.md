# Installing the CGP Skill

*Installing the CGP Skill* tells a reader how to install the `/cgp` agent skill in the agent they
use, starting with asking that agent to do it, then each harness's own route, all from the skill
repository's `main` branch, and how to update it.

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
Markdown with no scripts, and says every route takes `main`, which supports `cgp` v0.8.0 and every
later release, though not an older `cgp`. Then, in order:

- **Ask your agent to install it:** a request naming the repository's URL, which sends
  the agent to the `cgp-skills` README's steps for agents and asks it to confirm the scope first,
  and a warning that the harness may ask the reader to approve the copy.
- **Installing it yourself:** a warning to choose one route per harness, then one section per
  harness, each with its own installer and its user and project skills directories: Claude Code's
  plugin, invoked as `/cgp:cgp`; Codex's plugin, listed as `cgp:cgp`, and `$skill-installer`;
  Cursor's folders, `~/.cursor/skills/` being the one that syncs to Cloud Agents; `gh skill` for
  GitHub Copilot and VS Code; `gemini skills install`, which takes the default branch; OpenCode's
  folders; Pi's `pi install`; and `npx skills` or `gh skill` for any other agent, with the former's
  telemetry and how to turn it off.
- **Copying the skill by hand:** the clone and copy commands, keeping `SKILL.md` with `references/`,
  and copying rather than linking, since Codex names a linked skill `cgp:cgp`.
- **Installing it for a team:** committing the skill into the project's skills folders.
- **Checking that it loaded**, with the review warning and the skill's version check.
- **Updating the skill:** each route's update command, Claude Code's auto-update toggle, which is
  off for third-party marketplaces, Gemini CLI's reinstall, and Pi's `pi update --extensions`.
- **Agents without skill support:** attaching `SKILL.md` from `main`, and the note that the site's
  skill pages show the revision the site was built from.

## How it relates to the knowledge base

The page and the `cgp-skills` README give the same routes and directories, and a rule in
`cgp-skills`' `AGENTS.md` keeps them in agreement. The release post and *Using the Knowledge Base
with Your Agent* link the page.

The commands come from each tool's help, documentation, or source, and were tested from a local
clone before the tag existed, as far as the maintainer's machine allowed:

- **Loaded one skill:** the copy for Claude Code, Codex, OpenCode, and Pi, `npx skills`,
  `gh skill`, both plugins, and Pi's package, each installed into a scratch project or home.
- **Reached the approval step:** the ask-your-agent request, which led Claude Code and Codex to the
  README's folder for a project, where each harness refused the copy in a non-interactive run; an
  interactive session asks the user to approve it.
- **Documentation only:** the Cursor, GitHub Copilot, and Gemini CLI sections and the
  `$skill-installer` route, since none of those tools was available to test.

## Where it diverges

- none

## Maintaining it

- Change a route here and in the `cgp-skills` README together, and keep every route on `main`; no
  route names a tag, as `cgp-skills`' `AGENTS.md` requires.
- Follow [message.md](../../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these):
  the page says what the skill helps with and keeps the review warning, without promising that it
  removes a cost.
