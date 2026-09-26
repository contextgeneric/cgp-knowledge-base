# Adding an endpoint

A new endpoint touches six places in `transfer`, not only a handler and a table entry: the endpoint
needs a marker, request types, a handler, a pipeline, a `Send` impl, and a route, plus an entry in
the context's check. This guide lists each piece and where it goes, using a
`GET /whoami` endpoint that returns the logged-in user as the running example. Every snippet below
compiled and ran in a downstream probe crate against the `v0.8.0` branch, where the endpoint answered
`alice` for Alice's credentials.

## The six pieces

Each piece has a home in the crate's [module layout](../architecture/module-layout.md), and the list
gives it. A downstream crate that cannot edit `transfer` places all six in its own crate instead, with
the differences noted in [the last section](#from-a-downstream-crate).

1. **A marker** in `interfaces/api.rs`, which selects the provider:

   ```rust
   pub struct WhoAmIApi;
   ```

2. **Request types** in `types/requests/`: a query struct Axum deserializes, the raw extractor tuple,
   a domain struct that derives `HasField`, and a `From` impl between the last two. The domain struct
   must carry `basic_auth_header` and `logged_in_user` fields if the pipeline authenticates, since
   `UseBasicAuth` reads and writes them through its getters:

   ```rust
   #[derive(Deserialize)]
   pub struct WhoAmIQuery {}

   pub type AxumWhoAmIRequest = (Query<WhoAmIQuery>, Option<TypedHeader<Authorization<Basic>>>);

   #[derive(HasField)]
   pub struct WhoAmIRequest {
       pub basic_auth_header: Option<(String, String)>,
       pub logged_in_user: Option<String>,
   }

   impl From<AxumWhoAmIRequest> for WhoAmIRequest {
       fn from((_, auth): AxumWhoAmIRequest) -> Self {
           Self {
               basic_auth_header: auth.map(|TypedHeader(Authorization(b))| {
                   (b.username().into(), b.password().into())
               }),
               logged_in_user: None,
           }
       }
   }
   ```

   The raw type must implement `FromRequestParts`, so it can read the URI and headers but not a
   request body; see [the HTTP layer](../reference/http-layer.md#canaddroute).

3. **A handler** in `providers/api_handlers/`, an `ApiHandler` provider generic over its request, that
   names only the components it calls:

   ```rust
   #[derive(Serialize)]
   pub struct WhoAmIResponse {
       pub user: String,
   }

   #[cgp_impl(new HandleWhoAmI<Request>)]
   #[uses(CanRaiseHttpError<ErrUnauthorized, String>)]
   #[use_type(HasErrorType.Error, HasUserIdType.{UserId = String})]
   impl<Api, Request> ApiHandler<Api>
   where
       Request: HasLoggedInUser<Self>,
   {
       type Request = Request;
       type Response = WhoAmIResponse;

       async fn handle_api(&self, _api: PhantomData<Api>, request: Request) -> Result<WhoAmIResponse, Error> {
           let user = request.logged_in_user().clone().ok_or_else(|| {
               Self::raise_http_error(ErrUnauthorized, "you must first login".into())
           })?;

           Ok(WhoAmIResponse { user })
       }
   }
   ```

   The `{UserId = String}` pin is there only because this response holds a `String`; a handler whose
   output stays abstract, as `QueryBalanceResponse<App>` does, needs no pin.

4. **A pipeline** in `namespaces/api_handlers.rs`: one more entry in `DefaultApiHandlers`, which
   `MockApp`'s `for` loop then picks up with no change to the context's wiring:

   ```rust
   WhoAmIApi:
       HandleFromRequest<
           AxumWhoAmIRequest,
           ResponseToJson<UseBasicAuth<HandleWhoAmI<WhoAmIRequest>>>,
       >,
   ```

5. **A `Send` impl** in `contexts/app.rs`, because the route needs a `Send` future and the trait
   cannot be implemented generically:

   ```rust
   impl CanHandleApiSend<WhoAmIApi> for MockApp {
       async fn handle_api_send(
           &self,
           api: PhantomData<WhoAmIApi>,
           request: Self::Request,
       ) -> Result<Self::Response, Self::Error> {
           self.handle_api(api, request).await
       }
   }
   ```

6. **A route** in `providers/axum/routes.rs`: one more `CanAddRoute` bound and one more `add_route`
   call in `CanAddMainApiRoutes`, which fixes the path and the method:

   ```rust
   .add_route(PhantomData::<(WhoAmIApi, GetMethod)>, "/whoami")
   ```

Finally, add `WhoAmIApi` to the `ApiHandlerComponent` list in `MockApp`'s `check_components!` block,
so a missing dependency of the new pipeline is reported at the wiring rather than at the route.

## What the compiler checks for you

The check entry and the `Send` impl are the two places a mistake surfaces. A pipeline whose request
type lacks a field a getter needs, or whose handler calls a component the context does not wire,
fails the `check_components!` entry. A handler whose future holds something that is not `Send` across
an `.await` fails the `CanHandleApiSend` impl, since that impl is the only place the future's `Send`
is proven. A route whose request cannot be extracted from the URI and headers fails the `CanAddRoute`
bound in `CanAddMainApiRoutes`. These locations follow from where each bound is written; the probe
exercised only the passing case, so the exact messages are not recorded here.

## From a downstream crate

A crate that depends on `transfer` cannot wire a new endpoint onto `MockApp`. The entry would
implement CGP's `DelegateComponent` for `MockApp`, a foreign type, keyed by a `PathCons` path, which
is never a local type, so the orphan rule rejects it. The downstream crate instead defines its own
context with the fields the backend reads, joins the same namespace, loops over the same table, and
adds its endpoint as a direct entry beside the loop:

```rust
delegate_components! {
    ConstApp {
        namespace ConstNamespace;

        for <Key, Value> in DefaultApiHandlers {
            @app.api.ApiHandlerComponent.Key: Value,
        }

        @app.api.ApiHandlerComponent.WhoAmIApi:
            HandleFromRequest<AxumWhoAmIRequest, ResponseToJson<UseBasicAuth<HandleWhoAmI<WhoAmIRequest>>>>,
        @app.finance.MoneyTransferrerComponent: NoTransferToSelf<UseMockedApp>,
    }
}
```

The direct entry and the loop do not overlap, because the loop covers only the markers
`DefaultApiHandlers` binds. The probe's context joined its own namespace, `ConstNamespace`, from
[swapping the backend](swapping-the-backend.md), rather than `MockNamespace`. The route is added by calling `add_route` on the router directly, since `CanAddMainApiRoutes`
lists only the crate's own two endpoints, and the `Send` impl is written for the new context.

## Public material derived from this

"The payoff" section of the crate's own README, whose summary of this change ("adding a handler
provider and one line to `DefaultApiHandlers`") names two of the six pieces.
