from typing import NewType
from pydantic import BaseModel, ConfigDict

from aoidc.oauth2.enums import AccessTokenTypes
from aoidc.utils import UTCTime

AccessToken = NewType("AccessToken", str)


class TokenResponse(BaseModel):
    """
    Token response model, as defined in https://datatracker.ietf.org/doc/html/rfc6749#section-5.1
    """

    access_token: AccessToken
    token_type: AccessTokenTypes

    expires_in: UTCTime | None = None

    refresh_token: str | None = None
    scope: str | None = None

    model_config = ConfigDict(
        extra="allow",
    )


class TokenErrorResponse(BaseModel):
    """
    Token error response model, as defined in https://datatracker.ietf.org/doc/html/rfc6749#section-5.2
    TODO: do.
    """
