# ruff: noqa: S105
from enum import StrEnum

from aoidc.utils import show_unknown_enum_waring


class GrantTypes(StrEnum):
    AUTHORIZATION_CODE = "authorization_code"
    IMPLICIT = "implicit"

    PASSWORD = "password"
    CLIENT_CREDENTIALS = "client_credentials"

    REFRESH_TOKEN = "refresh_token"

    JWT_BEARER = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    SAML2_BEARER = "urn:ietf:params:oauth:grant-type:saml2-bearer"
    DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"

    # keycloak
    CIBA = "urn:openid:params:grant-type:ciba"
    TOKEN_EXCHANGE = "urn:ietf:params:oauth:grant-type:token-exchange"
    UMA_TICKET = "urn:ietf:params:oauth:grant-type:uma-ticket"

    _UNKNOWN = "_UNKNOWN"

    @classmethod
    def _missing_(cls, value):
        show_unknown_enum_waring(cls.__name__, value)
        return cls._UNKNOWN
