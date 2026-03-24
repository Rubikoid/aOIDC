# ruff: noqa: S105
from enum import StrEnum
from typing import Annotated, Any

from pydantic import BeforeValidator

from aoidc.utils import show_unknown_enum_waring

"""
Taken from https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml as of 11.03.2025

Defined here, instead of RFCs, because of extending among many RFCs, and I don't want to define state for
each RFC
"""


class ResponseType(StrEnum):
    """
    https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml#endpoint.

    Несмотря на то, что в стандарте написаны конкретные комбинации,
    некоторые IdP (например, ory hydra) возвращает конструкции вида `token id_token` и `token id_token code`
    Тогда как в стандарте написаны `token id_token code`

    Хотя вообще-то в https://datatracker.ietf.org/doc/html/rfc6749#section-3.1.1 про это написано, что
    порядок не важен
    Поэтому моя реализация этого вопроса корректна
    """

    NONE = "none"

    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"

    _UNKNOWN = "_UNKNOWN"

    @classmethod
    def _missing_(cls, value):
        show_unknown_enum_waring(cls.__name__, value)
        return cls._UNKNOWN


def reconstruct_response_types(
    data: Any,  # noqa: ANN401
) -> set[tuple[ResponseType, ...]]:
    if not isinstance(data, list) or any(not isinstance(i, str) for i in data):
        raise ValueError("Invalid ResponseTypes input")

    result: set[tuple[ResponseType, ...]] = set()
    for entry in data:
        responses: list[str] = entry.split(" ")
        result_part = {ResponseType(i) for i in responses}
        result.add(tuple(sorted(result_part)))

    return result


ResponseTypes = Annotated[
    set[tuple[ResponseType, ...]],
    BeforeValidator(reconstruct_response_types, json_schema_input_type=list[str]),
]


class AccessTokenTypes(StrEnum):
    """
    https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml#token-types.
    """

    BEARER = "Bearer"

    DPoP = "DPoP"
    N_A = "N_A"
    PoP = "PoP"

    _UNKNOWN = "_UNKNOWN"

    @classmethod
    def _missing_(cls, value):
        # because `introspection_endpoint_auth_methods_supported` in Metadata is
        # set[TokenEndpointAuthMetod | AccessTokenTypes]
        # ignore them here
        # so it will not spam warnings
        if value in TokenEndpointAuthMetod:
            return None

        show_unknown_enum_waring(cls.__name__, value)
        return cls._UNKNOWN


class TokenEndpointAuthMetod(StrEnum):
    """
    https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml#token-endpoint-auth-method.
    """

    NONE = "none"
    CLIENT_SECRET_POST = "client_secret_post"
    CLIENT_SECRET_BASIC = "client_secret_basic"

    CLIENT_SECRET_JWT = "client_secret_jwt"
    PRIVATE_KEY_JWT = "private_key_jwt"

    TLS_CLIENT_AUTH = "tls_client_auth"
    SELF_SIGNED_TLS_CLIENT_AUTH = "self_signed_tls_client_auth"

    _UNKNOWN = "_UNKNOWN"

    @classmethod
    def _missing_(cls, value):
        # because `introspection_endpoint_auth_methods_supported` in Metadata is
        # set[TokenEndpointAuthMetod | AccessTokenTypes]
        # ignore them here
        # so it will not spam warnings
        if value in AccessTokenTypes:
            return None

        show_unknown_enum_waring(cls.__name__, value)
        return cls._UNKNOWN


class CodeChallendeMethods(StrEnum):
    """
    https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml#pkce-code-challenge-method.
    """

    PLAIN = "plain"
    S256 = "S256"

    _UNKNOWN = "_UNKNOWN"

    @classmethod
    def _missing_(cls, value):
        show_unknown_enum_waring(cls.__name__, value)
        return cls._UNKNOWN
