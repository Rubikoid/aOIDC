import datetime
from collections.abc import Sequence


class GenericError(Exception):
    pass


class GenericAuthError(GenericError):
    pass


class GenericValidationError(ValueError, GenericError):
    pass


class GenericOAuthError(GenericError): ...


class GenericOIDCError(GenericError): ...


class TokenValidationError(GenericValidationError): ...


class TokenIssuerValidationError(TokenValidationError):
    issuer: str
    metadata_issuer: str

    def __init__(self, issuer: str, metadata_issuer: str) -> None:
        super().__init__("Invalid `iss` in token")
        self.issuer = issuer
        self.metadata_issuer = metadata_issuer


class TokenAudValidationError(TokenValidationError):
    aud: str | Sequence[str] | set[str]
    trusted_auds: Sequence[str] | set[str]

    def __init__(self, aud: str | Sequence[str] | set[str], trusted_auds: Sequence[str] | set[str]) -> None:
        if isinstance(aud, str):
            super().__init__("Untrusted `aud` in token")
        else:
            super().__init__("Untrusted `aud` entry in token")

        self.aud = aud
        self.trusted_auds = trusted_auds


class TokenExpireValidationError(TokenValidationError):
    exp: datetime.datetime
    now: datetime.datetime

    def __init__(self, exp: datetime.datetime, now: datetime.datetime) -> None:
        super().__init__("Token expired")

        self.exp = exp
        self.now = now


class TokenFutureValidationError(TokenValidationError):
    iat: datetime.datetime
    now: datetime.datetime

    def __init__(self, iat: datetime.datetime, now: datetime.datetime) -> None:
        super().__init__("Token from future")

        self.iat = iat
        self.now = now
