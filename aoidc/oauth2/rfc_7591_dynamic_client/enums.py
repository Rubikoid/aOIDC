# ruff: noqa: S105
from enum import StrEnum


class GrantTypes(StrEnum):
    AUTHORIZATION_CODE = "authorization_code"
    IMPLICIT = "implicit"

    PASSWORD = "password"
    CLIENT_CREDENTIALS = "client_credentials"

    REFRESH_TOKEN = "refresh_token"

    JWT_BEARER = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    SAML2_BEARER = "urn:ietf:params:oauth:grant-type:saml2-bearer"
    DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"
