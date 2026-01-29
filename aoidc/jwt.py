# ruff: noqa: S105
from enum import StrEnum


class JsonWebAlgos(StrEnum):
    """
    https://datatracker.ietf.org/doc/html/rfc7518#section-3.1

    + https://datatracker.ietf.org/doc/html/rfc9864#section-2.2
    """

    NONE = "none"

    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"

    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"

    ES256 = "ES256"
    ES256K = "ES256K"

    ES384 = "ES384"
    ES512 = "ES512"

    PS256 = "PS256"
    PS384 = "PS384"
    PS512 = "PS512"

    EDDSA = "EdDSA"
    ED25519 = "Ed25519"
    ED448 = "Ed448"
