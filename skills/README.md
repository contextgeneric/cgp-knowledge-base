# Writing skills

This directory publishes the agent skills that the knowledge base and its sibling projects name in
their rules but that no other repository ships. A rule such as "apply the `/point-first-writing`
skill" is only useful to an agent that can load the skill, and a contributor working outside the
author's own environment has no other place to get it.

Each skill sits in its own directory with a `SKILL.md`, the layout agent harnesses load skills from,
so a contributor can copy or link the directory into wherever their harness looks for skills. The
member repositories do not ship a copy, so this directory is the only one to edit, and a link to it
stays current where a copy would drift.

The CGP skill is not here. It lives in [`cgp-skills`](https://github.com/contextgeneric/cgp-skills)
and is published on the website, because it teaches CGP rather than a convention for writing about
it.

## The catalog

Register a new skill here, and in [../summary.md](../summary.md), in the same change that adds it.

- [point-first-writing](point-first-writing/SKILL.md): the prose convention for documents, guides,
  and code comments. It leads each paragraph with its point, uses prose for arguments and lists for
  sets, keeps to plain English, and replaces em dashes with punctuation that states the
  relationship. [writing-styles.md](../communication-strategy/writing-styles.md) builds its
  sentence-level rules on it, and the `AGENTS.md` files of this base, `cgp`, `cargo-cgp`, and
  `cgp-skills` require it.
