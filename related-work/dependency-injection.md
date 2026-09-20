# Dependency injection

Dependency injection (DI) is the practice of giving an object its collaborators from the outside
instead of letting it construct them. The frameworks built around it (Spring, Guice, Dagger, and their
kin) automate the wiring so a large application's object graph assembles itself. CGP solves the same
decoupling problem, but at compile time and without a container, so DI is the concept a reader with an
enterprise background is most likely to reach for when they first meet CGP wiring.

## Purpose

Every non-trivial program has to decide where its components get the things they depend on, and
dependency injection keeps those decisions out of the components themselves. A class that needs a
database, an HTTP client, and a logger can create them in its constructor, which hard-codes the concrete
types, or it can accept them as parameters and let whoever builds it supply them. The second choice is
dependency injection. Its payoff is decoupling: the class names only the *interfaces* it needs, so a test
can pass fakes, a different deployment can pass different implementations, and the class never changes.
The cost is that something has to do the supplying, and in a large graph that "something" is elaborate
enough that frameworks exist to run it.

CGP separates declared dependencies from selected implementations through traits and wiring.
DI frameworks address the same decoupling problem, but differ in resolution and object management:
Spring and Guice commonly assemble graphs at runtime, while Dagger generates wiring at compile time.
CGP resolves provider selection statically and leaves runtime value construction to Rust code.

## The concept in depth

Dependency injection is a specific form of *inversion of control*. Rather than a component reaching out
to fetch its dependencies, control is inverted so the dependencies are handed to it. The idea predates
any framework and is expressible in plain code by passing collaborators as constructor arguments, but
the frameworks are what most practitioners mean by "DI", because they automate the assembly. The
sections below cover the container-and-annotation model that Spring popularized, the module-and-binding
model of Guice and Dagger, and the plain-code form that Rust already encourages.

### The IoC container and beans (Spring)

Spring's core is an *inversion-of-control container*: an object, the `ApplicationContext`, that
instantiates, configures, and connects the application's objects, its *beans*, and manages their
lifecycles. A class is marked as a bean with an annotation such as `@Component` or `@Service`, and the
container discovers it by scanning the classpath. The container owns every bean it creates, so the
application asks the container for a fully assembled object rather than constructing one itself.

```java
@Service
public class UserService {
    // business logic lives here
}
```

The container is configured either by annotation-driven scanning, as above, or explicitly with a
`@Configuration` class whose `@Bean` methods return the objects to manage. The explicit form is where a
bean's construction is spelled out, including which implementation stands in for an interface:

```java
@Configuration
public class AppConfig {
    @Bean
    public StorageClient storageClient() {
        return new S3StorageClient(/* ... */);
    }
}
```

### Constructor, setter, and field injection

Once the container holds a set of beans, it injects each bean's dependencies by one of three
mechanisms, and the choice among them is the most-discussed decision in day-to-day Spring.
**Constructor injection** passes dependencies as constructor arguments, which makes them required and
lets the field be `final`:

```java
@Service
public class ProfilePictureService {
    private final StorageClient storage;
    private final UserRepository users;

    public ProfilePictureService(StorageClient storage, UserRepository users) {
        this.storage = storage;
        this.users = users;
    }
}
```

**Setter injection** supplies a dependency through a setter after construction, which suits optional
collaborators. **Field injection** writes the dependency straight into a private field by reflection,
marked with `@Autowired`:

```java
@Service
public class ProfilePictureService {
    @Autowired private StorageClient storage;   // field injection
    @Autowired private UserRepository users;
}
```

The `@Autowired` annotation instructs the container to resolve a dependency by type: it finds the one
bean assignable to `StorageClient` and injects it. When a class has a single constructor, Spring treats
it as autowired without the annotation, which is why modern Spring code favors constructor injection and
reserves `@Autowired` for the ambiguous or field-injected cases. The Spring team and the wider community
now recommend constructor injection for all required dependencies, because it makes a class's
dependencies explicit in its signature, keeps them non-null, and lets the object be built without a
container in a test ([Spring Framework reference](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)).

### Modules and bindings (Guice and Dagger)

