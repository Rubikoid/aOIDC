from collections.abc import Sequence

from httpx import URL, AsyncClient
from joserfc.jwk import KeySet
from pydantic import AnyUrl

from aoidc import __version__
from aoidc.errors import GenericOIDCError
from aoidc.utils import transform_url

from ..oauth2.enums import ResponseType
from .discovery import resolve_metadata
from .discovery.metadata import Metadata


class OIDCClient:
    _client: AsyncClient

    CLIENT_ID: str | None = None
    CLIENT_SECRET: str | None = None

    discovery_endpoint: URL

    metadata: Metadata
    keyset: KeySet | None = None

    def __init__(
        self,
        discovery_endpoint: str | AnyUrl | URL,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        client: AsyncClient | None = None,
    ) -> None:
        self._client = client or AsyncClient()
        self._client.headers["User-Agent"] = f"aoidc/{__version__}"

        if isinstance(discovery_endpoint, AnyUrl):
            self.discovery_endpoint = transform_url(discovery_endpoint)
        else:
            self.discovery_endpoint = URL(discovery_endpoint)

        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret

    async def init(self) -> None:
        await self.resolve_metadata()

    async def resolve_metadata(self) -> None:
        self.metadata = await resolve_metadata(
            self._client,
            self.discovery_endpoint,
        )

        if self.metadata.jwks_uri:
            jwks_resp = await self._client.get(str(self.metadata.jwks_uri))
            self.keyset = KeySet.import_key_set(jwks_resp.json())

    async def validate_token(self) -> None: ...

    async def start_authorization_code_flow(
        self,
        *,
        redirect_uri: str | AnyUrl | URL,
        scopes: set[str] = {"openid"},
        response_types: tuple[ResponseType, ...] = (ResponseType.CODE,),
        client_id: str | None = None,
        state: str | None = None,
        # TODO: other params
    ) -> URL:
        if not self.metadata.authorization_endpoint:
            raise GenericOIDCError("Metadata does not contain authorization_endpoint")

        if "openid" not in scopes:
            raise GenericOIDCError("No `openid` scope defined")

        response_types = tuple(sorted(response_types))
        if response_types not in self.metadata.response_types_supported:
            raise GenericOIDCError(f"Response type tuple {response_types} is unsupported by server")

        client_id = client_id or self.CLIENT_ID
        if client_id is None:
            raise GenericOIDCError("client_id is None")

        # TODO: check for scheme

        redirect_uri = str(redirect_uri)

        url = transform_url(self.metadata.authorization_endpoint)
        return url.copy_merge_params(
            {
                "scope": " ".join(scopes),
                "response_type": " ".join(response_types),
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "state": state,  # TODO: state
            }
        )
