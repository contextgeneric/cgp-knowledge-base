# Writing release notes

A release-notes page lists everything one official release changed that a user can see, and tells an
upgrader what to do about it. It is the site's one dated docs page: written for its release, published
with it, and not edited afterwards into agreement with later releases.

- **Where they live**: `docs/release-notes/`, the Release notes category after Resources, with one
  sub-category per artifact, `docs/release-notes/cgp/` and `docs/release-notes/cargo-cgp/`, and one
  page per release in each, recorded in [pages/release-notes.md](../pages/release-notes.md)
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Style**: point-first, the one page kind that names it, because a reader scans the page for the
  items that affect them
- **Derived from**: the release's source diff and its document in [releases/](../../releases/README.md),
  which stays the page's finer-detail companion; for `cargo-cgp`'s first release, the companion is
  the [cargo-cgp/](../../cargo-cgp/README.md) section
- **Status once published**: a dated record, *Historical* in the records'
  [status words](../README.md#status-words); see [A dated page](#a-dated-page)
- **Reading**: the shared set and [the release-notes row](README.md#release-notes-pages) of the
  reading map

## Two layers, two readers

**The page serves the upgrader; the release document serves an agent reading old code.** The page
holds the user-visible changes and the steps to upgrade. The release document holds the rest:
internal changes, names used and discarded during development, where the old changelog or an earlier
post was wrong, why the release took its shape, and how much of it still stands today.

**Every finding of the diff review lands in one of the two.** A change too fine or too internal for
the page goes into the release document's section for the changes the notes leave out, rather than
being dropped.

**The page is not the announcement.** The release post tells the release's story in the author's
voice and teaches its main feature; the notes give every change in the project voice and teach
nothing. Each links the other, and neither is trimmed to remove the overlap.

## Sources, and which one decides

A page is written from four inputs, read together:

- **The source diff** between the previous release's tag and this one, read one pull request at a
  time when the release is large. Tests, their snapshots, `Cargo.lock`, and the CI workflows are left
  out; a test is read only when the source leaves an item's user-visible effect unclear, such as the
  text of a new compile error.
- **The release document** in [releases/](../../releases/README.md), with its rows in the removal
  ledger.
- **The old changelog entry**, from `cgp`'s `CHANGELOG.md` at the release's tag, for the releases
  it covered.
- **The old release notes**: the GitHub Release body and the release post, where they exist.

**The diff decides a disagreement, then the release document, then the other three.** A release
document that the diff contradicts is corrected in the same change as the page. The changelog and the
old notes catch items the others leave implicit, but they never outrank the code: the changelog alone
carried errors that the
[release history](../../releases/README.md#what-counts-as-a-release-and-where-the-facts-come-from)
records.

**Three facts come from one source each:**

- **The date** is the version's publish date on crates.io, in ISO 8601 form, even where the tag is a
  day apart; the release document records both.
- **The minimum Rust version** is the `rust-version` in the release tag's `Cargo.toml`.
- **The pull-request links** come from the Git log's first-parent commits, written as
  `https://github.com/contextgeneric/<repository>/pull/<n>`.

## A dated page

**A page states what its release did, as of that release.** It is written on the website's release
branch before the tag, as though the release had shipped. Its date and its tag, compare, and
crates.io links are set on release day, when they first resolve, and it publishes with the website,
before the release's GitHub Release, which holds one sentence and a link to the page. A page for a
release that predates the category is written afterwards from the same sources and states the same
facts as of its release.

**After publication, only a factual error against the tag is corrected.** A page is never updated to
describe later behavior, never annotated with what a later release changed, and never given an
*Unreleased* section: a change appears only on the page of the release that ships it. This exempts the
category from the rule that a page under `docs/` describes the present.

## The section shape

**The category's index**, `docs/release-notes/index.md`, is the category's link target. It names
Context-Generic Programming beside a plain description, says what the notes are and that each
release has its own page, and links each artifact's sub-category and newest page.

**The index also states how CGP numbers its 0.x releases**, written only from the checked diffs of
the releases it describes, such as whether a patch release ever broke code.

**Each sub-category** has a `_category_.json` with its label (`cgp` or `cargo-cgp`), its position
(`cgp` first), a generated index, and a `description` that names Context-Generic Programming.

**Pages sort newest first.** Docusaurus sorts by `sidebar_position`, ascending, so each page sets it
to 100000 minus its version read as `major × 10000 + minor × 100 + patch`: v0.8.0 is 99200 and v0.7.0
is 99300. A later release never renumbers an earlier page.

## The page's parts, in order

Every page has the parts below, in this order, and leaves out a section with nothing in it:

- **Front matter**:
  - `title`: `<artifact> v<version> release notes`, such as `cgp v0.8.0 release notes`. It names the
    artifact, which for `cgp` is the crate, so the rule against naming CGP in a title does not apply.
  - `sidebar_label`: the bare version, and `sidebar_position` as above.
  - `description`: the release's two or three main changes, within about 155 characters, with
    apostrophes escaped as the reference guide's
    [conventions](reference.md#conventions-the-port-must-follow) give.
  - `slug`: the version with its dots, such as `v0.8.0`.
- **The heading and the opening**: the `#` heading names the artifact and version. The first sentence
  names Context-Generic Programming, linked to the Introduction, beside a plain description, and says
  what the release is for. A short form of the tag line appears only where the release's main change
  is about choosing an implementation.
- **The date and the links**: `Released on <YYYY-MM-DD>`, then the release post where one exists, the
  crate on crates.io, and the compare view from the previous tag, or the tag itself for an artifact's
  first release.
- **The summary**: two to four sentences on the release's main changes, each named once.
- **Compatibility**: the minimum Rust version; the versions released with it, such as the workspace's
  other crates and any `cargo-cgp` release made beside it; renamed or added crates; and changed Cargo
  features.
- **Upgrading**: the ordered steps for a project moving from the previous release, each linking the
  breaking change it carries out. A release without a breaking change says in one sentence that
  changing the version is enough, and only when the diff check supports it.
- **Breaking changes**: one `###` heading per change, so *Upgrading* can link it, since a heading is
  the only anchor the site generates.
- **Deprecated**, **New features**, **Improvements**, **Fixes**, and **Security**: one item per
  change. A long section is grouped under `###` headings by area, in the order the
  [reference](reference.md) groups its constructs.
- **The provenance line**, where the page ends. The previous and next links that Docusaurus generates
  take a reader to the neighbouring releases, and the opening's links lead to the post and the crate.

### Writing an entry

**An entry opens with the change, stated as what a user now meets**, in the present tense, with the
construct as the subject: "`#[use_type]` separates the trait from its type with `.`". The reason, the
condition, or the consequence follows in the next sentence.

- **A breaking change** gives the old form, the new form, and what a project does to move, in that
  order.
- **A deprecation** names its replacement and its planned removal, and lists only what the code marks
  with `#[deprecated]`. A form the documentation calls legacy, such as `UseDelegate` dispatch, stays
  out until the code marks it.
- **A removal** names what replaces it, or says that nothing does.
- **Every entry links** the construct's reference page where the site has one, and the pull request
  that introduced the change where one did.

**Code is inline unless one line cannot show a migration.** From v0.8.0, a page may show a block of
old and new code for such a migration; the new form compiles in the `example-code` crate, and the old
form is checked against the previous release's tag. A page for an earlier release writes both forms
inline only, because `example-code` builds against the current `cgp`.

## What every page owes its reader

- **The naming rule**: Context-Generic Programming once, in the opening, per
  [identity.md](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page).
- **The title and description levers**, per
  [seo.md](../seo.md#titles-and-descriptions-are-the-per-page-levers-and-docusaurus-separates-them):
  the artifact and version first, under about 60 characters, and a description written for this
  page rather than a template.
- **Every breaking change**: each removal-ledger row in which this release removes or renames
  something an earlier release shipped appears under *Breaking changes*. A reader who learns of a
  removal from a compiler error has been let down at the highest cost in trust.
- **A provenance line**, per
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md#linking-to-it-from-a-page), in
  italics after a `---` rule, as the other docs pages set it. It reads "An AI agent wrote this page
  from the release's source changes and the CGP knowledge base. Its content was verified against the
  library's source at the release's tag. See How AI is used in this project.", with the last phrase
  linking the disclosure page's documentation section; a `cargo-cgp` page says "the tool's source".
  The category's record holds the level.

## What must not be on one

- **No commit log.** Pull-request titles, refactors, test changes, and CI changes without a
  user-visible effect stay out; the release document keeps the internal ones.
- **No pre-release.** No page names an alpha, beta, or prerelease version, or says how one behaved,
  per the base's [rule on versions](../../AGENTS.md#document-official-versions-never-pre-releases).
- **No history of the documentation.** Where the old changelog was wrong, the page states what
  shipped, and the release document records the error.
- **No knowledge-base links**, per the
  [one-way rule](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links), and
  no link to or recommendation of a
  [legacy resource](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#legacy-resources).
- **No unbenchmarked performance claim** and no promotional wording, per the
  [avoid list](../../communication-strategy/vocabulary.md#words-and-framings-to-avoid).

## Checking a draft

- **Trace every item to the diff**, and every user-visible change in the diff to an item on the page
  or in the release document.
- **Compare the page with the changelog entry, the GitHub Release body, and the post**, item by item;
  each item they hold that the page lacks has a reason recorded in the release document.
- **Check the removal ledger's rows for the release** against *Breaking changes*; a rename within the
  release's own development, or a name never released, stays off the page.
- **Check the facts at their sources**: the date on crates.io, the minimum Rust version in the tag's
  `Cargo.toml`, and each pull-request number in the Git log.
- **Read the first sentence of each entry in order**; together they state the changes.
- **Build the site**, which fails on a broken link or anchor, and check that every external link
  answers, apart from the tag, compare, and crates.io links that resolve on release day.
- **Compile any code block** in `example-code`, and check its old form against the previous tag.
