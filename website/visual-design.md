# The site's visual design

This document records the website's theme: its colour palette, the fonts, the code colours, how
images read in both themes, and the check that keeps every colour readable. It is a record of what the
site ships on the `v0.8.0` branch, and an agent changing a colour, a font, or an image's treatment
starts here.

- **Source:** [src/css/custom.css](https://github.com/contextgeneric/contextgeneric.dev/blob/main/src/css/custom.css)
  for the tokens and fonts, [src/prism/themes.ts](https://github.com/contextgeneric/contextgeneric.dev/blob/main/src/prism/themes.ts)
  for the code colours, and
  [docusaurus.config.ts](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docusaurus.config.ts)
  for the logo, favicon, announcement bar, and code languages
- **Check:** [scripts/theme/contrast.py](https://github.com/contextgeneric/contextgeneric.dev/blob/main/scripts/theme/contrast.py)
- **Rule:** page styles use the tokens rather than hex colours, as the website repository's
  [AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md) requires

## The palette keeps the logo's red and builds around it

The one fixed colour is the CGP logo's red, `#8f1f1d`. Everything else is chosen to sit beside it: a
tint scale of the same hue, warm neutrals in both themes, and admonition and status colours that stay
clear of the red. The tokens are CSS custom properties named `--cgp-*`, defined once for the light
theme and once for the dark theme, and they feed Infima's own variables, so the navbar, sidebar, table
of contents, breadcrumbs, pagination, tables, admonitions, blog pages, and footer follow the palette
without restyling any component.

The red cannot carry text in the dark theme. Against the dark background it reaches only about 2:1, so
the dark theme gives links and other red text a lighter tint of the same hue, `#ef8f86`, and keeps
`--cgp-red` for filled elements with white text, where it reaches 8.8:1. In the light theme the red is
the link colour itself, at 8.5:1 on the page.

The tokens fall into four groups:

- **The red and its tints:** `--cgp-red` and `--cgp-red-50` to `--cgp-red-900`. The dark theme
  redefines the tints it uses, so a tint keeps its role in both themes: `--cgp-red-50`, for example,
  is the faint surface behind the active sidebar item and breadcrumb.
- **Warm neutrals:** the page background (`#fdfaf7` light, `#161110` dark), surfaces, borders, body
  and muted text, and headings. Infima's own grey scale takes the same warm values.
- **Roles:** links and their hover colour, the focus ring, code and inline-code backgrounds, the
  highlighted-line tint, the selection, the image frame, the announcement bar, and the footer.
  `--cgp-hero-art-bg` holds the hero art's own background colour, which the front page uses for the
  circle behind the art in the dark theme. `--cgp-diff-removed` and `--cgp-diff-added` tint the front
  page's diff lines, the line Rust rejects and the lines CGP adds, and `--cgp-diff-removed-mark` and
  `--cgp-diff-added-mark` colour each one's gutter mark and verdict badge. The added green is strong
  enough to read as green on the beige code background in both themes.
- **Admonitions:** `note`, `tip`, `info`, and `warning` use a warm grey, a green, a blue-grey, and an
  amber, each with its own tint for inline code inside it. `danger`, which no page uses, keeps a red
  distinct from the brand's.

Red marks what a reader can act on: links, the primary button, and, on the front page, the rejection
mark. Display text such as the front page's tag line and pull quote, and the titles of cards and
tiles, take the heading colour, and a linked card's title turns red only on hover.

Infima sets some colours as literals rather than from its scales: the two content colours that the
table of contents and other secondary text read, its grey scale, its primary alert colours, and the
admonition highlights. The theme points each of them at the tokens, so a new Docusaurus component that
reads one of them still matches. Infima's primary hero, which the blog archive's header uses, fills
with the primary colour, so the theme gives it the warm surface instead.

## Prose links are underlined

Colour alone does not separate a link from body text, because the red and the text colour differ by
less than 3:1. Links in Markdown content are therefore underlined with a softened underline that
darkens on hover, while navigation links, heading anchors, and generated category cards keep their
own styles. The footer's links share its text colour, so the links inside its licence line are
underlined too. Every link, button, and control shows a focus ring in the brand family.

## Code has its own two themes

The code colours are two Prism themes written for the palette, one per site theme. No token uses the
brand red, so code never reads as a link or an error, and each token colour keeps 4.5:1 against the
code background, against a highlighted line's amber tint, and against the front page's two diff
tints. The code background differs from the page in both themes.

Prism's default bundle lacks several languages the site's pages use, so the config adds `toml`,
`bash`, `ebnf`, `haskell`, `ocaml`, `java`, and `scala` from the `prismjs` package Docusaurus already
installs. Java precedes Scala because Scala's grammar extends Java's.

**Known limitation:** Docusaurus renders a code block with the light theme's colours on the server and
switches them when the page's JavaScript runs. A reader in the dark theme sees light code for a moment
on first load, and always without JavaScript. This is stock Docusaurus behaviour, not something the
theme introduces.

## Two self-hosted fonts

Body text, headings, and the navbar's title use Inter, with headings at weight 600, and code uses
JetBrains Mono. The author chose the pair from six candidates tried on the built site, because the
earlier display face for headings looked too fancy and a system body font differs by operating
system. Both fonts are under the SIL Open Font License and are committed under `static/fonts/` with
their licences, as WOFF2 subsets that total about 80 KB:

- **Inter:** weights 400 to 700, upright and italic, at the text optical size, Latin, which covers
  every character the site's prose sets.
- **JetBrains Mono:** weights 400 to 700, upright only, Latin plus Greek, superscripts and
  subscripts, and box drawing, which the code blocks and quoted diagnostics use, without its ligature
  feature. The code themes set comments upright, so no browser synthesizes a slant.

Each font has a fallback face sized to its metrics, so text does not shift when the font arrives, and
the upright Inter face is preloaded. The `@font-face` rules sit in a style tag in the config, not in
`custom.css`, because a `url()` in the stylesheet is copied to a hashed file name that the preload
cannot name. Code turns ligatures off, so `->`, `=>`, and `!=` show the characters a reader types. The
website's
[scripts/fonts/README.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/scripts/fonts/README.md)
gives the commands that cut the subsets; a character outside them renders in the fallback face, so a
page that starts using a new script or symbol block needs the subset recut.

## Images read in both themes

An image loaded by `<img>` follows the operating system's colour scheme, not the site's theme switch,
so a dark variant of an image cannot track the switch. The theme frames images instead: in the dark
theme every image in Markdown content sits in a rounded, paper-coloured frame. That keeps the light
diagrams and slides from reading as bright holes in the page, and it keeps transparent diagrams with
black lines, such as the Hypershell post's, visible at all.

The three shared diagrams (`wiring-table.svg`, `coherence-scoped.svg`, and
`consumer-provider-split.svg`) use the brand red and the warm neutrals. Dark variants of them are
optional. The front page's own art keeps its colours; its record is in
[site-structure.md](site-structure.md#the-front-page), and the illustration palette for new art is in
the [homepage guide](writing-guides/homepage.md#images-metadata-and-provenance), which is separate from
this interface palette.

The social card, `static/img/social-card.jpg`, uses the palette and the heading font, and its generator
must run again whenever the tag line, the hero art, or these colours change.

## The site's frame follows the theme

The shell carries the palette in both themes:

- **Logo:** the navbar shows `cgp-logo.svg` in the light theme and `cgp-logo-dark.svg`, the same
  drawing in `#d4645a`, in the dark theme, where the original red would reach only 2.1:1.
- **Favicon:** an SVG favicon shows the logo's red, or the same lighter tint on a dark browser tab,
  beside the PNG fallback.
- **Address bar:** two `theme-color` tags give a phone's address bar the page background of each
  theme. Like the favicon, they follow the operating system's colour scheme, which is also the site's
  default.
- **Announcement bar:** its colours point at the tokens, a pale warm neutral in the light theme and a
  dark warm grey in the dark theme, so it never reads as a red banner.
- **Footer:** a deep red in both themes, with near-white text and links.
- **Blog:** the archive's header takes the warm surface, and the blog list's post titles take the
  heading colour and turn red on hover, so a page of posts does not read as a wall of red.

## Checking a change

Run the contrast check after changing any colour:

```sh
python3 scripts/theme/contrast.py
```

It reads the tokens from `custom.css` for both themes, resolves their references, and checks each pair
the site uses: text at 4.5:1, including the first line of the front page's quoted diagnostic, and focus
rings, admonition borders, the two navbar logos, and the front page's diff marks and verdict badges at
3:1. It also checks every Prism token on the code background, on a highlighted line, and on each diff
tint. It exits non-zero on a
failing pair.

The check does not see the rendered page, so a theme change also needs screenshots of one page of each
kind, in both themes and at a desktop and a phone width: the front page, a docs page with code, a
Concepts page with a diagram, the reference index and a reference page with tables, a page with
admonitions, a generated category page, a blog post with images, the blog index and archive, and the
404 page. Firefox renders scrollbars and fonts differently from Chrome, so check both.

## How this relates to the stock-site policy

The theme stays inside the [stated policy](blog/new-website.md) of a stock Docusaurus installation. It
is CSS, a Prism theme file the config imports, configuration options, and static assets; it adds no
plugin and swizzles no theme component. The policy's purpose, spending time on content rather than on
theming, still holds: the theme is a set of tokens to adjust, not a design system to maintain.
