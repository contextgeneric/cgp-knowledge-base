# Writing an orientation page

An orientation page's job is to **send the reader somewhere**, or to **prove that the thing runs**.
It does not teach, and it does not persuade. Its reader has already decided CGP is worth a few
minutes and wants either the shortest route to what they came for or the shortest proof that it
works.

- **Where they live**: `docs/index.md`, `docs/quickstart.md`, `docs/resources.md`, and
  `docs/contribute.md`
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md), except the
  Contribute page's sponsorship section, which is the author's
- **Governed by**: [information-architecture.md](../information-architecture.md) for what each
  surface is for and where a reader goes next;
  [formats.md](../../communication-strategy/formats.md#the-conversion-ladder) for matching the next
  step to the reader
- **Reading**: the shared set and
  [the orientation pages' row](README.md#orientation-pages-the-introduction-the-quickstart-and-resources)
  of the reading map

## What separates orientation from every other page type

Four page types sit next to this one, and an orientation page is defined by what it refuses to do.

**The homepage persuades; an orientation page does not.** A reader on the front page may not yet
care, so that page carries the argument and the selling points. A reader who has clicked *Docs* has
already given CGP the benefit of the doubt, and repeating the pitch to them spends their patience on
something they have already accepted. The [homepage guide](homepage.md) owns persuasion.

**A tutorial teaches; an orientation page does not.** A [tutorial](tutorial.md) is judged on whether
the reader understood an idea, and it earns its length by deriving each construct from a problem. An
orientation page is judged on whether the reader got somewhere.

**An explanation page argues; an orientation page does not.** The [Concepts](explanation.md) tier
answers *why*. An orientation page may name an idea in a clause, and links rather than explaining.

**A reference page specifies; an orientation page does not.** It names no syntax and no construct
that the reader is not about to type.

The rule that falls out of all four: **if a sentence on an orientation page is not routing the
reader, orienting them in one line, or getting a program to run, it belongs on another page.**

## What every orientation page owes its reader

These pages are read cold and left within a screen, so each owes its reader an orientation in one
line and an obvious way onward.

**Orient a cold reader in the first paragraph.** Any of these pages may be someone's first contact
with CGP, per
[information-architecture.md](../information-architecture.md#most-readers-do-not-arrive-at-the-homepage),
so each opens by saying what CGP is in a sentence, naming Context-Generic Programming in full, with
a link onward. This is one sentence, not a summary of the front page. The Introduction presents the
project, so it states the settled tag line whole; the Quickstart and Resources relate a short form
of it to what they do, as in "CGP enables pluggable trait implementations in Rust, and this page
gets one running", or leave it out. The
[naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page) owns
the detail.

**End every path somewhere.** An orientation page that leaves the reader with no obvious next click
has failed at its only job. Where several routes are possible, name them by the question each
answers rather than by the section's title: *how its ideas work* rather than *Concepts*.

**Carry a `description` in the front matter.** These are among the most-linked pages on the site,
Docusaurus derives a useless one from the first line otherwise, and the measured failure the site
has is that pages are shown and not chosen; the reasoning is in [seo.md](../seo.md). One sentence
saying what the page is for.

**Say only what has been checked.** An orientation page is mostly claims about other things: that a
command works, that a link leads somewhere, that a crate exists. Every one of them is verified when
the page is touched, because a reader who follows a dead route from the routing page stops trusting
the routes.

## The Introduction

**The docs root, and the page that decides where most readers go.** Its reader clicked *Docs* from
the navigation bar and wants to know what CGP is and which part of the documentation answers their
question.

It carries a definition, a first step, and a routing list. **A definition**, two or three paragraphs: the settled
descriptor, one concrete example of the same interface with two implementations, and the vocabulary
a reader needs to read any other page (*context*, *provider*, *wiring*, *component*), each glossed
in a clause rather than explained. **A first step**, naming the tutorials, because a reader who wants
to write code should not have to find them. And **a routing list**, one line per destination, keyed
on the question the reader has rather than on what the section is called.

Its boundaries are settled, and a revision should not reopen them. It **keeps the vocabulary
introduction**, which is the one teaching-shaped thing an orientation page does, because every other
page assumes those four words. It **does not carry the maturity discussion**, which is *Project
status*'s job: an evaluator needs to reach that from above the fold on the front page, not by
scrolling the docs root. And it **does not route newcomers to the blog**; the blog is named as a
record of releases and talks, with the caveat that older posts describe the library as it was.

## The Quickstart

**The smallest page on the site, and the one with a measurable target.** It exists because the front
page's first call to action and every launch post ask the reader to try CGP, and the only honest
destination for that ask is a page that gets them to a running program without teaching them
anything.

**The target is ten minutes**, for a reader who has Rust installed and uses only this page, measured
with a [friction log](../../communication-strategy/readers.md#keeping-the-model-observed) on a clean
machine. That target comes from
[evidence.md](../../communication-strategy/evidence.md#what-we-watch-and-what-counts-as-a-result),
which records it as the site's activation signal, and this guide owns it. A draft that cannot be
walked in ten minutes is too long, and the fix is to remove a step rather than to explain it faster.

The page installs the crate, shows one program, states the output to expect, and routes onward.
**Install**: the `cargo` command and the version, with nothing about
toolchains, since CGP compiles on stable. **One program**, complete and copyable, that a reader can
paste into `main.rs` and run. **What to expect**: the exact output, so the reader knows whether it
worked. And **one link onward**, to the Hello World tutorial.

### What the program is, and where it stops

**One context, one operation, one printed line.** The gentlest entry CGP has is a `#[cgp_fn]`
function with an `#[implicit]` argument reading a field from a `#[derive(HasField)]` struct, which
is what [readers.md](../../communication-strategy/readers.md#the-comprehension-barriers) prescribes
for a reader who has never seen CGP: they write a function and a struct, and get a working program
with no wiring, no generics, and no trait to understand.

**It stops before the second context, and that boundary is the whole distinction from Hello World.**
The [Hello World tutorial](../tutorials/hello-world.md) uses the same constructs and is a genuinely
different page, because its payoff is the moment the same function works unchanged on a second
context, which is the idea it exists to teach. The Quickstart has no payoff and teaches no idea. It
proves the thing compiles and runs, and hands the reader to Hello World for the reason it matters.

So the two pages **deliberately show similar code**, which is not duplication
to be resolved: a reader arriving at Hello World from the Quickstart should recognize where they are
and immediately see what is new. And the Quickstart **must not grow a second example**, an
explanation of what `#[implicit]` does, or a note about what the macro generates, since each is a step
toward becoming a worse copy of the tutorial.

### The version pin, and why it is fragile

The install command names a version, so the page is wrong the moment the library moves. The pin is
the version the page's code is written against, which ties the Quickstart to the release the same
way the tutorials are tied to it, and re-pinning is on the
[release checklist](release-announcement.md#publishing-and-what-happens-afterwards). A page that
publishes ahead of its release needs a one-line note giving the git dependency instead, because a
pin crates.io does not yet carry is a reader's first experience of CGP failing to build.

## Resources

**The ecosystem index, for a reader who wants something that is not on this site.** Its reader
arrives already interested and wants to be routed, not persuaded, so it is a list, and the prose
around each entry says what the thing is and who it is for, in one line.

It earns its place by covering what the site does not. **The entries are the crates, the toolchain,
the talks, and the projects built with CGP**, leaving out the CGP Patterns book and the Hermes SDK, which
are [legacy resources](../AGENTS.md#leave-legacy-resources-off-public-pages). A link to another page of
this site belongs in the Introduction's routing list instead, where a reader looks for it.

Every entry is checked when the page is touched: that the crate exists under the name given, that
the link resolves, and that anything version-specific still holds. This page ages by accumulation,
and a dead link here costs more than on any other page because its only content is links.

## The Contribute page

**The enthusiast's page, and the top rung of the
[conversion ladder](../../communication-strategy/formats.md#the-conversion-ladder).** Its reader
already likes CGP and wants to know how to help, at whatever size of commitment they can offer, so
the page is a set of routes, one per way of helping, each saying what it asks and where it leads. It
routes rather than persuades: the reader has already been persuaded, and the page's job is to make
each way in obvious. Its reading is the shared set and
[its row of the reading map](README.md#the-contribute-page).

### The opening, and the routes in order

**The opening paragraph says what the page is for**, names Context-Generic Programming in full
beside a plain description, and links the Introduction, per the
[naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page). The
tag line has no job here and is left out. It says that help of every size counts, as a fact about
the routes below rather than as encouragement.

**Then one section per route, ordered from the smallest commitment to the largest**, so a reader
stops at the first that fits:

- **Discussion:** the Discord server, GitHub Discussions, and the subreddit, for questions and
  ideas.
- **Reporting a problem:** a confusing page, or an error in the knowledge base, which is a
  contribution in its own right because the base is still being reviewed, per
  [contributions from outside the project](../../communication-strategy/ai-disclosure.md#contributions-from-outside-the-project).
  Link the knowledge base's issue tracker and the section on reporting problems in *Contributing to
  CGP with an Agent*, which [knowledge-base.md](knowledge-base.md#the-section-shape) specifies.
- **Writing and sharing:** a post, a tutorial, or a talk written independently, and the project's
  social accounts.
- **Publishing reusable components:** the project's aim of an ecosystem of published components
  and providers, so that most users write only the wiring that selects them. State it as an aim, never as a
  description of an ecosystem that exists, and in the strategy's words rather than with "modular" as
  the lead, per [identity.md](../../communication-strategy/identity.md#using-modular-as-a-supporting-word).
- **Changing CGP itself:** one paragraph routing to *Contributing to CGP with an Agent*, the site's
  only guide to contributing code or documentation, which publishes the contribution policy. Do not
  restate the policy or add to it, and keep the agent framing to the one line beside the task, per
  [knowledge-base.md](knowledge-base.md#what-must-not-be-on-one).
- **Sponsoring the author:** last, because it changes voice, as the next section describes.

The routes may be grouped or renamed as the page reads best, and a route that has nowhere to lead,
such as a channel the project has closed, is removed rather than kept.

### The sponsorship section and the acknowledgement belong to the author

**The sponsorship section is the author's own first-person account**, candid about what support
means to him, and it stays in his voice, per
[author-personality.md](../../communication-strategy/author-personality.md#stated-preferences). The
switch of voice is visible: it has its own heading, and nothing before it speaks as "I". A revision
does not rewrite it into project prose or improve its wording; it fixes a broken link, and changes
anything else only at the author's request.

**The acknowledgement is the author's too.** It records where CGP came from and who supported it,
which [the website repository's rules](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#legacy-resources)
leave to the author. Keep its text, but put it under a `##` heading so the page has one `h1`. Its
link to the Hermes SDK is the only one outside the dated blog posts to that
[legacy resource](../AGENTS.md#leave-legacy-resources-off-public-pages), so raise it with the
author rather than editing it.

### The rest of the page

**Project voice everywhere else**: the reader is "you" and the project is "CGP". Never use "we" or
"our" for a project with one author, per
[voice-and-register.md](../../communication-strategy/voice-and-register.md#the-layered-voice), and
never "passionate", "invaluable", or a claim about the size of the community. Its front matter
carries a written `description` and keeps its `sidebar_position`, and every link is followed when
the page is touched, because a dead channel is a route that fails.

## What must never be on an orientation page

**No argument for CGP.** A reader on these pages is past the pitch, and the front page makes it
better.

**No teaching sequence.** No numbered steps that build an idea, no "notice that", no construct
introduced because the reader will need it later. The Quickstart's steps get a program running and
stop.

**No concept explanation.** Naming *coherence* or *impl-side dependency* and linking is fine.
Explaining either is the Concepts tier's job.

**No syntax the reader is not about to type.** These pages name no construct except the ones in the
Quickstart's program.

**No unverified route.** Every link followed and every command run before the page ships.

**No maturity discussion outside *Project status*.** The candour is an asset and is not diluted by
appearing in three places; it belongs on the page an evaluator is sent to.

## Checking a draft

**Ask where the page sends the reader, and check there is exactly one obvious answer for each
reader it serves.** If the page ends without a next step, it has failed at the only thing it does.

**Read the first paragraph alone** and ask whether someone who has never heard of CGP knows what it
is and what this page is for.

**For the Quickstart, run it on a clean machine and time it.** Not read it: run it. Paste the
program as the page gives it, run the command the page gives, and check the output matches what the
page promised. Over ten minutes means a step comes out.

**Count what the page teaches.** An orientation page should teach nothing except the Introduction's
four words of vocabulary. Anything else has drifted.

**Follow every link**, including the external ones, and check the front matter carries a
`description`.

**For the Contribute page, compare the sponsorship section and the acknowledgement with the
author's text**, which a revision leaves as he wrote it, and search the rest for "we", "our", and
"us".

## Where the current pages stand

**The Introduction** is current and close to this guide. Its one divergence is that it still carries
the *Current Status* section, which [E1](../tasks.md) moves to *Project status*; when that lands,
the Introduction keeps a one-line pointer to it. Its routing list already keys on questions rather
than section names, and it does not send newcomers to the blog.

**Resources** is current. It carries `cargo-cgp` with its install path and the full crate list, and
lists neither the CGP Patterns book nor the Hermes SDK, which are
[legacy resources](../AGENTS.md#leave-legacy-resources-off-public-pages).

**The Quickstart is written**, at `/docs/quickstart`. It is the destination the front page's first
call to action is specified to take, though the current front page still sends that button to the
Introduction and its second to Hello World, and repointing it is part of the front-page rebuild rather
than something done ahead of it. The page holds the contract above: install, one program, the exact output, a route onward,
no second example, and nothing explained. Two things are worth knowing before revising it. Its
`cgp = "0.8.0"` pin names a version crates.io does not yet carry, which is correct only because the
branch merges with the release, so the pin is right and the page must not publish before it. And **the
ten-minute target has not been measured**: the program is compiled in `example-code`, but no one has
walked the page on a clean machine with a friction log, which is what this guide asks for and the one
check the page has not had.

**The Contribute page predates this guide** and is to be rewritten against it, which the author has
allowed in full. Its routes are the right ones, and its code-and-documentation section already
routes to the contributing how-to and its reporting section. It diverges in five ways: the opening
and the documentation section speak as a corporate "we" and "us"; the opening never names
Context-Generic Programming; the components section leads with "modularity"; the front matter has
no `description`; and the acknowledgement sits under a second `#` heading. The sponsorship section
and the acknowledgement's text stay as they are.
