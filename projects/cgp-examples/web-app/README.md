# `web-app`

`web-app` wires one social-media backend four times, once per module, to show how the wiring of a
CGP application changes as its component count grows: coarse manager traits, fine-grained
per-operation traits with provider bundles, namespace-grouped wiring, and namespace default
implementations.

- **Source**: [web-app/](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/web-app), on the
  `v0.8.0` branch; see [which revision](../README.md#which-revision-these-documents-describe)
- **Run**: nothing: the crate has no binary and no test, and every provider body is `todo!()`
- **Needs**: nothing beyond the workspace build
- **Result**: compiles, and every check block passes. A probe called a method on the contexts of
  three stages, and each call panicked with `not yet implemented`; see
  [testing.md](testing.md#what-a-probe-ran)
- **Worked example**: [social media app](../../../examples/social-media-app.md)

## What it is

The application manages users and posts and filters their content. Each module holds one stage of it
and is self-contained: it declares its own components, its own providers, and its own
`ProductionApp`, so the same names recur in all four modules. The modules share only `types.rs`,
which holds unit structs for the domain (`User`, `UserId`, `Post`, and the rest), a `PostgresDb`
handle, a two-variant `Error` enum, and a `Probability` score. The crate root carries
`#![allow(unused)]`, which hides 84 unused-variable warnings from the arguments the `todo!()` bodies
never read, and nothing else. The implicit arguments cannot be renamed with a leading underscore to
silence them, because each one's name is the context field it reads.

| Stage | Module | Components | Contexts | How the context is wired |
|---|---|---|---|---|
| [Coarse-grained](coarse-grained.md) | `coarse_grained` | two managers and two filters | `ProductionApp` | four direct entries, checked in the same macro |
| [Fine-grained](fine-grained.md) | `fine_grained` | seven operations and two filters | `ProductionApp` | array keys forwarding to three bundles |
| [Namespaces](namespaces.md) | `namespace` | the same nine, each with a prefix | `ProductionApp`, `TestApp` | two path keys each, into namespace-joined bundles |
| [Default implementations](default-impls.md) | `default_impls` | the same nine, each with a prefix | `ProductionApp` | a custom namespace that supplies seven of the nine |

Every context is an **environmental context** with a single `database` field, and every component is
self-targeted. The components return the concrete `Error` rather than an abstract error type, which
keeps the crate's subject on wiring alone.

## Idioms

The crate uses current CGP idioms throughout. Providers are `#[cgp_impl]` blocks that read the
database as an [`#[implicit]`](../../../cgp/reference/attributes/implicit.md) argument, import the
traits they call with [`#[uses]`](../../../cgp/reference/attributes/uses.md), and bind an inner
provider with [`#[use_provider]`](../../../cgp/reference/attributes/use_provider.md). Components
register into a namespace with `#[prefix(… in DefaultNamespace)]`, and providers register as
namespace defaults with [`#[default_impl]`](../../../cgp/reference/attributes/default_impl.md).

## Status and gaps

The crate demonstrates wiring only, and nothing in it runs. Its gaps are each confirmed against the
`v0.8.0` branch and recorded in full in [issues.md](issues.md):

- **Nothing runs it**: no binary and no test, and every provider body is `todo!()`.
- **Two wiring steps are comments**: the flat nine-entry table and the flat namespace table exist
  only as commented-out blocks, so the compiler does not check them.

## Where the blog post's code lives

The [v0.8.0 release post](../../../website/blog/v0-8-0-release.md) develops this application section
by section and links both the repository and its public walkthrough. Its record describes the
verification and deliberate simplifications; this table maps its stages to the crate's source:

| Post section | Current code |
|---|---|
| Start with a manager per domain; Add dependencies as the service grows | `coarse_grained.rs` has the filter-dependent stage; the post also shows the earlier database-only stage and contrasts production and test filters |
| Split independently reusable operations; Separate filtering from database access | `fine_grained.rs`; the post also shows the intermediate creator before filtering is extracted |
| Count the cost of the separation | `fine_grained.rs`: the flat table, as a comment, the provider bundles, and array-key routing |
| Give component groups a path | `namespace.rs`, whose flat namespace table is a comment |
| Group paths hierarchically; Check the completed configuration | `namespace.rs`; the post's SQLite variant is hypothetical and not part of this crate |
| Sharing default implementations | `default_impls.rs`; the post wires `AiContentFilterComponents` directly in its defaults example |
| Breaking changes and migration | an illustrative user-only configuration checked in the website's example-code crate, not a stage in this crate |

## The documents

- [coarse-grained.md](coarse-grained.md): one manager trait per domain, and the dependency the whole
  manager inherits from one method.
- [fine-grained.md](fine-grained.md): one trait per operation, the two filter wrappers, and the
  three provider bundles.
- [namespaces.md](namespaces.md): the prefix tree, the bundles that join the namespace, and the
  production and test contexts.
- [default-impls.md](default-impls.md): the custom namespace, how its seven defaults are registered,
  and the one path the context still wires.
- [testing.md](testing.md): what the check blocks pin, what probes showed they catch, and what
  nothing tests.
- [issues.md](issues.md): the missing features and housekeeping.

## Public material derived from these documents

The [v0.8.0 release post](../../../website/blog/v0-8-0-release.md), whose worked wiring follows this
crate and awaits author review and publication. It also feeds the `web-app` index of the
[cgp-examples project section](../../../website/projects/cgp-examples.md).

## How it relates to the rest of the base

The [social media app](../../../examples/social-media-app.md) worked example teaches the crate's
progression through the namespace stage and stands alone. The patterns themselves are
[higher-order providers](../../../cgp/concepts/higher-order-providers.md),
[aggregate providers](../../../cgp/concepts/aggregate-providers.md), and
[namespaces](../../../cgp/concepts/namespaces.md), and the prescriptive treatment of the last is the
[namespaces and prefixes guide](../../../cgp/guides/namespaces-and-prefixes.md).
