from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from aoidc.oauth2.rfc_6749_oauth.models import TokenResponse as OAuthTokenResponse
from aoidc.oauth2.rfc_8414_server_metadata.subtypes import ValidatedIssuer
from aoidc.utils import UTCTime


class GenericIDToken(BaseModel):
    """
    Implementation of https://openid.net/specs/openid-connect-core-1_0-final.html#IDToken.
    """

    iss: ValidatedIssuer
    """
    REQUIRED. Issuer Identifier for the Issuer of the response.

    The `iss` value is a case sensitive URL using the `https` scheme that contains scheme, host, and optionally,
    port number and path components and no query or fragment components.
    """

    sub: Annotated[str, Field(max_length=255)]
    """
    REQUIRED. Subject Identifier.

    A locally unique and never reassigned identifier within the Issuer for the End-User, which is intended
    to be consumed by the Client, e.g., `24400320` or `AItOawmwtWwcT0k51BayewNvutrJUqsvl6qs7A4`.

    It MUST NOT exceed 255 ASCII characters in length. The `sub` value is a case sensitive string.
    """

    aud: str | set[str]
    """
    REQUIRED. Audience(s) that this ID Token is intended for.

    It MUST contain the OAuth 2.0 `client_id` of the Relying Party as an audience value.
    It MAY also contain identifiers for other audiences.
    In the general case, the `aud` value is an array of case sensitive strings.

    In the common special case when there is one audience, the `aud` value MAY be a single case sensitive string.
    """

    exp: UTCTime
    """
    REQUIRED. Expiration time on or after which the ID Token MUST NOT be accepted for processing.

    The processing of this parameter requires that the current date/time MUST be before
    the expiration date/time listed in the value.

    Implementers MAY provide for some small leeway, usually no more than a few minutes, to account for clock skew.
    Its value is a JSON number representing the number of seconds from 1970-01-01T0:0:0Z
    as measured in UTC until the date/time.

    See RFC 3339 [RFC3339] for details regarding date/times in general and UTC in particular.
    """

    iat: UTCTime
    """
    REQUIRED. Time at which the JWT was issued.

    Its value is a JSON number representing the number of seconds from 1970-01-01T0:0:0Z
    as measured in UTC until the date/time.
    """

    auth_time: UTCTime | None = None
    """
    Time when the End-User authentication occurred.

    Its value is a JSON number representing the number of seconds from 1970-01-01T0:0:0Z
    as measured in UTC until the date/time.

    When a `max_age` request is made or when `auth_time` is requested as an Essential Claim,
    then this Claim is REQUIRED;
    otherwise, its inclusion is OPTIONAL.
    (The `auth_time` Claim semantically corresponds to the OpenID 2.0 PAPE [OpenID.PAPE] auth_time response parameter.)
    """

    nonce: str | None = None
    """
    String value used to associate a Client session with an ID Token, and to mitigate replay attacks.

    The value is passed through unmodified from the Authentication Request to the ID Token.
    If present in the ID Token, Clients MUST verify that the `nonce` Claim Value is equal to the value of the
    `nonce` parameter sent in the Authentication Request.

    If present in the Authentication Request, Authorization Servers MUST include a `nonce` Claim in the
    ID Token with the Claim Value being the `nonce` value sent in the Authentication Request.

    Authorization Servers SHOULD perform no other processing on `nonce` values used.
    The `nonce` value is a case sensitive string.
    """

    acr: str | None = None
    """
    OPTIONAL. Authentication Context Class Reference.

    String specifying an Authentication Context Class Reference value that identifies the Authentication Context Class
    that the authentication performed satisfied.

    The value "0" indicates the End-User authentication did not meet the requirements of
    ISO/IEC 29115 [ISO29115] level 1.

    Authentication using a long-lived browser cookie, for instance, is one example where the use of "level 0"
    is appropriate.

    Authentications with level 0 SHOULD NOT be used to authorize access to any resource of any monetary value.
    (This corresponds to the OpenID 2.0 PAPE [OpenID.PAPE] nist_auth_level 0.)

    An absolute URI or an RFC 6711 [RFC6711] registered name SHOULD be used as the `acr` value;
    registered names MUST NOT be used with a different meaning than that which is registered.

    Parties using this claim will need to agree upon the meanings of the values used, which may be context-specific.
    The `acr` value is a case sensitive string.
    """

    amr: set[str] | None = None
    """
    OPTIONAL. Authentication Methods References.

    JSON array of strings that are identifiers for authentication methods used in the authentication.
    For instance, values might indicate that both password and OTP authentication methods were used.
    The definition of particular values to be used in the `amr` Claim is beyond the scope of this specification.
    Parties using this claim will need to agree upon the meanings of the values used, which may be context-specific.

    The `amr` value is an array of case sensitive strings.
    """

    azp: str | None = None
    """
    OPTIONAL. Authorized party - the party to which the ID Token was issued.

    If present, it MUST contain the OAuth 2.0 Client ID of this party.
    This Claim is only needed when the ID Token has a single audience value and that audience is different than the
    authorized party.

    It MAY be included even when the authorized party is the same as the sole audience.

    The `azp` value is a case sensitive string containing a StringOrURI value.
    """

    at_hash: str | None = None
    """
    OPTIONAL. Access Token hash value.

    Its value is the base64url encoding of the left-most half of the hash of the octets of the ASCII representation of
    the `access_token` value, where the hash algorithm used is the hash algorithm used in the `alg` parameter of
    the ID Token's JWS [JWS] header.

    For instance, if the `alg` is `RS256`, hash the `access_token` value with SHA-256,
    then take the left-most 128 bits and base64url encode them.

    The `at_hash` value is a case sensitive string.
    """

    model_config = ConfigDict(
        extra="allow",
    )

    @property
    def semiuniq_field(self) -> str:
        """
        Function guarantees, that will return SOME **SEMI**-uniq field.
        It means that in 99.9% this field will be really uniq.

        Function IS NOT standard and can be changed or removed.
        """

        if self.model_extra:
            if (pref_username := self.model_extra.get("preferred_username", None)) is not None:
                return pref_username

            if (email := self.model_extra.get("email", None)) is not None:
                return email

        return f"Generic {self.iss}/{self.sub}"


class BaseTokenResponse(OAuthTokenResponse):
    id_token: str
    """
    ID Token value associated with the authenticated session.
    """

    model_config = ConfigDict(
        extra="allow",
    )


class TokenResponse(BaseTokenResponse): ...
