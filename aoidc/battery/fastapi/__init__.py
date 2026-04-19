try:
    import fastapi
except ImportError:
    raise ImportError(
        "FastAPI is required for fastapi batteries."  # ...
        "Please install it with: pip install aoidc[fastapi]",
    ) from None

from collections.abc import Sequence
from logging import getLogger

import joserfc.errors
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from aoidc.errors import TokenValidationError
from aoidc.oauth2.rfc_7591_dynamic_client.enums import GrantTypes
from aoidc.oidc.discovery.metadata import Metadata
from aoidc.oidc.models import GenericIDToken
from aoidc.oidc.oidc import BaseOIDCClient
from fastapi.openapi import models as openapi_models
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param

logger = getLogger("aoidc.battery.fastapi")


class OpenIdConnectBetter[O: BaseOIDCClient, T: GenericIDToken](SecurityBase):
    """
    ... # TODO: ...
    """

    oidc: O
    scopes: Sequence[str]
    token_cls: type[T]
    description: str | None

    __initialized: bool = False

    def __init__(
        self,
        *,
        oidc: O,
        scopes: Sequence[str] = ("openid",),
        token_cls: type[T] = GenericIDToken,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        self.oidc = oidc
        self.scopes = scopes
        self.token_cls = token_cls
        self.description = description

        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

        # here we have a blue-and-red functions problem.
        # to define this model properly we need to call init
        # but without this model swagger ui will not work
        # so... ewww. TODO: think, how to make this better.
        self.model = openapi_models.OAuth2(
            description=f"UNINITIALIZED {self.description}",
            flows=openapi_models.OAuthFlows(),
        )

    async def init(self) -> None:
        """
        Setups all the OIDC things, requests .well-known thing and etc and etc.

        You can call it by youself, or it will be called automatically on first request.
        """

        if self.__initialized:
            return

        await self.oidc.init()

        meta: Metadata = self.oidc.metadata

        flows = openapi_models.OAuthFlows()
        if GrantTypes.AUTHORIZATION_CODE in meta.grant_types_supported:
            flows.authorizationCode = openapi_models.OAuthFlowAuthorizationCode(
                authorizationUrl=str(meta.authorization_endpoint),
                tokenUrl=str(meta.token_endpoint),
                scopes=dict.fromkeys(self.scopes, ""),
                # refreshUrl=str(meta) # TODO: what?)
            )

        if GrantTypes.CLIENT_CREDENTIALS in meta.grant_types_supported:
            flows.clientCredentials = openapi_models.OAuthFlowClientCredentials(
                tokenUrl=str(meta.token_endpoint),
                scopes=dict.fromkeys(self.scopes, ""),
            )

        if GrantTypes.PASSWORD in meta.grant_types_supported:
            flows.password = openapi_models.OAuthFlowPassword(
                tokenUrl=str(meta.token_endpoint),
                scopes=dict.fromkeys(self.scopes, ""),
            )

        if GrantTypes.IMPLICIT in meta.grant_types_supported:
            flows.implicit = openapi_models.OAuthFlowImplicit(
                authorizationUrl=str(meta.authorization_endpoint),
                scopes=dict.fromkeys(self.scopes, ""),
            )

        self.model = openapi_models.OAuth2(description=self.description, flows=flows)

        self.__initialized = True

    def make_not_authenticated_error(self) -> HTTPException:
        return HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def resolve_token(self, request: Request) -> T:
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise ValueError("No header value")

        params = get_authorization_scheme_param(authorization_header_value=authorization)
        if params[0].lower() != "bearer":
            raise ValueError("No bearer in header")

        id_token = await self.oidc.validate_id_token(
            params[1],
            token_cls=self.token_cls,
        )

        return id_token

    async def __call__(self, request: Request) -> T | None:
        await self.init()

        try:
            token = await self.resolve_token(request)
        except (joserfc.errors.JoseError, TokenValidationError, ValueError) as ex:
            logger.error(
                "Token validation error",
                extra={"url": request.url},
                exc_info=True,
            )

            if self.auto_error:
                raise self.make_not_authenticated_error() from ex
            return None

        return token
