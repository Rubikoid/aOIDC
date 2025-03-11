from typing import NewType, Self
from urllib.parse import urlparse

from msgspec import Struct
from pydantic import BaseModel, model_validator
from pydantic.networks import AnyUrl

from aoidc.errors import GenericValidationError
from aoidc.oauth2.rfc_7591_dynamic_client.enums import GrantTypes, ResponseTypes

from .subtypes import ValidatedAuthorizationEndpoint, ValidatedGenericEndpoint, ValidatedIssuer, ValidatedTokenEndpoint
from .enum import ResponseModes


class Metadata(BaseModel):
    """
    Metadata list, as defined in https://datatracker.ietf.org/doc/html/rfc8414#section-2
    """

    issuer: ValidatedIssuer
    """The authorization server's issuer identifier"""

    authorization_endpoint: ValidatedAuthorizationEndpoint | None = None
    """
    URL of the authorization server's authorization endpoint
    [RFC6749].  This is REQUIRED unless no grant types are supported
    that use the authorization endpoint.
    """

    token_endpoint: ValidatedTokenEndpoint | None = None
    """
    URL of the authorization server's token endpoint [RFC6749].  This
    is REQUIRED unless only the implicit grant type is supported.
    """

    jwks_uri: ValidatedGenericEndpoint | None = None
    """
    OPTIONAL.  URL of the authorization server's JWK Set [JWK]
    document.  The referenced document contains the signing key(s) the
    client uses to validate signatures from the authorization server.
    This URL MUST use the "https" scheme.  The JWK Set MAY also
    contain the server's encryption key or keys, which are used by
    clients to encrypt requests to the server.  When both signing and
    encryption keys are made available, a "use" (public key use)
    parameter value is REQUIRED for all keys in the referenced JWK Set
    to indicate each key's intended usage.
    """

    registration_endpoint: ValidatedGenericEndpoint | None = None
    """
    URL of the authorization server's OAuth 2.0 Dynamic Client Registration endpoint [RFC7591].

    The client registration endpoint is an OAuth 2.0 endpoint defined in
    this document that is designed to allow a client to be registered
    with the authorization server.

    https://datatracker.ietf.org/doc/html/rfc7591#section-3
    """

    scopes_supported: set[str] = set()
    """
    JSON array containing a list of the OAuth 2.0
    [RFC6749] "scope" values that this authorization server supports.
    Servers MAY choose not to advertise some supported scope values
    even when this parameter is used.
    """

    response_types_supported: set[ResponseTypes]
    """
    JSON array containing a list of the OAuth 2.0
    "response_type" values that this authorization server supports.
    The array values used are the same as those used with the
    "response_types" parameter defined by "OAuth 2.0 Dynamic Client
    Registration Protocol" [RFC7591].
    """

    response_modes_supported: set[ResponseModes] = {ResponseModes.query, ResponseModes.fragment}
    """
    OPTIONAL.  JSON array containing a list of the OAuth 2.0
    "response_mode" values that this authorization server supports, as
    specified in "OAuth 2.0 Multiple Response Type Encoding Practices"
    [OAuth.Responses].  If omitted, the default is "["query",
    "fragment"]".  The response mode value "form_post" is also defined
    in "OAuth 2.0 Form Post Response Mode" [OAuth.Post].
    """

    grant_types_supported: set[GrantTypes] = {GrantTypes.AUTHORIZATION_CODE, GrantTypes.IMPLICIT}
    """
    JSON array containing a list of the OAuth 2.0 grant
    type values that this authorization server supports.
    """

    @model_validator(mode="after")
    def validate(self) -> Self:
        # auth endpoint required for the next grants:
        # AUTHORIZATION_CODE
        # IMPLICIT
        # ~PASSWORD~
        # ~CLIENT_CREDENTIALS~
        # ~REFRESH_TOKEN~
        # ~JWT_BEARER~
        # ~SAML2_BEARER~
        _check = {GrantTypes.AUTHORIZATION_CODE, GrantTypes.IMPLICIT}
        if not self.authorization_endpoint and len(_check & self.grant_types_supported) != 0:
            raise GenericValidationError("No authorization_endpoint defined")

        # token endpoint required for the next grants:
        # AUTHORIZATION_CODE
        # ~IMPLICIT~
        # PASSWORD
        # CLIENT_CREDENTIALS
        # REFRESH_TOKEN
        # JWT_BEARER
        # SAML2_BEARER
        _check = {
            GrantTypes.AUTHORIZATION_CODE,
            GrantTypes.PASSWORD,
            GrantTypes.CLIENT_CREDENTIALS,
            GrantTypes.REFRESH_TOKEN,
            GrantTypes.JWT_BEARER,
            GrantTypes.SAML2_BEARER,
        }
        if not self.token_endpoint and len(_check & self.grant_types_supported) != 0:
            raise GenericValidationError("No token_endpoint defined")

        return self