Guice and Dagger express the same wiring not by classpath scanning but by explicit *bindings* declared
in a *module*. A Guice module maps an interface to an implementation, and the injector resolves a
request for the interface to the bound implementation:

```java
public class StorageModule extends AbstractModule {
    @Override
    protected void configure() {
        bind(StorageClient.class).to(S3StorageClient.class);
    }
}
```

A class requests its dependencies by annotating its constructor with `@Inject`, and the injector
supplies them from the bindings. Dagger uses the same `@Inject` and module vocabulary but resolves the
graph at *compile time*. Its annotation processor generates the wiring code during the build, so a
missing or ambiguous binding is a compile error and there is no reflection at runtime. This
compile-time-versus-runtime split is the sharpest axis of variation among DI frameworks. Spring and Guice
resolve bindings at runtime through reflection; Dagger resolves them at compile time through generated
code. CGP sits firmly at the compile-time end of that axis.

### Dependency injection without a framework (Rust)

Rust practitioners generally hold that the language needs no DI framework, because traits and generics
already provide the decoupling a container is built to deliver. A function that needs a dependency
takes a generic parameter bounded by a trait; a caller supplies any type implementing that trait; a test
supplies a fake. Construction is separated from use by the ordinary discipline of taking collaborators
as arguments rather than building them internally.

```rust
trait StorageClient {
    fn fetch(&self, object_id: &str) -> Vec<u8>;
}

struct ProfilePictureService<S: StorageClient> {
    storage: S,
}
```

This design is often sufficient. Different storage types can implement `StorageClient`, so replacing
one collaborator does not itself require CGP. The additional work appears when generic parameters
spread through enclosing types, or when reusable implementations overlap for the same target type.
CGP addresses those cases with a shared context and separately named providers. The
[coherence explanation](../cgp/concepts/coherence.md) develops the latter problem.

## How CGP expresses it

CGP performs dependency injection through two mechanisms working together. A provider declares what it
needs as [impl-side dependencies](../cgp/concepts/impl-side-dependencies.md), and a context supplies
them by [wiring](../cgp/concepts/consumer-and-provider-traits.md) each component to a provider. The
impl-side dependency is the counterpart of a constructor's parameter list, and the wiring table is the
counterpart of the container's configuration. Both are resolved by the compiler, so the "container" has
no runtime existence at all. The snippets below come from the [social media app](../examples/social-media-app.md)
and [profile picture](../examples/profile-picture.md) examples, and every context in them is an
**environmental context**: a type standing for an application, which carries the application's choices
and dependencies rather than being the data operated on.

### Impl-side dependencies are the injected constructor parameters

A provider states the collaborators and values it needs in a way that reads like declaring
dependencies, and CGP satisfies them from the context rather than from a container. Where a Spring
service lists `StorageClient` and `UserRepository` as constructor parameters, a CGP provider lists its
trait dependencies with [`#[uses(...)]`](../cgp/reference/attributes/uses.md) and its value
dependencies with [`#[implicit]`](../cgp/reference/attributes/implicit.md) arguments. A user-creation
provider that needs a database connection and a censorship service declares both. The `Error` here is
the example's own concrete enum, and the elided body inserts the user through `database`:

```rust
#[cgp_impl(new PostgresUserManager)]
#[uses(CanCensorUsername)]
impl UserManager {
    fn create_user(
        &self,
        #[implicit] database: &PostgresDb,
        username: &str,
        email: &Email,
    ) -> Result<User, Error> {
        if self.username_is_censored(username) > Probability::new(0.8) {
            return Err(Error::InvalidUsername);
        }
        // ... insert the user with `database`
    }
}
```

The `#[uses(CanCensorUsername)]` line injects a *trait dependency*, the role a `UserRepository`
collaborator plays in the Spring constructor. The `#[implicit] database` argument injects a *value*
pulled from the context's `database` field, the role a configuration bean plays. Neither dependency
appears in the `CanManageUser` consumer trait a caller invokes, so, unlike a leaked generic bound, they
do not cascade to callers. That is the decoupling a DI framework promises, delivered by hiding the
requirements one level down in the provider's impl rather than in a container.

