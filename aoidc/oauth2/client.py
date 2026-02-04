from collections.abc import Mapping, Sequence

from httpx import URL, AsyncClient, BasicAuth
from joserfc.jwk import KeySet
from pydantic import AnyUrl

from aoidc import __version__
from aoidc.errors import GenericOAuthError
from aoidc.oidc.discovery import MetadataResolver
from aoidc.utils import transform_url

from .enums import ResponseType
from .rfc_6749_oauth.models import TokenResponse
from .rfc_7591_dynamic_client.enums import GrantTypes
from .rfc_8414_server_metadata.metadata import Metadata
from .rfc_8414_server_metadata.resolver import BaseMetadataResolver


class BaseOAuth2Client[T: TokenResponse, M: Metadata, MR: BaseMetadataResolver]:
    _client: AsyncClient

    discovery_endpoint: URL

    CLIENT_ID: str | None = None
    CLIENT_SECRET: str | None = None

    metadata: M
    keyset: KeySet | None = None

    pass_client_secret_in_body: bool = False
    """
    Pass client_secret in POST body instead of HTTP Basic Auth

    There are two ways to pass client_secret to auth server: http basic auth and post form params
    HTTP basic auth is MUST be supported, while the request body way is MAY be supported...

    However this is the most way I seen ever, so implement this, but behind a flag.
    https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1
    """

    @classmethod
    def meta_resolver(cls) -> type[MR]:
        raise NotImplementedError

    @classmethod
    def token_type(cls) -> type[T]:
        raise NotImplementedError

    def __init__(
        self,
        /,
        discovery_endpoint: str | AnyUrl | URL,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        client: AsyncClient | None = None,
    ) -> None:
        self._client = client or AsyncClient()
        self._client.headers["User-Agent"] = f"aoidc/{__version__}"
        self._client.follow_redirects = False  # TODO: check, is this a good idea...

        if isinstance(discovery_endpoint, AnyUrl):
            self.discovery_endpoint = transform_url(discovery_endpoint)
        else:
            self.discovery_endpoint = URL(discovery_endpoint)

        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret

    async def init(self) -> None:
        await self.resolve_metadata()

    async def resolve_metadata(self) -> None:
        self.metadata = await self.meta_resolver().resolve_metadata(
            self._client,
            self.discovery_endpoint,
            # TODO: whitelist pass
        )

        if self.metadata.jwks_uri:
            jwks_resp = await self._client.get(str(self.metadata.jwks_uri))
            jwks_resp.raise_for_status()
            self.keyset = KeySet.import_key_set(jwks_resp.json())

    async def authorization_code_flow_start(
        self,
        /,
        *,
        redirect_uri: str | AnyUrl | URL | None,
        scopes: Sequence[str] = (),
        # response_types: Sequence[ResponseType] = (ResponseType.CODE,),
        state: str | None = None,
        extra_data: Mapping[str, str] = {},
    ) -> URL:
        """
        Create URL to pass to resource owner's user-agent.

        redirect_uri can be None, but you have to explicitly pass it.
        """

        if not self.metadata.authorization_endpoint:
            raise GenericOAuthError("Metadata does not contain authorization_endpoint")

        # this check is from authorization_code_flow_continue, but if auth server can't pass this check here
        # auth server will not pass this check in future authorization_code_flow_continue
        # so fail fast
        if not self.metadata.token_endpoint:
            raise GenericOAuthError("Metadata does not contain token_endpoint")

        # WTF: should it be done this way? :D
        response_types = (ResponseType.CODE,)
        if ResponseType.CODE not in response_types:
            raise GenericOAuthError("`code` does not not provided as response type for authorization code flow")

        response_types = tuple(sorted(response_types))
        if response_types not in self.metadata.response_types_supported:
            raise GenericOAuthError(f"Response type tuple {response_types} is unsupported by server")

        client_id = self.CLIENT_ID
        if client_id is None:
            raise GenericOAuthError("client_id is None")

        # TODO: validate redirect uri

        redirect_uri = str(redirect_uri)

        url = transform_url(self.metadata.authorization_endpoint)
        params = {
            "scope": " ".join(scopes),
            "response_type": " ".join(response_types),
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,  # TODO: state local management? maybe...
        }
        params.update(extra_data)
        return url.copy_merge_params(params)

    async def authorization_code_flow_continue(
        self,
        /,
        *,
        code: str,
        redirect_uri: str | AnyUrl | URL | None = None,
        state: str | None = None,
        extra_data: Mapping[str, str] = {},
    ) -> T:
        """
        Continue authorization code flow.

        Your app, not this library is responsible for `state` validation and checks
        """

        if not self.metadata.token_endpoint:
            raise GenericOAuthError("Metadata does not contain token_endpoint")

        client_id = self.CLIENT_ID
        if client_id is None:
            raise GenericOAuthError("client_id is None")

        client_secret = self.CLIENT_SECRET
        if client_secret is None:
            raise GenericOAuthError("client_secret is None")

        basic_data = {
            "grant_type": GrantTypes.AUTHORIZATION_CODE,
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
        }
        basic_data.update(extra_data)

        if not self.pass_client_secret_in_body:
            token_response = await self._client.post(
                transform_url(self.metadata.token_endpoint),
                data=basic_data,
                auth=BasicAuth(
                    username=client_id,
                    password=client_secret,
                ),
            )
        else:
            if client_secret in basic_data:
                raise GenericOAuthError("`client_secret` already in basic data. You doing something wrong.")
            token_response = await self._client.post(
                transform_url(self.metadata.token_endpoint),
                data=basic_data | {"client_secret": client_secret},
            )

        token_response.raise_for_status()
        token = self.token_type().model_validate_json(token_response.text)
        return token


class OAuth2Client(BaseOAuth2Client[TokenResponse, Metadata, BaseMetadataResolver]):
    @classmethod
    def meta_resolver(cls) -> type[MetadataResolver]:
        return MetadataResolver

    @classmethod
    def token_type(cls) -> type[TokenResponse]:
        return TokenResponse
