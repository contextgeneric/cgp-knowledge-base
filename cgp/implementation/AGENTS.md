# AGENTS.md: the CGP implementation documentation

Read [README.md](README.md) for the catalog. The base-wide [../../AGENTS.md](../../AGENTS.md) rules and
the [../AGENTS.md](../AGENTS.md) rules apply, including invoking the `/cgp` skill before writing.

## Rules

- Revise the matching implementation document in the same change as a parser, pipeline, generated-item,
  or error-path change.
- Update the Tests or Snapshots section in the same change as a test or snapshot move.
- Keep every test and snapshot pointer here; a reference document never points at a test.
- Verify every claim against the `types/<construct>/` modules, the `functions/` helpers, and the tests.
- Improve the code's inline docs in the same pass: add a one-line `///` to a public item that lacks
  one, correct a stale comment, and delete a comment that restates the code.
- Keep inline docs terse and leave the deep mechanics to the implementation document.
- Place a document by the source construct it describes.
- Make one `asts/` document cover one evaluation stack, not one type.
- Split `functions/` by what a helper does, adding a sub-directory when a family grows.
- Link an entrypoint to the AST stack, the functions, and the internal macros it drives.
- Follow the document shape: a level-one heading and one-sentence summary, the prescribed middle
  sections for the kind, and a closing Tests and Source.
- Make Tests and Source bullet lists, one test or source pointer per bullet.
- Give the high-level picture and leave the line-by-line mechanics to the code.
- Name an internal function only as an entry point into the code.
- Use a short before/after snippet where it makes a transform concrete.
- Use a bullet list for a set of tests, snapshots, keys, or source pointers.
- Link every behavioral test and rejection case in Tests, with a one-line note on what it pins.
- Index every snapshot in Snapshots, describe its variant, and state the variants that have no
  snapshot.
- List only files that invoke the macro's `snapshot_*!`; a behavioral test without a snapshot belongs
  under Tests.
- Record a limitation or bug under Known issues with the current behavior, the correct behavior, and a
  short snippet; cross-link the reference's user-visible consequence; remove the note when fixed.
- Index a failure case captured in `cgp-macro-tests` from the relevant Known issue and from its Tests
  section.

## Documenting how a macro's expansion can fail to compile

- Separate an acceptable failure, which the macro intentionally defers to the compiler, from a
  problematic failure, which is a defect.
- Record an acceptable failure in a `## Failure modes` section, link the error catalog class and its
  `cargo-cgp` fixture, and keep it out of Known issues.
- Apply the adjacency test before calling a failure acceptable: if the construct already handles the
  neighbouring case, the gap is a defect.
- Distrust the justification that the macro cannot know the author's intent; only missing
  expansion-time information or genuine ambiguity in the language justifies a deferral.
- Record a problematic failure under `## Known issues`, with the current behavior, the correct
  behavior, and the offending input.
- Give every documented case a short snippet, and update the class document and the fixture in the same
  change.
- Update the error catalog class and the owning macro's implementation document when you add or bless a
  fixture.

## Alignment

- The reference document owns the user-facing contract, syntax, expansion, and user-visible corner
  cases, and points only at library source.
- The implementation document owns the pipeline, the synthesizing functions, the AST types, and all
  test and snapshot pointers.
- Update both views in the same change; cross-link rather than duplicate.