### Wiring is the container configuration

A context selects which provider satisfies each component in a
[`delegate_components!`](../cgp/reference/macros/delegate_components.md) table, the direct analogue of
a Spring `@Configuration` class or a Guice module: the one place where interfaces are mapped to
implementations. Swapping an implementation is a one-line edit to this table. The crucial difference is
that two contexts can map the same component to different providers with no conflict, because the
choice is keyed on the context type. A profile-picture service backed by different object stores in
different deployments is two wiring tables:

```rust
#[cgp_component(StorageObjectFetcher)]
pub trait CanFetchStorageObject {
    fn fetch_storage_object(&self, object_id: &str) -> anyhow::Result<Vec<u8>>;
}

delegate_components! {
    App {
        StorageObjectFetcherComponent: FetchS3Object,
    }
}

delegate_components! {
    GCloudApp {
        StorageObjectFetcherComponent: FetchGCloudObject,
    }
}
```

`FetchS3Object` and `FetchGCloudObject` are interchangeable providers selected per context.
Calls through `App` route statically to the S3 provider, while calls through `GCloudApp` route to
GCloud. One program can use either context or both. The wiring does not require separate binaries
or guarantee that either provider is absent from a binary.

### Checking replaces the container's startup validation

A DI container discovers a missing or ambiguous binding when it assembles the graph: at startup for
Spring and Guice, at build time for Dagger. CGP's counterpart is
[`check_components!`](../cgp/reference/macros/check_components.md), which asserts at compile time that a
context's wiring is complete and every provider's transitive dependencies are satisfied:

```rust
check_components! {
    App {
        StorageObjectFetcherComponent,
    }
}
```

If `FetchS3Object` needs a field or trait the `App` context does not supply, this fails to compile with
the missing dependency named, rather than surfacing as a startup exception or a `NullPointerException`
deep in a request. It is the same guarantee Dagger gives, that the graph is verified before the program
runs, reached through the trait system instead of an annotation processor. CGP wiring is
[lazy](../cgp/concepts/check-traits.md), so this check is what turns a latent gap into an early, readable
error.

## What users like and dislike

Dependency-injection frameworks are among the most widely adopted tools in enterprise software, and
practitioners value them for real reasons. They decouple components from their collaborators, which
makes code testable (a fake is injected exactly where a real dependency would be) and swappable across
environments. They centralize wiring, so the shape of an application's object graph lives in one readable
place rather than scattered through constructors. And a mature framework like Spring brings an enormous
ecosystem: transaction management, security, web bindings, and configuration all keyed off the same bean
model, so adopting the container brings far more than injection.

