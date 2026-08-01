# Disclosing how AI is used in CGP

This document fixes what the project says about **how it is made** — where AI writes, where it revises,
where it only checks, and where it does not touch the work at all — and how a page carrying AI-assisted
content says so. Every other document in this section governs claims about CGP; this one governs claims
about CGP's own provenance, which is a different obligation and a more dangerous one to get wrong.

## Why this needs a policy rather than a footnote

**Disclosure is not optional here, because the use is substantial and already discoverable.** CGP's
documentation is written by agents from a knowledge base published at
<https://github.com/contextgeneric/cgp-knowledge-base>; its commits carry the model's name in a
`Co-Authored-By` trailer; one whole repository preserves an AI co-authorship record on purpose. A reader
who works any of that out for themselves, having read a page that presented itself as ordinary technical
writing, discounts everything else the project says — which is the same failure mode
[honesty-is-the-strategy](AGENTS.md#honesty-is-the-strategy) exists to prevent, applied to process rather
than to claims.

The disposition is already the author's, which makes this a policy rather than a new behaviour. The
[new-website post](../website/blog/new-website.md) volunteered that the front page's design, text, and
images were largely LLM-produced, that the colour theme was chosen the same way, and that the text
throughout the site had been LLM-refined — and it stated the trade-off plainly, that a professional
designer would have done better. Nobody asked for that. What this document adds is precision: that post
disclosed *the site*, uniformly, at a moment when the answer was uniform, and the answer is no longer
uniform.

The opposite failure is as real and is the one an agent is likelier to produce. **Over-disclosing is a
form of inaccuracy too** — a page that implies more human review than happened is a false claim, and a
project that decorates itself with AI language is read by this audience as chasing a trend. The register
is the same one the rest of the section prescribes: state the fact, state its limit, and move on.

## The principle that organizes the levels

**AI's role in CGP is not uniform, and the variation is a considered engineering position rather than an
accident of what was convenient.** Stating the principle is what makes the disclosure informative; a page
that merely lists four levels without saying why they differ reads as a compliance exercise.

Two questions decide how much of an artifact an agent may write, and they are independent.

**Does it become part of a user's program?** Code that a user imports and compiles into their own project
is code they inherit responsibility for and cannot easily audit at the moment they need to. Code that
merely *runs on* their project — a tool, a test suite — is inspected on its results and can be replaced
without touching anything they wrote.

**Can it be checked cheaply against something already true?** Prose about a macro can be checked against
the macro. A test can be checked by running it. A tool's output can be checked against a fixture. A
*design* can be checked against nothing, because it is the thing everything else is checked against.

The two answers point the same way, and the resulting gradient is the page's actual content: **the closer
an artifact sits to a user's own compiled code, the more of it is the author's; the more cheaply it can be
verified against a ground truth, the more of it an agent may write.** The core library is at one end
because it is both — imported by users and answerable to nothing but its own design. The documentation is
at the other because it is neither.

## The four levels

### Documentation and articles, written by agents from a public knowledge base

The reference, the concepts, the guides, the error catalog, and the website pages derived from them are
written by agents. What makes that defensible is not the agents but the arrangement around them, and the
arrangement is worth describing rather than asserting, because it is the part a skeptical reader can go
and check.

**Everything is written into a knowledge base first, and the knowledge base answers to the source code.**
The rule the base is built on is that the source in each project is the single source of truth, above any
document and above the agent skill built from it — so a claim about what a macro expands to, what
identifier it generates, or what syntax it accepts is not written from an agent's recollection but read
out of the code, the tests, or the expansion snapshots that pin them. Where several views of one truth
disagree — the implementation, the tests, the reference document, the internals document, the skill — the
disagreement is treated as a defect and the code wins. When behaviour changes, the documents change in the
same change rather than in a follow-up, on the principle that a document describing behaviour the code no
longer has is worse than no document, because the next reader trusts it.

**The base is public, so the claim is checkable.** The rules an agent works under, the summary of every
document, and the full history of how each was written are all visible at the URL above — including the
commit trailers naming the model that wrote each change. A reader who wants to know how a sentence about
`#[cgp_component]` came to exist can read the rule that produced it and the commit that landed it. That is
a stronger form of disclosure than a page can make on its own, and pointing at it is more persuasive than
any assurance.

**The author's role is stewardship, and stewardship is specific.** He sets the rules the base is written
under, decides what is written and in what order, reads the pages that carry the argument, and is
accountable for everything published under the project's name. What he does not do is read every line of
every ported reference page, and the disclosure must say so rather than implying otherwise — see
[the claims easiest to get wrong](#the-two-claims-that-are-easiest-to-get-wrong) below.

### Revision of human-written drafts

Blog posts and tutorials work the other way round. **The author writes the draft; an agent revises it
against the knowledge base.** The argument, the judgement about what is worth saying, the concessions, and
the voice all originate with him, and the agent's job is to improve the prose and to check the code and
claims against what the base records.

The ordering is the whole point and is worth stating in the disclosure, because "AI-assisted" covers both
this and the level above and a reader cannot otherwise tell which they are reading. A post written this
way is the author's argument, improved; a reference page is an agent's writing, governed. Those deserve
different sentences, and giving them the same one wastes the distinction.

### Code that users never import

`cargo-cgp` is mostly agent-written, and the CGP test suite is largely agent-maintained. Both are governed
by one rule, and naming the rule is what stops this reading as an inconsistency with the level below.

**Neither becomes part of a user's program.** A cargo subcommand runs *on* a project; it is never a
dependency of it, so a user is exposed to its behaviour rather than to its source, and its behaviour is
pinned by a snapshot suite that either matches or does not. A test suite is the same case in a sharper
form: a test is self-verifying against the real library, and a wrong test fails loudly rather than
misleading quietly.

The test suite also has a positive reason rather than merely a permissive one, and it should be stated:
**an agent achieves coverage the author could not reach by hand.** Exhaustively exercising a proc-macro's
accepted syntax forms is exactly the sort of large, mechanical, high-value work that a person writing in
their own time will never finish, and the library is better tested for it.

### The core library

**The design of every CGP construct and interface is the author's, and the core library is written almost
entirely by hand.** This is the code users import, and it is the level where the ground truth runs out:
there is nothing to check a design against, because the design is what everything else is checked against.

AI is used here, and the disclosure should say how rather than claiming it is absent: to verify
correctness, to review quality, and to work through the proc-macro implementations. That is assistance
against a standard the author sets, not authorship. The distinction between *designing a construct* and
*implementing it under review* is the one this level turns on, and it is the sentence a Rust developer
evaluating whether to depend on CGP most wants to read.

**Word this level carefully, because it is the one a reader can check and disprove.** The `cgp`
repository's commits carry `Co-Authored-By` trailers naming the model, and some of them sit on the proc
macros — so a page claiming the library is written by hand, full stop, is contradicted by a `git log` any
skeptic can run in a minute, and the contradiction would discredit the other three levels along with it.
The accurate claim separates the two things the trailers cannot: **what CGP is** — every construct, every
interface, every design decision about how the pieces fit — is the author's, while **how a macro is
implemented** is work he directs, reviews, and frequently shares. Say both halves. The version that
survives scrutiny is stronger than the version that sounds cleaner.

The trailers are worth naming as an asset rather than treating as an exposure, because they are the
project's most granular disclosure and they already exist: they record, commit by commit, which work was
shared and which was not. The website's own drafting history shows the same pattern from the other side —
the blog drafts the author writes by hand carry no trailer at all.

## How to word a disclosure

The wording rules are short, and they are the same as the section's rules everywhere else applied to an
unfamiliar subject.

**Say it plainly, as a fact about process.** "The pages in this reference are written by AI agents from a
public knowledge base, and verified against the library's source." Not "crafted with the help of
cutting-edge AI", and not "regrettably, parts of this were AI-assisted".

**Never claim more review than happened.** This is the rule that matters most, because it is the one that
converts an honest page into a false one, and it is the easiest to breach while trying to reassure.

**Never use it as an excuse.** An error in an AI-written page is the project's error. A disclosure that
functions as a pre-emptive apology invites the reader to discount the whole page, and it is not the
author's register — he states costs, he does not shelter behind them.

**Describe the practice, not the vendor.** Naming models dates within months and invites an argument that
has nothing to do with CGP. The [new-website post](../website/blog/new-website.md) named the models it
used and was right to, because it was recounting a specific episode; a standing page describes what is
done rather than what it is done with.

**Do not make it a feature.** AI use is not a capability CGP offers, and it does not belong in the tag
line, the feature set, or a hook. This is a separate rule from the one about
[agent support answering the cost objection](message.md#the-one-mitigation-that-spans-three-of-these),
and the two are easy to conflate: *CGP works well with coding agents* is a claim about the technology and
is made where costs are discussed; *CGP is partly written by coding agents* is a claim about the project
and is made here. A page that mixes them makes the first look like an excuse for the second.

## The two claims that are easiest to get wrong

Both are cases of the same mistake — smoothing a true-but-qualified statement into a cleaner one that is
false — and both are checkable by a reader in minutes, which is what makes them expensive. The first is
about the core library and is handled in [its section above](#the-core-library): the commit trailers make
"written by hand" disprovable, so the claim has to separate the design from the implementation. The
second is about review.

**Human review of AI-written pages is real but not uniform, and a disclosure that flattens it into "all
content is reviewed by the author" is the other false sentence this page could contain.** What is actually
true is set out in the website's
[authorship rule](../website/AGENTS.md#who-drafts-a-page-and-who-reads-it-before-it-publishes), which is
the authoritative list and the one to copy from when the page is written: the author reads the surfaces
that carry the argument in full — the front page, the explanation tier, the reference index, this page,
and every blog post — while the roughly seventy ported construct pages ship on their writing guide plus a
spot check. Take the list from there rather than from memory, since a page that names the wrong set is
making a false claim about the project in public.

That is a defensible arrangement and it should be described as one rather than smoothed over, because the
reason is good: the construct pages are a mechanical port of documents already written and verified
against the source, into a fixed template, so the risk they carry is a wrong expansion rather than a wrong
argument — and a wrong expansion is caught by the source, not by a reading. Say that. A reader who is told
"reviewed where judgement matters, verified against the source everywhere" believes it; a reader told
"everything is reviewed" and who then finds a mistake concludes the review was fictional.

The same rule applies whenever the arrangement changes. This document and the page built from it are bound
by the [synchronization rule](../AGENTS.md#the-synchronization-rule) exactly as a reference document's
expansion is: if the review policy loosens, the page says so before anyone notices.

## The page on the website

The site carries **one dedicated page** describing all four levels, and every other AI-assisted page links
to the section of it that applies. The page is the specification's destination, so its shape is fixed here
rather than in a [writing guide](../website/writing-guides/README.md) — it is a single project-meta page
rather than a kind of page the site will publish repeatedly, which is the same treatment
*Project status* gets.

**Its job is to let a reader decide how much to trust each part of the project, in one read.** That means
the four levels in the order above — most AI, least AI — because a reader who arrives worried is worried
about the library, and the page's most reassuring content is at the end. Opening with the core library
would read as leading with the answer they want to hear.

**Each level says four things and stops**: what it covers, who does what, why that division was chosen,
and what the honest limit is. The principle section comes first, because four levels without it read as
four excuses. The knowledge-base process is the longest part, because it is the only level whose
trustworthiness rests on a process rather than on a person, and it is the one a reader can verify.

**It is written in the project voice, with one permitted exception.** Accountability is personal — "every
error is mine" is a sentence a project cannot say and a person can — so if a line of the author's own
voice appears anywhere on this page it is that one, and the [Contribute page's sponsorship
section](../website/site-structure.md) is the precedent for switching visibly rather than laundering it.

**What must not be on it:** no defensiveness, no argument about whether AI writing is legitimate in
general, no comparison with other projects' practices, and no claim that the process makes the output
better than a human's would have been. The page describes what is done and why; it does not litigate it.

## Linking to it from a page

A page that carries AI-assisted content links to the matching section of the disclosure page, and the
rules below keep that consistent rather than decorative.

**One line, at the foot of the page.** A provenance note is a fact a reader may want, not a warning about
what follows, and putting it at the top primes them to discount everything beneath it — which is neither
accurate nor the register the rest of the site is written in. The foot is where a reader looks for
provenance, and it does not compete with the content.

**Consistent wording, linking the specific section**, so the line says which of the four levels applies
rather than gesturing at the page. A reference page's note and a blog post's note are different sentences,
because they describe different arrangements.

**New pages only.** A page written or substantially rewritten from now on carries the note; existing pages
are **not** swept, and an agent must not add the note retroactively without being asked. The decisive
reason is that a sweep would attach notes to pages whose actual provenance nobody has checked, which is a
guess presented as a disclosure and therefore worse than the silence it replaces. A second, weaker reason
is that the older pages are not undisclosed: the [new-website post](../website/blog/new-website.md) says
the site's text was LLM-refined throughout. Be precise about how far that reaches — it discloses
*refinement* of what existed when it was published, not *authorship*, and not anything added since — so
treat it as partial cover for the older pages rather than as a reason the gap is closed. Closing it
properly means going page by page and establishing what is actually true of each, which is work the user
asks for rather than work an agent starts.

**Record the level in the page's internal document.** Which of the four applies is a fact about how the
page was made, it will not be recoverable later, and the page document is where the site's provenance is
already recorded.

**The website only, for now.** Other repositories — `cargo-cgp` above all, whose whole source is at level
three — get their disclosure after the website redesign is published, as a separate piece of work. Do not
add disclosure notes to other projects' READMEs or documentation in the meantime.

## Keeping this current

This document goes stale in a way most of the section does not: it describes a working arrangement rather
than an audience, so it is wrong the moment the arrangement changes and nobody notices. Revisit it when
the review policy changes, when a new part of the project starts or stops being agent-written, and when a
level's honest limit stops being honest. A disclosure that has drifted is worse than none, because it is
the one page whose entire value is that it is accurate.
