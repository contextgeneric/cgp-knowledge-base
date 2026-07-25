# CGP has a new website, and why we moved from Zola to Docusaurus

The only post whose subject is the site itself. It explains the migration from Zola to Docusaurus, the
decision to keep the installation stock, and the project's use of LLM assistance for design and prose
— making it the closest thing to a stated policy for how the website is built and maintained.

- **URL** — <https://contextgeneric.dev/blog/2026/02/21/new-website> — a *dated* URL, because the
  post sets no explicit `slug`; every other post on the site has one
- **Source** — [blog/2026-02-21-new-website.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2026-02-21-new-website.md)
- **Published** — 21 February 2026, tagged `release`
- **Status** — Current

## What it covers

The post gives three reasons for leaving Zola, all practical rather than ideological: Zola has no
built-in way to discover and list pages in a sidebar, so navigation had to be hand-maintained;
customizing its appearance meant forking and editing a theme; and both consumed time better spent
writing Rust and documentation. Docusaurus was chosen for its out-of-the-box experience with
`npx create-docusaurus`, and the post commits explicitly to keeping it that way — a custom front page
and a CSS colour change, no plugins, no React or JSX beyond the landing page.

A short section reflects on Rust-based site generators, arguing the gap is talent rather than
technology: most frontend expertise lives in the JavaScript ecosystem, and Docusaurus benefits from
sustained funding where Zola is volunteer-maintained. It leaves the door open to CGP itself powering
such a tool one day, while placing that firmly out of scope.

The section on **LLM assistance** is the substantive one. It states plainly that the front page's
design, text, and images were largely produced with Claude Haiku and Gemini, that even the colour
theme was chosen this way, and that the whole site was built in three days — a timeline the author
attributes to the absence of communication latency rather than to raw speed. It is candid about the
trade-off: a professional human designer would produce something better, but the author was doing the
design themselves before, so this is a real improvement, and a human designer would be welcomed if the
project grows. It also notes that the site's prose, including the post itself, is LLM-reviewed.

The post closes by previewing v0.7.0 and implicit parameters.

## How it relates to the knowledge base

This post is the source for most of what [site-structure.md](../site-structure.md) records as policy,
and it should be read before proposing any change to how the site is built. The "no plugins, no React"
commitment in particular is a stated decision rather than an accident, so an agent adding site
machinery is working against it and should say so to the user.

The LLM-assistance section matters to this section for a different reason: it establishes that
AI-drafted content on the website is expected and disclosed, not hidden. That normalizes the workflow
[../AGENTS.md](../AGENTS.md) describes, in which an agent drafts website prose from the knowledge base
and the human reviews it. The disclosure practice is inconsistent, though — the
[v0.6.1 post](v0-6-1-release.md) carries an explicit per-post AI disclaimer while others do not — and
whether to standardize it is a question for the user rather than something to settle silently.

For framing, any revision here is governed by the same
[communication-strategy](../../communication-strategy/README.md) rules as the rest of the site; a
meta post about tooling is still public writing, and its audience is the same developers who read
everything else.

## Where it diverges

Nothing in the post is stale. Its forward-looking sections have simply been overtaken: v0.7.0 shipped
a week later with the implicit-argument feature it previews, and the tutorials, AI skills section, and
`cargo-cgp` documentation the site has since grown were not yet written. The commitment to a stock
Docusaurus installation still holds, as does the front page it describes.

## Maintaining it

Leave it alone; it is a dated account of a decision and is accurate about its own moment. Its policy
content, however, should be treated as live: when the project changes how the site is built — adding a
plugin, writing React, or migrating again — that decision belongs in a new post and in
[site-structure.md](../site-structure.md), not in an edit here.
