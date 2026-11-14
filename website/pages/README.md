# Page records

This directory holds one record per standalone website page and per `docs/` section, so a task on a
page reads that page's record alone. Each record follows the document template in
[AGENTS.md](../AGENTS.md#the-document-template). The facts every page shares, such as the build, the
branches, the `example-code` crate, and the navigation, are in [site.md](../site.md).

Pages recorded elsewhere:

- **Blog posts:** one record each under [blog/](../blog/README.md).
- **Tutorial series:** one record each under [tutorials/](../tutorials/README.md).
- **Projects** ([docs/projects/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/projects),
  position 8): ported from the base's [projects/](../../projects/README.md) sections, with the
  blueprint and one plan per project under [projects/](../projects/README.md) and the page type in
  [writing-guides/project.md](../writing-guides/project.md). Draft: the index, 21 Hypershell pages,
  49 cgp-serde pages, and 14 cgp-examples pages are written on `v0.8.0`; the error backends are
  planned.

## Standalone pages

- [front-page.md](front-page.md): the front page, its hero, code band, and five-section essay.
- [introduction.md](introduction.md): the docs root, which defines CGP briefly and routes by question.
- [quickstart.md](quickstart.md): the install, one program, and its output.
- [overview.md](overview.md): the feature tour with compiled examples and the problems table.
- [resources.md](resources.md): the ecosystem's link directory.
- [contribute.md](contribute.md): the contribution paths and the acknowledgement.

## Docs sections

- [concepts.md](concepts.md): the explanation tier, eighteen pages, and what each must preserve.
- [comparisons.md](comparisons.md): eleven pages placing CGP among related ideas.
- [reference.md](reference.md): the construct reference, its groups, mapping, and port conventions.
- [compile-errors.md](compile-errors.md): the reference's consolidated error page and code tables.
- [glossary.md](glossary.md): the reference's term lookup and its linking rules.
- [cargo-cgp.md](cargo-cgp.md): the tool's nine pages and the facts behind their quoted output.
- [ai-overview.md](ai-overview.md): the AI section's landing page and its two directions.
- [ai-skills.md](ai-skills.md): the skill index and the skill served from the submodule.
- [knowledge-base.md](knowledge-base.md): the four pages that explain this base to a person.
- [ai-disclaimer.md](ai-disclaimer.md): how the project uses AI, part by part.
