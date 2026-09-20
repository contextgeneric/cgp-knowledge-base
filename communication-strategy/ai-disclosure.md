# Disclosing how AI is used in CGP

Describe AI's role in each part of CGP accurately, including who writes, who reviews, and what the
review covers.

## Why this needs a policy rather than a footnote

CGP must disclose its substantial use of AI. Agent-written documentation, the
[public knowledge base](https://github.com/contextgeneric/cgp-knowledge-base), and
`Co-Authored-By` commit trailers make that use visible. A disclosure should give readers an
accurate account without making them reconstruct it from repository history. The
[honesty rule](AGENTS.md#honesty-is-the-strategy) applies to process as well as technical claims.

The author's own writing provides the model for disclosure. The
[new-website post](../website/blog/new-website.md) describes LLM assistance with the site's design,
images, colour theme, and prose, and acknowledges that a professional designer could do better.
Use the same plain register while distinguishing the different arrangements across the project.

Avoid exaggerating either AI's contribution or human oversight. State what happened and its limits,
without apology or promotional language. A reassuring claim about review is still false if that
review did not happen.

## The principle that organizes the levels

The project allows more agent authorship where work can be checked against an established source
and less where it defines the library users compile into their programs. Explain this principle
before describing the levels, so readers understand the division of work.

Assess each artifact through these questions:

- **Does it become part of a user's program?** Library code becomes a dependency users must trust.
  A tool runs on their project and can be replaced without changing the program's implementation.
- **Can it be checked against an established source?** Documentation can be compared with code,
  tests can exercise the library, and tool output can be compared with fixtures. Designing an
  interface requires the author's judgment about what it should do; checking an implementation
  against that design answers a different question.

These criteria explain the range from agent-written documentation to a largely hand-written core
library. They guide authorship decisions without guaranteeing that any resulting artifact is correct.

## The four levels

### Documentation and articles, written by agents from a public knowledge base

Agents write the reference, concepts, guides, error catalog, and website pages derived from them.
Describe the process that governs this work so readers can assess it.

The knowledge base is written first and must agree with the source code. Agents check claims about
syntax, generated identifiers, and macro expansions against the implementation, tests, and expansion
snapshots. The source takes priority over the documentation and the skill. Changes to behavior must
include matching documentation changes, under the
[synchronization rule](../AGENTS.md#the-synchronization-rule).

The public repository exposes the process for inspection. Readers can consult the authoring rules,
document catalog, and commit history, including trailers that identify AI co-authorship. This record
helps explain how a page was produced; it does not prove every statement is correct.

The author directs the work and remains accountable for publication. He sets the rules, chooses
what gets written, and reads the pages that carry the argument. He does not read every line of every
ported reference page. Disclosures must preserve that limit; see
[the review requirements](#the-two-claims-that-are-easiest-to-get-wrong).

### Revision of human-written drafts

The author writes blog and tutorial drafts, and agents revise them against the knowledge base.
He supplies the argument, priorities, concessions, and voice. Agents improve the prose and check
code and claims.

State this order explicitly. "AI-assisted" alone does not distinguish an author's draft revised by
an agent from an agent-written reference page. The provenance note must describe the arrangement
that actually applies to the page.

### Code that users never import

`cargo-cgp` is mostly agent-written, and the CGP test suite is largely agent-maintained. These
artifacts run on a project or test the library without becoming part of the user's compiled program.
Their results can be checked against fixtures and the library's behavior.

Tests and snapshots make this work easier to verify, but still require judgment about expected
results and coverage. A passing test can miss a defect, and a snapshot can preserve a mistaken
expectation. Describe the checks without claiming that tests verify themselves.

Agents also make broad, repetitive coverage practical. Exercising a proc-macro's accepted syntax
forms is valuable work that the author has limited time to complete by hand. This is the reason for
using agents extensively in the test suite.

### The core library

The author designs every CGP construct and interface, and writes the core library almost entirely
by hand. This is the code users import, so the disclosure must distinguish design ownership from
implementation assistance.

AI assists with correctness checks, quality review, and proc-macro implementation. The author sets
the design and directs and reviews the implementation work. Say both: he decides what CGP's
constructs mean, and agents sometimes help implement them.

Avoid the unqualified claim that the library is entirely hand-written. The `cgp` history includes
AI co-authorship trailers on proc-macro work. Those records are useful disclosure, but a trailer
alone does not distinguish design from implementation or establish how much review occurred.
Describe those responsibilities directly.

## How to word a disclosure

Use a short factual description of the actual process. Apply these rules:

- **Use plain language.** For example: "AI agents write these reference pages from a public
  knowledge base and check their claims against the library's source." Use this only where it
  describes the work performed.
- **Claim only the review that happened.** Do not replace spot checks with a claim that every page
  received full human review.
- **Keep responsibility with the project.** An error in an AI-written page is the project's error.
  Disclosure must not serve as an excuse.
- **Describe the practice.** A standing policy should explain the work, without depending on model
  names. A dated account, such as the [new-website post](../website/blog/new-website.md), may name
  the tools used in that episode.
- **Keep provenance out of the feature pitch.** AI authorship describes how the project is made.
  [Agent support](message.md#the-one-mitigation-that-spans-three-of-these) describes help with using
  CGP and belongs beside adoption costs. Keep those claims separate.

## The two claims that are easiest to get wrong

Preserve the qualifications on core-library authorship and human review. The
[core-library section](#the-core-library) distinguishes the author's design from assisted
implementation. The review claim must be equally precise.

The website's [authorship rule](../website/AGENTS.md#who-drafts-a-page-and-who-reads-it-before-it-publishes)
is the authority on which pages receive full review. It requires the author to read the front page,
every Concepts explanation page, the reference index, the AI disclosure page, and every blog post in
full before publication. Other pages follow their writing guides and receive spot checks. Consult
that rule when drafting a disclosure instead of reconstructing the list from memory.

The review policy reflects the kind of work each page requires. Construct reference pages are ports
of source-checked documents into a fixed template, while argument and framing require close human
reading. Source checks and spot checks can still miss errors. Do not turn this process into a
promise that every claim is correct or every page has been read in full.

Update the disclosure whenever the review arrangement changes. The
[synchronization rule](../AGENTS.md#the-synchronization-rule) applies to these process claims just
as it applies to claims about a macro's expansion.

## The page on the website

Use one dedicated disclosure page to explain the levels and help readers assess each part of the
project. This document specifies that page because it is a single project-information page, like
Project status, rather than a recurring page type needing a separate writing guide.

Open with the organizing principle, then present the levels in this document's order. Begin with
agent-written documentation and end with the core library, so the page explains substantial AI use
before describing its limits. Each level covers its scope, the division of work, the reason for
that division, and the limits of review. Give the knowledge-base process enough space for readers
to understand how it can be checked.

Write in the project voice, with a visible personal statement where accountability requires it.
For example, the author may say "every error is mine." The
[Contribute page's sponsorship section](../website/site-structure.md) provides a precedent for
switching visibly to his voice.

Keep the page focused on CGP's actual practice. Omit defensiveness, arguments about AI's general
legitimacy, comparisons with other projects' practices, and claims that the process produces better
work than a human would.

## Linking to it from a page

Add a provenance note to each new or substantially rewritten AI-assisted website page. Follow
these requirements:

- **Put one line at the foot of the page.** Keep provenance easy to find without interrupting the
  page's explanation.
- **Link to the applicable disclosure section.** Use consistent wording for each arrangement;
  agent-written reference pages and agent-revised blog posts need different sentences.
- **Do not add notes to existing pages without a request.** Establish each page's actual provenance
  before labeling it. A site-wide sweep would risk presenting guesses as disclosures.
- **Record the level in the page's internal document.** Preserve the authorship arrangement where
  the website's page records are maintained.
- **Limit this work to the website.** Disclosure for other repositories, including `cargo-cgp`, is
  separate work after the website redesign is published. Do not add notes to their READMEs or
  documentation in the meantime.

The [new-website post](../website/blog/new-website.md) supplies only partial disclosure for older
pages. It describes LLM refinement of text that existed when it was published. It does not establish
agent authorship or cover later additions. Closing those gaps requires a requested review of each
page's provenance.

## Keeping this current

Revise this policy and its public page when authorship or review practices change. Check them when
a part of the project starts or stops being agent-written, when review requirements change, or when
a stated limit becomes inaccurate. The disclosure must describe the process in use.
