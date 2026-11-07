# AGENTS.md: the worked examples

Read [README.md](README.md) for the catalog and what an example is for. The base-wide
[../AGENTS.md](../AGENTS.md) rules apply.

## Building on a sibling CGP project

- Build on a sibling CGP project when it already serves the use case: use its crates, link its
  documents and source at the branch [../sibling-projects.md](../sibling-projects.md) records, and
  verify against that branch.
- Use a sibling project rather than re-implementing a use case it already serves.
- Verify an example that imports a sibling project against that project's source at the recorded
  branch, and say near the top which crates and branch the snippets assume.

## Rules

- Judge an example by whether it is quotable and correct, not by whether it covers every detail.
- Keep the prose light: enough to make the code legible, a short note on the concept each step shows,
  and a link to the reference document that owns it.
- Never re-explain a construct the example uses.
- Verify every snippet against the source, and invoke the `/cgp` skill before writing CGP code.
- Treat an outside source as a reference for the scenario and patterns, then write a fresh,
  self-contained example.
- Do not cite, name, or link the outside source; the example reads as native knowledge-base material.
- Re-derive the code in current CGP vocabulary rather than copying the source verbatim.
- Give the example a coherent narrative arc, usually from the simplest form to the fully wired version,
  rather than mirroring the source's structure.
- Teach every key takeaway within the example itself; a pointer to a project section goes after the
  teaching sections.
- Carry none of a project's records; a reproduced program matches the project's branch.
- Record a project's older idiom as a change in its `issues.md` rather than modernizing the example
  alone.
- Omit parts and abbreviate a repeated item with a comment, but never show a variant the branch does
  not contain.
- Open with a level-one heading, a one-sentence summary, a concept list with reference links, and any
  shared assumption.
- Develop the use case in titled sections, each with a sentence of context, the code, and a concept
  note.
- Say whether the example wires a value or environmental context and whether the component is self- or
  parameter-targeted.
- Add a missing concept to the reference or a new concept page and link it from the example.
- Register the example in [README.md](README.md) and [../summary.md](../summary.md) in the same change.
