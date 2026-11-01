# The driver

This directory documents `cargo-cgp-driver`, the `rustc` replacement cargo runs for each workspace crate.
The two documents answer different questions: read the first when debugging a launch or changing how the
driver runs the compiler, and the second when changing what the tool says about one class of mistake.

- [The driver as a program](program.md): how cargo invokes it, argument preparation, compiler-API access,
  the two argument levers, de-duplication and coalescing, and panic containment.
- [Diagnostic reshapes](diagnostic-reshapes.md): the emitter's stages in order, and what each does to its
  class of CGP mistake.

The [typed resolver](../typed-resolution/README.md), the emitter's last stage, has its own directory.
