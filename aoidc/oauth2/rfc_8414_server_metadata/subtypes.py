from typing import Annotated, NewType
from urllib.parse import urlparse

from pydantic import AfterValidator, AnyUrl, UrlConstraints
from pydantic_core import Url

from aoidc.config import settings
from aoidc.errors import GenericValidationError

Issuer = NewType("Issuer", AnyUrl)


def generic_endpoint_validator(endpoint: AnyUrl) -> AnyUrl:
    """
    https check is not debug
    """  # noqa: D401

    if endpoint.scheme != "https" and not settings.DEBUG:
        raise GenericValidationError("Invalid endpoint")

    return endpoint


def issuer_validator(issuer: Issuer) -> Issuer:
    """
    REQUIRED.  The authorization server's issuer identifier, which is
    a URL that uses the "https" scheme and has no query or fragment
    components.  Authorization server metadata is published at a
    location that is ".well-known" according to RFC 5785 [RFC5785]
    derived from this issuer identifier, as described in Section 3.
    The issuer identifier is used to prevent authorization server mix-
    up attacks, as described in "OAuth 2.0 Mix-Up Mitigation"
    [MIX-UP].
    """  # noqa: D401 # wtf ruff

    if (issuer.scheme != "https" and not settings.DEBUG) or issuer.query or issuer.fragment:
        raise GenericValidationError("Invalid issuer")

    return issuer


def authorization_endpoint_validator(endpoint: AnyUrl) -> AnyUrl:
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
    """  # noqa: D401

    if (endpoint.scheme != "https" and not settings.DEBUG) or endpoint.fragment:
        raise GenericValidationError("Invalid endpoint")

    return endpoint


def token_endpoint_validator(endpoint: AnyUrl) -> AnyUrl:
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
    """  # noqa: D401

    if (endpoint.scheme != "https" and not settings.DEBUG) or endpoint.fragment:
        raise GenericValidationError("Invalid endpoint")

    return endpoint


ValidatedGenericEndpoint = Annotated[Issuer, AfterValidator(generic_endpoint_validator)]

ValidatedIssuer = Annotated[Issuer, AfterValidator(issuer_validator)]
ValidatedAuthorizationEndpoint = Annotated[AnyUrl, AfterValidator(authorization_endpoint_validator)]
ValidatedTokenEndpoint = Annotated[AnyUrl, AfterValidator(token_endpoint_validator)]