The complaints are equally well documented, and they cluster around the runtime, reflective nature of the
popular frameworks. The most common is that dependencies become *hidden*. With field injection, a class's
signature says nothing about what it needs, so a reader must scan the whole class and a maintainer can add
a dependency invisibly. Reflection-based resolution means a missing or mis-typed binding is a *runtime*
failure, a startup exception or a `NullPointerException` in production, not a compile error, which is why
the Spring community steers toward constructor injection and away from field injection
([Nuri, *Field injection is not recommended*](https://blog.marcnuri.com/field-injection-is-not-recommended)).
There is a performance and startup cost to scanning the classpath and building the graph reflectively,
which is why Dagger's compile-time generation exists and why it wins on Android and in latency-sensitive
services. And there is the recurring complaint of *magic*: the framework does so much automatically,
through reflection and proxies, that when something goes wrong the developer has little visibility into
why, and the behavior is hard to reason about from the code alone
([Shore, *The Problem With Dependency Injection Frameworks*](https://www.jamesshore.com/v2/blog/2023/the-problem-with-dependency-injection-frameworks)).
Even proponents concede the learning curve is steep and the machinery is heavy for a small program.

## How CGP compares

DI frameworks centralize object construction and wiring, but their automation takes work to trace.
Field injection can hide dependencies from a class's constructor, and runtime graph assembly can
report missing bindings only when that graph is built. Constructor injection makes dependencies
visible; compile-time generation, as in Dagger, moves binding validation into the build. These costs
therefore depend on the framework and injection style. The
[Spring reference](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)
explains the injection trade-offs, and
[Shore's critique](https://www.jamesshore.com/v2/blog/2023/the-problem-with-dependency-injection-frameworks)
argues that framework automation can make a dependency graph harder to follow.

CGP requires declarations, wiring, and compile-time trait resolution. Developers must learn the
consumer/provider split and trace dependencies through the context. Its wiring selects providers
statically; runtime reconfiguration requires ordinary Rust mechanisms, such as enums or trait
objects, inside or alongside that wiring. CGP also leaves object construction and lifecycle
management to the application.

CGP's raw errors can be difficult to read because they include generated traits and types.
[`cargo cgp check`](../cargo-cgp/reference/usage.md) leads with the root cause for the classes it recognizes,
and the tool is a v0.1.0-alpha that does not yet reshape every class. The
[Modularity Hierarchy](../cgp/concepts/modularity-hierarchy.md) weighs the additional machinery against
plain traits, generics, and other alternatives.

### Where the other approach fits

A DI framework fits applications that rely on its object lifecycle support, runtime configuration,
or surrounding ecosystem. A JVM application built around Spring's bean model already has reasons
to use that model beyond selecting implementations. Dagger is an option when that application wants
compile-time graph validation.

Plain Rust traits and generics fit dependencies that can be expressed without extensive parameter
propagation or overlapping implementations. CGP becomes useful when reusable providers need
independent implementation choices per context and static wiring justifies the extra declarations.
A build-time dependency graph alone does not make CGP necessary.

## Presenting CGP to someone who knows this

Map a provider's declared requirements to constructor dependencies and its wiring to configuration.
Distinguish selecting an implementation from constructing and managing runtime objects: CGP handles
the former through traits, while ordinary Rust code handles values and lifetimes.

Compare frameworks individually. Dagger already validates graphs at compile time, and DI frameworks
can support multiple graphs or configurations. Do not imply that per-application choice belongs only
to CGP, or that plain Rust generics cannot substitute different collaborator types.

Scope the guarantees to declared dependencies and static provider selection. Checks do not validate
credentials or other runtime conditions. Contexts and providers can use enums, trait objects, and
runtime configuration. Avoid claims that a provider necessarily disappears from a binary or that a
CGP application cannot fail at runtime.

## Sources

The public version of this document is the website's
[dependency-injection comparison page](https://contextgeneric.dev/docs/comparisons/dependency-injection), ported per the
[comparison page guide](../website/writing-guides/related-work.md); a change here updates that page
in the same change.

The account of the related work draws on the official framework documentation and representative
community writing. The CGP snippets are taken from the [social media app](../examples/social-media-app.md)
and [profile picture](../examples/profile-picture.md) examples.

- [Spring Framework reference — Dependency Injection](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html) — the authoritative description of the IoC container, beans, and the constructor and setter injection mechanisms.
- [Baeldung — Inversion of Control and Dependency Injection in Spring](https://www.baeldung.com/inversion-control-and-dependency-injection-in-spring) — the distinction between IoC and DI and the `@Autowired` autowiring-by-type behavior.
- [Comparing Dependency Injection Frameworks — Spring, Guice, Dagger, and Micronaut](https://medium.com/@AlexanderObregon/comparing-dependency-injection-frameworks-spring-guice-and-dagger-a614dccd5859) and [Dagger vs Guice](https://www.hackingnote.com/en/versus/dagger-vs-guice/) — the runtime-versus-compile-time split and the reflection-versus-generated-code trade-off across frameworks.
- [Field injection is not recommended (Marc Nuri)](https://blog.marcnuri.com/field-injection-is-not-recommended) and [James Shore — The Problem With Dependency Injection Frameworks](https://www.jamesshore.com/v2/blog/2023/the-problem-with-dependency-injection-frameworks) — the hidden-dependency, runtime-failure, and "magic" criticisms, and the case for constructor injection.
- [Rust traits and dependency injection (jmmv.dev)](https://jmmv.dev/2022/04/rust-traits-and-dependency-injection.html) — the position that Rust performs dependency injection through traits and generics without a framework.
