# Writing the error catalog

This guide holds the rules for writing and revising the class documents and code entries of the
error catalog. The knowledge base's [AGENTS.md](../../AGENTS.md) holds the rules every document
follows, and [the `cgp` writing guide](../writing-guide.md) the rules for the reference.

## Class documents

- Verify a claim against a real compilation, not memory: read the fixture's blessed `.rust.stderr` and
  `.cgp.stderr`, or re-run `cargo cgp check`.
- Check a raw-diagnostic claim on stable `rustc`; the `.rust.stderr` is blessed on the pinned nightly
  and can differ.
- Summarize the kind of error; never paste the verbatim output.
- Record the diagnostic kind, whether the root cause is present, and where it sits.
- Follow the document structure: What triggers it, the raw diagnostic, where the root cause is, how
  cargo-cgp presents it, resolving it, notes for tooling, backing fixtures, and Related.
- Omit the tooling-notes heading when the cargo-cgp section already covers the handling.
- Back every class with at least one `cargo-cgp` UI fixture, and catalog every post-codegen
  compile-fail fixture.
- Add the class document and its fixture in the same change when both checkouts are present; when
  `cargo-cgp` is absent, state the fixture that needs adding.

## Code entries

- Verify every error-code entry against the official Rust documentation, the reference, and the linked
  RFCs or issues.
- Confirm the message wording against a real compilation where a class already pins it.
- Make the entry's "Where CGP produces it" section link back to every class that emits the code, and
  keep the two directions in sync.
- Cite the local `error_codes/` entry in a class document rather than a raw
  `doc.rust-lang.org/error_codes/` URL.
- State the Rust rule only in a code entry; keep the CGP anatomy in the class document.
- Add a code entry when a class first surfaces a code not already covered.
- Link `cargo-cgp`'s own codes to its error-code catalog rather than redefining them.

## Handling the acceptable / problematic / rejection split

- Keep a fixture's output quality, its `//@quality:` header, separate from the CGP-defect
  classification the [catalog README](README.md) describes.
- Document an acceptable failure here in full; do not record it under a macro's Known issues.
- Catalog a problematic failure here for the observable error, and keep the defect explanation under
  the owning macro's `## Known issues`, cross-linked.
- Do not catalog a failure the macro catches by rejecting its input; keep it with the macro.

## Gathering an error with a sub-agent

- Grep the captured `.stderr` for the suspected line before delegating.
- Delegate the reading when the grep will not settle it, using the
  [error-extraction skill](https://github.com/contextgeneric/cgp-skills/blob/main/cgp/references/error-extraction.md).
- Write the document from the returned anatomy, not the raw dump.
