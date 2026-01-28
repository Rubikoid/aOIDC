# ruff: noqa: S105
from enum import StrEnum

"""
Taken from https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml as of 11.03.2025

Defined here, instead of RFCs, because of extending among many RFCs, and I don't want to define state for 
each RFC
"""


class ResponseTypes(StrEnum):
    """
    https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml#endpoint
    """

    NONE = "none"

    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"

    CODE_AND_ID_TOKEN = "code id_token"
    CODE_AND_ID_TOKEN_AND_TOKEN = "code id_token token"
    CODE_AND_TOKEN = "code token"

    ID_TOKEN_AND_TOKEN = "id_token token"


class AccessTokenTypes(StrEnum):
    """
    https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml#token-types
    """

    BEARER = "Bearer"

    DPoP = "DPoP"
    N_A = "N_A"
    PoP = "PoP"


class TokenEndpointAuthMetod(StrEnum):
    """
    https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml#token-endpoint-auth-method
    """

    NONE = "none"
    CLIENT_SECRET_POST = "client_secret_post"
    CLIENT_SECRET_BASIC = "client_secret_basic"

    CLIENT_SECRET_JWT = "client_secret_jwt"
    PRIVATE_KEY_JWT = "private_key_jwt"

    TLS_CLIENT_AUTH = "tls_client_auth"
    SELF_SIGNED_TLS_CLIENT_AUTH = "self_signed_tls_client_auth"


class CodeChallendeMethods(StrEnum):
    """
    https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml#pkce-code-challenge-method
    """

    PLAIN = "plain"
    S256 = "S256"
