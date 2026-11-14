# CGP has a new website, and why we moved from Zola to Docusaurus

The only post about the site itself: the move from Zola to Docusaurus, the decision to keep the
installation stock, and the project's use of LLM assistance, the closest thing to a stated policy for
how the website is built.

- **URL**: <https://contextgeneric.dev/blog/2026/02/21/new-website>, a *dated* URL, because the
  post sets no explicit `slug`; every other published post has one
- **Source**: [blog/2026-02-21-new-website.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2026-02-21-new-website.md)
- **Published**: 21 February 2026, tagged `release`
- **Status**: Current

## What it covers

- **Leaving Zola, for practical reasons:** no built-in page discovery for a sidebar, so navigation was
  hand-maintained; restyling meant forking a theme; and both took time from Rust and documentation.
- **Docusaurus kept stock:** chosen for `npx create-docusaurus`'s out-of-the-box experience, with an
  explicit commitment to a custom front page and a CSS colour change, no plugins, and no React or JSX
  beyond the landing page.
- **Rust site generators:** the gap is talent rather than technology, since most frontend expertise is
  in the JavaScript ecosystem and Docusaurus is funded where Zola is volunteer-maintained; CGP powering
  such a tool one day is placed out of scope.
- **LLM assistance, the substantive section:** the front page's design, text, and images, and the
  colour theme, were largely produced with Claude Haiku and Gemini, and the site was built in three
  days, which the author attributes to no communication latency rather than raw speed. A professional
  designer would do better, but the author was the designer before, so it is an improvement, and a
  human designer is welcome if the project grows. The site's prose, this post included, is
  LLM-reviewed.
- **The close:** a preview of v0.7.0 and implicit parameters.

## How it relates to the knowledge base

- **Site policy:** the source of most of what [site.md](../site.md#how-the-site-is-built) records;
  read it before proposing a change to how the site is built. "No plugins, no React" is a stated
  decision, so an agent adding site machinery works against it and says so to the user.
- **AI disclosure:** AI-drafted content on the website is expected and disclosed, which normalizes
  the workflow [../AGENTS.md](../AGENTS.md) describes: an agent drafts from the knowledge base and the
  author reviews. The practice is inconsistent: the [v0.6.1 post](v0-6-1-release.md) carries a per-post
  AI disclaimer while others do not, and whether to standardize it is the user's question.
- **Framing:** a revision follows the [communication strategy](../../communication-strategy/README.md)
  like any public page.

## Where it diverges

Nothing in it is stale; its forward-looking parts were overtaken. v0.7.0 shipped a week later with the
implicit arguments it previews. Only the Hello World tutorial existed then; the area-calculation series
and the AI skills section came later on the live site, and the Concepts, Reference, Comparisons,
Projects, and `cargo-cgp` sections on the `v0.8.0` branch. The live site keeps the stock installation
and front page the post describes; the `v0.8.0` branch rebuilds the front page and the theme, per
[visual-design.md](../visual-design.md), and departs from stock in three settings, all to publish the
agent skill, per [site.md](../site.md#how-the-site-is-built).

## Maintaining it

Leave it alone; it is accurate about its own moment. Treat its policy as live: a change to how the site
is built (a plugin, React, another migration) belongs in a new post and in
[site.md](../site.md#how-the-site-is-built), not in an edit here.
