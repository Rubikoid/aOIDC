# ruff: noqa: D401
from typing import Annotated, NewType
from urllib.parse import urlparse

from pydantic import AfterValidator, AnyUrl, UrlConstraints, ValidationInfo
from pydantic_core import Url

from aoidc.config import settings
from aoidc.errors import GenericValidationError
from aoidc.jwt import JsonWebAlgos
from aoidc.oauth2.context import ValidationContext
from aoidc.utils import is_same_origin

Issuer = NewType("Issuer", AnyUrl)


def check_for_allowned_urls(endpoint: AnyUrl, info: ValidationInfo) -> None:
    # TODO: Я не нашел явных требований или ограничений в стандартах на хосты возвращаемых урлов
    # Поэтому тут, для защиты от SSRF, делаем вот такой костыль
    # адреса, возвращаемые в .well-known должны вести либо на такой же Origin, как и сам .well-known
    # либо быть в отдельном явно прописанном списке избранных адресов

    if settings.ALLOW_ALL_URLS:
        return

    ctx = info.context
    if not isinstance(ctx, ValidationContext):
        return

    if is_same_origin(endpoint, ctx.origin_url):
        return

    if any(is_same_origin(endpoint, i) for i in ctx.allowed_urls):
        return

    raise GenericValidationError(f"URL {endpoint} is not allowned")


def generic_endpoint_validator(endpoint: AnyUrl, info: ValidationInfo) -> AnyUrl:
    """
    https check is not debug
    """

    if endpoint.scheme != "https" and not settings.ALLOW_HTTP:
        raise GenericValidationError("Invalid endpoint")

    check_for_allowned_urls(endpoint, info)

    return endpoint


def issuer_validator(issuer: Issuer, info: ValidationInfo) -> Issuer:
    """
    REQUIRED.  The authorization server's issuer identifier, which is
    a URL that uses the "https" scheme and has no query or fragment
    components.  Authorization server metadata is published at a
    location that is ".well-known" according to RFC 5785 [RFC5785]
    derived from this issuer identifier, as described in Section 3.
    The issuer identifier is used to prevent authorization server mix-
    up attacks, as described in "OAuth 2.0 Mix-Up Mitigation"
    [MIX-UP].
    """

    if (issuer.scheme != "https" and not settings.ALLOW_HTTP) or issuer.query or issuer.fragment:
        raise GenericValidationError("Invalid issuer")

    check_for_allowned_urls(issuer, info)

    return issuer


def authorization_endpoint_validator(endpoint: AnyUrl, info: ValidationInfo) -> AnyUrl:
    """
    The endpoint URI MAY include an "application/x-www-form-urlencoded"
    formatted (per Appendix B) query component ([RFC3986] Section 3.4),
    which MUST be retained when adding additional query parameters.  The
    endpoint URI MUST NOT include a fragment component.

    Since requests to the authorization endpoint result in user
    authentication and the transmission of clear-text credentials (in the
    HTTP response), the authorization server MUST require the use of TLS
    as described in Section 1.6 when sending requests to the
    authorization endpoint.

    https://datatracker.ietf.org/doc/html/rfc6749#section-3.1
    """

    if (endpoint.scheme != "https" and not settings.ALLOW_HTTP) or endpoint.fragment:
        raise GenericValidationError("Invalid endpoint")

    check_for_allowned_urls(endpoint, info)

    return endpoint


def token_endpoint_validator(endpoint: AnyUrl, info: ValidationInfo) -> AnyUrl:
    """
    The endpoint URI MAY include an "application/x-www-form-urlencoded"
    formatted (per Appendix B) query component ([RFC3986] Section 3.4),
    which MUST be retained when adding additional query parameters.  The
    endpoint URI MUST NOT include a fragment component.

    Since requests to the token endpoint result in the transmission of
    clear-text credentials (in the HTTP request and response), the
    authorization server MUST require the use of TLS as described in
    Section 1.6 when sending requests to the token endpoint.

    https://datatracker.ietf.org/doc/html/rfc6749#section-3.1
    """

    if (endpoint.scheme != "https" and not settings.ALLOW_HTTP) or endpoint.fragment:
        raise GenericValidationError("Invalid endpoint")

    check_for_allowned_urls(endpoint, info)

    return endpoint


def json_web_algos_validator(algos: set[JsonWebAlgos]) -> set[JsonWebAlgos]:
    """
    OPTIONAL.  JSON array containing a list of the JWS signing
    algorithms ("alg" values) supported by the token endpoint for the
    signature on the JWT [JWT] used to authenticate the client at the
    token endpoint for the "private_key_jwt" and "client_secret_jwt"
    authentication methods.  This metadata entry MUST be present if
    either of these authentication methods are specified in the
    "token_endpoint_auth_methods_supported" entry.  No default
    algorithms are implied if this entry is omitted.  Servers SHOULD
    support "RS256".  The value "none" MUST NOT be used.
    """

    if JsonWebAlgos.RS256 not in algos:
        raise GenericValidationError("RS256 is not supported")

    if not settings.ALLOW_ALG_NONE and JsonWebAlgos.NONE in algos:
        raise GenericValidationError("NONE alg is supported")

    return algos


ValidatedGenericEndpoint = Annotated[Issuer, AfterValidator(generic_endpoint_validator)]

ValidatedIssuer = Annotated[Issuer, AfterValidator(issuer_validator)]
ValidatedAuthorizationEndpoint = Annotated[AnyUrl, AfterValidator(authorization_endpoint_validator)]
ValidatedTokenEndpoint = Annotated[AnyUrl, AfterValidator(token_endpoint_validator)]
ValidatedJsonWebAlgos = Annotated[set[JsonWebAlgos], AfterValidator(json_web_algos_validator)]
