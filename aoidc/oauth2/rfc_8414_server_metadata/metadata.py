from typing import NewType, Self
from urllib.parse import urlparse

from msgspec import Struct
from pydantic import BaseModel, model_validator
from pydantic.networks import AnyUrl

from aoidc.errors import GenericValidationError
from aoidc.oauth2.enums import AccessTokenTypes, CodeChallendeMethods, ResponseTypes, TokenEndpointAuthMetod
from aoidc.oauth2.rfc_7591_dynamic_client.enums import GrantTypes

from .enum import ResponseModes
from .subtypes import (
    ValidatedAuthorizationEndpoint,
    ValidatedGenericEndpoint,
    ValidatedIssuer,
    ValidatedJsonWebAlgos,
    ValidatedTokenEndpoint,
)


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

    response_types_supported: ResponseTypes
    """
    JSON array containing a list of the OAuth 2.0
    "response_type" values that this authorization server supports.
    The array values used are the same as those used with the
    "response_types" parameter defined by "OAuth 2.0 Dynamic Client
    Registration Protocol" [RFC7591].
    """

    response_modes_supported: set[ResponseModes] = {ResponseModes.QUERY, ResponseModes.FRAGMENT}
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

    token_endpoint_auth_methods_supported: set[TokenEndpointAuthMetod] = {TokenEndpointAuthMetod.CLIENT_SECRET_BASIC}
    """
    OPTIONAL.  JSON array containing a list of client authentication
    methods supported by this token endpoint.  Client authentication
    method values are used in the "token_endpoint_auth_method"
    parameter defined in Section 2 of [RFC7591].  If omitted, the
    default is "client_secret_basic" -- the HTTP Basic Authentication
    Scheme specified in Section 2.3.1 of OAuth 2.0 [RFC6749].
    """

    token_endpoint_auth_signing_alg_values_supported: ValidatedJsonWebAlgos = set()
    """
    OPTIONAL.  JSON array containing a list of the JWS signing
    algorithms ("alg" values) supported by the token endpoint for the
    signature on the JWT [JWT] used to authenticate the client at the
    token endpoint for the "private_key_jwt" and "client_secret_jwt"
    authentication methods. This metadata entry MUST be present if
    either of these authentication methods are specified in the
    "token_endpoint_auth_methods_supported" entry.
    """

    service_documentation: AnyUrl | None = None
    """
    OPTIONAL.  URL of a page containing human-readable information
    that developers might want or need to know when using the
    authorization server.  In particular, if the authorization server
    does not support Dynamic Client Registration, then information on
    how to register clients needs to be provided in this
    documentation.
    """

    ui_locales_supported: set[str] = set()
    """
    OPTIONAL.  Languages and scripts supported for the user interface,
    represented as a JSON array of language tag values from BCP 47
    [RFC5646].  If omitted, the set of supported languages and scripts
    is unspecified.

    TODO: make here proper type 
    """

    op_policy_uri: AnyUrl | None = None
    """
    OPTIONAL.  URL that the authorization server provides to the
    person registering the client to read about the authorization
    server's requirements on how the client can use the data provided
    by the authorization server.  The registration process SHOULD
    display this URL to the person registering the client if it is
    given.  As described in Section 5, despite the identifier
    "op_policy_uri" appearing to be OpenID-specific, its usage in this
    specification is actually referring to a general OAuth 2.0 feature
    that is not specific to OpenID Connect.
    """

    op_tos_uri: AnyUrl | None = None
    """
    OPTIONAL.  URL that the authorization server provides to the
    person registering the client to read about the authorization
    server's terms of service.  The registration process SHOULD
    display this URL to the person registering the client if it is
    given.  As described in Section 5, despite the identifier
    "op_tos_uri", appearing to be OpenID-specific, its usage in this
    specification is actually referring to a general OAuth 2.0 feature
    that is not specific to OpenID Connect.
    """

    revocation_endpoint: ValidatedAuthorizationEndpoint | None = None
    """
    OPTIONAL.  URL of the authorization server's OAuth 2.0 revocation
    endpoint [RFC7009].

    The client requests the revocation of a particular token by making an
    HTTP POST request to the token revocation endpoint URL.  This URL
    MUST conform to the rules given in [RFC6749], Section 3.1.  Clients
    MUST verify that the URL is an HTTPS URL.
    """

    revocation_endpoint_auth_methods_supported: set[TokenEndpointAuthMetod] = {
        TokenEndpointAuthMetod.CLIENT_SECRET_BASIC,
    }
    """
    OPTIONAL.  JSON array containing a list of client authentication
    methods supported by this revocation endpoint.  The valid client
    authentication method values are those registered in the IANA
    "OAuth Token Endpoint Authentication Methods" registry
    [IANA.OAuth.Parameters].  If omitted, the default is
    "client_secret_basic" -- the HTTP Basic Authentication Scheme
    specified in Section 2.3.1 of OAuth 2.0 [RFC6749].
    """

    revocation_endpoint_auth_signing_alg_values_supported: ValidatedJsonWebAlgos = set()
    """
    OPTIONAL.  JSON array containing a list of the JWS signing
    algorithms ("alg" values) supported by the revocation endpoint for
    the signature on the JWT [JWT] used to authenticate the client at
    the revocation endpoint for the "private_key_jwt" and
    "client_secret_jwt" authentication methods.  This metadata entry
    MUST be present if either of these authentication methods are
    specified in the "revocation_endpoint_auth_methods_supported"
    entry.  No default algorithms are implied if this entry is
    omitted. The value "none" MUST NOT be used.
    """

    introspection_endpoint: ValidatedGenericEndpoint | None = None
    """
    OPTIONAL.  URL of the authorization server's OAuth 2.0
    introspection endpoint [RFC7662].

    https://datatracker.ietf.org/doc/html/rfc7662#section-2
    """

    introspection_endpoint_auth_methods_supported: set[TokenEndpointAuthMetod | AccessTokenTypes] = set()
    """
    OPTIONAL.  JSON array containing a list of client authentication
    methods supported by this introspection endpoint.  The valid
    client authentication method values are those registered in the
    IANA "OAuth Token Endpoint Authentication Methods" registry
    [IANA.OAuth.Parameters] or those registered in the IANA "OAuth
    Access Token Types" registry [IANA.OAuth.Parameters].  (These
    values are and will remain distinct, due to Section 7.2.)  If
    omitted, the set of supported authentication methods MUST be
    determined by other means.
    """

    introspection_endpoint_auth_signing_alg_values_supported: ValidatedJsonWebAlgos = set()
    """
    OPTIONAL.  JSON array containing a list of the JWS signing
    algorithms ("alg" values) supported by the introspection endpoint
    for the signature on the JWT [JWT] used to authenticate the client
    at the introspection endpoint for the "private_key_jwt" and
    "client_secret_jwt" authentication methods.  This metadata entry
    MUST be present if either of these authentication methods are
    specified in the "introspection_endpoint_auth_methods_supported"
    entry.  No default algorithms are implied if this entry is
    omitted.  The value "none" MUST NOT be used.
    """

    code_challenge_methods_supported: set[CodeChallendeMethods] = set()
    """
    OPTIONAL.  JSON array containing a list of Proof Key for Code
    Exchange (PKCE) [RFC7636] code challenge methods supported by this
    authorization server.  Code challenge method values are used in
    the "code_challenge_method" parameter defined in Section 4.3 of
    [RFC7636].  The valid code challenge method values are those
    registered in the IANA "PKCE Code Challenge Methods" registry
    [IANA.OAuth.Parameters].  If omitted, the authorization server
    does not support PKCE.
    """

    @model_validator(mode="after")
    def __validate(self) -> Self:
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

        for field_part in ["token_endpoint", "revocation_endpoint", "introspection_endpoint"]:
            auth_methods_supported = getattr(self, f"{field_part}_auth_methods_supported")
            auth_signing_alg_values_supported = getattr(self, f"{field_part}_auth_signing_alg_values_supported")

            if (
                TokenEndpointAuthMetod.PRIVATE_KEY_JWT in auth_methods_supported
                or TokenEndpointAuthMetod.CLIENT_SECRET_JWT in auth_methods_supported
            ) and not auth_signing_alg_values_supported:
                raise GenericValidationError(
                    f"{field_part = }: {auth_methods_supported = } but {auth_signing_alg_values_supported = }"
                )

        return self
