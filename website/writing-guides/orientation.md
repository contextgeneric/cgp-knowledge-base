# Writing an orientation page

An orientation page's job is to **send the reader somewhere**, to **prove that the thing runs**, or,
on the Overview, to **show each feature working**. It does not teach, and it does not argue: its
reader has already decided CGP is worth a few minutes and wants the shortest route or the shortest
proof.

- **Where they live**: `docs/index.md`, `docs/overview.md`, `docs/quickstart.md`,
  `docs/resources.md`, and `docs/contribute.md`, each with its record under
  [pages/](../pages/README.md); the AI section's overview, `docs/ai/index.md`, follows the same
  rules, as [its record](../pages/ai-overview.md) states
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md), except the
  Contribute page's sponsorship section, which is the author's
- **Governed by**: [information-architecture.md](../information-architecture.md) for what each
  surface is for and where a reader goes next;
  [formats.md](../../communication-strategy/formats.md#the-conversion-ladder) for matching the next
  step to the reader
- **Reading**: the shared set and
  [the orientation pages' row](README.md#orientation-pages-the-introduction-the-quickstart-and-resources)
  of the reading map; the Overview reads the front page's row, and the Contribute page its own

## What separates orientation from every other page type

**If a sentence on an orientation page is not routing the reader, orienting them in one line,
getting a program to run, or, on the Overview, showing a feature, it belongs on another page.** Each
neighbouring type owns what this one refuses:

- **The [homepage](homepage.md) persuades.** A reader who clicked *Docs* has already given CGP the
  benefit of the doubt, and repeating the pitch spends their patience.
- **A [tutorial](tutorial.md) teaches**, judged on whether the reader understood an idea; an
  orientation page is judged on whether the reader got somewhere.
- **An [explanation page](explanation.md) argues *why***; an orientation page names an idea in a
  clause and links.
- **A [reference page](reference.md) specifies**; an orientation page names no syntax the reader is
  not about to type.

## What every orientation page owes its reader

- **Orient a cold reader in the first paragraph.** Any of these may be a first contact, per
  [information-architecture.md](../information-architecture.md#most-readers-do-not-arrive-at-the-homepage),
  so each opens by naming Context-Generic Programming in full, saying what CGP is in one sentence, and
  linking onward, not summarizing the front page. The Introduction and the Overview present the
  project and state the tag line whole; the Quickstart and Resources relate a short form to what they
  do, as in "CGP enables pluggable trait implementations in Rust, and this page gets one running", or
  leave it out, per the
  [naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page).
- **End every path somewhere**, naming routes by the question each answers (*how its ideas work*)
  rather than by the section's title (*Concepts*).
- **Carry a written `description`**, one sentence saying what the page is for, because these are
  among the most-linked pages and Docusaurus otherwise derives a poor one, per [seo.md](../seo.md).
- **Say only what has been checked.** Every command, link, and crate name is verified when the page
  is touched, because one dead route makes a reader distrust the rest.

## The Introduction

**The docs root, and the page that decides where most readers go.** Its reader clicked *Docs* and
wants to know what CGP is and which part of the documentation answers their question. It carries:

- **A definition** of two or three paragraphs: the settled descriptor, a plain sentence or two on what
  it lets a reader do, without a scenario of its own, and the four words every other page assumes
  (*context*, *provider*, *wiring*, *component*), each glossed in a clause. This vocabulary is the one
  teaching-shaped thing an orientation page keeps.
- **A first step**, naming the tutorials.
- **A routing list**, one line per destination, keyed on the reader's question.

It **does not carry the maturity discussion**, which the front page's cost section holds and an
evaluator reaches from above the fold there, and it **does not route newcomers to the blog**, which it
names as a record of releases and talks whose older posts describe the library as it was.

## The Overview

**The feature tour: it shows each feature working, states where it stops, and sends the reader to the
page that explains it.** It is the front page's
[offload destination](homepage.md#the-offload-rule-and-the-pages-it-offloads-to) for essay sections 2
and 3, and it settles the site's feature lists: the front page carries the five from
[identity.md](../../communication-strategy/identity.md#the-headline-feature-set), four as cards and the
fifth in its reassurance line, and the Overview expands each with an example. Each section leads from
a problem the reader may have to its example and limit, so a reader who followed a front-page card
reads one connected explanation.

The page has these parts, in this order:

- **Opening:** the problem the tour answers, the name and the tag line, what the tour covers, that the
  examples are fragments of compiled programs, a pointer for a newcomer to *Still Ordinary Rust*, and
  a link to the Quickstart for a reader who wants to run one.
- **Key features:** the five headline features under identity.md's titles, word for word and in its
  order, each opening with the problem, stated fairly (where plain Rust already handles a case, say so
  first), then one compiled example of about fifteen lines, the limit the strategy pairs with the
  strength, and a link to the page
  [seo.md](../seo.md#the-tag-line-orients-the-reader-the-features-carry-the-searchable-words) names as
  the feature's owner. The opening says once that examples leave out the imports, unneeded
  definitions, and each context's check, and Type-Safe Wiring names `delegate_and_check_components!`
  as the one-step form.
- **Beyond choosing implementations:** abstract types, extensible records and variants, composable
  handlers, namespaces, and higher-order providers, one or two sentences each with its Concepts page
  and no code, since a first-time reader shown them in code meets more constructs than the tour can
  explain. The abstract-types item carries the payoff: the error type stops being a parameter every
  layer carries.
- **The problems it solves:** a two-column table from each problem in
  [message.md](../../communication-strategy/message.md#the-problems-cgp-removes), in the reader's
  words, to the Concepts page that answers it; the framework author's path in
  [information-architecture.md](../information-architecture.md#how-each-reader-moves-through-the-site)
  starts here.
- **When a plain trait is enough:** the costs in two short paragraphs, pointing to Type-Safe Wiring
  for the raw errors rather than repeating the `cargo-cgp` qualification, the agent skill beside the
  learning time, a link to the front page's cost section for the maturity, and *Modularity Hierarchy*.
- **Where to go next:** the Quickstart and Hello World, the Concepts pages, the comparisons, and the
  reference.

**The headline features run one scenario**, the profile-picture scenario under the names the `cgp`
README uses, among the
[canonical examples](../../communication-strategy/voice-and-register.md#show-it-canonical-examples-diagrams-and-diffs),
compiled in the website's `example-code` crate at `tests/overview.rs`. Off the page: a construct
reference, a second explanation of what a Concepts page explains, and the project's maturity.

## The Quickstart

**The smallest page on the site, with a measurable target: ten minutes** for a reader who has Rust
installed and uses only this page, measured with a
[friction log](../../communication-strategy/readers.md#keeping-the-model-observed) on a clean machine.
[evidence.md](../../communication-strategy/evidence.md#what-we-watch-and-what-counts-as-a-result)
records it as the site's activation signal, and this guide owns it. A draft over ten minutes loses a
step rather than explaining it faster.

The page has four parts:

- **Install:** the minimum Rust version, then the commands that create a project and add the crate,
  and the version they write, with nothing else about toolchains. The minimum matters because Cargo's
  version-aware resolver gives an older toolchain an old `cgp`, which fails on the program rather than
  on the toolchain.
- **One program**, complete and copyable into `main.rs`: one context, one operation, one printed line.
  It is a `#[cgp_fn]` function with an `#[implicit]` argument reading a field of a
  `#[derive(HasField)]` struct, the gentlest entry
  [readers.md](../../communication-strategy/readers.md#the-comprehension-barriers) prescribes: no
  wiring, generics, or trait to understand.
- **What to expect:** the exact output.
- **One link onward**, to the Hello World tutorial.

**It stops before the second context, the whole boundary against
[Hello World](../tutorials/hello-world.md)**, whose payoff is the same function working unchanged on a
second context. The two show similar code on purpose, so a reader arriving at Hello World sees at once
what is new; the Quickstart never grows a second example, an explanation of `#[implicit]`, or a note
on what the macro generates.

**The install pins the version the page's code is written against**, so re-pinning is on the
[release checklist](release-announcement.md#publishing-and-what-happens-afterwards) beside the
tutorials. A page that publishes ahead of its release gives the git dependency in a one-line note
instead, because a pin crates.io does not carry fails on the reader's first build.

## Resources

**The ecosystem index, for a reader who wants something that is not on this site.** It is a list, and
each entry says in one line what the thing is and who it is for. The entries are the crates, the
toolchain, the talks, and the projects built with CGP, leaving out the CGP Patterns book and the
Hermes SDK, which are [legacy resources](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#legacy-resources). A link
to another page of this site belongs in the Introduction's routing list instead. Every entry is
checked when the page is touched: the crate exists under the name given, the link resolves, and
anything version-specific holds, since this page ages by accumulation.

## The Contribute page

**The enthusiast's page, the top rung of the
[conversion ladder](../../communication-strategy/formats.md#the-conversion-ladder)**: a set of routes,
one per way of helping, each saying what it asks and where it leads. Its reading is the shared set and
[its row of the reading map](README.md#the-contribute-page).

**The opening** says what the page is for, names Context-Generic Programming beside a plain
description, and links the Introduction, without the tag line. It says that help of every size counts,
as a fact about the routes rather than as encouragement.

**Then one section per route, from the smallest commitment to the largest**, so a reader stops at the
first that fits. The routes may be grouped or renamed, and one with nowhere to lead is removed:

- **Discussion:** the Discord server, GitHub Discussions, and the subreddit.
- **Reporting a problem:** a confusing page, or an error in the knowledge base, a contribution in its
  own right because the checks can miss an error, per
  [contributions from outside the project](../../communication-strategy/ai-disclosure.md#contributions-from-outside-the-project).
  Link the knowledge base's issue tracker and the section on reporting problems in *Contributing to
  CGP with an Agent*, which [knowledge-base.md](knowledge-base.md#the-section-shape) specifies.
- **Writing and sharing:** an independent post, tutorial, or talk, and the project's social accounts.
- **Publishing reusable components:** the aim of an ecosystem of published components and providers,
  so most users write only the wiring that selects them; state it as an aim, never as an ecosystem
  that exists, and without "modular" as the lead, per
  [identity.md](../../communication-strategy/identity.md#using-modular-as-a-supporting-word).
- **Changing CGP itself:** one paragraph routing to *Contributing to CGP with an Agent*, which
  publishes the contribution policy. Do not restate or extend the policy, and keep the agent framing
  to one line beside the task, per [knowledge-base.md](knowledge-base.md#what-must-not-be-on-one).
- **Sponsoring the author:** last, because it changes voice.

**The sponsorship section and the acknowledgement belong to the author.** The sponsorship section is
his first-person account, per
[author-personality.md](../../communication-strategy/author-personality.md#stated-preferences), under
its own heading, with nothing before it speaking as "I"; a revision fixes a broken link and changes
anything else only at his request. The acknowledgement records where CGP came from, which
[the website repository's rules](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#legacy-resources)
leave to the author: keep its text under a `##` heading, so the page has one `h1`, and raise its
Hermes SDK link, the only one outside the dated posts to that
[legacy resource](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#legacy-resources), with the author rather than
editing it.

**Elsewhere the page is in project voice**: the reader is "you" and the project is "CGP", never "we"
or "our" for a project with one author, per
[voice-and-register.md](../../communication-strategy/voice-and-register.md#the-layered-voice), and
never "passionate", "invaluable", or a claim about the community's size. It keeps its
`sidebar_position`.

## What must never be on an orientation page

- **No argument for CGP**; the front page makes it.
- **No teaching sequence**: no steps that build an idea, no "notice that", no construct introduced for
  later. The Quickstart's steps get a program running and stop.
- **No concept explanation**; naming *coherence* and linking is fine.
- **No syntax the reader is not about to type**, beyond the Quickstart's program and the Overview's
  examples.
- **No unverified route.**
- **No maturity discussion.** The front page's cost section carries it, and an evaluator is sent
  there, so its candour is not diluted across three places.

## Checking a draft

- **Ask where the page sends each reader it serves**, and check there is exactly one obvious answer.
- **Read the first paragraph alone**: someone who has never heard of CGP knows what it is and what this
  page is for.
- **Count what the page teaches**: nothing beyond the Introduction's four words.
- **Follow every link**, external ones included, and check the front matter's `description`.
- **For the Quickstart, run it on a clean machine and time it**: paste the program as given, run the
  command given, and compare the output; over ten minutes, a step comes out.
- **For the Overview**, read it through with natural-writing's checks, then check each feature title
  against identity.md, each feature section for its problem, example, limit, and link, the breadth list
  for code, the table against every problem in message.md, every snippet against `tests/overview.rs`,
  and the naming check; view it at phone width in both themes, where long signatures scroll inside
  their block.
- **For the Contribute page, compare the sponsorship section and the acknowledgement with the author's
  text**, and search the rest for "we", "our", and "us".
